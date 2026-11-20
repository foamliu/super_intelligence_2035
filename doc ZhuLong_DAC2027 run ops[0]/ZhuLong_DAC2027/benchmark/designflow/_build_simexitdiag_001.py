#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build EDA-Eval-DesignFlow-SimExitMatrixDiag-001 (spice_sim, A-faithful, L1).

Trace: ypzheng @ hfeg0pkn003, session 1793667622298_rh3ek.
A-faithful prompt (U#0 verbatim): scan a NanoSpice matrix-run dir, diagnose
why simulations exited. Gold = assistant scan_sim_exit3.py classified 24 run
dirs into COMPLETE / FAILED(verilog_a_bsource) / FAILED(transient_convergence)
/ RUNNING and extracted failure reasons from si.out.

Builds assets (A matrix_run_A, hidden B matrix_run_B), reference script,
check.py (14 assertions), negatives.
"""
import os, json, shutil, zipfile, hashlib, textwrap

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-SimExitMatrixDiag-001"
AROOT = os.path.join(BENCH, "assets", CID)
RROOT = os.path.join(BENCH, "reference", CID)

# ---------- si.out content generators (authentic NanoSpice patterns) ----------
HEADER = """  Copyright (c) 2010-2025  Primarius Tech
  NanoSpice Pro version 2024.12.1 (linux64)
  License: Primarius NanoSpice (node-locked)
  Reading netlist file: netlist.spf ...
  Netlist expanded: 19846532 nodes, 134021 bsource instances.
  Elaboration done.
"""
MEMWARN = "  !NanoSpice-WARNING: The available physical memory is only {mem:.4f}GB, the simulation has risk of being killed due to memory exhausted.\n"

def si_complete(corner, mem=19.95):
    s = HEADER
    s += "  Trying Homotopy Method (Real Pseudo Tran) for DC\n"
    s += MEMWARN.format(mem=mem)
    s += "  DC operating point found.\n"
    s += "  Transient analysis: my_tran  tstop=3.75ns\n"
    s += "  ... 50% ... 80% ... 100% ...\n"
    s += "  Transient analysis my_tran completed.\n"
    s += '  Simulation completed successfully\n'
    return s

def si_bsource_fail(corner, mem=2.80):
    s = HEADER
    s += "  Trying Homotopy Method (Real Pseudo Tran) for DC\n"
    s += MEMWARN.format(mem=mem)
    s += "  Elaborating Verilog-A module bsource_resistor ...\n"
    s += "  !!NanoSpice-ERROR: Cannot found shared object library for VerilogA module: bsource_primarius_3.\n"
    s += "  Cannot open file: compile.info\n"
    s += "  !!NanoSpice-ERROR: Verilog-A error: Cannot find shared object library for bsource module.\n"
    s += "     Maybe other NanoSpice process is running this netlist, please rerun with a new work dir.\n"
    s += '  Simulation failed due to "Verilog-A error: Cannot find shared object library for bsource module."\n'
    return s

def si_conv_fail(corner, mem=3.26):
    s = HEADER
    s += "  Trying Homotopy Method (Real Pseudo Tran) for DC\n"
    s += MEMWARN.format(mem=mem)
    s += "  DC operating point found.\n"
    s += "  Transient analysis: my_tran  tstop=0.75ns\n"
    s += "  ... 30% ...\n"
    s += "  !!NanoSpice-ERROR: Transient analysis my_tran did not converge at time 2.31e-10.\n"
    s += "  !!NanoSpice-ERROR: time step too small: dt = 9.98e-16 < 1e-15, convergence failed.\n"
    s += '  Simulation failed due to "Transient analysis did not converge."\n'
    return s

def si_running(corner, mem=11.03):
    s = HEADER
    s += "  Trying Homotopy Method (Real Pseudo Tran) for DC\n"
    s += MEMWARN.format(mem=mem)
    s += "  DC operating point found.\n"
    s += "  Transient analysis: my_tran  tstop=3.75ns\n"
    s += "  ... 10% ... 40% ... 70% ...\n"
    # no completion / no failure marker => still running (partial log)
    return s

def run_dir_name(sec, width, corner, rid):
    return "nanospice.perbank_Sec{sec}WL0CSL0_ypzhengcoretiming_{w}_B0_tck{tck}nsRL{rl}WL{wl}CKR{ckr}_{rid}_DVFSCLowSpeed.x16.{corner}.X16.tmp.voltage_s_LP5X.forcecell".format(
        sec=sec, w=width, tck="3.75" if width=="16b" else "0.75",
        rl="8" if width=="16b" else "28", wl="4" if width=="16b" else "16",
        ckr="2" if width=="16b" else "4", rid=rid, corner=corner)

# ---------- build A matrix (16 dirs): 2 complete, 5 bsource, 3 conv, 6 running ----------
A_SPEC = [
    # (kind, sec, width, corner, rid, mem)  -- rid unique per entry to avoid dir-name collision
    ("complete", 28, "16b", "TT0.94v-40c", "A101", 19.95),
    ("complete", 28, "4b4g", "TT0.94v25c", "A102", 13.41),
    ("bsource",  28, "16b", "FF1.25v-40c", "A103", 2.80),
    ("bsource",  28, "4b4g", "SS0.9v-40c",  "A104", 2.74),
    ("bsource",  28, "4b4g", "TT0.94v25c",  "A105", 19.95),
    ("bsource",  56, "4b4g", "SS0.9v-40c",  "A106", 3.26),
    ("bsource",  28, "16b", "SS0.9v130c",   "A107", 2.83),
    ("conv",     28, "4b4g", "SS0.9v130c",  "A108", 3.26),
    ("conv",     28, "16b", "SS0.9v-40c",   "A109", 11.03),
    ("conv",     28, "4b4g", "FF1.25v130c", "A110", 22.43),
    ("running",  28, "16b", "TT0.94v25c",   "A111", 3.69),
    ("running",  28, "16b", "SS0.9v-40c",   "A112", 11.03),
    ("running",  28, "16b", "SS0.9v130c",   "A113", 9.86),
    ("running",  28, "4b4g", "FF1.25v-40c", "A114", 13.41),
    ("running",  28, "4b4g", "FF1.25v130c", "A115", 22.43),
    ("running",  56, "16b", "TT0.94v25c",   "A116", 19.95),
]

GEN = {"complete": si_complete, "bsource": si_bsource_fail,
       "conv": si_conv_fail, "running": si_running}

# A-only marker dir (named with a unique A token to test non-hardcoding)
A_MARKER_DIR = run_dir_name(28, "16b", "TT0.94v25c", "ZZA_ONLY_MARKER")

def build_matrix(root, spec, with_marker=False):
    if os.path.exists(root):
        shutil.rmtree(root)
    os.makedirs(root)
    names = []
    for kind, sec, w, corner, rid, mem in spec:
        dn = run_dir_name(sec, w, corner, rid)
        os.makedirs(os.path.join(root, dn))
        with open(os.path.join(root, dn, "si.out"), "w") as fh:
            fh.write(GEN[kind](corner, mem))
        names.append(dn)
    if with_marker:
        os.makedirs(os.path.join(root, A_MARKER_DIR))
        with open(os.path.join(root, A_MARKER_DIR, "si.out"), "w") as fh:
            fh.write(si_complete("TT0.94v25c", 19.95))
        names.append(A_MARKER_DIR)
    # also drop a stray non-dir file to test the scanner ignores files
    with open(os.path.join(root, "README_matrix.txt"), "w") as fh:
        fh.write("matrix run index\n")
    return names

# ---------- build B matrix (14 dirs): 3 complete, 4 bsource, 2 conv, 5 running ----------
B_SPEC = [
    ("complete", 28, "16b", "TT0.94v25c",  "B201", 12.41),
    ("complete", 56, "4b4g", "FF1.25v-40c", "B202", 18.30),
    ("complete", 28, "4b4g", "SS0.9v-40c",  "B203", 9.20),
    ("bsource",  28, "16b", "FF1.25v130c",  "B204", 5.10),
    ("bsource",  28, "4b4g", "TT0.94v-40c",  "B205", 4.40),
    ("bsource",  56, "16b", "SS0.9v130c",   "B206", 6.60),
    ("bsource",  28, "16b", "SS0.9v-40c",   "B207", 8.80),
    ("conv",     56, "16b", "TT0.94v25c",   "B208", 7.70),
    ("conv",     28, "4b4g", "FF1.25v-40c", "B209", 14.20),
    ("running",  28, "16b", "TT0.94v-40c",  "B210", 10.50),
    ("running",  28, "4b4g", "TT0.94v25c",  "B211", 16.00),
    ("running",  56, "4b4g", "SS0.9v-40c",  "B212", 21.00),
    ("running",  28, "4b4g", "SS0.9v130c",  "B213", 4.90),
    ("running",  56, "16b", "FF1.25v130c",  "B214", 13.00),
]

def ground_truth(root):
    """Re-derive ground truth classification from a matrix dir."""
    complete, failed, running = [], [], []
    ftypes = set()
    for dn in sorted(os.listdir(root)):
        full = os.path.join(root, dn)
        if not os.path.isdir(full):
            continue
        si = os.path.join(full, "si.out")
        if not os.path.isfile(si):
            running.append(dn); continue
        with open(si, "r", errors="replace") as fh:
            txt = fh.read()
        low = txt.lower()
        if "simulation completed successfully" in low:
            complete.append(dn)
        elif "simulation failed" in low:
            # reason = last 'Simulation failed due to "..."' line
            reason = ""
            for line in txt.splitlines():
                if "simulation failed" in line.lower():
                    reason = line.strip()
            if "shared object library" in low or "bsource" in low or "verilog-a" in low or "veriloga" in low:
                ftype = "verilog_a_bsource"
            elif "converge" in low or "my_tran" in low or "time step" in low:
                ftype = "transient_convergence"
            else:
                ftype = "unknown"
            ftypes.add(ftype)
            failed.append({"dir": dn, "reason": reason, "type": ftype})
        else:
            running.append(dn)
    return {"total": len([d for d in os.listdir(root) if os.path.isdir(os.path.join(root,d))]),
            "complete": sorted(complete), "failed": sorted(failed, key=lambda x: x["dir"]),
            "running": sorted(running), "failure_types": sorted(ftypes)}

# ================= build =================
# A assets
ama_root = os.path.join(AROOT, "matrix_run_A")
a_names = build_matrix(ama_root, A_SPEC, with_marker=True)
# hidden B
hb_root = os.path.join(RROOT, "hidden", "matrix_run_B")
b_names = build_matrix(hb_root, B_SPEC, with_marker=False)

# task_brief.md + prompt.txt
PROMPT = "/proj/ddgoa/V0/simdir/finesim/workdir/ypzheng/ddgoaF/MatrixRun_Netlist_SpfBa_20261031PM_wisteria/去这个目录，看看仿真exit的原因是什么，应该怎么解决"
with open(os.path.join(AROOT, "prompt.txt"), "w") as fh:
    fh.write(PROMPT + "\n")
with open(os.path.join(AROOT, "task_brief.md"), "w") as fh:
    fh.write("交付接口：sim_exit_diag.py <matrix_run_dir> -o out.json\n")
    fh.write("out.json = {\"total\":int, \"complete\":[dir], \"failed\":[{dir,reason,type}], \"running\":[dir], \"failure_types\":[str]}\n")
    fh.write("可见输入 assets/matrix_run_A/；判分只跑隐藏 B。\n")

# hidden manifest
gt_a = ground_truth(ama_root)
gt_b = ground_truth(hb_root)
with open(os.path.join(RROOT, "hidden", "hidden_manifest.json"), "w") as fh:
    json.dump({"B_dir": "matrix_run_B", "ground_truth_B": gt_b,
               "A_ground_truth": gt_a, "A_marker_dir": A_MARKER_DIR}, fh, ensure_ascii=False, indent=2)

print("A dirs:", len(a_names), "B dirs:", len(b_names))
print("GT A:", json.dumps(gt_a, ensure_ascii=False)[:400])
print("GT B:", json.dumps(gt_b, ensure_ascii=False)[:400])
print("A_MARKER_DIR:", A_MARKER_DIR)
