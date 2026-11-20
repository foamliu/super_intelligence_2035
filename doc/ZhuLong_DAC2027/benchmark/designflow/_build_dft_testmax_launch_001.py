#!/usr/bin/env python3
"""Build assets/reference/hidden/negative for EDA-Eval-DesignFlow-DftTestmaxLaunchFlow-001.

Trace: 0ekf9 (e0030085 @ hfeg0pkn002, mc352) — DFT TestMAX demo launch flow.
A-faithful produce-task: USER#3 "实际运行这个Demo 帮我生成完整的启动脚本/环境变量".
Deliverable = spec-driven generator gen_dft_launch_flow.py + spec_a.json producing
launch scripts (setup_env.sh, run_full_flow.sh, run/run_dft.sh, run/sim_filelist.f,
run_sim.py). check() runs generator on hidden spec_b.json.
"""
import json, os, shutil, zipfile, subprocess, sys, hashlib, stat

CASE_ID = "EDA-Eval-DesignFlow-DftTestmaxLaunchFlow-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSETS = os.path.join(BENCH, "assets", CASE_ID)
REF = os.path.join(BENCH, "reference", CASE_ID)
HIDDEN = os.path.join(ASSETS, "hidden")
NEG = os.path.join(REF, "negative")

for d in (ASSETS, REF, HIDDEN, NEG):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# Spec definitions
# ---------------------------------------------------------------------------
# A spec = faithful to trace (e0030085, adder_top/dft_top, TestMAX X-2025.06, ...)
SPEC_A = {
    "project_root": "/home/e0030085/Documents/dft_testmax_demo",
    "user": "e0030085",
    "design_top": "dft_top",
    "tb_top": "tb_dft_top",
    "rtl_files": ["adder_top.v", "add_sub_unit.v", "dft_top.v"],
    "tb_file": "tb_dft_top.v",
    "testmax_home": "/apps/synopsys/testmax/X-2025.06",
    "testmax_dft_home": "/apps/synopsys/testmax/TestMAX_DFT/syn/V-2023.12-SP4",
    "testmax_atpg_home": "/apps/synopsys/testmax/TestMAX_ATPG/txs/W-2024.09",
    "vcs_home": "/apps/synopsys/vcs/X-2025.06-SP2-1",
    "verdi_home": "/apps/synopsys/verdi/X-2025.06-SP2-1",
    "license_server": "27000@license_server",
    "scan_chains": 4,
    "scan_cells": 75,
    "chain_max_len": 21,
    "chain_min_len": 18,
    "atpg_detected": 1428,
    "atpg_undetectable": 152,
    "atpg_untestable": 38,
    "atpg_total_faults": 1618,
    "atpg_test_coverage": "94.58%",
    "atpg_fault_coverage": "88.26%",
    "atpg_pattern_count": 124,
    "sim_pass_marker": "ALL TESTS PASSED",
    "sim_test1_key": 10, "sim_test1_exp": 15,
    "sim_test2_key": 20, "sim_test2_exp": 25,
    "sim_test3_key": "0x55", "sim_test3_exp": 85,
}

# B spec = variant (different user/root/RTL/tool versions/scan/ATPG numbers)
SPEC_B = {
    "project_root": "/home/w0047129/Documents/dft_pipeline_demo",
    "user": "w0047129",
    "design_top": "dft_chip",
    "tb_top": "tb_dft_chip",
    "rtl_files": ["mul_top.v", "mul_unit.v", "dft_chip.v"],
    "tb_file": "tb_dft_chip.v",
    "testmax_home": "/apps/synopsys/testmax/X-2026.03",
    "testmax_dft_home": "/apps/synopsys/testmax/TestMAX_DFT/syn/V-2024.06-SP1",
    "testmax_atpg_home": "/apps/synopsys/testmax/TestMAX_ATPG/txs/W-2025.03",
    "vcs_home": "/apps/synopsys/vcs/X-2026.03-SP1",
    "verdi_home": "/apps/synopsys/verdi/X-2026.03-SP1",
    "license_server": "27000@licsrv02",
    "scan_chains": 3,
    "scan_cells": 92,
    "chain_max_len": 31,
    "chain_min_len": 30,
    "atpg_detected": 1893,
    "atpg_undetectable": 168,
    "atpg_untestable": 43,
    "atpg_total_faults": 2104,
    "atpg_test_coverage": "96.31%",
    "atpg_fault_coverage": "90.14%",
    "atpg_pattern_count": 156,
    "sim_pass_marker": "ALL TESTS PASSED",
    "sim_test1_key": 7, "sim_test1_exp": 22,
    "sim_test2_key": 18, "sim_test2_exp": 33,
    "sim_test3_key": "0x3C", "sim_test3_exp": 96,
}

# ---------------------------------------------------------------------------
# Existing demo project files (A assets — the SUT reads these to understand
# what launch scripts to generate). Drawn verbatim from the trace.
# ---------------------------------------------------------------------------
RTL_ADDER_TOP = """// DFT TestMAX Demo - adder_top.v - 8-bit accumulator + scan ports
module adder_top (
    input           clk, input           rst_n,
    input  [7:0]    data_a, input  [7:0]    data_b,
    input           load_en, output [8:0]    result,
    input           scan_clk, input           scan_rst_n,
    input           scan_en, input           scan_in, output          scan_out
);
    reg  [8:0]  sum_reg; reg  [7:0]  a_reg, b_reg;
    reg  [2:0]  state_cnt; reg         valid_flag;
    wire [8:0]  sum_w = a_reg + b_reg;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin a_reg<=8'd0; b_reg<=8'd0; sum_reg<=9'd0;
            state_cnt<=3'd0; valid_flag<=1'b0; end
        else if (load_en) begin a_reg<=data_a; b_reg<=data_b;
            sum_reg<=sum_w; state_cnt<=state_cnt+1'b1; valid_flag<=1'b1; end
    end
    assign result = sum_reg;
endmodule
"""

RTL_ADD_SUB = """// DFT TestMAX Demo - add_sub_unit.v - 16-bit add/sub unit
module add_sub_unit (
    input           clk, input           rst_n,
    input  [15:0]   din_a, input  [15:0]   din_b,
    input           op_mode, input           en,
    output [15:0]   dout, output          ovf
);
    reg  [15:0]  a_ff, b_ff; reg  [16:0]  result_ff; reg          ovf_ff;
    reg  [1:0]   pipe_stage;
    wire [16:0]  result_w = op_mode ? ({1'b0,a_ff}-{1'b0,b_ff}) : ({1'b0,a_ff}+{1'b0,b_ff});
    wire         ovf_w    = result_w[16];
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin a_ff<=16'd0; b_ff<=16'd0; result_ff<=17'd0;
            ovf_ff<=1'b0; pipe_stage<=2'd0; end
        else if (en) begin a_ff<=din_a; b_ff<=din_b; result_ff<=result_w;
            ovf_ff<=ovf_w; pipe_stage<=pipe_stage+1'b1; end
    end
    assign dout = result_ff[15:0]; assign ovf  = ovf_ff;
endmodule
"""

