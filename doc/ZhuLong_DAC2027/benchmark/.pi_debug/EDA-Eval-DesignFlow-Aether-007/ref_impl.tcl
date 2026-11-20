# Reference implementation: layout_antenna_audit
# Audits a pyAether-emitted textual antenna-rule-check report for a layout cellview.
# Pure text + float/integer math; runs on Empyrean WaveView Tcl (no aether host).
#
# Report grammar (lines, '#' = comment, blank skipped; optional header ignored):
#   NET <name> layer=<L> gate_area=<N> diode_area=<N> ratio=<float> limit=<float> status=<S>
#   SUMMARY nets_checked=<N> violations=<N> warns=<N> skipped=<N> max_ratio=<float> worst_net=<name>
#
# Returns a flat Tcl dict with EXACTLY these 10 keys in order:
#   total_nets total_lines pass_count warn_count fail_count
#   skip_count worst_net max_ratio mismatched_summary verdict

proc _atoks {line} {
    return [regexp -all -inline -- {[^[:space:]]+} $line]
}
proc _astrip {tok prefix} {
    return [string range $tok [string length $prefix] end]
}

proc layout_antenna_audit {report_text} {
    set nl [format %c 10]
    set cr [format %c 13]
    set lines [split [string map [list $cr ""] $report_text] $nl]

    # key=(net,layer) -> list: ratioVal limitVal status ; last-wins
    array set rec {}
    set order {}        ;# list of (net,layer) keys in first-seen order
    set netsSeen {}     ;# distinct net names in first-seen order
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
        set toks [_atoks $line]
        if {[llength $toks] == 0} { continue }
        set kw [lindex $toks 0]

        if {$kw eq "NET"} {
            set net [lindex $toks 1]
            set layer ""
            set ratio 0.0; set hasR 0
            set limit 400.0; set hasL 0
            set status ""; set hasS 0
            foreach t [lrange $toks 2 end] {
                if {[string match "layer=*" $t]} {
                    set layer [_astrip $t "layer="]
                } elseif {[string match "ratio=*" $t]} {
                    set ratio [_astrip $t "ratio="]; set hasR 1
                } elseif {[string match "limit=*" $t]} {
                    set limit [_astrip $t "limit="]; set hasL 1
                } elseif {[string match "status=*" $t]} {
                    set status [_astrip $t "status="]; set hasS 1
                }
                # gate_area / diode_area are red herrings; ignored
            }
            set ratioVal [expr {double($ratio)}]
            set limitVal [expr {double($limit)}]
            if {$hasS} {
                set st [string toupper $status]
            } else {
                if {$ratioVal > $limitVal} { set st "FAIL" } else { set st "PASS" }
            }
            set key [list $net $layer]
            if {![info exists rec($key)]} { lappend order $key }
            if {[lsearch -exact $netsSeen $net] < 0} { lappend netsSeen $net }
            set rec($key) [list $ratioVal $limitVal $st]
        } elseif {$kw eq "SUMMARY"} {
            set summarySeen 1
            foreach t [lrange $toks 1 end] {
                if {[string match "nets_checked=*" $t]} {
                    set sumNC [_astrip $t "nets_checked="]; set sumNC_has 1
                } elseif {[string match "violations=*" $t]} {
                    set sumV [_astrip $t "violations="]; set sumV_has 1
                } elseif {[string match "warns=*" $t]} {
                    set sumW [_astrip $t "warns="]; set sumW_has 1
                } elseif {[string match "skipped=*" $t]} {
                    set sumS [_astrip $t "skipped="]; set sumS_has 1
                } elseif {[string match "max_ratio=*" $t]} {
                    set sumMR [_astrip $t "max_ratio="]; set sumMR_has 1
                } elseif {[string match "worst_net=*" $t]} {
                    set sumWN [_astrip $t "worst_net="]; set sumWN_has 1
                }
            }
        }
    }

    set total_nets [llength $netsSeen]
    set total_lines [llength $order]
    set pass_count 0; set warn_count 0; set fail_count 0; set skip_count 0
    set max_ratio -1.0
    set worst_net ""
    set seen_non_skip 0

    foreach key $order {
        set r $rec($key)
        set ratioVal [lindex $r 0]
        set st [lindex $r 2]
        switch -- $st {
            PASS { incr pass_count }
            WARN { incr warn_count }
            FAIL { incr fail_count }
            SKIP { incr skip_count }
        }
        # max_ratio / worst_net over NON-SKIP only
        if {$st ne "SKIP"} {
            set n [lindex $key 0]
            if {!$seen_non_skip} {
                set seen_non_skip 1
                set max_ratio $ratioVal
                set worst_net $n
            } else {
                if {$ratioVal > $max_ratio} {
                    set max_ratio $ratioVal
                    set worst_net $n
                } elseif {$ratioVal == $max_ratio} {
                    if {[string compare $n $worst_net] < 0} {
                        set worst_net $n
                    }
                }
            }
        }
    }
    # if no non-SKIP lines: max_ratio stays -1.0, worst_net stays ""

    # mismatched_summary
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
            if {[expr {double($sumMR)}] != $max_ratio} { lappend mismatched "max_ratio" }
        }
        if {$sumWN_has} {
            if {$sumWN ne $worst_net} { lappend mismatched "worst_net" }
        }
    }
    set mismatched [lsort -dictionary $mismatched]

    # verdict
    if {$fail_count > 0} {
        set verdict "FAIL"
    } elseif {[llength $mismatched] > 0 || !$summarySeen} {
        set verdict "INCOMPLETE"
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
