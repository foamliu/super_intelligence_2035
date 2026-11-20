#!/usr/bin/env python3
"""Create a parameter-matched Dense Llama (36L, 2.229B) with random init weights.

This model is for speed/VRAM benchmarking only — weights are random (std=0.02).
Architecture matches p3_dense (MiniCPM5-2B 42L) but with 36 layers to hit ~2.220B params.

Output: hf_checkpoints/dense_matched_2.22b/
"""
import json, os, shutil, sys

def create_config():
    return {
        "architectures": ["LlamaForCausalLM"],
        "model_type": "llama",
        "vocab_size": 129408, "hidden_size": 2048,
        "intermediate_size": 6144, "num_hidden_layers": 36,
        "num_attention_heads": 16, "num_key_value_heads": 2,
        "head_dim": 128, "hidden_act": "silu",
        "max_position_embeddings": 4096, "rms_norm_eps": 1e-06,
        "attention_bias": False, "mlp_bias": False,
        "tie_word_embeddings": False, "torch_dtype": "bfloat16",
        "bos_token_id": 1, "eos_token_id": 2, "pad_token_id": 0,
        "use_cache": True, "rope_theta": 10000.0, "initializer_range": 0.02,
    }

def count_params(config):
    V,H,I = config["vocab_size"],config["hidden_size"],config["intermediate_size"]
    L,nh,nkv,hd = config["num_hidden_layers"],config["num_attention_heads"],config["num_key_value_heads"],config["head_dim"]
    tie = config["tie_word_embeddings"]
    embed = V*H; lm_head = 0 if tie else V*H
    q = nh*hd*H; k = nkv*hd*H; v = nkv*hd*H; o = nh*hd*H
    attn = q+k+v+o; mlp = 3*H*I; norms = 2*H
    per_layer = attn+mlp+norms; final_norm = H
    total = embed+lm_head+L*per_layer+final_norm
    return total

def main():
    import torch
    from safetensors.torch import save_file
    config = create_config()
    total = count_params(config)
    target = 2_220_268_032
    diff_pct = abs(total-target)/target*100
    print(f"=== Dense Llama 36L (param-matched) ===")
    print(f"  TOTAL params: {total:,}")
    print(f"  vs hybrid 2,220,268,032: {total/target*100-100:+.3f}%")
    assert diff_pct < 1.0, f"Param mismatch: {diff_pct:.3f}% > 1%"
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hf_checkpoints", "dense_matched_2.22b")
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "config.json"), "w") as f:
        json.dump(config, f, indent=2)
    print(f"[1/3] config.json written")
    src_tok = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p3_dense/hf_iter_5000"
    for fname in ["tokenizer.json","tokenizer_config.json","special_tokens_map.json"]:
        src = os.path.join(src_tok, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(output_dir, fname))
            print(f"[2/3] Copied {fname}")
    print(f"[3/3] Generating random weights (std=0.02, bf16)...")
    dtype = torch.bfloat16; std = 0.02
    H,I,V,L = 2048,6144,129408,36
    nh,nkv,hd = 16,2,128
    sd = {}
    sd["model.embed_tokens.weight"] = torch.randn(V,H,dtype=dtype)*std
    for i in range(L):
        p = f"model.layers.{i}."
        sd[p+"self_attn.q_proj.weight"] = torch.randn(nh*hd,H,dtype=dtype)*std
        sd[p+"self_attn.k_proj.weight"] = torch.randn(nkv*hd,H,dtype=dtype)*std
        sd[p+"self_attn.v_proj.weight"] = torch.randn(nkv*hd,H,dtype=dtype)*std
        sd[p+"self_attn.o_proj.weight"] = torch.randn(H,nh*hd,dtype=dtype)*std
        sd[p+"mlp.gate_proj.weight"] = torch.randn(I,H,dtype=dtype)*std
        sd[p+"mlp.up_proj.weight"] = torch.randn(I,H,dtype=dtype)*std
        sd[p+"mlp.down_proj.weight"] = torch.randn(H,I,dtype=dtype)*std
        sd[p+"input_layernorm.weight"] = torch.ones(H,dtype=dtype)
        sd[p+"post_attention_layernorm.weight"] = torch.ones(H,dtype=dtype)
    sd["model.norm.weight"] = torch.ones(H,dtype=dtype)
    sd["lm_head.weight"] = torch.randn(V,H,dtype=dtype)*std
    save_path = os.path.join(output_dir, "model.safetensors")
    save_file(sd, save_path, metadata={"format": "pt"})
    tp = sum(t.numel() for t in sd.values())
    print(f"  Saved {len(sd)} tensors, {tp:,} params to {save_path}")
    assert tp == total, f"Mismatch: {tp} != {total}"
    print(f"  File size: {os.path.getsize(save_path)/1e9:.2f} GB")
    print(f"  Output: {output_dir}")
    print(f"\n✅ Dense Llama 36L (2.229B, random init) created.")

if __name__ == "__main__":
    main()
