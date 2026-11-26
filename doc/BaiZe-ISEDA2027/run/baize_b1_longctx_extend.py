#!/usr/bin/env python3
"""
B1 Extension: Long-context scaling to 256K / 512K / 1M for Mamba2-hybrid 2.2B.
Extends B1 step 2/3 (up to 128K) to answer:
  "Can ctx keep expanding? 128K -> 256K -> 512K -> 1M? Who breaks first?"

Bottleneck categories:
  (a) RoPE extrapolation quality — only affects 4 attention layers
  (b) KV cache / VRAM — only grows with 4 attention layers (vs dense 42)
  (c) Attention O(n^2) — SSM is O(n); attention may dominate at extreme ctx
"""
import json, math, os, sys, time, gc, random
os.environ["CUDA_VISIBLE_DEVICES"] = "1"  # only GPU1 visible (GPU0 occupied by A v2)
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

MODEL_PATH = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/hf_iter_4771"
DATA_BIN   = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/p5b_l3/p5b_l3_train_s0.bin"
EOD_TOKEN  = 129280
OUTPUT     = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/b1_longctx_extend_results.json"
GPU_ID     = 0  # GPU1 is now device 0 via CUDA_VISIBLE_DEVICES

CONFIGS = [
    {"name": "ABF_1e6", "max_pos": 1048576, "rope_theta": 1000000.0},
    {"name": "ABF_5e6", "max_pos": 1048576, "rope_theta": 5000000.0},
]
CTX_LENGTHS = [131072, 262144, 524288, 1048576]
CHUNK_SIZE  = 4096

DENSE_CONFIG = {"num_attn_layers": 42, "num_kv_heads": 4, "head_dim": 128, "params_B": 2.512}
HYBRID_CONFIG = {"num_attn_layers": 4, "num_ssm_layers": 24, "num_kv_heads": 4,
                 "head_dim": 128, "ssm_state_size": 128, "mamba_num_heads": 64,
                 "mamba_head_dim": 64, "params_B": 2.220}


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def load_model(cfg_mod):
    log(f"Loading model: {cfg_mod['name']} (max_pos={cfg_mod['max_pos']}, rope_theta={cfg_mod['rope_theta']})")
    config = AutoConfig.from_pretrained(MODEL_PATH, trust_remote_code=True)
    config.max_position_embeddings = cfg_mod["max_pos"]
    config.rope_theta = cfg_mod["rope_theta"]
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH, config=config, dtype=torch.bfloat16,
        trust_remote_code=True, low_cpu_mem_usage=True)
    model = model.cuda(GPU_ID).eval()
    tok = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    return model, tok

def free_model(m):
    del m; gc.collect(); torch.cuda.empty_cache()

def get_ppl_tokens(n):
    data = np.memmap(DATA_BIN, dtype=np.int32, mode='r')
    raw = np.array(data[:n + 10000])
    raw[raw == EOD_TOKEN] = 295
    return torch.tensor(raw[:n], dtype=torch.long)

def compute_ppl_timed(model, tokens, max_ctx):
    """Compute PPL with chunked KV-cache processing, recording per-chunk timing."""
    n = min(max_ctx, len(tokens))
    if n < 2:
        return float('nan'), 0, 0, [], 0
    total_loss = 0.0
    total_count = 0
    past_kv = None
    chunk_times = []
    torch.cuda.reset_peak_memory_stats(GPU_ID)
    t_total_start = time.time()
    with torch.no_grad():
        for start in range(0, n, CHUNK_SIZE):
            end = min(start + CHUNK_SIZE, n)
            input_ids = tokens[start:end].unsqueeze(0).cuda(GPU_ID)
            t_chunk = time.time()
            outputs = model(input_ids=input_ids, use_cache=True,
                            past_key_values=past_kv, return_dict=True)
            chunk_times.append(time.time() - t_chunk)
            logits = outputs.logits
            past_kv = outputs.past_key_values
            chunk_len = end - start
            if chunk_len > 1:
                sl = logits[0, :-1].float()
                slb = input_ids[0, 1:]
                total_loss += F.cross_entropy(sl, slb, reduction='sum').item()
                total_count += chunk_len - 1
            if end < n:
                nxt = tokens[end:end+1].cuda(GPU_ID)
                total_loss += F.cross_entropy(logits[0, -1:].float(), nxt, reduction='sum').item()
                total_count += 1
            del logits, outputs
    total_time = time.time() - t_total_start
    peak_mem = torch.cuda.max_memory_allocated(GPU_ID) / 1e9
    avg = total_loss / max(total_count, 1)
    ppl = math.exp(min(avg, 20))
    return ppl, total_count, total_time, chunk_times, peak_mem

