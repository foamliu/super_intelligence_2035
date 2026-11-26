# Naive implementation: layout_drc_audit  (intentionally WRONG on many traps)
# Bugs vs reference:
#  - severity: exact compare "err" (case-sensitive) -> ERR/Err miscounted as warnings
#  - duplicate rule names: first-wins (keeps first count, ignores later RULE lines)
#  - duplicate_rule_names: never reported (empty)
#  - total_violations/errors/warnings: trusts SUMMARY fields when present
#  - missing SUMMARY -> verdict PASS (no INCOMPLETE)
#  - zero-count rules skipped from checked_rules
#  - per_layer_errors: unsorted + includes warn layers
#  - mismatched_summary: always empty (trusts SUMMARY)

proc _ntoks {line} {
    return [regexp -all -inline -- {[^[:space:]]+} $line]
}
proc _nstrip {tok prefix} {
    return [string range $tok [string length $prefix] end]
}

proc layout_drc_audit {drc_text} {
    set nl [format %c 10]
    set lines [split [string map [list [format %c 13] ""] $drc_text] $nl]

    array set rule {}
    set order {}
    set sumTotal 0; set sumErrors 0; set sumWarns 0; set sumChecked 0
    set summarySeen 0

    foreach raw $lines {
        set line [string trim $raw]
        if {$line eq ""} { continue }
        if {[string index $line 0] eq "#"} { continue }
        set toks [_ntoks $line]
        if {[llength $toks] == 0} { continue }
        set kw [lindex $toks 0]
        if {$kw eq "RULE"} {
            set name [lindex $toks 1]
            set layer ""; set count 0; set sev ""
            foreach t [lrange $toks 2 end] {
                if {[string match "layer=*" $t]} { set layer [_nstrip $t "layer="]
                } elseif {[string match "count=*" $t]} { set count [_nstrip $t "count="]
                } elseif {[string match "severity=*" $t]} { set sev [_nstrip $t "severity="] }
            }
            # BUG: first-wins (skip if name already seen) -> ignores re-definition
            if {![info exists rule($name)]} {
                lappend order $name
                set rule($name) [list $count $layer $sev]
            }
            continue
        }
        if {$kw eq "SUMMARY"} {
            set summarySeen 1
            foreach t [lrange $toks 1 end] {
                if {[string match "total=*" $t]} { set sumTotal [_nstrip $t "total="]
                } elseif {[string match "errors=*" $t]} { set sumErrors [_nstrip $t "errors="]
                } elseif {[string match "warnings=*" $t]} { set sumWarns [_nstrip $t "warnings="]
                } elseif {[string match "checked=*" $t]} { set sumChecked [_nstrip $t "checked="] }
            }
            continue
        }
    }

    # BUG: skip zero-count rules from checked_rules
    set checked_rules 0
    set total_violations 0
    set error_count 0
    set warning_count 0
    set perLayer {}
    set layersList {}
    foreach name $order {
        set rec $rule($name)
        set count [lindex $rec 0]
        set layer [lindex $rec 1]
        set sev [lindex $rec 2]
        if {$count == 0} { continue }
        incr checked_rules
        incr total_violations $count
        # BUG: case-sensitive "err"
        if {$sev eq "err"} {
            incr error_count $count
            lappend perLayer $layer $count
        } elseif {$sev eq "warn"} {
            incr warning_count $count
            # BUG: include warn layers in per_layer_errors too
            lappend perLayer $layer $count
        }
        lappend layersList $layer
    }

    # BUG: trust SUMMARY when present
    if {$summarySeen} {
        set total_violations $sumTotal
        set error_count $sumErrors
        set warning_count $sumWarns
        set checked_rules $sumChecked
    }

    set duplicate_rule_names {}
    set per_layer_errors $perLayer
    set mismatched_summary {}
    set layers_used $layersList
    set verdict "PASS"
    if {$error_count > 0} { set verdict "FAIL"
    } elseif {$warning_count > 0} { set verdict "WARN" }

    return [dict create \
        total_rules [llength $order] \
        total_violations $total_violations \
        error_count $error_count \
        warning_count $warning_count \
        checked_rules $checked_rules \
        duplicate_rule_names $duplicate_rule_names \
        per_layer_errors $per_layer_errors \
        mismatched_summary $mismatched_summary \
        layers_used $layers_used \
        verdict $verdict]
}
