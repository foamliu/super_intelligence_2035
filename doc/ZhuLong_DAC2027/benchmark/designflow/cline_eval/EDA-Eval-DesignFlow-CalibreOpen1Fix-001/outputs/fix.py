#!/usr/bin/env python3
"""fix.py -- inject LAYOUT PRECISION into a Calibre DRC rule file.

Usage:
    python3 fix.py <rule_file> <config_file> <output_rule_file>

Reads `precision` from the config file and ensures the rule file carries a
matching `LAYOUT PRECISION <value>` statement:

    * if a LAYOUT PRECISION line already exists, its value is replaced;
    * if it is missing, a new line is inserted right after the
      LAYOUT system line.

All other LAYOUT statements (and every other line) are preserved verbatim.
Exits 0 on success, non-zero on failure.
"""

import re
import sys


def load_config(path):
    """Parse `key = value` lines, skipping blanks/comments/malformed lines."""
    cfg = {}
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            cfg[key.strip()] = value.strip()
    return cfg


PRECISION_RE = re.compile(r"^\s*LAYOUT\s+PRECISION\b", re.IGNORECASE)
SYSTEM_RE = re.compile(r"^\s*LAYOUT\s+system\b", re.IGNORECASE)


def fix_rule(rule_path, config_path, output_path):
    cfg = load_config(config_path)
    precision = cfg.get("precision")
    if precision is None:
        sys.stderr.write(
            "ERROR: 'precision' not found in config file: {}\n".format(config_path)
        )
        return 1

    new_line = "LAYOUT PRECISION " + precision

    with open(rule_path) as fh:
        lines = fh.readlines()

    # Case A: a LAYOUT PRECISION line already exists -> replace its value.
    precision_indices = [i for i, line in enumerate(lines) if PRECISION_RE.match(line)]
    if precision_indices:
        for idx in precision_indices:
            lines[idx] = new_line + "\n"
    else:
        # Case B: missing -> insert right after the LAYOUT system line.
        inserted = False
        for i, line in enumerate(lines):
            if SYSTEM_RE.match(line):
                lines.insert(i + 1, new_line + "\n")
                inserted = True
                break
        if not inserted:
            # No LAYOUT system line found; append at end as a safe fallback.
            lines.append(new_line + "\n")

    with open(output_path, "w") as fh:
        fh.writelines(lines)

    return 0


def main(argv):
    if len(argv) != 4:
        sys.stderr.write(
            "usage: python3 fix.py <rule_file> <config_file> <output_rule_file>\n"
        )
        return 2
    rule_file, config_file, output_file = argv[1], argv[2], argv[3]
    return fix_rule(rule_file, config_file, output_file)


if __name__ == "__main__":
    sys.exit(main(sys.argv))