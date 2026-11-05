#!/usr/bin/env python3
"""
extract_subckt.py

Streaming extractor + one-level parser for a single .SUBCKT definition inside a
large SPICE (hspice / ALPS style) netlist.

Usage:
    python3 extract_subckt.py --netlist NETLIST.sp --cell CELL --out REPORT.json
                              [--extract OUT.sp]

* The netlist is read line-by-line (streaming); never loaded with one read().
* '+' continuation lines are joined back onto the card they extend before parsing.
* Only 'X'/'XI' instance cards are reported; primitive devices are ignored.
* Fully parameterised by --cell; no cell/port/net names are hard-coded.

Pure Python standard library only; ASCII only; no EDA tools invoked.
"""

import argparse
import json
import sys


def continuation_joined(lines):
    """Join one card and its '+' continuation lines into a single string."""
    parts = []
    for idx, line in enumerate(lines):
        s = line.rstrip("\r\n").strip()
        if idx > 0 and s.startswith("+"):
            s = s[1:].strip()
        if s:
            parts.append(s)
    return " ".join(parts)


def build_logical_cards(section_lines):
    """Turn raw section lines into logical cards, merging '+' continuation
    lines into the preceding card.  Returns a list of card strings."""
    cards = []
    i = 0
    n = len(section_lines)
    while i < n:
        group = [section_lines[i]]
        j = i + 1
        while j < n and section_lines[j].lstrip().startswith("+"):
            group.append(section_lines[j])
            j += 1
        cards.append(continuation_joined(group))
        i = j
    return cards


def parse_section(section_lines):
    """Parse the extracted .SUBCKT body into (ports, subcells)."""
    ports = []
    seen_ports = set()
    subcells = []
    for card in build_logical_cards(section_lines):
        tokens = card.split()
        if not tokens:
            continue
        low = tokens[0].lower()
        if low == ".subckt":
            for p in tokens[2:]:
                if p not in seen_ports:
                    seen_ports.add(p)
                    ports.append(p)
        elif low.startswith("x"):
            subcells.append({
                "inst": tokens[0],
                "cell": tokens[-1],
                "pins": tokens[1:-1],
            })
    return ports, subcells


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Streamingly extract and parse a single .SUBCKT definition")
    parser.add_argument("--netlist", required=True,
                        help="input SPICE netlist (may be very large)")
    parser.add_argument("--cell", required=True,
                        help="target .SUBCKT cell name (case-insensitive)")
    parser.add_argument("--out", required=True,
                        help="path for the JSON report")
    parser.add_argument("--extract", default=None,
                        help="optional path to dump the .SUBCKT ... .ENDS text")
    args = parser.parse_args(argv)

    target = args.cell.strip()
    target_low = target.lower()

    start_line = None
    end_line = None
    last_idx = None
    cell_actual = target
    section = []

    with open(args.netlist, "r", buffering=1 << 20, newline="") as f:
        in_target = False
        for idx, raw in enumerate(f, 1):
            stripped = raw.lstrip()
            low = stripped.lower()
            if not in_target:
                if low.startswith(".subckt"):
                    tokens = stripped.split()
                    if len(tokens) >= 2 and tokens[1].lower() == target_low:
                        in_target = True
                        start_line = idx
                        cell_actual = tokens[1]
                        section.append(raw)
                        last_idx = idx
                continue
            last_idx = idx
            if low.startswith(".ends"):
                end_line = idx
                section.append(raw)
                break
            section.append(raw)

    if start_line is None:
        report = {"subckt": target, "found": False}
        with open(args.out, "w") as out:
            json.dump(report, out, indent=2)
            out.write("\n")
        return 1

    if end_line is None:
        end_line = last_idx if last_idx is not None else start_line

    ports, subcells = parse_section(section)

    subcell_types = sorted({sc["cell"] for sc in subcells})

    net_set = set(ports)
    for sc in subcells:
        net_set.update(sc["pins"])
    nets = sorted(net_set)

    report = {
        "subckt": cell_actual,
        "found": True,
        "ports": ports,
        "subcells": subcells,
        "subcell_types": subcell_types,
        "nets": nets,
        "line_range": [start_line, end_line],
        "line_count": end_line - start_line + 1,
    }

    with open(args.out, "w") as out:
        json.dump(report, out, indent=2)
        out.write("\n")

    if args.extract:
        with open(args.extract, "w", newline="") as ex:
            ex.write("".join(section))

    return 0


if __name__ == "__main__":
    sys.exit(main())