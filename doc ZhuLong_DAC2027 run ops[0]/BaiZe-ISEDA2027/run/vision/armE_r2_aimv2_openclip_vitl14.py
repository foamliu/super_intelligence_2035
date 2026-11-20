#!/usr/bin/env python
"""ArmE-R2 - open_clip ViT-L/14 (224px) + AIMv2-style dense objective.

Operator instruction 2026-10-22 14:2x (user direct order, highest priority):
  ArmE diverged (C1=0.0014, approx random at step~30000) with lr=1e-3/warmup=2000.
  Root cause: ViT-L/14(304M) is 3.5x larger than ViT-B/16(86M) but used same
  lr=1e-3 -> update magnitude too large -> repeated spikes, slow C1 recovery.
  Decision: stop ArmE, rerun as ArmE-R2 with LOWER lr + LONGER warmup.

  ArmE-R2 vs ArmE = ONLY 2 variables: peak LR 1e-3->5e-4, warmup 2000->3000.
    Tower (ViT-L/14, 304M visual / 427.6M total) / data / steps 63400 / min_lr
    1e-5 / wd 0.01 / GBS 8192 / mask 0.6 / 1:1 loss / seed 1234 ALL IDENTICAL
    to ArmE.  pretrained=None (random init, NO pretrained weights).
  ArmE-R2 vs ArmD-R2 = 3 variables: tower(B->L) + LR + warmup (report separately).

  NOTE on model name: open_clip 3.2.0 has NO 'ViT-L-14-224' built-in.  The 224px
  variant IS plain 'ViT-L/14' (image_size=224, patch=14, 256 patches, width=1024).

  Objective (AIMv2-style, identical to ArmB/ArmD/ArmE):
    loss = contrast_weight*InfoNCE + patch_loss_weight*MSE(predictor(patches[mask]), target[mask])
    contrast_weight=1.0, patch_loss_weight=1.0, mask_ratio=0.6
  Patch tokens via forward hook on visual.transformer (single forward, no double).
  L/14 has NO .trunk wrapper but the hook on visual.transformer + visual.ln_post
  works identically (verified: out=[B,257,1024]).
  Predictor is training-only auxiliary head, stripped from open_clip ckpt.
  Batch: GBS=8192 = MBS=256x8xaccum=4 (OOM-forced from MBS=512). Fallback: MBS=128/accum=8.
"""
import argparse, glob, json, math, os, time
from contextlib import nullcontext
import torch
import torch.distributed as dist
import torch.nn as nn
from torch.nn.parallel import DistributedDataParallel as DDP
import open_clip
import data as D

