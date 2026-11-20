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
# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}

# helper: compare a list to an expected sorted list via joined string.
proc lcmp {actual expected} {
    set a [join [lsort $actual] ","]
    set e [join [lsort $expected] ","]
    return [expr {$a eq $e}]
}

# helper: approximate numeric equality (tolerance for floating-point margins).
proc approx {a b {tol 1e-9}} {
    return [expr {abs($a - $b) < $tol}]
}

proc check {candidate} {
    # ---- Case A: baseline -- 3 corners, 2 metrics (gain min, voff max), all pass.
    # worst gain = ss (margin 5); worst voff = ff (margin 0.1); overall worst = voff/ff (0.1).
    set crA [list \
        "tt gain=60 voff=0.8" \
        "ff gain=70 voff=0.9" \
        "ss gain=55 voff=0.7"]
    set spA [dict create gain {min 50} voff {max 1.0}]
    set d [$candidate $crA $spA]
    assert {[dict get $d corners_scanned] == 3} "A corners_scanned=3"
    assert {[lcmp [dict get $d metrics_audited] {gain voff}]} "A metrics_audited={gain voff}"
    assert {[dict get $d overall_verdict] eq "pass"} "A overall_verdict=pass"
    assert {[lcmp [dict get $d failing_pairs] {}]} "A failing_pairs empty"
    assert {[dict get $d worst_metric] eq "voff"} "A worst_metric=voff"
    assert {[dict get $d worst_corner] eq "ff"} "A worst_corner=ff (voff margin 0.1 tightest)"
    assert {[approx [dict get $d worst_margin] 0.1]} "A worst_margin=0.1"
    assert {[dict get $d missing_count] == 0} "A missing_count=0"

    # ---- Case B: worst-direction teeth -- max-spec voff: HIGHEST value is worst.
    # tt voff=0.5 (margin 1.5); ff voff=1.8 (margin 0.2); ss voff=1.2 (margin 0.8).
    # worst = ff (margin 0.2). Naive "lowest value is worst" picks tt (safest) -> TEETH.
    set crB [list \
        "tt voff=0.5" \
        "ff voff=1.8" \
        "ss voff=1.2"]
    set spB [dict create voff {max 2.0}]
    set d [$candidate $crB $spB]
    assert {[dict get $d corners_scanned] == 3} "B corners_scanned=3"
    assert {[dict get $d overall_verdict] eq "pass"} "B overall_verdict=pass"
    assert {[dict get $d worst_metric] eq "voff"} "B worst_metric=voff"
    assert {[dict get $d worst_corner] eq "ff"} "B worst_corner=ff (highest voff=1.8, smallest margin 0.2)"
    assert {[approx [dict get $d worst_margin] 0.2]} "B worst_margin=0.2"
    assert {[dict get $d missing_count] == 0} "B missing_count=0"

    # ---- Case C: missing-metric teeth -- corner "ss" lacks voff; voff still passes
    # (tt/ff have it and pass); missing_count=1; verdict pass.
    # Naive "missing -> 0 -> margin -1.0 -> fail" wrongly fails -> TEETH.
    set crC [list \
        "tt gain=60 voff=0.8" \
        "ff gain=70 voff=0.9" \
        "ss gain=55"]
    set spC [dict create gain {min 50} voff {max 1.0}]
    set d [$candidate $crC $spC]
    assert {[dict get $d corners_scanned] == 3} "C corners_scanned=3"
    assert {[dict get $d overall_verdict] eq "pass"} "C overall_verdict=pass (missing voff in ss is NOT a failure)"
    assert {[lcmp [dict get $d failing_pairs] {}]} "C failing_pairs empty"
    assert {[dict get $d missing_count] == 1} "C missing_count=1 (ss lacks voff)"
    assert {[dict get $d worst_metric] eq "voff"} "C worst_metric=voff"
    assert {[dict get $d worst_corner] eq "ff"} "C worst_corner=ff"

    # ---- Case D: AND-logic fail teeth -- gain passes all corners; voff fails in ff.
    # overall verdict = fail; failing_pairs = {"ff voff"}; worst = voff/ff (margin -0.2).
    # Naive "majority of metrics pass -> overall pass" -> TEETH.
    set crD [list \
        "tt gain=60 voff=0.8" \
        "ff gain=70 voff=1.2" \
        "ss gain=55 voff=0.7"]
    set spD [dict create gain {min 50} voff {max 1.0}]
    set d [$candidate $crD $spD]
    assert {[dict get $d overall_verdict] eq "fail"} "D overall_verdict=fail (AND-logic: one failing pair fails all)"
    assert {[lcmp [dict get $d failing_pairs] {"ff voff"}]} "D failing_pairs={ff voff}"
    assert {[dict get $d worst_metric] eq "voff"} "D worst_metric=voff"
    assert {[dict get $d worst_corner] eq "ff"} "D worst_corner=ff"
    assert {[approx [dict get $d worst_margin] -0.2]} "D worst_margin=-0.2 (1.0-1.2)"
    assert {[dict get $d missing_count] == 0} "D missing_count=0"

    # ---- Case E: tie-break teeth -- two corners with identical worst margin;
    # lexicographically smaller corner name wins.
    # zz gain=60 (margin 10); aa gain=60 (margin 10); worst margin 10 -> corner "aa".
    # Naive "first-encountered" picks "zz" -> TEETH.
    set crE [list \
        "zz gain=60" \
        "aa gain=60" \
        "mm gain=70"]
    set spE [dict create gain {min 50}]
    set d [$candidate $crE $spE]
    assert {[dict get $d overall_verdict] eq "pass"} "E overall_verdict=pass"
    assert {[dict get $d worst_metric] eq "gain"} "E worst_metric=gain"
    assert {[dict get $d worst_corner] eq "aa"} "E worst_corner=aa (tie margin 10, lexicographic smallest)"
    assert {[approx [dict get $d worst_margin] 10]} "E worst_margin=10"

    # ---- Case F: empty / invariant -- empty corner_results + empty spec.
    set d [$candidate [list] [dict create]]
    assert {[dict get $d corners_scanned] == 0} "F corners_scanned=0"
    assert {[lcmp [dict get $d metrics_audited] {}]} "F metrics_audited empty"
    assert {[dict get $d overall_verdict] eq "pass"} "F overall_verdict=pass (vacuous)"
    assert {[lcmp [dict get $d failing_pairs] {}]} "F failing_pairs empty"
    assert {[dict get $d worst_metric] eq ""} "F worst_metric empty"
    assert {[dict get $d worst_corner] eq ""} "F worst_corner empty"
    assert {[dict get $d worst_margin] == 0} "F worst_margin=0"
    assert {[dict get $d missing_count] == 0} "F missing_count=0"

    return "ALL_ASSERTS_PASS"
}

set r [check hspice_corner_worst_case_audit]; puts "RESULT:$r"; if {$r eq "ALL_ASSERTS_PASS"} { puts "DESIGN_FLOW_VERDICT=PASS" } else { puts "DESIGN_FLOW_VERDICT=FAIL" }
