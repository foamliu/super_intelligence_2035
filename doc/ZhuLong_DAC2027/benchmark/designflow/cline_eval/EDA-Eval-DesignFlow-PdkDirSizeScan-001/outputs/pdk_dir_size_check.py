#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdk_dir_size_check.py

Scan the first-level sub-directories under a root directory, compute each
sub-directory's total size, keep only those *larger than* a given threshold
(in GB), and then:

  1. write an HTML report listing the matching directories sorted ascending
     (smallest first);
  2. write an ``input.js`` that can be used together with
     ``/home/xxchen/mail/autoMail.py`` to e-mail the report, e.g.::

         python3 /home/xxchen/mail/autoMail.py <out-dir>/input.js

Requirements honoured:
  * The ``.snapshot`` directory is never scanned (pruned at every level and
    skipped as a first-level entry).
  * The total time budget for scanning directories is capped at 1 hour
    (3600 seconds); directories not fully scanned before the deadline are
    marked as incomplete.
  * Only directories *strictly greater* than the threshold (default 200 GB)
    are reported.

Usage::

    python3 pdk_dir_size_check.py --root <dir> --threshold <GB> --out-dir <out>
"""

import argparse
import json
import os
import sys
import time
from html import escape

# Requirement: the directory query must not run longer than 1 hour.
SCAN_TIMEOUT_SECONDS = 3600  # 1h = 3600s

# 1 GB is treated as 2**30 bytes (the conventional "binary" gigabyte used by
# tools such as ``du``). Adjust here if a decimal gigabyte (1e9) is needed.
GB = 1024 ** 3


def format_size(num_bytes):
    """Return a human readable size string (1024-based units, like ``du -h``)."""
    if num_bytes < 1024:
        return "%d B" % num_bytes
    units = ("KB", "MB", "GB", "TB", "PB", "EB")
    value = float(num_bytes)
    for unit in units:
        value /= 1024.0
        if value < 1024.0:
            return "%.2f %s" % (value, unit)
    return "%.2f %s" % (value, units[-1])


def format_threshold(gb):
    """Nicely format the threshold value, avoiding trailing '.0'."""
    if float(gb).is_integer():
        return str(int(gb))
    return repr(float(gb))
def directory_size(path, deadline):
    """Return ``(size_in_bytes, completed)`` for ``path``.

    Directories named ``.snapshot`` are pruned so that they are neither
    descended into nor counted.  The scan is aborted (returning the partial
    size and ``completed=False``) once ``deadline`` (``time.monotonic``
    seconds) is reached.
    """
    total = 0
    completed = True
    for dirpath, dirnames, filenames in os.walk(path):
        if time.monotonic() > deadline:
            completed = False
            break
        # Prune .snapshot directories at every level -> never scan them.
        dirnames[:] = [d for d in dirnames if d != ".snapshot"]
        for name in filenames:
            full = os.path.join(dirpath, name)
            try:
                # Avoid double counting symlinked files and do not follow them.
                if os.path.islink(full):
                    continue
                total += os.lstat(full).st_size
            except OSError:
                # File may have vanished between listdir and lstat; ignore it.
                continue
    return total, completed


def scan_root(root, threshold_gb):
    """Scan first-level sub-directories of ``root``.

    Returns ``(results, threshold_bytes)`` where ``results`` is a list of
    dicts (``name``, ``size``, ``completed``) sorted ascending by size.
    """
    if not os.path.isdir(root):
        raise ValueError("root is not a directory: %s" % root)

    threshold_bytes = threshold_gb * GB
    deadline = time.monotonic() + SCAN_TIMEOUT_SECONDS

    try:
        entries = sorted(os.listdir(root))
    except OSError as exc:
        sys.exit("cannot list root directory %s: %s" % (root, exc))

    results = []
    for name in entries:
        # Do not check the .snapshot directory.
        if name == ".snapshot":
            continue
        full = os.path.join(root, name)
        if not os.path.isdir(full):
            continue

        size, completed = directory_size(full, deadline)
        if size > threshold_bytes:
            results.append({"name": name, "size": size, "completed": completed})

        # Stop early once the 1h budget is exhausted.
        if time.monotonic() > deadline:
            break

    # Ascending order (smallest -> largest); tie-break by name for determinism.
    results.sort(key=lambda r: (r["size"], r["name"]))
    return results, threshold_bytes
def build_html(results, root, threshold_gb):
    """Build the HTML report string for the matching directories."""
    if results:
        rows = []
        for index, r in enumerate(results, 1):
            remark = ""
            if not r["completed"]:
                remark = " <em>(scan hit 1h limit &mdash; size incomplete)</em>"
            rows.append(
                "<tr><td>%d</td><td>%s%s</td><td class=\"num\">%s</td></tr>"
                % (index, escape(r["name"]), remark, format_size(r["size"]))
            )
        table_rows = "\n".join(rows)
    else:
        table_rows = (
            "<tr><td colspan=\"3\">No first-level directory exceeds the "
            "threshold.</td></tr>"
        )

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>PDK Directory Size Report</title>
<style>
body { font-family: Arial, Helvetica, sans-serif; margin: 24px; color: #222; }
h1 { font-size: 20px; }
p { color: #444; }
code { background: #f4f4f4; padding: 1px 4px; }
table { border-collapse: collapse; width: 100%%; margin-top: 12px; }
th, td { border: 1px solid #ccc; padding: 6px 10px; text-align: left; }
th { background: #f2f2f2; }
.num { text-align: right; }
</style>
</head>
<body>
<h1>PDK Directory Size Report</h1>
<p>Root: <code>%s</code><br>
First-level directories larger than %s GB, sorted ascending (smallest first).
The <code>.snapshot</code> directory is excluded.</p>
<table>
<thead><tr><th>#</th><th>Directory</th><th>Size</th></tr></thead>
<tbody>
%s
</tbody>
</table>
</body>
</html>
""" % (escape(root), format_threshold(threshold_gb), table_rows)
    return html


