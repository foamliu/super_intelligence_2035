#!/usr/bin/env python
"""external_encoder_protb.py — Protocol B linear probing on public vision encoders.

Evaluates CLIP, SigLIP2, AIMv2, OpenVision2, RICE-ViT with Protocol B
(SGD+momentum0.9, cosine 90ep, bs1024, 3 seeds) — same probe protocol as BaiZe
from-scratch models, but each encoder uses its NATIVE resolution + NATIVE mean/std
preprocessing.  Features = pooled/CLS output.

RED LINE: Results are a REFERENCE TABLE for public pretrained encoders.
   Must NOT be mixed in the same table with BaiZe from-scratch results.

Usage:
  conda activate py310 && cd doc/BaiZe-ISEDA2027/run/vision
  python external_encoder_protb.py --smoke
  python external_encoder_protb.py --models clip-vitl14-336 --gpu 0
  python external_encoder_protb.py --gpu 0
  python external_encoder_protb.py --models clip-vitl14-336 --skip-extract --gpu 0
"""
import argparse, glob, json, math, os, sys, time
from io import BytesIO

# ── Thread limits (critical for parallel runs) ──
os.environ.setdefault('OMP_NUM_THREADS', '8')
os.environ.setdefault('MKL_NUM_THREADS', '8')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '8')
import pyarrow as pa
pa.set_cpu_count(8)

import torch
import torch.nn as nn
import torchvision.transforms as T
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lp_protocol_bridge import (
    linear_probe_mainstream,
    IN1K_TRAIN_GLOB, IN1K_VAL_GLOB,
    decode_img,
)

MODELS_DIR = '/nas_train/app.e0031982/models'
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'external_features_cache')

EXTERNAL_MODELS = {
    'clip-vitl14-336': {
        'path': f'{MODELS_DIR}/openai/clip-vit-large-patch14-336',
        'resolution': 336, 'encode_bs': 128, 'loader': 'clip',
        'mean': (0.48145466, 0.4578275, 0.40821073),
        'std':  (0.26862954, 0.26130258, 0.27577711),
        'feature_dim': 1024,
        'paper_lp': '~88.1% (CLIP ViT-L/14@336, OpenCLIP lp)',
    },
    'siglip2-so400m-384': {
        'path': f'{MODELS_DIR}/google/siglip2-so400m-patch14-384',
        'resolution': 384, 'encode_bs': 96, 'loader': 'siglip2',
        'mean': (0.5, 0.5, 0.5), 'std': (0.5, 0.5, 0.5),
        'feature_dim': 1152,
        'paper_lp': '~83.1% (SigLIP2 so400m@384, hf lp)',
    },
    'aimv2-1B-336': {
        'path': f'{MODELS_DIR}/apple/aimv2-1B-patch14-336',
        'resolution': 336, 'encode_bs': 64, 'loader': 'aimv2',
        'mean': (0.48145466, 0.4578275, 0.40821073),
        'std':  (0.26862954, 0.26130258, 0.27577711),
        'feature_dim': 2048,
        'paper_lp': '~87.6% (AIMv2-L 0.3B@336, frozen trunk)',
    },
    'openvision2-vitl14-336': {
        'path': f'{MODELS_DIR}/UCSC-VLAA/openvision2-vit-large-patch14-336-vision-only',
        'resolution': 336, 'encode_bs': 128, 'loader': 'openclip',
        'mean': (0.48145466, 0.4578275, 0.40821073),
        'std':  (0.26862954, 0.26130258, 0.27577711),
        'feature_dim': 1024,
        'paper_lp': '79.81% (OV2 L/14@336, BaiZe ProtA R13)',
    },
    'rice-vitl14-560': {
        'path': f'{MODELS_DIR}/DeepGlint-AI/rice-vit-large-patch14-560',
        'resolution': 560, 'encode_bs': 48, 'loader': 'rice',
        'mean': (0.48145466, 0.4578275, 0.40821073),
        'std':  (0.26862954, 0.26130258, 0.27577711),
        'feature_dim': 1024,
        'paper_lp': '~84.0% (RICE-ViT-L@560, estimated)',
    },
}

