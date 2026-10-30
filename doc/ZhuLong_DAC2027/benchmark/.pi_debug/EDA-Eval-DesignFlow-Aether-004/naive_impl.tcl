# Naive implementation: layout_gds_layermap_audit  (intentionally WRONG on many traps)
# Bugs vs reference:
#  - purpose: exact compare "drawing" (case-sensitive) -> DRAWING/Drawing misbucketed
#  - duplicate layer NAME: first-wins (keeps first count, ignores later LAYER lines)
#  - dup_gdsno: checks gdsno ALONE (ignores datatype) -> false dup when same gdsno diff dt
#  - missing_purpose: defaults to "drawing" -> never reports missing, wrong bucket
#  - max_shape_layer: first-seen on tie (no lex tie-break)
#  - total_shapes: sums ALL input LAYER lines (not last-wins distinct)
#  - mismatched_summary: always empty (trusts SUMMARY)
#  - verdict: reports INCOMPLETE when dup present (wrong priority: missing>dup)
#  - lists not sorted

proc _ntoks {line} {
    return [regexp -all -inline -- {[^[:space:]]+} $line]
}
proc _nstrip {tok prefix} {
    return [string range $tok [string length $prefix] end]
}

proc layout_gds_layermap_audit {report_text} {
    set nl [format %c 10]
    set lines [split [string map [list [format %c 13] ""] $report_text] $nl]

    array set layer {}
    set order {}
    set sumTotal 0; set sumShapes 0
    set summarySeen 0
    set total_shapes 0

    foreach raw $lines {
        set line [string trim $raw]
        if {$line eq ""} { continue }
        if {[string index $line 0] eq "#"} { continue }
        set toks [_ntoks $line]
        if {[llength $toks] == 0} { continue }
        set kw [lindex $toks 0]
        if {$kw eq "LAYER"} {
            set name [lindex $toks 1]
            set gdsno ""; set dt ""; set purpose ""; set count ""
            foreach t [lrange $toks 2 end] {
                if {[string match "gdsno=*" $t]} { set gdsno [_nstrip $t "gdsno="]
                } elseif {[string match "datatype=*" $t]} { set dt [_nstrip $t "datatype="]
                } elseif {[string match "purpose=*" $t]} { set purpose [_nstrip $t "purpose="]
                } elseif {[string match "count=*" $t]} { set count [_nstrip $t "count="] }
            }
            # BUG: first-wins
            if {![info exists layer($name)]} {
                lappend order $name
                set layer($name) [list $gdsno $dt $purpose $count]
            }
            # BUG: sum ALL lines
            if {$count eq ""} { set count 0 }
            incr total_shapes [expr {$count + 0}]
            continue
        }
        if {$kw eq "SUMMARY"} {
            set summarySeen 1
            foreach t [lrange $toks 1 end] {
                if {[string match "total_layers=*" $t]} { set sumTotal [_nstrip $t "total_layers="]
                } elseif {[string match "total_shapes=*" $t]} { set sumShapes [_nstrip $t "total_shapes="] }
            }
        }
    }

    set total_layers [llength $order]
    set drawing {}; set pin {}; set label {}; set missing {}
    array set pairHits {}
    foreach name $order {
        set rec $layer($name)
        set gdsno [lindex $rec 0]
        set purpose [lindex $rec 2]
        # BUG: case-sensitive; BUG: default to drawing if empty
        if {$purpose eq ""} { set purpose "drawing" }
        if {$purpose eq "drawing"} { lappend drawing $name
        } elseif {$purpose eq "pin"} { lappend pin $name
        } elseif {$purpose eq "label"} { lappend label $name }
        # BUG: gdsno ALONE (ignore datatype)
        if {$gdsno ne ""} {
            if {![info exists pairHits($gdsno)]} { set pairHits($gdsno) 0 }
            incr pairHits($gdsno)
        }
    }
    set dup {}
    foreach name $order {
        set rec $layer($name)
        set gdsno [lindex $rec 0]
        if {$gdsno ne "" && $pairHits($gdsno) > 1} { lappend dup $name }
    }

    # BUG: max first-seen tie
    set max_shape_layer ""
    set maxCount ""
    foreach name $order {
        set rec $layer($name)
        set count [lindex $rec 3]
        if {$count eq ""} { set count 0 }
        set count [expr {$count + 0}]
        if {$maxCount eq "" || $count > $maxCount} {
            set maxCount $count
            set max_shape_layer $name
        }
    }

    # BUG: verdict priority missing>dup, and trusts summary
    set verdict "PASS"
    if {[llength $missing] > 0} { set verdict "INCOMPLETE"
    } elseif {[llength $dup] > 0} { set verdict "FAIL"
    } elseif {!$summarySeen} { set verdict "INCOMPLETE" }

    return [dict create \
        total_layers $total_layers \
        total_shapes $total_shapes \
        drawing_layers $drawing \
        pin_layers $pin \
        label_layers $label \
        dup_gdsno $dup \
        missing_purpose_layers $missing \
        max_shape_layer $max_shape_layer \
        mismatched_summary {} \
        verdict $verdict]
}
