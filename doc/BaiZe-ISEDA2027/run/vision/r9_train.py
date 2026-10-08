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
import math
import os
import time

import numpy as np
import torch
import torch.distributed as dist
from torch import nn
from torch.nn.parallel import DistributedDataParallel as DDP

import models
from models import get_vision_tower, param_count, active_param_count, CoCaDecoder, PatchPredictor, ARTextDecoder

EMBED = 768
CLIP_PATH = '/nas_train/app.e0031982/models/openai/clip-vit-large-patch14-336'


def setup(rank, world_size):
    dist.init_process_group('nccl', rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)


def cleanup():
    dist.destroy_process_group()


class LoRAParam(nn.Module):
    """R11-L2: low-rank additive parametrization for a Linear weight.

    Implemented via torch.nn.utils.parametrize so the pretrained weight stays frozen
    in-place and only lora_A/lora_B are trainable. lora_B is *zero*-initialised, so at
    step 0 the effective weight == the frozen CLIP weight (no cold-start drift: the
    LoRA arm starts byte-identical to the frozen baseline).
    """

    def __init__(self, in_features, out_features, rank, alpha):
        super().__init__()
        self.rank = rank
        self.scale = alpha / (rank if rank > 0 else 1)
        self.lora_A = nn.Parameter(torch.zeros(rank, in_features))
        self.lora_B = nn.Parameter(torch.zeros(out_features, rank))
        nn.init.kaiming_uniform_(self.lora_A, a=math.sqrt(5))
        nn.init.zeros_(self.lora_B)

    def forward(self, W):
        return W + self.scale * (self.lora_B @ self.lora_A)


class FrozenClipText(nn.Module):
    """Pretrained CLIP text tower (768-dim).

    finetune='frozen' (R4/R9/R10/R11-L baseline): every param frozen (default).
    finetune='lora'   (R11-L2 arm): inject zero-init LoRA on q_proj+v_proj of each of
       the 12 BERT encoder layers; pretrained weights stay frozen, only lora_A/lora_B
       are trainable.
    """

    def __init__(self, path, device, finetune='frozen', lora_rank=8, lora_alpha=16.0):
        super().__init__()
        from transformers import CLIPModel, CLIPTokenizer
        self.tok = CLIPTokenizer.from_pretrained(path, local_files_only=True)
        clip = CLIPModel.from_pretrained(path, local_files_only=True)
        for p in clip.parameters():
            p.requires_grad_(False)
        self.finetune = finetune
        if finetune == 'lora':
            from torch.nn.utils.parametrize import register_parametrization
            for layer in clip.text_model.encoder.layers:
                for proj_name in ('q_proj', 'v_proj'):
                    proj = getattr(layer.self_attn, proj_name)
                    out_f, in_f = proj.weight.shape
                    register_parametrization(
                        proj, 'weight', LoRAParam(in_f, out_f, lora_rank, lora_alpha))
        elif finetune != 'frozen':
            raise ValueError(f"unknown text-finetune mode {finetune!r}")
        self.clip = clip.to(device).eval()

    def trainable_params(self):
        return [p for p in self.clip.parameters() if p.requires_grad]

    def text_module(self):
        c = self.clip
        return c.module if isinstance(c, DDP) else c

    def tokenize(self, caps):
        return self.tok(caps, return_tensors='pt', padding='max_length',
                        max_length=77, truncation=True)['input_ids']

    def tokenize_cap(self, caps):
        """Caption tokens with attention mask (for autoregressive caption CE)."""
        out = self.tok(caps, return_tensors='pt', padding='max_length',
                       max_length=77, truncation=True)
        return out['input_ids'], out['attention_mask']

    def forward(self, ids):
        return self.text_module().get_text_features(ids)


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


def coca_caption_loss(logits, labels, mask):
    """Autoregressive caption CE (teacher forcing). Only masked positions are penalised.

    logits: (B, T-1, V) from decoder(ids[:, :-1])
    labels: (B, T-1)  = ids[:, 1:]  (predict next token)
    mask  : (B, T-1)  = attention_mask[:, 1:] (1 = real caption token)
    """
    B, T, V = logits.shape
    ce = torch.nn.functional.cross_entropy(
        logits.reshape(B * T, V), labels.reshape(B * T), reduction='none').reshape(B, T)
    m = mask.float()
    denom = m.sum().clamp(min=1.0)
    loss = (ce * m).sum() / denom
    return loss, float(denom.item())


