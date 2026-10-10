#!/usr/bin/env python
"""lp_protocol_bridge.py — Linear-probe protocol bridging evaluation.

Bridges the BaiZe internal lp protocol (A) with the mainstream lp protocol (B)
on the SAME frozen-trunk checkpoints, to quantify how much of the lp gap vs
published numbers (DINOv2 ~78%, MAE ~68%) is attributable to *protocol*
differences rather than model quality / data scale.

Protocol A (BaiZe internal — reproduces r8_eval_in1k.py exactly):
  - IN-1k self-split from *train* parquet: val 50/class + probe 50/class
  - Normalization: CLIP mean/std
  - Linear(d -> 1000) + CE, AdamW lr=3e-3, full-batch, 100 epochs
  - RAW (non-L2-normalized) frozen-trunk pooled features, seed 0

Protocol B (mainstream — aligned with DINOv2 / MAE / iBOT / VISSL):
  - Eval: IN-1k OFFICIAL validation (50k, 14 parquet, labels 0-999)
  - Probe-train: IN-1k FULL train (1 281 167) or subset (--probe-per-class N)
  - Normalization: ImageNet mean/std
  - SGD+momentum 0.9, cosine (5-ep warmup), 90 ep, mini-batch 1024
  - Repeats 3 (seeds 0,1,2) → mean ± σ

Key finding (2026-10-06): R13 official OV2 L/14 lp=79.81% used Protocol A
(r13_eval_official.py line 10: "Protocol identical to r8_eval_in1k.py").
⇒ Protocol A does NOT systematically suppress strong models.

Usage:
  conda activate py310 && cd doc/BaiZe-ISEDA2027/run/vision
  python lp_protocol_bridge.py --ckpts ckpt1.pt ckpt2.pt --protocol both --probe-full-train
  python lp_protocol_bridge.py --ckpts ckpt1.pt --protocol B --probe-per-class 200
  python lp_protocol_bridge.py --ckpts ckpt1.pt --protocol A
"""
import argparse
import glob
import math
from io import BytesIO

import torch
import torch.nn as nn
import torchvision.transforms as T
from PIL import Image

import r8_eval_in1k as R8
from r8_eval_in1k import load_vision, encode_images, linear_probe as lp_baize

IN1K_TRAIN_GLOB = '/nas_train/app.e0031982/datasets/imagenet-1k/data/train-*.parquet'
IN1K_VAL_GLOB   = '/nas_train/app.e0031982/datasets/imagenet-1k/data/validation-*.parquet'

CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073)
CLIP_STD  = (0.26862954, 0.26130258, 0.27577711)
IN_MEAN   = (0.485, 0.456, 0.406)
IN_STD    = (0.229, 0.224, 0.225)


def get_transform(size=224, norm='clip'):
    """Val transform with either CLIP or ImageNet normalization."""
    mean = CLIP_MEAN if norm == 'clip' else IN_MEAN
    std  = CLIP_STD  if norm == 'clip' else IN_STD
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


def load_official_val(size=224, norm='imagenet'):
    """Load the official IN-1k validation set (50k, 14 parquet, labels 0-999)."""
    import pyarrow.parquet as pq
    tf = get_transform(size, norm)
    files = sorted(glob.glob(IN1K_VAL_GLOB))
    tensors, labels = [], []
    for f in files:
        table = pq.ParquetFile(f).read()
        imgs = table.column('image').to_pylist()
        labs = table.column('label').to_numpy()
        for img_dict, lab in zip(imgs, labs):
            img = decode_img(img_dict)
            if img is not None:
                tensors.append(tf(img))
                labels.append(int(lab))
    imgs_t = torch.stack(tensors).half()
    labs_t = torch.tensor(labels)
    print(f'  [official-val] {imgs_t.shape[0]} images, labels '
          f'{labs_t.min().item()}-{labs_t.max().item()}', flush=True)
    return imgs_t, labs_t


def load_probe_train_subset(per_class=50, size=224, norm='clip', max_files=40):
    """Load probe-train subset (N/class) from train parquet."""
    import pyarrow.parquet as pq
    tf = get_transform(size, norm)
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


def extract_features_streaming(vision, parquet_files, transform, device,
                               bs=128, max_images=None):
    """Stream through parquet, decode + transform + encode features.
    Returns (features[N,d] float32 CPU, labels[N] long CPU)."""
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
                print(f'    [streaming] max_images={max_images} at '
                      f'file {fi+1}/{len(parquet_files)}', flush=True)
                feats = torch.cat(all_feats)[:max_images]
                return feats, torch.tensor(all_labels[:max_images])
        if fi % 50 == 0 and fi > 0:
            print(f'    [streaming] {count} images after '
                  f'{fi+1}/{len(parquet_files)} files', flush=True)
    feats = torch.cat(all_feats)
    labels = torch.tensor(all_labels)
    print(f'    [streaming] total {feats.shape[0]} images from '
          f'{len(parquet_files)} files', flush=True)
    return feats, labels


