# checker.tcl for layout_drc_audit
# Builds fixtures inline and asserts on the returned dict. Pure text analysis.
# Prints "RESULT:ALL_ASSERTS_PASS" if every assertion passes, else
# "RESULT:ASSERTS_FAILED" with the first failing assert name.
#
# Keys asserted: total_rules total_violations error_count warning_count
# checked_rules duplicate_rule_names per_layer_errors mismatched_summary
# layers_used verdict

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
    # ---- Case A: clean, no violations, has SUMMARY -> PASS, totals 0
    set a "# DRC run INVX1 at 2026-10-30 06:00:00
RULE R1 layer=M1 count=0 severity=err
RULE R2 layer=M2 count=0 severity=warn
SUMMARY total=0 errors=0 warnings=0 checked=2"
    set rA [$fn $a]
    _chk A_total_rules {[dict get $rA total_rules] == 2}
    _chk A_total_violations {[dict get $rA total_violations] == 0}
    _chk A_error_count {[dict get $rA error_count] == 0}
    _chk A_warning_count {[dict get $rA warning_count] == 0}
    _chk A_checked_rules {[dict get $rA checked_rules] == 2}
    _chk A_duplicate_empty {[llength [dict get $rA duplicate_rule_names]] == 0}
    _chk A_mismatch_empty {[llength [dict get $rA mismatched_summary]] == 0}
    _chk A_verdict {[dict get $rA verdict] eq "PASS"}

    # ---- Case B: severity case-insensitive (ERR, Err, err all errors)
    set b "RULE R1 layer=M1 count=3 severity=ERR
RULE R2 layer=M2 count=2 severity=Err
RULE R3 layer=M3 count=1 severity=err
SUMMARY total=6 errors=6 warnings=0 checked=3"
    set rB [$fn $b]
    _chk B_error_count {[dict get $rB error_count] == 6}
    _chk B_warning_count {[dict get $rB warning_count] == 0}
    _chk B_total_violations {[dict get $rB total_violations] == 6}
    _chk B_verdict {[dict get $rB verdict] eq "FAIL"}

    # ---- Case C: last-wins dedup by rule name (R1 redefined -> count 5 wins)
    set c "RULE R1 layer=M1 count=2 severity=err
RULE R1 layer=M1 count=5 severity=err
SUMMARY total=5 errors=5 warnings=0 checked=1"
    set rC [$fn $c]
    _chk C_total_rules {[dict get $rC total_rules] == 1}
    _chk C_total_violations {[dict get $rC total_violations] == 5}
    _chk C_duplicate {[llength [dict get $rC duplicate_rule_names]] == 1}
    _chk C_duplicate_val {[lindex [dict get $rC duplicate_rule_names] 0] eq "R1"}
    _chk C_checked_rules {[dict get $rC checked_rules] == 1}

    # ---- Case D: zero-count rule still counts as checked (not skipped)
    set d "RULE Z1 layer=M1 count=0 severity=err
RULE Z2 layer=M2 count=4 severity=err
SUMMARY total=4 errors=4 warnings=0 checked=2"
    set rD [$fn $d]
    _chk D_checked_rules {[dict get $rD checked_rules] == 2}
    _chk D_total_violations {[dict get $rD total_violations] == 4}

    # ---- Case E: missing SUMMARY -> verdict INCOMPLETE (not PASS), mismatch empty
    set e "RULE R1 layer=M1 count=0 severity=err"
    set rE [$fn $e]
    _chk E_verdict {[dict get $rE verdict] eq "INCOMPLETE"}
    _chk E_mismatch_empty {[llength [dict get $rE mismatched_summary]] == 0}

    # ---- Case F: mismatched_summary detects wrong total & errors
    set f "RULE R1 layer=M1 count=3 severity=err
SUMMARY total=99 errors=1 warnings=0 checked=1"
    set rF [$fn $f]
    set mm [dict get $rF mismatched_summary]
    _chk F_mismatch_len {[llength $mm] == 2}
    _chk F_mismatch_has_total {"total" in $mm}
    _chk F_mismatch_has_errors {"errors" in $mm}
    _chk F_no_mismatch_checked {"checked" ni $mm}

    # ---- Case G: per_layer_errors only err layers, sorted, warn excluded
    set g "RULE R1 layer=M2 count=4 severity=err
