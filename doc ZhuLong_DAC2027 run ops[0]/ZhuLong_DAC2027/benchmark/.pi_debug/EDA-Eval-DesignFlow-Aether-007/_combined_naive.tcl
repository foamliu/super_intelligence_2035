# Naive implementation: layout_antenna_audit
# Intentionally WRONG on several traps so the checker proves the teeth:
#  - status case-SENSITIVE (only matches uppercase FAIL/PASS/SKIP/WARN)
#  - first-wins dedup (keeps earliest occurrence of a (net,layer) pair)
#  - ratio >= limit -> FAIL (not strict)
#  - missing limit -> 0.0 (not 400)
#  - missing ratio -> skip line from max (treated as -1.0)
#  - max_ratio over ALL lines (including SKIP)
#  - worst_net = first max encountered (no lex tie-break)
#  - mismatched_summary: STRING compare for max_ratio (so "100.0" != "100")
#  - verdict: ignores mismatched_summary (only FAIL if fail_count>0, else PASS)

proc _ntoks {line} {
    return [regexp -all -inline -- {[^[:space:]]+} $line]
}
proc _nstrip {tok prefix} {
    return [string range $tok [string length $prefix] end]
}

proc layout_antenna_audit {report_text} {
    set nl [format %c 10]
    set lines [split $report_text $nl]

    array set rec {}
    set order {}
    set netsSeen {}
    set summarySeen 0
    set sumNC ""; set sumNC_has 0
    set sumV "";  set sumV_has 0
    set sumW "";  set sumW_has 0
    set sumS "";  set sumS_has 0
    set sumMR ""; set sumMR_has 0
    set sumWN ""; set sumWN_has 0

    foreach raw $lines {
        set line [string trim $raw]
        if {$line eq ""} { continue }
        if {[string index $line 0] eq "#"} { continue }
        set toks [_ntoks $line]
        if {[llength $toks] == 0} { continue }
        set kw [lindex $toks 0]

        if {$kw eq "NET"} {
            set net [lindex $toks 1]
            set layer ""
            set ratio -1.0; set hasR 0
            set limit 0.0; set hasL 0
            set status "PASS"
            foreach t [lrange $toks 2 end] {
                if {[string match "layer=*" $t]} {
                    set layer [_nstrip $t "layer="]
                } elseif {[string match "ratio=*" $t]} {
                    set ratio [_nstrip $t "ratio="]; set hasR 1
                } elseif {[string match "limit=*" $t]} {
                    set limit [_nstrip $t "limit="]; set hasL 1
                } elseif {[string match "status=*" $t]} {
                    set status [_nstrip $t "status="]
                }
            }
            # naive: status absent -> PASS (not inferred from ratio)
            if {$status eq ""} { set status "PASS" }
            # naive: status taken literally (case-SENSITIVE) -- lowercase won't match
            set key [list $net $layer]
            if {![info exists rec($key)]} {
                # first-wins: keep this one
                lappend order $key
                if {[lsearch -exact $netsSeen $net] < 0} { lappend netsSeen $net }
                set ratioVal [expr {double($ratio)}]
                set limitVal [expr {double($limit)}]
                set rec($key) [list $ratioVal $limitVal $status]
            }
            ;# else: ignore duplicates (first-wins)
        } elseif {$kw eq "SUMMARY"} {
            set summarySeen 1
            foreach t [lrange $toks 1 end] {
                if {[string match "nets_checked=*" $t]} {
                    set sumNC [_nstrip $t "nets_checked="]; set sumNC_has 1
                } elseif {[string match "violations=*" $t]} {
                    set sumV [_nstrip $t "violations="]; set sumV_has 1
                } elseif {[string match "warns=*" $t]} {
                    set sumW [_nstrip $t "warns="]; set sumW_has 1
                } elseif {[string match "skipped=*" $t]} {
                    set sumS [_nstrip $t "skipped="]; set sumS_has 1
                } elseif {[string match "max_ratio=*" $t]} {
                    set sumMR [_nstrip $t "max_ratio="]; set sumMR_has 1
                } elseif {[string match "worst_net=*" $t]} {
                    set sumWN [_nstrip $t "worst_net="]; set sumWN_has 1
                }
            }
        }
    }

    set total_nets [llength $netsSeen]
    set total_lines [llength $order]
    set pass_count 0; set warn_count 0; set fail_count 0; set skip_count 0
    set max_ratio -1.0
    set worst_net ""

    foreach key $order {
        set r $rec($key)
        set ratioVal [lindex $r 0]
        set st [lindex $r 2]
        switch -- $st {
            PASS { incr pass_count }
            WARN { incr warn_count }
            FAIL { incr fail_count }
            SKIP { incr skip_count }
            default { incr pass_count }
        }
        # naive: max over ALL lines (including SKIP); first max wins (no tie-break)
        if {$ratioVal > $max_ratio} {
            set max_ratio $ratioVal
            set worst_net [lindex $key 0]
        }
    }

    set mismatched {}
    if {$summarySeen} {
        if {$sumNC_has} {
            if {[scan $sumNC %d] != $total_lines} { lappend mismatched "nets_checked" }
        }
        if {$sumV_has} {
            if {[scan $sumV %d] != $fail_count} { lappend mismatched "violations" }
        }
        if {$sumW_has} {
            if {[scan $sumW %d] != $warn_count} { lappend mismatched "warns" }
        }
        if {$sumS_has} {
            if {[scan $sumS %d] != $skip_count} { lappend mismatched "skipped" }
        }
        if {$sumMR_has} {
            # naive: STRING compare (so "100.0" != "100")
            if {$sumMR ne $max_ratio} { lappend mismatched "max_ratio" }
        }
        if {$sumWN_has} {
            if {$sumWN ne $worst_net} { lappend mismatched "worst_net" }
        }
    }
    set mismatched [lsort -dictionary $mismatched]

    # naive verdict: ignores mismatched (only FAIL if fail_count>0 else PASS)
    if {$fail_count > 0} {
        set verdict "FAIL"
    } else {
        set verdict "PASS"
    }

    return [dict create \
        total_nets $total_nets \
        total_lines $total_lines \
        pass_count $pass_count \
        warn_count $warn_count \
        fail_count $fail_count \
        skip_count $skip_count \
        worst_net $worst_net \
        max_ratio $max_ratio \
        mismatched_summary $mismatched \
        verdict $verdict]
}
# checker.tcl for layout_antenna_audit
# Builds fixtures inline and asserts on the returned dict. Pure text analysis.
# Prints "RESULT:ALL_ASSERTS_PASS" if every assertion passes, else
# "RESULT:ASSERTS_FAILED" with the first failing assert name.
#
# Keys asserted: total_nets total_lines pass_count warn_count fail_count
# skip_count worst_net max_ratio mismatched_summary verdict

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

    # ---- Case A: clean, one net on two layers, all PASS, SUMMARY numeric eq
    #   (max_ratio="100.0" vs computed 100 -> numeric equal -> no mismatch)
    set a "# Antenna check INVX1 at 2026-10-30 08:00:00
