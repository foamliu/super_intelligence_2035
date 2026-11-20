#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_r206_consolidate_v11_v35.py
R206 -- Consolidate v11-v35 PyAether SFT corpus (25 files, 943 pairs) into a
single training-ready merged JSONL + summary.

  1. Reads all 25 corpus files sft_pyaether_corpus_v{11..35}_*.jsonl.
  2. Normalises schema: maps `id` -> `pair_id`, ensures required fields.
  3. Deduplicates by `id` (keeps first occurrence).
  4. Loads 155 eval entry_points from the EDA-Eval dataset.
  5. Fingerprint scan: rejects any pair whose prompt+completion contains a
     literal eval entry_point string (S5.1 red-line, same as R205).
  6. Writes merged JSONL: sft_pyaether_corpus_v11_v35_merged.jsonl
  7. Writes summary JSON: r206_consolidate_summary.json

NOTE: The full 13-gram contamination gate is run SEPARATELY on the merged file
after this script.  This script only does the fast entry_point fingerprint scan.

Usage: python3 baize_posttrain_r206_consolidate_v11_v35.py [--dry-run]
"""
import argparse, json, os, sys, glob, collections

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_DS = "/home/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
OUT_JSONL = os.path.join(RUN_DIR, "sft_pyaether_corpus_v11_v35_merged.jsonl")
OUT_SUMMARY = os.path.join(RUN_DIR, "r206_consolidate_summary.json")
CORPUS_GLOB = "sft_pyaether_corpus_v{}_*.jsonl"
VERSIONS = list(range(11, 36))


def load_eval_entry_points():
    eps = set()
    if not os.path.exists(EVAL_DS):
        sys.stderr.write("WARNING: eval dataset not found at %s\n" % EVAL_DS)
        return eps
    with open(EVAL_DS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            ep = d.get("entry_point", "")
            if ep:
                eps.add(ep)
    return eps


def fingerprint_scan(text, eval_eps):
    for ep in eval_eps:
        if ep and ep in text:
            return ep
    return None


def discover_corpus_files():
    found = []
    for v in VERSIONS:
        pattern = os.path.join(RUN_DIR, CORPUS_GLOB.format(v))
        matches = sorted(glob.glob(pattern))
        if not matches:
            sys.stderr.write("WARNING: no file for v%d\n" % v)
            continue
        for m in matches:
            found.append((v, m))
    return found


def normalise_pair(raw, source_file):
    pair_id = raw.get("pair_id") or raw.get("id") or ""
    au = raw.get("api_used", [])
    if not isinstance(au, list):
        au = [au] if au else []
    return {
        "pair_id": pair_id,
        "id": raw.get("id", pair_id),
        "type": raw.get("type", ""),
        "api_used": au,
        "prompt": raw.get("prompt", ""),
        "completion": raw.get("completion", ""),
        "contamination_check": raw.get("contamination_check", ""),
        "note": raw.get("note", ""),
        "source": raw.get("source", source_file),
    }


def main():
    parser = argparse.ArgumentParser(description="R206 consolidate v11-v35 corpus")
    parser.add_argument("--dry-run", action="store_true", help="scan only, do not write")
    args = parser.parse_args()
    print("=" * 64)
    print("R206 -- Consolidate v11-v35 PyAether SFT corpus (25 files -> 1)")
    print("=" * 64)
    eval_eps = load_eval_entry_points()
    print("\n  Eval entry_points loaded: %d" % len(eval_eps))
    files = discover_corpus_files()
    print("  Corpus files discovered: %d (expected 25)" % len(files))
    if len(files) != 25:
        sys.stderr.write("  WARNING: expected 25 files, found %d\n" % len(files))
    all_pairs = []
    seen_ids = set()
    per_file_counts = []
    rejected_fp = 0
    reject_details = []
    dup_count = 0
    parse_errors = 0
    for ver, fpath in files:
        fname = os.path.basename(fpath)
        n_read = 0; n_added = 0; n_dup = 0; n_rej = 0
        with open(fpath, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                n_read += 1
                try:
                    raw = json.loads(line)
                except json.JSONDecodeError:
                    parse_errors += 1
                    continue
                pair = normalise_pair(raw, fname)
                pid = pair["pair_id"]
                if pid in seen_ids:
                    n_dup += 1; dup_count += 1
                    continue
                blob = pair["prompt"] + "\n" + pair["completion"]
                hit = fingerprint_scan(blob, eval_eps)
                if hit:
                    n_rej += 1; rejected_fp += 1
                    reject_details.append((pid, hit, fname))
                    continue
                seen_ids.add(pid)
                all_pairs.append(pair)
                n_added += 1
        per_file_counts.append({"version": ver, "file": fname, "read": n_read,
                                "added": n_added, "dup": n_dup, "rejected_fp": n_rej})
        print("  v%-2d %-52s read=%-4d added=%-4d dup=%-3d rej=%-3d" %
              (ver, fname[:52], n_read, n_added, n_dup, n_rej))
    total_added = len(all_pairs)
    print("\n  TOTAL: %d pairs (dedup removed %d, fp rejected %d, parse errors %d)" %
          (total_added, dup_count, rejected_fp, parse_errors))
    type_counts = collections.Counter(p["type"] for p in all_pairs)
    api_counts = collections.Counter()
    for p in all_pairs:
        for a in p["api_used"]:
            if a:
                api_counts[a] += 1
    contam_counts = collections.Counter(p["contamination_check"] for p in all_pairs)
    print("\n  Per-type distribution:")
    for t, c in sorted(type_counts.items()):
        print("    %-28s %4d" % (t, c))
    print("\n  Unique APIs covered: %d" % len(api_counts))
    print("  Contamination_check values: %s" % dict(contam_counts))
    if rejected_fp > 0:
        print("\n  FINGERPRINT SCAN: FAIL (%d rejected)" % rejected_fp)
        for pid, hit, fn in reject_details[:10]:
            print("    REJECT %s -> entry_point '%s' (in %s)" % (pid, hit, fn))
    else:
        print("\n  FINGERPRINT SCAN: PASS (0 contamination)")
    if args.dry_run:
        print("\n  [DRY-RUN] not writing merged file or summary.")
        return 0
    with open(OUT_JSONL, "w", encoding="utf-8") as fh:
        for p in all_pairs:
            fh.write(json.dumps(p, ensure_ascii=False) + "\n")
    out_size = os.path.getsize(OUT_JSONL)
    print("\n  Written: %s" % OUT_JSONL)
    print("    %d pairs, %d bytes (%.1f KB)" % (total_added, out_size, out_size / 1024.0))
    summary = {
        "round": "R206", "eval_entry_points_count": len(eval_eps),
        "corpus_files_count": len(files), "total_pairs": total_added,
        "dedup_removed": dup_count, "fingerprint_rejected": rejected_fp,
        "parse_errors": parse_errors,
        "fingerprint_scan": "PASS" if rejected_fp == 0 else "FAIL",
        "per_file": per_file_counts, "type_distribution": dict(type_counts),
        "unique_apis_covered": len(api_counts),
        "api_frequency": dict(api_counts.most_common()),
        "contamination_check_values": dict(contam_counts),
        "output_jsonl": OUT_JSONL, "output_jsonl_bytes": out_size,
        "output_summary": OUT_SUMMARY,
        "reject_details": [{"pair_id": p, "hit_entry_point": h, "source_file": f}
                           for p, h, f in reject_details],
    }
    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print("  Summary: %s" % OUT_SUMMARY)
    if rejected_fp > 0:
        print("\n  RESULT: FAIL -- %d pairs contain eval entry_point strings." % rejected_fp)
        return 2
    print("\n  RESULT: PASS -- %d pairs ready for SFT (pending 13-gram gate)." % total_added)
    return 0


if __name__ == "__main__":
    sys.exit(main())
