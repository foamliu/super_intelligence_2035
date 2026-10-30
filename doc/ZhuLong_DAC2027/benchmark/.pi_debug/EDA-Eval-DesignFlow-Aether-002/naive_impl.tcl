# NAIVE implementation: has every trap wrong on purpose.
proc layout_placement_audit {placement_text} {
    set lines [split [string map [list "\r" ""] $placement_text] "\n"]
    set insts {}; set rects {}; set pins {}
    array set req {}; set reqSeen 0
    set reINST {^INST[[:space:]]+([^[:space:]]+)[[:space:]]+lib=([^[:space:]]+)[[:space:]]+cell=([^[:space:]]+)[[:space:]]+origin=\(([^,)]+),([^,)]+)\)[[:space:]]+orient=([^[:space:]]+)[[:space:]]+bbox=\(([^,)]+),([^,)]+),([^,)]+),([^,)]+)\)[[:space:]]*$}
    set reRECT {^RECT[[:space:]]+layer=([^[:space:]]+)[[:space:]]+bbox=\(([^,)]+),([^,)]+),([^,)]+),([^,)]+)\)[[:space:]]*$}
    set rePIN  {^PIN[[:space:]]+([^[:space:]]+)[[:space:]]+layer=([^[:space:]]+)[[:space:]]+bbox=\(([^,)]+),([^,)]+),([^,)]+),([^,)]+)\)[[:space:]]+dir=([^[:space:]]+)[[:space:]]*$}
    set reREQ  {^REQUIRE[[:space:]]+(.*)$}
    foreach raw $lines {
        set line [string trim $raw]
        if {$line eq ""} continue
        if {[string index $line 0] eq "#"} continue
        if {[regexp $reINST $line -> name lib cell ox oy orient llx lly urx ury]} { lappend insts [list $name $llx $lly $urx $ury]; continue }
        if {[regexp $reRECT $line -> layer llx lly urx ury]} { lappend rects [list $layer $llx $lly $urx $ury]; continue }
        if {[regexp $rePIN $line -> name layer llx lly urx ury dir]} { lappend pins [list $name $layer]; continue }
        if {[regexp $reREQ $line -> rest]} { set reqSeen 1; foreach L [split $rest " "] { set L [string trim $L]; if {$L ne ""} { set req($L) 1 } }; continue }
    }
    set total_instances [llength $insts]
    set total_rects [llength $rects]
    set pin_count [llength $pins]
    array set nameCount {}
    foreach rec $insts { set nm [lindex $rec 0]; incr nameCount($nm) }
    set dups {}
    foreach nm [array names nameCount] { if {$nameCount($nm) > 1} { lappend dups $nm } }
    set duplicate_inst_names [lsort -dictionary $dups]

    # TRAP: malformed uses strict < (misses zero-area urx==llx)
    set malformed {}
    foreach rec $insts { lassign $rec name llx lly urx ury; if {$urx < $llx || $ury < $lly} { lappend malformed "INST:$name" } }
    set ridx 0
    foreach rec $rects { incr ridx; lassign $rec layer llx lly urx ury; if {$urx < $llx || $ury < $lly} { lappend malformed "RECT:$ridx" } }
    foreach rec $pins { lassign $rec name layer; if {0} { lappend malformed "PIN:$name" } }
    set malformed [lsort -dictionary $malformed]

    # TRAP: layers_used includes INST bbox layers too (naive treats any layer as present)
    array set allLayer {}
    foreach rec $rects { set allLayer([lindex $rec 0]) 1 }
    # naive: also count PIN layers as "used"
    foreach rec $pins { set allLayer([lindex $rec 1]) 1 }
    set layers_used [lsort -dictionary [array names allLayer]]

    set missing {}
    if {$reqSeen} { foreach L [array names req] { if {![info exists allLayer($L)]} { lappend missing $L } } }
    set missing_layers [lsort -dictionary $missing]

    # TRAP: unconnected_pins checks pin layer in any layer (incl PIN-derived) -> never unconnected here
    set unconnected {}
    foreach rec $pins { lassign $rec name layer; if {![info exists allLayer($layer)]} { lappend unconnected $name } }
    set unconnected_pins [lsort -dictionary $unconnected]

    # TRAP: overlap uses <= / >= (includes touching) AND includes rects, AND includes malformed
    set allb {}
    foreach rec $insts { lassign $rec name llx lly urx ury; lappend allb [list $name $llx $lly $urx $ury] }
    foreach rec $rects { lassign $rec layer llx lly urx ury; lappend allb [list "RECT:$layer" $llx $lly $urx $ury] }
    array set pairSet {}
    for {set i 0} {$i < [llength $allb]} {incr i} {
        lassign [lindex $allb $i] na ax1 ay1 ax2 ay2
        for {set j [expr {$i+1}]} {$j < [llength $allb]} {incr j} {
            lassign [lindex $allb $j] nb bx1 by1 bx2 by2
            # naive: non-strict (<= / >=) includes touching
            set ov [expr {($ax1 <= $bx2) && ($ax2 >= $bx1) && ($ay1 <= $by2) && ($ay2 >= $by1)}]
            if {$ov} {
                # naive: not lex-ordered, may include reverse
                set pairSet("$na<->$nb") 1
            }
        }
    }
    set overlapping_pairs [lsort -dictionary [array names pairSet]]

    # TRAP: verdict = first-detected (overlap before malformed)
    set verdict "clean"
    if {[llength $overlapping_pairs] > 0} { set verdict "overlap"
    } elseif {[llength $malformed] > 0} { set verdict "malformed"
    } elseif {[llength $missing_layers] > 0} { set verdict "missing_layer"
    } elseif {[llength $unconnected_pins] > 0} { set verdict "unconnected_pin" }

    return [dict create total_instances $total_instances total_rects $total_rects pin_count $pin_count duplicate_inst_names $duplicate_inst_names malformed_entries $malformed overlapping_pairs $overlapping_pairs missing_layers $missing_layers unconnected_pins $unconnected_pins layers_used $layers_used verdict $verdict]
}
