# Naive (wrong) implementation -- deliberately fails several traps:
#  - first-wins dedup (should be last-wins)
#  - below_min uses <= (should be strict <; equal is compliant)
#  - missing actual_density defaults to 0 -> goes to below_min and into min_seen (WRONG)
#  - min_seen/max_seen computed over ALL layers incl. missing-actual-as-0 (WRONG for trap E/D)
#  - fill_shapes missing -> leaves empty -> incr breaks / treated as 0 inconsistently
#  - no lex sort
#  - verdict: only FAIL if below_min, else PASS (no INCOMPLETE for missing/no-summary)
# Used only to PROVE TEETH (that a naive impl fails the checker). Not shipped.
proc layout_density_fill_audit {density_text} {
    array set L {}
    set hasSummary 0
    set sumTL 0; set sumTF 0; set sumMin 0; set sumMax 0

    foreach line [split $density_text "\n"] {
        set line [string trim $line]
        if {$line eq "" || [string index $line 0] eq "#"} { continue }
        if {[string match "LAYER *" $line]} {
            set toks [split $line " \t"]
            set name [lindex $toks 1]
            if {[info exists L($name)]} { continue }        ;# FIRST-WINS (WRONG)
            set min 0; set actual 0; set fill 0
            foreach tok [lrange $toks 2 end] {
                if {[string match "min_density=*" $tok]} {
                    set min [expr {double([string trimright [string range $tok [string length "min_density="] end] "%"])}]
                } elseif {[string match "actual_density=*" $tok]} {
                    set actual [expr {double([string trimright [string range $tok [string length "actual_density="] end] "%"])}]
                } elseif {[string match "fill_shapes=*" $tok]} {
                    set fill [expr {int([string range $tok [string length "fill_shapes="] end])}]
                }
            }
            set L($name) [list $min $actual $fill]
        } elseif {[string match "SUMMARY *" $line]} {
            set hasSummary 1
            foreach tok [lrange [split $line " \t"] 1 end] {
                if {[string match "total_layers=*" $tok]} { set sumTL [string range $tok [string length "total_layers="] end] }
                if {[string match "total_fill_shapes=*" $tok]} { set sumTF [string range $tok [string length "total_fill_shapes="] end] }
            }
        }
    }

    set total_layers [llength [array names L]]
    set total_fill 0
    set below [list]; set compl [list]; set used [list]
    set minS ""; set maxS ""
    foreach name [array names L] {
        lassign $L($name) min actual fill
        incr total_fill $fill
        lappend used $name
        if {$minS eq "" || $actual < $minS} { set minS $actual }
        if {$maxS eq "" || $actual > $maxS} { set maxS $actual }
        if {$actual <= $min} { lappend below $name } else { lappend compl $name }   ;# <= WRONG, no missing handling
    }

    if {[llength $below] > 0} { set verdict FAIL } else { set verdict PASS }   ;# no INCOMPLETE

    return [dict create \
        total_layers $total_layers \
        total_fill_shapes $total_fill \
        below_min_layers $below \
        compliant_layers $compl \
        missing_density_layers [list] \
        min_seen_density $minS \
        max_seen_density $maxS \
        layers_used $used \
        mismatched_summary [list] \
        verdict $verdict]
}
# checker.tcl for layout_density_fill_audit
# Builds fixtures inline and asserts on the returned dict. Pure text analysis.
# Prints "RESULT:ALL_ASSERTS_PASS" if every assertion passes, else
# "RESULT:ASSERTS_FAILED" with the first failing assert name.
#
# Keys asserted: total_layers total_fill_shapes below_min_layers compliant_layers
# missing_density_layers min_seen_density max_seen_density layers_used
# mismatched_summary verdict

if {![info exists _chk_pass]} {
    set _chk_pass 1
    set _chk_fail ""
}
proc _chk {name cond} {
    global _chk_pass _chk_fail
    if {$_chk_pass} {
        if {![uplevel 1 [list expr $cond]]} {
            set _chk_pass 0
            set _chk_fail $name
            puts "ASSERT FAIL: $name"
        }
    }
}
proc _chk_done {} {}

