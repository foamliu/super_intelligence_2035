# Naive implementation: layout_metalfill_target_audit  (intentionally WRONG on many traps)
# Bugs vs reference:
#  - duplicate layer NAME: first-wins (keeps first target/actual/fill_count)
#  - total_fill: sums ALL input LAYER lines (not last-wins distinct)
#  - missing actual: skips the layer entirely (no 0.0 default) -> wrong underfill/min/max
#  - missing target: puts layer in met_layers (wrong -> should be missing_target)
#  - underfill: uses actual <= target (inclusive, should be strict <)
#  - min/max density: first-seen on tie (no lex tie-break smallest name)
#  - mismatched_summary: STRING equality (so "72.30" != "72.3" -> false mismatch)
#  - verdict: missing_target priority OVER underfill (wrong order)
#  - fill_count missing: treated as "" -> never flagged zero_fill_met
#  - output lists NOT sorted

proc _ntoks {line} {
    return [regexp -all -inline -- {[^[:space:]]+} $line]
}
proc _nstrip {tok prefix} {
    return [string range $tok [string length $prefix] end]
}

proc layout_metalfill_target_audit {report_text} {
    set nl [format %c 10]
    set lines [split [string map [list [format %c 13] ""] $report_text] $nl]

    array set layer {}
    set order {}
    set total_fill 0
    set summarySeen 0
    set sumTL ""; set sumTF ""; set sumMin ""; set sumMax ""

    foreach raw $lines {
        set line [string trim $raw]
        if {$line eq ""} { continue }
        if {[string index $line 0] eq "#"} { continue }
        set toks [_ntoks $line]
        if {[llength $toks] == 0} { continue }
        set kw [lindex $toks 0]
        if {$kw eq "LAYER"} {
            set name [lindex $toks 1]
            set target ""; set actual ""; set fill ""
            foreach t [lrange $toks 2 end] {
                if {[string match "target=*" $t]} {
                    set target [_nstrip $t "target="]
                } elseif {[string match "actual=*" $t]} {
                    set actual [_nstrip $t "actual="]
                } elseif {[string match "fill_count=*" $t]} {
                    set fill [_nstrip $t "fill_count="]
                }
            }
            # sum ALL lines (bug)
            if {$fill ne ""} { incr total_fill [scan $fill %d] }
            # skip layers with no actual (bug: should default 0.0)
            if {$actual eq ""} { continue }
            # first-wins (bug: should be last-wins)
            if {![info exists layer($name)]} {
                set layer($name) [list $target $actual $fill]
                lappend order $name
            }
        } elseif {$kw eq "SUMMARY"} {
            set summarySeen 1
            foreach t [lrange $toks 1 end] {
                if {[string match "total_layers=*" $t]} {
                    set sumTL [_nstrip $t "total_layers="]
                } elseif {[string match "total_fill=*" $t]} {
                    set sumTF [_nstrip $t "total_fill="]
                } elseif {[string match "min_density=*" $t]} {
                    set sumMin [_nstrip $t "min_density="]
                } elseif {[string match "max_density=*" $t]} {
                    set sumMax [_nstrip $t "max_density="]
                }
            }
        }
    }

    set total_layers [llength $order]
    set underfill {}; set met {}; set missingTarget {}; set zeroFillMet {}
    set minName ""; set minVal ""; set maxName ""; set maxVal ""

    foreach name $order {
        set rec $layer($name)
        set target [lindex $rec 0]
        set actual [lindex $rec 1]
        set fill [lindex $rec 2]
        set act [expr {double($actual)}]
        # min/max first-seen tie (bug: no lex tie-break)
        if {$minName eq ""} {
            set minName $name; set minVal $act
        } elseif {$act < $minVal} {
            set minName $name; set minVal $act
        }
        if {$maxName eq ""} {
            set maxName $name; set maxVal $act
        } elseif {$act > $maxVal} {
            set maxName $name; set maxVal $act
        }

        if {$target eq ""} {
            lappend met $name ;# bug: should be missingTarget
        } else {
            set tgt [expr {double($target)}]
            if {$act <= $tgt} { ;# bug: should be strict <
                lappend underfill $name
            } else {
                lappend met $name
                if {$fill ne "" && [scan $fill %d] == 0} { lappend zeroFillMet $name }
            }
        }
    }

    set mismatched {}
    if {$summarySeen} {
        if {$sumTL ne "" && $sumTL != $total_layers} { lappend mismatched "total_layers" }
        if {$sumTF ne "" && $sumTF != $total_fill} { lappend mismatched "total_fill" }
        if {$sumMin ne "" && ![string equal $sumMin $minVal]} { lappend mismatched "min_density" } ;# bug: string eq
        if {$sumMax ne "" && ![string equal $sumMax $maxVal]} { lappend mismatched "max_density" }
    }

    # verdict: missing_target priority OVER underfill (bug: should be underfill first)
    if {[llength $missingTarget] > 0} {
        set verdict "INCOMPLETE"
    } elseif {[llength $underfill] > 0} {
        set verdict "FAIL"
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
