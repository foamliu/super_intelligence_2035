#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""postprocess_ocr_synth.py — independent quality validation for ocr_synth_10m.

Required deliverable of the 2026-10-25 operator instruction §4 (quality & leakage):
  - cross-shard text-SHA1 dedup re-check (independent of gen's inline seen_sha)
  - REAL eval-leakage check vs OCRBench / DocVQA / ChartQA / InfoVQA
  - per-category count / text-length / byte aggregation
  -> emits VALIDATION.json + stdout summary

IMPORTANT: gen_ocr_synth._load_leakage_hashes() only searched ~/.cache/huggingface,
but the eval sets live under /nas_env/app.e0031982/hf_home/hub/. So the inline guard
was a NO-OP (STATS reports 'leakage eval files found: 0'). This script performs the
REAL post-hoc check by reading the actual eval parquet files and intersecting their
normalized question+answer hashes with the index.jsonl text_sha1 column.

Canonicalization MUST match gen_ocr_synth._norm_hash:
    sha1( ''.join(ch for ch in text.lower() if ch.isalnum()) )

CPU-only, single-process, light I/O. Safe alongside the running generator on .12.
"""
from __future__ import annotations
import argparse, glob, hashlib, json, os, sys, time
import numpy as np


def norm_hash(text):
    t = "".join(ch for ch in text.lower() if ch.isalnum())
    return hashlib.sha1(t.encode("utf-8")).hexdigest()


def _iter_text_cols(parquet_path):
    try:
        import pyarrow.parquet as pq
    except Exception as e:
        print(f"  [warn] pyarrow unavailable: {e}"); return
    try:
        pf = pq.ParquetFile(parquet_path)
    except Exception as e:
        print(f"  [warn] cannot open {parquet_path}: {e}"); return
    text_cols = [f.name for f in pf.schema_arrow
                 if f.name.lower() in ("question", "answer", "answers", "query",
                 "queries", "text", "label", "solution", "response", "gt")]
    if not text_cols:
        return
    for batch in pf.iter_batches(columns=text_cols, batch_size=1024):
        d = batch.to_pydict()
        for col in text_cols:
            for v in d[col]:
                if isinstance(v, str) and v.strip():
                    yield v
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, str) and item.strip():
                            yield item


def build_eval_hash_set(eval_root):
    found = {}
    hset = set()
    if not eval_root or not os.path.isdir(eval_root):
        return found, hset
    targets = {
        "OCRBench": ["**/datasets--echo840--OCRBench/**/*.parquet"],
        "DocVQA":   ["**/datasets--lmms-lab--DocVQA/**/*.parquet"],
        "ChartQA":  ["**/datasets--lmms-lab--ChartQA/**/*.parquet"],
        "InfoVQA":  ["**/datasets--lmms-lab--infographicsVQA*/**/*.parquet",
                     "**/datasets--lmms-lab--InfoVQA/**/*.parquet"],
    }
    for name, pats in targets.items():
        files = []
        for pat in pats:
            files.extend(glob.glob(os.path.join(eval_root, pat), recursive=True))
        files = sorted(set(files))
        n = 0
        for f in files:
            for txt in _iter_text_cols(f):
                hset.add(norm_hash(txt)); n += 1
        if files:
            found[name] = {"n_files": len(files), "n_text_rows": n}
    return found, hset


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir",
                    default="/nas_train/app.e0031982/datasets/baize-vision/ocr_synth_10m_full")
    ap.add_argument("--eval-root", default="/nas_env/app.e0031982/hf_home/hub")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    dd = args.data_dir
    idx_path = os.path.join(dd, "index.jsonl")
    if not os.path.exists(idx_path):
        print(f"[FAIL] no index.jsonl under {dd}"); sys.exit(2)
    out_path = args.out or os.path.join(dd, "VALIDATION.json")

    t0 = time.time()
    print(f"[postproc] scanning {idx_path} ...", flush=True)

    sha_counts = {}; cat_counts = {}; lang_counts = {}; ntok = []; n_total = 0
    with open(idx_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            n_total += 1
            tsha = rec.get("text_sha1", "")
            sha_counts[tsha] = sha_counts.get(tsha, 0) + 1
            c = rec.get("cat", "?"); cat_counts[c] = cat_counts.get(c, 0) + 1
            lg = rec.get("lang", "?"); lang_counts[lg] = lang_counts.get(lg, 0) + 1
            nt = rec.get("n_tokens")
            if isinstance(nt, (int, float)):
                ntok.append(nt)
    print(f"[postproc] index records = {n_total}  ({time.time()-t0:.1f}s)", flush=True)

    n_dup_hashes = sum(1 for v in sha_counts.values() if v > 1)
    n_dup_extra = sum(v - 1 for v in sha_counts.values() if v > 1)
    dup_rate = n_dup_extra / max(n_total, 1)

    tld = {}
    if ntok:
        arr = np.asarray(ntok)
        tld = {"p50": int(np.percentile(arr, 50)), "p95": int(np.percentile(arr, 95)),
               "max": int(arr.max()), "mean": round(float(arr.mean()), 2),
               "count": int(arr.size)}

    tars = sorted(glob.glob(os.path.join(dd, "shard-*.tar")))
    n_tars = len(tars)
    total_bytes = 0
    for t in tars:
        try:
            total_bytes += os.path.getsize(t)
        except OSError:
            pass
    avg_bytes = int(total_bytes / max(n_total, 1))

    t1 = time.time()
    eval_found, eval_hashes = build_eval_hash_set(args.eval_root)
    print(f"[postproc] eval hash set size = {len(eval_hashes)}  ({time.time()-t1:.1f}s)", flush=True)
    gen_sha_set = set(sha_counts.keys())
    leak_hits = gen_sha_set & eval_hashes if eval_hashes else set()
    n_leak = len(leak_hits)
    leak_rate = n_leak / max(len(gen_sha_set), 1)

    stats_in = {}
    sp = os.path.join(dd, "STATS.json")
    if os.path.exists(sp):
        try:
            with open(sp, encoding="utf-8") as f:
                stats_in = json.load(f)
        except Exception:
            pass

    result = {
        "data_dir": dd, "n_index_records": n_total,
        "n_unique_text_sha1": len(sha_counts),
        "n_dup_text_hashes": n_dup_hashes, "n_dup_extra_samples": n_dup_extra,
        "dup_rate": round(dup_rate, 6), "dup_target": 0.01, "dup_pass": dup_rate < 0.01,
        "cat_counts": cat_counts, "lang_counts": lang_counts,
        "n_tokens_dist": tld, "n_tars": n_tars, "total_bytes": total_bytes,
        "total_tb": round(total_bytes / 1e12, 4), "avg_bytes_per_sample": avg_bytes,
        "leakage": {
            "eval_root": args.eval_root, "eval_sets_found": eval_found,
            "eval_hash_set_size": len(eval_hashes), "n_leak_hits": n_leak,
            "leak_rate": round(leak_rate, 8), "leak_pass": n_leak == 0,
            "note": ("gen inline guard searched ~/.cache/huggingface (wrong path) -> no-op; "
                     "this check reads the REAL eval parquet under /nas_env/.../hub."),
        },
        "gen_stats_present": bool(stats_in), "gen_fail_rate": stats_in.get("fail_rate"),
        "gen_fail": stats_in.get("fail"), "gen_ok": stats_in.get("ok"),
        "elapsed_s": round(time.time() - t0, 1),
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print(f"[postproc] VALIDATION -> {out_path}")
    print(f"  index records      : {n_total}")
    print(f"  unique text_sha1   : {len(sha_counts)}")
    print(f"  dup text hashes    : {n_dup_hashes}  (extra {n_dup_extra})")
    print(f"  dup_rate           : {dup_rate:.6f}  PASS={dup_rate<0.01}")
    print(f"  cat_counts         : {cat_counts}")
    print(f"  n_tokens dist      : {tld}")
    print(f"  tars               : {n_tars}  bytes={total_bytes} ({result['total_tb']} TB)")
    print(f"  eval sets found    : {eval_found}")
    print(f"  eval hash set size : {len(eval_hashes)}")
    print(f"  leak hits          : {n_leak}  PASS={n_leak==0}")
    print(f"  gen STATS present  : {bool(stats_in)} (fail={stats_in.get('fail')}, ok={stats_in.get('ok')})")
    print(f"  elapsed            : {result['elapsed_s']}s")
    print("=" * 60)
    overall = result["dup_pass"] and result["leakage"]["leak_pass"]
    print(f"[postproc] OVERALL PASS = {overall}")
    if not overall:
        sys.exit(1)


if __name__ == "__main__":
    main()