def build_input_js(results, root, threshold_gb, html_path):
    """Build the ``input.js`` content (a JSON object understood by autoMail)."""
    if results:
        lines = []
        for r in results:
            flag = "" if r["completed"] else "  [incomplete]"
            lines.append("%-12s %s%s" % (format_size(r["size"]), r["name"], flag))
        text = (
            "First-level directories under %s larger than %s GB "
            "(smallest to largest):\n%s"
            % (root, format_threshold(threshold_gb), "\n".join(lines))
        )
    else:
        text = (
            "No first-level directory under %s exceeds %s GB."
            % (root, format_threshold(threshold_gb))
        )

    data = {
        "Text": text,
        "subject": "PDK Directory Size Report (> %s GB)"
        % format_threshold(threshold_gb),
        "receivers": ["Bill.Chen@cxmt.com"],
        "filePath": [html_path],
    }
    return json.dumps(data, indent=4, ensure_ascii=False)
def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Scan first-level sub-directories of --root, report those larger "
            "than --threshold GB in an HTML file, and generate input.js for "
            "/home/xxchen/mail/autoMail.py."
        )
    )
    parser.add_argument(
        "--root",
        required=True,
        help="root directory whose first-level sub-directories are scanned",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=200.0,
        help="size threshold in GB (binary, 1024^3 bytes); directories "
        "strictly larger than this are kept (default: 200)",
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        help="directory where the HTML report and input.js are written",
    )
    args = parser.parse_args(argv)

    if args.threshold < 0:
        parser.error("--threshold must be >= 0")

    results, _threshold_bytes = scan_root(args.root, args.threshold)

    os.makedirs(args.out_dir, exist_ok=True)
    html_path = os.path.join(args.out_dir, "pdk_dir_size_report.html")
    js_path = os.path.join(args.out_dir, "input.js")
    html_abs = os.path.abspath(html_path)
    js_abs = os.path.abspath(js_path)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(build_html(results, args.root, args.threshold))

    with open(js_path, "w", encoding="utf-8") as f:
        f.write(build_input_js(results, args.root, args.threshold, html_abs))

    print("Scanned root : %s" % args.root)
    print("Threshold    : > %s GB" % format_threshold(args.threshold))
    print("Directories  : %d" % len(results))
    for r in results:
        print("  %-12s %s%s"
              % (format_size(r["size"]), r["name"],
                 "" if r["completed"] else "  [incomplete]"))
    print("HTML report  : %s" % html_abs)
    print("Mail input   : %s" % js_abs)
    print("Send e-mail  : python3 /home/xxchen/mail/autoMail.py %s" % js_abs)
    return 0


if __name__ == "__main__":
    sys.exit(main())