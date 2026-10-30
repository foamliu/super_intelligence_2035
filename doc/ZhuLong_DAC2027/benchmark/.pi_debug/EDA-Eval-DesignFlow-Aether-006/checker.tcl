# checker.tcl for layout_metalfill_target_audit
# Builds fixtures inline and asserts on the returned dict. Pure text analysis.
# Prints "RESULT:ALL_ASSERTS_PASS" if every assertion passes, else
# "RESULT:ASSERTS_FAILED" with the first failing assert name.
#
# Keys asserted: total_layers total_fill underfill_layers met_layers
# missing_target_layers zero_fill_met_layers min_density_layer
# max_density_layer mismatched_summary verdict

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
proc _chk_done {} {
    global _chk_pass _chk_fail
    if {$_chk_pass} {
        puts "RESULT:ALL_ASSERTS_PASS"
    } else {
        puts "RESULT:ASSERTS_FAILED:$_chk_fail"
    }
}

proc check {fn} {
    global _chk_pass _chk_fail

    # ---- Case A: clean, distinct layers, all met, SUMMARY present -> PASS
    set a "# Metal-fill density INVX1 at 2026-10-30 07:00:00
LAYER M1 target=80 actual=85.5 fill_count=12
LAYER M2 target=80 actual=72.3 fill_count=8
LAYER VIA1 target=40 actual=40.0 fill_count=0
SUMMARY total_layers=3 total_fill=20 min_density=40.0 max_density=85.5"
    set rA [$fn $a]
    _chk A_total_layers {[dict get $rA total_layers] == 3}
    _chk A_total_fill {[dict get $rA total_fill] == 20}
    _chk A_underfill_len {[llength [dict get $rA underfill_layers]] == 1}
    _chk A_underfill_val {[lindex [dict get $rA underfill_layers] 0] eq "M2"}
    _chk A_met_len {[llength [dict get $rA met_layers]] == 2}
    _chk A_met_sorted {[lindex [dict get $rA met_layers] 0] eq "M1" && [lindex [dict get $rA met_layers] 1] eq "VIA1"}
    _chk A_missing_empty {[llength [dict get $rA missing_target_layers]] == 0}
    _chk A_zero_fill_len {[llength [dict get $rA zero_fill_met_layers]] == 1}
    _chk A_zero_fill_val {[lindex [dict get $rA zero_fill_met_layers] 0] eq "VIA1"}
    _chk A_min {[dict get $rA min_density_layer] eq "VIA1"}
    _chk A_max {[dict get $rA max_density_layer] eq "M1"}
    _chk A_mismatch_empty {[llength [dict get $rA mismatched_summary]] == 0}
    _chk A_verdict {[dict get $rA verdict] eq "FAIL"}

    # ---- Case B: SUMMARY numeric equality (72.30 == 72.3) -> no mismatch
    set b "LAYER A target=80 actual=72.30 fill_count=5
LAYER B target=80 actual=85.5 fill_count=6
SUMMARY total_layers=2 total_fill=11 min_density=72.3 max_density=85.50"
    set rB [$fn $b]
    _chk B_mismatch_empty {[llength [dict get $rB mismatched_summary]] == 0}
    _chk B_underfill_len {[llength [dict get $rB underfill_layers]] == 1}
    _chk B_underfill_val {[lindex [dict get $rB underfill_layers] 0] eq "A"}
    _chk B_met_len {[llength [dict get $rB met_layers]] == 1}
    _chk B_verdict {[dict get $rB verdict] eq "FAIL"}

    # ---- Case C: duplicate layer NAME -> last-wins (replace, not sum fill)
    set c "LAYER M1 target=80 actual=85 fill_count=3
LAYER M1 target=80 actual=70 fill_count=9
SUMMARY total_layers=1 total_fill=9"
    set rC [$fn $c]
    _chk C_total_layers {[dict get $rC total_layers] == 1}
    _chk C_total_fill {[dict get $rC total_fill] == 9}
    _chk C_underfill_len {[llength [dict get $rC underfill_layers]] == 1}
    _chk C_underfill_val {[lindex [dict get $rC underfill_layers] 0] eq "M1"}
    _chk C_met_empty {[llength [dict get $rC met_layers]] == 0}
    _chk C_mismatch_empty {[llength [dict get $rC mismatched_summary]] == 0}
    _chk C_verdict {[dict get $rC verdict] eq "FAIL"}

    # ---- Case D: underfill present -> FAIL; met layers also reported
    set d "LAYER A target=90 actual=80 fill_count=4
LAYER B target=50 actual=60 fill_count=2
SUMMARY total_layers=2 total_fill=6 min_density=60 max_density=80"
    set rD [$fn $d]
    _chk D_underfill_len {[llength [dict get $rD underfill_layers]] == 1}
    _chk D_underfill_val {[lindex [dict get $rD underfill_layers] 0] eq "A"}
    _chk D_met_len {[llength [dict get $rD met_layers]] == 1}
    _chk D_met_val {[lindex [dict get $rD met_layers] 0] eq "B"}
    _chk D_zero_fill_empty {[llength [dict get $rD zero_fill_met_layers]] == 0}
    _chk D_min {[dict get $rD min_density_layer] eq "B"}
    _chk D_max {[dict get $rD max_density_layer] eq "A"}
    _chk D_mismatch_empty {[llength [dict get $rD mismatched_summary]] == 0}
    _chk D_verdict {[dict get $rD verdict] eq "FAIL"}

    # ---- Case E: missing target -> missing_target_layers, NOT underfill/met, INCOMPLETE
    set e "LAYER M1 actual=85 fill_count=10
LAYER M2 target=80 actual=85 fill_count=5
SUMMARY total_layers=2 total_fill=15 min_density=85 max_density=85"
    set rE [$fn $e]
    _chk E_missing_len {[llength [dict get $rE missing_target_layers]] == 1}
    _chk E_missing_val {[lindex [dict get $rE missing_target_layers] 0] eq "M1"}
    _chk E_underfill_empty {[llength [dict get $rE underfill_layers]] == 0}
    _chk E_met_len {[llength [dict get $rE met_layers]] == 1}
    _chk E_met_val {[lindex [dict get $rE met_layers] 0] eq "M2"}
    _chk E_total_layers {[dict get $rE total_layers] == 2}
    _chk E_verdict {[dict get $rE verdict] eq "INCOMPLETE"}

    # ---- Case F: missing actual -> actual=0.0 -> underfill if target>0; min density
    set f "LAYER A target=80 fill_count=3
LAYER B target=0 actual=0 fill_count=0
SUMMARY total_layers=2 total_fill=3 min_density=0 max_density=0"
    set rF [$fn $f]
    _chk F_underfill_len {[llength [dict get $rF underfill_layers]] == 1}
    _chk F_underfill_val {[lindex [dict get $rF underfill_layers] 0] eq "A"}
    _chk F_met_len {[llength [dict get $rF met_layers]] == 1}
    _chk F_met_val {[lindex [dict get $rF met_layers] 0] eq "B"}
    _chk F_min {[dict get $rF min_density_layer] eq "A"}
    _chk F_max {[dict get $rF max_density_layer] eq "A"}
    _chk F_verdict {[dict get $rF verdict] eq "FAIL"}

    # ---- Case G: missing fill_count -> default 0; met layer -> zero_fill_met
    set g "LAYER A target=80 actual=90
LAYER B target=80 actual=85 fill_count=4
SUMMARY total_layers=2 total_fill=4 min_density=85 max_density=90"
    set rG [$fn $g]
    _chk G_total_fill {[dict get $rG total_fill] == 4}
    _chk G_met_len {[llength [dict get $rG met_layers]] == 2}
    _chk G_zero_fill_len {[llength [dict get $rG zero_fill_met_layers]] == 1}
    _chk G_zero_fill_val {[lindex [dict get $rG zero_fill_met_layers] 0] eq "A"}
    _chk G_underfill_empty {[llength [dict get $rG underfill_layers]] == 0}
    _chk G_verdict {[dict get $rG verdict] eq "PASS"}

    # ---- Case H: min/max density tie -> lexicographically smallest name wins
    set h "LAYER Z target=50 actual=70 fill_count=1
LAYER A target=50 actual=70 fill_count=1
LAYER M target=50 actual=70 fill_count=1
SUMMARY total_layers=3 total_fill=3 min_density=70 max_density=70"
    set rH [$fn $h]
    _chk H_min {[dict get $rH min_density_layer] eq "A"}
    _chk H_max {[dict get $rH max_density_layer] eq "A"}
    _chk H_met_len {[llength [dict get $rH met_layers]] == 3}
    _chk H_underfill_empty {[llength [dict get $rH underfill_layers]] == 0}
    _chk H_verdict {[dict get $rH verdict] eq "PASS"}

    # ---- Case I: verdict priority underfill(FAIL) > missing_target(INCOMPLETE)
    set i "LAYER A target=90 actual=80 fill_count=2
LAYER B actual=85 fill_count=3
SUMMARY total_layers=2 total_fill=5 min_density=80 max_density=85"
    set rI [$fn $i]
    _chk I_underfill_len {[llength [dict get $rI underfill_layers]] == 1}
    _chk I_underfill_val {[lindex [dict get $rI underfill_layers] 0] eq "A"}
    _chk I_missing_len {[llength [dict get $rI missing_target_layers]] == 1}
    _chk I_missing_val {[lindex [dict get $rI missing_target_layers] 0] eq "B"}
    _chk I_verdict {[dict get $rI verdict] eq "FAIL"}

    # ---- Case J: no SUMMARY, no underfill, no missing -> INCOMPLETE, mismatched empty
    set j "LAYER A target=80 actual=85 fill_count=3
LAYER B target=80 actual=90 fill_count=2"
    set rJ [$fn $j]
    _chk J_mismatch_empty {[llength [dict get $rJ mismatched_summary]] == 0}
    _chk J_underfill_empty {[llength [dict get $rJ underfill_layers]] == 0}
    _chk J_verdict {[dict get $rJ verdict] eq "INCOMPLETE"}

    # ---- Case K: SUMMARY mismatches reported; absent fields NOT reported
    set k "LAYER A target=80 actual=85 fill_count=3
LAYER B target=80 actual=90 fill_count=2
SUMMARY total_layers=5 total_fill=99 max_density=85"
    set rK [$fn $k]
    set mk [dict get $rK mismatched_summary]
    _chk K_mismatch_len {[llength $mk] == 3}
    _chk K_mismatch_total_layers {[lsearch $mk "total_layers"] >= 0}
    _chk K_mismatch_total_fill {[lsearch $mk "total_fill"] >= 0}
    _chk K_mismatch_max_density {[lsearch $mk "max_density"] >= 0}
    _chk K_mismatch_min_density_absent {[lsearch $mk "min_density"] < 0}
    _chk K_verdict {[dict get $rK verdict] eq "PASS"}

    # ---- Case L: empty report -> all empty, min/max "", mismatched empty, INCOMPLETE
    set l "# header only
"
    set rL [$fn $l]
    _chk L_total_layers {[dict get $rL total_layers] == 0}
    _chk L_total_fill {[dict get $rL total_fill] == 0}
    _chk L_underfill_empty {[llength [dict get $rL underfill_layers]] == 0}
    _chk L_met_empty {[llength [dict get $rL met_layers]] == 0}
    _chk L_missing_empty {[llength [dict get $rL missing_target_layers]] == 0}
    _chk L_zero_fill_empty {[llength [dict get $rL zero_fill_met_layers]] == 0}
    _chk L_min_empty {[dict get $rL min_density_layer] eq ""}
    _chk L_max_empty {[dict get $rL max_density_layer] eq ""}
    _chk L_mismatch_empty {[llength [dict get $rL mismatched_summary]] == 0}
    _chk L_verdict {[dict get $rL verdict] eq "INCOMPLETE"}

    # ---- Case M: empty report WITH SUMMARY present + min/max density -> mismatched
    set m "# header
SUMMARY total_layers=0 total_fill=0 min_density=0 max_density=0"
    set rM [$fn $m]
    set mm [dict get $rM mismatched_summary]
    _chk M_mismatch_min {[lsearch $mm "min_density"] >= 0}
    _chk M_mismatch_max {[lsearch $mm "max_density"] >= 0}
    _chk M_mismatch_total_layers_absent {[lsearch $mm "total_layers"] < 0}
    _chk M_verdict {[dict get $rM verdict] eq "PASS"}

    _chk_done
    if {$_chk_pass} { return "ALL_ASSERTS_PASS" } else { return "ASSERTS_FAILED" }
}
