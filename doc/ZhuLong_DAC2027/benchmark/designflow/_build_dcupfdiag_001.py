#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-DcUpfDiag-001 (digital, A-grade faithful, L2).

DC synthesis UPF / save_upf empty-output *diagnosis* (verb: synth-upf-diagnose).
Faithful to trace 1793362556805_gytxt (alan3zh@hfeg0pkn001, mc=440, digital):
user turn 0 verbatim:
  「检查synth/scripts中的dc.tcl和upf/test_chip_power.upf定义，推测dc结果
    save_upf输出的upf文件为空的问题，而且dc产生的netlist无VDD/VSS」
=> user gives SYMPTOMS only (empty save_upf + netlist no PG), no root cause /
   fix => A-grade rule 2 OK => A-grade faithful.

Gold diagnosis (assistant msg#47, verified against real files):
- save_upf empty == `-supplemental` expected (golden UPF + 0 isolation/
  level-shifter/retention => 0 delta => only 2-line comment header). NOT a
  defect. Fix: drop `-supplemental` (or load original UPF downstream).
- netlist no VDD/VSS == DC `write -format verilog` never emits PG pins; PG
  intent travels via UPF + DDC; RTL top has no VDD port. NOT a defect.
- latent: load_upf after link (warn); comma in set_port_attributes port list
  (bug, commented so dormant); `-include_scope -elements {.}` redundant (info).

Distinct verb from AprSetupAudit / AprLogAudit / AprStampFix / VcsEquiv /
FlatNet (none is "diagnose DC UPF root cause").

Deliverable: submit.zip { diagnose_upf.py (generic DC UPF/save_upf diagnostic,
CLI `diagnose_upf.py <bundle_root> [-o out.json]`, pure stdlib) +
diagnosis_A.json }.

Cross-input guard: hidden B bundle has `load_upf` COMMENTED OUT =>
root_cause="upf_not_loaded" (NOT A's "supplemental_zero_delta"); B UPF has an
active `set_isolation` (so "no isolation" evidence differs); B's
set_port_attributes uses SPACE separators (no comma bug); B has no
`-include_scope` (no redundant issue). SUT must truly parse dc.tcl + dc.log
to distinguish, not hardcode A.

Creates:
  assets/<id>/                   (A bundle, real-faithful)
  assets/<id>/hidden/            (B bundle, synthesized, load_upf commented)
  reference/<id>/diagnose_upf.py (reference solution)
  reference/<id>/diagnosis_A.json
  reference/<id>/reference_submit.zip
  reference/<id>/check.py        (14 conditions a-n, L2 subprocess)
  reference/<id>/negative/*.zip  (5)
  reference/<id>/negative_selftest.py
"""
import os, sys, re, json, zipfile, subprocess, tempfile, shutil, py_compile

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID  = "EDA-Eval-DesignFlow-DcUpfDiag-001"
A_DIR   = os.path.join(ROOT, "assets", CID)
B_DIR   = os.path.join(A_DIR, "hidden")
REF_DIR = os.path.join(ROOT, "reference", CID)

# ===========================================================================
# A bundle — faithful reconstruction of gytxt real assets
# ===========================================================================

A_DC_TCL = r"""# dc.tcl -- Design Compiler synthesis driver for hl22_porting_test_chip_v1
# (faithful reconstruction of test_chip_v1/synth/scripts/dc.tcl, 130 lines)
source -echo -verbose ${SETUP_DIR}/common_setup.tcl
source -echo -verbose ${SETUP_DIR}/dc_setup_filenames.tcl

set_app_options -name hdlin.auto_rtl_connect_all_pins -value true
set_app_options -name compile.enable_register_merging -value false

# library search path + target link
set_search_path ${SEARCH_PATH}
set_target_library ${TARGET_LIBRARY_FILES}
set_link_library ${LINK_LIBRARY_FILES}

# read + elaborate RTL
define_design_lib WORK -path ./${DESIGN_NAME}_work
analyze -format sverilog -work WORK ${RTL_SOURCE_FILES}
elaborate ${DESIGN_NAME} -work WORK
current_design ${DESIGN_NAME}
link

# timing / constraints
source -echo -verbose ${SDC_FILE}
set_wire_load_model -name ${WIRE_LOAD_MODEL}
set_wire_load_mode top

# clock
create_clock -name ${CLOCK_NAME} -period ${CLOCK_PERIOD} [get_ports ${CLOCK_PORT}]
set_dont_touch_network [get_clocks ${CLOCK_NAME}]

# --- UPF power intent (loaded AFTER link; see notes) ---
set_app_options -name upf.enable_golden_upf -value true
load_upf ${UPF_FILE}
set_voltage ${VDD_VOLTAGE} -object_list [get_supply_nets VDD]
set_voltage ${VSS_VOLTAGE} -object_list [get_supply_nets VSS]

# multi-voltage + retention checks
check_mv_design -verbose

# compile
compile_ultra -no_autoungroup -gate_clock

# write netlist (note: write -format verilog never emits PG pins)
change_names -rules verilog -hierarchy
write -format verilog -hierarchy -output ${RESULTS_DIR}/${DESIGN_NAME}_postsyn.v

# save upf (supplemental => only writes DELTAS vs golden UPF)
save_upf -supplemental -include_supply_exceptions ${RESULTS_DIR}/${DESIGN_NAME}_dc.upf

# reports
report_area   > ${REPORTS_DIR}/${DESIGN_NAME}.area.rpt
report_timing > ${REPORTS_DIR}/${DESIGN_NAME}.timing.rpt
report_power  > ${REPORTS_DIR}/${DESIGN_NAME}.power.rpt
exit
"""

A_UPF = r"""# test_chip_power.upf -- UPF 3.0 power intent for hl22_porting_test_chip_v1
# (faithful reconstruction, 48 lines)
upf_version 3.0

# supply ports / nets
create_supply_port VDD
create_supply_port VSS
create_supply_port VDD_PM
create_supply_net  VDD -domain pm_top
create_supply_net  VSS -domain pm_top
create_supply_net  VDD_PM -domain pm_top
connect_supply_net pm_top.VDD    -ports VDD
connect_supply_net pm_top.VSS    -ports VSS
connect_supply_net pm_top.VDD_PM -ports VDD_PM

# power domains
set_domain_supply_net ss_aon -primary_power_net VDD    -primary_ground_net VSS
set_domain_supply_net ss_pm  -primary_power_net VDD_PM -primary_ground_net VSS
create_power_domain pd_aon -include_scope -elements {.}
create_power_domain pd_pm  -elements TOPPMBLK_Blk4129/PM_VDDI_Inst

# (no isolation / level-shifter / retention strategies -- both domains 0.72V)

# port states
add_port_state VDD    -state {on  0.72}
add_port_state VSS    -state {on  0.0}
add_port_state VDD_PM -state {on  0.72}
add_port_state VDD    -state {off -}

# (dormant bug: comma-separated port list -- UPF/Tcl requires space-separated)
#set_port_attributes -ports {ClearFreqDiv, SelByFreq0, ModeSel0, ModeSel1, CtrlEn} \
#                    -attribute EXPLICIT_CONNECTION -value false

# power state table
create_pst pst_top -supplies {VDD VSS VDD_PM}
add_pst_state pst_top -state OnAll -supply_test {VDD VSS VDD_PM}
"""

A_SIM_UPF = r"""# sim.upf -- simulation-only UPF (28 lines)
upf_version 3.0
create_supply_port VDD
create_supply_port VSS
create_supply_net VDD -domain sim_top
create_supply_net VSS -domain sim_top
set_domain_supply_net ss_sim -primary_power_net VDD -primary_ground_net VSS
create_power_domain pd_sim -elements {.}
add_port_state VDD -state {on 0.72}
add_port_state VSS -state {on 0.0}
"""

A_SETUP_TCL = r"""# dc_setup_filenames.tcl -- file path variables (59 lines)
# NOTE: FINAL_UPF is defined here but dc.tcl hardcodes ${DESIGN_NAME}_dc.upf
#       in save_upf -- FINAL_UPF is never referenced (latent inconsistency).
set DESIGN_NAME      hl22_porting_test_chip_v1
set SETUP_DIR        ./synth/scripts
set RTL_SOURCE_FILES [glob ./rtl_power/*.v]
set SDC_FILE         ./sdc/hl22.mapped.sdc
set RESULTS_DIR      ./synth/results/dc_2026-10-30-20.08.51
set REPORTS_DIR      ./synth/reports/dc_2026-10-30-20.08.51
set TARGET_LIBRARY_FILES [glob ./pdk/stdcells_ssg.lib]
set LINK_LIBRARY_FILES   [glob ./pdk/stdcells_ssg.lib]
set WIRE_LOAD_MODEL  "smic18_wl10"
set CLOCK_NAME       clk
set CLOCK_PORT       clk
set CLOCK_PERIOD     5.0
set VDD_VOLTAGE      0.72
set VSS_VOLTAGE      0.0
set UPF_FILE         ./upf/test_chip_power.upf
set FINAL_UPF        ${RESULTS_DIR}/${DESIGN_NAME}_dc.upf
set SEARCH_PATH      "./pdk ./rtl_power ./sdc ./upf"
"""

A_SNPS_UPF_LOG = """# snps_hl22_porting_test_chip_v1.upf.log -- UPF load echo (44 lines)
Begin loading UPF file: ./upf/test_chip_power.upf
upf_version 3.0
create_supply_port VDD
create_supply_port VSS
create_supply_port VDD_PM
create_supply_net  VDD -domain pm_top
create_supply_net  VSS -domain pm_top
create_supply_net  VDD_PM -domain pm_top
connect_supply_net pm_top.VDD    -ports VDD
connect_supply_net pm_top.VSS    -ports VSS
connect_supply_net pm_top.VDD_PM -ports VDD_PM
set_domain_supply_net ss_aon -primary_power_net VDD    -primary_ground_net VSS
set_domain_supply_net ss_pm  -primary_power_net VDD_PM -primary_ground_net VSS
create_power_domain pd_aon -include_scope -elements {.}
create_power_domain pd_pm  -elements TOPPMBLK_Blk4129/PM_VDDI_Inst
add_port_state VDD    -state {on  0.72}
add_port_state VSS    -state {on  0.0}
add_port_state VDD_PM -state {on  0.72}
add_port_state VDD    -state {off -}
create_pst pst_top -supplies {VDD VSS VDD_PM}
add_pst_state pst_top -state OnAll -supply_test {VDD VSS VDD_PM}
End loading UPF file: ./upf/test_chip_power.upf
1
"""

A_DC_LOG = """# dc_2026-10-30-20.08.51.log -- Design Compiler run log (excerpt, 768L)
# ELABORATE / LINK
Current design is 'hl22_porting_test_chip_v1'.
Linking ...
Linking complete.
# UPF LOAD
set_app_options -name upf.enable_golden_upf -value true
Loading UPF file ./upf/test_chip_power.upf ...
End loading UPF file.
# MULTI-VOLTAGE CHECK
check_mv_design -verbose
Information: UPF-405 Primary supply VDD/VSS assumed for 13 ports. (UPF-405)
Information: UPF-464 0 repeater cells inserted. (UPF-464)
Information: UPF-214 0 isolation cells inserted. (UPF-214)
Information: MV-238 0 level shifters inserted. (MV-238)
Information: MV-239 0 retention cells inserted. (MV-239)
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
check_mv_design: No Errors/Warnings Found.
# COMPILE
compile_ultra -no_autoungroup -gate_clock
Beginning Assignment-Pass.
Beginning Optimization-Pass.
Optimization complete.
# WRITE
write -format verilog -hierarchy -output ./synth/results/dc_2026-10-30-20.08.51/hl22_porting_test_chip_v1_postsyn.v
# SAVE_UPF (supplemental => only deltas vs golden UPF)
save_upf -supplemental -include_supply_exceptions ./synth/results/dc_2026-10-30-20.08.51/hl22_porting_test_chip_v1_dc.upf
# REPORTS
report_area   > ./synth/reports/dc_2026-10-30-20.08.51/hl22_porting_test_chip_v1.area.rpt
report_timing > ./synth/reports/dc_2026-10-30-20.08.51/hl22_porting_test_chip_v1.timing.rpt
report_power  > ./synth/reports/dc_2026-10-30-20.08.51/hl22_porting_test_chip_v1.power.rpt
exit
"""

A_DC_UPF = """#Generated by Design Compiler (S-2021.06-SP2)
#Supplemental UPF [includes derived supply exceptions]
"""

A_POSTSYN_HEAD = """// hl22_porting_test_chip_v1_postsyn.v  (head excerpt, 60 lines)
module hl22_porting_test_chip_v1 ( TMOut, TMReady, GroupSelect0, GroupSelect1,
    GroupSelect2, GroupSelect3, ClearFreqDiv, SelByFreq0, ModeSel0, ModeSel1,
    CtrlEn, clk, rst_n );
    input TMOut, TMReady, GroupSelect0, GroupSelect1, GroupSelect2, GroupSelect3;
    input ClearFreqDiv, SelByFreq0, ModeSel0, ModeSel1, CtrlEn;
    input clk, rst_n;
    wire n1, n2, n3, n4, n5, n6, n7, n8, n9, n10;
    INVD2BWP40P140LVT U1 ( .I(D0), .ZN(n1) );
    INVD2BWP40P140LVT U2 ( .I(D1), .ZN(n2) );
    INVD4BWP40P140LVT U3 ( .I(n1), .ZN(n3) );
    ND2D1BWP40P140LVT U4 ( .A1(n2), .A2(n3), .ZN(n4) );
    ND2D1BWP40P140LVT U5 ( .A1(n4), .A2(D2), .ZN(n5) );
    INVD2BWP40P140LVT U6 ( .I(n5), .ZN(n6) );
    INVD2BWP40P140LVT U7 ( .I(D3), .ZN(n7) );
    ND2D1BWP40P140LVT U8 ( .A1(n6), .A2(n7), .ZN(n8) );
    INVD2BWP40P140LVT U9 ( .I(n8), .ZN(n9) );
    INVD2BWP40P140LVT U10 ( .I(D4), .ZN(n10) );
    ND2D1BWP40P140LVT U11 ( .A1(n9), .A2(n10), .ZN(TMOut) );
    INVD2BWP40P140LVT U12 ( .I(D5), .ZN(TMReady) );
    ND2D1BWP40P140LVT U13 ( .A1(GroupSelect0), .A2(GroupSelect1), .ZN(n11) );
    ND2D1BWP40P140LVT U14 ( .A1(GroupSelect2), .A2(GroupSelect3), .ZN(n12) );
    ND2D1BWP40P140LVT U15 ( .A1(n11), .A2(n12), .ZN(ClearFreqDiv) );
    INVD2BWP40P140LVT U16 ( .I(SelByFreq0), .ZN(n13) );
    ND2D1BWP40P140LVT U17 ( .A1(ModeSel0), .A2(ModeSel1), .ZN(n14) );
    ND2D1BWP40P140LVT U18 ( .A1(n13), .A2(n14), .ZN(CtrlEn) );
endmodule
"""

A_RTL_TOP = """// hl22_porting_test_chip.v -- RTL top (rtl_power/, head excerpt, 96 lines)
module hl22_porting_test_chip_v1 (
    TMOut, TMReady, GroupSelect0, GroupSelect1, GroupSelect2, GroupSelect3,
    ClearFreqDiv, SelByFreq0, ModeSel0, ModeSel1, CtrlEn, clk, rst_n
);
    output TMOut, TMReady;
    output GroupSelect0, GroupSelect1, GroupSelect2, GroupSelect3;
    output ClearFreqDiv, SelByFreq0, ModeSel0, ModeSel1, CtrlEn;
    input  clk, rst_n;

    wire [7:0] data_bus;
    wire [3:0] sel;
    reg  [15:0] cnt;
    reg  [7:0]  acc;

    // frequency divider
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) cnt <= 16'h0;
        else cnt <= cnt + 1'b1;
    end
    assign ClearFreqDiv = (cnt == 16'hffff);
    assign SelByFreq0   = cnt[0];
    assign ModeSel0     = cnt[1];
    assign ModeSel1     = cnt[2];
    assign CtrlEn       = cnt[3];
    assign GroupSelect0 = cnt[4];
    assign GroupSelect1 = cnt[5];
    assign GroupSelect2 = cnt[6];
    assign GroupSelect3 = cnt[7];

    // accumulator
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) acc <= 8'h0;
        else acc <= acc + data_bus[7:0];
    end
    assign TMOut    = acc[7];
    assign TMReady  = (acc == 8'hff);
endmodule
"""

# ===========================================================================
# B bundle -- synthesized, load_upf COMMENTED => root_cause upf_not_loaded
# ===========================================================================

B_DC_TCL = r"""# dc.tcl -- Design Compiler synthesis driver for hl22_porting_test_chip_v2
# (B-grade synthesized: load_upf COMMENTED OUT => UPF never loaded)
source -echo -verbose ${SETUP_DIR}/common_setup.tcl
source -echo -verbose ${SETUP_DIR}/dc_setup_filenames.tcl

set_app_options -name hdlin.auto_rtl_connect_all_pins -value true
set_search_path ${SEARCH_PATH}
set_target_library ${TARGET_LIBRARY_FILES}
set_link_library ${LINK_LIBRARY_FILES}

define_design_lib WORK -path ./${DESIGN_NAME}_work
analyze -format sverilog -work WORK ${RTL_SOURCE_FILES}
elaborate ${DESIGN_NAME} -work WORK
current_design ${DESIGN_NAME}
link

source -echo -verbose ${SDC_FILE}
create_clock -name ${CLOCK_NAME} -period ${CLOCK_PERIOD} [get_ports ${CLOCK_PORT}]
set_dont_touch_network [get_clocks ${CLOCK_NAME}]

# --- UPF power intent (B: load_upf COMMENTED OUT -- UPF never loaded) ---
set_app_options -name upf.enable_golden_upf -value true
#load_upf ${UPF_FILE}
set_voltage ${VDDIO_VOLTAGE} -object_list [get_supply_nets VDDIO]
set_voltage ${VSS_VOLTAGE}    -object_list [get_supply_nets VSS]

check_mv_design -verbose
compile_ultra -no_autoungroup -gate_clock

change_names -rules verilog -hierarchy
write -format verilog -hierarchy -output ${RESULTS_DIR}/${DESIGN_NAME}_postsyn.v
save_upf -supplemental -include_supply_exceptions ${RESULTS_DIR}/${DESIGN_NAME}_dc.upf

report_area   > ${REPORTS_DIR}/${DESIGN_NAME}.area.rpt
report_timing > ${REPORTS_DIR}/${DESIGN_NAME}.timing.rpt
report_power  > ${REPORTS_DIR}/${DESIGN_NAME}.power.rpt
exit
"""

B_UPF = r"""# test_chip_power.upf -- UPF 3.0 power intent for hl22_porting_test_chip_v2
# (B-grade synthesized: VDDIO domain, ACTIVE isolation, space-separated ports)
upf_version 3.0

create_supply_port VDDIO
create_supply_port VSS
create_supply_net  VDDIO -domain pm_io
create_supply_net  VSS   -domain pm_io
connect_supply_net pm_io.VDDIO -ports VDDIO
connect_supply_net pm_io.VSS   -ports VSS

set_domain_supply_net ss_io  -primary_power_net VDDIO -primary_ground_net VSS
set_domain_supply_net ss_aon -primary_power_net VDDIO -primary_ground_net VSS
create_power_domain pd_io  -elements {.}
create_power_domain pd_aon -elements TOPPMBLK_Blk5500/PM_VDDI_Inst

# ACTIVE isolation strategy (B has isolation; A has none)
set_isolation iso -domain pd_io \
    -source_supply ss_io.power -sink_supply ss_aon.power \
    -apply-condition {VDDIO == off}

# ACTIVE set_port_attributes with SPACE-separated list (B has no comma bug)
set_port_attributes -ports {PortA PortB PortC PortD PortE} \
                    -attribute EXPLICIT_CONNECTION -value false

add_port_state VDDIO -state {on 0.72}
add_port_state VSS   -state {on 0.0}
add_port_state VDDIO -state {off -}

create_pst pst_io -supplies {VDDIO VSS}
add_pst_state pst_io -state OnIO  -supply_test {VDDIO VSS}
add_pst_state pst_io -state OffIO -supply_test {VDDIO VSS}
"""

B_SETUP_TCL = r"""# dc_setup_filenames.tcl -- file path variables (B)
set DESIGN_NAME      hl22_porting_test_chip_v2
set SETUP_DIR        ./synth/scripts
set RTL_SOURCE_FILES [glob ./rtl_power/*.v]
set SDC_FILE         ./sdc/hl22_v2.mapped.sdc
set RESULTS_DIR      ./synth/results/dc_2026-11-04-09.00.00
set REPORTS_DIR      ./synth/reports/dc_2026-11-04-09.00.00
set TARGET_LIBRARY_FILES [glob ./pdk/stdcells_ssg.lib]
set LINK_LIBRARY_FILES   [glob ./pdk/stdcells_ssg.lib]
set WIRE_LOAD_MODEL  "smic18_wl10"
set CLOCK_NAME       clk
set CLOCK_PORT       clk
set CLOCK_PERIOD     4.0
set VDDIO_VOLTAGE    0.72
set VSS_VOLTAGE      0.0
set UPF_FILE         ./upf/test_chip_power.upf
set FINAL_UPF        ${RESULTS_DIR}/${DESIGN_NAME}_dc.upf
set SEARCH_PATH      "./pdk ./rtl_power ./sdc ./upf"
"""

B_SNPS_UPF_LOG = """# snps_hl22_porting_test_chip_v2.upf.log -- (B: UPF NOT loaded)
# load_upf is commented in dc.tcl; this log is empty of UPF content
# (no "End loading UPF file" line)
0
"""

B_DC_LOG = """# dc_2026-11-04-09.00.00.log -- Design Compiler run log (B, excerpt)
Current design is 'hl22_porting_test_chip_v2'.
Linking ...
Linking complete.
# UPF LOAD
set_app_options -name upf.enable_golden_upf -value true
Warning: UPF not loaded -- load_upf not invoked. (UPF-900)
# MULTI-VOLTAGE CHECK
check_mv_design -verbose
Warning: No power intent loaded; skipping MV checks. (MV-100)
check_mv_design: No Errors/Warnings Found.
# COMPILE
compile_ultra -no_autoungroup -gate_clock
Optimization complete.
# WRITE
write -format verilog -hierarchy -output ./synth/results/dc_2026-11-04-09.00.00/hl22_porting_test_chip_v2_postsyn.v
# SAVE_UPF (supplemental; UPF never loaded => 0 delta => empty output)
save_upf -supplemental -include_supply_exceptions ./synth/results/dc_2026-11-04-09.00.00/hl22_porting_test_chip_v2_dc.upf
exit
"""

B_DC_UPF = """#Generated by Design Compiler (S-2021.06-SP2)
#Supplemental UPF [includes derived supply exceptions]
"""

B_POSTSYN_HEAD = """// hl22_porting_test_chip_v2_postsyn.v  (B, head excerpt)
module hl22_porting_test_chip_v2 ( DOut, DReady, BankSel0, BankSel1, BankSel2,
    BankSel3, WrEn, RdEn, clk, rst_n );
    input DOut, DReady, BankSel0, BankSel1, BankSel2, BankSel3, WrEn, RdEn;
    input clk, rst_n;
    wire q1, q2, q3, q4, q5, q6;
    INVD2BWP40P140LVT R1 ( .I(A0), .ZN(q1) );
    INVD4BWP40P140LVT R2 ( .I(q1), .ZN(q2) );
    ND2D1BWP40P140LVT R3 ( .A1(q2), .A2(A1), .ZN(q3) );
    INVD2BWP40P140LVT R4 ( .I(q3), .ZN(q4) );
    ND2D1BWP40P140LVT R5 ( .A1(q4), .A2(A2), .ZN(q5) );
    INVD2BWP40P140LVT R6 ( .I(q5), .ZN(q6) );
    ND2D1BWP40P140LVT R7 ( .A1(q6), .A2(A3), .ZN(DOut) );
    INVD2BWP40P140LVT R8 ( .I(A4), .ZN(DReady) );
endmodule
"""

B_RTL_TOP = """// hl22_porting_test_chip_v2.v -- RTL top (B, head excerpt)
module hl22_porting_test_chip_v2 (
    DOut, DReady, BankSel0, BankSel1, BankSel2, BankSel3, WrEn, RdEn, clk, rst_n
);
    output DOut, DReady;
    output BankSel0, BankSel1, BankSel2, BankSel3, WrEn, RdEn;
    input  clk, rst_n;

    reg  [15:0] phase;
    reg  [7:0]  buf;
    wire [3:0]  sel;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) phase <= 16'h0;
        else phase <= phase + 1'b1;
    end
    assign BankSel0 = phase[4];
    assign BankSel1 = phase[5];
    assign BankSel2 = phase[6];
    assign BankSel3 = phase[7];
    assign WrEn = phase[8];
    assign RdEn = phase[9];
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) buf <= 8'h0;
        else buf <= buf + sel;
    end
    assign DOut   = buf[7];
    assign DReady = (buf == 8'hff);
endmodule
"""

# ===========================================================================
# Reference solution: diagnose_upf.py  (generic, pure stdlib, ADAPTIVE)
# ===========================================================================

DIAGNOSE_UPF_PY = r'''#!/usr/bin/env python3
"""diagnose_upf.py -- Generic DC synthesis UPF / save_upf diagnostic.

CLI: diagnose_upf.py <bundle_root> [-o out.json]

Reads a bundle of DC synthesis artefacts and emits a structured diagnosis of
two symptoms:
  1. save_upf output is empty  -> root_cause + is_defect + evidence + fix
  2. postsyn netlist has no VDD/VSS -> root_cause + is_defect + evidence

plus a list of latent UPF / dc.tcl issues.

The diagnostic is GENERIC: it parses the bundle's files (dc.tcl, *.upf, dc.log,
dc.upf, postsyn_head.v, rtl_top.v) and infers the root cause from observed
evidence. It does NOT hardcode any design name or any specific answer.

Bundle layout (any of these that exist are read):
  <bundle>/dc.tcl              -- DC driver Tcl
  <bundle>/*.upf               -- UPF power-intent (test_chip_power.upf etc.)
  <bundle>/dc.log              -- DC run log (must contain UPF-214 / UPF-405 etc.)
  <bundle>/dc.upf              -- save_upf output (often empty)
  <bundle>/postsyn_head.v      -- postsyn netlist head excerpt
  <bundle>/rtl_top.v           -- RTL top module port excerpt
  <bundle>/snps_upf.log        -- UPF-load echo log

Output schema (JSON):
  {
    "save_upf_empty": {
        "root_cause": "supplemental_zero_delta" | "upf_not_loaded" |
                      "save_upf_missing" | "unknown",
        "mechanism": "<human-readable explanation>",
        "evidence": ["<evidence string>", ...],
        "fix": ["<fix step>", ...],
        "is_defect": false | true
    },
    "netlist_no_pg": {
        "root_cause": "dc_write_verilog_no_pg" | "pg_present" | "unknown",
        "mechanism": "...",
        "evidence": [...],
        "is_defect": false | true
    },
    "latent_issues": [
        {"id":"<id>","severity":"bug|warn|info","desc":"...","fix":"..."}
    ]
  }
"""
import os, sys, re, json, glob, argparse


def _read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def _find(bundle, *names):
    """Return first existing path under bundle matching any of names (basename)."""
    for n in names:
        p = os.path.join(bundle, n)
        if os.path.isfile(p):
            return p
    # fallback: glob by suffix
    return None


def _find_by_glob(bundle, pat):
    matches = glob.glob(os.path.join(bundle, pat))
    return matches[0] if matches else None


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------

def parse_dc_tcl(text):
    """Extract structural facts from dc.tcl."""
    facts = {
        "has_load_upf_active": False,
        "has_load_upf_commented": False,
        "has_save_upf_supplemental": False,
        "has_save_upf": False,
        "has_enable_golden_upf": False,
        "link_line": None,
        "load_upf_line": None,
    }
    for i, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        # load_upf
        m = re.search(r'(^|\s)#\s*load_upf\b', s)
        if m:
            facts["has_load_upf_commented"] = True
        elif re.search(r'(^|\s)load_upf\b', s) and not s.startswith("#"):
            facts["has_load_upf_active"] = True
            if facts["load_upf_line"] is None:
                facts["load_upf_line"] = i
        # save_upf
        if re.search(r'\bsave_upf\b', s) and not s.startswith("#"):
            facts["has_save_upf"] = True
            if "-supplemental" in s:
                facts["has_save_upf_supplemental"] = True
        # enable_golden_upf
        if "enable_golden_upf" in s and "true" in s.lower() and not s.startswith("#"):
            facts["has_enable_golden_upf"] = True
        # link (active link command, not in a comment)
        if re.search(r'(^|\s)link\b', s) and not s.startswith("#"):
            if facts["link_line"] is None:
                facts["link_line"] = i
    return facts


def parse_upf(text):
    """Extract UPF power-strategy facts.

    Strategies (isolation/level-shifter/retention) are checked on
    comment-stripped text (only ACTIVE strategies count).
    The comma-in-set_port_attributes bug is checked on RAW text including
    COMMENTED lines -- a dormant comma-separated port list is still a latent
    bug that will surface when the line is uncommented.
    """
    t = re.sub(r'(?m)^\s*#.*$', '', text)  # stripped for active strategies
    return {
        "has_isolation": bool(re.search(r'\bset_isolation\b', t)),
        "has_level_shifter": bool(re.search(r'\bset_level_shifter\b', t)),
        "has_retention": bool(re.search(r'\bset_retention\b', t)),
        "has_comma_in_set_port_attributes": bool(
            re.search(r'set_port_attributes[^}]*\{[^}]*,[^}]*\}', text)),
        "has_include_scope_elements_dot": bool(
            re.search(r'-include_scope\s+-elements\s*\{\s*\.\s*\}', t)),
    }


def parse_dc_log(text):
    """Extract UPF / MV markers from DC log."""
    return {
        "upf_214": bool(re.search(r'UPF-214\b', text)),
        "upf_214_zero_isolation": bool(
            re.search(r'UPF-214\s+0\s+isolation', text)),
        "upf_405": bool(re.search(r'UPF-405\b', text)),
        "upf_464": bool(re.search(r'UPF-464\b', text)),
        "upf_not_loaded": bool(re.search(r'UPF not loaded', text, re.I)),
        "has_enable_golden_upf": bool(
            re.search(r'enable_golden_upf.*true', text, re.I)),
        "has_save_upf_supplemental": bool(
            re.search(r'save_upf\s+-supplemental', text)),
        "check_mv_clean": bool(re.search(r'check_mv_design:\s*No Errors', text)),
    }


def parse_dc_upf(text):
    """Return non-comment, non-blank line count of the save_upf output."""
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        lines.append(s)
    return {"non_comment_lines": len(lines), "is_empty": len(lines) == 0}


def parse_postsyn(text):
    """Detect PG pin references in postsyn netlist head."""
    return {"has_pg_pin": bool(re.search(r'\.(VDD|VSS|VDD_PM|VDDIO)\b', text))}


def parse_rtl_top(text):
    """Detect PG ports in RTL top module port list."""
    return {"has_pg_port": bool(re.search(r'\b(VDD|VSS|VDD_PM|VDDIO)\b', text))}


# ---------------------------------------------------------------------------
# Root-cause inference
# ---------------------------------------------------------------------------

def diagnose_save_upf_empty(dc_tcl, upf, dc_log, dc_upf):
    """Decide why save_upf output is empty."""
    evidence = []
    # Case 1: UPF never loaded (load_upf commented / UPF not loaded warning)
    if dc_tcl["has_load_upf_commented"] and not dc_tcl["has_load_upf_active"]:
        evidence.append("load_upf commented out in dc.tcl (UPF never loaded)")
        if dc_log["upf_not_loaded"]:
            evidence.append("dc.log: 'UPF not loaded' warning")
        return {
            "root_cause": "upf_not_loaded",
            "mechanism": "UPF power intent was never loaded into DC; save_upf "
                         "-supplemental has no golden UPF baseline and no delta "
                         "to write, so only the comment header is emitted.",
            "evidence": evidence,
            "fix": ["Uncomment `load_upf ${UPF_FILE}` in dc.tcl so the UPF "
                    "power intent is loaded before save_upf is invoked."],
            "is_defect": True,
        }
    # Case 2: supplemental with zero power strategies => zero delta
    if dc_tcl["has_save_upf_supplemental"] and dc_tcl["has_enable_golden_upf"]:
        if (not upf["has_isolation"] and not upf["has_level_shifter"]
                and not upf["has_retention"]):
            evidence.append("save_upf -supplemental + enable_golden_upf true "
                            "(only deltas vs golden UPF are written)")
            evidence.append("UPF has no isolation / level-shifter / retention "
                            "strategies (both domains same voltage)")
            if dc_log["upf_214_zero_isolation"]:
                evidence.append("dc.log: UPF-214 0 isolation cells inserted")
            if dc_log["upf_405"]:
                evidence.append("dc.log: UPF-405 primary supply assumed")
            if dc_log["upf_464"]:
                evidence.append("dc.log: UPF-464 0 repeater cells")
            if dc_log["check_mv_clean"]:
                evidence.append("dc.log: check_mv_design No Errors/Warnings "
                                "(power intent consistent)")
            return {
                "root_cause": "supplemental_zero_delta",
                "mechanism": "With enable_golden_upf=true and save_upf "
                             "-supplemental, DC writes only the DELTA between "
                             "the synthesized design and the golden UPF. The "
                             "UPF declares no isolation/level-shifter/retention "
                             "and both domains share the same voltage, so DC "
                             "inserts no power-management cells (UPF-214/464 = "
                             "0) and there is no supply exception. The delta "
                             "is empty => save_upf emits only the 2-line "
                             "comment header. This is expected behaviour, NOT "
                             "a defect.",
                "evidence": evidence,
                "fix": ["Drop `-supplemental` to emit the full UPF: "
                        "`save_upf ${RESULTS_DIR}/${DESIGN_NAME}_dc.upf`",
                        "OR keep `-supplemental` and have the downstream tool "
                        "(ICC2/Innovus) load the original UPF first, then this "
                        "supplemental delta."],
                "is_defect": False,
            }
    # Case 3: no save_upf at all
    if not dc_tcl["has_save_upf"]:
        return {
            "root_cause": "save_upf_missing",
            "mechanism": "dc.tcl does not invoke save_upf at all.",
            "evidence": ["no `save_upf` command found in dc.tcl"],
            "fix": ["Add `save_upf ${RESULTS_DIR}/${DESIGN_NAME}_dc.upf` to "
                    "dc.tcl."],
            "is_defect": True,
        }
    # Fallback
    return {
        "root_cause": "unknown",
        "mechanism": "Could not determine root cause from the provided files.",
        "evidence": evidence,
        "fix": ["Inspect dc.tcl + dc.log manually."],
        "is_defect": True,
    }


def diagnose_netlist_no_pg(postsyn, rtl_top):
    """Decide why postsyn netlist has no VDD/VSS."""
    evidence = []
    if (not postsyn["has_pg_pin"]) and (not rtl_top["has_pg_port"]):
        evidence.append("postsyn netlist head: no .VDD/.VSS pin references on "
                        "any cell instance")
        evidence.append("rtl top module port list: no VDD/VSS/VDD_PM port")
        return {
            "root_cause": "dc_write_verilog_no_pg",
            "mechanism": "Design Compiler `write -format verilog` never emits "
                         "PG (power/ground) pins on cell instances, even in a "
                         "UPF flow. PG connectivity is carried by the UPF "
                         "power intent + DDC database, and is realised "
                         "downstream by ICC2 `connect_pg` / Innovus "
                         "`globalNetConnect` / power-aware simulation. The RTL "
                         "top itself has no VDD port -- UPF create_supply_port "
                         "is a virtual power port, not a verilog port. This is "
                         "DC's固有 behaviour, NOT a defect.",
            "evidence": evidence,
            "fix": ["No fix required in DC. Connect PG downstream: ICC2 "
                    "connect_pg / Innovus globalNetConnect; use sim.upf for "
                    "power-aware simulation."],
            "is_defect": False,
        }
    if postsyn["has_pg_pin"]:
        return {
            "root_cause": "pg_present",
            "mechanism": "postsyn netlist already contains PG pin references.",
            "evidence": ["postsyn netlist has .VDD/.VSS pins"],
            "is_defect": False,
        }
    return {
        "root_cause": "unknown",
        "mechanism": "Could not determine PG status.",
        "evidence": evidence,
        "is_defect": False,
    }


def collect_latent_issues(dc_tcl, upf, dc_log):
    issues = []
    # load_upf ordering: link before load_upf (active)
    if (dc_tcl["has_load_upf_active"] and dc_tcl["link_line"] is not None
            and dc_tcl["load_upf_line"] is not None
            and dc_tcl["link_line"] < dc_tcl["load_upf_line"]):
        issues.append({
            "id": "load_upf_order",
            "severity": "warn",
            "desc": "load_upf is invoked AFTER link (dc.tcl). Synopsys "
                    "recommends elaborate -> load_upf -> link so the supply "
                    "network is bound before linking.",
            "fix": "Move `load_upf ${UPF_FILE}` before `link` in dc.tcl.",
        })
    # load_upf commented out (B-specific)
    if dc_tcl["has_load_upf_commented"] and not dc_tcl["has_load_upf_active"]:
        issues.append({
            "id": "load_upf_commented",
            "severity": "bug",
            "desc": "load_upf is commented out in dc.tcl -- UPF power intent "
                    "is never loaded; save_upf output is empty because there "
                    "is no golden UPF baseline.",
            "fix": "Uncomment `load_upf ${UPF_FILE}` in dc.tcl.",
        })
    # comma in set_port_attributes port list (dormant bug)
    if upf["has_comma_in_set_port_attributes"]:
        issues.append({
            "id": "comma_in_set_port_attributes",
            "severity": "bug",
            "desc": "set_port_attributes port list uses COMMA separators. "
                    "UPF/Tcl lists must be SPACE-separated. Currently dormant "
                    "(the line is commented), but un-commenting will raise a "
                    "Tcl syntax error.",
            "fix": "Replace commas with spaces in the set_port_attributes "
                   "port list: `{ClearFreqDiv SelByFreq0 ModeSel0 ModeSel1 "
                   "CtrlEn}`.",
        })
    # redundant -include_scope -elements {.}
    if upf["has_include_scope_elements_dot"]:
        issues.append({
            "id": "redundant_include_scope",
            "severity": "info",
            "desc": "`create_power_domain ... -include_scope -elements {.}` -- "
                    "`-include_scope` together with `-elements {.}` is "
                    "redundant (the top scope is already implied).",
            "fix": "Drop `-elements {.}` (keep -include_scope) or vice versa.",
        })
    return issues


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def diagnose(bundle):
    dc_tcl_path = _find(bundle, "dc.tcl") or _find_by_glob(bundle, "*dc*.tcl")
    upf_path = (_find(bundle, "test_chip_power.upf")
                or _find_by_glob(bundle, "*.upf"))
    dc_log_path = _find(bundle, "dc.log") or _find_by_glob(bundle, "*dc*.log")
    dc_upf_path = _find(bundle, "dc.upf")
    postsyn_path = _find(bundle, "postsyn_head.v") or _find(bundle, "postsyn.v")
    rtl_top_path = _find(bundle, "rtl_top.v")
    # snps_upf.log read into dc_log supplement (optional)
    snps_path = _find(bundle, "snps_upf.log")

    dc_tcl_text = _read(dc_tcl_path) if dc_tcl_path else ""
    upf_text = _read(upf_path) if upf_path else ""
    # If multiple .upf files, pick the one that is NOT dc.upf and NOT sim.upf
    if upf_path is None or os.path.basename(upf_path) in ("dc.upf", "sim.upf"):
        for p in glob.glob(os.path.join(bundle, "*.upf")):
            if os.path.basename(p) not in ("dc.upf", "sim.upf"):
                upf_text = _read(p)
                upf_path = p
                break
    dc_log_text = _read(dc_log_path) if dc_log_path else ""
    dc_upf_text = _read(dc_upf_path) if dc_upf_path else ""
    postsyn_text = _read(postsyn_path) if postsyn_path else ""
    rtl_top_text = _read(rtl_top_path) if rtl_top_path else ""

    dc_tcl_f = parse_dc_tcl(dc_tcl_text)
    upf_f = parse_upf(upf_text)
    dc_log_f = parse_dc_log(dc_log_text)
    dc_upf_f = parse_dc_upf(dc_upf_text)
    postsyn_f = parse_postsyn(postsyn_text)
    rtl_top_f = parse_rtl_top(rtl_top_text)

    save_upf_diag = diagnose_save_upf_empty(dc_tcl_f, upf_f, dc_log_f, dc_upf_f)
    netlist_diag = diagnose_netlist_no_pg(postsyn_f, rtl_top_f)
    latent = collect_latent_issues(dc_tcl_f, upf_f, dc_log_f)

    return {
        "save_upf_empty": save_upf_diag,
        "netlist_no_pg": netlist_diag,
        "latent_issues": latent,
        "_bundle": os.path.abspath(bundle),
        "_files_found": {
            "dc.tcl": bool(dc_tcl_path),
            "upf": bool(upf_path),
            "dc.log": bool(dc_log_path),
            "dc.upf": bool(dc_upf_path),
            "postsyn_head.v": bool(postsyn_path),
            "rtl_top.v": bool(rtl_top_path),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle_root")
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()
    if not os.path.isdir(args.bundle_root):
        sys.stderr.write("bundle_root not a directory: %s\n" % args.bundle_root)
        sys.exit(2)
    diag = diagnose(args.bundle_root)
    out = json.dumps(diag, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        sys.stdout.write(out + "\n")


if __name__ == "__main__":
    main()
'''

# ===========================================================================
# check.py -- 14 conditions a-n, L2 subprocess
# ===========================================================================

CHECK_PY = r'''#!/usr/bin/env python3
"""check.py - grader for EDA-Eval-DesignFlow-DcUpfDiag-001.

Deliverable: submit.zip containing diagnose_upf.py (generic DC UPF/save_upf
diagnostic, CLI `diagnose_upf.py <bundle_root> [-o out.json]`, pure stdlib)
and diagnosis_A.json (precomputed diagnosis for the visible A bundle).

Judgment: runs the candidate's diagnose_upf.py on visible A and hidden B
(subprocess, real python interpreter), compares to an INDEPENDENT oracle that
re-derives the expected root causes + latent issues from the bundle files
(different code path than the candidate). 14 independent conditions (a)-(n).

Cross-input guard: hidden B has `load_upf` COMMENTED OUT => expected
root_cause="upf_not_loaded" (NOT A's "supplemental_zero_delta"); B's UPF has
an active isolation + space-separated set_port_attributes + no -include_scope.
A candidate that hardcodes A's answer will fail on B (k / l / n).

Distinct from AprSetupAudit / AprLogAudit / AprStampFix / VcsEquiv / FlatNet:
verb = synth-upf-diagnose (diagnose root cause, not audit-setup / audit-log /
fix / run-equiv / flatten).
"""
import os, re, sys, json, zipfile, subprocess, tempfile, py_compile, shutil

CID = "EDA-Eval-DesignFlow-DcUpfDiag-001"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "..", "assets", CID))
A_DIR = ASSETS
B_DIR = os.path.join(ASSETS, "hidden")


def _run(cmd, cwd, timeout=120):
    try:
        r = subprocess.run(["bash", "-lc", cmd], cwd=cwd,
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)


def _extract(zip_path, dest):
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(dest)


# ---------------------------------------------------------------------------
# INDEPENDENT oracle (different code path than the candidate)
# ---------------------------------------------------------------------------

def _o_read(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def oracle(bundle):
    """Re-derive expected diagnosis for a bundle via a separate parser."""
    dc_tcl = _o_read(os.path.join(bundle, "dc.tcl"))
    upf = _o_read(os.path.join(bundle, "test_chip_power.upf"))
    dc_log = _o_read(os.path.join(bundle, "dc.log"))

    # load_upf active vs commented
    load_upf_active = bool(re.search(r'(?m)^\s*load_upf\b', dc_tcl))
    load_upf_commented = bool(re.search(r'(?m)^\s*#\s*load_upf\b', dc_tcl))
    save_upf_sup = bool(re.search(r'(?m)^\s*save_upf\b.*-supplemental', dc_tcl))
    golden = bool(re.search(r'enable_golden_upf.*true', dc_tcl, re.I))

    # upf strategies (strip comments first for ACTIVE strategies)
    upf_nc = re.sub(r'(?m)^\s*#.*$', '', upf)
    has_iso = bool(re.search(r'\bset_isolation\b', upf_nc))
    has_ls  = bool(re.search(r'\bset_level_shifter\b', upf_nc))
    has_ret = bool(re.search(r'\bset_retention\b', upf_nc))
    # comma bug: check RAW text (incl. commented) -- dormant bug still counts
    has_comma = bool(re.search(r'set_port_attributes[^}]*\{[^}]*,[^}]*\}', upf))
    has_incl_scope = bool(re.search(
        r'-include_scope\s+-elements\s*\{\s*\.\s*\}', upf_nc))

    upf_214_zero = bool(re.search(r'UPF-214\s+0\s+isolation', dc_log))
    upf_405 = bool(re.search(r'UPF-405\b', dc_log))
    upf_464 = bool(re.search(r'UPF-464\b', dc_log))
    upf_not_loaded = bool(re.search(r'UPF not loaded', dc_log, re.I))
    mv_clean = bool(re.search(r'check_mv_design:\s*No Errors', dc_log))

    # root cause
    if load_upf_commented and not load_upf_active:
        rc = "upf_not_loaded"
        is_def = True
    elif (save_upf_sup and golden and not has_iso and not has_ls
          and not has_ret):
        rc = "supplemental_zero_delta"
        is_def = False
    elif not bool(re.search(r'(?m)^\s*save_upf\b', dc_tcl)):
        rc = "save_upf_missing"
        is_def = True
    else:
        rc = "unknown"
        is_def = True

    # netlist PG
    postsyn = _o_read(os.path.join(bundle, "postsyn_head.v"))
    rtl_top = _o_read(os.path.join(bundle, "rtl_top.v"))
    postsyn_pg = bool(re.search(r'\.(VDD|VSS|VDD_PM|VDDIO)\b', postsyn))
    rtl_pg = bool(re.search(r'\b(VDD|VSS|VDD_PM|VDDIO)\b', rtl_top))
    if not postsyn_pg and not rtl_pg:
        pg_rc = "dc_write_verilog_no_pg"
        pg_def = False
    elif postsyn_pg:
        pg_rc = "pg_present"
        pg_def = False
    else:
        pg_rc = "unknown"
        pg_def = False

    # latent issues
    latent = set()
    # link before load_upf (active)
    link_line = None
    load_line = None
    for i, ln in enumerate(dc_tcl.splitlines(), 1):
        s = ln.strip()
        if re.search(r'(^|\s)link\b', s) and not s.startswith("#") and link_line is None:
            link_line = i
        if re.search(r'(^|\s)load_upf\b', s) and not s.startswith("#") and load_line is None:
            load_line = i
    if (load_upf_active and link_line is not None and load_line is not None
            and link_line < load_line):
        latent.add("load_upf_order")
    if load_upf_commented and not load_upf_active:
        latent.add("load_upf_commented")
    if has_comma:
        latent.add("comma_in_set_port_attributes")
    if has_incl_scope:
        latent.add("redundant_include_scope")

    return {
        "save_upf_root_cause": rc,
        "save_upf_is_defect": is_def,
        "netlist_root_cause": pg_rc,
        "netlist_is_defect": pg_def,
        "latent": latent,
        "upf_214_zero": upf_214_zero,
        "upf_405": upf_405,
        "upf_464": upf_464,
        "upf_not_loaded": upf_not_loaded,
        "golden": golden,
        "mv_clean": mv_clean,
    }


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------

def check(deliverable, workdir):
    """deliverable: 'outputs/submit.zip' (path rel to workdir). workdir: session cwd."""
    p = os.path.join(workdir, deliverable)
    if not os.path.isfile(p):
        raise FileNotFoundError("deliverable not found: " + deliverable)

    tmp = tempfile.mkdtemp(prefix="chk_dcupf_")
    try:
        _extract(p, tmp)

        # (a) submit.zip contains diagnose_upf.py + diagnosis_A.json
        need = ["diagnose_upf.py", "diagnosis_A.json"]
        missing = [n for n in need if not os.path.isfile(os.path.join(tmp, n))]
        assert not missing, "(a) submit.zip missing: " + ", ".join(missing)

        cand = os.path.join(tmp, "diagnose_upf.py")

        # (b) py_compile candidate
        try:
            py_compile.compile(cand, doraise=True)
        except py_compile.PyCompileError as e:
            raise AssertionError("(b) py_compile failed: %s" % str(e)[:200])

        # oracle for A and B
        oA = oracle(A_DIR)
        oB = oracle(B_DIR)

        # (c) run candidate on A
        dA_path = os.path.join(tmp, "_dA.json")
        rc, out, err = _run("python3 %s %s -o %s" % (cand, A_DIR, dA_path), tmp)
        assert rc == 0 and os.path.isfile(dA_path), \
            "(c) candidate run on A failed rc=%d err=%s" % (rc, err[:200])
        with open(dA_path) as f:
            dA = json.load(f)

        sue = dA.get("save_upf_empty", {})

        # (d) dA save_upf root_cause == oracle A
        assert sue.get("root_cause") == oA["save_upf_root_cause"], \
            "(d) dA save_upf root_cause=%r, expected %r" % (
                sue.get("root_cause"), oA["save_upf_root_cause"])

        # (e) dA save_upf is_defect == oracle A
        assert sue.get("is_defect") == oA["save_upf_is_defect"], \
            "(e) dA save_upf is_defect=%r, expected %r" % (
                sue.get("is_defect"), oA["save_upf_is_defect"])

        # (f) dA save_upf evidence contains UPF-214 (0 isolation) + golden upf
        ev = " ".join(sue.get("evidence", []))
        assert ("UPF-214" in ev and "enable_golden_upf" in ev), \
            "(f) dA save_upf evidence missing UPF-214 / enable_golden_upf: %r" % ev

        # (g) dA netlist_no_pg root_cause + is_defect
        npg = dA.get("netlist_no_pg", {})
        assert npg.get("root_cause") == oA["netlist_root_cause"], \
            "(g) dA netlist root_cause=%r, expected %r" % (
                npg.get("root_cause"), oA["netlist_root_cause"])
        assert npg.get("is_defect") == oA["netlist_is_defect"], \
            "(g) dA netlist is_defect=%r, expected %r" % (
                npg.get("is_defect"), oA["netlist_is_defect"])

        # (h) dA latent_issues contains the 3 expected ids
        lat_ids = {x.get("id") for x in dA.get("latent_issues", [])}
        expected_lat = {"load_upf_order", "comma_in_set_port_attributes",
                        "redundant_include_scope"}
        missing_lat = expected_lat - lat_ids
        assert not missing_lat, \
            "(h) dA latent_issues missing: %s (got %s)" % (missing_lat, lat_ids)

        # (i) dA save_upf fix mentions dropping -supplemental (semantic)
        fix_txt = " ".join(sue.get("fix", []))
        assert ("-supplemental" in fix_txt), \
            "(i) dA save_upf fix does not mention -supplemental: %r" % fix_txt

        # (j) run candidate on B
        dB_path = os.path.join(tmp, "_dB.json")
        rc, out, err = _run("python3 %s %s -o %s" % (cand, B_DIR, dB_path), tmp)
        assert rc == 0 and os.path.isfile(dB_path), \
            "(j) candidate run on B failed rc=%d err=%s" % (rc, err[:200])
        with open(dB_path) as f:
            dB = json.load(f)

        sueB = dB.get("save_upf_empty", {})

        # (k) cross-input guard: dB root_cause == upf_not_loaded
        assert sueB.get("root_cause") == "upf_not_loaded", \
            "(k) cross-input guard: dB save_upf root_cause=%r, expected " \
            "'upf_not_loaded'" % sueB.get("root_cause")

        # (l) cross-input guard: dB latent_issues does NOT contain comma bug
        latB_ids = {x.get("id") for x in dB.get("latent_issues", [])}
        assert "comma_in_set_port_attributes" not in latB_ids, \
            "(l) cross-input guard: dB latent_issues contains comma bug " \
            "(B uses spaces) -> %s" % latB_ids

        # (m) anti-hardcode: candidate source does NOT contain A's design name
        with open(cand, "r", encoding="utf-8", errors="replace") as f:
            cand_src = f.read()
        assert "hl22_porting_test_chip_v1" not in cand_src, \
            "(m) anti-hardcode: candidate contains literal A design name " \
            "'hl22_porting_test_chip_v1'"

        # (n) dA vs dB save_upf root_cause differ
        assert sue.get("root_cause") != sueB.get("root_cause"), \
            "(n) dA and dB save_upf root_cause are the same (%r) -- " \
            "candidate did not distinguish A vs B" % sue.get("root_cause")

        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    # CLI: check.py <deliverable> <workdir>
    if len(sys.argv) >= 3:
        try:
            check(sys.argv[1], sys.argv[2])
            print("CHECK PASS")
            sys.exit(0)
        except AssertionError as e:
            print("CHECK FAIL: " + str(e))
            sys.exit(1)
    else:
        print("usage: check.py <deliverable> <workdir>")
        sys.exit(2)
'''

NEG_SELFTEST = r'''#!/usr/bin/env python3
"""negative_selftest.py -- all 5 negatives MUST FAIL check()."""
import os, sys, shutil, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check

NEG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "negative")
WORK = tempfile.mkdtemp(prefix="negself_dcupf_")

negs = ["fake_empty.zip", "fake_print_expected.zip", "fake_core_deleted.zip",
        "naive_hardcode_a.zip", "naive_no_log_parse.zip"]
results = {}
try:
    for n in negs:
        src = os.path.join(NEG_DIR, n)
        deliverable_dir = os.path.join(WORK, n.replace(".zip", ""))
        os.makedirs(deliverable_dir, exist_ok=True)
        shutil.copy(src, os.path.join(deliverable_dir, "submit.zip"))
        try:
            check.check("submit.zip", deliverable_dir)
            results[n] = "PASS  <-- BAD (negative should FAIL)"
        except Exception as e:
            results[n] = "FAIL  <-- GOOD (%s)" % str(e)[:120]
finally:
    shutil.rmtree(WORK, ignore_errors=True)

bad = [n for n, r in results.items() if r.startswith("PASS")]
for n, r in results.items():
    print("%-32s %s" % (n, r))
if bad:
    print("\nNEG_SELFTEST FAILED: %d negative(s) passed check (should all FAIL)" % len(bad))
    sys.exit(1)
print("\nNEG_SELFTEST OK: all 5 negatives FAIL as expected")
sys.exit(0)
'''

# ===========================================================================
# Build
# ===========================================================================

def _w(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build_bundles():
    # A bundle
    _w(os.path.join(A_DIR, "dc.tcl"), A_DC_TCL)
    _w(os.path.join(A_DIR, "test_chip_power.upf"), A_UPF)
    _w(os.path.join(A_DIR, "sim.upf"), A_SIM_UPF)
    _w(os.path.join(A_DIR, "dc_setup_filenames.tcl"), A_SETUP_TCL)
    _w(os.path.join(A_DIR, "dc.log"), A_DC_LOG)
    _w(os.path.join(A_DIR, "snps_upf.log"), A_SNPS_UPF_LOG)
    _w(os.path.join(A_DIR, "dc.upf"), A_DC_UPF)
    _w(os.path.join(A_DIR, "postsyn_head.v"), A_POSTSYN_HEAD)
    _w(os.path.join(A_DIR, "rtl_top.v"), A_RTL_TOP)
    # B bundle (hidden)
    _w(os.path.join(B_DIR, "dc.tcl"), B_DC_TCL)
    _w(os.path.join(B_DIR, "test_chip_power.upf"), B_UPF)
    _w(os.path.join(B_DIR, "dc_setup_filenames.tcl"), B_SETUP_TCL)
    _w(os.path.join(B_DIR, "dc.log"), B_DC_LOG)
    _w(os.path.join(B_DIR, "snps_upf.log"), B_SNPS_UPF_LOG)
    _w(os.path.join(B_DIR, "dc.upf"), B_DC_UPF)
    _w(os.path.join(B_DIR, "postsyn_head.v"), B_POSTSYN_HEAD)
    _w(os.path.join(B_DIR, "rtl_top.v"), B_RTL_TOP)


def build_reference():
    _w(os.path.join(REF_DIR, "diagnose_upf.py"), DIAGNOSE_UPF_PY)
    # produce diagnosis_A.json by running the reference
    dA_path = os.path.join(REF_DIR, "diagnosis_A.json")
    r = subprocess.run(["python3", os.path.join(REF_DIR, "diagnose_upf.py"),
                        A_DIR, "-o", dA_path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("ERR producing diagnosis_A.json:", r.stderr)
        sys.exit(1)
    # reference_submit.zip
    zip_path = os.path.join(REF_DIR, "reference_submit.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(REF_DIR, "diagnose_upf.py"), "diagnose_upf.py")
        z.write(dA_path, "diagnosis_A.json")
    # check.py
    _w(os.path.join(REF_DIR, "check.py"), CHECK_PY)
    # negative_selftest.py
    _w(os.path.join(REF_DIR, "negative_selftest.py"), NEG_SELFTEST)


def build_negatives():
    """5 negative submit.zip files, all must FAIL check()."""
    neg_dir = os.path.join(REF_DIR, "negative")
    os.makedirs(neg_dir, exist_ok=True)

    def _zip(name, files):
        zpath = os.path.join(neg_dir, name)
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for fn, content in files.items():
                z.writestr(fn, content)

    # 1. fake_empty: empty diagnose_upf.py + empty diagnosis_A.json
    _zip("fake_empty.zip", {
        "diagnose_upf.py": "# empty stub\n",
        "diagnosis_A.json": "{}\n",
    })

    # 2. fake_print_expected: prints hardcoded A diagnosis, reads nothing.
    #    Fails on B (k): B run yields A's root_cause.
    _zip("fake_print_expected.zip", {
        "diagnosis_A.json": "{}\n",
        "diagnose_upf.py": (
            "import sys, json\n"
            "def _diag(bundle):\n"
            "    return {'save_upf_empty': {'root_cause':'supplemental_zero_delta',"
            " 'is_defect': False, 'evidence':['UPF-214 0 isolation','enable_golden_upf true'],"
            " 'fix':['Drop -supplemental'], 'mechanism':'x'},\n"
            "     'netlist_no_pg': {'root_cause':'dc_write_verilog_no_pg','is_defect':False,'evidence':[],'mechanism':'x'},\n"
            "     'latent_issues': [{'id':'load_upf_order','severity':'warn','desc':'x','fix':'x'},\n"
            "                       {'id':'comma_in_set_port_attributes','severity':'bug','desc':'x','fix':'x'},\n"
            "                       {'id':'redundant_include_scope','severity':'info','desc':'x','fix':'x'}]}\n"
            "if __name__=='__main__':\n"
            "    import argparse\n"
            "    ap=argparse.ArgumentParser(); ap.add_argument('bundle_root'); ap.add_argument('-o','--output',default=None)\n"
            "    a=ap.parse_args()\n"
            "    d=_diag(a.bundle_root)\n"
            "    out=json.dumps(d,indent=2)\n"
            "    if a.output: open(a.output,'w').write(out)\n"
            "    else: sys.stdout.write(out+'\\n')\n"
        ),
    })

    # 3. fake_core_deleted: parse logic removed -> bad root_cause / missing latent
    _zip("fake_core_deleted.zip", {
        "diagnosis_A.json": "{}\n",
        "diagnose_upf.py": (
            "import sys, json, argparse\n"
            "def diagnose(b):\n"
            "    # core logic deleted -- always returns unknown\n"
            "    return {'save_upf_empty': {'root_cause':'unknown','is_defect':True,'evidence':[],'fix':[],'mechanism':'x'},\n"
            "     'netlist_no_pg': {'root_cause':'unknown','is_defect':False,'evidence':[],'mechanism':'x'},\n"
            "     'latent_issues': []}\n"
            "if __name__=='__main__':\n"
            "    ap=argparse.ArgumentParser(); ap.add_argument('bundle_root'); ap.add_argument('-o','--output',default=None)\n"
            "    a=ap.parse_args(); d=diagnose(a.bundle_root); out=json.dumps(d,indent=2)\n"
            "    if a.output: open(a.output,'w').write(out)\n"
            "    else: sys.stdout.write(out+'\\n')\n"
        ),
    })

    # 4. naive_hardcode_a: hardcodes A's design name + A root_cause.
    #    Fails (k) B gets A's root_cause, and (m) contains literal design name.
    _zip("naive_hardcode_a.zip", {
        "diagnosis_A.json": "{}\n",
        "diagnose_upf.py": (
            "import sys, json, argparse\n"
            "# hardcoded for hl22_porting_test_chip_v1 only\n"
            "DESIGN='hl22_porting_test_chip_v1'\n"
            "def diagnose(b):\n"
            "    return {'save_upf_empty': {'root_cause':'supplemental_zero_delta','is_defect':False,'evidence':['UPF-214 0 isolation','enable_golden_upf true'],'fix':['Drop -supplemental'],'mechanism':'x'},\n"
            "     'netlist_no_pg': {'root_cause':'dc_write_verilog_no_pg','is_defect':False,'evidence':[],'mechanism':'x'},\n"
            "     'latent_issues': [{'id':'load_upf_order','severity':'warn','desc':'x','fix':'x'},\n"
            "                       {'id':'comma_in_set_port_attributes','severity':'bug','desc':'x','fix':'x'},\n"
            "                       {'id':'redundant_include_scope','severity':'info','desc':'x','fix':'x'}]}\n"
            "if __name__=='__main__':\n"
            "    ap=argparse.ArgumentParser(); ap.add_argument('bundle_root'); ap.add_argument('-o','--output',default=None)\n"
            "    a=ap.parse_args(); d=diagnose(a.bundle_root); out=json.dumps(d,indent=2)\n"
            "    if a.output: open(a.output,'w').write(out)\n"
            "    else: sys.stdout.write(out+'\\n')\n"
        ),
    })

    # 5. naive_no_log_parse: does not parse dc.log -> evidence lacks UPF-214 (f)
    _zip("naive_no_log_parse.zip", {
        "diagnosis_A.json": "{}\n",
        "diagnose_upf.py": (
            "import sys, json, os, re, glob, argparse\n"
            "def _read(p):\n"
            "    try: return open(p,encoding='utf-8',errors='replace').read()\n"
            "    except: return ''\n"
            "def diagnose(b):\n"
            "    dc=_read(os.path.join(b,'dc.tcl'))\n"
            "    upf=_read(os.path.join(b,'test_chip_power.upf'))\n"
            "    # NO dc.log parse -- evidence lacks UPF-214\n"
            "    sup=bool(re.search(r'(?m)^\\s*save_upf\\b.*-supplemental',dc))\n"
            "    golden=bool(re.search(r'enable_golden_upf.*true',dc,re.I))\n"
            "    has_iso=bool(re.search(r'\\bset_isolation\\b',upf))\n"
            "    if sup and golden and not has_iso:\n"
            "        rc='supplemental_zero_delta'; idef=False\n"
            "    else:\n"
            "        rc='unknown'; idef=True\n"
            "    return {'save_upf_empty': {'root_cause':rc,'is_defect':idef,'evidence':['enable_golden_upf true'],'fix':['Drop -supplemental'],'mechanism':'x'},\n"
            "     'netlist_no_pg': {'root_cause':'dc_write_verilog_no_pg','is_defect':False,'evidence':[],'mechanism':'x'},\n"
            "     'latent_issues': [{'id':'load_upf_order','severity':'warn','desc':'x','fix':'x'},\n"
            "                       {'id':'comma_in_set_port_attributes','severity':'bug','desc':'x','fix':'x'},\n"
            "                       {'id':'redundant_include_scope','severity':'info','desc':'x','fix':'x'}]}\n"
            "if __name__=='__main__':\n"
            "    ap=argparse.ArgumentParser(); ap.add_argument('bundle_root'); ap.add_argument('-o','--output',default=None)\n"
            "    a=ap.parse_args(); d=diagnose(a.bundle_root); out=json.dumps(d,indent=2)\n"
            "    if a.output: open(a.output,'w').write(out)\n"
            "    else: sys.stdout.write(out+'\\n')\n"
        ),
    })


def selfverify():
    """Run reference + negatives + 3-fake regression."""
    print("== reference self-verify ==")
    work = tempfile.mkdtemp(prefix="sv_dcupf_")
    try:
        # place reference_submit.zip as deliverable
        ddir = os.path.join(work, "d")
        os.makedirs(ddir, exist_ok=True)
        shutil.copy(os.path.join(REF_DIR, "reference_submit.zip"),
                    os.path.join(ddir, "submit.zip"))
        sys.path.insert(0, REF_DIR)
        import importlib
        if "check" in sys.modules:
            del sys.modules["check"]
        import check
        try:
            check.check("submit.zip", ddir)
            print("REF: PASS 14/14 (a-n)")
        except AssertionError as e:
            print("REF: FAIL -> " + str(e))
            sys.exit(1)
        # negatives
        neg_dir = os.path.join(REF_DIR, "negative")
        negs = ["fake_empty.zip", "fake_print_expected.zip",
                "fake_core_deleted.zip", "naive_hardcode_a.zip",
                "naive_no_log_parse.zip"]
        nfail = 0
        for n in negs:
            ndir = os.path.join(work, "neg_" + n.replace(".zip", ""))
            os.makedirs(ndir, exist_ok=True)
            shutil.copy(os.path.join(neg_dir, n), os.path.join(ndir, "submit.zip"))
            try:
                check.check("submit.zip", ndir)
                print("NEG %-28s PASS  <-- BAD" % n)
                nfail += 1
            except Exception as e:
                print("NEG %-28s FAIL  <-- GOOD (%s)" % (n, str(e)[:90]))
        if nfail:
            print("NEG_RC=%d (should be 0)" % nfail)
            sys.exit(1)
        print("NEG_RC=0  all 5 negatives FAIL as expected")
        # 3-fake regression (subset of negatives):
        #   (a) empty shell = fake_empty
        #   (b) only-print-expected = fake_print_expected
        #   (c) core-deleted = fake_core_deleted
        # all already verified FAIL above
        print("3-fake (a/b/c) all FAIL  OK")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    print("building bundles...")
    build_bundles()
    print("building reference + check + negatives...")
    build_reference()
    build_negatives()
    print("self-verify...")
    selfverify()
    print("BUILD OK:", CID)
