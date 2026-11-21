#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate unified anti_hardcode_audit_all.tsv in directive's required columns.

Input: per-shard static-audit TSVs (/tmp/audit_{D_full,A_s25,B_s25,C_s25}.tsv)
Output: designflow/anti_hardcode_audit_all.tsv with columns:
  shard | case_id | k_check | 有anti_hardcode(y/n) | 只在B跑(y/n) | print_only | core_deleted | hardcode_a | 判定(PASS/GAP) | 建议

Mapping (static signals → directive columns):
  有anti_hardcode = y iff (has_embed_A AND has_A_gold_xcheck)  [A-gold cross-check mechanism]
  只在B跑       = y iff has_subprocess AND not has_A_gold_xcheck (candidate run on B only)
                  n if no subprocess (static read, no candidate run) / MISSING
  print_only    = PASS(vuln) iff (only_static_read) OR (has_subprocess AND not has_A_gold_xcheck)
                  FAIL iff has_A_gold_xcheck
  core_deleted  = same as print_only (both defeated only by A-gold cross-check / subprocess+deriv)
  hardcode_a    = FAIL(static) for most (check runs on B, A-answer mismatches B-expected).
                  Marked "FAIL(静态)" with caveat: not runtime-tested; could PASS if check leaks A.
  判定          = GAP if print_only==PASS or core_deleted==PASS or hardcode_a==PASS else PASS
  建议          = action

Runtime-confirmed GAPs (this round):
  D ParasiticsAnnotDiag-001 (print_only PASS, confirmed)
  D AddrRtlGateMap-001 (print_only PASS, confirmed)
