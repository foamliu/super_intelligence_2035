#!/usr/bin/env python3
"""baize_posttrain_a5_qwen35_server.py -- OpenAI-compatible serving for A5 arm.

Purpose (ops 令 2026-11-22 09:3x, P0-2): serve Qwen3.5-2B as the A5 arm baseline
so cline harness can eval it with `--endpoint http://127.0.0.1:8097/v1 --model
qwen3.5-2b-a5`. This is the ONLY variable-vs-A0 component that changes between
the A0 (MiniCPM5-2B, vLLM :8098) and A5 (Qwen3.5-2B, this server :8097) arms.

Why a self-written transformers server (not vLLM):
  - Qwen3.5-2B is a hybrid linear-attention architecture (model_type=qwen3_5,
    Qwen3_5ForCausalLM) that needs transformers >=5.20 AND vLLM/SGLang main
    branch (nightly). The nightly wheels require CUDA 12.8 / driver >=560; this
    host is driver 550.54.14 / CUDA 12.4 max -> vLLM/sglang nightly are NOT
    installable on the cu124 stack (confirmed by `uv` dry-run, wake736).
  - The ONLY env on this host that loads qwen3_5 is conda py310 (transformers
    5.20.2, torch 2.6.0+cu124). It has no vLLM/sglang -> serve via HF
    transformers generate() behind a small OpenAI-compatible HTTP layer.
  - Linear-attention kernels (causal_conv1d / flash-linear-attention) NOT
    installed -> reference PyTorch impl; single-stream ~35 tok/s on A40
    (measured wake739). See THROUGHPUT CAVEAT below.

Pre-registration integrity (ops 令 §二 '唯一自变量 = 基座模型'):
  - To hold the serving stack constant across arms, the SAME self-written
    transformers server can also serve A0 (MiniCPM5-2B is a plain
    LlamaForCausalLM, loadable by the same transformers). Pass --model-path to
    point at MiniCPM5 and --tool-format minicpm5 to parse its `<function name=>`
    format. Running A0 through this server re-measures A0 on the identical stack
    -> serving stack is no longer a confound (vLLM-A0 43.29% becomes a separate
    data point; A0-vs-A5 paired comparison uses both-on-this-server numbers).
  - This file defaults to A5 (Qwen3.5-2B, qwen3_coder tool format).

THROUGHPUT CAVEAT (must be reported with any A5 number):
  - HF generate() without continuous batching serializes concurrent requests on
    the GPU. Under cline `-p 8` parallelism, effective per-request throughput
    drops to ~single_stream/8 (~4-5 tok/s). Many EDA traces need >10k output
    tokens -> under -p 8 most tasks would exceed the 2500s timeout. This makes
    a naive 5-run at -p 8 CONFOUNDED by throughput-induced timeouts.
  - Therefore a 5-run A5 eval via this (non-batched) server is NOT valid until
    either (a) continuous batching is added, or (b) ops authorizes the
    vLLM-nightly path (driver upgrade to >=560, cross-line on GPU0-3). A 1-run
    smoke with reduced concurrency is the maximal valid use until then.

API (OpenAI-compatible subset used by cline):
  GET  /v1/models          -> {"data":[{"id":<served-name>,...}]}
  POST /v1/chat/completions -> chat completion, supports `tools`; non-streaming
         tool_calls parsed from qwen3_coder `<function=..>` output format
  GET  /health             -> internal health
  POST /shutdown           -> graceful stop (localhost only)

Usage:
  CUDA_VISIBLE_DEVICES=5 /nas_data/.../py310/bin/python \\
      baize_posttrain_a5_qwen35_server.py \\
      --port 8097 --gpu 0 --served-model-name qwen3.5-2b-a5
"""
import argparse, json, os, re, sys, threading, time, traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import torch

DEFAULT_MODEL = "/nas_data/app.e0031982/models/Qwen3.5-2B"
DEFAULT_PORT = 8097
DEFAULT_SERVED = "qwen3.5-2b-a5"