LOADERS = {}  # filled below

def get_transform(size, mean, std):
    return T.Compose([
        T.Resize(int(size * 1.15)),
        T.CenterCrop(size),
        T.ToTensor(),
        T.Normalize(mean, std),
    ])

# ── Model loaders ───────────────────────────────────────────────────

def load_clip(path, device):
    from transformers import CLIPVisionModel
    model = CLIPVisionModel.from_pretrained(path, dtype=torch.bfloat16)
    model = model.to(device).eval()
    feat_dim = model.config.hidden_size
    class Wrapper(nn.Module):
        def forward(self, x):
            out = self.model(pixel_values=x)
            if hasattr(out, 'pooler_output') and out.pooler_output is not None:
                return out.pooler_output
            return out.last_hidden_state[:, 0, :]
    w = Wrapper().to(device); w.model = model
    return w, feat_dim

def load_siglip2(path, device):
    _pooler_attr = 'pooler_output'
    try:
        from transformers import Siglip2VisionModel
        model = Siglip2VisionModel.from_pretrained(path, dtype=torch.bfloat16)
    except (ImportError, Exception) as e1:
        print(f'  [siglip2] Siglip2VisionModel failed ({e1}), trying SiglipVisionModel...', flush=True)
        from transformers import SiglipVisionModel
        model = SiglipVisionModel.from_pretrained(path, dtype=torch.bfloat16)
    model = model.to(device).eval()
    feat_dim = model.config.hidden_size
    class Wrapper(nn.Module):
        def forward(self, x):
            out = self.model(pixel_values=x)
            if hasattr(out, _pooler_attr) and getattr(out, _pooler_attr) is not None:
                return getattr(out, _pooler_attr)
            return out.last_hidden_state[:, 0, :]
    w = Wrapper().to(device); w.model = model
    return w, feat_dim

