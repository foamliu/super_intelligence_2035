#===============================================================================
# FILE    : 8_report_timing.tcl
# PURPOSE : Timing reports (setup/hold) for the current corner/mode.
#===============================================================================
puts "RM-Info: [info script] : reporting timing"

set timing_rpt_file [file join $RPT_DIR "${REPORT_TAG}.timing.rpt"]
set timing_paths_txt [file join $RPT_DIR "${REPORT_TAG}.paths.rpt"]

# Setup (max delay) report: top N violating / near-violating paths.
report_timing \
    -delay_type  max \
    -max_paths   200 \
    -nworst      5 \
    -path_type   full_clock_expanded \
    -slack_lesser_than 0.0 \
    > $timing_rpt_file

# Hold (min delay) report: top N violating / near-violating paths.
report_timing \
    -delay_type  min \
    -max_paths   200 \
    -nworst      5 \
    -path_type   full_clock_expanded \
    -slack_lesser_than 0.0 \
    >> $timing_rpt_file

# One-line summary of the most critical endpoints.
report_timing \
    -delay_type max \
    -max_paths  20 \
    -path_type  end \
    > $timing_paths_txt

puts "RM-Info: timing report written to $timing_rpt_file"
puts "RM-Info: [info script] completed"