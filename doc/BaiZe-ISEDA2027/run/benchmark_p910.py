#!/usr/bin/env python3
"""P-9.10 inference benchmark: hybrid vs dense across contexts x batch.

Uses mamba_ssm.Mamba2 for hybrid SSM layers, transformers for dense model.
Measures: prefill latency, decode tok/s, peak VRAM, state/KV bytes.
"""
import argparse, json, os, sys, time, gc, traceback
import torch
import torch.nn as nn
import torch.nn.functional as F

HYBRID_PATTERN = "M-M-M--M-M*-M-M-M-M--M*-M-M-M-M-M*--M-M-M-M-M*-M--M-M-M-"
N_MAMBA = HYBRID_PATTERN.count("M")  # 24
N_ATTN  = HYBRID_PATTERN.count("*")  # 4
N_MLP   = HYBRID_PATTERN.count("-")  # 28

class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-5):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(dim))
        self.eps = eps
    def forward(self, x):
        return F.rms_norm(x, (self.weight.shape[0],), self.weight, self.eps)

class AttentionLayer(nn.Module):
    """GQA attention without RoPE (matching mcore hybrid)."""
    def __init__(self, hidden=2048, n_heads=16, n_kv=4, head_dim=128):
        super().__init__()
        self.n_heads = n_heads
        self.n_kv = n_kv
        self.head_dim = head_dim
        self.q_proj = nn.Linear(hidden, n_heads * head_dim, bias=False)
        self.k_proj = nn.Linear(hidden, n_kv * head_dim, bias=False)
        self.v_proj = nn.Linear(hidden, n_kv * head_dim, bias=False)
        self.o_proj = nn.Linear(n_heads * head_dim, hidden, bias=False)
        self.kv_cache = None
    def forward(self, x, use_cache=False):
        B, S, D = x.shape
        q = self.q_proj(x).view(B, S, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, S, self.n_kv, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, S, self.n_kv, self.head_dim).transpose(1, 2)
        if use_cache:
            if self.kv_cache is None:
                self.kv_cache = (k, v)
            else:
                self.kv_cache = (
                    torch.cat([self.kv_cache[0], k], dim=2),
                    torch.cat([self.kv_cache[1], v], dim=2),
                )
            k_full, v_full = self.kv_cache
            is_causal = (S == k_full.shape[2])
        else:
            k_full, v_full = k, v
            is_causal = True
        if self.n_heads != self.n_kv:
            rep = self.n_heads // self.n_kv
            k_full = k_full.repeat_interleave(rep, dim=1)
            v_full = v_full.repeat_interleave(rep, dim=1)
        out = F.scaled_dot_product_attention(q, k_full, v_full, is_causal=is_causal)
        out = out.transpose(1, 2).contiguous().view(B, S, -1)
        return self.o_proj(out)
    def reset_cache(self):
        self.kv_cache = None

class MLPLayer(nn.Module):
    """Non-gated MLP with GELU activation."""
    def __init__(self, hidden=2048, inter=8192):
        super().__init__()
        self.up_proj = nn.Linear(hidden, inter, bias=False)
        self.down_proj = nn.Linear(inter, hidden, bias=False)
    def forward(self, x, **kw):
        return self.down_proj(F.gelu(self.up_proj(x)))

class HybridLayer(nn.Module):
    """Wrapper for a single hybrid layer (Mamba/Attention/MLP + norm)."""
    def __init__(self, layer_type, mixer, norm):
        super().__init__()
        self.layer_type = layer_type
        self.mixer = mixer
        self.norm = norm
    def forward(self, h, inference_params=None, use_cache=False):
        h_normed = self.norm(h)
        if self.layer_type == "M":
            out = self.mixer(h_normed, inference_params=inference_params)
        elif self.layer_type == "*":
            out = self.mixer(h_normed, use_cache=use_cache)
        else:
            out = self.mixer(h_normed)
        return h + out