"""
import os, re, sys
from collections import Counter, defaultdict

WORK = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark"
OUT_TSV = os.path.join(WORK, "designflow", "anti_hardcode_audit_all.tsv")

SOURCES = [
    ("D", "/tmp/audit_D_full.tsv"),
    ("A", "/tmp/audit_A_s25.tsv"),
    ("B", "/tmp/audit_B_s25.tsv"),
    ("C", "/tmp/audit_C_s25.tsv"),
]

RUNTIME_CONFIRMED = {
    ("D", "EDA-Eval-DesignFlow-ParasiticsAnnotDiag-001"): "print_only PASS (confirmed: ship reference_report_B.md verbatim)",
    ("D", "EDA-Eval-DesignFlow-AddrRtlGateMap-001"): "print_only PASS (confirmed: ship precomputed B gold netlist.json)",
}


def load_tsv(path):
    rows = []
    with open(path) as f:
        header = f.readline().rstrip("\n").split("\t")
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(header):
                parts += [""] * (len(header) - len(parts))
            rows.append(dict(zip(header, parts)))
    return rows


def b(v):
    if v in ("True", "true", True): return True
    return False


def classify(r):
    shard = r["shard"]; cid = r["case_id"]
    verdict = r["verdict"]
    has_sub = b(r.get("has_subprocess"))
    has_embed = b(r.get("has_embed_A"))
    has_agold = b(r.get("has_A_gold_xcheck"))
    only_static = b(r.get("only_static_read"))
    k = r.get("k", "0")
    try: k = int(k)
    except: k = 0

    if verdict == "MISSING":
        return dict(k=k, anti="n/a", onlyB="n/a",
                    po="n/a", cd="n/a", ha="n/a",
                    judge="MISSING", sug="check.py 缺失，先补 check.py 再审")
    if verdict == "WEAK":
        # has teeth (subprocess+embed+A_gold) but low k -> structurally OK, low assertion count
        return dict(k=k, anti="y", onlyB="n",
                    po="FAIL", cd="FAIL", ha="FAIL(静态)",
                    judge="WEAK", sug="k=%d<12 偏低，补断言至 ≥8 独立条件（anti-hardcode 闸门已具备）" % k)

    anti_hardcode = "y" if (has_embed and has_agold) else "n"
    only_B = "y" if (has_sub and not has_agold) else ("n" if not has_sub else "n")
    # print_only / core_deleted vuln
    if has_agold:
        po = "FAIL"; cd = "FAIL"
    elif only_static:
        po = "PASS"; cd = "PASS"
    elif has_sub and not has_agold:
        po = "PASS"; cd = "PASS"
    else:
        po = "FAIL"; cd = "FAIL"
    # hardcode_a: A-answer run on B; if check uses B (subprocess or B-constants) → FAIL.
    # Statically assume FAIL (check runs on B / compares to B). Caveat: not runtime-tested.
    ha = "FAIL(静态)" if has_sub else "FAIL(静态)"
    # if only_static read and report is about whatever candidate analyzed (A), check wants B
    # tokens → hardcode_a (ship A report) FAILs. So hardcode_a FAIL.

    judge = "GAP" if (po == "PASS" or cd == "PASS" or ha.startswith("PASS")) else "PASS"

    # suggestion
    if judge == "PASS":
        sug = "保留；抽查 1 条重跑 negative_selftest"
    elif only_static:
        sug = "重写 check.py：要求交付分析脚本而非报告，check 在 B 上 subprocess 运行脚本 + 嵌入 A fixture 做 A-gold 交叉校验"
    elif has_sub and not has_agold:
        sug = "补 A-gold 交叉校验：嵌入 A fixture(base64)，check 同时在 A 上跑候选并断言 A-gold，击穿 B-only 硬编码 stub"
    else:
        sug = "补 anti-hardcode 闸门（A-gold 交叉校验 + 三假回归）"

    # runtime-confirmed marker
    if (shard, cid) in RUNTIME_CONFIRMED:
        sug = "【运行时已确认 GAP】" + RUNTIME_CONFIRMED[(shard, cid)] + "；" + sug

    return dict(k=k, anti=anti_hardcode, onlyB=only_B,
                po=po, cd=cd, ha=ha, judge=judge, sug=sug)


def main():
    all_rows = []
    for shard, path in SOURCES:
        if not os.path.exists(path):
            sys.stderr.write("missing %s\n" % path)
            continue
        for r in load_tsv(path):
            c = classify(r)
            all_rows.append((r["shard"], r["case_id"], c))

    cols = ["shard", "case_id", "k_check", "有anti_hardcode(y/n)",
            "只在B跑(y/n)", "print_only", "core_deleted", "hardcode_a",
            "判定(PASS/GAP)", "建议"]
    lines = ["\t".join(cols)]
    for shard, cid, c in all_rows:
        lines.append("\t".join([
            shard, cid, str(c["k"]), c["anti"], c["onlyB"],
            c["po"], c["cd"], c["ha"], c["judge"], c["sug"]
        ]))
    with open(OUT_TSV, "w") as f:
        f.write("\n".join(lines) + "\n")
    sys.stderr.write("wrote %s (%d rows)\n" % (OUT_TSV, len(all_rows)))

    # summary
    by_shard = defaultdict(Counter)
    for shard, cid, c in all_rows:
        by_shard[shard][c["judge"]] += 1
    print("\n=== 判定 by shard ===")
    print("shard  PASS  GAP  MISSING  total")
    for s in ["A", "B", "C", "D"]:
        c = by_shard[s]
        tot = sum(c.values())
        print(f"{s:6} {c.get('PASS',0):5} {c.get('GAP',0):4} {c.get('MISSING',0):8} {tot:5}")
    # GAP by k-band (D only, full)
    print("\n=== D GAP by k-band ===")
    bands = Counter()
    for shard, cid, c in all_rows:
        if shard != "D" or c["judge"] != "GAP": continue
        k = c["k"]
        if k == 0: b = "k=0(无rationale)"
        elif k < 8: b = "k<8"
        elif k < 12: b = "8<=k<12"
        elif k < 16: b = "12<=k<16"
        else: b = "k>=16"
        bands[b] += 1
    for b in ["k=0(无rationale)","k<8","8<=k<12","12<=k<16","k>=16"]:
        print(f"  {b:18} {bands[b]}")

if __name__ == "__main__":
    main()
