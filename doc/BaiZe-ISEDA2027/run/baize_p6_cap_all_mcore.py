#!/usr/bin/env python3
# P-6 诊断：mcore 侧逐层(全部 56 层)激活导出，定位「首个分歧层」（重点看 attention 层 10/22/33/45）。
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
        dir="/tmp/baize2b_fwd", name="p6_l", tokenizer_path=args.tokenizer_path,
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
    model = _unwrap_model(out.model).eval()

    layers = model.decoder.layers
    caps = {}

    def mk(k):
        def hook(m, inp, outp):
            t = outp[0] if isinstance(outp, (tuple, list)) else outp
            caps[k] = t.detach().float().cpu()
        return hook

    model.embedding.register_forward_hook(mk("emb"))
    for i, layer in enumerate(layers):
        layer.register_forward_hook(mk(f"L{i:02d}"))
    model.decoder.register_forward_hook(mk("final"))

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

    torch.save({"input_ids": input_ids.cpu().long(), "logits": logits,
                "caps": caps}, args.out)
    for k in sorted(caps):
        print(f"[A] {k} std={float(caps[k].std()):.4f}", flush=True)
    print("A_L_DONE", flush=True)


if __name__ == "__main__":
    main()