#!/usr/bin/env python
"""Aggregate S4-S9 -> backfill HTML + tex. Usage: python finalize_backfill.py [/path/to/pipeline.log]"""
import re
import os
import sys

OUT = '/nas_train/app.e0031982/datasets/baize-vision/out'
PLOG = sys.argv[1] if len(sys.argv) > 1 else '/tmp/vision_pipeline.log'
HTML = '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/BAIZE_VISION_ENCODER_RESULT.html'
TEX = '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/ISEDA2027/6_vision_encoder.tex'


def parse_train_log(path):
    loss = None
    steady = None
    if not os.path.exists(path):
        return None, None
    for line in open(path):
        m = re.search(r'loss=(\d+\.\d+)', line)
        if m:
            loss = float(m.group(1))
        d = re.search(r'\[done\].*?steady_image_s=(\d+\.\d+)', line)
        if d:
            steady = float(d.group(1))
    return loss, steady


def fl(v):
    return 'PENDING' if v is None else f'{v:.4f}'


def fi(v):
    return 'PENDING' if v is None else f'{v:.1f}'


R = {}
for tlabel, key in [('openvision2', 'OV2'), ('deepencoder_v2', 'DE')]:
    for s in ['1234', '42', '7']:
        R[f'{key}_S{s}'] = parse_train_log(f'{OUT}/S4_{tlabel}_s{s}/train.log')

R['S6_224_16'] = parse_train_log(f'{OUT}/S4_openvision2_s1234/train.log')
for r, p in [(336, 16), (448, 16), (224, 14), (336, 14), (448, 14)]:
    R[f'S6_{r}_{p}'] = parse_train_log(f'{OUT}/S6_ov2_r{r}_p{p}/train.log')

R['S7_SIGLIP'] = parse_train_log(f'{OUT}/S7_ov2_siglip/train.log')
R['S7_CLIP'] = parse_train_log(f'{OUT}/S7_ov2_clip/train.log')
for lr in ['1e-3', '3e-3', '5e-3']:
    R['S8_' + lr.replace('-', '')] = parse_train_log(f'{OUT}/S8_ov2_lr{lr}/train.log')

s5 = {}
s9 = []
if os.path.exists(PLOG):
    cur = ''
    for line in open(PLOG):
        m = re.search(r'\[S5\] tower=(\S+)', line)
        if m:
            cur = m.group(1)
            s5.setdefault(cur, {})
        m = re.search(r'\[S5\] text->image R@1/5/10 = ([0-9./ ]+)', line)
        if m:
            s5[cur]['t2i'] = m.group(1).strip()
        m = re.search(r'\[S5\] image->text R@1/5/10 = ([0-9./ ]+)', line)
        if m:
            s5[cur]['i2t'] = m.group(1).strip()
        m = re.search(r'\[bench\] tower=(\S+) batch=(\d+) res=(\d+) patch=(\d+)', line)
        if m:
            s9.append([f"tower={m.group(1)} batch={m.group(2)} res={m.group(3)} patch={m.group(4)}", None])
        m = re.search(r'\[bench\] ms/img=([\d.]+)ms\s+image/s=([\d.]+)\s+token/s=([\d.]+)', line)
        if m and s9:
            s9[-1][1] = f"ms/img={m.group(1)} image/s={m.group(2)} token/s={m.group(3)}"

print('=== S4 ===')
for k in ['OV2_S1234', 'OV2_S42', 'OV2_S7', 'DE_S1234', 'DE_S42', 'DE_S7']:
    print(f'  {k}: loss={fl(R[k][0])} img/s={fi(R[k][1])}')
print('=== S6 ===')
for k in ['S6_224_16', 'S6_336_16', 'S6_448_16', 'S6_224_14', 'S6_336_14', 'S6_448_14']:
    print(f'  {k}: loss={fl(R[k][0])} img/s={fi(R[k][1])}')
print('=== S7 ===')
for k in ['S7_SIGLIP', 'S7_CLIP']:
    print(f'  {k}: loss={fl(R[k][0])} img/s={fi(R[k][1])}')
