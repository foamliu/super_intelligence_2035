#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rcmax_compare.py

Recursively compare two StarRC RCMAX plaintext data trees.

Usage:
    python3 rcmax_compare.py <rootA> <rootB> <out_report.txt>

Behaviour
---------
* Recursively walks ``rootA`` and ``rootB`` and collects the relative path of
  every file (paths are normalised to POSIX ``/`` separators).
* For every file present in both trees, performs a *byte-level* comparison
  (size + SHA-256). Files whose bytes are identical are reported as IDENTICAL.
* For every byte-different file, performs a *line-by-line* comparison and
  counts the differing lines (added / removed / changed). A short unified-diff
  preview is included in the report.
* Files present only under ``rootA`` or only under ``rootB`` are reported
  separately (missing files / added files).
* A structured report is written to ``<out_report.txt>`` and a human readable
  summary is printed to stdout.

The tool has no third-party dependencies and works with Python 3.6+.
"""

import sys
import os
import hashlib
import difflib
from datetime import datetime

__version__ = "1.0.0"

PREVIEW_LIMIT = 200


def _walk_files(root):
    """Return an ordered mapping of relative-path (posix) -> absolute path."""
    result = {}
    for dirpath, dirnames, filenames in os.walk(root):
        # Deterministic traversal order.
        dirnames.sort()
        filenames.sort()
        for fn in filenames:
            abspath = os.path.join(dirpath, fn)
            relpath = os.path.relpath(abspath, root).replace(os.sep, "/")
            result[relpath] = abspath
    return result


def _read_bytes(path):
    """Read a file by streaming, returning (size, sha256_hex)."""
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
            size += len(chunk)
    return size, h.hexdigest()


def _is_binary(raw):
    """Heuristic binary detection: a NUL byte => binary content."""
    return b"\x00" in raw


def _count_line_diffs(path_a, path_b):
    """
    Line-by-line comparison between two files.

    Returns a dict describing the difference.
    """
    with open(path_a, "rb") as f:
        raw_a = f.read()
    with open(path_b, "rb") as f:
        raw_b = f.read()

    lines_a = raw_a.splitlines()
    lines_b = raw_b.splitlines()

    binary_a = _is_binary(raw_a)
    binary_b = _is_binary(raw_b)

    # Lossy decode for display only; this never raises.
    a_txt = [ln.decode("utf-8", "replace") for ln in lines_a]
    b_txt = [ln.decode("utf-8", "replace") for ln in lines_b]

    sm = difflib.SequenceMatcher(None, a_txt, b_txt, autojunk=False)
    lines_added = 0
    lines_removed = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        lines_removed += (i2 - i1)
        lines_added += (j2 - j1)

    preview = []
    if not binary_a and not binary_b:
        try:
            diff = difflib.unified_diff(
                a_txt,
                b_txt,
                fromfile=os.path.basename(path_a) + " (A)",
                tofile=os.path.basename(path_b) + " (B)",
                lineterm="",
            )
            for line in diff:
                preview.append(line)
                if len(preview) >= PREVIEW_LIMIT:
                    preview.append("... (diff preview truncated)")
                    break
        except Exception:
            preview = []

    return {
        "lines_a": len(lines_a),
        "lines_b": len(lines_b),
        "lines_added": lines_added,
        "lines_removed": lines_removed,
        "lines_changed": lines_added + lines_removed,
        "binary_a": binary_a,
        "binary_b": binary_b,
        "preview": preview,
    }


def _build_report(root_a, root_b, files_a, files_b, common, only_a, only_b,
                  identical, different):
    """Build the structured report as a list of text lines."""
    out = []
    w = out.append

    w("=" * 80)
    w("RCMAX TREE COMPARISON REPORT")
    w("=" * 80)
    w("generated          : {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    w("rcmax_compare ver  : {}".format(__version__))
    w("root_a             : {}".format(root_a))
    w("root_b             : {}".format(root_b))
    w("")

    total_changed = sum(item["lines_changed"] for item in different)

    w("[SUMMARY]")
    w("files_in_a          = {}".format(len(files_a)))
    w("files_in_b          = {}".format(len(files_b)))
    w("files_common        = {}".format(len(common)))
    w("files_identical     = {}".format(len(identical)))
    w("files_different     = {}".format(len(different)))
    w("files_only_in_a     = {}".format(len(only_a)))
    w("files_only_in_b     = {}".format(len(only_b)))
    w("total_lines_changed = {}".format(total_changed))
    w("")

    w("[FILES ONLY IN A]  (present in root_a but missing in root_b)")
    if only_a:
        for rel in only_a:
            w("  - {}".format(rel))
    else:
        w("  (none)")
    w("")

    w("[FILES ONLY IN B]  (present in root_b but missing in root_a)")
    if only_b:
        for rel in only_b:
            w("  - {}".format(rel))
    else:
        w("  (none)")
    w("")

    w("[IDENTICAL FILES]  (byte-level identical)")
    if identical:
        for rel in identical:
            w("  = {}".format(rel))
    else:
        w("  (none)")
    w("")

    w("[DIFFERENT FILES]  (byte-level different, line-by-line diff follows)")
    if not different:
        w("  (none)")
    else:
        for item in different:
            w("-" * 80)
            w("file            : {}".format(item["rel"]))
            w("  bytes_a       : {}".format(item["bytes_a"]))
            w("  bytes_b       : {}".format(item["bytes_b"]))
            w("  sha256_a      : {}".format(item["sha256_a"]))
            w("  sha256_b      : {}".format(item["sha256_b"]))
            w("  lines_a       : {}".format(item["lines_a"]))
            w("  lines_b       : {}".format(item["lines_b"]))
            w("  lines_added   : {}".format(item["lines_added"]))
            w("  lines_removed : {}".format(item["lines_removed"]))
            w("  lines_changed : {}".format(item["lines_changed"]))
            w("  binary_a      : {}".format(item["binary_a"]))
            w("  binary_b      : {}".format(item["binary_b"]))
            if item["preview"]:
                w("  diff_preview  :")
                for line in item["preview"]:
                    w("    | {}".format(line))
            else:
                w("  diff_preview  : (binary or unavailable)")
        w("-" * 80)

    w("")
    w("[END OF REPORT]")
    return out


def _print_summary(root_a, root_b, files_a, files_b, common, only_a, only_b,
                   identical, different):
    """Print a compact human readable summary to stdout."""
    total_changed = sum(item["lines_changed"] for item in different)
    print("RCMAX compare summary")
    print("  A = {}".format(root_a))
    print("  B = {}".format(root_b))
    print("  files_in_a={} files_in_b={} common={} identical={} different={} "
          "only_in_a={} only_in_b={} total_lines_changed={}".format(
              len(files_a), len(files_b), len(common), len(identical),
              len(different), len(only_a), len(only_b), total_changed))

    if different:
        print("  DIFFERENT files:")
        for item in different:
            print("    - {}  (lines_changed={}, added={}, removed={})".format(
                item["rel"], item["lines_changed"],
                item["lines_added"], item["lines_removed"]))

    if only_a:
        print("  ONLY IN A (missing in B):")
        for rel in only_a:
            print("    - {}".format(rel))

    if only_b:
        print("  ONLY IN B (extra in B):")
        for rel in only_b:
            print("    - {}".format(rel))

    if not different and not only_a and not only_b:
        print("  RESULT: the two trees are identical.")


def main(argv):
    if len(argv) != 4:
        print("usage: python3 rcmax_compare.py <rootA> <rootB> <out_report.txt>",
              file=sys.stderr)
        return 2

    root_a = argv[1]
    root_b = argv[2]
    out_path = argv[3]

    if not os.path.isdir(root_a):
        print("error: root_a is not a directory: {}".format(root_a),
              file=sys.stderr)
        return 2
    if not os.path.isdir(root_b):
        print("error: root_b is not a directory: {}".format(root_b),
              file=sys.stderr)
        return 2

    files_a = _walk_files(root_a)
    files_b = _walk_files(root_b)

    rel_a = set(files_a)
    rel_b = set(files_b)

    common = sorted(rel_a & rel_b)
    only_a = sorted(rel_a - rel_b)
    only_b = sorted(rel_b - rel_a)

    identical = []
    different = []

    for rel in common:
        pa = files_a[rel]
        pb = files_b[rel]
        size_a, sha_a = _read_bytes(pa)
        size_b, sha_b = _read_bytes(pb)
        if sha_a == sha_b:
            identical.append(rel)
        else:
            info = _count_line_diffs(pa, pb)
            info["rel"] = rel
            info["bytes_a"] = size_a
            info["bytes_b"] = size_b
            info["sha256_a"] = sha_a
            info["sha256_b"] = sha_b
            different.append(info)

    report = _build_report(root_a, root_b, files_a, files_b, common, only_a,
                           only_b, identical, different)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        f.write("\n")

    _print_summary(root_a, root_b, files_a, files_b, common, only_a, only_b,
                   identical, different)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))