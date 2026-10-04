#!/usr/bin/env python
"""R13 — OpenVision2 OFFICIAL weights (L/14 @224) IN-1k evaluation.

Purpose (ROUND -> R13, operator-approved 2026-10-04):
  load the OFFICIAL OpenVision2 vision encoder (patch14 / depth24 / width1024 /
  GELU MLP / no_ln_pre / pool=avg / final_ln_after_pool), released at
  HF `UCSC-VLAA/openvision2-vit-large-patch14-224-vision-only` (Apache-2.0),
  and evaluate on IN-1k with THE SAME protocol as our from-scratch towers.

Protocol (identical to r8_eval_in1k.py):
  - IN-1k self-split: val 50/class + probe 50/class (deterministic file order).
  - frozen-trunk linear-probe top-1 (single Linear(d -> 1000), AdamW, full-batch,
    100 epochs, seed 0) on RAW (non-L2-normalized) trunk features.
  - zero-shot: reported with an explicit protocol-mismatch caveat — the official
    OpenVision2 is GENERATIVE (patch tokens + caption decoder), its 1024-dim
    features are NOT aligned to the frozen CLIP-L/14-336 (768-dim) text space,
    so a CLIP-cosine zero-shot is not applicable / expected ~random.

Loads via the official patched open_clip shipped by the OpenVision repo
(`/tmp/ov_survey/src/convert_upload/open_clip`), `create_vision_encoder_and_transforms`.
"""
import sys
import os

# patched open_clip (official OpenVision fork) first, so `import open_clip` resolves to it.
_PATCHED_OC = "/tmp/ov_survey/src/convert_upload"
if os.path.isdir(_PATCHED_OC) and _PATCHED_OC not in sys.path:
    sys.path.insert(0, _PATCHED_OC)

import argparse

import torch
import torch.nn.functional as F

# our R8/R9 eval pipeline (same directory `run/vision/`)
import r8_eval_in1k as R8
from r8_eval_in1k import load_in1k_split, linear_probe, text_class_embeddings
from r7_train import FrozenClipText, CLIP_PATH, EMBED

REPO = "UCSC-VLAA/openvision2-vit-large-patch14-224-vision-only"
R13_DIR = "/nas_train/app.e0031982/datasets/baize-vision/r13_official"
CONFIG_PATH = os.path.join(R13_DIR, "open_clip_config.json")
BIN_PATH = os.path.join(R13_DIR, "open_clip_pytorch_model.bin")


def load_official(device):
    """Build the OFFICIAL patch14/d24 tower from the released open_clip_config.json and
    load the released open_clip_pytorch_model.bin (visual.* keys) with strict=True.
    Uses the OpenVision repo's patched open_clip `_build_vision_tower` (GELU ViT)."""
    import json
    from open_clip.model import _build_vision_tower, CLIPVisionCfg

    cfg = json.load(open(CONFIG_PATH))["model_cfg"]
    vision_cfg = CLIPVisionCfg(**cfg["vision_cfg"])
    embed_dim = cfg["embed_dim"]
    visual = _build_vision_tower(embed_dim=embed_dim, vision_cfg=vision_cfg, cast_dtype=None)

    checkpoint = torch.load(BIN_PATH, map_location="cpu")
    if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
        sd = checkpoint["state_dict"]
    else:
        sd = checkpoint
    if next(iter(sd.items()))[0].startswith("module"):
        sd = {k[7:]: v for k, v in sd.items()}
    if any(k.startswith("visual.") for k in sd):
        sd = {k.replace("visual.", ""): v for k, v in sd.items() if k.startswith("visual.")}

    visual.load_state_dict(sd, strict=True)
    n = sum(p.numel() for p in visual.parameters())
    return visual.to(device), n


@torch.no_grad()
def encode(enc, imgs, device, bs=128):
    """Encode a stack of uint8->float images [0,1] produced by load_in1k_split (R8).
    Returns pooled trunk features (float32)."""
    outs = []
    for i in range(0, imgs.shape[0], bs):
        b = imgs[i:i + bs].to(device).float().to(torch.bfloat16)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            out = enc(b)
        pooled = out[0] if isinstance(out, tuple) else out
        outs.append(pooled.float())
    return torch.cat(outs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-files", type=int, default=40)
    ap.add_argument("--per-class", type=int, default=50)
    ap.add_argument("--bs", type=int, default=128)
    args = ap.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.backends.cudnn.benchmark = True

    print("[R13] loading OFFICIAL OpenVision2 L/14 (patch14/d24) ...", flush=True)
    enc, nparams = load_official(device)
    print(f"[R13] official encoder params = {nparams/1e6:.2f} M", flush=True)

    # probe the pooled feature dim on a dummy batch
    with torch.no_grad():
        dummy = torch.zeros(1, 3, 224, 224, device=device)
        dout = enc(dummy)
        pooled = dout[0] if isinstance(dout, tuple) else dout
        feat = pooled.shape[-1]
    print(f"[R13] pooled feature dim = {feat}", flush=True)

    print("[R13] loading IN-1k split (val 50/class + probe 50/class) ...", flush=True)
    val_imgs, val_labels, probe_imgs, probe_labels = load_in1k_split(
        args.max_files, args.per_class)
    val_labels = val_labels.to(device)
    probe_labels = probe_labels.to(device)
    print(f"[R13] val={val_imgs.shape[0]} probe={probe_imgs.shape[0]} "
          f"labels {val_labels.min().item()}/{val_labels.max().item()}", flush=True)

    print("[R13] encoding val ...", flush=True)
    Iv = encode(enc, val_imgs, device, args.bs)
    print("[R13] encoding probe ...", flush=True)
    Pprobe = encode(enc, probe_imgs, device, args.bs)
    print(f"[R13] encoded val {tuple(Iv.shape)} probe {tuple(Pprobe.shape)}", flush=True)

    lp1 = linear_probe(Pprobe, probe_labels, Iv, val_labels, device)
    print(f"[R13] frozen-trunk linear-probe top1 = {lp1:.4f}", flush=True)

    # Zero-shot: only comparable if the trunk is CLIP-aligned (768-dim). The official
    # OpenVision2 is generative and 1024-dim -> report honestly, do not fake-align.
    if feat == EMBED:
        print("[R13] computing CLIP-cosine zero-shot ...", flush=True)
        text = FrozenClipText(CLIP_PATH, device)
        Z = text_class_embeddings(text, device)
        In = F.normalize(Iv.float(), dim=-1)
        sim = In @ Z.T
        acc1 = (sim.argmax(1) == val_labels).float().mean().item()
        top5 = sim.topk(5, dim=1).indices
        acc5 = (top5 == val_labels.unsqueeze(1)).any(1).float().mean().item()
        print(f"[R13] CLIP-cosine zero-shot top1={acc1:.4f} top5={acc5:.4f}", flush=True)
    else:
        print(f"[R13] zero-shot N/A: official trunk is {feat}-dim (generative, no CLIP-"
              f"aligned readout) vs frozen CLIP-L text {EMBED}-dim -> protocol mismatch, "
              f"an aligned CLIP-cosine zs would be ~random by construction.", flush=True)

    print("[R13] DONE", flush=True)


if __name__ == "__main__":
    main()