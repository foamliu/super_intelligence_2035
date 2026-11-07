#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-MonteCarloDeckGen-001 to EDA-Eval-DesignFlow_B.jsonl"""
import json, os

CASE_ID = "EDA-Eval-DesignFlow-MonteCarloDeckGen-001"
JSONL = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_B.jsonl"

PROMPT = """我在 hfeg0pkn005 上用 FineSim 跑 XDec driver 的仿真，deck 文件是 sim_driver_x20_adj.sp（见附件）。这个 deck 现在用 PVT corner（FF/TT/SS 通过 .if pcor_*==1 切换，sigmaflag=1.36 固定，.tran 1p 2us）来覆盖工艺/温度/电压偏差。

我想把这个文件修改成一个蒙特卡罗仿真。蒙特卡罗给予的随机量是什么？如果我想仿真把温度、工艺和电压都随机，应该怎么改？帮我把改之后的 deck 存到路径下。

附件：sim_driver_x20_adj.sp（FineSim XDec driver 仿真 deck，含 netlist/stimulus/measure 的 .inc、PVT corner 块、sigmaflag/.param、.tran/.probe/.end）。

请给我一个可重复使用的 Python 生成器 gen_monte_carlo.py，读取一个 FineSim PVT deck，产出一个正确的蒙特卡罗 deck（不要用 HSPICE 的 .dc var gauss 写法，FineSim 会报 "incomplete or unsupported sweep statement"），并随机化工艺、温度、电压三个量。"""

TEST = '''def check(deliverable, workdir):
    import os, re, shutil, subprocess, sys, tempfile, zipfile
    HIDDEN_DECK_NAME = "sim_driver_alt_b.sp"
    B_NETLIST_PATHS = ["/proj/ddgoa/V1/simdir/finesim/workdir/kerwind/simulation/sa_control_vwlp/sa_control_top_schematic.netlist", "/proj/ddgoa/V1/simdir/finesim/workdir/kerwind/simulation/sa_control_vwlp/sa_control_driver_x40_adj.netlist"]
    B_MEASURE_PATH = "/proj/ddgoa/V1/simdir/finesim/workdir/kerwind/simulation/sa_control_vwlp/measure_sa.sp"
    B_BASE = "sim_driver_alt_b"
    bpath = None
    for root, _d, files in os.walk(workdir):
        if HIDDEN_DECK_NAME in files: bpath = os.path.join(root, HIDDEN_DECK_NAME); break
    if not bpath and os.path.isfile(os.path.join(workdir, "hidden", HIDDEN_DECK_NAME)): bpath = os.path.join(workdir, "hidden", HIDDEN_DECK_NAME)
    if not bpath or not os.path.isfile(bpath): raise AssertionError("a: hidden deck B not found")
    tmp = tempfile.mkdtemp(prefix="chk_mc_")
    try:
        if not os.path.isfile(deliverable): raise AssertionError("a: deliverable zip not found")
        if not zipfile.is_zipfile(deliverable): raise AssertionError("a: deliverable is not a zip")
        with zipfile.ZipFile(deliverable) as z:
            names = z.namelist(); gen_name = None
            for n in names:
                if n.endswith(".py") and "monte_carlo" in n.lower(): gen_name = n; break
            if not gen_name:
                pys = [n for n in names if n.endswith(".py") and "/" not in n]
                if len(pys) == 1: gen_name = pys[0]
            if not gen_name: raise AssertionError("a: no gen_monte_carlo.py in zip")
            z.extract(gen_name, tmp); gen_path = os.path.join(tmp, gen_name)
        cr = subprocess.run([sys.executable, "-m", "py_compile", gen_path], capture_output=True, text=True, timeout=30)
        if cr.returncode != 0: raise AssertionError("a: generator does not compile")
        outdir = os.path.join(tmp, "out"); os.makedirs(outdir, exist_ok=True)
        rr = subprocess.run([sys.executable, gen_path, bpath, outdir], capture_output=True, text=True, timeout=120)
        if rr.returncode != 0: raise AssertionError("b: generator exited non-zero on B")
        mcA_p = os.path.join(outdir, B_BASE+"_mc.sp"); mcB_p = os.path.join(outdir, B_BASE+"_mc_var.sp")
        if not (os.path.isfile(mcA_p) and os.path.isfile(mcB_p)): raise AssertionError("b: missing _mc.sp / _mc_var.sp outputs")
        mcA = open(mcA_p, errors="ignore").read(); mcB = open(mcB_p, errors="ignore").read()
        if not re.search(r"\\.tran\\b.*SWEEP\\s+MONTE\\s*=\\s*\\d+", mcA, re.I): raise AssertionError("c: mcA missing .tran SWEEP MONTE=N")
        if len(re.findall(r"AGAUSS\\s*\\(", mcA, re.I)) < 3: raise AssertionError("d: mcA needs >=3 AGAUSS() (process/temp/voltage)")
        if not re.search(r"\\.param\\s+pcor_ff\\s*=\\s*0\\s+pcor_tt\\s*=\\s*1\\s+pcor_ss\\s*=\\s*0", mcA): raise AssertionError("e: mcA does not lock TT corner base")
        for np in B_NETLIST_PATHS:
            if np not in mcA: raise AssertionError("f: mcA missing netlist .inc: "+np)
        if not re.search(r"\\.probe\\b", mcA, re.I): raise AssertionError("g: mcA missing .probe")
        if B_MEASURE_PATH not in mcA: raise AssertionError("g: mcA missing measure .inc")
        if not re.search(r"\\.Variation\\b", mcB, re.I): raise AssertionError("h: mcB missing .Variation")
        if not re.search(r"\\.Global_Variation\\b", mcB, re.I): raise AssertionError("h: mcB missing .Global_Variation")
        if not re.search(r"\\bTemp\\s+temp\\s*=", mcB, re.I): raise AssertionError("h: mcB missing Temp temp=")
        if not re.search(r"Parameter\\s+\\w+\\s*=\\s*Perturb\\s*\\(", mcB, re.I): raise AssertionError("h: mcB missing Parameter Perturb()")
        if not re.search(r"\\.tran\\b.*SWEEP\\s+MONTE\\s*=\\s*\\d+", mcB, re.I): raise AssertionError("i: mcB missing .tran SWEEP MONTE=N")
        for lbl, c in (("mcA", mcA), ("mcB", mcB)):
            if re.search(r"\\.dc\\b[^.\\n]*gauss\\b", c, re.I): raise AssertionError("j: "+lbl+" uses unsupported .dc gauss")
        ap = set()
        for m in re.finditer(r"\\.param\\s+(\\w+)\\s*=\\s*AGAUSS\\s*\\(", mcA, re.I): ap.add(m.group(1).lower())
        if len(ap) < 3: raise AssertionError("k: mcA defines only %d distinct AGAUSS params" % len(ap))
        dp = os.path.join(outdir, "diagnosis.md")
        if not os.path.isfile(dp): raise AssertionError("l: diagnosis.md not produced")
        diag = open(dp, errors="ignore").read()
        if "AGAUSS" not in diag: raise AssertionError("l: diagnosis.md missing AGAUSS")
        if not re.search(r"SWEEP\\s+MONTE", diag, re.I): raise AssertionError("l: diagnosis.md missing SWEEP MONTE")
        for kw in ("process", "temperature", "voltage"):
            if kw.lower() not in diag.lower(): raise AssertionError("l: diagnosis.md missing "+kw)
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)'''

