#!/usr/bin/env python
"""R4 Step B dataset comparison: Stanford GPIC caption-granularity analysis.

Reads GPIC tar shards and reports, per caption_type (tag/short/medium/long):
  image count, CLIP-BPE token length distribution, word count, license mix.
Also computes how much of the corpus is available on disk.
"""
import argparse
import glob
import json
import tarfile
import collections
import numpy as np
from open_clip.tokenizer import SimpleTokenizer

GPIC_TRAIN = '/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar'


def scan_tars(n_tars):
    shards = sorted(glob.glob(GPIC_TRAIN))
    tok = SimpleTokenizer()
    agg = collections.defaultdict(lambda: dict(
        n=0, toks=[], words=[], chars=[], licenses=collections.Counter(),
        empty=0, trunc=0))
    limgs = 0
    for sp in shards[:n_tars]:
        tf = tarfile.open(sp)
        for m in tf.getmembers():
            if not m.name.endswith('.json'):
                continue
            f = tf.extractfile(m)
            try:
                d = json.load(f)
            except Exception:
                continue
            cap = (d.get('caption') or '').strip()
            ctype = d.get('caption_type') or '?'
            lic = d.get('license') or '?'
            w = len(cap.split())
            t = len(tok.encode(cap)) if cap else 0
            a = agg[ctype]
            a['n'] += 1
            a['words'].append(w)
            a['chars'].append(len(cap))
            a['toks'].append(t)
            a['licenses'][lic] += 1
            if not cap:
                a['empty'] += 1
            if t > 75:
                a['trunc'] += 1
            limgs += 1
            limgs_n = (m.name.endswith('.jpg') or m.name.endswith('.png'))
        tf.close()
    return agg, len(shards)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tars', type=int, default=6)
    args = ap.parse_args()

    total_tars = len(glob.glob(GPIC_TRAIN))
    print(f'[GPIC] total tars on disk = {total_tars} (of 8000 in full set)')
    agg, n = scan_tars(args.tars)
    print(f'[GPIC] scanned {args.tars} tars')

    print(f'{"type":8s} {"n_img":>8s} {"%":>6s} {"tok mean":>9s} '
          f'{"tok med":>7s} {"tok p90":>7s} {"tok max":>7s} '
          f'{"w mean":>7s} {"trunc77":>7s} {"empty":>6s}')
    tot = sum(a['n'] for a in agg.values())
    for ctype in ['tag', 'short', 'medium', 'long']:
        a = agg.get(ctype)
        if not a:
            continue
        t = np.array(a['toks'], dtype=float)
        w = np.array(a['words'], dtype=float)
        print(f'{ctype:8s} {a["n"]:8d} {a["n"]/tot*100:5.1f}% '
              f'{t.mean():9.1f} {np.median(t):7.0f} '
              f'{np.percentile(t,90):7.0f} {t.max():7.0f} '
              f'{w.mean():7.1f} {a["trunc"]/a["n"]*100:6.2f}% {a["empty"]:6d}')

    print(f'\n[GPIC] license mix (across scanned tars):')
    lic_all = collections.Counter()
    for a in agg.values():
        lic_all.update(a['licenses'])
    for lic, cnt in lic_all.most_common(10):
        print(f'  {lic:20s} {cnt:6d} ({cnt/sum(lic_all.values())*100:.1f}%)')

    # sample captions per type for reference
    print(f'\n[GPIC] sample captions per type:')
    shards = sorted(glob.glob(GPIC_TRAIN))
    shown = set()
    for sp in shards[:3]:
        tf = tarfile.open(sp)
        for m in tf.getmembers():
            if not m.name.endswith('.json'):
                continue
            d = json.load(tf.extractfile(m))
            ctype = d.get('caption_type')
            if ctype in shown:
                continue
            shown.add(ctype)
            print(f'  [{ctype}] ({len((d.get("caption") or "").split())} words) '
                  f'{(d.get("caption") or "")[:180]!r}')
            if len(shown) >= 4:
                tf.close()
                print('[DONE]')
                return
        tf.close()
    print('[DONE]')


if __name__ == '__main__':
    main()