#!/usr/bin/env python
"""probe_comparison_eval.py — Stronger probe comparison on E1fair (2026-10-10 ②).

ARMS:
  1. k-NN probe (k=5,10,20) — pure feature quality test, no training
  2. Protocol B ×5 epochs (450 instead of 90) — tests probe underfitting
  3. wd/LR sweep on Protocol B

Usage:
  cd doc/BaiZe-ISEDA2027/run/vision
  python probe_comparison_eval.py --ckpt /path/to/vision.pt [--knn-only] [--probe-only]
"""
import argparse, glob, math
from io import BytesIO
import torch, torch.nn as nn, torchvision.transforms as T
from PIL import Image
import models
from models import get_vision_tower, ReadoutHead
from r7_train import FrozenClipText, CLIP_PATH, EMBED

IN1K_TRAIN_GLOB = '/nas_train/app.e0031982/datasets/imagenet-1k/data/train-*.parquet'
IN1K_VAL_GLOB   = '/nas_train/app.e0031982/datasets/imagenet-1k/data/validation-*.parquet'
IN_MEAN = (0.485, 0.456, 0.406); IN_STD = (0.229, 0.224, 0.225)

def get_transform(size=224, norm='imagenet'):
    mean = IN_MEAN if norm == 'imagenet' else (0.48145466,0.4578275,0.40821073)
    std  = IN_STD  if norm == 'imagenet' else (0.26862954,0.26130258,0.27577711)
    return T.Compose([T.Resize(int(size*1.15)), T.CenterCrop(size), T.ToTensor(), T.Normalize(mean, std)])

def decode_img(image_dict):
    raw = image_dict.get('bytes') or b''
    if not raw: return None
    return Image.open(BytesIO(raw)).convert('RGB')

def load_official_val(size=224):
    import pyarrow.parquet as pq
    tf = get_transform(size, 'imagenet')
    files = sorted(glob.glob(IN1K_VAL_GLOB))
    tensors, labels = [], []
    for f in files:
        table = pq.ParquetFile(f).read()
        imgs = table.column('image').to_pylist()
        labs = table.column('label').to_numpy()
        for img_dict, lab in zip(imgs, labs):
            img = decode_img(img_dict)
            if img is not None: tensors.append(tf(img)); labels.append(int(lab))
    return torch.stack(tensors).half(), torch.tensor(labels)

def load_train_subset(per_class=50, size=224, max_files=40):
    import pyarrow.parquet as pq
    tf = get_transform(size, 'imagenet')
    files = sorted(glob.glob(IN1K_TRAIN_GLOB))
    class_lists = {c: [] for c in range(1000)}; class_cnt = {c: 0 for c in range(1000)}
    for f in files[:max_files]:
        table = pq.ParquetFile(f).read()
        imgs = table.column('image').to_pylist(); labs = table.column('label').to_numpy()
        for img_dict, lab in zip(imgs, labs):
            lab = int(lab)
            if class_cnt[lab] < per_class:
                img = decode_img(img_dict)
                if img is not None: class_lists[lab].append(tf(img)); class_cnt[lab] += 1
        if sum(1 for c in range(1000) if class_cnt[c] >= per_class) == 1000: break
    tensors = [t for c in range(1000) for t in class_lists[c][:per_class]]
    labels = [c for c in range(1000) for _ in range(len(class_lists[c][:per_class]))]
    return torch.stack(tensors).half(), torch.tensor(labels)

def load_vision(ckpt_path, device):
    ck = torch.load(ckpt_path, map_location='cpu')
    cfg = ck.get('config', {})
    tower = cfg.get('tower', 'openvision2'); res = cfg.get('resolution', 224); patch = cfg.get('patch', 16)
    embed = cfg.get('embed_dim', EMBED)
    v = get_vision_tower(tower, width=cfg.get('width'), depth=cfg.get('depth'), heads=cfg.get('heads'), mlp_dim=cfg.get('mlp_dim'))
    w = v.head.proj.in_features; v.head = ReadoutHead(w, embed_dim=embed)
    if (res != 224 or patch != 16) and hasattr(v, 'embed'):
        v.embed = models.PatchEmbed(res, patch, v.embed.conv.out_channels); v.image_size = res; v.patch_size = patch
    v.load_state_dict(ck['vision'])
    return v.to(device).eval(), cfg

