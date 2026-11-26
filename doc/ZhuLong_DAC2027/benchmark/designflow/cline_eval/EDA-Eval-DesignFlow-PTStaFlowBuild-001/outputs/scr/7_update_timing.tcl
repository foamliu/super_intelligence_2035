#===============================================================================
# FILE    : 7_update_timing.tcl
# PURPOSE : Update (propagate) timing for the configured corner/mode and run
#           quick timing sanity / constraint checks.
#===============================================================================
puts "RM-Info: [info script] : updating timing"

update_timing -full

# Quick sanity checks on the timing environment.
check_timing -verbose

# Report all timing violations (one line per path) into the report directory.
report_constraint -all_violators \
    > [file join $RPT_DIR "${REPORT_TAG}.constraint.rpt"]

# Also dump the annotated timing to the command log for traceability.
echo "RM-Info: timing updated for ${DESIGN_NAME} (${PT_CORNER}/${PT_MODE})"

puts "RM-Info: [info script] completed"