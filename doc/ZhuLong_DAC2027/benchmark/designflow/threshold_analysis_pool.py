#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""threshold_analysis_pool.py -- compute mc threshold table from a 3-col
shard-A pool (sid, mc, strong) + the 4-shard trace ledgers.

For each mc threshold (>=30/25/20/15/10/5) over the shard A pool:
  - sessions              : unique sids with mc>=T
  - unique_users          : (n/a from 3-col pool; reported as '-'; use host pool
                            if needed) -- here we report session/user counts
                            from the 5-col pool if available
  - un_ledgered           : sids not in any shard ledger
  - digital_strong        : sids with strong=1
  - digital_strong_unledgered : strong AND un-ledgered (actionable new pool)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
THRESHOLDS = [30, 25, 20, 15, 10, 5]


def load_ledger_excl():
    excl = set()
    per_shard = {}
    for shard in ("A", "B", "C", "D"):
        p = os.path.join(HERE, "trace_ledger_%s.tsv" % shard)
        n = 0
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.rstrip("\n")
                    if not line or line.startswith("session_file"):
                        continue
                    parts = line.split("\t")
                    if parts:
                        excl.add(parts[0].strip())
                        n += 1
        per_shard[shard] = n
    return excl, per_shard


def load_pool(path):
    """3-col: sid, mc, strong. Returns list of dicts."""
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            sid, mc_s, strong_s = parts[0], parts[1], parts[2]
            try:
                mc = int(mc_s)
            except ValueError:
                continue
            rows.append({"sid": sid, "mc": mc, "strong": strong_s == "1"})
    return rows


def main():
    pool_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        HERE, "shardA_pool_rescan.tsv")
    excl, per_shard = load_ledger_excl()
    rows = load_pool(pool_path)

    table = {}
    for T in THRESHOLDS:
        sub = [r for r in rows if r["mc"] >= T]
        sids = set(r["sid"] for r in sub)
        unledgered = [r for r in sub if r["sid"] not in excl]
        strong = [r for r in sub if r["strong"]]
        strong_unl = [r for r in sub if r["strong"] and r["sid"] not in excl]
        table[T] = {
            "sessions": len(sids),
            "un_ledgered": len(unledgered),
            "digital_strong": len(strong),
            "digital_strong_unledgered": len(strong_unl),
        }

    out = {
        "pool_file": os.path.basename(pool_path),
        "pool_total_sessions": len(rows),
        "ledger_excl_total": len(excl),
        "ledger_per_shard": per_shard,
        "threshold_table": table,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

    # also print a readable table
    print("\n=== mc threshold table (shard A, full rescan 11/09) ===")
    print("%-7s %10s %12s %14s %22s" % (
        "mc>=", "sessions", "un_ledgered", "digital_strong",
        "strong_unledgered"))
    for T in THRESHOLDS:
        t = table[T]
        print("%-7d %10d %12d %14d %22d" % (
            T, t["sessions"], t["un_ledgered"],
            t["digital_strong"], t["digital_strong_unledgered"]))


if __name__ == "__main__":
    main()
