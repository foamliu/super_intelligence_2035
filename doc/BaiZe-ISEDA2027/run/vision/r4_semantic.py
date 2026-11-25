#!/usr/bin/env python
"""R4 decisive semantic-comparison: does truncation / caption-granularity degrade
negative-sample distinctiveness?

Loads a FROZEN pretrained CLIP text tower (semantic encoder) and measures, for each
caption source, the pairwise off-diagonal cosine of text embeddings:
  - LLaVA imagenet/EN  (truncated to 77, exactly what training feeds)
  - GPIC tag / short / medium / long
High off-diagonal cosine => different samples' text looks near-identical => the
"negatives" in contrastive loss carry no signal => collapse driver.

Also reports a random-init text tower baseline (S5) for reference.
"""
import argparse
import glob
import tarfile
import json
import collections
import torch
import numpy as np

CLIP_PATH = '/nas_train/app.e0031982/models/openai/clip-vit-large-patch14-336'
EN500K = '/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'
GPIC = '/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar'


def read_llava(n):
    caps = []
    for sp in sorted(glob.glob(EN500K)):
        tf = tarfile.open(sp)
        for m in tf.getmembers():
            if not m.name.endswith('.txt'):
                continue
            cap = tf.extractfile(m).read().decode('utf-8', 'replace').strip()
            if cap:
                caps.append(cap)
            if len(caps) >= n:
                tf.close()
                return caps
        tf.close()
    return caps


def read_gpic(n_per_type):
    shards = sorted(glob.glob(GPIC))
    acc = collections.defaultdict(list)
    for sp in shards[:12]:
        tf = tarfile.open(sp)
        for m in tf.getmembers():
            if not m.name.endswith('.json'):
                continue
            try:
                d = json.load(tf.extractfile(m))
            except Exception:
                continue
            ctype = d.get('caption_type')
            cap = (d.get('caption') or '').strip()
            if not cap or ctype not in ('tag', 'short', 'medium', 'long'):
                continue
            if len(acc[ctype]) < n_per_type:
                acc[ctype].append(cap)
        tf.close()
        if all(len(v) >= n_per_type for v in acc.values()):
            break
    return acc


def offdiag_cosine(F):
    Fn = torch.nn.functional.normalize(F.float(), dim=-1)
    G = Fn @ Fn.T
    n = G.shape[0]
    eye = torch.eye(n, dtype=torch.bool, device=G.device)
    off = G[~eye].reshape(n, n - 1)
    return off.mean().item(), off.min().item(), off.max().item(), \
        off.quantile(0.5).item(), off.quantile(0.9).item()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=1500)
    ap.add_argument('--device', default='cuda')
    args = ap.parse_args()
    device = torch.device(args.device)

    from transformers import CLIPModel, CLIPTokenizer
    print(f'[semantic] loading CLIP text tower from {CLIP_PATH}')
    clip = CLIPModel.from_pretrained(CLIP_PATH, local_files_only=True)
    tok = CLIPTokenizer.from_pretrained(CLIP_PATH, local_files_only=True)
    clip = clip.to(device).eval()
    for p in clip.parameters():
        p.requires_grad_(False)

    def embed(caps, bs=128):
        F = []
        for i in range(0, len(caps), bs):
            ids = tok(caps[i:i+bs], return_tensors='pt', padding='max_length',
                      max_length=77, truncation=True)['input_ids'].to(device)
            with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
                f = clip.get_text_features(ids)
            F.append(f.float())
        return torch.cat(F)

    print(f'\n{"source":22s} {"n":>6s} {"offdiag mean":>13s} {"min":>7s} '
          f'{"max":>7s} {"p50":>7s} {"p90":>7s}')
    # seed reproducibility
    torch.manual_seed(1234)

    # 1) LLaVA truncated
    llava = read_llava(args.n)
    F = embed(llava)
    m, mn, mx, p50, p90 = offdiag_cosine(F)
    print(f'{">LLaVA(trunc77)":22s} {len(llava):6d} {m:13.4f} {mn:7.4f} {mx:7.4f} {p50:7.4f} {p90:7.4f}')

    # 2) GPIC per type
    gpic = read_gpic(args.n)
    for ctype in ['tag', 'short', 'medium', 'long']:
        if ctype not in gpic or len(gpic[ctype]) == 0:
            print(f'{">GPIC-"+ctype:22s} {"0":6d}')
            continue
        caps = gpic[ctype][:args.n]
        F = embed(caps)
        m, mn, mx, p50, p90 = offdiag_cosine(F)
        print(f'{">GPIC-"+ctype:22s} {len(caps):6d} {m:13.4f} {mn:7.4f} {mx:7.4f} {p50:7.4f} {p90:7.4f}')

    # 3) random-init text tower baseline (S5) using open_clip TextTransformer width=512
    from open_clip.transformer import TextTransformer
    from models import EMBED_DIM
    rnd = TextTransformer(context_length=77, vocab_size=49408, width=512,
                          heads=8, layers=12, output_dim=EMBED_DIM).to(device).eval()
    cap_sub = llava[:600]
    ids = tok(cap_sub, return_tensors='pt', padding='max_length',
              max_length=77, truncation=True)['input_ids'].to(device)
    with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
        Fr = rnd(ids).float()
    m, mn, mx, p50, p90 = offdiag_cosine(Fr)
    print(f'{">RANDOM-text(512w)":22s} {len(cap_sub):6d} {m:13.4f} {mn:7.4f} {mx:7.4f} {p50:7.4f} {p90:7.4f}')

    print('[DONE]')


if __name__ == '__main__':
    main()