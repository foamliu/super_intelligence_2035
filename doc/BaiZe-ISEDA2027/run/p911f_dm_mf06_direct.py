#!/usr/bin/env python3
"""Direct benchmark for DM 2.229B at mf=0.6, filling 512K and 1M gaps.
Uses the existing SGLang server on port 30050 (already running on GPU 0).
"""
import sys, json, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p911d_sglang_vram_bench import benchmark_cell

BASE_URL = 'http://127.0.0.1:30050'
MODEL_NAME = 'default'
MODEL_PATH = '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/hf_checkpoints/dense_matched_2.22b'
GPU_ID = 0
RESULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'p911f_results')
os.makedirs(RESULT_DIR, exist_ok=True)

CONFIGS = [
    (524288,  1),   # 512K bs=1
    (1048576, 1),   # 1M bs=1
]

for ctx, bs in CONFIGS:
    print(f'\n=== DM 2.229B | ctx={ctx} bs={bs} mf=0.6 (repeats=3) ===', flush=True)
    r = benchmark_cell(BASE_URL, MODEL_NAME, MODEL_PATH, ctx, bs, 64, GPU_ID,
                       warmup=1, repeats=3)
    r['mem_frac'] = 0.6
    r['model_arch'] = 'llama'
    r['ssm_dtype'] = 'N/A'
    if r.get('prefill_tok_s') and bs > 0:
        r['prefill_tok_s_perB'] = round(r['prefill_tok_s'] / bs, 1)
    if r.get('decode_tok_s') and bs > 0:
        r['decode_tok_s_perB'] = round(r['decode_tok_s'] / bs, 1)
    of = os.path.join(RESULT_DIR, f'bench_dense_matched_2.229b_gpu0_mf0.6_ctx{ctx}_bs{bs}.json')
    with open(of, 'w') as f:
        json.dump(r, f, indent=2)
    print(f'  Saved to {of}', flush=True)
    print(f'  prefill={r.get("prefill_tok_s")} decode={r.get("decode_tok_s")} '
          f'error={r.get("error")} tct={r.get("total_completion_tokens")}', flush=True)
    time.sleep(2)

print('\n=== ALL DONE ===', flush=True)
