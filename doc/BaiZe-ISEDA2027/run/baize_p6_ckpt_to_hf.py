#!/usr/bin/env python3
# Copyright (c) 2026, BaiZe Stage(i) LLM pretrain.
#
# P-6 第 1 步：把 mcore "torch_dist" checkpoint 转换为
# HF Nemotron-H（model_type="nemotron_h"）格式，供 SGLang 起服 + lm_eval 零样本评测。
#
# 2026-10-07 更新：支持 **自动架构检测**（2B / d128 proxy）。
#   - 从 checkpoint 的 embedding.weight 形状自动推断 hidden_size
#   - hidden_size=2048 → 2B 模型常量（56 层，原口径，向后兼容）
#   - hidden_size=128  → d128 proxy 常量（14 层，tie_embed=True）
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

# ── 架构常量：默认 2B（与 mamba2_hybrid_2b/provider.py + s5_01/run_config.yaml 完全一致）────
# 2026-10-07：这些全局变量会在 main() 中根据 checkpoint 自动检测后被覆盖（d128 proxy）。
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

# tie_word_embeddings：2B=False, d128 proxy=True（share_embeddings_and_output_weights）
_TIE_EMBEDDINGS = False


def _detect_and_set_arch(sd: dict):
    """从 checkpoint 的 embedding.weight 形状自动推断架构，覆盖全局常量。"""
    global HIDDEN_SIZE, INTERMEDIATE_SIZE, NUM_LAYERS, NUM_ATTENTION_HEADS
    global NUM_KV_HEADS, HEAD_DIM, MAMBA_NUM_HEADS, MAMBA_HEAD_DIM
    global SSM_STATE_SIZE, N_GROUPS, EXPAND, CONV_KERNEL
    global MAX_POSITION_EMBEDDINGS, HYBRID_PATTERN, _TIE_EMBEDDINGS

    emb_key = "embedding.word_embeddings.weight"
    if emb_key not in sd:
        raise KeyError(f"Cannot find '{emb_key}' in checkpoint for architecture detection")
    detected_hidden = sd[emb_key].shape[1]

    if detected_hidden == 2048:
        # 2B model — explicitly set defaults (in case globals were modified by a prior call)
        print(f"[arch] detected 2B model (hidden_size={detected_hidden})")
        HIDDEN_SIZE = 2048
        INTERMEDIATE_SIZE = 8192
        NUM_LAYERS = 56
        NUM_ATTENTION_HEADS = 16
        NUM_KV_HEADS = 4
        HEAD_DIM = HIDDEN_SIZE // NUM_ATTENTION_HEADS   # 128
        MAMBA_NUM_HEADS = 64
        MAMBA_HEAD_DIM = 64
        SSM_STATE_SIZE = 128
        N_GROUPS = 8
        EXPAND = 2
        CONV_KERNEL = 4
        MAX_POSITION_EMBEDDINGS = 4096
        HYBRID_PATTERN = "M-M-M--M-M*-M-M-M-M--M*-M-M-M-M-M*--M-M-M-M-M*-M--M-M-M-"
        _TIE_EMBEDDINGS = False
    elif detected_hidden == 128:
        # d128 proxy model (18.5M, d=128/L=14, tie_embed=True)
        # See: mamba2_hybrid_proxy_d128/provider.py
        print(f"[arch] detected d128 proxy model (hidden_size={detected_hidden})")
        HIDDEN_SIZE = 128
        INTERMEDIATE_SIZE = 512          # 4 × hidden
        NUM_LAYERS = 14
        NUM_ATTENTION_HEADS = 1          # d/128 = 128/128
        NUM_KV_HEADS = 1                 # ≤ heads
        HEAD_DIM = HIDDEN_SIZE // NUM_ATTENTION_HEADS   # 128
        MAMBA_NUM_HEADS = 4              # d_inner(256) / head_dim(64) = 4
        MAMBA_HEAD_DIM = 64
        SSM_STATE_SIZE = 128
        N_GROUPS = 1                     # ≤ heads
        EXPAND = 2
        CONV_KERNEL = 4
        MAX_POSITION_EMBEDDINGS = 2048
        HYBRID_PATTERN = "M-M-M--M-M*-M-"   # 56层pattern的前14字符 (6M/1*/7-)
        _TIE_EMBEDDINGS = True
    else:
        raise ValueError(
            f"Unknown hidden_size={detected_hidden}; expected 128 (d128 proxy) or 2048 (2B)"
        )


