#!/usr/bin/env python3
"""baize_posttrain_a5_server_v3_realstream.py -- OpenAI-compatible serving with
STATIC MICRO-BATCHING + REAL STREAMING (keepalive-during-generation) for the
A5 (Qwen3.5-2B) / A0 (MiniCPM5-2B) arms. v3 supersedes v2: v2 FAKE-STREAMED
(generate() to completion THEN emit chunks) so cline maxIdleMs ~252s aborted
any generation >252s before the first chunk -> 93.75% false-negative
contamination on A5 run1 (wake744). v3 emits the role chunk immediately +
SSE keepalive comments every KEEPALIVE_S during generation => cline never
trips maxIdleMs. With flash-linear-attention installed (wake745) batched
throughput is ~221 tok/s (vs ~40 contaminated) => self-written server path
is FEASIBLE without the ops driver>=560/vLLM-nightly upgrade wake744 declared
the ONLY clean path. Same server serves BOTH arms (--tool-format) => serving
stack constant for the A0-vs-A5 paired comparison.

WHY v2 (batched) supersedes v1 (baize_posttrain_a5_qwen35_server.py, GEN_LOCK
serial): v1 serializes concurrent requests one-at-a-time on the GPU. Under
cline `-p 8`, aggregate throughput stays at single-stream ~35 tok/s => ~4.4
tok/s per agent. A0 run1 total output = 1,967,539 tok (mean 12,453/task); at
4.4 tok/s the mean task needs 2,830s > the 2,500s timeout => a -p8 eval on v1
is CONFOUNDED by throughput-induced timeouts (measured wake740).

v2 collects concurrent requests into one HF `generate()` call (static
micro-batch, left-padded), raising aggregate throughput ~3-4x so a -p8 eval
completes within timeout for typical tasks. This unblocks the A5 5-run (and
A0 re-measurement on the identical stack) without needing the vLLM-nightly
driver upgrade.

Pre-registration integrity (ops 令 §二 '唯一自变量 = 基座模型'):
  The SAME v2 server serves BOTH arms (--model-path + --tool-format). A0's
  vLLM 43.29% becomes a separate data point; the A0-vs-A5 paired comparison
  uses both-on-v2 numbers => serving stack is held constant.

CORRECTNESS of static batching (greedy, the EDA-eval regime):
  - Left-pad inputs to equal length; HF generate runs the batch with
    attention_mask, per-sequence EOS early-stop. For greedy (temp=0) the
    first N tokens of a sequence are IDENTICAL whether generated alone or in
    a batch => slicing each output to its own max_tokens reproduces the
    single-request result exactly.
  - Sampling requests (temp>0) cannot share a batch (HF generate takes one
    temperature); they run solo. EDA eval is greedy, so this is rare.

THROUGHPUT CAVEAT (report with any number): this is STATIC batching, not
continuous batching -- within a batch the longest sequence determines
duration (finished sequences wait padded). Net aggregate is still well above
serial. Per-request max_tokens is capped at MAX_GEN_CAP to bound waste.

Usage (A5):
  CUDA_VISIBLE_DEVICES=5 /nas_data/.../py310/bin/python \\
      baize_posttrain_a5_server_v2_batched.py \\
      --port 8097 --gpu 0 --served-model-name qwen3.5-2b-a5 --tool-format qwen3_coder
"""
import argparse, json, os, re, sys, threading, time, traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from collections import deque
import torch

DEFAULT_MODEL = "/nas_data/app.e0031982/models/Qwen3.5-2B"
DEFAULT_PORT = 8097
DEFAULT_SERVED = "qwen3.5-2b-a5"
MAX_BATCH = 8
MAX_GEN_CAP = 16384
FORMATION_MS = 15
FORMATION_POLL_S = 0.005
# v3 real-streaming: cline (@ai-sdk/openai-compatible) enforces maxIdleMs
# ~252s with maxIdleAfter=turn-started; if no stream bytes arrive within that
# window it aborts (TimeoutError, empty code dir). v2 fake-streamed (generated
# the full output THEN emitted chunks) so any generation > ~252s before the
# first chunk was abandoned -> 93.75% false-negative contamination (wake744).
# v3 emits the role chunk immediately, then SSE keepalive comments every
# KEEPALIVE_S while the batch generates, so cline sees bytes continuously and
# never trips maxIdleMs. The parsed content/tool_calls are emitted at the end
# (preserves server-side tool-call parsing). KEEPALIVE_S well under 252s.
KEEPALIVE_S = 60