proc check {fn} {
    global _chk_pass _chk_fail
    set _chk_pass 1
    set _chk_fail ""

    # ---- Case A: basic all compliant, summary matches -> PASS
    set a "LAYER M1 min_density=20% target_density=30% actual_density=25% fill_shapes=3
LAYER M2 min_density=20% target_density=30% actual_density=22% fill_shapes=2
SUMMARY total_layers=2 total_fill_shapes=5 min_seen=22% max_seen=25%"
    set rA [$fn $a]
    _chk A_total_layers {[dict get $rA total_layers] == 2}
    _chk A_total_fill {[dict get $rA total_fill_shapes] == 5}
    _chk A_below_empty {[llength [dict get $rA below_min_layers]] == 0}
    _chk A_compliant {[dict get $rA compliant_layers] eq "M1 M2"}
    _chk A_missing_empty {[llength [dict get $rA missing_density_layers]] == 0}
    _chk A_min {[dict get $rA min_seen_density] == 22.0}
    _chk A_max {[dict get $rA max_seen_density] == 25.0}
    _chk A_used {[dict get $rA layers_used] eq "M1 M2"}
    _chk A_mismatch_empty {[llength [dict get $rA mismatched_summary]] == 0}
    _chk A_verdict {[dict get $rA verdict] eq "PASS"}

    # ---- Case B: duplicate layer name LAST-WINS (replace, not sum, not first)
    set b "LAYER M1 min_density=20% target_density=30% actual_density=25% fill_shapes=3
LAYER M1 min_density=20% target_density=30% actual_density=18% fill_shapes=7
SUMMARY total_layers=1 total_fill_shapes=7 min_seen=18% max_seen=18%"
    set rB [$fn $b]
    _chk B_total_layers {[dict get $rB total_layers] == 1}
    _chk B_total_fill {[dict get $rB total_fill_shapes] == 7}
    _chk B_below {[dict get $rB below_min_layers] eq "M1"}
    _chk B_compliant_empty {[llength [dict get $rB compliant_layers]] == 0}
    _chk B_min {[dict get $rB min_seen_density] == 18.0}
    _chk B_max {[dict get $rB max_seen_density] == 18.0}
    _chk B_verdict {[dict get $rB verdict] eq "FAIL"}

    # ---- Case C: STRICT < boundary; actual==min is compliant, actual=min-epsilon is below
    set c "LAYER A min_density=20% target_density=30% actual_density=20% fill_shapes=1
LAYER B min_density=20% target_density=30% actual_density=19.9% fill_shapes=1
SUMMARY total_layers=2 total_fill_shapes=2 min_seen=19.9% max_seen=20%"
    set rC [$fn $c]
    _chk C_below {[dict get $rC below_min_layers] eq "B"}
    _chk C_compliant {[dict get $rC compliant_layers] eq "A"}
    _chk C_min {[dict get $rC min_seen_density] == 19.9}
    _chk C_max {[dict get $rC max_seen_density] == 20.0}
    _chk C_verdict {[dict get $rC verdict] eq "FAIL"}

    # ---- Case D: missing actual_density -> missing_density, excluded from min/max/used
    set d "LAYER M1 min_density=20% target_density=30% fill_shapes=3
LAYER M2 min_density=20% target_density=30% actual_density=25% fill_shapes=2
SUMMARY total_layers=2 total_fill_shapes=5 min_seen=25% max_seen=25%"
    set rD [$fn $d]
    _chk D_total_layers {[dict get $rD total_layers] == 2}
    _chk D_total_fill {[dict get $rD total_fill_shapes] == 5}
    _chk D_missing {[dict get $rD missing_density_layers] eq "M1"}
    _chk D_below_empty {[llength [dict get $rD below_min_layers]] == 0}
    _chk D_compliant {[dict get $rD compliant_layers] eq "M2"}
    _chk D_used {[dict get $rD layers_used] eq "M2"}
    _chk D_min {[dict get $rD min_seen_density] == 25.0}
    _chk D_max {[dict get $rD max_seen_density] == 25.0}
    _chk D_mismatch_empty {[llength [dict get $rD mismatched_summary]] == 0}
    _chk D_verdict {[dict get $rD verdict] eq "INCOMPLETE"}

    # ---- Case E: missing MIN but has actual -> missing_density BUT in min/max_seen + used (TRAP)
    set e "LAYER M1 target_density=30% actual_density=25% fill_shapes=3
LAYER M2 min_density=20% target_density=30% actual_density=22% fill_shapes=2
SUMMARY total_layers=2 total_fill_shapes=5 min_seen=22% max_seen=25%"
    set rE [$fn $e]
    _chk E_missing {[dict get $rE missing_density_layers] eq "M1"}
    _chk E_below_empty {[llength [dict get $rE below_min_layers]] == 0}
    _chk E_compliant {[dict get $rE compliant_layers] eq "M2"}
    _chk E_used {[dict get $rE layers_used] eq "M1 M2"}
    _chk E_min {[dict get $rE min_seen_density] == 22.0}
    _chk E_max {[dict get $rE max_seen_density] == 25.0}
    _chk E_mismatch_empty {[llength [dict get $rE mismatched_summary]] == 0}
    _chk E_verdict {[dict get $rE verdict] eq "INCOMPLETE"}

    # ---- Case F: missing fill_shapes -> default 0
    set f "LAYER M1 min_density=20% target_density=30% actual_density=25%
LAYER M2 min_density=20% target_density=30% actual_density=22% fill_shapes=4
SUMMARY total_layers=2 total_fill_shapes=4 min_seen=22% max_seen=25%"
    set rF [$fn $f]
    _chk F_total_fill {[dict get $rF total_fill_shapes] == 4}
    _chk F_compliant {[dict get $rF compliant_layers] eq "M1 M2"}
    _chk F_mismatch_empty {[llength [dict get $rF mismatched_summary]] == 0}
    _chk F_verdict {[dict get $rF verdict] eq "PASS"}

    # ---- Case G: no SUMMARY -> mismatched empty, verdict INCOMPLETE
    set g "LAYER M1 min_density=20% target_density=30% actual_density=25% fill_shapes=3
LAYER M2 min_density=20% target_density=30% actual_density=28% fill_shapes=2"
    set rG [$fn $g]
    _chk G_total_layers {[dict get $rG total_layers] == 2}
    _chk G_total_fill {[dict get $rG total_fill_shapes] == 5}
    _chk G_min {[dict get $rG min_seen_density] == 25.0}
    _chk G_max {[dict get $rG max_seen_density] == 28.0}
    _chk G_mismatch_empty {[llength [dict get $rG mismatched_summary]] == 0}
    _chk G_verdict {[dict get $rG verdict] eq "INCOMPLETE"}

    # ---- Case H: SUMMARY present, wrong values; absent field NOT reported
    set h "LAYER M1 min_density=20% target_density=30% actual_density=25% fill_shapes=3
SUMMARY total_layers=9 total_fill_shapes=1 min_seen=99%"
    set rH [$fn $h]
    _chk H_mismatch {[dict get $rH mismatched_summary] eq "min_seen total_fill_shapes total_layers"}
    _chk H_below_empty {[llength [dict get $rH below_min_layers]] == 0}
    _chk H_missing_empty {[llength [dict get $rH missing_density_layers]] == 0}
    _chk H_verdict {[dict get $rH verdict] eq "PASS"}

    # ---- Case I: % parsing 85 vs 85.0 numerically equal; min_seen as float
    set i "LAYER A min_density=85% target_density=90% actual_density=85% fill_shapes=1
LAYER B min_density=85.0% target_density=90% actual_density=85.0% fill_shapes=1
SUMMARY total_layers=2 total_fill_shapes=2 min_seen=85% max_seen=85%"
    set rI [$fn $i]
    _chk I_compliant {[dict get $rI compliant_layers] eq "A B"}
    _chk I_min {[dict get $rI min_seen_density] == 85.0}
    _chk I_max {[dict get $rI max_seen_density] == 85.0}
    _chk I_mismatch_empty {[llength [dict get $rI mismatched_summary]] == 0}
    _chk I_verdict {[dict get $rI verdict] eq "PASS"}

    # ---- Case J: below_min + missing_density -> verdict FAIL (priority)
    set j "LAYER A min_density=20% target_density=30% actual_density=10% fill_shapes=1
LAYER B min_density=20% target_density=30% fill_shapes=1
SUMMARY total_layers=2 total_fill_shapes=2 min_seen=10% max_seen=10%"
    set rJ [$fn $j]
    _chk J_below {[dict get $rJ below_min_layers] eq "A"}
    _chk J_missing {[dict get $rJ missing_density_layers] eq "B"}
    _chk J_compliant_empty {[llength [dict get $rJ compliant_layers]] == 0}
    _chk J_used {[dict get $rJ layers_used] eq "A"}
    _chk J_min {[dict get $rJ min_seen_density] == 10.0}
    _chk J_verdict {[dict get $rJ verdict] eq "FAIL"}

    # ---- Case K: missing_density, no below_min, no summary -> INCOMPLETE
    set k "LAYER A min_density=20% target_density=30% fill_shapes=1
LAYER B min_density=20% target_density=30% actual_density=25% fill_shapes=1"
    set rK [$fn $k]
    _chk K_missing {[dict get $rK missing_density_layers] eq "A"}
    _chk K_below_empty {[llength [dict get $rK below_min_layers]] == 0}
    _chk K_compliant {[dict get $rK compliant_layers] eq "B"}
    _chk K_mismatch_empty {[llength [dict get $rK mismatched_summary]] == 0}
    _chk K_verdict {[dict get $rK verdict] eq "INCOMPLETE"}

    # ---- Case L: layers_used = actual-present only, sorted lex; missing excluded from min/max
    set l "LAYER Z min_density=20% target_density=30% fill_shapes=1
LAYER A min_density=20% target_density=30% actual_density=25% fill_shapes=1
LAYER M min_density=20% target_density=30% actual_density=22% fill_shapes=1
SUMMARY total_layers=3 total_fill_shapes=3 min_seen=22% max_seen=25%"
    set rL [$fn $l]
    _chk L_total_layers {[dict get $rL total_layers] == 3}
    _chk L_used {[dict get $rL layers_used] eq "A M"}
    _chk L_missing {[dict get $rL missing_density_layers] eq "Z"}
    _chk L_compliant {[dict get $rL compliant_layers] eq "A M"}
    _chk L_min {[dict get $rL min_seen_density] == 22.0}
    _chk L_max {[dict get $rL max_seen_density] == 25.0}
    _chk L_verdict {[dict get $rL verdict] eq "INCOMPLETE"}

    # ---- Case M: empty report -> 0 layers, min/max "", verdict INCOMPLETE (no summary)
    set m "# density fill report (empty)"
    set rM [$fn $m]
    _chk M_total_layers {[dict get $rM total_layers] == 0}
    _chk M_total_fill {[dict get $rM total_fill_shapes] == 0}
    _chk M_below_empty {[llength [dict get $rM below_min_layers]] == 0}
    _chk M_compliant_empty {[llength [dict get $rM compliant_layers]] == 0}
    _chk M_missing_empty {[llength [dict get $rM missing_density_layers]] == 0}
    _chk M_used_empty {[llength [dict get $rM layers_used]] == 0}
    _chk M_min_empty {[dict get $rM min_seen_density] eq ""}
    _chk M_max_empty {[dict get $rM max_seen_density] eq ""}
    _chk M_mismatch_empty {[llength [dict get $rM mismatched_summary]] == 0}
    _chk M_verdict {[dict get $rM verdict] eq "INCOMPLETE"}

    _chk_done
    if {$_chk_pass} { return "ALL_ASSERTS_PASS" } else { return "ASSERTS_FAILED" }
}
set r [check layout_density_fill_audit]; puts "NAIVE_RESULT:$r"
