#!/usr/bin/env python3
# 轻量：直接对比 embedding 权重（HF safetensors vs mcore checkpoint）。
import os
os.environ.setdefault("MASTER_ADDR", "127.0.0.1")
os.environ.setdefault("MASTER_PORT", "29504")
import torch
from safetensors.torch import load_file

HF = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/hf_nemotron_h/model.safetensors"
hf = load_file(HF)
hf_emb = hf["model.embeddings.weight"].float()
print(f"[hf] emb shape={tuple(hf_emb.shape)} std={hf_emb.std():.5f} mean={hf_emb.mean():.5f}")

torch.distributed.init_process_group(backend="gloo", rank=0, world_size=1)
from megatron.core.dist_checkpointing.serialization import load_plain_tensors
CKPT = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/checkpoints/iter_0020000"
sd = load_plain_tensors(CKPT)
mc_emb = sd["embedding.word_embeddings.weight"].float()
print(f"[mc] emb shape={tuple(mc_emb.shape)} std={mc_emb.std():.5f} mean={mc_emb.mean():.5f}")
d = (hf_emb - mc_emb).abs()
print(f"[cmp] maxdiff={d.max().item():.3e} meandiff={d.mean().item():.3e} "
      f"equal={bool((hf_emb == mc_emb).all())}")

# 如果不等，看是不是缩放关系
ratio = hf_emb / (mc_emb + 1e-8)
print(f"[ratio] emb ratio min={ratio.min():.4f} max={ratio.max():.4f} mean={ratio.mean():.4f}")

# lm_head 也对比一下
hf_lm = hf["lm_head.weight"].float()
mc_lm = sd["output_layer.weight"].float()
print(f"[lm] maxdiff={(hf_lm-mc_lm).abs().max():.3e} equal={bool((hf_lm==mc_lm).all())}")

# norm_f
hf_norm = hf["model.norm_f.weight"].float()
mc_norm = sd["decoder.final_norm.weight"].float()
print(f"[norm_f] maxdiff={(hf_norm-mc_norm).abs().max():.3e} equal={bool((hf_norm==mc_norm).all())}")