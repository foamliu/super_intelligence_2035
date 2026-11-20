#!/usr/bin/env python3
# P-6 第 1 步：前向 logits 对拍 —— 【Side B（被验侧）】HF NemotronH 前向。
# 用 p6_tf5 里隔离安装的 transformers 5.17.0 加载 hf_nemotron_h/，
# 对 Side A 保存的同一 input_ids 做 prefill 前向，与 mcore logits 逐位对比。
#
# 用法：
#   CUDA_VISIBLE_DEVICES=<gpu> python baize_p6_fwd_hf.py \
#       --model <hf_nemotron_h> --ref <p6_fwd_mcore.pt> [--dtype bf16|fp32]
import argparse
import sys

sys.path.insert(0, "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5")

import torch  # noqa: E402
from transformers import NemotronHForCausalLM  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--dtype", default="bf16")
    args = ap.parse_args()

    ref = torch.load(args.ref, map_location="cpu")
    input_ids = ref["input_ids"].long()  # [1, S]
    ref_logits = ref["logits"].float()   # [1, 1, V]  (last-token logits from runtime_gather_output)
    ref_last = ref_logits.reshape(-1, ref_logits.shape[-1])[0]  # [V]

    dtype = torch.bfloat16 if args.dtype == "bf16" else torch.float32
    model = NemotronHForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=None
    ).cuda().eval()
    n_param = sum(p.numel() for p in model.parameters())
    print(f"[B:hf] params={n_param/1e9:.3f}B dtype={args.dtype}", flush=True)

    with torch.no_grad():
        out = model(input_ids.to("cuda"))
    logits = out.logits.float().cpu()  # [1, S, V]
    hf_last = logits[0, -1]            # [V]  预测第 S 个 token

    diff = (hf_last - ref_last).abs()
    print(f"[B:hf] logits shape={tuple(logits.shape)} finite={bool(torch.isfinite(logits).all())}", flush=True)
    print(f"[B:hf] ref_argmax={int(ref_last.argmax())} hf_argmax={int(hf_last.argmax())} "
          f"match={int(ref_last.argmax()) == int(hf_last.argmax())}", flush=True)
    print(f"[B:hf] ref_std={float(ref_last.std()):.4f} max_abs_diff={float(diff.max()):.6e} "
          f"mean_abs_diff={float(diff.mean()):.6e}", flush=True)

    # top-k 重合度（对拍弱判据）
    for k in (1, 5, 10, 50):
        a = set(torch.topk(ref_last, k).indices.tolist())
        b = set(torch.topk(hf_last, k).indices.tolist())
        print(f"[B:hf] top{k} overlap={len(a & b)}/{k}", flush=True)

    # 相对误差（对 log-sigmoid 归一化后）
    rel = (diff / (ref_last.abs() + 1e-6))
    print(f"[B:hf] max_rel_diff={float(rel.max()):.6e}", flush=True)

    torch.save({"hf_logits": logits}, args.ref + ".hf.pt")
    print("B_DONE", flush=True)


if __name__ == "__main__":
    main()