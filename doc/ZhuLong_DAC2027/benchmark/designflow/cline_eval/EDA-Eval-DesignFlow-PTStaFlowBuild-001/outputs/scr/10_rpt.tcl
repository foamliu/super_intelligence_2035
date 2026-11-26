#===============================================================================
# FILE    : 10_rpt.tcl
# PURPOSE : Final STA reports: quality-of-results, timing, constraints, area and
#           power summary, all written into the rpt/ directory.
#===============================================================================
puts "RM-Info: [info script] : final reports"

set qor_rpt_file     [file join $RPT_DIR "${REPORT_TAG}.qor.rpt"]
set timing_rpt_file  [file join $RPT_DIR "${REPORT_TAG}.timing.rpt"]
set viol_rpt_file    [file join $RPT_DIR "${REPORT_TAG}.violators.rpt"]
set area_rpt_file    [file join $RPT_DIR "${REPORT_TAG}.area.rpt"]
set power_rpt_file   [file join $RPT_DIR "${REPORT_TAG}.power.rpt"]

# Quality-of-results summary (WNS/TNS per clock group).
report_qor -summary > $qor_rpt_file

# Worst violating paths, short summary.
report_timing -delay_type max -max_paths 50 -path_type end \
    > $viol_rpt_file

# Full timing snapshot appended (mirrors step 8).
report_timing -delay_type max -max_paths 200 -nworst 5 \
    -path_type full_clock_expanded \
    > $timing_rpt_file

# Area report.
report_area -hierarchy > $area_rpt_file

# Power report (average power).
if {[info exists PT_POWER_ANALYSIS]} {
    report_power -hierarchy > $power_rpt_file
} else {
    # Power is optional; still attempt it but do not fail the flow.
    if {[catch {report_power -hierarchy} power_rc]} {
        puts "RM-Warning: report_power skipped: $power_rc"
    } else {
        report_power -hierarchy > $power_rpt_file
    }
}

puts "RM-Info: reports written under $RPT_DIR"
puts "RM-Info: [info script] completed"