#!/usr/bin/env python3
"""P-9.11 D: sglang production-stack VRAM benchmark (H3 gap fill).

Key fixes vs original benchmark_p911_sglang.py:
  1. Uses tokenizer to PRECISELY control prompt token count (fixes the
     char-count bug that caused 128K to be rejected in original P-9.11).
  2. Designed to run with LOW --mem-fraction-static (0.3) so sglang does NOT
     pre-allocate ~68 GB, revealing TRUE VRAM usage at each context length.
  3. Samples VRAM via nvidia-smi DURING the request (not just before/after).

Test matrix: ctx {4K,16K,64K,128K} x bs {1,8}, gen_len=64.
Model: BaiZe Mamba2-hybrid 2.220B (p3_hybrid/hf_iter_5000, nemotron_h).
"""
import argparse, json, os, subprocess, sys, time, threading
import requests

_TOKENIZER = None

def get_tokenizer(model_path):
    global _TOKENIZER
    if _TOKENIZER is not None:
        return _TOKENIZER
    try:
        from transformers import AutoTokenizer
        _TOKENIZER = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    except Exception as e:
        print(f"[warn] AutoTokenizer failed ({e}), fallback to char estimate", file=sys.stderr)
        _TOKENIZER = False
    return _TOKENIZER

def make_prompt_precise(model_path, target_tokens):
    """Build a prompt whose tokenized length is <= target_tokens - 128 (safety margin)."""
    sentence = ("The quick brown fox jumps over the lazy dog near the river bank "
                "while the ancient oak tree watches silently in the morning mist. ")
    tok = get_tokenizer(model_path)
    if tok:
        ids = tok.encode(sentence, add_special_tokens=False)
        full_ids = []
        while len(full_ids) < target_tokens - 128:
            full_ids.extend(ids)
        full_ids = full_ids[:target_tokens - 128]
        prompt = tok.decode(full_ids, skip_special_tokens=True)
        actual_len = len(tok.encode(prompt, add_special_tokens=False))
        return prompt, actual_len
    else:
        chars_needed = int((target_tokens - 128) * 4.5)
        return sentence * (chars_needed // len(sentence) + 1), -1


class VRAMSampler:
    """Continuously samples GPU VRAM in a background thread."""
    def __init__(self, gpu_id, interval=0.2):
        self.gpu_id = gpu_id
        self.interval = interval
        self.samples = []
        self._stop = False
        self._thread = None

    def start(self):
        self._stop = False
        self.samples = []
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self._stop:
            try:
                out = subprocess.check_output(
                    ["nvidia-smi", f"--id={self.gpu_id}",
                     "--query-gpu=memory.used",
                     "--format=csv,noheader,nounits"],
                    text=True, timeout=5).strip()
                self.samples.append(float(out) / 1024.0)
            except Exception:
                pass
            time.sleep(self.interval)

    def stop(self):
        self._stop = True
        if self._thread:
            self._thread.join(timeout=2)

    def peak(self):
        return max(self.samples) if self.samples else -1.0

def benchmark_cell(base_url, model_name, model_path, context, batch, gen_len, gpu_id):
    prompt, actual_tok = make_prompt_precise(model_path, context)
    url = f"{base_url}/v1/completions"
    payload = {"model": model_name, "prompt": [prompt] * batch,
               "max_tokens": gen_len, "temperature": 0.0, "stream": True,
               "stream_options": {"include_usage": True}}
    result = {"model": model_name, "ctx": context, "batch": batch,
              "gen_len": gen_len, "prompt_tokens_actual": actual_tok}
    sampler = VRAMSampler(gpu_id, interval=0.1)
    sampler.start()
    try:
        t_start = time.perf_counter()
        resp = requests.post(url, json=payload, stream=True, timeout=600)
        resp.raise_for_status()
        ttft = None; total_tokens = 0; first_token_time = None
        for line in resp.iter_lines():
            if not line: continue
            ls = line.decode("utf-8", errors="replace")
            if not ls.startswith("data: "): continue
            ds = ls[6:]
            if ds.strip() == "[DONE]": break
            try: chunk = json.loads(ds)
            except json.JSONDecodeError: continue
            choices = chunk.get("choices", [])
            if choices:
                tp = choices[0].get("text", "")
                if tp and first_token_time is None:
                    first_token_time = time.perf_counter()
                    ttft = first_token_time - t_start
                for ch in choices:
                    total_tokens += len(ch.get("text", ""))
            usage = chunk.get("usage")
            if usage: total_tokens = usage.get("completion_tokens", total_tokens)
        t_end = time.perf_counter()
        e2e = t_end - t_start
        sampler.stop()
        peak_vram = sampler.peak()
        decode_tokens = gen_len * batch
        prefill_tokens = actual_tok * batch
        if ttft and ttft > 0:
            result["ttft_s"] = round(ttft, 4)
            result["prefill_tok_s"] = round(prefill_tokens / ttft, 1)
        else:
            result["ttft_s"] = None; result["prefill_tok_s"] = None
        dt = e2e - (ttft or 0)
        result["decode_tok_s"] = round(decode_tokens / dt, 1) if dt > 0 else None
        result["e2e_latency_s"] = round(e2e, 4)
        result["peak_vram_gb"] = round(peak_vram, 2)
        result["total_completion_tokens"] = total_tokens
        result["vram_samples"] = len(sampler.samples)
    except Exception as e:
        sampler.stop()
        result["error"] = f"{type(e).__name__}: {e}"
        result["peak_vram_gb"] = round(sampler.peak(), 2)
    return result

def main():
    ap = argparse.ArgumentParser(description="P-9.11 D: sglang VRAM benchmark (H3 gap fill)")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--model-name", required=True)
    ap.add_argument("--model-path", required=True, help="HF model path for tokenizer")
    ap.add_argument("--gpu-id", type=int, default=0)
    ap.add_argument("--output", required=True)
    ap.add_argument("--contexts", type=int, nargs="+", default=[4096, 16384, 65536, 131072])
    ap.add_argument("--batches", type=int, nargs="+", default=[1, 8])
    ap.add_argument("--gen-len", type=int, default=64)
    args = ap.parse_args()
    try:
        models = requests.get(f"{args.base_url}/v1/models", timeout=30).json()
        print(f"[health] server models: {[m['id'] for m in models.get('data', [])]}")
    except Exception as e:
        print(f"[error] server health check failed: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"[init] loading tokenizer from {args.model_path} ...")
    get_tokenizer(args.model_path)
    results = []
    for ctx in args.contexts:
        for bs in args.batches:
            print(f"\n=== {args.model_name} | ctx={ctx} batch={bs} ===")
            r = benchmark_cell(args.base_url, args.model_name, args.model_path,
                               ctx, bs, args.gen_len, args.gpu_id)
            if "error" in r:
                print(f"  ERROR: {r['error']}")
            else:
                print(f"  TTFT={r.get('ttft_s')}s  prefill={r.get('prefill_tok_s')} tok/s  "
                      f"decode={r.get('decode_tok_s')} tok/s  e2e={r.get('e2e_latency_s')}s  "
                      f"VRAM={r.get('peak_vram_gb')}GB  prompt_tok={r.get('prompt_tokens_actual')}")
            results.append(r)
            time.sleep(2)
    output = {
        "experiment": "P-9.11-D",
        "description": "sglang VRAM benchmark with low mem-fraction (H3 gap fill)",
        "model_name": args.model_name,
        "model_path": args.model_path,
        "base_url": args.base_url,
        "gpu_id": args.gpu_id,
        "gen_len": args.gen_len,
        "contexts": args.contexts,
        "batches": args.batches,
        "results": results,
    }
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n[done] results saved to {args.output}")

if __name__ == "__main__":
    main()