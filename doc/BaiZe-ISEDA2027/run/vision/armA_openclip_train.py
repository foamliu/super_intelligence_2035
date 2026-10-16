#!/usr/bin/env python
"""ArmA — open_clip native ViT-B/16 from-scratch CLIP training.

Operator instruction 2026-10-16:
  "启动 vision ArmA（open_clip 从头训 encoder）"
  - open_clip 协议/框架从头训练 vision encoder (NOT custom vision/models.py)
  - open_clip 标准 ViT-B/16 224px, 86.2M visual / 149.6M total
  - 从头对比学习 (from-scratch contrastive learning, both towers random init)
  - 数据复用现有图文对 (GPIC/CC12M/Amshaker) via data.py mixed loader
  - 训完能被 open_clip.create_model_and_transforms(pretrained=<ckpt>) 加载
  - 主判据 ProtB, 对齐 ④-4ep 口径

Model : open_clip.create_model_and_transforms('ViT-B-16', pretrained=None)
Loss  : open_clip.loss.ClipLoss (standard CLIP InfoNCE, global gather, local_loss=False)
Data  : data.build_mixed_loader (GPIC json-caption + CC12M/Amshaker txt-caption),
        open_clip.get_tokenizer('ViT-B-16') as tokenizer
DDP   : torchrun --nproc_per_node=8
"""
import argparse
import glob
import math
import os
import time

import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

import open_clip
import data as D

MODEL_NAME = 'ViT-B-16'


def setup_ddp():
    rank = int(os.environ.get('RANK', 0))
    world_size = int(os.environ.get('WORLD_SIZE', 1))
    local_rank = int(os.environ.get('LOCAL_RANK', 0))
    if world_size > 1:
        dist.init_process_group(backend='nccl')
    torch.cuda.set_device(local_rank)
    return rank, world_size, local_rank


def log(rank, *a):
    if rank == 0:
        print(*a, flush=True)


def cosine_lr(step, total, warmup, lr_max, lr_min):
    """Linear warmup -> cosine decay to lr_min."""
    if step < warmup:
        return lr_max * step / max(1, warmup)
    prog = (step - warmup) / max(1, total - warmup)
    prog = min(1.0, max(0.0, prog))
    return lr_min + 0.5 * (lr_max - lr_min) * (1.0 + math.cos(math.pi * prog))


def parse_shards(data_arg, rank, world_size):
    """Comma-separated globs and/or snapshot .txt files -> rank-sliced list."""
    all_shards = []
    for _g in data_arg.split(','):
        _g = _g.strip()
        if not _g:
            continue
        if os.path.isfile(_g) and _g.endswith('.txt'):
            with open(_g) as _f:
                all_shards.extend([ln.strip() for ln in _f if ln.strip()])
        else:
            all_shards.extend(sorted(glob.glob(_g)))
    all_shards = sorted(set(all_shards))
    my_shards = all_shards[rank::world_size]
    return my_shards, all_shards

