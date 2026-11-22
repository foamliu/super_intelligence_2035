#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""negative_selftest.py -- verify the grader accepts the reference solution
and rejects all 5 negative submissions, each on a DIFFERENT condition.

Run:
    python3 negative_selftest.py
Expected: 1 PASS (reference) + 5 FAIL with distinct cond letters.
"""
import os
import shutil
import tempfile
import zipfile
import importlib.util
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CID = "EDA-Eval-DesignFlow-NetMissingCellExtract-001"
REF_DIR = os.path.join(HERE, "reference", CID)
CHECK_PATH = os.path.join(REF_DIR, "check.py")
REF_SOLVE = os.path.join(REF_DIR, "solve.py")
NEG_DIR = os.path.join(REF_DIR, "negative")
HIDDEN_DIR = os.path.join(HERE, "assets", CID, "hidden")

NEGATIVES = [
    ("empty_shell", "empty_shell.py"),
    ("print_only", "print_only.py"),
    ("hardcode_b", "hardcode_b.py"),
    ("naive_stub", "naive_stub.py"),
    ("delete_core", "delete_core.py"),
]


def _load_check():
    spec = importlib.util.spec_from_file_location("chk_" + CID, CHECK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_submit(script_path):
    """Zip a candidate script as netlist_missing_cell_extract.py into a temp
    submit.zip and return its path (workdir = HERE so hidden/ resolves)."""
    tmp = tempfile.mkdtemp(prefix="neg_submit_")
    zpath = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zpath, "w") as z:
        z.write(script_path, arcname="netlist_missing_cell_extract.py")
    # also stage hidden B into tmp/hidden so check resolves it from workdir
    hd = os.path.join(tmp, "hidden")
    os.makedirs(hd, exist_ok=True)
    for fn in ("netlist_b.v", "simlib_b.sv"):
        src = os.path.join(HIDDEN_DIR, fn)
        if os.path.isfile(src):
            shutil.copy(src, os.path.join(hd, fn))
    return zpath, tmp


def _norm(result):
    if result is True:
        return ("PASS", "")
    if isinstance(result, dict):
        return ("FAIL", result.get("cond", "?"))
    return ("FAIL", "?")


def main():
    chk = _load_check()
    print("=== reference solution (expect PASS) ===")
    zpath, tmp = _make_submit(REF_SOLVE)
    try:
        res = chk.check(zpath, tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    status, cond = _norm(res)
    print("reference: %s cond=%s" % (status, cond))
    if status != "PASS":
        print("  !! reference must PASS; aborting. raw=%r" % res)
        sys.exit(1)
    print("\n=== negatives (expect 5 FAIL with distinct conds) ===")
    seen_conds = set()
    all_ok = True
    for name, fn in NEGATIVES:
        zpath, tmp = _make_submit(os.path.join(NEG_DIR, fn))
        try:
            res = chk.check(zpath, tmp)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        status, cond = _norm(res)
        print("%-14s: %s cond=%s" % (name, status, cond))
        if status != "FAIL":
            print("  !! negative %s must FAIL" % name)
            all_ok = False
            continue
        if cond in seen_conds:
            print("  !! cond %s重复 (not distinct)" % cond)
            all_ok = False
        seen_conds.add(cond)
    print("\nsummary: 1 PASS + 5 FAIL, distinct conds = %s"
          % sorted(seen_conds))
    if all_ok and len(seen_conds) == 5:
        print("SELFTEST OK")
        sys.exit(0)
    else:
        print("SELFTEST FAIL")
        sys.exit(2)


if __name__ == "__main__":
    main()