RATIONALE = ("12 条断言：①zip含gen_monte_carlo.py且可编译 ②生成器在B上exit 0且产出_mc.sp+_mc_var.sp两文件 "
             "③mcA含.tran...SWEEP MONTE=N ④mcA含≥3个AGAUSS()调用(工艺/温度/电压) ⑤mcA锁定TT corner基(pcor_tt=1,ff/ss=0) "
             "⑥mcA保留B的netlist .inc路径 ⑦mcA保留.probe与measure .inc ⑧mcB含.Variation/.Global_Variation/Temp temp=/Parameter Perturb() "
             "⑨mcB含.tran SWEEP MONTE=N ⑩mcA/mcB均不使用.dc...gauss(FineSim不支持) ⑪mcA定义≥3个不同AGAUSS随机参量名 "
             "⑫diagnosis.md存在且提及AGAUSS+SWEEP MONTE+process/temperature/voltage三随机量")

case = {
    "id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": TEST,
    "prompt": PROMPT,
    "attachments": ["assets/EDA-Eval-DesignFlow-MonteCarloDeckGen-001/sim_driver_x20_adj.sp",
                    "assets/EDA-Eval-DesignFlow-MonteCarloDeckGen-001/task_brief.md"],
    "metadata": {
        "trace_source": {
            "user": "gallopc",
            "host": "hfeg0pkn005",
            "session_file": "1793790756982_bjazn.messages.json",
            "match_count": 296,
            "real_task_summary": "把 FineSim XDec driver PVT deck (sim_driver_x20_adj.sp) 改成蒙特卡罗仿真，随机化温度/工艺/电压；assistant 查 finesim_ug 后用 AGAUSS+SWEEP MONTE + .Variation 块两套正确写法（首版 .dc gauss 被 FineSim 拒）"
        },
        "domain": "spice_sim",
        "track": "faithful",
        "level": "L1",
        "test_rationale": RATIONALE,
        "hidden_inputs": ["assets/EDA-Eval-DesignFlow-MonteCarloDeckGen-001/hidden/sim_driver_alt_b.sp",
                          "assets/EDA-Eval-DesignFlow-MonteCarloDeckGen-001/hidden/hidden_manifest.json"]
    }
}

with open(JSONL, "a") as f:
    f.write(json.dumps(case, ensure_ascii=False) + "\n")
print("appended", CASE_ID, "to", JSONL)
# verify
import subprocess
r = subprocess.run(["wc", "-l", JSONL], capture_output=True, text=True)
print(r.stdout.strip())
