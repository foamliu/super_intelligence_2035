#!/usr/bin/env python3
"""Wilson-score 95% confidence intervals for EDA-LiveFlow-Bench pass rates.

stdout only, stdlib only.  Ground truth = run_batch_20261109_171201:
    total 696, PASS 62, FAIL 558, ERROR 70, ABSENT 6
    (as recorded in the paper dir's results.txt)

Usage:  python ci_wilson.py
"""
from math import sqrt, erfc

Z = 1.959963984540054  # two-sided 95%


def wilson(k, n, z=Z):
    """Wilson score interval for k successes out of n."""
    if n <= 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n
    d = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = (z / d) * sqrt(p * (1 - p) / n + z * z / (4.0 * n * n))
    lo = max(0.0, centre - half)
    hi = min(1.0, centre + half)
    return (100 * p, 100 * lo, 100 * hi)


def table(rows, head):
    w = [max(len(str(r[i])) for r in ([head] + rows)) for i in range(len(head))]
    out = []
    fmt = "  ".join("{:<%d}" % x for x in w)
    out.append(fmt.format(*head))
    out.append("  ".join("-" * x for x in w))
    for r in rows:
        out.append(fmt.format(*[str(c) for c in r]))
    return "\n".join(out)


# ---------------------------------------------------------------- grand totals
P, F, E, A = 62, 558, 70, 6
N_TOTAL = P + F + E + A

print("=" * 78)
print("SECTION A  Grand totals from run_batch_20261109_171201")
print("=" * 78)
print(f"PASS={P}  FAIL={F}  ERROR={E}  ABSENT={A}  ->  sum={N_TOTAL}   (expected 696)")
print()

rows = []
for label, denom, note in [
    ("PASS/(PASS+FAIL)", P + F, "paper's current denominator (620)"),
    ("PASS/(PASS+FAIL+ABSENT)", P + F + A, "ABSENT treated as failure (626)"),
    ("PASS/all 696 cases", N_TOTAL, "ERROR counted as non-pass (696)"),
]:
    p, lo, hi = wilson(P, denom)
    rows.append([label, f"{P}/{denom}", note, f"{p:.2f}", f"[{lo:.2f}, {hi:.2f}]", f"{hi - lo:.2f}"])
print(table(rows, ["estimator", "k/n", "note", "p_hat %", "Wilson 95% CI", "width pp"]))
print()
print("delta between the 620 and 626 point estimates: "
      f"{wilson(P, 620)[0]:.2f}% - {wilson(P, 626)[0]:.2f}% = "
      f"{wilson(P, 620)[0] - wilson(P, 626)[0]:.3f} pp")
print("620-CI and 626-CI overlap -> the '9.9' vs '10.0' decimal is noise, NOT a finding.")
print()

# ------------------------------------------------------- per-domain (paper tab)
# Identical PASS/FAIL cells in sections/4_experiments.tex tab:main-results (l.44-56)
# and appendix/B_additional_results.tex tab:full-domain-results (l.25-37).
DOMAINS = [
    # name, PASS, FAIL, ERROR, ABSENT  (ERROR/ABSENT only in appendix table)
    ("pnr_signoff",       5,  19, 0, 1),
    ("characterization",  5,  21, 2, 0),
    ("eda_other",         6,  27, 4, 1),
    ("pg_layout",         4,  24, 0, 0),
    ("schematic_netlist", 13, 100, 18, 0),
    ("digital",           5,  40, 6, 0),
    ("layout_virtuoso",   4,  35, 0, 1),
    ("analog_context",    4,  39, 12, 0),
    ("verification",      3,  30, 5, 0),
    ("spice_sim",         8,  87, 7, 2),
    ("waveform",          2,  37, 8, 0),
    ("physical_verify",   2,  66, 4, 1),
    ("layout_aether",     1,  33, 4, 0),
]

print("=" * 78)
print("SECTION B  Per-domain p_hat and Wilson 95% CI  (n = PASS+FAIL)")
print("=" * 78)
rows = []
for name, p_, f_, e_, a_ in DOMAINS:
    n = p_ + f_
    ph, lo, hi = wilson(p_, n)
    flag = "SMALL n<30 -> CI uncomparable" if n < 30 else ""
    rows.append([name, f"{p_}/{n}", f"{ph:.2f}", f"[{lo:.2f}, {hi:.2f}]",
                 f"{hi - lo:.1f}", flag])
print(table(rows, ["domain", "PASS/decided", "p_hat %", "Wilson 95% CI", "width pp", "flag"]))
print()

tp = sum(d[1] for d in DOMAINS)
tf = sum(d[2] for d in DOMAINS)
te = sum(d[3] for d in DOMAINS)
ta = sum(d[4] for d in DOMAINS)
print(f"column sums: PASS={tp}  FAIL={tf}  ERROR={te}  ABSENT={ta}  "
      f"case-total={tp + tf + te + ta}")
print(f"decided={tp + tf}   p_hat={100 * tp / (tp + tf):.4f}%  "
      f"-> rounds to {100 * tp / (tp + tf):.1f}%")
print()
print("Weighting sensitivity (case-pooled vs mean-of-domain-rates):")
unw = sum(100 * d[1] / (d[1] + d[2]) for d in DOMAINS) / len(DOMAINS)
print(f"  case-pooled (62/620)          = {100 * P / (P + F):.2f}%")
print(f"  unweighted mean of 13 domains = {unw:.2f}%")
print()

