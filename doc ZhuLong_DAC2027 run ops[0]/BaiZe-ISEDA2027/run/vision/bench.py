"""S2 inference benchmark: unified forward timing (single GPU, bf16).

Reports image->token/s for the pure vision tower (no text tower). Batch is the
inference batch (default 1). tokens = images * patch_count.
"""
import argparse
import time
import torch
import models


def run(tower, resolution, patch, batch, iters, warmup):
    m = models.get_vision_tower(tower)
    m.image_size = resolution
    m.patch_size = patch
    # Rebuild the patch embed for the requested resolution/patch (mirrors train.py),
    # otherwise the learned positional embedding (sized for 224/16 = 196 patches)
    # mismatches the patch grid and crashes for multi-resolution inference.
    if resolution != 224 or patch != 16:
        m.embed = models.PatchEmbed(resolution, patch, m.embed.conv.out_channels)
    gridside = resolution // patch
    n_patches = gridside * gridside
    m = m.cuda().eval()
    x = torch.randn(batch, 3, resolution, resolution, device='cuda')

    # warmup
    with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
        for _ in range(warmup):
            m(x)
    torch.cuda.synchronize()

    times = []
    with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
        for _ in range(iters):
            t0 = torch.cuda.Event(enable_timing=True)
            t1 = torch.cuda.Event(enable_timing=True)
            t0.record()
            m(x)
            t1.record()
            torch.cuda.synchronize()
            times.append(t0.elapsed_time(t1))

    ms = sum(times) / len(times)
    img_s = batch / (ms / 1000.0)
    tok_s = img_s * n_patches
    return ms, img_s, tok_s, n_patches


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--tower', required=True)
    ap.add_argument('--resolution', type=int, default=224)
    ap.add_argument('--patch', type=int, default=16)
    ap.add_argument('--batch', type=int, default=1)
    ap.add_argument('--iters', type=int, default=100)
    ap.add_argument('--warmup', type=int, default=30)
    args = ap.parse_args()
    ms, img_s, tok_s, np_ = run(args.tower, args.resolution, args.patch,
                                args.batch, args.iters, args.warmup)
    print(f'[bench] tower={args.tower} batch={args.batch} res={args.resolution} '
          f'patch={args.patch} patches={np_}')
    print(f'[bench] ms/img={ms/args.batch:.3f}ms  image/s={img_s:.1f}  token/s={tok_s:.1f}')