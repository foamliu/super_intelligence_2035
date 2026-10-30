# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc feq {a b {tol 0.001}} { return [expr {abs(double($a)-double($b)) < $tol}] }

proc check {candidate} {
    ## Case A: REAL session -- addr_to_rowcol_v7 Innovus PR -> StarRC -> SPEF -> PrimeTime STA.
    set reportA {# PrimeTime STA Report
# Design: addr_to_rowcol_v7 (cxmtG5_CIP DRAM), 107 cells / 116 nets
# Reading SPEF file: parasitics.spef
#   Number of nets annotated: 116
#   Number of nets total:     116
#   SPEF annotation coverage: 100.00%

  Startpoint: reg_addr_0 (rising edge-triggered flip-flop clocked by clk)
  Endpoint:   reg_col_7 (rising edge-triggered flip-flop clocked by clk)
  Path Group: clk
  Path Type:  max
  ------------------------------------------------------------
  slack (VIOLATED)                                    -0.04

  Startpoint: reg_addr_1 (rising edge-triggered flip-flop clocked by clk)
  Endpoint:   reg_col_5 (rising edge-triggered flip-flop clocked by clk)
  Path Group: clk
  Path Type:  max
  ------------------------------------------------------------
  slack (VIOLATED)                                    -0.04

  Startpoint: reg_addr_2 (rising edge-triggered flip-flop clocked by clk)
  Endpoint:   reg_col_4 (rising edge-triggered flip-flop clocked by clk)
  Path Group: clk
  Path Type:  max
  ------------------------------------------------------------
  slack (VIOLATED)                                    -0.03

  Startpoint: reg_addr_3 (rising edge-triggered flip-flop clocked by clk)
  Endpoint:   reg_col_3 (rising edge-triggered flip-flop clocked by clk)
  Path Group: clk
  Path Type:  max
  ------------------------------------------------------------
  slack (VIOLATED)                                    -0.03

  Startpoint: reg_addr_4 (rising edge-triggered flip-flop clocked by clk)
  Endpoint:   reg_col_2 (rising edge-triggered flip-flop clocked by clk)
  Path Group: clk
  Path Type:  max
  ------------------------------------------------------------
  slack (VIOLATED)                                    -0.03

  Startpoint: reg_addr_5 (rising edge-triggered flip-flop clocked by clk)
  Endpoint:   reg_col_1 (rising edge-triggered flip-flop clocked by clk)
  Path Group: clk
  Path Type:  max
  ------------------------------------------------------------
  slack (MET)                                         0.12

  Startpoint: reg_addr_6 (rising edge-triggered flip-flop clocked by clk)
  Endpoint:   reg_col_0 (rising edge-triggered flip-flop clocked by clk)
  Path Group: clk
  Path Type:  max
  ------------------------------------------------------------
  slack (MET)                                         0.08

# Timing Summary
  WNS (ns): -0.04
  TNS (ns): -0.17
  Number of violating endpoints: 5
  Number of total endpoints:     116

# Critical Path Summary
  Critical Path Levels: 13
  Data Arrival Time:    0.54 ns
  Data Required Time:   0.50 ns
  Slack (VIOLATED):     -0.04 ns
}
    set dA [$candidate $reportA]
    set dA [dict create {*}$dA]
    assert {[dict get $dA num_startpoints] == 7} "A: num_startpoints must be 7"
    assert {[dict get $dA spef_annotated] == 116} "A: spef_annotated must be 116"
    assert {[dict get $dA spef_total] == 116} "A: spef_total must be 116"
    assert {[feq [dict get $dA spef_coverage_pct] 100.0 0.05]} "A: spef_coverage_pct must be 100.0"
    assert {[feq [dict get $dA wns_ns] -0.04]} "A: wns_ns must be -0.04 (worst slack)"
    assert {[feq [dict get $dA tns_ns] -0.17]} "A: tns_ns must be -0.17 (sum of negatives only, MET excluded)"
    assert {[dict get $dA num_violating_endpoints] == 5} "A: num_violating_endpoints must be 5"
    assert {[dict get $dA num_total_endpoints] == 116} "A: num_total_endpoints must be 116"
    assert {[dict get $dA critical_levels] == 13} "A: critical_levels must be 13"
    assert {[feq [dict get $dA critical_arrival_ns] 0.54]} "A: critical_arrival_ns must be 0.54"
    assert {[feq [dict get $dA critical_required_ns] 0.50]} "A: critical_required_ns must be 0.50"
    assert {[feq [dict get $dA critical_slack_ns] -0.04]} "A: critical_slack_ns must be -0.04"
    assert {[dict get $dA slack_convention_ok] == 1} "A: slack must equal required - arrival (sign convention)"
    assert {[dict get $dA critical_slack_ns] < 0} "A: violated path slack must be negative"

    ## Case B: PASSING design (all MET).
    set reportB {# PrimeTime STA Report
# Design: rowdec_ctrl (cxmtG5_CIP DRAM), 80 nets
# Reading SPEF file: parasitics.spef
#   Number of nets annotated: 80
#   Number of nets total:     80
#   SPEF annotation coverage: 100.00%

  Startpoint: r_dec_0 (rising edge-triggered flip-flop clocked by clk)
  Endpoint:   r_out_0 (rising edge-triggered flip-flop clocked by clk)
  Path Group: clk
  Path Type:  max
  ------------------------------------------------------------
  slack (MET)                                         0.12

# Timing Summary
  WNS (ns): 0.12
  TNS (ns): 0.00
  Number of violating endpoints: 0
  Number of total endpoints:     80

# Critical Path Summary
  Critical Path Levels: 8
  Data Arrival Time:    0.38 ns
  Data Required Time:   0.50 ns
  Slack (MET):          0.12 ns
}
    set dB [$candidate $reportB]
    set dB [dict create {*}$dB]
    assert {[feq [dict get $dB wns_ns] 0.12]} "B: wns_ns must be +0.12 (POSITIVE, MET -- not negated)"
    assert {[dict get $dB wns_ns] > 0} "B: passing design WNS must be positive"
    assert {[feq [dict get $dB tns_ns] 0.0]} "B: tns_ns must be 0.0 (no violations)"
    assert {[dict get $dB num_violating_endpoints] == 0} "B: num_violating_endpoints must be 0"
    assert {[dict get $dB num_total_endpoints] == 80} "B: num_total_endpoints must be 80"
    assert {[dict get $dB spef_annotated] == 80} "B: spef_annotated must be 80"
    assert {[dict get $dB spef_total] == 80} "B: spef_total must be 80"
    assert {[feq [dict get $dB spef_coverage_pct] 100.0 0.05]} "B: spef_coverage_pct must be 100.0"
    assert {[dict get $dB critical_levels] == 8} "B: critical_levels must be 8"
    assert {[feq [dict get $dB critical_arrival_ns] 0.38]} "B: critical_arrival_ns must be 0.38"
    assert {[feq [dict get $dB critical_required_ns] 0.50]} "B: critical_required_ns must be 0.50"
    assert {[feq [dict get $dB critical_slack_ns] 0.12]} "B: critical_slack_ns must be +0.12"
    assert {[dict get $dB slack_convention_ok] == 1} "B: slack = required - arrival = 0.12 (sign convention holds for MET)"
    assert {[dict get $dB critical_slack_ns] > 0} "B: MET path slack must be positive"

    ## Case C: PARTIAL SPEF coverage.
    set reportC {# PrimeTime STA Report
# Design: addr_buf_v2 (cxmtG5_CIP DRAM), 116 nets
# Reading SPEF file: parasitics_partial.spef
#   Number of nets annotated: 95
#   Number of nets total:     116
#   SPEF annotation coverage: 81.90%

  Startpoint: r_a_0 (rising edge-triggered flip-flop clocked by clk)
  Endpoint:   r_b_0 (rising edge-triggered flip-flop clocked by clk)
  Path Group: clk
  Path Type:  max
  ------------------------------------------------------------
  slack (VIOLATED)                                    -0.10

  Startpoint: r_a_1 (rising edge-triggered flip-flop clocked by clk)
  Endpoint:   r_b_1 (rising edge-triggered flip-flop clocked by clk)
  Path Group: clk
  Path Type:  max
  ------------------------------------------------------------
  slack (VIOLATED)                                    -0.10

  Startpoint: r_a_2 (rising edge-triggered flip-flop clocked by clk)
  Endpoint:   r_b_2 (rising edge-triggered flip-flop clocked by clk)
  Path Group: clk
  Path Type:  max
  ------------------------------------------------------------
  slack (VIOLATED)                                    -0.10

  Startpoint: r_a_3 (rising edge-triggered flip-flop clocked by clk)
  Endpoint:   r_b_3 (rising edge-triggered flip-flop clocked by clk)
  Path Group: clk
  Path Type:  max
  ------------------------------------------------------------
  slack (MET)                                         0.05

# Timing Summary
  WNS (ns): -0.10
  TNS (ns): -0.30
  Number of violating endpoints: 3
  Number of total endpoints:     116

# Critical Path Summary
  Critical Path Levels: 10
  Data Arrival Time:    0.60 ns
  Data Required Time:   0.50 ns
  Slack (VIOLATED):     -0.10 ns
}
    set dC [$candidate $reportC]
    set dC [dict create {*}$dC]
    assert {[dict get $dC spef_annotated] == 95} "C: spef_annotated must be 95"
    assert {[dict get $dC spef_total] == 116} "C: spef_total must be 116"
    assert {[dict get $dC spef_annotated] != [dict get $dC spef_total]} "C: annotated != total (partial coverage)"
    assert {[feq [dict get $dC spef_coverage_pct] 81.9 0.05]} "C: spef_coverage_pct must be 81.9 (annotated/total)"
    assert {[feq [dict get $dC wns_ns] -0.10]} "C: wns_ns must be -0.10"
    assert {[feq [dict get $dC tns_ns] -0.30]} "C: tns_ns must be -0.30"
    assert {[dict get $dC num_violating_endpoints] == 3} "C: num_violating_endpoints must be 3"
    assert {[dict get $dC num_total_endpoints] == 116} "C: num_total_endpoints must be 116"
    assert {[dict get $dC num_startpoints] == 4} "C: num_startpoints must be 4"
    assert {[dict get $dC critical_levels] == 10} "C: critical_levels must be 10"
    assert {[feq [dict get $dC critical_arrival_ns] 0.60]} "C: critical_arrival_ns must be 0.60"
    assert {[feq [dict get $dC critical_required_ns] 0.50]} "C: critical_required_ns must be 0.50"
    assert {[feq [dict get $dC critical_slack_ns] -0.10]} "C: critical_slack_ns must be -0.10"
    assert {[dict get $dC slack_convention_ok] == 1} "C: slack = required - arrival = -0.10 (sign convention)"

    return "CHECK_PASS: 3 cases, 41 asserts"
}

# --- driver ---
if {[catch {check pnr_signoff_parse_sta_report} msg]} {
    puts "REF_CHECK_RC=1"
    puts "REF_CHECK_MSG=$msg"
} else {
    puts "REF_CHECK_RC=0"
    puts "REF_CHECK_MSG=$msg"
}
