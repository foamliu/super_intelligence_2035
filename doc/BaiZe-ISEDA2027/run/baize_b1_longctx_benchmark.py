#!/usr/bin/env python3
"""
B1 Step 2/3: Long-context degradation curve for Mamba2-hybrid 2.2B.
Tests PPL + passkey retrieval at ctx in {4K,8K,16K,32K,64K,128K}
under different RoPE/config variants.
"""
import json, math, os, sys, time, gc, random
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

MODEL_PATH = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/hf_iter_4771"
DATA_BIN   = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/p5b_l3/p5b_l3_train_s0.bin"
EOD_TOKEN  = 129280
OUTPUT     = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/b1_longctx_results.json"

CONFIGS = [
    {"name": "baseline",   "max_pos": 4096,   "rope_theta": 10000.0},
    {"name": "maxpos_only","max_pos": 131072, "rope_theta": 10000.0},
    {"name": "ABF_1e6",    "max_pos": 131072, "rope_theta": 1000000.0},
]
CTX_LENGTHS = [4096, 8192, 16384, 32768, 65536, 131072]
CHUNK_SIZE  = 4096
NUM_PASSKEY_TRIALS = 5   # reduced from 10 for time budget
NUM_PASSKEY_TRIALS_LONG = 3  # for ctx >= 64K

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def load_model(cfg_mod):
    log(f"Loading model: {cfg_mod}")
    config = AutoConfig.from_pretrained(MODEL_PATH, trust_remote_code=True)
    config.max_position_embeddings = cfg_mod["max_pos"]
    config.rope_theta = cfg_mod["rope_theta"]
    log(f"  max_pos={config.max_position_embeddings}, rope_theta={config.rope_theta}")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH, config=config, dtype=torch.bfloat16,
        trust_remote_code=True, low_cpu_mem_usage=True)
    model = model.cuda().eval()
    tok = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
    return model, tok

def free_model(m):
    del m; gc.collect(); torch.cuda.empty_cache()

def get_ppl_tokens(n):
    data = np.memmap(DATA_BIN, dtype=np.int32, mode='r')
    raw = np.array(data[:n + 10000])
    raw[raw == EOD_TOKEN] = 295  # replace EOD with "."
    return torch.tensor(raw[:n], dtype=torch.long)

def compute_ppl(model, tokens, max_ctx):
    """Compute PPL on first max_ctx tokens, chunked processing with KV cache."""
    n = min(max_ctx, len(tokens))
    if n < 2:
        return float('nan'), 0
    total_loss = 0.0
    total_count = 0
    past_kv = None
    with torch.no_grad():
        for start in range(0, n, CHUNK_SIZE):
            end = min(start + CHUNK_SIZE, n)
            input_ids = tokens[start:end].unsqueeze(0).cuda()
            outputs = model(input_ids=input_ids, use_cache=True,
                            past_key_values=past_kv, return_dict=True)
            logits = outputs.logits
            past_kv = outputs.past_key_values
            chunk_len = end - start
            if chunk_len > 1:
                sl = logits[0, :-1].float()
                slb = input_ids[0, 1:]
                total_loss += F.cross_entropy(sl, slb, reduction='sum').item()
                total_count += chunk_len - 1
            if end < n:
                nxt = tokens[end:end+1].cuda()
                total_loss += F.cross_entropy(logits[0, -1:].float(), nxt, reduction='sum').item()
                total_count += 1
            del logits, outputs
    avg = total_loss / max(total_count, 1)
    ppl = math.exp(min(avg, 20))
    return ppl, total_count

