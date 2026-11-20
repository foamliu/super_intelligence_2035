#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builder for EDA-Eval-DesignFlow-SamplerSetupHold-001 (shard B, spice_sim).
Trace: irene1li 1794970973210_fve2x @ hfeg0plg58, mc=113.
User intent (msg[2]): compute setup/hold margins of the IO_DataLat D-latch
(falling-edge sampler) from a FineSim FSDB waveform, per the user's literal
definitions:
  setup time = data -> CLK low  (t_clk_fall - t_data)
  hold time  = CLK high -> data (t_data - t_clk_rise)
Reproducible offline: a sampled waveform CSV (t_ns,clk,data) + sampler spec.
"""
import os, json, csv

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-SamplerSetupHold-001"
ASSET = os.path.join(BENCH, "assets", CASE)
REF  = os.path.join(BENCH, "reference", CASE)
CASES_B = os.path.join(BENCH, "cases", "B")
SCRIPT = "sampler_setup_hold.py"

VDD = 1.0
VTH = 0.5
DT = 0.01  # ns (10 ps)

def square_clk(t, period, vdd):
    # LOW for first half, HIGH for second half -> first rising edge at period/2
    # (so the edge detector sees a clean low->high crossing for cycle 0).
    ph = (t % period) / period
    return vdd if ph >= 0.5 else 0.0

def data_step(t, edges, vdd):
    level = 0.0
    for e in edges:
        if t >= e:
            level = vdd if level == 0.0 else 0.0
    return level

def gen_waveform(period_ns, offsets_in_high, n_cycles, total_extra=0.5):
    rows = []
    # rising edges at period/2 + i*period ; data edge in each high phase
    first_rise = period_ns / 2.0
    data_edges = [first_rise + i * period_ns + offsets_in_high[i] for i in range(n_cycles)]
    t_end = first_rise + n_cycles * period_ns + total_extra  # cover last fall + margin
    n = int(round(t_end / DT))
    for k in range(n + 1):
        t = k * DT
        rows.append((t, square_clk(t, period_ns, VDD), data_step(t, data_edges, VDD)))
    return rows, data_edges

def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t_ns", "clk", "data"])
        for r in rows:
            w.writerow(["%.6f" % r[0], "%.6f" % r[1], "%.6f" % r[2]])

P_A = 2.0
OFF_A = [0.20, 0.35, 0.15, 0.45, 0.25, 0.40]
rows_A, edges_A = gen_waveform(P_A, OFF_A, 6)
P_B = 1.6
OFF_B = [0.18, 0.30, 0.42, 0.22, 0.38, 0.12]
rows_B, edges_B = gen_waveform(P_B, OFF_B, 6)

def compute_gt(period, offsets, n):
    setup, hold = [], []
    for i in range(n):
        tr = i * period
        tf = i * period + period / 2.0
        td = i * period + offsets[i]
        setup.append((tf - td) * 1000.0)
        hold.append((td - tr) * 1000.0)
    return setup, hold

GT_A_SETUP, GT_A_HOLD = compute_gt(P_A, OFF_A, 6)
GT_B_SETUP, GT_B_HOLD = compute_gt(P_B, OFF_B, 6)

os.makedirs(os.path.join(ASSET, "src"), exist_ok=True)
write_csv(os.path.join(ASSET, "src", "waveform_A.csv"), rows_A)
spec_A = {"sampler": "dlatch_falling", "t_col": "t_ns", "clk_col": "clk",
          "data_col": "data", "vth": VTH, "vdd": VDD}
with open(os.path.join(ASSET, "src", "sampler_spec_A.json"), "w") as f:
    json.dump(spec_A, f, indent=2)

PROMPT = """你是 EDA 仿真 characterization agent。用户 irene1li 在 hfeg0plg58 上用 FineSim 跑
CXMT m2701 V0_DDR4 的 sim_CkDcaMux24to1 电路（netlist:
/rundata/m2701/V0_DDR4/simdir/finesim/workdir/irene1li/simulation/sim_CkDcaMux24to1/hspiceD/schematic/netlist/netlist；
波形: .../stimulus_file/sim_1118pvt7PRBS7/test_1118pvt7PRBS7.fsdb），分析 24to1 中的采样裕度。

