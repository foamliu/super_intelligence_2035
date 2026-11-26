#!/usr/bin/env python3
"""Generate a Design Compiler ``set_dont_use`` policy script from a Liberty
(.lib) library and a cell allowlist.

Strategy (disable-all-then-enable-allowed):

1.  Parse the library name from the ``library (NAME)`` header of the .lib file
    (never hardcoded).
2.  Collect every ``cell (NAME)`` declared in the library.
3.  Read the allowlist (one cell short name per line; blank lines and ``#``
    comment lines are skipped).  Each entry is uppercased and matched against
    the library cell names case-insensitively/exactly.
4.  Emit ``set_dont_use`` that disables the whole library first, then re-enables
    exactly the allowlisted cells that actually exist in the library.

Pure Python standard library only - no third-party dependencies.
"""

import argparse
import re
import sys

# Liberty ``library (...)`` header and ``cell (...)`` declarations are simple
# enough to parse with a line-oriented regex.  ``[^\\s()]+`` captures the name
# (no whitespace or parentheses), which matches the synthetic libs used here.
LIBRARY_RE = re.compile(r"\blibrary\s*\(\s*([^\s()]+)\s*\)", re.IGNORECASE)
CELL_RE = re.compile(r"\bcell\s*\(\s*([^\s()]+)\s*\)", re.IGNORECASE)

# Strip standard Liberty ``/* ... */`` block comments before matching so a
# commented-out header/cell line cannot fool the parser.
COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


def parse_lib_name(lib_text):
    """Return the library name declared in the ``library (NAME)`` header."""
    stripped = COMMENT_RE.sub("", lib_text)
    match = LIBRARY_RE.search(stripped)
    if match is None:
        raise ValueError("could not find a `library (NAME)` header in the .lib file")
    return match.group(1)


def parse_cells(lib_text):
    """Return all ``cell (NAME)`` names in declaration order."""
    stripped = COMMENT_RE.sub("", lib_text)
    return CELL_RE.findall(stripped)


def read_allowlist(path):
    """Read allowlist entries, skipping blank lines and ``#`` comment lines."""
    entries = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            entries.append(line)
    return entries


def render_tcl(lib_name, enabled_cells):
    """Render the DC ``set_dont_use`` policy tcl script."""
    lines = ['set LIB_NAME "%s"' % lib_name]
    lines.append('set_dont_use [get_lib_cells "${LIB_NAME}/*"] true')
    for cell in enabled_cells:
        lines.append('set_dont_use [get_lib_cells "${LIB_NAME}/%s"] false' % cell)
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate a DC set_dont_use policy tcl from a Liberty lib + allowlist."
    )
    parser.add_argument("--lib", required=True, help="input Liberty (.lib) file path")
    parser.add_argument(
        "--allow", required=True, help="allowlist file (one cell short name per line)"
    )
    parser.add_argument(
        "-o", "--output", required=True, help="output tcl file path"
    )
    args = parser.parse_args(argv)

    with open(args.lib, "r", encoding="utf-8") as fh:
        lib_text = fh.read()

    lib_name = parse_lib_name(lib_text)
    cells = parse_cells(lib_text)

    # Case-insensitive exact match: uppercase every cell name once.
    upper_cells = set(c.upper() for c in cells)

    allow_entries = read_allowlist(args.allow)

    enabled = []
    seen = set()
    for entry in allow_entries:
        key = entry.upper()
        if key in upper_cells and key not in seen:
            seen.add(key)
            enabled.append(key)

    tcl = render_tcl(lib_name, enabled)

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(tcl)

    return 0


if __name__ == "__main__":
    sys.exit(main())