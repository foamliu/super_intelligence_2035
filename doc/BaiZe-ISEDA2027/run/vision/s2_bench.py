"""S2 inference benchmark: image -> token/s for the 4 candidate vision towers.

Single GPU, batch=1, bf16, fixed 224x224 / patch 16. Measures pure forward
latency/throughput (weights irrelevant to FLOPs; random-init used). CUDA-event
timing over <reps> forwards. Each image -> one 512-d pooled visual embedding
(ReadoutHead mean-pool + proj); we report img/s (= emb/s) plus raw patch-token/s.
"""
import torch

import models
from models import get_vision_tower, param_count


def bench(tower_name, device, res=224, patch=16, batch=1, warmup=50, reps=500):
    model = get_vision_tower(tower_name).to(device)
    model.eval()
    n_params = param_count(model) / 1e6
    img = torch.randn(batch, 3, res, res, device=device)

    with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
        for _ in range(warmup):
            _ = model(img)

    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    start.record()
    with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
        for _ in range(reps):
            _ = model(img)
    end.record()
    torch.cuda.synchronize()

    ms = start.elapsed_time(end) / reps
    img_s = 1000.0 / ms
    patch_tok_per_img = (res // patch) * (res // patch)
    patch_tok_s = img_s * patch_tok_per_img

    print(f"[S2] {tower_name:16s} params={n_params:6.1f}M  "
          f"lat={ms:7.2f}ms  img/s={img_s:8.1f}  emb/s={img_s:8.1f}  "
          f"patch_tok/s={patch_tok_s:10.0f}", flush=True)

    del model, img
    torch.cuda.empty_cache()
    return {'tower': tower_name, 'params': n_params, 'lat_ms': ms,
            'img_s': img_s, 'emb_s': img_s, 'patch_tok_s': patch_tok_s}


def main():
    torch.backends.cudnn.benchmark = True
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    res, patch, batch = 224, 16, 1
    print(f"[S2] device={device} batch={batch} res={res} patch={patch} dtype=bf16",
          flush=True)

    towers = ['openvision2', 'mambaeye', 'moevie', 'deepencoder_v2']
    results = [bench(t, device, res, patch, batch) for t in towers]

    print("--- S2 SUMMARY (batch=1, bf16, 224/16) ---", flush=True)
    for r in results:
        print(f"{r['tower']:16s} {r['params']:6.1f}M  "
              f"{r['lat_ms']:7.2f}ms  {r['img_s']:8.1f} img/s", flush=True)
    print("[S2] DONE", flush=True)


if __name__ == '__main__':
    main()