#!/usr/bin/env python3
"""Builder for EDA-Eval-DesignFlow-DcPolicyRemoveMigrate-001 (shard A, r217).

Trace: johnl@hfeg0pkn001 session 1793933023338_1uxza (A档 faithful).
Task: migrate the "copy" DC scripts (from /home/EDA env) to a self-contained
      local project using 3 new libraries, AND -- per user clarification
      "不用管原来的检查啊不准用的啥的所有的都可以用" -- REMOVE the cell
      allow/forbid policy entirely (distinct from DcScriptMigrate-001 which
      KEEPS/fixes the policy).

Distinctness vs DcScriptMigrate-001 (i7eyp, r214):
  - i7eyp check VERIFIES the policy is kept + LVS-bug fixed (CUSTOM_CELLS,
    ORDINARY_CELL_PATTERN with LVS-first, set_dont_use marking).
  - THIS case check VERIFIES the policy is REMOVED (no CUSTOM_CELLS, no
    ORDINARY_CELL_PATTERN, no set_dont_use marking, no cell-count assertions),
    only clear dont_use/dont_touch markers + is_unmapped guard.
  Opposite transformations -> genuinely distinct cases.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
import py_compile

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "DcPolicyRemoveMigrate-001"                      # dir name (assets/reference)
CASE_ID = "EDA-Eval-DesignFlow-DcPolicyRemoveMigrate-001"  # full task_id in jsonl
ASSETS = os.path.join(REPO, "assets", CASE)
REF = os.path.join(REPO, "reference", CASE)
GOLD = os.path.join(REF, "dc_policy_remove_migrate.py")

# ---------------- A (visible) copy scripts (verbatim from 1uxza trace) ----------------
A_COPY_RUN_DC = '''#!/usr/bin/env bash
set -euo pipefail

# Edit these absolute paths to select the input and where new runs are saved.
SCRIPT_DIR=/home/EDA/rowred_work/behavioral_rebuild_20261103/restricted_lv_l_gs_custom_non_oa_20261105_r4/standalone_dc
OUTPUT_ROOT=/home/EDA/rowred_work/behavioral_rebuild_20261103/restricted_lv_l_gs_custom_non_oa_20261105_r4/standalone_dc/outputs
DC=/home/EDA/synopsys/syn/X-2025.06-SP3/amd64/syn/bin/dc_shell
GUARD=/usr/local/sbin/eda-guard

test -r "$SCRIPT_DIR/synth.tcl"
test -r "$SCRIPT_DIR/timing_constraints.tcl"
test -x "$DC"
test -x "$GUARD"
mkdir -p "$OUTPUT_ROOT"
RUN_DIR=$(mktemp -d "$OUTPUT_ROOT/run_$(date +%Y%m%d_%H%M%S)_XXXX")
echo "DC output: $RUN_DIR"
cd "$RUN_DIR"
"$GUARD" "$DC" -f "$SCRIPT_DIR/synth.tcl" > dc.log 2>&1
echo "Completed: $RUN_DIR"
'''

A_COPY_SYNTH = '''# Edit inputs here. This script runs from run_dc.sh and writes into its run directory.
# The historical r4 run used a separate 1,092-component multibit grouping plan
# and an extra area-recovery pass. This readable three-file flow omits those
# steps, so its mapped netlist and area will not exactly reproduce r4.
set RTL /home/EDA/rowred_work/behavioral_rebuild_20261103/non_oa_phase_ms_r6/rowred_behavioral.v
set LIB_DB /home/EDA/rowred_work/behavioral_rebuild_20261103/mapping_library_cell_area_bank42_cmp6/stdcells.db
set LIB_NAME rowred_behavioral_cell_mapping_area_objective
set CONSTRAINTS /home/EDA/rowred_work/behavioral_rebuild_20261103/restricted_lv_l_gs_custom_non_oa_20261105_r4/standalone_dc/timing_constraints.tcl
set TOP R_RowRed1024_full

proc fail {message} {puts stderr "ROWRED_DC_FAIL: $message"; exit 2}
foreach path [list $RTL $LIB_DB $CONSTRAINTS] {
    if {![file readable $path]} {fail "Input not readable: $path"}
}

set target_library [list $LIB_DB]
set link_library [concat * $target_library]
read_db $LIB_DB
set_host_options -max_cores 2
set_svf mapped.svf
set_app_var verilogout_no_tri true
set_app_var hdlin_infer_multibit default_all
read_verilog $RTL
current_design $TOP
if {![link]} {fail "Top failed to link"}

# The original policy allows the LV, L and GS ordinary-cell families plus
# these eight unchanged RowRed custom cells (some have LVS in their names).
set CUSTOM_CELLS {
    latbank_RowRed_AF2_invLVSx1 latbank_RowRed_AF4_invLVSx1
    latcmp_RowRed_AF latqn_RowRed_AF latqn_RowRed_AF_lvclk1
    latqn_RowRed_fuse3 latqn_RowRed_fuse3_lvclk1
    xnor2_RowRed_cmp4_invLVSx1
}
set ORDINARY_CELL_PATTERN {^(inv|buf|nand[0-9]|nor[0-9]|and[0-9]|or[0-9]|aoi[0-9]+|oai[0-9]+|xor[0-9]|xnor[0-9])(LV|L|GS)x[0-9]+(_pc60)?$}
set inventory [get_lib_cells $LIB_NAME/*]
if {[sizeof_collection $inventory] != 633} {fail "Expected 633 library cells"}
set allowed 0
set blocked 0
foreach_in_collection libcell $inventory {
    set name [lindex [split [get_object_name $libcell] /] end]
    # Library Compiler can mark measured compound cells dont_touch by default.
    remove_attribute -quiet $libcell dont_use
    remove_attribute -quiet $libcell dont_touch
    if {[regexp $ORDINARY_CELL_PATTERN $name] || $name in $CUSTOM_CELLS] {
        incr allowed
    } else {
        set_dont_use $libcell
        incr blocked
    }
}
if {$allowed != 239 || $blocked != 394} {
    fail "Cell policy changed: allowed=$allowed forbidden=$blocked"
}
foreach_in_collection cell [get_cells -hierarchical -filter "dont_touch == true"] {
    remove_attribute -quiet $cell dont_touch
}
puts "CELL_POLICY allowed=$allowed forbidden=$blocked"

source $CONSTRAINTS
apply_synthesis_constraints
redirect check_before.rpt {check_design}
if {![compile_ultra -area_high_effort_script]} {fail "Area synthesis failed"}
if {![compile_ultra -incremental]} {fail "Incremental synthesis failed"}
optimize_netlist -area
define_name_rules rr_scalar -allowed "a-z A-Z 0-9 _" -first_restricted "0-9" -map {{{\\[} _} {{\\]} _} {: _}}
change_names -rules rr_scalar -hierarchy

proc check_mapping {stage} {
    global CUSTOM_CELLS ORDINARY_CELL_PATTERN
    set bad {}
    foreach_in_collection cell [get_cells -hierarchical] {
        set name [get_attribute $cell ref_name]
        if {[regexp $ORDINARY_CELL_PATTERN $name] || $name in $CUSTOM_CELLS} {continue}
        if {$name in {**logic_0** **logic_1**}} {continue}
        lappend bad "[get_object_name $cell]:$name"
    }
    if {[llength $bad]} {fail "$stage has forbidden/unmapped cells: [lrange $bad 0 9]"}
    puts "MAPPING_PASS $stage"
}
check_mapping synthesis
redirect synth_area.rpt {report_area}
redirect synth_timing.rpt {report_timing -max_paths 30 -significant_digits 6}
write -format verilog -hierarchy -output synth_mapped.v
write -format ddc -hierarchy -output synth_mapped.ddc
write_sdc synth_mapped.sdc

# Same-session hold repair; the mapped design and target policy remain loaded.
set_fix_multiple_port_nets -all [current_design]
if {![compile -incremental_mapping -only_design_rule]} {fail "Design-rule repair failed"}
apply_hold_constraints
redirect hold_before.rpt {report_timing -delay_type min -max_paths 30 -significant_digits 6}
if {![compile -incremental_mapping -only_hold_time]} {fail "Hold repair failed"}
for {set pass 0} {$pass < 2} {incr pass} {
    redirect -variable result {report_timing -delay_type min -max_paths 1 -significant_digits 9}
    if {![regexp {slack \\((MET|VIOLATED)\\)\\s+([-0-9.]+)} $result unused state slack]} {
        fail "Missing minimum-path report"
    }
    if {$slack >= 0} {break}
    if {![compile -incremental_mapping -only_hold_time]} {fail "Residual hold repair failed"}
}
check_mapping hold
redirect hold_after.rpt {report_timing -delay_type min -max_paths 30 -significant_digits 6}
redirect final_constraints.rpt {report_constraint -all_violators -significant_digits 6}
redirect final_area.rpt {report_area}
redirect final_references.rpt {report_reference -hierarchy}
write -format verilog -hierarchy -output hold_mapped.v
write -format ddc -hierarchy -output hold_mapped.ddc
write_sdc hold_mapped.sdc
puts "ROWRED_DC_COMPLETE"
quit
'''

A_COPY_SDC = '''# Units: ns and pF. The first procedure is applied before synthesis.
proc apply_synthesis_constraints {} {
    foreach port {rrp_vcc_ rrp_vbp_} {
        set pin [get_ports -quiet $port]
        if {[sizeof_collection $pin]} {set_case_analysis 1 $pin}
    }
    foreach port {rrp_vss_ rrp_vbn_} {
        set pin [get_ports -quiet $port]
        if {[sizeof_collection $pin]} {set_case_analysis 0 $pin}
    }
    set_input_transition 0.100 [all_inputs]
    set_load 0.012 [all_outputs]
    set_max_transition 0.500 [current_design]
    set_max_capacitance 0.120 [current_design]
    set_max_delay 1.600 -from [all_inputs] -to [all_outputs]
    set_max_area 0
    # The source run used RR_MAX_FANOUT=0, so there is no extra fanout limit.
}

# These are protocol reference clocks for minimum-path repair, not a
# frequency or cross-domain setup signoff for the aperiodic protocol.
proc apply_hold_constraints {} {
    foreach spec {
        {EF0 rrp_EFsDataLd_0_ 32 {4 10}}
        {EF1 rrp_EFsDataLd_1_ 32 {16 22}}
        {FS rrp_FsLdClk 8 {0 4}}
        {SPPR rrp_SPPRWR 32 {6 14}}
    } {
        lassign $spec name port period edges
        if {[sizeof_collection [get_ports -quiet $port]] != 1} {
            error "Missing protocol input $port"
        }
        create_clock -name $name -period $period -waveform $edges [get_ports $port]
    }
    set_propagated_clock [all_clocks]
    set_clock_groups -asynchronous -group [get_clocks EF0] -group [get_clocks EF1] -group [get_clocks FS] -group [get_clocks SPPR]
    set_clock_uncertainty -hold 0.025 [all_clocks]
    set_fix_hold [all_clocks]
}
'''

A_META = {
    "case_id": CASE_ID,
    "top_module": "R_RowRed1024_full",
    "rtl_filename": "rowred_behavioral.restored.v",
    "rtl_dir": "rtl",
    "constraints_filename": "timing_constraints.tcl",
    "libraries": [
        {"tag": "GS",     "db_filename": "stdcells_ac_all_comb_SS_0p98_m40c_GS.db",   "logical_name": "SS_0p98_m40c"},
        {"tag": "CUSTOM", "db_filename": "rowred_new_cells_v2_SS_0p98_m40.db",        "logical_name": "rowred_new_cells_v2_SS_0p98_m40"},
        {"tag": "LVS",    "db_filename": "stdcells_ac_all_comb_SS_0p98_m40c_lvs.db",  "logical_name": "SS_0p98_m40c"},
    ],
    "custom_cells": [
        "latqn_RowRed_AF_lvclk1",
        "latbank_RowRed_AF2_invLVSx1",
        "latbank_RowRed_AF4_invLVSx1",
        "xnor2_RowRed_cmp4_invLVSx1",
    ],
    "copy_synth": "copy_synth.tcl",
    "copy_run_dc": "copy_run_dc.sh",
    "copy_sdc": "copy_sdc.sdc",
    "source_environment_root": "/home/EDA/rowred_work/behavioral_rebuild_20261103",
}

# ---------------- B (hidden) -- structurally distinct, zero key-identifier overlap ----------------
B_META = {
    "case_id": CASE_ID,
    "top_module": "D_DspWrap512_full",
    "rtl_filename": "dspwrap_behavioral.v",
    "rtl_dir": "rtl",
    "constraints_filename": "timing_constraints.tcl",
    "libraries": [
        {"tag": "GS",     "db_filename": "stdcells_ac_all_comb_FF_1p3_m40c_GS.db",   "logical_name": "FF_1p3_m40c"},
        {"tag": "CUSTOM", "db_filename": "dspwrap_new_cells_v3_FF_1p3_m40.db",       "logical_name": "dspwrap_new_cells_v3_FF_1p3_m40"},
        {"tag": "LVS",    "db_filename": "stdcells_ac_all_comb_FF_1p3_m40c_lvs.db",  "logical_name": "FF_1p3_m40c"},
    ],
    "custom_cells": [
        "latqn_DspWrap_AF_lvclk1",
        "latbank_DspWrap_AF2_invLVSx1",
        "latbank_DspWrap_AF4_invLVSx1",
        "xnor2_DspWrap_cmp8_invLVSx1",
        "latcmp_DspWrap_AF",
        "latqn_DspWrap_fuse3",
    ],
    "copy_synth": "copy_synth.tcl",
    "copy_run_dc": "copy_run_dc.sh",
    "copy_sdc": "copy_sdc.sdc",
    "source_environment_root": "/home/EDA/rowred_work/dspwrap_rebuild_20261120",
}

# B copy scripts: transform A's by substitution (different root, libs, top, cells, counts).
B_COPY_RUN_DC = A_COPY_RUN_DC.replace(
    "/home/EDA/rowred_work/behavioral_rebuild_20261103/restricted_lv_l_gs_custom_non_oa_20261105_r4/standalone_dc",
    "/home/EDA/rowred_work/dspwrap_rebuild_20261120/dspwrap_lv_l_gs_custom_20261125_r2/standalone_dc")

B_COPY_SYNTH = (A_COPY_SYNTH
    .replace("/home/EDA/rowred_work/behavioral_rebuild_20261103/non_oa_phase_ms_r6/rowred_behavioral.v",
             "/home/EDA/rowred_work/dspwrap_rebuild_20261120/wrap_phase_r3/dspwrap_behavioral.v")
    .replace("/home/EDA/rowred_work/behavioral_rebuild_20261103/mapping_library_cell_area_bank42_cmp6/stdcells.db",
             "/home/EDA/rowred_work/dspwrap_rebuild_20261120/mapping_library_dspwrap_bank8_cmp4/stdcells_dspwrap.db")
    .replace("rowred_behavioral_cell_mapping_area_objective",
             "dspwrap_cell_mapping_area_objective")
    .replace("/home/EDA/rowred_work/behavioral_rebuild_20261103/restricted_lv_l_gs_custom_non_oa_20261105_r4/standalone_dc/timing_constraints.tcl",
             "/home/EDA/rowred_work/dspwrap_rebuild_20261120/dspwrap_lv_l_gs_custom_20261125_r2/standalone_dc/timing_constraints.tcl")
    .replace("R_RowRed1024_full", "D_DspWrap512_full")
    .replace("latbank_RowRed_AF2_invLVSx1", "latbank_DspWrap_AF2_invLVSx1")
    .replace("latbank_RowRed_AF4_invLVSx1", "latbank_DspWrap_AF4_invLVSx1")
    .replace("latcmp_RowRed_AF", "latcmp_DspWrap_AF")
    .replace("latqn_RowRed_AF_lvclk1", "latqn_DspWrap_AF_lvclk1")
    .replace("latqn_RowRed_fuse3", "latqn_DspWrap_fuse3")
    .replace("xnor2_RowRed_cmp4_invLVSx1", "xnor2_DspWrap_cmp8_invLVSx1")
    .replace("ROWRED_DC_FAIL", "DSPWRAP_DC_FAIL")
    .replace("ROWRED_DC_COMPLETE", "DSPWRAP_DC_COMPLETE")
    .replace("!= 633", "!= 712")
    .replace("Expected 633 library cells", "Expected 712 library cells")
    .replace("$allowed != 239 || $blocked != 394", "$allowed != 312 || $blocked != 400")
    .replace("Cell policy changed: allowed=$allowed forbidden=$blocked",
             "DspWrap policy changed: allowed=$allowed forbidden=$blocked")
    .replace("CELL_POLICY allowed=$allowed forbidden=$blocked",
             "CELL_POLICY allowed=$allowed forbidden=$blocked"))

B_COPY_SDC = (A_COPY_SDC
    .replace("rrp_vcc_", "dwp_vcc_").replace("rrp_vbp_", "dwp_vbp_")
    .replace("rrp_vss_", "dwp_vss_").replace("rrp_vbn_", "dwp_vbn_")
    .replace("rrp_EFsDataLd_0_", "dwp_EFsDataLd_0_").replace("rrp_EFsDataLd_1_", "dwp_EFsDataLd_1_")
    .replace("rrp_FsLdClk", "dwp_FsLdClk").replace("rrp_SPPRWR", "dwp_SPPRWR")
    .replace("Missing protocol input", "Missing DspWrap protocol input"))


def write_assets():
    os.makedirs(ASSETS, exist_ok=True)
    os.makedirs(os.path.join(ASSETS, "hidden"), exist_ok=True)
    # A prompt (user msg 0 + msg 28 verbatim from 1uxza trace)
    prompt = (
        "/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/run_dc.sh    "
        "/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/synth.tcl    "
        "/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/T_mBistTopNew.sdc       "
        "这几个是在本机之前跑通过的dc脚本。后面带copy的是其他环境迁移过来的脚本 "
        "我现在要跑迁移过来的在本机，你需要帮我修改迁移过来的脚本以便能在本机运行，库要换一下 "
        "/home/johnl/.cline/scripts/data/primelib/primelib_char_all_comb/output/stdcells_ac_all_comb_SS_0p98_m40c_GS.db  "
        "/home/johnl/.cline/scripts/data/primelib/rowred_new_cells_v2_SS_0p98_m40.db  "
        "/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/output/stdcells_ac_all_comb_SS_0p98_m40c_lvs.db  "
        "用上面这三个库，rtl 用这个/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/rtl/rowred_behavioral.restored.v  "
        "请进行修改 修改后diff 检查修改前后的必要性和准确性 然后跑dc ，"
        "你要在/home/johnl/.cline/scripts/data/ 下单独建立一个工程目录并且 所有用到的文件复制到这个目录里 不能引用其他目录到文件你懂我意思吗\n\n"
        "（后续补充）不用管原来的检查啊不准用的啥的所有的都可以用\n")
    with open(os.path.join(ASSETS, "prompt.txt"), "w") as f:
        f.write(prompt)
    brief = (
        "交付接口：把迁移脚本 `dc_policy_remove_migrate.py` 打包成 `outputs/submit.zip`。\n"
        "脚本签名：`dc_policy_remove_migrate.py --project <dir> --out <dir>`，"
        "`<dir>` 含 `copy_synth.tcl` / `copy_run_dc.sh` / `copy_sdc.sdc` / `lib_metadata.json`，"
        "`<out>` 为待生成的自包含工程目录。\n"
        "脚本需在 `<out>` 下生成 `synth.tcl`、`run_dc.sh`、`timing_constraints.tcl`"
        "（自包含，路径相对 `$SCRIPT_DIR`，不引用工程外文件；按用户指示删除原有 cell 白名单/dont_use 策略，所有库内 cell 均可用）。\n")
    with open(os.path.join(ASSETS, "task_brief.md"), "w") as f:
        f.write(brief)
    with open(os.path.join(ASSETS, "copy_run_dc.sh"), "w") as f:
        f.write(A_COPY_RUN_DC)
    with open(os.path.join(ASSETS, "copy_synth.tcl"), "w") as f:
        f.write(A_COPY_SYNTH)
    with open(os.path.join(ASSETS, "copy_sdc.sdc"), "w") as f:
        f.write(A_COPY_SDC)
    with open(os.path.join(ASSETS, "lib_metadata.json"), "w") as f:
        json.dump(A_META, f, indent=2, ensure_ascii=False)
    # hidden B
    with open(os.path.join(ASSETS, "hidden", "copy_run_dc.sh"), "w") as f:
        f.write(B_COPY_RUN_DC)
    with open(os.path.join(ASSETS, "hidden", "copy_synth.tcl"), "w") as f:
        f.write(B_COPY_SYNTH)
    with open(os.path.join(ASSETS, "hidden", "copy_sdc.sdc"), "w") as f:
        f.write(B_COPY_SDC)
    with open(os.path.join(ASSETS, "hidden", "lib_metadata.json"), "w") as f:
        json.dump(B_META, f, indent=2, ensure_ascii=False)
    hmanifest = {
        "case_id": CASE_ID,
        "hidden_set": "B",
        "description": ("Synthetic DspWrap DC migration, structurally parallel to A but with "
                        "zero identifier overlap (different top module D_DspWrap512_full, FF-corner "
                        "db filenames, dspwrap custom cells, dwp_ ports, hardcoded counts 712/312/400). "
                        "Candidate must generalize and produce a correct self-contained policy-REMOVED flow for B."),
        "files": ["copy_synth.tcl", "copy_run_dc.sh", "copy_sdc.sdc", "lib_metadata.json"],
        "identifier_overlap_with_A": [],
    }
    with open(os.path.join(ASSETS, "hidden", "hidden_manifest.json"), "w") as f:
        json.dump(hmanifest, f, indent=2, ensure_ascii=False)
    print("assets written")


CHECK_PY = r'''#!/usr/bin/env python3
"""Checker for EDA-Eval-DesignFlow-DcPolicyRemoveMigrate-001.