class HybridModel(nn.Module):
    def __init__(self, ckpt_dir, device="cuda", dtype=torch.bfloat16):
        super().__init__()
        from mamba_ssm import Mamba2
        from safetensors.torch import load_file
        self.device = device
        self.dtype = dtype
        self.n_layers = 56
        self.hidden = 2048
        self.n_mamba = N_MAMBA
        self.n_attn = N_ATTN
        
        # Load weights
        print(f"Loading weights from {ckpt_dir}/model.safetensors ...")
        sd = load_file(os.path.join(ckpt_dir, "model.safetensors"))
        
        # Embedding + final norm + LM head
        self.embeddings = nn.Embedding(129408, 2048)
        self.embeddings.weight.data = sd["backbone.embeddings.weight"].to(dtype).to(device)
        self.norm_f = RMSNorm(2048, eps=1e-5)
        self.norm_f.weight.data = sd["backbone.norm_f.weight"].to(dtype).to(device)
        self.lm_head = nn.Linear(2048, 129408, bias=False)
        self.lm_head.weight.data = sd["lm_head.weight"].to(dtype).to(device)
        
        # Build layers
        self.layers = nn.ModuleList()
        mamba_layer_idx = 0
        for i in range(self.n_layers):
            lt = HYBRID_PATTERN[i]
            p = f"backbone.layers.{i}"
            if lt == "M":
                mamba = Mamba2(
                    d_model=2048, d_state=128, d_conv=4, expand=2,
                    headdim=64, ngroups=8, chunk_size=256,
                    rmsnorm=True, conv_bias=True, bias=False,
                    layer_idx=mamba_layer_idx,
                    device=device, dtype=dtype,
                )
                mamba_layer_idx += 1
                msd = mamba.state_dict()
                msd["A_log"].copy_(sd[f"{p}.mixer.A_log"].to(dtype).to(device))
                msd["D"].copy_(sd[f"{p}.mixer.D"].to(device))
                msd["dt_bias"].copy_(sd[f"{p}.mixer.dt_bias"].to(dtype).to(device))
                msd["in_proj.weight"].copy_(sd[f"{p}.mixer.in_proj.weight"].to(dtype).to(device))
                msd["conv1d.weight"].copy_(sd[f"{p}.mixer.conv1d.weight"].to(dtype).to(device))
                msd["conv1d.bias"].copy_(sd[f"{p}.mixer.conv1d.bias"].to(dtype).to(device))
                msd["norm.weight"].copy_(sd[f"{p}.mixer.norm.weight"].to(dtype).to(device))
                msd["out_proj.weight"].copy_(sd[f"{p}.mixer.out_proj.weight"].to(dtype).to(device))
                mamba.load_state_dict(msd)
                norm = RMSNorm(2048, eps=1e-5)
                norm.weight.data = sd[f"{p}.norm.weight"].to(dtype).to(device)
                self.layers.append(HybridLayer("M", mamba, norm))
            elif lt == "*":
                attn = AttentionLayer(2048, 16, 4, 128)
                attn.q_proj.weight.data = sd[f"{p}.mixer.q_proj.weight"].to(dtype).to(device)
                attn.k_proj.weight.data = sd[f"{p}.mixer.k_proj.weight"].to(dtype).to(device)
                attn.v_proj.weight.data = sd[f"{p}.mixer.v_proj.weight"].to(dtype).to(device)
                attn.o_proj.weight.data = sd[f"{p}.mixer.o_proj.weight"].to(dtype).to(device)
                norm = RMSNorm(2048, eps=1e-5)
                norm.weight.data = sd[f"{p}.norm.weight"].to(dtype).to(device)
                self.layers.append(HybridLayer("*", attn, norm))
            elif lt == "-":
                mlp = MLPLayer(2048, 8192)
                mlp.up_proj.weight.data = sd[f"{p}.mixer.up_proj.weight"].to(dtype).to(device)
                mlp.down_proj.weight.data = sd[f"{p}.mixer.down_proj.weight"].to(dtype).to(device)
                norm = RMSNorm(2048, eps=1e-5)
                norm.weight.data = sd[f"{p}.norm.weight"].to(dtype).to(device)
                self.layers.append(HybridLayer("-", mlp, norm))
        print(f"Loaded hybrid model: {sum(p.numel() for p in self.parameters())/1e9:.2f}B params")
    
    def forward(self, input_ids, inference_params=None, use_cache=False, compute_logits=True):
        h = self.embeddings(input_ids)
        for layer in self.layers:
            h = layer(h, inference_params=inference_params, use_cache=use_cache)
        h = self.norm_f(h)
        if compute_logits:
            return self.lm_head(h[:, -1:])
        return h
    
    def reset_kv_caches(self):
        for layer in self.layers:
            if layer.layer_type == "*":
                layer.mixer.reset_cache()

