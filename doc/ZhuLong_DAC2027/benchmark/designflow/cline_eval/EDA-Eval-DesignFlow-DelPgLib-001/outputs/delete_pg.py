#!/usr/bin/env python3
"""Generate a cleaned Liberty (.lib) file with the power/ground (VDD/VSS)
information removed.

Usage:
    python3 delete_pg.py <input.lib> <output.lib>

The script applies the following three rules, in order:

1. Delete the whole block that starts with ``pg_pin (VDD) {`` and ends with
   its matching closing brace ``}`` (brace depth is tracked so any nested
   braces are handled correctly).
2. Delete the whole block that starts with ``pg_pin (VSS) {`` and ends with
   its matching closing brace ``}``.
3. Delete every remaining line that contains the substring ``VDD`` or ``VSS``.

This script uses only the Python standard library (no third-party packages).
"""

import re
import sys

# Matches a line whose first non-whitespace text opens a ``pg_pin`` block for
# either VDD or VSS, e.g.:
#     pg_pin (VDD) {
#     pg_pin(VSS){
# Whitespace between the tokens is permitted.
_PG_PIN_START_RE = re.compile(r"^\s*pg_pin\s*\(\s*(VDD|VSS)\s*\)\s*\{")


def _brace_delta(line):
    """Return the net change in brace balance contributed by ``line``."""
    return line.count("{") - line.count("}")


def clean_lines(lines):
    """Return a new list of lines with the pg_pin(VDD/VSS) blocks and any
    VDD/VSS-containing lines removed."""
    result = []
    index = 0
    total = len(lines)
    block_depth = 0

    while index < total:
        line = lines[index]

        if block_depth > 0:
            # Inside a pg_pin block: consume lines until the brace balance
            # returns to zero (the block's closing brace).
            block_depth += _brace_delta(line)
            index += 1
            continue

        if _PG_PIN_START_RE.match(line):
            # Opening line of a pg_pin(VDD/VSS) block: drop the entire block,
            # tracking brace depth until the matching closing brace.
            block_depth = _brace_delta(line)
            index += 1
            continue

        # Rule 3: drop any still-remaining line that mentions VDD or VSS.
        if "VDD" in line or "VSS" in line:
            index += 1
            continue

        result.append(line)
        index += 1

    return result


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("Usage: python3 delete_pg.py <input.lib> <output.lib>\n")
        return 2

    input_path = argv[1]
    output_path = argv[2]

    with open(input_path, "r") as handle:
        lines = handle.readlines()

    cleaned = clean_lines(lines)

    with open(output_path, "w") as handle:
        handle.writelines(cleaned)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))