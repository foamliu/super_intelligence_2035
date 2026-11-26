#===============================================================================
# FILE    : sta_main.tcl
# PURPOSE : PrimeTime STA flow master script.
#           Sources the numbered step scripts (1_setup.tcl .. 10_rpt.tcl) in
#           the order they are listed, so each step is read in numeric order as
#           requested. Invoked by run/run_sta.csh through pt_shell.
#===============================================================================

#---- global defaults (overridden by the -x assignments from run_sta.csh) ------
if {![info exists ROOT_DIR]}    { set ROOT_DIR    [file normalize [file dirname [pwd]]] }
if {![info exists RUN_DIR]}     { set RUN_DIR     [file join $ROOT_DIR run] }
if {![info exists SCR_DIR]}     { set SCR_DIR     [file join $ROOT_DIR scr] }
if {![info exists LOG_DIR]}     { set LOG_DIR     [file join $ROOT_DIR log] }
if {![info exists RPT_DIR]}     { set RPT_DIR     [file join $ROOT_DIR rpt] }
if {![info exists SDC_DIR]}     { set SDC_DIR     [file join $ROOT_DIR sdc] }
if {![info exists SES_DIR]}     { set SES_DIR     [file join $ROOT_DIR session] }
if {![info exists DESIGN_NAME]} { set DESIGN_NAME "design" }
if {![info exists PT_CORNER]}   { set PT_CORNER   "tt0p8v25c" }
if {![info exists PT_MODE]}     { set PT_MODE     "func" }

file mkdir $LOG_DIR $RPT_DIR $SDC_DIR $SES_DIR

puts "=================================================================="
puts " PrimeTime STA Flow : sta_main.tcl"
puts " design             : $DESIGN_NAME"
puts " corner             : $PT_CORNER"
puts " mode               : $PT_MODE"
puts "=================================================================="

# Continue on error so a single failing report does not abort the whole flow;
# the log/reports still get written and can be inspected.
set sh_continue_on_error true
set sh_command_log_file [file join $LOG_DIR "sta_commands_${DESIGN_NAME}_${PT_CORNER}_${PT_MODE}.log"]

# Numbered step scripts, sourced strictly in read (numeric) order.
set STEP_SCRIPTS [list \
    1_setup.tcl          \
    2_read_constraint.tcl \
    3_read_library.tcl    \
    4_read_netlist.tcl    \
    5_link_design.tcl     \
    6_timing_config.tcl   \
    7_update_timing.tcl   \
    8_report_timing.tcl   \
    9_write_output.tcl    \
    10_rpt.tcl            \
]

foreach step $STEP_SCRIPTS {
    set step_file [file join $SCR_DIR $step]
    puts "RM-Info: ================= source $step ================="
    if {[file exists $step_file]} {
        source $step_file
    } else {
        puts "RM-Error: missing step script $step_file"
    }
}

puts "RM-Info: sta_main.tcl finished for design $DESIGN_NAME (corner=$PT_CORNER, mode=$PT_MODE)"