def mae_norm_pix_target(imgs, patch_size):
    """MAE norm_pix_loss target (OpenVision src/losses/common.py:mae_loss, Apache-2.0).

    imgs: (B,3,H,W) normalised with CLIP MEAN/STD. Returns (B, N, patch**2*3)
    per-patch normalised pixels: un-normalise to [0,1], fold into patches, then
    subtract the per-patch mean / divide the per-patch std over the full patch
    vector (standard MAE norm_pix_loss). N = (H//patch)**2.
    """
    from data import MEAN, STD
    mean = torch.tensor(MEAN, device=imgs.device, dtype=imgs.dtype).view(1, 3, 1, 1)
    std = torch.tensor(STD, device=imgs.device, dtype=imgs.dtype).view(1, 3, 1, 1)
    raw = imgs * std + mean                       # (B,3,H,W) in [0,1]
    B, C, H, W = raw.shape
    p = patch_size
    assert H % p == 0 and W % p == 0, f'image {H}x{W} not divisible by patch {p}'
    g = H // p
    raw = raw.reshape(B, C, g, p, g, p)           # (B,C,g,p,g,p)
    raw = raw.permute(0, 2, 4, 1, 3, 5).reshape(B, g * g, C * p * p)  # (B,N,C*p*p)
    mean_pp = raw.mean(dim=-1, keepdim=True)
    std_pp = raw.std(dim=-1, keepdim=True).clamp(min=1e-6)
    return (raw - mean_pp) / std_pp               # (B,N,patch_dim)


