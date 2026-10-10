#!/usr/bin/env python
"""zeroshot_in1k_eval.py — Same-model zero-shot evaluation on IN-1k (2026-10-10 ①).

PURPOSE (operator instruction 2026-10-10 ①):
  Answer "did the features benefit from text alignment?" by running the model's
  OWN zero-shot classification on IN-1k, then comparing lp vs zs.

PATHWAY (精确构造):
  - Vision: OpenVision2 w512/d30 ViT → ReadoutHead (LayerNorm + mean-pool +
    Linear(512→768)) → 768-d image features. This head was trained via InfoNCE
    to align with the frozen CLIP text tower's 768-d space.
  - Text: Frozen CLIP-ViT-L/14-336 text tower (768-d), loaded from
    /nas_train/app.e0031982/models/openai/clip-vit-large-patch14-336.
    get_text_features(ids) → 768-d text embedding.
  - Prompts: 1000 IN-1k class names × 80 OpenAI templates (from open_clip),
    averaged per class, L2-normalized → (1000, 768) text class embeddings.
  - Classification: cosine_sim(image_features, text_class_embeddings) → argmax.
  - Temperature: logit_scale from checkpoint (learned during training).

EVAL SET: Official IN-1k validation (50k images, 14 parquet files, labels 0-999).
  Normalization: ImageNet mean/std (same as Protocol B).

Usage:
  cd doc/BaiZe-ISEDA2027/run/vision
  python zeroshot_in1k_eval.py --ckpt /path/to/vision.pt [--ckpt2 /path/to/vision2.pt]
"""
import argparse, glob, math
from io import BytesIO
import torch, torchvision.transforms as T
from PIL import Image
import models
from models import get_vision_tower, ReadoutHead
from r7_train import FrozenClipText, CLIP_PATH, EMBED
from open_clip import IMAGENET_CLASSNAMES, OPENAI_IMAGENET_TEMPLATES

IN1K_VAL_GLOB = '/nas_train/app.e0031982/datasets/imagenet-1k/data/validation-*.parquet'
IN_MEAN = (0.485, 0.456, 0.406)
IN_STD  = (0.229, 0.224, 0.225)

def get_val_transform(size=224):
    return T.Compose([T.Resize(int(size*1.15)), T.CenterCrop(size),
                      T.ToTensor(), T.Normalize(IN_MEAN, IN_STD)])

def decode_img(image_dict):
    raw = image_dict.get('bytes') or b''
    if not raw: return None
    return Image.open(BytesIO(raw)).convert('RGB')

def load_official_val(size=224):
    import pyarrow.parquet as pq
    tf = get_val_transform(size)
    files = sorted(glob.glob(IN1K_VAL_GLOB))
    tensors, labels = [], []
    for f in files:
        table = pq.ParquetFile(f).read()
        imgs = table.column('image').to_pylist()
        labs = table.column('label').to_numpy()
        for img_dict, lab in zip(imgs, labs):
            img = decode_img(img_dict)
            if img is not None:
                tensors.append(tf(img)); labels.append(int(lab))
        print(f'  [val] {f.split("/")[-1]}: {len(tensors)} cumulative', flush=True)
    return torch.stack(tensors).half(), torch.tensor(labels)

def load_vision(ckpt_path, device):
    ck = torch.load(ckpt_path, map_location='cpu')
    cfg = ck.get('config', {})
    tower = cfg.get('tower', 'openvision2')
    res = cfg.get('resolution', 224); patch = cfg.get('patch', 16)
    embed = cfg.get('embed_dim', EMBED)
    v = get_vision_tower(tower, width=cfg.get('width'), depth=cfg.get('depth'),
                         heads=cfg.get('heads'), mlp_dim=cfg.get('mlp_dim'))
    w = v.head.proj.in_features
    v.head = ReadoutHead(w, embed_dim=embed)
    if (res != 224 or patch != 16) and hasattr(v, 'embed'):
        v.embed = models.PatchEmbed(res, patch, v.embed.conv.out_channels)
        v.image_size = res; v.patch_size = patch
    v.load_state_dict(ck['vision'])
    logit_scale = ck.get('logit_scale', torch.tensor(math.log(10)))
    return v.to(device).eval(), logit_scale.to(device), cfg