@torch.no_grad()
def encode_images(vision, imgs, device, bs=128):
    outs = []
    for i in range(0, imgs.shape[0], bs):
        b = imgs[i:i+bs].to(device).float().to(torch.bfloat16)
        with torch.autocast('cuda', dtype=torch.bfloat16): outs.append(vision(b).float())
    return torch.cat(outs)

@torch.no_grad()
def encode_train_full(vision, device, bs=256):
    import pyarrow.parquet as pq
    tf = get_transform(224, 'imagenet')
    files = sorted(glob.glob(IN1K_TRAIN_GLOB))
    all_feats, all_labels = [], []
    for fi, f in enumerate(files):
        table = pq.ParquetFile(f).read()
        imgs = table.column('image').to_pylist(); labs = table.column('label').to_numpy()
        tensors, file_labels = [], []
        for img_dict, lab in zip(imgs, labs):
            img = decode_img(img_dict)
            if img is not None: tensors.append(tf(img)); file_labels.append(int(lab))
        if not tensors: continue
        batch = torch.stack(tensors).half()
        feats = encode_images(vision, batch, device, bs)
        all_feats.append(feats.cpu()); all_labels.extend(file_labels)
        if fi % 5 == 0: print(f'  [train-encode] {fi+1}/{len(files)}: {sum(x.shape[0] for x in all_feats)} cumul', flush=True)
    return torch.cat(all_feats), torch.tensor(all_labels)

def knn_probe(Xtr, ytr, Xva, yva, k=5, device='cuda'):
    Xtr_n = torch.nn.functional.normalize(Xtr.float(), dim=-1).to(device)
    Xva_n = torch.nn.functional.normalize(Xva.float(), dim=-1).to(device)
    correct, total = 0, Xva_n.shape[0]; bs = 500
    for i in range(0, total, bs):
        batch = Xva_n[i:i+bs]; sim = batch @ Xtr_n.T
        topk_idx = sim.topk(k, dim=1).indices; topk_labels = ytr[topk_idx.cpu()]
        for j in range(topk_labels.shape[0]):
            vals, counts = torch.unique(topk_labels[j], return_counts=True)
            pred = vals[counts.argmax()]
            if pred == yva[i+j]: correct += 1
        if i % 5000 == 0: print(f'  [knn k={k}] {i}/{total}...', flush=True)
    return correct / total