NET clk layer=M1 gate_area=20 diode_area=0 ratio=50 limit=400 status=PASS
NET clk layer=M2 gate_area=15 diode_area=0 ratio=60 limit=400 status=PASS
NET vdd layer=M1 gate_area=5 diode_area=0 ratio=100 limit=400 status=PASS
SUMMARY nets_checked=3 violations=0 warns=0 skipped=0 max_ratio=100.0 worst_net=vdd"
    set rA [$fn $a]
    _chk A_total_nets {[dict get $rA total_nets] == 2}
    _chk A_total_lines {[dict get $rA total_lines] == 3}
    _chk A_pass {[dict get $rA pass_count] == 3}
    _chk A_warn {[dict get $rA warn_count] == 0}
    _chk A_fail {[dict get $rA fail_count] == 0}
    _chk A_skip {[dict get $rA skip_count] == 0}
    _chk A_worst {[dict get $rA worst_net] eq "vdd"}
    _chk A_max {[dict get $rA max_ratio] == 100}
    _chk A_mismatch_empty {[llength [dict get $rA mismatched_summary]] == 0}
    _chk A_verdict {[dict get $rA verdict] eq "PASS"}

    # ---- Case B: one explicit FAIL (ratio>limit) -> FAIL verdict; SUMMARY matches
    set b "NET n1 layer=M1 gate_area=10 ratio=500 limit=400 status=FAIL
