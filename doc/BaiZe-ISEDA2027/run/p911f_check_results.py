#!/usr/bin/env python3
"""Check all p911f results and summarize."""
import json, glob, os

RESULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "p911f_results")

for pattern in [
    "bench_dense_matched_2.229b_gpu*_mf0.6_*.json",
    "bench_dense_matched_2.229b_gpu*_mf0.85_*.json",
    "bench_dense_ref_2.512b_gpu*_mf0.6_*.json",
    "bench_dense_ref_2.512b_gpu*_mf0.85_*.json",
    "bench_hybrid_2.220b_gpu*_mf0.6_*.json",
    "bench_hybrid_2.220b_gpu*_mf0.75_*.json",
]:
    files = sorted(glob.glob(os.path.join(RESULT_DIR, pattern)))
    if not files:
        continue
    print(f"\n=== {pattern} ({len(files)} files) ===")
    for f in files:
        try:
            d = json.load(open(f))
            name = os.path.basename(f)
            ctx = d.get("ctx", "?")
            bs = d.get("batch", "?")
            pf = d.get("prefill_tok_s")
            dc = d.get("decode_tok_s")
            tct = d.get("total_completion_tokens")
            err = d.get("error")
            vram = d.get("peak_vram_gb")
            print(f"  {name:70s} ctx={ctx:>8} bs={bs} pf={pf} dc={dc} vram={vram} tct={tct} err={err}")
        except Exception as e:
            print(f"  {os.path.basename(f):70s} ERROR: {e}")
