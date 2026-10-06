#!/usr/bin/env python3
# Copyright (c) 2026, BaiZe data mixture optimization.
#
# Proxy model (d=128/L=14, ~18.5M) mcore distcp checkpoint -> HF Nemotron-H.
# Based on baize_p6_ckpt_to_hf.py but with proxy architecture constants
# and tie_word_embeddings=True.
#
# Usage:
#   MASTER_ADDR=127.0.0.1 PYTHONPATH=/nas_train/app.e0031982/omegaconf_230 \
#   python baize_proxy_ckpt_to_hf.py \
#       --ckpt <iter_XXXXXXX> --tokenizer <tokenizer_eod> --out <hf_nemotron_h>
import argparse
import json
import os
import shutil

os.environ.setdefault("MASTER_ADDR", "127.0.0.1")
os.environ.setdefault("MASTER_PORT", "29502")

import torch  # noqa: E402
from safetensors.torch import save_file  # noqa: E402

# -- Architecture constants (mamba2_hybrid_proxy_d128/provider.py) --
HIDDEN_SIZE = 128
INTERMEDIATE_SIZE = 512
NUM_LAYERS = 14
NUM_ATTENTION_HEADS = 1
NUM_KV_HEADS = 1
HEAD_DIM = HIDDEN_SIZE // NUM_ATTENTION_HEADS
MAMBA_NUM_HEADS = 4
MAMBA_HEAD_DIM = 64
SSM_STATE_SIZE = 128
N_GROUPS = 1
EXPAND = 2
CONV_KERNEL = 4
VOCAB_SIZE = 129408
MAX_POS_EMBED = 2048
TIE_WORD_EMBEDDINGS = True
HYBRID_PATTERN = "M-M-M--M-M*-M-"


def build_config_json() -> dict:
    mapping = {"M": "linear_attention", "*": "full_attention", "-": "mlp"}
    layers_block_type = [mapping[c] for c in HYBRID_PATTERN]
    assert len(layers_block_type) == NUM_LAYERS
    return {
        "model_type": "nemotron_h",
        "architectures": ["NemotronHForCausalLM"],
        "vocab_size": VOCAB_SIZE,
        "hidden_size": HIDDEN_SIZE,
        "intermediate_size": INTERMEDIATE_SIZE,
        "layers_block_type": layers_block_type,
        "num_attention_heads": NUM_ATTENTION_HEADS,
        "num_key_value_heads": NUM_KV_HEADS,
        "head_dim": HEAD_DIM,
        "max_position_embeddings": MAX_POS_EMBED,
        "attention_bias": False,
        "mlp_bias": False,
        "tie_word_embeddings": TIE_WORD_EMBEDDINGS,
        "ssm_state_size": SSM_STATE_SIZE,
        "mamba_num_heads": MAMBA_NUM_HEADS,
        "mamba_head_dim": MAMBA_HEAD_DIM,
        "n_groups": N_GROUPS,
        "expand": EXPAND,
        "conv_kernel": CONV_KERNEL,
        "use_conv_bias": True,
        "mamba_proj_bias": False,
        "time_step_min": 0.001,
        "time_step_max": 0.1,
        "time_step_floor": 1e-4,
        "mlp_hidden_act": "gelu",
        "mamba_hidden_act": "silu",
        "chunk_size": 256,
        "layer_norm_epsilon": 1e-5,
        "rescale_prenorm_residual": False,
        "torch_dtype": "bfloat16",
        "bos_token_id": 1,
        "eos_token_id": 2,
        "pad_token_id": 0,
        "use_cache": True,
    }


