#!/usr/bin/env python
"""armB_protb_eval.py — Protocol-B linear-probe evaluation for ArmB open_clip ViT-B/16.

Operator instruction 2026-10-17 12:4x:
  "训完立即 ProtB：复用 armA_protb_eval.py 口径（full IN-1k 1.28M train + 50k val、
   SGD 90ep、seeds 0/1/2、feature=projected、5-NN），输出 armB_protb_vitb16_224_results.json"

ArmB trains open_clip ViT-B/16 with the AIMv2-style dense objective
(InfoNCE + masked-patch MSE).  This script evaluates the resulting checkpoint with
the **mainstream linear-probe protocol (Protocol B)** — identical to armA_protb_eval.py.

The ONLY difference from armA_protb_eval.py is the checkpoint loading: ArmB saves
the full model (ArmBModel = open_clip CLIP + PatchPredictor) so the state_dict keys
are prefixed with 'clip.' and 'predictor.'.  We strip the 'clip.' prefix and ignore
predictor keys (the predictor is a training-only auxiliary head).  Alternatively,
ArmB also saves a clean 'open_clip_state_dict.pt' which is a raw CLIP state_dict.

Checkpoint formats produced by armB_aimv2_openclip.py:330-340:
  1. open_clip_state_dict.pt  : raw model.clip.state_dict()  (preferred — no predictor)
  2. latest.pt / checkpoint_*.pt : {'model_state_dict': ArmBModel.state_dict(), ...}
     ArmBModel.state_dict() keys: 'clip.visual.*', 'clip.text.*', 'predictor.*'
"""
import argparse
import glob
import json
import math
import os
from io import BytesIO

import torch
import torch.nn as nn
import torchvision.transforms as T
from PIL import Image

import open_clip

MODEL_NAME = 'ViT-B-16'

IN1K_TRAIN_GLOB = '/nas_train/app.e0031982/datasets/imagenet-1k/data/train-*.parquet'
IN1K_VAL_GLOB = '/nas_train/app.e0031982/datasets/imagenet-1k/data/validation-*.parquet'

CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
CLIP_STD = (0.26862954, 0.26130258, 0.27577711)
IN_MEAN = (0.485, 0.456, 0.406)
IN_STD = (0.229, 0.224, 0.225)


def get_transform(size=224, norm='imagenet'):
    """Val/probe transform — Resize(short*1.15) -> CenterCrop -> Normalize.

    Protocol B mandates ImageNet mean/std (BP-3).
    """
    mean = CLIP_MEAN if norm == 'clip' else IN_MEAN
    std = CLIP_STD if norm == 'clip' else IN_STD
    return T.Compose([
        T.Resize(int(size * 1.15)),
        T.CenterCrop(size),
        T.ToTensor(),
        T.Normalize(mean, std),
    ])


def decode_img(image_dict):
    raw = image_dict.get('bytes') or b''
    if not raw:
        return None
    return Image.open(BytesIO(raw)).convert('RGB')


def load_armB_visual(ckpt_path, device, feature='projected', model_name=None):
    """Load the ArmB open_clip visual tower from a training checkpoint.

    Handles both ArmB checkpoint formats:
      1. open_clip_state_dict.pt — raw CLIP state_dict (preferred, no predictor)
      2. latest.pt / checkpoint_*.pt — {'model_state_dict': ArmBModel.state_dict()}
         where keys are prefixed 'clip.' (CLIP model) and 'predictor.' (aux head)

    model_name: open_clip model name (default: MODEL_NAME='ViT-B-16').
                Pass 'ViT-L-14' for ArmE checkpoints.
    """
    model, _, _ = open_clip.create_model_and_transforms(
        model_name or MODEL_NAME, pretrained=None)
    ckpt = torch.load(ckpt_path, map_location='cpu')

    if isinstance(ckpt, dict) and 'model_state_dict' in ckpt:
        # Full ArmB checkpoint: strip 'clip.' prefix, drop predictor keys.
        raw_state = ckpt['model_state_dict']
        state = {k[len('clip.'):]: v for k, v in raw_state.items()
                 if k.startswith('clip.')}
        step = ckpt.get('step', '?')
        loss = ckpt.get('loss', float('nan'))
        print(f'  [load] ArmB full ckpt: {len(raw_state)} keys -> '
              f'{len(state)} CLIP keys (predictor stripped)', flush=True)
    else:
        # open_clip_state_dict.pt — raw CLIP state_dict, load directly.
        state = ckpt
        step = '?'
        loss = float('nan')
        print(f'  [load] ArmB open_clip_state_dict: {len(state)} keys', flush=True)

    missing, unexpected = model.load_state_dict(state, strict=False)
    real_missing = [k for k in missing if k.startswith('visual.')]
    if real_missing:
        print(f'  [load] WARNING visual keys missing: {real_missing[:5]}'
              f' ... ({len(real_missing)} total)', flush=True)
    print(f'  [load] ArmB ckpt step={step} loss={loss:.4f} feature={feature}',
          flush=True)

    vision = model.visual
    if feature == 'pooled':
        vision.proj = None
    vision = vision.to(device).eval()
    n = sum(p.numel() for p in vision.parameters())
    print(f'  [load] visual tower on {device} ({n / 1e6:.1f}M params, eval)',
          flush=True)
    return vision


