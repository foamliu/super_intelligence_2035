#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""P2 rft2 retest paired McNemar analysis.

Compares the P2 rft2 *retest* (V2-only re-run on 182 code_gen WaveView cases,
served by rft2_adapter_seed11 at :30003) against the ORIGINAL V2 run
(rft2_adapter_seed11, 32/182 = 17.6%) recorded in
``codegen_full_results_snapshot.json``.

Usage:
    python3 p2_rft2_retest_paired_analysis.py <retest_results.json> [<original_snapshot.json>]

Outputs a JSON report with per-case pairing, McNemar b/c/n, two-sided p-value,
and pass-rate comparison.  Honest negative-result reporting: if the retest
differs from the original we report it plainly; if it reproduces 17.6% we
report reproducibility confirmed.

This is preparation for when the P2 retest (run_codegen_v2only_rft2_rerun.py on
36.15) completes all 182 cases.
"""
import json
import sys
import math


def load_rows(path):
    with open(path) as f:
        d = json.load(f)
    return d["rows"] if isinstance(d, dict) and "rows" in d else d


def v2_verdict_map(rows):
    """Map case_id -> bool verdict for V2 arm rows."""
    m = {}
    for r in rows:
        if r.get("arm") == "V2":
            m[r["case_id"]] = bool(r.get("verdict", False))
    return m


def mcnemar_p(b, c, exact=True):
    """Two-sided McNemar p-value.  Exact binomial for small n=b+c (<=25),
    otherwise chi2 with continuity correction."""
    n = b + c
    if n == 0:
        return 1.0
    if exact and n <= 25:
        # exact two-sided binomial test: P(X<=min(b,c) or X>=max(b,c))
        from math import comb
        lo, hi = min(b, c), max(b, c)
        p_two = 0.0
        for k in range(0, lo + 1):
            p_two += comb(n, k) * (0.5 ** n)
        for k in range(hi, n + 1):
            p_two += comb(n, k) * (0.5 ** n)
        return min(p_two, 1.0)
    # chi2 with continuity correction
    chi2 = (abs(b - c) - 1) ** 2 / n if n > 0 else 0.0
    # survival function of chi2 with 1 dof
    return math.erfc(math.sqrt(chi2 / 2.0))


def main():
    if len(sys.argv) < 2:
        print("usage: p2_rft2_retest_paired_analysis.py <retest_results.json> "
              "[<original_snapshot.json>]", file=sys.stderr)
        sys.exit(2)
    retest_path = sys.argv[1]
    orig_path = sys.argv[2] if len(sys.argv) > 2 else \
        "codegen_full_results_snapshot.json"

    retest_rows = load_rows(retest_path)
    orig_rows = load_rows(orig_path)

    orig_v2 = v2_verdict_map(orig_rows)
    retest_v2 = v2_verdict_map(retest_rows)

    # pair on intersection of case_ids
    common = sorted(set(orig_v2) & set(retest_v2))
    only_orig = sorted(set(orig_v2) - set(retest_v2))
    only_retest = sorted(set(retest_v2) - set(orig_v2))

    b = 0  # orig pass, retest fail
    c = 0  # orig fail, retest pass
    both_pass = 0
    both_fail = 0
    flips = []
    for cid in common:
        o = orig_v2[cid]
        r = retest_v2[cid]
        if o and r:
            both_pass += 1
        elif not o and not r:
            both_fail += 1
        elif o and not r:
            b += 1
            flips.append({"case_id": cid, "dir": "pass->fail"})
        else:
            c += 1
            flips.append({"case_id": cid, "dir": "fail->pass"})

    orig_pass = sum(1 for cid in common if orig_v2[cid])
    retest_pass = sum(1 for cid in common if retest_v2[cid])
    n = len(common)
    p = mcnemar_p(b, c)

    report = {
        "analysis": "P2 rft2 retest vs original V2 (rft2) paired McNemar",
        "original_snapshot": orig_path,
        "retest_results": retest_path,
        "n_common": n,
        "n_only_original": len(only_orig),
        "n_only_retest": len(only_retest),
        "original_v2_pass": orig_pass,
        "original_v2_rate": round(orig_pass / n, 4) if n else None,
        "retest_v2_pass": retest_pass,
        "retest_v2_rate": round(retest_pass / n, 4) if n else None,
        "delta_pp": round((retest_pass - orig_pass) / n * 100, 2) if n else None,
        "both_pass": both_pass,
        "both_fail": both_fail,
        "mcnemar_b": b,
        "mcnemar_c": c,
        "mcnemar_p_two_sided": round(p, 6),
        "flips": flips,
        "conclusion": (
            "reproducible (no significant difference)" if p >= 0.05
            else "significant difference (retest != original)"
        ),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
