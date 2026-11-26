proc _toks {line} {
    return [regexp -all -inline -- {[^[:space:]]+} $line]
}
proc _strip_prefix {tok prefix} {
    return [string range $tok [string length $prefix] end]
}
proc _strip_parens {s} {
    return [string range $s 1 end-1]
}

proc layout_placement_audit {placement_text} {
    set nl [format %c 10]
    set cr [format %c 13]
    set lines [split [string map [list $cr ""] $placement_text] $nl]

    set insts {}
    set rects {}
    set pins {}
    array set req {}
    set reqSeen 0

    foreach raw $lines {
        set line [string trim $raw]
        if {$line eq ""} { continue }
        if {[string index $line 0] eq "#"} { continue }
        set toks [_toks $line]
        if {[llength $toks] == 0} { continue }
        set kw [lindex $toks 0]

        if {$kw eq "INST"} {
            set name [lindex $toks 1]
            set ox ""; set oy ""; set orient ""
            set llx ""; set lly ""; set urx ""; set ury ""
            foreach t $toks {
                if {[string match "origin=*" $t]} {
                    set v [_strip_parens [_strip_prefix $t "origin="]]
                    set parts [split $v ","]
                    set ox [lindex $parts 0]; set oy [lindex $parts 1]
                } elseif {[string match "orient=*" $t]} {
                    set orient [_strip_prefix $t "orient="]
                } elseif {[string match "bbox=*" $t]} {
                    set v [_strip_parens [_strip_prefix $t "bbox="]]
                    set parts [split $v ","]
                    set llx [lindex $parts 0]; set lly [lindex $parts 1]
                    set urx [lindex $parts 2]; set ury [lindex $parts 3]
                }
            }
            lappend insts [list $name $ox $oy $orient $llx $lly $urx $ury]
            continue
        }
        if {$kw eq "RECT"} {
            set layer ""; set llx ""; set lly ""; set urx ""; set ury ""
            foreach t $toks {
                if {[string match "layer=*" $t]} { set layer [_strip_prefix $t "layer="]
                } elseif {[string match "bbox=*" $t]} {
                    set v [_strip_parens [_strip_prefix $t "bbox="]]
                    set parts [split $v ","]
                    set llx [lindex $parts 0]; set lly [lindex $parts 1]
                    set urx [lindex $parts 2]; set ury [lindex $parts 3]
                }
            }
            lappend rects [list $layer $llx $lly $urx $ury]
            continue
        }
        if {$kw eq "PIN"} {
            set name [lindex $toks 1]
            set layer ""; set llx ""; set lly ""; set urx ""; set ury ""
            foreach t $toks {
                if {[string match "layer=*" $t]} { set layer [_strip_prefix $t "layer="]
                } elseif {[string match "bbox=*" $t]} {
                    set v [_strip_parens [_strip_prefix $t "bbox="]]
                    set parts [split $v ","]
                    set llx [lindex $parts 0]; set lly [lindex $parts 1]
                    set urx [lindex $parts 2]; set ury [lindex $parts 3]
                }
            }
            lappend pins [list $name $layer $llx $lly $urx $ury]
            continue
        }
        if {$kw eq "REQUIRE"} {
            set reqSeen 1
            foreach t [lrange $toks 1 end] { if {$t ne ""} { set req($t) 1 } }
            continue
        }
    }

    set total_instances [llength $insts]
    set total_rects [llength $rects]
    set pin_count [llength $pins]

    array set nameCount {}
    foreach rec $insts { set nm [lindex $rec 0]; incr nameCount($nm) }
    set dups {}
    foreach nm [array names nameCount] { if {$nameCount($nm) > 1} { lappend dups $nm } }
    set duplicate_inst_names [lsort -dictionary $dups]

    set malformed {}
    foreach rec $insts {
        set name [lindex $rec 0]
        set llx [lindex $rec 4]; set lly [lindex $rec 5]
        set urx [lindex $rec 6]; set ury [lindex $rec 7]
        if {$urx <= $llx || $ury <= $lly} { lappend malformed "INST:$name" }
    }
    set ridx 0
    foreach rec $rects {
        incr ridx
        set llx [lindex $rec 1]; set lly [lindex $rec 2]
        set urx [lindex $rec 3]; set ury [lindex $rec 4]
        if {$urx <= $llx || $ury <= $lly} { lappend malformed "RECT:$ridx" }
    }
    foreach rec $pins {
        set name [lindex $rec 0]
        set llx [lindex $rec 2]; set lly [lindex $rec 3]
        set urx [lindex $rec 4]; set ury [lindex $rec 5]
        if {$urx <= $llx || $ury <= $lly} { lappend malformed "PIN:$name" }
    }
    set malformed [lsort -dictionary $malformed]

    array set rectLayer {}
    foreach rec $rects { set rectLayer([lindex $rec 0]) 1 }
    set layers_used [lsort -dictionary [array names rectLayer]]

    set missing {}
    if {$reqSeen} {
        foreach L [array names req] { if {![info exists rectLayer($L)]} { lappend missing $L } }
    }
    set missing_layers [lsort -dictionary $missing]

    set unconnected {}
    foreach rec $pins {
        set name [lindex $rec 0]
        set layer [lindex $rec 1]
        if {![info exists rectLayer($layer)]} { lappend unconnected $name }
    }
    set unconnected_pins [lsort -dictionary $unconnected]

    set wf {}
    foreach rec $insts {
        set name [lindex $rec 0]
        set llx [lindex $rec 4]; set lly [lindex $rec 5]
        set urx [lindex $rec 6]; set ury [lindex $rec 7]
        if {$urx > $llx && $ury > $lly} {
            lappend wf [list $name [expr {$llx+0}] [expr {$lly+0}] [expr {$urx+0}] [expr {$ury+0}]]
        }
    }
    array set pairSet {}
    for {set i 0} {$i < [llength $wf]} {incr i} {
        set na [lindex [lindex $wf $i] 0]
        set ax1 [lindex [lindex $wf $i] 1]
        set ay1 [lindex [lindex $wf $i] 2]
        set ax2 [lindex [lindex $wf $i] 3]
        set ay2 [lindex [lindex $wf $i] 4]
        for {set j [expr {$i+1}]} {$j < [llength $wf]} {incr j} {
            set nb [lindex [lindex $wf $j] 0]
            set bx1 [lindex [lindex $wf $j] 1]
            set by1 [lindex [lindex $wf $j] 2]
            set bx2 [lindex [lindex $wf $j] 3]
            set by2 [lindex [lindex $wf $j] 4]
            set ov [expr {($ax1 < $bx2) && ($ax2 > $bx1) && ($ay1 < $by2) && ($ay2 > $by1)}]
            if {$ov} {
                if {[string compare $na $nb] <= 0} { set p "$na<->$nb" } else { set p "$nb<->$na" }
                set pairSet($p) 1
            }
        }
    }
    set overlapping_pairs [lsort -dictionary [array names pairSet]]

    set verdict "clean"
    if {[llength $malformed] > 0} { set verdict "malformed"
    } elseif {[llength $overlapping_pairs] > 0} { set verdict "overlap"
    } elseif {[llength $missing_layers] > 0} { set verdict "missing_layer"
    } elseif {[llength $unconnected_pins] > 0} { set verdict "unconnected_pin" }

    return [dict create total_instances $total_instances total_rects $total_rects pin_count $pin_count duplicate_inst_names $duplicate_inst_names malformed_entries $malformed overlapping_pairs $overlapping_pairs missing_layers $missing_layers unconnected_pins $unconnected_pins layers_used $layers_used verdict $verdict]
}
