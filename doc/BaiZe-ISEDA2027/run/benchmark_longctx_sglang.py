#!/usr/bin/env python3
"""Long-context inference cost benchmark using SGLang.

For a given model (already running on SGLang server), tests context lengths
64K -> 128K -> 256K -> 512K -> 1M -> 2M -> ... until OOM.

Records per context length:
  - peak/steady VRAM (GB)
  - prefill throughput (tok/s)
  - decode throughput (tok/s)
  - end-to-end latency (s)
  - TTFT (s)
  - success / OOM
"""
import argparse, json, os, subprocess, sys, threading, time, statistics
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
    sentence = ("The quick brown fox jumps over the lazy dog near the river bank "
                "while the ancient oak tree watches silently in the morning mist. ")
    tok = get_tokenizer(model_path)
    if tok:
        ids = tok.encode(sentence, add_special_tokens=False)
        full_ids = []
        while len(full_ids) < target_tokens - 256:
            full_ids.extend(ids)
        full_ids = full_ids[:target_tokens - 256]
        prompt = tok.decode(full_ids, skip_special_tokens=True)
        actual_len = len(tok.encode(prompt, add_special_tokens=False))
        return prompt, actual_len
    else:
        chars_needed = int((target_tokens - 256) * 4.5)
        return sentence * (chars_needed // len(sentence) + 1), -1

class VRAMSampler:
    def __init__(self, gpu_id, interval=0.1):
        self.gpu_id = gpu_id; self.interval = interval
        self.samples = []; self._stop = False; self._thread = None
    def start(self):
        self._stop = False; self.samples = []
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
    def _run(self):
        while not self._stop:
            try:
                out = subprocess.check_output(
                    ["nvidia-smi", f"--id={self.gpu_id}", "--query-gpu=memory.used",
                     "--format=csv,noheader,nounits"], text=True, timeout=5).strip()
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
    def steady(self):
        if not self.samples:
            return -1.0
        n = len(self.samples)
        tail = self.samples[int(n * 0.7):]
        return statistics.median(tail) if tail else -1.0

def get_vram_gb(gpu_id):
    try:
        out = subprocess.check_output(
            ["nvidia-smi", f"--id={gpu_id}", "--query-gpu=memory.used",
             "--format=csv,noheader,nounits"], text=True, timeout=10).strip()
        return float(out) / 1024.0
    except Exception:
        return -1.0

def benchmark_single(base_url, model_name, model_path, context, gen_len, gpu_id, timeout=900):
    prompt, actual_tok = make_prompt_precise(model_path, context)
    url = f"{base_url}/v1/completions"
    payload = {"model": model_name, "prompt": prompt, "max_tokens": gen_len,
               "temperature": 0.0, "stream": True,
               "stream_options": {"include_usage": True}}
    result = {"context": context, "prompt_tokens_actual": actual_tok, "gen_len": gen_len}
    vram_before = get_vram_gb(gpu_id)
    sampler = VRAMSampler(gpu_id, interval=0.1)
    sampler.start()
    try:
        t_start = time.perf_counter()
        resp = requests.post(url, json=payload, stream=True, timeout=timeout)
        resp.raise_for_status()
        ttft = None; total_tokens = 0; first_token_time = None; usage_completion = None
        for line in resp.iter_lines():
            if not line:
                continue
            ls = line.decode("utf-8", errors="replace")
            if not ls.startswith("data: "):
                continue
            ds = ls[6:]
            if ds.strip() == "[DONE]":
                break
            try:
                chunk = json.loads(ds)
            except json.JSONDecodeError:
                continue
            choices = chunk.get("choices", [])
            if choices and first_token_time is None:
                first_token_time = time.perf_counter()
                ttft = first_token_time - t_start
            if choices:
                tp = choices[0].get("text", "")
                for ch in choices:
                    total_tokens += len(ch.get("text", ""))
            usage = chunk.get("usage")
            if usage:
                usage_completion = usage.get("completion_tokens", total_tokens)
        t_end = time.perf_counter()
        e2e = t_end - t_start
        sampler.stop()
        vram_after = get_vram_gb(gpu_id)
        peak_vram = max(sampler.peak(), vram_before, vram_after)
        steady_vram = sampler.steady()
        decode_tokens = usage_completion or gen_len
        prefill_tokens = actual_tok if actual_tok > 0 else context
        if ttft and ttft > 0:
            result["ttft_s"] = round(ttft, 4)
            result["prefill_tok_s"] = round(prefill_tokens / ttft, 1)
        else:
            result["ttft_s"] = None; result["prefill_tok_s"] = None
        dt = e2e - (ttft or 0)
        result["decode_tok_s"] = round(decode_tokens / dt, 1) if dt > 0 else None
        result["e2e_latency_s"] = round(e2e, 4)
        result["peak_vram_gb"] = round(peak_vram, 2)
        result["steady_vram_gb"] = round(steady_vram, 2)
        result["kv_cache_gb"] = round(peak_vram - vram_before, 2) if peak_vram > 0 and vram_before > 0 else None
        result["completion_tokens"] = usage_completion or total_tokens
        result["status"] = "success"; result["error"] = None
    except requests.exceptions.ReadTimeout:
        sampler.stop()
        result["status"] = "timeout"; result["error"] = "Request timed out"
        result["peak_vram_gb"] = round(sampler.peak(), 2) if sampler.samples else None
    except Exception as e:
        sampler.stop()
        result["status"] = "error"; result["error"] = f"{type(e).__name__}: {e}"
        result["peak_vram_gb"] = round(sampler.peak(), 2) if sampler.samples else None
    return result
def main():
    ap = argparse.ArgumentParser(description="SGLang long-context inference cost benchmark")
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--model-name", required=True)
    ap.add_argument("--model-path", required=True)
    ap.add_argument("--gpu-id", type=int, default=0)
    ap.add_argument("--output", required=True)
    ap.add_argument("--start-ctx", type=int, default=65536)
    ap.add_argument("--gen-len", type=int, default=128)
    ap.add_argument("--max-ctx", type=int, default=2097152)
    ap.add_argument("--warmup", type=int, default=1)
    ap.add_argument("--repeats", type=int, default=2)
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
    ctx = args.start_ctx
    while ctx <= args.max_ctx:
        print(f"\n{'='*60}")
        print(f"=== Context = {ctx} ({ctx/1024:.0f}K) ===")
        print(f"{'='*60}")
        # Warmup
        for w in range(args.warmup):
            print(f"  [warmup {w+1}/{args.warmup}] ctx={ctx} ...")
            r = benchmark_single(args.base_url, args.model_name, args.model_path,
                                 ctx, args.gen_len, args.gpu_id, timeout=600)
            if r["status"] != "success":
                print(f"  [warmup] FAILED: {r.get('error', 'unknown')}")
                break
            time.sleep(2)
        # Measured runs
        measured = []
        for i in range(args.repeats):
            print(f"  [run {i+1}/{args.repeats}] ctx={ctx} ...")
            r = benchmark_single(args.base_url, args.model_name, args.model_path,
                                 ctx, args.gen_len, args.gpu_id, timeout=900)
            if r["status"] == "success":
                print(f"    OK TTFT={r.get('ttft_s')}s  prefill={r.get('prefill_tok_s')} tok/s  "
                      f"decode={r.get('decode_tok_s')} tok/s  e2e={r.get('e2e_latency_s')}s  "
                      f"VRAM_peak={r.get('peak_vram_gb')}GB  VRAM_steady={r.get('steady_vram_gb')}GB")
                measured.append(r)
            else:
                print(f"    FAILED: {r.get('error', 'unknown')}")
                results.append({"context": ctx, "status": r["status"],
                                "error": r["error"], "peak_vram_gb": r.get("peak_vram_gb")})
                break
            time.sleep(2)
        if measured:
            def med(key):
                vals = [r[key] for r in measured if r.get(key) is not None]
                return round(statistics.median(vals), 4) if vals else None
            med_result = {
                "context": ctx,
                "prompt_tokens_actual": measured[0].get("prompt_tokens_actual"),
                "gen_len": args.gen_len,
                "status": "success",
                "ttft_s": med("ttft_s"),
                "prefill_tok_s": med("prefill_tok_s"),
                "decode_tok_s": med("decode_tok_s"),
                "e2e_latency_s": med("e2e_latency_s"),
                "peak_vram_gb": med("peak_vram_gb"),
                "steady_vram_gb": med("steady_vram_gb"),
                "kv_cache_gb": med("kv_cache_gb"),
                "completion_tokens": measured[-1].get("completion_tokens"),
                "n_runs": len(measured),
                "all_runs": measured,
            }
            results.append(med_result)
            print(f"\n  MEDIAN: TTFT={med_result['ttft_s']}s  prefill={med_result['prefill_tok_s']} tok/s  "
                  f"decode={med_result['decode_tok_s']} tok/s  VRAM_peak={med_result['peak_vram_gb']}GB")
        else:
            print(f"\n  All runs failed at ctx={ctx} -- stopping (OOM point reached)")
            break
        ctx *= 2
        time.sleep(5)

    output = {
        "experiment": "longctx_infer_cost", "framework": "SGLang",
        "model_name": args.model_name, "model_path": args.model_path,
        "base_url": args.base_url, "gpu_id": args.gpu_id,
        "gen_len": args.gen_len, "start_ctx": args.start_ctx,
        "results": results, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[done] results saved to {args.output}")
    print(f"[summary] {len(results)} context lengths tested")

if __name__ == "__main__":
    main()


