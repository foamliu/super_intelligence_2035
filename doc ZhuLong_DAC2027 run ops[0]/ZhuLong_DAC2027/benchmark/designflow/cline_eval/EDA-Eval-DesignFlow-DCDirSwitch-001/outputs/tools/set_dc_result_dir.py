#!/usr/bin/env python3
"""set_dc_result_dir.py

Switch the DC (Design Compiler) synthesis result directory that the downstream
implementation-flow files reference.

A DC result directory is always a ``dc_<timestamp>`` directory that lives under
``<project>/synth/results/`` (e.g. ``synth/results/dc_2026-10-29-19.16.52``).

Given a new DC result directory this tool updates every place that anchors the
*current* one:

  1. The ``DC_RESULT_DIR`` / ``POWER_RES_DIR`` variable in each flow Makefile
     (fm, apr, pe, signoff, pp, ptpx, sim, ...).
  2. The fallback default in ``fm/fm.tcl`` (``set dflt [file join $PRJ_ROOT
     synth results dc_<timestamp>]``).
  3. The gate-level simulation SDF path in ``rtl_power/<TOP>.vf``
     (``$sdf_annotate("synth/results/dc_<timestamp>/<TOP>.mapped.sdf", ...)``).

Usage:
    set_dc_result_dir.py <new_dc_result_dir> [--project <root>]
                          [--dry-run] [--backup]

``<new_dc_result_dir>`` may be given on the command line, or set directly in
this file via ``DEFAULT_DC_RESULT_DIR`` below.
"""

import argparse
import os
import re
import sys

# Set the new DC result directory here to avoid passing it on the command line.
DEFAULT_DC_RESULT_DIR = ""

# A DC result directory is named dc_<timestamp>, e.g. dc_2026-10-29-19.16.52
DC_TIMESTAMP_RE = re.compile(r"dc_\d{4}-\d{2}-\d{2}-\d{2}\.\d{2}\.\d{2}")

# File names recognised as (GNU) Makefiles.
MAKEFILE_NAMES = {"makefile", "gnumakefile", "bsdmakefile"}


def _error(msg):
    sys.stderr.write("set_dc_result_dir.py: error: %s\n" % msg)


def _find_target_files(project):
    """Return (makefiles, tcl_files, vf_files) under ``project``.

    The top-level driver Makefile (directly under the project root) is
    excluded: it is the entry point that *drives* this tool, not a flow
    Makefile that needs updating.
    """
    makefiles = []
    tcl_files = []
    vf_files = []
    root = os.path.realpath(project)
    for dirpath, _dirnames, filenames in os.walk(project):
        real_dir = os.path.realpath(dirpath)
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            low = fn.lower()
            if low in MAKEFILE_NAMES or low.endswith(".mk"):
                if real_dir == root:
                    continue  # skip the top-level driver Makefile
                makefiles.append(full)
            elif low.endswith(".tcl"):
                tcl_files.append(full)
            elif low.endswith(".vf"):
                vf_files.append(full)
    return makefiles, tcl_files, vf_files


def _replace_in_file(path, new_token, dry_run, backup):
    with open(path, "r") as fh:
        text = fh.read()

    if not DC_TIMESTAMP_RE.search(text):
        return False  # nothing anchored in this file

    new_text = DC_TIMESTAMP_RE.sub(new_token, text)
    if new_text == text:
        return False

    if dry_run:
        print("[dry-run] would update %s" % path)
    else:
        if backup:
            with open(path, "rb") as fh:
                data = fh.read()
            with open(path + ".bak", "wb") as fh:
                fh.write(data)
        with open(path, "w") as fh:
            fh.write(new_text)
        print("updated %s" % path)
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Switch the DC synthesis result directory referenced "
                    "across the implementation flow."
    )
    parser.add_argument(
        "new_dc_result_dir",
        nargs="?",
        default=None,
        help="new DC result directory (e.g. synth/results/dc_<timestamp>)",
    )
    parser.add_argument(
        "--project",
        default=".",
        help="project root (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="only report what would change; do not write any file",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="keep a .bak copy of every modified file",
    )
    args = parser.parse_args(argv)

    project = args.project
    value = args.new_dc_result_dir if args.new_dc_result_dir is not None \
        else DEFAULT_DC_RESULT_DIR

    if not os.path.isdir(project):
        _error("project root does not exist or is not a directory: %s" % project)
        return 1

    if not value:
        _error("no DC result directory given (pass it as an argument or set "
               "DEFAULT_DC_RESULT_DIR)")
        return 1

    new_token = os.path.basename(value.rstrip("/\\"))
    if not DC_TIMESTAMP_RE.fullmatch(new_token):
        _error("invalid DC result directory: %r (expected a directory name "
               "matching dc_<timestamp>)" % value)
        return 1

    makefiles, tcl_files, vf_files = _find_target_files(project)

    changed = 0
    for path in makefiles + tcl_files + vf_files:
        if _replace_in_file(path, new_token, args.dry_run, args.backup):
            changed += 1

    if changed == 0:
        print("no DC result references found under %s" % project)
    else:
        print("switched %d file(s) to DC result directory %s"
              % (changed, new_token))
    return 0


if __name__ == "__main__":
    sys.exit(main())