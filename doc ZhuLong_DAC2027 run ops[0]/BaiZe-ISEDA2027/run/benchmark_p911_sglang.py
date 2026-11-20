#!/usr/bin/env python3
"""P-9.11: sglang production-stack inference benchmark.

BaiZe (Mamba2-hybrid 2B, nemotron_h) vs MiniCPM5-2B (dense GPT, Llama).
Connects to a running sglang OpenAI-compatible server and measures:
  - TTFT (time to first token)
  - prefill throughput (tok/s)
  - decode throughput (tok/s)
  - end-to-end latency
  - peak VRAM (via nvidia-smi)
Test matrix: context in {4K,16K,64K,128K} x batch in {1,8}, gen_len=64.
"""
import argparse, json, os, subprocess, sys, time
import requests

def make_prompt(target_tokens):
    sentence = ("The quick brown fox jumps over the lazy dog near the river bank "
                "while the ancient oak tree watches silently in the morning mist. ")
    repeats = max(1, target_tokens // 20 + 1)
    return sentence * repeats

def get_peak_vram_gb(gpu_id):
    try:
        out = subprocess.check_output(
            ["nvidia-smi", f"--id={gpu_id}", "--query-gpu=memory.used",
             "--format=csv,noheader,nounits"], text=True, timeout=10).strip()
        return float(out) / 1024.0
    except Exception as e:
        print(f"[warn] nvidia-smi failed: {e}", file=sys.stderr)
        return -1.0

def benchmark_cell(base_url, model_name, context, batch, gen_len, gpu_id):
    prompt = make_prompt(context)
    url = f"{base_url}/v1/completions"
    payload = {"model": model_name, "prompt": [prompt]*batch,
               "max_tokens": gen_len, "temperature": 0.0, "stream": True,
               "stream_options": {"include_usage": True}}
    result = {"model": model_name, "ctx": context, "batch": batch, "gen_len": gen_len}
    vram_before = get_peak_vram_gb(gpu_id)
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
        vram_after = get_peak_vram_gb(gpu_id)
        peak_vram = max(vram_before, vram_after)
        decode_tokens = gen_len * batch
        prefill_tokens = context * batch
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
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--model-name", required=True)
    ap.add_argument("--gpu-id", type=int, default=0)
    ap.add_argument("--output", required=True)
    ap.add_argument("--contexts", type=int, nargs="+", default=[4096,16384,65536,131072])
    ap.add_argument("--batches", type=int, nargs="+", default=[1,8])
    ap.add_argument("--gen-len", type=int, default=64)
    args = ap.parse_args()
    try:
        models = requests.get(f"{args.base_url}/v1/models", timeout=30).json()
        print(f"[health] server models: {[m['id'] for m in models.get('data', [])]}")
    except Exception as e:
        print(f"[error] server health check failed: {e}", file=sys.stderr); sys.exit(1)
    results = []
    for ctx in args.contexts:
        for bs in args.batches:
            print(f"\n=== {args.model_name} | ctx={ctx} batch={bs} ===")
            r = benchmark_cell(args.base_url, args.model_name, ctx, bs, args.gen_len, args.gpu_id)
            if "error" in r: print(f"  ERROR: {r['error']}")
            else: print(f"  TTFT={r.get('ttft_s')}s  prefill={r.get('prefill_tok_s')} tok/s  decode={r.get('decode_tok_s')} tok/s  e2e={r.get('e2e_latency_s')}s  VRAM={r.get('peak_vram_gb')}GB")
            results.append(r); time.sleep(2)
    output = {"experiment":"P-9.11","description":"sglang production-stack inference benchmark",
              "model_name":args.model_name,"base_url":args.base_url,"gpu_id":args.gpu_id,
              "gen_len":args.gen_len,"contexts":args.contexts,"batches":args.batches,"results":results}
    with open(args.output, "w") as f: json.dump(output, f, indent=2)
    print(f"\n[done] results saved to {args.output}")

if __name__ == "__main__": main()
