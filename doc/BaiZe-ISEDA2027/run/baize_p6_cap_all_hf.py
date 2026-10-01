#!/usr/bin/env python3
# P-6 诊断：HF 侧逐层(全部 56 层)激活导出，与 mcore 逐层对比定位分歧层。
import argparse
import sys

sys.path.insert(0, "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5")

import torch  # noqa: E402
from transformers import NemotronHForCausalLM  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    ref = torch.load(args.ref, map_location="cpu", weights_only=False)
    input_ids = ref["input_ids"].long()

    model = NemotronHForCausalLM.from_pretrained(args.model, torch_dtype=torch.bfloat16).cuda().eval()
    caps = {}

    def mk(k):
        def hook(m, inp, outp):
            t = outp[0] if isinstance(outp, tuple) else outp
            caps[k] = t.detach().float().cpu()
        return hook

    model.model.embeddings.register_forward_hook(mk("emb"))
    for i, layer in enumerate(model.model.layers):
        layer.register_forward_hook(mk(f"L{i:02d}"))
    model.model.norm_f.register_forward_hook(mk("final"))

    with torch.no_grad():
        logits = model(input_ids.to("cuda")).logits.float().cpu()

    torch.save({"input_ids": input_ids, "logits": logits, "caps": caps}, args.out)
    for k in sorted(caps):
        print(f"[B] {k} std={float(caps[k].std()):.4f}", flush=True)
    print("B_L_DONE", flush=True)


if __name__ == "__main__":
    main()