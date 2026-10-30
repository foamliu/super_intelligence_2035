# ---- implementation: argus_lvs_log_triage ----
proc _argus_pg_net {net} {
    if {[string index $net end] eq "!"} { return 1 }
    foreach n {vcc vss vdd gnd vdda vssa vddq vdpg avdd avss iovdd iovss} {
        if {[string equal -nocase $net $n]} { return 1 }
    }
    return 0
}

proc argus_lvs_log_triage {path} {
    set lvs_completed 0
    set final_real_time ""
    set cum_max 0
    set ne_progress_pct -1
    set max_pending 0
    set pg_short 0
    set pairs {}
    set pin_error_count 0

    set fo [open $path r]
    set data [read $fo]
    close $fo

    foreach raw [split $data "\n"] {
        set line [string trimright $raw]
        if {[string match "*============end============*" $line]} break

        # final summary => LVS COMPLETED + final REAL TIME
        if {[string match "*LVS TOTAL TIME/MEM:*" $line]} {
            set lvs_completed 1
            if {[regexp {REAL TIME\s*=\s*([0-9.]+)} $line -> r]} {
                set final_real_time $r
            }
            continue
        }

        # alternative completion marker
        if {[regexp {LVS.*Done\.} $line]} {
            set lvs_completed 1
            continue
        }

        # cumulative forms (track max)
        if {[regexp {CUMULATIVE CPU/REAL TIME\s*=\s*[0-9.]+/([0-9.]+)} $line -> r]} {
            if {$r > $cum_max} { set cum_max $r }
            continue
        }
        if {[regexp {CUMULATIVE REAL TIME\s*=\s*([0-9.]+)} $line -> r]} {
            if {$r > $cum_max} { set cum_max $r }
            continue
        }

        # NE phase progress (last reported wins)
        if {[regexp {NE PHASE PROGRESS:\s*([0-9.]+)\s*%} $line -> p]} {
            set ne_progress_pct $p
            continue
        }

        # concurrent process count (report max only; NEVER used for stuck)
        if {[regexp {AND\s+([0-9]+)\s+PENDING OPERATIONS} $line -> n]} {
            if {$n > $max_pending} { set max_pending $n }
            continue
        }

        # shorts
        if {[regexp {SHORT:\s*(\S+)\s*-\s*(\S+)} $line -> a b]} {
            if {[_argus_pg_net $a] && [_argus_pg_net $b]} {
                set pg_short 1
                lappend pairs "$a-$b"
            }
            continue
        }

        # pin error summary
        if {[regexp {TOTAL PIN ERRORS:\s*([0-9]+)} $line -> n]} {
            set pin_error_count $n
            continue
        }
    }

    # total real time: final summary wins, else max cumulative
    if {$final_real_time ne ""} {
        set total_real_time_sec $final_real_time
    } else {
        set total_real_time_sec $cum_max
    }

    set pin_error_storm [expr {$pin_error_count > 10000}]
    set stuck_long_running [expr {$ne_progress_pct >= 0 && $ne_progress_pct < 15 && $total_real_time_sec > 120}]
    set interrupted [expr {(!$lvs_completed) && ($total_real_time_sec <= 30)}]

    if {$interrupted} {
        set primary_category interrupted
    } elseif {$pg_short} {
        set primary_category power_ground_short
    } elseif {$pin_error_storm} {
        set primary_category pin_error_storm
    } elseif {$stuck_long_running} {
        set primary_category stuck_long_running
    } else {
        set primary_category completed_clean
    }

    set short_net_pairs [join $pairs ";"]

    set out [list \
        lvs_completed $lvs_completed \
        total_real_time_sec $total_real_time_sec \
        ne_progress_pct $ne_progress_pct \
        max_pending_operations $max_pending \
        power_ground_short $pg_short \
        short_net_pairs $short_net_pairs \
        pin_error_count $pin_error_count \
        pin_error_storm $pin_error_storm \
        stuck_long_running $stuck_long_running \
        interrupted $interrupted \
        primary_category $primary_category]

    return [join $out " "]
}

