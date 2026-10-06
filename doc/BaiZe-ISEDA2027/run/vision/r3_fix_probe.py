#!/usr/bin/env python
"""R3 collapse fix-probe: does freezing the text tower stop the collapse?

Single-GPU, short from-scratch SigLIP runs (rand init), measures whether the
vision tower's features stay diverse (non-collapsed) at the end.
Configs: baseline (text trained) vs frozen-text (text frozen at random init).
"""
import glob, time
import numpy as np
import torch
from torch import nn
import data as D
import models
from models import get_vision_tower, EMBED_DIM
from open_clip.tokenizer import SimpleTokenizer
from open_clip.loss import SigLipLoss
from open_clip.transformer import TextTransformer


def build_text_tower():
    return TextTransformer(context_length=77, vocab_size=49408, width=512,
                           heads=8, layers=12, output_dim=EMBED_DIM)


def cosine_stats(X):
    Xn = torch.nn.functional.normalize(X.float(), dim=-1)
    G = Xn @ Xn.T
    n = X.shape[0]
    eye = torch.eye(n, dtype=torch.bool, device=X.device)
    off = G[~eye].reshape(n, n - 1)
    return off.mean().item(), off.min().item(), off.max().item()


@torch.no_grad()
def probe_collapse(vision, text, device):
    # reuse a fixed batch of eval5k images/texts to measure feature diversity
    import glob as g
    from r3_stepA_diag import load_eval_set
    pairs = load_eval_set('/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar', 224, 128)
    imgs = torch.stack([p[0] for p in pairs]).to(device)
    tok = SimpleTokenizer()
    caps = [p[1] for p in pairs]
    with torch.autocast('cuda', dtype=torch.bfloat16):
        I = vision(imgs)
        T = text(tok(caps).to(device))
    im, ix, xa = cosine_stats(I)
    tm, tx, xx = cosine_stats(T)
    In = torch.nn.functional.normalize(I.float(), dim=-1)
    Tn = torch.nn.functional.normalize(T.float(), dim=-1)
    G = Tn @ In.T
    n = G.shape[0]
    eye = torch.eye(n, dtype=torch.bool, device=G.device)
    diag = G.diagonal().mean().item()
    off = G[~eye].reshape(n, n - 1).mean().item()
    return im, tm, diag, off


def run(freeze_text, steps=200, bs=64, seed=1234, fixed_bias=False):
    device = torch.device('cuda')
    torch.backends.cudnn.benchmark = True
    torch.manual_seed(seed); np.random.seed(seed)
    vision = get_vision_tower('openvision2').to(device)
    text = build_text_tower().to(device)
    logit_scale = nn.Parameter(torch.full((), float(np.log(10)), device=device, dtype=torch.float32))
    bias_init = 0.0 if fixed_bias else -10.0
    logit_bias = nn.Parameter(torch.full((), bias_init, device=device, dtype=torch.float32), requires_grad=not fixed_bias)

    params = [logit_scale]
    if logit_bias.requires_grad:
        params.append(logit_bias)
    for p in vision.parameters():
        params.append(p)
    if not freeze_text:
        for p in text.parameters():
            params.append(p)
    else:
        for p in text.parameters():
            p.requires_grad_(False)
    opt = torch.optim.AdamW([{'params': [p for p in params if p.requires_grad]}],
                            lr=3e-3, betas=(0.9, 0.95), eps=1e-6)
    loss_fn = SigLipLoss(rank=0, world_size=1, dist_impl='bidir')
    tok = SimpleTokenizer()
    shards = sorted(glob.glob('/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'))[:2]
    loader = D.build_loader(shards, bs, tok, size=224, num_workers=2)
    it = iter(loader)
    def lr_at(s):
        w = 20
        if s < w: return 3e-3 * s / max(1, w)
        return 3e-3
    vision.train(); text.train()
    t0 = time.time()
    for s in range(steps):
        for g in opt.param_groups: g['lr'] = lr_at(s)
        try:
            imgs, txts = next(it)
        except StopIteration:
            it = iter(loader); imgs, txts = next(it)
        imgs = imgs.to(device); txts = txts.to(device)
        with torch.autocast('cuda', dtype=torch.bfloat16):
            If = vision(imgs); Tf = text(txts)
            If = torch.nn.functional.normalize(If, dim=-1)
            Tf = torch.nn.functional.normalize(Tf, dim=-1)
            loss = loss_fn(If, Tf, logit_scale, logit_bias)
        opt.zero_grad(set_to_none=True)
        loss.backward(); opt.step()
        if s % 50 == 0 or s == steps - 1:
            print(f'  [ft={freeze_text},fb={fixed_bias}] step {s}/{steps} loss={loss.item():.4f}', flush=True)
    vision.eval(); text.eval()
    im, tm, diag, off = probe_collapse(vision, text, device)
    print(f'[RESULT ft={freeze_text},fb={fixed_bias}] vision_cos_mean={im:.4f}, '
          f'text_cos_mean={tm:.4f}, cross_diag={diag:.4f}, cross_offdiag={off:.4f}, '
          f'wall={time.time()-t0:.0f}s', flush=True)
    return im, tm, diag, off


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', choices=['baseline', 'frozen', 'fixed-bias', 'all'], default='all')
    ap.add_argument('--steps', type=int, default=200)
    args = ap.parse_args()
    if args.config in ('baseline', 'all'):
        print('=== BASELINE (ft=0 text trained, fb=0 bias learned init -10) ===', flush=True)
        run(freeze_text=False, steps=args.steps)
    if args.config in ('frozen', 'all'):
        print('=== FROZEN-TEXT (ft=1 text frozen random, fb=0 bias init -10) ===', flush=True)
        run(freeze_text=True, steps=args.steps)
    if args.config in ('fixed-bias', 'all'):
        print('=== FIXED-BIAS (ft=0 text trained, fb=1 bias frozen at 0) ===', flush=True)
        run(freeze_text=False, steps=args.steps, fixed_bias=True)
    print('[ALL DONE]', flush=True)