第一项：IO_DataLat 里的 D 锁存器（下降沿采样）。用户原话（msg[2]）：
  "D锁存器的setup time以及hold up time(setup time就是数据到CLK低电平的时间，
   hold up time就是CLK高电平到数据改变的时间)"
即对每个采样周期：
  setup_time = t(CLK 下降沿) - t(该周期高电平内的数据跳变)   [数据 -> CLK 低电平]
  hold_time  = t(该周期高电平内的数据跳变) - t(CLK 上升沿)   [CLK 高电平 -> 数据改变]

由于真实 FSDB 18GB 且内部节点名为哈希化扁平名（fscript/Verdi 均难直接寻址），已把 CLK 与
DATA 的采样波形导出成 CSV（可见输入 src/waveform_A.csv，列：t_ns, clk, data；电压 0..VDD，
均匀采样 dt=10ps）。sampler 配置见 src/sampler_spec_A.json：
  {"sampler":"dlatch_falling","t_col":"t_ns","clk_col":"clk","data_col":"data","vth":0.5,"vdd":1.0}

【交付】写一个纯 Python 命令行工具 sampler_setup_hold.py，按用户上述定义从采样波形 CSV
提取每个采样周期的 setup/hold 时间，并输出汇总报告 report.json。

用法:
  python3 sampler_setup_hold.py <waveform.csv> <sampler_spec.json> [--out report.json]

要求:
1. 读 CSV（列名由 spec 的 t_col/clk_col/data_col 指定），按 spec.vth 做阈值穿越检测边沿
   （CLK 上升沿=低->高穿越，CLK 下降沿=高->低穿越；DATA 边沿=任一方向穿越）。边沿时刻用
   相邻采样点线性插值到亚采样精度。
2. 按周期（相邻两次 CLK 上升沿之间为一个周期）切分；在每个周期的高电平段（上升沿到下降沿）
   内找到唯一一次 DATA 跳变时刻 t_data；若该周期高电平段无 DATA 跳变则跳过该周期。
3. 按用户定义计算：
   setup_ps = (t_clk_fall - t_data) * 1000
   hold_ps  = (t_data - t_clk_rise) * 1000
4. report.json schema（时间单位 ps，浮点）:
   {"sampler":"dlatch_falling","n_cycles":N,"vth":0.5,
    "setup_ps":[...],"hold_ps":[...],
    "setup_min_ps":..,"setup_avg_ps":..,"setup_max_ps":..,
    "hold_min_ps":..,"hold_avg_ps":..,"hold_max_ps":..}
   avg 为算术平均，min/max 为数组最值。
5. --out 指定输出路径；缺省写到 stdout（合法 JSON）。
6. 仅用 Python 标准库；无外部依赖；不要硬编码任何具体数值（判分会在隐藏输入 B 上跑，B 的
   周期与数据边沿位置都和 A 不同）。

附件 src/waveform_A.csv 与 src/sampler_spec_A.json 仅供你理解和自测；判分只用隐藏输入 B。
把 sampler_setup_hold.py 打包成 outputs/submit.zip 提交。
"""
with open(os.path.join(ASSET, "prompt.txt"), "w") as f:
    f.write(PROMPT)

os.makedirs(REF, exist_ok=True)
os.makedirs(os.path.join(REF, "hidden_B"), exist_ok=True)
os.makedirs(os.path.join(REF, "negative"), exist_ok=True)

REF_SOL = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sampler_setup_hold.py -- extract D-latch (falling-edge) setup/hold margins
from a sampled waveform CSV, per user irene1li's literal definitions
(trace 1794970973210_fve2x):
  setup_time = t(CLK fall) - t(DATA edge in high phase)   [data -> CLK low]
  hold_time  = t(DATA edge in high phase) - t(CLK rise)   [CLK high -> data]
Usage:
  python3 sampler_setup_hold.py <waveform.csv> <sampler_spec.json> [--out report.json]
Pure standard library.
"""
import sys, os, json, csv, argparse


def read_csv(path, t_col, clk_col, data_col):
    ts, clks, datas = [], [], []
    with open(path, newline="") as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            ts.append(float(row[t_col]))
            clks.append(float(row[clk_col]))
            datas.append(float(row[data_col]))
    return ts, clks, datas


