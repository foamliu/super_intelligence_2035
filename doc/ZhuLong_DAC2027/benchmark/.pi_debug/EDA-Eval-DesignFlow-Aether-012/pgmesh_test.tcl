proc layout_pgmesh_audit {report_text} {
    set has_summary 0
    array set summary {}
    array set rec {}
    set keys {}

    foreach raw [split $report_text "\n"] {
        set line [string trim $raw]
        if {$line eq ""} { continue }
        if {[string index $line 0] eq "#"} { continue }
        set w [split $line]
        set kw [lindex $w 0]
        if {$kw eq "MESH"} {
            set name [lindex $w 1]
            set layer [lindex $w 2]
            set rest [lrange $w 3 end]
            set n [llength $rest]
            set i 0
            set direction ""
            set width 0.0
            set space 0.0
            set vias 1
            set status "ok"
            # optional direction (case-insensitive), first
            if {$i < $n} {
                set tok [lindex $rest $i]
                set lt [string tolower $tok]
                if {$lt eq "h" || $lt eq "v" || $lt eq "horizontal" || $lt eq "vertical"} {
                    set direction $lt
                    incr i
                }
            }
            # optional width (real)
            if {$i < $n} {
                set tok [lindex $rest $i]
                if {[string is double -strict $tok]} {
                    set width $tok
                    incr i
                }
            }
            # optional space (real)
            if {$i < $n} {
                set tok [lindex $rest $i]
                if {[string is double -strict $tok]} {
                    set space $tok
                    incr i
                }
            }
            # optional vias (integer)
            if {$i < $n} {
                set tok [lindex $rest $i]
                if {[string is double -strict $tok]} {
                    set vias $tok
                    incr i
                }
            }
            # optional status (case-insensitive)
            if {$i < $n} {
                set tok [lindex $rest $i]
                set lt [string tolower $tok]
                if {$lt eq "ok" || $lt eq "skip" || $lt eq "short" || $lt eq "open"} {
                    set status $lt
                    incr i
                }
            }
            set key [list $name $layer]
            if {![info exists rec($key)]} { lappend keys $key }
            set rec($key) [list $name $layer $direction $width $space $vias $status]
        } elseif {$kw eq "SUMMARY"} {
            set has_summary 1
            foreach tok [lrange $w 1 end] {
                set eq [string first "=" $tok]
                if {$eq >= 0} {
                    set f [string range $tok 0 [expr {$eq - 1}]]
                    set v [string range $tok [expr {$eq + 1}] end]
                    set summary($f) $v
                }
            }
        }
    }

    set total [llength $keys]
    set power 0
    set ground 0
    set unknown 0
    set short 0
    set open 0
    set skip 0
    set non_skip_present 0
    set min_width -1.0
    set max_space -1.0
    set min_names {}
    set max_names {}

    foreach key $keys {
        set r $rec($key)
        set name [lindex $r 0]
        set status [lindex $r 6]
        set width [lindex $r 3]
        set space [lindex $r 4]
        set ln [string tolower $name]
        set class "unknown"
        if {[string match {*vdd*} $ln] || [string match {*vcc*} $ln] || [string match {*power*} $ln]} {
            set class "power"
        } elseif {[string match {*gnd*} $ln] || [string match {*vss*} $ln] || [string match {*ground*} $ln]} {
            set class "ground"
        }
        if {$class eq "power"} { incr power } elseif {$class eq "ground"} { incr ground } else { incr unknown }
        if {$status eq "short"} { incr short }
        if {$status eq "open"} { incr open }
        if {$status eq "skip"} { incr skip }

        if {$status ne "skip"} {
            set dw [expr {double($width)}]
            set ds [expr {double($space)}]
            if {!$non_skip_present} {
                set non_skip_present 1
                set min_width $dw
                set max_space $ds
                set min_names [list $name]
                set max_names [list $name]
            } else {
                if {$dw < $min_width} {
                    set min_width $dw
                    set min_names [list $name]
                } elseif {$dw == $min_width} {
                    lappend min_names $name
                }
                if {$ds > $max_space} {
                    set max_space $ds
                    set max_names [list $name]
                } elseif {$ds == $max_space} {
                    lappend max_names $name
                }
            }
        }
    }

    if {$non_skip_present} {
        set worst_min [lindex [lsort -dictionary $min_names] 0]
        set worst_max [lindex [lsort -dictionary $max_names] 0]
    } else {
        set worst_min ""
        set worst_max ""
    }

    if {$total == 0} {
        set coverage 0
    } else {
        set coverage [expr {round(($power + $ground) * 100.0 / $total)}]
    }

    set mismatched {}
    if {$has_summary} {
        if {[info exists summary(total)] && $summary(total) != $total} {
            lappend mismatched "total=$summary(total) vs $total"
        }
        if {[info exists summary(power)] && $summary(power) != $power} {
            lappend mismatched "power=$summary(power) vs $power"
        }
        if {[info exists summary(ground)] && $summary(ground) != $ground} {
            lappend mismatched "ground=$summary(ground) vs $ground"
        }
        if {[info exists summary(min_width)]} {
            if {![expr {double($summary(min_width)) == double($min_width)}]} {
                lappend mismatched "min_width=$summary(min_width) vs $min_width"
            }
        }
        if {[info exists summary(max_space)]} {
            if {![expr {double($summary(max_space)) == double($max_space)}]} {
                lappend mismatched "max_space=$summary(max_space) vs $max_space"
            }
        }
        if {[info exists summary(coverage)] && $summary(coverage) != $coverage} {
            lappend mismatched "coverage=$summary(coverage) vs $coverage"
        }
    }

    if {$short > 0} {
        set verdict "FAIL"
    } elseif {$open > 0} {
        set verdict "REVIEW"
    } elseif {!$has_summary || [llength $mismatched] > 0} {
        set verdict "INCOMPLETE"
    } else {
        set verdict "PASS"
    }

    return [dict create \
        total_straps $total \
        power_straps $power \
        ground_straps $ground \
        unknown_straps $unknown \
        short_count $short \
        open_count $open \
        skip_count $skip \
        min_width $min_width \
        max_space $max_space \
        worst_min_width_strap $worst_min \
        worst_max_space_strap $worst_max \
        coverage_pct $coverage \
        mismatched_summary $mismatched \
        verdict $verdict]
}

