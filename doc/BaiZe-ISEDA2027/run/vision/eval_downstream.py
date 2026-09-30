"""S5 downstream proxy: zero-shot text<->image retrieval R@K on a held-out set.

Loads a full checkpoint (vision + jointly-trained text tower, as saved by a
train.py that records 'text' in vision.pt) or a vision-only checkpoint, then
evaluates bidirectional retrieval recall on a held-out webdataset tar set.

Metrics (CLIP-style):
  - text->image: for each caption query, rank all images by cosine sim -> R@1/5/10
  - image->text: symmetric direction

Usage:
  python eval_downstream.py --tower openvision2 \
      --ckpt out/S3_openvision2/vision.pt --eval-tar 'eval/*.tar' --n 5000
"""
import argparse
import glob
import os

import torch
from open_clip.tokenizer import SimpleTokenizer
from open_clip.transformer import TextTransformer

import data as D
import models
from models import get_vision_tower, EMBED_DIM


def build_text_tower():
    return TextTransformer(context_length=77, vocab_size=49408, width=512,
                           heads=8, layers=12, output_dim=EMBED_DIM)


def load_model(tower, ckpt_path, device):
    vision = get_vision_tower(tower)
    ckpt = torch.load(ckpt_path, map_location='cpu')
    cfg = ckpt.get('config', {})
    vision.load_state_dict(ckpt['vision'])
    vision = vision.to(device).eval()

    text = build_text_tower()
    has_text = 'text' in ckpt and ckpt['text'] is not None
    if has_text:
        text.load_state_dict(ckpt['text'])
    text = text.to(device).eval()
    return vision, text, has_text, cfg


def load_eval_set(shard_glob, size, n):
    """Return a flat list of (image_tensor, caption_str) using the val transform."""
    tok = SimpleTokenizer()
    tf = D.get_val_transform(size)
    shards = sorted(glob.glob(shard_glob))
    pairs = []
    import webdataset as wds
    ds = (wds.WebDataset(shards, nodesplitter=D._no_split)
          .decode('pil')
          .to_tuple('png;jpg;img', 'txt'))
    for img, cap in ds:
        if img is None or cap is None:
            continue
        pairs.append((tf(img), (cap or '').strip()))
        if len(pairs) >= n:
            break
    return pairs


@torch.no_grad()
def encode(vision, text, tokenizer, pairs, device, bs=64):
    imgs = torch.stack([p[0] for p in pairs]).to(device)
    caps = [p[1] for p in pairs]
    I, T = [], []
    for i in range(0, len(pairs), bs):
        with torch.autocast('cuda', dtype=torch.bfloat16):
            I.append(vision(imgs[i:i + bs]))
    for i in range(0, len(caps), bs):
        tok = tokenizer(caps[i:i + bs]).to(device)
        with torch.autocast('cuda', dtype=torch.bfloat16):
            T.append(text(tok))
    I = torch.cat(I); T = torch.cat(T)
    return torch.nn.functional.normalize(I, dim=-1), torch.nn.functional.normalize(T, dim=-1)


def recall_at_k(sim, k):
    # sim[i,j] = similarity(text_i, image_j). For text->image, correct diag.
    n = sim.shape[0]
    idx = sim.topk(k, dim=1).indices
    gt = torch.arange(n, device=sim.device).unsqueeze(1)
    return (idx == gt).any(dim=1).float().mean().item()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tower', required=True)
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--eval-tar', required=True, help='held-out webdataset shard glob')
    ap.add_argument('--n', type=int, default=5000)
    ap.add_argument('--resolution', type=int, default=224)
    ap.add_argument('--batch', type=int, default=64)
    args = ap.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    torch.backends.cudnn.benchmark = True
    vision, text, has_text, cfg = load_model(args.tower, args.ckpt, device)
    tok = SimpleTokenizer()

    print(f'[S5] tower={args.tower} ckpt={args.ckpt} has_text={has_text} '
          f'cfg={cfg}', flush=True)
    pairs = load_eval_set(args.eval_tar, args.resolution, args.n)
    print(f'[S5] eval pairs = {len(pairs)}', flush=True)

    I, T = encode(vision, text, tok, pairs, device, args.batch)
    sim = T @ I.T  # (n_text, n_image)
    t2i = {k: recall_at_k(sim, k) for k in (1, 5, 10)}
    i2t = {k: recall_at_k(sim.T, k) for k in (1, 5, 10)}

    print(f'[S5] text->image R@1/5/10 = {t2i[1]:.4f} / {t2i[5]:.4f} / {t2i[10]:.4f}', flush=True)
    print(f'[S5] image->text R@1/5/10 = {i2t[1]:.4f} / {i2t[5]:.4f} / {i2t[10]:.4f}', flush=True)
    print('[S5] DONE', flush=True)


if __name__ == '__main__':
    main()