def load_aimv2(path, device):
    """Load AIMv2-1B using the custom modeling code shipped with the model.
    The checkpoint uses original Apple key names (embeddings.*, encoder.layers.*)
    while the HF-style modeling code uses preprocessor.*/trunk.blocks.* — so we
    remap the state dict before loading."""
    import importlib.util, types
    from safetensors.torch import load_file
    pkg_name = '_aimv2_pkg'
    pkg = types.ModuleType(pkg_name)
    pkg.__path__ = [path]
    sys.modules[pkg_name] = pkg
    spec_c = importlib.util.spec_from_file_location(
        f'{pkg_name}.configuration_aimv2',
        os.path.join(path, 'configuration_aimv2.py'),
        submodule_search_locations=[path])
    mod_c = importlib.util.module_from_spec(spec_c)
    sys.modules[f'{pkg_name}.configuration_aimv2'] = mod_c
    spec_c.loader.exec_module(mod_c)
    spec_m = importlib.util.spec_from_file_location(
        f'{pkg_name}.modeling_aimv2',
        os.path.join(path, 'modeling_aimv2.py'),
        submodule_search_locations=[path])
    mod_m = importlib.util.module_from_spec(spec_m)
    sys.modules[f'{pkg_name}.modeling_aimv2'] = mod_m
    spec_m.loader.exec_module(mod_m)
    # Instantiate model from config (NOT from_pretrained — keys don't match)
    config = mod_c.AIMv2Config.from_pretrained(path)
    model = mod_m.AIMv2Model(config)
    # Load raw checkpoint and remap keys
    sd = load_file(os.path.join(path, 'model.safetensors'))
    num_layers = config.num_hidden_layers
    remapped = {}
    # Embeddings → preprocessor
    if 'embeddings.patch_embed.weight' in sd:
        remapped['preprocessor.patchifier.proj.weight'] = sd['embeddings.patch_embed.weight']
    if 'embeddings.patch_embed.bias' in sd:
        remapped['preprocessor.patchifier.proj.bias'] = sd['embeddings.patch_embed.bias']
    if 'embeddings.position_embedding.weight' in sd:
        remapped['preprocessor.pos_embed'] = sd['embeddings.position_embedding.weight'].unsqueeze(0)
    if 'embeddings.rms_norm.weight' in sd:
        remapped['preprocessor.patchifier.norm.weight'] = sd['embeddings.rms_norm.weight']
    # Encoder layers → trunk blocks
    for i in range(num_layers):
        pfx_s = f'encoder.layers.{i}.'
        pfx_t = f'trunk.blocks.{i}.'
        # Attention: merge q/k/v into qkv
        q = sd.get(f'{pfx_s}attention.q_proj.weight')
        k = sd.get(f'{pfx_s}attention.k_proj.weight')
        v = sd.get(f'{pfx_s}attention.v_proj.weight')
        if q is not None and k is not None and v is not None:
            remapped[f'{pfx_t}attn.qkv.weight'] = torch.cat([q, k, v], dim=0)
        if f'{pfx_s}attention.out_proj.weight' in sd:
            remapped[f'{pfx_t}attn.proj.weight'] = sd[f'{pfx_s}attention.out_proj.weight']
        # FFN: gate→fc1, up→fc3, down→fc2
        if f'{pfx_s}ffn.gate_proj.weight' in sd:
            remapped[f'{pfx_t}mlp.fc1.weight'] = sd[f'{pfx_s}ffn.gate_proj.weight']
        if f'{pfx_s}ffn.up_proj.weight' in sd:
            remapped[f'{pfx_t}mlp.fc3.weight'] = sd[f'{pfx_s}ffn.up_proj.weight']
        if f'{pfx_s}ffn.down_proj.weight' in sd:
            remapped[f'{pfx_t}mlp.fc2.weight'] = sd[f'{pfx_s}ffn.down_proj.weight']
        # Norms
        if f'{pfx_s}rms_norm1.weight' in sd:
            remapped[f'{pfx_t}norm_1.weight'] = sd[f'{pfx_s}rms_norm1.weight']
        if f'{pfx_s}rms_norm2.weight' in sd:
            remapped[f'{pfx_t}norm_2.weight'] = sd[f'{pfx_s}rms_norm2.weight']
    # Final norm
    if 'rms_norm.weight' in sd:
        remapped['trunk.post_trunk_norm.weight'] = sd['rms_norm.weight']
    # Load remapped state dict
    missing, unexpected = model.load_state_dict(remapped, strict=False)
    if missing:
        print(f'  [aimv2] MISSING (first 5): {missing[:5]}', flush=True)
    if unexpected:
        print(f'  [aimv2] UNEXPECTED (first 5): {unexpected[:5]}', flush=True)
    if not missing and not unexpected:
        print(f'  [aimv2] All {len(remapped)} keys loaded successfully', flush=True)
    model = model.to(device).to(torch.bfloat16).eval()
    feat_dim = config.hidden_size
    class Wrapper(nn.Module):
        def forward(self, x):
            out = self.model(pixel_values=x)
            if isinstance(out, tuple): out = out[0]
            # AIMv2 has NO CLS token (576 patches only) -> use mean pooling
            if hasattr(out, 'last_hidden_state'):
                return out.last_hidden_state.mean(dim=1)
            return out.mean(dim=1)
    w = Wrapper().to(device); w.model = model
    return w, feat_dim

