# Naive (buggy) implementation -- proves the test cases have teeth.
# BUGS:
#  (1) margin = value - bound for ALL metrics (ignores max-spec direction).
#      -> max-spec: lowest value -> most-negative margin -> wrongly "worst" AND "fail".
#      -> fails Case B (worst-direction) and Case C (missing as 0).
#  (2) missing metric is treated as value 0.
#      -> margin = 0 - bound -> negative -> wrongly counted as failing pair.
#      -> fails Case C (verdict wrongly "fail").
#  (3) overall worst tie-break: first-encountered (no lexicographic name tie-break).
#      -> fails Case E (picks "zz" instead of "aa").
proc hspice_corner_worst_case_audit {corner_results spec} {
    set corners_scanned 0
    set metrics_audited [lsort [dict keys $spec]]
    set failing_pairs [list]
    set missing_count 0
    set worst_per_metric [dict create]
    set worst_metric ""
    set worst_corner ""
    set have_worst 0
    set worst_margin 0

    foreach line $corner_results {
        set line [string trim $line]
        if {$line eq ""} continue
        set parts [split $line " "]
        set parts [lsearch -all -inline -not -exact $parts ""]
        if {[llength $parts] == 0} continue
        incr corners_scanned
        set corner [lindex $parts 0]
        set vals [dict create]
        foreach tok [lrange $parts 1 end] {
            set eq [string first "=" $tok]
            if {$eq < 0} continue
            dict set vals [string range $tok 0 [expr {$eq - 1}]] [string range $tok [expr {$eq + 1}] end]
        }
        foreach m $metrics_audited {
            set specv [dict get $spec $m]
            set bound [lindex $specv 1]
            # BUG (1)+(2): always margin = value - bound; missing -> 0
            if {![dict exists $vals $m]} {
                incr missing_count
                set val 0
            } else {
                set val [dict get $vals $m]
            }
            set margin [expr {$val - $bound}]
            if {$margin < 0} {
                lappend failing_pairs "$corner $m"
            }
            if {![dict exists $worst_per_metric $m]} {
                dict set worst_per_metric $m [list $corner $margin]
            } else {
                set cur [dict get $worst_per_metric $m]
                set curMargin [lindex $cur 1]
                # BUG (3): no tie-break by name
                if {$margin < $curMargin} {
                    dict set worst_per_metric $m [list $corner $margin]
                }
            }
        }
    }
    foreach m $metrics_audited {
        if {[dict exists $worst_per_metric $m]} {
            set entry [dict get $worst_per_metric $m]
            set mcorner [lindex $entry 0]
            set mmargin [lindex $entry 1]
            if {!$have_worst || $mmargin < $worst_margin} {
                set worst_metric $m
                set worst_corner $mcorner
                set worst_margin $mmargin
                set have_worst 1
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
