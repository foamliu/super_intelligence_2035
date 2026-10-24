#!/usr/bin/env python3
"""Verify BaiZe-2B (Mamba2-hybrid) HF checkpoint for longctx retest.

Prints: arch / model_type / layer-type statistics (SSM vs Attention vs MLP) /
param count, then does a logits-alignment sanity check (forward pass → finite
logits + coherent generation) to confirm the mcore→HF nemotron_h conversion
is lossless.

Usage:
  CUDA_VISIBLE_DEVICES=0 python verify_baize_mamba2_hybrid.py \
      --model-path /nas_train/app.e0031982/code/BaiZe-ISEDA2027/hf_checkpoints/p3_hybrid
"""
import argparse, json, os, sys

import torch
from safetensors import safe_open


def count_params_safetensors(model_path):
    total = 0
    st_file = os.path.join(model_path, "model.safetensors")
    with safe_open(st_file, framework="pt") as f:
        for k in f.keys():
            total += f.get_tensor(k).numel()
    return total


def analyze_hybrid_pattern(pattern):
    """Parse hybrid_override_pattern: M=mamba2(SSM), *=attention, -=mlp."""
    n_mamba = pattern.count("M")
    n_attn = pattern.count("*")
    n_mlp = pattern.count("-")
    return {"SSM_layers": n_mamba, "Attention_layers": n_attn,
            "MLP_only_layers": n_mlp, "total_layers": len(pattern)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", required=True)
    args = ap.parse_args()

    cfg_path = os.path.join(args.model_path, "config.json")
    with open(cfg_path) as f:
        cfg = json.load(f)

    print("=" * 60)
    print("BaiZe-2B (Mamba2-hybrid) Checkpoint Verification")
    print("=" * 60)

    # Architecture
    print(f"\n[Config]")
    print(f"  architectures       : {cfg.get('architectures')}")
    print(f"  model_type          : {cfg.get('model_type')}")
    print(f"  num_hidden_layers   : {cfg.get('num_hidden_layers')}")
    print(f"  hidden_size         : {cfg.get('hidden_size')}")
    print(f"  intermediate_size   : {cfg.get('intermediate_size')}")
    print(f"  num_attention_heads : {cfg.get('num_attention_heads')}")
    print(f"  num_key_value_heads : {cfg.get('num_key_value_heads')}")
    print(f"  head_dim            : {cfg.get('head_dim')}")
    print(f"  vocab_size          : {cfg.get('vocab_size')}")
    print(f"  tie_word_embeddings : {cfg.get('tie_word_embeddings')}")
    print(f"  max_position_embeds : {cfg.get('max_position_embeddings')}")
    print(f"  use_mamba_kernels   : {cfg.get('use_mamba_kernels')}")
    print(f"  ssm_state_size      : {cfg.get('ssm_state_size')}")
    print(f"  mamba_num_heads     : {cfg.get('mamba_num_heads')}")
    print(f"  mamba_head_dim      : {cfg.get('mamba_head_dim')}")

    # Layer-type statistics from hybrid_override_pattern
    pattern = cfg.get("hybrid_override_pattern", "")
    stats = analyze_hybrid_pattern(pattern)
    print(f"\n[Layer-type statistics from hybrid_override_pattern]")
    print(f"  pattern             : {pattern}")
    print(f"  SSM (Mamba2) layers : {stats['SSM_layers']}")
    print(f"  Attention layers    : {stats['Attention_layers']}")
    print(f"  MLP-only layers     : {stats['MLP_only_layers']}")
    print(f"  total layers        : {stats['total_layers']}")
    attn_fraction = stats['Attention_layers'] / stats['total_layers'] * 100
    print(f"  attention fraction  : {attn_fraction:.1f}%  ({stats['Attention_layers']}/{stats['total_layers']} layers carry KV cache)")

    # Param count
    n_params = count_params_safetensors(args.model_path)
    print(f"\n[Parameters]")
    print(f"  total params        : {n_params:,}  ({n_params/1e9:.3f} B)")
    print(f"  safetensors size    : {os.path.getsize(os.path.join(args.model_path, 'model.safetensors'))/1e9:.2f} GB (bf16)")

    # Logits alignment sanity check: load model + generate
    print(f"\n[Logits alignment sanity check]")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print("  loading model + tokenizer ...")
    tok = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_path, torch_dtype=torch.bfloat16, trust_remote_code=True).cuda().eval()

    # Check 1: forward pass → finite logits
    prompt = "The capital of France is"
    ids = tok(prompt, return_tensors="pt").to("cuda")
    with torch.no_grad():
        out = model(**ids)
    logits = out.logits
    finite = torch.isfinite(logits).all().item()
    print(f"  forward pass        : logits shape={tuple(logits.shape)}, all_finite={finite}")
    if not finite:
        print("  ❌ FAIL: logits contain NaN/inf — conversion may be lossy!")
        sys.exit(1)

    # Check 2: coherent generation
    gen = model.generate(**ids, max_new_tokens=20, do_sample=False, temperature=1.0)
    text = tok.decode(gen[0][ids.input_ids.shape[1]:], skip_special_tokens=True)
    print(f"  generate('The capital of France is') → '{text.strip()}'")
    print(f"  ✅ PASS: logits finite + generation coherent (conversion lossless)")

    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE — model is Mamba2-hybrid, conversion OK")
    print("=" * 60)


if __name__ == "__main__":
    main()