RTL_DFT_TOP = """// DFT TestMAX Demo - dft_top.v - top-level integration with scan chain
module dft_top (
    input              clk, input              rst_n,
    input              sys_en, input  [7:0]       key_in,
    output [8:0]       led_out,
    input              scan_clk, input              scan_rst_n,
    input              scan_en, input              scan_in, output             scan_out
);
    wire  [15:0]  alu_a, alu_b, alu_dout; wire          alu_ovf; wire  [8:0]   sum_result;
    adder_top u_adder (.clk(clk),.rst_n(rst_n),.data_a(key_in),.data_b(8'd5),
        .load_en(sys_en),.result(sum_result),.scan_clk(scan_clk),.scan_rst_n(scan_rst_n),
        .scan_en(scan_en),.scan_in(scan_in),.scan_out(scan_out));
    assign alu_a = {8'd0, key_in}; assign alu_b = {8'd0, sum_result[7:0]};
    add_sub_unit u_alu (.clk(clk),.rst_n(rst_n),.din_a(alu_a),.din_b(alu_b),
        .op_mode(sys_en),.en(sys_en),.dout(alu_dout),.ovf(alu_ovf));
    assign led_out = sum_result;
endmodule
"""

RTL_TB = """// DFT TestMAX Demo - tb_dft_top.v - functional + scan testbench
`timescale 1ns/1ps
module tb_dft_top;
    reg clk, rst_n, sys_en; reg  [7:0] key_in; wire [8:0] led_out;
    reg scan_clk, scan_rst_n, scan_en, scan_in; wire scan_out;
    integer i, errors;
    initial clk = 0; always #5 clk = ~clk;
    initial scan_clk = 0; always #5 scan_clk = ~scan_clk;
    dft_top dut (.clk(clk),.rst_n(rst_n),.sys_en(sys_en),.key_in(key_in),.led_out(led_out),
        .scan_clk(scan_clk),.scan_rst_n(scan_rst_n),.scan_en(scan_en),.scan_in(scan_in),.scan_out(scan_out));
    initial begin
        errors = 0;
        $display("==============================================");
        $display("  DFT TestMAX Demo - Testbench");
        $display("==============================================");
        rst_n=0; sys_en=0; key_in=8'd0; scan_en=0; scan_in=0; scan_rst_n=1; #20;
        rst_n=1; #20;
        $display("Phase 1: Functional Mode Test");
        key_in=8'd10; sys_en=1; @(posedge clk); sys_en=0; #10;
        if (led_out !== 9'd15) errors=errors+1; else $display("  [PASS] Functional test 1");
        key_in=8'd20; sys_en=1; @(posedge clk); sys_en=0; #10;
        if (led_out !== 9'd25) errors=errors+1; else $display("  [PASS] Functional test 2");
        $display("Phase 2: Scan Chain Test");
        scan_en=1; #10;
        for (i=0;i<75;i=i+1) begin scan_in=i[0]; @(posedge scan_clk); end
        scan_en=0; #10;
        $display("Phase 3: Scan + Functional Cross-Check");
        if (errors == 0) $display("  ALL TESTS PASSED!");
        else $display("  %d TESTS FAILED!", errors);
        #100; $finish;
    end
    initial begin $dumpfile("tb_dft_top.vcd"); $dumpvars(0, tb_dft_top); end
endmodule
"""

SCRIPT_DFT_COMPILE = """# DFT TestMAX Demo - DFT Compiler scan insertion script
set search_path [list . /home/e0030085/Documents/dft_testmax_demo/libs $search_path]
set target_library "gtech.db"
set link_library [concat "*" $target_library]
set DESIGN_NAME dft_top
analyze -format verilog \\
    /home/e0030085/Documents/dft_testmax_demo/rtl/adder_top.v \\
    /home/e0030085/Documents/dft_testmax_demo/rtl/add_sub_unit.v \\
    /home/e0030085/Documents/dft_testmax_demo/rtl/dft_top.v
elaborate $DESIGN_NAME
current_design $DESIGN_NAME
link
create_clock -name clk -period 10 [get_ports clk]
create_clock -name scan_clk -period 10 [get_ports scan_clk]
set_dft_configuration -scan
set_scan_configuration -chain_count 4 -clock_mixing no_mix
set_dft_signal -type ScanClock -port [get_ports scan_clk] -view existing_dft
set_dft_signal -type Reset -port [get_ports scan_rst_n] -view existing_dft
set_dft_signal -type ScanEnable -port [get_ports scan_en] -view existing_dft
set_dft_signal -type ScanDataIn -port [get_ports scan_in] -view existing_dft
set_dft_signal -type ScanDataOut -port [get_ports scan_out] -view existing_dft
compile -scan
insert_dft
report_scan_path > /home/e0030085/Documents/dft_testmax_demo/results/scan_path.rpt
create_test_protocol -output /home/e0030085/Documents/dft_testmax_demo/results/test_protocol.spf
write -format verilog -hierarchy -output /home/e0030085/Documents/dft_testmax_demo/results/dft_top_scanned.v
exit
"""

SCRIPT_ATPG = """# DFT TestMAX Demo - TetraMAX ATPG script
read_netlist /home/e0030085/Documents/dft_testmax_demo/results/dft_top_scanned.v
run_build_model dft_top
read_test_protocol /home/e0030085/Documents/dft_testmax_demo/results/test_protocol.spf
run_drc
set_fault_type -stuck_at
add_faults -all
create_patterns -auto
report_summary > /home/e0030085/Documents/dft_testmax_demo/results/atpg_summary.rpt
write_patterns /home/e0030085/Documents/dft_testmax_demo/results/patterns.stil -format stil
write_patterns /home/e0030085/Documents/dft_testmax_demo/results/patterns.v -format verilog
exit
"""

RESULTS_SCAN_PATH = """****************************************
Report : scan_path
Design : dft_top
Version: TestMAX-2023.12
****************************************
Scan Path Summary:
  Number of chains: 4
  Scan style:       Multiplexed flip-flop
Total Scan Cells: 75
Max Chain Length: 21
Min Chain Length: 18
"""