def convert(sd: dict) -> dict:
    """mcore state_dict -> HF Nemotron-H state_dict (weight name mapping)."""
    hf = {}
    mcore = "decoder"
    hf_pre = "model"

    def put(name, val):
        hf[f"{hf_pre}.{name}"] = val

    emb = sd["embedding.word_embeddings.weight"]
    put("embeddings.weight", emb)
    put("norm_f.weight", sd[f"{mcore}.final_norm.weight"])
    # tie_word_embeddings=True: save lm_head as copy of embedding (HF ties after load)
    hf["lm_head.weight"] = emb.clone()

    for i, btype in enumerate(HYBRID_PATTERN):
        mcore_l = f"{mcore}.layers.{i}"
        hfp = f"layers.{i}"
        if btype == "M":
            m = f"{mcore_l}.mixer"
            put(f"{hfp}.norm.weight", sd[f"{m}.in_proj.layer_norm_weight"])
            in_proj = torch.cat([
                sd[f"{m}.in_proj.weight.z"],
                sd[f"{m}.in_proj.weight.x"],
                sd[f"{m}.in_proj.weight.B"],
                sd[f"{m}.in_proj.weight.C"],
                sd[f"{m}.in_proj.weight.dt"],
            ], dim=0)
            put(f"{hfp}.mixer.in_proj.weight", in_proj)
            conv_w = torch.cat([
                sd[f"{m}.conv1d.weight.x"],
                sd[f"{m}.conv1d.weight.B"],
                sd[f"{m}.conv1d.weight.C"],
            ], dim=0)
            conv_b = torch.cat([
                sd[f"{m}.conv1d.bias.x"],
                sd[f"{m}.conv1d.bias.B"],
                sd[f"{m}.conv1d.bias.C"],
            ], dim=0)
            put(f"{hfp}.mixer.conv1d.weight", conv_w)
            put(f"{hfp}.mixer.conv1d.bias", conv_b)
            put(f"{hfp}.mixer.A_log", sd[f"{m}.A_log"].float())
            put(f"{hfp}.mixer.D", sd[f"{m}.D"].float())
            put(f"{hfp}.mixer.dt_bias", sd[f"{m}.dt_bias"].float())
            put(f"{hfp}.mixer.norm.weight", sd[f"{m}.norm.weight"])
            put(f"{hfp}.mixer.out_proj.weight", sd[f"{m}.out_proj.weight"])
        elif btype == "*":
            a = f"{mcore_l}.self_attention"
            put(f"{hfp}.norm.weight", sd[f"{a}.linear_qkv.layer_norm_weight"])
            qkv = sd[f"{a}.linear_qkv.weight"]
            sizes = [HIDDEN_SIZE, NUM_KV_HEADS * HEAD_DIM, NUM_KV_HEADS * HEAD_DIM]
            q, k, v = qkv.split(sizes, dim=0)
            put(f"{hfp}.mixer.q_proj.weight", q)
            put(f"{hfp}.mixer.k_proj.weight", k)
            put(f"{hfp}.mixer.v_proj.weight", v)
            put(f"{hfp}.mixer.o_proj.weight", sd[f"{a}.linear_proj.weight"])
        elif btype == "-":
            mlp = f"{mcore_l}.mlp"
            put(f"{hfp}.norm.weight", sd[f"{mlp}.linear_fc1.layer_norm_weight"])
            put(f"{hfp}.mixer.up_proj.weight", sd[f"{mlp}.linear_fc1.weight"])
            put(f"{hfp}.mixer.down_proj.weight", sd[f"{mlp}.linear_fc2.weight"])
        else:
            raise ValueError("unexpected pattern char " + btype)
    return hf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--tokenizer", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if not torch.distributed.is_initialized():
        torch.distributed.init_process_group(backend="gloo", rank=0, world_size=1)

    from megatron.core.dist_checkpointing.serialization import load_plain_tensors

    sd = load_plain_tensors(args.ckpt)
    n_param = sum(v.numel() for v in sd.values() if hasattr(v, "numel"))
    print(f"[load] {len(sd)} keys, {n_param/1e6:.3f}M params")

    hf = convert(sd)
    print(f"[map] {len(hf)} HF keys")

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "config.json"), "w") as f:
        json.dump(build_config_json(), f, indent=2)
    save_file({k: v.to(torch.bfloat16) for k, v in hf.items()},
              os.path.join(args.out, "model.safetensors"))
    for fn in ("tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"):
        src = os.path.join(args.tokenizer, fn)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(args.out, fn))
    print(f"[done] wrote HF model to {args.out}")


if __name__ == "__main__":
    main()