@torch.no_grad()
def encode_images(vision, imgs, device, bs=128):
    outs = []
    for i in range(0, imgs.shape[0], bs):
        b = imgs[i:i+bs].to(device).float().to(torch.bfloat16)
        with torch.autocast('cuda', dtype=torch.bfloat16):
            outs.append(vision(b).float())
    return torch.cat(outs)

@torch.no_grad()
def text_class_embeddings(text, device):
    feats = []
    for name in IMAGENET_CLASSNAMES:
        caps = [t(name) for t in OPENAI_IMAGENET_TEMPLATES]
        ids = text.tokenize(caps).to(device)
        with torch.autocast('cuda', dtype=torch.bfloat16):
            z = text(ids).float()
        feats.append(z.mean(0))
    Z = torch.stack(feats)
    return torch.nn.functional.normalize(Z, dim=-1)

def zero_shot_eval(I, Z, logit_scale):
    In = torch.nn.functional.normalize(I.float(), dim=-1)
    sim = In @ Z.T * logit_scale.exp()
    pred = sim.argmax(1)
    top5 = sim.topk(5, dim=1).indices
    return pred, top5

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', required=True)
    ap.add_argument('--ckpt2', default=None)
    ap.add_argument('--bs', type=int, default=256)
    ap.add_argument('--device', default='cuda:0')
    args = ap.parse_args()
    device = torch.device(args.device)
    torch.cuda.set_device(device)
    print('[zs] Loading frozen CLIP text tower...', flush=True)
    text = FrozenClipText(CLIP_PATH, device)
    print('[zs] Computing text class embeddings (1000 classes × 80 templates)...', flush=True)
    Z = text_class_embeddings(text, device)
    print(f'[zs] Text embeddings: {Z.shape}', flush=True)
    print('[zs] Loading official IN-1k validation (50k)...', flush=True)
    val_imgs, val_labels = load_official_val(224)
    val_labels = val_labels.to(device)
    ckpts = [(args.ckpt, 'E1fair')]
    if args.ckpt2: ckpts.append((args.ckpt2, 'E2fair'))
    results = {}
    for ckpt_path, name in ckpts:
        print(f'\n[zs] === {name}: {ckpt_path} ===', flush=True)
        vision, logit_scale, cfg = load_vision(ckpt_path, device)
        print(f'[zs] w={cfg.get("width")} d={cfg.get("depth")} embed={cfg.get("embed_dim")}', flush=True)
        print(f'[zs] logit_scale={logit_scale.item():.4f} temp={logit_scale.exp().item():.4f}', flush=True)
        I = encode_images(vision, val_imgs, device, bs=args.bs)
        pred, top5 = zero_shot_eval(I, Z, logit_scale)
        top1 = (pred == val_labels).float().mean().item()
        top5_acc = (top5 == val_labels.unsqueeze(1)).any(dim=1).float().mean().item()
        In = torch.nn.functional.normalize(I.float(), dim=-1)
        pred_raw = (In @ Z.T).argmax(1)
        top1_raw = (pred_raw == val_labels).float().mean().item()
        print(f'[zs] {name} zs: top1={top1*100:.2f}% top5={top5_acc*100:.2f}% (raw cosine: {top1_raw*100:.2f}%)', flush=True)
        results[name] = {'top1': top1, 'top5': top5_acc, 'top1_raw': top1_raw, 'logit_scale': logit_scale.item()}
        del vision, I; torch.cuda.empty_cache()
    print('\n' + '='*60, flush=True)
    print('SAME-MODEL ZERO-SHOT SUMMARY (BaiZe internal protocol)', flush=True)
    print('='*60, flush=True)
    print(f'{"Arm":<12} {"top1%":>8} {"top5%":>8} {"raw%":>8} {"logit_scale":>12}', flush=True)
    for name, r in results.items():
        print(f'{name:<12} {r["top1"]*100:>8.2f} {r["top5"]*100:>8.2f} {r["top1_raw"]*100:>8.2f} {r["logit_scale"]:>12.4f}', flush=True)
    print('='*60, flush=True)
    print('Pathway: ViT→ReadoutHead(768-d)→InfoNCE-aligned→CLIP text(frozen)×80 templates', flush=True)
    print('Eval: Official IN-1k val (50k, ImageNet norm)', flush=True)
    print('='*60, flush=True)
    return results

if __name__ == '__main__': main()