# ---- test procs (verbatim) ----
# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc _wlog {path content} {
    set fo [open $path w]
    puts -nonewline $fo $content
    close $fo
}
proc check {candidate} {
    # ---- Case A: power/ground short + pin-error storm, LVS FAIL, completed ----
    _wlog _pv_lvs_A.log {Empyrean Argus - Physical Verification Tool
Version 2021.06, Build on 08/04/2021 09:28
Starting at Thu Aug  5 14:43:05 2021
Running in hierarchical mode
---- CMD 68(3) OPERATION START ON T4(W4), AND OTHER 2(2) PARALLEL OPERATIONS(TASKS) ARE RUNNING, AND 270 PENDING OPERATIONS
"M1_drawing" = GEOM_OR ("M1_drawing_ori")
---- REAL TIME = 79
NE PHASE PROGRESS: 100%
PROCESSING SHORTS ...
SHORT: vcc! - vss!
SHORT: data_sig - data_sig_b
TOTAL PIN ERRORS: 105342
NETLIST COMPARISON: CPU TIME = 14, REAL TIME = 76, PEAK MEM = 7236
LVS FAIL
LVS ... Done.
LVS TOTAL TIME/MEM: CPU TIME = 14, REAL TIME = 76, PEAK MEM = 7236
============end============
pve -port 41001 -hostname localhost -viewer aether -lvs lvs.rep
PVE viewer started, loading results ...}
    set outA [$candidate _pv_lvs_A.log]
    assert {[regexp {lvs_completed\s+1} $outA]} "A: lvs_completed must be 1 (completion marker present)"
    assert {[regexp {total_real_time_sec\s+76} $outA]} "A: total_real_time_sec must be 76"
    assert {[regexp {ne_progress_pct\s+100} $outA]} "A: ne_progress_pct must be 100"
    assert {[regexp {max_pending_operations\s+270} $outA]} "A: max_pending_operations must be 270 (reported even though not used for stuck)"
    assert {[regexp {power_ground_short\s+1} $outA]} "A: power_ground_short must be 1 (vcc!-vss! is a power/ground short)"
    assert {[regexp {short_net_pairs\s+vcc!-vss!} $outA]} "A: short_net_pairs must list vcc!-vss! (data_sig-data_sig_b is NOT power/ground -> excluded)"
    assert {![regexp {short_net_pairs\s+[^\s]*data_sig} $outA]} "A: short_net_pairs must NOT contain the signal short data_sig-data_sig_b"
    assert {[regexp {pin_error_count\s+105342} $outA]} "A: pin_error_count must be 105342"
    assert {[regexp {pin_error_storm\s+1} $outA]} "A: pin_error_storm must be 1 (>10000)"
    assert {[regexp {stuck_long_running\s+0} $outA]} "A: stuck_long_running must be 0 (progress 100%, despite high PENDING)"
    assert {[regexp {interrupted\s+0} $outA]} "A: interrupted must be 0 (completed)"
    assert {[regexp {primary_category\s+power_ground_short} $outA]} "A: primary_category must be power_ground_short (priority over pin_error_storm)"

    # ---- Case B: stuck long-running (low progress + high REAL TIME, high PENDING) ----
    _wlog _pv_lvs_B.log {Empyrean Argus - Physical Verification Tool
Version 2021.06, Build on 08/04/2021 09:28
Starting at Thu Aug  5 14:43:05 2021
Running in hierarchical mode
---- CMD 66(3) OPERATION START ON T4(W4), AND OTHER 2(2) PARALLEL OPERATIONS(TASKS) ARE RUNNING, AND 206 PENDING OPERATIONS
"M1_drawing" = GEOM_OR ("M1_drawing_ori")
---- REAL TIME = 140
NE PHASE PROGRESS: 7%
CUMULATIVE REAL TIME = 140
CUMULATIVE CPU/REAL TIME = 901/140
CUR/PEAK MEM(G) = 18.9/18.9}
    set outB [$candidate _pv_lvs_B.log]
    assert {[regexp {lvs_completed\s+0} $outB]} "B: lvs_completed must be 0 (no completion marker)"
    assert {[regexp {total_real_time_sec\s+140} $outB]} "B: total_real_time_sec must be 140 (from CUMULATIVE REAL TIME)"
    assert {[regexp {ne_progress_pct\s+7} $outB]} "B: ne_progress_pct must be 7"
    assert {[regexp {max_pending_operations\s+206} $outB]} "B: max_pending_operations must be 206 (reported)"
    assert {[regexp {power_ground_short\s+0} $outB]} "B: power_ground_short must be 0 (no shorts)"
    assert {[regexp {pin_error_count\s+0} $outB]} "B: pin_error_count must be 0"
    assert {[regexp {pin_error_storm\s+0} $outB]} "B: pin_error_storm must be 0"
    assert {[regexp {stuck_long_running\s+1} $outB]} "B: stuck_long_running must be 1 (progress 7% < 15% AND real_time 140 > 120)"
    assert {[regexp {interrupted\s+0} $outB]} "B: interrupted must be 0 (real_time 140 > 30, not a crash)"
    assert {[regexp {primary_category\s+stuck_long_running} $outB]} "B: primary_category must be stuck_long_running"

    # ---- Case C: completed CLEAN with HIGH PENDING (the PENDING-is-not-backlog trap) + a signal-only short ----
    _wlog _pv_lvs_C.log {Empyrean Argus - Physical Verification Tool
Version 2021.06, Build on 08/04/2021 09:28
Starting at Thu Aug  5 14:43:05 2021
Running in hierarchical mode
---- CMD 99(3) OPERATION START ON T8(W8), AND OTHER 4(4) PARALLEL OPERATIONS(TASKS) ARE RUNNING, AND 250 PENDING OPERATIONS
"M2_drawing" = GEOM_OR ("M2_drawing_ori")
---- REAL TIME = 45
NE PHASE PROGRESS: 100%
PROCESSING SHORTS ...
SHORT: dataA - dataB
TOTAL PIN ERRORS: 0
NETLIST COMPARISON: CPU TIME = 12, REAL TIME = 45, PEAK MEM = 4096
LVS PASS
LVS ... Done.
LVS TOTAL TIME/MEM: CPU TIME = 12, REAL TIME = 45, PEAK MEM = 4096
============end============
pve -port 41002 -hostname localhost -viewer aether}
    set outC [$candidate _pv_lvs_C.log]
    assert {[regexp {lvs_completed\s+1} $outC]} "C: lvs_completed must be 1"
    assert {[regexp {total_real_time_sec\s+45} $outC]} "C: total_real_time_sec must be 45"
    assert {[regexp {ne_progress_pct\s+100} $outC]} "C: ne_progress_pct must be 100"
    assert {[regexp {max_pending_operations\s+250} $outC]} "C: max_pending_operations must be 250 (high, but reported only)"
    assert {[regexp {power_ground_short\s+0} $outC]} "C: power_ground_short must be 0 (dataA-dataB is a SIGNAL short, not power/ground)"
    assert {[regexp {short_net_pairs\s+(\s|$)} $outC]} "C: short_net_pairs must be empty (no power/ground short)"
    assert {![regexp {short_net_pairs\s+[^\s]*dataA} $outC]} "C: short_net_pairs must NOT contain dataA-dataB"
    assert {[regexp {pin_error_storm\s+0} $outC]} "C: pin_error_storm must be 0"
    assert {[regexp {stuck_long_running\s+0} $outC]} "C: stuck_long_running must be 0 (HIGH PENDING but progress 100% -> NOT stuck; this is the key trap)"
    assert {[regexp {interrupted\s+0} $outC]} "C: interrupted must be 0"
    assert {[regexp {primary_category\s+completed_clean} $outC]} "C: primary_category must be completed_clean (high PENDING alone must not flag stuck)"

    # ---- Case D: power/ground short DESPITE LVS PASS (BCenter-style trap) ----
    _wlog _pv_lvs_D.log {Empyrean Argus - Physical Verification Tool
Version 2021.06, Build on 08/04/2021 09:28
Starting at Thu Aug  5 14:43:05 2021
Running in hierarchical mode
---- CMD 50(2) OPERATION START ON T3(W3), AND OTHER 1(1) PARALLEL OPERATIONS(TASKS) ARE RUNNING, AND 80 PENDING OPERATIONS
---- REAL TIME = 50
NE PHASE PROGRESS: 100%
PROCESSING SHORTS ...
SHORT: vddq! - vdpg!
TOTAL PIN ERRORS: 0
NETLIST COMPARISON: CPU TIME = 10, REAL TIME = 50, PEAK MEM = 3072
LVS PASS
LVS ... Done.
LVS TOTAL TIME/MEM: CPU TIME = 10, REAL TIME = 50, PEAK MEM = 3072
============end============
pve -port 41003 -hostname localhost -viewer aether}
    set outD [$candidate _pv_lvs_D.log]
    assert {[regexp {lvs_completed\s+1} $outD]} "D: lvs_completed must be 1"
    assert {[regexp {total_real_time_sec\s+50} $outD]} "D: total_real_time_sec must be 50"
    assert {[regexp {ne_progress_pct\s+100} $outD]} "D: ne_progress_pct must be 100"
    assert {[regexp {max_pending_operations\s+80} $outD]} "D: max_pending_operations must be 80"
    assert {[regexp {power_ground_short\s+1} $outD]} "D: power_ground_short must be 1 (vddq!-vdpg! short even though LVS PASS)"
    assert {[regexp {short_net_pairs\s+vddq!-vdpg!} $outD]} "D: short_net_pairs must list vddq!-vdpg!"
    assert {[regexp {pin_error_count\s+0} $outD]} "D: pin_error_count must be 0"
    assert {[regexp {pin_error_storm\s+0} $outD]} "D: pin_error_storm must be 0"
    assert {[regexp {stuck_long_running\s+0} $outD]} "D: stuck_long_running must be 0"
    assert {[regexp {interrupted\s+0} $outD]} "D: interrupted must be 0"
    assert {[regexp {primary_category\s+power_ground_short} $outD]} "D: primary_category must be power_ground_short (short detected independent of LVS PASS verdict)"

    # ---- Case E: interrupted (crashed early, no completion marker, small REAL TIME) ----
    _wlog _pv_lvs_E.log {Empyrean Argus - Physical Verification Tool
Version 2021.06, Build on 08/04/2021 09:28
Starting at Thu Aug  5 14:43:05 2021
Running in hierarchical mode
---- CMD 5(1) OPERATION START ON T1(W1), AND OTHER 0(0) PARALLEL OPERATIONS(TASKS) ARE RUNNING, AND 12 PENDING OPERATIONS
---- REAL TIME = 5
NE PHASE PROGRESS: 3%
CUMULATIVE REAL TIME = 5
ARGUS_STACK_DUMP_PATH = /tmp/argus_core_dump
Segmentation fault (core dumped)}
    set outE [$candidate _pv_lvs_E.log]
    assert {[regexp {lvs_completed\s+0} $outE]} "E: lvs_completed must be 0 (no completion marker)"
    assert {[regexp {total_real_time_sec\s+5} $outE]} "E: total_real_time_sec must be 5"
    assert {[regexp {ne_progress_pct\s+3} $outE]} "E: ne_progress_pct must be 3"
    assert {[regexp {max_pending_operations\s+12} $outE]} "E: max_pending_operations must be 12"
    assert {[regexp {power_ground_short\s+0} $outE]} "E: power_ground_short must be 0"
    assert {[regexp {pin_error_count\s+0} $outE]} "E: pin_error_count must be 0"
    assert {[regexp {stuck_long_running\s+0} $outE]} "E: stuck_long_running must be 0 (real_time 5 <= 120, not hung)"
    assert {[regexp {interrupted\s+1} $outE]} "E: interrupted must be 1 (no completion AND real_time 5 <= 30 -> crashed early)"
    assert {[regexp {primary_category\s+interrupted} $outE]} "E: primary_category must be interrupted"
}

# --- driver ---
if {[catch {check argus_lvs_log_triage} msg]} {
    puts "REF_CHECK_RC=1"
    puts "REF_CHECK_MSG=$msg"
} else {
    puts "REF_CHECK_RC=0"
    puts "REF_CHECK_MSG=$msg"
}