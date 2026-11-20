# trace_deepreads/wh1mf_rtl_path_swap.md

**session**: 1795070537204_wh1mf  ·  user: e0048255  ·  host: hfeg0plg80  ·  mc=175  ·  domain: digital
**claim**: r804 (2026-11-19 17:3x)  ·  status: claimed  ·  **case synth DEBT for next round**
**liveness**: ALIVE (r804 subdir-path check per C r818 fix): `/home/e0048255/.cline/data/sessions/1795070537204_wh1mf/1795070537204_wh1mf.messages.json` 1.08MB mtime Nov 19 16:51
**scan source**: ssh_eda_search_20261119_172105 (r804 new full scan, A-pure mc≥5)

## 用户意图（逐字）

- **U0 (ts=1795070537578)**: 「帮我把/proj/lacaa/V0/workdir/wenjun/SOC_MPW/IP_Dev/io_top_par_wrap/test/run_tb_vcs.py 里面吃的rtl path 变成 /proj/lacaa/V0/workdir/wenjun/SOC_MPW/IP_Dev/io_top_par_wrap/src_rtl/io_top_par_wrap.all.v」
- **U18 (ts=1795070991334)**: 同上重复（用户在两次问之间文件被外部改成另一版本——agent 注释「这个文件在你上次修改后又换成了另一个版本，原本会用 build_all() 从 rtl/io_top_par_wrap.f 重新生成 {ROOT}/rtl/io_top_par_wrap.all.v 再喂给 VCS」）
- **U34 (ts=1795071161346)**: 「帮我分析/proj/lacaa/V0/workdir/wenjun/SOC_MPW/IP_Dev/io_top_par_wrap/test/sim.log分析为什么fail,是tb 写的不对还是RTL 有问题？」(独立后续分析任务，**不纳入本 case**)

## trace 结构（247 msgs）

- msgs 0-17: U0 任务首轮 — agent read_files 读 run_tb_vcs.py → list_allowed_files → run_approved_command patch → 验证
- msgs 18-33: U18 重复任务（文件被改回原版后 agent 重新 patch）— run_approved_command + 「SYNTAX OK」
- msgs 34-246: U34 sim.log fail 分析（独立子任务，可作另案或忽略）

**本 case focus = U0/U18 produce-task**：修改 run_tb_vcs.py 使其 `RTL_FILES` 从 14 文件 list + `RTL=ROOT/rtl` 改为单一 `.all.v` 路径。

## Asset A：原始 run_tb_vcs.py（88 行，verbatim from trace msg 2 read_files result）

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_tb_vcs.py -- compile & run the io_top_par_wrap testbench with Synopsys VCS.

Requires: vcs / simv on PATH (VCS 2020.12 or later), or VCS_HOME set.
Verdi/DVE can open the VPD waveform if you switch the tb to $vcdpluson
(see note at the bottom of tb_io_top_par_wrap.v).

Usage:
    python sim/run_tb_vcs.py