def protocol_b_probe(Xtr, ytr, Xva, yva, device, epochs=90, lr=0.1, wd=0.0, bs=1024, seed=0):
    torch.manual_seed(seed)
    d = Xtr.shape[1]; clf = nn.Linear(d, 1000).to(device)
    opt = torch.optim.SGD(clf.parameters(), lr=lr, momentum=0.9, weight_decay=wd)
    ce = nn.CrossEntropyLoss()
    warmup_ep = 5; total_steps = epochs * (Xtr.shape[0] // bs); warmup_steps = warmup_ep * (Xtr.shape[0] // bs)
    def lr_at(step):
        if step < warmup_steps: return lr * step / max(1, warmup_steps)
        p = (step - warmup_steps) / max(1, total_steps - warmup_steps)
        return lr * 0.5 * (1 + math.cos(math.pi * p))
    Xtr_d = Xtr.float().to(device); ytr_d = ytr.to(device)
    Xva_d = Xva.float().to(device); yva_d = yva.to(device)
    step = 0
    for ep in range(epochs):
        perm = torch.randperm(Xtr_d.shape[0])
        for i in range(0, Xtr_d.shape[0], bs):
            idx = perm[i:i+bs]
            for g in opt.param_groups: g['lr'] = lr_at(step)
            opt.zero_grad(); ce(clf(Xtr_d[idx]), ytr_d[idx]).backward(); opt.step(); step += 1
        if ep % 30 == 0 or ep == epochs - 1:
            with torch.no_grad(): pred = clf(Xva_d).argmax(1); acc = (pred == yva_d).float().mean().item()
            print(f'  [probe ep={ep}/{epochs} lr={lr} wd={wd} s={seed}] val={acc*100:.2f}%', flush=True)
    with torch.no_grad(): pred = clf(Xva_d).argmax(1)
    return (pred == yva_d).float().mean().item()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True); ap.add_argument('--device', default='cuda:0')
    ap.add_argument('--knn-only', action='store_true'); ap.add_argument('--probe-only', action='store_true')
    ap.add_argument('--knn-per-class', type=int, default=50)
    ap.add_argument('--probe-epochs', type=int, default=450)
    args = ap.parse_args()
    device = torch.device(args.device); torch.cuda.set_device(device)
    print('[probe] Loading checkpoint...', flush=True)
    vision, cfg = load_vision(args.ckpt, device)
    print(f'[probe] {cfg.get("tower")} w={cfg.get("width")} d={cfg.get("depth")}', flush=True)
    print('[probe] Loading official IN-1k validation (50k)...', flush=True)
    val_imgs, val_labels = load_official_val(224)
    print('[probe] Encoding validation images...', flush=True)
    Xva = encode_images(vision, val_imgs, device, bs=256)
    del val_imgs; torch.cuda.empty_cache()
    print(f'[probe] Val features: {Xva.shape}', flush=True)
    results = {}
    if not args.probe_only:
        print('\n[probe] === k-NN Probe ===', flush=True)
        train_imgs, train_labels = load_train_subset(args.knn_per_class, 224)
        print(f'[probe] Train subset: {train_imgs.shape[0]} images', flush=True)
        Xtr_knn = encode_images(vision, train_imgs, device, bs=256)
        del train_imgs; torch.cuda.empty_cache()
        for k in [5, 10, 20]:
            acc = knn_probe(Xtr_knn, train_labels, Xva, val_labels, k=k, device=device)
            print(f'[probe] k-NN k={k}: top1={acc*100:.2f}%', flush=True); results[f'knn_k{k}'] = acc
        del Xtr_knn, train_labels; torch.cuda.empty_cache()
    if not args.knn_only:
        print('\n[probe] === Protocol B Enhanced ===', flush=True)
        Xtr_full, ytr_full = encode_train_full(vision, device, bs=256)
        print(f'[probe] Full train features: {Xtr_full.shape}', flush=True)
        print('\n[probe] ProtB baseline (90ep, lr=0.1, wd=0, s=0)...', flush=True)
        acc = protocol_b_probe(Xtr_full, ytr_full, Xva, val_labels, device, epochs=90, lr=0.1, wd=0.0, bs=1024, seed=0)
        print(f'[probe] ProtB 90ep: {acc*100:.2f}%', flush=True); results['protb_90ep_lr0.1_wd0_s0'] = acc
        print(f'\n[probe] ProtB ×5 ({args.probe_epochs}ep, lr=0.1, wd=0, s=0)...', flush=True)
        acc = protocol_b_probe(Xtr_full, ytr_full, Xva, val_labels, device, epochs=args.probe_epochs, lr=0.1, wd=0.0, bs=1024, seed=0)
        print(f'[probe] ProtB {args.probe_epochs}ep: {acc*100:.2f}%', flush=True); results[f'protb_{args.probe_epochs}ep'] = acc
        for wd in [1e-4, 1e-3]:
            acc = protocol_b_probe(Xtr_full, ytr_full, Xva, val_labels, device, epochs=90, lr=0.1, wd=wd, bs=1024, seed=0)
            print(f'[probe] ProtB wd={wd}: {acc*100:.2f}%', flush=True); results[f'protb_90ep_wd{wd}'] = acc
        for lr in [0.01, 0.3]:
            acc = protocol_b_probe(Xtr_full, ytr_full, Xva, val_labels, device, epochs=90, lr=lr, wd=0.0, bs=1024, seed=0)
            print(f'[probe] ProtB lr={lr}: {acc*100:.2f}%', flush=True); results[f'protb_90ep_lr{lr}'] = acc
        del Xtr_full, ytr_full; torch.cuda.empty_cache()
    print('\n' + '='*70, flush=True)
    print('PROBE COMPARISON SUMMARY (E1fair, BaiZe internal protocol)', flush=True)
    print('='*70, flush=True)
    print(f'{"Config":<35} {"top1%":>8}', flush=True); print('-'*70, flush=True)
    for name, acc in sorted(results.items()): print(f'{name:<35} {acc*100:>8.2f}', flush=True)
    print('='*70, flush=True)
    baseline = results.get('protb_90ep_lr0.1_wd0_s0')
    if baseline:
        print(f'Baseline (ProtB 90ep) = {baseline*100:.2f}%', flush=True)
        for name, acc in results.items():
            if name != 'protb_90ep_lr0.1_wd0_s0': print(f'  Δ ({name}): {(acc-baseline)*100:+.2f}pp', flush=True)
    print('='*70, flush=True)
    return results

if __name__ == '__main__': main()
