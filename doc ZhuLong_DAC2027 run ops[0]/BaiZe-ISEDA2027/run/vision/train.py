"""Unified SigLIP/CLIP from-scratch pretraining of a candidate vision tower (open_clip stack).

torchrun-driven DDP; fixed shared text tower; SigLIP loss (default) or CLIP InfoNCE.
"""
import argparse
import glob
import math
import os
import time

import numpy as np
import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP

import models
from models import get_vision_tower, param_count, active_param_count, EMBED_DIM
from open_clip.transformer import TextTransformer
from open_clip.loss import SigLipLoss, ClipLoss
from open_clip.tokenizer import SimpleTokenizer
import data as D


def setup(rank, world_size):
    dist.init_process_group('nccl', rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)


def cleanup():
    dist.destroy_process_group()


class CLIP(nn.Module):
    def __init__(self, vision, text, loss_type='siglip'):
        super().__init__()
        self.visual = vision
        self.text = text
        scale_val = np.log(10) if loss_type == 'siglip' else np.log(1 / 0.07)
        self.logit_scale = nn.Parameter(torch.ones([]) * scale_val)
        self.logit_bias = nn.Parameter(torch.ones([]) * -10.0) if loss_type == 'siglip' else None

    def encode_image(self, img):
        return self.visual(img)

    def encode_text(self, txt):
        return self.text(txt)


def build_text_tower(embed_dim=EMBED_DIM):
    return TextTransformer(context_length=77, vocab_size=49408, width=512,
                           heads=8, layers=12, output_dim=embed_dim)


