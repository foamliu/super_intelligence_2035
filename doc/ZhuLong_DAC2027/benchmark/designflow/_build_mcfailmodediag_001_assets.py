#!/usr/bin/env python3
"""Builder for EDA-Eval-DesignFlow-McFailModeDiag-001.
Generates assets (A visible + B hidden) + reference (candidate + check + 6 neg + selftest + reference_submit.zip).
L1 static log-based MC failure-mode classifier + status/aggregate consistency auditor.
"""
import os, json, zipfile, shutil, hashlib, textwrap

CASE = "EDA-Eval-DesignFlow-McFailModeDiag-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSETS = f"{BENCH}/assets/{CASE}"
REF   = f"{BENCH}/reference/{CASE}"

for d in (ASSETS, REF):
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d, exist_ok=True)

# ---------- run log builders (FineSim-style) ----------
def log_passed(run, metrics):
    lines = [
        f"FineSim> FineSimPro V-2023.12-1 (Rev 1)",
        f"FineSim> job: {run}",
        "FineSim> reading netlist ...",
        "FineSim> Checked out finesim(1) successfully",
        "FineSim> DC analysis ...",
        "FineSim> Successfully Completed",
        "FineSim> job concluded",
    ]
    return "\n".join(lines)+"\n"

def mt0_passed(metrics):
    hdr = " ".join(metrics.keys())
    vals= " ".join(f"{v:.6e}" for v in metrics.values())
    return f"$DATA1 .TITLE {hdr}\n{vals}\n"

def log_nonconv():
    return ("FineSim> FineSimPro V-2023.12-1\n"
            "FineSim> Checked out finesim(1) successfully\n"
            "FineSim> DC analysis ...\n"
            "WARNING! DC not converged at node x1\n"
            "ERROR! DC not converged\n"
            "FineSim> job aborted\n")

def log_measure_error():
    return ("FineSim> FineSimPro V-2023.12-1\n"
            "FineSim> Checked out finesim(1) successfully\n"
            "FineSim> DC analysis ... Successfully Completed\n"
            ".measure dc voh failed: target not reached\n"
            ".measure dc vol aborted\n"
            "FineSim> job concluded\n")

def log_port_mismatch(sub_a, sub_b):
    # also plant an env_error marker to test priority (port_mismatch > env_error)
    return (f"FineSim> FineSimPro V-2023.12-1\n"
            f"WARNING! subckt {sub_a} and {sub_b} have different number of pins\n"
            f"sh: ./run.sh: Permission denied\n"   # secondary env marker (must NOT flip to env_error)
            "FineSim> Simulation halted: port mismatch\n")

def log_license():
    # plant a non-conv marker too (license > non_conv)
    return ("FineSim> FineSimPro V-2023.12-1\n"
            "WARNING! no valid license(-8)! License to run is temporarily unavailable. Waiting for license to check in\n"
            "WARNING! DC not converged at node y2\n"  # secondary (must NOT flip to non_conv)
            "FineSim> job aborted: license\n")

def log_timeout():
    return ("FineSim> FineSimPro V-2023.12-1\n"
            "FineSim> Checked out finesim(1) successfully\n"
            "FineSim> DC analysis ... iteration 482\n"
            "FineSim> DC analysis ... iteration 483\n"
            "Killed (SIGKILL)\n")  # no "job concluded"

def log_env_error():
    return ("bash: line 1: ./CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_FS.sp: Permission denied\n"
            "module: command not found\n")

def mt0_empty():  return "$DATA1 .TITLE\n# empty (measure failed)\n"
def status_json(name, verdict): return json.dumps({"name":name,"status": "passed" if verdict=="passed" else "failed"})

# ---------- A: 8 runs, ALL failed (various modes), summary INCONSISTENT (trace Bug #1) ----------
A_METRICS = {"Ileak":1.23e-9,"Iread":42.5e-6,"Iwrite":38.1e-6,"WNM_1":0.31,"WNM_2":0.28}
A_RUNS = [
    ("arun_01", "non_convergence",  log_nonconv(),        mt0_empty()),
    ("arun_02", "measure_error",    log_measure_error(),   mt0_empty()),
    ("arun_03", "port_mismatch_abort", log_port_mismatch("sram_bc_a","sram_bc_b"), mt0_empty()),
    ("arun_04", "license_fail",     log_license(),         mt0_empty()),
    ("arun_05", "timeout",          log_timeout(),         mt0_empty()),
    ("arun_06", "env_error",        log_env_error(),       mt0_empty()),
    ("arun_07", "non_convergence",  log_nonconv(),         mt0_empty()),
    ("arun_08", "measure_error",    log_measure_error(),   mt0_empty()),
]
A_RUNS_DIR = f"{ASSETS}/mc_runs_A"
os.makedirs(A_RUNS_DIR, exist_ok=True)
A_GOLD = []
for name, mode, log, mt0 in A_RUNS:
    rd = f"{A_RUNS_DIR}/{name}"; os.makedirs(rd, exist_ok=True)
    with open(f"{rd}/run.log","w") as f: f.write(log)
    with open(f"{rd}/result.mt0","w") as f: f.write(mt0)
    with open(f"{rd}/status.json","w") as f: f.write(status_json(name, mode))
    A_GOLD.append({"name":name,"verdict":mode})
# A summary: BUG #1 — reports all passed / yield +inf while every run failed
with open(f"{ASSETS}/summary_A.json","w") as f:
    json.dump({"n_total":8,"n_pass":8,"n_fail":0,"yield":"infinity",
               "metrics":["Ileak","Iread","Iwrite","WNM_1","WNM_2"],
               "corner":"TT_-40C_0.825V","tool":"SolidoVD2022"}, f, indent=2)