def load_openclip(path, device):
    """Load OpenVision2 vision-only model by building the vision tower from
    open_clip and loading the raw state dict (keys have no 'visual.' prefix)."""
    import open_clip
    from open_clip.model import _build_vision_tower, CLIPVisionCfg
    cfg_path = os.path.join(path, 'open_clip_config.json')
    with open(cfg_path) as f: full_cfg = json.load(f)
    model_cfg = full_cfg['model_cfg']
    # Build CLIPVisionCfg from dict (filter unknown keys gracefully)
    vis_cfg_dict = model_cfg['vision_cfg']
    import inspect
    valid_keys = set(inspect.signature(CLIPVisionCfg).parameters.keys())
    filtered = {k: v for k, v in vis_cfg_dict.items() if k in valid_keys}
    vis_cfg = CLIPVisionCfg(**filtered)
    vision_tower = _build_vision_tower(
        embed_dim=model_cfg['embed_dim'],
        vision_cfg=vis_cfg,
        quick_gelu=False,
    )
    # Load raw state dict (vision-only, no 'visual.' prefix)
    ckpt_path = os.path.join(path, 'open_clip_pytorch_model.bin')
    state_dict = torch.load(ckpt_path, map_location='cpu')
    clean_sd = {k.replace('module.', ''): v for k, v in state_dict.items()}
    missing, unexpected = vision_tower.load_state_dict(clean_sd, strict=False)
    if missing: print(f'  [openclip] missing (first 5): {missing[:5]}', flush=True)
    if unexpected: print(f'  [openclip] unexpected (first 5): {unexpected[:5]}', flush=True)
    vision_tower = vision_tower.to(device).to(torch.bfloat16).eval()
    feat_dim = model_cfg['embed_dim']
    class Wrapper(nn.Module):
        def forward(self, x):
            # VisionTransformer.forward returns (features, tokens) or features
            out = self.model(x)
            if isinstance(out, tuple): return out[0]
            return out
    w = Wrapper().to(device); w.model = vision_tower
    return w, feat_dim

def load_rice(path, device):
    from transformers import AutoModel
    model = AutoModel.from_pretrained(path, torch_dtype=torch.bfloat16, trust_remote_code=True)
    model = model.to(device).eval()
    feat_dim = model.config.hidden_size
    class Wrapper(nn.Module):
        def forward(self, x):
            out = self.model(pixel_values=x)
            if hasattr(out, 'pooler_output') and out.pooler_output is not None: return out.pooler_output
            if hasattr(out, 'last_hidden_state'): return out.last_hidden_state[:, 0, :]
            if isinstance(out, tuple): return out[0][:, 0, :]
            return out[:, 0, :]
    w = Wrapper().to(device); w.model = model
    return w, feat_dim

LOADERS = {'clip': load_clip, 'siglip2': load_siglip2, 'aimv2': load_aimv2,
           'openclip': load_openclip, 'rice': load_rice}

# ── Feature extraction ──────────────────────────────────────────────

def extract_features(wrapper, parquet_files, transform, device,
                     bs=128, max_images=None, desc=''):
    import pyarrow.parquet as pq
    all_feats, all_labels = [], []
    count = 0; t0 = time.time()
    for fi, f in enumerate(parquet_files):
        pf = pq.ParquetFile(f)
        for rb in pf.iter_batches(batch_size=bs * 4):
            imgs_col = rb.column('image').to_pylist()
            labs_col = rb.column('label').to_numpy()
            bt, bl = [], []
            for img_dict, lab in zip(imgs_col, labs_col):
                lab = int(lab)
                if lab < 0 or lab >= 1000: continue
                img = decode_img(img_dict)
                if img is None: continue
                bt.append(transform(img)); bl.append(lab)
            if not bt: continue
            # Process in sub-batches of bs (don't drop any images)
            for si in range(0, len(bt), bs):
                sub_bt = bt[si:si+bs]
                sub_bl = bl[si:si+bs]
                b = torch.stack(sub_bt).to(device).to(torch.bfloat16)
                with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
                    out = wrapper(b)
                pooled = out[0] if isinstance(out, tuple) else out
                all_feats.append(pooled.float().cpu()); all_labels.extend(sub_bl)
                count += len(sub_bl)
                if max_images and count >= max_images: break
            if max_images and count >= max_images: break
        elapsed = time.time() - t0
        speed = count / max(elapsed, 0.1)
        print(f'    [{desc}] {count} imgs, {fi+1}/{len(parquet_files)} files, '
              f'{speed:.0f} img/s, {elapsed:.0f}s', flush=True)
        if max_images and count >= max_images: break
    feats = torch.cat(all_feats); labels = torch.tensor(all_labels)
    elapsed = time.time() - t0
    print(f'    [{desc}] DONE: {feats.shape[0]} imgs, {elapsed:.0f}s, '
          f'{feats.shape[0]/max(elapsed,0.1):.0f} img/s', flush=True)
    return feats, labels