def passkey_test(model, tok, max_ctx):
    """Passkey retrieval: hide a 5-digit key in long context, ask model to find it."""
    if max_ctx < 1024:
        return {"acc": float('nan'), "trials": 0, "correct": 0}
    n_trials = NUM_PASSKEY_TRIALS_LONG if max_ctx >= 65536 else NUM_PASSKEY_TRIALS
    pad_sent = "The library is located at the corner of the street, near the park. "
    pad_tok = tok.encode(pad_sent, add_special_tokens=False)
    results = []
    for trial in range(n_trials):
        random.seed(trial * 1000 + max_ctx)
        key = f"{random.randint(10000, 99999)}"
        key_text = f"The passkey is {key}. Remember this passkey. "
        q_text = "\nWhat is the passkey? The passkey is "
        key_tok = tok.encode(key_text, add_special_tokens=False)
        q_tok = tok.encode(q_text, add_special_tokens=False)
        avail = max_ctx - len(key_tok) - len(q_tok) - 10
        if avail <= 0:
            results.append(False); continue
        pad1_len = avail // 2
        pad2_len = avail - pad1_len
        def build_pad(tl):
            reps = (tl // len(pad_tok)) + 1
            return (pad_tok * reps)[:tl]
        ids = build_pad(pad1_len) + key_tok + build_pad(pad2_len) + q_tok
        ids = ids[:max_ctx - 1]
        inp = torch.tensor([ids], dtype=torch.long).cuda()
        try:
            with torch.no_grad():
                out = model.generate(inp, max_new_tokens=10, do_sample=False,
                                     pad_token_id=tok.pad_token_id or 0)
            gen = tok.decode(out[0, len(ids):], skip_special_tokens=True).strip()
            ok = key in gen
            results.append(ok)
            if trial < 3:
                log(f"    trial {trial}: key={key} gen='{gen[:40]}' ok={ok}")
        except Exception as e:
            log(f"    trial {trial} err: {e}")
            results.append(False)
        torch.cuda.empty_cache()
    return {"acc": sum(results)/len(results), "trials": len(results), "correct": sum(results)}

def main():
    log("="*60)
    log("B1 Step 2/3: Long-context degradation curve")
    log(f"Model: {MODEL_PATH}")
    log(f"GPU: {torch.cuda.get_device_name(0)}")
    log("="*60)
    log("Loading pre-tokenized data for PPL...")
    ppl_tokens = get_ppl_tokens(max(CTX_LENGTHS) + 100)
    log(f"  Loaded {len(ppl_tokens)} tokens")

    all_res = {"metadata": {"model": MODEL_PATH, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "gpu": torch.cuda.get_device_name(0), "ctx_lengths": CTX_LENGTHS},
               "configs": {}}

    for cfg in CONFIGS:
        cn = cfg["name"]
        log(f"\n{'='*40}\nConfig: {cn} (max_pos={cfg['max_pos']}, rope_theta={cfg['rope_theta']})\n{'='*40}")
        model, tok = load_model(cfg)
        cr = {"max_pos": cfg["max_pos"], "rope_theta": cfg["rope_theta"], "ppl": {}, "passkey": {}}

        for ctx in CTX_LENGTHS:
            if ctx > cfg["max_pos"]:
                log(f"  ctx={ctx}: skip (ctx>max_pos)")
                cr["ppl"][str(ctx)] = {"ppl": None, "reason": "ctx>max_pos"}
                cr["passkey"][str(ctx)] = {"acc": None, "reason": "ctx>max_pos"}
                continue
            log(f"  ctx={ctx}: PPL...")
            t0 = time.time()
            try:
                ppl, nt = compute_ppl(model, ppl_tokens, ctx)
                log(f"    PPL={ppl:.4f} (n={nt}, {time.time()-t0:.1f}s)")
                cr["ppl"][str(ctx)] = {"ppl": ppl, "n_tokens": nt, "time_s": round(time.time()-t0,1)}
            except Exception as e:
                log(f"    PPL FAILED: {e}")
                cr["ppl"][str(ctx)] = {"ppl": None, "error": str(e)}
            log(f"  ctx={ctx}: passkey...")
            t0 = time.time()
            try:
                pk = passkey_test(model, tok, ctx)
                log(f"    acc={pk['acc']:.2f} ({pk['correct']}/{pk['trials']}, {time.time()-t0:.1f}s)")
                pk["time_s"] = round(time.time()-t0, 1)
                cr["passkey"][str(ctx)] = pk
            except Exception as e:
                log(f"    passkey FAILED: {e}")
                cr["passkey"][str(ctx)] = {"acc": None, "error": str(e)}

        all_res["configs"][cn] = cr
        with open(OUTPUT, 'w') as f:
            json.dump(all_res, f, indent=2)
        log(f"  Saved to {OUTPUT}")
        free_model(model)

    log("\n"+"="*60+"\nB1 Step 2/3 COMPLETE\n"+"="*60)
    # Summary
    print("\n=== PPL ===")
    print(f"{'ctx':>8}" + "".join(f" | {c['name']:>14}" for c in CONFIGS))
    for ctx in CTX_LENGTHS:
        row = f"{ctx:>8}"
        for c in CONFIGS:
            v = all_res["configs"].get(c["name"],{}).get("ppl",{}).get(str(ctx),{})
            p = v.get("ppl")
            row += f" | {'skip':>14}" if p is None else f" | {p:>14.2f}"
        print(row)
    print("\n=== Passkey ===")
    print(f"{'ctx':>8}" + "".join(f" | {c['name']:>14}" for c in CONFIGS))
    for ctx in CTX_LENGTHS:
        row = f"{ctx:>8}"
        for c in CONFIGS:
            v = all_res["configs"].get(c["name"],{}).get("passkey",{}).get(str(ctx),{})
            a = v.get("acc")
            row += f" | {'skip':>14}" if a is None else f" | {a:>14.2f}"
        print(row)

if __name__ == "__main__":
    main()
