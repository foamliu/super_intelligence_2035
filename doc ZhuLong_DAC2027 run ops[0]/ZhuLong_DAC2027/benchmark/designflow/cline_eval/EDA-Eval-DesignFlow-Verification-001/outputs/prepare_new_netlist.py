#!/usr/bin/env python3
"""Prepare netlist from an ERC CSV, filtered by section.

Derived from real trace ukkn7 (desensitized). The original file used Windows
CRLF line endings; this file preserves them - handle the trailing carriage
return carefully when editing line-by-line (a naive line split leaves a stray
carriage return on field values and can break the section comparison). The CSV
is therefore opened with newline="" so the csv module strips those carriage
returns for us.

Defect fixed: filter_erc_by_section previously collapsed every token to its
MAIN section number (so "2.1,2.2,...,2.8" was reduced to {"2"} and matched
2.1..2.9 indiscriminately). It now does exact sub-section matching, so
"2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8" matches exactly those sub-sections and
excludes 2.9 / 3.x / 5.x. A bare main-section token (e.g. "2") still matches
that section and all of its sub-sections, preserving the old main-only
behaviour.
"""
import argparse
import csv
import json
import os
import sys


def filter_erc_by_section(csv_path, section_arg):
    """Filter ERC CSV rows by section (exact sub-section match).

    section_arg is a comma-separated list of section tokens. Each token is
    compared against the row's "section" field:
      * exact token match -- "2.1" matches only section "2.1";
      * bare main-section token -- "2" matches "2" and every "2.x".

    Thus "2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8" matches exactly 2.1..2.8 and
    excludes 2.9 / 3.x / 5.x.
    """
    want = set()
    for tok in str(section_arg).split(","):
        tok = tok.strip()
        if not tok:
            continue
        want.add(tok)

    def matches(sec):
        sec = (sec or "").strip()
        if sec in want:
            return True
        # bare main-section fallback: "2" matches "2", "2.1", "2.2", ...
        return sec.split(".")[0] in want

    out = []
    # Source CSV is CRLF; newline="" lets the csv module strip the trailing
    # carriage return instead of us having to split lines manually.
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            if matches(row.get("section", "")):
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