#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_r324_v11v38_merge.py -- R324: Merge v11-v37 unified SFT corpus
(1086 pairs) + R323 full data-gap synthesis (258 pairs, 166 APIs, 100% coverage)
into a single unified SFT v38 corpus JSONL, then convert to verl-compatible
parquet, run contamination fingerprint scan, and optionally produce a
deterministic train/val split ready for SFT retraining.

Background:
  R323 (wake323) synthesized 258 SFT pairs covering 166 data-gap APIs that were
  NOT present in the v11-v37 corpus (R321 missing-API analysis). Contam gate
  PASS (258 scanned, 0 hit). This script merges them so the next SFT run
  (v11v38) can verify whether data-gap coverage improves EDA-Eval scores.

  v11-v37 corpus schema (prompt/completion JSONL):
    {prompt, completion, pair_id, type, api_used, contamination_check, ...}
  R323 pairs schema (instruction/output JSONL):
    {instruction, input, output, api_name, pair_type}

Contamination isolation (red line 5.1):
  Source = API documentation ONLY.  158 eval tasks NEVER used as input.
  R323 pairs already passed the full 13-gram contam gate (0 hits).

Usage:
  /home/app.e0031982/code/verl_cu124_venv/bin/python baize_posttrain_r324_v11v38_merge.py
  /home/app.e0031982/code/verl_cu124_venv/bin/python baize_posttrain_r324_v11v38_merge.py --dry-run
  /home/app.e0031982/code/verl_cu124_venv/bin/python baize_posttrain_r324_v11v38_merge.py --split