NET n2 layer=M1 gate_area=10 ratio=50 limit=400 status=PASS
SUMMARY nets_checked=2 violations=1 warns=0 skipped=0 max_ratio=500 worst_net=n1"
    set rB [$fn $b]
    _chk B_total_nets {[dict get $rB total_nets] == 2}
    _chk B_total_lines {[dict get $rB total_lines] == 2}
    _chk B_fail {[dict get $rB fail_count] == 1}
    _chk B_pass {[dict get $rB pass_count] == 1}
    _chk B_worst {[dict get $rB worst_net] eq "n1"}
    _chk B_max {[dict get $rB max_ratio] == 500}
    _chk B_mismatch_empty {[llength [dict get $rB mismatched_summary]] == 0}
    _chk B_verdict {[dict get $rB verdict] eq "FAIL"}

    # ---- Case C: duplicate (net,layer) -> LAST-WINS (first FAIL then PASS)
    set c "NET n1 layer=M1 ratio=500 limit=400 status=FAIL
NET n1 layer=M1 ratio=50 limit=400 status=PASS
SUMMARY nets_checked=1 violations=0 warns=0 skipped=0 max_ratio=50 worst_net=n1"
    set rC [$fn $c]
    _chk C_total_nets {[dict get $rC total_nets] == 1}
    _chk C_total_lines {[dict get $rC total_lines] == 1}
    _chk C_pass {[dict get $rC pass_count] == 1}
    _chk C_fail {[dict get $rC fail_count] == 0}
    _chk C_worst {[dict get $rC worst_net] eq "n1"}
    _chk C_max {[dict get $rC max_ratio] == 50}
    _chk C_mismatch_empty {[llength [dict get $rC mismatched_summary]] == 0}
    _chk C_verdict {[dict get $rC verdict] eq "PASS"}

    # ---- Case D: status CASE-INSENSITIVE (fail/pass/skip lowercase).
    #   Non-SKIP lines = a(fail,500) + b(pass,50); SKIP c(999) excluded.
    #   -> max_ratio=500, worst_net=a (NOT c, which is SKIP).
    set d "NET a layer=M1 ratio=500 limit=400 status=fail
NET b layer=M1 ratio=50 limit=400 status=pass
NET c layer=M1 ratio=999 limit=400 status=skip
SUMMARY nets_checked=3 violations=1 warns=0 skipped=1 max_ratio=500 worst_net=a"
    set rD [$fn $d]
    _chk D_fail {[dict get $rD fail_count] == 1}
    _chk D_pass {[dict get $rD pass_count] == 1}
    _chk D_skip {[dict get $rD skip_count] == 1}
    _chk D_warn {[dict get $rD warn_count] == 0}
    _chk D_worst {[dict get $rD worst_net] eq "a"}
    _chk D_max {[dict get $rD max_ratio] == 500}
    _chk D_mismatch_empty {[llength [dict get $rD mismatched_summary]] == 0}
    _chk D_verdict {[dict get $rD verdict] eq "FAIL"}

    # ---- Case E: status ABSENT -> infer FAIL (ratio>limit) / PASS (ratio<=limit)
    set e "NET a layer=M1 ratio=500 limit=400