# ── Smoke test ───────────────────────────────────────────────────────

def smoke_test(model_name, cfg, device):
    print(f'\n[SMOKE] {model_name} (loader={cfg["loader"]})', flush=True)
    loader = LOADERS[cfg['loader']]
    try:
        wrapper, feat_dim = loader(cfg['path'], device)
        print(f'  Loaded OK, reported feature_dim={feat_dim}', flush=True)
    except Exception as e:
        import traceback; print(f'  LOAD FAILED: {e}', flush=True); traceback.print_exc()
        return False, None
    dummy = torch.randn(4, 3, cfg['resolution'], cfg['resolution'],
                        device=device, dtype=torch.bfloat16)
    try:
        with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
            out = wrapper(dummy)
        pooled = out[0] if isinstance(out, tuple) else out
        print(f'  Forward OK: output={pooled.shape}, dtype={pooled.dtype}', flush=True)
        assert pooled.shape[0] == 4
        assert pooled.shape[1] == feat_dim, f'Expected dim={feat_dim}, got {pooled.shape[1]}'
        print(f'  Shape check PASSED: (4, {feat_dim})', flush=True)
    except Exception as e:
        import traceback; print(f'  FORWARD FAILED: {e}', flush=True); traceback.print_exc()
        return False, feat_dim
    mem = torch.cuda.memory_allocated(device) / 1e9
    print(f'  GPU memory: {mem:.1f} GB', flush=True)
    del wrapper; torch.cuda.empty_cache()
    return True, feat_dim

# ── Full evaluation ─────────────────────────────────────────────────

def evaluate_model(model_name, cfg, device, cache_dir, seeds=(0,1,2),
                   skip_extract=False):
    print(f'\n{"="*72}', flush=True)
    print(f'[EVAL] {model_name}  res={cfg["resolution"]}  dim={cfg["feature_dim"]}  '
          f'loader={cfg["loader"]}', flush=True)
    print(f'{"="*72}', flush=True)
    train_cache = os.path.join(cache_dir, f'{model_name}_train.pt')
    val_cache   = os.path.join(cache_dir, f'{model_name}_val.pt')
    if skip_extract and os.path.exists(train_cache) and os.path.exists(val_cache):
        print('[EVAL] Loading cached features...', flush=True)
        td = torch.load(train_cache, map_location='cpu')
        vd = torch.load(val_cache, map_location='cpu')
        Xtr, ytr = td['features'], td['labels']
        Xva, yva = vd['features'], vd['labels']
        print(f'  Train: {Xtr.shape}, Val: {Xva.shape}', flush=True)
    else:
        loader = LOADERS[cfg['loader']]
        wrapper, feat_dim = loader(cfg['path'], device)
        tf = get_transform(cfg['resolution'], cfg['mean'], cfg['std'])
        val_files = sorted(glob.glob(IN1K_VAL_GLOB))
        print(f'[EVAL] Extracting val features ({len(val_files)} parquet)...', flush=True)
        Xva, yva = extract_features(wrapper, val_files, tf, device,
                                     bs=cfg['encode_bs'], desc=f'{model_name}-val')
        train_files = sorted(glob.glob(IN1K_TRAIN_GLOB))
        print(f'[EVAL] Extracting train features ({len(train_files)} parquet, ~1.28M)...', flush=True)
        Xtr, ytr = extract_features(wrapper, train_files, tf, device,
                                     bs=cfg['encode_bs'], desc=f'{model_name}-train')
        os.makedirs(cache_dir, exist_ok=True)
        torch.save({'features': Xtr, 'labels': ytr}, train_cache)
        torch.save({'features': Xva, 'labels': yva}, val_cache)
        print(f'[EVAL] Cached -> {train_cache} ({Xtr.element_size()*Xtr.nelement()/1e9:.1f} GB)', flush=True)
        del wrapper; torch.cuda.empty_cache()
    yva_dev = yva.to(device)
    results = []
    for seed in seeds:
        t0 = time.time()
        lp = linear_probe_mainstream(Xtr, ytr, Xva, yva_dev, device,
                                     epochs=90, batch_size=1024, lr=0.1,
                                     momentum=0.9, weight_decay=0.0,
                                     warmup_epochs=5, optimizer='sgd', seed=seed)
        elapsed = time.time() - t0
        results.append(lp)
        print(f'[EVAL] seed={seed}: lp={lp*100:.2f}%  [{elapsed:.0f}s]', flush=True)
    mean = sum(results) / len(results)
    std  = (sum((x - mean)**2 for x in results) / len(results)) ** 0.5
    print(f'[EVAL] {model_name}: ProtB = {mean*100:.2f}+/-{std*100:.2f}% '
          f'(runs: {[f"{r*100:.2f}" for r in results]})', flush=True)
    return {'model': model_name, 'resolution': cfg['resolution'],
            'feature_dim': cfg['feature_dim'], 'loader': cfg['loader'],
            'protb_mean': float(mean), 'protb_std': float(std),
            'protb_runs': [float(r) for r in results], 'seeds': list(seeds),
            'paper_lp': cfg.get('paper_lp', 'N/A')}