RULE R2 layer=M1 count=2 severity=err
RULE R3 layer=M1 count=1 severity=warn
SUMMARY total=7 errors=6 warnings=1 checked=3"
    set rG [$fn $g]
    set pl [dict get $rG per_layer_errors]
    _chk G_per_layer_keys {[llength $pl] == 4}
    _chk G_per_layer_sorted1 {[lindex $pl 0] eq "M1"}
    _chk G_per_layer_sorted2 {[lindex $pl 2] eq "M2"}
    _chk G_per_layer_M1 {[lindex $pl 1] == 2}
    _chk G_per_layer_M2 {[lindex $pl 3] == 4}
    _chk G_warning_count {[dict get $rG warning_count] == 1}

    # ---- Case H: verdict WARN when only warnings, no errors, summary present
    set h "RULE W1 layer=M1 count=2 severity=warn
SUMMARY total=2 errors=0 warnings=2 checked=1"
    set rH [$fn $h]
    _chk H_verdict {[dict get $rH verdict] eq "WARN"}
    _chk H_error_count {[dict get $rH error_count] == 0}

    # ---- Case I: verdict priority error>warn (errors present even with warns)
    set i "RULE R1 layer=M1 count=1 severity=err
RULE R2 layer=M2 count=5 severity=warn
SUMMARY total=6 errors=1 warnings=5 checked=2"
    set rI [$fn $i]
    _chk I_verdict {[dict get $rI verdict] eq "FAIL"}

    # ---- Case J: layers_used sorted, includes warn+err layers
    set j "RULE R1 layer=M3 count=1 severity=err
RULE R2 layer=M1 count=2 severity=warn
SUMMARY total=3 errors=1 warnings=2 checked=2"
    set rJ [$fn $j]
    set lu [dict get $rJ layers_used]
    _chk J_layers_len {[llength $lu] == 2}
    _chk J_layers_sorted {[lindex $lu 0] eq "M1" && [lindex $lu 1] eq "M3"}

    # ---- Case K: mismatched_summary empty when SUMMARY correct (all match)
    set k "RULE R1 layer=M1 count=3 severity=err
RULE R2 layer=M2 count=2 severity=warn
SUMMARY total=5 errors=3 warnings=2 checked=2"
    set rK [$fn $k]
    _chk K_mismatch_empty {[llength [dict get $rK mismatched_summary]] == 0}
    _chk K_verdict {[dict get $rK verdict] eq "FAIL"}

    # ---- Case L: duplicate_rule_names reports name seen 3x, dedup sorted
    set l "RULE DUP layer=M1 count=1 severity=err
RULE AAA layer=M2 count=1 severity=err
RULE DUP layer=M1 count=2 severity=err
RULE DUP layer=M1 count=3 severity=err
SUMMARY total=4 errors=4 warnings=0 checked=2"
    set rL [$fn $l]
    set dn [dict get $rL duplicate_rule_names]
    _chk L_dup_len {[llength $dn] == 1}
    _chk L_dup_val {[lindex $dn 0] eq "DUP"}
    _chk L_total_rules {[dict get $rL total_rules] == 2}
    _chk L_total_violations {[dict get $rL total_violations] == 4}

    # ---- Case M: multiple mismatched fields sorted (errors, total, warnings)
    set m "RULE R1 layer=M1 count=1 severity=err
RULE R2 layer=M2 count=1 severity=warn
SUMMARY total=99 errors=88 warnings=77 checked=2"
    set rM [$fn $m]
    set mmM [dict get $rM mismatched_summary]
    _chk M_mismatch_len {[llength $mmM] == 3}
    _chk M_mismatch_sorted {[lindex $mmM 0] eq "errors" && [lindex $mmM 1] eq "total" && [lindex $mmM 2] eq "warnings"}

    _chk_done
    if {$_chk_pass} { return "ALL_ASSERTS_PASS" } else { return "ASSERTS_FAILED" }
}