NET b layer=M1 ratio=50 limit=400
SUMMARY nets_checked=2 violations=1 warns=0 skipped=0 max_ratio=500 worst_net=a"
    set rE [$fn $e]
    _chk E_fail {[dict get $rE fail_count] == 1}
    _chk E_pass {[dict get $rE pass_count] == 1}
    _chk E_skip {[dict get $rE skip_count] == 0}
    _chk E_warn {[dict get $rE warn_count] == 0}
    _chk E_worst {[dict get $rE worst_net] eq "a"}
    _chk E_max {[dict get $rE max_ratio] == 500}
    _chk E_mismatch_empty {[llength [dict get $rE mismatched_summary]] == 0}
    _chk E_verdict {[dict get $rE verdict] eq "FAIL"}

    # ---- Case F: ratio == limit -> PASS (inclusive; FAIL only strict >)
    set f "NET a layer=M1 ratio=400 limit=400 status=PASS
SUMMARY nets_checked=1 violations=0 warns=0 skipped=0 max_ratio=400 worst_net=a"
    set rF [$fn $f]
    _chk F_pass {[dict get $rF pass_count] == 1}
    _chk F_fail {[dict get $rF fail_count] == 0}
    _chk F_max {[dict get $rF max_ratio] == 400}
    _chk F_worst {[dict get $rF worst_net] eq "a"}
    _chk F_mismatch_empty {[llength [dict get $rF mismatched_summary]] == 0}
    _chk F_verdict {[dict get $rF verdict] eq "PASS"}

    # ---- Case G: missing limit -> default 400.0; status absent -> inferred
    set g "NET a layer=M1 ratio=500
NET b layer=M1 ratio=100
SUMMARY nets_checked=2 violations=1 warns=0 skipped=0 max_ratio=500 worst_net=a"
    set rG [$fn $g]
    _chk G_fail {[dict get $rG fail_count] == 1}
    _chk G_pass {[dict get $rG pass_count] == 1}
    _chk G_worst {[dict get $rG worst_net] eq "a"}
    _chk G_max {[dict get $rG max_ratio] == 500}
    _chk G_mismatch_empty {[llength [dict get $rG mismatched_summary]] == 0}
    _chk G_verdict {[dict get $rG verdict] eq "FAIL"}

    # ---- Case H: missing ratio -> default 0.0 -> PASS; max_ratio=0
    set h "NET a layer=M1 limit=400 status=PASS
SUMMARY nets_checked=1 violations=0 warns=0 skipped=0 max_ratio=0 worst_net=a"
    set rH [$fn $h]
    _chk H_pass {[dict get $rH pass_count] == 1}
    _chk H_fail {[dict get $rH fail_count] == 0}
    _chk H_max {[dict get $rH max_ratio] == 0}
    _chk H_worst {[dict get $rH worst_net] eq "a"}
    _chk H_mismatch_empty {[llength [dict get $rH mismatched_summary]] == 0}
    _chk H_verdict {[dict get $rH verdict] eq "PASS"}

    # ---- Case I: SKIP excluded from max_ratio/worst_net (SKIP ratio=999 highest)
    set i "NET a layer=M1 ratio=100 limit=400 status=PASS
NET b layer=M1 ratio=999 limit=400 status=SKIP
SUMMARY nets_checked=2 violations=0 warns=0 skipped=1 max_ratio=100 worst_net=a"
    set rI [$fn $i]
    _chk I_pass {[dict get $rI pass_count] == 1}
    _chk I_skip {[dict get $rI skip_count] == 1}
    _chk I_worst {[dict get $rI worst_net] eq "a"}
    _chk I_max {[dict get $rI max_ratio] == 100}
    _chk I_mismatch_empty {[llength [dict get $rI mismatched_summary]] == 0}
    _chk I_verdict {[dict get $rI verdict] eq "PASS"}

    # ---- Case J: worst_net tie at max_ratio -> lexicographically smallest net
    set j "NET z layer=M1 ratio=100 limit=400 status=PASS
