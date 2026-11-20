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
