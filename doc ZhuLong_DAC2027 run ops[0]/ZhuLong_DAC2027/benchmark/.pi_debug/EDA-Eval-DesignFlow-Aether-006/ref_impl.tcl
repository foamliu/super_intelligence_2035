# Reference implementation: layout_metalfill_target_audit
# Audits a pyAether-emitted textual metal-fill / density report for a layout cellview.
# Pure text + float/integer math; runs on Empyrean WaveView Tcl (no aether host).
#
# Report grammar (lines, '#' = comment, blank skipped; optional header ignored):
#   LAYER <name> target=<float> actual=<float> fill_count=<N>
#   SUMMARY total_layers=<N> total_fill=<N> min_density=<float> max_density=<float>
#
# Returns a flat Tcl dict with EXACTLY these 10 keys in order:
#   total_layers total_fill underfill_layers met_layers missing_target_layers
#   zero_fill_met_layers min_density_layer max_density_layer mismatched_summary verdict

proc _dtoks {line} {
    return [regexp -all -inline -- {[^[:space:]]+} $line]
}
proc _dstrip {tok prefix} {
    return [string range $tok [string length $prefix] end]
}

proc layout_metalfill_target_audit {report_text} {
    set nl [format %c 10]
    set cr [format %c 13]
    set lines [split [string map [list $cr ""] $report_text] $nl]

    # layer(name) -> list: target hasTgt actual hasAct fill_count  (last-wins)
    array set layer {}
    set order {}
    set summarySeen 0
    set sumTL ""; set sumTF ""; set sumMin ""; set sumMax ""
    set sumTLhas 0; set sumTFhas 0; set sumMinhas 0; set sumMaxhas 0

    foreach raw $lines {
        set line [string trim $raw]
        if {$line eq ""} { continue }
        if {[string index $line 0] eq "#"} { continue }
        set toks [_dtoks $line]
        if {[llength $toks] == 0} { continue }
        set kw [lindex $toks 0]

        if {$kw eq "LAYER"} {
            set name [lindex $toks 1]
            if {![info exists layer($name)]} { lappend order $name }
            set target ""; set hasT 0
            set actual 0.0; set hasA 0
            set fill 0
            foreach t [lrange $toks 2 end] {
                if {[string match "target=*" $t]} {
                    set target [_dstrip $t "target="]; set hasT 1
                } elseif {[string match "actual=*" $t]} {
                    set actual [_dstrip $t "actual="]; set hasA 1
                } elseif {[string match "fill_count=*" $t]} {
                    set fill [_dstrip $t "fill_count="]
                }
            }
            # store last-wins
            set layer($name) [list $target $hasT $actual $hasA $fill]
        } elseif {$kw eq "SUMMARY"} {
            set summarySeen 1
            foreach t [lrange $toks 1 end] {
                if {[string match "total_layers=*" $t]} {
                    set sumTL [_dstrip $t "total_layers="]; set sumTLhas 1
                } elseif {[string match "total_fill=*" $t]} {
                    set sumTF [_dstrip $t "total_fill="]; set sumTFhas 1
                } elseif {[string match "min_density=*" $t]} {
                    set sumMin [_dstrip $t "min_density="]; set sumMinhas 1
                } elseif {[string match "max_density=*" $t]} {
                    set sumMax [_dstrip $t "max_density="]; set sumMaxhas 1
                }
            }
        }
    }

    set total_layers [llength $order]
    set total_fill 0
    set underfill {}
    set met {}
    set missingTarget {}
    set zeroFillMet {}
    set minName ""
    set minVal ""
    set maxName ""
    set maxVal ""

    foreach name $order {
        set rec $layer($name)
        set target [lindex $rec 0]
        set hasT [lindex $rec 1]
        set actual [lindex $rec 2]
        set hasA [lindex $rec 3]
        set fill [lindex $rec 4]

        # total_fill: sum fill_count (missing = 0)
        if {$fill eq ""} { set fill 0 }
        incr total_fill [scan $fill %d]

        # actual default already 0.0 if absent
        set act [expr {double($actual)}]

        # min/max density (lex tie-break smallest name)
        if {$minName eq ""} {
            set minName $name; set minVal $act
        } else {
            if {$act < $minVal} {
                set minName $name; set minVal $act
            } elseif {$act == $minVal && [string compare $name $minName] < 0} {
                set minName $name
            }
        }
        if {$maxName eq ""} {
            set maxName $name; set maxVal $act
        } else {
            if {$act > $maxVal} {
                set maxName $name; set maxVal $act
            } elseif {$act == $maxVal && [string compare $name $maxName] < 0} {
                set maxName $name
            }
        }

        # bucketing
        if {!$hasT} {
            lappend missingTarget $name
        } else {
            set tgt [expr {double($target)}]
            if {$act < $tgt} {
                lappend underfill $name
            } else {
                lappend met $name
                if {$fill eq ""} { set fill 0 }
                if {[scan $fill %d] == 0} {
                    lappend zeroFillMet $name
                }
            }
        }
    }

    set underfill [lsort -dictionary $underfill]
    set met [lsort -dictionary $met]
    set missingTarget [lsort -dictionary $missingTarget]
    set zeroFillMet [lsort -dictionary $zeroFillMet]

    # mismatched_summary
    set mismatched {}
    if {$summarySeen} {
        if {$sumTLhas} {
            if {[scan $sumTL %d] != $total_layers} { lappend mismatched "total_layers" }
        }
        if {$sumTFhas} {
            if {[scan $sumTF %d] != $total_fill} { lappend mismatched "total_fill" }
        }
        # computed min/max density value
        if {$total_layers == 0} {
            set cmin ""; set cmax ""
        } else {
            set cmin $minVal; set cmax $maxVal
        }
        if {$sumMinhas} {
            if {$total_layers == 0} {
                lappend mismatched "min_density"
            } else {
                if {[expr {double($sumMin)}] != $cmin} { lappend mismatched "min_density" }
            }
        }
        if {$sumMaxhas} {
            if {$total_layers == 0} {
                lappend mismatched "max_density"
            } else {
                if {[expr {double($sumMax)}] != $cmax} { lappend mismatched "max_density" }
            }
        }
    }
    set mismatched [lsort -dictionary $mismatched]

    # verdict
    if {[llength $underfill] > 0} {
        set verdict "FAIL"
    } elseif {[llength $missingTarget] > 0} {
        set verdict "INCOMPLETE"
    } elseif {!$summarySeen} {
        set verdict "INCOMPLETE"
    } else {
        set verdict "PASS"
    }

    return [dict create \
        total_layers $total_layers \
        total_fill $total_fill \
        underfill_layers $underfill \
        met_layers $met \
        missing_target_layers $missingTarget \
        zero_fill_met_layers $zeroFillMet \
        min_density_layer $minName \
        max_density_layer $maxName \
        mismatched_summary $mismatched \
        verdict $verdict]
}
