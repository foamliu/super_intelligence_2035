#!/usr/bin/env python
"""R3 Step A diagnostics: is eval5k retrieval actually measuring anything?"""
import argparse, glob
import numpy as np
import torch
import data as D
import models
from models import get_vision_tower, EMBED_DIM
from open_clip.tokenizer import SimpleTokenizer
from open_clip.transformer import TextTransformer


def build_text_tower():
    return TextTransformer(context_length=77, vocab_size=49408, width=512,
                           heads=8, layers=12, output_dim=EMBED_DIM)


def inspect_keys(path):
    ckpt = torch.load(path, map_location='cpu', weights_only=False)
    keys = sorted(ckpt.keys())
    cfg = ckpt.get('config', {})
    nv = sum(p.numel() for p in ckpt['vision'].values()) if 'vision' in ckpt else 0
    has_text = 'text' in ckpt and ckpt['text'] is not None
    nt = sum(p.numel() for p in ckpt['text'].values()) if has_text else 0
    print(f'\n=== {path} ===')
    print(f'  top-level keys: {keys}')
    print(f'  config: {cfg}')
    print(f'  vision params: {nv/1e6:.1f}M | text params: {nt/1e6:.1f}M | has_text={has_text}')
    if has_text:
        v = get_vision_tower(cfg.get('tower', 'openvision2'))
        if int(cfg.get('resolution', 224)) != 224 or int(cfg.get('patch', 16)) != 16:
            v.image_size = int(cfg.get('resolution', 224))
            v.patch_size = int(cfg.get('patch', 16))
            v.embed = models.PatchEmbed(v.image_size, v.patch_size, v.embed.conv.out_channels)
        tv = build_text_tower()
        vs = set(v.state_dict().keys()); ck_vs = set(ckpt['vision'].keys())
        ts = set(tv.state_dict().keys()); ck_ts = set(ckpt['text'].keys())
        print(f'  vision keys match: {vs == ck_vs} (missing={ck_vs - vs}, extra={vs - ck_vs})')
        print(f'  text keys match:   {ts == ck_ts} (missing={ck_ts - ts}, extra={ts - ck_ts})')
    del ckpt
    torch.cuda.empty_cache()
    return has_text


def load_model(tower, ckpt_path, device):
    ckpt = torch.load(ckpt_path, map_location='cpu', weights_only=False)
    cfg = ckpt.get('config', {})
    vision = get_vision_tower(tower)
    resolution = int(cfg.get('resolution', 224))
    patch = int(cfg.get('patch', 16))
    if resolution != 224 or patch != 16:
        vision.image_size = resolution
        vision.patch_size = patch
        vision.embed = models.PatchEmbed(resolution, patch, vision.embed.conv.out_channels)
    vision.load_state_dict(ckpt['vision'])
    vision = vision.to(device).eval()
    text = build_text_tower()
    has_text = 'text' in ckpt and ckpt['text'] is not None
    if has_text:
        text.load_state_dict(ckpt['text'])
    text = text.to(device).eval()
    del ckpt
    return vision, text, has_text, cfg


def load_eval_set(shard_glob, size, n):
    import webdataset as wds
    tf = D.get_val_transform(size)
    shards = sorted(glob.glob(shard_glob))
    pairs = []
    ds = (wds.WebDataset(shards, nodesplitter=D._no_split)
          .decode('pil').to_tuple('png;jpg;img', 'txt'))
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
    I = torch.nn.functional.normalize(I, dim=-1)
    T = torch.nn.functional.normalize(T, dim=-1)
    return I, T


def recall_at_k(sim, k):
    n = sim.shape[0]
    idx = sim.topk(k, dim=1).indices
    gt = torch.arange(n, device=sim.device).unsqueeze(1)
    return (idx == gt).any(dim=1).float().mean().item()


def retrieval_report(I, T, tag):
    sim = T @ I.T
    n = sim.shape[0]
    diag = sim.diagonal()
    eye = torch.eye(n, dtype=torch.bool, device=sim.device)
    off = sim[~eye].reshape(n, n - 1)
    t2i = {k: recall_at_k(sim, k) for k in (1, 5, 10)}
    i2t = {k: recall_at_k(sim.T, k) for k in (1, 5, 10)}
    print(f'[{tag}] n={n} mean_diag={diag.mean().item():.4f} '
          f'mean_offdiag={off.mean().item():.4f} max_offdiag={off.max().item():.4f}')
    print(f'[{tag}] t2i R@1/5/10 = {t2i[1]:.4f}/{t2i[5]:.4f}/{t2i[10]:.4f}')
    print(f'[{tag}] i2t R@1/5/10 = {i2t[1]:.4f}/{i2t[5]:.4f}/{i2t[10]:.4f}')
    return sim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['keys', 'retrieval'], default='retrieval')
    ap.add_argument('--ckpts', nargs='*', default=[])
    ap.add_argument('--ckpt', default=None)
    ap.add_argument('--tower', default='openvision2')
    ap.add_argument('--eval-tar', default='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar')
    ap.add_argument('--n', type=int, default=1000)
    ap.add_argument('--batch', type=int, default=64)
    args = ap.parse_args()

    if args.mode == 'keys':
        for p in args.ckpts:
            inspect_keys(p)
        return

    device = torch.device('cuda')
    torch.backends.cudnn.benchmark = True
    vision, text, has_text, cfg = load_model(args.tower, args.ckpt, device)
    tok = SimpleTokenizer()
    eval_res = int(cfg.get('resolution', 224))
    print(f'[load] tower={args.tower} ckpt={args.ckpt} has_text={has_text} cfg={cfg}')
    pairs = load_eval_set(args.eval_tar, eval_res, args.n)
    print(f'[load] eval pairs = {len(pairs)}')
    I, T = encode(vision, text, tok, pairs, device, args.batch)
    retrieval_report(I, T, 'eval5k')
    retrieval_report(I, T, 'in-batch')
    idx = torch.randperm(len(pairs), device=device)
    sim_shuf = T[idx] @ I.T
    t2i_shuf = {k: recall_at_k(sim_shuf, k) for k in (1, 5, 10)}
    print(f'[shuffle-control] t2i R@1/5/10 = {t2i_shuf[1]:.4f}/{t2i_shuf[5]:.4f}/{t2i_shuf[10]:.4f}')
    print('[DONE]')


if __name__ == '__main__':
    main()
