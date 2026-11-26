#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""threshold_analysis.py -- mc threshold table for shard A domains.

Reads a summary.tsv (from .75 full rescan) + the 4-shard trace ledgers,
and for each mc threshold (>=30/25/20/15/10/5) computes over shard A's
domain filter:
  - sessions       : unique sids matching shard A relaxed filter, mc>=T
  - unique_users   : unique users among those
  - un_ledgered    : sids not in any shard ledger
  - digital_strong : sids whose tools/keywords hit STRONG digital markers
                     (verdi|vcs|dc_shell|verilint|formality|innovus|
                      primetime|design_compiler|rc|pt_shell) -- the
                     original strict set, NOT the relaxed verilog/rtl/tcl
  - digital_strong_unledgered : strong + un-ledgered (the actionable new pool)

Outputs JSON (threshold_table) + a readable table to stdout.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# shard A relaxed filter (from trace_ledger.py SHARD_DOMAINS, 11/06 relaxed)
SHARD_A_RE = re.compile(
    r"verdi|vcs|dc_shell|verilint|formality|innovus|primetime|"
    r"design_compiler|rc|pt_shell|synthesis|synopsys|tcl|verilog|"
    r"systemverilog|rtl|sdc|vivado|yosys|openroad", re.I)
# strong digital markers (original strict set, pre-relaxation)
STRONG_DIGITAL_RE = re.compile(
    r"verdi|vcs|dc_shell|verilint|formality|innovus|primetime|"
    r"design_compiler|pt_shell", re.I)
# even stricter "real digital tool execution" (exclude innovus which is PNR,
# keep it actually -- innovus is pnr_signoff, belongs shard A). Keep as above.

THRESHOLDS = [30, 25, 20, 15, 10, 5]


def normalize_sid(session_file):
    """strip .messages.json / .json suffix -> sid"""
    s = session_file
    for suf in (".messages.json", ".json"):
        if s.endswith(suf):
            return s[: -len(suf)]
    return s


def load_ledger_excl():
    excl = set()
    for shard in ("A", "B", "C", "D"):
        p = os.path.join(HERE, "trace_ledger_%s.tsv" % shard)
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line or line.startswith("session_file"):
                    continue
                parts = line.split("\t")
                if parts:
                    excl.add(parts[0].strip())
    return excl


def load_summary(path):
    """return list of dicts: sid, user, host, mc, keywords, tools, matches_shardA, strong"""
    rows = []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        header = f.readline()
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 7:
                continue
            ip, host, user, sf, mc_s, kw, tools = parts[:7]
            try:
                mc = int(mc_s)
            except ValueError:
                continue
            sid = normalize_sid(sf)
            blob = kw + " " + tools
            matches_A = bool(SHARD_A_RE.search(blob))
            strong = bool(STRONG_DIGITAL_RE.search(blob))
            rows.append({
                "sid": sid, "user": user, "host": host, "mc": mc,
                "kw": kw, "tools": tools, "matches_A": matches_A,
                "strong": strong,
            })
    return rows


def threshold_table(rows, excl):
    # dedup by sid: a session appears twice (.json + .messages.json).
    # keep max mc per sid, and union of strong/matches_A flags.
    by_sid = {}
    for r in rows:
        sid = r["sid"]
        if sid not in by_sid:
            by_sid[sid] = {
                "sid": sid, "user": r["user"], "host": r["host"],
                "mc": r["mc"], "matches_A": r["matches_A"],
                "strong": r["strong"],
            }
        else:
            e = by_sid[sid]
            e["mc"] = max(e["mc"], r["mc"])
            e["matches_A"] = e["matches_A"] or r["matches_A"]
            e["strong"] = e["strong"] or r["strong"]

    all_sids = list(by_sid.values())
    # shard A pool = matches_A sids
    pool_A = [s for s in all_sids if s["matches_A"]]

    table = {}
    for T in THRESHOLDS:
        sub = [s for s in pool_A if s["mc"] >= T]
        sids = set(s["sid"] for s in sub)
        users = set(s["user"] for s in sub)
        unledgered = [s for s in sub if s["sid"] not in excl]
        strong = [s for s in sub if s["strong"]]
        strong_unl = [s for s in sub if s["strong"] and s["sid"] not in excl]
        table[T] = {
            "sessions": len(sids),
            "unique_users": len(users),
            "un_ledgered": len(unledgered),
            "digital_strong": len(strong),
            "digital_strong_unledgered": len(strong_unl),
        }
    return table, pool_A, all_sids, by_sid


def main():
    if len(sys.argv) < 2:
        print("usage: threshold_analysis.py <summary.tsv> [--peek N]")
        sys.exit(1)
    path = sys.argv[1]
    peek_n = 0
    if "--peek" in sys.argv:
        i = sys.argv.index("--peek")
        peek_n = int(sys.argv[i + 1])

    excl = load_ledger_excl()
    rows = load_summary(path)
    table, pool_A, all_sids, by_sid = threshold_table(rows, excl)

    # overall scan stats
    all_sids_set = set(s["sid"] for s in all_sids)
    all_users = set(s["user"] for s in all_sids)
    all_hosts = set(s["host"] for s in all_sids)
    mc30_all = sum(1 for s in all_sids if s["mc"] >= 30)

    out = {
        "summary_tsv": path,
        "scan_stats": {
            "total_rows": len(rows),
            "dedup_sessions": len(all_sids_set),
            "unique_users": len(all_users),
            "unique_hosts": len(all_hosts),
            "mc30_all": mc30_all,
            "ledger_excl_size": len(excl),
        },
        "threshold_table": table,
    }

    # peek: top-N un-ledgered strong-digital per threshold
    if peek_n > 0:
        peek = {}
        for T in THRESHOLDS:
            sub = [s for s in pool_A
                   if s["mc"] >= T and s["strong"]
                   and s["sid"] not in excl]
            sub.sort(key=lambda s: -s["mc"])
            peek[T] = [{"sid": s["sid"], "user": s["user"], "host": s["host"],
                        "mc": s["mc"], "tools": by_sid[s["sid"]]["tools"][:120]
                        if False else ""}
                       for s in sub[:peek_n]]
        out["peek_top_unledgered_strong"] = peek

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
