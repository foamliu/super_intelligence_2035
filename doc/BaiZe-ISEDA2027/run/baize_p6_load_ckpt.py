#!/usr/bin/env python3
# Copyright (c) 2026, BaiZe Stage(i) LLM pretrain.
#
# P-6 第 1 步关键解锁：把 megatron-core "torch_dist" (DCP) 格式的 20000 步 checkpoint
# 在【单进程、无需 torchrun/8 卡】下完整载入，得到全量 2.220B 权重。
#
# 用法：
#   PYTHONPATH=/nas_train/app.e0031982/omegaconf_230 python baize_p6_load_ckpt.py \
#       --ckpt /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/s5_01/checkpoints/iter_0020000
#
# 关键点（本脚本已在 2026-10-02 实测验证）：
#   - checkpoint 由 megatron-core 0.16.1 以 ckpt_format="torch_dist" + fully_parallel_load + save_optim=False
#     保存，模型权重按 DP=8 全分片（fully_reshardable）摊到 8 个 rank 的 `__N_X.distcp`。
#   - `megatron.core.dist_checkpointing.serialization.load_plain_tensors()` 会读取 .metadata +
#     全部 .distcp 分片，在单进程内把每条 tensor 拼回【全局完整形状】（无需 8 卡 all-gather）。
#   - 唯一前置：`torch.distributed` 需已初始化（backend=gloo、world_size=1 即可），
#     因为 mcore_to_pyt_state_dict() 会调用 torch.distributed.get_rank()。
#
# 实测（2026-10-02）：
#   507 个 tensor key，合计 2,220,268,032 = 2.220B 参数，载入约 6.4s（NFS 读 4.4GB）。
import argparse
import os
import time

os.environ.setdefault("MASTER_ADDR", "127.0.0.1")
os.environ.setdefault("MASTER_PORT", "29501")

import torch  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Load Baize 2B torch_dist checkpoint plain tensors")
    ap.add_argument("--ckpt", required=True, help="checkpoint dir (iter_XXXXXXX)")
    args = ap.parse_args()

    if not torch.distributed.is_initialized():
        torch.distributed.init_process_group(backend="gloo", rank=0, world_size=1)

    from megatron.core.dist_checkpointing.serialization import load_plain_tensors

    t0 = time.time()
    sd = load_plain_tensors(args.ckpt)
    dt = time.time() - t0

    n_param = sum(v.numel() for v in sd.values() if hasattr(v, "numel"))
    print(f"loaded {len(sd)} keys | {n_param} params = {n_param/1e9:.3f}B | {dt:.1f}s", flush=True)
    return sd


if __name__ == "__main__":
    main()