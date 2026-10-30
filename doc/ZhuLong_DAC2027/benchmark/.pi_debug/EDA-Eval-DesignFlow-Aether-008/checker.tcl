# checker.tcl for layout_via_enclosure_audit
# Builds fixtures inline and asserts on the returned dict. Pure text analysis.
# Prints "RESULT:ALL_ASSERTS_PASS" if every assertion passes, else
# "RESULT:ASSERTS_FAILED" with the first failing assert name.
#
# Keys asserted: total_via_types total_lines pass_count warn_count fail_count
# skip_count worst_via min_enclosure mismatched_summary verdict

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

    # ---- Case A: clean, two via types on different cuts, all PASS;
    #   SUMMARY min_enclosure="0.080" vs computed 0.08 -> NUMERIC equal -> no mismatch
    set a "# Via enclosure check INVX1 at 2026-10-30 08:00:00
VIA vddvia cut=VIA1 bottom=M1 top=M2 enc_bot=0.10 enc_top=0.12 req=0.05 count=3 status=PASS
VIA clkvia cut=VIA1 bottom=M1 top=M2 enc_bot=0.08 enc_top=0.09 req=0.05 count=5 status=PASS
VIA vddvia cut=VIA2 bottom=M2 top=M3 enc_bot=0.11 enc_top=0.13 req=0.05 count=2 status=PASS
SUMMARY vias_checked=3 violations=0 warns=0 skipped=0 min_enclosure=0.080 worst_via=clkvia"
    set rA [$fn $a]
    _chk A_total_via_types {[dict get $rA total_via_types] == 2}
    _chk A_total_lines {[dict get $rA total_lines] == 3}
    _chk A_pass {[dict get $rA pass_count] == 3}
    _chk A_warn {[dict get $rA warn_count] == 0}
    _chk A_fail {[dict get $rA fail_count] == 0}
    _chk A_skip {[dict get $rA skip_count] == 0}
    _chk A_worst {[dict get $rA worst_via] eq "clkvia"}
    _chk A_min {[dict get $rA min_enclosure] == 0.08}
    _chk A_mismatch_empty {[llength [dict get $rA mismatched_summary]] == 0}
    _chk A_verdict {[dict get $rA verdict] eq "PASS"}

    # ---- Case B: one explicit FAIL (enc_bot<req) -> FAIL verdict; SUMMARY matches
    set b "VIA badvia cut=VIA1 bottom=M1 top=M2 enc_bot=0.02 enc_top=0.12 req=0.05 count=2 status=FAIL
VIA goodvia cut=VIA1 bottom=M1 top=M2 enc_bot=0.08 enc_top=0.09 req=0.05 count=4 status=PASS
SUMMARY vias_checked=2 violations=1 warns=0 skipped=0 min_enclosure=0.02 worst_via=badvia"
    set rB [$fn $b]
    _chk B_total_via_types {[dict get $rB total_via_types] == 2}
    _chk B_total_lines {[dict get $rB total_lines] == 2}
    _chk B_fail {[dict get $rB fail_count] == 1}
    _chk B_pass {[dict get $rB pass_count] == 1}
    _chk B_worst {[dict get $rB worst_via] eq "badvia"}
    _chk B_min {[dict get $rB min_enclosure] == 0.02}
    _chk B_mismatch_empty {[llength [dict get $rB mismatched_summary]] == 0}
    _chk B_verdict {[dict get $rB verdict] eq "FAIL"}

    # ---- Case C: duplicate (name,cut) -> LAST-WINS (first FAIL then PASS)
    set c "VIA dvia cut=VIA1 enc_bot=0.02 enc_top=0.12 req=0.05 status=FAIL
VIA dvia cut=VIA1 enc_bot=0.08 enc_top=0.09 req=0.05 status=PASS
SUMMARY vias_checked=1 violations=0 warns=0 skipped=0 min_enclosure=0.08 worst_via=dvia"
    set rC [$fn $c]
    _chk C_total_via_types {[dict get $rC total_via_types] == 1}
    _chk C_total_lines {[dict get $rC total_lines] == 1}
    _chk C_pass {[dict get $rC pass_count] == 1}
    _chk C_fail {[dict get $rC fail_count] == 0}
    _chk C_worst {[dict get $rC worst_via] eq "dvia"}
    _chk C_min {[dict get $rC min_enclosure] == 0.08}
    _chk C_mismatch_empty {[llength [dict get $rC mismatched_summary]] == 0}
    _chk C_verdict {[dict get $rC verdict] eq "PASS"}

    # ---- Case D: status CASE-INSENSITIVE (fail/pass/skip lowercase).
    #   Non-SKIP = a(fail,0.02) + b(pass,0.08); SKIP c(0.01) excluded from min.
    #   -> min_enclosure=0.02, worst_via=a (NOT c, which is SKIP).
    set d "VIA a cut=VIA1 enc_bot=0.02 enc_top=0.12 req=0.05 status=fail
