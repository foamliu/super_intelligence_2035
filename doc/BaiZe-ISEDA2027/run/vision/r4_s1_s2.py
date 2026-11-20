#!/usr/bin/env python
"""R4 Step A (S1 + S2): CLIP token-length distribution + truncation ratio of the
LLaVA-OneVision imagenet/EN captions that feed contrastive training.

S1: sample N captions from the en500k webdataset, measure BPE token length via the
    exact SimpleTokenizer used in train.py, word count, and the fraction truncated to
    context_length=77.
S2: empty / ultra-short (<3 words) caption ratio.
"""
import argparse
import glob
import collections
import numpy as np
from open_clip.tokenizer import SimpleTokenizer

EN500K = '/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'


def read_captions(n):
    import tarfile
    shards = sorted(glob.glob(EN500K))
    caps = []
    for sp in shards:
        tf = tarfile.open(sp)
        for m in tf.getmembers():
            if not m.name.endswith('.txt'):
                continue
            cap = tf.extractfile(m).read().decode('utf-8', 'replace').strip()
            caps.append(cap)
            if len(caps) >= n:
                tf.close()
                return caps
        tf.close()
    return caps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=10000)
    args = ap.parse_args()

    caps = read_captions(args.n)
    print(f'[S1/S2] read {len(caps)} captions from en500k')

    tok = SimpleTokenizer()
    lens = []          # BPE token count (encode = no SOT/EOT, no truncation)
    words = []         # whitespace word count
    chars = []
    empty = 0
    short3 = 0
    for c in caps:
        if not c:
            empty += 1
            lens.append(0); words.append(0); chars.append(0)
            continue
        t = tok.encode(c)
        lens.append(len(t))
        w = len(c.split())
        words.append(w)
        chars.append(len(c))
        if w < 3:
            short3 += 1

    lens = np.array(lens, dtype=np.float64)
    words = np.array(words, dtype=np.float64)
    chars = np.array(chars, dtype=np.float64)
    # content tokens = context_length(77) - sot - eot = 75
    trunc = float((lens > 75).mean())

    def q(a, p):
        return float(np.percentile(a, p))

    print(f'--- S1: CLIP BPE token length (encode, no SOT/EOT) ---')
    print(f'  mean={lens.mean():.1f} median={q(lens,50):.0f} '
          f'p75={q(lens,75):.0f} p90={q(lens,90):.0f} p95={q(lens,95):.0f} '
          f'p99={q(lens,99):.0f} max={lens.max():.0f}')
    print(f'  words: mean={words.mean():.1f} median={q(words,50):.0f} '
          f'p90={q(words,90):.0f} max={words.max():.0f}')
    print(f'  chars: mean={chars.mean():.1f} median={q(chars,50):.0f}')
    print(f'  TRUNCATION at 77 (content tokens > 75): {trunc*100:.2f}%')
    print(f'  >60 words: {(words>60).mean()*100:.2f}%  >77 BPE: {(lens>77).mean()*100:.2f}%')
    # how much content survives truncation on average
    surv = np.minimum(lens, 75.0)
    print(f'  avg tokens retained after truncation: {surv.mean():.1f} '
          f'(={surv.mean()/lens.mean()*100:.1f}% of mean full length)')

    print(f'--- S2: empty / ultra-short captions ---')
    print(f'  empty ("")            : {empty}/{len(caps)} = {empty/len(caps)*100:.3f}%')
    print(f'  <3 words              : {short3}/{len(caps)} = {short3/len(caps)*100:.3f}%')
    print(f'  <=5 BPE tokens        : {(lens<=5).mean()*100:.3f}%')

    # formulaic-opening analysis: top common first-3-words prefixes
    prefixes = collections.Counter(
        ' '.join(c.split()[:3]).lower() for c in caps if c)
    print(f'--- formulaic openings (top 12 first-3-word prefixes) ---')
    for p, cnt in prefixes.most_common(12):
        print(f'  {cnt:5d} ({cnt/len(caps)*100:5.1f}%)  {p!r}')
    # top first-2-words
    p2 = collections.Counter(' '.join(c.split()[:2]).lower() for c in caps if c)
    print(f'  -- top first-2-word prefixes --')
    for p, cnt in p2.most_common(8):
        print(f'  {cnt:5d} ({cnt/len(caps)*100:5.1f}%)  {p!r}')
    print('[DONE]')


if __name__ == '__main__':
    main()