# A deck (context)
with open(f"{ASSETS}/deck_A.sp","w") as f:
    f.write("* tt_-40_0.675.sp  TT corner -40C VVDD=0.825\n"
            ".include option_hspice.sp\n.include pwr.sp\n.include switch.sp\n"
            ".include sram_bitcell_netlist.sp\n.LIB ttg_sram_fs\n.LIB pre_sim_fs\n"
            ".TEMP -40\n.param VVDD=0.825\n.DC VIN 0.0 VVDD 10e-3 sweep monte=1\n")

# ---------- B: 10 runs, mixed, summary CONSISTENT ----------
B_METRICS = {"vil":0.42,"vih":0.61,"snm_lv":0.18,"snh_lv":0.22,"ion":55.3e-6,"ioff":7.8e-9}
def log_pass_b(run):
    return (f"FineSim> FineSimPro V-2023.12-1\nFineSim> job: {run}\n"
            "FineSim> Checked out finesim(1) successfully\nFineSim> DC analysis ...\n"
            "FineSim> Successfully Completed\nFineSim> job concluded\n")
B_RUNS = [
    ("brun_01", "passed",              log_pass_b("brun_01"),       mt0_passed(B_METRICS)),
    ("brun_02", "passed",              log_pass_b("brun_02"),       mt0_passed(B_METRICS)),
    ("brun_03", "non_convergence",     log_nonconv(),               mt0_empty()),
    ("brun_04", "measure_error",       log_measure_error(),          mt0_empty()),
    ("brun_05", "port_mismatch_abort", log_port_mismatch("inv_chain_b","nand2_chain_b"), mt0_empty()),
    ("brun_06", "license_fail",        log_license(),               mt0_empty()),
    ("brun_07", "timeout",             log_timeout(),               mt0_empty()),
    ("brun_08", "env_error",           log_env_error(),             mt0_empty()),
    ("brun_09", "passed",              log_pass_b("brun_09"),       mt0_passed(B_METRICS)),
    ("brun_10", "non_convergence",     log_nonconv(),               mt0_empty()),
]
B_RUNS_DIR = f"{ASSETS}/hidden/mc_runs_B"
os.makedirs(B_RUNS_DIR, exist_ok=True)
B_GOLD = []
for name, mode, log, mt0 in B_RUNS:
    rd = f"{B_RUNS_DIR}/{name}"; os.makedirs(rd, exist_ok=True)
    with open(f"{rd}/run.log","w") as f: f.write(log)
    with open(f"{rd}/result.mt0","w") as f: f.write(mt0)
    with open(f"{rd}/status.json","w") as f: f.write(status_json(name, mode))
    B_GOLD.append({"name":name,"verdict":mode})
with open(f"{ASSETS}/hidden/summary_B.json","w") as f:
    json.dump({"n_total":10,"n_pass":3,"n_fail":7,"yield":0.30,
               "metrics":["vil","vih","snm_lv","snh_lv","ion","ioff"],
               "corner":"SS_125C_0.88V","tool":"FineSimDirect"}, f, indent=2)
with open(f"{ASSETS}/hidden/deck_B.sp","w") as f:
    f.write("* brun deck SS 125C 0.88V\n.include opt_fs.sp\n.inc inv_chain_b.sp\n.LIB ss_fs\n.tran 1p 10n\n")
with open(f"{ASSETS}/hidden/hidden_manifest.json","w") as f:
    json.dump({"runs":[r["name"] for r in B_GOLD],
               "verdicts":{r["name"]:r["verdict"] for r in B_GOLD},
               "n_total":10,"n_pass":3,"yield":0.30,
               "aggregate_consistent":True,
               "metrics":["vil","vih","snm_lv","snh_lv","ion","ioff"]}, f, indent=2)

# prompt + task_brief
with open(f"{ASSETS}/prompt.txt","w") as f:
    f.write(
"用户 e0024852 在 Solido Variation Designer + FineSim 上跑了一组 Monte Carlo / corner 仿真"
"（见 mc_runs_A/，每条 run 一个子目录含 run.log / result.mt0 / status.json，以及顶层 summary_A.json 与 deck_A.sp）。"
"用户原话：「see variation_designer_7, find data bug, and how to debug」「check testbench」「how to fix each bug」。\n\n"
"请交付一个 Python 诊断器 mc_faildiag.py，给定 runs 目录与 summary.json，逐 run 分类失败模式"
"（passed / non_convergence / measure_error / port_mismatch_abort / license_fail / timeout / env_error），"
"并审计 per-run 状态与 summary 聚合（n_pass / yield）是否一致，输出 mc_faildiag_report.json。\n")
with open(f"{ASSETS}/task_brief.md","w") as f:
    f.write("交付接口：`python3 mc_faildiag.py <runs_dir> <summary.json> <out_dir>`，产出 `<out_dir>/mc_faildiag_report.json`。"
            "打包提交 `outputs/submit.zip`（内含 mc_faildiag.py 与 report）。资产见 mc_runs_A/ 与 summary_A.json。\n")

# save gold for selftest
with open(f"{REF}/gold_A.json","w") as f: json.dump(A_GOLD,f,indent=2)
with open(f"{REF}/gold_B.json","w") as f: json.dump(B_GOLD,f,indent=2)

print("assets built:", ASSETS)
print("A runs:", len(A_RUNS), "B runs:", len(B_RUNS))
