#!/usr/bin/env python3
# P-6 对拍诊断：mcore 侧逐层激活导出（用于与 HF 侧逐位对比定位分歧层）。
# 复用 baize_p6_fwd_mcore.py 的加载逻辑，额外用 forward hook 抓中间激活。
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
    p.add_argument("--seq", type=int, default=128)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    from mamba2_hybrid_2b.recipe import pretrain_config

    cfg = pretrain_config(
        dir="/tmp/baize2b_fwd", name="p6_fwd", tokenizer_path=args.tokenizer_path,
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
    model = _unwrap_model(out.model)
    model.eval()

    # discover decoder / layers module paths
    decoder = model.decoder
    layers = decoder.layers
    print(f"[A] model type={type(model).__name__} n_layers={len(layers)}", flush=True)

    caps = {}

    def mk(k, clear=False):
        def hook(m, inp, outp):
            if clear:
                caps[k] = None
                return
            tensors = [x for x in outp if isinstance(x, torch.Tensor)] if isinstance(outp, (tuple, list)) else [outp]
            caps[k] = tensors[0].detach().float().cpu()
        return hook

    model.embedding.register_forward_hook(mk("emb"))
    layers[0].register_forward_hook(mk("L0"))
    layers[1].register_forward_hook(mk("L1"))
    layers[10].register_forward_hook(mk("L10"))
    layers[55].register_forward_hook(mk("L55"))
    decoder.register_forward_hook(mk("final"))

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.tokenizer_path)
    text = ("The mitochondria is the powerhouse of the cell. "
            "Photosynthesis converts sunlight into chemical energy. "
            "Machine learning models learn patterns from data.")
    ids = tok(text, add_special_tokens=False)["input_ids"]
    S = min(len(ids), args.seq)
    input_ids = torch.tensor([ids[:S]], dtype=torch.long, device="cuda")
    pos = torch.arange(S, dtype=torch.long, device="cuda").unsqueeze(0)

    with torch.no_grad():
        ctx = StaticInferenceContext(max_batch_size=1, max_sequence_length=S + 32)
        logits = model(input_ids, pos, None, inference_context=ctx, runtime_gather_output=True)
    logits = logits.float().cpu()

    dump = {"input_ids": input_ids.cpu().long(), "logits": logits,
            "caps": {k: v for k, v in caps.items() if v is not None}}
    for k, v in dump["caps"].items():
        print(f"[A] cap {k} shape={tuple(v.shape)} std={float(v.std()):.4f}", flush=True)
    torch.save(dump, args.out)
    print("A_CAP_DONE", flush=True)


if __name__ == "__main__":
    main()