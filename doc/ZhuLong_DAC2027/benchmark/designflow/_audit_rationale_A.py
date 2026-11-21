#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_rationale consistency audit for shard A (21:5x hard gate)."""
import os, re, json

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")
REF   = os.path.join(BENCH, "reference")

RE_ASSERT = re.compile(r"^\s*assert\b", re.MULTILINE)
RE_RATIONALE_K = re.compile(r"\s*(\d+)\s*条?断?言?")
RE_HAS_LADEN = re.compile(r"[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]")

def resolve_check(cid):
    for p in (os.path.join(REF, cid, "check.py"),
              os.path.join(REF, cid.replace("EDA-Eval-DesignFlow-", ""), "check.py")):
        if os.path.exists(p):
            return p
    return None

def main():
    with open(JSONL) as f:
        cases = [json.loads(l) for l in f if l.strip()]
    rows = []
    for c in cases:
        cid = c.get("id") or c.get("task_id") or "?"
        meta = c.get("metadata", {})
        tr = meta.get("test_rationale", "") or ""
        kc = meta.get("k_check", 0)
        try: kc = int(kc)
        except: kc = 0
        m = RE_RATIONALE_K.match(tr)
        kr = int(m.group(1)) if m else 0
        cp = resolve_check(cid)
        if cp:
            src = open(cp, encoding="utf-8", errors="replace").read()
            ka = len(RE_ASSERT.findall(src))
        else:
            ka = -2
        has_laden = bool(RE_HAS_LADEN.search(tr))
        gate_ok = (kr == kc) and (kc >= 8)
        fmt_ok = has_laden and (kr > 0)
        rows.append({"cid": cid, "k_rationale": kr, "k_check": kc, "k_assert": ka,
                     "gate_ok": gate_ok, "fmt_ok": fmt_ok})
    n = len(rows)
    n_gate_ok = sum(1 for r in rows if r["gate_ok"])
    n_fmt_ok  = sum(1 for r in rows if r["fmt_ok"])
    n_klt8    = sum(1 for r in rows if r["k_check"] < 8)
    n_mismatch= sum(1 for r in rows if r["k_rationale"] != r["k_check"])
    n_nofound = sum(1 for r in rows if r["k_assert"] == -2)
    print(f"=== test_rationale consistency audit (shard A) ===")
    print(f"total cases: {n}")
    print(f"gate OK (kr==kc AND kc>=8): {n_gate_ok} ({100*n_gate_ok/n:.1f}%)")
    print(f"format OK (circled numerals + k>0): {n_fmt_ok} ({100*n_fmt_ok/n:.1f}%)")
    print(f"k_check < 8: {n_klt8}")
    print(f"kr != kc mismatch: {n_mismatch}")
    print(f"check.py not found: {n_nofound}")
    print()
    fails = [r for r in rows if not r["gate_ok"]]
    if fails:
        print(f"=== GATE FAILURES ({len(fails)}) ===")
        print(f"{'cid':<58} kr  kc  k_assert  fmt gate")
        for r in fails[:80]:
            print(f"{r['cid']:<58} {r['k_rationale']:>2} {r['k_check']:>3} {r['k_assert']:>7}  {'Y' if r['fmt_ok'] else 'N':>3} {'OK' if r['gate_ok'] else 'FAIL'}")
        if len(fails) > 80:
            print(f"... and {len(fails)-80} more")
    drift = [r for r in rows if r["k_assert"] >= 0 and abs(r["k_assert"] - r["k_check"]) > max(3, r["k_check"]*0.3)]
    if drift:
        print()
        print(f"=== k_assert DRIFT (>30%) ({len(drift)}) ===")
        for r in drift[:30]:
            print(f"{r['cid']:<58} kc={r['k_check']:>3} k_assert={r['k_assert']:>3}")
    out = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/test_rationale_audit_A.tsv"
    with open(out, "w") as f:
        f.write("case_id\tk_rationale\tk_check\tk_assert\tformat_ok\tgate_ok\n")
        for r in rows:
            f.write(f"{r['cid']}\t{r['k_rationale']}\t{r['k_check']}\t{r['k_assert']}\t{'Y' if r['fmt_ok'] else 'N'}\t{'OK' if r['gate_ok'] else 'FAIL'}\n")
    print(f"\nwritten: {out}")

if __name__ == "__main__":
    main()