def extract_features_streaming(vision, parquet_files, transform, device,
                               bs=256, max_images=None, label='streaming'):
    """Stream through parquet, decode + transform + encode frozen features."""
    import pyarrow.parquet as pq
    all_feats, all_labels = [], []
    count = 0
    for fi, f in enumerate(parquet_files):
        pf = pq.ParquetFile(f)
        for rb in pf.iter_batches(batch_size=bs):
            imgs_col = rb.column('image').to_pylist()
            labs_col = rb.column('label').to_numpy()
            bt, bl = [], []
            for img_dict, lab in zip(imgs_col, labs_col):
                lab = int(lab)
                if lab < 0 or lab >= 1000:
                    continue
                img = decode_img(img_dict)
                if img is None:
                    continue
                bt.append(transform(img))
                bl.append(lab)
            if not bt:
                continue
            b = torch.stack(bt).to(device).float().to(torch.bfloat16)
            with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
                out = vision(b)
            pooled = out[0] if isinstance(out, tuple) else out
            all_feats.append(pooled.float().cpu())
            all_labels.extend(bl)
            count += len(bl)
            if max_images and count >= max_images:
                feats = torch.cat(all_feats)[:max_images]
                return feats, torch.tensor(all_labels[:max_images])
        if fi % 25 == 0:
            print(f'    [{label}] {count} images after '
                  f'{fi + 1}/{len(parquet_files)} files', flush=True)
    feats = torch.cat(all_feats)
    labels = torch.tensor(all_labels)
    print(f'    [{label}] total {feats.shape[0]} images -> feat {list(feats.shape)}',
          flush=True)
    return feats, labels


def load_probe_train_subset(per_class=50, size=224, max_files=40):
    """Load probe-train subset (N/class) — decode+transform only (no GPU)."""
    import pyarrow.parquet as pq
    tf = get_transform(size, 'imagenet')
    files = sorted(glob.glob(IN1K_TRAIN_GLOB))
    probe_lists = {c: [] for c in range(1000)}
    probe_cnt = {c: 0 for c in range(1000)}
    for f in files[:max_files]:
        table = pq.ParquetFile(f).read()
        imgs = table.column('image').to_pylist()
        labels = table.column('label').to_numpy()
        for img_dict, lab in zip(imgs, labels):
            lab = int(lab)
            if probe_cnt[lab] < per_class:
                img = decode_img(img_dict)
                if img is not None:
                    probe_lists[lab].append(tf(img))
                    probe_cnt[lab] += 1
        if sum(1 for c in range(1000) if probe_cnt[c] >= per_class) == 1000:
            break
    probe = [t for c in range(1000) for t in probe_lists[c][:per_class]]
    probe_labels = torch.tensor(
        [c for c in range(1000) for _ in range(len(probe_lists[c][:per_class]))])
    probe_imgs = torch.stack(probe).half()
    print(f'  [probe-train subset] {probe_imgs.shape[0]} images '
          f'({per_class}/class)', flush=True)
    return probe_imgs, probe_labels


def cosine_lr(step, total_steps, lr_max, lr_min=0.0, warmup_steps=0):
    if step < warmup_steps:
        return lr_max * (step + 1) / max(warmup_steps, 1)
    progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
    return lr_min + 0.5 * (lr_max - lr_min) * (1 + math.cos(math.pi * progress))


