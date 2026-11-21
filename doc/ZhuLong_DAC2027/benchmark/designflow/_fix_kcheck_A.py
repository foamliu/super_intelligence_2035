#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix k_check/k_rationale metadata hygiene for shard A (21:5x gate).

1. For 254 cases missing both k_check & k_rationale fields: parse k from
   test_rationale header ("N 条断言：①…" or "N 条独立断言（k=N）"), add both
   fields = k. All have k>=8 and proper assertion-list format.
2. Ddr5PatternAnalyze-001: fix test_rationale header "14 条断言" -> "17 条断言"
   (fields already correct at 17; string header was stale).
"""
import json, re, os, sys

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")
BAK   = JSONL + ".bak_kcheck"

RE_K_HEADER = re.compile(r"^\s*(\d+)\s*条")

def parse_k_from_rationale(tr):
    if not tr: return 0
    m = RE_K_HEADER.match(tr)
    return int(m.group(1)) if m else 0

def insert_after(d, anchor_key, new_items):
    """Rebuild dict inserting new_items right after anchor_key."""
    out = {}
    for k, v in d.items():
        out[k] = v
        if k == anchor_key:
            for nk, nv in new_items:
                out[nk] = nv
    # if anchor not found, append at end
    for nk, nv in new_items:
        if nk not in out:
            out[nk] = nv
    return out

def main():
    with open(JSONL, encoding="utf-8") as f:
        lines = f.readlines()
    # backup
    with open(BAK, "w", encoding="utf-8") as f:
        f.writelines(lines)
    n_fixed_missing = 0
    n_fixed_ddr5 = 0
    n_already_ok = 0
    new_lines = []
    for ln in lines:
        if not ln.strip():
            new_lines.append(ln); continue
        d = json.loads(ln)
        m = d.get("metadata", {})
        cid = d.get("id") or d.get("task_id") or "?"
        # Fix 2: Ddr5PatternAnalyze-001 header
        if cid == "EDA-Eval-DesignFlow-Ddr5PatternAnalyze-001":
            tr = m.get("test_rationale", "")
            if tr.startswith("14 条断言"):
                m["test_rationale"] = "17 条断言" + tr[len("14 条断言"):]
                n_fixed_ddr5 += 1
                d["metadata"] = m
        kc = m.get("k_check", None)
        kr = m.get("k_rationale", None)
        # Fix 1: missing both fields
        if kc is None and kr is None:
            k = parse_k_from_rationale(m.get("test_rationale", ""))
            if k >= 8:
                m = insert_after(m, "test_rationale", [("k_check", k), ("k_rationale", k)])
                d["metadata"] = m
                n_fixed_missing += 1
            else:
                print(f"WARNING: {cid} k={k} <8 or unparseable, skipped", file=sys.stderr)
        elif kc is not None and kr is not None:
            n_already_ok += 1
        new_lines.append(json.dumps(d, ensure_ascii=False) + "\n")
    with open(JSONL, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print(f"total lines: {len(lines)}")
    print(f"fixed missing k_check/k_rationale: {n_fixed_missing}")
    print(f"fixed Ddr5PatternAnalyze header: {n_fixed_ddr5}")
    print(f"already had both fields: {n_already_ok}")
    print(f"backup: {BAK}")
    # verify
    with open(JSONL, encoding="utf-8") as f:
        check = [json.loads(l) for l in f if l.strip()]
    print(f"verify: {len(check)} lines, all valid JSON")
    missing = sum(1 for c in check if "k_check" not in c.get("metadata",{}))
    print(f"verify: {missing} cases still missing k_check")

if __name__ == "__main__":
    main()