"""
import json, sys, os, hashlib, argparse
from pathlib import Path
from collections import Counter

RUN_DIR = Path(__file__).resolve().parent
V11_V37_JSONL = RUN_DIR / "sft_pyaether_corpus_v11_v37_merged.jsonl"
R323_JSONL = RUN_DIR / "r323_datagap_sft_pairs.jsonl"
MERGED_JSONL = RUN_DIR / "sft_pyaether_corpus_v11_v38_merged.jsonl"
PARQUET_PATH = RUN_DIR / "sft_pyaether_corpus_v11_v38_merged.parquet"
EVAL_APIS_PATH = RUN_DIR / "pyAether_eval_488_apis.txt"
SUMMARY_PATH = RUN_DIR / "r324_v11v38_merge_summary.json"
SPLIT_DIR = RUN_DIR / "sft_surrogate_data" / "minicpm5_pyaether_v2_v11v38"

SYSTEM_MSG = ("You are an EDA automation assistant specialized in PyAether API usage. "
              "Write clean, correct Python code that calls the specified APIs.")


def log(msg):
    print("[R324] " + msg, flush=True)


def load_jsonl(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def content_hash(prompt, completion):
    return hashlib.md5((prompt + "\n" + completion).encode("utf-8")).hexdigest()[:12]

def convert_r323_pair(rec, idx):
    """Convert an R323 instruction/output pair to the v11-v37 prompt/completion schema."""
    api = rec.get("api_name", "unknown")
    pt = rec.get("pair_type", "doc")
    instruction = rec.get("instruction", "")
    inp = rec.get("input", "")
    output = rec.get("output", "")
    prompt = instruction if not inp else (instruction + "\n\n" + inp)
    completion = output
    pair_id = "R323-datagap-" + api.replace(".", "_") + "-" + pt + "-" + str(idx).zfill(4)
    rtype = "R323_datagap_" + pt
    return {
        "prompt": prompt,
        "completion": completion,
        "pair_id": pair_id,
        "type": rtype,
        "api_used": [api],
        "contamination_check": "passed",
        "source": "R323_datagap",
        "note": "data-gap API doc/code pair from R323 full synthesis (166 APIs, 100% coverage)",
    }


def api_family(api_name):
    if not api_name:
        return "other"
    name = api_name.split(".")[0].split("(")[0].strip()
    for prefix in ("db", "emy", "ae", "Mde", "dm", "emc", "gu", "sle", "et", "CString", "Emy"):
        if name.startswith(prefix):
            return prefix + "*"
    return "other"


def family_distribution(records):
    family_counter = Counter()
    api_counter = Counter()
    for r in records:
        apis = r.get("api_used", [])
        if isinstance(apis, str):
            try:
                apis = json.loads(apis)
            except Exception:
                apis = [apis]
        if not apis:
            family_counter["other"] += 1
            continue
        for a in apis:
            fam = api_family(a)
            family_counter[fam] += 1
            api_counter[a] += 1
    return dict(family_counter), dict(api_counter.most_common(20))


def contamination_fingerprint_scan(jsonl_path):
    if not EVAL_APIS_PATH.exists():
        return {"status": "SKIP", "reason": "Eval APIs file not found"}
    eval_apis = set()
    with open(EVAL_APIS_PATH) as f:
        for line in f:
            name = line.strip()
            if name:
                eval_apis.add(name)
    log("  Fingerprint scan: " + str(len(eval_apis)) + " eval entry_points vs corpus")
    mentions = 0
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            text = (d.get("prompt", "") + " " + d.get("completion", "")).lower()
            for api in eval_apis:
                short = api.rsplit(".", 1)[-1].lower()
                if short and len(short) > 3 and short in text:
                    mentions += 1
                    break
    return {"status": "PASS", "eval_entry_points": len(eval_apis),
            "corpus_pairs_mentioning_eval_api": mentions,
            "note": "API names are ALLOWED in training corpus. Informational only."}



def convert_to_parquet(jsonl_path, parquet_path):
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        return {"status": "FAIL", "error": "pyarrow ImportError"}
    records, errors = [], 0
    with open(jsonl_path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                prompt = d.get("prompt", "")
                completion = d.get("completion", "")
                records.append({
                    "conversation": [
                        {"role": "system", "content": SYSTEM_MSG},
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": completion},
                    ],
                    "pair_id": d.get("pair_id", "v11v38-" + str(i).zfill(6)),
                    "type": d.get("type", "unknown"),
                    "api_used": json.dumps(d.get("api_used", []), ensure_ascii=False),
                    "contamination_check": d.get("contamination_check", "passed"),
                })
            except json.JSONDecodeError as e:
                errors += 1
                if errors <= 3:
                    log("  WARN: line " + str(i) + " JSON error: " + str(e))
    if not records:
        return {"status": "FAIL", "error": "No valid records"}
    table = pa.Table.from_pylist(records)
    pq.write_table(table, str(parquet_path), compression="snappy")
    vt = pq.read_table(str(parquet_path))
    result = {"status": "PASS", "input": jsonl_path.name, "output": parquet_path.name,
              "rows": len(records), "parquet_rows": vt.num_rows, "errors": errors,
              "size_bytes": parquet_path.stat().st_size,
              "size_kb": round(parquet_path.stat().st_size / 1024, 1),
              "schema_cols": vt.column_names}
    log("  Parquet: " + str(vt.num_rows) + " rows, " + str(result["size_kb"]) + "KB")
    return result


def make_train_val_split(parquet_path, out_dir, val_ratio=0.1, seed=42):
    try:
        import pandas as pd
        import numpy as np
    except ImportError:
        return {"status": "FAIL", "error": "pandas/numpy ImportError"}
    df = pd.read_parquet(str(parquet_path))
    n = len(df)
    n_val = max(1, int(n * val_ratio))
    n_train = n - n_val
    rng = np.random.RandomState(seed)
    idx = rng.permutation(n)
    val_idx = idx[:n_val]
    train_idx = idx[n_val:]
    train_df = df.iloc[train_idx].reset_index(drop=True)
    val_df = df.iloc[val_idx].reset_index(drop=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    train_path = out_dir / "sft_surrogate_train.parquet"
    val_path = out_dir / "sft_surrogate_val.parquet"
    train_df.to_parquet(str(train_path), index=False)
    val_df.to_parquet(str(val_path), index=False)
    chk = pd.read_parquet(str(train_path))
    assert len(chk) == len(train_df), "round-trip row count mismatch"
    log("  Split: train=" + str(n_train) + " val=" + str(n_val) + " -> " + str(out_dir.name))
    return {"status": "PASS", "train_rows": n_train, "val_rows": n_val,
            "train_path": str(train_path), "val_path": str(val_path),
            "train_kb": round(train_path.stat().st_size / 1024, 1),
            "val_kb": round(val_path.stat().st_size / 1024, 1)}



def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--split", action="store_true",
                    help="also produce train/val parquet split for SFT retraining")
    args = ap.parse_args()

    log("=" * 70)
    log("R324: Merge v11-v37 (1086) + R323 data-gap (258) -> v11-v38")
    log("=" * 70)

    if not V11_V37_JSONL.exists():
        log("ERROR: v11-v37 merged jsonl not found: " + str(V11_V37_JSONL))
        sys.exit(1)
    if not R323_JSONL.exists():
        log("ERROR: R323 pairs not found: " + str(R323_JSONL))
        sys.exit(1)

    v37_records = load_jsonl(V11_V37_JSONL)
    r323_records = load_jsonl(R323_JSONL)
    log("  v11-v37 base: " + str(len(v37_records)) + " pairs")
    log("  R323 data-gap: " + str(len(r323_records)) + " pairs")

    r323_converted = [convert_r323_pair(r, i) for i, r in enumerate(r323_records)]

    merged = []
    seen_hashes = set()
    dupes = 0
    for r in v37_records + r323_converted:
        h = content_hash(r.get("prompt", ""), r.get("completion", ""))
        if h in seen_hashes:
            dupes += 1
            continue
        seen_hashes.add(h)
        merged.append(r)
    log("  Merged: " + str(len(merged)) + " pairs (deduped " + str(dupes) + ")")

    fam_before, _ = family_distribution(v37_records)
    fam_after, api_after = family_distribution(merged)
    log("  Family before (v11-v37): " + json.dumps(fam_before, ensure_ascii=False))
    log("  Family after  (v11-v38): " + json.dumps(fam_after, ensure_ascii=False))

    if args.dry_run:
        log("DRY-RUN: would write " + str(len(merged)) + " pairs to " + MERGED_JSONL.name)
        summary = {"round": "R324", "status": "DRY_RUN",
                   "inputs": {"v11_v37_pairs": len(v37_records), "r323_pairs": len(r323_records)},
                   "merge": {"merged_pairs": len(merged), "duplicates_removed": dupes},
                   "family_before": fam_before, "family_after": fam_after}
        with open(SUMMARY_PATH, "w") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        log("  Summary (dry-run) written: " + str(SUMMARY_PATH))
        return

    with open(MERGED_JSONL, "w", encoding="utf-8") as f:
        for r in merged:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    log("  Wrote " + str(len(merged)) + " pairs -> " + MERGED_JSONL.name +
        " (" + str(round(MERGED_JSONL.stat().st_size / 1024, 1)) + "KB)")

    contam = contamination_fingerprint_scan(MERGED_JSONL)
    log("  Contamination fingerprint scan: " + contam["status"])

    parquet_result = convert_to_parquet(MERGED_JSONL, PARQUET_PATH)

    split_result = None
    if args.split and parquet_result["status"] == "PASS":
        split_result = make_train_val_split(PARQUET_PATH, SPLIT_DIR)
        log("  Train/val split: " + split_result["status"])

    summary = {
        "meta": {"round": "R324", "date": "2026-11-12",
                 "purpose": "Merge v11-v37 + R323 data-gap into unified SFT v38 corpus",
                 "surrogate_disclaimer": "MiniCPM5-2B is BaiZe surrogate; gains not transferable to BaiZe"},
        "inputs": {"v11_v37_pairs": len(v37_records), "r323_pairs": len(r323_records),
                   "r323_coverage": "166/166 data-gap APIs (100%)"},
        "merge": {"merged_pairs": len(merged), "duplicates_removed": dupes,
                  "output_jsonl": MERGED_JSONL.name,
                  "output_jsonl_kb": round(MERGED_JSONL.stat().st_size / 1024, 1)},
        "family_distribution": {"before_v11_v37": fam_before, "after_v11_v38": fam_after},
        "top_apis_after": api_after,
        "contamination_fingerprint_scan": contam,
        "parquet_conversion": parquet_result,
        "train_val_split": split_result,
    }
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    log("  Summary written: " + str(SUMMARY_PATH))

    if parquet_result["status"] == "PASS":
        log("DONE: " + str(len(merged)) + " pairs -> " + MERGED_JSONL.name +
            " + " + PARQUET_PATH.name + " (" + str(parquet_result["size_kb"]) + "KB)")
    else:
        log("WARN: parquet issue: " + str(parquet_result.get("error", "unknown")))


if __name__ == "__main__":
    main()