# ── Main ─────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description='Protocol B LP on external vision encoders')
    ap.add_argument('--models', nargs='+', default=None)
    ap.add_argument('--smoke', action='store_true')
    ap.add_argument('--gpu', type=int, default=0)
    ap.add_argument('--seeds', type=int, nargs='+', default=[0, 1, 2])
    ap.add_argument('--skip-extract', action='store_true')
    ap.add_argument('--cache-dir', type=str, default=CACHE_DIR)
    args = ap.parse_args()
    device = torch.device(f'cuda:{args.gpu}')
    torch.backends.cudnn.benchmark = True
    models_to_run = args.models or list(EXTERNAL_MODELS.keys())
    print('='*72, flush=True)
    print('[EXTERNAL-PROTB] Protocol B LP on Public Vision Encoders', flush=True)
    print(f'  device={device}  models={models_to_run}', flush=True)
    if args.smoke: print('  MODE: SMOKE TEST', flush=True)
    print('='*72, flush=True)
    if args.smoke:
        results = {}
        for name in models_to_run:
            cfg = EXTERNAL_MODELS[name]
            ok, fd = smoke_test(name, cfg, device)
            results[name] = {'smoke_ok': ok, 'feature_dim': fd, **cfg}
            torch.cuda.empty_cache()
        print('\n[SMOKE] Summary:', flush=True)
        for name, r in results.items():
            st = 'PASS' if r['smoke_ok'] else 'FAIL'
            print(f'  {st} {name}: res={r["resolution"]}, dim={r.get("feature_dim","?")}', flush=True)
        return
    all_results = []
    for name in models_to_run:
        cfg = EXTERNAL_MODELS[name]
        result = evaluate_model(name, cfg, device, args.cache_dir,
                                tuple(args.seeds), args.skip_extract)
        all_results.append(result)
    print('\n' + '='*72, flush=True)
    print('[EXTERNAL-PROTB] FINAL RESULTS', flush=True)
    print('='*72, flush=True)
    hdr = f'{"Model":<28} {"Res":>5} {"Dim":>6} {"ProtB":>14} {"Paper LP":>12}'
    print(hdr, flush=True); print('-'*len(hdr), flush=True)
    for r in all_results:
        print(f'{r["model"]:<28} {r["resolution"]:>5} {r["feature_dim"]:>6} '
              f'{r["protb_mean"]*100:>8.2f}+/-{r["protb_std"]*100:.2f} '
              f'{r["paper_lp"]:>12}', flush=True)
    print('-'*len(hdr), flush=True)
    results_path = os.path.join(os.path.dirname(args.cache_dir),
                                f'external_protb_results_{models_to_run[0]}.json'
                                if len(models_to_run) == 1
                                else 'external_protb_results.json')
    with open(results_path, 'w') as f: json.dump(all_results, f, indent=2)
    print(f'\n[EXTERNAL-PROTB] Results saved -> {results_path}', flush=True)

if __name__ == '__main__':
    main()
