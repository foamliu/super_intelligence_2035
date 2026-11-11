#!/usr/bin/env python3
"""baize_posttrain_r210_v11v36_parquet.py -- R210: Convert v11-v36 merged SFT
corpus (1029 pairs) from JSONL to verl-compatible parquet + validate + contamination
fingerprint scan.

Schema (identical to R102 v5 parquet, validated by read-back):
  conversation      : list<struct<role: string, content: string>>
  pair_id           : string
  type              : string
  api_used          : string   (json.dumps of the original list)
  contamination_check: string

Usage:
  /home/app.e0031982/code/verl_cu124_venv/bin/python baize_posttrain_r210_v11v36_parquet.py
  /home/app.e0031982/code/verl_cu124_venv/bin/python baize_posttrain_r210_v11v36_parquet.py --dry-run
"""
import json, sys, os
from pathlib import Path
from collections import Counter

RUN_DIR = Path(__file__).resolve().parent
JSONL_PATH = RUN_DIR / "sft_pyaether_corpus_v11_v36_merged.jsonl"
PARQUET_PATH = RUN_DIR / "sft_pyaether_corpus_v11_v36_merged.parquet"
EVAL_APIS_PATH = RUN_DIR / "pyAether_eval_488_apis.txt"
SUMMARY_PATH = RUN_DIR / "r210_v11v36_parquet_summary.json"
SYSTEM_MSG = ("You are an EDA automation assistant specialized in PyAether API usage. "
              "Write clean, correct Python code that calls the specified APIs.")

def log(msg):
    print("[R210] " + msg, flush=True)

def convert_jsonl_to_parquet(dry_run=False):
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        log("ERROR: pyarrow not available. Use verl venv python.")
        return {"status": "FAIL", "error": "pyarrow ImportError"}
    if not JSONL_PATH.exists():
        return {"status": "FAIL", "error": "JSONL not found: " + str(JSONL_PATH)}
    log("Converting: " + JSONL_PATH.name + " -> " + PARQUET_PATH.name)
    records, errors = [], 0
    type_counter = Counter()
    contam_counter = Counter()
    empty_prompt = 0
    empty_completion = 0
    with open(JSONL_PATH) as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                prompt = d.get("prompt", "")
                completion = d.get("completion", "")
                if not prompt.strip():
                    empty_prompt += 1
                if not completion.strip():
                    empty_completion += 1
                records.append({
                    "conversation": [
                        {"role": "system", "content": SYSTEM_MSG},
                        {"role": "user", "content": prompt},
                        {"role": "assistant", "content": completion},
                    ],
                    "pair_id": d.get("pair_id", d.get("id", "v11v36-" + str(i).zfill(6))),
                    "type": d.get("type", "unknown"),
                    "api_used": json.dumps(d.get("api_used", []), ensure_ascii=False),
                    "contamination_check": d.get("contamination_check", "passed"),
                })
                type_counter[d.get("type", "unknown")] += 1
                contam_counter[d.get("contamination_check", "missing")] += 1
            except json.JSONDecodeError as e:
                errors += 1
                if errors <= 3:
                    log("  WARN: line " + str(i) + " JSON error: " + str(e))
    if not records:
        return {"status": "FAIL", "error": "No valid records"}
    if dry_run:
        log("DRY-RUN: would write " + str(len(records)) + " records")
        return {"status": "DRY_RUN", "input": JSONL_PATH.name, "output": PARQUET_PATH.name,
                "rows": len(records), "errors": errors,
                "type_distribution": dict(type_counter.most_common()),
                "contamination_check_values": dict(contam_counter),
                "empty_prompt": empty_prompt, "empty_completion": empty_completion}
    table = pa.Table.from_pylist(records)
    pq.write_table(table, str(PARQUET_PATH), compression="snappy")
    log("  Wrote " + str(len(records)) + " records -> " + PARQUET_PATH.name)
    vt = pq.read_table(str(PARQUET_PATH))
    result = {"status": "PASS", "input": JSONL_PATH.name, "output": PARQUET_PATH.name,
              "rows": len(records), "parquet_rows": vt.num_rows, "errors": errors,
              "size_bytes": PARQUET_PATH.stat().st_size,
              "size_mb": round(PARQUET_PATH.stat().st_size / 1048576, 2),
              "schema_cols": vt.column_names,
              "types": sorted(set(r["type"] for r in records)),
              "type_distribution": dict(type_counter.most_common()),
              "contamination_check_values": dict(contam_counter),
              "empty_prompt": empty_prompt, "empty_completion": empty_completion}
    log("  OK: " + str(vt.num_rows) + " rows, " + str(result["size_mb"]) + "MB")
    first_conv = vt.column("conversation")[0].as_py()
    result["first_row_conv_roles"] = [m["role"] for m in first_conv]
    result["first_row_conv_lengths"] = [len(m["content"]) for m in first_conv]
    v5_path = RUN_DIR / "sft_pyaether_corpus_v5_deep_enriched.parquet"
    if v5_path.exists():
        v5t = pq.read_table(str(v5_path))
        result["v5_schema_cols"] = v5t.column_names
        result["schema_match_v5"] = (vt.column_names == v5t.column_names)
        log("  Schema match vs v5: " + str(result["schema_match_v5"]))
    return result

def contamination_fingerprint_scan():
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
    with open(JSONL_PATH) as f:
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

def main():
    dry_run = "--dry-run" in sys.argv
    log("R210 v11-v36 parquet conversion (dry_run=" + str(dry_run) + ")")
    conv = convert_jsonl_to_parquet(dry_run=dry_run)
    contam = contamination_fingerprint_scan() if not dry_run else {"status": "SKIP"}
    summary = {"round": "R210", "wake": "wake279", "date": "2026-11-11",
               "conversion": conv, "contamination_fingerprint_scan": contam}
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    log("  Summary written: " + str(SUMMARY_PATH))
    if conv["status"] == "PASS":
        log("DONE: " + str(conv["parquet_rows"]) + " rows -> " + PARQUET_PATH.name +
            " (" + str(conv["size_mb"]) + "MB), schema_match_v5=" + str(conv.get("schema_match_v5")))
    elif conv["status"] == "DRY_RUN":
        log("DRY-RUN DONE: " + str(conv["rows"]) + " records")
    else:
        log("FAIL: " + str(conv.get("error", "unknown")))
        sys.exit(1)

if __name__ == "__main__":
    main()