def cosine_lr(step, total_steps, lr_max, lr_min=0.0, warmup_steps=0):
    if step < warmup_steps:
        return lr_max * (step + 1) / max(warmup_steps, 1)
    progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
    return lr_min + 0.5 * (lr_max - lr_min) * (1 + math.cos(math.pi * progress))


def linear_probe_mainstream(Xtr, ytr, Xva, yva, device,
                            epochs=90, batch_size=1024, lr=0.1,
                            momentum=0.9, weight_decay=0.0,
                            warmup_epochs=5, optimizer='sgd', seed=0):
    """Mainstream linear probe on pre-extracted frozen-trunk features.
    SGD+momentum+cosine (DINOv2-style) or AdamW+cosine+warmup (secondary)."""
    torch.manual_seed(seed)
    d = Xtr.shape[1]
    clf = nn.Linear(d, 1000).to(device)
    Xtr = Xtr.to(device)
    ytr = ytr.to(device)
    yva = yva.to(device)
    n = Xtr.shape[0]
    spe = math.ceil(n / batch_size)
    total_steps = epochs * spe
    wu = warmup_epochs * spe
    if optimizer == 'sgd':
        opt = torch.optim.SGD(clf.parameters(), lr=lr, momentum=momentum,
                              weight_decay=weight_decay)
    else:
        opt = torch.optim.AdamW(clf.parameters(), lr=lr,
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
    with torch.no_grad():
        pred = clf(Xva).argmax(1)
    return (pred == yva).float().mean().item()


def knn_probe(Xtr, ytr, Xva, yva, k=5, device='cuda'):
    """k-NN probe: classify each val image by majority vote of k nearest train
    images in cosine-similarity space. No training needed — pure feature
    quality test.  Added 2026-10-10 (② probe ablation)."""
    Xtr_n = torch.nn.functional.normalize(Xtr.float(), dim=-1).to(device)
    Xva_n = torch.nn.functional.normalize(Xva.float(), dim=-1).to(device)
    correct, total = 0, Xva_n.shape[0]
    bs = 500
    for i in range(0, total, bs):
        batch = Xva_n[i:i + bs]
        sim = batch @ Xtr_n.T
        topk_idx = sim.topk(k, dim=1).indices
        topk_labels = ytr[topk_idx.cpu()]
        for j in range(topk_labels.shape[0]):
            vals, counts = torch.unique(topk_labels[j], return_counts=True)
            pred = vals[counts.argmax()]
            if pred == yva[i + j]:
                correct += 1
        if i % 5000 == 0:
            print(f'    [knn k={k}] {i}/{total}...', flush=True)
    return correct / total


def main():
    ap = argparse.ArgumentParser(
        description='LP protocol bridging eval (A=BaiZe, B=mainstream)',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--ckpts', nargs='+', required=True)
    ap.add_argument('--protocol', choices=['A', 'B', 'both', 'knn'], default='both')
    ap.add_argument('--probe-full-train', action='store_true',
                    help='B: use full IN-1k train (1.28M). Heavy I/O.')
    ap.add_argument('--probe-per-class', type=int, default=200,
                    help='B: probe images/class (if not --probe-full-train)')
    ap.add_argument('--max-train-files', type=int, default=0,
                    help='B full-train: limit parquet files (0=all 294)')
    ap.add_argument('--repeats', type=int, default=3, help='B: repeats for σ')
    ap.add_argument('--optimizer', choices=['sgd', 'adamw'], default='sgd')
    ap.add_argument('--epochs', type=int, default=None)
    ap.add_argument('--warmup-epochs', type=int, default=None)
    ap.add_argument('--batch-size', type=int, default=1024)
    ap.add_argument('--lr', type=float, default=None)
    ap.add_argument('--weight-decay', type=float, default=0.0,
                    help='B: weight decay for SGD/AdamW (default 0)')
    ap.add_argument('--knn', action='store_true',
                    help='Run k-NN probe (k=5,10,20) on val set')
    ap.add_argument('--knn-k', type=int, nargs='+', default=[5, 10, 20],
                    help='k values for k-NN probe')
    ap.add_argument('--size', type=int, default=224)
    ap.add_argument('--bs-encode', type=int, default=128)
    ap.add_argument('--gpu', type=int, default=0)
    args = ap.parse_args()

    if args.optimizer == 'sgd':
        epochs = args.epochs or 90
        warmup = args.warmup_epochs or 5
        lr = args.lr or 0.1
    else:
        epochs = args.epochs or 20
        warmup = args.warmup_epochs or 20
        lr = args.lr or 1e-3

    device = torch.device(
        f'cuda:{args.gpu}' if torch.cuda.is_available() else 'cpu')
    torch.backends.cudnn.benchmark = True

    print('=' * 72, flush=True)
    print('[BRIDGE] LP Protocol Bridging Evaluation', flush=True)
    print(f'[BRIDGE] device={device}  protocol={args.protocol}', flush=True)
    print(f'[BRIDGE] ckpts: {args.ckpts}', flush=True)
    if args.protocol in ('B', 'both'):
        mode = 'full-train(1.28M)' if args.probe_full_train else \
               f'{args.probe_per_class}/class'
        print(f'[BRIDGE] B: {mode}, {args.optimizer} ep={epochs} '
              f'wu={warmup} lr={lr} bs={args.batch_size} '
              f'reps={args.repeats}', flush=True)
    print('=' * 72, flush=True)

    # Pre-load Protocol A data
    A_val_imgs = A_val_labels = A_probe_imgs = A_probe_labels = None
    if args.protocol in ('A', 'both'):
        print('\n[BRIDGE] Loading Protocol A (self-split, CLIP norm) ...',
              flush=True)
        A_val_imgs, A_val_labels, A_probe_imgs, A_probe_labels = \
            R8.load_in1k_split(max_files=40, per_class=50, size=args.size)
        A_val_labels = A_val_labels.to(device)
        A_probe_labels = A_probe_labels.to(device)

    # Pre-load Protocol B eval data
    B_val_imgs = B_val_labels = None
    if args.protocol in ('B', 'both'):
        print('\n[BRIDGE] Loading Protocol B eval (official val, IN norm) ...',
              flush=True)
        B_val_imgs, B_val_labels = load_official_val(
            size=args.size, norm='imagenet')
        B_val_labels = B_val_labels.to(device)

    results = []
    for ckpt in args.ckpts:
        print(f'\n{"─"*72}', flush=True)
        print(f'[BRIDGE] ckpt={ckpt}', flush=True)
        ckpt_result = {'ckpt': ckpt, 'A': None, 'B': None}
        vision = load_vision(ckpt, device)
        Iv_B = None  # shared between Protocol B and k-NN

        # Protocol A
        if args.protocol in ('A', 'both'):
            print('[BRIDGE] A (BaiZe: AdamW full-batch 100ep) ...', flush=True)
            Iv_A = encode_images(vision, A_val_imgs, device,
                                 args.bs_encode).float()
            Pp_A = encode_images(vision, A_probe_imgs, device,
                                 args.bs_encode).float()
            lp_A = lp_baize(Pp_A, A_probe_labels, Iv_A, A_val_labels, device)
            print(f'[BRIDGE] A: lp_top1={lp_A:.4f} ({lp_A*100:.2f}%)',
                  flush=True)
            ckpt_result['A'] = lp_A
            del Iv_A, Pp_A
            torch.cuda.empty_cache()

        # Protocol B
        if args.protocol in ('B', 'both'):
            print(f'[BRIDGE] B ({args.optimizer}+cosine {epochs}ep '
                  f'bs{args.batch_size}) ...', flush=True)
            Iv_B = encode_images(vision, B_val_imgs, device,
                                 args.bs_encode).float()
            if args.probe_full_train:
                train_files = sorted(glob.glob(IN1K_TRAIN_GLOB))
                if args.max_train_files > 0:
                    train_files = train_files[:args.max_train_files]
                print(f'  [B] streaming {len(train_files)} train parquet '
                      f'(IN norm) ...', flush=True)
                tf_in = get_transform(args.size, 'imagenet')
                Pp_B, Pl_B = extract_features_streaming(
                    vision, train_files, tf_in, device, bs=args.bs_encode)
            else:
                print(f'  [B] probe-train {args.probe_per_class}/class '
                      f'(IN norm) ...', flush=True)
                B_pi, B_pl = load_probe_train_subset(
                    per_class=args.probe_per_class, size=args.size,
                    norm='imagenet')
                Pp_B = encode_images(vision, B_pi, device,
                                     args.bs_encode).float()
                Pl_B = B_pl.to(device)

            lp_B_runs = []
            for seed in range(args.repeats):
                lp_B = linear_probe_mainstream(
                    Pp_B, Pl_B, Iv_B, B_val_labels, device,
                    epochs=epochs, batch_size=args.batch_size, lr=lr,
                    momentum=0.9, weight_decay=args.weight_decay,
                    warmup_epochs=warmup, optimizer=args.optimizer, seed=seed)
                lp_B_runs.append(lp_B)
                print(f'[BRIDGE] B seed={seed}: lp_top1={lp_B:.4f} '
                      f'({lp_B*100:.2f}%)', flush=True)

            lp_B_mean = sum(lp_B_runs) / len(lp_B_runs)
            lp_B_std = (sum((x - lp_B_mean)**2 for x in lp_B_runs)
                        / len(lp_B_runs)) ** 0.5
            print(f'[BRIDGE] B: lp_top1={lp_B_mean:.4f}±{lp_B_std:.4f} '
                  f'({lp_B_mean*100:.2f}±{lp_B_std*100:.2f}%)', flush=True)
            ckpt_result['B'] = {
                'mean': lp_B_mean, 'std': lp_B_std, 'runs': lp_B_runs,
                'optimizer': args.optimizer, 'epochs': epochs,
                'batch_size': args.batch_size, 'probe_n': Pp_B.shape[0]}
            del Pp_B, Pl_B
            torch.cuda.empty_cache()

        # k-NN probe (② probe ablation, added 2026-10-10)
        if args.knn or args.protocol == 'knn':
            print('[BRIDGE] k-NN probe ...', flush=True)
            # Encode val features if not already done by Protocol B
            if Iv_B is not None:
                Iv_knn = Iv_B  # reuse
                B_val_labels_knn = B_val_labels
            else:
                if B_val_imgs is None:
                    print('  [knn] Loading official val (IN norm) ...', flush=True)
                    B_val_imgs, B_val_labels = load_official_val(
                        size=args.size, norm='imagenet')
                    B_val_labels = B_val_labels.to(device)
                Iv_knn = encode_images(vision, B_val_imgs, device,
                                       args.bs_encode).float()
                B_val_labels_knn = B_val_labels
            # Encode train subset for k-NN reference
            print(f'  [knn] Loading train subset (50/class, IN norm) ...', flush=True)
            knn_tr_imgs, knn_tr_labels = load_probe_train_subset(
                per_class=50, size=args.size, norm='imagenet')
            Xtr_knn = encode_images(vision, knn_tr_imgs, device,
                                    args.bs_encode).float()
            Pl_knn = knn_tr_labels.to(device)
            knn_results = {}
            for k in args.knn_k:
                acc = knn_probe(Xtr_knn, Pl_knn, Iv_knn,
                                B_val_labels_knn, k=k, device=device)
                print(f'[BRIDGE] k-NN k={k}: top1={acc:.4f} ({acc*100:.2f}%)',
                      flush=True)
                knn_results[f'k{k}'] = acc
            ckpt_result['knn'] = knn_results
            del Xtr_knn, Pl_knn
            if Iv_B is None:
                del Iv_knn
            else:
                del Iv_B
                Iv_B = None
            torch.cuda.empty_cache()

        if ckpt_result['A'] is not None and ckpt_result['B'] is not None:
            delta = ckpt_result['B']['mean'] - ckpt_result['A']
            print(f'[BRIDGE] Δlp = B - A = {delta:+.4f} '
                  f'({delta*100:+.2f} pp)', flush=True)
            ckpt_result['delta'] = delta

        results.append(ckpt_result)
        del vision
        torch.cuda.empty_cache()

    # Summary
    print(f'\n{"="*72}', flush=True)
    print('[BRIDGE] SUMMARY', flush=True)
    print(f'{"ckpt":<40} {"A(BaiZe)":>12} {"B(mainstream)":>18} '
          f'{"Δlp":>10}', flush=True)
    print('-' * 82, flush=True)
    for r in results:
        a = f'{r["A"]*100:.2f}%' if r['A'] is not None else '—'
        b = (f'{r["B"]["mean"]*100:.2f}±{r["B"]["std"]*100:.2f}%'
             if r['B'] else '—')
        d = f'{r["delta"]*100:+.2f}pp' if 'delta' in r else '—'
        print(f'{r["ckpt"].split("/")[-1]:<40} {a:>12} {b:>18} {d:>10}',
              flush=True)
        if 'knn' in r:
            knn_str = '  '.join(f'k{k}={v*100:.2f}%' for k, v in r['knn'].items())
            print(f'  {"k-NN:":<40} {knn_str}', flush=True)
    print('=' * 72, flush=True)
    print('[BRIDGE] DONE', flush=True)


if __name__ == '__main__':
    main()
