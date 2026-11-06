#===============================================================================
# FILE    : 5_link_design.tcl
# PURPOSE : Link the gate-level design against the read libraries and validate it.
#===============================================================================
puts "RM-Info: [info script] : linking design"

if {![info exists DESIGN_NAME]} { set DESIGN_NAME "design" }

# Enable library auto-detect so the design name can be resolved from the netlist
# if DESIGN_NAME is left generic, then link explicitly.
set link_disable_auto_detect true
link_design $DESIGN_NAME
current_design $DESIGN_NAME

# Basic design sanity checks. Any unresolved reference is reported by
# report_reference (typically caused by a missing submodule library, see
# 3_read_library.tcl).
check_design
report_reference > [file join $RPT_DIR "${REPORT_TAG}.reference.rpt"]

puts "RM-Info: [info script] completed"