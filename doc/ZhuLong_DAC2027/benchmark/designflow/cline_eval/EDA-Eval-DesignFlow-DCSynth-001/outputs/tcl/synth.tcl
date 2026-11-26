# ============================================================================
# Design Compiler (dc_shell) top-down synthesis script
# ----------------------------------------------------------------------------
# Design     : addr_to_rowcol_region  (RAM address -> row / col / region decode)
# Library    : stdcells_ac_FF_1p3_m40c.db   (FF 1.3 V -40 C local std cells)
# Flow       : read RTL -> link -> apply SDC -> compile -> report -> write
# Hierarchy  : PRESERVED (no ungroup / no flatten / no autoungroup)
# ============================================================================

# ----------------------------------------------------------------------------
# 0. User parameters / generics  (edit ONLY this block)
# ----------------------------------------------------------------------------
set TOP_DESIGN    "addr_to_rowcol_region"
set RTL_DIR       "../rtl"
set LIB_DIR       "../lib"
set LIB_NAME      "stdcells_ac_FF_1p3_m40c"
set RTL_FILES     [list "${RTL_DIR}/addr_to_rowcol_region.v"]
set SDC_FILE      "../constraints/addr_to_rowcol_region.sdc"

set CLK_PERIOD    2.0     ;# ns  : virtual-clock period budgeting the datapath
set INPUT_DELAY   0.5     ;# ns
set OUTPUT_DELAY  0.5     ;# ns
set OUTPUT_LOAD   0.05    ;# pF

set REPORT_DIR    "../reports"
set NETLIST_DIR   "../netlist"

# ----------------------------------------------------------------------------
# 1. Library setup
# ----------------------------------------------------------------------------
set search_path    [concat $search_path $RTL_DIR $LIB_DIR]
set target_library "${LIB_NAME}.db"
set link_library   "* ${LIB_NAME}.db"

# ----------------------------------------------------------------------------
# 2. Read and elaborate the RTL (top-down, original hierarchy intact)
# ----------------------------------------------------------------------------
foreach f $RTL_FILES { analyze -format verilog $f }
elaborate $TOP_DESIGN
current_design $TOP_DESIGN
link
uniquify

# ----------------------------------------------------------------------------
# 3. Read timing / physical constraints (SDC)
# ----------------------------------------------------------------------------
source $SDC_FILE

# ----------------------------------------------------------------------------
# 4. Compile (optimize) while KEEPING the design hierarchy
# ----------------------------------------------------------------------------
# Disable all automatic ungrouping / boundary optimization so that the
# elaborated module hierarchy (addr_region_decode, addr_region0/1/2/3_calc,
# addr_rowcol_mux) is preserved in the final netlist.
set auto_ungroup false
compile_ultra -no_autoungroup
# Legacy fallback:   compile -map_effort high -area_effort high

# ----------------------------------------------------------------------------
# 5. Reports
# ----------------------------------------------------------------------------
file mkdir $REPORT_DIR
report_qor                       > ${REPORT_DIR}/qor.rpt
report_area                      > ${REPORT_DIR}/area.rpt
report_timing                    > ${REPORT_DIR}/timing.rpt
report_power                     > ${REPORT_DIR}/power.rpt
report_constraint -all_violators > ${REPORT_DIR}/constraints.rpt
report_reference                 > ${REPORT_DIR}/reference.rpt

# ----------------------------------------------------------------------------
# 6. Write outputs  (netlist keeps hierarchy via -hierarchy)
# ----------------------------------------------------------------------------
file mkdir $NETLIST_DIR
write -format verilog -hierarchy -output ${NETLIST_DIR}/${TOP_DESIGN}_syn.v
write_sdc                              ${NETLIST_DIR}/${TOP_DESIGN}_syn.sdc
write_sdf -version 2.1                 ${NETLIST_DIR}/${TOP_DESIGN}_syn.sdf

puts "INFO: synthesis of ${TOP_DESIGN} finished (hierarchy preserved)."
exit