def main():
    ap = argparse.ArgumentParser(description='ArmA open_clip ViT-B/16 from-scratch CLIP')
    ap.add_argument('--data', required=True,
                    help='tar shard glob(s) / snapshot .txt, comma-separated')
    ap.add_argument('--data-source', default='mixed', choices=['mixed', 'wds'])
    ap.add_argument('--caption-type', default='all', help='GPIC caption_type filter')
    ap.add_argument('--eval-data',
                    default='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar')
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--steps', type=int, default=154500)
    ap.add_argument('--batch-size', type=int, default=256, help='per-GPU MBS')
    ap.add_argument('--lr', type=float, default=2e-3)
    ap.add_argument('--min-lr', type=float, default=2e-4)
    ap.add_argument('--warmup', type=int, default=8000)
    ap.add_argument('--wd', type=float, default=0.1)
    ap.add_argument('--beta1', type=float, default=0.9)
    ap.add_argument('--beta2', type=float, default=0.98)
    ap.add_argument('--eps', type=float, default=1e-8)
    ap.add_argument('--seed', type=int, default=1234)
    ap.add_argument('--num-workers', type=int, default=6)
    ap.add_argument('--save-every', type=int, default=10000)
    ap.add_argument('--log-every', type=int, default=20)
    ap.add_argument('--precision', default='bf16', choices=['bf16', 'amp', 'fp32'])
    ap.add_argument('--grad-clip', type=float, default=1.0)
    ap.add_argument('--resume', action='store_true',
                    help='resume from latest.pt in output-dir')
    args = ap.parse_args()

    rank, world_size, local_rank = setup_ddp()
    device = torch.device('cuda', local_rank)
    torch.manual_seed(args.seed + rank)
    os.makedirs(args.output_dir, exist_ok=True)

    # ---- Model: open_clip ViT-B/16, from scratch ----
    model, _, _ = open_clip.create_model_and_transforms(
        MODEL_NAME, pretrained=None, precision=args.precision)
    model = model.to(device)
    n_total = sum(p.numel() for p in model.parameters())
    n_visual = sum(p.numel() for p in model.visual.parameters())
    if world_size > 1:
        model = DDP(model, device_ids=[local_rank], find_unused_parameters=False)
    raw_model = model.module if isinstance(model, DDP) else model

    # ---- Tokenizer + Loss + Optimizer ----
    tokenizer = open_clip.get_tokenizer(MODEL_NAME)
    clip_loss = open_clip.loss.ClipLoss(
        local_loss=False, gather_with_grad=False, cache_labels=True,
        rank=rank, world_size=world_size)
    trainable = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(trainable, lr=args.lr, betas=(args.beta1, args.beta2),
                            eps=args.eps, weight_decay=args.wd)


    # ---- Resume from checkpoint if requested ----
    start_step = 0
    if args.resume:
        latest_path = os.path.join(args.output_dir, 'latest.pt')
        if os.path.isfile(latest_path):
            ckpt = torch.load(latest_path, map_location='cpu')
            raw_model.load_state_dict(ckpt['state_dict'])
            start_step = ckpt.get('step', 0)
            if 'optimizer' in ckpt:
                opt.load_state_dict(ckpt['optimizer'])
            log(rank, f'[ArmA] RESUMED from {latest_path} at step {start_step}')
        else:
            log(rank, f'[ArmA] --resume but no latest.pt found, starting fresh')

    # ---- Data: rank-sliced shards via data.py mixed loader ----
    my_shards, all_shards = parse_shards(args.data, rank, world_size)
    gbs = args.batch_size * world_size
    if args.data_source == 'mixed':
        loader = D.build_mixed_loader(my_shards, args.batch_size, tokenizer,
                                      size=224, num_workers=args.num_workers,
                                      shuffle=True, train=True, drop_last=True,
                                      gpic_caption_type=args.caption_type)
    else:
        loader = D.build_loader(my_shards, args.batch_size, tokenizer,
                                size=224, num_workers=args.num_workers,
                                shuffle=True, train=True, drop_last=True)

    log(rank, f'[ArmA] open_clip {MODEL_NAME} from-scratch CLIP training')
    log(rank, f'[ArmA] visual={n_visual/1e6:.1f}M total={n_total/1e6:.1f}M '
              f'GBS={gbs} (MBS={args.batch_size}x{world_size})')
    log(rank, f'[ArmA] lr={args.lr} warmup={args.warmup} cos->min_lr={args.min_lr} '
              f'steps={args.steps} wd={args.wd} prec={args.precision}')
    log(rank, f'[ArmA] data={args.data}')
    log(rank, f'[ArmA] shards: total={len(all_shards)} rank={rank}={len(my_shards)}')
    log(rank, f'[ArmA] ~{len(all_shards)*10900/1e6:.1f}M pairs (approx)')
    log(rank, f'[ArmA] output_dir={args.output_dir}')

    # ---- Training loop ----
    if args.precision == 'bf16':
        autocast_ctx = torch.autocast('cuda', dtype=torch.bfloat16)
    elif args.precision == 'amp':
        autocast_ctx = torch.cuda.amp.autocast()
    else:
        autocast_ctx = torch.cuda.amp.autocast(enabled=False)
    model.train()
    step = start_step
    t0 = time.time()
    loss_ema = None
    data_iter = iter(loader)

    while step < args.steps:
        try:
            imgs, texts = next(data_iter)
        except StopIteration:
            data_iter = iter(loader)
            imgs, texts = next(data_iter)
        imgs = imgs.to(device, non_blocking=True)
        texts = texts.to(device, non_blocking=True)

        lr_now = cosine_lr(step, args.steps, args.warmup, args.lr, args.min_lr)
        for pg in opt.param_groups:
            pg['lr'] = lr_now

        opt.zero_grad(set_to_none=True)
        with autocast_ctx:
            img_feat, txt_feat, logit_scale = model(imgs, texts)
            loss = clip_loss(img_feat, txt_feat, logit_scale)

        loss.backward()
        if args.grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(trainable, args.grad_clip)
        opt.step()

        loss_val = loss.detach().item()
        loss_ema = loss_val if loss_ema is None else 0.98 * loss_ema + 0.02 * loss_val
        step += 1

        if step % args.log_every == 0 and rank == 0:
            el = time.time() - t0
            sps = step / el
            eta_h = (args.steps - step) / sps / 3600
            log(rank, f'[ArmA] step {step}/{args.steps} loss={loss_ema:.4f} '
                      f'lr={lr_now:.2e} {sps:.2f} it/s ETA={eta_h:.1f}h '
                      f'C1~{math.exp(-loss_ema):.4f} t={el/60:.1f}min')

        if step % args.save_every == 0 or step == args.steps:
            if rank == 0:
                ckpt_path = os.path.join(args.output_dir, f'checkpoint_{step}.pt')
                payload = {'state_dict': raw_model.state_dict(), 'step': step,
                           'model_name': MODEL_NAME, 'loss': loss_ema,
                           'optimizer': opt.state_dict()}
                torch.save(payload, ckpt_path)
                torch.save(payload, os.path.join(args.output_dir, 'latest.pt'))
                log(rank, f'[ArmA] saved {ckpt_path} + latest.pt (loss={loss_ema:.4f})')
            if world_size > 1:
                dist.barrier()

    log(rank, f'[ArmA] DONE step={step} loss={loss_ema:.4f} '
              f'time={(time.time()-t0)/3600:.2f}h')
    if world_size > 1:
        dist.destroy_process_group()


if __name__ == '__main__':
    main()

