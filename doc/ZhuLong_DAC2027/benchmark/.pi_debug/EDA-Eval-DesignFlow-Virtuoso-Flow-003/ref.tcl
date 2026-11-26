# Reference implementation for EDA-Eval-DesignFlow-Virtuoso-Flow-003
# proc vflow_runlog_audit(runlog_text) -> flat dict (10 keys)
proc _vfrl_sec {ts} {
    set p [split $ts ":"]
    return [expr {[lindex $p 0]*3600 + [lindex $p 1]*60 + [lindex $p 2]}]
}
proc _vfrl_dur {a b} {
    set sa [_vfrl_sec $a]
    set sb [_vfrl_sec $b]
    if {$sb < $sa} { set sb [expr {$sb + 86400}] }
    return [expr {$sb - $sa}]
}
proc vflow_runlog_audit {log} {
    set flow_start ""
    set flow_end ""
    set seen {}
    set seen_order {}
    set status {}
    set attempts {}
    set final_start {}
    set final_end {}
    set skip_reasons {}

    foreach raw [split $log "\n"] {
        set line [string map {"\r" ""} $raw]
        set t [string trim $line]
        if {$t eq ""} continue

        # [flow] start / end
        if {[regexp -- {^\[flow\][[:space:]]+start[[:space:]]+([0-9]{2}:[0-9]{2}:[0-9]{2})$} $t -> ts]} {
            set flow_start $ts
            continue
        }
        if {[regexp -- {^\[flow\][[:space:]]+end[[:space:]]+([0-9]{2}:[0-9]{2}:[0-9]{2})$} $t -> ts]} {
            set flow_end $ts
            continue
        }

        # [step:<name>] <rest>
        if {[regexp -- {^\[step:([^]]+)\][[:space:]]+(.+)$} $t -> name rest]} {
            set rest [string trim $rest]
            if {![dict exists $seen $name]} {
                dict set seen $name 1
                lappend seen_order $name
                dict set attempts $name 0
                dict set status $name "INTERRUPTED"
            }
            # start -> new block
            if {[regexp -- {^start[[:space:]]+([0-9]{2}:[0-9]{2}:[0-9]{2})$} $rest -> ts]} {
                dict incr attempts $name 1
                dict set final_start $name $ts
                continue
            }
            # retry marker (no ts)
            if {[regexp -- {^retry$} $rest]} {
                continue
            }
            # PASS / FAIL : "STATUS HH:MM:SS"
            if {[regexp -- {^(PASS|FAIL)[[:space:]]+([0-9]{2}:[0-9]{2}:[0-9]{2})$} $rest -> st ts]} {
                dict set status $name $st
                dict set final_end $name $ts
                continue
            }
            # ERROR : "ERROR <msg> HH:MM:SS"  (ts is last token)
            if {[regexp -- {^ERROR[[:space:]]+(.+)[[:space:]]+([0-9]{2}:[0-9]{2}:[0-9]{2})$} $rest -> msg ts]} {
                dict set status $name "ERROR"
                dict set final_end $name $ts
                continue
            }
            # SKIP : "SKIP reason=<tok> HH:MM:SS"
            if {[regexp -- {^SKIP[[:space:]]+reason=([^[:space:]]+)[[:space:]]+([0-9]{2}:[0-9]{2}:[0-9]{2})$} $rest -> reason ts]} {
                dict set status $name "SKIP"
                dict set final_end $name $ts
                dict set skip_reasons $name $reason
                continue
            }
            # WARN / anything else -> ignored for status & attempts
        }
    }

    # pair lists, lex sorted by name
    set step_status {}
    set step_attempts {}
    set step_duration {}
    set skip_reason_pairs {}
    foreach n [lsort $seen_order] {
        lappend step_status "$n:[dict get $status $n]"
        lappend step_attempts "$n:[dict get $attempts $n]"
        set d 0
        if {[dict exists $final_start $n] && [dict exists $final_end $n]} {
            set d [_vfrl_dur [dict get $final_start $n] [dict get $final_end $n]]
        }
        lappend step_duration "$n:$d"
        if {[dict exists $skip_reasons $n]} {
            lappend skip_reason_pairs "$n:[dict get $skip_reasons $n]"
        }
    }

    set retried {}
    set skipped {}
    set failed {}
    foreach n $seen_order {
        if {[dict get $attempts $n] > 1} { lappend retried $n }
        set st [dict get $status $n]
        if {$st eq "SKIP"} { lappend skipped $n }
        if {$st eq "FAIL" || $st eq "ERROR"} { lappend failed $n }
    }
    set retried [lsort $retried]
    set skipped [lsort $skipped]
    set failed [lsort $failed]

    set total_wall 0
    if {$flow_start ne "" && $flow_end ne ""} {
        set total_wall [_vfrl_dur $flow_start $flow_end]
    }

    set verdict "PASS"
    if {[llength $failed] > 0} {
        set verdict "ERROR"
    } elseif {[llength $skipped] > 0} {
        set verdict "SKIPPED"
    } else {
        foreach n $seen_order {
            if {[dict get $status $n] eq "INTERRUPTED"} { set verdict "ERROR"; break }
        }
    }

    return [dict create \
        steps_seen $seen_order \
        step_status $step_status \
        step_attempts $step_attempts \
        step_duration_sec $step_duration \
        skip_reasons $skip_reason_pairs \
        total_wall_sec $total_wall \
        retried_steps $retried \
        skipped_steps $skipped \
        failed_steps $failed \
        overall_verdict $verdict]
}
