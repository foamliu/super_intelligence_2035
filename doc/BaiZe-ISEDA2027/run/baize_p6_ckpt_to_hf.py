#!/usr/bin/env python3
# Copyright (c) 2026, BaiZe Stage(i) LLM pretrain.
#
# P-6 第 1 步：把 s5_01 20000 步 mcore "torch_dist" checkpoint 转换为
# HF Nemotron-H（model_type="nemotron_h"）格式，供 SGLang 起服 + lm_eval 零样本评测。
#
# 用法：
#   PYTHONPATH=/nas_train/app.e0031982/omegaconf_230 python baize_p6_ckpt_to_hf.py \
#       --ckpt <iter_XXXXXXX> --tokenizer <tokenizer_eod> --out <hf_nemotron_h>
import argparse
import json
import os
import shutil

os.environ.setdefault("MASTER_ADDR", "127.0.0.1")
os.environ.setdefault("MASTER_PORT", "29502")

import torch  # noqa: E402
from safetensors.torch import save_file  # noqa: E402

# ── 架构常量（与 mamba2_hybrid_2b/provider.py + s5_01/run_config.yaml 完全一致）────
HIDDEN_SIZE = 2048
INTERMEDIATE_SIZE = 8192          # ffn_hidden_size
NUM_LAYERS = 56
NUM_ATTENTION_HEADS = 16
NUM_KV_HEADS = 4                  # num_query_groups
HEAD_DIM = HIDDEN_SIZE // NUM_ATTENTION_HEADS          # 128
MAMBA_NUM_HEADS = 64              # d_inner/headdim = 4096/64
MAMBA_HEAD_DIM = 64
SSM_STATE_SIZE = 128              # d_state = mamba_state_dim
N_GROUPS = 8                      # mamba_num_groups
EXPAND = 2
CONV_KERNEL = 4
VOCAB_SIZE = 129408               # 129281 pad 到 make_vocab_size_divisible_by=128
MAX_POSITION_EMBEDDINGS = 4096

# 56 层 hybrid pattern：M=mamba2 / *=attention / -=mlp（provider._HYBRID_OVERRIDE_PATTERN 一致）
HYBRID_PATTERN = "M-M-M--M-M*-M-M-M-M--M*-M-M-M-M-M*--M-M-M-M-M*-M--M-M-M-"


def build_config_json() -> dict:
    """SGLang/transformers NemotronHConfig 的 config.json。

    SGLang 新版以 layers_block_type（list）为规范写法，同时兼容 hybrid_override_pattern。
    """
    mapping = {"M": "mamba", "*": "attention", "-": "mlp"}
    layers_block_type = [mapping[c] for c in HYBRID_PATTERN]
    assert len(layers_block_type) == NUM_LAYERS, len(layers_block_type)
    return {
        "model_type": "nemotron_h",
        "architectures": ["NemotronHForCausalLM"],
        "vocab_size": VOCAB_SIZE,
        "hidden_size": HIDDEN_SIZE,
        "intermediate_size": INTERMEDIATE_SIZE,
        "num_hidden_layers": NUM_LAYERS,
        "hybrid_override_pattern": HYBRID_PATTERN,
        "layers_block_type": layers_block_type,
        "num_attention_heads": NUM_ATTENTION_HEADS,
        "num_key_value_heads": NUM_KV_HEADS,
        "head_dim": HEAD_DIM,
        "max_position_embeddings": MAX_POSITION_EMBEDDINGS,
        "attention_bias": False,
        "mlp_bias": False,
        "tie_word_embeddings": False,
        # mamba-2
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
        # ★ 待验证：megatron run_config 报 activation_func=gelu；Nemotron-H MLP 默认 relu2。
        "mlp_hidden_act": "gelu",
        "mamba_hidden_act": "silu",
        "mamba_chunk_size": 256,
        "torch_dtype": "bfloat16",
        "bos_token_id": 1,
        "eos_token_id": 2,
        "pad_token_id": 0,
        "use_cache": True,
    }