class ModelBackend:
    """Loads a causal LM once; answers OpenAI chat-completion requests.

    tool_format selects how assistant tool-call output is parsed into structured
    tool_calls:
      - 'qwen3_coder': `<function=NAME>\n<parameter=K>\nV\n</parameter>\n</function>`
      - 'minicpm5'  : `<function name=NAME>...<parameter=K>V</parameter></function>`
    """
    def __init__(self, model_path, device, tool_format="qwen3_coder", max_model_len=32768):
        from transformers import AutoTokenizer, AutoModelForCausalLM
        t0 = time.time()
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path, dtype=torch.bfloat16, device_map=device, trust_remote_code=True)
        self.model.eval()
        self.device = device
        self.tool_format = tool_format
        self.max_model_len = int(max_model_len)
        self.model_name = os.path.basename(model_path.rstrip("/"))
        self.eos_token_id = self.tokenizer.eos_token_id
        self.load_s = time.time() - t0
        self.im_end_id = self._maybe_token_id("<|im_end|>")

    def _maybe_token_id(self, s):
        try:
            return self.tokenizer.convert_tokens_to_ids(s)
        except Exception:
            return None

    @staticmethod
    def _normalize_messages(messages):
        """Normalize OpenAI messages for the HF chat template.

        The qwen3.5 chat template iterates `tool_call.arguments|items` which
        requires arguments to be a DICT, but OpenAI clients (cline) round-trip
        `arguments` as a JSON STRING. Also normalize the assistant tool_calls
        shape ({function:{name,arguments}}). Returns a deep-copied list.
        """
        import copy
        out = []
        for m in messages:
            mm = copy.deepcopy(m)
            tcs = mm.get("tool_calls")
            if isinstance(tcs, list):
                norm = []
                for tc in tcs:
                    fn = tc.get("function", tc)
                    args = fn.get("arguments")
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {"_raw": args}
                    elif args is None:
                        args = {}
                    norm.append({"id": tc.get("id", "call_0"), "type": "function",
                                 "function": {"name": fn.get("name"), "arguments": args}})
                mm["tool_calls"] = norm
            out.append(mm)
        return out

    @torch.inference_mode()
    def chat_complete(self, messages, tools=None, max_tokens=4096, temperature=0.0, stop=None):
        messages = self._normalize_messages(messages)
        kw = dict(tokenize=False, add_generation_prompt=True)
        if tools:
            kw["tools"] = tools
        text = self.tokenizer.apply_chat_template(messages, **kw)
        ids = self.tokenizer(text, return_tensors="pt").to(self.model.device)
        input_len = ids.input_ids.shape[1]
        budget = self.max_model_len - int(max_tokens)
        if input_len > budget:
            ids.input_ids = ids.input_ids[:, -budget:]
            ids.attention_mask = ids.attention_mask[:, -budget:]
            input_len = budget
        do_sample = float(temperature) > 0
        gen_kw = dict(max_new_tokens=int(max_tokens), do_sample=do_sample,
                      pad_token_id=self.tokenizer.pad_token_id or self.eos_token_id)
        if do_sample:
            gen_kw["temperature"] = float(temperature)
        stop_ids = [self.eos_token_id]
        if self.im_end_id is not None and self.im_end_id != self.eos_token_id:
            stop_ids.append(self.im_end_id)
        gen_kw["eos_token_id"] = stop_ids
        t0 = time.time()
        out = self.model.generate(**ids, **gen_kw)
        gen = out[0][input_len:]
        raw = self.tokenizer.decode(gen, skip_special_tokens=False)
        clean = self.tokenizer.decode(gen, skip_special_tokens=True)
        gen_tokens = int(gen.shape[0])
        elapsed = time.time() - t0
        content, tool_calls, finish_reason = self._parse_output(raw, clean, stop)
        usage = {"prompt_tokens": input_len, "completion_tokens": gen_tokens,
                 "total_tokens": input_len + gen_tokens, "elapsed_s": round(elapsed, 3)}
        return content, tool_calls, finish_reason, usage

    def _parse_output(self, raw, clean, stop):
        if self.tool_format == "qwen3_coder":
            return self._parse_qwen3_coder(raw, clean, stop)
        if self.tool_format == "minicpm5":
            return self._parse_minicpm5(raw, clean, stop)
        return clean.strip(), [], "stop"

    def _parse_qwen3_coder(self, raw, clean, stop):
        tool_calls = []
        pattern = re.compile(r"<function=([^>]+)>(.*?)</function>", re.DOTALL)
        param_pat = re.compile(r"<parameter=([^>]+)>\s*(.*?)\s*</parameter>", re.DOTALL)
        matches = list(pattern.finditer(raw))
        if matches:
            content = self._strip_special(raw[:matches[0].start()]).strip()
            for m in matches:
                fname = m.group(1).strip()
                body = m.group(2)
                args = {}
                for pm in param_pat.finditer(body):
                    args[pm.group(1).strip()] = self._coerce(pm.group(2).strip())
                tool_calls.append({"id": "call_%d" % (len(tool_calls) + 1), "type": "function",
                    "function": {"name": fname, "arguments": json.dumps(args, ensure_ascii=False)}})
            finish = "tool_calls"
        else:
            content = clean.strip()
            finish = "stop"
            if stop:
                for s in (stop if isinstance(stop, list) else [stop]):
                    if s and s in content:
                        content = content.split(s)[0]
        return content, tool_calls, finish

    def _parse_minicpm5(self, raw, clean, stop):
        tool_calls = []
        pattern = re.compile(r"<function\s+name=([^>]+)>(.*?)</function>", re.DOTALL)
        param_pat = re.compile(r"<parameter\s+name=([^>]+)>(.*?)</parameter>", re.DOTALL)
        matches = list(pattern.finditer(raw))
        if matches:
            content = self._strip_special(raw[:matches[0].start()]).strip()
            for m in matches:
                fname = m.group(1).strip()
                body = m.group(2)
                args = {}
                for pm in param_pat.finditer(body):
                    args[pm.group(1).strip()] = self._coerce(pm.group(2).strip())
                tool_calls.append({"id": "call_%d" % (len(tool_calls) + 1), "type": "function",
                    "function": {"name": fname, "arguments": json.dumps(args, ensure_ascii=False)}})
            finish = "tool_calls"
        else:
            content = clean.strip()
            finish = "stop"
            if stop:
                for s in (stop if isinstance(stop, list) else [stop]):
                    if s and s in content:
                        content = content.split(s)[0]
        return content, tool_calls, finish

    @staticmethod
    def _strip_special(text):
        for tok in ["<|im_start|>", "<|im_end|>", "<tool_call>", "</tool_call>", "<tool_response>", "</tool_response>", "<|endoftext|>"]:
            text = text.replace(tok, "")
        return text

    @staticmethod
    def _coerce(val):
        val = val.strip()
        if val.lower() == "true": return True
        if val.lower() == "false": return False
        if val.lower() == "null": return None
        try:
            if re.fullmatch(r"-?\d+", val): return int(val)
            if re.fullmatch(r"-?\d+\.\d+", val): return float(val)
        except Exception:
            pass
        if val and val[0] in "[{":
            try: return json.loads(val)
            except Exception: pass
        return val


