#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-PwrGlobals-001 (shard A, A档 trace-faithful, pnr_signoff).

Trace: 1792399916731_00i9f (alan3zh / hfeg0plg49 / mc=101 / innovus=1105).
Task (user #17 verbatim): 将apr/innovus下的初始配置，写入apr/innovus/gui/power.globals中，
  使其能在innovus中进行后续任务.
Gold = Innovus init-globals Tcl (power.globals) consolidating apr/innovus initial config
  (Makefile vars + mmmc.view + innovus_fp.tcl init_design block), parameterized via
  setup/common_setup.tcl.  Grader: static Tcl structural checks + tclsh-stub cross-input
  guard on hidden B (no Innovus binary on judge machine; real Innovus verified at gold
  creation on .75 by the user).
"""
import json, os, sys, zipfile, io, re, base64, subprocess, tempfile, shutil, hashlib

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-PwrGlobals-001"
A = os.path.join(BENCH, "assets", CASE)
R = os.path.join(BENCH, "reference", CASE)
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")

# ---------------------------------------------------------------- gold content
GOLD_POWER_GLOBALS = r'''#############################################################################
# power.globals -- Innovus initial setup for follow-on GUI tasks
#   (power / IR analysis, ECO, debug) -- lives in apr/innovus/gui
#
# Mirrors the "initial configuration" of apr/innovus (Makefile variables +
# mmmc.view + the init_design block of innovus_fp.tcl) so an interactive
# session starts from exactly the same setup as the batch flow.
#
#   * no design in memory  -> sets the classic init_* globals, runs
#     init_design (routed netlist, tech LEF + cell LEF, MMMC view), then
#     reads the routed DEF so layout + power grid exist for power/IR views
#   * design already loaded -> changes nothing, just prints the pointers
#
# Usage (Innovus, module tools/innovus/<ver>):
#     cd apr/innovus/gui && innovus -files power.globals
#   or, inside an Innovus GUI / command window:
#     source power.globals
#
# All design-specific values come from ../setup/common_setup.tcl so the same
# script drives any design in this PDK.
#
# NOTE: any secondary power domain whose grid is not yet built (see the TODO
#       in ../innovus_fp.tcl) is still listed in PWR_NETS so init_design
#       registers it, but its power/IR results are not signoff-grade until
#       that grid is added.
#############################################################################

# --- load design-specific setup (paths, top, power nets) ---------------------
set SETUP_DIR [file dirname [file normalize [info script]]]/../setup
if {![file exists $SETUP_DIR/common_setup.tcl]} {
    puts "ERROR: power.globals: missing $SETUP_DIR/common_setup.tcl"
    return
}
source $SETUP_DIR/common_setup.tcl

# --- design inputs (same values as apr/innovus/Makefile) ---------------------
# TECH_LEF MUST be loaded before CELL_LEF (IMPLF-26 layer ordering).
# Liberty (single corner) enters via the MMMC view's library_set; SDCs enter
# via its constraint_mode.

# default: ROUTED netlist (matches DEF / SPEF / post-sim exactly).  To replay
# the original fp-stage init instead, point IN_V at the postsyn netlist.
if {![info exists IN_V]}      { set IN_V      $WORK_DIR/${TOP}.routed.v }
if {![info exists DEF_IN]}    { set DEF_IN    $WORK_DIR/${TOP}.def }
if {![info exists ROUTED_DB]} { set ROUTED_DB $WORK_DIR/${TOP}_inv_routed.dat }

# file existence precheck -- abort cleanly if a required input is missing
foreach f [list $TECH_LEF $CELL_LEF $MMMC_VIEW $IN_V $DEF_IN] {
    if {![file exists $f]} {
        puts "ERROR: power.globals: required file missing : $f"
        return
    }
}

# --- load the design if none is in memory ------------------------------------
set have_design 0
catch { if {[llength [dbGet top.name]] > 0} { set have_design 1 } }

if {!$have_design} {
    puts "INFO: power.globals -- no design in memory, running init_design"
    set init_verilog       $IN_V
    set init_lef_file      [list $TECH_LEF $CELL_LEF]  ;# tech LEF first (IMPLF-26)
    set init_top_cell      $TOP
    set init_design_settop 1
    set init_pwr_net       $PWR_NETS
    set init_gnd_net       $GND_NET
    set init_mmmc_file     $MMMC_VIEW
    if {[catch {init_design} err]} {
        puts "ERROR: init_design failed : $err"
        return
    }
    # routed DEF adds layout + power grid (ring / stripes / M1 followpins),
    # which the power and IR views need
    if {![catch {defIn $DEF_IN} err]} {
        puts "INFO: defIn OK : $DEF_IN"
    } else {
        puts "WARN: defIn failed : $err"
        puts "WARN: physical view / power grid will be missing until a DEF is read"
    }
    catch {setMultiCpuUsage -localCpu 8}
} else {
    puts "INFO: power.globals -- design already loaded ([dbGet top.name]); init skipped"
    puts "INFO:   routed-db alternative (fresh session):"
    puts "INFO:     restoreDesign $ROUTED_DB $TOP"
}

# --- pointers for follow-on work ---------------------------------------------
puts "INFO: power.globals loaded -- session ready"
puts "INFO:   TOP          : $TOP"
puts "INFO:   power nets   : $PWR_NETS / $GND_NET"
puts "INFO:   routed DEF   : $DEF_IN"
puts "INFO:   SPEF (pe)    : $SPEF"
puts "INFO:   FSDB (sim)   : $FSDB"
puts "INFO:   next (GUI)   : Power Analysis (report_power) for power;"
puts "INFO:                  IR/EM views need the power grid (defIn above) and,"
puts "INFO:                  for signoff-grade, Voltus-Fi analyze_power_grid"
'''

COMMON_SETUP_A = r'''# common_setup.tcl -- design-specific setup for power.globals (design A)
# Sourced by ../gui/power.globals.  Edit paths / top / corner per design.
set ROOT     /home/alan3zh/workspace/test_chip/test_chip
set APR_DIR  $ROOT/apr/innovus
set WORK_DIR $APR_DIR/work
set PDK_ROOT /apps/imctf/extpdk/HL22/LAGAT/Digital/current

set TOP "hl22_porting_test_chip_power"

# tech LEF MUST be first in init_lef_file (IMPLF-26 ordering)
set TECH_LEF $PDK_ROOT/Innovus_tf/Au22_1P7M_4_1X_2_2X_1_8X_withRDL_HVH.tlef
set CELL_LEF $PDK_ROOT/Au22_basic_lvt/lef/Au22_basic_lvt.lef

# MMMC view (single corner ssg_0p72v_m40c; library_set + constraint_mode inside)
set MMMC_VIEW $WORK_DIR/mmmc.view

# power nets: VDD = main domain; second entry = secondary domain (grid TODO)
set PWR_NETS {VDD VDD_PM}
set GND_NET  VSS

set SPEF $ROOT/pe/work/${TOP}.spef
set FSDB $ROOT/post_sim_sdf/${TOP}_post_sdf.fsdb
'''

COMMON_SETUP_B = r'''# common_setup.tcl -- design-specific setup for power.globals (design B)
# Sourced by ../gui/power.globals.  Edit paths / top / corner per design.
set ROOT     /home/baiqiu/workspace/io_ctrl/io_ctrl
set APR_DIR  $ROOT/apr/innovus
set WORK_DIR $APR_DIR/work
set PDK_ROOT /apps/imctf/extpdk/HL22/LAGAT/Digital/current

set TOP "hl22_io_ctrl_top"

# tech LEF MUST be first in init_lef_file (IMPLF-26 ordering)
set TECH_LEF $PDK_ROOT/Innovus_tf/Au22_1P7M_4_1X_2_2X_1_8X_VHV.tlef
set CELL_LEF $PDK_ROOT/Au22_io_lvt/lef/Au22_io_lvt.lef

# MMMC view (single corner tt_0p8v_25c; library_set + constraint_mode inside)
set MMMC_VIEW $WORK_DIR/mmmc.view

# power nets: VDD = main domain; second entry = secondary domain (grid TODO)
set PWR_NETS {VDD VDD_PE}
set GND_NET  VSS

set SPEF $ROOT/pe/work/${TOP}.spef
set FSDB $ROOT/post_sim_sdf/${TOP}_post_sdf.fsdb
'''

README_MD = r'''# power.globals -- Innovus initial setup for follow-on GUI tasks

`gui/power.globals` is an Innovus init-globals + session-configuration script
(Tcl).  It consolidates the "initial configuration" of `apr/innovus` (the
Makefile variables, `mmmc.view`, and the `init_design` block of
`innovus_fp.tcl`) so an interactive session starts from exactly the same setup
as the batch flow.

## Usage

```sh
cd apr/innovus/gui && innovus -files power.globals     # open GUI auto-init
# or, inside an Innovus GUI / command window:
source power.globals
```

## Behavior

- **no design in memory** -> sets the classic `init_*` globals, runs
  `init_design` (routed netlist + tech LEF + cell LEF + MMMC view), then
  `defIn` the routed DEF so layout + power grid exist for power/IR views.
- **design already loaded** -> changes nothing, prints a `restoreDesign`
  alternative for a fresh session.

All design-specific values (`TOP`, PDK paths, `TECH_LEF`, `CELL_LEF`,
`MMMC_VIEW`, `PWR_NETS`, `GND_NET`, `SPEF`, `FSDB`) live in
`setup/common_setup.tcl`; `power.globals` only `source`s it and wires the
values into `init_*`.  To drive a different design / corner, swap
`common_setup.tcl` -- `power.globals` itself is design-agnostic.

## Dependencies / caveats

- Innovus (module `tools/innovus/<ver>`); tech LEF must precede cell LEF in
  `init_lef_file` (IMPLF-26 layer ordering).
- Liberty enters via the MMMC view's `library_set`; SDCs via its
  `constraint_mode`.
- Any secondary power domain whose grid is not yet built (see the TODO in
  `../innovus_fp.tcl`) is still listed in `PWR_NETS` so `init_design`
  registers it, but its power/IR results are **not** signoff-grade until that
  grid is added.
- `defIn` of the routed DEF is what brings in the power grid (ring / stripes /
  M1 followpins) required by the power and IR views.
'''

# ---------------------------------------------------------------- asset A
ASSET_MAKEFILE_INIT = r'''#############################################################################
# Makefile -- Innovus floorplan + routing (place/CTS/route), via LSF bsub
#   (excerpt: project paths + PDK inputs + power nets -- the "initial config")
#############################################################################
SHELL := /bin/bash
.PHONY: all pr fp route submit run clean help

# project paths (this Makefile lives in <project>/apr/innovus)
PRJ_ROOT       := $(abspath $(CURDIR)/../..)
TOP            ?= hl22_porting_test_chip_power
DC_RESULT_DIR  ?= $(PRJ_ROOT)/results/dc_2026-10-13-13.08.17
NETLIST        ?= $(DC_RESULT_DIR)/$(TOP)_postsyn.v
SDC_FILE       ?= $(DC_RESULT_DIR)/$(TOP).mapped.sdc

# PDK inputs -- Innovus uses Liberty .lib (not Synopsys .db)
PDK_ROOT_PATH  ?= /apps/imctf/extpdk/HL22/LAGAT/Digital/current
LEF_FILE       ?= $(PDK_ROOT_PATH)/Au22_basic_lvt/lef/Au22_basic_lvt.lef
# Cadence tech LEF (defines M1.. layers) -- MUST be loaded before the cell LEF.
TECH_LEF       ?= $(PDK_ROOT_PATH)/Innovus_tf/Au22_1P7M_4_1X_2_2X_1_8X_withRDL_HVH.tlef
LIB_FILE       ?= $(PDK_ROOT_PATH)/Au22_basic_lvt/lib/Au22_basic_lvt_ssg_0p72v_m40c_ccs.lib
INV_POWER_NET  ?= VDD
INV_GROUND_NET ?= VSS

WORK_DIR       := $(CURDIR)/work
MMMC_VIEW      := $(WORK_DIR)/mmmc.view
DEF_OUT        := $(WORK_DIR)/$(TOP).def
'''

ASSET_MMMC_VIEW = r'''# =====================================================================
# Innovus MMMC view file -- generated by apr/innovus/Makefile
#   (single corner: ssg_0p72v_m40c; add corners per foundry template)
# =====================================================================
create_rc_corner -name rc_typ -temperature 25
create_library_set -name libs_typ \
    -timing {/apps/imctf/extpdk/HL22/LAGAT/Digital/current/Au22_basic_lvt/lib/Au22_basic_lvt_ssg_0p72v_m40c_ccs.lib}
create_delay_corner -name delay_typ -library_set libs_typ -rc_corner rc_typ
create_constraint_mode -name mode_func \
    -sdc_files {/home/alan3zh/workspace/test_chip/test_chip/results/dc_2026-10-13-13.08.17/hl22_porting_test_chip_power.mapped.sdc /home/alan3zh/workspace/test_chip/test_chip/apr/innovus/work/cts_clk.sdc}
create_analysis_view -name av_func_typ -delay_corner delay_typ -constraint_mode mode_func
set_analysis_view -setup {av_func_typ} -hold {av_func_typ}
'''

ASSET_FP_INIT = r'''# innovus_fp.tcl -- Innovus stage 1 : init_design + floorplan + power plan
#   (excerpt: the init_design block -- the "initial config" to consolidate)
#   inputs : LEF + DC postsyn netlist + SDC + Liberty(.lib, via mmmc.view)
set TOP       [env_or TOP  "hl22_porting_test_chip_power"]
set VIEW_FILE [env_or MMMC_VIEW "mmmc.view"]
# ... (paths resolved from Makefile vars: TECH_LEF/LEF_FILE/NETLIST/PWR_NET) ...

# init_design (MMMC views come from the generated mmmc.view file)
set init_verilog       $NETLIST
set init_lef_file      [list $TECH_LEF $LEF_FILE]   ;# tech LEF first (IMPLF-26)
set init_top_cell      $TOP
set init_design_settop 1
set init_pwr_net       $PWR_NET
set init_gnd_net       $GND_NET
set init_mmmc_file     $VIEW_FILE

puts "INFO: init_design (lef=$init_lef_file)"
if {[catch {init_design} err]} {
    puts "ERROR: init_design failed : $err"
}
'''

ASSET_WORK_INV = r'''# apr/innovus/work inventory (routed-stage outputs -- the design inputs
# power.globals must wire into init_*).
TOP          = hl22_porting_test_chip_power
routed.v     = work/hl22_porting_test_chip_power.routed.v     # init_verilog (routed netlist, matches DEF/SPEF/post-sim)
DEF          = work/hl22_porting_test_chip_power.def          # defIn (layout + power grid)
routed.db    = work/hl22_porting_test_chip_power_inv_routed.dat  # restoreDesign alternative
mmmc.view    = work/mmmc.view                                  # init_mmmc_file (single corner ssg_0p72v_m40c)
cts_clk.sdc  = work/cts_clk.sdc                                # constraint_mode SDC (real clock for CTS)
# SPEF (parasitics, pe stage) : pe/work/hl22_porting_test_chip_power.spef
# FSDB (post-sim, for dynamic power) : post_sim_sdf/hl22_porting_test_chip_power_post_sdf.fsdb
'''

ASSET_POWER_NETS = r'''# power / ground nets of the design (from apr/innovus/Makefile + innovus_fp.tcl)
PWR_NETS = {VDD VDD_PM}     ;# VDD = main domain ; VDD_PM = pd_pm domain (grid TODO in innovus_fp.tcl)
GND_NET  = VSS
# NOTE: VDD_PM (pd_pm domain) has no rails/stripes yet -- pd_pm power/IR
#       results are not signoff-grade until that grid is added.  VDD_PM is
#       still listed so init_design registers the domain.
'''

TASK_BRIEF = (
"交付 outputs/submit.zip，含 gui/power.globals（Innovus 初始配置 Tcl，供 innovus -files / "
"source 加载）、setup/common_setup.tcl（power.globals 引用的设计取值）、README.md（用法与依赖）。\n"
"判分对隐藏输入 B 注入 setup/common_setup.tcl 后跑 power.globals，断言 init_* 配置正确、结构齐备、无 A 字面量硬编码。\n"
"mode=design_flow / entry_point=outputs/submit.zip / test=check(deliverable, workdir)。"
)

PROMPT = (
"场景（真实 trace：alan3zh / Innovus 初始配置固化 / pnr_signoff / session 1792399916731_00i9f）\n\n"
"我是 alan3zh，在 .75 全定制环境下完成 test_chip 数字后端链路（Innovus 布线已就绪）。"
"任务意图（用户原话，仅说明本地副本位置，未改写）：\n\n"
"> 将apr/innovus下的初始配置，写入apr/innovus/gui/power.globals中，使其能在innovus中进行后续任务\n\n"
"apr/innovus 的初始配置上下文（Makefile 初始化变量节、gui/mmmc.view、innovus_fp.tcl 的 init_design 块、"
"work 清单、电源网络）见工作目录 assets/apr_innovus_config/。交付接口见 task_brief.md。"
)

# ---------------------------------------------------------------- check.py
CHECK_PY = r'''def check(deliverable, workdir):
    """EDA-Eval-DesignFlow-PwrGlobals-001 checker -- Innovus init-globals (power.globals).

    Deliverable submit.zip must contain:
      gui/power.globals        -- Innovus init-globals Tcl (sources ../setup/common_setup.tcl)
      setup/common_setup.tcl   -- design-specific values (TOP/LEF/MMMC/power nets/...)
      README.md                -- usage

    Grader = 20 independent conditions (a)-(t):
      (a)-(j)   static structural checks on power.globals (comment-stripped active code)
      (k)-(t)   tclsh-stub cross-input guard: inject hidden-B common_setup.tcl, run
                power.globals with init_*/init_design/defIn/dbGet/file-exists stubbed,
                assert B values flow through + structure + no A-literal leak.
    """
    import os, sys, re, zipfile, tempfile, subprocess, shutil
    _sys = sys
    ok = True
    fails = []

    def _(label, msg, cond):
        nonlocal ok
        if not cond:
            ok = False
            fails.append("%s: %s" % (label, msg))

    deliverable = os.path.join(workdir, deliverable) if not os.path.isabs(deliverable) else deliverable
    if not os.path.isfile(deliverable):
        print("FAIL: deliverable not found: %s" % deliverable)
        _sys.exit(1)

    tmp = tempfile.mkdtemp(prefix="pwrglobals_chk_")
    try:
        with zipfile.ZipFile(deliverable) as z:
            z.extractall(tmp)
        pg = os.path.join(tmp, "gui", "power.globals")
        cs = os.path.join(tmp, "setup", "common_setup.tcl")
        rd = os.path.join(tmp, "README.md")

        # (a) zip has gui/power.globals + setup/common_setup.tcl + README.md
        _("a", "zip has gui/power.globals + setup/common_setup.tcl + README.md",
          os.path.isfile(pg) and os.path.isfile(cs) and os.path.isfile(rd))

        pg_src = open(pg, errors="replace").read() if os.path.isfile(pg) else ""

        def active_code(src):
            out = []
            for ln in src.splitlines():
                s = ln.strip()
                if s.startswith("#"):
                    continue
                if ";#" in ln:
                    ln = ln.split(";#", 1)[0]
                out.append(ln)
            return "\n".join(out)

        ac = active_code(pg_src)

        # (b) sources common_setup.tcl
        _("b", "power.globals sources common_setup.tcl",
          re.search(r"source\s+\S*common_setup\.tcl", ac) is not None)

        # (c) init_lef_file = [list $TECH_LEF $CELL_LEF]  (tech LEF first)
        _("c", "init_lef_file = [list $TECH_LEF $CELL_LEF] (tech-first)",
          re.search(r"set\s+init_lef_file\s+\[list\s+\$TECH_LEF\s+\$CELL_LEF\]", ac) is not None)

        # (d) init_design_settop 1
        _("d", "set init_design_settop 1",
          re.search(r"set\s+init_design_settop\s+1", ac) is not None)

        # (e) catch {init_design}  (error guard)
        _("e", "init_design inside catch",
          re.search(r"catch\s*\{?\s*init_design", ac) is not None)

        # (f) catch defIn  (reads routed DEF for power grid)
        _("f", "defIn inside catch",
          re.search(r"catch\s*\{?\s*defIn", ac) is not None)

        # (g) have_design guard via dbGet top.name
        _("g", "have_design guard via dbGet top.name",
          re.search(r"dbGet\s+top\.name", ac) is not None)

        # (h) file-existence precheck (foreach + file exists + return)
        _("h", "file-existence precheck (foreach + file exists + return)",
          re.search(r"foreach.*file exists", ac, re.S) is not None and
          re.search(r"foreach\b", ac) is not None and "return" in ac)

        # (i) INFO pointers (power nets + SPEF + FSDB)
        _("i", "INFO pointers (power nets + SPEF + FSDB puts)",
          re.search(r"puts\s+\"INFO:.*power nets", ac) is not None and
          re.search(r"puts\s+\"INFO:.*SPEF", ac) is not None and
          re.search(r"puts\s+\"INFO:.*FSDB", ac) is not None)

        # (j) no A-literal hardcode in active code
        a_literals = ["hl22_porting_test_chip_power", "VDD_PM", "Au22_basic_lvt"]
        leaked = [lit for lit in a_literals if lit in ac]
        _("j", "no A-literal hardcode in active code (%s)" % (", ".join(leaked) if leaked else "none"),
          not leaked)

        # ---- cross-input guard: inject hidden-B common_setup.tcl, tclsh stub run ----
        # hidden B is embedded below (B is NOT in the SUT sandbox).
        B_SETUP = (
            "set ROOT     /home/baiqiu/workspace/io_ctrl/io_ctrl\n"
            "set APR_DIR  $ROOT/apr/innovus\n"
            "set WORK_DIR $APR_DIR/work\n"
            "set PDK_ROOT /apps/imctf/extpdk/HL22/LAGAT/Digital/current\n"
            "set TOP \"hl22_io_ctrl_top\"\n"
            "set TECH_LEF $PDK_ROOT/Innovus_tf/Au22_1P7M_4_1X_2_2X_1_8X_VHV.tlef\n"
            "set CELL_LEF $PDK_ROOT/Au22_io_lvt/lef/Au22_io_lvt.lef\n"
            "set MMMC_VIEW $WORK_DIR/mmmc.view\n"
            "set PWR_NETS {VDD VDD_PE}\n"
            "set GND_NET VSS\n"
            "set SPEF $ROOT/pe/work/${TOP}.spef\n"
            "set FSDB $ROOT/post_sim_sdf/${TOP}_post_sdf.fsdb\n"
        )
        stub_out = ""
        stub_err = ""
        ran_stub = False
        if os.path.isfile(pg):
            stage = tempfile.mkdtemp(prefix="pwrglobals_stub_")
            try:
                os.makedirs(os.path.join(stage, "setup"), exist_ok=True)
                # inject B values into setup/common_setup.tcl
                open(os.path.join(stage, "setup", "common_setup.tcl"), "w").write(B_SETUP)
                os.makedirs(os.path.join(stage, "gui"), exist_ok=True)
                shutil.copy(pg, os.path.join(stage, "gui", "power.globals"))
                stub = (
                    "rename file _file_orig\n"
                    "proc file {args} {\n"
                    "    if {[lindex $args 0] eq \"exists\"} {return 1}\n"
                    "    return [_file_orig {*}$args]\n"
                    "}\n"
                    "proc dbGet {args} {return \"\"}\n"
                    "proc setMultiCpuUsage {args} {}\n"
                    "proc restoreDesign {args} {}\n"
                    "proc init_design {} {\n"
                    "    global init_verilog init_lef_file init_top_cell init_design_settop init_pwr_net init_gnd_net init_mmmc_file\n"
                    "    puts \"STUB_INIT_VERILOG=$init_verilog\"\n"
                    "    puts \"STUB_INIT_LEF_FILE=$init_lef_file\"\n"
                    "    puts \"STUB_INIT_TOP_CELL=$init_top_cell\"\n"
                    "    puts \"STUB_INIT_DESIGN_SETTOP=$init_design_settop\"\n"
                    "    puts \"STUB_INIT_PWR_NET=$init_pwr_net\"\n"
                    "    puts \"STUB_INIT_GND_NET=$init_gnd_net\"\n"
                    "    puts \"STUB_INIT_MMMC_FILE=$init_mmmc_file\"\n"
                    "    return\n"
                    "}\n"
                    "proc defIn {path} {puts \"STUB_DEFIN=$path\"}\n"
                    "source gui/power.globals\n"
                )
                open(os.path.join(stage, "stub.tcl"), "w").write(stub)
                pr = subprocess.run(["tclsh", "stub.tcl"], cwd=stage,
                                    capture_output=True, text=True, timeout=60)
                stub_out = pr.stdout
                stub_err = pr.stderr
                ran_stub = True
            finally:
                shutil.rmtree(stage, ignore_errors=True)

        def stub_val(tag):
            m = re.search(re.escape(tag) + r"=(.*)", stub_out)
            return m.group(1).strip() if m else None

        # (k) stub init_verilog == B's IN_V (hl22_io_ctrl_top.routed.v)
        iv = stub_val("STUB_INIT_VERILOG")
        _("k", "stub init_verilog == B routed netlist (hl22_io_ctrl_top.routed.v), got=%r" % iv,
          iv is not None and iv.endswith("hl22_io_ctrl_top.routed.v"))

        # (l) stub init_top_cell == B TOP (hl22_io_ctrl_top)
        tc = stub_val("STUB_INIT_TOP_CELL")
        _("l", "stub init_top_cell == hl22_io_ctrl_top, got=%r" % tc,
          tc == "hl22_io_ctrl_top")

        # (m) stub init_pwr_net == {VDD VDD_PE}  (B pd_pe, not A's VDD_PM)
        pn = stub_val("STUB_INIT_PWR_NET")
        _("m", "stub init_pwr_net == {VDD VDD_PE}, got=%r" % pn,
          pn is not None and "VDD_PE" in pn and "VDD" in pn and "VDD_PM" not in pn)

        # (n) stub init_lef_file == [B VHV tlef, B io_lvt lef] (tech-first + B lefs)
        lf = stub_val("STUB_INIT_LEF_FILE") or ""
        _("n", "stub init_lef_file tech-first with B lefs (VHV + io_lvt), got=%r" % lf,
          "VHV" in lf and "io_lvt" in lf and "HVH" not in lf and "basic_lvt" not in lf
          and lf.find("VHV") < lf.find("io_lvt"))

        # (o) stub init_mmc_file == B's mmmc.view (io_ctrl ... work/mmmc.view)
        mf = stub_val("STUB_INIT_MMMC_FILE") or ""
        _("o", "stub init_mmmc_file == B mmmc.view (io_ctrl/work/mmmc.view), got=%r" % mf,
          mf.endswith("work/mmmc.view") and "io_ctrl" in mf)

        # (p) stub defIn == B's DEF_IN (hl22_io_ctrl_top.def)
        di = stub_val("STUB_DEFIN")
        _("p", "stub defIn == B DEF (hl22_io_ctrl_top.def), got=%r" % di,
          di is not None and di.endswith("hl22_io_ctrl_top.def"))

        # (q) stub init_gnd_net == VSS
        gn = stub_val("STUB_INIT_GND_NET")
        _("q", "stub init_gnd_net == VSS, got=%r" % gn, gn == "VSS")

        # (r) stub stdout "session ready" (ran to completion, init branch executed)
        _("r", "stub stdout has 'power.globals loaded -- session ready'",
          "power.globals loaded -- session ready" in stub_out)

        # (s) stub stdout no A-literal leak
        leak_out = [lit for lit in a_literals if lit in stub_out]
        _("s", "stub stdout no A-literal leak (%s)" % (", ".join(leak_out) if leak_out else "none"),
          not leak_out)

        # (t) stub init_design_settop == 1
        st = stub_val("STUB_INIT_DESIGN_SETTOP")
        _("t", "stub init_design_settop == 1, got=%r" % st, st == "1")

        if not ran_stub:
            ok = False
            fails.append("STUB: tclsh stub run did not execute (pg missing=%s, stderr=%s)"
                         % (not os.path.isfile(pg), stub_err[:200]))

    except Exception as e:
        ok = False
        fails.append("EXC: %s: %s" % (type(e).__name__, e))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    for f in fails:
        print("FAIL " + f)
    print("PASS" if ok else "FAIL")
    _sys.exit(0 if ok else 1)

if __name__ == "__main__":
    import sys
    check(sys.argv[1] if len(sys.argv) > 1 else "outputs/submit.zip", sys.argv[2] if len(sys.argv) > 2 else ".")
'''

# ---------------------------------------------------------------- negatives
def make_submit(path, files):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)

# 1. fake_empty (§4.9a 空壳): power.globals empty comment, NO setup/common_setup.tcl
NEG_FAKE_EMPTY = {
    "gui/power.globals": "# (empty) -- no init configured\n",
    "README.md": "# empty\n",
}
# 2. fake_print_expected (§4.9b 只print期望串): sources common_setup + prints INFO, but no init_design/defIn
NEG_FAKE_PRINT = {
    "gui/power.globals": (
        "source ../setup/common_setup.tcl\n"
        'puts "INFO: power.globals loaded -- session ready"\n'
        'puts "INFO:   TOP          : $TOP"\n'
        'puts "INFO:   power nets   : $PWR_NETS / $GND_NET"\n'
        'puts "INFO:   routed DEF   : $DEF_IN"\n'
        'puts "INFO:   SPEF (pe)    : $SPEF"\n'
        'puts "INFO:   FSDB (sim)   : $FSDB"\n'
    ),
    "setup/common_setup.tcl": COMMON_SETUP_A,
    "README.md": "# fake print\n",
}
# 3. fake_core_deleted (§4.9c 参考解删核心): full gold but defIn block removed
_PG_NO_DEFIN = GOLD_POWER_GLOBALS.replace(
    '''    # routed DEF adds layout + power grid (ring / stripes / M1 followpins),
    # which the power and IR views need
    if {![catch {defIn $DEF_IN} err]} {
        puts "INFO: defIn OK : $DEF_IN"
    } else {
        puts "WARN: defIn failed : $err"
        puts "WARN: physical view / power grid will be missing until a DEF is read"
    }
    catch {setMultiCpuUsage -localCpu 8}''',
    '''    # (defIn of routed DEF removed -- core deleted)
    catch {setMultiCpuUsage -localCpu 8}''')
NEG_FAKE_CORE = {
    "gui/power.globals": _PG_NO_DEFIN,
    "setup/common_setup.tcl": COMMON_SETUP_A,
    "README.md": README_MD,
}
# 4. naive_hardcode_a: A values hardcoded, no source common_setup
NEG_NAIVE_HARDCODE = {
    "gui/power.globals": (
        'set TOP "hl22_porting_test_chip_power"\n'
        "set ROOT /home/alan3zh/workspace/test_chip/test_chip\n"
        "set WORK_DIR $ROOT/apr/innovus/work\n"
        "set PDK_ROOT /apps/imctf/extpdk/HL22/LAGAT/Digital/current\n"
        "set TECH_LEF $PDK_ROOT/Innovus_tf/Au22_1P7M_4_1X_2_2X_1_8X_withRDL_HVH.tlef\n"
        "set CELL_LEF $PDK_ROOT/Au22_basic_lvt/lef/Au22_basic_lvt.lef\n"
        "set MMMC_VIEW $WORK_DIR/mmmc.view\n"
        "set PWR_NETS {VDD VDD_PM}\n"
        "set GND_NET VSS\n"
        "set IN_V $WORK_DIR/${TOP}.routed.v\n"
        "set DEF_IN $WORK_DIR/${TOP}.def\n"
        "set init_verilog $IN_V\n"
        "set init_lef_file [list $TECH_LEF $CELL_LEF]\n"
        "set init_top_cell $TOP\n"
        "set init_design_settop 1\n"
        "set init_pwr_net $PWR_NETS\n"
        "set init_gnd_net $GND_NET\n"
        "set init_mmmc_file $MMMC_VIEW\n"
        "catch {init_design}\n"
        "catch {defIn $DEF_IN}\n"
        'puts "INFO: power.globals loaded -- session ready"\n'
    ),
    "setup/common_setup.tcl": COMMON_SETUP_A,  # present but unused
    "README.md": "# naive hardcode\n",
}
# 5. naive_no_source: sources common_setup but hardcodes IN_V with A path
NEG_NAIVE_NOSOURCE = {
    "gui/power.globals": (
        "source ../setup/common_setup.tcl\n"
        "# hardcode A's routed netlist path instead of using $TOP/$WORK_DIR\n"
        "set IN_V /home/alan3zh/workspace/test_chip/test_chip/apr/innovus/work/hl22_porting_test_chip_power.routed.v\n"
        "set DEF_IN $WORK_DIR/${TOP}.def\n"
        "foreach f [list $TECH_LEF $CELL_LEF $MMMC_VIEW $IN_V $DEF_IN] {\n"
        "    if {![file exists $f]} { return }\n"
        "}\n"
        "set have_design 0\n"
        "catch { if {[llength [dbGet top.name]] > 0} { set have_design 1 } }\n"
        "if {!$have_design} {\n"
        "    set init_verilog $IN_V\n"
        "    set init_lef_file [list $TECH_LEF $CELL_LEF]\n"
        "    set init_top_cell $TOP\n"
        "    set init_design_settop 1\n"
        "    set init_pwr_net $PWR_NETS\n"
        "    set init_gnd_net $GND_NET\n"
        "    set init_mmmc_file $MMMC_VIEW\n"
        "    catch {init_design}\n"
        "    catch {defIn $DEF_IN}\n"
        "}\n"
        'puts "INFO: power.globals loaded -- session ready"\n'
    ),
    "setup/common_setup.tcl": COMMON_SETUP_A,
    "README.md": "# naive no-source\n",
}

NEGATIVES = {
    "fake_empty": (NEG_FAKE_EMPTY, "§4.9a 空壳"),
    "fake_print_expected": (NEG_FAKE_PRINT, "§4.9b 只print期望串"),
    "fake_core_deleted": (NEG_FAKE_CORE, "§4.9c 参考解删核心(defIn)"),
    "naive_hardcode_a": (NEG_NAIVE_HARDCODE, "naive A值硬编码无source"),
    "naive_no_source": (NEG_NAIVE_NOSOURCE, "naive source但IN_V硬编码A路径"),
}

# ---------------------------------------------------------------- build
def main():
    # 1. asset A
    cfg_dir = os.path.join(A, "apr_innovus_config")
    os.makedirs(cfg_dir, exist_ok=True)
    open(os.path.join(cfg_dir, "Makefile.init-vars"), "w").write(ASSET_MAKEFILE_INIT)
    open(os.path.join(cfg_dir, "mmmc.view"), "w").write(ASSET_MMMC_VIEW)
    open(os.path.join(cfg_dir, "innovus_fp_init.tcl"), "w").write(ASSET_FP_INIT)
    open(os.path.join(cfg_dir, "work_inventory.txt"), "w").write(ASSET_WORK_INV)
    open(os.path.join(cfg_dir, "power_nets.txt"), "w").write(ASSET_POWER_NETS)
    open(os.path.join(A, "task_brief.md"), "w").write(TASK_BRIEF)

    # hidden B under assets/<CASE>/apr_innovus_config/hidden/  (NOT in SUT sandbox)
    hid_dir = os.path.join(cfg_dir, "hidden")
    os.makedirs(hid_dir, exist_ok=True)
    open(os.path.join(hid_dir, "common_setup_B.tcl"), "w").write(COMMON_SETUP_B)
    open(os.path.join(hid_dir, "hidden_manifest.json"), "w").write(json.dumps({
        "id": CASE,
        "input": "B",
        "design": "hl22_io_ctrl_top",
        "differences_from_A": [
            "TOP: hl22_io_ctrl_top (A: hl22_porting_test_chip_power)",
            "TECH_LEF: Au22_..._VHV.tlef (A: ..._HVH.tlef)",
            "CELL_LEF: Au22_io_lvt.lef (A: Au22_basic_lvt.lef)",
            "PWR_NETS secondary: VDD_PE (A: VDD_PM)",
            "ROOT path: /home/baiqiu/workspace/io_ctrl/io_ctrl (A: /home/alan3zh/workspace/test_chip/test_chip)",
        ],
        "note": "check.py injects common_setup_B.tcl as setup/common_setup.tcl then tclsh-stub runs power.globals",
    }, indent=2, ensure_ascii=False))

    # 2. reference gold
    os.makedirs(os.path.join(R, "gui"), exist_ok=True)
    os.makedirs(os.path.join(R, "setup"), exist_ok=True)
    open(os.path.join(R, "gui", "power.globals"), "w").write(GOLD_POWER_GLOBALS)
    open(os.path.join(R, "setup", "common_setup.tcl"), "w").write(COMMON_SETUP_A)
    open(os.path.join(R, "README.md"), "w").write(README_MD)
    ref_zip = os.path.join(R, "reference_submit.zip")
    make_submit(ref_zip, {
        "gui/power.globals": GOLD_POWER_GLOBALS,
        "setup/common_setup.tcl": COMMON_SETUP_A,
        "README.md": README_MD,
    })
    open(os.path.join(R, "check.py"), "w").write(CHECK_PY)

    # 3. negatives + selftest
    neg_dir = os.path.join(R, "negative")
    os.makedirs(neg_dir, exist_ok=True)
    for name, (files, desc) in NEGATIVES.items():
        make_submit(os.path.join(neg_dir, name + ".zip"), files)
    neg_selftest = r'''#!/usr/bin/env python3
"""negative_selftest -- all 5 negatives must FAIL check()."""
import sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
CHK = os.path.join(HERE, "..", "check.py")
REF_ZIP = os.path.join(HERE, "..", "reference_submit.zip")
rc_all = 0
# ref must PASS
r = subprocess.run([sys.executable, CHK, REF_ZIP, HERE + "/.."], capture_output=True, text=True)
print("REF:", "PASS" if r.returncode == 0 else "FAIL", r.stdout.strip().splitlines()[-1] if r.stdout else "")
if r.returncode != 0:
    rc_all = 1
for name in ["fake_empty", "fake_print_expected", "fake_core_deleted", "naive_hardcode_a", "naive_no_source"]:
    z = os.path.join(HERE, name + ".zip")
    r = subprocess.run([sys.executable, CHK, z, HERE + "/.."], capture_output=True, text=True)
    verdict = "FAIL(as expected)" if r.returncode != 0 else "PASS(BAD!!)"
    print("NEG %-22s -> %s" % (name, verdict))
    if r.returncode == 0:
        rc_all = 1
sys.exit(rc_all)
'''
    open(os.path.join(neg_dir, "negative_selftest.py"), "w").write(neg_selftest)

    # 4. self-verify
    print("== self-verify ==")
    # ref PASS
    r = subprocess.run([sys.executable, os.path.join(R, "check.py"), ref_zip, R],
                       capture_output=True, text=True)
    print("REF check:", "PASS" if r.returncode == 0 else "FAIL", "| stdout:", r.stdout.strip()[-300:])
    if r.returncode != 0:
        print("STDERR:", r.stderr[-800:])
        print("ERROR: reference did not PASS -- aborting"); sys.exit(1)
    # negatives all FAIL
    neg_rc = subprocess.run([sys.executable, os.path.join(neg_dir, "negative_selftest.py")],
                            capture_output=True, text=True)
    print(neg_selftest and neg_rc.stdout)
    if neg_rc.returncode != 0:
        print("ERROR: negative_selftest did not all-FAIL -- aborting"); sys.exit(1)

    # 5. append jsonl
    test_src = open(os.path.join(R, "check.py")).read()
    entry = {
        "task_id": CASE,
        "mode": "design_flow",
        "prompt": PROMPT,
        "attachments": [
            {"name": "apr_innovus_config/Makefile.init-vars", "source": "assets/%s/apr_innovus_config/Makefile.init-vars" % CASE, "desc": "apr/innovus/Makefile 初始化变量节（TOP/NETLIST/PDK 路径/LEF/LIB/电源网络）—— 真实 trace 本地副本"},
            {"name": "apr_innovus_config/mmmc.view", "source": "assets/%s/apr_innovus_config/mmmc.view" % CASE, "desc": "apr/innovus/gui/mmmc.view（单 corner ssg_0p72v_m40c，library_set + constraint_mode 带 2 SDC）—— 真实 trace 本地副本"},
            {"name": "apr_innovus_config/innovus_fp_init.tcl", "source": "assets/%s/apr_innovus_config/innovus_fp_init.tcl" % CASE, "desc": "innovus_fp.tcl 的 init_design 块（init_verilog/init_lef_file[tech-first]/init_top_cell/init_design_settop/init_pwr_net/init_gnd_net/init_mmmc_file + catch）—— 真实 trace 本地副本"},
            {"name": "apr_innovus_config/work_inventory.txt", "source": "assets/%s/apr_innovus_config/work_inventory.txt" % CASE, "desc": "apr/innovus/work 清单（routed.v/DEF/routed.db/mmmc.view/cts_clk.sdc + SPEF/FSDB 指针）—— 真实 trace 本地副本"},
            {"name": "apr_innovus_config/power_nets.txt", "source": "assets/%s/apr_innovus_config/power_nets.txt" % CASE, "desc": "电源/地网络（PWR_NETS={VDD VDD_PM}，VDD_PM pd_pm 域 grid TODO；GND_NET=VSS）—— 真实 trace 本地副本"},
            {"name": "task_brief.md", "source": "assets/%s/task_brief.md" % CASE, "desc": "交付接口说明（≤3 行：submit.zip 含 gui/power.globals+setup/common_setup.tcl+README.md，mode=design_flow/entry_point=outputs/submit.zip）"},
        ],
        "entry_point": "outputs/submit.zip",
        "expected_artifacts": ["gui/power.globals", "setup/common_setup.tcl", "README.md"],
        "test": test_src,
        "budget": {"max_turns": 20, "max_seconds": 1800},
        "metadata": {
            "domain": "pnr_signoff",
            "task_name": "Innovus 初始配置固化 (power.globals)",
            "scenario": "A档 trace-faithful: 把 apr/innovus 初始配置（Makefile 变量+mmmc.view+innovus_fp.tcl init_design 块）固化成 Innovus 可加载的 gui/power.globals，供后续功耗/IR/ECO GUI 任务",
            "difficulty": "L1-boundary",
            "artifacts": ["gui/power.globals", "setup/common_setup.tcl", "README.md"],
            "track": "faithful",
            "test_rationale": (
                "20 条断言：① submit.zip 含 gui/power.globals+setup/common_setup.tcl+README.md（对象:zip内容;判定:三文件皆存在）"
                " ② power.globals source common_setup.tcl（对象:脚本;判定:含 source ...common_setup.tcl）"
                " ③ init_lef_file=[list $TECH_LEF $CELL_LEF] tech-first（对象:init_lef_file;判定:tech LEF 在前）"
                " ④ set init_design_settop 1（对象:init_design_settop;判定:值为1）"
                " ⑤ init_design 在 catch 内（对象:init_design;判定:错误守护）"
                " ⑥ defIn 在 catch 内（对象:defIn;判定:读布线DEF带电源网格）"
                " ⑦ have_design 守护用 dbGet top.name（对象:加载前探测;判定:已有设计则跳过init）"
                " ⑧ 文件存在性预检 foreach+file exists+return（对象:输入预检;判定:缺失即中止）"
                " ⑨ INFO 指针含 power nets/SPEF/FSDB（对象:puts指针;判定:后续任务路径齐备）"
                " ⑩ 活跃代码无 A 字面量硬编码 hl22_porting_test_chip_power/VDD_PM/Au22_basic_lvt（对象:power.globals;判定:设计相关值来自common_setup）"
                " ⑪ 跨输入守护 stub init_verilog==B 的 hl22_io_ctrl_top.routed.v（对象:init_verilog;判定:B值流过非A）"
                " ⑫ stub init_top_cell==hl22_io_ctrl_top（对象:init_top_cell;判定:B设计名）"
                " ⑬ stub init_pwr_net 含 VDD_PE 不含 VDD_PM（对象:init_pwr_net;判定:B电源域）"
                " ⑭ stub init_lef_file 含 VHV+io_lvt 且 tech-first 不含 HVH/basic_lvt（对象:init_lef_file;判定:B的LEF）"
                " ⑮ stub init_mmmc_file==B 的 io_ctrl/work/mmmc.view（对象:init_mmmc_file;判定:B的MMVC）"
                " ⑯ stub defIn==B 的 hl22_io_ctrl_top.def（对象:defIn;判定:B的DEF）"
                " ⑰ stub init_gnd_net==VSS（对象:init_gnd_net;判定:地网络）"
                " ⑱ stub stdout 含 'power.globals loaded -- session ready'（对象:运行完成;判定:init分支执行到底）"
                " ⑲ stub stdout 无 A 字面量泄漏（对象:运行时输出;判定:无hl22_porting_test_chip_power/VDD_PM/Au22_basic_lvt）"
                " ⑳ stub init_design_settop==1（对象:init_design_settop;判定:置顶设置传递）"
            ),
            "trace_source": {
                "user": "alan3zh",
                "host": "hfeg0plg49",
                "session_file": "1792399916731_00i9f.messages.json",
                "match_count": 101,
                "real_task_summary": (
                    "test_chip 数字后端链路：把 apr/innovus 的初始配置（Makefile 变量 + gui/mmmc.view + "
                    "innovus_fp.tcl init_design 块）固化成 Innovus 可加载的 gui/power.globals（init_* 全局变量 + "
                    "init_design + defIn 布线DEF带电源网格 + have_design 探测 + INFO 后续任务指针），供 GUI 做后续功耗/IR/ECO。"
                    "真实 trace #17 用户原话『将apr/innovus下的初始配置，写入apr/innovus/gui/power.globals中，"
                    "使其能在innovus中进行后续任务』。最终接受 power.globals（102 行 Tcl）。"
                    "顺带收尾 RedHawk 经典版 pp 流（Makefile/README）。"
                    "Innovus 23.35，TOP=hl22_porting_test_chip_power，PWR={VDD,VDD_PM}/GND=VSS，单 corner ssg_0p72v_m40c。"
                ),
            },
        },
    }
    # roundtrip check: test field == disk check.py
    assert test_src == open(os.path.join(R, "check.py")).read(), "test field != disk check.py"
    with open(JSONL, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("== appended %s to %s ==" % (CASE, os.path.basename(JSONL)))

    # 6. count
    n = sum(1 for _ in open(JSONL))
    print("A jsonl now %d lines" % n)
    print("DONE")

if __name__ == "__main__":
    main()