def build_config_json() -> dict:
    """SGLang/transformers NemotronHConfig 的 config.json。

    SGLang 新版以 layers_block_type（list）为规范写法，同时兼容 hybrid_override_pattern。
    """
    # ★ transformers 5.17.0 NemotronHConfig 的规范层名：
    #   linear_attention (Mamba2) / full_attention / mlp
    mapping = {"M": "linear_attention", "*": "full_attention", "-": "mlp"}
    layers_block_type = [mapping[c] for c in HYBRID_PATTERN]
    assert len(layers_block_type) == NUM_LAYERS, len(layers_block_type)
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
        "max_position_embeddings": MAX_POSITION_EMBEDDINGS,
        "attention_bias": False,
        "mlp_bias": False,
        "tie_word_embeddings": _TIE_EMBEDDINGS,
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
        # ★ 已确认：megatron run_config `activation_func: torch._C._nn.gelu` → 精确 erf GELU，
        #   与 transformers ACT2FN["gelu"] 一致（非 tanh 近似）。
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
    """mcore state_dict → HF Nemotron-H state_dict（权重名映射）。

    mcore 命名（load_plain_tensors 实测）：
      embedding.word_embeddings.weight          [129408, 2048]
      decoder.layers.{i}.mixer.*                (mamba-2)
      decoder.layers.{i}.self_attention.*       (attention)
      decoder.layers.{i}.mlp.linear_fc1/fc2.*   (mlp-only)
      decoder.final_norm.weight                 [2048]
      output_layer.weight                       [129408, 2048]
    HF 命名（transformers 5.17.0 NemotronHForCausalLM 实测 state_dict）：
      model.embeddings.weight / lm_head.weight
      model.layers.{i}.norm.weight
      model.layers.{i}.mixer.{in_proj,conv1d,norm,out_proj}.weight + mixer.A_log/D/dt_bias   (linear_attention)
      model.layers.{i}.mixer.{q,k,v,o}_proj.weight                                        (full_attention)
      model.layers.{i}.mixer.{up,down}_proj.weight                                        (mlp)
      model.norm_f.weight
    """
    hf = {}

    def put(name, t):
        assert name not in hf, "dup key " + name
        hf[name] = t.contiguous()

    put("model.embeddings.weight", sd["embedding.word_embeddings.weight"])
    put("model.norm_f.weight", sd["decoder.final_norm.weight"])
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
            put(f"{hfp}.norm.weight", sd[f"{m}.in_proj.layer_norm_weight"])
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
            put(f"{hfp}.norm.weight", sd[f"{a}.linear_qkv.layer_norm_weight"])
            qkv = sd[f"{a}.linear_qkv.weight"]  # [3072,2048] = q(2048) k(512) v(512)
            sizes = [HIDDEN_SIZE, NUM_KV_HEADS * HEAD_DIM, NUM_KV_HEADS * HEAD_DIM]
            q, k, v = qkv.split(sizes, dim=0)
            put(f"{hfp}.mixer.q_proj.weight", q)
            put(f"{hfp}.mixer.k_proj.weight", k)
            put(f"{hfp}.mixer.v_proj.weight", v)
            put(f"{hfp}.mixer.o_proj.weight", sd[f"{a}.linear_proj.weight"])
            # qk_layernorm=false（run_config）→ 无 q_norm/k_norm
        elif btype == "-":
            mlp = f"{mcore}.mlp"
            put(f"{hfp}.norm.weight", sd[f"{mlp}.linear_fc1.layer_norm_weight"])
            # 非门控单投影 MLP：fc1[8192,2048]=up、fc2[2048,8192]=down
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
    print(f"[load] {len(sd)} keys, {n_param/1e9:.3f}B params")

    # Auto-detect architecture (2B vs d128 proxy) from checkpoint
    _detect_and_set_arch(sd)

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