"""

import os
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RTL  = os.path.join(ROOT, "rtl")
SIM  = os.path.dirname(os.path.abspath(__file__))

RTL_FILES = [
    "io_cell_lib.v", "iocfg.v", "gpio_top.v", "iomux_pp.v", "iomuxt_pp.v",
    "io_top_ao_1.v", "io_top_ao_2.v", "io_top_ao_3.v", "io_top_ao_4.v",
    "io_top_ao_5.v", "io_top_ao_6.v", "iomux_np.v", "iomuxt_np.v",
    "io_top_glue.v", "io_top_par_wrap.v",
]


def which(exe: str):
    """Return path to executable, searching VCS_HOME then PATH."""
    if os.environ.get("VCS_HOME"):
        cand = os.path.join(os.environ["VCS_HOME"], "bin", exe)
        if os.path.exists(cand):
            return cand
    found = shutil.which(exe)
    if found:
        return found
    # Windows: also try .exe explicitly
    found = shutil.which(exe + ".exe")
    return found


def main():
    vcs = which("vcs")
    if not vcs:
        print("ERROR: vcs not found. Source the VCS environment or set VCS_HOME.",
              file=sys.stderr)
        return 2

    tb    = os.path.join(SIM, "tb_io_top_par_wrap.v")
    simv  = os.path.join(SIM, "simv")
    clog  = os.path.join(SIM, "compile.log")
    rlog  = os.path.join(SIM, "sim.log")
    rtl_files = [os.path.join(RTL, f) for f in RTL_FILES]

    cmd = [vcs, "-sverilog", "-timescale=1ns/1ps",
           "-debug_access+all", "-o", simv, tb] + rtl_files
    print(" ".join(cmd))
    with open(clog, "w") as fh:
        rc = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT).returncode
    if rc != 0:
        print("ERROR: VCS compile failed (exit %d); see %s" % (rc, clog),
              file=sys.stderr)
        return rc

    print("Compile OK -> %s" % simv)
    exe = simv + ".exe" if os.path.exists(simv + ".exe") else simv
    with open(rlog, "w") as fh:
        rc = subprocess.run([exe, "-l", rlog], stdout=fh,
                            stderr=subprocess.STDOUT).returncode
    if rc != 0:
        print("ERROR: Simulation failed (exit %d); see %s" % (rc, rlog),
              file=sys.stderr)
        return rc

    print("Simulation finished. VCD waveform: sim/tb_io_top_par_wrap.vcd")
    # print PASS/FAIL lines for a quick summary
    with open(rlog) as fh:
        for line in fh:
            if any(k in line for k in ("[PASS]", "[FAIL]", "TESTBENCH")):
                print("   " + line.rstrip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

## Agent 实际改动（trace msg 33 总结）

「这个文件在你上次修改后又换成了另一个版本——它原本会用 `build_all()` 从 `rtl/io_top_par_wrap.f` 重新生成 `{ROOT}/rtl/io_top_par_wrap.all.v` 再喂给 VCS。我已按你的要求把"吃的 rtl path"直接改成了 `src_rtl/io_top_par_wrap.all.v`」

实际 patch（推断 + trace 证据）：把 `RTL_FILES` 列表用法 + `RTL=ROOT/rtl` 替换为单一 `RTL_FILE = os.path.join(ROOT, "src_rtl", "io_top_par_wrap.all.v")`，cmd 用 `[vcs, ..., tb, RTL_FILE]`。

## 拟造任务形态（produce-task + hidden-B + subprocess-on-B）

- **domain**: digital (VCS RTL 编译 driver 脚本修改)
- **A 档 trace-faithful**: 用 U0 逐字作 prompt；A = 上述 88 行原 run_tb_vcs.py + 一个 `tb_io_top_par_wrap.v` stub + `rtl/` 目录占位（14 个空 .v 文件）+ `src_rtl/io_top_par_wrap.all.v` placeholder
- **B 档 hidden specificity oracle**: 改名 `run_tb_vcs_b.py` + 不同 target path（`src_rtl_v2/io_top_par_wrap_v2.all.v`）+ 不同 RTL_FILES 列表（如 8 个不同名 .v）+ 不同 tb 名（`tb_io_top_par_wrap_b.v`）+ 不同 simv 名
- **ref 解**: 修改 run_tb_vcs.py 使 RTL_FILE 指向 user 指定 .all.v 路径，删除 RTL_FILES 列表展开
- **check.py**（k>=8 独立断言，subprocess 在 B 上跑候选脚本 with stub vcs/simv）：
  1. submit.zip 含修改后的 run_tb_vcs.py
  2. 文件 syntax OK（py_compile 通过）
  3. RTL_FILES 列表被删除或 RTL_FILE 单 path 替换
  4. cmd 构造使用单一 .all.v 路径（非 14 文件 list）
  5. 路径值 = B 指定的 hidden path（非 A 的 path，防硬编 A）
  6. script 在 stub vcs/simv 环境下 subprocess.run 返回 0
  7. cmd print 行包含 hidden target .all.v 文件名
  8. RTL_FILES 旧 14 文件名均不出现在 cmd 构造（防 partial patch）
  9. vcs not found 分支保留（return 2）
  10. tb path 仍从 SIM 派生（未破坏）
  11. simv/clog/rlog 路径未破坏
  12. main() return 0 on success 路径保留
  13. `if __name__ == "__main__"` 入口保留
  14. 确定性：3 次跑同布局
  15. §4.9 anti-stub: 空壳/只 print/删核心 三假全 FAIL
- **5 negatives**: neg_empty / neg_print_only / neg_core_deleted (只改注释不改逻辑) / neg_wrong_path (用 A 路径非 B) / neg_partial (RTL_FILES 删一半)
- **参考解**: `run_tb_vcs_ref.py` = 参数化 argv[1] 接受 target .all.v 路径，删 RTL_FILES list，cmd 用单 file

## DEBT 状态

- **case_id 拟**: `EDA-Eval-DesignFlow-RtlPathSwapProduce-001`（digital）
- **未交付根因**: r804 40-min budget 已用于 (a) 新全量 ssh_eda_scan 7min + POOL_SWITCH summary_stats.json refresh + (b) C r818 path-bug fix A 域 liveness 验证 4 候选 3 ALIVE + (c) discuss r804 mandatory 配额清付 + (d) 本 deepread note。fresh-context full pipeline（fetch full trace + synth assets + check.py k>=8 + 5 neg + ref PASS + §4.9 a/b/c + e2e）单轮 ~25-30min，超 budget。
- **下轮 loop agent 续**: 本 deepread note 已含 A asset verbatim + check.py 15 断言骨架 + 5 neg 设计 + ref 解方向，下轮 fresh-context 可在 ~20min 完成合成 + 自验 + 落库。
- **优先级**: 高（fresh A-pure ALIVE digital produce-task，无历史 case 覆盖此 reframe 类型）