def benchmark_hybrid(ckpt_dir, contexts, batches, device="cuda:0", decode_tokens=32):
    """Benchmark hybrid model: prefill latency, decode tok/s, VRAM."""
    from mamba_ssm.utils.generation import InferenceParams
    results = []
    torch.cuda.set_device(device)
    model = HybridModel(ckpt_dir, device=device, dtype=torch.bfloat16)
    model.eval()
    # Max context for decode (larger contexts risk CUDA errors with inference_params)
    max_decode_ctx = 16384
    
    for ctx in contexts:
        for bs in batches:
            print(f"\n--- Hybrid: ctx={ctx}, batch={bs} ---", flush=True)
            input_ids = torch.randint(1, 129408, (bs, ctx), device=device)
            try:
                # Warmup (no inference_params, no cache)
                with torch.no_grad():
                    _ = model(input_ids[:, :min(256, ctx)], compute_logits=False)
                torch.cuda.synchronize()
                gc.collect(); torch.cuda.empty_cache()
                
                # === PREFILL benchmark (no inference_params, no cache) ===
                # Split into sub-batches if total tokens too large (Mamba2 kernel limit)
                max_prefill_tokens = 262144  # 256K tokens per sub-batch
                sub_bs = bs
                if bs * ctx > max_prefill_tokens:
                    sub_bs = max(1, max_prefill_tokens // ctx)
                    n_sub = (bs + sub_bs - 1) // sub_bs
                    print(f"  (splitting batch={bs} into {n_sub}x sub_bs={sub_bs})", flush=True)
                
                torch.cuda.reset_peak_memory_stats(device)
                torch.cuda.synchronize()
                t0 = time.perf_counter()
                with torch.no_grad():
                    if sub_bs >= bs:
                        logits = model(input_ids, compute_logits=True)
                    else:
                        logits_parts = []
                        for i in range(0, bs, sub_bs):
                            chunk = input_ids[i:i+sub_bs]
                            logits_parts.append(model(chunk, compute_logits=True))
                        logits = torch.cat(logits_parts, dim=0)
                        del logits_parts
                torch.cuda.synchronize()
                t1 = time.perf_counter()
                
                prefill_time = t1 - t0
                prefill_tok_s = (bs * ctx) / prefill_time
                peak_vram = torch.cuda.max_memory_allocated(device) / 1e9
                
                # === DECODE benchmark (only for small contexts) ===
                decode_tok_s = None
                tpot_ms = None
                if ctx <= max_decode_ctx:
                    # Need to re-prefill with inference_params to set up SSM state
                    model.reset_kv_caches()
                    inf_params = InferenceParams(max_seqlen=ctx + decode_tokens + 10, max_batch_size=bs)
                    with torch.no_grad():
                        logits_dec = model(input_ids, inference_params=inf_params, use_cache=True)
                    next_tok = logits_dec[:, -1, :].argmax(dim=-1, keepdim=True)
                    torch.cuda.synchronize()
                    t0 = time.perf_counter()
                    with torch.no_grad():
                        for _ in range(decode_tokens):
                            next_tok = model(next_tok, inference_params=inf_params, use_cache=True)[:, -1, :].argmax(dim=-1, keepdim=True)
                    torch.cuda.synchronize()
                    t1 = time.perf_counter()
                    decode_time = t1 - t0
                    decode_tok_s = round((bs * decode_tokens) / decode_time, 1)
                    tpot_ms = round((decode_time / (bs * decode_tokens)) * 1000, 2)
                    del logits_dec, next_tok, inf_params
                    model.reset_kv_caches()
                
                # State/KV bytes (analytical)
                mamba_state_bytes = N_MAMBA * 4096 * 128 * 4 * bs
                mamba_conv_bytes = N_MAMBA * 4096 * 4 * 2 * bs
                attn_kv_bytes = N_ATTN * 2 * 4 * 128 * ctx * 2 * bs
                
                r = {
                    "model": "hybrid", "ctx": ctx, "batch": bs,
                    "prefill_s": round(prefill_time, 4),
                    "prefill_tok_s": round(prefill_tok_s, 1),
                    "decode_tok_s": decode_tok_s,
                    "tpot_ms": tpot_ms,
                    "peak_vram_gb": round(peak_vram, 2),
                    "mamba_state_mb": round((mamba_state_bytes + mamba_conv_bytes) / 1e6, 2),
                    "attn_kv_mb": round(attn_kv_bytes / 1e6, 2),
                    "total_state_mb": round((mamba_state_bytes + mamba_conv_bytes + attn_kv_bytes) / 1e6, 2),
                }
                results.append(r)
                print(f"  prefill: {prefill_time:.3f}s ({prefill_tok_s:.0f} tok/s)", flush=True)
                if decode_tok_s is not None:
                    print(f"  decode:  {decode_tok_s} tok/s (TPOT={tpot_ms}ms)", flush=True)
                else:
                    print(f"  decode:  skipped (ctx > {max_decode_ctx})", flush=True)
                print(f"  peak VRAM: {peak_vram:.2f} GB", flush=True)
                print(f"  state: mamba={r['mamba_state_mb']:.1f}MB attn_kv={r['attn_kv_mb']:.1f}MB total={r['total_state_mb']:.1f}MB", flush=True)
                
                # Incremental save
                with open("/tmp/bench_p910_hybrid_partial.json", "w") as f:
                    json.dump(results, f, indent=2)
                
                del logits, input_ids
                gc.collect(); torch.cuda.empty_cache()
            except torch.cuda.OutOfMemoryError as e:
                print(f"  OOM: {str(e)[:200]}", flush=True)
                r = {"model": "hybrid", "ctx": ctx, "batch": bs, "error": "OOM"}
                results.append(r)
                gc.collect(); torch.cuda.empty_cache()
    return results

def benchmark_dense(ckpt_dir, contexts, batches, device="cuda:0", decode_tokens=32):
    """Benchmark dense model using transformers."""
    from transformers import AutoModelForCausalLM
    results = []
    torch.cuda.set_device(device)
    print(f"Loading dense model from {ckpt_dir} ...", flush=True)
    model = AutoModelForCausalLM.from_pretrained(
        ckpt_dir, dtype=torch.bfloat16, device_map=device,
        attn_implementation="sdpa",
    )
    model.eval()
    n_layers = 42
    n_kv = 2
    head_dim = 128
    max_decode_ctx = 16384
    
    for ctx in contexts:
        for bs in batches:
            print(f"\n--- Dense: ctx={ctx}, batch={bs} ---", flush=True)
            input_ids = torch.randint(1, 129408, (bs, ctx), device=device)
            try:
                with torch.no_grad():
                    _ = model(input_ids[:, :min(256, ctx)])
                torch.cuda.synchronize()
                torch.cuda.empty_cache()
                
                # === PREFILL (no cache, last-token logits to save VRAM) ===
                max_prefill_tokens = 262144
                sub_bs = bs
                if bs * ctx > max_prefill_tokens:
                    sub_bs = max(1, max_prefill_tokens // ctx)
                    print(f"  (splitting batch={bs} into sub_bs={sub_bs})", flush=True)
                
                torch.cuda.reset_peak_memory_stats(device)
                torch.cuda.synchronize()
                t0 = time.perf_counter()
                with torch.no_grad():
                    if sub_bs >= bs:
                        out = model(input_ids, use_cache=False, logits_to_keep=1)
                    else:
                        for i in range(0, bs, sub_bs):
                            chunk = input_ids[i:i+sub_bs]
                            _ = model(chunk, use_cache=False, logits_to_keep=1)
                torch.cuda.synchronize()
                t1 = time.perf_counter()
                prefill_time = t1 - t0
                prefill_tok_s = (bs * ctx) / prefill_time
                peak_vram = torch.cuda.max_memory_allocated(device) / 1e9
                
                # === DECODE (only for small contexts) ===
                decode_tok_s = None
                tpot_ms = None
                if ctx <= max_decode_ctx:
                    # Re-prefill with cache for decode (avoid full logits)
                    with torch.no_grad():
                        out = model(input_ids, use_cache=True, logits_to_keep=1)
                    past_kv = out.past_key_values
                    next_tok = out.logits[:, -1, :].argmax(dim=-1, keepdim=True)
                    torch.cuda.synchronize()
                    t0 = time.perf_counter()
                    with torch.no_grad():
                        for _ in range(decode_tokens):
                            out = model(next_tok, past_key_values=past_kv, use_cache=True)
                            past_kv = out.past_key_values
                            next_tok = out.logits[:, -1, :].argmax(dim=-1, keepdim=True)
                    torch.cuda.synchronize()
                    t1 = time.perf_counter()
                    decode_time = t1 - t0
                    decode_tok_s = round((bs * decode_tokens) / decode_time, 1)
                    tpot_ms = round((decode_time / (bs * decode_tokens)) * 1000, 2)
                    del out, past_kv, next_tok
                
                kv_bytes = n_layers * 2 * n_kv * head_dim * ctx * 2 * bs
                r = {
                    "model": "dense", "ctx": ctx, "batch": bs,
                    "prefill_s": round(prefill_time, 4),
                    "prefill_tok_s": round(prefill_tok_s, 1),
                    "decode_tok_s": decode_tok_s,
                    "tpot_ms": tpot_ms,
                    "peak_vram_gb": round(peak_vram, 2),
                    "kv_cache_mb": round(kv_bytes / 1e6, 2),
                }
                results.append(r)
                print(f"  prefill: {prefill_time:.3f}s ({prefill_tok_s:.0f} tok/s)", flush=True)
                if decode_tok_s is not None:
                    print(f"  decode:  {decode_tok_s} tok/s (TPOT={tpot_ms}ms)", flush=True)
                else:
                    print(f"  decode:  skipped (ctx > {max_decode_ctx})", flush=True)
                print(f"  peak VRAM: {peak_vram:.2f} GB", flush=True)
                print(f"  KV cache: {kv_bytes/1e6:.1f} MB", flush=True)
                
                # Incremental save
                with open("/tmp/bench_p910_dense_partial.json", "w") as f:
                    json.dump(results, f, indent=2)
                
                del input_ids
                gc.collect(); torch.cuda.empty_cache()
            except torch.cuda.OutOfMemoryError as e:
                print(f"  OOM: {str(e)[:200]}", flush=True)
                r = {"model": "dense", "ctx": ctx, "batch": bs, "error": "OOM"}
                results.append(r)
                gc.collect(); torch.cuda.empty_cache()
    return results

def main():
    parser = argparse.ArgumentParser(description="P-9.10 inference benchmark")
    parser.add_argument("--model", choices=["hybrid", "dense", "both"], default="both")
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--contexts", nargs="+", type=int, default=[4096, 16384, 65536, 131072])
    parser.add_argument("--batches", nargs="+", type=int, default=[1, 8])
    parser.add_argument("--decode_tokens", type=int, default=32)
    parser.add_argument("--output", default="benchmark_p910_results.json")
    args = parser.parse_args()
    
    base = os.path.dirname(os.path.abspath(__file__))
    all_results = []
    
    if args.model in ("hybrid", "both"):
        hybrid_dir = os.path.join(base, "hf_checkpoints", "p3_hybrid")
        all_results.extend(benchmark_hybrid(hybrid_dir, args.contexts, args.batches, args.device, args.decode_tokens))
        gc.collect(); torch.cuda.empty_cache()
    if args.model in ("dense", "both"):
        gc.collect(); torch.cuda.empty_cache()
        dense_dir = os.path.join(base, "hf_checkpoints", "p3_dense")
        all_results.extend(benchmark_dense(dense_dir, args.contexts, args.batches, args.device, args.decode_tokens))
    
    with open(args.output, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n=== Results saved to {args.output} ===")
    for r in all_results:
        print(json.dumps(r))

if __name__ == "__main__":
    main()
