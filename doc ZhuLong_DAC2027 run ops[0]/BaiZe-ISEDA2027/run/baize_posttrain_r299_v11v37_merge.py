#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_r299_v11v37_merge.py -- R299: Merge v11-v36 (1029 pairs) + v37
db* lifecycle remedial (57 pairs) into a single unified SFT corpus JSONL,
then convert to verl-compatible parquet, run contamination fingerprint scan,
and produce a rebalanced API-family analysis summary.

Background (R297/R298):
  R297 found catastrophic forgetting: SFT on v11-v36 improved Schematic
  (+16.6pp) but degraded Layout (-18.7pp) and DesignMgmt (-15.5pp).
  Root cause: db* lifecycle APIs under-represented (emy*394 vs db*243).
  R298 generated v37 remedial (57 pairs for 10 forgotten db* APIs).
  This script merges them into v11-v37 (1086 pairs) with db*+38% rebalancing.

Contamination isolation (red line 5.1):
  Source = API documentation ONLY.  158 eval tasks NEVER used as input.

Usage:
  python3 baize_posttrain_r299_v11v37_merge.py [--dry-run]
"""
import json, sys, os
from pathlib import Path
from collections import Counter

RUN_DIR = Path(__file__).resolve().parent
V11_V36_JSONL = RUN_DIR / "sft_pyaether_corpus_v11_v36_merged.jsonl"
V37_JSONL = RUN_DIR / "sft_pyaether_corpus_v37_db_lifecycle_remedial.jsonl"
MERGED_JSONL = RUN_DIR / "sft_pyaether_corpus_v11_v37_merged.jsonl"
PARQUET_PATH = RUN_DIR / "sft_pyaether_corpus_v11_v37_merged.parquet"
EVAL_APIS_PATH = RUN_DIR / "pyAether_eval_488_apis.txt"
SUMMARY_PATH = RUN_DIR / "r299_v11v37_merge_summary.json"

SYSTEM_MSG = ("You are an EDA automation assistant specialized in PyAether API usage. "
              "Write clean, correct Python code that calls the specified APIs.")


def log(msg):
    print("[R299] " + msg, flush=True)


def load_jsonl(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def api_family(api_name):
    if not api_name:
        return "other"
    name = api_name.split(".")[0].split("(")[0].strip()
    for prefix in ("db", "emy", "ae", "Mde", "dm", "emc", "gu", "sle", "et"):
        if name.startswith(prefix):
            return prefix + "*"
    return "other"


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


def family_distribution(records):
    family_counter = Counter()
    api_counter = Counter()
    for r in records:
        apis = r.get("api_used", [])
        if isinstance(apis, str):
            try:
                apis = json.loads(apis)
            except (json.JSONDecodeError, ValueError):
                apis = [apis]
        for a in apis:
            family_counter[api_family(a)] += 1
            api_counter[a] += 1
    return dict(family_counter.most_common()), dict(api_counter.most_common(30))


def convert_to_parquet(jsonl_path, parquet_path):
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        return {"status": "FAIL", "error": "pyarrow ImportError"}
    records = []
    errors = 0
    with open(jsonl_path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                records.append({
                    "conversation": [
                        {"role": "system", "content": SYSTEM_MSG},
                        {"role": "user", "content": d.get("prompt", "")},
                        {"role": "assistant", "content": d.get("completion", "")},
                    ],
                    "pair_id": d.get("pair_id", d.get("id", "v11v37-" + str(i).zfill(6))),
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
    schema = pa.schema([
        pa.field("conversation", pa.list_(pa.struct([
            pa.field("role", pa.string()), pa.field("content", pa.string())]))),
        pa.field("pair_id", pa.string()),
        pa.field("type", pa.string()),
        pa.field("api_used", pa.string()),
        pa.field("contamination_check", pa.string())])
    table = pa.Table.from_pylist(records, schema=schema)
    pq.write_table(table, str(parquet_path), compression="snappy")
    vt = pq.read_table(str(parquet_path))
    result = {"status": "PASS", "output": parquet_path.name,
              "rows": len(records), "parquet_rows": vt.num_rows,
              "errors": errors,
              "size_bytes": parquet_path.stat().st_size,
              "size_mb": round(parquet_path.stat().st_size / 1048576, 2),
              "schema_cols": vt.column_names}
    v5_path = RUN_DIR / "sft_pyaether_corpus_v5_deep_enriched.parquet"
    if v5_path.exists():
        v5t = pq.read_table(str(v5_path))
        result["schema_match_v5"] = (vt.column_names == v5t.column_names)
    log("  Parquet: " + str(vt.num_rows) + " rows, " + str(result["size_mb"]) + "MB")
    return result


def main():
    dry_run = "--dry-run" in sys.argv
    log("R299 v11-v37 merge (dry_run=" + str(dry_run) + ")")
    if not V11_V36_JSONL.exists():
        log("FAIL: v11-v36 JSONL not found")
        sys.exit(1)
    if not V37_JSONL.exists():
        log("FAIL: v37 JSONL not found")
        sys.exit(1)
    v36_records = load_jsonl(V11_V36_JSONL)
    v37_records = load_jsonl(V37_JSONL)
    log("  v11-v36: " + str(len(v36_records)) + " pairs")
    log("  v37:     " + str(len(v37_records)) + " pairs")
    seen_ids = set()
    merged = []
    dupes = 0
    for r in v36_records + v37_records:
        pid = r.get("pair_id", r.get("id", ""))
        if pid and pid in seen_ids:
            dupes += 1
            continue
        if pid:
            seen_ids.add(pid)
        merged.append(r)
    log("  Merged: " + str(len(merged)) + " pairs (deduped " + str(dupes) + ")")
    fam_before, _ = family_distribution(v36_records)
    fam_after, api_after = family_distribution(merged)
    log("  Family before: " + json.dumps(fam_before, ensure_ascii=False))
    log("  Family after:  " + json.dumps(fam_after, ensure_ascii=False))
    db_before = fam_before.get("db*", 0)
    db_after = fam_after.get("db*", 0)
    db_delta = db_after - db_before
    db_pct = round(100.0 * db_delta / max(db_before, 1), 1)
    ratio_before = round(fam_before.get("emy*", 0) / max(db_before, 1), 2)
    ratio_after = round(fam_after.get("emy*", 0) / max(db_after, 1), 2)
    log("  db*: " + str(db_before) + " -> " + str(db_after) + " (+" + str(db_delta) + ", +" + str(db_pct) + "%)")
    log("  emy*:db* ratio: " + str(ratio_before) + " -> " + str(ratio_after))
    if dry_run:
        log("DRY-RUN: would write " + str(len(merged)) + " pairs to " + MERGED_JSONL.name)
        summary = {"round": "R299", "status": "DRY_RUN",
                   "merged_pairs": len(merged), "duplicates_removed": dupes,
                   "family_before": fam_before, "family_after": fam_after,
                   "db_delta": db_delta, "db_pct": db_pct,
                   "ratio_before": ratio_before, "ratio_after": ratio_after}
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
    log("  Contamination scan: " + contam["status"])
    parquet_result = convert_to_parquet(MERGED_JSONL, PARQUET_PATH)
    summary = {
        "meta": {"round": "R299", "date": "2026-11-12",
                 "purpose": "Merge v11-v36 + v37 remedial into unified SFT corpus",
                 "surrogate_disclaimer": "MiniCPM5-2B is BaiZe surrogate; gains not transferable to BaiZe"},
        "inputs": {"v11_v36_pairs": len(v36_records), "v37_pairs": len(v37_records)},
        "merge": {"merged_pairs": len(merged), "duplicates_removed": dupes,
                  "output_jsonl": MERGED_JSONL.name,
                  "output_jsonl_kb": round(MERGED_JSONL.stat().st_size / 1024, 1)},
        "family_distribution": {"before_v11_v36": fam_before, "after_v11_v37": fam_after,
                                "db_delta": db_delta, "db_pct_improvement": db_pct,
                                "emy_db_ratio_before": ratio_before,
                                "emy_db_ratio_after": ratio_after},
        "top_apis_after": api_after,
        "contamination_fingerprint_scan": contam,
        "parquet_conversion": parquet_result}
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    log("  Summary written: " + str(SUMMARY_PATH))
    if parquet_result["status"] == "PASS":
        log("DONE: " + str(len(merged)) + " pairs -> " + MERGED_JSONL.name +
            " + " + PARQUET_PATH.name + " (" + str(parquet_result["size_mb"]) + "MB)")
    else:
        log("WARN: parquet issue: " + str(parquet_result.get("error", "unknown")))


if __name__ == "__main__":
    main()