class Request:
    __slots__ = ("messages", "tools", "max_tokens", "temperature", "stop",
                 "model", "result", "done", "ts")

    def __init__(self, messages, tools, max_tokens, temperature, stop, model):
        self.messages = messages
        self.tools = tools
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.stop = stop
        self.model = model
        self.result = None
        self.done = threading.Event()
        self.ts = time.time()


class ModelBackend:
    """Loads a causal LM once; answers OpenAI chat-completion requests.

    tool_format selects how assistant tool-call output is parsed:
      - 'qwen3_coder': `<function=NAME>\n<parameter=K>\nV\n</parameter>\n</function>`
      - 'minicpm5'  : `<function name=NAME>...<parameter=K>V</parameter></function>`
    """
    def __init__(self, model_path, device, tool_format="qwen3_coder", max_model_len=32768):
        from transformers import AutoTokenizer, AutoModelForCausalLM
        t0 = time.time()
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.tokenizer.padding_side = "left"
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path, dtype=torch.bfloat16, device_map=device, trust_remote_code=True)
        self.model.eval()
        self.device = device
        self.tool_format = tool_format
        self.max_model_len = int(max_model_len)
        self.model_name = os.path.basename(model_path.rstrip("/"))
        self.eos_token_id = self.tokenizer.eos_token_id
        self.pad_id = self.tokenizer.pad_token_id
        if self.pad_id is None:
            self.pad_id = self.eos_token_id
        self.load_s = time.time() - t0
        self.im_end_id = self._maybe_token_id("<|im_end|>")
        self.stop_ids = [self.eos_token_id]
        if self.im_end_id is not None and self.im_end_id != self.eos_token_id:
            self.stop_ids.append(self.im_end_id)
        self.n_batches = 0
        self.n_requests = 0
        self.n_tokens = 0

    def _maybe_token_id(self, s):
        try:
            return self.tokenizer.convert_tokens_to_ids(s)
        except Exception:
            return None

    @staticmethod
    def _normalize_messages(messages):
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

    def prep(self, req):
        messages = self._normalize_messages(req.messages)
        kw = dict(tokenize=False, add_generation_prompt=True)
        if req.tools:
            kw["tools"] = req.tools
        text = self.tokenizer.apply_chat_template(messages, **kw)
        ids = self.tokenizer(text, add_special_tokens=False)["input_ids"]
        input_len = len(ids)
        budget = self.max_model_len - int(req.max_tokens)
        if budget < 1:
            budget = 1
        if input_len > budget:
            ids = ids[-budget:]
            input_len = budget
        return ids, input_len

    @torch.inference_mode()
    def generate_batch(self, batch):
        reqs = [b[0] for b in batch]
        ids_list = [b[1] for b in batch]
        input_lens = [b[2] for b in batch]
        max_new = min(max(int(r.max_tokens) for r in reqs), MAX_GEN_CAP)
        maxlen = max(len(x) for x in ids_list)
        input_ids = []
        attn = []
        for ids in ids_list:
            padlen = maxlen - len(ids)
            input_ids.append([self.pad_id] * padlen + list(ids))
            attn.append([0] * padlen + [1] * len(ids))
        ii = torch.tensor(input_ids, dtype=torch.long, device=self.device)
        am = torch.tensor(attn, dtype=torch.long, device=self.device)
        do_sample = any(float(r.temperature) > 0 for r in reqs)
        gen_kw = dict(max_new_tokens=max_new, do_sample=do_sample,
                      pad_token_id=self.pad_id, attention_mask=am)
        if do_sample:
            gen_kw["temperature"] = max(float(r.temperature) for r in reqs)
        gen_kw["eos_token_id"] = self.stop_ids
        t0 = time.time()
        out = self.model.generate(input_ids=ii, **gen_kw)
        elapsed = time.time() - t0
        for i, req in enumerate(reqs):
            gen = out[i][maxlen:]
            mt = min(int(req.max_tokens), gen.shape[0])
            gen = gen[:mt]
            raw = self.tokenizer.decode(gen, skip_special_tokens=False)
            clean = self.tokenizer.decode(gen, skip_special_tokens=True)
            content, tool_calls, finish_reason = self._parse_output(raw, clean, req.stop)
            usage = {"prompt_tokens": int(input_lens[i]),
                     "completion_tokens": int(gen.shape[0]),
                     "total_tokens": int(input_lens[i]) + int(gen.shape[0]),
                     "elapsed_s": round(elapsed, 3)}
            req.result = (content, tool_calls, finish_reason, usage)
            self.n_tokens += int(gen.shape[0])
        self.n_batches += 1
        self.n_requests += len(reqs)

    @torch.inference_mode()
    def generate_single(self, req, ids, input_len):
        ii = torch.tensor([ids], dtype=torch.long, device=self.device)
        am = torch.ones_like(ii)
        max_new = min(int(req.max_tokens), MAX_GEN_CAP)
        gen_kw = dict(max_new_tokens=max_new, do_sample=True,
                      pad_token_id=self.pad_id, attention_mask=am,
                      temperature=float(req.temperature),
                      eos_token_id=self.stop_ids)
        t0 = time.time()
        out = self.model.generate(input_ids=ii, **gen_kw)
        elapsed = time.time() - t0
        gen = out[0][len(ids):]
        mt = min(int(req.max_tokens), gen.shape[0])
        gen = gen[:mt]
        raw = self.tokenizer.decode(gen, skip_special_tokens=False)
        clean = self.tokenizer.decode(gen, skip_special_tokens=True)
        content, tool_calls, finish_reason = self._parse_output(raw, clean, req.stop)
        usage = {"prompt_tokens": int(input_len),
                 "completion_tokens": int(gen.shape[0]),
                 "total_tokens": int(input_len) + int(gen.shape[0]),
                 "elapsed_s": round(elapsed, 3)}
        req.result = (content, tool_calls, finish_reason, usage)
        self.n_tokens += int(gen.shape[0])
        self.n_batches += 1
        self.n_requests += 1

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
        toks = ["<|im_start|>", "<|im_end|>", "<function_calls>", "</function_calls>",
                "<tool_call>", "</tool_call>", "<tool_response>", "</tool_response>"]
        for tok in toks:
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
QUEUE = deque()
QUEUE_LOCK = threading.Lock()
QUEUE_CV = threading.Condition(QUEUE_LOCK)


