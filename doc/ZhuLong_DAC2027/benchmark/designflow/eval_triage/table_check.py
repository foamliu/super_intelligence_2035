#!/usr/bin/env python3
"""Arithmetic audit of the two results tables, parsed straight from the .tex.

Read-only.  Checks, per row:
  * PASS + FAIL == decided denominator used for Pass%
  * Pass% == round(100*PASS/(PASS+FAIL), 1)
  * in the appendix table: PASS+FAIL+ERROR+ABSENT == Total, and Total col sums to 696
  * in the main table: what the "Total" column actually is
  * column sums and the Overall row

Usage:  python table_check.py
"""
import re
from pathlib import Path

PAPER = Path(r"D:\Users\Administrator\code\super_intelligence_2035\doc\ZhuLong_DAC2027"
             r"\EDA-LiveFlow-Bench_ICML2027")


def rows_of(rel, start, end):
    """Return [(lineno, [cells])] for body rows between two line markers."""
    lines = (PAPER / rel).read_text(encoding="utf-8").splitlines()
    out = []
    for i in range(start, end + 1):
        ln = lines[i - 1]
        if "\\\\" not in ln or "&" not in ln:
            continue
        cells = [c.strip().replace("\\textbf{", "").replace("}", "").strip()
                 for c in ln.split("&")]
        cells[-1] = cells[-1].rstrip("\\ ").strip()  # drop the "\\\\" row terminator
        out.append((i, cells))
    return out


def check(rel, start, end, ncols, has_err_abs, overall_line):
    print(f"\n########## {rel}  rows {start}-{end} ##########")
    R = rows_of(rel, start, end)
    sum_p = sum_f = sum_e = sum_a = sum_tot = 0
    bad = []
    print(f"{'ln':>4} {'domain':<20}{'P':>4}{'F':>5}{'E':>4}{'A':>4}{'Tot':>5}"
          f"{'P+F':>5}{'calc%':>8}{'tex%':>7}  verdict")
    for ln, c in R:
        name = c[0]
        if has_err_abs:
            p, f, e, a, tot, pct = (int(c[1]), int(c[2]), int(c[3]), int(c[4]),
                                    int(c[5]), float(c[6]))
        else:
            p, f, tot, pct = int(c[1]), int(c[2]), int(c[3]), float(c[4])
            e = a = 0
        dec = p + f
        calc = 100.0 * p / dec
        ok_pair = abs(round(calc, 1) - pct) < 1e-9
        verdict = []
        if not ok_pair:
            verdict.append(f"PASS% MISMATCH (should be {calc:.2f}->{round(calc, 1)})")
            bad.append((ln, "pct"))
        if has_err_abs:
            if p + f + e + a != tot:
                verdict.append(f"ROW SUM MISMATCH {p}+{f}+{e}+{a}!={tot}")
                bad.append((ln, "rowsum"))
        else:
            if p + f != tot:
                verdict.append(f"Total col {tot} != PASS+FAIL {dec}"
                               f" (Total is the 696-case count incl. ERROR/ABSENT)")
        sum_p += p; sum_f += f; sum_e += e; sum_a += a; sum_tot += tot
        print(f"{ln:>4} {name:<20}{p:>4}{f:>5}{e:>4}{a:>4}{tot:>5}"
              f"{dec:>5}{calc:>8.2f}{pct:>7.1f}  {'; '.join(verdict) if verdict else 'OK'}")

    print(f"  column sums: PASS={sum_p} FAIL={sum_f} ERROR={sum_e} "
          f"ABSENT={sum_a} TotalCol={sum_tot} decided={sum_p + sum_f}")
    overall_pct = 100.0 * sum_p / (sum_p + sum_f)
    print(f"  recomputed overall = {sum_p}/{sum_p + sum_f} = {overall_pct:.4f}% "
          f"-> {round(overall_pct, 1)}")
    ln, c = overall_line
    print(f"  tex Overall row (line {ln}): {c}")
    print(f"  -> arithmetic defects: {len(bad)}  {bad}")
    return sum_p, sum_f, sum_e, sum_a, sum_tot


# sections/4_experiments.tex tab:main-results: header l.42, body rows l.44-56, Overall l.58
check("sections/4_experiments.tex", 44, 56, 5, False, (58, ["Overall", "62", "558", "620", "10.0"]))
# appendix/B_additional_results.tex tab:full-domain-results: body l.25-37, Total l.39
check("appendix/B_additional_results.tex", 25, 37, 7, True, (39, ["Total", "62", "558", "70", "6", "696", "10.0"]))