def linear_probe_mainstream(Xtr, ytr, Xva, yva, device,
                            epochs=90, batch_size=1024, lr=0.1,
                            momentum=0.9, weight_decay=0.0,
                            warmup_epochs=5, seed=0):
    """SGD + momentum + cosine (DINOv2-style) linear probe on frozen features."""
    torch.manual_seed(seed)
    d = Xtr.shape[1]
    clf = nn.Linear(d, 1000).to(device)
    Xtr = Xtr.to(device)
    ytr = ytr.to(device)
    yva = yva.to(device)
    Xva = Xva.to(device)
    n = Xtr.shape[0]
    spe = math.ceil(n / batch_size)
    total_steps = epochs * spe
    wu = warmup_epochs * spe
    opt = torch.optim.SGD(clf.parameters(), lr=lr, momentum=momentum,
                          weight_decay=weight_decay)
    ce = nn.CrossEntropyLoss()
    step = 0
    for ep in range(epochs):
        perm = torch.randperm(n, device=device)
        for i in range(0, n, batch_size):
            idx = perm[i:i + batch_size]
            lr_t = cosine_lr(step, total_steps, lr, 0.0, wu)
            for pg in opt.param_groups:
                pg['lr'] = lr_t
            opt.zero_grad()
            ce(clf(Xtr[idx]), ytr[idx]).backward()
            opt.step()
            step += 1
        if ep % 10 == 0 or ep == epochs - 1:
            with torch.no_grad():
                acc = (clf(Xva).argmax(1) == yva).float().mean().item()
            print(f'    [lp seed={seed}] ep {ep}/{epochs} lr={lr_t:.4e} '
                  f'val_acc={acc * 100:.2f}%', flush=True)
    with torch.no_grad():
        pred = clf(Xva).argmax(1)
    return (pred == yva).float().mean().item()


def knn_probe(Xtr, ytr, Xva, yva, k=5, device='cuda'):
    """k-NN probe (cosine sim) — pure feature-quality test."""
    Xtr_n = torch.nn.functional.normalize(Xtr.float(), dim=-1).to(device)
    Xva_n = torch.nn.functional.normalize(Xva.float(), dim=-1).to(device)
    correct, total = 0, Xva_n.shape[0]
    bs = 500
    for i in range(0, total, bs):
        batch = Xva_n[i:i + bs]
        sim = batch @ Xtr_n.T
        topk_idx = sim.topk(k, dim=1).indices
        topk_labels = ytr[topk_idx.cpu()]
        pred = torch.mode(topk_labels, dim=1).values
        correct += (pred == yva[i:i + bs].cpu()).sum().item()
    return correct / total