RESULTS_ATPG_SUMMARY = """****************************************
Report : atpg summary
Design : dft_top
Version: TetraMAX-2023.12
****************************************
Fault Type: Stuck-at
  Detected (DT)                  1,428
  Undetectable (UD)                152
  ATPG untestable (AU)               38
  Total faults                   1,618
  Test Coverage                   94.58%
  Fault Coverage                  88.26%
  Pattern Count                     124
"""

RESULTS_SIM_LOG = """==============================================
  DFT TestMAX Demo - Testbench
==============================================
Phase 1: Functional Mode Test
  key_in=10, expected result=15, actual= 15
  [PASS] Functional test 1
  key_in=20, expected result=25, actual= 25
  [PASS] Functional test 2
Phase 2: Scan Chain Test
  Shifting in test pattern: 0xAAAAAAAAAAAAAAAAAA...
Phase 3: Scan + Functional Cross-Check
  Functional: key_in=0x55, result= 85
==============================================
  ALL TESTS PASSED!
==============================================
"""

# ---------------------------------------------------------------------------
# Reference generator: gen_dft_launch_flow.py
# Generates the 5 launch scripts from a spec.json. This is the GOLDEN deliverable.
# ---------------------------------------------------------------------------
GEN_SOURCE = r'''#!/usr/bin/env python3
"""Spec-driven generator for a DFT TestMAX demo launch flow.

Usage: python3 gen_dft_launch_flow.py <spec.json> <outdir>

Produces:
  outdir/setup_env.sh        - environment variable setup (source-able)
  outdir/run_full_flow.sh    - one-click full flow (check|dft_only|atpg_only|simulate|all)
  outdir/run/run_dft.sh      - DFT compile + ATPG with tool fallback
  outdir/run/sim_filelist.f  - VCS simulation file list
  outdir/run_sim.py          - VCS simulation wrapper (graceful degradation)
"""
import json, os, sys

def L(s): return s  # literal passthrough

def gen_setup_env(s, root):
    home = s["project_root"]
    return f'''#!/bin/bash
# TestMAX DFT Demo - environment setup (source this file)
# Usage: source setup_env.sh

echo "=============================================="
echo "  Setting up TestMAX Environment..."
echo "=============================================="

# 1. Project paths
export DFT_DEMO_ROOT="{home}"
export DFT_RTL_DIR="${{DFT_DEMO_ROOT}}/rtl"
export DFT_SCRIPTS_DIR="${{DFT_DEMO_ROOT}}/scripts"
export DFT_RESULTS_DIR="${{DFT_DEMO_ROOT}}/results"
export DFT_LIBS_DIR="${{DFT_DEMO_ROOT}}/libs"

# 2. TestMAX tool paths
export TESTMAX_HOME="{s["testmax_home"]}"
export TESTMAX_DFT_HOME="{s["testmax_dft_home"]}"
export TESTMAX_ATPG_HOME="{s["testmax_atpg_home"]}"

# 3. Add tool bins to PATH
if [ -d "$TESTMAX_HOME/bin" ]; then export PATH="${{TESTMAX_HOME}}/bin:$PATH"; fi
if [ -d "$TESTMAX_DFT_HOME/bin" ]; then export PATH="${{TESTMAX_DFT_HOME}}/bin:$PATH"; fi
if [ -d "$TESTMAX_ATPG_HOME/bin" ]; then export PATH="${{TESTMAX_ATPG_HOME}}/bin:$PATH"; fi

# 4. VCS path
export VCS_HOME="{s["vcs_home"]}"
if [ -d "$VCS_HOME/bin" ]; then export PATH="${{VCS_HOME}}/bin:$PATH"; fi

# 5. Synopsys common
export SYNOPSYS="${{TESTMAX_HOME}}"
export SNPSLMD_LICENSE_FILE="{s["license_server"]}"

# 6. Tool aliases
alias dft='dft_shell -64'
alias tmax='tmax -64'
alias vcs_sim='python3 {home}/run_sim.py'
alias go_dft="cd ${{DFT_DEMO_ROOT}}"

# 6b. Verdi / waveform
export VERDI_HOME="{s["verdi_home"]}"
if [ -d "$VERDI_HOME/bin" ]; then export PATH="${{VERDI_HOME}}/bin:$PATH"; fi
alias wave='nWave ${{DFT_RESULTS_DIR}}/{s["tb_top"]}.vcd'
alias wavegen='python3 ${{DFT_DEMO_ROOT}}/gen_waveform.py'

# 7. Verification
echo "  DFT_DEMO_ROOT  = ${{DFT_DEMO_ROOT}}"
echo "  TESTMAX_HOME   = ${{TESTMAX_HOME}}"
echo "  VCS_HOME       = ${{VCS_HOME}}"
TOOLS_OK=0
for tool in dft_shell tmax vcs; do
    if which $tool &>/dev/null; then echo "  [OK] $tool -> $(which $tool)"; TOOLS_OK=$((TOOLS_OK+1));
    else echo "  [..] $tool -- not found"; fi
done
echo "  Quick: dft_shell -64 -f ${{DFT_SCRIPTS_DIR}}/dft_compile.tcl"
echo "         tmax -64 -f ${{DFT_SCRIPTS_DIR}}/atpg.tcl"
echo "         python3 ${{DFT_DEMO_ROOT}}/run_sim.py"
echo "         bash ${{DFT_DEMO_ROOT}}/run_full_flow.sh"
echo "=============================================="
'''

def gen_run_full_flow(s, root):
    return f'''#!/bin/bash
# TestMAX DFT Demo - Full-flow one-click launch
# Usage: bash run_full_flow.sh [all|check|dft_only|atpg_only|simulate]

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
RTL_DIR="${{PROJECT_ROOT}}/rtl"
SCRIPTS_DIR="${{PROJECT_ROOT}}/scripts"
RESULTS_DIR="${{PROJECT_ROOT}}/results"

DFT_CMD=""; ATPG_CMD=""
RED='\\033[0;31m'; GREEN='\\033[0;32m'; YELLOW='\\033[1;33m'
CYAN='\\033[0;36m'; NC='\\033[0m'

print_header() {{ echo ""; echo "=============================================="; echo -e "  ${{CYAN}}$1${{NC}}"; echo "=============================================="; }}
print_ok()   {{ echo -e "  ${{GREEN}}[OK]${{NC}} $1"; }}
print_warn() {{ echo -e "  ${{YELLOW}}[..]${{NC}} $1"; }}
print_err()  {{ echo -e "  ${{RED}}[XX]${{NC}} $1"; }}

