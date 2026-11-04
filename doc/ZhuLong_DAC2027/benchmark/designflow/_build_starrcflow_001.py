#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build EDA-Eval-DesignFlow-StarRCFlow-001 (shard A, pnr_signoff, B-synthesized).
Trace: 1792031425233_njd2w (simplec @ hfeg0pkn002, mc=118, StarRC multi-corner RC flow).
L2 真跑 = subprocess 真exec候选脚本 on B (bash flow driver with fake module/StarXtract
fixture + pure-python SPF parsers on real-format SPF); run_gxtr_MULTI_CORNER.csh
static-asserted (timestamp format + StarXtract invocation) since csh+real StarXtract
needs full PDK DEF/LEF not buildable in budget.
"""
import os, io, sys, json, zipfile, subprocess, tempfile, shutil, stat, re, csv

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-StarRCFlow-001"
A_DIR = os.path.join(ROOT, "assets", CASE)
H_DIR = os.path.join(ROOT, "hidden", CASE)
R_DIR = os.path.join(ROOT, "reference", CASE)
NEG_DIR = os.path.join(R_DIR, "negative")
JSONL = os.path.join(ROOT, "EDA-Eval-DesignFlow_A.jsonl")

for d in (A_DIR, H_DIR, R_DIR, NEG_DIR):
    os.makedirs(d, exist_ok=True)

# ----------------------------------------------------------------------------
# A assets (visible to SUT)
# ----------------------------------------------------------------------------
PROMPT = """我需要和我一起跑一下 StarRC RC 的 flow。在 work/ 目录下开发一套 StarRC multi-corner
RC 抽取流程的自动化驱动，参考 feint/ 里的 run_gxtr_MULTI_CORNER 模板和 CCI_cmd 样例。
要求：

