#===============================================================================
# FILE    : 6_timing_config.tcl
# PURPOSE : Timing analysis configuration: operating conditions, derating,
#           clock margins, path groups and analysis options for the corner/mode.
#===============================================================================
puts "RM-Info: [info script] : timing analysis configuration"

# Operating condition: derive the PVT/RC corner operating condition from the
# target library (single analysis). Switch to multi-corner via set_operating_conditions
# when MCMM runs are launched through the -corners sweep in run_sta.csh.
if {[info exists OPERATING_CONDITION]} {
    set_operating_conditions $OPERATING_CONDITION
} else {
    set_operating_conditions -analysis_type on_chip_variation
}

# On-chip variation derates (placeholder values; adjust per signoff methodology).
if {![info exists OCV_DERATE_EARLY]} { set OCV_DERATE_EARLY 0.90 }
if {![info exists OCV_DERATE_LATE]}  { set OCV_DERATE_LATE  1.10 }

set_timing_derate -early $OCV_DERATE_EARLY
set_timing_derate -late  $OCV_DERATE_LATE

# Clock uncertainty for setup/hold (default margin).
if {![info exists CLK_UNCERTAINTY_SETUP]} { set CLK_UNCERTAINTY_SETUP 0.050 }
if {![info exists CLK_UNCERTAINTY_HOLD]}  { set CLK_UNCERTAINTY_HOLD  0.030 }
set_clock_uncertainty -setup $CLK_UNCERTAINTY_SETUP [all_clocks]
set_clock_uncertainty -hold  $CLK_UNCERTAINTY_HOLD  [all_clocks]

# Path groups: one group per clock domain.
if {[llength [all_clocks]] > 0} {
    group_path -name REG2REG -from [all_registers -clock_pins] -to [all_registers -data_pins]
    group_path -name IN2REG  -from [all_inputs]                -to [all_registers -data_pins]
    group_path -name REG2OUT -from [all_registers -clock_pins] -to [all_outputs]
    group_path -name IN2OUT  -from [all_inputs]                -to [all_outputs]
}

# Report analysis mode and margins.
puts "RM-Info: OCV early=[expr {100.0*$OCV_DERATE_EARLY}]% late=[expr {100.0*$OCV_DERATE_LATE}]%"
puts "RM-Info: clock uncertainty setup=$CLK_UNCERTAINTY_SETUP hold=$CLK_UNCERTAINTY_HOLD"

puts "RM-Info: [info script] completed"