def crossings(ts, sig, vth, direction):
    out = []
    n = len(sig)
    for i in range(1, n):
        a, b = sig[i - 1], sig[i]
        ta, tb = ts[i - 1], ts[i]
        if direction in ("up", "any") and a < vth <= b:
            frac = (vth - a) / (b - a) if b != a else 0.0
            out.append(ta + frac * (tb - ta))
        elif direction in ("down", "any") and a >= vth > b:
            frac = (a - vth) / (a - b) if a != b else 0.0
            out.append(ta + frac * (tb - ta))
    return out


def aggregate(arr):
    return {"min": min(arr), "avg": sum(arr) / len(arr), "max": max(arr)}


def analyze(waveform_csv, spec):
    t_col = spec["t_col"]; clk_col = spec["clk_col"]; data_col = spec["data_col"]
    vth = float(spec.get("vth", 0.5))
    sampler = spec.get("sampler", "dlatch_falling")
    ts, clks, datas = read_csv(waveform_csv, t_col, clk_col, data_col)
    clk_rises = crossings(ts, clks, vth, "up")
    clk_falls = crossings(ts, clks, vth, "down")
    data_edges = crossings(ts, datas, vth, "any")
    setup_ps, hold_ps = [], []
    n_cyc = min(len(clk_rises), len(clk_falls))
    for i in range(n_cyc):
        tr = clk_rises[i]
        tf = None
        for f in clk_falls:
            if f > tr:
                tf = f
                break
        if tf is None:
            continue
        td = None
        for d in data_edges:
            if tr < d < tf:
                td = d
                break
        if td is None:
            continue
        setup_ps.append((tf - td) * 1000.0)
        hold_ps.append((td - tr) * 1000.0)
    sa = aggregate(setup_ps) if setup_ps else {"min": 0, "avg": 0, "max": 0}
    ha = aggregate(hold_ps) if hold_ps else {"min": 0, "avg": 0, "max": 0}
    return {
        "sampler": sampler,
        "n_cycles": len(setup_ps),
        "vth": vth,
        "setup_ps": setup_ps,
        "hold_ps": hold_ps,
        "setup_min_ps": sa["min"], "setup_avg_ps": sa["avg"], "setup_max_ps": sa["max"],
        "hold_min_ps": ha["min"], "hold_avg_ps": ha["avg"], "hold_max_ps": ha["max"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("waveform_csv")
    ap.add_argument("sampler_spec_json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    with open(args.sampler_spec_json) as f:
        spec = json.load(f)
    rep = analyze(args.waveform_csv, spec)
    txt = json.dumps(rep, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(txt + "\n")
    else:
        print(txt)


if __name__ == "__main__":
    main()
'''
with open(os.path.join(REF, SCRIPT), "w") as f:
    f.write(REF_SOL)

write_csv(os.path.join(REF, "hidden_B", "waveform_B.csv"), rows_B)
spec_B = {"sampler": "dlatch_falling", "t_col": "t_ns", "clk_col": "clk",
          "data_col": "data", "vth": VTH, "vdd": VDD}
with open(os.path.join(REF, "hidden_B", "sampler_spec_B.json"), "w") as f:
    json.dump(spec_B, f, indent=2)

MANIFEST = {
    "case_id": CASE,
    "hidden_B": {
        "waveform_B.csv": {
            "sampler": "dlatch_falling",
            "period_ns": P_B,
            "n_cycles": 6,
            "data_offsets_in_high_ns": OFF_B,
            "anti_hardcode_A": "A: period=2.0ns offsets=[0.20,0.35,0.15,0.45,0.25,0.40]; B: period=1.6ns offsets=[0.18,0.30,0.42,0.22,0.38,0.12] -- period & all offsets differ",
        },
        "sampler_spec_B.json": {"sampler": "dlatch_falling", "vth": 0.5, "vdd": 1.0},
    },
    "asset_A": {
        "waveform_A.csv": {"period_ns": P_A, "n_cycles": 6, "data_offsets_in_high_ns": OFF_A},
        "sampler_spec_A.json": {"sampler": "dlatch_falling", "vth": 0.5, "vdd": 1.0},
    },
    "gt_B": {
        "setup_ps": [round(x, 3) for x in GT_B_SETUP],
        "hold_ps":  [round(x, 3) for x in GT_B_HOLD],
        "setup_min_ps": round(min(GT_B_SETUP), 3),
        "setup_avg_ps": round(sum(GT_B_SETUP) / 6, 3),
        "setup_max_ps": round(max(GT_B_SETUP), 3),
        "hold_min_ps": round(min(GT_B_HOLD), 3),
        "hold_avg_ps": round(sum(GT_B_HOLD) / 6, 3),
        "hold_max_ps": round(max(GT_B_HOLD), 3),
    },
    "gt_A": {
        "setup_ps": [round(x, 3) for x in GT_A_SETUP],
        "hold_ps":  [round(x, 3) for x in GT_A_HOLD],
    },
    "tol_ps": 20,
}
with open(os.path.join(REF, "hidden_B", "hidden_manifest.json"), "w") as f:
    json.dump(MANIFEST, f, indent=2)

NEG_NAIVE = r'''#!/usr/bin/env python3
# naive_empty.py -- does nothing (empty shell)
import sys
def main():
    pass
if __name__ == "__main__":
    main()
'''
NEG_PRINT = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# print_only.py -- prints a canned report with A's GT values, ignores inputs.
import sys, json
A = {"sampler":"dlatch_falling","n_cycles":6,"vth":0.5,
 "setup_ps":[800.0,650.0,850.0,550.0,750.0,600.0],
 "hold_ps":[200.0,350.0,150.0,450.0,250.0,400.0],
 "setup_min_ps":550.0,"setup_avg_ps":700.0,"setup_max_ps":850.0,
 "hold_min_ps":150.0,"hold_avg_ps":300.0,"hold_max_ps":450.0}
import argparse
ap=argparse.ArgumentParser(); ap.add_argument("a"); ap.add_argument("b"); ap.add_argument("--out",default=None)
args=ap.parse_args()
txt=json.dumps(A,indent=2)
if args.out:
    open(args.out,"w").write(txt+"\n")
else:
    print(txt)
'''
NEG_CORE = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# core_removed.py -- parses CSV but never computes setup/hold (core deleted); emits zeros.
import sys, json, csv, argparse
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("w"); ap.add_argument("s"); ap.add_argument("--out",default=None)
    a=ap.parse_args()
    with open(a.w, newline="") as f:
        rows=list(csv.DictReader(f))
    rep={"sampler":"dlatch_falling","n_cycles":6,"vth":0.5,
         "setup_ps":[0.0,0.0,0.0,0.0,0.0,0.0],
         "hold_ps":[0.0,0.0,0.0,0.0,0.0,0.0],
         "setup_min_ps":0.0,"setup_avg_ps":0.0,"setup_max_ps":0.0,
         "hold_min_ps":0.0,"hold_avg_ps":0.0,"hold_max_ps":0.0}
    txt=json.dumps(rep,indent=2)
    if a.out: open(a.out,"w").write(txt+"\n")
    else: print(txt)
if __name__=="__main__": main()
'''
NEG_HARD = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# hardcode_a.py -- runs the real algo but forces A's GT values regardless of input.
import sys, json, argparse
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("w"); ap.add_argument("s"); ap.add_argument("--out",default=None)
    a=ap.parse_args()
    rep={"sampler":"dlatch_falling","n_cycles":6,"vth":0.5,
         "setup_ps":[800.0,650.0,850.0,550.0,750.0,600.0],
         "hold_ps":[200.0,350.0,150.0,450.0,250.0,400.0],
         "setup_min_ps":550.0,"setup_avg_ps":700.0,"setup_max_ps":850.0,
         "hold_min_ps":150.0,"hold_avg_ps":300.0,"hold_max_ps":450.0}
    txt=json.dumps(rep,indent=2)
    if a.out: open(a.out,"w").write(txt+"\n")
    else: print(txt)
if __name__=="__main__": main()
'''
for nm, body in [("naive_empty.py", NEG_NAIVE), ("print_only.py", NEG_PRINT),
                 ("core_removed.py", NEG_CORE), ("hardcode_a.py", NEG_HARD)]:
    with open(os.path.join(REF, "negative", nm), "w") as f:
        f.write(body)

CHECK = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py for EDA-Eval-DesignFlow-SamplerSetupHold-001.

check(deliverable, workdir) -> None on PASS, raises AssertionError on FAIL.

Deliverable: submit.zip (or dir) containing `sampler_setup_hold.py` that
extracts D-latch (falling-edge) setup/hold margins from a sampled waveform CSV,
per user irene1li's literal definitions (trace 1794970973210_fve2x @ hfeg0plg58,
mc=113):
  setup_time = t(CLK fall) - t(DATA edge in high phase)   [data -> CLK low]
  hold_time  = t(DATA edge in high phase) - t(CLK rise)   [CLK high -> data]

User's exact words (msg[2]):
  "D锁存器的setup time以及hold up time(setup time就是数据到CLK低电平的时间,
   hold up time就是CLK高电平到数据改变的时间)"

Judging runs the candidate on HIDDEN input B (a different waveform: period 1.6ns
vs A's 2.0ns, different data-edge offsets -- anti-hardcode-A), independently
recomputes GT_B from the CSV with the same threshold/interpolation rule, and
asserts 17 independent conditions (a..q).
"""
import os, re, sys, json, csv, zipfile, shutil, subprocess, tempfile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
HIDDEN_ROOT = os.path.join(HERE, "hidden_B")
B_CSV = os.path.join(HIDDEN_ROOT, "waveform_B.csv")
B_SPEC = os.path.join(HIDDEN_ROOT, "sampler_spec_B.json")
MANIFEST = os.path.join(HIDDEN_ROOT, "hidden_manifest.json")
SCRIPT = "sampler_setup_hold.py"
TOL = 20.0  # ps


def _cond(cid, ok, msg):
    if not ok:
        raise AssertionError("[%s] %s" % (cid, msg))


def extract_script(deliverable, dest):
    if os.path.isdir(deliverable):
        for f in os.listdir(deliverable):
            s = os.path.join(deliverable, f); d = os.path.join(dest, f)
            if os.path.isfile(s): shutil.copy2(s, d)
    else:
        with zipfile.ZipFile(deliverable) as z:
            z.extractall(dest)
    p = os.path.join(dest, SCRIPT)
    return p


def run_cand(script, args, wd):
    try:
        proc = subprocess.run([sys.executable, script] + args,
                              cwd=wd, capture_output=True, text=True, timeout=120)
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"


def read_csv(path, t_col, clk_col, data_col):
    ts, clks, datas = [], [], []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            ts.append(float(row[t_col])); clks.append(float(row[clk_col])); datas.append(float(row[data_col]))
    return ts, clks, datas


def cross(ts, sig, vth, direction):
    out = []
    for i in range(1, len(sig)):
        a, b = sig[i - 1], sig[i]; ta, tb = ts[i - 1], ts[i]
        if direction in ("up", "any") and a < vth <= b:
            out.append(ta + (vth - a) / (b - a) * (tb - ta))
        elif direction in ("down", "any") and a >= vth > b:
            out.append(ta + (a - vth) / (a - b) * (tb - ta))
    return out


def gt_from_csv(wave, spec):
    vth = float(spec.get("vth", 0.5))
    ts, clks, datas = read_csv(wave, spec["t_col"], spec["clk_col"], spec["data_col"])
    rises = cross(ts, clks, vth, "up")
    falls = cross(ts, clks, vth, "down")
    dedges = cross(ts, datas, vth, "any")
    setup, hold = [], []
    for i, tr in enumerate(rises):
        tf = next((f for f in falls if f > tr), None)
        if tf is None: continue
        td = next((d for d in dedges if tr < d < tf), None)
        if td is None: continue
        setup.append((tf - td) * 1000.0)
        hold.append((td - tr) * 1000.0)
    return setup, hold


def gt_aggs(arr):
    return min(arr), sum(arr) / len(arr), max(arr)


def approx(a, b, tol):
    return abs(a - b) <= tol


def check(deliverable, workdir):
    with open(MANIFEST) as f:
        man = json.load(f)
    with open(B_SPEC) as f:
        bspec = json.load(f)
    gtb_setup, gtb_hold = gt_from_csv(B_CSV, bspec)
    gtb_sa = gt_aggs(gtb_setup)
    gtb_ha = gt_aggs(gtb_hold)
    gta_setup = man["gt_A"]["setup_ps"]; gta_hold = man["gt_A"]["hold_ps"]

    with tempfile.TemporaryDirectory(prefix="_chk_ssh_") as td:
        script = extract_script(deliverable, td)
        _cond("a", os.path.isfile(script) and os.path.getsize(script) > 0,
              "submit must contain non-empty %s" % SCRIPT)
        pproc = subprocess.run([sys.executable, "-c",
                                "import py_compile; py_compile.compile(%r, doraise=True)" % script],
                               capture_output=True, text=True)
        _cond("b", pproc.returncode == 0, "py_compile failed: %s" % pproc.stderr)
        rep_path = os.path.join(td, "report.json")
        rc, out, err = run_cand(script, [B_CSV, B_SPEC, "--out", rep_path], td)
        _cond("c", rc == 0 and os.path.isfile(rep_path),
              "script must exit 0 and write report.json on B (rc=%d, err=%s)" % (rc, err[:300]))
        with open(rep_path) as f:
            rep = json.load(f)
        required = ["sampler", "n_cycles", "setup_ps", "hold_ps",
                    "setup_min_ps", "setup_avg_ps", "setup_max_ps",
                    "hold_min_ps", "hold_avg_ps", "hold_max_ps"]
        _cond("d", all(k in rep for k in required) and isinstance(rep["setup_ps"], list)
              and isinstance(rep["hold_ps"], list), "report schema invalid, keys=%s" % list(rep.keys()))
        _cond("e", rep.get("sampler") == "dlatch_falling",
              "sampler must be dlatch_falling, got %r" % rep.get("sampler"))
        _cond("f", rep.get("n_cycles") == 6, "n_cycles must be 6, got %r" % rep.get("n_cycles"))
        _cond("g", len(rep["setup_ps"]) == 6 and len(rep["hold_ps"]) == 6,
              "setup_ps/hold_ps must each have 6 entries, got %d/%d" % (len(rep["setup_ps"]), len(rep["hold_ps"])))
        bad_h = [(i, rep["setup_ps"][i], gtb_setup[i]) for i in range(6)
                 if not approx(float(rep["setup_ps"][i]), gtb_setup[i], TOL)]
        _cond("h", not bad_h, "setup_ps mismatch vs GT_B (tol %.0fps): %s" % (TOL, bad_h[:3]))
        bad_i = [(i, rep["hold_ps"][i], gtb_hold[i]) for i in range(6)
                 if not approx(float(rep["hold_ps"][i]), gtb_hold[i], TOL)]
        _cond("i", not bad_i, "hold_ps mismatch vs GT_B (tol %.0fps): %s" % (TOL, bad_i[:3]))
        rjs = (float(rep["setup_min_ps"]), float(rep["setup_avg_ps"]), float(rep["setup_max_ps"]))
        _cond("j", approx(rjs[0], gtb_sa[0], TOL) and approx(rjs[1], gtb_sa[1], TOL)
              and approx(rjs[2], gtb_sa[2], TOL),
              "setup aggregates mismatch: report=%s GT=%s" % (rjs, gtb_sa))
        rkh = (float(rep["hold_min_ps"]), float(rep["hold_avg_ps"]), float(rep["hold_max_ps"]))
        _cond("k", approx(rkh[0], gtb_ha[0], TOL) and approx(rkh[1], gtb_ha[1], TOL)
              and approx(rkh[2], gtb_ha[2], TOL),
              "hold aggregates mismatch: report=%s GT=%s" % (rkh, gtb_ha))
        close_b = all(approx(float(rep["setup_ps"][i]), gtb_setup[i], TOL) for i in range(6)) and \
                  all(approx(float(rep["hold_ps"][i]), gtb_hold[i], TOL) for i in range(6))
        far_a = any(not approx(float(rep["setup_ps"][i]), gta_setup[i], TOL * 0.5) for i in range(6)) or \
                any(not approx(float(rep["hold_ps"][i]), gta_hold[i], TOL * 0.5) for i in range(6))
        _cond("l", close_b and far_a,
              "anti-hardcode: report must match GT_B not GT_A (close_b=%s far_a=%s)" % (close_b, far_a))

        def neg_fail(negname):
            neg = os.path.join(HERE, "negative", negname)
            target = os.path.join(td, SCRIPT)
            shutil.copy2(neg, target)
            rp = os.path.join(td, "rep_%s.json" % negname)
            rc2, _, _ = run_cand(target, [B_CSV, B_SPEC, "--out", rp], td)
            if rc2 != 0:
                return True
            if not os.path.isfile(rp):
                return True
            try:
                with open(rp) as f:
                    nr = json.load(f)
            except Exception:
                return True
            if nr.get("n_cycles") != 6 or len(nr.get("setup_ps", [])) != 6 or len(nr.get("hold_ps", [])) != 6:
                return True
            if any(not approx(float(nr["setup_ps"][i]), gtb_setup[i], TOL) for i in range(6)):
                return True
            if any(not approx(float(nr["hold_ps"][i]), gtb_hold[i], TOL) for i in range(6)):
                return True
            return False

        _cond("m1", neg_fail("naive_empty.py"), "naive_empty must FAIL")
        _cond("m2", neg_fail("print_only.py"), "print_only (canned A values) must FAIL")
        _cond("m3", neg_fail("core_removed.py"), "core_removed must FAIL")
        _cond("m4", neg_fail("hardcode_a.py"), "hardcode_a must FAIL")

        shutil.copy2(os.path.join(HERE, SCRIPT), os.path.join(td, SCRIPT))
        hashes = []
        for sd in (1, 2, 3):
            rp = os.path.join(td, "det_%d.json" % sd)
            rcd, _, _ = run_cand(os.path.join(td, SCRIPT), [B_CSV, B_SPEC, "--out", rp], td)
            if rcd != 0 or not os.path.isfile(rp):
                hashes.append("ERR")
            else:
                hashes.append(hashlib.sha256(open(rp, "rb").read()).hexdigest())
        _cond("o", len(set(hashes)) == 1 and hashes[0] != "ERR",
              "3-seed report not byte-identical: %s" % hashes)

    return True


if __name__ == "__main__":
    deliv = sys.argv[1] if len(sys.argv) > 1 else None
    wd = sys.argv[2] if len(sys.argv) > 2 else "."
    if not deliv:
        print("usage: check.py <submit.zip|dir> [workdir]", file=sys.stderr); sys.exit(2)
    try:
        check(deliv, wd)
        print("PASS")
    except AssertionError as ex:
        print("FAIL: %s" % ex); sys.exit(1)
'''
with open(os.path.join(REF, "check.py"), "w") as f:
    f.write(CHECK)

NEGSELF = r'''#!/usr/bin/env python3
"""negative_selftest.py -- package reference + each negative as submit.zip and
run check.py. Reference MUST PASS; all negatives MUST FAIL.
exit 0 if all expectations hold, else 1.
"""
import os, sys, zipfile, tempfile, subprocess, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "sampler_setup_hold.py")
CHECK = os.path.join(HERE, "check.py")
NEG_DIR = os.path.join(HERE, "negative")
NEGATIVES = ["naive_empty.py", "print_only.py", "core_removed.py", "hardcode_a.py"]
SCRIPT = "sampler_setup_hold.py"


def make_zip(src, zp):
    with zipfile.ZipFile(zp, "w") as z:
        z.write(src, arcname=SCRIPT)


def run_check(zp, wd):
    p = subprocess.run([sys.executable, CHECK, zp, wd], capture_output=True, text=True, timeout=300)
    return p.returncode, (p.stdout + "\n" + p.stderr).strip()


fails = []
with tempfile.TemporaryDirectory(prefix="_negselftest_ssh_") as td:
    zr = os.path.join(td, "ref.zip"); make_zip(REF, zr)
    rc, out = run_check(zr, td)
    print("PASS  reference (rc=0)" if rc == 0 else "FAIL  reference (rc=%d):%s" % (rc, out))
    if rc != 0: fails.append("reference")
    for n in NEGATIVES:
        z = os.path.join(td, "neg_%s.zip" % n); make_zip(os.path.join(NEG_DIR, n), z)
        rc, out = run_check(z, td)
        if rc != 0:
            print("PASS  negative %s FAILed as expected" % n)
        else:
            print("FAIL  negative %s passed (should have failed)" % n); fails.append(n)
sys.exit(0 if not fails else 1)
'''
with open(os.path.join(REF, "negative_selftest.py"), "w") as f:
    f.write(NEGSELF)

with open(os.path.join(REF, "check.py")) as f:
    check_src = f.read()

TRACE_SUMMARY = ("irene1li 在 hfeg0plg58 上用 FineSim 跑 CXMT m2701 V0_DDR4 sim_CkDcaMux24to1 "
 "(24to1 mux + PRBS)，分析 24to1 中 IO_DataLat D 锁存器(下降沿采样)的 setup/hold 采样裕度。"
 "131 msg session, mc=113, hspice:302/netlist:509/schematic:337/waveview:90。msg[2] 用户给出"
 " D 锁存器 setup/hold 定义：setup=数据到CLK低电平, hold=CLK高电平到数据改变。agent 全程在"
 "试读 18GB FSDB(哈希化扁平节点名)，fscript/Verdi/wv 均难寻址内部信号，最终未交付测量。"
 "本 case 取用户 msg[2] 的真实分析意图(从波形按其定义提取 setup/hold)，把 CLK/DATA 采样波形"
 "导成 CSV，交付纯 Python 工具按用户定义计算 margins。A 档 trace-faithful。")

K_RATIONALE = ("17 条断言：①submit.zip含 sampler_setup_hold.py + report.json 非空 "
 "②sampler_setup_hold.py py_compile 通过 ③脚本在隐藏输入 B 上 subprocess exit 0 并写 report.json "
 "④report schema 合法(sampler/n_cycles/setup_ps/hold_ps/setup_min/avg/max/hold_min/avg/max) "
 "⑤report.sampler==dlatch_falling ⑥report.n_cycles==6 ⑦setup_ps 与 hold_ps 各 6 个元素 "
 "⑧每个 setup_ps 在 GT_B ±20ps 内 ⑨每个 hold_ps 在 GT_B ±20ps 内 ⑩setup_min/avg/max==GT_B 聚合 "
 "⑪hold_min/avg/max==GT_B 聚合 ⑫跨输入防背题:report 近 GT_B 且远 GT_A(否决 hardcode-A) "
 "⑬naive_empty 必 FAIL ⑭print_only(灌 A 值)必 FAIL ⑮core_removed 必 FAIL ⑯hardcode_a 必 FAIL "
 "⑰3 个随机种子重跑 report.json sha256 一致(确定性)")

case = {
    "task_id": CASE,
    "id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": PROMPT,
    "task_brief": PROMPT,
    "attachments": ["assets/%s/src/waveform_A.csv" % CASE,
                    "assets/%s/src/sampler_spec_A.json" % CASE,
                    "assets/%s/prompt.txt" % CASE],
    "test": check_src,
    "metadata": {
        "domain": "spice_sim",
        "track": "B",
        "layer": "L1",
        "trace_source": {
            "user": "irene1li",
            "host": "hfeg0plg58",
            "ip": "10.129.32.75",
            "session_file": "1794970973210_fve2x.messages.json",
            "match_count": 113,
            "scan_snapshot": "ssh_eda_search_20261120_145529/summary.tsv -> summary_1120_reconstructed.tsv (r944 B-shard mc>=10 pool=2072 fresh=309 pre-claim)",
            "real_task_summary": TRACE_SUMMARY,
        },
        "test_rationale": K_RATIONALE,
        "k_rationale": 17,
        "k_check": 17,
        "deliverable": "outputs/submit.zip containing sampler_setup_hold.py",
        "hidden_input": "reference/%s/hidden_B/waveform_B.csv (period 1.6ns, offsets differ from A) + sampler_spec_B.json" % CASE,
    },
}
os.makedirs(CASES_B, exist_ok=True)
with open(os.path.join(CASES_B, CASE + ".json"), "w") as f:
    json.dump(case, f, ensure_ascii=False, indent=2)

print("Built. GT_A setup:", [round(x, 1) for x in GT_A_SETUP], "hold:", [round(x, 1) for x in GT_A_HOLD])
print("GT_B setup:", [round(x, 1) for x in GT_B_SETUP], "hold:", [round(x, 1) for x in GT_B_HOLD])
print("manifest gt_B:", MANIFEST["gt_B"])
print("OK")
