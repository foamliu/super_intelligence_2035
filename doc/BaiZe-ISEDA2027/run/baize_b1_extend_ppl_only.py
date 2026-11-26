#!/usr/bin/env python3
"""
B1 Extension PPL-only: 512K / 1M (passkey/generate crashes Triton, skip it).
Merges into b1_longctx_extend_results.json.
"""
import json, math, os, sys, time, gc
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

MODEL_PATH = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/hf_iter_4771"
DATA_BIN   = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/p5b_l3/p5b_l3_train_s0.bin"
EOD_TOKEN  = 129280
OUTPUT     = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/b1_longctx_extend_results.json"
CHUNK_SIZE = 4096

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def get_ppl_tokens(n):
    data = np.memmap(DATA_BIN, dtype=np.int32, mode='r')
    raw = np.array(data[:n + 10000])
    raw[raw == EOD_TOKEN] = 295
    return torch.tensor(raw[:n], dtype=torch.long)

def compute_ppl_timed(model, tokens, max_ctx):
    n = min(max_ctx, len(tokens))
    if n < 2:
        return float('nan'), 0, 0, 0
    total_loss = 0.0; total_count = 0; past_kv = None
    torch.cuda.reset_peak_memory_stats(0)
    t_start = time.time()
    with torch.no_grad():
        for start in range(0, n, CHUNK_SIZE):
            end = min(start + CHUNK_SIZE, n)
            input_ids = tokens[start:end].unsqueeze(0).cuda()
            outputs = model(input_ids=input_ids, use_cache=True,
                            past_key_values=past_kv, return_dict=True)
            logits = outputs.logits; past_kv = outputs.past_key_values
            chunk_len = end - start
            if chunk_len > 1:
                total_loss += F.cross_entropy(logits[0, :-1].float(), input_ids[0, 1:], reduction='sum').item()
                total_count += chunk_len - 1
            if end < n:
                total_loss += F.cross_entropy(logits[0, -1:].float(), tokens[end:end+1].cuda(), reduction='sum').item()
                total_count += 1
            del logits, outputs
    total_time = time.time() - t_start
    peak_mem = torch.cuda.max_memory_allocated(0) / 1e9
    ppl = math.exp(min(total_loss / max(total_count, 1), 20))
    return ppl, total_count, total_time, peak_mem

def run_config(name, max_pos, rope_theta, ctxs, ppl_tokens, existing):
    log(f"\n{'='*40}\nConfig: {name} (max_pos={max_pos}, rope_theta={rope_theta})\n{'='*40}")
    config = AutoConfig.from_pretrained(MODEL_PATH, trust_remote_code=True)
    config.max_position_embeddings = max_pos
    config.rope_theta = rope_theta
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH, config=config, dtype=torch.bfloat16,
        trust_remote_code=True, low_cpu_mem_usage=True).cuda().eval()
    log(f"  Model loaded on {torch.cuda.get_device_name(0)}")

    if name not in existing:
        existing[name] = {"max_pos": max_pos, "rope_theta": rope_theta, "ppl": {}, "passkey": {}}
    cr = existing[name]

    for ctx in ctxs:
        key = str(ctx)
        if key in cr["ppl"] and cr["ppl"][key].get("ppl") is not None:
            log(f"  ctx={ctx}: already have result, skip")
            continue
        log(f"  ctx={ctx}: PPL + timing...")
        try:
            ppl, nt, total_time, peak_mem = compute_ppl_timed(model, ppl_tokens, ctx)
            log(f"    PPL={ppl:.4f} (n={nt}, total={total_time:.1f}s, peak={peak_mem:.2f}GB)")
            cr["ppl"][key] = {
                "ppl": ppl, "n_tokens": nt, "total_time_s": round(total_time, 2),
                "peak_vram_GB": round(peak_mem, 2),
                "per_token_ms": round(total_time / max(nt,1) * 1000, 4),
            }
        except Exception as e:
            log(f"    PPL FAILED: {e}")
            cr["ppl"][key] = {"ppl": None, "error": str(e), "error_type": type(e).__name__}
        # Save after each ctx
        with open(OUTPUT, 'w') as f:
            json.dump(existing, f, indent=2, default=str)
        log(f"    Saved to {OUTPUT}")

    del model; gc.collect(); torch.cuda.empty_cache()
    return existing

def main():
    log("=" * 60)
    log("B1 EXTENSION PPL-ONLY: 512K / 1M (no passkey/generate)")
    log("=" * 60)

    # Load existing results
    try:
        with open(OUTPUT, 'r') as f:
            all_res = json.load(f)
        log(f"Loaded existing results from {OUTPUT}")
    except:
        all_res = {"metadata": {}, "configs": {}, "kv_memory_analysis": {}, "complexity_fit": {}}
    if "configs" not in all_res:
        all_res["configs"] = {}

    log("Loading pre-tokenized data (up to 1M tokens)...")
    ppl_tokens = get_ppl_tokens(1048576 + 100)
    log(f"  Loaded {len(ppl_tokens)} tokens")

    # ABF_1e6: 512K + 1M (128K/256K already done)
    all_res = run_config("ABF_1e6", 1048576, 1000000.0, [524288, 1048576], ppl_tokens, all_res["configs"])

    # ABF_5e6: 1M only
    all_res = run_config("ABF_5e6", 1048576, 5000000.0, [1048576], ppl_tokens, all_res["configs"])

    with open(OUTPUT, 'w') as f:
        json.dump(all_res, f, indent=2, default=str)

    log("\n" + "=" * 60 + "\nPPL-ONLY EXTENSION COMPLETE\n" + "=" * 60)
    print("\n=== Summary ===")
    for cn in ["ABF_1e6", "ABF_5e6"]:
        cfg = all_res["configs"].get(cn, {})
        print(f"\n{cn}:")
        for ctx in [131072, 262144, 524288, 1048576]:
            v = cfg.get("ppl", {}).get(str(ctx), {})
            p = v.get("ppl"); t = v.get("total_time_s", ""); m = v.get("peak_vram_GB", "")
            print(f"  ctx={ctx:>8}: PPL={p}, time={t}s, VRAM={m}GB")

if __name__ == "__main__":
    main()
