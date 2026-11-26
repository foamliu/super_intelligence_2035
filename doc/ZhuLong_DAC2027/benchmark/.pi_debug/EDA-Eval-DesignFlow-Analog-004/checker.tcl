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
