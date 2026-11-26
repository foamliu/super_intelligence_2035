###############################################################################
#  wlm_multibit.tcl
#  ----------------------------------------------------------------------------
#  Design Compiler (dc_shell) synthesis script.
#
#  Theme : Enable MULTI-BIT (multi-bit) cell inference / optimization in
#          WIRE-LOAD-MODEL (WLM) mode WITHOUT a physical library.
#
#            * "No physical library"  -> non-topographical flow: no Milkyway,
#              no TLU+, no floorplan. Wire delay is estimated by WLM.
#            * "Multi-bit"            -> multi-bit register cells are inferred
#              and used by compile.
#
#  Reusable : this script `source`s common_setup.tcl to obtain the project
#             variables listed in section 0 below.
###############################################################################

# ----------------------------------------------------------------------------
# 0. Project variables provided by assets/common_setup.tcl
#      $DESIGN_NAME, $MB_LIB_PREFIX, $MB_CELL_PATTERN,
#      $OPT_MODE, $CRITICAL_RANGE, $REPORTS_DIR
# ----------------------------------------------------------------------------
source common_setup.tcl

# ----------------------------------------------------------------------------
# 1. Logical library setup (WLM mode uses logical .db libraries only,
#    i.e. there is NO physical / Milkyway library referenced here).
# ----------------------------------------------------------------------------
# Directory that holds the .db library files (adjust to the project layout).
set LIB_DIR "./db"

# The base (single-bit) standard-cell library is the multi-bit library name
# with the "_MB" token removed, e.g.
#   DBCP51H180L6W25T5_MB_SVT  ->  DBCP51H180L6W25T5_SVT
set MB_LIB_NAME   ${MB_LIB_PREFIX}
set BASE_LIB_NAME [string map {"_MB" ""} ${MB_LIB_PREFIX}]

lappend search_path ${LIB_DIR}
set target_library    "${BASE_LIB_NAME}.db ${MB_LIB_NAME}.db"
set link_library      "* ${target_library}"
set synthetic_library [list dw_foundation.sldb]

# ----------------------------------------------------------------------------
# 2. Wire-load-model (WLM) setup -- the "no physical library" mode.
#    In a non-topographical flow there is no placement information, so wire
#    delay is modelled with wire-load tables instead of an RC extraction.
# ----------------------------------------------------------------------------
set auto_wire_load_selection true
set_wire_load_mode top

# ----------------------------------------------------------------------------
# 3. Read, link and constrain the design
# ----------------------------------------------------------------------------
read_file -format verilog ${DESIGN_NAME}.v
current_design ${DESIGN_NAME}
link
uniquify

if {[file exists ${DESIGN_NAME}.sdc]} {
    read_sdc ${DESIGN_NAME}.sdc
}

# ----------------------------------------------------------------------------
# 4. Enable MULTI-BIT optimization (WLM / non-topographical mode)
# ----------------------------------------------------------------------------
# 4.1 Sanity-check the multi-bit library cells using $MB_LIB_PREFIX and
#     $MB_CELL_PATTERN. `string match` honours the '[...]' character-class of
#     the pattern (MB[24]SDF* == MB2SDF* or MB4SDF*).
if {[sizeof_collection [get_libs -quiet ${MB_LIB_NAME}]] > 0} {
    set mb_hits {}
    foreach_in_collection mc [get_lib_cells -quiet "${MB_LIB_NAME}/*"] {
        set mc_name [get_object_name ${mc}]
        set mc_base [lindex [split ${mc_name} /] end]
        if {[string match ${MB_CELL_PATTERN} ${mc_base}]} {
            lappend mb_hits ${mc_name}
        }
    }
    if {[llength ${mb_hits}] == 0} {
        puts "ERROR: no multi-bit cells match '${MB_CELL_PATTERN}' in library ${MB_LIB_NAME}"
    } else {
        puts "INFO : [llength ${mb_hits}] multi-bit cells (pattern '${MB_CELL_PATTERN}') -> ${mb_hits}"
    }
} else {
    puts "WARNING: multi-bit library '${MB_LIB_NAME}' is not loaded; skipping cell scan."
}

# 4.2 Infer multi-bit components from bused HDL registers.
set hdlin_infer_multibit default_all

# 4.3 Prefer single-bit flops that have a multi-bit equivalent -> better
#     multi-bit packing ratio.
set seqmap_prefer_registers_with_multibit_equivalent true

# 4.4 Multi-bit optimization mode and critical range.
#     multibit_mode: non_timing_driven | timing_driven | timing_only | none
set_multibit_options -mode ${OPT_MODE}
set_multibit_options -critical_range ${CRITICAL_RANGE}

# ----------------------------------------------------------------------------
# 5. Synthesize
# ----------------------------------------------------------------------------
compile_ultra

# ----------------------------------------------------------------------------
# 6. Reports (written to $REPORTS_DIR)
# ----------------------------------------------------------------------------
file mkdir ${REPORTS_DIR}
report_compile_options > ${REPORTS_DIR}/${DESIGN_NAME}.compile_options.rpt
report_multibit        > ${REPORTS_DIR}/${DESIGN_NAME}.multibit.rpt
report_qor             > ${REPORTS_DIR}/${DESIGN_NAME}.qor.rpt
report_timing          > ${REPORTS_DIR}/${DESIGN_NAME}.timing.rpt
report_area -hierarchy > ${REPORTS_DIR}/${DESIGN_NAME}.area.rpt
report_power           > ${REPORTS_DIR}/${DESIGN_NAME}.power.rpt
check_design           > ${REPORTS_DIR}/${DESIGN_NAME}.check_design.rpt

# ----------------------------------------------------------------------------
# 7. Write out the optimized netlist
# ----------------------------------------------------------------------------
write -format verilog -hierarchy -output ${REPORTS_DIR}/${DESIGN_NAME}.multibit.vg
write -format ddc     -hierarchy -output ${REPORTS_DIR}/${DESIGN_NAME}.ddc

puts "== WLM multi-bit synthesis done for ${DESIGN_NAME} =="