#!/usr/bin/env python3
"""Qwen3.5-2B VQA tool server (vision line · 用户令 2026-11-14 09:1x #3).

Persistent HTTP server that loads Qwen3.5-2B (multimodal / VL) once on a GPU
and answers visual questions about images — lets cline / designflow benchmark
"看懂波形图" ability. For the waveview use-case: designflow restores the 11
「原意图需看图」 cases (reports/waveview_need_image_handoff.md), then calls
this tool to measure the 「基线 fail → 上 VQA 后 pass」 delta.

API:
  GET  /health   -> {"ok": true, "model": "...", "ready": bool, "load_s": ..}
  POST /vqa      -> JSON body:
        {"image_path": "/abs/path.png",  # preferred (shared NFS)
         "image_b64": "<base64>",        # OR base64
         "question": "How many cycles ...",
         "max_new_tokens": 256,          # optional, default 512
         "temperature": 0.0}             # optional, default greedy
      -> {"ok": true, "answer": "...", "elapsed_s": 1.23, "image": "..."}
  POST /shutdown  -> graceful stop (localhost only)

Usage:
  CUDA_VISIBLE_DEVICES=5 python qwen35_vqa_server.py --port 30001 --gpu 0

Notes:
  - transformers 5.20.2 in conda py310 recognizes `qwen3_5` (verified).
  - Linear-attention kernels (causal_conv1d / flash-linear-attention) NOT
    installed -> transformers falls back to reference PyTorch impl (slower but
    correct, ~2.7s/req on A40 for the 2B model).
"""
import argparse, base64, io, json, os, sys, time, traceback
import torch
from PIL import Image

MODEL_PATH = os.environ.get(
    "QWEN35_VQA_MODEL", "/nas_data/app.e0031982/models/Qwen3.5-2B")


class VQAModel:
    """Loads Qwen3.5-2B VL once; answers image+question pairs.

    If ``adapter`` is given, the base model is wrapped with a PEFT LoRA adapter
    (e.g. the vision-line v2-RFT strengthen adapter) so the SAME HTTP VQA tool
    interface can serve either the base model or the SFT/RL-strengthened model --
    the only variable between the V1 (base) and V2 (adapter) selftest arms.
    """
    def __init__(self, model_path, device, adapter=None):
        from transformers import AutoProcessor, Qwen3_5ForConditionalGeneration
        t0 = time.time()
        self.processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
        self.model = Qwen3_5ForConditionalGeneration.from_pretrained(
            model_path, torch_dtype=torch.bfloat16, device_map=device,
            trust_remote_code=True)
        if adapter:
            from peft import PeftModel
            print(f"[vqa-server] loading LoRA adapter: {adapter}", flush=True)
            self.model = PeftModel.from_pretrained(self.model, adapter)
            self.adapter_name = os.path.basename(os.path.normpath(adapter))
        else:
            self.adapter_name = None
        self.model.eval()
        self.device = device
        self.load_s = time.time() - t0
        self.model_name = os.path.basename(model_path.rstrip("/"))
        if self.adapter_name:
            self.model_name = f"{self.model_name}+{self.adapter_name}"

    @torch.inference_mode()
    def answer(self, image, question, max_new_tokens=512, temperature=0.0):
        t0 = time.time()
        messages = [{"role": "user", "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": question}]}]
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True)
        if not isinstance(image, Image.Image):
            image = Image.open(image).convert("RGB")
        inputs = self.processor(text=[text], images=[image],
                                return_tensors="pt").to(self.model.device)
        do_sample = float(temperature) > 0
        kw = dict(max_new_tokens=int(max_new_tokens), do_sample=do_sample)
        if do_sample:
            kw["temperature"] = float(temperature)
        out = self.model.generate(**inputs, **kw)
        gen = out[0][inputs.input_ids.shape[1]:]
        answer = self.processor.decode(gen, skip_special_tokens=True).strip()
        return answer, time.time() - t0


MODEL = None  # VQAModel, loaded at startup


def _decode_image(image_path=None, image_b64=None):
    if image_path:
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"image_path not found: {image_path}")
        return Image.open(image_path).convert("RGB"), image_path
    if image_b64:
        return Image.open(io.BytesIO(base64.b64decode(image_b64))).convert("RGB"), "<b64>"
    raise ValueError("provide image_path or image_b64")


from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        sys.stderr.write("[%s] %s\n" % (time.strftime("%H:%M:%S"), fmt % args))

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"ok": True, "model": MODEL.model_name if MODEL else None,
                             "ready": MODEL is not None,
                             "load_s": round(MODEL.load_s, 1) if MODEL else None})
        else:
            self._send(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
        except Exception as e:
            self._send(400, {"ok": False, "error": f"bad json: {e}"}); return
        if self.path == "/shutdown":
            if self.client_address[0] not in ("127.0.0.1", "::1"):
                self._send(403, {"ok": False, "error": "remote shutdown denied"}); return
            self._send(200, {"ok": True, "shutting_down": True})
            import threading
            threading.Timer(0.2, lambda: sys.exit(0)).start(); return
        if self.path != "/vqa":
            self._send(404, {"ok": False, "error": "not found"}); return
        if MODEL is None:
            self._send(503, {"ok": False, "error": "model not ready"}); return
        try:
            image, img_tag = _decode_image(payload.get("image_path"),
                                           payload.get("image_b64"))
            q = payload.get("question") or payload.get("prompt")
            if not q:
                raise ValueError("missing 'question'")
            ans, elapsed = MODEL.answer(image, q,
                                        max_new_tokens=payload.get("max_new_tokens", 512),
                                        temperature=payload.get("temperature", 0.0))
            self._send(200, {"ok": True, "answer": ans,
                             "elapsed_s": round(elapsed, 3), "image": img_tag})
        except Exception as e:
            traceback.print_exc()
            self._send(500, {"ok": False, "error": repr(e)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=30001)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--gpu", default="0", help="index within CUDA_VISIBLE_DEVICES")
    ap.add_argument("--model", default=MODEL_PATH)
    ap.add_argument("--adapter", default=None,
                    help="optional PEFT LoRA adapter dir (e.g. v2-RFT strengthen adapter)")
    args = ap.parse_args()
    device = f"cuda:{args.gpu}" if torch.cuda.is_available() else "cpu"
    print(f"[vqa-server] loading {args.model} on {device} ...", flush=True)
    global MODEL
    MODEL = VQAModel(args.model, device, adapter=args.adapter)
    print(f"[vqa-server] ready on {device} (load {MODEL.load_s:.1f}s) "
          f"serving http://{args.host}:{args.port}", flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