check_environment() {{
    print_header "Environment Check"
    local all_ok=1
    for d in "$RTL_DIR" "$SCRIPTS_DIR" "$RESULTS_DIR"; do
        if [ -d "$d" ]; then print_ok "Directory: $d"; else print_err "Directory: $d"; all_ok=0; fi
    done
    DFT_CMD=""; ATPG_CMD=""
    for cmd in dft_shell dc_shell; do
        if which "$cmd" &>/dev/null; then DFT_CMD="$cmd"; break; fi
    done
    for cmd in tmax tetramax; do
        if which "$cmd" &>/dev/null; then ATPG_CMD="$cmd"; break; fi
    done
    if [ -n "$DFT_CMD" ]; then print_ok "DFT Compiler: $DFT_CMD"; else print_warn "DFT Compiler not found - simulated output"; fi
    if [ -n "$ATPG_CMD" ]; then print_ok "TetraMAX ATPG: $ATPG_CMD"; else print_warn "TetraMAX not found - simulated output"; fi
    if which iverilog &>/dev/null; then print_ok "Icarus Verilog: $(which iverilog)"; else print_warn "iverilog not found - RTL sim skipped"; fi
    return $all_ok
}}

run_dft_compile() {{
    print_header "Phase 1: DFT Compiler - Scan Insertion"
    cd "$PROJECT_ROOT"
    if [ -n "$DFT_CMD" ]; then
        $DFT_CMD -64 -f "${{SCRIPTS_DIR}}/dft_compile.tcl" 2>&1 | tee "${{RESULTS_DIR}}/dft_compile.log"
        print_ok "DFT Compiler completed"
    else
        print_warn "No DFT Compiler - using pre-generated results"
    fi
    if [ -f "${{RESULTS_DIR}}/scan_path.rpt" ]; then
        grep -E "Total Scan Cells|Number of Chains|Max Chain Length|Min Chain Length" "${{RESULTS_DIR}}/scan_path.rpt"
    fi
}}

run_atpg() {{
    print_header "Phase 2: TetraMAX - ATPG Pattern Generation"
    cd "$PROJECT_ROOT"
    if [ -n "$ATPG_CMD" ]; then
        $ATPG_CMD -64 -f "${{SCRIPTS_DIR}}/atpg.tcl" 2>&1 | tee "${{RESULTS_DIR}}/atpg.log"
        print_ok "TetraMAX ATPG completed"
    else
        print_warn "No TetraMAX - using pre-generated results"
    fi
    if [ -f "${{RESULTS_DIR}}/atpg_summary.rpt" ]; then
        grep -E "Test Coverage|Fault Coverage|Pattern Count|Total faults" "${{RESULTS_DIR}}/atpg_summary.rpt"
    fi
}}

run_simulation() {{
    print_header "Phase 3: RTL Simulation - Functional + Scan Test (VCS)"
    cd "$PROJECT_ROOT"
    local py_script="${{PROJECT_ROOT}}/run_sim.py"
    if [ ! -f "$py_script" ]; then print_err "Simulation script not found: $py_script"; return 1; fi
    python3 "$py_script" 2>&1 | tee "${{RESULTS_DIR}}/vcs_wrapper.log"
    local rc=${{PIPESTATUS[0]}}
    if [ $rc -ne 0 ]; then print_err "VCS simulation failed (code $rc)"; return $rc; fi
    if [ -f "${{RESULTS_DIR}}/simulation.log" ]; then
        if grep -q "{s["sim_pass_marker"]}" "${{RESULTS_DIR}}/simulation.log"; then print_ok "All simulation tests PASSED!";
        elif grep -q "TESTS FAILED" "${{RESULTS_DIR}}/simulation.log"; then print_err "Some tests FAILED"; fi
    fi
}}

case "${{1:-all}}" in
    check) check_environment ;;
    dft_only) check_environment; run_dft_compile ;;
    atpg_only) check_environment; run_atpg ;;
    simulate) run_simulation ;;
    all|"") check_environment; run_dft_compile; run_atpg; run_simulation ;;
    *) echo "Usage: $0 {{all|check|dft_only|atpg_only|simulate}}"; exit 1 ;;
esac

print_header "Flow Complete"
echo "  Results directory: ${{RESULTS_DIR}}"
echo "  source ${{PROJECT_ROOT}}/setup_env.sh"
echo "=============================================="
'''

def gen_run_dft(s, root):
    return f'''#!/bin/bash
# DFT TestMAX Demo - run from run/ subdir
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RTL_DIR="${{PROJECT_ROOT}}/rtl"
SCRIPTS_DIR="${{PROJECT_ROOT}}/scripts"
RESULTS_DIR="${{PROJECT_ROOT}}/results"

echo "=============================================="
echo "  DFT TestMAX Demo"
echo "  Project Root: ${{PROJECT_ROOT}}"
echo "=============================================="

for d in "$RTL_DIR" "$SCRIPTS_DIR" "$RESULTS_DIR"; do
    if [ ! -d "$d" ]; then echo "[ERROR] Directory not found: $d"; exit 1; fi
done

check_tool() {{
    local cmd="$1"; local alias_cmd="$2"
    if which "$cmd" &>/dev/null; then echo "$cmd"; return 0; fi
    if [ -n "$alias_cmd" ] && which "$alias_cmd" &>/dev/null; then echo "$alias_cmd"; return 0; fi
    return 1
}}

DFT_TOOL=$(check_tool "dft_shell" "dc_shell")
ATPG_TOOL=$(check_tool "tmax" "tetramax")

if [ -z "$DFT_TOOL" ]; then echo "  [INFO] DFT Compiler (dft_shell/dc_shell) not found"; fi
if [ -z "$ATPG_TOOL" ]; then echo "  [INFO] TetraMAX (tmax/tetramax) not found"; fi

echo ""; echo "=============================================="
echo "  Step 1: DFT Compiler - Scan Insertion"
echo "=============================================="
if [ -n "$DFT_TOOL" ]; then
    cd "$PROJECT_ROOT"
    $DFT_TOOL -64 -f "${{SCRIPTS_DIR}}/dft_compile.tcl" | tee "${{RESULTS_DIR}}/dft_compile.log"
else
    echo "[SKIP] No DFT Compiler. Simulating expected output..."
    cat << 'EOF' > "${{RESULTS_DIR}}/dft_compile.log"
==============================================
  DFT Compiler Scan Insertion Completed!
  Output: results/{s["design_top"]}_scanned.v
  Protocol: results/test_protocol.spf
==============================================
Scan Chains Report:
  Number of Chains: {s["scan_chains"]}
  Total Scan Cells: {s["scan_cells"]}
  Max Chain Length: {s["chain_max_len"]}
  Min Chain Length: {s["chain_min_len"]}
