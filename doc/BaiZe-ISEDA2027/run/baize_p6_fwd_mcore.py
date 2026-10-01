#!/usr/bin/env python3
# Copyright (c) 2026, BaiZe Stage(i) LLM pretrain.
#
# P-6 第 1 步：前向 logits 对拍 —— 【Side A（权威侧）】mcore 直驱前向。
# 把 s5_01 20000 步 checkpoint 用 megatron-core 加载（TP1/PP1/单卡），
# 对固定 input_ids 做一次 prefill 前向，导出完整 logits（供与 HF/SGLang 侧逐位对比）。
#
# 用法（单卡 torchrun）：
#   CUDA_VISIBLE_DEVICES=<gpu> torchrun --nnodes=1 --nproc_per_node=1 \
#     baize_p6_fwd_mcore.py --load-dir <iter_0020000> \
#     --tokenizer-path <hf_tokenizer_eod> --out <logits.pt> [--seq 128]
import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for p in (BASE_DIR, "/nas_train/app.e0031982/code/BaiZe-ISEDA2027"):
    if p not in sys.path:
        sys.path.insert(0, p)

import torch  # noqa: E402

from megatron.bridge.data.utils import get_dataset_provider  # noqa: E402
from megatron.bridge.training.config import runtime_config_update  # noqa: E402
from megatron.bridge.training.setup import setup  # noqa: E402
from megatron.bridge.training.state import GlobalState  # noqa: E402
from megatron.core.inference.contexts.static_context import StaticInferenceContext  # noqa: E402

import bridge_compat  # noqa: E402


def _unwrap_model(model):
    depth = 0
    while hasattr(model, "module") and depth < 10:
        model = model.module
        depth += 1
    if isinstance(model, (list, tuple)):
        model = model[0]
    return model


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--load-dir", required=True)
    p.add_argument("--tokenizer-path", default=None)
    p.add_argument("--seq", type=int, default=128)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    from mamba2_hybrid_2b.recipe import pretrain_config

    cfg = pretrain_config(
        dir="/tmp/baize2b_fwd",
        name="p6_fwd",
        tokenizer_path=args.tokenizer_path,
        tensor_parallelism=1,
        pipeline_parallelism=1,
        global_batch_size=1,
        micro_batch_size=1,
        seq_length=4096,
    )
    cfg.checkpoint.load = args.load_dir
    cfg.checkpoint.save = args.load_dir
    cfg.checkpoint.save_interval = 0
    cfg.train.skip_train = True
    cfg.train.do_validation = False
    cfg.train.do_test = False

    runtime_config_update(cfg)
    state = GlobalState()
    state.cfg = cfg
    bridge_compat.apply_all_compat_shims()
    dataset_provider = get_dataset_provider(cfg.dataset)
    out = setup(state, dataset_provider)
    model = _unwrap_model(out.model)
    model.eval()

    n_params = sum(x.numel() for x in model.parameters())
    print(f"[A:mcore] params={n_params/1e9:.3f}B", flush=True)

    # 用 DeepSeek tokenizer 编码一段固定文本 → 与 HF 侧共用同一 input_ids。
    import json
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(args.tokenizer_path)
    text = ("The mitochondria is the powerhouse of the cell. "
            "Photosynthesis converts sunlight into chemical energy. "
            "Machine learning models learn patterns from data.")
    ids = tok(text, add_special_tokens=False)["input_ids"]
    S = min(len(ids), args.seq)
    input_ids = torch.tensor([ids[:S]], dtype=torch.long, device="cuda")
    print(f"[A:mcore] tokenized seq_len={S} ids[:8]={ids[:8]}", flush=True)

    pos = torch.arange(S, dtype=torch.long, device="cuda").unsqueeze(0)
    with torch.no_grad():
        ctx = StaticInferenceContext(max_batch_size=1, max_sequence_length=S + 32)
        logits = model(input_ids, pos, None, inference_context=ctx, runtime_gather_output=True)
    logits = logits.float().cpu()  # [1, S, V]

    print(f"[A:mcore] logits shape={tuple(logits.shape)} "
          f"finite={bool(torch.isfinite(logits).all())} "
          f"argmax_last={int(logits[0, -1].argmax().item())} "
          f"std={float(logits[0, -1].std().item()):.4f}", flush=True)

    torch.save({"input_ids": input_ids.cpu().long(), "logits": logits}, args.out)
    # 供逐位对拍的确定性摘要（跨机器/跨实现可复算）
    h = logits[0].contiguous().numpy().tobytes()
    import hashlib
    print(f"[A:mcore] sha256(logits)={hashlib.sha256(h).hexdigest()}", flush=True)
    print("A_DONE", flush=True)


if __name__ == "__main__":
    main()