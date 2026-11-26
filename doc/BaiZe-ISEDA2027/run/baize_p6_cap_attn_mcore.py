#!/usr/bin/env python3
# P-6 诊断：L10(首个 attention 层)内部 —— QKV 投影输出 vs attention 输出，两侧对比定位分歧。
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


def _unwrap_model(m):
    d = 0
    while d < 10:
        if isinstance(m, (list, tuple)):
            m = m[0]; continue
        if hasattr(m, "module"):
            m = m.module; continue
        if hasattr(m, "m"):
            m = m.m; continue
        break
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--load-dir", required=True)
    ap.add_argument("--tokenizer-path", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    from mamba2_hybrid_2b.recipe import pretrain_config
    cfg = pretrain_config(
        dir="/tmp/baize2b_fwd", name="p6_attn", tokenizer_path=args.tokenizer_path,
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
    dp = get_dataset_provider(cfg.dataset)
    out = setup(state, dp)
    model = _unwrap_model(out.model).eval()

    caps = {}
    layer = model.decoder.layers[10]

    def mk(k):
        def hook(m, inp, outp):
            t = outp[0] if isinstance(outp, (tuple, list)) else outp
            caps[k] = t.detach().float().cpu()
        return hook

    sa = layer.self_attention
    # 尝试标准 megatron 属性名
    lqkv = getattr(sa, "linear_qkv", None)
    if lqkv is not None:
        lqkv.register_forward_hook(mk("qkv"))
    layer.register_forward_hook(mk("attn_out"))
    model.decoder.layers[9].register_forward_hook(mk("L9_in"))

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.tokenizer_path)
    text = ("The mitochondria is the powerhouse of the cell. "
            "Photosynthesis converts sunlight into chemical energy. "
            "Machine learning models learn patterns from data.")
    ids = tok(text, add_special_tokens=False)["input_ids"]
    S = len(ids)
    input_ids = torch.tensor([ids[:S]], dtype=torch.long, device="cuda")
    pos = torch.arange(S, dtype=torch.long, device="cuda").unsqueeze(0)

    with torch.no_grad():
        ctx = StaticInferenceContext(max_batch_size=1, max_sequence_length=S + 32)
        model(input_ids, pos, None, inference_context=ctx, runtime_gather_output=True)

    torch.save({k: v for k, v in caps.items() if v is not None}, args.out)
    for k in caps:
        print(f"[A] {k} shape={tuple(caps[k].shape)} std={float(caps[k].std()):.4f}", flush=True)
    print("A_ATTN_DONE", flush=True)


if __name__ == "__main__":
    main()