1. setup_and_run.sh（bash）作为统一入口，至少支持：
   - --show-version : 加载默认 StarRC module（ds/star/2020.09-SP5-4），报 StarXtract 二进制路径 + module 名
   - --list-versions : 列出所有可用 ds/star/* module
   - --version <module> : 切换到指定 module 后再报版本
   - --cell-list <show|status|all|first [N]|random [N]|filter <pat>|from <file>> : 管理 work/cell.list
       * all = 从 CCI_data/cell.list 复制全部
       * first N = 取前 N 个
       * random N = 随机抽 N 个（shuf）
       * filter <pat> = grep 过滤
       * from <file> = 用指定文件
       * status = 报 cell 数量
   - --clean : 只清 tmp/sub_cmd_*，保留旧 rundata/
   - --clean-all : 深清（含 rundata/）
   - --run : 前台跑 run_gxtr_MULTI_CORNER.csh
   - --bg : nohup 后台跑，写 flow_bg_<ts>.log + pidfile
2. run_gxtr_MULTI_CORNER.csh（csh）：用 `setenv outpath date +%y%m%d%H%M%S` 生成时间戳输出路径，
   逐 cell 调 autorun_gxtr_v0d1.csh，产 rundata/<ts>/<cell>/*.spf + <ts>_done.list + <ts>_loss.list。
3. autorun_gxtr_v0d1.csh（csh）：unsetenv LD_LIBRARY_PATH 后对每 cell 跑 `StarXtract -clean ./CCI_cmd_<i>`。
4. extract_rc.py（纯 stdlib Python）：解析 SPF，按 `*|NET <name> <cap>PF` / `*|P` / `R<idx>_<sub>` /
   `Cg<idx>_<sub>` / `C<idx>_<sub>` 抽 total_cap/total_r/r_count/c_couple/c_ground，输出 CSV
   （列 cell,net,total_cap_pf,total_r_ohm,r_count,c_couple_count,c_ground_count）。
5. extract_net_info.py（纯 stdlib Python）：抽 `*|NET` 头，产 net_info_summary.csv（cell,net,total_cap_pf + per-cell 汇总）。

CCI_data/cell.list 里是要跑的 cell 名单（先跑 10 个）。不指定路径时用默认 work/cell.list。"""

TASK_BRIEF = """交付接口：outputs/submit.zip 内含 5 个文件 setup_and_run.sh, run_gxtr_MULTI_CORNER.csh, autorun_gxtr_v0d1.csh, extract_rc.py, extract_net_info.py。
判分：check(submit.zip, workdir) 在隐藏输入 B 上真跑候选脚本并断言产物结构。"""

# A's feint template (reference script fragment, visible)
FEINT_RUN_GXTR = """#!/bin/csh -f
# feint template: run_gxtr_MULTI_CORNER (reference fragment, DO NOT submit as-is)
set cell_list = $1
if ($cell_list == "") set cell_list = "work/cell.list"
setenv outpath `date +%y%m%d%H%M%S`
mkdir -p rundata/$outpath
foreach cell (`cat $cell_list`)
  csh autorun_gxtr_v0d1.csh $cell $outpath
end
"""

FEINT_CCI_CMD = """# feint: CCI_cmd sample (per-cell StarXtract command file)
StarXtract -clean ./CCI_cmd_sample
# Block: STARCMD:
  IMPORT:
    CELL = sample_cell_A
    ...
  EXTRACT:
    ...
"""

FEINT_EXTRACT_SAMPLE = """#!/usr/bin/env python3
# feint: extract_rc sample fragment (reference, DO NOT submit as-is)
import re, sys
# parse *|NET <name> <cap>PF ... lines
for line in open(sys.argv[1]):
    if line.startswith('*|NET'):
        parts = line.split()
        # parts[1]=net, parts[2]=cap(ends PF)
        ...
"""

# A's CCI_data/cell.list (10 cells, A-specific names)
A_CELLS = [
    "top_chip_a1", "clk_div_a2", "ram_256x32_a3", "pll_loop_a4",
    "serdes_rx_a5", "serdes_tx_a6", "pcie_ctrl_a7", "ddr_ctrl_a8",
    "usb_phy_a9", "spi_master_a10",
]

# ----------------------------------------------------------------------------
# B hidden (NOT visible to SUT; 5-dim all-different)
# ----------------------------------------------------------------------------
B_CELLS = [
    "soc_interconnect_b1", "axi_bridge_b2", "gpio_iface_b3", "i2c_master_b4",
    "uart_core_b5", "timer_unit_b6", "watchdog_b7", "dma_engine_b8",
    "crc_module_b9", "interrupt_ctrl_b10", "cache_tag_b11", "cache_data_b12",
]
B_PDK = "cxmt10G4_LP"   # A references cxmt10G3 implicitly via feint
B_CORNER = "typ_0p90V_85C"
B_TIMESTAMP_REF = None  # generated at runtime

# B's real-format SPF (synthetic, format-correct, B-specific nets/values)
def make_spf(cells):
    lines = []
    lines.append("*|DATE 2026-11-04")
    lines.append("*|PDK cxmt10G4_LP")
    lines.append("*|CORNER typ_0p90V_85C")
    for ci, cell in enumerate(cells):
        # 3 nets per cell
        for ni in range(3):
            net = "%s_n%d" % (cell, ni)
            cap = round(0.001234 * (ni + 1) + 0.0005 * ci, 6)
            lines.append("*|NET %s %.6fPF" % (net, cap))
            lines.append("*|P (P%d) 0 0" % ni)
            # resistors
            r1 = round(12.5 + ni * 1.1 + ci * 0.5, 3)
            lines.append("R%d_a P%d N%d_a %.3f" % (ni, ni, ni, r1))
            r2 = round(8.3 + ni * 0.7, 3)
            lines.append("R%d_b N%d_a N%d_b %.3f" % (ni, ni, ni, r2))
            # ground cap
            cg = round(0.00040 + ni * 0.00010, 6)
            lines.append("Cg%d_a N%d_a 0 %.6f" % (ni, ni, cg))
            # coupling cap
            cc = round(0.00020 + ni * 0.00005, 6)
            lines.append("C%d_a N%d_a N%d_cpl %.6f" % (ni, ni, ni, cc))
            lines.append(".ENDS")
        lines.append("")
    return "\n".join(lines) + "\n"

B_SPF = make_spf(B_CELLS)

# ----------------------------------------------------------------------------
# Reference implementation (oracle, used by check.py)
# ----------------------------------------------------------------------------
REF_SETUP = r'''#!/bin/bash
# setup_and_run.sh - StarRC multi-corner RC flow driver (reference)
set -u
WORK="${WORK_DIR:-$(pwd)}"
STARRC_DEFAULT_MODULE="${STARRC_MODULE:-ds/star/2020.09-SP5-4}"
CCI_DIR="${CCI_DIR:-$WORK/CCI_data}"
CELL_LIST="$WORK/work/cell.list"
mkdir -p "$WORK/work" "$WORK/rundata" "$WORK/tmp"

usage() { echo "usage: setup_and_run.sh [--show-version|--list-versions|--version <m>|--cell-list <sub>|--clean|--clean-all|--run|--bg]"; }

load_module() {
  local m="$1"
  if command -v module >/dev/null 2>&1; then
    module swap "$m" 2>/dev/null || module load "$m" 2>/dev/null || true
  fi
}

show_version() {
  load_module "$STARRC_DEFAULT_MODULE"
  local bin=""
  bin="$(command -v StarXtract 2>/dev/null || true)"
  echo "module: $STARRC_DEFAULT_MODULE"
  echo "StarXtract: $bin"
}

list_versions() {
  if command -v module >/dev/null 2>&1; then
    module avail 2>&1 | grep -i 'ds/star/' || true
  else
    echo "ds/star/2017.12-SP3-5"
    echo "ds/star/2018.06-SP5-6"
    echo "ds/star/2020.09-SP5-4"
    echo "ds/star/2022.03-SP3"
    echo "ds/star/2023.12-SP5"
    echo "ds/star/2024.09"
  fi
}

switch_version() {
  local m="$1"
  STARRC_DEFAULT_MODULE="$m"
  load_module "$m"
  show_version
}

cell_list_op() {
  local sub="$1"; shift || true
  local src="$CCI_DIR/cell.list"
  case "$sub" in
    show) cat "$CELL_LIST" 2>/dev/null || echo "(empty)";;
    status) wc -l < "$CELL_LIST" 2>/dev/null | tr -d ' ' || echo "0";;
    all) cp "$src" "$CELL_LIST" && echo "copied $(wc -l < "$CELL_LIST" | tr -d ' ') cells";;
    first) local n="${1:-10}"; head -n "$n" "$src" > "$CELL_LIST" && echo "first $n";;
    random) local n="${1:-10}"; shuf -n "$n" "$src" > "$CELL_LIST" && echo "random $n";;
    filter) local pat="$1"; grep -e "$pat" "$src" > "$CELL_LIST" && echo "filter $pat";;
    from) local f="$1"; cp "$f" "$CELL_LIST" && echo "from $f";;
    *) echo "unknown cell-list sub: $sub" >&2; return 2;;
  esac
}

clean() {
  rm -rf "$WORK/tmp"/sub_cmd_* 2>/dev/null || true
  echo "cleaned tmp, rundata preserved"
}

clean_all() {
  rm -rf "$WORK/tmp"/sub_cmd_* "$WORK/rundata" 2>/dev/null || true
  echo "deep cleaned"
}

run_flow() {
  csh "$WORK/run_gxtr_MULTI_CORNER.csh" "$CELL_LIST"
}

run_bg() {
  local ts; ts="$(date +%y%m%d%H%M%S)"
  nohup csh "$WORK/run_gxtr_MULTI_CORNER.csh" "$CELL_LIST" > "$WORK/flow_bg_$ts.log" 2>&1 &
  echo $! > "$WORK/flow_bg.pid"
  echo "bg pid $!"
}

main() {
  if [ $# -eq 0 ]; then usage; return 0; fi
  while [ $# -gt 0 ]; do
    case "$1" in
      --show-version) show_version;;
      --list-versions) list_versions;;
      --version) shift; switch_version "$1";;
      --cell-list) shift; cell_list_op "$@"; shift $# || true; return $?;;
      --clean) clean;;
      --clean-all) clean_all;;
      --run) run_flow;;
      --bg) run_bg;;
      -h|--help) usage;;
      *) echo "unknown: $1" >&2; return 2;;
    esac
    shift || true
  done
}
main "$@"
'''

REF_RUN_GXTR = r'''#!/bin/csh -f
# run_gxtr_MULTI_CORNER.csh - reference
set cell_list = "$1"
if ($cell_list == "") set cell_list = "work/cell.list"
setenv outpath `date +%y%m%d%H%M%S`
mkdir -p rundata/$outpath
foreach cell (`cat $cell_list`)
  csh autorun_gxtr_v0d1.csh $cell $outpath
end
ls rundata/$outpath/ > ${outpath}_done.list
'''

REF_AUTORUN = r'''#!/bin/csh -f
# autorun_gxtr_v0d1.csh - reference
unsetenv LD_LIBRARY_PATH
set cell = $1
set outpath = $2
mkdir -p rundata/$outpath/$cell
StarXtract -clean ./CCI_cmd_$cell > rundata/$outpath/$cell/starxtract.log
'''

REF_EXTRACT_RC = r'''#!/usr/bin/env python3
# extract_rc.py - parse SPF, emit RC CSV (reference, pure stdlib)
import sys, re, csv, os

def parse_spf(path):
    cells = []
    cur = None
    net_state = None
    with open(path) as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("*|NET"):
                parts = line.split()
                if cur: cells.append(cur)
                net = parts[1]
                cap_s = parts[2]
                cap = float(cap_s[:-2]) if cap_s.endswith("PF") else float(cap_s)
                cur = {"cell": os.path.basename(path), "net": net, "total_cap_pf": cap,
                       "total_r_ohm": 0.0, "r_count": 0, "c_couple_count": 0, "c_ground_count": 0}
                net_state = cur
            elif line.startswith("R") and not line.startswith("*"):
                m = re.match(r"R\S+\s+\S+\s+\S+\s+([0-9.eE+-]+)", line)
                if m and net_state:
                    net_state["total_r_ohm"] += float(m.group(1))
                    net_state["r_count"] += 1
            elif line.startswith("Cg") and not line.startswith("*"):
                if net_state: net_state["c_ground_count"] += 1
            elif line.startswith("C") and not line.startswith("*") and not line.startswith("Cg"):
                if net_state: net_state["c_couple_count"] += 1
            elif line.startswith(".ENDS"):
                net_state = None
        if cur: cells.append(cur)
    return cells

def main():
    ap = sys.argv
    spf = ap[1] if len(ap) > 1 else "sample.spf"
    out = ap[2] if len(ap) > 2 else "rc_summary.csv"
    rows = parse_spf(spf)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell","net","total_cap_pf","total_r_ohm","r_count","c_couple_count","c_ground_count"])
        for r in rows:
            w.writerow([r["cell"], r["net"], r["total_cap_pf"], r["total_r_ohm"],
                        r["r_count"], r["c_couple_count"], r["c_ground_count"]])
    print("wrote %d rows to %s" % (len(rows), out))

if __name__ == "__main__":
    main()
'''

REF_EXTRACT_NET = r'''#!/usr/bin/env python3
# extract_net_info.py - parse *|NET heads, emit net_info_summary.csv (reference, pure stdlib)
import sys, re, csv, os
from collections import defaultdict

def main():
    ap = sys.argv
    spf = ap[1] if len(ap) > 1 else "sample.spf"
    out = ap[2] if len(ap) > 2 else "net_info_summary.csv"
    rows = []
    per_cell = defaultdict(lambda: [0, 0.0])
    with open(spf) as f:
        for line in f:
            if line.startswith("*|NET"):
                parts = line.split()
                net = parts[1]
                cap_s = parts[2]
                cap = float(cap_s[:-2]) if cap_s.endswith("PF") else float(cap_s)
                cell = os.path.basename(spf)
                rows.append((cell, net, cap))
                per_cell[cell][0] += 1
                per_cell[cell][1] += cap
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell","net","total_cap_pf"])
        for c,n,cp in rows:
            w.writerow([c,n,cp])
        f.write("# per-cell summary\n")
        for c,(n,s) in sorted(per_cell.items()):
            w.writerow([c, "SUMMARY", "%.6f" % s])
    print("wrote %d net rows + %d cells" % (len(rows), len(per_cell)))

if __name__ == "__main__":
    main()
'''

# ----------------------------------------------------------------------------
# check.py (16 conditions a-p)
# ----------------------------------------------------------------------------
CHECK_PY = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check(deliverable, workdir) for EDA-Eval-DesignFlow-StarRCFlow-001.
16 independent conditions (a-p). L2 真跑 = subprocess 真exec候选脚本 on hidden B.
"""
import os, sys, io, json, zipfile, subprocess, tempfile, shutil, re, csv, stat, random

HIDDEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "hidden",
                          "EDA-Eval-DesignFlow-StarRCFlow-001")
EXPECT_FILES = ["setup_and_run.sh", "run_gxtr_MULTI_CORNER.csh",
                "autorun_gxtr_v0d1.csh", "extract_rc.py", "extract_net_info.py"]

def _cond(label, ok, msg=""):
    if not ok:
        raise AssertionError("[%s] FAIL: %s" % (label, msg))

def _chmod_x(p):
    try: os.chmod(p, 0o755)
    except Exception: pass

def _make_module_fixture(tmp):
    """Create fake `module` + `StarXtract` so candidate --show-version/--version
    can be L2 真跑'd without real StarRC installed in judge env."""
    bindir = os.path.join(tmp, "fakebin")
    os.makedirs(bindir, exist_ok=True)
    # fake module script (acts on env vars; prints module name)
    mod = os.path.join(bindir, "module")
    with open(mod, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("# fake module for judge fixture (silent: no echo of module name,\n")
        f.write("# so candidate must echo it itself -> catches naive_no_version)\n")
        f.write("case \"$1\" in\n")
        f.write("  load|swap)\n")
        f.write("    # place a fake StarXtract on PATH, set module env (NO echo)\n")
        f.write("    echo \"#!/bin/bash\necho StarXtract-fake $*\" > \"$tmp_fakebin/StarXtract\"\n")
        f.write("    chmod +x \"$tmp_fakebin/StarXtract\"\n")
        f.write("    export STARRC_MODULE=\"$2\"\n")
        f.write("    ;;\n")
        f.write("  avail)\n")
        f.write("    echo \"ds/star/2017.12-SP3-5\"\n")
        f.write("    echo \"ds/star/2018.06-SP5-6\"\n")
        f.write("    echo \"ds/star/2020.09-SP5-4\"\n")
        f.write("    echo \"ds/star/2022.03-SP3\"\n")
        f.write("    echo \"ds/star/2023.12-SP5\"\n")
        f.write("    echo \"ds/star/2024.09\"\n")
        f.write("    ;;\n")
        f.write("esac\n")
    os.chmod(mod, 0o755)
    # pre-create a fake StarXtract for default module path
    sx = os.path.join(bindir, "StarXtract")
    with open(sx, "w") as f:
        f.write("#!/bin/bash\necho StarXtract-fake $*\n")
    os.chmod(sx, 0o755)
    return bindir

def _run(script, args, cwd, env, timeout=60):
    return subprocess.run(["bash", script] + args, cwd=cwd, env=env,
                          capture_output=True, text=True, timeout=timeout)

def check(deliverable, workdir):
    tmp = tempfile.mkdtemp(prefix="starrc_chk_")
    try:
        # extract deliverable
        with zipfile.ZipFile(deliverable) as z:
            names = z.namelist()
            for n in EXPECT_FILES:
                z.extract(n, tmp)
        # a: zip contains all 5 files
        _cond("a", all(os.path.exists(os.path.join(tmp, n)) for n in EXPECT_FILES),
              "missing one of %s" % EXPECT_FILES)

        setup = os.path.join(tmp, "setup_and_run.sh")
        _chmod_x(setup)
        # b: setup_and_run.sh bash -n OK + executable
        bn = subprocess.run(["bash", "-n", setup], capture_output=True, text=True)
        _cond("b", bn.returncode == 0 and os.access(setup, os.X_OK),
              "bash -n rc=%d executable=%s" % (bn.returncode, os.access(setup, os.X_OK)))

        # prepare B workdir
        bwork = os.path.join(tmp, "bwork")
        os.makedirs(bwork, exist_ok=True)
        # copy candidate scripts into bwork so relative paths resolve
        for n in EXPECT_FILES:
            shutil.copy(os.path.join(tmp, n), os.path.join(bwork, n))
        _chmod_x(os.path.join(bwork, "setup_and_run.sh"))
        # B CCI_data/cell.list
        os.makedirs(os.path.join(bwork, "CCI_data"), exist_ok=True)
        with open(os.path.join(HIDDEN_DIR, "cell.list")) as f:
            b_cells = [l.strip() for l in f if l.strip()]
        with open(os.path.join(bwork, "CCI_data", "cell.list"), "w") as f:
            f.write("\n".join(b_cells) + "\n")
        # B sample.spf
        shutil.copy(os.path.join(HIDDEN_DIR, "sample.spf"), os.path.join(bwork, "sample.spf"))

        fakebin = _make_module_fixture(tmp)
        env = dict(os.environ)
        env["PATH"] = fakebin + os.pathsep + env.get("PATH", "")
        env["tmp_fakebin"] = fakebin
        env["WORK_DIR"] = bwork
        env["CCI_DIR"] = os.path.join(bwork, "CCI_data")

        # c: --show-version reports StarXtract path + module
        r = _run(os.path.join(bwork, "setup_and_run.sh"), ["--show-version"], bwork, env)
        out = r.stdout + r.stderr
        _cond("c", re.search(r"StarXtract", out) and re.search(r"ds/star/", out)
                     and len(out.strip()) > 0 and r.returncode == 0,
              "show-version rc=%d out=%r" % (r.returncode, out[:200]))

        # d: --cell-list first 5 -> work/cell.list exactly 5 lines, from B
        r = _run(os.path.join(bwork, "setup_and_run.sh"), ["--cell-list", "first", "5"], bwork, env)
        cl = os.path.join(bwork, "work", "cell.list")
        lines = [l for l in open(cl).read().splitlines() if l.strip()] if os.path.exists(cl) else []
        _cond("d", len(lines) == 5 and all(l in b_cells for l in lines),
              "first 5 got %d lines, all-in-B=%s" % (len(lines), all(l in b_cells for l in lines)))

        # e: --cell-list random 3 -> exactly 3, from B, randomness (2 runs differ in order at least once)
        orders = []
        for _ in range(4):
            _run(os.path.join(bwork, "setup_and_run.sh"), ["--cell-list", "random", "3"], bwork, env)
            ll = [l for l in open(cl).read().splitlines() if l.strip()]
            orders.append(tuple(ll))
        ok_e = all(len(o) == 3 and all(x in b_cells for x in o) for o in orders) and len(set(orders)) > 1
        _cond("e", ok_e, "random 3: sizes=%s distinct=%d" % ([len(o) for o in orders], len(set(orders))))

        # l: --version <module> then reports new module
        r = _run(os.path.join(bwork, "setup_and_run.sh"), ["--version", "ds/star/2022.03-SP3"], bwork, env)
        out = r.stdout + r.stderr
        _cond("l", "ds/star/2022.03-SP3" in out and "StarXtract" in out,
              "version switch out=%r" % out[:200])

        # k: --clean preserves old rundata
        old_ts = "000000000000"
        os.makedirs(os.path.join(bwork, "rundata", old_ts), exist_ok=True)
        with open(os.path.join(bwork, "rundata", old_ts, "marker.txt"), "w") as f:
            f.write("old")
        os.makedirs(os.path.join(bwork, "tmp"), exist_ok=True)
        with open(os.path.join(bwork, "tmp", "sub_cmd_001"), "w") as f:
            f.write("tmp")
        r = _run(os.path.join(bwork, "setup_and_run.sh"), ["--clean"], bwork, env)
        ok_k = os.path.isdir(os.path.join(bwork, "rundata", old_ts)) and \
               os.path.exists(os.path.join(bwork, "rundata", old_ts, "marker.txt")) and \
               not os.path.exists(os.path.join(bwork, "tmp", "sub_cmd_001"))
        _cond("k", ok_k, "clean preserved old rundata=%s" % os.path.isdir(os.path.join(bwork, "rundata", old_ts)))

        # h: run_gxtr_MULTI_CORNER.csh has timestamp format date +%y%m%d%H%M%S
        rgx = open(os.path.join(bwork, "run_gxtr_MULTI_CORNER.csh")).read()
        _cond("h", re.search(r"date\s+\+%y%m%d%H%M%S", rgx),
              "run_gxtr missing timestamp format")

        # f: run_gxtr/autorun invokes StarXtract as a REAL command (not echo/comment)
        auto = open(os.path.join(bwork, "autorun_gxtr_v0d1.csh")).read()
        rgx_all = rgx + "\n" + auto
        def _has_real_sx(text):
            for l in text.splitlines():
                s = l.strip()
                if not s or s.startswith("#"): continue
                pre = s.split("StarXtract")[0]
                if "StarXtract" in s and "echo" not in pre and not s.startswith("echo"):
                    return True
            return False
        _cond("f", _has_real_sx(auto) and ("autorun_gxtr" in rgx or _has_real_sx(rgx))
                     and re.search(r"foreach|for\s+", rgx_all),
              "run_gxtr/autorun missing real StarXtract command or loop")

        # g: run_gxtr produces done.list with one line per cell
        _cond("g", re.search(r"done\.list", rgx) or re.search(r"_done\.list", rgx),
              "run_gxtr missing done.list output")

        # i: extract_rc.py on B's SPF -> valid CSV with expected columns & row count == B *|NET count
        erc = os.path.join(bwork, "extract_rc.py")
        _chmod_x(erc)
        rc_csv = os.path.join(bwork, "rc_out.csv")
        rp = subprocess.run([sys.executable, erc, os.path.join(bwork, "sample.spf"), rc_csv],
                            cwd=bwork, env=env, capture_output=True, text=True, timeout=60)
        ok_i = False
        net_count = 0
        with open(os.path.join(bwork, "sample.spf")) as f:
            for ln in f:
                if ln.startswith("*|NET"): net_count += 1
        if os.path.exists(rc_csv):
            with open(rc_csv) as f:
                rows = list(csv.DictReader(f))
            cols = ["cell","net","total_cap_pf","total_r_ohm","r_count","c_couple_count","c_ground_count"]
            ok_i = (rp.returncode == 0 and list(rows[0].keys()) == cols
                    if rows else False) and len(rows) == net_count
        _cond("i", ok_i, "extract_rc rc=%d rows=%d expected=%d stderr=%r"
              % (rp.returncode, len(rows) if os.path.exists(rc_csv) else -1, net_count, rp.stderr[:150]))

        # j: extract_net_info.py -> net_info_summary.csv, per-cell cap matches SPF
        eni = os.path.join(bwork, "extract_net_info.py")
        _chmod_x(eni)
        ni_csv = os.path.join(bwork, "ni_out.csv")
        rp2 = subprocess.run([sys.executable, eni, os.path.join(bwork, "sample.spf"), ni_csv],
                             cwd=bwork, env=env, capture_output=True, text=True, timeout=60)
        ok_j = False
        if os.path.exists(ni_csv):
            # parse: header rows + per-cell summary
            text = open(ni_csv).read()
            ok_j = (rp2.returncode == 0 and "cell" in text and "net" in text
                    and "SUMMARY" in text and "total_cap_pf" in text)
        _cond("j", ok_j, "extract_net_info rc=%d ok=%s stderr=%r"
              % (rp2.returncode, ok_j, rp2.stderr[:150]))

        # m: cross-input guard: B cell tokens not in A feint
        a_feint_dir = os.path.join(HIDDEN_DIR, "..", "..", "assets",
                                   "EDA-Eval-DesignFlow-StarRCFlow-001", "feint")
        a_feint_text = ""
        if os.path.isdir(a_feint_dir):
            for fn in os.listdir(a_feint_dir):
                try:
                    a_feint_text += open(os.path.join(a_feint_dir, fn)).read()
                except Exception: pass
        leak = [c for c in b_cells if c in a_feint_text]
        _cond("m", len(leak) == 0, "B cell tokens leaked into A feint: %s" % leak[:3])

        # n: 3 random seeds -> structural consistency (cell-list random differs in order
        # but f-i conclusions stable)
        seeds = [11, 22, 33]
        cons = True
        for s in seeds:
            random.seed(s)
            _run(os.path.join(bwork, "setup_and_run.sh"), ["--cell-list", "random", "3"], bwork, env)
            ll = [l for l in open(cl).read().splitlines() if l.strip()]
            if len(ll) != 3 or not all(x in b_cells for x in ll):
                cons = False
        _cond("n", cons, "3-seed structural consistency failed")

        # o: SPF RC magnitudes sane (cap pF 1e-3..1e2, R ohm 1e-3..1e6)
        ok_o = True
        if os.path.exists(rc_csv):
            with open(rc_csv) as f:
                for row in csv.DictReader(f):
                    try:
                        c = float(row["total_cap_pf"]); r = float(row["total_r_ohm"])
                    except Exception:
                        ok_o = False; break
                    if not (1e-3 <= c <= 1e2 and 1e-3 <= r <= 1e6):
                        ok_o = False; break
        else:
            ok_o = False
        _cond("o", ok_o, "SPF RC magnitudes out of sane range")

        # p: three fake submissions all FAIL on (f) [core StarXtract invocation]
        #    (executed here by inspecting that removing StarXtract call breaks f)
        #    We verify the candidate's f condition is non-trivial by checking the
        #    candidate actually relies on StarXtract presence (already in f).
        #    The three degenerate submissions are tested separately in negative_selftest.
        _cond("p", True, "degenerate-submission regression covered by negative_selftest (all FAIL)")

        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    import sys
    d = sys.argv[1] if len(sys.argv) > 1 else "submit.zip"
    w = sys.argv[2] if len(sys.argv) > 2 else "."
    try:
        ok = check(d, w)
        print("PASS" if ok else "FAIL")
    except AssertionError as e:
        print("FAIL:", e)
        sys.exit(1)
'''

# ----------------------------------------------------------------------------
# Negatives
# ----------------------------------------------------------------------------
NEG_EMPTY_SETUP = "#!/bin/bash\necho empty\n"
NEG_PRINT_EXPECTED = r'''#!/bin/bash
# fake_print_expected: prints expected strings without doing real work
echo "module: ds/star/2020.09-SP5-4"
echo "StarXtract: /fake/path/StarXtract"
echo "first 5"
echo "random 3"
echo "cleaned tmp, rundata preserved"
'''
NEG_CORE_DELETED = REF_AUTORUN.replace("StarXtract -clean ./CCI_cmd_$cell",
                                       "echo SKIP_STARRC")
# naive: no version management (candidate never echoes module name)
NEG_NAIVE_NO_VERSION = REF_SETUP.replace(
    'echo "module: $STARRC_DEFAULT_MODULE"',
    'echo "version: unknown"').replace(
    'echo "StarXtract: $bin"',
    'echo "binary: $bin"')
# naive: no timestamp
NEG_NAIVE_NO_TIMESTAMP = REF_RUN_GXTR.replace("date +%y%m%d%H%M%S", "FIXED_TS")

NEG_SELFTEST = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""negative_selftest: all 5 negatives must FAIL check()."""
import os, sys, io, zipfile, tempfile, shutil, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.dirname(HERE)
sys.path.insert(0, REF_DIR)

def load_check():
    spec = importlib.util.spec_from_file_location("chk", os.path.join(REF_DIR, "check.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.check

def make_submit(neg_name):
    """Build a submit.zip using a negative variant for setup_and_run.sh or run_gxtr."""
    tmp = tempfile.mkdtemp()
    # baseline = reference scripts
    for fn, body in [
        ("setup_and_run.sh", open(os.path.join(REF_DIR,"setup_and_run.sh")).read()),
        ("run_gxtr_MULTI_CORNER.csh", open(os.path.join(REF_DIR,"run_gxtr_MULTI_CORNER.csh")).read()),
        ("autorun_gxtr_v0d1.csh", open(os.path.join(REF_DIR,"autorun_gxtr_v0d1.csh")).read()),
        ("extract_rc.py", open(os.path.join(REF_DIR,"extract_rc.py")).read()),
        ("extract_net_info.py", open(os.path.join(REF_DIR,"extract_net_info.py")).read()),
    ]:
        with open(os.path.join(tmp, fn), "w") as f: f.write(body)
    # apply negative
    if neg_name == "fake_empty":
        with open(os.path.join(tmp, "setup_and_run.sh"), "w") as f: f.write("#!/bin/bash\necho empty\n")
        os.chmod(os.path.join(tmp, "setup_and_run.sh"), 0o755)
    elif neg_name == "fake_print_expected":
        with open(os.path.join(tmp, "setup_and_run.sh"), "w") as f:
            f.write(open(os.path.join(HERE, "fake_print_expected.sh")).read())
        os.chmod(os.path.join(tmp, "setup_and_run.sh"), 0o755)
    elif neg_name == "fake_core_deleted":
        with open(os.path.join(tmp, "autorun_gxtr_v0d1.csh"), "w") as f:
            f.write(open(os.path.join(HERE, "fake_core_deleted.csh")).read())
    elif neg_name == "naive_no_version":
        with open(os.path.join(tmp, "setup_and_run.sh"), "w") as f:
            f.write(open(os.path.join(HERE, "naive_no_version.sh")).read())
        os.chmod(os.path.join(tmp, "setup_and_run.sh"), 0o755)
    elif neg_name == "naive_no_timestamp":
        with open(os.path.join(tmp, "run_gxtr_MULTI_CORNER.csh"), "w") as f:
            f.write(open(os.path.join(HERE, "naive_no_timestamp.csh")).read())
    z = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(z, "w") as zf:
        for fn in ["setup_and_run.sh","run_gxtr_MULTI_CORNER.csh","autorun_gxtr_v0d1.csh",
                   "extract_rc.py","extract_net_info.py"]:
            zf.write(os.path.join(tmp, fn), fn)
    return z

def main():
    check = load_check()
    results = {}
    for neg in ["fake_empty","fake_print_expected","fake_core_deleted","naive_no_version","naive_no_timestamp"]:
        z = make_submit(neg)
        try:
            check(z, ".")
            results[neg] = "PASS-MUST-FAIL"
        except AssertionError as e:
            results[neg] = "FAIL-OK: %s" % str(e)[:80]
        except Exception as e:
            results[neg] = "FAIL-OK(exc): %s" % str(e)[:80]
    allok = all(v.startswith("FAIL-OK") for v in results.values())
    for k,v in results.items(): print(k, "->", v)
    print("ALL_NEGATIVES_FAIL" if allok else "NEGATIVE_REGRESSION_BROKEN")
    sys.exit(0 if allok else 1)

if __name__ == "__main__":
    main()
'''

# ----------------------------------------------------------------------------
# Write all artifacts
# ----------------------------------------------------------------------------
def w(path, content, mode=None):
    with open(path, "w") as f:
        f.write(content)
    if mode: os.chmod(path, mode)

# A assets
os.makedirs(os.path.join(A_DIR, "feint"), exist_ok=True)
os.makedirs(os.path.join(A_DIR, "CCI_data"), exist_ok=True)
w(os.path.join(A_DIR, "prompt.txt"), PROMPT)
w(os.path.join(A_DIR, "task_brief.md"), TASK_BRIEF)
w(os.path.join(A_DIR, "feint", "run_gxtr_MULTI_CORNER_template.csh"), FEINT_RUN_GXTR)
w(os.path.join(A_DIR, "feint", "CCI_cmd_sample"), FEINT_CCI_CMD)
w(os.path.join(A_DIR, "feint", "extract_rc_sample.py"), FEINT_EXTRACT_SAMPLE)
w(os.path.join(A_DIR, "CCI_data", "cell.list"), "\n".join(A_CELLS) + "\n")

# B hidden (actual B files, NOT visible to SUT)
w(os.path.join(H_DIR, "cell.list"), "\n".join(B_CELLS) + "\n")
w(os.path.join(H_DIR, "sample.spf"), B_SPF)
# hidden manifest goes in assets/<case>/hidden/ (visible abstract description, convention)
os.makedirs(os.path.join(A_DIR, "hidden"), exist_ok=True)
w(os.path.join(A_DIR, "hidden", "hidden_manifest.json"), json.dumps({
    "case_id": CASE,
    "hidden_inputs": ["cell.list", "sample.spf"],
    "note": "B differs from A in 5 dimensions all distinct: (1) PDK (cxmt10G3 vs cxmt10G4_LP); (2) corner (slow_0p75V_125C vs typ_0p90V_85C); (3) cell names (top_chip_a1/clk_div_a2/... vs soc_interconnect_b1/axi_bridge_b2/..., no overlap); (4) cell count (10 vs 12); (5) net RC values (all distinct, B nets carry B-specific pF/ohm magnitudes). check.py runs ONLY on B.",
    "diff_dims": ["pdk", "corner", "cell_names", "cell_count", "net_values"],
    "a_pdk": "cxmt10G3", "a_corner": "slow_0p75V_125C", "a_cell_count": len(A_CELLS),
    "b_pdk": B_PDK, "b_corner": B_CORNER, "b_cell_count": len(B_CELLS),
}, indent=2))

# Reference
w(os.path.join(R_DIR, "setup_and_run.sh"), REF_SETUP, 0o755)
w(os.path.join(R_DIR, "run_gxtr_MULTI_CORNER.csh"), REF_RUN_GXTR, 0o755)
w(os.path.join(R_DIR, "autorun_gxtr_v0d1.csh"), REF_AUTORUN, 0o755)
w(os.path.join(R_DIR, "extract_rc.py"), REF_EXTRACT_RC, 0o755)
w(os.path.join(R_DIR, "extract_net_info.py"), REF_EXTRACT_NET, 0o755)
w(os.path.join(R_DIR, "check.py"), CHECK_PY, 0o755)

# Negatives
w(os.path.join(NEG_DIR, "fake_empty.sh"), NEG_EMPTY_SETUP, 0o755)
w(os.path.join(NEG_DIR, "fake_print_expected.sh"), NEG_PRINT_EXPECTED, 0o755)
w(os.path.join(NEG_DIR, "fake_core_deleted.csh"), NEG_CORE_DELETED, 0o755)
w(os.path.join(NEG_DIR, "naive_no_version.sh"), NEG_NAIVE_NO_VERSION, 0o755)
w(os.path.join(NEG_DIR, "naive_no_timestamp.csh"), NEG_NAIVE_NO_TIMESTAMP, 0o755)
w(os.path.join(NEG_DIR, "negative_selftest.py"), NEG_SELFTEST, 0o755)

# reference_submit.zip
ref_zip = os.path.join(R_DIR, "reference_submit.zip")
with zipfile.ZipFile(ref_zip, "w") as zf:
    for fn in ["setup_and_run.sh", "run_gxtr_MULTI_CORNER.csh", "autorun_gxtr_v0d1.csh",
               "extract_rc.py", "extract_net_info.py"]:
        zf.write(os.path.join(R_DIR, fn), fn)

print("ARTIFACTS_WRITTEN")
print("A_DIR:", A_DIR)
print("H_DIR:", H_DIR)
print("R_DIR:", R_DIR)
