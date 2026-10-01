#!/usr/bin/env python
"""R8 ImageNet-1k evaluation: zero-shot top-1/5 + linear-probe top-1.

IN-1k on-disk facts (verified by agent):
  - /nas_train/app.e0031982/datasets/imagenet-1k/data/train-*.parquet : 1,281,167
    LABELED images (label 0..999), image.bytes embedded (ImageNet train filenames).
  - .../data/test-*.parquet : 100,000 images with label = -1 (UNLABELED) -> NOT a val set.
  - => NO official 50k validation split on disk. Per R8.5 we SELF-SPLIT from train:
        val        = first 50 images/class = 50,000 (deterministic file order)
        probe-train= next  50 images/class = 50,000 (for the linear classifier)
    This split is disjoint from R8's training data (Stanford GPIC), so it is a clean
    OUT-OF-DOMAIN held-out for the 6 GPIC-trained architectures.

Zero-shot: frozen CLIP-768 text tower + open_clip IMAGENET_CLASSNAMES x 80 templates.
Linear-probe: sklearn multinomial logistic regression on FROZEN trunk features
    (raw, non-L2-normalized), trained on probe-train, evaluated on val. Fixed protocol.

Decodes the 100k IN-1k images ONCE, then evaluates every checkpoint in --ckpts.
Usage:
  python r8_eval_in1k.py --ckpts ckpt1.pt ckpt2.pt ... [--max-files 40] [--bs 128]
"""
import argparse
import glob

import torch
from PIL import Image

import models
from models import get_vision_tower, ReadoutHead
from r7_train import FrozenClipText, CLIP_PATH, EMBED
from open_clip import IMAGENET_CLASSNAMES, OPENAI_IMAGENET_TEMPLATES

IN1K = '/nas_train/app.e0031982/datasets/imagenet-1k/data/train-*.parquet'


def get_in1k_transform(size=224):
    import data as D
    return D.get_val_transform(size)


def decode_img(image_dict, size=224):
    from io import BytesIO
    raw = image_dict.get('bytes') or b''
    if not raw:
        return None
    return Image.open(BytesIO(raw)).convert('RGB')


def load_in1k_split(max_files=40, per_class=50, size=224):
    import pyarrow.parquet as pq
    tf = get_in1k_transform(size)
    files = sorted(glob.glob(IN1K))
    val_lists = {c: [] for c in range(1000)}
    probe_lists = {c: [] for c in range(1000)}
    val_cnt = {c: 0 for c in range(1000)}
    probe_cnt = {c: 0 for c in range(1000)}
    for f in files[:max_files]:
        pf = pq.ParquetFile(f)
        table = pf.read()
        imgs = table.column('image').to_pylist()
        labels = table.column('label').to_numpy()
        for img_dict, lab in zip(imgs, labels):
            lab = int(lab)
            if val_cnt[lab] < per_class:
                img = decode_img(img_dict, size)
                if img is not None:
                    val_lists[lab].append(tf(img))
                    val_cnt[lab] += 1
            elif probe_cnt[lab] < per_class:
                img = decode_img(img_dict, size)
                if img is not None:
                    probe_lists[lab].append(tf(img))
                    probe_cnt[lab] += 1
        if sum(1 for c in range(1000) if probe_cnt[c] >= per_class) == 1000:
            break
    val = [t for c in range(1000) for t in val_lists[c][:per_class]]
    probe = [t for c in range(1000) for t in probe_lists[c][:per_class]]
    val_labels = torch.tensor([c for c in range(1000) for _ in range(len(val_lists[c][:per_class]))])
    probe_labels = torch.tensor([c for c in range(1000) for _ in range(len(probe_lists[c][:per_class]))])
    val_imgs = torch.stack(val).half()
    probe_imgs = torch.stack(probe).half()
    return val_imgs, val_labels, probe_imgs, probe_labels


def load_vision(ckpt, device):
    ck = torch.load(ckpt, map_location='cpu')
    cfg = ck.get('config', {})
    tower = cfg.get('tower', 'openvision2')
    res = cfg.get('resolution', 224)
    patch = cfg.get('patch', 16)
    embed = cfg.get('embed_dim', EMBED)
    v = get_vision_tower(tower)
    w = v.head.proj.in_features
    v.head = ReadoutHead(w, embed_dim=embed)
    if (res != 224 or patch != 16) and hasattr(v, 'embed'):
        v.embed = models.PatchEmbed(res, patch, v.embed.conv.out_channels)
        v.image_size = res
        v.patch_size = patch
    v.load_state_dict(ck['vision'])
    return v.to(device).eval()


