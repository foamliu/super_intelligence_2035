# Reference implementation: layout_gds_layermap_audit
# Audits a pyAether-emitted textual GDS layer-map usage report for a layout cellview.
# Pure text + integer math; runs on Empyrean WaveView Tcl (no aether host).
#
# Report grammar (lines, '#' = comment, blank skipped; optional header ignored):
#   LAYER <name> gdsno=<N> datatype=<N> purpose=<drawing|pin|label> count=<N>
#   SUMMARY total_layers=<N> total_shapes=<N>
#
# Returns a flat Tcl dict with EXACTLY these 11 keys in order:
#   total_layers total_shapes drawing_layers pin_layers label_layers
#   dup_gdsno missing_purpose_layers max_shape_layer mismatched_summary verdict

proc _gtoks {line} {
    return [regexp -all -inline -- {[^[:space:]]+} $line]
}
proc _gstrip {tok prefix} {
    return [string range $tok [string length $prefix] end]
}

proc layout_gds_layermap_audit {report_text} {
    set nl [format %c 10]
    set cr [format %c 13]
    set lines [split [string map [list $cr ""] $report_text] $nl]

    # layer(name) -> list: gdsno datatype purpose count  (last-wins on duplicate name)
    array set layer {}
    set order {}
    set summarySeen 0
    set sumTotal ""; set sumShapes ""

    foreach raw $lines {
        set line [string trim $raw]
        if {$line eq ""} { continue }
        if {[string index $line 0] eq "#"} { continue }
        set toks [_gtoks $line]
        if {[llength $toks] == 0} { continue }
        set kw [lindex $toks 0]

        if {$kw eq "LAYER"} {
            set name [lindex $toks 1]
            set gdsno ""; set dt ""; set purpose ""; set count ""
            foreach t [lrange $toks 2 end] {
                if {[string match "gdsno=*" $t]} { set gdsno [_gstrip $t "gdsno="]
                } elseif {[string match "datatype=*" $t]} { set dt [_gstrip $t "datatype="]
                } elseif {[string match "purpose=*" $t]} { set purpose [_gstrip $t "purpose="]
                } elseif {[string match "count=*" $t]} { set count [_gstrip $t "count="] }
            }
            set purpose [string tolower $purpose]
            if {![info exists layer($name)]} { lappend order $name }
            set layer($name) [list $gdsno $dt $purpose $count]
            continue
        }
        if {$kw eq "SUMMARY"} {
            set summarySeen 1
            foreach t [lrange $toks 1 end] {
                if {[string match "total_layers=*" $t]} { set sumTotal [_gstrip $t "total_layers="]
                } elseif {[string match "total_shapes=*" $t]} { set sumShapes [_gstrip $t "total_shapes="] }
            }
            continue
        }
    }

    set total_layers [llength $order]
    set total_shapes 0
    set drawing {}; set pin {}; set label {}; set missing {}
    array set pairHits {}
    array set pairFirst {}

    foreach name $order {
        set rec $layer($name)
        set gdsno [lindex $rec 0]
        set dt [lindex $rec 1]
        set purpose [lindex $rec 2]
        set count [lindex $rec 3]
        if {$count eq ""} { set count 0 }
        set count [expr {$count + 0}]
        incr total_shapes $count

        if {$purpose eq "drawing"} { lappend drawing $name
        } elseif {$purpose eq "pin"} { lappend pin $name
        } elseif {$purpose eq "label"} { lappend label $name
        } else { lappend missing $name }

        if {$gdsno ne ""} {
            set key "${gdsno}|${dt}"
            if {![info exists pairHits($key)]} { set pairHits($key) 0 }
            incr pairHits($key)
            if {![info exists pairFirst($key)]} { set pairFirst($key) $name }
        }
    }

    # dup_gdsno: layer names whose (gdsno,datatype) pair is shared by >1 layer.
    # Include ALL layer names that belong to a shared pair (sorted, dedup).
    set dup {}
    foreach name $order {
        set rec $layer($name)
        set gdsno [lindex $rec 0]
        set dt [lindex $rec 1]
        if {$gdsno eq ""} { continue }
        set key "${gdsno}|${dt}"
        if {$pairHits($key) > 1} { lappend dup $name }
    }
    set dup_gdsno [lsort -dictionary [lrmdups $dup]]

    set drawing_layers [lsort -dictionary $drawing]
    set pin_layers [lsort -dictionary $pin]
    set label_layers [lsort -dictionary $label]
    set missing_purpose_layers [lsort -dictionary $missing]

    # max_shape_layer: layer name with max count, tie-break lex smallest name.
    set max_shape_layer ""
    set maxCount ""
    foreach name [lsort -dictionary $order] {
        set rec $layer($name)
        set count [lindex $rec 3]
        if {$count eq ""} { set count 0 }
        set count [expr {$count + 0}]
        if {$maxCount eq "" || $count > $maxCount} {
            set maxCount $count
            set max_shape_layer $name
        }
    }

    # mismatched_summary
    set mismatch {}
    if {$summarySeen} {
        if {$sumTotal ne "" && ($sumTotal + 0) != $total_layers} { lappend mismatch "total_layers" }
        if {$sumShapes ne "" && ($sumShapes + 0) != $total_shapes} { lappend mismatch "total_shapes" }
    }
    set mismatched_summary [lsort -dictionary $mismatch]

    # verdict priority: dup>0 FAIL > missing_purpose>0 INCOMPLETE > no-summary INCOMPLETE > PASS
    set verdict "PASS"
    if {[llength $dup_gdsno] > 0} { set verdict "FAIL"
    } elseif {[llength $missing_purpose_layers] > 0} { set verdict "INCOMPLETE"
    } elseif {!$summarySeen} { set verdict "INCOMPLETE" }

    return [dict create \
        total_layers $total_layers \
        total_shapes $total_shapes \
        drawing_layers $drawing_layers \
        pin_layers $pin_layers \
        label_layers $label_layers \
        dup_gdsno $dup_gdsno \
        missing_purpose_layers $missing_purpose_layers \
        max_shape_layer $max_shape_layer \
        mismatched_summary $mismatched_summary \
        verdict $verdict]
}

# remove duplicates from a list preserving a clean sorted dedup helper
proc lrmdups {lst} {
    array set s {}
    set out {}
    foreach x $lst { if {![info exists s($x)]} { set s($x) 1; lappend out $x } }
    return $out
}