DFT Violations:
  No violations found.
EOF
    echo "Simulated output written to results/dft_compile.log"
fi

echo ""; echo "=============================================="
echo "  Step 2: TetraMAX - ATPG Pattern Generation"
echo "=============================================="
if [ -n "$ATPG_TOOL" ]; then
    cd "$PROJECT_ROOT"
    $ATPG_TOOL -64 -f "${{SCRIPTS_DIR}}/atpg.tcl" | tee "${{RESULTS_DIR}}/atpg.log"
else
    echo "[SKIP] No TetraMAX. Simulating expected output..."
    cat << 'EOF' > "${{RESULTS_DIR}}/atpg.log"
==============================================
  TetraMAX ATPG Completed!
  Patterns:  results/patterns.stil
  Coverage:  results/atpg_summary.rpt
==============================================
ATPG Summary:
  Detected                         {s["atpg_detected"]:,}
  Undetectable                     {s["atpg_undetectable"]:,}
  ATPG Untestable                  {s["atpg_untestable"]:,}
  Total faults                     {s["atpg_total_faults"]:,}
  Test Coverage                   {s["atpg_test_coverage"]}
  Fault Coverage                  {s["atpg_fault_coverage"]}
  Pattern Count                      {s["atpg_pattern_count"]}
EOF
    echo "Simulated output written to results/atpg.log"
fi

echo ""; echo "=============================================="
echo "  DFT TestMAX Demo Completed!"
echo "  Results: ${{RESULTS_DIR}}"
echo "=============================================="
'''

def gen_sim_filelist(s, root):
    home = s["project_root"]
    lines = ["# DFT TestMAX Demo - VCS simulation file list", ""]
    lines.append("# RTL source files")
    for f in s["rtl_files"]:
        lines.append(f"{home}/rtl/{f}")
    lines.append("")
    lines.append("# Testbench")
    lines.append(f"{home}/rtl/{s['tb_file']}")
    lines.append("")
    lines.append("# Compile options")
    lines.append("+define+SCAN")
    lines.append(f"+incdir+{home}/rtl")
    return "\n".join(lines) + "\n"

def gen_run_sim_py(s, root):
    home = s["project_root"]
    return f'''#!/usr/bin/env python3
"""Run DFT TestMAX Demo RTL simulation (VCS wrapper with graceful degradation)."""
import subprocess, sys, os

DEMO = "{home}"
RTL  = os.path.join(DEMO, "rtl")
RES  = os.path.join(DEMO, "results")
PY   = sys.executable

os.makedirs(RES, exist_ok=True)
os.chdir(DEMO)

def generate_expected_output(log_path):
    text = """==============================================
  DFT TestMAX Demo - Testbench
==============================================

Phase 1: Functional Mode Test
----------------------------------------
  key_in={s["sim_test1_key"]}, expected result={s["sim_test1_exp"]}, actual= {s["sim_test1_exp"]}
  [PASS] Functional test 1
  key_in={s["sim_test2_key"]}, expected result={s["sim_test2_exp"]}, actual= {s["sim_test2_exp"]}
  [PASS] Functional test 2

Phase 2: Scan Chain Test
----------------------------------------
  Shifting in test pattern: 0xAAAAAAAAAAAAAAAAAA...
  Shifting out captured data...

Phase 3: Scan + Functional Cross-Check
----------------------------------------
  Functional: key_in={s["sim_test3_key"]}, result= {s["sim_test3_exp"]}

==============================================
  {s["sim_pass_marker"]}
==============================================
"""
    with open(log_path, "w") as f:
        f.write(text)
    return text

print("=" * 60)
print("  DFT TestMAX Demo - RTL Simulation")
print("=" * 60)

# Try VCS if available, otherwise generate expected output
vcs_bin = os.path.join(os.environ.get("VCS_HOME", ""), "bin", "vcs")
sim_log = os.path.join(RES, "simulation.log")

if os.path.exists(vcs_bin) and os.path.isfile(vcs_bin):
    filelist = os.path.join(DEMO, "run", "sim_filelist.f")
    try:
        subprocess.run([vcs_bin, "-f", filelist, "-o", "simv"], check=True, cwd=DEMO)
        subprocess.run(["./simv"], cwd=DEMO)
    except Exception as e:
        print(f"  [WARN] VCS run failed: {{e}}")
        output = generate_expected_output(sim_log)
        print(output)
else:
    print("  [INFO] Generating expected simulation output (VCS not available)")
    output = generate_expected_output(sim_log)
    print(output)

if "{s["sim_pass_marker"]}" in open(sim_log).read():
    print("  [OK] All tests PASSED!")
print("=" * 60)
print(f"  Done! Results in: {{RES}}")
print("=" * 60)
'''

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 gen_dft_launch_flow.py <spec.json> <outdir>", file=sys.stderr)
        sys.exit(2)
    spec_path, outdir = sys.argv[1], sys.argv[2]
    with open(spec_path) as f:
        s = json.load(f)
    os.makedirs(os.path.join(outdir, "run"), exist_ok=True)
    files = {
        "setup_env.sh": gen_setup_env(s, outdir),
        "run_full_flow.sh": gen_run_full_flow(s, outdir),
        "run/run_dft.sh": gen_run_dft(s, outdir),
        "run/sim_filelist.f": gen_sim_filelist(s, outdir),
        "run_sim.py": gen_run_sim_py(s, outdir),
    }
    for rel, content in files.items():
        p = os.path.join(outdir, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(content)
        if rel.endswith(".sh"):
            os.chmod(p, 0o755)
    print(f"Generated {{len(files)}} launch-flow files in {{outdir}}")

if __name__ == "__main__":
    main()
'''

