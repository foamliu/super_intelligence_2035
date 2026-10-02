#!/usr/bin/env python
"""Plot the R9 scaling-law curve: IN-1k linear-probe top-1 (and zs) vs
cumulative samples, log-x. Pure CPU, no GPU. Reads the CSV written by
`r9_scaling.py` (default /tmp/r9_scaling_points.csv), re-fits the stage-2
points with the same two models (power law + log-linear), and saves a PNG.

Usage:
  python r9_plot_scaling.py [--csv /tmp/r9_scaling_points.csv] [--png /tmp/r9_scaling_curve.png]
"""
import argparse
import csv
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.stats import linregress


def _powerlaw(N, a, b, c):
    return a - b * np.power(N.astype(float), -c)


def fit_powerlaw(N, acc):
    N = N.astype(float)
    a0 = max(acc) * 1.2 + 1e-3
    p0 = [a0, max((a0 - min(acc)), 0.1) * 0.5, 0.3]
    bounds = ([max(acc) * 0.95, 0.0, 1e-3], [1.0, 1e3, 5.0])
    try:
        popt, _ = curve_fit(_powerlaw, N, acc, p0=p0, bounds=bounds, maxfev=40000)
    except Exception:
        return None
    pred = _powerlaw(N, *popt)
    ss_res = float(np.sum((acc - pred) ** 2))
    ss_tot = float(np.sum((acc - np.mean(acc)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {"a": popt[0], "b": popt[1], "c": popt[2], "r2": r2}


def fit_loglinear(N, acc):
    lg = np.log10(N.astype(float))
    res = linregress(lg, acc)
    pred = res.intercept + res.slope * lg
    ss_res = float(np.sum((acc - pred) ** 2))
    ss_tot = float(np.sum((acc - np.mean(acc)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return {"a": res.intercept, "b": res.slope, "r2": r2}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="/tmp/r9_scaling_points.csv")
    ap.add_argument("--png", default="/tmp/r9_scaling_curve.png")
    args = ap.parse_args()

    pts = []
    with open(args.csv) as fh:
        for r in csv.DictReader(fh):
            r["samples"] = float(r["samples"])
            r["zs1"] = float(r["zs1"])
            r["zs5"] = float(r["zs5"])
            r["lp"] = float(r["lp"])
            pts.append(r)

    s2 = sorted([p for p in pts if p["tag"] == "stage2"], key=lambda x: x["samples"])
    s1 = [p for p in pts if p["tag"] == "stage1"]

    fig, ax = plt.subplots(figsize=(9, 6))

    # stage-2 long curve (w512)
    if s2:
        N2 = np.array([p["samples"] for p in s2])
        lp2 = np.array([p["lp"] for p in s2])
        zs2 = np.array([p["zs1"] for p in s2])
        ax.plot(N2 / 1e6, lp2 * 100, "o-", color="#1f77b4", label="stage2 w512 lp top-1")
        ax.plot(N2 / 1e6, zs2 * 100, "s--", color="#1f77b4", alpha=0.55,
                label="stage2 w512 zs top-1")
        # fits over a dense grid
        grid = np.logspace(np.log10(N2.min()), np.log10(N2.max()), 200)
        pw = fit_powerlaw(N2, lp2)
        if pw is not None:
            ax.plot(grid / 1e6, _powerlaw(grid, pw["a"], pw["b"], pw["c"]) * 100,
                    "-", color="red", lw=1.4,
                    label=f"power-law fit (R2={pw['r2']:.3f}, a={pw['a']*100:.1f}%)")
        ll = fit_loglinear(N2, lp2)
        if ll is not None:
            ax.plot(grid / 1e6, (ll["a"] + ll["b"] * np.log10(grid)) * 100,
                    "--", color="green", lw=1.4,
                    label=f"log-linear fit (R2={ll['r2']:.3f})")

    # stage-1 width sweep (3 points at 30k steps)
    for p in sorted(s1, key=lambda x: x["width"]):
        w = p["width"]
        ax.plot(p["samples"] / 1e6, p["lp"] * 100, "^", markersize=10,
                markeredgecolor="black", color="#ff7f0e")
        ax.annotate(f"w{w}", (p["samples"] / 1e6, p["lp"] * 100),
                    textcoords="offset points", xytext=(8, -2))

    ax.set_xscale("log")
    ax.set_xlabel("cumulative samples (M, log scale; bs64 x 8 ranks = 512/step)")
    ax.set_ylabel("ImageNet-1k top-1 (%)  [frozen trunk]")
    ax.set_title("R9 scaling law: IN-1k linear-probe top-1 vs cumulative samples")
    ax.grid(True, which="both", alpha=0.3)
    ax.axvline(53.0, color="gray", linestyle=":", lw=1.2, label="local ceiling ~53M pairs")
    ax.legend(fontsize=8, loc="best")
    fig.tight_layout()
    fig.savefig(args.png, dpi=110)
    print(f"[saved] {args.png}")


if __name__ == "__main__":
    main()