def worker_loop():
    """Single generator thread: forms micro-batches and runs generate()."""
    while True:
        with QUEUE_CV:
            while len(QUEUE) == 0:
                QUEUE_CV.wait()
            first = QUEUE.popleft()
        batch = [first]
        deadline = time.time() + FORMATION_MS / 1000.0
        while len(batch) < MAX_BATCH and time.time() < deadline:
            with QUEUE_LOCK:
                if QUEUE:
                    batch.append(QUEUE.popleft())
                else:
                    break
            if len(batch) >= MAX_BATCH:
                break
            time.sleep(FORMATION_POLL_S)
        prepped = []
        errors = []
        for req in batch:
            try:
                ids, il = BACKEND.prep(req)
                prepped.append((req, ids, il))
            except Exception as e:
                req.result = ("", [], "stop",
                              {"prompt_tokens": 0, "completion_tokens": 0,
                               "total_tokens": 0, "elapsed_s": 0.0, "error": repr(e)})
                errors.append(req)
        prepped = [p for p in prepped if p[0] not in errors]
        greedy = [p for p in prepped if float(p[0].temperature) <= 0]
        sampling = [p for p in prepped if float(p[0].temperature) > 0]
        try:
            if greedy:
                BACKEND.generate_batch(greedy)
            for p in sampling:
                BACKEND.generate_single(p[0], p[1], p[2])
        except Exception as e:
            traceback.print_exc()
            for p in prepped:
                if p[0].result is None:
                    p[0].result = ("", [], "stop",
                                   {"prompt_tokens": 0, "completion_tokens": 0,
                                    "total_tokens": 0, "elapsed_s": 0.0, "error": repr(e)})
        for req in batch:
            if req.result is None:
                req.result = ("", [], "stop",
                              {"prompt_tokens": 0, "completion_tokens": 0,
                               "total_tokens": 0, "elapsed_s": 0.0, "error": "no-result"})
            req.done.set()