VIA b cut=VIA1 enc_bot=0.08 enc_top=0.09 req=0.05 status=pass
VIA c cut=VIA1 enc_bot=0.01 enc_top=0.01 req=0.05 status=skip
SUMMARY vias_checked=3 violations=1 warns=0 skipped=1 min_enclosure=0.02 worst_via=a"
    set rD [$fn $d]
    _chk D_fail {[dict get $rD fail_count] == 1}
    _chk D_pass {[dict get $rD pass_count] == 1}
    _chk D_skip {[dict get $rD skip_count] == 1}
    _chk D_warn {[dict get $rD warn_count] == 0}
    _chk D_worst {[dict get $rD worst_via] eq "a"}
    _chk D_min {[dict get $rD min_enclosure] == 0.02}
    _chk D_mismatch_empty {[llength [dict get $rD mismatched_summary]] == 0}
    _chk D_verdict {[dict get $rD verdict] eq "FAIL"}

    # ---- Case E: status ABSENT -> infer FAIL (enc<req) / PASS
    set e "VIA a cut=VIA1 enc_bot=0.02 enc_top=0.12 req=0.05
VIA b cut=VIA1 enc_bot=0.08 enc_top=0.09 req=0.05
SUMMARY vias_checked=2 violations=1 warns=0 skipped=0 min_enclosure=0.02 worst_via=a"
    set rE [$fn $e]
    _chk E_fail {[dict get $rE fail_count] == 1}
    _chk E_pass {[dict get $rE pass_count] == 1}
    _chk E_skip {[dict get $rE skip_count] == 0}
    _chk E_warn {[dict get $rE warn_count] == 0}
    _chk E_worst {[dict get $rE worst_via] eq "a"}
    _chk E_min {[dict get $rE min_enclosure] == 0.02}
    _chk E_mismatch_empty {[llength [dict get $rE mismatched_summary]] == 0}
    _chk E_verdict {[dict get $rE verdict] eq "FAIL"}

    # ---- Case F: enc == req -> PASS (inclusive; FAIL only strict <)
    set f "VIA a cut=VIA1 enc_bot=0.05 enc_top=0.05 req=0.05 status=PASS
SUMMARY vias_checked=1 violations=0 warns=0 skipped=0 min_enclosure=0.05 worst_via=a"
    set rF [$fn $f]
    _chk F_pass {[dict get $rF pass_count] == 1}
    _chk F_fail {[dict get $rF fail_count] == 0}
    _chk F_min {[dict get $rF min_enclosure] == 0.05}
    _chk F_worst {[dict get $rF worst_via] eq "a"}
    _chk F_mismatch_empty {[llength [dict get $rF mismatched_summary]] == 0}
    _chk F_verdict {[dict get $rF verdict] eq "PASS"}

    # ---- Case G: missing req -> default 0.0 (always PASS); status absent inferred
    set g "VIA a cut=VIA1 enc_bot=0.02 enc_top=0.03
VIA b cut=VIA1 enc_bot=0.08 enc_top=0.09
SUMMARY vias_checked=2 violations=0 warns=0 skipped=0 min_enclosure=0.02 worst_via=a"
    set rG [$fn $g]
    _chk G_fail {[dict get $rG fail_count] == 0}
    _chk G_pass {[dict get $rG pass_count] == 2}
    _chk G_worst {[dict get $rG worst_via] eq "a"}
    _chk G_min {[dict get $rG min_enclosure] == 0.02}
    _chk G_mismatch_empty {[llength [dict get $rG mismatched_summary]] == 0}
    _chk G_verdict {[dict get $rG verdict] eq "PASS"}

    # ---- Case H: missing enc_bot -> default 0.0; status absent -> FAIL (0<req);
    #              the missing enc_bot=0.0 is included in min_enclosure as 0.0
    set h "VIA a cut=VIA1 enc_top=0.12 req=0.05
VIA b cut=VIA1 enc_bot=0.08 enc_top=0.09 req=0.05 status=PASS
SUMMARY vias_checked=2 violations=1 warns=0 skipped=0 min_enclosure=0.0 worst_via=a"
    set rH [$fn $h]
    _chk H_fail {[dict get $rH fail_count] == 1}
    _chk H_pass {[dict get $rH pass_count] == 1}
    _chk H_worst {[dict get $rH worst_via] eq "a"}
    _chk H_min {[dict get $rH min_enclosure] == 0.0}
    _chk H_mismatch_empty {[llength [dict get $rH mismatched_summary]] == 0}
    _chk H_verdict {[dict get $rH verdict] eq "FAIL"}

    # ---- Case I: SKIP excluded from min_enclosure (SKIP has lowest enclosure)
    set i "VIA a cut=VIA1 enc_bot=0.08 enc_top=0.09 req=0.05 status=PASS
