#!/usr/bin/env python3
"""Prepare netlist from an ERC CSV, filtered by section.

Derived from real trace ukkn7 (desensitized). The original file used Windows
CRLF line endings; this file preserves them — handle "\r\n" carefully when
editing line-by-line (naive str.split("\n") leaves trailing "\r" on values).

KNOWN DEFECT (must fix):
    filter_erc_by_section only supports MAIN section numbers (e.g. "2"), NOT
    sub-sections (e.g. "2.1"). Passing --erc-section "2.1,2.2,...,2.8" is
    silently collapsed to main number {"2"} and swallows ALL 2.x rows
    (2.1..2.9), instead of matching exactly 2.1..2.8.

FIXME: make --erc-section support sub-section filtering so that
       "2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8" matches exactly those sub-sections,
       excluding 2.9 / 3.x / 5.x.
"""
import argparse
import csv
import json
import os
import sys


def filter_erc_by_section(csv_path, section_arg):
    """Filter ERC CSV rows by section.

    Current (BUGGY) behaviour: section_arg is comma-separated; only the MAIN
    section number (the token before the first '.') is used for matching.
    Thus "2.1,2.2" -> {"2"} -> matches 2.1..2.9 indiscriminately.
    """
    main_set = set()
    for tok in str(section_arg).split(","):
        tok = tok.strip()
        if not tok:
            continue
        main_set.add(tok.split(".")[0])  # BUG: drops the sub-section part
    out = []
    # NOTE: original file is CRLF; open with newline="" so csv handles \r.
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            sec = row.get("section", "")
            if sec.split(".")[0] in main_set:  # BUG: main-only match
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