def cosine_schedule(base_lr, warmup, total, min_lr):
    def lr_at(step):
        if step < warmup:
            return base_lr * step / max(1, warmup)
        p = (step - warmup) / max(1, total - warmup)
        return min_lr + 0.5 * (base_lr - min_lr) * (1 + math.cos(math.pi * p))
    return lr_at


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tower', required=True)
    ap.add_argument('--resolution', type=int, default=224)
    ap.add_argument('--patch', type=int, default=16)
    ap.add_argument('--batch-size', type=int, default=32)
    ap.add_argument('--steps', type=int, default=1000)
    ap.add_argument('--lr', type=float, default=1e-3)
    ap.add_argument('--min-lr', type=float, default=1e-5)
    ap.add_argument('--wd', type=float, default=0.1)
    ap.add_argument('--warmup', type=int, default=100)
    ap.add_argument('--loss', choices=['siglip', 'clip'], default='siglip')
    ap.add_argument('--data', required=True, help='tar shard glob')
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--seed', type=int, default=1234)
    ap.add_argument('--log-every', type=int, default=10)
    ap.add_argument('--num-workers', type=int, default=2)
    args = ap.parse_args()

    rank = int(os.environ['RANK'])
    world_size = int(os.environ['WORLD_SIZE'])
    setup(rank, world_size)
    is_main = rank == 0
    device = torch.device('cuda')

    torch.manual_seed(args.seed + rank)
    np.random.seed(args.seed + rank)
    torch.backends.cudnn.benchmark = True

    vision = get_vision_tower(args.tower)
    vision.image_size = args.resolution
    vision.patch_size = args.patch
    if args.resolution != 224 or args.patch != 16:
        vision.embed = models.PatchEmbed(args.resolution, args.patch,
                                         vision.embed.conv.out_channels)
    text = build_text_tower()
    model = CLIP(vision, text, args.loss).to(device)
    model = DDP(model, device_ids=[rank], find_unused_parameters=False)

    n_total = param_count(vision)
    if is_main:
        msg = f'[model] {args.tower} vision params={n_total/1e6:.1f}M'
        if args.tower == 'moevie':
            msg += f' (active={active_param_count(vision)/1e6:.1f}M)'
        print(msg)

    if args.loss == 'siglip':
        loss_fn = SigLipLoss(dist_impl='bidir', rank=rank, world_size=world_size)
    else:
        loss_fn = ClipLoss(local_loss=False, gather_with_grad=True,
                           rank=rank, world_size=world_size)

    decay, no_decay = [], []
    for n, p in model.named_parameters():
        if p.ndim <= 1 or 'logit_scale' in n or 'logit_bias' in n or 'norm' in n or 'pos' in n:
            no_decay.append(p)
        else:
            decay.append(p)
    groups = [{'params': decay, 'weight_decay': args.wd},
              {'params': no_decay, 'weight_decay': 0.0}]
    opt = torch.optim.AdamW(groups, lr=args.lr, betas=(0.9, 0.95), eps=1e-6)
    lr_at = cosine_schedule(args.lr, args.warmup, args.steps, args.min_lr)
    tokenizer = SimpleTokenizer()
    all_shards = sorted(glob.glob(args.data))
    my_shards = all_shards[rank::world_size]
    loader = D.build_loader(my_shards, args.batch_size, tokenizer,
                            size=args.resolution, num_workers=args.num_workers)
    loader_iter = iter(loader)

    os.makedirs(args.output_dir, exist_ok=True)
    logf = open(os.path.join(args.output_dir, 'train.log'), 'a') if is_main else None

    def log(msg):
        if is_main:
            print(msg, flush=True)
            logf.write(msg + '\n')
            logf.flush()

    log(f'[start] tower={args.tower} loss={args.loss} lr={args.lr} bs={args.batch_size} '
        f'world={world_size} steps={args.steps} res={args.resolution} '
        f'patch={args.patch} seed={args.seed} shards={len(my_shards)}/rank')

    model.train()
    step = 0
    t_start = time.time()
    rolling = []
    while step < args.steps:
        for g in opt.param_groups:
            g['lr'] = lr_at(step)
        try:
            imgs, texts = next(loader_iter)
        except StopIteration:
            loader_iter = iter(loader)
            imgs, texts = next(loader_iter)

        imgs = imgs.to(device, non_blocking=True)
        texts = texts.to(device, non_blocking=True)

        t0 = time.time()
        with torch.autocast('cuda', dtype=torch.bfloat16):
            image_features = model.module.encode_image(imgs)
            text_features = model.module.encode_text(texts)
            image_features = torch.nn.functional.normalize(image_features, dim=-1)
            text_features = torch.nn.functional.normalize(text_features, dim=-1)
            if args.loss == 'siglip':
                cur_loss = loss_fn(image_features, text_features,
                                   model.module.logit_scale, model.module.logit_bias)
            else:
                cur_loss = loss_fn(image_features, text_features,
                                   model.module.logit_scale.exp(), None)

        opt.zero_grad(set_to_none=True)
        cur_loss.backward()
        opt.step()

        rolling.append(time.time() - t0)
        step += 1

        if step % args.log_every == 0 or step == args.steps:
            avg_dt = np.mean(rolling[-args.log_every:])
            imgs_per_sec = args.batch_size * world_size / avg_dt
            log(f'[step {step}/{args.steps}] loss={cur_loss.item():.4f} '
                f'ms/iter={avg_dt*1000:.1f} image/s={imgs_per_sec:.1f} lr={lr_at(step):.2e}')

    total = time.time() - t_start
    log(f'[done] total={total:.1f}s steps={args.steps} '
        f'steady_image_s={args.batch_size*world_size/np.mean(rolling[-20:]):.1f}')

    if is_main:
        ckpt = os.path.join(args.output_dir, 'vision.pt')
        torch.save({'vision': model.module.visual.state_dict(),
                    'text': model.module.text.state_dict(),
                    'logit_scale': model.module.logit_scale.detach().cpu(),
                    'logit_bias': (model.module.logit_bias.detach().cpu()
                                   if model.module.logit_bias is not None else None),
                    'config': {'tower': args.tower, 'resolution': args.resolution,
                               'patch': args.patch, 'steps': args.steps, 'loss': args.loss}},
                   ckpt)
        log(f'[saved] {ckpt}')
        logf.close()
    cleanup()


if __name__ == '__main__':
    main()