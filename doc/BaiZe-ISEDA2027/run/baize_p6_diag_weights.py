#!/usr/bin/env python3
# 诊断：逐位比较 HF 已加载模型权重 vs mcore checkpoint 原始权重，
# 以定位对拍失败是「权重加载/映射」还是「前向计算」问题。
import os
os.environ.setdefault("MASTER_ADDR", "127.0.0.1")
os.environ.setdefault("MASTER_PORT", "29503")
import sys
sys.path.insert(0, "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5")

import torch
from safetensors.torch import load_file
from transformers import NemotronHForCausalLM


def cat_in_proj(sd, m):
    return torch.cat([
        sd[f"{m}.in_proj.weight.z"], sd[f"{m}.in_proj.weight.x"],
        sd[f"{m}.in_proj.weight.B"], sd[f"{m}.in_proj.weight.C"],
        sd[f"{m}.in_proj.weight.dt"],
    ], dim=0)


def cat_conv_w(sd, m):
    return torch.cat([
        sd[f"{m}.conv1d.weight.x"], sd[f"{m}.conv1d.weight.B"], sd[f"{m}.conv1d.weight.C"],
    ], dim=0)


def cat_conv_b(sd, m):
    return torch.cat([
        sd[f"{m}.conv1d.bias.x"], sd[f"{m}.conv1d.bias.B"], sd[f"{m}.conv1d.bias.C"],
    ], dim=0)


def main():
    if not torch.distributed.is_initialized():
        torch.distributed.init_process_group(backend="gloo", rank=0, world_size=1)
    from megatron.core.dist_checkpointing.serialization import load_plain_tensors

    CKPT = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/checkpoints/iter_0020000"
    HF = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/hf_nemotron_h"

    sd = load_plain_tensors(CKPT)
    print(f"[mcore] {len(sd)} keys", flush=True)

    model = NemotronHForCausalLM.from_pretrained(HF, torch_dtype=torch.bfloat16).cuda().eval()
    hf = model.state_dict()

    def cmp(name_hf, t_mcore, tol=0.0):
        t_hf = hf[name_hf].float().cpu()
        t_mcore = t_mcore.float().cpu()
        if t_hf.shape != t_mcore.shape:
            print(f"[MISMATCH-SHAPE] {name_hf}: hf={tuple(t_hf.shape)} mcore={tuple(t_mcore.shape)}", flush=True)
            return
        d = (t_hf - t_mcore).abs()
        print(f"[{ 'OK' if d.max().item() <= tol else 'DIFF' }] {name_hf} maxdiff={d.max().item():.3e} "
              f"hf_mean={t_hf.mean():.4f} mcore_mean={t_mcore.mean():.4f}", flush=True)

    # embedding
    cmp("model.embeddings.weight", sd["embedding.word_embeddings.weight"])
    cmp("lm_head.weight", sd["output_layer.weight"])
    cmp("model.norm_f.weight", sd["decoder.final_norm.weight"])

    # layer 0 = mamba (linear_attention)
    m = "decoder.layers.0.mixer"
    cmp("model.layers.0.norm.weight", sd["decoder.layers.0.mixer.in_proj.layer_norm_weight"])
    cmp("model.layers.0.mixer.in_proj.weight", cat_in_proj(sd, m))
    cmp("model.layers.0.mixer.conv1d.weight", cat_conv_w(sd, m))
    cmp("model.layers.0.mixer.conv1d.bias", cat_conv_b(sd, m))
    cmp("model.layers.0.mixer.A_log", sd[f"{m}.A_log"])
    cmp("model.layers.0.mixer.D", sd[f"{m}.D"])
    cmp("model.layers.0.mixer.dt_bias", sd[f"{m}.dt_bias"])
    cmp("model.layers.0.mixer.norm.weight", sd[f"{m}.norm.weight"])
    cmp("model.layers.0.mixer.out_proj.weight", sd[f"{m}.out_proj.weight"])

    # layer 1 = mlp
    m = "decoder.layers.1.mlp"
    cmp("model.layers.1.norm.weight", sd["decoder.layers.1.mlp.linear_fc1.layer_norm_weight"])
    cmp("model.layers.1.mixer.up_proj.weight", sd[f"{m}.linear_fc1.weight"])
    cmp("model.layers.1.mixer.down_proj.weight", sd[f"{m}.linear_fc2.weight"])

    # layer 10 = attention
    a = "decoder.layers.10.self_attention"
    cmp("model.layers.10.norm.weight", sd["decoder.layers.10.self_attention.linear_qkv.layer_norm_weight"])
    qkv = sd[f"{a}.linear_qkv.weight"]
    q, k, v = qkv.split([2048, 512, 512], dim=0)
    cmp("model.layers.10.mixer.q_proj.weight", q)
    cmp("model.layers.10.mixer.k_proj.weight", k)
    cmp("model.layers.10.mixer.v_proj.weight", v)
    cmp("model.layers.10.mixer.o_proj.weight", sd[f"{a}.linear_proj.weight"])

    print("DIAG_DONE", flush=True)


if __name__ == "__main__":
    main()