def get_vision(name, resolution, patch, device,
               width=None, depth=None, heads=None, mlp_dim=None):
    v = get_vision_tower(name, width=width, depth=depth, heads=heads, mlp_dim=mlp_dim)
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
    ap.add_argument('--width', type=int, default=None,
                    help='vision width override (R9 shrink-tower pilot: 512/768/1024)')
    ap.add_argument('--depth', type=int, default=None, help='vision depth override')
    ap.add_argument('--heads', type=int, default=None, help='vision heads override')
    ap.add_argument('--mlp-dim', type=int, default=None, help='vision mlp hidden override')
    ap.add_argument('--resolution', type=int, default=224)
    ap.add_argument('--patch', type=int, default=16)
    ap.add_argument('--batch-size', type=int, default=64)
    ap.add_argument('--steps', type=int, default=3000)
    ap.add_argument('--lr', type=float, default=3e-3)
    ap.add_argument('--warmup', type=int, default=20)
    ap.add_argument('--loss', choices=['clip', 'siglip', 'localloss', 'coca', 'aimv2', 'aimv2_ar'], default='clip',
                    help='clip=InfoNCE (R9/R10 baseline); siglip=SigLIP bidirectional sigmoid (R11-L arm2); '
                         'localloss=InfoNCE local_loss=True per-rank pool (R11-L arm3); '
                         'coca=InfoNCE contrastive + autoregressive caption CE (R11-L arm4); '
                         'aimv2=InfoNCE+masked-patch-MSE (R11-L arm6); '
                         'aimv2_ar=official AIMv2 pure AR: causal ViT + next-patch pixel + text AR (no InfoNCE)')
    ap.add_argument('--data', required=True,
                    help='tar shard glob(s), comma-separated for multi-source (e.g. CC12M,Amshaker)')
    ap.add_argument('--data-source', default='wds', choices=['wds', 'gpic', 'mixed'],
                    help='wds=webdataset .txt captions (en500k/CC12M); '
                         'gpic=GPIC tar .json captions; '
                         'mixed=both GPIC+CC12M+Amshaker in one shard list (R12)')
    ap.add_argument('--caption-type', default='short',
                    choices=['short', 'medium', 'short+medium', 'all'],
                    help='GPIC caption_type filter (only --data-source gpic/mixed); '
                         'long not supported for gpic (100%% 77-truncation). '
                         'short+medium keeps both (~90%% of GPIC pairs). '
                         'all = no filtering (accept all GPIC types incl. long; '
                         'mixed mode only).')
    ap.add_argument('--eval-data', default='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar')
    ap.add_argument('--output-dir', required=True)
    ap.add_argument('--seed', type=int, default=1234)
    ap.add_argument('--log-every', type=int, default=50)
    ap.add_argument('--probe-every', type=int, default=300)
    ap.add_argument('--probe-n', type=int, default=128)
    ap.add_argument('--num-workers', type=int, default=2)
    ap.add_argument('--save-every', type=int, default=10000,
                    help='save a checkpoint every N steps (0 = only final)')
    ap.add_argument('--resume', default=None,
                    help='path to checkpoint .pt to resume from. Loads vision + logit_scale '
                         '(+ predictor/decoder if present in ckpt) and sets the step counter to '
                         'the ckpt step, so training continues to --steps. Optimizer state is '
                         'NOT saved/loaded (AdamW restarts — minor transient). C4 loss-decreasing '
                         'guard is disabled on resume (C1/C2 feature-collapse guards remain active).')
    ap.add_argument('--caption-loss-weight', type=float, default=2.0,
                    help='CoCa caption-CE weight (OpenVision coca_caption_loss_weight=2)')
    ap.add_argument('--decoder-depth', type=int, default=4,
                    help='CoCa caption decoder layers (dim=768 heads=12, cross-attn to patches)')
    ap.add_argument('--mask-ratio', type=float, default=0.6,
                    help='R11-L arm6 (AIMv2-style): fraction of patches masked for pixel '
                         'reconstruction (MAE norm_pix_loss). 0 disables the dense term.')
    ap.add_argument('--patch-loss-weight', type=float, default=1.0,
                    help='R11-L arm6: weight of masked-patch reconstruction MSE '
                         '(total = contrast_weight*InfoNCE + patch_loss_weight * mse).')
    ap.add_argument('--contrast-weight', type=float, default=1.0,
                    help='R11-H arm6-B (pure AR): weight of InfoNCE contrast term in '
                         'aimv2 loss. 1.0 = ⑥-A (InfoNCE+MSE); 0.0 = pure masked-patch '
                         'reconstruction, text tower NOT in gradient graph (official AIMv2 route).')
    ap.add_argument('--c2-collapse-guard', type=int, default=1,
                    help='R11-H: whether the C2_gap<=0.005 auto-fuse guard is active. '
                         '1=on (default, contrastive arms); 0=off for pure-AR (C2_gap measures '
                         'cross-modal alignment which is N/A without a contrastive objective; '
                         'C1 feature-collapse + C4 loss-decreasing guards REMAIN active).')
    ap.add_argument('--text-finetune', choices=['frozen', 'lora'], default='frozen',
                    help='R11-L2: frozen=CLIP-768 text tower frozen (baseline); '
                         'lora=zero-init LoRA on q+v proj (lightweight unfreeze)')
    ap.add_argument('--lora-rank', type=int, default=8, help='LoRA rank r (R11-L2)')
    ap.add_argument('--lora-alpha', type=float, default=16.0, help='LoRA alpha (scale=alpha/r)')
    ap.add_argument('--lora-lr', type=float, default=1e-4,
                    help='LoRA parameter-group lr (separate from vision lr=3e-3)')
    ap.add_argument('--alpha-pixel', type=float, default=0.4,
                    help='AIMv2 AR (aimv2_ar): weight of next-patch pixel_loss in '
                         'total = cap_loss + alpha_pixel * pixel_loss (official AIMv2 alpha≈0.4)')
    args = ap.parse_args()

    _OBJ = {'clip': 'InfoNCE', 'siglip': 'SigLIP', 'localloss': 'LocalLoss', 'coca': 'CoCa',
            'aimv2': 'AIMv2-style(MIM+InfoNCE)',
            'aimv2_ar': 'AIMv2-official-AR'}[args.loss]
    _LOSS_KEY = {'clip': 'clip_infonce', 'siglip': 'siglip', 'localloss': 'clip_local',
                 'coca': 'coca', 'aimv2': 'aimv2_mim',
                 'aimv2_ar': 'aimv2_ar'}[args.loss]

    rank = int(os.environ['RANK'])
    world_size = int(os.environ['WORLD_SIZE'])
    setup(rank, world_size)
    is_main = rank == 0
    device = torch.device('cuda')

    # identical init across ranks (DDP will also broadcast from rank 0)
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    import data as D
    from open_clip.loss import ClipLoss, SigLipLoss

    vision = get_vision(args.tower, args.resolution, args.patch, device,
                        args.width, args.depth, args.heads, args.mlp_dim)
    if is_main:
        total = param_count(vision)
        active = active_param_count(vision)
        print(f'[params] tower={args.tower} total={total/1e6:.1f}M '
              f'active={active/1e6:.1f}M embed_dim={EMBED} res={args.resolution} '
              f'patch={args.patch}', flush=True)

    vision = DDP(vision, device_ids=[rank], find_unused_parameters=True)
    text = FrozenClipText(CLIP_PATH, device, finetune=args.text_finetune,
                          lora_rank=args.lora_rank, lora_alpha=args.lora_alpha)
    text_trainable = args.text_finetune != 'frozen'
    if text_trainable:
        text.clip = DDP(text.clip, device_ids=[rank], find_unused_parameters=True)
        if is_main:
            n_lora = sum(p.numel() for p in text.trainable_params())
            print(f'[text-finetune] mode={args.text_finetune} rank={args.lora_rank} '
                  f'alpha={args.lora_alpha} lr={args.lora_lr} '
                  f'trainable={n_lora/1e6:.3f}M', flush=True)

    logit_scale = nn.Parameter(torch.full((), float(np.log(10)), device=device),
                               requires_grad=True)
    logit_bias = None
    if args.loss == 'siglip':
        logit_bias = nn.Parameter(torch.full((), -10.0, device=device),
                                  requires_grad=True)
        loss_fn = SigLipLoss(rank=rank, world_size=world_size)
    elif args.loss == 'localloss':
        loss_fn = ClipLoss(local_loss=True, gather_with_grad=False,
                           rank=rank, world_size=world_size)
    else:
        loss_fn = ClipLoss(local_loss=False, gather_with_grad=False,
                           rank=rank, world_size=world_size)

    # ---- CoCa caption decoder (R11-L arm4) / ARTextDecoder (aimv2_ar) ---- #
    decoder = None
    dec_trainable = 0
    dec_total = 0
    if args.loss == 'coca':
        tok_emb = text.clip.text_model.embeddings.token_embedding
        _vis_w = args.width if args.width is not None else 1024
        dec_mod = CoCaDecoder(dim=EMBED, heads=12, depth=args.decoder_depth, mlp_dim=2048,
                              vocab_size=tok_emb.num_embeddings, max_len=77,
                              vision_width=_vis_w, token_embed=tok_emb).to(device)
        decoder = DDP(dec_mod, device_ids=[rank], find_unused_parameters=True)
        dec_trainable = sum(p.numel() for p in dec_mod.parameters() if p.requires_grad)
        dec_total = param_count(dec_mod)
        if is_main:
            print(f'[decoder] depth={args.decoder_depth} dim={EMBED} heads=12 '
                  f'trainable={dec_trainable/1e6:.1f}M total={dec_total/1e6:.1f}M '
                  f'vocab={tok_emb.num_embeddings} caption_weight={args.caption_loss_weight}',
                  flush=True)
    elif args.loss == 'aimv2_ar':
        _vis_w = args.width if args.width is not None else 1024
        dec_mod = ARTextDecoder(dim=EMBED, heads=12, depth=args.decoder_depth, mlp_dim=2048,
                                vocab_size=49408, max_len=77, vision_width=_vis_w).to(device)
        decoder = DDP(dec_mod, device_ids=[rank], find_unused_parameters=True)
        dec_trainable = sum(p.numel() for p in dec_mod.parameters() if p.requires_grad)
        dec_total = param_count(dec_mod)
        if is_main:
            print(f'[ar-decoder] depth={args.decoder_depth} dim={EMBED} heads=12 '
                  f'trainable={dec_trainable/1e6:.1f}M total={dec_total/1e6:.1f}M '
                  f'vocab=49408 alpha_pixel={args.alpha_pixel} (trainable token_embed)',
                  flush=True)

    # ---- AIMv2-style patch predictor (R11-L arm6 / aimv2_ar) ---- #
    predictor = None
    if args.loss in ('aimv2', 'aimv2_ar'):
        _vis_w = args.width if args.width is not None else 1024
        _patch_dim = (args.patch ** 2) * 3
        pred_mod = PatchPredictor(width=_vis_w, patch_dim=_patch_dim).to(device)
        predictor = DDP(pred_mod, device_ids=[rank], find_unused_parameters=True)
        _pred_trainable = sum(p.numel() for p in pred_mod.parameters() if p.requires_grad)
        _pred_total = param_count(pred_mod)
        if args.loss == 'aimv2_ar':
            dec_trainable += _pred_trainable
            dec_total += _pred_total
        else:
            dec_trainable = _pred_trainable
            dec_total = _pred_total
        if is_main:
            print(f'[predictor] patch_dim={_patch_dim} width={_vis_w} '
                  f'trainable={_pred_trainable/1e6:.2f}M total={_pred_total/1e6:.2f}M '
                  f'mask_ratio={args.mask_ratio} patch_loss_weight={args.patch_loss_weight}',
                  flush=True)

    opt_params = list(vision.parameters()) + [logit_scale]
    if logit_bias is not None:
        opt_params.append(logit_bias)
    if decoder is not None:
        opt_params += list(decoder.parameters())
    if predictor is not None:
        opt_params += list(predictor.parameters())
    opt_groups = [{'params': opt_params}]
    if text_trainable:
        opt_groups.append({'params': text.trainable_params(),
                           'lr': args.lora_lr, 'weight_decay': 0.0})
    opt = torch.optim.AdamW(opt_groups, lr=args.lr, betas=(0.9, 0.95), eps=1e-6)

    # ---- Resume from checkpoint (R12 续跑: continue training beyond the original --steps) ---- #
    start_step = 0
    _resumed_loss = None
    if args.resume:
        if is_main:
            print(f'[resume] loading checkpoint: {args.resume}', flush=True)
        ckpt = torch.load(args.resume, map_location='cpu')
        # sanity: loss config + tower must match (prevent silent recipe change)
        _ck_loss = ckpt['config'].get('loss')
        _ck_tower = ckpt['config'].get('tower')
        if _ck_loss != _LOSS_KEY:
            raise ValueError(f'[resume] LOSS mismatch: ckpt="{_ck_loss}" vs current="{_LOSS_KEY}" — '
                             f'refusing to resume with a different objective')
        if _ck_tower != args.tower:
            raise ValueError(f'[resume] TOWER mismatch: ckpt="{_ck_tower}" vs current="{args.tower}" — '
                             f'refusing to resume with a different architecture')
        # load vision tower
        vision.module.load_state_dict(ckpt['vision'], strict=True)
        logit_scale.data.copy_(ckpt['logit_scale'].to(device))
        if ckpt.get('logit_bias') is not None and logit_bias is not None:
            logit_bias.data.copy_(ckpt['logit_bias'].to(device))
        # load predictor if present (AIMv2-style); warn if missing (random re-init, re-warms fast)
        if predictor is not None and ckpt.get('predictor') is not None:
            predictor.module.load_state_dict(ckpt['predictor'], strict=True)
            if is_main:
                print('[resume] predictor state loaded from ckpt', flush=True)
        elif predictor is not None:
            if is_main:
                print('[resume] WARNING: no predictor state in ckpt — predictor keeps random init '
                      '(re-warms in ~1-2k steps; InfoNCE gradient unaffected, only patch-MSE transient)',
                      flush=True)
        # load decoder if present (CoCa)
        if decoder is not None and ckpt.get('decoder') is not None:
            decoder.module.load_state_dict(ckpt['decoder'], strict=True)
        start_step = int(ckpt['config'].get('steps', 0))
        _resumed_loss = ckpt.get('final_loss')
        if start_step >= args.steps:
            raise ValueError(f'[resume] ckpt step={start_step} >= --steps={args.steps} — nothing to do')
        if is_main:
            print(f'[resume] OK: resuming at step={start_step} → will train to step={args.steps} '
                  f'({args.steps - start_step} new steps). resumed_loss={_resumed_loss}', flush=True)

    def lr_at(s):
        w = args.warmup
        return args.lr * (s / max(1, w)) if s < w else args.lr

    def lora_lr_at(s):
        w = args.warmup
        return args.lora_lr * (s / max(1, w)) if s < w else args.lora_lr

    # rank-sliced shard list (disjoint reads across ranks).
    # Multi-source: --data accepts comma-separated globs (CC12M + Amshaker both wds .txt).
    _globs = [g.strip() for g in args.data.split(',') if g.strip()]
    all_shards = []
    for _g in _globs:
        if _g.endswith('.txt') and os.path.isfile(_g):
            # frozen tar snapshot list (R11-F: ensures GPIC arms A/B/C use the
            # same set of tars even while download adds files between arms).
            with open(_g) as _f:
                all_shards.extend([ln.strip() for ln in _f if ln.strip()])
        else:
            all_shards.extend(sorted(glob.glob(_g)))
    all_shards = sorted(set(all_shards))
    my_shards = all_shards[rank::world_size]
    _tok = text.tokenize_cap if args.loss in ('coca', 'aimv2_ar') else text.tokenize
    if args.data_source == 'gpic':
        loader = D.build_gpic_loader(my_shards, args.batch_size, _tok,
                                     size=args.resolution, num_workers=args.num_workers,
                                     caption_type=args.caption_type)
    elif args.data_source == 'mixed':
        loader = D.build_mixed_loader(my_shards, args.batch_size, _tok,
                                      size=args.resolution, num_workers=args.num_workers,
                                      gpic_caption_type=args.caption_type)
    else:
        loader = D.build_loader(my_shards, args.batch_size, _tok,
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
        f"seed={args.seed} shards={len(my_shards)}/rank objective={_OBJ} "
        f'text={args.text_finetune}-CLIP-768(r={args.lora_rank},a={args.lora_alpha},lr={args.lora_lr}) '
        f'negatives={args.batch_size*world_size} '
        f'data_source={args.data_source} caption_type={args.caption_type} '
        f'total_shards={len(all_shards)}')