MODEL_NAME = 'ViT-L-14'   # open_clip 3.2.0: plain ViT-L-14 == 224px (ViT-L-14-224 NOT a built-in)
PATCH_SIZE = 14
IMAGE_SIZE = 224
N_PATCHES = (IMAGE_SIZE // PATCH_SIZE) ** 2  # (224//14)^2 = 16^2 = 256  (B/16 was 196)
PATCH_DIM = PATCH_SIZE * PATCH_SIZE * 3       # 14*14*3 = 588   (B/16 was 768)
WIDTH = 1024  # ViT-L/14 hidden dim (B/16 was 768)


class PatchPredictor(nn.Module):
    """MAE-style 2-layer decoder: patch feature -> normalised raw pixels.
    Reference: models.py:518, OpenVision src/losses/common.py (Apache-2.0)."""
    def __init__(self, width, patch_dim, hidden=None):
        super().__init__()
        hidden = hidden if hidden is not None else width
        self.fc1 = nn.Linear(width, hidden, bias=True)
        self.norm = nn.LayerNorm(hidden)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(hidden, patch_dim, bias=True)
        nn.init.normal_(self.fc2.weight, std=0.02)
        nn.init.zeros_(self.fc2.bias)

    def forward(self, x):
        x = self.fc1(x)
        x = self.norm(x)
        x = self.act(x)
        return self.fc2(x)


def mae_norm_pix_target(imgs, patch_size):
    """MAE norm_pix_loss target (r9_train.py:298, OpenVision Apache-2.0)."""
    mean = torch.tensor(D.MEAN, device=imgs.device, dtype=imgs.dtype).view(1,3,1,1)
    std = torch.tensor(D.STD, device=imgs.device, dtype=imgs.dtype).view(1,3,1,1)
    raw = imgs * std + mean
    B, C, H, W = raw.shape
    p = patch_size
    g = H // p
    raw = raw.reshape(B, C, g, p, g, p).permute(0,2,4,1,3,5).reshape(B, g*g, C*p*p)
    mean_pp = raw.mean(dim=-1, keepdim=True)
    std_pp = raw.std(dim=-1, keepdim=True).clamp(min=1e-6)
    return (raw - mean_pp) / std_pp


class ArmEModel(nn.Module):
    """Wraps open_clip CLIP + PatchPredictor for unified DDP.
    Forward hook on visual.transformer captures (B,257,1024) for ViT-L/14
    (1 cls + 256 patches) -> patch_tokens = ln_post(out[:,1:]) = (B,256,1024),
    from the SAME forward — zero extra compute.  Renamed from ArmBModel."""
    def __init__(self, clip_model, predictor):
        super().__init__()
        self.clip = clip_model
        self.predictor = predictor
        self._captured = {}
        self.clip.visual.transformer.register_forward_hook(self._hook_fn)

    def _hook_fn(self, module, input, output):
        self._captured['transformer_out'] = output

    def forward(self, imgs, texts):
        img_feat, txt_feat, logit_scale = self.clip(imgs, texts)
        transformer_out = self._captured['transformer_out']
        patch_tokens = self.clip.visual.ln_post(transformer_out[:, 1:])
        return img_feat, txt_feat, logit_scale, patch_tokens


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
    if step < warmup:
        return lr_max * step / max(1, warmup)
    prog = (step - warmup) / max(1, total - warmup)
    prog = min(1.0, max(0.0, prog))
    return lr_min + 0.5 * (lr_max - lr_min) * (1.0 + math.cos(math.pi * prog))


def parse_shards(data_arg, rank, world_size):
    """LPT byte-balanced shard assignment (same as ArmA)."""
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
    if world_size <= 1:
        return list(all_shards), all_shards
    sizes = []
    for s in all_shards:
        try:
            sizes.append(os.path.getsize(s))
        except OSError:
            sizes.append(0)
    pairs = sorted(zip(sizes, all_shards), key=lambda x: -x[0])
    rank_shards = [[] for _ in range(world_size)]
    rank_bytes = [0] * world_size
    for sz, sh in pairs:
        r = min(range(world_size), key=lambda i: rank_bytes[i])
        rank_shards[r].append(sh)
        rank_bytes[r] += sz
    if rank == 0:
        bal = ' '.join(f'r{r}={rank_bytes[r]/1e9:.2f}GB/{len(rank_shards[r])}t'
                       for r in range(world_size))
        mx, mn = max(rank_bytes), min(rank_bytes)
        log(0, f'[ArmE-R2] LPT shard balance: {bal} spread={(mx-mn)/1e9:.2f}GB '
              f'({(mx-mn)/mx*100:.1f}% imbalance)')
    return rank_shards[rank], all_shards


def main():
    ap = argparse.ArgumentParser(description='ArmE open_clip ViT-L/14 (224px) + AIMv2-style')
    ap.add_argument('--data', required=True)
    ap.add_argument('--data-source', default='mixed', choices=['mixed','wds'])
    ap.add_argument('--caption-type', default='all')
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--steps', type=int, default=42940)
    ap.add_argument('--batch-size', type=int, default=512, help='per-GPU MBS')
    ap.add_argument('--accumulate', type=int, default=2)
    ap.add_argument('--lr', type=float, default=5e-4)
    ap.add_argument('--min-lr', type=float, default=1e-4)
    ap.add_argument('--warmup', type=int, default=3000)
    ap.add_argument('--wd', type=float, default=0.1)
    ap.add_argument('--beta1', type=float, default=0.9)
    ap.add_argument('--beta2', type=float, default=0.98)
    ap.add_argument('--eps', type=float, default=1e-8)
    ap.add_argument('--seed', type=int, default=1234)
    ap.add_argument('--num-workers', type=int, default=12)
    ap.add_argument('--save-every', type=int, default=10000)
    ap.add_argument('--log-every', type=int, default=20)
    ap.add_argument('--precision', default='bf16', choices=['bf16','amp','fp32'])
    ap.add_argument('--grad-clip', type=float, default=1.0)
    ap.add_argument('--contrast-weight', type=float, default=1.0)
    ap.add_argument('--patch-loss-weight', type=float, default=1.0)
    ap.add_argument('--mask-ratio', type=float, default=0.6)
    ap.add_argument('--persistent-workers', action='store_true', default=True)
    ap.add_argument('--prefetch-factor', type=int, default=4)
    ap.add_argument('--pin-memory', action='store_true', default=True)
    ap.add_argument('--cudnn-benchmark', action='store_true', default=True)
    ap.add_argument('--fused-adamw', action='store_true', default=True)
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--keep-ckpts', type=int, default=2)
    args = ap.parse_args()

    rank, world_size, local_rank = setup_ddp()
    device = torch.device('cuda', local_rank)
    torch.manual_seed(args.seed + rank)
    os.makedirs(args.output_dir, exist_ok=True)
    if args.cudnn_benchmark:
        torch.backends.cudnn.benchmark = True

    # ---- Model: open_clip ViT-L/14, from scratch ----
    clip_model, _, _ = open_clip.create_model_and_transforms(
        MODEL_NAME, pretrained=None)
    n_total = sum(p.numel() for p in clip_model.parameters())
    n_visual = sum(p.numel() for p in clip_model.visual.parameters())
    predictor = PatchPredictor(width=WIDTH, patch_dim=PATCH_DIM)
    n_pred = sum(p.numel() for p in predictor.parameters())
    model = ArmEModel(clip_model, predictor).to(device)
    if world_size > 1:
        model = DDP(model, device_ids=[local_rank], find_unused_parameters=False)
    raw_model = model.module if isinstance(model, DDP) else model

    gbs = args.batch_size * world_size * args.accumulate
    log(rank, f'[ArmE-R2] open_clip {MODEL_NAME} + AIMv2-style dense objective')
    log(rank, f'[ArmE-R2] visual={n_visual/1e6:.1f}M total_clip={n_total/1e6:.1f}M '
              f'predictor={n_pred/1e6:.2f}M GBS={gbs} '
              f'(MBS={args.batch_size}x{world_size}xaccum={args.accumulate})')
    log(rank, f'[ArmE-R2] lr={args.lr} warmup={args.warmup} cos->min_lr={args.min_lr} '
              f'steps={args.steps} wd={args.wd} prec={args.precision}')
    log(rank, f'[ArmE-R2] contrast_w={args.contrast_weight} '
              f'patch_w={args.patch_loss_weight} mask={args.mask_ratio}')

    tokenizer = open_clip.get_tokenizer(MODEL_NAME)
    clip_loss = open_clip.loss.ClipLoss(
        local_loss=False, gather_with_grad=False, cache_labels=True,
        rank=rank, world_size=world_size)
    trainable = [p for p in model.parameters() if p.requires_grad]
    try:
        opt = torch.optim.AdamW(trainable, lr=args.lr, betas=(args.beta1, args.beta2),
                                eps=args.eps, weight_decay=args.wd, fused=args.fused_adamw)
        if args.fused_adamw and rank == 0:
            log(rank, '[ArmE-R2] AdamW fused=True')
    except (TypeError, RuntimeError):
        log(rank, '[ArmE-R2] fused AdamW unavailable, standard AdamW')
        opt = torch.optim.AdamW(trainable, lr=args.lr, betas=(args.beta1, args.beta2),
                                eps=args.eps, weight_decay=args.wd)

    my_shards, all_shards = parse_shards(args.data, rank, world_size)
    if args.data_source == 'mixed':
        loader = D.build_mixed_loader(
            my_shards, batch_size=args.batch_size, tokenizer=tokenizer,
            size=IMAGE_SIZE, num_workers=args.num_workers, shuffle=True, train=True,
            drop_last=True, gpic_caption_type=args.caption_type,
            persistent_workers=args.persistent_workers,
            prefetch_factor=args.prefetch_factor, pin_memory=args.pin_memory)
    else:
        loader = D.build_loader(
            my_shards, batch_size=args.batch_size, tokenizer=tokenizer,
            size=IMAGE_SIZE, num_workers=args.num_workers, shuffle=True, train=True,
            drop_last=True, persistent_workers=args.persistent_workers,
            prefetch_factor=args.prefetch_factor, pin_memory=args.pin_memory)
    log(rank, f'[ArmE-R2] shards: total={len(all_shards)} rank={rank}={len(my_shards)}')
    log(rank, f'[ArmE-R2] output_dir={args.output_dir}')

    start_step = 0
    resumed_loss = None
    latest_path = os.path.join(args.output_dir, 'latest.pt')
    if args.resume and os.path.isfile(latest_path):
        ckpt = torch.load(latest_path, map_location='cpu')
        raw_model.load_state_dict(ckpt['model_state_dict'])
        if 'optimizer' in ckpt:
            opt.load_state_dict(ckpt['optimizer'])
        start_step = ckpt.get('step', 0)
        resumed_loss = ckpt.get('loss')
        log(rank, f'[ArmE-R2] resumed from step {start_step} (loss={resumed_loss})')

    if args.precision == 'bf16':
        autocast_ctx = torch.autocast('cuda', dtype=torch.bfloat16)
    elif args.precision == 'amp':
        autocast_ctx = torch.cuda.amp.autocast()
    else:
        autocast_ctx = torch.cuda.amp.autocast(enabled=False)

    model.train()
    step = start_step
    t0 = time.time()
    loss_ema = resumed_loss
    contr_ema = None
    patch_ema = None
    data_iter = iter(loader)
    peak_mem = 0

    while step < args.steps:
        lr_now = cosine_lr(step, args.steps, args.warmup, args.lr, args.min_lr)
        for pg in opt.param_groups:
            pg['lr'] = lr_now
        opt.zero_grad(set_to_none=True)
        for accum in range(args.accumulate):
            is_last = (accum == args.accumulate - 1)
            sync_ctx = nullcontext() if is_last else model.no_sync()
            try:
                imgs, texts = next(data_iter)
            except StopIteration:
                data_iter = iter(loader)
                imgs, texts = next(data_iter)
            imgs = imgs.to(device, non_blocking=True)
            texts = texts.to(device, non_blocking=True)
            with sync_ctx:
                with autocast_ctx:
                    img_feat, txt_feat, logit_scale, patch_tokens = model(imgs, texts)
                    contrastive = clip_loss(img_feat, txt_feat, logit_scale)
                    B = imgs.shape[0]
                    target = mae_norm_pix_target(imgs, PATCH_SIZE)
                    mrand = torch.rand(B, N_PATCHES, device=device) < args.mask_ratio
                    pred = raw_model.predictor(patch_tokens[mrand])
                    tgt = target[mrand]
                    patch_loss = torch.mean((pred.float() - tgt.float()) ** 2)
                    loss = (args.contrast_weight * contrastive
                            + args.patch_loss_weight * patch_loss)
                    loss = loss / args.accumulate
                loss.backward()
        if args.grad_clip > 0:
            torch.nn.utils.clip_grad_norm_(trainable, args.grad_clip)
        opt.step()

        if rank == 0:
            mem = torch.cuda.max_memory_allocated() / 1e9
            if mem > peak_mem:
                peak_mem = mem
        contr_v = contrastive.detach().item()
        patch_v = patch_loss.detach().item()
        loss_v = args.contrast_weight * contr_v + args.patch_loss_weight * patch_v
        loss_ema = loss_v if loss_ema is None else 0.98*loss_ema + 0.02*loss_v
        contr_ema = contr_v if contr_ema is None else 0.98*contr_ema + 0.02*contr_v
        patch_ema = patch_v if patch_ema is None else 0.98*patch_ema + 0.02*patch_v
        step += 1

        if step % args.log_every == 0 and rank == 0:
            el = time.time() - t0
            sps = (step - start_step) / el
            eta_h = (args.steps - step) / sps / 3600
            log(rank, f'[ArmE-R2] step {step}/{args.steps} loss={loss_ema:.4f} '
                      f'contr={contr_ema:.4f} patch={patch_ema:.4f} '
                      f'lr={lr_now:.2e} {sps:.2f} it/s ETA={eta_h:.1f}h '
                      f'C1~{math.exp(-contr_ema):.4f} peak={peak_mem:.1f}GB '
                      f't={el/60:.1f}min')

        if step % args.save_every == 0 or step == args.steps:
            if rank == 0:
                payload = {'model_state_dict': raw_model.state_dict(),
                           'step': step, 'loss': loss_ema,
                           'contrast_loss': contr_ema, 'patch_loss': patch_ema,
                           'optimizer': opt.state_dict(), 'config': vars(args)}
                ckpt_path = os.path.join(args.output_dir, f'checkpoint_{step}.pt')
                torch.save(payload, ckpt_path)
                torch.save(payload, latest_path)
                torch.save(raw_model.clip.state_dict(),
                           os.path.join(args.output_dir, 'open_clip_state_dict.pt'))
                torch.save(raw_model.predictor.state_dict(),
                           os.path.join(args.output_dir, 'predictor.pt'))
                with open(os.path.join(args.output_dir, 'config.json'), 'w') as f:
                    json.dump({**vars(args), 'step': step, 'loss': loss_ema,
                               'n_total': n_total, 'n_visual': n_visual,
                               'n_predictor': n_pred, 'model_name': MODEL_NAME,
                               'patch_size': PATCH_SIZE, 'image_size': IMAGE_SIZE,
                               'n_patches': N_PATCHES}, f, indent=2)
                log(rank, f'[ArmE-R2] saved ckpt step={step} loss={loss_ema:.4f} '
                          f'contr={contr_ema:.4f} patch={patch_ema:.4f}')
                if args.keep_ckpts > 0:
                    olds = sorted(glob.glob(
                        os.path.join(args.output_dir, 'checkpoint_*.pt')))
                    while len(olds) > args.keep_ckpts:
                        oldest = olds.pop(0)
                        os.remove(oldest)
                        log(rank, f'[ArmE-R2] removed old ckpt {os.path.basename(oldest)}')
            if world_size > 1:
                dist.barrier()

    log(rank, f'[ArmE-R2] DONE step={step} loss={loss_ema:.4f} '
              f'contr={contr_ema:.4f} patch={patch_ema:.4f} '
              f'time={(time.time()-t0)/3600:.2f}h peak={peak_mem:.1f}GB')
    if world_size > 1:
        dist.destroy_process_group()


if __name__ == '__main__':
    main()