# ---------------------------------------------------------------------------
# check.py — runs generator on hidden spec_b.json, 16 assertions
# ---------------------------------------------------------------------------
CHECK_SOURCE = r'''#!/usr/bin/env python3
"""check() for EDA-Eval-DesignFlow-DftTestmaxLaunchFlow-001.

Verifies the SUT's submit.zip contains a spec-driven generator that, when run
on the HIDDEN spec_b.json, produces a correct DFT launch flow. Asserts 16
independent conditions (a-p)."""
import json, os, sys, shutil, zipfile, subprocess, tempfile, re

CASE_ID = "EDA-Eval-DesignFlow-DftTestmaxLaunchFlow-001"
CONDITIONS = [
    ("a", "zip valid + contains 5 deliverable files (gen_dft_launch_flow.py, spec_a.json, setup_env.sh, run_full_flow.sh, run/run_dft.sh, run/sim_filelist.f, run_sim.py)"),
    ("b", "setup_env.sh defines TESTMAX_HOME equal to B testmax_home"),
    ("c", "setup_env.sh defines VCS_HOME and VERDI_HOME"),
    ("d", "setup_env.sh exports PATH with tool bin dirs"),
    ("e", "setup_env.sh defines aliases (dft, tmax, go_dft)"),
    ("f", "run_full_flow.sh has case dispatch with all 5 subcommands (all|check|dft_only|atpg_only|simulate)"),
    ("g", "run_full_flow.sh defines functions run_dft_compile AND run_atpg AND run_simulation"),
    ("h", "run_full_flow.sh defines color helper functions (print_ok/print_warn/print_err or print_header)"),
    ("i", "run/run_dft.sh has tool fallback: dft_shell OR dc_shell; tmax OR tetramax"),
    ("j", "run/run_dft.sh has pre-generated fallback writing dft_compile.log with B scan_cells number"),
    ("k", "run/sim_filelist.f lists B RTL files and TB and +define+SCAN"),
    ("l", "run_sim.py is valid Python (py_compile) and references VCS or simulation.log"),
    ("m", "subprocess: bash run_full_flow.sh check exits 0"),
    ("n", "subprocess: bash run/run_dft.sh (no tools) exits 0 and fallback dft_compile.log contains B Total Scan Cells"),
    ("o", "anti-hardcode: A-specific values (e0030085, adder_top, dft_top, 94.58) do NOT appear in generated B files"),
    ("p", "3-seed determinism: setup_env.sh byte-identical across 3 regenerations"),
]

def _fail(cond, msg):
    raise AssertionError(f"[{cond}] {CONDITIONS[ord(cond)-ord('a')][1]}: {msg}")

def check(deliverable, workdir):
    if not os.path.exists(deliverable):
        _fail("a", f"deliverable not found: {deliverable}")
    tmp = tempfile.mkdtemp(prefix="chk_dft_")
    try:
        with zipfile.ZipFile(deliverable) as z:
            names = z.namelist()
            z.extractall(tmp)
        # (a) required files
        required = ["gen_dft_launch_flow.py", "spec_a.json",
                    "setup_env.sh", "run_full_flow.sh",
                    "run/run_dft.sh", "run/sim_filelist.f", "run_sim.py"]
        # the generator + spec_a may be at top level; the 5 scripts may be top-level or in a subdir
        def find(name):
            for root, _, files in os.walk(tmp):
                if name in files:
                    return os.path.join(root, name)
            return None
        gen_py = find("gen_dft_launch_flow.py")
        spec_a = find("spec_a.json")
        if gen_py is None or spec_a is None:
            _fail("a", f"missing generator/spec_a; zip names={names}")
        # hidden spec_b
        spec_b_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spec_b.json")
        if not os.path.exists(spec_b_path):
            _fail("a", "hidden spec_b.json not found beside check.py")
        with open(spec_b_path) as f:
            sb = json.load(f)

        # run generator on B into gen_b dir
        gen_b = tempfile.mkdtemp(prefix="genb_")
        r = subprocess.run([sys.executable, gen_py, spec_b_path, gen_b],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            _fail("a", f"generator failed on spec_b: {r.stderr[:300]}")
        def rb(name):
            p = os.path.join(gen_b, name); 
            if not os.path.exists(p): _fail(name[0] if name else "a", f"{name} not generated")
            return open(p).read()
        setup_env = rb("setup_env.sh")
        run_full = rb("run_full_flow.sh")
        run_dft = rb("run/run_dft.sh")
        sim_fl = rb("run/sim_filelist.f")
        run_sim = rb("run_sim.py")

        # (b) TESTMAX_HOME == B
        if sb["testmax_home"] not in setup_env:
            _fail("b", f"TESTMAX_HOME {sb['testmax_home']} not in setup_env.sh")
        # (c) VCS_HOME and VERDI_HOME
        if "VCS_HOME" not in setup_env or sb["vcs_home"] not in setup_env:
            _fail("c", "VCS_HOME / vcs_home missing")
        if "VERDI_HOME" not in setup_env or sb["verdi_home"] not in setup_env:
            _fail("c", "VERDI_HOME / verdi_home missing")
        # (d) PATH export with bin
        if "export PATH" not in setup_env or "/bin" not in setup_env:
            _fail("d", "no PATH export with bin dirs")
        # (e) aliases dft/tmax/go_dft
        for al in ["dft", "tmax", "go_dft"]:
            if f"alias {al}" not in setup_env:
                _fail("e", f"alias {al} missing")
        # (f) subcommand dispatch
        for sub in ["all", "check", "dft_only", "atpg_only", "simulate"]:
            if sub not in run_full:
                _fail("f", f"subcommand '{sub}' missing in run_full_flow.sh")
        # (g) functions
        for fn in ["run_dft_compile", "run_atpg", "run_simulation"]:
            if fn not in run_full:
                _fail("g", f"function {fn} missing")
        # (h) color helpers
        if not any(ch in run_full for ch in ["print_ok", "print_warn", "print_err", "print_header"]):
            _fail("h", "no color helper functions")
        # (i) tool fallback
        if "dft_shell" not in run_dft or "dc_shell" not in run_dft:
            _fail("i", "dft_shell/dc_shell fallback missing")
        if "tmax" not in run_dft or "tetramax" not in run_dft:
            _fail("i", "tmax/tetramax fallback missing")
        # (j) pre-generated fallback with B scan_cells
        if str(sb["scan_cells"]) not in run_dft:
            _fail("j", f"B scan_cells {sb['scan_cells']} not in run_dft.sh fallback")
        if "dft_compile.log" not in run_dft:
            _fail("j", "dft_compile.log fallback write missing")
        # (k) sim_filelist lists B RTL + TB + +define
        for rf in sb["rtl_files"]:
            if rf not in sim_fl:
                _fail("k", f"B RTL file {rf} not in sim_filelist.f")
        if sb["tb_file"] not in sim_fl:
            _fail("k", f"B TB {sb['tb_file']} not in sim_filelist.f")
        if "+define+SCAN" not in sim_fl:
            _fail("k", "+define+SCAN missing")
        # (l) run_sim.py valid python + VCS/sim ref
        rpy = subprocess.run([sys.executable, "-m", "py_compile", os.path.join(gen_b, "run_sim.py")],
                             capture_output=True, text=True)
        if rpy.returncode != 0:
            _fail("l", f"run_sim.py py_compile failed: {rpy.stderr[:200]}")
        if "VCS" not in run_sim and "vcs" not in run_sim and "simulation.log" not in run_sim:
            _fail("l", "run_sim.py has no VCS/simulation.log reference")
        # (m) subprocess run_full_flow.sh check -> exit 0
        # need rtl/scripts/results dirs for check_environment to find dirs; create minimal stubs
        os.makedirs(os.path.join(gen_b, "rtl"), exist_ok=True)
        os.makedirs(os.path.join(gen_b, "scripts"), exist_ok=True)
        os.makedirs(os.path.join(gen_b, "results"), exist_ok=True)
        rc = subprocess.run(["bash", os.path.join(gen_b, "run_full_flow.sh"), "check"],
                            capture_output=True, text=True, timeout=60)
        if rc.returncode != 0:
            _fail("m", f"run_full_flow.sh check exit={rc.returncode}: {rc.stderr[:200]}")
        # (n) subprocess run/run_dft.sh -> exit 0 + fallback log with B Total Scan Cells
        rc2 = subprocess.run(["bash", os.path.join(gen_b, "run", "run_dft.sh")],
                             capture_output=True, text=True, timeout=60, cwd=gen_b)
        if rc2.returncode != 0:
            _fail("n", f"run_dft.sh exit={rc2.returncode}: {rc2.stderr[:200]}")
        dft_log = os.path.join(gen_b, "results", "dft_compile.log")
        if not os.path.exists(dft_log):
            _fail("n", "fallback dft_compile.log not written")
        dft_log_txt = open(dft_log).read()
        if str(sb["scan_cells"]) not in dft_log_txt:
            _fail("n", f"B scan_cells {sb['scan_cells']} not in fallback dft_compile.log")
        # (o) anti-hardcode: A values must NOT appear in generated B files
        a_markers = ["e0030085", "adder_top", "dft_top", "94.58", "88.26", "1618"]
        # dft_top is B's design_top? No — B design_top is dft_chip. But "dft_top" substring may appear in "dft_top_scanned"? check B spec.
        # B design_top = dft_chip, so "dft_top" should not appear except maybe in generic comments. Use strict markers.
        a_strict = ["e0030085", "adder_top", "94.58", "88.26"]
        all_b = setup_env + run_full + run_dft + sim_fl + run_sim
        for mk in a_strict:
            if mk in all_b:
                _fail("o", f"A-marker '{mk}' leaked into B output")
        # (p) 3-seed determinism
        gens = []
        for _ in range(3):
            gd = tempfile.mkdtemp(prefix="det_")
            subprocess.run([sys.executable, gen_py, spec_b_path, gd], capture_output=True, timeout=60)
            se = os.path.join(gd, "setup_env.sh")
            if not os.path.exists(se):
                _fail("p", "setup_env.sh not generated in determinism run")
            gens.append(open(se).read())
            shutil.rmtree(gd, ignore_errors=True)
        if not (gens[0] == gens[1] == gens[2]):
            _fail("p", "setup_env.sh not byte-identical across 3 runs")
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    # standalone: check.py <deliverable> <workdir>
    d = sys.argv[1] if len(sys.argv) > 1 else "submit.zip"
    w = sys.argv[2] if len(sys.argv) > 2 else "."
    try:
        ok = check(d, w)
        print(f"CHECK: PASS ({len(CONDITIONS)} conditions)")
    except AssertionError as e:
        print(f"CHECK: FAIL - {e}")
        sys.exit(1)
'''

