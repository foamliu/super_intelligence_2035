#!/usr/bin/env python
"""Plot the ④ epoch-scaling curve: IN-1k linear-probe top-1 (ProtB) vs
training epochs (1ep → 2ep → [4ep if available]).

Pure CPU, no GPU. Generates a PNG with:
  - Data points (E1fair=1ep, ④-2ep, and optionally ④-4ep)
  - Pre-registered decision thresholds (62.34% baseline, 70% positive, 63.84% moderate)
  - Connecting line

Usage:
  python plot_lp_epoch_curve.py \
    --e1fair 62.34 --e1fair-err 0.01 \
    --e2ep <value> --e2ep-err <value> \
    [--e4ep <value> --e4ep-err <value>] \
    [--png /tmp/lp_epoch_curve.png]
"""
import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--e1fair", type=float, required=True, help="1ep ProtB lp (E1fair)")
    ap.add_argument("--e1fair-err", type=float, default=0.01)
    ap.add_argument("--e2ep", type=float, required=True, help="2ep ProtB lp (④-2ep)")
    ap.add_argument("--e2ep-err", type=float, default=0.01)
    ap.add_argument("--e4ep", type=float, default=None, help="4ep ProtB lp (④-4ep, if available)")
    ap.add_argument("--e4ep-err", type=float, default=0.01)
    ap.add_argument("--png", default="/tmp/lp_epoch_curve.png")
    args = ap.parse_args()

    epochs = [1, 2]
    lp = [args.e1fair, args.e2ep]
    err = [args.e1fair_err, args.e2ep_err]

    if args.e4ep is not None:
        epochs.append(4)
        lp.append(args.e4ep)
        err.append(args.e4ep_err)

    fig, ax = plt.subplots(figsize=(7, 5))

    # Pre-registered thresholds
    baseline = args.e1fair
    positive_thresh = 70.0
    moderate_thresh = 63.84  # baseline + 1.5pp
    ax.axhline(baseline, color="gray", ls="--", lw=0.8, alpha=0.7,
               label=f"Baseline (1ep) = {baseline:.2f}%")
    ax.axhline(moderate_thresh, color="orange", ls=":", lw=0.8, alpha=0.7,
               label=f"Moderate threshold = {moderate_thresh:.2f}%")
    ax.axhline(positive_thresh, color="green", ls=":", lw=0.8, alpha=0.7,
               label=f"Positive threshold = {positive_thresh:.0f}%")

    # Data points
    ax.errorbar(epochs, lp, yerr=err, fmt="o-", color="#2563eb", markersize=8,
                capsize=4, lw=2, label="ProtB lp top-1")

    # Annotate each point
    for ep, val, e in zip(epochs, lp, err):
        ax.annotate(f"{val:.2f}±{e:.2f}%", (ep, val), textcoords="offset points",
                    xytext=(8, 8), fontsize=9, color="#2563eb")

    ax.set_xlabel("Training epochs (over 95.8M pairs)", fontsize=12)
    ax.set_ylabel("IN-1k linear-probe top-1 (Protocol B)", fontsize=12)
    ax.set_title("④ Epoch Scaling: lp vs epochs (AIMv2-style, w512/d30/p16/224)", fontsize=11)
    ax.set_xticks(epochs)
    ax.set_ylim(min(lp) - 5, max(max(lp) + 5, positive_thresh + 3))
    ax.legend(fontsize=9, loc="lower right")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(args.png, dpi=150)
    print(f"Saved: {args.png}")

    # Print decision summary
    delta = args.e2ep - baseline
    print(f"\n=== Decision Summary ===")
    print(f"1ep (E1fair): {baseline:.2f}±{args.e1fair_err:.2f}%")
    print(f"2ep (④-2ep):  {args.e2ep:.2f}±{args.e2ep_err:.2f}%")
    print(f"Δlp (2ep-1ep): {delta:+.2f}pp")
    if args.e2ep >= positive_thresh:
        print(f"VERDICT: POSITIVE (≥70%) → Budget insufficient → Launch 4ep")
    elif args.e2ep > moderate_thresh:
        print(f"VERDICT: MODERATE (>63.84%) → Some gain, diminishing returns → Decision pending")
    else:
        print(f"VERDICT: FLAT (~63%) → Feature/objective quality ceiling → No 4ep needed")
    if args.e4ep is not None:
        delta4 = args.e4ep - baseline
        print(f"4ep (④-4ep):  {args.e4ep:.2f}±{args.e4ep_err:.2f}%")
        print(f"Δlp (4ep-1ep): {delta4:+.2f}pp")


if __name__ == "__main__":
    main()
