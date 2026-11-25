#!/usr/bin/env python
"""Pinpoint collapse: which tower, and what does the feature spread look like?"""
import glob, torch
import data as D
from open_clip.tokenizer import SimpleTokenizer
from r3_stepA_diag import load_model, load_eval_set, encode

def stats(X, name):
    # X: (n, d) unnormalized
    Xn = torch.nn.functional.normalize(X, dim=-1)
    G = Xn @ Xn.T
    n = X.shape[0]
    eye = torch.eye(n, dtype=torch.bool, device=X.device)
    off = G[~eye].reshape(n, n - 1)
    # per-dim mean & std of raw features (across samples)
    raw_mean = X.mean(dim=0)
    raw_std = X.std(dim=0)
    print(f'[{name}] raw_feat: per-dim mean range [{raw_mean.min().item():.3f},{raw_mean.max().item():.3f}] '
          f'per-dim std range [{raw_std.min().item():.4f},{raw_std.max().item():.4f}] '
          f'global std={X.std().item():.4f}')
    print(f'[{name}] cosine same-tower: mean_offdiag={off.mean().item():.4f} '
          f'min={off.min().item():.4f} max={off.max().item():.4f}')

@torch.no_grad()
def encode_sep(vision, text, tokenizer, pairs, device, bs=64):
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
    return torch.cat(I), torch.cat(T)

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--tower', default='openvision2')
    ap.add_argument('--n', type=int, default=256)
    args = ap.parse_args()
    device = torch.device('cuda')
    torch.backends.cudnn.benchmark = True
    vision, text, has_text, cfg = load_model(args.tower, args.ckpt, device)
    tok = SimpleTokenizer()
    pairs = load_eval_set('/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar',
                          int(cfg.get('resolution', 224)), args.n)
    I, T = encode_sep(vision, text, tok, pairs, device)
    print(f'has_text={has_text}')
    stats(I.float(), 'IMAGE')
    stats(T.float(), 'TEXT')
    In = torch.nn.functional.normalize(I.float(), dim=-1)
    Tn = torch.nn.functional.normalize(T.float(), dim=-1)
    G = Tn @ In.T
    n = G.shape[0]
    eye = torch.eye(n, dtype=torch.bool, device=G.device)
    diag = G.diagonal(); off = G[~eye].reshape(n, n - 1)
    print(f'[CROSS] diag mean={diag.mean().item():.4f} min={diag.min().item():.4f} max={diag.max().item():.4f}')
    print(f'[CROSS] offdiag mean={off.mean().item():.4f} min={off.min().item():.4f} max={off.max().item():.4f}')
    print('[DONE]')
