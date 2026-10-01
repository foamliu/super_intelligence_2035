#!/usr/bin/env python
"""R5 multi-GPU trainer for the FIXED recipe (validated in R4, C1-C4 all passed).

Fixed recipe (per R5.1 / R4.4-D):
  - Text tower = FROZEN pretrained CLIP text encoder
      `openai/clip-vit-large-patch14-336` (768-dim), loaded via transformers
      with `local_files_only=True`.
  - Objective = open_clip.loss.ClipLoss (CLIP InfoNCE), local_loss=False so
      features are all-gathered across ranks -> world_size * batch negatives.
      Learns only logit_scale (temperature); NO logit_bias.
  - Vision readout head -> embed_dim = 768 (to align with CLIP text dim).
  - lr 3e-3, warmup 20 steps, constant thereafter (matches R4 r4_c3.py).
  - C1/C2/C4 probes every `--probe-every` (300) steps on rank 0, with the
      R5.2 fusing thresholds (abort + record if triggered).

torchrun DDP, TP1/DP8. All four candidate towers supported.
"""
import argparse
import glob
import os
import time

import numpy as np
import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP

import models
from models import get_vision_tower, param_count, active_param_count

EMBED = 768
CLIP_PATH = '/nas_train/app.e0031982/models/openai/clip-vit-large-patch14-336'


def setup(rank, world_size):
    dist.init_process_group('nccl', rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)


def cleanup():
    dist.destroy_process_group()


class FrozenClipText(nn.Module):
    """Frozen pretrained CLIP text tower (768-dim). Consistent with R4 TextEnc('sem_clip')."""

    def __init__(self, path, device):
        super().__init__()
        from transformers import CLIPModel, CLIPTokenizer
        self.tok = CLIPTokenizer.from_pretrained(path, local_files_only=True)
        clip = CLIPModel.from_pretrained(path, local_files_only=True)
        for p in clip.parameters():
            p.requires_grad_(False)
        self.clip = clip.to(device).eval()

    def tokenize(self, caps):
        return self.tok(caps, return_tensors='pt', padding='max_length',
                        max_length=77, truncation=True)['input_ids']

    def forward(self, ids):
        return self.clip.get_text_features(ids)


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


def get_vision(name, resolution, patch, device):
    v = get_vision_tower(name)
    # readout head -> EMBED (768) to align with CLIP text dim
    w = v.head.proj.in_features
    v.head = models.ReadoutHead(w, embed_dim=EMBED)
    # resolution / patch (rebuild positional embedding when != 224/16)
    if resolution != 224 or patch != 16:
        v.embed = models.PatchEmbed(resolution, patch, v.embed.conv.out_channels)
        v.image_size = resolution
        v.patch_size = patch
    return v.to(device)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tower', required=True)
    ap.add_argument('--resolution', type=int, default=224)
    ap.add_argument('--patch', type=int, default=16)
    ap.add_argument('--batch-size', type=int, default=64)
    ap.add_argument('--steps', type=int, default=3000)
    ap.add_argument('--lr', type=float, default=3e-3)
    ap.add_argument('--warmup', type=int, default=20)
    ap.add_argument('--data', required=True, help='tar shard glob (LLaVA en500k webdataset)')
    ap.add_argument('--data-source', default='wds', choices=['wds', 'gpic'],
                    help='wds=webdataset .txt captions (en500k/CC12M); gpic=GPIC tar .json captions (short only)')
    ap.add_argument('--eval-data', default='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar')
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--seed', type=int, default=1234)
    ap.add_argument('--log-every', type=int, default=50)
    ap.add_argument('--probe-every', type=int, default=300)
    ap.add_argument('--probe-n', type=int, default=128)
    ap.add_argument('--num-workers', type=int, default=2)
    args = ap.parse_args()

    rank = int(os.environ['RANK'])
    world_size = int(os.environ['WORLD_SIZE'])
    setup(rank, world_size)
    is_main = rank == 0
    device = torch.device('cuda')

    # identical init across ranks (DDP will also broadcast from rank 0)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    import data as D
    from open_clip.loss import ClipLoss

    vision = get_vision(args.tower, args.resolution, args.patch, device)
    if is_main:
        total = param_count(vision)
        active = active_param_count(vision)
        print(f'[params] tower={args.tower} total={total/1e6:.1f}M '
              f'active={active/1e6:.1f}M embed_dim={EMBED} res={args.resolution} '
              f'patch={args.patch}', flush=True)

    vision = DDP(vision, device_ids=[rank], find_unused_parameters=True)
    text = FrozenClipText(CLIP_PATH, device)

    logit_scale = nn.Parameter(torch.full((), float(np.log(10)), device=device),
                               requires_grad=True)
    loss_fn = ClipLoss(local_loss=False, gather_with_grad=False,
                       rank=rank, world_size=world_size)
    opt = torch.optim.AdamW([{'params': list(vision.parameters()) + [logit_scale]}],
                            lr=args.lr, betas=(0.9, 0.95), eps=1e-6)

    def lr_at(s):
        w = args.warmup
        return args.lr * (s / max(1, w)) if s < w else args.lr

    # rank-sliced shard list (disjoint reads across ranks)
    all_shards = sorted(glob.glob(args.data))
    my_shards = all_shards[rank::world_size]
    if args.data_source == 'gpic':
        loader = D.build_gpic_loader(my_shards, args.batch_size, text.tokenize,
                                     size=args.resolution, num_workers=args.num_workers)
    else:
        loader = D.build_loader(my_shards, args.batch_size, text.tokenize,
                                size=args.resolution, num_workers=args.num_workers)
    loader_iter = iter(loader)

    os.makedirs(args.output_dir, exist_ok=True)
    logf = open(os.path.join(args.output_dir, 'train.log'), 'a') if is_main else None

    def log(msg):
        if is_main:
            print(msg, flush=True)
            logf.write(msg + '\n')
            logf.flush()

    log(f'[start] tower={args.tower} lr={args.lr} warmup={args.warmup} bs={args.batch_size} '
        f'world={world_size} steps={args.steps} res={args.resolution} patch={args.patch} '
        f'seed={args.seed} shards={len(my_shards)}/rank objective=InfoNCE '
        f'text=frozen-CLIP-768 negatives={args.batch_size*world_size}')