print('=== S8 ===')
for k in ['S8_1e3', 'S8_3e3', 'S8_5e3']:
    print(f'  {k}: loss={fl(R[k][0])} img/s={fi(R[k][1])}')
print('=== S5 ===')
for t, d in s5.items():
    print(f'  {t}: t2i={d.get("t2i")} i2t={d.get("i2t")}')
print('=== S9 ===')
for cfg, val in s9:
    print('  ' + cfg + ('  ' + val if val else ''))

# ---------- HTML backfill ----------
repl = {}
for k in ['OV2_S1234', 'OV2_S42', 'OV2_S7', 'DE_S1234', 'DE_S42', 'DE_S7']:
    repl[f'__{k}__'] = fl(R[k][0])
    repl[f'__{k}_T__'] = fi(R[k][1])
for k in ['S6_224_16', 'S6_336_16', 'S6_448_16', 'S6_224_14', 'S6_336_14', 'S6_448_14']:
    repl[f'__{k}__'] = fl(R[k][0])
    repl[f'__{k}_T__'] = fi(R[k][1])
for k in ['S7_SIGLIP', 'S7_CLIP']:
    repl[f'__{k}__'] = fl(R[k][0])
    repl[f'__{k}_T__'] = fi(R[k][1])
for k in ['S8_1e3', 'S8_3e3', 'S8_5e3']:
    repl[f'__{k}__'] = fl(R[k][0])
    repl[f'__{k}_T__'] = fi(R[k][1])

s5t = []
for t, d in s5.items():
    s5t.append(f'{t}: t2i R@1/5/10 = {d.get("t2i","?")} ; i2t R@1/5/10 = {d.get("i2t","?")}')
repl['__S5_RESULTS__'] = ' &nbsp;|&nbsp; '.join(s5t) if s5t else 'PENDING'

s9t = []
for cfg, val in s9:
    s9t.append(cfg + ('  ' + val if val else ''))
repl['__S9_RESULTS__'] = '\n'.join(s9t) if s9t else 'PENDING'

html = open(HTML).read()
for k, v in repl.items():
    html = html.replace(k, v)
open(HTML, 'w').write(html)
print(f'[HTML] backfilled {len(repl)} placeholders')

# ---------- TEX backfill ----------
tex = open(TEX).read()
res = {'224/16 (anchor)': 'S6_224_16', '336/16': 'S6_336_16', '448/16': 'S6_448_16',
       '224/14': 'S6_224_14', '336/14': 'S6_336_14', '448/14': 'S6_448_14'}
for label, key in res.items():
    l, s = R[key]
    need = f'{label} & {fl(l)} & {fi(s)} \\\\'
    esc = re.escape(label)
    pat = re.compile(esc + r'\s*&\s*\[TBD\]\s*&\s*\[TBD\]\s*\\\\')
    tex, n = pat.subn(need, tex)
    print(f'[TEX] res {key}: replaced={n}')

obj = {'SigLIP (anchor)': ('S7_SIGLIP', 'sigmoid contrastive'),
       'CLIP InfoNCE': ('S7_CLIP', 'softmax contrastive (scale differs)'),
       'lr $10^{-3}$ (anchor)': ('S8_1e3', '---'),
       r'lr $3{\times}10^{-3}$': ('S8_3e3', '---'),
       r'lr $5{\times}10^{-3}$': ('S8_5e3', '---')}
for label, (key, note) in obj.items():
    l, s = R[key]
    need = f'{label} & {fl(l)} & {note} \\\\'
    cur = f'{label} & [TBD] & {note} \\\\'
    if cur in tex:
        tex = tex.replace(cur, need)
        print(f'[TEX] obj {key}: replaced=1')
    else:
        print(f'[TEX] obj {key}: NOT FOUND')

open(TEX, 'w').write(tex)
rem = len(re.findall(r"\[TBD\]", tex))
print('[TEX] remaining [TBD] = ' + str(rem))
print('DONE')