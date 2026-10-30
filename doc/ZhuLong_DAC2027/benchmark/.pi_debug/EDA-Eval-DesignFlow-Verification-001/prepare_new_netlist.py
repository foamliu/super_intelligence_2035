#!/usr/bin/env python3
"""Prepare netlist from an ERC CSV, filtered by section.

Derived from real trace ukkn7 (desensitized). The original file used Windows
CRLF line endings; this file preserves them — handle "\r\n" carefully when
editing line-by-line (naive str.split("\n") leaves trailing "\r" on values).

KNOWN DEFECT (FIXED):
    filter_erc_by_section now matches EXACT section tokens, including
    sub-sections. Passing --erc-section "2.1,2.2,...,2.8" matches
    exactly those sub-sections (2.1..2.8), excluding 2.9 / 3.x / 5.x.
    This file keeps CRLF line endings; the CSV is opened with newline=""
    so the csv module strips the trailing "\r" from field values.
"""
import argparse
import csv
import json
import os
import sys


def filter_erc_by_section(csv_path, section_arg):
    """Filter ERC CSV rows by exact section (including sub-sections).

    section_arg is comma-separated; each token is matched verbatim, so
    "2.1,2.2,...,2.8" matches exactly those sub-sections (2.1..2.8),
    excluding 2.9 / 3.x / 5.x.
    """
    section_set = set()
    for tok in str(section_arg).split(","):
        tok = tok.strip()
        if not tok:
            continue
        section_set.add(tok)  # keep the full sub-section token
    out = []
    # NOTE: original file is CRLF; open with newline="" so csv handles \r.
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            sec = (row.get("section") or "").strip()
            if sec in section_set:  # exact sub-section match
                out.append(row)
    return out


def write_report(rows, out_path):
    if not rows:
        fieldnames = ["section", "severity", "rule_id", "message", "cell"]
    else:
        fieldnames = list(rows[0].keys())
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--erc-section", required=True,
                    help='comma-separated sections, e.g. "2.1,2.2,...,2.8"')
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rows = filter_erc_by_section(args.csv, args.erc_section)
    write_report(rows, args.out)
    print(f"[prepare_new_netlist] {len(rows)} rows -> {args.out}")
    # also emit a project_config.json for downstream steps
    cfg = {
        "csv": os.path.abspath(args.csv),
        "erc_section": args.erc_section,
        "out": os.path.abspath(args.out),
        "row_count": len(rows),
    }
    with open("project_config.json", "w") as f:
        json.dump(cfg, f, indent=2)


if __name__ == "__main__":
    main()