# ---- fixed probe batch (rank 0): precompute once; text is FROZEN so T is constant ----
    if is_main:
        from r3_stepA_diag import load_eval_set
        t0p = time.time()
        pr = load_eval_set(args.eval_data, args.resolution, args.probe_n)
        peimgs = torch.stack([p[0] for p in pr]).to(device)
        pcap = [p[1] for p in pr]
        pcap_ids = text.tokenize(pcap).to(device)
        with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
            pT = text.text_module().get_text_features(pcap_ids).float()
        log(f'[probe-setup] n={len(pr)} wall={time.time()-t0p:.0f}s text_trainable={text_trainable}')

    roll = []          # per-step wall times (training forward/backward)
    loss_ema = _resumed_loss     # None if fresh start; ckpt final_loss if resuming
    loss_early = None            # C4 disabled on resume (loss history reset; C1/C2 remain active)
    fused = False
    fuse_reason = None

    def save_ckpt(fname, fused=False, reason=None):
        if not is_main:
            return
        state = {
            'vision': dict(vision.module.state_dict()),
            'logit_scale': logit_scale.detach().cpu(),
            'logit_bias': logit_bias.detach().cpu() if logit_bias is not None else None,
            'predictor': (dict(predictor.module.state_dict()) if predictor is not None else None),
            'decoder': (dict(decoder.module.state_dict()) if decoder is not None else None),
            'config': {'tower': args.tower, 'resolution': args.resolution,
                       'patch': args.patch, 'steps': step,
                       'loss': _LOSS_KEY,
                       'embed_dim': EMBED, 'lr': args.lr, 'warmup': args.warmup,
                       'batch_size': args.batch_size, 'world_size': world_size,
                       'seed': args.seed,
                       'objective': _OBJ,
                       'text': ('lora-CLIP-768' if text_trainable else 'frozen-CLIP-768'),
                       'width': args.width, 'depth': args.depth,
                       'heads': args.heads, 'mlp_dim': args.mlp_dim,
                       'caption_loss_weight': args.caption_loss_weight if args.loss in ('coca', 'aimv2_ar') else None,
                       'decoder_depth': args.decoder_depth if args.loss in ('coca', 'aimv2_ar') else None,
                       'mask_ratio': args.mask_ratio if args.loss == 'aimv2' else None,
                       'patch_loss_weight': args.patch_loss_weight if args.loss == 'aimv2' else None,
                        'contrast_weight': args.contrast_weight if args.loss == 'aimv2' else None,
                        'c2_collapse_guard': args.c2_collapse_guard if args.loss in ('aimv2', 'aimv2_ar') else None,
                         'alpha_pixel': args.alpha_pixel if args.loss == 'aimv2_ar' else None},
            'final_loss': loss_ema,
            'params_total': param_count(vision.module),
            'params_active': active_param_count(vision.module),
            'decoder_params': dec_trainable,
            'text_finetune': args.text_finetune,
            'text_trainable_params': (sum(p.numel() for p in text.trainable_params())
                                      if text_trainable else 0),
            'lora_rank': args.lora_rank if args.text_finetune == 'lora' else None,
            'lora_alpha': args.lora_alpha if args.text_finetune == 'lora' else None,
            'lora_lr': args.lora_lr if args.text_finetune == 'lora' else None,
            'fused': fused,
        }
        if fused:
            state['fuse_reason'] = reason
        torch.save(state, os.path.join(args.output_dir, fname))
        log(f'[saved] {os.path.join(args.output_dir, fname)} (fused={fused})')

    t_start = time.time()
    step = start_step
    while step < args.steps:
        for gi, g in enumerate(opt.param_groups):
            if text_trainable and gi == len(opt.param_groups) - 1:
                g['lr'] = lora_lr_at(step)
            else:
                g['lr'] = lr_at(step)
        try:
            batch = next(loader_iter)
        except StopIteration:
            loader_iter = iter(loader)
            batch = next(loader_iter)

        if args.loss in ('coca', 'aimv2_ar'):
            imgs, (ids, mask) = batch
            ids = ids.to(device, non_blocking=True)
            mask = mask.to(device, non_blocking=True)
        else:
            imgs, txts = batch
            txts = txts.to(device, non_blocking=True)
        imgs = imgs.to(device, non_blocking=True)

        t0 = time.time()
        contr_i = None
        cap_i = None
        pixel_i = None
        with torch.autocast('cuda', dtype=torch.bfloat16):
            if args.loss == 'coca':
                pooled, patches = vision(imgs, return_patch=True)
                If = torch.nn.functional.normalize(pooled, dim=-1)
                Tf = torch.nn.functional.normalize(text(ids), dim=-1)
                contrastive = loss_fn(If, Tf, logit_scale.exp(), None)
                cap_logits = decoder(ids[:, :-1], patches)
                cap_loss, _ntok = coca_caption_loss(cap_logits, ids[:, 1:], mask[:, 1:])
                cur_loss = contrastive + args.caption_loss_weight * cap_loss
                contr_i = contrastive.item()
                cap_i = cap_loss.item()
            elif args.loss == 'aimv2':
                pooled, patches = vision(imgs, return_patch=True)
                # masked patch reconstruction (MAE norm_pix_loss; Apache-2.0 ref)
                B, N, _W = patches.shape
                target = mae_norm_pix_target(imgs, args.patch)      # (B,N,patch_dim)
                mrand = torch.rand(B, N, device=device) < args.mask_ratio
                pred = predictor(patches[mrand])                    # (n_masked, patch_dim)
                tgt = target[mrand]                                 # (n_masked, patch_dim)
                patch_loss = torch.mean((pred.float() - tgt.float()) ** 2)
                if args.contrast_weight > 0:
                    If = torch.nn.functional.normalize(pooled, dim=-1)
                    Tf = torch.nn.functional.normalize(text(txts), dim=-1)
                    contrastive = loss_fn(If, Tf, logit_scale.exp(), None)
                    cur_loss = args.contrast_weight * contrastive + args.patch_loss_weight * patch_loss
                    contr_i = contrastive.item()
                else:
                    # R11-H (arm 6-B): pure AR, NO contrast term -> text tower NOT in graph
                    cur_loss = args.patch_loss_weight * patch_loss
                    contr_i = 0.0
                cap_i = patch_loss.item()          # reuse cap_i slot -> logged as patch_mse
            elif args.loss == 'aimv2_ar':
                # Official AIMv2 pure AR: causal ViT → next-patch pixel + text AR (no InfoNCE)
                # AR ≠ MAE: AR predicts patch i+1 from prefix 0..i (causal, unidirectional);
                #   MAE reconstructs masked patches from bidirectional context.
                # See VISION_AIMV2_OFFICIAL_PLAN.md §3.2 (revision point ①).
                # Hybrid mode: --contrast-weight > 0 adds InfoNCE using causal pooled features
                #   (R13 follow-up: test if contrastive prevents AR collapse).
                pooled, ar_patches = vision(imgs, return_patch=True, causal=True)
                B, N, _W = ar_patches.shape
                # Next-patch pixel prediction: pred[:, :-1] predicts target[:, 1:]
                target = mae_norm_pix_target(imgs, args.patch)       # (B, N, patch_dim)
                pred_pixels = predictor(ar_patches)                   # (B, N, patch_dim)
                # AR shift-by-1: position 0 sees only patch 0, position 195 has no target
                pixel_loss = torch.mean((pred_pixels[:, :-1].float() -
                                         target[:, 1:].float()) ** 2)
                # Text AR: caption next-token, cross-attn to CAUSAL vision patches
                # (revision point ②: must cross-attend to causal patches, NOT bidirectional)
                cap_logits = decoder(ids[:, :-1], ar_patches)
                cap_loss, _ntok = coca_caption_loss(cap_logits, ids[:, 1:], mask[:, 1:])
                if args.contrast_weight > 0:
                    # Hybrid AR + InfoNCE: contrastive on causal pooled features + text
                    If = torch.nn.functional.normalize(pooled, dim=-1)
                    Tf = torch.nn.functional.normalize(text(ids), dim=-1)
                    contrastive = loss_fn(If, Tf, logit_scale.exp(), None)
                    cur_loss = (args.contrast_weight * contrastive
                                + cap_loss + args.alpha_pixel * pixel_loss)
                    contr_i = contrastive.item()
                else:
                    # Pure AR (official AIMv2): no InfoNCE
                    cur_loss = cap_loss + args.alpha_pixel * pixel_loss
                    contr_i = 0.0  # no InfoNCE in pure AR
                cap_i = cap_loss.item()
                pixel_i = pixel_loss.item()
            else:
                If = torch.nn.functional.normalize(vision(imgs), dim=-1)
                Tf = torch.nn.functional.normalize(text(txts), dim=-1)
                if args.loss == 'siglip':
                    cur_loss = loss_fn(If, Tf, logit_scale.exp(), logit_bias)
                else:
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
            bias_s = f' bias={logit_bias.item():.3f}' if logit_bias is not None else ''
            if args.loss == 'coca':
                cap_s = f' contrast={contr_i:.4f} caption={cap_i:.4f}'
            elif args.loss == 'aimv2':
                cap_s = f' contrast={contr_i:.4f} patch_mse={cap_i:.4f}'
            elif args.loss == 'aimv2_ar':
                if args.contrast_weight > 0:
                    cap_s = f' contrast={contr_i:.4f} cap={cap_i:.4f} pixel={pixel_i:.4f}'
                else:
                    cap_s = f' cap={cap_i:.4f} pixel={pixel_i:.4f}'
            else:
                cap_s = ''
            log(f'[step {step}/{args.steps}] loss={li:.4f}{cap_s} scale={logit_scale.exp().item():.3f}{bias_s} '
                f'ms/iter={avg_dt*1000:.1f} image/s={imgs_per_sec:.1f} lr={lr_at(step):.2e}')

        # ---- C1/C2/C4 probe ---- #
        if is_main and step % args.probe_every == 0:
            vision_module = vision.module
            with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
                pI = vision_module(peimgs).float()
                # R11-L2: if the text tower is trainable, recompute T with the CURRENT
                # text params each probe (the frozen-baseline precomputed pT would be stale).
                if text_trainable:
                    pT = text.text_module().get_text_features(pcap_ids).float()
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
            elif args.c2_collapse_guard and gap <= 0.005:
                fused, fuse_reason = True, f'C2 no-gap (gap={gap:+.4f}~0)@step{step}'
            elif not c4_ok:
                fused, fuse_reason = True, f'C4 loss-not-decreasing (ema={loss_ema:.4f} vs early={loss_early:.4f})@step{step}'

        # periodic checkpoint (R9.3 stage-2 needs a ckpt every 10k; also crash resilience)
        if args.save_every and step and step % args.save_every == 0:
            save_ckpt(f'vision_step{step}.pt')

        # ---- DDP-safe fuse broadcast ---- #
        # The probe (which sets `fused`) only runs on rank 0. Broadcast the flag
        # to all ranks so they break together, preventing DDP deadlock where
        # non-zero ranks hang waiting for rank 0 in the next forward/backward.
        if world_size > 1:
            fused_flag = torch.tensor([1 if fused else 0], dtype=torch.int, device=device)
            dist.broadcast(fused_flag, src=0)
            if fused_flag.item():
                fused = True

        if fused:
            break

    total_wall = time.time() - t_start
    steady_img_s = args.batch_size * world_size / float(np.mean(roll[-20:])) if roll else 0.0
    log(f'[done] total={total_wall:.1f}s steps={step} steady_image_s={steady_img_s:.1f} '
        f'final_loss={loss_ema:.4f} fused={fused}')

    save_ckpt('vision_fused.pt' if fused else 'vision.pt', fused=fused, reason=fuse_reason)
    if is_main:
        logf.close()

    cleanup()


if __name__ == '__main__':
    main()