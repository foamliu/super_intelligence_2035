# Reference implementation of hspice_corner_worst_case_audit
# (PVT corner sweep worst-case audit, single-sided spec, flat dict output)
proc hspice_corner_worst_case_audit {corner_results spec} {
    set corners_scanned 0
    set metrics_audited [lsort [dict keys $spec]]
    set failing_pairs [list]
    set missing_count 0
    # worst_per_metric: dict metric -> {corner margin}
    set worst_per_metric [dict create]
    # overall worst tracking
    set worst_metric ""
    set worst_corner ""
    set have_worst 0
    set worst_margin 0

    foreach line $corner_results {
        set line [string trim $line]
        if {$line eq ""} continue
        # split on runs of spaces, drop empties
        set parts [split $line " "]
        set parts [lsearch -all -inline -not -exact $parts ""]
        if {[llength $parts] == 0} continue
        incr corners_scanned
        set corner [lindex $parts 0]
        # parse metric=value tokens
        set vals [dict create]
        foreach tok [lrange $parts 1 end] {
            set eq [string first "=" $tok]
            if {$eq < 0} continue
            set k [string range $tok 0 [expr {$eq - 1}]]
            set v [string range $tok [expr {$eq + 1}] end]
            dict set vals $k $v
        }
        # audit each spec metric
        foreach m $metrics_audited {
            set specv [dict get $spec $m]
            set dir [lindex $specv 0]
            set bound [lindex $specv 1]
            if {![dict exists $vals $m]} {
                incr missing_count
                continue
            }
            set val [dict get $vals $m]
            if {$dir eq "min"} {
                set margin [expr {$val - $bound}]
            } else {
                set margin [expr {$bound - $val}]
            }
            if {$margin < 0} {
                lappend failing_pairs "$corner $m"
            }
            # update worst per metric (smallest margin; tie -> lexicographic corner)
            if {![dict exists $worst_per_metric $m]} {
                dict set worst_per_metric $m [list $corner $margin]
            } else {
                set cur [dict get $worst_per_metric $m]
                set curCorner [lindex $cur 0]
                set curMargin [lindex $cur 1]
                if {$margin < $curMargin} {
                    dict set worst_per_metric $m [list $corner $margin]
                } elseif {$margin == $curMargin && [string compare $corner $curCorner] < 0} {
                    dict set worst_per_metric $m [list $corner $margin]
                }
            }
        }
    }

    # overall worst: smallest margin across all metrics' worst
    foreach m $metrics_audited {
        if {[dict exists $worst_per_metric $m]} {
            set entry [dict get $worst_per_metric $m]
            set mcorner [lindex $entry 0]
            set mmargin [lindex $entry 1]
            if {!$have_worst} {
                set worst_metric $m
                set worst_corner $mcorner
                set worst_margin $mmargin
                set have_worst 1
            } elseif {$mmargin < $worst_margin} {
                set worst_metric $m
                set worst_corner $mcorner
                set worst_margin $mmargin
            } elseif {$mmargin == $worst_margin && [string compare $mcorner $worst_corner] < 0} {
                set worst_metric $m
                set worst_corner $mcorner
                set worst_margin $mmargin
            }
        }
    }

    set failing_pairs [lsort $failing_pairs]
    set overall_verdict [expr {[llength $failing_pairs] == 0 ? "pass" : "fail"}]

    return [dict create \
        corners_scanned $corners_scanned \
        metrics_audited $metrics_audited \
        overall_verdict $overall_verdict \
        failing_pairs $failing_pairs \
        worst_metric $worst_metric \
        worst_corner $worst_corner \
        worst_margin $worst_margin \
        missing_count $missing_count]
}