BACKEND = None
SERVED_NAME = DEFAULT_SERVED
GEN_LOCK = threading.Lock()


def _json_resp(handler, code, obj):
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    server_version = "baize-a5-server/1.0"
    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (time.strftime("%H:%M:%S"), fmt % args))

    def do_GET(self):
        if self.path == "/health":
            _json_resp(self, 200, {"ok": True, "ready": BACKEND is not None,
                "model": SERVED_NAME, "backend": BACKEND.model_name if BACKEND else None,
                "tool_format": BACKEND.tool_format if BACKEND else None,
                "load_s": round(BACKEND.load_s, 1) if BACKEND else None})
        elif self.path == "/v1/models":
            _json_resp(self, 200, {"object": "list", "data": [
                {"id": SERVED_NAME, "object": "model", "created": int(time.time()), "owned_by": "posttrain-a5"}]})
        else:
            _json_resp(self, 404, {"error": {"message": "not found"}})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
        except Exception as e:
            _json_resp(self, 400, {"error": {"message": "bad json: %s" % e}}); return
        if self.path == "/shutdown":
            if self.client_address[0] not in ("127.0.0.1", "::1"):
                _json_resp(self, 403, {"error": {"message": "remote shutdown denied"}}); return
            _json_resp(self, 200, {"ok": True, "shutting_down": True})
            threading.Timer(0.2, lambda: sys.exit(0)).start(); return
        if self.path != "/v1/chat/completions":
            _json_resp(self, 404, {"error": {"message": "not found"}}); return
        if BACKEND is None:
            _json_resp(self, 503, {"error": {"message": "model not ready"}}); return
        try:
            self._handle_chat(payload)
        except Exception as e:
            traceback.print_exc()
            _json_resp(self, 500, {"error": {"message": repr(e)}})

    def _handle_chat(self, payload):
        messages = payload.get("messages", [])
        tools = payload.get("tools")
        max_tokens = int(payload.get("max_tokens") or payload.get("max_completion_tokens") or 4096)
        temperature = float(payload.get("temperature", 0.0))
        stop = payload.get("stop")
        model = payload.get("model", SERVED_NAME)
        with GEN_LOCK:
            content, tool_calls, finish_reason, usage = BACKEND.chat_complete(
                messages, tools=tools, max_tokens=max_tokens, temperature=temperature, stop=stop)
        msg = {"role": "assistant", "content": content if content else None}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        resp = {"id": "chatcmpl-%d" % int(time.time() * 1000), "object": "chat.completion",
                "created": int(time.time()), "model": model,
                "choices": [{"index": 0, "message": msg, "finish_reason": finish_reason}],
                "usage": usage}
        _json_resp(self, 200, resp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--gpu", default="0", help="index within CUDA_VISIBLE_DEVICES")
    ap.add_argument("--model-path", default=DEFAULT_MODEL)
    ap.add_argument("--served-model-name", default=DEFAULT_SERVED)
    ap.add_argument("--tool-format", default="qwen3_coder", choices=["qwen3_coder", "minicpm5"],
                    help="qwen3_coder for Qwen3.5-2B (A5); minicpm5 for MiniCPM5-2B (A0 re-measurement)")
    ap.add_argument("--max-model-len", type=int, default=32768)
    args = ap.parse_args()
    global BACKEND, SERVED_NAME
    SERVED_NAME = args.served_model_name
    device = "cuda:%s" % args.gpu if torch.cuda.is_available() else "cpu"
    print("[a5-server] loading %s on %s (tool_format=%s) ..." % (args.model_path, device, args.tool_format), flush=True)
    t0 = time.time()
    BACKEND = ModelBackend(args.model_path, device, tool_format=args.tool_format, max_model_len=args.max_model_len)
    print("[a5-server] READY load=%.1fs served=%s backend=%s http://%s:%d" % (
        time.time() - t0, SERVED_NAME, BACKEND.model_name, args.host, args.port), flush=True)
    print("[a5-server] THROUGHPUT CAVEAT: no continuous batching; -p 8 eval will be slow/timeout-prone. See module docstring.", flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