def main():
    ap = argparse.ArgumentParser(
        description='ArmB open_clip ViT-B/16 Protocol-B linear-probe eval')
    ap.add_argument('--ckpt', required=True,
                    help='ArmB checkpoint: open_clip_state_dict.pt (preferred) '
                         'or latest.pt / checkpoint_*.pt')
    ap.add_argument('--model', default=MODEL_NAME)
    ap.add_argument('--device', default='cuda:0')
    ap.add_argument('--size', type=int, default=224)
    ap.add_argument('--feature', default='projected',
                    choices=['projected', 'pooled'],
                    help='projected=512-d | pooled=768-d pre-projection CLS')
    ap.add_argument('--probe-full-train', action='store_true',
                    help='use IN-1k FULL train (1.28M) as probe-train (Protocol B)')
    ap.add_argument('--probe-per-class', type=int, default=0,
                    help='subset N/class (0 = use --probe-full-train)')
    ap.add_argument('--seeds', type=int, nargs='+', default=[0, 1, 2])
    ap.add_argument('--epochs', type=int, default=90)
    ap.add_argument('--probe-batch', type=int, default=1024)
    ap.add_argument('--lr', type=float, default=0.1)
    ap.add_argument('--warmup-epochs', type=int, default=5)
    ap.add_argument('--extract-bs', type=int, default=256)
    ap.add_argument('--knn', action='store_true', help='also run 5-NN probe')
    ap.add_argument('--shard', type=int, default=0)
    ap.add_argument('--num-shards', type=int, default=1)
    ap.add_argument('--feat-dir', default='',
                    help='dir for sharded feature caches (enables --gather)')
    ap.add_argument('--gather', action='store_true',
                    help='gather sharded caches + run probe (no extraction)')
    ap.add_argument('--out-json',
                    default='armB_protb_vitb16_224_results.json')
    args = ap.parse_args()

    device = torch.device(args.device)
    tf = get_transform(args.size, 'imagenet')

    if args.gather:
        feat_dir = args.feat_dir or os.path.dirname(args.out_json) or '.'
        train_feats, train_labels = [], []
        for s in range(args.num_shards):
            p = os.path.join(feat_dir, f'train.shard{s}.pt')
            if os.path.isfile(p):
                d = torch.load(p)
                train_feats.append(d['feats'])
                train_labels.append(d['labels'])
        val_p = os.path.join(feat_dir, 'val.pt')
        if not train_feats or not os.path.isfile(val_p):
            raise FileNotFoundError(
                f'--gather: missing shard caches in {feat_dir}')
        Xtr = torch.cat(train_feats)
        ytr = torch.cat(train_labels)
        vd = torch.load(val_p)
        Xva, yva = vd['feats'], vd['labels']
        print(f'[gather] Xtr {list(Xtr.shape)} Xva {list(Xva.shape)}', flush=True)
    else:
        vision = load_armB_visual(args.ckpt, device, args.feature, args.model)
        if args.shard == 0 or args.num_shards == 1:
            val_files = sorted(glob.glob(IN1K_VAL_GLOB))
            print(f'[extract] val: {len(val_files)} parquet files', flush=True)
            Xva, yva = extract_features_streaming(
                vision, val_files, tf, device, bs=args.extract_bs, label='val')
        else:
            print(f'[extract] shard {args.shard}: skip val', flush=True)
        if args.probe_per_class and args.probe_per_class > 0:
            probe_imgs, probe_labels = load_probe_train_subset(
                args.probe_per_class, args.size)
            with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
                b = probe_imgs.to(device).float().to(torch.bfloat16)
                out = vision(b)
            pooled = out[0] if isinstance(out, tuple) else out
            Xtr = pooled.float().cpu()
            ytr = probe_labels
        else:
            train_files = sorted(glob.glob(IN1K_TRAIN_GLOB))
            if args.num_shards > 1:
                train_files = train_files[args.shard::args.num_shards]
            print(f'[extract] probe-train (full): {len(train_files)} parquet '
                  f'files [shard {args.shard}/{args.num_shards}]', flush=True)
            Xtr, ytr = extract_features_streaming(
                vision, train_files, tf, device, bs=args.extract_bs,
                label=f'train.s{args.shard}')
        if args.feat_dir:
            os.makedirs(args.feat_dir, exist_ok=True)
            torch.save({'feats': Xtr, 'labels': ytr},
                       os.path.join(args.feat_dir, f'train.shard{args.shard}.pt'))
            if args.shard == 0:
                torch.save({'feats': Xva, 'labels': yva},
                           os.path.join(args.feat_dir, 'val.pt'))
            print(f'[extract] cached to {args.feat_dir}; rerun --gather', flush=True)
            return

    # ---- Protocol-B linear probe (3 seeds) ----
    print(f'\n[probe] Protocol B: SGD+mom0.9 cosine(5ep wu) {args.epochs}ep '
          f'mb{args.probe_batch} lr{args.lr} seeds={args.seeds}', flush=True)
    accs = []
    for s in args.seeds:
        acc = linear_probe_mainstream(
            Xtr, ytr, Xva, yva, device, epochs=args.epochs,
            batch_size=args.probe_batch, lr=args.lr,
            momentum=0.9, weight_decay=0.0,
            warmup_epochs=args.warmup_epochs, seed=s)
        accs.append(acc * 100)
        print(f'[probe] seed={s} lp={acc * 100:.2f}%', flush=True)

    mean = sum(accs) / len(accs)
    sigma = (sum((a - mean) ** 2 for a in accs) / len(accs)) ** 0.5
    print(f'\n[RESULT] Protocol-B lp = {mean:.2f} +/- {sigma:.2f} % '
          f'(seeds={args.seeds})', flush=True)

    result = {
        'ckpt': os.path.basename(args.ckpt),
        'model': args.model,
        'feature': args.feature,
        'protocol': 'B',
        'probe_train': ('full' if not args.probe_per_class
                        else f'{args.probe_per_class}/class'),
        'epochs': args.epochs,
        'seeds': args.seeds,
        'lp_per_seed': accs,
        'lp_mean': round(mean, 4),
        'lp_sigma': round(sigma, 4),
    }

    if args.knn:
        knn = knn_probe(Xtr, ytr, Xva, yva, k=5, device=device) * 100
        result['knn5'] = round(knn, 4)
        print(f'[RESULT] 5-NN probe = {knn:.2f}%', flush=True)

    with open(args.out_json, 'w') as f:
        json.dump(result, f, indent=2)
    print(f'[RESULT] saved -> {args.out_json}', flush=True)


if __name__ == '__main__':
    main()
