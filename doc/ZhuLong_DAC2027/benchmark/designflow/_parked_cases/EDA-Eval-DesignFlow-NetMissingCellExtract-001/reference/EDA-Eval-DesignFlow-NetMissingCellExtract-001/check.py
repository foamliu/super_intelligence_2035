#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py - grader for EDA-Eval-DesignFlow-NetMissingCellExtract-001
(shard C, physical_verify, deterministic netlist missing-cell extractor).

Deliverable: submit.zip containing netlist_missing_cell_extract.py -- a
deterministic Python parser that, given a Verilog netlist + a simlib library
file, prints a structured JSON report of every instance whose cell is NOT
defined in simlib (a "missing cell").

Judgment: 15 independent conditions (a)-(o). The L2 core (d)+(m) is a REAL
subprocess execution of the candidate's script on the HIDDEN B inputs
(netlist_b.v / simlib_b.sv -- NOT shipped in the SUT sandbox), asserting the
parsed JSON exactly matches the ground-truth oracle derived from B. A
hardcoded-B solution fails (o) because running it on A (sample_a, disjoint
cell set) would not yield A's 14-missing oracle. A print-only / empty stub
fails (e)/(g). Determinism is enforced across 3 PYTHONHASHSEED seeds (n).
"""
import os
import re
import json
import shutil
import hashlib
import zipfile
import subprocess
import tempfile
import py_compile

CID = "EDA-Eval-DesignFlow-NetMissingCellExtract-001"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "..", "assets", CID))

# ---- Hidden B inputs (resolved across judge-dir / repo layouts) ----
B_NETLIST_CANDS = [
    os.path.join(os.getcwd(), "hidden", "netlist_b.v"),
    os.path.join(HERE, "hidden", "netlist_b.v"),
    os.path.join(ASSETS, "hidden", "netlist_b.v"),
]
B_SIMLIB_CANDS = [
    os.path.join(os.getcwd(), "hidden", "simlib_b.sv"),
    os.path.join(HERE, "hidden", "simlib_b.sv"),
    os.path.join(ASSETS, "hidden", "simlib_b.sv"),
]
# ---- Visible A inputs (anti-hardcode cross-input guard) ----
A_NETLIST = os.path.join(ASSETS, "sample_a", "netlist_a.v")
A_SIMLIB = os.path.join(ASSETS, "sample_a", "simlib_a.sv")

# ---- Ground-truth oracle for hidden B (cell/module names disjoint from A) ----
B_TOTAL = 28
B_MISSING_COUNT = 12
B_AVAILABLE_COUNT = 16
B_MISSING_CELLS = [
    "bufLV_drv", "delayRC3", "invLVSx2", "invenIOLV", "keeperRC",
    "mux4IOLV", "nor2LVx2", "ntn_io", "ptn_io", "tg_lv",
]
B_AVAILABLE_CELLS = [
    "andbase_clk", "bufLV", "clkbufLV", "dff_base", "invLV",
    "keeper_base", "mux2LV", "nmos_b", "pgmon_b", "pmos_b", "tie_base",
]
B_MISSING_INSTANCES = [
    {"line": 11, "cell": "bufLV_drv", "instance": "I1",
     "ports": {"Y": "net1", "A": "clk_in", "vcc": "vcc", "vss": "vss"}},
    {"line": 12, "cell": "invLVSx2", "instance": "I2",
     "ports": {"Y": "net2", "A": "clk_in", "vcc": "vcc", "vss": "vss"}},
    {"line": 23, "cell": "nor2LVx2", "instance": "I0",
     "ports": {"Y": "Y", "A": "A", "B": "B", "vcc": "vcc", "vss": "vss"}},
    {"line": 24, "cell": "nor2LVx2", "instance": "I1",
     "ports": {"Y": "net10", "A": "Y", "B": "B", "vcc": "vcc", "vss": "vss"}},
    {"line": 25, "cell": "ntn_io", "instance": "MN0",
     "ports": {"D": "net10", "G": "A", "S": "vss", "B": "vss"}},
    {"line": 26, "cell": "ptn_io", "instance": "MP0",
     "ports": {"D": "net10", "G": "A", "S": "vcc", "B": "vcc"}},
    {"line": 37, "cell": "invenIOLV", "instance": "I0",
     "ports": {"Y": "Q", "A": "D", "En": "en", "EnN": "enN", "vcc": "vcc", "vss": "vss"}},
    {"line": 38, "cell": "keeperRC", "instance": "I1",
     "ports": {"Q": "Q", "vcc": "vcc", "vss": "vss"}},
    {"line": 40, "cell": "tg_lv", "instance": "I3",
     "ports": {"P0": "D", "P1": "Q", "S": "en", "SN": "enN"}},
    {"line": 51, "cell": "mux4IOLV", "instance": "I0",
     "ports": {"Y": "Y", "A": "A", "B": "B", "C": "C", "D": "D",
               "S0": "S0", "S1": "S1", "vcc": "vcc", "vss": "vss"}},
    {"line": 65, "cell": "delayRC3", "instance": "I0",
     "ports": {"OUT": "out", "IN": "in", "vcc": "vcc", "vss": "vss"}},
    {"line": 82, "cell": "invLVSx2", "instance": "I5",
     "ports": {"Y": "net40", "A": "sin", "vcc": "vpwr", "vss": "vgnd"}},
]
# A oracle (for anti-hardcode): A has 14 missing instances; missing cell set
# is DISJOINT from B's missing cell set.
A_MISSING_COUNT = 14
A_MISSING_CELLS = {
    "invCS", "invDSx1", "invenCS", "invenLVSx1", "invhizCS",
    "nand2IOLVx2", "nand3IOLVx2", "ntn_lv", "parasiticRC2", "ptn_lv",
}

_FAILED = []


def _fail(cond, msg):
    _FAILED.append((cond, msg))
    raise _FailExit(cond, msg)


class _FailExit(Exception):
    def __init__(self, cond, msg):
        super().__init__("[%s] %s" % (cond, msg))
        self.cond = cond
        self.msg = msg


def _first_existing(cands):
    for c in cands:
        if os.path.isfile(c):
            return c
    return None


def _run_solve(script, netlist, simlib, env=None, timeout=60):
    cmd = ["python3", script, netlist, simlib]
    return subprocess.run(cmd, capture_output=True, text=True,
                          env=env, timeout=timeout)


def check(deliverable, workdir):
    _FAILED.clear()
    tmp = tempfile.mkdtemp(prefix="chk_netmcell_")
    try:
        # (a) deliverable is a valid zip
        if not os.path.isfile(deliverable):
            _fail("a", "deliverable not found: %s" % deliverable)
        try:
            with zipfile.ZipFile(deliverable) as z:
                z.extractall(tmp)
        except Exception as e:
            _fail("a", "submit.zip not a valid zip: %s" % e)
        solve = os.path.join(tmp, "netlist_missing_cell_extract.py")
        if not os.path.isfile(solve):
            _fail("b", "submit.zip missing netlist_missing_cell_extract.py")
        # (c) script compiles
        try:
            py_compile.compile(solve, doraise=True)
        except py_compile.PyCompileError as e:
            _fail("c", "script does not compile: %s" % e)
        # resolve hidden B inputs
        b_net = _first_existing(B_NETLIST_CANDS)
        b_sim = _first_existing(B_SIMLIB_CANDS)
        if not b_net or not b_sim:
            _fail("d", "hidden B inputs not resolvable (net=%s sim=%s)"
                  % (b_net, b_sim))
        # (d) REAL subprocess run on B returns rc==0
        try:
            r = _run_solve(solve, b_net, b_sim)
        except subprocess.TimeoutExpired:
            _fail("d", "subprocess run on B timed out")
        if r.returncode != 0:
            _fail("d", "run on B exit=%d stderr=%s"
                  % (r.returncode, r.stderr[-300:]))
        out = r.stdout
        # (e) stdout is valid JSON
        try:
            rep = json.loads(out)
        except Exception as e:
            _fail("e", "stdout not valid JSON: %s (head=%r)"
                  % (e, out[:200]))
        # (f) top-level keys present and typed
        if not isinstance(rep.get("missing_instances"), list):
            _fail("f", "missing missing_instances list")
        if not isinstance(rep.get("summary"), dict):
            _fail("f", "missing summary dict")
        s = rep["summary"]
        # (g) summary.missing_count == oracle
        if s.get("missing_count") != B_MISSING_COUNT:
            _fail("g", "summary.missing_count=%r expected %d"
                  % (s.get("missing_count"), B_MISSING_COUNT))
        # (h) summary.total_instances == oracle
        if s.get("total_instances") != B_TOTAL:
            _fail("h", "summary.total_instances=%r expected %d"
                  % (s.get("total_instances"), B_TOTAL))
        # (i) summary.available_count == oracle
        if s.get("available_count") != B_AVAILABLE_COUNT:
            _fail("i", "summary.available_count=%r expected %d"
                  % (s.get("available_count"), B_AVAILABLE_COUNT))
        # (j) summary.missing_cells == sorted-unique oracle
        if s.get("missing_cells") != B_MISSING_CELLS:
            _fail("j", "summary.missing_cells=%r expected %r"
                  % (s.get("missing_cells"), B_MISSING_CELLS))
        # (k) summary.available_cells_used == sorted-unique oracle
        if s.get("available_cells_used") != B_AVAILABLE_CELLS:
            _fail("k", "summary.available_cells_used=%r expected %r"
                  % (s.get("available_cells_used"), B_AVAILABLE_CELLS))
        # (l) each missing_instances entry has the 4 required keys + types
        mi = rep["missing_instances"]
        REQ_KEYS = {"line", "cell", "instance", "ports"}
        for idx, e in enumerate(mi):
            if set(e.keys()) != REQ_KEYS:
                _fail("l", "entry#%d keys=%r expected %r"
                      % (idx, sorted(e.keys()), sorted(REQ_KEYS)))
            if not isinstance(e["line"], int) or e["line"] < 1:
                _fail("l", "entry#%d line not a positive int: %r"
                      % (idx, e["line"]))
            if not isinstance(e["ports"], dict):
                _fail("l", "entry#%d ports not a dict" % idx)
        # (m) exact match: missing_instances == oracle (order-independent by
        # (line, cell, instance) signature; ports compared as dicts)
        got_sig = sorted((e["line"], e["cell"], e["instance"],
                          tuple(sorted(e["ports"].items())))
                         for e in mi)
        exp_sig = sorted((e["line"], e["cell"], e["instance"],
                          tuple(sorted(e["ports"].items())))
                         for e in B_MISSING_INSTANCES)
        if got_sig != exp_sig:
            _fail("m", "missing_instances does not exactly match oracle")
        # (n) determinism across 3 PYTHONHASHSEED seeds
        import os as _os
        base_env = dict(_os.environ)
        digests = []
        for seed in ("0", "1", "42"):
            env = dict(base_env)
            env["PYTHONHASHSEED"] = seed
            rr = _run_solve(solve, b_net, b_sim, env=env)
            if rr.returncode != 0:
                _fail("n", "run on B seed=%s exit=%d" % (seed, rr.returncode))
            digests.append(hashlib.md5(rr.stdout.encode("utf-8")).hexdigest())
        if len(set(digests)) != 1:
            _fail("n", "non-deterministic output across seeds: %s" % digests)
        # (o) anti-hardcode: running solve on A (visible sample_a, DISJOINT
        # cell set) must produce A's 14-missing oracle, not B's. A solution
        # that hardcodes B's answer fails here.
        if not (os.path.isfile(A_NETLIST) and os.path.isfile(A_SIMLIB)):
            _fail("o", "sample_a inputs missing (net=%s sim=%s)"
                  % (A_NETLIST, A_SIMLIB))
        try:
            ra = _run_solve(solve, A_NETLIST, A_SIMLIB)
        except subprocess.TimeoutExpired:
            _fail("o", "run on A timed out")
        if ra.returncode != 0:
            _fail("o", "run on A exit=%d (script must be generic)"
                  % ra.returncode)
        try:
            rep_a = json.loads(ra.stdout)
        except Exception as e:
            _fail("o", "A stdout not valid JSON: %s" % e)
        sa = rep_a.get("summary", {})
        if sa.get("missing_count") != A_MISSING_COUNT:
            _fail("o", "A missing_count=%r expected %d (hardcoded B?)"
                  % (sa.get("missing_count"), A_MISSING_COUNT))
        a_cells = set(sa.get("missing_cells", []))
        if a_cells != A_MISSING_CELLS:
            _fail("o", "A missing_cells=%r expected %r"
                  % (sorted(a_cells), sorted(A_MISSING_CELLS)))
        if a_cells & set(B_MISSING_CELLS):
            _fail("o", "A missing_cells overlap with B (not disjoint): %s"
                  % sorted(a_cells & set(B_MISSING_CELLS)))
        return True
    except _FailExit as ex:
        return {"pass": False, "cond": ex.cond, "reason": ex.msg}
    except Exception as ex:
        return {"pass": False, "cond": "?", "reason": "unexpected: %r" % ex}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    import sys
    sub = sys.argv[1] if len(sys.argv) > 1 else "reference_submit.zip"
    print(check(sub, os.getcwd()))