def convert(sd: dict) -> dict:
    """mcore state_dict → HF Nemotron-H state_dict（权重名映射）。

    mcore 命名（load_plain_tensors 实测）：
      embedding.word_embeddings.weight          [129408, 2048]
      decoder.layers.{i}.mixer.*                (mamba-2)
      decoder.layers.{i}.self_attention.*       (attention)
      decoder.layers.{i}.mlp.linear_fc1/fc2.*   (mlp-only)
      decoder.final_norm.weight                 [2048]
      output_layer.weight                       [129408, 2048]
    HF 命名（SGLang/vLLM NemotronH）：
      model.embed_tokens.weight / lm_head.weight
      model.layers.{i}.input_layernorm.weight
      model.layers.{i}.mixer.{in_proj,conv1d,norm,out_proj}.weight + mixer.A_log/D/dt_bias
      model.layers.{i}.self_attn.{q,k,v,o}_proj.weight
      model.layers.{i}.mlp.{up,down}_proj.weight
      model.norm.weight
    """
    hf = {}

    def put(name, t):
        assert name not in hf, "dup key " + name
        hf[name] = t.contiguous()

    put("model.embed_tokens.weight", sd["embedding.word_embeddings.weight"])
    put("model.norm.weight", sd["decoder.final_norm.weight"])
    if "output_layer.weight" in sd:
        put("lm_head.weight", sd["output_layer.weight"])
    else:
        put("lm_head.weight", sd["embedding.word_embeddings.weight"].clone())

    for i in range(NUM_LAYERS):
        btype = HYBRID_PATTERN[i]
        mcore = f"decoder.layers.{i}"
        hfp = f"model.layers.{i}"
        # 每类层的「输入 RMSNorm」在 mcore 里被融合进第一个 projection：
        #   mixer.in_proj / self_attention.linear_qkv / mlp.linear_fc1 的 .layer_norm_weight
        #   → 统一映射为 HF 的 input_layernorm.weight
        if btype == "M":
            m = f"{mcore}.mixer"
            put(f"{hfp}.input_layernorm.weight", sd[f"{m}.in_proj.layer_norm_weight"])
            # in_proj 拼接顺序（mamba_mixer.py "# z x B C dt"）：
            #   [z(4096)|x(4096)|B(1024)|C(1024)|dt(64)] → [10304, 2048]
            in_proj = torch.cat([
                sd[f"{m}.in_proj.weight.z"],
                sd[f"{m}.in_proj.weight.x"],
                sd[f"{m}.in_proj.weight.B"],
                sd[f"{m}.in_proj.weight.C"],
                sd[f"{m}.in_proj.weight.dt"],
            ], dim=0)
            put(f"{hfp}.mixer.in_proj.weight", in_proj)
            # conv1d 拼接顺序 "# x B C" → [6144, 1, 4]
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
            a = f"{mcore}.self_attention"
            put(f"{hfp}.input_layernorm.weight", sd[f"{a}.linear_qkv.layer_norm_weight"])
            qkv = sd[f"{a}.linear_qkv.weight"]  # [3072,2048] = q(2048) k(512) v(512)
            sizes = [HIDDEN_SIZE, NUM_KV_HEADS * HEAD_DIM, NUM_KV_HEADS * HEAD_DIM]
            q, k, v = qkv.split(sizes, dim=0)
            put(f"{hfp}.self_attn.q_proj.weight", q)
            put(f"{hfp}.self_attn.k_proj.weight", k)
            put(f"{hfp}.self_attn.v_proj.weight", v)
            put(f"{hfp}.self_attn.o_proj.weight", sd[f"{a}.linear_proj.weight"])
            # qk_layernorm=false（run_config）→ 无 q_norm/k_norm
        elif btype == "-":
            mlp = f"{mcore}.mlp"
            put(f"{hfp}.input_layernorm.weight", sd[f"{mlp}.linear_fc1.layer_norm_weight"])
            # 非门控单投影 MLP：fc1[8192,2048]=up、fc2[2048,8192]=down
            put(f"{hfp}.mlp.up_proj.weight", sd[f"{mlp}.linear_fc1.weight"])
            put(f"{hfp}.mlp.down_proj.weight", sd[f"{mlp}.linear_fc2.weight"])
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
    print(f"[load] {len(sd)} keys, {n_param/1e9:.3f}B params")

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