def _json_resp(handler, code, obj):
    body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    try:
        handler.wfile.write(body)
    except Exception:
        pass


class Handler(BaseHTTPRequestHandler):
    server_version = "baize-a5-server-v2/1.0"
    protocol_version = "HTTP/1.1"  # required for chunked SSE streaming (cline always sends stream:true)
    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (time.strftime("%H:%M:%S"), fmt % args))

    def do_GET(self):
        if self.path == "/health":
            b = BACKEND
            _json_resp(self, 200, {"ok": True, "ready": b is not None,
                "model": SERVED_NAME, "backend": b.model_name if b else None,
                "tool_format": b.tool_format if b else None,
                "load_s": round(b.load_s, 1) if b else None,
                "n_batches": b.n_batches if b else 0,
                "n_requests": b.n_requests if b else 0,
                "n_tokens": b.n_tokens if b else 0,
                "max_batch": MAX_BATCH})
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
        stream = bool(payload.get("stream", False))
        req = Request(messages, tools, max_tokens, temperature, stop, model)
        with QUEUE_CV:
            QUEUE.append(req)
            QUEUE_CV.notify()
        if stream:
            # v3: begin the SSE response IMMEDIATELY (role chunk + keepalives
            # while the batch generates), so cline's maxIdleMs never fires.
            self._emit_stream(req, model)
        else:
            req.done.wait(timeout=3600)
            if req.result is None:
                content, tool_calls, finish_reason, usage = ("", [], "stop",
                    {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0,
                     "elapsed_s": 0.0, "error": "generation-timeout"})
            else:
                content, tool_calls, finish_reason, usage = req.result
            self._emit_json(content, tool_calls, finish_reason, usage, model)

    def _emit_json(self, content, tool_calls, finish_reason, usage, model):
        msg = {"role": "assistant", "content": content if content else None}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        resp = {"id": "chatcmpl-%d" % int(time.time() * 1000), "object": "chat.completion",
                "created": int(time.time()), "model": model,
                "choices": [{"index": 0, "message": msg, "finish_reason": finish_reason}],
                "usage": usage}
        _json_resp(self, 200, resp)

    def _emit_stream(self, req, model):
        """v3 REAL streaming: emit role chunk immediately, then SSE keepalive
        comments every KEEPALIVE_S while the batch generates (so cline's
        maxIdleMs ~252s never fires), then emit the parsed content/tool_calls
        + finish_reason + [DONE] once generation completes.

        cline (@ai-sdk/openai-compatible) treats any bytes on the stream
        (including SSE comment lines starting with ':') as connection
        activity that resets the idle timer; this is the standard SSE
        keepalive pattern. The role-establishing chunk is a real event so
        cline enters the assistant turn immediately.
        """
        self.close_connection = True
        cid = "chatcmpl-%d" % int(time.time() * 1000)
        created = int(time.time())
        base = {"id": cid, "object": "chat.completion.chunk", "created": created, "model": model}
        try:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Transfer-Encoding", "chunked")
            self.send_header("Connection", "close")
            self.end_headers()

            def send_chunk(delta, finish=None, with_usage=False):
                choice = {"index": 0, "delta": delta, "finish_reason": finish}
                obj = dict(base)
                obj["choices"] = [choice]
                if with_usage:
                    obj["usage"] = {"prompt_tokens": int(req.result[3].get("prompt_tokens", 0)) if req.result else 0,
                                    "completion_tokens": int(req.result[3].get("completion_tokens", 0)) if req.result else 0,
                                    "total_tokens": int(req.result[3].get("total_tokens", 0)) if req.result else 0}
                data = ("data: " + json.dumps(obj, ensure_ascii=False) + "\n\n").encode("utf-8")
                self.wfile.write(("%x\r\n" % len(data)).encode("ascii") + data + b"\r\n")
                self.wfile.flush()

            def send_raw(raw_bytes):
                # raw SSE line (keepalive comment), chunked-encoded
                self.wfile.write(("%x\r\n" % len(raw_bytes)).encode("ascii") + raw_bytes + b"\r\n")
                self.wfile.flush()

            # 1) role-establishing chunk immediately (resets idle timer at t=0)
            send_chunk({"role": "assistant"})
            # 2) keepalive loop while the batch generates
            while not req.done.is_set():
                got = req.done.wait(timeout=KEEPALIVE_S)
                if got:
                    break
                # generation still running: emit keepalive comment
                try:
                    send_raw(b": keepalive\n\n")
                except (BrokenPipeError, ConnectionResetError, OSError):
                    return  # client disconnected; stop streaming
            # 3) generation complete: emit parsed content / tool_calls / finish
            if req.result is None:
                content, tool_calls, finish_reason, usage = ("", [], "stop",
                    {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0,
                     "elapsed_s": 0.0, "error": "generation-timeout"})
            else:
                content, tool_calls, finish_reason, usage = req.result
            if content:
                send_chunk({"content": content})
            if tool_calls:
                tc_list = []
                for i, tc in enumerate(tool_calls):
                    fn = tc.get("function", tc)
                    tc_list.append({"index": i, "id": tc.get("id", "call_%d" % (i + 1)),
                                    "type": "function",
                                    "function": {"name": fn.get("name"),
                                                 "arguments": fn.get("arguments", "")}})
                send_chunk({"tool_calls": tc_list})
            clean_usage = {"prompt_tokens": int(usage.get("prompt_tokens", 0)),
                           "completion_tokens": int(usage.get("completion_tokens", 0)),
                           "total_tokens": int(usage.get("total_tokens", 0))}
            # final chunk with finish_reason + usage
            fchoice = {"index": 0, "delta": {}, "finish_reason": finish_reason}
            fobj = dict(base); fobj["choices"] = [fchoice]; fobj["usage"] = clean_usage
            fdata = ("data: " + json.dumps(fobj, ensure_ascii=False) + "\n\n").encode("utf-8")
            self.wfile.write(("%x\r\n" % len(fdata)).encode("ascii") + fdata + b"\r\n")
            # 4) SSE terminator
            done = b"data: [DONE]\n\n"
            self.wfile.write(("%x\r\n" % len(done)).encode("ascii") + done + b"\r\n")
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            # client disconnected mid-stream; nothing more to do
            pass


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
    print("[a5-server-v2] loading %s on %s (tool_format=%s) ..." % (args.model_path, device, args.tool_format), flush=True)
    t0 = time.time()
    BACKEND = ModelBackend(args.model_path, device, tool_format=args.tool_format, max_model_len=args.max_model_len)
    print("[a5-server-v2] READY load=%.1fs served=%s backend=%s http=%s:%d" % (
        time.time() - t0, SERVED_NAME, BACKEND.model_name, args.host, args.port), flush=True)
    print("[a5-server-v2] STATIC MICRO-BATCHING: max_batch=%d formation_ms=%d max_gen_cap=%d" % (
        MAX_BATCH, FORMATION_MS, MAX_GEN_CAP), flush=True)
    w = threading.Thread(target=worker_loop, daemon=True)
    w.start()
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