def passkey_test_single(model, tok, max_ctx):
    """Single passkey trial at long ctx (model too weak, just confirm no crash)."""
    if max_ctx < 1024:
        return {"acc": float('nan'), "trials": 0, "correct": 0}
    pad_sent = "The library is located at the corner of the street, near the park. "
    pad_tok = tok.encode(pad_sent, add_special_tokens=False)
    random.seed(99999 + max_ctx)
    key = f"{random.randint(10000, 99999)}"
    key_text = f"The passkey is {key}. Remember this passkey. "
    q_text = "\nWhat is the passkey? The passkey is "
    key_tok = tok.encode(key_text, add_special_tokens=False)
    q_tok = tok.encode(q_text, add_special_tokens=False)
    avail = max_ctx - len(key_tok) - len(q_tok) - 10
    pad1_len = avail // 2
    pad2_len = avail - pad1_len
    def build_pad(tl):
        reps = (tl // len(pad_tok)) + 1
        return (pad_tok * reps)[:tl]
    ids = build_pad(pad1_len) + key_tok + build_pad(pad2_len) + q_tok
    ids = ids[:max_ctx - 1]
    inp = torch.tensor([ids], dtype=torch.long).cuda(GPU_ID)
    t0 = time.time()
    try:
        with torch.no_grad():
            out = model.generate(inp, max_new_tokens=10, do_sample=False,
                                 pad_token_id=tok.pad_token_id or 0)
        gen = tok.decode(out[0, len(ids):], skip_special_tokens=True).strip()
        ok = key in gen
        dt = time.time() - t0
        log(f"    passkey: key={key} gen='{gen[:40]}' ok={ok} ({dt:.1f}s)")
        return {"acc": 1.0 if ok else 0.0, "trials": 1, "correct": int(ok),
                "gen": gen[:60], "time_s": round(dt, 1)}
    except Exception as e:
        log(f"    passkey err: {e}")
        return {"acc": None, "error": str(e), "time_s": round(time.time()-t0, 1)}
    finally:
        torch.cuda.empty_cache()

def analytical_kv_memory(ctx):
    """Compute KV cache memory for hybrid vs dense at given ctx (bs=1, bf16)."""
    def attn_kv(num_layers, num_kv_heads, head_dim):
        return 2 * ctx * num_kv_heads * head_dim * 2 * num_layers
    ssm_state = 1 * HYBRID_CONFIG["mamba_num_heads"] * HYBRID_CONFIG["mamba_head_dim"] \
                * HYBRID_CONFIG["ssm_state_size"] * 2 * HYBRID_CONFIG["num_ssm_layers"]
    hybrid_kv = attn_kv(HYBRID_CONFIG["num_attn_layers"], HYBRID_CONFIG["num_kv_heads"],
                        HYBRID_CONFIG["head_dim"])
    dense_kv  = attn_kv(DENSE_CONFIG["num_attn_layers"], DENSE_CONFIG["num_kv_heads"],
                        DENSE_CONFIG["head_dim"])
    hybrid_weight = HYBRID_CONFIG["params_B"] * 1e9 * 2
    dense_weight  = DENSE_CONFIG["params_B"] * 1e9 * 2
    return {
        "ctx": ctx,
        "hybrid_kv_GB": hybrid_kv / 1e9,
        "hybrid_ssm_state_GB": ssm_state / 1e9,
        "hybrid_total_cache_GB": (hybrid_kv + ssm_state) / 1e9,
        "hybrid_total_GB": (hybrid_kv + ssm_state + hybrid_weight) / 1e9,
        "dense_kv_GB": dense_kv / 1e9,
        "dense_total_cache_GB": dense_kv / 1e9,
        "dense_total_GB": (dense_kv + dense_weight) / 1e9,
        "hybrid_vs_dense_cache_ratio": (hybrid_kv + ssm_state) / dense_kv if dense_kv > 0 else None,
        "dense_oom_80GB": (dense_kv + dense_weight) / 1e9 > 80,
    }

def fit_complexity(times, ctxs):
    """Fit time = a*N + b*N^2, return coefficients and O(N^2) fraction at each ctx."""
    if len(times) < 2:
        return None
    A = np.array([[c, c*c] for c in ctxs], dtype=np.float64)
    b = np.array(times, dtype=np.float64)
    try:
        coef, *_ = np.linalg.lstsq(A, b, rcond=None)
        a, b_coef = coef
        result = {"a_linear": float(a), "b_quadratic": float(b_coef)}
        for c, t in zip(ctxs, times):
            lin_part = a * c
            quad_part = b_coef * c * c
            total = lin_part + quad_part
            result[f"ctx_{c}"] = {
                "measured_s": float(t), "predicted_s": float(total),
                "linear_part_s": float(lin_part), "quadratic_part_s": float(quad_part),
                "quadratic_fraction": float(quad_part / total) if total > 0 else 0,
            }
        return result
    except Exception as e:
        return {"error": str(e)}

def main():
    log("=" * 60)
    log("B1 EXTENSION: Long-context scaling 128K -> 256K -> 512K -> 1M")
    log(f"Model: {MODEL_PATH}")
    log(f"GPU{GPU_ID}: {torch.cuda.get_device_name(GPU_ID)}")
    log("=" * 60)

    log("Loading pre-tokenized data for PPL (up to 1M tokens)...")
    ppl_tokens = get_ppl_tokens(max(CTX_LENGTHS) + 100)
    log(f"  Loaded {len(ppl_tokens)} tokens")

    all_res = {
        "metadata": {"model": MODEL_PATH, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                     "gpu": torch.cuda.get_device_name(GPU_ID), "ctx_lengths": CTX_LENGTHS,
                     "chunk_size": CHUNK_SIZE,
                     "description": "B1 extension: 256K/512K/1M + bottleneck analysis"},
        "configs": {}, "kv_memory_analysis": {}, "complexity_fit": {},
    }

    log("\n=== Analytical KV cache / VRAM comparison (bs=1, bf16) ===")
    for ctx in [4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576]:
        kv = analytical_kv_memory(ctx)
        all_res["kv_memory_analysis"][str(ctx)] = kv
        log(f"  ctx={ctx:>8}: hybrid={kv['hybrid_total_cache_GB']:.2f}GB "
            f"dense={kv['dense_total_cache_GB']:.2f}GB ratio={kv['hybrid_vs_dense_cache_ratio']:.3f} "
            f"dense_80G={'OOM' if kv['dense_oom_80GB'] else 'OK'}")

    all_times = {c["name"]: [] for c in CONFIGS}
    all_ctxs = {c["name"]: [] for c in CONFIGS}

    for cfg in CONFIGS:
        cn = cfg["name"]
        ctxs_to_test = CTX_LENGTHS if cn == "ABF_1e6" else [1048576]
        log(f"\n{'='*40}\nConfig: {cn}\n{'='*40}")
        model, tok = load_model(cfg)
        cr = {"max_pos": cfg["max_pos"], "rope_theta": cfg["rope_theta"], "ppl": {}, "passkey": {}}

        for ctx in ctxs_to_test:
            if ctx > cfg["max_pos"]:
                cr["ppl"][str(ctx)] = {"ppl": None, "reason": "ctx>max_pos"}
                continue
            log(f"  ctx={ctx}: PPL + timing...")
            try:
                ppl, nt, total_time, chunk_times, peak_mem = compute_ppl_timed(model, ppl_tokens, ctx)
                log(f"    PPL={ppl:.4f} (n={nt}, total={total_time:.1f}s, peak={peak_mem:.2f}GB)")
                cr["ppl"][str(ctx)] = {
                    "ppl": ppl, "n_tokens": nt, "total_time_s": round(total_time, 2),
                    "peak_vram_GB": round(peak_mem, 2),
                    "per_token_ms": round(total_time / max(nt,1) * 1000, 4),
                    "first_chunk_s": round(chunk_times[0], 3) if chunk_times else None,
                    "last_chunk_s": round(chunk_times[-1], 3) if chunk_times else None,
                    "num_chunks": len(chunk_times),
                }
                all_times[cn].append(total_time)
                all_ctxs[cn].append(ctx)
            except Exception as e:
                log(f"    PPL FAILED: {e}")
                cr["ppl"][str(ctx)] = {"ppl": None, "error": str(e), "error_type": type(e).__name__}

            if ctx >= 262144:
                log(f"  ctx={ctx}: passkey (1 trial)...")
                try:
                    cr["passkey"][str(ctx)] = passkey_test_single(model, tok, ctx)
                except Exception as e:
                    log(f"    passkey BLOCKED (cuda may be corrupted): {e}")
                    cr["passkey"][str(ctx)] = {"acc": None, "error": str(e), "blocked": True}
            else:
                cr["passkey"][str(ctx)] = {"acc": None, "reason": "skipped"}

        all_res["configs"][cn] = cr
        with open(OUTPUT, 'w') as f:
            json.dump(all_res, f, indent=2, default=str)
        log(f"  Saved to {OUTPUT}")
        free_model(model)

    log("\n=== Complexity fit: time = a*N + b*N^2 ===")
    for cn in ["ABF_1e6"]:
        if len(all_times[cn]) >= 2:
            fit = fit_complexity(all_times[cn], all_ctxs[cn])
            all_res["complexity_fit"][cn] = fit
            if fit and "error" not in fit:
                log(f"  {cn}: a={fit['a_linear']:.2e}, b={fit['b_quadratic']:.2e}")
                for c in all_ctxs[cn]:
                    d = fit.get(f"ctx_{c}", {})
                    log(f"    ctx={c}: quad_frac={d.get('quadratic_fraction', 0):.3f}")

    with open(OUTPUT, 'w') as f:
        json.dump(all_res, f, indent=2, default=str)

    log("\n" + "=" * 60 + "\nB1 EXTENSION COMPLETE\n" + "=" * 60)
    print("\n=== PPL + Prefill Time + VRAM (ABF_1e6) ===")
    print(f"{'ctx':>8} | {'PPL':>8} | {'time_s':>8} | {'VRAM_GB':>8} | {'ms/tok':>8}")
    for ctx in CTX_LENGTHS:
        v = all_res["configs"].get("ABF_1e6", {}).get("ppl", {}).get(str(ctx), {})
        p = v.get("ppl"); t = v.get("total_time_s", ""); m = v.get("peak_vram_GB", ""); ms = v.get("per_token_ms", "")
        print(f"{ctx:>8} | {str(p):>8} | {str(t):>8} | {str(m):>8} | {str(ms):>8}")
    print("\n=== ABF_5e6 @ 1M ===")
    v5 = all_res["configs"].get("ABF_5e6", {}).get("ppl", {}).get("1048576", {})
    print(f"  PPL={v5.get('ppl')}, time={v5.get('total_time_s')}s, VRAM={v5.get('peak_vram_GB')}GB")
    print(f"\nResults saved to {OUTPUT}")

if __name__ == "__main__":
    main()



