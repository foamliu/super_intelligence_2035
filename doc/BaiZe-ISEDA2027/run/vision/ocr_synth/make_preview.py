#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_preview.py — preview_200.html + preview_10k.tar for ocr_synth_10m.

Deliverable of the 2026-10-25 operator instruction §5:
  - preview_200.html: 200 thumbnails (base64 inline) + text + caption + cat,
    self-contained, 0 <script>, 0 external links.
  - preview_10k.tar: 10k raw jpg+json sample pack (for user trial runs).

Optimized: groups sampled keys by shard so each tar is opened ONCE (earlier
per-sample open re-read 225MB headers 200x -> timeout). CPU-only, light I/O.
Usage:
    python3 make_preview.py --data-dir <dir> [--n-preview 200] [--n-pack 10000]
"""
from __future__ import annotations
import argparse, base64, glob, io, json, os, random, tarfile, time
from PIL import Image


def _index_records(idx_path):
    recs = []
    with open(idx_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                recs.append(json.loads(line))
            except Exception:
                pass
    return recs


def _shard_of(rec, per_tar=5000):
    # Prefer the authoritative "shard" field written by the generator; fall back
    # to key//per_tar only if absent.
    s = rec.get("shard")
    if isinstance(s, int) and s >= 0:
        return s
    key = rec.get("key", "")
    try:
        gi = int(key)
    except Exception:
        gi = -1
    return gi // per_tar if gi >= 0 else 0


def _group_by_shard(recs, per_tar):
    by = {}
    for r in recs:
        by.setdefault(_shard_of(r, per_tar), {})[r.get("key", "")] = r
    return by


def _sample_by_cat(recs, n, rng):
    by_cat = {}
    for r in recs:
        by_cat.setdefault(r.get("cat", "?"), []).append(r)
    picked = []
    cats = sorted(by_cat.keys())
    total = len(recs)
    for c in cats:
        share = max(1, int(round(n * len(by_cat[c]) / max(total, 1))))
        share = min(share, len(by_cat[c]))
        picked.extend(rng.sample(by_cat[c], share))
    if len(picked) > n:
        picked = rng.sample(picked, n)
    return picked


def _iter_shard_samples(dd, sidx, keys):
    """Open shard once; yield (key, jpg_bytes, meta) for each key found."""
    tar_path = os.path.join(dd, f"shard-{sidx:06d}.tar")
    if not os.path.exists(tar_path):
        return
    try:
        with tarfile.open(tar_path) as tf:
            members = {m.name: m for m in tf.getmembers()}
            for key in keys:
                jm = members.get(f"{key}.jpg")
                jsm = members.get(f"{key}.json")
                if jm is None or jsm is None:
                    continue
                jpg_f = tf.extractfile(jm); js_f = tf.extractfile(jsm)
                if jpg_f is None or js_f is None:
                    continue
                try:
                    meta = json.loads(js_f.read())
                except Exception:
                    meta = {}
                yield key, jpg_f.read(), meta
    except Exception:
        return


def _thumb_b64(jpg_bytes, max_side=220):
    try:
        img = Image.open(io.BytesIO(jpg_bytes)).convert("RGB")
        img.thumbnail((max_side, max_side))
        buf = io.BytesIO(); img.save(buf, "JPEG", quality=80)
        return base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        return ""


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir",
                    default="/nas_train/app.e0031982/datasets/baize-vision/ocr_synth_10m_full")
    ap.add_argument("--n-preview", type=int, default=200)
    ap.add_argument("--n-pack", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20261026)
    ap.add_argument("--per-tar", type=int, default=5000)
    args = ap.parse_args()

    dd = args.data_dir
    idx_path = os.path.join(dd, "index.jsonl")
    recs = _index_records(idx_path)
    print(f"[preview] index records = {len(recs)}", flush=True)
    rng = random.Random(args.seed)

    # ---------- preview_200.html ----------
    sample = _sample_by_cat(recs, args.n_preview, rng)
    print(f"[preview] picked {len(sample)} for HTML", flush=True)
    grouped = _group_by_shard(sample, args.per_tar)
    rows = []
    t0 = time.time()
    for sidx, kw in sorted(grouped.items()):
        for key, jpg, meta in _iter_shard_samples(dd, sidx, list(kw.keys())):
            b64 = _thumb_b64(jpg)
            if not b64:
                continue
            rec = kw.get(key, {})
            rows.append({
                "cat": rec.get("cat", "?"), "lang": rec.get("lang", "?"),
                "key": key,
                "text": (meta or {}).get("text", "")[:200],
                "caption": (meta or {}).get("caption", "")[:120],
                "w": (meta or {}).get("w", ""), "h": (meta or {}).get("h", ""),
                "b64": b64,
            })
    print(f"[preview] HTML rows decoded = {len(rows)}  ({time.time()-t0:.1f}s)", flush=True)

    html = [
        "<!DOCTYPE html>",
        "<html lang='zh'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        "<title>BaiZe ocr_synth 预览 " + str(len(rows)) + " 张</title>",
        "<style>",
        "body{font-family:system-ui,Arial,sans-serif;margin:0;background:#f4f4f4;color:#222}",
        "h1{background:#2b3a55;color:#fff;padding:14px 18px;margin:0;font-size:18px}",
        ".sub{padding:8px 18px;background:#e8eef7;color:#445;font-size:13px}",
        ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px;padding:14px}",
        ".card{background:#fff;border:1px solid #ddd;border-radius:6px;padding:8px;overflow:hidden}",
        ".card img{width:100%;height:auto;border-radius:4px;display:block}",
        ".meta{font-size:11px;color:#666;margin-top:6px}",
        ".cat{display:inline-block;padding:1px 6px;border-radius:3px;background:#2b6cb0;color:#fff;font-size:10px;margin-right:4px}",
        ".txt{font-family:monospace;font-size:11px;background:#f7f7f7;border:1px solid #eee;padding:4px;margin-top:4px;max-height:64px;overflow:auto;white-space:pre-wrap;word-break:break-all}",
        ".cap{font-size:11px;color:#355;margin-top:4px;font-style:italic}",
        "</style></head><body>",
        f"<h1>BaiZe ocr_synth 预览（{len(rows)} / {len(recs)} 样本）</h1>",
        f"<div class='sub'>数据目录：{esc(dd)} · 自包含 HTML（0 script / 0 外链）· 缩略图 ≤220px</div>",
        "<div class='grid'>",
    ]
    for r in rows:
        html.append("<div class='card'>")
        html.append(f"<img src='data:image/jpeg;base64,{r['b64']}' alt='thumb'>")
        html.append(f"<div class='meta'><span class='cat'>{esc(r['cat'])}</span>"
                    f"{esc(r['lang'])} · {esc(r['key'])} · {esc(r['w'])}x{esc(r['h'])}</div>")
        html.append(f"<div class='txt'>{esc(r['text'])}</div>")
        html.append(f"<div class='cap'>caption: {esc(r['caption'])}</div>")
        html.append("</div>")
    html.append("</div></body></html>")
    out_html = os.path.join(dd, "preview_200.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write("\n".join(html))
    print(f"[preview] HTML -> {out_html}  size={os.path.getsize(out_html)}B", flush=True)

    # ---------- preview_10k.tar ----------
    pack = _sample_by_cat(recs, args.n_pack, rng)
    out_tar = os.path.join(dd, "preview_10k.tar")
    written = 0
    t0 = time.time()
    grouped2 = _group_by_shard(pack, args.per_tar)
    with tarfile.open(out_tar, "w") as tf:
        for sidx, kw in sorted(grouped2.items()):
            for key, jpg, meta in _iter_shard_samples(dd, sidx, list(kw.keys())):
                js = json.dumps(meta, ensure_ascii=False).encode("utf-8")
                ji = tarfile.TarInfo(name=f"{key}.jpg"); ji.size = len(jpg)
                tf.addfile(ji, io.BytesIO(jpg))
                si = tarfile.TarInfo(name=f"{key}.json"); si.size = len(js)
                tf.addfile(si, io.BytesIO(js))
                written += 1
            if written % 2000 < 50 and written > 0:
                print(f"  ...pack written={written} ({time.time()-t0:.1f}s)", flush=True)
    print(f"[preview] 10k pack -> {out_tar}  written={written}  size={os.path.getsize(out_tar)}B", flush=True)
    print(f"[preview] DONE")


if __name__ == "__main__":
    main()