deliverable: path to submit.zip (must contain dc_policy_remove_migrate.py)
workdir:     SUT workdir (unused; hidden B resolved relative to this check.py)

The candidate migration script is run on the HIDDEN set B. The adapted DC
scripts produced for B are validated against 15 independent conditions (a-o),
focused on the DISTINCT angle of THIS case: the cell allow/forbid policy must
be REMOVED entirely (no whitelist, no dont_use marking, no cell-count
assertions), only dont_touch/dont_use markers cleared + is_unmapped guard.

Distinct from DcScriptMigrate-001 (which VERIFIES the policy is kept + fixed).
"""
import os
import re
import sys
import shutil
import zipfile
import subprocess
import tempfile
import py_compile

CASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(CASE_DIR, "..", "..", "assets", "DcPolicyRemoveMigrate-001"))
A_PROJECT = ASSETS
B_PROJECT = os.path.join(ASSETS, "hidden")

COND = []


def _fail(label, msg):
    raise AssertionError("[%s] %s" % (label, msg))


def _candidate_ok(zip_path, tmp):
    """a: zip valid + contains dc_policy_remove_migrate.py + no forbidden calls."""
    if not os.path.isfile(zip_path):
        _fail("a", "submit.zip missing: %s" % zip_path)
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        if not any(n.endswith("dc_policy_remove_migrate.py") for n in names):
            _fail("a", "dc_policy_remove_migrate.py not in zip: %s" % names)
        z.extractall(tmp)
    cand = None
    for root, _, files in os.walk(tmp):
        for fn in files:
            if fn == "dc_policy_remove_migrate.py":
                cand = os.path.join(root, fn)
    if cand is None:
        _fail("a", "dc_policy_remove_migrate.py not found after extract")
    with open(cand) as f:
        src = f.read()
    for pat in ["os.system(", "shell=True", "eval(", "exec(", "__import__",
                "os.popen(", "os.exec"]:
        if pat in src:
            _fail("a", "forbidden call pattern %r in candidate" % pat)
    return cand


def _compile(cand):
    """b: candidate py_compiles."""
    try:
        py_compile.compile(cand, doraise=True)
    except py_compile.PyCompileError as e:
        _fail("b", "py_compile failed: %s" % e)


def _run(cand, project, out):
    os.makedirs(out, exist_ok=True)
    try:
        r = subprocess.run([sys.executable, cand, "--project", project, "--out", out],
                           capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        _fail("c", "candidate timed out on project %s" % project)
    return r


def _produced(out, meta, r):
    """c: candidate exits 0 and produces the 3 adapted files for B."""
    if r.returncode != 0:
        _fail("c", "candidate rc=%d stderr=%s" % (r.returncode, r.stderr[:300]))
    synth = os.path.join(out, "synth.tcl")
    run_dc = os.path.join(out, "run_dc.sh")
    cons = os.path.join(out, meta["constraints_filename"])
    for p, tag in [(synth, "synth.tcl"), (run_dc, "run_dc.sh"), (cons, meta["constraints_filename"])]:
        if not os.path.isfile(p) or os.path.getsize(p) == 0:
            _fail("c", "missing/empty %s" % tag)
    return synth, run_dc, cons


def _read(p):
    with open(p) as f:
        return f.read()


def _b_libs_ref(synth, meta):
    """d: synth.tcl references all 3 B .db libs (read_db each, by B db filename)."""
    for lib in meta["libraries"]:
        if lib["db_filename"] not in synth:
            _fail("d", "B lib %s not referenced in synth.tcl" % lib["db_filename"])
        if not re.search(r'read_db\s+\$LIB_DB_%s' % re.escape(lib["tag"]), synth):
            _fail("d", "read_db $LIB_DB_%s missing in synth.tcl" % lib["tag"])


def _b_target_list(synth, meta):
    """e: target_library = list containing the 3 B .db paths (not logical names)."""
    m = re.search(r'set target_library\s*\[list([^\]]*)\]', synth)
    if not m:
        _fail("e", "set target_library [list ...] not found")
    body = m.group(1)
    for lib in meta["libraries"]:
        if "$LIB_DB_%s" % lib["tag"] not in body:
            _fail("e", "$LIB_DB_%s not in target_library list" % lib["tag"])
    # must NOT use the logical name as target
    for lib in meta["libraries"]:
        if re.search(r'set target_library[^=]*=\s*%s' % re.escape(lib["logical_name"]), synth):
            _fail("e", "target_library uses logical name %s" % lib["logical_name"])


def _no_policy_whitelist(synth):
    """f: POLICY REMOVED -- no set CUSTOM_CELLS whitelist in synth.tcl."""
    if re.search(r'^\s*set\s+CUSTOM_CELLS\s*\{', synth, re.M):
        _fail("f", "set CUSTOM_CELLS whitelist still present (policy not removed)")


def _no_ordinary_pattern(synth):
    """g: POLICY REMOVED -- no set ORDINARY_CELL_PATTERN in synth.tcl."""
    if re.search(r'^\s*set\s+ORDINARY_CELL_PATTERN', synth, re.M):
        _fail("g", "set ORDINARY_CELL_PATTERN still present (policy not removed)")


def _no_dont_use_marking(synth):
    """h: POLICY REMOVED -- no set_dont_use MARKING of libcells (remove_attribute is OK)."""
    # a policy-removal flow must NOT call set_dont_use to forbid cells
    if re.search(r'^\s*set_dont_use\s+\$libcell', synth, re.M):
        _fail("h", "set_dont_use $libcell marking still present (policy not removed)")


def _no_cell_count_assertion(synth):
    """i: POLICY REMOVED -- no hardcoded cell-count assertion."""
    bad = [r'sizeof_collection[^)]*\)\s*!=\s*\d+',
           r'Expected\s+\d+\s+library\s+cells',
           r'allowed\s*!=\s*\d+\s*\|\|\s*\$blocked\s*!=\s*\d+',
           r'Cell policy changed']
    for pat in bad:
        if re.search(pat, synth):
            _fail("i", "hardcoded cell-count assertion present: %r" % pat)


def _clears_markers(synth):
    """j: synth.tcl clears dont_use/dont_touch markers (remove_attribute)."""
    if not re.search(r'remove_attribute\s+-quiet\s+\$libcell\s+dont_use', synth):
        _fail("j", "remove_attribute $libcell dont_use (clear marker) missing")
    if not re.search(r'remove_attribute\s+-quiet\s+\$libcell\s+dont_touch', synth):
        _fail("j", "remove_attribute $libcell dont_touch (clear marker) missing")


def _check_mapping_unmapped_only(synth):
    """k: check_mapping uses is_unmapped only (no ORDINARY_CELL_PATTERN/CUSTOM_CELLS ref)."""
    m = re.search(r'proc\s+check_mapping\s*\{stage\}\s*\{(.*?)\n\}', synth, re.S)
    if not m:
        _fail("k", "check_mapping proc not found")
    body = m.group(1)
    if "ORDINARY_CELL_PATTERN" in body or "CUSTOM_CELLS" in body:
        _fail("k", "check_mapping still references policy (ORDINARY_CELL_PATTERN/CUSTOM_CELLS)")
    if "is_unmapped" not in body:
        _fail("k", "check_mapping does not use is_unmapped guard")


def _self_contained(synth, run_dc):
    """l: no /home/EDA or /home/<user> absolute paths in synth.tcl/run_dc.sh."""
    for name, txt in [("synth.tcl", synth), ("run_dc.sh", run_dc)]:
        if re.search(r'/home/EDA/', txt) or re.search(r'/home/[A-Za-z0-9_]+/\.cline', txt):
            _fail("l", "%s contains /home absolute path (not self-contained)" % name)


def _run_dc_no_guard(run_dc):
    """m: run_dc.sh -- no eda-guard, dc_shell from PATH, no /home/EDA/synopsys dc_shell path, no GUARD var."""
    # strip comment lines so a docstring mentioning "no eda-guard" does not trip the check
    functional = "\n".join(l for l in run_dc.splitlines() if not l.lstrip().startswith("#"))
    if "eda-guard" in functional or re.search(r'\bGUARD\b', functional):
        _fail("m", "eda-guard / GUARD var still present in run_dc.sh")
    if "/home/EDA/synopsys" in run_dc:
        _fail("m", "/home/EDA/synopsys dc_shell absolute path still present")
    if "dc_shell" not in run_dc:
        _fail("m", "dc_shell not invoked in run_dc.sh")
    # must use PATH-resolved dc_shell (command -v dc_shell or bare dc_shell), not an absolute path
    if re.search(r'=\s*/.+/dc_shell\b', run_dc):
        _fail("m", "dc_shell referenced by absolute path (not from PATH)")


def _anti_hardcode(synth, meta):
    """n: anti-hardcode -- TOP = B's top (not A's R_RowRed1024_full); no A-specific db filenames."""
    if "R_RowRed1024_full" in synth:
        _fail("n", "synth.tcl contains A's top module R_RowRed1024_full (hardcoded A)")
    if meta["top_module"] not in synth:
        _fail("n", "synth.tcl does not reference B's top module %s" % meta["top_module"])
    for a_db in ["stdcells_ac_all_comb_SS_0p98_m40c_GS.db",
                 "rowred_new_cells_v2_SS_0p98_m40.db",
                 "stdcells_ac_all_comb_SS_0p98_m40c_lvs.db"]:
        if a_db in synth:
            _fail("n", "synth.tcl contains A-specific db filename %s (hardcoded A)" % a_db)


def _run_dc_rtl_check(run_dc, meta):
    """o: run_dc.sh has RTL existence check (test -r ... rtl) AND tees dc.log."""
    if not re.search(r'test\s+-r\b.*rtl', run_dc):
        _fail("o", "run_dc.sh missing RTL existence check (test -r ... rtl)")
    if "tee dc.log" not in run_dc and "tee" not in run_dc:
        _fail("o", "run_dc.sh does not tee dc.log")
    if meta["rtl_filename"] not in run_dc and meta["rtl_dir"] not in run_dc:
        _fail("o", "run_dc.sh does not reference B's rtl dir/filename")


def check(deliverable, workdir):
    zip_path = deliverable
    if not isinstance(zip_path, str):
        zip_path = deliverable.get("submit.zip") or deliverable.get("path") or str(deliverable)
    tmp = tempfile.mkdtemp(prefix="chk_dcpr_")
    try:
        cand = _candidate_ok(zip_path, tmp)          # a
        COND.append(("a", "zip+candidate+no-forbidden"))
        _compile(cand)                                # b
        COND.append(("b", "py_compile"))
        with open(os.path.join(B_PROJECT, "lib_metadata.json")) as f:
            bmeta = json_load(f)
        out = os.path.join(tmp, "B_out")
        r = _run(cand, B_PROJECT, out)                # c
        synth_p, run_dc_p, cons_p = _produced(out, bmeta, r)
        COND.append(("c", "run B + 3 files produced"))
        synth = _read(synth_p); run_dc = _read(run_dc_p)
        _anti_hardcode(synth, bmeta)                  # n  (before d: catches hardcode-A first)
        COND.append(("n", "anti-hardcode (B top, no A dbs)"))
        _b_libs_ref(synth, bmeta)                     # d
        COND.append(("d", "3 B libs read_db"))
        _b_target_list(synth, bmeta)                  # e
        COND.append(("e", "target_library = 3 B .db paths"))
        _no_policy_whitelist(synth)                   # f
        COND.append(("f", "no CUSTOM_CELLS whitelist"))
        _no_ordinary_pattern(synth)                   # g
        COND.append(("g", "no ORDINARY_CELL_PATTERN"))
        _no_dont_use_marking(synth)                   # h
        COND.append(("h", "no set_dont_use marking"))
        _no_cell_count_assertion(synth)               # i
        COND.append(("i", "no cell-count assertion"))
        _clears_markers(synth)                        # j
        COND.append(("j", "clears dont_use/dont_touch markers"))
        _check_mapping_unmapped_only(synth)           # k
        COND.append(("k", "check_mapping is_unmapped only"))
        _self_contained(synth, run_dc)                # l
        COND.append(("l", "self-contained (no /home paths)"))
        _run_dc_no_guard(run_dc)                      # m
        COND.append(("m", "run_dc: no guard, dc_shell from PATH"))
        _run_dc_rtl_check(run_dc, bmeta)              # o
        COND.append(("o", "run_dc RTL check + tee log"))
        return {"pass": True, "conditions": COND, "k": len(COND)}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def json_load(f):
    import json
    return json.load(f)


if __name__ == "__main__":
    try:
        res = check(sys.argv[1] if len(sys.argv) > 1 else "submit.zip", ".")
        print("PASS", res["k"], "conditions")
    except AssertionError as e:
        print("FAIL", e)
        sys.exit(1)
'''


def write_check():
    os.makedirs(REF, exist_ok=True)
    with open(os.path.join(REF, "check.py"), "w") as f:
        f.write(CHECK_PY)
    print("check.py written")


# ---------------- negatives ----------------
def _negative(codename, body):
    """Write a negative candidate dc_policy_remove_migrate.py."""
    nd = os.path.join(REF, "negative")
    os.makedirs(nd, exist_ok=True)
    path = os.path.join(nd, codename + ".py")
    with open(path, "w") as f:
        f.write(body)
    return path


NEG_EMPTY = '''#!/usr/bin/env python3
import sys
# fake_empty: does nothing
if __name__ == "__main__":
    pass
'''

NEG_PRINT_EXPECTED = '''#!/usr/bin/env python3
# fake_print_expected: writes 3 files containing only expected marker strings +
# B's top/db names as plain text (passes anti-hardcode n) but no real migration
# (no read_db -> fails cond d).
import os, sys, argparse, json
ap = argparse.ArgumentParser(); ap.add_argument("--project", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
meta = json.load(open(os.path.join(a.project, "lib_metadata.json")))
os.makedirs(a.out, exist_ok=True)
libs = " ".join(l["db_filename"] for l in meta["libraries"])
open(os.path.join(a.out,"synth.tcl"),"w").write(
    "MAPPING_PASS hold\\nDC_POLICY_REMOVE_COMPLETE\\n"
    "set TOP %s\\nlibs: %s\\n" % (meta["top_module"], libs))
open(os.path.join(a.out,"run_dc.sh"),"w").write(
    "#!/usr/bin/env bash\\ntest -r %s/%s\\ndc_shell -no_gui -f synth.tcl 2>&1 | tee dc.log\\n"
    % (meta["rtl_dir"], meta["rtl_filename"]))
open(os.path.join(a.out, meta["constraints_filename"]),"w").write("proc apply_synthesis_constraints {} {}\\n")
'''

NEG_CORE_DELETED = '''#!/usr/bin/env python3
# fake_core_deleted: removes the policy block but check_mapping STILL uses
# ORDINARY_CELL_PATTERN (core deletion -> fails cond k).
import os, sys, argparse, json
sys.path.insert(0, %r)
import dc_policy_remove_migrate as gold
ap = argparse.ArgumentParser(); ap.add_argument("--project", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
meta = gold.load_meta(a.project)
os.makedirs(a.out, exist_ok=True)
synth = gold.synth_template(meta)
# re-inject a policy-referencing check_mapping (the bug)
bad_check = """proc check_mapping {stage} {
    global ORDINARY_CELL_PATTERN
    set bad {}
    foreach_in_collection cell [get_cells -hierarchical] {
        set name [get_attribute $cell ref_name]
        if {[regexp $ORDINARY_CELL_PATTERN $name]} {continue}
        if {[get_attribute $cell is_unmapped]} {lappend bad $name}
    }
    if {[llength $bad]} {fail "unmapped"}
    puts "MAPPING_PASS $stage"
}"""
synth = synth.replace("""proc check_mapping {stage} {
    set bad {}
    foreach_in_collection cell [get_cells -hierarchical] {
        set name [get_attribute $cell ref_name]
        if {$name in {**logic_0** **logic_1**}} {continue}
        if {[get_attribute $cell is_unmapped]} {lappend bad "[get_object_name $cell]:$name"}
    }
    if {[llength $bad]} {fail "$stage has unmapped cells: [lrange $bad 0 9]"}
    puts "MAPPING_PASS $stage"
}""", bad_check)
open(os.path.join(a.out,"synth.tcl"),"w").write(synth)
open(os.path.join(a.out,"run_dc.sh"),"w").write(gold.run_dc_template(meta))
open(os.path.join(a.out, meta["constraints_filename"]),"w").write(gold.constraints_from_sdc(a.project, meta))
''' % REF

NEG_KEEP_POLICY = '''#!/usr/bin/env python3
# naive_keep_policy: migrates paths/libs to B but KEEPS the cell policy
# (CUSTOM_CELLS + ORDINARY_CELL_PATTERN + set_dont_use marking + count assertion)
# -> fails cond f (and g/h/i).
import os, sys, argparse, json, re
sys.path.insert(0, %r)
import dc_policy_remove_migrate as gold
ap = argparse.ArgumentParser(); ap.add_argument("--project", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
meta = gold.load_meta(a.project)
os.makedirs(a.out, exist_ok=True)
synth = gold.synth_template(meta)
# re-inject the full policy block before "source $CONSTRAINTS"
policy = """
set CUSTOM_CELLS {
    latqn_DspWrap_AF_lvclk1
    latbank_DspWrap_AF2_invLVSx1
}
set ORDINARY_CELL_PATTERN {^(inv|buf|nand[0-9])(LV|L|GS)x[0-9]+(_pc60)?$}
set allowed 0; set blocked 0
foreach_in_collection lib $libs {
    set lname [get_object_name $lib]
    if {$lname eq "gtech" || $lname eq "standard.sldb"} continue
    foreach_in_collection libcell [get_lib_cells ${lname}/*] {
        set name [lindex [split [get_object_name $libcell] /] end]
        if {[regexp $ORDINARY_CELL_PATTERN $name] || $name in $CUSTOM_CELLS} {
            incr allowed
        } else {
            set_dont_use $libcell
            incr blocked
        }
    }
}
if {$allowed != 312 || $blocked != 400} { fail "Cell policy changed" }
"""
synth = synth.replace("source $CONSTRAINTS", policy + "\\nsource $CONSTRAINTS", 1)
open(os.path.join(a.out,"synth.tcl"),"w").write(synth)
open(os.path.join(a.out,"run_dc.sh"),"w").write(gold.run_dc_template(meta))
open(os.path.join(a.out, meta["constraints_filename"]),"w").write(gold.constraints_from_sdc(a.project, meta))
''' % REF

NEG_HARDCODE_A = '''#!/usr/bin/env python3
# naive_hardcode_a: produces correct structure but hardcodes A's db filenames
# and A's top module for B -> fails cond n (and d).
import os, sys, argparse, json, re
sys.path.insert(0, %r)
import dc_policy_remove_migrate as gold
ap = argparse.ArgumentParser(); ap.add_argument("--project", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()
ameta = json.load(open(os.path.join(a.project, "lib_metadata.json")))
# Force A's values regardless of B's metadata
ameta["top_module"] = "R_RowRed1024_full"
ameta["libraries"] = [
    {"tag":"GS","db_filename":"stdcells_ac_all_comb_SS_0p98_m40c_GS.db","logical_name":"SS_0p98_m40c"},
    {"tag":"CUSTOM","db_filename":"rowred_new_cells_v2_SS_0p98_m40.db","logical_name":"rowred_new_cells_v2_SS_0p98_m40"},
    {"tag":"LVS","db_filename":"stdcells_ac_all_comb_SS_0p98_m40c_lvs.db","logical_name":"SS_0p98_m40c"},
]
os.makedirs(a.out, exist_ok=True)
open(os.path.join(a.out,"synth.tcl"),"w").write(gold.synth_template(ameta))
open(os.path.join(a.out,"run_dc.sh"),"w").write(gold.run_dc_template(ameta))
open(os.path.join(a.out, ameta["constraints_filename"]),"w").write(gold.constraints_from_sdc(a.project, ameta))
''' % REF


def write_negatives():
    _negative("naive_empty", NEG_EMPTY)
    _negative("naive_print_expected", NEG_PRINT_EXPECTED)
    _negative("naive_core_deleted", NEG_CORE_DELETED)
    _negative("naive_keep_policy", NEG_KEEP_POLICY)
    _negative("naive_hardcode_a", NEG_HARDCODE_A)
    print("negatives written")


NEG_SELFTEST = r'''#!/usr/bin/env python3
"""negative_selftest for DcPolicyRemoveMigrate-001: all negatives must FAIL
the checker at distinct first-fail labels; the reference must PASS."""
import os, sys, subprocess, zipfile, shutil, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check as CHK

REF = os.path.dirname(os.path.abspath(__file__))
NEG = os.path.join(REF, "negative")
GOLD = os.path.join(REF, "dc_policy_remove_migrate.py")


def _zip(py):
    tmp = tempfile.mkdtemp()
    zpath = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zpath, "w") as z:
        z.write(py, "dc_policy_remove_migrate.py")
    return zpath


def _expect_fail(name):
    z = _zip(os.path.join(NEG, name + ".py"))
    try:
        CHK.check(z, ".")
        return None  # should have failed
    except AssertionError as e:
        msg = str(e)
        label = msg.split("]")[0].lstrip("[")
        return label
    except Exception as e:
        return "ERR:" + type(e).__name__ + ":" + str(e)[:120]


def main():
    # reference must PASS
    z = _zip(GOLD)
    res = CHK.check(z, ".")
    assert res["pass"], "REFERENCE must PASS but failed"
    print("REF_PASS k=%d" % res["k"])
    # negatives must FAIL at distinct labels
    expected = {
        "naive_empty": "c",
        "naive_print_expected": "d",
        "naive_core_deleted": "k",
        "naive_keep_policy": "f",
        "naive_hardcode_a": "n",
    }
    seen = {}
    all_ok = True
    for name, exp in expected.items():
        lab = _expect_fail(name)
        ok = (lab == exp)
        seen[name] = (lab, exp, ok)
        if not ok:
            all_ok = False
        print("  %-24s first_fail=%-6s expected=%-6s %s" % (name, lab, exp, "OK" if ok else "MISMATCH"))
    distinct = len(set(l for l, _, _ in seen.values() if l and not l.startswith("ERR")))
    print("DISTINCT_CONDS =", distinct)
    print("ALL_FAIL =", all_ok)
    if not all_ok or distinct < 2:
        print("NEG_SELFTEST_FAIL")
        sys.exit(1)
    print("NEG_SELFTEST_PASS")


if __name__ == "__main__":
    main()
'''


def write_selftest():
    with open(os.path.join(REF, "negative_selftest.py"), "w") as f:
        f.write(NEG_SELFTEST)
    print("negative_selftest.py written")


def build_ref_zip():
    zpath = os.path.join(REF, "reference_submit.zip")
    if os.path.exists(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(GOLD, "dc_policy_remove_migrate.py")
    print("reference_submit.zip written")


def selfverify():
    # 1. ref PASS via check.py (build ref zip, run check)
    build_ref_zip()
    zpath = os.path.join(REF, "reference_submit.zip")
    print("=== ref check ===")
    r = subprocess.run([sys.executable, os.path.join(REF, "check.py"), zpath],
                       capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        print("REF FAIL stderr:", r.stderr)
        sys.exit(1)
    # 2. negative_selftest
    print("=== negative_selftest ===")
    r = subprocess.run([sys.executable, os.path.join(REF, "negative_selftest.py")],
                       capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        print("NEG SELFTEST FAIL stderr:", r.stderr)
        sys.exit(1)
    # 3. §4.9 three fakes (empty / print_expected / core_deleted) via check.py
    print("=== 4.9 three-fake ===")
    for name in ["naive_empty", "naive_print_expected", "naive_core_deleted"]:
        tmp = tempfile.mkdtemp()
        z = os.path.join(tmp, "submit.zip")
        with zipfile.ZipFile(z, "w") as zf:
            zf.write(os.path.join(REF, "negative", name + ".py"), "dc_policy_remove_migrate.py")
        r = subprocess.run([sys.executable, os.path.join(REF, "check.py"), z],
                           capture_output=True, text=True)
        print("  %-24s rc=%d %s" % (name, r.returncode, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""))
        if r.returncode == 0:
            print("  !! %s unexpectedly PASSED" % name); sys.exit(1)
    print("SELFVERIFY_ALL_GREEN")


def append_jsonl():
    jsonl = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_A.jsonl"
    # read check.py for the test field
    with open(os.path.join(REF, "check.py")) as f:
        check_src = f.read()
    entry = {
        "task_id": CASE_ID,
        "mode": "design_flow",
        "entry_point": "outputs/submit.zip",
        "test": check_src,
        "prompt": open(os.path.join(ASSETS, "prompt.txt")).read(),
        "attachments": [
            {"name": "prompt.txt", "source": "assets/%s/prompt.txt" % CASE},
            {"name": "task_brief.md", "source": "assets/%s/task_brief.md" % CASE},
            {"name": "copy_synth.tcl", "source": "assets/%s/copy_synth.tcl" % CASE},
            {"name": "copy_run_dc.sh", "source": "assets/%s/copy_run_dc.sh" % CASE},
            {"name": "copy_sdc.sdc", "source": "assets/%s/copy_sdc.sdc" % CASE},
            {"name": "lib_metadata.json", "source": "assets/%s/lib_metadata.json" % CASE},
            {"name": "hidden/hidden_manifest.json", "source": "assets/%s/hidden/hidden_manifest.json" % CASE},
        ],
        "metadata": {
            "trace_source": {
                "user": "johnl",
                "host": "hfeg0pkn001",
                "session_file": "1793933023338_1uxza.messages.json",
                "match_count": 302,
                "real_task_summary": "DC synthesis script migration: adapt migrated 'copy' run_dc.sh/synth.tcl/sdc (from /home/EDA env) to a self-contained local RowRed project using 3 new libraries (GS/rowred-custom/LVS), and per user clarification remove the cell allow/forbid policy entirely so all cells are usable.",
            },
            "domain": "digital",
            "level": "L2-static",
            "track": "A",
            "test_rationale": (
                "15 条断言："
                "① zip 含 dc_policy_remove_migrate.py 且无 os.system/shell=True/eval/exec 等禁调 "
                "② dc_policy_remove_migrate.py 可 py_compile 通过 "
                "③ [隐藏 B] 候选 --project B --out 退出码 0 且生成 synth.tcl/run_dc.sh/timing_constraints.tcl 三件套 "
                "④ [隐藏 B] synth.tcl 对 3 个 B .db 库各 read_db $LIB_DB_<tag> 且引用 B 的 db 文件名 "
                "⑤ [隐藏 B] target_library=[list $LIB_DB_GS $LIB_DB_CUSTOM $LIB_DB_LVS]（.db 路径非逻辑名） "
                "⑥ [隐藏 B] policy 已删除：synth.tcl 无 set CUSTOM_CELLS 白名单 "
                "⑦ [隐藏 B] policy 已删除：synth.tcl 无 set ORDINARY_CELL_PATTERN "
                "⑧ [隐藏 B] policy 已删除：无 set_dont_use $libcell 禁用标记（remove_attribute 清除则允许） "
                "⑨ [隐藏 B] policy 已删除：无 sizeof_collection!=NNN / Expected NNN cells / allowed!=NNN 硬编计数断言 "
                "⑩ [隐藏 B] synth.tcl 含 remove_attribute $libcell dont_use 与 dont_touch（清除继承标记） "
                "⑪ [隐藏 B] check_mapping 仅用 is_unmapped 守卫，不引用 ORDINARY_CELL_PATTERN/CUSTOM_CELLS "
                "⑫ [隐藏 B] synth.tcl 与 run_dc.sh 无 /home/EDA 或 /home/<user>/.cline 绝对路径（自包含） "
                "⑬ [隐藏 B] run_dc.sh 无 eda-guard/GUARD、dc_shell 取自 PATH（非 /home/EDA/synopsys 绝对路径） "
                "⑭ [隐藏 B] 反硬编：synth.tcl 不含 A 的 top R_RowRed1024_full 及 A 的 SS_0p98 库文件名，且含 B 的 top "
                "⑮ [隐藏 B] run_dc.sh 含 test -r ...rtl 存在性检查与 tee dc.log，且引用 B 的 rtl 目录/文件名"
            ),
        },
    }
    # append only if not present
    exist = False
    if os.path.exists(jsonl):
        with open(jsonl) as f:
            for line in f:
                if CASE_ID in line:
                    exist = True; break
    if exist:
        print("case already in jsonl, skipping append")
        return
    with open(jsonl, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    # count
    n = sum(1 for _ in open(jsonl))
    print("jsonl appended; A jsonl now %d lines" % n)


if __name__ == "__main__":
    write_assets()
    write_check()
    write_negatives()
    write_selftest()
    selfverify()
    append_jsonl()
    print("BUILD_DONE")
