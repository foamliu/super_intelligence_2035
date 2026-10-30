# Reference implementation: layout_drc_audit
# Audits a pyAether-emitted textual DRC violation report.
# Pure text + integer math; runs on Empyrean WaveView Tcl (no aether host).
#
# Report grammar (lines, '#' = comment, blank skipped):
#   RULE <rulename> layer=<L> count=<N> severity=<err|warn>
#   SUMMARY total=<N> errors=<N> warnings=<N> checked=<N>
#   (optional header: "# DRC run ..." ignored)
#
# Returns a flat Tcl dict with EXACTLY these 10 keys in order:
#   total_rules total_violations error_count warning_count checked_rules
#   duplicate_rule_names per_layer_errors mismatched_summary layers_used verdict

proc _toks {line} {
    return [regexp -all -inline -- {[^[:space:]]+} $line]
}
proc _strip_prefix {tok prefix} {
    return [string range $tok [string length $prefix] end]
}

proc layout_drc_audit {drc_text} {
    set nl [format %c 10]
    set cr [format %c 13]
    set lines [split [string map [list $cr ""] $drc_text] $nl]

    # rule(name) -> list: count layer severity  (last-wins on duplicate name)
    array set rule {}
    set ruleOrder {}
    set summarySeen 0
    set sumTotal ""; set sumErrors ""; set sumWarns ""; set sumChecked ""

    foreach raw $lines {
        set line [string trim $raw]
        if {$line eq ""} { continue }
        if {[string index $line 0] eq "#"} { continue }
        set toks [_toks $line]
        if {[llength $toks] == 0} { continue }
        set kw [lindex $toks 0]

        if {$kw eq "RULE"} {
            set name [lindex $toks 1]
            set layer ""; set count ""; set sev ""
            foreach t [lrange $toks 2 end] {
                if {[string match "layer=*" $t]} { set layer [_strip_prefix $t "layer="]
                } elseif {[string match "count=*" $t]} { set count [_strip_prefix $t "count="]
                } elseif {[string match "severity=*" $t]} { set sev [_strip_prefix $t "severity="] }
            }
            # severity case-insensitive: normalize to lower
            set sev [string tolower $sev]
            # last-wins: replace earlier entry with same name
            if {![info exists rule($name)]} { lappend ruleOrder $name }
            set rule($name) [list $count $layer $sev]
            continue
        }
        if {$kw eq "SUMMARY"} {
            set summarySeen 1
            foreach t [lrange $toks 1 end] {
                if {[string match "total=*" $t]} { set sumTotal [_strip_prefix $t "total="]
                } elseif {[string match "errors=*" $t]} { set sumErrors [_strip_prefix $t "errors="]
                } elseif {[string match "warnings=*" $t]} { set sumWarns [_strip_prefix $t "warnings="]
                } elseif {[string match "checked=*" $t]} { set sumChecked [_strip_prefix $t "checked="] }
            }
            continue
        }
    }

    set total_rules [llength $ruleOrder]
    set total_violations 0
    set error_count 0
    set warning_count 0
    array set layerErr {}
    set layersList {}
    array set layerSeen {}

    foreach name $ruleOrder {
        set rec $rule($name)
        set count [lindex $rec 0]
        set layer [lindex $rec 1]
        set sev [lindex $rec 2]
        # coerce count to integer (defensive: empty -> 0)
        if {$count eq ""} { set count 0 }
        set count [expr {$count + 0}]
        incr total_violations $count
        if {$sev eq "err"} {
            incr error_count $count
            if {$layer ne ""} {
                if {![info exists layerErr($layer)]} { set layerErr($layer) 0 }
                incr layerErr($layer) $count
            }
        } elseif {$sev eq "warn"} {
            incr warning_count $count
        }
        if {$layer ne "" && ![info exists layerSeen($layer)]} {
            set layerSeen($layer) 1
            lappend layersList $layer
        }
    }
    set layers_used [lsort -dictionary $layersList]

    # duplicate rule names = names that appeared more than once in input order.
    # We track input-order occurrences to detect duplicates even though rule()
    # keeps only last value.
    array set nameHits {}
    foreach raw $lines {
        set line [string trim $raw]
        if {$line eq ""} { continue }
        if {[string index $line 0] eq "#"} { continue }
        set toks [_toks $line]
        if {[llength $toks] == 0} { continue }
        if {[lindex $toks 0] eq "RULE"} {
            set nm [lindex $toks 1]
            incr nameHits($nm)
        }
    }
    set dups {}
    foreach nm [array names nameHits] { if {$nameHits($nm) > 1} { lappend dups $nm } }
    set duplicate_rule_names [lsort -dictionary $dups]

    # per_layer_errors: dict layer->err count, sorted by layer name, ONLY layers with err>0
    set perLayer {}
    foreach L [lsort -dictionary [array names layerErr]] {
        lappend perLayer $L $layerErr($L)
    }
    set per_layer_errors $perLayer

    # checked_rules = number of distinct RULE entries (zero-count still counts as checked)
    set checked_rules $total_rules

    # mismatched_summary: compare SUMMARY fields to computed if SUMMARY present.
    # Returns a sorted list of mismatched field names; empty if no SUMMARY or all match.
    set mismatch {}
    if {$summarySeen} {
        if {$sumTotal ne "" && ($sumTotal + 0) != $total_violations} { lappend mismatch "total" }
        if {$sumErrors ne "" && ($sumErrors + 0) != $error_count} { lappend mismatch "errors" }
        if {$sumWarns ne "" && ($sumWarns + 0) != $warning_count} { lappend mismatch "warnings" }
        # checked in SUMMARY refers to checked rules count
        if {$sumChecked ne "" && ($sumChecked + 0) != $checked_rules} { lappend mismatch "checked" }
    }
    set mismatched_summary [lsort -dictionary $mismatch]

    # verdict priority: error_count>0 -> FAIL
    #                  elif warning_count>0 -> WARN
    #                  elif !summarySeen -> INCOMPLETE
    #                  else PASS
    set verdict "PASS"
    if {$error_count > 0} { set verdict "FAIL"
    } elseif {$warning_count > 0} { set verdict "WARN"
    } elseif {!$summarySeen} { set verdict "INCOMPLETE" }

    return [dict create \
        total_rules $total_rules \
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