NET a layer=M1 ratio=100 limit=400 status=PASS
NET b layer=M1 ratio=50 limit=400 status=PASS
SUMMARY nets_checked=3 violations=0 warns=0 skipped=0 max_ratio=100 worst_net=a"
    set rJ [$fn $j]
    _chk J_worst {[dict get $rJ worst_net] eq "a"}
    _chk J_max {[dict get $rJ max_ratio] == 100}
    _chk J_pass {[dict get $rJ pass_count] == 3}
    _chk J_mismatch_empty {[llength [dict get $rJ mismatched_summary]] == 0}
    _chk J_verdict {[dict get $rJ verdict] eq "PASS"}

    # ---- Case K: no SUMMARY, no fails -> INCOMPLETE, mismatched empty
    set k "NET a layer=M1 ratio=50 limit=400 status=PASS
NET b layer=M1 ratio=60 limit=400 status=PASS"
    set rK [$fn $k]
    _chk K_pass {[dict get $rK pass_count] == 2}
    _chk K_fail {[dict get $rK fail_count] == 0}
    _chk K_worst {[dict get $rK worst_net] eq "b"}
    _chk K_max {[dict get $rK max_ratio] == 60}
    _chk K_mismatch_empty {[llength [dict get $rK mismatched_summary]] == 0}
    _chk K_verdict {[dict get $rK verdict] eq "INCOMPLETE"}

    # ---- Case L: SUMMARY mismatches (3 wrong, 2 absent) -> mismatched has 3;
    #             absent warns/skipped NOT reported; verdict INCOMPLETE (no fails)
    set l "NET a layer=M1 ratio=50 limit=400 status=PASS
NET b layer=M1 ratio=60 limit=400 status=PASS
SUMMARY nets_checked=5 violations=2 max_ratio=99"
    set rL [$fn $l]
    set ml [dict get $rL mismatched_summary]
    _chk L_mismatch_len {[llength $ml] == 3}
    _chk L_mismatch_nets_checked {[lsearch $ml "nets_checked"] >= 0}
    _chk L_mismatch_violations {[lsearch $ml "violations"] >= 0}
    _chk L_mismatch_max_ratio {[lsearch $ml "max_ratio"] >= 0}
    _chk L_mismatch_warns_absent {[lsearch $ml "warns"] < 0}
    _chk L_mismatch_skipped_absent {[lsearch $ml "skipped"] < 0}
    _chk L_mismatch_worst_net_absent {[lsearch $ml "worst_net"] < 0}
    _chk L_fail {[dict get $rL fail_count] == 0}
    _chk L_verdict {[dict get $rL verdict] eq "INCOMPLETE"}

    # ---- Case M: empty report, no SUMMARY -> all zero/empty, INCOMPLETE
    set m "# header only
"
    set rM [$fn $m]
    _chk M_total_nets {[dict get $rM total_nets] == 0}
    _chk M_total_lines {[dict get $rM total_lines] == 0}
    _chk M_pass {[dict get $rM pass_count] == 0}
    _chk M_fail {[dict get $rM fail_count] == 0}
    _chk M_skip {[dict get $rM skip_count] == 0}
    _chk M_warn {[dict get $rM warn_count] == 0}
    _chk M_worst_empty {[dict get $rM worst_net] eq ""}
    _chk M_max_neg {[dict get $rM max_ratio] == -1.0}
    _chk M_mismatch_empty {[llength [dict get $rM mismatched_summary]] == 0}
    _chk M_verdict {[dict get $rM verdict] eq "INCOMPLETE"}

    _chk_done
    if {$_chk_pass} { return "ALL_ASSERTS_PASS" } else { return "ASSERTS_FAILED" }
}
