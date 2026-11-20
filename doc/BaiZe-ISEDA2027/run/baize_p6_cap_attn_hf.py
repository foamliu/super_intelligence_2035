#!/usr/bin/env python3
# P-6 诊断：HF 侧 L10 attention 内部捕获（q/k/v 投影输出 + attention 输出），用于与 mcore 对拍。
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
            t = outp[0] if isinstance(outp, (tuple, list)) else outp
            caps[k] = t.detach().float().cpu()
        return hook

    layer = model.model.layers[10]
    layer.mixer.q_proj.register_forward_hook(mk("q"))
    layer.mixer.k_proj.register_forward_hook(mk("k"))
    layer.mixer.v_proj.register_forward_hook(mk("v"))
    layer.register_forward_hook(mk("attn_out"))
    model.model.layers[9].register_forward_hook(mk("L9_in"))

    with torch.no_grad():
        model(input_ids.to("cuda")).logits.float().cpu()

    torch.save({k: v for k, v in caps.items() if v is not None}, args.out)
    for k in caps:
        print(f"[B] {k} shape={tuple(caps[k].shape)} std={float(caps[k].std()):.4f}", flush=True)
    print("B_ATTN_DONE", flush=True)


if __name__ == "__main__":
    main()