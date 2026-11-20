#!/usr/bin/env python
"""Parse S1 train.log files into a comparison table (loss + throughput)."""
import re
import os

OUT = os.environ.get('OUTROOT', '/nas_train/app.e0031982/datasets/baize-vision/out')
TOWERS = ['openvision2', 'mambaeye', 'moevie', 'deepencoder_v2']

print(f"{'tower':16} {'final_loss':>11} {'image/s':>9} {'ms/iter':>8} {'steps':>6}")
for t in TOWERS:
    lg = f'{OUT}/S1_{t}/train.log'
    if not os.path.exists(lg):
        print(f'{t:16} (no log)')
        continue
    steps, losses = [], []
    with open(lg) as f:
        for line in f:
            m = re.search(r'step (\d+)/\d+\] loss=([\d.]+) ms/iter=([\d.]+) image/s=([\d.]+)', line)
            if m:
                steps.append(int(m.group(1)))
                losses.append(float(m.group(2)))
            d = re.search(r'^\[done\].*steady_image_s=([\d.]+)', line)
            if d:
                steady = float(d.group(1))
    if not steps:
        print(f'{t:16} (running, no steps yet)')
        continue
    final = losses[-1]
    ms = float(m.group(3)) if m else 0
    img_s = float(m.group(4)) if m else 0
    print(f'{t:16} {final:11.4f} {img_s:9.1f} {ms:8.1f} {steps[-1]:6d}  steady={steady}')

# also dump loss history as CSV for plotting
for t in TOWERS:
    lg = f'{OUT}/S1_{t}/train.log'
    if not os.path.exists(lg):
        continue
    hist = []
    with open(lg) as f:
        for line in f:
            m = re.search(r'step (\d+)/\d+\] loss=([\d.]+)', line)
            if m:
                hist.append(f"{m.group(1)},{m.group(2)}")
    with open(f'/tmp/s1_loss_{t}.csv', 'w') as f:
        f.write('step,loss\n' + '\n'.join(hist) + '\n')
print('loss CSVs -> /tmp/s1_loss_<tower>.csv')