#!/usr/bin/env python
"""R7.2 cross-evaluation: text<->image retrieval R@K on two held-out evals.

Loads an R5/R7 vision checkpoint (openvision2, head->768) and the SAME frozen
CLIP-768 text tower used in training (reconstructed identically), then evaluates
bidirectional retrieval on a held-out set. Two eval formats:
  --eval-type wds  : webdataset (.txt caption)  -> eval5k (LLaVA recaption)
  --eval-type gpic : GPIC tar (.json caption)   -> GPIC test (128 tar)

Usage:
  python r7_eval.py --ckpt out/R5_P0_openvision2/vision.pt \
      --eval-data '/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar' \
      --eval-type wds --n 5000
  python r7_eval.py --ckpt out/R7_B_gpic/vision.pt \
      --eval-data '/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/test/*.tar' \
      --eval-type gpic --n 5000
"""
import argparse
import glob
import io
import json

import torch

import data as D
import models
from models import get_vision_tower, ReadoutHead
from r7_train import FrozenClipText, CLIP_PATH, EMBED


def load_vision(ckpt_path, device):
    v = get_vision_tower('openvision2')
    v.head = ReadoutHead(v.head.proj.in_features, embed_dim=EMBED)
    ck = torch.load(ckpt_path, map_location='cpu')
    v.load_state_dict(ck['vision'])
    return v.to(device).eval()


def load_pairs_wds(shard_glob, size, n):
    tf = D.get_val_transform(size)
    shards = sorted(glob.glob(shard_glob))
    import webdataset as wds
    ds = (wds.WebDataset(shards, nodesplitter=D._no_split)
          .decode('pil')
          .to_tuple('png;jpg;img', 'txt'))
    pairs = []
    for img, cap in ds:
        if img is None or cap is None:
            continue
        pairs.append((tf(img), (cap or '').strip()))
        if len(pairs) >= n:
            break
    return pairs


def load_pairs_gpic(shard_glob, size, n, caption_type=None):
    tf = D.get_val_transform(size)
    import webdataset as wds
    from PIL import Image

    def dec(sample):
        try:
            meta = json.loads(sample.get('json') or b'{}')
            cap = (meta.get('caption') or '').strip()
            if caption_type and meta.get('caption_type') != caption_type:
                return None
            raw = sample.get('jpg') or sample.get('png') or sample.get('img')
            if not raw or not cap:
                return None
            return tf(Image.open(io.BytesIO(raw)).convert('RGB')), cap
        except Exception:
            return None

    shards = sorted(glob.glob(shard_glob))
    ds = (wds.WebDataset(shards, nodesplitter=D._no_split,
                         handler=wds.ignore_and_continue)
          .map(dec)
          .select(lambda s: s is not None))
    pairs = []
    for p in ds:
        pairs.append(p)
        if len(pairs) >= n:
            break
    return pairs


@torch.no_grad()
def encode(vision, text, pairs, device, bs=64):
    imgs = torch.stack([p[0] for p in pairs]).to(device)
    caps = [p[1] for p in pairs]
    I, T = [], []
    for i in range(0, len(pairs), bs):
        with torch.autocast('cuda', dtype=torch.bfloat16):
            I.append(vision(imgs[i:i + bs]))
    for i in range(0, len(caps), bs):
        ids = text.tokenize(caps[i:i + bs]).to(device)
        with torch.autocast('cuda', dtype=torch.bfloat16):
            T.append(text(ids))
    I = torch.cat(I); T = torch.cat(T)
    return torch.nn.functional.normalize(I.float(), dim=-1), \
        torch.nn.functional.normalize(T.float(), dim=-1)


def recall_at_k(sim, k):
    n = sim.shape[0]
    idx = sim.topk(k, dim=1).indices
    gt = torch.arange(n, device=sim.device).unsqueeze(1)
    return (idx == gt).any(dim=1).float().mean().item()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--eval-data', required=True, help='held-out shard glob')
    ap.add_argument('--eval-type', choices=['wds', 'gpic'], required=True)
    ap.add_argument('--caption-type', default=None,
                    help='for gpic eval: restrict to this caption_type (default: all)')
    ap.add_argument('--n', type=int, default=5000)
    ap.add_argument('--resolution', type=int, default=224)
    ap.add_argument('--batch', type=int, default=64)
    args = ap.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    torch.backends.cudnn.benchmark = True

    vision = load_vision(args.ckpt, device)
    text = FrozenClipText(CLIP_PATH, device)

    if args.eval_type == 'wds':
        pairs = load_pairs_wds(args.eval_data, args.resolution, args.n)
    else:
        pairs = load_pairs_gpic(args.eval_data, args.resolution, args.n,
                                args.caption_type)
    print(f'[R7eval] ckpt={args.ckpt} type={args.eval_type} pairs={len(pairs)}',
          flush=True)
    if not pairs:
        print('[R7eval] empty eval set, abort', flush=True)
        return

    I, T = encode(vision, text, pairs, device, args.batch)
    sim = T @ I.T  # (n_text, n_image)
    t2i = {k: recall_at_k(sim, k) for k in (1, 5, 10)}
    i2t = {k: recall_at_k(sim.T, k) for k in (1, 5, 10)}
    print(f'[R7eval] text->image R@1/5/10 = {t2i[1]:.4f} / {t2i[5]:.4f} / {t2i[10]:.4f}',
          flush=True)
    print(f'[R7eval] image->text R@1/5/10 = {i2t[1]:.4f} / {i2t[5]:.4f} / {i2t[10]:.4f}',
          flush=True)
    print('[R7eval] DONE', flush=True)


if __name__ == '__main__':
    main()