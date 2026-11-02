#!/usr/bin/env python3
"""analyze_errors_v1.py — stub error analyzer (kept minimal; do not break step2)."""
import argparse, csv, sys


def analyze(report_path):
    n = 0
    with open(report_path, newline="") as f:
        for row in csv.DictReader(f):
            n += 1
    print(f"[analyze_errors_v1] {n} ERC rows in {report_path}")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True)
    args = ap.parse_args()
    analyze(args.report)


if __name__ == "__main__":
    main()