# ---------------------------------------------------------------------------
# Checker for layout_pgmesh_audit
# Builds fixtures inline and asserts on the returned dict.
proc _chk {name cond} {
    global _chk_pass _chk_fail _chk_first
    if {![uplevel 1 [list expr $cond]]} {
        set _chk_pass 0
        if {$_chk_fail == 0} { set _chk_first $name }
        incr _chk_fail
        puts "ASSERT FAIL: $name"
    } else {
        incr _chk_pass
    }
}
proc _chk_done {} {
    global _chk_pass _chk_fail
    if {$_chk_fail == 0} { puts "ALL_ASSERTS_PASS" } else { puts "ASSERTS_FAILED" }
}
proc check {fn} {
    global _chk_pass _chk_fail _chk_first
    set _chk_pass 1; set _chk_fail 0; set _chk_first ""

    # ---- Case A: baseline (power/ground mix + summary match -> PASS) ----
    set a "# PG-MESH report
MESH vdd_core M5 H 0.5 0.3 8 ok
MESH vss_core M5 H 0.5 0.3 8 ok
MESH vdd_io M6 V 0.6 0.4 4 ok
MESH vss_io M6 V 0.6 0.4 4 ok
SUMMARY total=4 power=2 ground=2 min_width=0.5 max_space=0.4 coverage=100"
    set rA [$fn $a]
    _chk A_total {[dict get $rA total_straps] == 4}
    _chk A_power {[dict get $rA power_straps] == 2}
    _chk A_ground {[dict get $rA ground_straps] == 2}
    _chk A_unknown {[dict get $rA unknown_straps] == 0}
    _chk A_short {[dict get $rA short_count] == 0}
    _chk A_open {[dict get $rA open_count] == 0}
    _chk A_skip {[dict get $rA skip_count] == 0}
    _chk A_min_width {[dict get $rA min_width] == 0.5}
    _chk A_max_space {[dict get $rA max_space] == 0.4}
    _chk A_worst_min {[dict get $rA worst_min_width_strap] eq "vdd_core"}
    _chk A_worst_max {[dict get $rA worst_max_space_strap] eq "vdd_io"}
    _chk A_coverage {[dict get $rA coverage_pct] == 100}
    _chk A_mismatch_empty {[llength [dict get $rA mismatched_summary]] == 0}
    _chk A_verdict {[dict get $rA verdict] eq "PASS"}

    # ---- Case B: direction & status CASE-INSENSITIVE; FAIL beats PASS ----
    set b "# case-insensitive direction & status
MESH vdd1 M5 HORIZONTAL 0.5 0.3 8 OK
MESH vss1 M5 horizontal 0.5 0.3 8 Skip
MESH vdd2 M6 VERTICAL 0.6 0.4 4 Short
MESH vss2 M6 vertical 0.6 0.4 4 OPEN
SUMMARY total=4 power=2 ground=2 min_width=0.5 max_space=0.4 coverage=100"
    set rB [$fn $b]
    _chk B_total {[dict get $rB total_straps] == 4}
    _chk B_power {[dict get $rB power_straps] == 2}
    _chk B_ground {[dict get $rB ground_straps] == 2}
    _chk B_short {[dict get $rB short_count] == 1}
    _chk B_open {[dict get $rB open_count] == 1}
    _chk B_skip {[dict get $rB skip_count] == 1}
    _chk B_min_width {[dict get $rB min_width] == 0.5}
    _chk B_max_space {[dict get $rB max_space] == 0.4}
    _chk B_worst_min {[dict get $rB worst_min_width_strap] eq "vdd1"}
    _chk B_worst_max {[dict get $rB worst_max_space_strap] eq "vdd2"}
    _chk B_mismatch_empty {[llength [dict get $rB mismatched_summary]] == 0}
    _chk B_verdict {[dict get $rB verdict] eq "FAIL"}

    # ---- Case C: dup (name,layer) LAST-WINS (replace, not first-wins) ----
    set c "# dup (name,layer): vdd1,M5 twice; last wins (skip, width 0.9)
MESH vdd1 M5 H 0.5 0.3 8 ok
MESH vdd1 M5 H 0.9 0.7 4 skip
MESH vss1 M5 H 0.5 0.3 8 ok
SUMMARY total=2 power=1 ground=1 min_width=0.5 max_space=0.3 coverage=100"
    set rC [$fn $c]
    _chk C_total {[dict get $rC total_straps] == 2}
    _chk C_power {[dict get $rC power_straps] == 1}
    _chk C_ground {[dict get $rC ground_straps] == 1}
    _chk C_skip {[dict get $rC skip_count] == 1}
    _chk C_min_width {[dict get $rC min_width] == 0.5}
    _chk C_worst_min {[dict get $rC worst_min_width_strap] eq "vss1"}
    _chk C_max_space {[dict get $rC max_space] == 0.3}
    _chk C_worst_max {[dict get $rC worst_max_space_strap] eq "vss1"}
    _chk C_mismatch_empty {[llength [dict get $rC mismatched_summary]] == 0}
    _chk C_verdict {[dict get $rC verdict] eq "PASS"}

    # ---- Case D: status absent -> default "ok"; missing width/space/vias ----
    set d "# absent status -> ok; missing width->0.0, space->0.0, vias->1
MESH vdd1 M5 H 0.5 0.3 8
MESH vss1 M5 H
SUMMARY total=2 power=1 ground=1 min_width=0.0 max_space=0.3 coverage=100"
    set rD [$fn $d]
    _chk D_total {[dict get $rD total_straps] == 2}
    _chk D_power {[dict get $rD power_straps] == 1}
    _chk D_ground {[dict get $rD ground_straps] == 1}
    _chk D_skip {[dict get $rD skip_count] == 0}
    _chk D_min_width {[dict get $rD min_width] == 0.0}
    _chk D_worst_min {[dict get $rD worst_min_width_strap] eq "vss1"}
    _chk D_max_space {[dict get $rD max_space] == 0.3}
    _chk D_worst_max {[dict get $rD worst_max_space_strap] eq "vdd1"}
    _chk D_mismatch_empty {[llength [dict get $rD mismatched_summary]] == 0}
    _chk D_verdict {[dict get $rD verdict] eq "PASS"}

    # ---- Case E: name classification (power/ground/unknown) + coverage rounding ----
    set e "# classification by name; coverage rounding 2/3 -> 67
MESH vdd_core M5 H 0.5 0.3 8 ok
MESH VSS_io M5 H 0.5 0.3 8 ok
MESH strap_x M6 V 0.4 0.2 4 ok
SUMMARY total=3 power=1 ground=1 min_width=0.4 max_space=0.3 coverage=67"
    set rE [$fn $e]
    _chk E_total {[dict get $rE total_straps] == 3}
    _chk E_power {[dict get $rE power_straps] == 1}
    _chk E_ground {[dict get $rE ground_straps] == 1}
    _chk E_unknown {[dict get $rE unknown_straps] == 1}
    _chk E_coverage {[dict get $rE coverage_pct] == 67}
    _chk E_min_width {[dict get $rE min_width] == 0.4}
    _chk E_worst_min {[dict get $rE worst_min_width_strap] eq "strap_x"}
    _chk E_max_space {[dict get $rE max_space] == 0.3}
    _chk E_worst_max {[dict get $rE worst_max_space_strap] eq "vdd_core"}
    _chk E_mismatch_empty {[llength [dict get $rE mismatched_summary]] == 0}
    _chk E_verdict {[dict get $rE verdict] eq "PASS"}

    # ---- Case F: min_width excludes SKIP; tie-break strap2 < strap10 ----
    set f "# min_width excludes SKIP; tie-break strap2<strap10 (dictionary numeric-aware)
MESH strap10 M5 H 0.5 0.3 8 ok
MESH strap2 M5 H 0.5 0.4 8 ok
MESH vdd1 M5 H 0.9 0.3 8 skip
SUMMARY total=3 power=1 ground=0 min_width=0.5 max_space=0.4 coverage=33"
    set rF [$fn $f]
    _chk F_total {[dict get $rF total_straps] == 3}
    _chk F_power {[dict get $rF power_straps] == 1}
    _chk F_unknown {[dict get $rF unknown_straps] == 2}
    _chk F_skip {[dict get $rF skip_count] == 1}
    _chk F_min_width {[dict get $rF min_width] == 0.5}
    _chk F_worst_min {[dict get $rF worst_min_width_strap] eq "strap2"}
    _chk F_max_space {[dict get $rF max_space] == 0.4}
    _chk F_worst_max {[dict get $rF worst_max_space_strap] eq "strap2"}
    _chk F_coverage {[dict get $rF coverage_pct] == 33}
    _chk F_mismatch_empty {[llength [dict get $rF mismatched_summary]] == 0}
    _chk F_verdict {[dict get $rF verdict] eq "PASS"}

    # ---- Case G: max_space excludes SKIP; tie-break ----
    set g "# max_space excludes SKIP; tie-break
MESH vdd_a M5 H 0.5 0.4 8 ok
MESH vdd_b M5 H 0.5 0.4 8 ok
MESH vss_a M5 H 0.5 0.9 8 skip
SUMMARY total=3 power=2 ground=1 min_width=0.5 max_space=0.4 coverage=100"
    set rG [$fn $g]
    _chk G_power {[dict get $rG power_straps] == 2}
    _chk G_ground {[dict get $rG ground_straps] == 1}
    _chk G_skip {[dict get $rG skip_count] == 1}
    _chk G_min_width {[dict get $rG min_width] == 0.5}
    _chk G_worst_min {[dict get $rG worst_min_width_strap] eq "vdd_a"}
    _chk G_max_space {[dict get $rG max_space] == 0.4}
    _chk G_worst_max {[dict get $rG worst_max_space_strap] eq "vdd_a"}
    _chk G_coverage {[dict get $rG coverage_pct] == 100}
    _chk G_mismatch_empty {[llength [dict get $rG mismatched_summary]] == 0}
    _chk G_verdict {[dict get $rG verdict] eq "PASS"}

    # ---- Case H: numeric-equality min_width 0.080 vs summary 0.08 (NOT mismatched) ----
    set h "# numeric equality: min_width 0.080 == 0.08 (NOT mismatched)
MESH vdd1 M5 H 0.080 0.3 8 ok
MESH vss1 M5 H 0.5 0.3 8 ok
SUMMARY total=2 power=1 ground=1 min_width=0.08 max_space=0.3 coverage=100"
    set rH [$fn $h]
    _chk H_total {[dict get $rH total_straps] == 2}
    _chk H_min_width {[dict get $rH min_width] == 0.08}
    _chk H_worst_min {[dict get $rH worst_min_width_strap] eq "vdd1"}
    _chk H_max_space {[dict get $rH max_space] == 0.3}
    _chk H_worst_max {[dict get $rH worst_max_space_strap] eq "vdd1"}
    _chk H_mismatch_empty {[llength [dict get $rH mismatched_summary]] == 0}
    _chk H_verdict {[dict get $rH verdict] eq "PASS"}

    # ---- Case I: short>0 -> FAIL (short is non-skip, included in min_width) ----
    set i "# short_count>0 -> FAIL; short strap still counted in min_width
MESH vdd1 M5 H 0.5 0.3 8 short
MESH vss1 M5 H 0.5 0.3 8 ok
SUMMARY total=2 power=1 ground=1 min_width=0.5 max_space=0.3 coverage=100"
    set rI [$fn $i]
    _chk I_short {[dict get $rI short_count] == 1}
    _chk I_skip {[dict get $rI skip_count] == 0}
    _chk I_min_width {[dict get $rI min_width] == 0.5}
    _chk I_worst_min {[dict get $rI worst_min_width_strap] eq "vdd1"}
    _chk I_mismatch_empty {[llength [dict get $rI mismatched_summary]] == 0}
    _chk I_verdict {[dict get $rI verdict] eq "FAIL"}

    # ---- Case J: open>0 (no short) -> REVIEW ----
    set j "# open_count>0 -> REVIEW
MESH vdd1 M5 H 0.5 0.3 8 open
MESH vss1 M5 H 0.5 0.3 8 ok
SUMMARY total=2 power=1 ground=1 min_width=0.5 max_space=0.3 coverage=100"
    set rJ [$fn $j]
    _chk J_open {[dict get $rJ open_count] == 1}
    _chk J_short {[dict get $rJ short_count] == 0}
    _chk J_mismatch_empty {[llength [dict get $rJ mismatched_summary]] == 0}
    _chk J_verdict {[dict get $rJ verdict] eq "REVIEW"}

    # ---- Case K: no SUMMARY -> INCOMPLETE ----
    set k "# no summary -> INCOMPLETE
MESH vdd1 M5 H 0.5 0.3 8 ok
MESH vss1 M5 H 0.5 0.3 8 ok"
    set rK [$fn $k]
    _chk K_total {[dict get $rK total_straps] == 2}
    _chk K_coverage {[dict get $rK coverage_pct] == 100}
    _chk K_mismatch_empty {[llength [dict get $rK mismatched_summary]] == 0}
    _chk K_verdict {[dict get $rK verdict] eq "INCOMPLETE"}

    # ---- Case L: mismatched SUMMARY (power wrong) -> INCOMPLETE ----
    set l "# mismatched summary: power=5 vs computed 1 -> mismatched
MESH vdd1 M5 H 0.5 0.3 8 ok
MESH vss1 M5 H 0.5 0.3 8 ok
SUMMARY total=2 power=5 ground=1 min_width=0.5 max_space=0.3 coverage=100"
    set rL [$fn $l]
    _chk L_mismatch_len {[llength [dict get $rL mismatched_summary]] == 1}
    _chk L_mismatch_has {[lsearch [dict get $rL mismatched_summary] "power=5 vs 1"] >= 0}
    _chk L_verdict {[dict get $rL verdict] eq "INCOMPLETE"}

    # ---- Case M: empty report -> total=0, coverage=0, min_width=-1.0, worst="" ----
    set m "# empty report (no MESH, no SUMMARY)"
    set rM [$fn $m]
    _chk M_total {[dict get $rM total_straps] == 0}
    _chk M_power {[dict get $rM power_straps] == 0}
    _chk M_ground {[dict get $rM ground_straps] == 0}
    _chk M_unknown {[dict get $rM unknown_straps] == 0}
    _chk M_short {[dict get $rM short_count] == 0}
    _chk M_min_width {[dict get $rM min_width] == -1.0}
    _chk M_max_space {[dict get $rM max_space] == -1.0}
    _chk M_worst_min {[dict get $rM worst_min_width_strap] eq ""}
    _chk M_worst_max {[dict get $rM worst_max_space_strap] eq ""}
    _chk M_coverage {[dict get $rM coverage_pct] == 0}
    _chk M_mismatch_empty {[llength [dict get $rM mismatched_summary]] == 0}
    _chk M_verdict {[dict get $rM verdict] eq "INCOMPLETE"}

    _chk_done
    if {$_chk_fail == 0} { return "ALL_ASSERTS_PASS" } else { return "ASSERTS_FAILED" }
}

set r [check layout_pgmesh_audit]
puts "RESULT:$r"
if {$r eq "ALL_ASSERTS_PASS"} {
    puts "DESIGN_FLOW_VERDICT=PASS"
} else {
    puts "DESIGN_FLOW_VERDICT=FAIL"
}