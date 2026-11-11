#!/usr/bin/env python3
"""
baize_posttrain_r208_corpus_coverage_audit.py - R208: v11-v35 SFT Corpus
Coverage Audit vs EDA-Eval-PyAether 158-task API Requirement.

QUESTION: Does the 943-pair v11-v35 merged corpus teach the APIs that the
158 eval tasks actually require? Quantify the gap BEFORE spending GPU.

Inputs (all in run/):
  - pyAether_eval_488_apis.txt        : 488 fully-qualified eval-required APIs
                                        (pyAether.Func  OR  pyAether.Class.method)
  - sft_pyaether_corpus_v11_v35_merged.jsonl : 943 pairs, field api_used = list
                                        of short API names (class/func level)

Coverage metric (3 tiers, most-defensible first):
  - Tier-2 CLASS-AWARE (primary): eval entry pyAether.X covered if
        * X in corpus_apis           (1-dot: top-level func/class taught), OR
        * for 2-dot pyAether.C.m: C in corpus_apis (class taught) OR m in corpus_apis
  - Tier-1 LEAF (loose): eval entry covered if its last '.'-token in corpus_apis
  - Tier-3 STRICT (full): eval entry covered if full path in corpus_apis

Also reports:
  - per-family gap (families = token after pyAether.)
  - per-type corpus pair distribution
  - top uncovered families (concentration of the gap)
  - surplus = corpus APIs taught but not eval-required

Pure Python 3.8+ stdlib. Compatible with system python on .17.

Usage:
  python baize_posttrain_r208_corpus_coverage_audit.py
  python baize_posttrain_r208_corpus_coverage_audit.py --dry-run
  python baize_posttrain_r208_corpus_coverage_audit.py --json r208_coverage_audit.json

R208 (2026-11-11 wake277): evidence-based de-risking before GPU spend on v11-v35 SFT.
References: R206 (943-pair consolidation), task red-line #5 (numbers traceable to files).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from typing import Dict, List, Set, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_API_FILE = os.path.join(SCRIPT_DIR, "pyAether_eval_488_apis.txt")
CORPUS_FILE = os.path.join(SCRIPT_DIR, "sft_pyaether_corpus_v11_v35_merged.jsonl")


def load_eval_apis(path):
    if not os.path.isfile(path):
        print("ERROR: eval API file not found: " + path, file=sys.stderr)
        sys.exit(2)
    out = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            s = line.strip()
            if s:
                out.append(s)
    return out


def load_corpus(path):
    if not os.path.isfile(path):
        print("ERROR: corpus file not found: " + path, file=sys.stderr)
        sys.exit(2)
    records = []
    apis = set()
    tcount = Counter()
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            records.append(rec)
            tcount[rec.get("type", "?")] += 1
            for a in rec.get("api_used", []) or []:
                apis.add(a)
    return records, apis, tcount


def family_of(eval_api):
    parts = eval_api.split(".")
    if len(parts) >= 2 and parts[0] == "pyAether":
        return parts[1]
    return eval_api


def leaf_of(eval_api):
    return eval_api.split(".")[-1]


def coverage_tiers(eval_apis, corpus_apis):
    t1 = Counter()
    t2 = Counter()
    t3 = Counter()
    for entry in eval_apis:
        leaf = leaf_of(entry)
        fam = family_of(entry)
        parts = entry.split(".")
        is_method = (len(parts) == 3 and parts[0] == "pyAether")
        if leaf in corpus_apis:
            t1["covered"] += 1
        else:
            t1["uncovered"] += 1
        if is_method:
            if fam in corpus_apis or leaf in corpus_apis:
                t2["covered"] += 1
            else:
                t2["uncovered"] += 1
        else:
            if fam in corpus_apis:
                t2["covered"] += 1
            else:
                t2["uncovered"] += 1
        if entry in corpus_apis or (entry.startswith("pyAether.") and entry[len("pyAether."):] in corpus_apis):
            t3["covered"] += 1
        else:
            t3["uncovered"] += 1
    return t1, t2, t3


def gap_by_family(eval_apis, corpus_apis):
    fam_total = Counter()
    fam_uncov = Counter()
    for entry in eval_apis:
        fam = family_of(entry)
        parts = entry.split(".")
        is_method = (len(parts) == 3 and parts[0] == "pyAether")
        leaf = leaf_of(entry)
        fam_total[fam] += 1
        covered = (fam in corpus_apis) or (is_method and leaf in corpus_apis)
        if not covered:
            fam_uncov[fam] += 1
    rows = []
    for fam, total in fam_total.most_common():
        rows.append((fam, fam_uncov.get(fam, 0), total))
    return rows


def main():
    ap = argparse.ArgumentParser(description="R208 corpus coverage audit")
    ap.add_argument("--dry-run", action="store_true", help="use built-in sample")
    ap.add_argument("--json", metavar="PATH", help="write JSON summary to PATH")
    args = ap.parse_args()

    if args.dry_run:
        eval_apis = ["pyAether.dbCrtInst", "pyAether.EmyLPPHeader.create",
                     "pyAether.EmyLPPHeader.getLayerNum", "pyAether.notInCorpus",
                     "pyAether.CColor"]
        corpus_apis = {"dbCrtInst", "EmyLPPHeader", "CColor"}
        tcount = Counter({"S1": 2, "S4": 1})
        n_pairs = 3
        src_eval = "dry-run sample"
        src_corpus = "dry-run sample"
    else:
        eval_apis = load_eval_apis(EVAL_API_FILE)
        records, corpus_apis, tcount = load_corpus(CORPUS_FILE)
        n_pairs = len(records)
        src_eval = EVAL_API_FILE
        src_corpus = CORPUS_FILE

    n_eval = len(eval_apis)
    eval_leaf = set(leaf_of(e) for e in eval_apis)
    eval_fam = set(family_of(e) for e in eval_apis)

    t1, t2, t3 = coverage_tiers(eval_apis, corpus_apis)

    fam_rows = gap_by_family(eval_apis, corpus_apis)
    fam_with_gap = [(f, u, t) for (f, u, t) in fam_rows if u > 0]
    fam_fully_uncovered = [(f, u, t) for (f, u, t) in fam_rows if u == t and t > 0]
    fam_fully_covered = [(f, u, t) for (f, u, t) in fam_rows if u == 0]

    surplus = sorted(corpus_apis - eval_leaf)

    print("=" * 70)
    print("R208: v11-v35 SFT Corpus Coverage Audit vs 158-task Eval API Set")
    print("=" * 70)
    print("eval API file     : " + src_eval)
    print("corpus file       : " + src_corpus)
    print("corpus pairs      : " + str(n_pairs))
    print("corpus unique APIs: " + str(len(corpus_apis)))
    print("eval API entries  : " + str(n_eval) + "  (unique leaf: " + str(len(eval_leaf)) + ", families: " + str(len(eval_fam)) + ")")
    print("-" * 70)
    cov1 = t1["covered"]
    cov2 = t2["covered"]
    cov3 = t3["covered"]
    print("Coverage (3 tiers):")
    print("  Tier-2 CLASS-AWARE (PRIMARY): " + str(cov2) + "/" + str(n_eval) + " = " + str(round(cov2 / n_eval * 100, 1)) + "%")
    print("  Tier-1 LEAF (loose)         : " + str(cov1) + "/" + str(n_eval) + " = " + str(round(cov1 / n_eval * 100, 1)) + "%")
    print("  Tier-3 STRICT (full path)   : " + str(cov3) + "/" + str(n_eval) + " = " + str(round(cov3 / n_eval * 100, 1)) + "%")
    print("-" * 70)
    print("Corpus per-type pair distribution: " + str(dict(tcount.most_common())))
    print("-" * 70)
    print("Families with gap (uncovered>0): " + str(len(fam_with_gap)) + " / " + str(len(fam_rows)) + " total")
    print("Families FULLY uncovered       : " + str(len(fam_fully_uncovered)))
    print("Families FULLY covered         : " + str(len(fam_fully_covered)))
    print("Top 20 families by uncovered count (family, uncovered, total):")
    for f, u, t in sorted(fam_with_gap, key=lambda x: -x[1])[:20]:
        print("  " + f.ljust(42) + "  uncov=" + str(u).rjust(3) + "  total=" + str(t).rjust(3))
    print("-" * 70)
    print("Surplus corpus APIs (taught, NOT eval-required): " + str(len(surplus)))
    if surplus:
        print("  sample: " + str(surplus[:20]))
    print("-" * 70)
    pct2 = cov2 / n_eval * 100
    if pct2 >= 70:
        verdict = "GOOD - corpus covers >=70% of eval APIs; proceed to SFT with confidence."
    elif pct2 >= 50:
        verdict = "MODERATE - 50-70% coverage; SFT may help but gap material; consider v36+ augmentation targeting uncovered families."
    else:
        verdict = "WEAK - <50% coverage; SFT on this corpus alone unlikely to move eval much; augment corpus targeting top uncovered families before GPU spend."
    print("Pre-GPU verdict (tier-2 " + str(round(pct2, 1)) + "%): " + verdict)
    print("=" * 70)

    summary = {
        "round": "R208",
        "purpose": "v11-v35 corpus coverage audit vs 158-task eval API requirement (de-risk GPU spend)",
        "sources": {"eval_apis": src_eval, "corpus": src_corpus},
        "corpus_pairs": n_pairs,
        "corpus_unique_apis": len(corpus_apis),
        "eval_api_entries": n_eval,
        "eval_unique_leaf_names": len(eval_leaf),
        "eval_families": len(eval_fam),
        "coverage": {
            "tier2_class_aware_primary": {"covered": cov2, "total": n_eval, "pct": round(cov2 / n_eval * 100, 2)},
            "tier1_leaf_loose": {"covered": cov1, "total": n_eval, "pct": round(cov1 / n_eval * 100, 2)},
            "tier3_strict_full": {"covered": cov3, "total": n_eval, "pct": round(cov3 / n_eval * 100, 2)},
        },
        "corpus_type_distribution": dict(tcount.most_common()),
        "families_total": len(fam_rows),
        "families_with_gap": len(fam_with_gap),
        "families_fully_uncovered": len(fam_fully_uncovered),
        "families_fully_covered": len(fam_fully_covered),
        "top_uncovered_families": [
            {"family": f, "uncovered": u, "total": t}
            for f, u, t in sorted(fam_with_gap, key=lambda x: -x[1])[:30]
        ],
        "fully_uncovered_families_sample": [
            {"family": f, "total": t}
            for f, u, t in fam_fully_uncovered[:30]
        ],
        "surplus_corpus_apis_count": len(surplus),
        "surplus_corpus_apis_sample": surplus[:30],
        "pre_gpu_verdict": verdict,
        "note": ("Tier-2 is the defensible primary metric: 1-dot pyAether.F covered if F in "
                 "corpus; 2-dot pyAether.C.m covered if C (class) or m (method) in corpus. "
                 "Surplus = corpus APIs the eval does not test (not necessarily bad)."),
    }
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, ensure_ascii=False, indent=2)
        print("")
        print("JSON summary written: " + args.json)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