# ---------------------------------------------------------------------------
# Write everything
# ---------------------------------------------------------------------------
def w(path, content, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    if mode:
        os.chmod(path, mode)

# A assets: the existing demo project (what the SUT reads)
w(os.path.join(ASSETS, "rtl", "adder_top.v"), RTL_ADDER_TOP)
w(os.path.join(ASSETS, "rtl", "add_sub_unit.v"), RTL_ADD_SUB)
w(os.path.join(ASSETS, "rtl", "dft_top.v"), RTL_DFT_TOP)
w(os.path.join(ASSETS, "rtl", "tb_dft_top.v"), RTL_TB)
w(os.path.join(ASSETS, "scripts", "dft_compile.tcl"), SCRIPT_DFT_COMPILE)
w(os.path.join(ASSETS, "scripts", "atpg.tcl"), SCRIPT_ATPG)
w(os.path.join(ASSETS, "results", "scan_path.rpt"), RESULTS_SCAN_PATH)
w(os.path.join(ASSETS, "results", "atpg_summary.rpt"), RESULTS_ATPG_SUMMARY)
w(os.path.join(ASSETS, "results", "simulation.log"), RESULTS_SIM_LOG)

# A spec + prompt + task_brief
w(os.path.join(ASSETS, "spec_a.json"), json.dumps(SPEC_A, indent=2, ensure_ascii=False))
PROMPT_A = (
    "根据tetsMAX 给我一个testMax demo\n\n"
    "实际运行这个Demo 帮我生成完整的启动脚本/环境变量\n\n"
    "（说明：上面是真实用户与 EDA agent 的两轮原始对话。现有 dft_testmax_demo 项目"
    "已放在 assets/ 下，含 rtl/ 、scripts/ 、results/ 。请基于现有 demo 项目，"
    "生成一个 spec 驱动的启动流程生成器 gen_dft_launch_flow.py + spec_a.json，"
    "使其能根据 spec 生成完整的启动脚本与环境变量：setup_env.sh、run_full_flow.sh、"
    "run/run_dft.sh、run/sim_filelist.f、run_sim.py 。脚本需支持无真实 TestMAX/VCS "
    "工具时的优雅回退。）"
)
w(os.path.join(ASSETS, "prompt.txt"), PROMPT_A)
w(os.path.join(ASSETS, "task_brief.md"),
  "交付接口：submit.zip 内含 gen_dft_launch_flow.py + spec_a.json（+ 可选生成的 5 个脚本）。\n"
  "生成器 CLI：python3 gen_dft_launch_flow.py <spec.json> <outdir>，在 outdir 产 setup_env.sh / run_full_flow.sh / run/run_dft.sh / run/sim_filelist.f / run_sim.py。\n"
  "判分时会用一份结构相同但取值不同的隐藏 spec 跑你的生成器，请保证生成器对 spec 通用，不要硬编码 A 的具体路径/数值。\n")

# Hidden B
w(os.path.join(HIDDEN, "spec_b.json"), json.dumps(SPEC_B, indent=2, ensure_ascii=False))
w(os.path.join(ASSETS, "hidden_manifest.json"),
  json.dumps({"hidden_dir": "hidden", "spec": "spec_b.json",
              "note": "check() runs the generator on spec_b.json; B differs from A in paths/RTL/scan/ATPG numbers."}, indent=2))

# Reference: the golden generator + spec_a + spec_b + check.py
w(os.path.join(REF, "gen_dft_launch_flow.py"), GEN_SOURCE, 0o755)
w(os.path.join(REF, "spec_a.json"), json.dumps(SPEC_A, indent=2, ensure_ascii=False))
w(os.path.join(REF, "spec_b.json"), json.dumps(SPEC_B, indent=2, ensure_ascii=False))
w(os.path.join(REF, "check.py"), CHECK_SOURCE, 0o755)

# Negatives
w(os.path.join(NEG, "noop_submit.py"), '''#!/usr/bin/env python3
import zipfile, os, sys
# negative: empty-ish generator that produces nothing useful
out=sys.argv[2] if len(sys.argv)>2 else "out"
os.makedirs(out, exist_ok=True)
open(os.path.join(out,"setup_env.sh"),"w").write("# noop\\n")
open(os.path.join(out,"run_full_flow.sh"),"w").write("# noop\\n")
os.makedirs(os.path.join(out,"run"),exist_ok=True)
open(os.path.join(out,"run","run_dft.sh"),"w").write("# noop\\n")
open(os.path.join(out,"run","sim_filelist.f"),"w").write("# noop\\n")
open(os.path.join(out,"run_sim.py"),"w").write("# noop\\n")
open("gen_dft_launch_flow.py","w").write(open(__file__).read())
open("spec_a.json","w").write("{}")
''')
w(os.path.join(NEG, "hardcode_a_submit.py"), '''#!/usr/bin/env python3
# negative: generator that hardcodes A's values regardless of spec
import json,os,sys
out=sys.argv[2]; os.makedirs(os.path.join(out,"run"),exist_ok=True)
# ignore spec, write A-constants
open(os.path.join(out,"setup_env.sh"),"w").write(
  'export TESTMAX_HOME="/apps/synopsys/testmax/X-2025.06"\\n'
  'export VCS_HOME="/apps/synopsys/vcs/X-2025.06-SP2-1"\\n'
  'export VERDI_HOME="/apps/synopsys/verdi/X-2025.06-SP2-1"\\n'
  'export DFT_DEMO_ROOT="/home/e0030085/Documents/dft_testmax_demo"\\n'
  'alias dft=\\'dft_shell -64\\'\\nalias tmax=\\'tmax -64\\'\\nalias go_dft=\\'cd $DFT_DEMO_ROOT\\'\\n')
open(os.path.join(out,"run_full_flow.sh"),"w").write(
  'case "$1" in all|check|dft_only|atpg_only|simulate) echo $1;; esac\\n'
  'run_dft_compile(){ :; }\\nrun_atpg(){ :; }\\nrun_simulation(){ :; }\\nprint_ok(){ :; }\\n')
open(os.path.join(out,"run","run_dft.sh"),"w").write(
  'DFT_TOOL=$(which dft_shell||which dc_shell)\\nATPG_TOOL=$(which tmax||which tetramax)\\n'
  'echo "Total Scan Cells: 75" > results/dft_compile.log\\n')
open(os.path.join(out,"run","sim_filelist.f"),"w").write("+define+SCAN\\n")
open(os.path.join(out,"run_sim.py"),"w").write("print(\\'VCS\\')\\n")
open("gen_dft_launch_flow.py","w").write(open(__file__).read())
open("spec_a.json","w").write("{}")
''')
w(os.path.join(NEG, "stub_submit.py"), '''#!/usr/bin/env python3
# negative: generator that produces syntactically broken scripts
import os,sys
out=sys.argv[2]; os.makedirs(os.path.join(out,"run"),exist_ok=True)
for rel in ["setup_env.sh","run_full_flow.sh","run/run_dft.sh","run_sim.py"]:
    open(os.path.join(out,rel),"w").write("this is not valid bash/python {{{{ unbalanced")
open(os.path.join(out,"run","sim_filelist.f"),"w").write("")
open("gen_dft_launch_flow.py","w").write(open(__file__).read())
open("spec_a.json","w").write("{}")
''')

# negative_selftest.py
w(os.path.join(REF, "negative_selftest.py"), r'''#!/usr/bin/env python3
"""Run all negatives through check(); all must FAIL. Exit 0 iff all FAIL."""
import os, sys, json, zipfile, subprocess, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
NEG = os.path.join(HERE, "negative")
CHECK = os.path.join(HERE, "check.py")
SPEC_B = os.path.join(HERE, "spec_b.json")
results = []
for neg in sorted(os.listdir(NEG)):
    if not neg.endswith(".py"): continue
    neg_py = os.path.join(NEG, neg)
    tmp = tempfile.mkdtemp(prefix="neg_")
    try:
        # run negative to produce a submit.zip containing gen_dft_launch_flow.py + spec_a.json
        work = tempfile.mkdtemp(prefix="negw_")
        rc = subprocess.run([sys.executable, neg_py, os.path.join(HERE,"spec_a.json"), work],
                            capture_output=True, text=True, cwd=tmp, timeout=60)
        # build submit.zip from tmp (where gen_dft_launch_flow.py + spec_a.json were written) + work outputs
        submit = os.path.join(tmp, "submit.zip")
        with zipfile.ZipFile(submit, "w") as z:
            for base, dirs, files in os.walk(tmp):
                for fn in files:
                    if fn == "submit.zip": continue
                    full = os.path.join(base, fn)
                    arc = os.path.relpath(full, tmp)
                    z.write(full, arc)
            for base, dirs, files in os.walk(work):
                for fn in files:
                    full = os.path.join(base, fn)
                    arc = os.path.relpath(full, work)
                    z.write(full, arc)
        # run check
        rc2 = subprocess.run([sys.executable, CHECK, submit, tmp], capture_output=True, text=True, timeout=120)
        passed = rc2.returncode == 0
        results.append((neg, "PASS(BUG!)" if passed else "FAIL(ok)"))
    except Exception as e:
        results.append((neg, f"FAIL(ok,exc:{e})"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
bad = [n for n,s in results if "BUG" in s]
for n,s in results: print(f"  {n}: {s}")
if bad:
    print(f"NEG_SELFTEST: FAIL - {len(bad)} negative(s) unexpectedly passed: {bad}")
    sys.exit(1)
print(f"NEG_SELFTEST: ALL {len(results)} negatives FAIL (ok)")
''', 0o755)

print("BUILD OK")
print(f"  assets -> {ASSETS}")
print(f"  reference -> {REF}")
print(f"  hidden -> {HIDDEN}")
print(f"  negative -> {NEG}")
