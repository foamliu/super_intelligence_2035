#!/usr/bin/env python
"""Aggregate S4-S9 results into a single comparison summary (for HTML/tex backfill).

Reads out/Sx_*/train.log final loss + steady throughput, and extracts S5/S9
stdout (retrieval R@K / bench) from the pipeline log. Run on either node (NFS).
"""
import re
import os
import glob

OUT = os.environ.get('OUTROOT', '/nas_train/app.e0031982/datasets/baize-vision/out')


def final_loss(path):
    loss, steady = None, None
    if not os.path.exists(path):
        return None, None
    for line in open(path):
        m = re.search(r'loss=(\d+\.\d+)', line)
        if m:
            loss = float(m.group(1))
        d = re.search(r'\[done\].*steady_image_s=(\d+\.\d+)', line)
        if d:
            steady = float(d.group(1))
    return loss, steady


def done(path):
    return os.path.exists(path) and '[done]' in open(path).read()


def main():
    print('=== S4 multi-seed ===')
    for t in ['openvision2', 'deepencoder_v2']:
        for s in ['1234', '42', '7']:
            p = f'{OUT}/S4_{t}_s{s}/train.log'
            loss, steady = final_loss(p)
            print(f'  {t}_s{s}: loss={loss} img/s={steady} done={done(p)}')

    print('=== S6 resolution/patch (openvision2) ===')
    for r, pt in [(224, 16), (336, 16), (448, 16), (224, 14), (336, 14), (448, 14)]:
        p = f'{OUT}/S6_ov2_r{r}_p{pt}/train.log'
        loss, steady = final_loss(p)
        print(f'  r{r}/p{pt}: loss={loss} img/s={steady} done={done(p)}')

    print('=== S7 objective (openvision2) ===')
    for l in ['siglip', 'clip']:
        p = f'{OUT}/S7_ov2_{l}/train.log'
        loss, steady = final_loss(p)
        print(f'  {l}: loss={loss} img/s={steady} done={done(p)}')

    print('=== S8 lr sweep (openvision2) ===')
    for lr in ['1e-3', '3e-3', '5e-3']:
        p = f'{OUT}/S8_ov2_lr{lr}/train.log'
        loss, steady = final_loss(p)
        print(f'  lr={lr}: loss={loss} img/s={steady} done={done(p)}')

    # S5 / S9 stdout live in pipeline log (on 10.239.2.12 local /tmp)
    print('=== S5 retrieval / S9 bench (from /tmp/vision_pipeline.log if present) ===')
    plog = '/tmp/vision_pipeline.log'
    if os.path.exists(plog):
        for line in open(plog):
            if re.search(r'\[S5\]|\[bench\]', line):
                print(' ', line.rstrip())
    else:
        print('  (no local pipeline log here; run on 10.239.2.12 or grep its /tmp)')


if __name__ == '__main__':
    main()