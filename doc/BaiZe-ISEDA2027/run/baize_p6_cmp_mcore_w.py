#!/usr/bin/env python3
# 对比 mcore 模型「实际加载」的权重 vs checkpoint 原始权重，判断是否真的加载了。
import os
os.environ.setdefault("MASTER_ADDR", "127.0.0.1")
os.environ.setdefault("MASTER_PORT", "29505")
import torch

W = torch.load("/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/p6_mcore_w.pt", map_location="cpu", weights_only=False)

torch.distributed.init_process_group(backend="gloo", rank=0, world_size=1)
from megatron.core.dist_checkpointing.serialization import load_plain_tensors
CKPT = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/checkpoints/iter_0020000"
sd = load_plain_tensors(CKPT)

for k, mcore_t in W.items():
    if k not in sd:
        print(f"[{k}] NOT in checkpoint")
        continue
    ckpt_t = sd[k].float()
    m = mcore_t.float()
    if ckpt_t.shape != m.shape:
        print(f"[{k}] SHAPE mcore={tuple(m.shape)} ckpt={tuple(ckpt_t.shape)}")
        continue
    d = (m - ckpt_t).abs()
    eq = bool((m == ckpt_t).all())
    print(f"[{k}] maxdiff={d.max().item():.3e} equal={eq} ckpt_std={ckpt_t.std():.5f}")