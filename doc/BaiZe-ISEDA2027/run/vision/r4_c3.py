#!/usr/bin/env python
"""R4 C3: train the WINNING config (frozen CLIP text + CLIP InfoNCE + vision scratch)
for a longer horizon, then measure eval5k retrieval R@1/5/10 (image<->text)."""
import argparse, glob, time
import numpy as np
import torch
from torch import nn

from r4_fix_probe import TextEnc, get_vision, cosine_offdiag, cross_gap, EMBED


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--steps', type=int, default=2000)
    ap.add_argument('--bs', type=int, default=64)
    args = ap.parse_args()
    device = torch.device('cuda')
    torch.backends.cudnn.benchmark = True
    torch.manual_seed(1234); np.random.seed(1234)

    import data as D
    from open_clip.loss import ClipLoss

    vision = get_vision(device)
    text = TextEnc('sem_clip', device)
    logit_scale = nn.Parameter(torch.full((), float(np.log(10)), device=device))
    loss_fn = ClipLoss(local_loss=False, gather_with_grad=False, rank=0, world_size=1)
    opt = torch.optim.AdamW([{'params': list(vision.parameters()) + [logit_scale]}],
                            lr=3e-3, betas=(0.9, 0.95), eps=1e-6)

    shards = sorted(glob.glob('/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'))[:3]
    loader = D.build_loader(shards, args.bs, text.tok, size=224, num_workers=2)
    it = iter(loader)

    def lr_at(s):
        w = 20
        return 3e-3 * (s / max(1, w)) if s < w else 3e-3

    t0 = time.time()
    for s in range(args.steps):
        for g in opt.param_groups:
            g['lr'] = lr_at(s)
        try:
            imgs, txts = next(it)
        except StopIteration:
            it = iter(loader); imgs, txts = next(it)
        imgs = imgs.to(device); txts = txts.to(device)
        with torch.autocast('cuda', dtype=torch.bfloat16):
            If = torch.nn.functional.normalize(vision(imgs), dim=-1)
            Tf = torch.nn.functional.normalize(text(txts), dim=-1)
            loss = loss_fn(If, Tf, logit_scale.exp(), None)
        opt.zero_grad(set_to_none=True)
        loss.backward(); opt.step()
        if s % 500 == 0 or s == args.steps - 1:
            print(f'[step {s}/{args.steps}] loss={loss.item():.4f} temp={logit_scale.exp().item():.3f} '
                  f'wall={time.time()-t0:.0f}s', flush=True)

    vision.eval()
    # ---- C1/C2 on a 256-sample probe ----
    from r3_stepA_diag import load_eval_set
    pr = load_eval_set('/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar', 224, 256)
    pimg = torch.stack([p[0] for p in pr]).to(device)
    pcap = [p[1] for p in pr]
    with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
        Ip = vision(pimg)
        Tp = text(text.tok(pcap).to(device))
    c1 = cosine_offdiag(Ip)
    diag, off = cross_gap(Ip, Tp)
    print(f'[C1/C2] C1={c1:.4f} cross_diag={diag:.4f} offdiag={off:.4f} gap={diag-off:+.4f}', flush=True)

    # ---- C3: full eval5k retrieval ----
    pairs = load_eval_set('/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar', 224, 5000)
    pimg = torch.stack([p[0] for p in pairs]).to(device)
    pcap = [p[1] for p in pairs]
    I, T = [], []
    bs = 256
    with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
        for i in range(0, len(pairs), bs):
            I.append(vision(pimg[i:i+bs]))
        for i in range(0, len(pcap), bs):
            T.append(text(text.tok(pcap[i:i+bs]).to(device)))
    I = torch.nn.functional.normalize(torch.cat(I), dim=-1)
    T = torch.nn.functional.normalize(torch.cat(T), dim=-1)
    sim = T @ I.T
    n = sim.shape[0]

    def R(k, mat):
        idx = mat.topk(k, dim=1).indices
        gt = torch.arange(mat.shape[0], device=mat.device).unsqueeze(1)
        return (idx == gt).any(dim=1).float().mean().item()

    t2i = {1: R(1, sim), 5: R(5, sim), 10: R(10, sim)}
    i2t = {1: R(1, sim.T), 5: R(5, sim.T), 10: R(10, sim.T)}
    print(f'[C3] eval5k n={n} t2i R@1/5/10 = {t2i[1]:.4f}/{t2i[5]:.4f}/{t2i[10]:.4f}   '
          f'i2t R@1/5/10 = {i2t[1]:.4f}/{i2t[5]:.4f}/{i2t[10]:.4f}   '
          f'(chance R@1 = {1/n:.5f})', flush=True)
    print(f'[ALL DONE] wall={time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()