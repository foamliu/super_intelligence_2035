#!/usr/bin/env python3
# P-6 诊断：导出 mcore 模型「实际加载」的权重，与 checkpoint/HF 逐位对比，
# 判断 mcore 侧是否真的从 checkpoint 加载了权重（还是部分被重新初始化）。
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
import bridge_compat  # noqa: E402


def _unwrap_model(model):
    depth = 0
    while depth < 10:
        if isinstance(model, (list, tuple)):
            model = model[0]
            continue
        if hasattr(model, "module"):
            model = model.module
            continue
        if hasattr(model, "m"):
            model = model.m
            continue
        break
    return model


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--load-dir", required=True)
    p.add_argument("--tokenizer-path", default=None)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    from mamba2_hybrid_2b.recipe import pretrain_config

    cfg = pretrain_config(
        dir="/tmp/baize2b_w", name="p6_w", tokenizer_path=args.tokenizer_path,
        tensor_parallelism=1, pipeline_parallelism=1, global_batch_size=1,
        micro_batch_size=1, seq_length=4096,
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
    m = _unwrap_model(out.model).eval()

    sd = m.state_dict()
    keys = [
        "embedding.word_embeddings.weight",
        "output_layer.weight",
        "decoder.final_norm.weight",
        "decoder.layers.0.mixer.in_proj.weight.x",
        "decoder.layers.0.mixer.A_log",
        "decoder.layers.0.mixer.norm.weight",
        "decoder.layers.10.self_attention.linear_qkv.layer_norm_weight",
        "decoder.layers.10.self_attention.linear_qkv.weight",
    ]
    dump = {}
    for k in keys:
        if k in sd:
            t = sd[k].detach().float().cpu()
            dump[k] = t
            print(f"[A:w] {k} shape={tuple(t.shape)} std={t.std():.5f} mean={t.mean():.5f}", flush=True)
        else:
            print(f"[A:w] MISSING {k}", flush=True)
    torch.save(dump, args.out)
    print("A_W_DONE", flush=True)


if __name__ == "__main__":
    main()