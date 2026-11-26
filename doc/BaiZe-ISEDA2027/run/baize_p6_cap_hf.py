#!/usr/bin/env python3
# P-6 对拍诊断：HF 侧逐层激活导出，与 mcore 侧 cap 逐位对比。
import argparse
import sys

sys.path.insert(0, "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5")

import torch  # noqa: E402
from transformers import NemotronHForCausalLM  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--ref", required=True)   # mcore cap pt (含 input_ids)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    ref = torch.load(args.ref, map_location="cpu")
    input_ids = ref["input_ids"].long()

    model = NemotronHForCausalLM.from_pretrained(args.model, torch_dtype=torch.bfloat16).cuda().eval()
    caps = {}

    def mk(k):
        def hook(m, inp, outp):
            t = outp[0] if isinstance(outp, tuple) else outp
            caps[k] = t.detach().float().cpu()
        return hook

    model.model.embeddings.register_forward_hook(mk("emb"))
    model.model.layers[0].register_forward_hook(mk("L0"))
    model.model.layers[1].register_forward_hook(mk("L1"))
    model.model.layers[10].register_forward_hook(mk("L10"))
    model.model.layers[55].register_forward_hook(mk("L55"))
    model.model.norm_f.register_forward_hook(mk("final"))

    with torch.no_grad():
        logits = model(input_ids.to("cuda")).logits.float().cpu()

    for k, v in caps.items():
        print(f"[B] cap {k} shape={tuple(v.shape)} std={float(v.std()):.4f}", flush=True)

    torch.save({"input_ids": input_ids, "logits": logits, "caps": caps}, args.out)
    print("B_CAP_DONE", flush=True)


if __name__ == "__main__":
    main()