# ---- fixed probe batch (rank 0): precompute once; text is FROZEN so T is constant ----
    if is_main:
        from r3_stepA_diag import load_eval_set
        t0p = time.time()
        pr = load_eval_set(args.eval_data, args.resolution, args.probe_n)
        peimgs = torch.stack([p[0] for p in pr]).to(device)
        pcap = [p[1] for p in pr]
        with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
            pT = text(text.tokenize(pcap).to(device)).float()
        log(f'[probe-setup] n={len(pr)} wall={time.time()-t0p:.0f}s')

    roll = []          # per-step wall times (training forward/backward)
    loss_ema = None
    loss_early = None
    fused = False
    fuse_reason = None

    t_start = time.time()
    step = 0
    while step < args.steps:
        for g in opt.param_groups:
            g['lr'] = lr_at(step)
        try:
            imgs, txts = next(loader_iter)
        except StopIteration:
            loader_iter = iter(loader)
            imgs, txts = next(loader_iter)

        imgs = imgs.to(device, non_blocking=True)
        txts = txts.to(device, non_blocking=True)

        t0 = time.time()
        with torch.autocast('cuda', dtype=torch.bfloat16):
            If = torch.nn.functional.normalize(vision(imgs), dim=-1)
            Tf = torch.nn.functional.normalize(text(txts), dim=-1)
            cur_loss = loss_fn(If, Tf, logit_scale.exp(), None)
        opt.zero_grad(set_to_none=True)
        cur_loss.backward()
        opt.step()

        roll.append(time.time() - t0)
        step += 1
        li = cur_loss.item()
        loss_ema = li if loss_ema is None else 0.98 * loss_ema + 0.02 * li
        if step == 50:
            loss_early = loss_ema

        if step % args.log_every == 0 or step == args.steps:
            avg_dt = float(np.mean(roll[-args.log_every:]))
            imgs_per_sec = args.batch_size * world_size / avg_dt
            log(f'[step {step}/{args.steps}] loss={li:.4f} temp={logit_scale.exp().item():.3f} '
                f'ms/iter={avg_dt*1000:.1f} image/s={imgs_per_sec:.1f} lr={lr_at(step):.2e}')

        # ---- C1/C2/C4 probe ---- #
        if is_main and step % args.probe_every == 0:
            vision_module = vision.module
            with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
                pI = vision_module(peimgs).float()
            c1 = cosine_offdiag(pI)
            diag, off = cross_gap(pI, pT)
            gap = diag - off
            c4_ok = True
            if loss_early is not None:
                c4_ok = loss_ema < loss_early - 0.01
            log(f'[PROBE step {step}] C1={c1:.4f} C2_diag={diag:.4f} C2_off={off:.4f} '
                f'C2_gap={gap:+.4f} loss_ema={loss_ema:.4f} '
                f'loss_early={loss_early if loss_early is None else round(loss_early,4)} '
                f'C4={"OK" if c4_ok else "FAIL"}')

            # R5.2 fusing thresholds
            if c1 > 0.95:
                fused, fuse_reason = True, f'C1 collapse (offdiag={c1:.4f}>0.95)@step{step}'
            elif gap <= 0.005:
                fused, fuse_reason = True, f'C2 no-gap (gap={gap:+.4f}~0)@step{step}'
            elif not c4_ok:
                fused, fuse_reason = True, f'C4 loss-not-decreasing (ema={loss_ema:.4f} vs early={loss_early:.4f})@step{step}'

        if fused:
            break

    total_wall = time.time() - t_start
    steady_img_s = args.batch_size * world_size / float(np.mean(roll[-20:])) if roll else 0.0
    log(f'[done] total={total_wall:.1f}s steps={step} steady_image_s={steady_img_s:.1f} '
        f'final_loss={loss_ema:.4f} fused={fused}')

    if is_main:
        ckpt = os.path.join(args.output_dir, 'vision.pt')
        if fused:
            ckpt = os.path.join(args.output_dir, 'vision_fused.pt')
        state = {
            'vision': dict(vision.module.state_dict()),
            'logit_scale': logit_scale.detach().cpu(),
            'config': {'tower': args.tower, 'resolution': args.resolution,
                       'patch': args.patch, 'steps': step, 'loss': 'clip_infonce',
                       'embed_dim': EMBED, 'lr': args.lr, 'warmup': args.warmup,
                       'batch_size': args.batch_size, 'world_size': world_size,
                       'seed': args.seed, 'objective': 'InfoNCE', 'text': 'frozen-CLIP-768'},
            'final_loss': loss_ema,
            'params_total': param_count(vision.module),
            'params_active': active_param_count(vision.module),
            'fused': fused,
        }
        if fused:
            state['fuse_reason'] = fuse_reason
        torch.save(state, ckpt)
        log(f'[saved] {ckpt} (fused={fused})')
        logf.close()

    cleanup()


if __name__ == '__main__':
    main()