VIA b cut=VIA1 enc_bot=0.005 enc_top=0.005 req=0.05 status=SKIP
SUMMARY vias_checked=2 violations=0 warns=0 skipped=1 min_enclosure=0.08 worst_via=a"
    set rI [$fn $i]
    _chk I_pass {[dict get $rI pass_count] == 1}
    _chk I_skip {[dict get $rI skip_count] == 1}
    _chk I_worst {[dict get $rI worst_via] eq "a"}
    _chk I_min {[dict get $rI min_enclosure] == 0.08}
    _chk I_mismatch_empty {[llength [dict get $rI mismatched_summary]] == 0}
    _chk I_verdict {[dict get $rI verdict] eq "PASS"}

    # ---- Case J: worst_via tie at min_enclosure -> DICTIONARY smallest
    #   via10 (0.05) and via2 (0.05) tie; dictionary: via2 < via10 (2 < 10).
    #   (ASCII string compare would wrongly pick via10.)
    set j "VIA via10 cut=VIA1 enc_bot=0.05 enc_top=0.05 req=0.05 status=PASS
VIA via2 cut=VIA1 enc_bot=0.05 enc_top=0.05 req=0.05 status=PASS
VIA via1 cut=VIA1 enc_bot=0.08 enc_top=0.08 req=0.05 status=PASS
SUMMARY vias_checked=3 violations=0 warns=0 skipped=0 min_enclosure=0.05 worst_via=via2"
    set rJ [$fn $j]
    _chk J_worst {[dict get $rJ worst_via] eq "via2"}
    _chk J_min {[dict get $rJ min_enclosure] == 0.05}
    _chk J_pass {[dict get $rJ pass_count] == 3}
    _chk J_mismatch_empty {[llength [dict get $rJ mismatched_summary]] == 0}
    _chk J_verdict {[dict get $rJ verdict] eq "PASS"}

    # ---- Case K: no SUMMARY, no fails -> INCOMPLETE, mismatched empty
    set k "VIA a cut=VIA1 enc_bot=0.08 enc_top=0.09 req=0.05 status=PASS
VIA b cut=VIA1 enc_bot=0.07 enc_top=0.06 req=0.05 status=PASS"
    set rK [$fn $k]
    _chk K_pass {[dict get $rK pass_count] == 2}
    _chk K_fail {[dict get $rK fail_count] == 0}
    _chk K_worst {[dict get $rK worst_via] eq "b"}
    _chk K_min {[dict get $rK min_enclosure] == 0.06}
    _chk K_mismatch_empty {[llength [dict get $rK mismatched_summary]] == 0}
    _chk K_verdict {[dict get $rK verdict] eq "INCOMPLETE"}

    # ---- Case L: SUMMARY mismatches (3 wrong, 3 absent) -> mismatched has 3;
    #             absent warns/skipped/worst_via NOT reported; verdict INCOMPLETE
    set l "VIA a cut=VIA1 enc_bot=0.08 enc_top=0.09 req=0.05 status=PASS
VIA b cut=VIA1 enc_bot=0.07 enc_top=0.06 req=0.05 status=PASS
SUMMARY vias_checked=5 violations=2 min_enclosure=0.99"
    set rL [$fn $l]
    set ml [dict get $rL mismatched_summary]
    _chk L_mismatch_len {[llength $ml] == 3}
    _chk L_mismatch_vias_checked {[lsearch $ml "vias_checked"] >= 0}
    _chk L_mismatch_violations {[lsearch $ml "violations"] >= 0}
    _chk L_mismatch_min_enclosure {[lsearch $ml "min_enclosure"] >= 0}
    _chk L_mismatch_warns_absent {[lsearch $ml "warns"] < 0}
    _chk L_mismatch_skipped_absent {[lsearch $ml "skipped"] < 0}
    _chk L_mismatch_worst_via_absent {[lsearch $ml "worst_via"] < 0}
    _chk L_fail {[dict get $rL fail_count] == 0}
    _chk L_verdict {[dict get $rL verdict] eq "INCOMPLETE"}

    # ---- Case M: empty report, no SUMMARY -> all zero/empty, min_enclosure=-1.0, INCOMPLETE
    set m "# header only "
    set rM [$fn $m]
    _chk M_total_via_types {[dict get $rM total_via_types] == 0}
    _chk M_total_lines {[dict get $rM total_lines] == 0}
    _chk M_pass {[dict get $rM pass_count] == 0}
    _chk M_fail {[dict get $rM fail_count] == 0}
    _chk M_skip {[dict get $rM skip_count] == 0}
    _chk M_warn {[dict get $rM warn_count] == 0}
    _chk M_worst_empty {[dict get $rM worst_via] eq ""}
    _chk M_min_neg {[dict get $rM min_enclosure] == -1.0}
    _chk M_mismatch_empty {[llength [dict get $rM mismatched_summary]] == 0}
    _chk M_verdict {[dict get $rM verdict] eq "INCOMPLETE"}

    _chk_done
    if {$_chk_pass} { return "ALL_ASSERTS_PASS" } else { return "ASSERTS_FAILED" }
}
