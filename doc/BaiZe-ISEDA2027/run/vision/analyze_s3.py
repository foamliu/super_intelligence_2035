#!/usr/bin/env python
"""Parse S3 long-horizon train.log files into a comparison table + loss-history CSVs."""
import re
import os

OUT = os.environ.get('OUTROOT', '/nas_train/app.e0031982/datasets/baize-vision/out')
# S3 towers in run order
TOWERS = ['openvision2', 'deepencoder_v2', 'mambaeye', 'moevie']

def parse(logpath):
    steps, losses, img_s = [], [], []
    steady = None
    if not os.path.exists(logpath):
        return steps, losses, img_s, steady, False
    with open(logpath) as f:
        for line in f:
            m = re.search(r'step (\d+)/\d+\] loss=([\d.]+) ms/iter=[\d.]+ image/s=([\d.]+)', line)
            if m:
                steps.append(int(m.group(1)))
                losses.append(float(m.group(2)))
                img_s.append(float(m.group(3)))
            d = re.search(r'^\[done\].*steady_image_s=([\d.]+)', line)
            if d:
                steady = float(d.group(1))
    return steps, losses, img_s, steady, True

print(f"{'tower':16} {'final_loss':>11} {'last_step':>9} {'steady_img/s':>12} {'done':>5}")
rows = {}
for t in TOWERS:
    steps, losses, img_s, steady, exists = parse(f'{OUT}/S3_{t}/train.log')
    if not exists or not steps:
        print(f'{t:16} (no log / not started)')
        continue
    rows[t] = (steps, losses)
    final = losses[-1]
    print(f'{t:16} {final:11.4f} {steps[-1]:9d} {steady if steady else max(img_s[-20:]):12.1f} {str(exists):>5}')
    # dump loss history CSV
    with open(f'/tmp/s3_loss_{t}.csv', 'w') as fh:
        fh.write('step,loss\n' + '\n'.join(f'{s},{l}' for s, l in zip(steps, losses)) + '\n')

# print loss at key checkpoints (500 / 1000 / 5000 / 10000) for cross-arch comparison
checkpoints = {500: '500', 1000: '1000', 5000: '5000', 10000: '10000'}
print('\nLoss at checkpoints:')
print(f"{'tower':16} " + ' '.join(f'{k:>9}' for k in checkpoints))
for t, (steps, losses) in rows.items():
    vals = []
    for cp in checkpoints:
        idx = next((i for i, s in enumerate(steps) if s >= cp), None)
        vals.append(f'{losses[idx]:9.4f}' if idx is not None else '      nan')
    print(f'{t:16} ' + ' '.join(vals))
print('\nloss CSVs -> /tmp/s3_loss_<tower>.csv')