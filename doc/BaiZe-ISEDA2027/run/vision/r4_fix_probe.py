#!/usr/bin/env python
"""R4 Step C minimal-fix probe: does a FROZEN PRETRAINED semantic text tower stop collapse?

300-step single-GPU from-scratch vision runs measuring R4.1 criteria:
  C1 = vision same-tower off-diagonal cosine mean (collapse if > 0.9)
  C2 = cross diag - offdiag gap (should be clearly positive)
  C4 = loss trajectory.

Configs:
  A 'baseline'  : random 768w text tower JOINTLY trained + SigLIP + learnable scale/bias (negative control)
  B 'sem_siglip': FROZEN CLIP text + SigLIP + learnable scale/bias
  C 'sem_bias0' : FROZEN CLIP text + SigLIP + bias FROZEN at 0
  D 'sem_clip'  : FROZEN CLIP text + CLIP InfoNCE (learnable temp, no bias)
"""
import argparse, glob, time
import numpy as np
import torch
from torch import nn

CLIP_PATH = '/nas_train/app.e0031982/models/openai/clip-vit-large-patch14-336'
EMBED = 768


class TextEnc:
    def __init__(self, cfg, device):
        self.cfg = cfg
        if cfg == 'baseline':
            from open_clip.transformer import TextTransformer
            from open_clip.tokenizer import SimpleTokenizer
            self.model = TextTransformer(context_length=77, vocab_size=49408,
                                         width=512, heads=8, layers=12,
                                         output_dim=EMBED).to(device)
            self._tok = SimpleTokenizer()
            self.frozen = False
        else:
            from transformers import CLIPModel, CLIPTokenizer
            clip = CLIPModel.from_pretrained(CLIP_PATH, local_files_only=True)
            self._tok = CLIPTokenizer.from_pretrained(CLIP_PATH, local_files_only=True)
            for p in clip.parameters():
                p.requires_grad_(False)
            self.model = clip.to(device).eval()
            self.frozen = True

    def tok(self, caps):
        if self.frozen:
            return self._tok(caps, return_tensors='pt', padding='max_length',
                             max_length=77, truncation=True)['input_ids']
        return self._tok(caps)

    def params(self):
        return [] if self.frozen else list(self.model.parameters())

    def train_mode(self):
        if not self.frozen:
            self.model.train()

    def __call__(self, x):
        if self.frozen:
            return self.model.get_text_features(x)
        return self.model(x)


def cosine_offdiag(X):
    Xn = torch.nn.functional.normalize(X.float(), dim=-1)
    G = Xn @ Xn.T
    n = G.shape[0]
    eye = torch.eye(n, dtype=torch.bool, device=G.device)
    off = G[~eye].reshape(n, n - 1)
    return off.mean().item()


def cross_gap(I, T):
    In = torch.nn.functional.normalize(I.float(), dim=-1)
    Tn = torch.nn.functional.normalize(T.float(), dim=-1)
    G = Tn @ In.T
    n = G.shape[0]
    eye = torch.eye(n, dtype=torch.bool, device=G.device)
    diag = G.diagonal().mean().item()
    off = G[~eye].reshape(n, n - 1).mean().item()
    return diag, off


def get_vision(device):
    import models
    from models import ReadoutHead
    v = models.get_vision_tower('openvision2')
    w = v.head.proj.in_features
    v.head = ReadoutHead(w, embed_dim=EMBED)
    return v.to(device)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', choices=['baseline', 'sem_siglip', 'sem_bias0',
                                         'sem_clip', 'all'], default='all')
    ap.add_argument('--steps', type=int, default=300)
    ap.add_argument('--bs', type=int, default=64)
    args = ap.parse_args()
    device = torch.device('cuda')
    torch.backends.cudnn.benchmark = True

    import data as D
    from open_clip.loss import SigLipLoss, ClipLoss

    def run(cfg):
        torch.manual_seed(1234); np.random.seed(1234)
        vision = get_vision(device)
        text = TextEnc(cfg, device)
        text.train_mode()

        use_siglip = cfg != 'sem_clip'
        logit_scale = nn.Parameter(torch.full((), float(np.log(10)), device=device),
                                   requires_grad=True)
        if cfg in ('sem_bias0',):
            logit_bias = nn.Parameter(torch.zeros((), device=device), requires_grad=False)
        elif cfg in ('sem_clip',):
            logit_bias = None
        else:
            logit_bias = nn.Parameter(torch.full((), -10.0, device=device), requires_grad=True)
        loss_fn = SigLipLoss(rank=0, world_size=1, dist_impl='bidir') if use_siglip \
            else ClipLoss(local_loss=False, gather_with_grad=False, rank=0, world_size=1)

        params = [logit_scale]
        if logit_bias is not None and logit_bias.requires_grad:
            params.append(logit_bias)
        params += list(vision.parameters()) + text.params()
        opt = torch.optim.AdamW([{'params': [p for p in params if p.requires_grad]}],
                                lr=3e-3, betas=(0.9, 0.95), eps=1e-6)

        shards = sorted(glob.glob('/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'))[:3]
        loader = D.build_loader(shards, args.bs, text.tok, size=224, num_workers=2)
        it = iter(loader)

        def lr_at(s):
            w = 20
            return 3e-3 * (s / max(1, w)) if s < w else 3e-3

        # fixed eval batch for C1/C2
        import r3_stepA_diag as R3
        pairs = R3.load_eval_set('/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar', 224, 128)
        eimgs = torch.stack([p[0] for p in pairs]).to(device)
        ecaps = [p[1] for p in pairs]
        etok = text.tok(ecaps).to(device)

        def probe(tag):
            with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
                I = vision(eimgs)
            with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
                T = text(etok)
            c1 = cosine_offdiag(I)
            diag, off = cross_gap(I, T)
            print(f'  [{tag}] C1={c1:.4f} C2_diag={diag:.4f} off={off:.4f} gap={diag-off:+.4f}',
                  flush=True)

        t0 = time.time()
        print(f'=== CONFIG {cfg} steps={args.steps} bs={args.bs} ===', flush=True)
        for s in range(args.steps):
            for g in opt.param_groups:
                g['lr'] = lr_at(s)
            try:
                imgs, txts = next(it)
            except StopIteration:
                it = iter(loader); imgs, txts = next(it)
            imgs = imgs.to(device)
            txts = txts.to(device)
            with torch.autocast('cuda', dtype=torch.bfloat16):
                If = torch.nn.functional.normalize(vision(imgs), dim=-1)
                Tf = torch.nn.functional.normalize(text(txts), dim=-1)
                if use_siglip:
                    cur_loss = loss_fn(If, Tf, logit_scale, logit_bias)
                else:
                    cur_loss = loss_fn(If, Tf, logit_scale.exp(), None)
            opt.zero_grad(set_to_none=True)
            cur_loss.backward()
            opt.step()
            if s % 100 == 0 or s == args.steps - 1:
                print(f'  [step {s}/{args.steps}] loss={cur_loss.item():.4f} '
                      f'scale={logit_scale.item():.3f} '
                      f'bias={logit_bias.item() if logit_bias is not None else "-"}', flush=True)
        vision.eval(); text.train_mode() if False else None
        probe('FINAL')
        print(f'[RESULT {cfg}] wall={time.time()-t0:.0f}s', flush=True)

    for c in (['baseline', 'sem_siglip', 'sem_bias0', 'sem_clip']
              if args.config == 'all' else [args.config]):
        run(c)
    print('[ALL DONE]', flush=True)


if __name__ == '__main__':
    main()