#===============================================================================
# FILE    : 1_setup.tcl
# PURPOSE : Environment configuration & tool selection (step 1 of the STA flow).
#   * resolve the project directory hierarchy (run/ scr/ log/ rpt/ sdc/ session/ data/)
#   * select the PrimeTime tool and corner-aware analysis libraries
#   * enable the key STA features (CCS waveform propagation, POCV)
#   All variables are overridable via the -x assignments emitted by run_sta.csh.
#===============================================================================
puts "RM-Info: [info script] : environment configuration & tool selection"

#---- directories -------------------------------------------------------------
if {![info exists ROOT_DIR]} { set ROOT_DIR  [file normalize [file dirname [pwd]]] }
set RUN_DIR  [file join $ROOT_DIR run]
set SCR_DIR  [file join $ROOT_DIR scr]
set LOG_DIR  [file join $ROOT_DIR log]
set RPT_DIR  [file join $ROOT_DIR rpt]
set SDC_DIR  [file join $ROOT_DIR sdc]
set SES_DIR  [file join $ROOT_DIR session]
set DATA_DIR [file join $ROOT_DIR data]

foreach d [list $LOG_DIR $RPT_DIR $SDC_DIR $SES_DIR] {
    file mkdir $d
}

#---- design / corner / mode ----------------------------------------------------
if {![info exists DESIGN_NAME]} { set DESIGN_NAME "design" }
if {![info exists PT_CORNER]}   { set PT_CORNER   "tt0p8v25c" }
if {![info exists PT_MODE]}     { set PT_MODE     "func" }

puts "RM-Info: DESIGN_NAME = $DESIGN_NAME"
puts "RM-Info: PT_CORNER   = $PT_CORNER"
puts "RM-Info: PT_MODE     = $PT_MODE"

#---- tool selection (PrimeTime) -------------------------------------------------
# PrimeTime lives under /apps/synopsys/primetime and is exposed through the
# environment module 'pt/...' loaded by run/run_sta.csh. This variable is kept
# available so the shell binary can be located explicitly if it is not on PATH.
if {![info exists PT_TOOL_DIR]} { set PT_TOOL_DIR "/apps/synopsys/primetime" }
puts "RM-Info: PT_TOOL_DIR = $PT_TOOL_DIR"

#---- corner-aware library configuration -----------------------------------------
# The demo input netlist / libraries / SDC are expected under DATA_DIR. Corner
# specific Liberty databases live in data/lib/<corner>/.
set LIB_BASE [file join $DATA_DIR "lib" $PT_CORNER]

if {![info exists ADDITIONAL_SEARCH_PATH]} { set ADDITIONAL_SEARCH_PATH "" }
set search_path [concat . $DATA_DIR $LIB_BASE $ADDITIONAL_SEARCH_PATH]

if {![info exists ANALYSIS_LIBRARY_FILES]} {
    set ANALYSIS_LIBRARY_FILES [concat \
        [glob -nocomplain [file join $LIB_BASE "*.db"]] \
        [glob -nocomplain [file join $LIB_BASE "*.lib"]] ]
}
if {![info exists ADDITIONAL_LINK_LIB_FILES]} {
    set ADDITIONAL_LINK_LIB_FILES $ANALYSIS_LIBRARY_FILES
}

# target_library : cells used for mapping/delay calc of the cell library
# link_library   : everything needed to resolve the design references
set target_library $ANALYSIS_LIBRARY_FILES
set link_path      [concat {*} $target_library $ADDITIONAL_LINK_LIB_FILES]

puts "RM-Info: target_library = $target_library"
puts "RM-Info: link_path      = $link_path"

#---- enable key features ----------------------------------------------------------
set sh_continue_on_error                true
set delay_calc_waveform_analysis_mode   full_design   ;# CCS-based waveform propagation
set timing_pocvm_enable_analysis        true          ;# POCV (LVF) statistical timing
set si_enable_analysis                  true          ;# crosstalk analysis

#---- common report tag -------------------------------------------------------------
set REPORT_TAG "${DESIGN_NAME}_${PT_CORNER}_${PT_MODE}"
set REPORT_PREFIX [file join $RPT_DIR $REPORT_TAG]

puts "RM-Info: [info script] completed"