@torch.no_grad()
def encode_images(vision, imgs, device, bs=128):
    outs = []
    for i in range(0, imgs.shape[0], bs):
        b = imgs[i:i + bs].to(device).float().to(torch.bfloat16)
        with torch.autocast('cuda', dtype=torch.bfloat16):
            outs.append(vision(b))
    return torch.cat(outs)


@torch.no_grad()
def text_class_embeddings(text, device):
    feats = []
    for name in IMAGENET_CLASSNAMES:
        caps = [t(name) for t in OPENAI_IMAGENET_TEMPLATES]
        ids = text.tokenize(caps).to(device)
        with torch.autocast('cuda', dtype=torch.bfloat16):
            z = text(ids).float()
        feats.append(z.mean(0))
    Z = torch.stack(feats)
    return torch.nn.functional.normalize(Z, dim=-1)


def zero_shot(I, Z):
    In = torch.nn.functional.normalize(I.float(), dim=-1)
    sim = In @ Z.T
    pred = sim.argmax(1)
    top5 = sim.topk(5, dim=1).indices
    return pred, top5


def linear_probe(Xtr, ytr, Xva, yva, device, epochs=100, lr=3e-3):
    """Linear classifier on raw frozen-trunk features (fixed, reproducible protocol).
    Single Linear(768 -> 1000) + softmax, AdamW, full-batch on GPU, 100 epochs."""
    d = Xtr.shape[1]
    clf = torch.nn.Linear(d, 1000).to(device)
    torch.manual_seed(0)
    opt = torch.optim.AdamW(clf.parameters(), lr=lr)
    ce = torch.nn.CrossEntropyLoss()
    for _ in range(epochs):
        opt.zero_grad()
        ce(clf(Xtr), ytr).backward()
        opt.step()
    with torch.no_grad():
        pred = clf(Xva).argmax(1)
    return (pred == yva).float().mean().item()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpts', nargs='+', required=True)
    ap.add_argument('--max-files', type=int, default=40)
    ap.add_argument('--per-class', type=int, default=50)
    ap.add_argument('--bs', type=int, default=128)
    args = ap.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    torch.backends.cudnn.benchmark = True

    print('[R8-IN1K] loading IN-1k split (val 50/class + probe 50/class) ...', flush=True)
    val_imgs, val_labels, probe_imgs, probe_labels = load_in1k_split(
        args.max_files, args.per_class)
    print(f'[R8-IN1K] val={val_imgs.shape[0]} probe={probe_imgs.shape[0]} '
          f'labels {val_labels.min().item()}/{val_labels.max().item()}', flush=True)
    val_labels = val_labels.to(device)
    probe_labels = probe_labels.to(device)

    print('[R8-IN1K] encoding text class embeddings (1000 x 80 templates) ...', flush=True)
    text = FrozenClipText(CLIP_PATH, device)
    Z = text_class_embeddings(text, device)
    print(f'[R8-IN1K] Z={tuple(Z.shape)}', flush=True)

    for ckpt in args.ckpts:
        print(f'[R8-IN1K] ckpt={ckpt}', flush=True)
        vision = load_vision(ckpt, device)
        Iv = encode_images(vision, val_imgs, device, args.bs).float()
        pred, top5 = zero_shot(Iv, Z)
        acc1 = (pred == val_labels).float().mean().item()
        acc5 = (top5 == val_labels.unsqueeze(1)).any(1).float().mean().item()

        Pprobe = encode_images(vision, probe_imgs, device, args.bs).float()
        lp1 = linear_probe(Pprobe, probe_labels, Iv, val_labels, device)

        print(f'[R8-IN1K] zero-shot top1={acc1:.4f} top5={acc5:.4f}  '
              f'linear-probe top1={lp1:.4f}', flush=True)
        del vision, Iv, Pprobe
        torch.cuda.empty_cache()

    print('[R8-IN1K] DONE', flush=True)


if __name__ == '__main__':
    main()