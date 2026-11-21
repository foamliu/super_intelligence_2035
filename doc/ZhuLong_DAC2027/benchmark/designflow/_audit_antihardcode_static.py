#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Static anti-hardcode audit scanner (§4.9).

Scans check.py for each case and flags GAPs by static signals:
  - has_subprocess : does check.py RUN the candidate script on B? (anti print_only)
  - has_embed_A    : does check.py embed A fixture (base64) for A-gold cross-check?
  - has_A_gold_xcheck : does check.py run candidate on A and compare to A-gold?
  - only_static_read : check.py only reads static artifacts (.md/.txt/.csv) from zip
                       -> inherently vulnerable to fake_print_only
  - B_only_constants : B expected values hardcoded, no A-run -> vulnerable to hardcode_a

Classification:
  PASS  : has_subprocess AND has_embed_A AND has_A_gold_xcheck (full anti-hardcode)
  GAP   : any of the 3 fakes can PASS by static analysis
  WEAK  : partial (e.g. subprocess on B but no A-gold cross-check)

Usage:
  python3 _audit_antihardcode_static.py --shard D --all
  python3 _audit_antihardcode_static.py --shard A --sample 25
"""
import os, sys, re, json, glob, argparse, random

DEFAULT_BENCH_ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
BENCH_ROOT = DEFAULT_BENCH_ROOT
REF_ROOT = os.path.join(BENCH_ROOT, "reference")
JSONL = {
    "A": "EDA-Eval-DesignFlow_A.jsonl",
    "B": "EDA-Eval-DesignFlow_B.jsonl",
    "C": "EDA-Eval-DesignFlow_C.jsonl",
    "D": "EDA-Eval-DesignFlow_D.jsonl",
}

# anti-hardcode signals (case-insensitive)
RE_SUBPROCESS = re.compile(r"\bsubprocess\b|\bPopen\b|os\.system|os\.popen|run\(\[|subprocess\.run|subprocess\.check_")
RE_B64 = re.compile(r"b64decode|base64|b64encode")
RE_A_GOLD = re.compile(r"A_gold|A-gold|Agold|a_gold|cross[_-]?check|on_a_|run_on_a|_on_A\b|A_fixture|A_netlist|A_input|recount|_gt_|ground_truth|gt_parse|gt_recount|gt_simulate")
RE_STATIC_READ = re.compile(r"\.md\b|\.txt\b|\.csv\b|\.log\b|\.json\b|\.lis\b|report|diagnos|read_report|\.read\(\)|extractall")
RE_B_CONST = re.compile(r"\bB_[A-Z]+\s*=|B_EXPECTED|B_DESIGN|B_MAIN|B_TOTAL|expected_b|HIDDEN_B_|B_ANSWER")
RE_ZIP_EXTRACT = re.compile(r"extractall|ZipFile")
RE_ASSERT_COUNT = re.compile(r"^\s*assert\b", re.MULTILINE)


def k_from_rationale(tr):
    if not tr: return 0
    m = re.match(r"\s*(\d+)", tr)
    return int(m.group(1)) if m else 0


def resolve_check_path(cid):
    """Try reference/<cid>/check.py and reference/<short>/check.py."""
    p = os.path.join(REF_ROOT, cid, "check.py")
    if os.path.exists(p):
        return p
    short = cid.replace("EDA-Eval-DesignFlow-", "")
    p2 = os.path.join(REF_ROOT, short, "check.py")
    if os.path.exists(p2):
        return p2
    return None


def scan_check(check_path):
    """Return dict of static signals for one check.py."""
    if check_path is None or not os.path.exists(check_path):
        return None
    try:
        with open(check_path, "r", errors="replace") as f:
            src = f.read()
    except Exception:
        return None
    n_assert = len(RE_ASSERT_COUNT.findall(src))
    has_sub = bool(RE_SUBPROCESS.search(src))
    has_b64 = bool(RE_B64.search(src))
    has_agold = bool(RE_A_GOLD.search(src))
    has_static = bool(RE_STATIC_READ.search(src))
    has_bconst = bool(RE_B_CONST.search(src))
    has_zip = bool(RE_ZIP_EXTRACT.search(src))
    # "only static read" = reads report-like artifact AND no subprocess
    only_static = has_static and not has_sub
    # anti-hardcode score: how many of the 3 teeth present
    teeth = sum([has_sub, has_b64, has_agold])
    return {
        "n_assert": n_assert,
        "has_subprocess": has_sub,
        "has_embed_A": has_b64,
        "has_A_gold_xcheck": has_agold,
        "has_static_read": has_static,
        "has_B_constants": has_bconst,
        "only_static_read": only_static,
        "teeth": teeth,
        "size": len(src),
    }


def classify(sig, k):
    """Classify PASS / GAP / WEAK by static signals + k."""
    if sig is None:
        return "MISSING", "check.py not found"
    reasons = []
    # §4.9(b) print_only: if check only reads static report and does substring match,
    # a candidate shipping the expected B report passes.
    if sig["only_static_read"]:
        reasons.append("print_only_vuln(no subprocess; static report grep)")
    # §4.9(c) core_deleted: if no subprocess, deleting core logic of candidate
    # (which never runs) trivially passes -- same vuln as print_only
    if not sig["has_subprocess"]:
        reasons.append("core_deleted_vuln(no subprocess execution of candidate)")
    # §4.9 hardcode_a: if check only runs B and B constants hardcoded with no
    # A-gold cross-check, a candidate that hardcodes B passes (B-only stub).
    if sig["has_subprocess"] and not sig["has_A_gold_xcheck"] and not sig["has_embed_A"]:
        reasons.append("hardcode_a_vuln(subprocess on B only, no A-gold cross-check)")
    # low-k amplifies risk
    if 0 < k < 12:
        reasons.append("low_k(%d)" % k)
    if reasons:
        # GAP if any vuln, else WEAK
        if any("vuln" in r for r in reasons):
            return "GAP", "; ".join(reasons)
        return "WEAK", "; ".join(reasons)
    return "PASS", "subprocess+embed_A+A_gold_xcheck all present"


def load_shard_cases(shard):
    path = os.path.join(BENCH_ROOT, JSONL[shard])
    cases = []
    with open(path) as f:
        for line in f:
            c = json.loads(line)
            cid = c.get("id") or c.get("case_id") or c.get("task_id_full") or c.get("task_id")
            meta = c.get("metadata", {})
            tr = meta.get("test_rationale", "")
            k = k_from_rationale(tr)
            kc = meta.get("k_check", 0)
            try: kc = int(kc)
            except: kc = 0
            cases.append({
                "id": cid,
                "k_rationale": k,
                "k_check": kc,
                "domain": meta.get("domain", ""),
                "subdomain": meta.get("subdomain", ""),
                "hidden_b": meta.get("hidden_b"),
            })
    return cases


def audit_shard(shard, sample=None, prefer_low_k=True):
    cases = load_shard_cases(shard)
    # decide sample
    if sample and sample < len(cases):
        if prefer_low_k:
            low = [c for c in cases if 0 < c["k_rationale"] < 12]
            rest = [c for c in cases if not (0 < c["k_rationale"] < 12)]
            random.seed(42)
            pick_low = low[:min(sample, len(low))]
            need = sample - len(pick_low)
            pick_rest = random.sample(rest, min(max(need, 0), len(rest))) if need > 0 else []
            sampled = pick_low + pick_rest
        else:
            random.seed(42)
            sampled = random.sample(cases, sample)
    else:
        sampled = cases
    rows = []
    for c in sampled:
        cid = c["id"]
        # find check.py: try reference/<cid>/check.py
        check_path = resolve_check_path(cid)
        sig = scan_check(check_path)
        verdict, reason = classify(sig, c["k_rationale"] or c["k_check"])
        rows.append({
            "shard": shard,
            "case_id": cid,
            "k": c["k_rationale"] or c["k_check"],
            "domain": c["domain"],
            "n_assert": sig["n_assert"] if sig else 0,
            "has_subprocess": sig["has_subprocess"] if sig else False,
            "has_embed_A": sig["has_embed_A"] if sig else False,
            "has_A_gold_xcheck": sig["has_A_gold_xcheck"] if sig else False,
            "only_static_read": sig["only_static_read"] if sig else False,
            "verdict": verdict,
            "reason": reason,
        })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", required=True)
    ap.add_argument("--sample", type=int, default=0, help="0 = all")
    ap.add_argument("--all", action="store_true", help="scan all cases in shard")
    ap.add_argument("--out", default=None)
    ap.add_argument("--bench-root", default=DEFAULT_BENCH_ROOT,
                    help="benchmarks/EDA-Eval-DesignFlow root (default: EDA-Flow-Bench)")
    args = ap.parse_args()
    global BENCH_ROOT, REF_ROOT
    BENCH_ROOT = args.bench_root
    REF_ROOT = os.path.join(BENCH_ROOT, "reference")
    sample = args.sample if args.sample > 0 else None
    rows = audit_shard(args.shard, sample=sample)
    # print TSV
    cols = ["shard","case_id","k","domain","n_assert","has_subprocess","has_embed_A","has_A_gold_xcheck","only_static_read","verdict","reason"]
    print("\t".join(cols))
    for r in rows:
        print("\t".join(str(r.get(c)) for c in cols))
    # summary
    from collections import Counter
    vc = Counter(r["verdict"] for r in rows)
    sys.stderr.write("\n[%s] verdict summary (n=%d): %s\n" % (args.shard, len(rows), dict(vc)))
    if args.out:
        with open(args.out, "w") as f:
            f.write("\t".join(cols) + "\n")
            for r in rows:
                f.write("\t".join(str(r.get(c)) for c in cols) + "\n")
        sys.stderr.write("wrote %s\n" % args.out)

if __name__ == "__main__":
    main()
