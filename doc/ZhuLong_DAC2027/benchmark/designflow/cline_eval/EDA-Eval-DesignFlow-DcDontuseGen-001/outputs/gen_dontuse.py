#!/usr/bin/env python3
"""Generate a Synopsys Design Compiler ``set_dont_use`` policy script.

Strategy: disable-all-then-enable-allowed.

  1. Parse the ``library (...)`` header from a Liberty (.lib) file to obtain
     LIB_NAME (never hard-coded).
  2. Parse every ``cell (...)`` defined in the library to build the ordered,
     complete cell list.
  3. Read an allow-list file (one cell short-name per line; blank lines and
     ``#`` comment lines are ignored).
  4. Emit a Tcl script that:
       * defines ``LIB_NAME``,
       * disables every cell in the library, and
       * re-enables exactly the cells whose names match an allow-list entry
         (case-insensitive exact match).  Allow-list entries that match no
         cell are skipped silently; library cells absent from the allow-list
         stay disabled.

CLI:
    python3 gen_dontuse.py --lib <path.lib> --allow <allow.txt> -o <out.tcl>

Pure Python standard library; no third-party dependencies.
"""

import argparse
import re
import sys

LIB_HEADER_RE = re.compile(r"\blibrary\s*\(\s*([^)\s]+)\s*\)")
CELL_RE = re.compile(r"\bcell\s*\(\s*([^)\s]+)\s*\)")
BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
LINE_COMMENT_RE = re.compile(r"//[^\n]*")


def strip_comments(text):
    """Best-effort removal of Liberty comments (does not touch string content
    of pin functions because those live inside double quotes that carry no
    comment markers in typical liberty files)."""
    text = BLOCK_COMMENT_RE.sub("", text)
    text = LINE_COMMENT_RE.sub("", text)
    return text


def parse_lib_name(text):
    """Return the library name from a Liberty file, or None if not found."""
    match = LIB_HEADER_RE.search(text)
    if match is None:
        return None
    return match.group(1)


def parse_cells(text):
    """Return the ordered list of cell names defined in a Liberty file."""
    return CELL_RE.findall(text)


def normalize_allow(name):
    """Normalize an allow-list token to the case used by the library."""
    return name.strip().upper()


def read_allow_list(path):
    """Read allow-list entries, skipping blank lines and ``#`` comment lines."""
    allowed = []
    with open(path, "r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            # Keep only the first whitespace-delimited token (drops trailing
            # inline comments or accidental extra fields).
            token = line.split()[0]
            allowed.append(normalize_allow(token))
    return allowed


def generate_tcl(lib_name, cells, allowed):
    """Return the dont_use Tcl script text.

    cells:    ordered cell names as parsed from the library.
    allowed:  upper-cased allow-list entries.
    """
    allowed_set = set(allowed)
    matched = [cell for cell in cells if cell.upper() in allowed_set]

    lines = []
    lines.append('set LIB_NAME "%s"' % lib_name)
    lines.append('set_dont_use [get_lib_cells "${LIB_NAME}/*"] true')
    for cell in matched:
        lines.append('set_dont_use [get_lib_cells "${LIB_NAME}/%s"] false' % cell)
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate a DC set_dont_use policy script from a Liberty "
                    "library and an allow-list of cell names."
    )
    parser.add_argument("--lib", required=True,
                        help="Path to the input Liberty (.lib) file.")
    parser.add_argument("--allow", required=True,
                        help="Path to the allow-list file (one cell short-name "
                             "per line).")
    parser.add_argument("-o", "--output", required=True,
                        help="Path to the output Tcl script.")
    args = parser.parse_args(argv)

    with open(args.lib, "r", encoding="utf-8") as handle:
        lib_text = handle.read()

    lib_text = strip_comments(lib_text)

    lib_name = parse_lib_name(lib_text)
    if lib_name is None:
        print("error: could not parse library (...) name from %s" % args.lib,
              file=sys.stderr)
        return 1

    cells = parse_cells(lib_text)
    if not cells:
        print("error: no cell (...) definitions found in %s" % args.lib,
              file=sys.stderr)
        return 1

    allowed = read_allow_list(args.allow)

    tcl = generate_tcl(lib_name, cells, allowed)

    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(tcl)

    return 0


if __name__ == "__main__":
    sys.exit(main())