print("=" * 78)
print("SECTION C  Domain-gap claims (abstract / intro / concl. / Sec.4)")
print("=" * 78)
d = {x[0]: (100 * x[1] / (x[1] + x[2])) for x in DOMAINS}
print(f"best  (pnr_signoff)     = {d['pnr_signoff']:.2f}%  "
      f"CI [{wilson(5, 24)[1]:.1f}, {wilson(5, 24)[2]:.1f}]  (n=24)")
print(f"worst (physical_verify) = {d['physical_verify']:.2f}%  "
      f"CI [{wilson(2, 68)[1]:.1f}, {wilson(2, 68)[2]:.1f}]  (n=68)")
print(f"tie   (layout_aether)   = {d['layout_aether']:.2f}%  "
      f"CI [{wilson(1, 34)[1]:.1f}, {wilson(1, 34)[2]:.1f}]  (n=34)")
print(f"ratio best/worst        = {d['pnr_signoff'] / d['physical_verify']:.2f}x "
      f"(paper says ~7x)")
blo = wilson(5, 24)[1]
whi = wilson(2, 68)[2]
print(f"CAVEAT: best-domain lower bound {blo:.2f}% vs worst-domain upper bound "
      f"{whi:.2f}% -> intervals "
      f"{'OVERLAP' if blo <= whi else 'do not overlap'}.")
print("        With overlapping Wilson CIs (n=24 vs n=68), the ~7x ranking is a point-")
print("        estimate, not a significant one: +-1 PASS in pnr_signoff moves it "
      f"to {wilson(6, 25)[0]:.1f}% / {wilson(4, 23)[0]:.1f}%.")
# Exact conditional test substitute: Fisher-style two-proportion z (report only).
n1, k1, n2, k2 = 24, 5, 68, 2
p1, p2 = k1 / n1, k2 / n2
pp = (k1 + k2) / (n1 + n2)
se = sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
z = (p1 - p2) / se
print(f"        two-proportion z = {z:.2f}  (two-sided p = "
      f"{erfc(abs(z) / sqrt(2)):.4f}); CIs overlap is the conservative view ->")
print("        report the intervals, and phrase the gap as descriptive, not significant.")
print()

print("=" * 78)
print("SECTION D  Sec.5 grounding-depth bins vs table values")
print("=" * 78)
bins = [
    ("Depth 1--2", ["pnr_signoff", "characterization", "eda_other"], "14--21"),
    ("Depth 3--5", ["pg_layout", "schematic_netlist", "digital", "layout_virtuoso",
                    "analog_context", "verification", "spice_sim"], "8--14"),
    ("Depth 6+",   ["waveform", "physical_verify", "layout_aether"], "3--5"),
]
for label, ds, claimed in bins:
    vals = [d[x] for x in ds]
    k = sum(next(z[1] for z in DOMAINS if z[0] == x) for x in ds)
    n = sum(next(z[1] + z[2] for z in DOMAINS if z[0] == x) for x in ds)
    print(f"{label:11s} paper says {claimed:6s}% | actual min={min(vals):.2f}% "
          f"max={max(vals):.2f}% | unweighted mean={sum(vals) / len(vals):.2f}% "
          f"| case-pooled={100 * k / n:.2f}% ({k}/{n})")
print()

print("=" * 78)
print("SECTION E  Sec.5 threats-to-validity percentages (which denominator?)")
print("=" * 78)
top3_696 = sum(next(z[1] + z[2] + z[3] + z[4] for z in DOMAINS if z[0] == x)
               for x in ("schematic_netlist", "spice_sim", "physical_verify"))
dv_696 = sum(next(z[1] + z[2] + z[3] + z[4] for z in DOMAINS if z[0] == x)
             for x in ("digital", "verification"))
# corpus-level counts hardcoded in sections/2_benchmark.tex l.65-71 & make_figs.py l.48-62
CORPUS = {"spice_sim": 177, "schematic_netlist": 166, "physical_verify": 106,
          "layout_aether": 66, "analog_context": 63, "digital": 59,
          "layout_virtuoso": 57, "verification": 55, "waveform": 54,
          "eda_other": 53, "characterization": 43, "pg_layout": 38, "pnr_signoff": 27}
cs = sum(CORPUS.values())
print(f"corpus counts in Sec.2 / make_figs.py sum to {cs} (\\Ntasks is 1007)")
print(f"  top-3 by corpus size = {100 * (177 + 166 + 106) / cs:.1f}% of {cs}, "
      f"or {100 * (177 + 166 + 106) / 1007:.1f}% of 1007")
print(f"  paper says 'top 3 domains = 44%' -> matches the evaluated 696 run: "
      f"{100 * top3_696 / 696:.1f}% ({top3_696}/696)")
print(f"  'digital+verification = 13%' -> evaluated {100 * dv_696 / 696:.1f}% "
      f"({dv_696}/696); corpus {100 * (59 + 55) / cs:.1f}% of {cs}")
print()

print("=" * 78)
print("SECTION F  Footnote-ready intervals")
print("=" * 78)
for k, n in [(62, 620), (62, 626), (62, 696)]:
    p, lo, hi = wilson(k, n)
    print(f"{k}/{n} = {p:.2f}%   Wilson 95% CI [{lo:.1f}, {hi:.1f}]")
print()

print("=" * 78)
print("SECTION G  Outcome mix over all 696 runs (for the 'error rate' footnote)")
print("=" * 78)
for lab, v in [("PASS", P), ("FAIL", F), ("ERROR", E), ("ABSENT", A)]:
    print(f"  {lab:<7}{v:>4}  {100 * v / N_TOTAL:6.2f}% of 696   {100 * v / (P + F):6.2f}% of 620")
print(f"  decided fraction = {(P + F) / N_TOTAL * 100:.2f}% of 696")

