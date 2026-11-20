#!/usr/bin/env python
"""R4 S1 decisive experiment: does 77-token truncation throw away the DISTINCTIVE part
of LLaVA long recaptions?

For long captions (BPE > 75 content tokens) we embed, with the FROZEN CLIP text tower:
  - head = first 75 content tokens  (what truncation KEEPS)
  - tail = last  75 content tokens  (what truncation DISCARDS)
If head's pairwise off-diagonal cosine is clearly HIGHER than tail's (i.e. the kept
prefix is formulaic/similar while the discarded tail carries the discriminative detail),
then truncation directly reduces negative-sample distinctiveness (confirms S1).
"""
import argparse, glob, tarfile
import torch

CLIP_PATH = '/nas_train/app.e0031982/models/openai/clip-vit-large-patch14-336'
EN500K = '/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'


def read_llava(n):
    caps = []
    for sp in sorted(glob.glob(EN500K)):
        tf = tarfile.open(sp)
        for m in tf.getmembers():
            if not m.name.endswith('.txt'):
                continue
            cap = tf.extractfile(m).read().decode('utf-8', 'replace').strip()
            if cap:
                caps.append(cap)
            if len(caps) >= n:
                tf.close()
                return caps
        tf.close()
    return caps


def offdiag(F):
    Fn = torch.nn.functional.normalize(F.float(), dim=-1)
    G = Fn @ Fn.T
    n = G.shape[0]
    eye = torch.eye(n, dtype=torch.bool, device=G.device)
    off = G[~eye].reshape(n, n - 1)
    return off.mean().item(), off.min().item(), off.max().item(), off.quantile(0.9).item()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=2500)
    args = ap.parse_args()
    device = torch.device('cuda')

    from transformers import CLIPModel, CLIPTokenizer
    clip = CLIPModel.from_pretrained(CLIP_PATH, local_files_only=True).to(device).eval()
    for p in clip.parameters():
        p.requires_grad_(False)
    tok = CLIPTokenizer.from_pretrained(CLIP_PATH, local_files_only=True)
    bos, eos = tok.bos_token_id, tok.eos_token_id
    pad = tok.pad_token_id if tok.pad_token_id is not None else eos

    caps = read_llava(args.n)
    heads, tails, kept = [], [], 0
    for c in caps:
        enc = tok(c, add_special_tokens=False)['input_ids']
        if len(enc) <= 75:
            continue
        h = enc[:75]
        t = enc[-75:]
        heads.append([bos] + h + [eos] + [pad] * (75 - len(h)))
        tails.append([bos] + t + [eos] + [pad] * (75 - len(t)))
        kept += 1

    H = torch.tensor(heads, device=device)
    T = torch.tensor(tails, device=device)
    print(f'[S1-dec] {len(caps)} sampled, {kept} long captions (>75 BPE, i.e. truncated)')

    def embed(ids):
        F = []
        for i in range(0, ids.shape[0], 128):
            with torch.no_grad(), torch.autocast('cuda', dtype=torch.bfloat16):
                F.append(clip.get_text_features(ids[i:i+128]).float())
        return torch.cat(F)

    Fh = embed(H)
    Ft = embed(T)
    hm, hmn, hmx, hp90 = offdiag(Fh)
    tm, tmn, tmx, tp90 = offdiag(Ft)
    print(f'  HEAD (kept,  first 75 tok): offdiag mean={hm:.4f} min={hmn:.4f} max={hmx:.4f} p90={hp90:.4f}')
    print(f'  TAIL (discarded, last 75 tok): offdiag mean={tm:.4f} min={tmn:.4f} max={tmx:.4f} p90={tp90:.4f}')
    # also: is head MORE self-similar than tail on a per-caption basis (head vs its own tail)?
    Hn = torch.nn.functional.normalize(Fh, dim=-1)
    Tn = torch.nn.functional.normalize(Ft, dim=-1)
    self_sim = (Hn * Tn).sum(-1)
    print(f'  mean cosine(head_i, tail_i of same caption) = {self_sim.mean().item():.4f} '
          f'(low => head & tail carry DIFFERENT info)')
    print(f'  => head offdiag - tail offdiag = {hm - tm:+.4f} '
          f'({"head MORE concentrated -> truncation hurts" if hm > tm + 0.02 else "no clear truncation effect"})')
    print('[DONE]')


if __name__ == '__main__':
    main()