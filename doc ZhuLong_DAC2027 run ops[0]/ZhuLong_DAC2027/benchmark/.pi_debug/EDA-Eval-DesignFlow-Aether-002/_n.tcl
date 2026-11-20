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
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc dget {d k} { return [dict get $d $k] }
proc llist {d k} { return [dict get $d $k] }
proc j {d k} { return [join [dict get $d $k] "|"] }

proc check {candidate} {
    # ---- Case A: baseline inverter layout, clean ----
    set cA {# cellview: bench_inv_lib/inv/layout
INST MP0 lib=reference_pdk cell=p18 origin=(0,1800) orient=R0 bbox=(0,1800,400,2200)
INST MN0 lib=reference_pdk cell=n18 origin=(0,0) orient=R0 bbox=(0,0,400,400)
RECT layer=M1 bbox=(0,400,200,1800)
RECT layer=PO bbox=(0,0,400,2200)
PIN IN layer=M1 bbox=(0,800,200,1000) dir=input
PIN OUT layer=M1 bbox=(200,800,400,1000) dir=output
PIN VDD layer=M1 bbox=(0,2000,400,2200) dir=input
PIN GND layer=M1 bbox=(0,0,400,200) dir=input
REQUIRE M1 PO}
    set dA [$candidate $cA]
    assert {[dget $dA total_instances] == 2} "A total_instances=2"
    assert {[dget $dA total_rects] == 2} "A total_rects=2"
    assert {[dget $dA pin_count] == 4} "A pin_count=4"
    assert {[llength [llist $dA duplicate_inst_names]] == 0} "A no dup names"
    assert {[llength [llist $dA malformed_entries]] == 0} "A no malformed"
    assert {[llength [llist $dA overlapping_pairs]] == 0} "A no overlap (MP0/MN0 disjoint in y)"
    assert {[j $dA layers_used] eq "M1|PO"} "A layers_used=M1|PO (lex sorted)"
    assert {[llength [llist $dA missing_layers]] == 0} "A no missing (M1+PO present)"
    assert {[llength [llist $dA unconnected_pins]] == 0} "A no unconnected (all pins M1 in rects)"
    assert {[string equal [dget $dA verdict] "clean"]} "A verdict=clean"

    # ---- Case B: STRICT INTERIOR OVERLAP tooth (touching edge is NOT overlap) ----
    set cB {INST A lib=L cell=C origin=(0,0) orient=R0 bbox=(0,0,100,100)
INST B lib=L cell=C origin=(100,0) orient=R0 bbox=(100,0,200,100)}
    set dB [$candidate $cB]
    assert {[dget $dB total_instances] == 2} "B total=2"
    assert {[llength [llist $dB overlapping_pairs]] == 0} "B touching edge NOT overlap (strict interior)"
    assert {[string equal [dget $dB verdict] "clean"]} "B verdict=clean"

    # ---- Case C: real strict interior overlap ----
    set cC {INST A lib=L cell=C origin=(0,0) orient=R0 bbox=(0,0,100,100)
INST B lib=L cell=C origin=(50,50) orient=R0 bbox=(50,50,150,150)}
    set dC [$candidate $cC]
    assert {[j $dC overlapping_pairs] eq "A<->B"} "C overlap A<->B (strict interior, ordered)"
    assert {[string equal [dget $dC verdict] "overlap"]} "C verdict=overlap"

    # ---- Case D: MALFORMED bbox (zero-area + inverted) ----
    set cD {INST W lib=L cell=C origin=(10,10) orient=R0 bbox=(10,10,5,20)
INST Z lib=L cell=C origin=(0,0) orient=R0 bbox=(0,0,0,100)}
    set dD [$candidate $cD]
    assert {[dget $dD total_instances] == 2} "D total=2 (malformed still counted)"
    assert {[j $dD malformed_entries] eq "INST:W|INST:Z"} "D malformed lex sorted INST:W|INST:Z (W inverted, Z zero-area)"
    assert {[llength [llist $dD overlapping_pairs]] == 0} "D malformed excluded from overlap"
    assert {[string equal [dget $dD verdict] "malformed"]} "D verdict=malformed"

    # ---- Case E: DUPLICATE inst names ----
    set cE {INST X1 lib=L cell=C origin=(0,0) orient=R0 bbox=(0,0,100,100)
INST X1 lib=L cell=C origin=(200,0) orient=R0 bbox=(200,0,300,100)}
    set dE [$candidate $cE]
    assert {[dget $dE total_instances] == 2} "E total=2"
    assert {[j $dE duplicate_inst_names] eq "X1"} "E dup names=X1"
    assert {[llength [llist $dE overlapping_pairs]] == 0} "E no overlap (disjoint)"
    assert {[string equal [dget $dE verdict] "clean"]} "E verdict=clean (dup names alone is not a verdict category)"

    # ---- Case F: MISSING LAYER tooth (layer in INST/PIN but not RECT doesn't satisfy) ----
    set cF {INST A lib=L cell=C origin=(0,0) orient=R0 bbox=(0,0,100,100)
RECT layer=M1 bbox=(0,0,100,100)
PIN P layer=PO bbox=(0,0,10,10) dir=input
REQUIRE M1 PO}
    set dF [$candidate $cF]
    assert {[j $dF layers_used] eq "M1"} "F layers_used=M1 only (RECT layers)"
    assert {[j $dF missing_layers] eq "PO"} "F missing=PO (PO in PIN/INST bbox does NOT satisfy REQUIRE)"
    assert {[string equal [dget $dF verdict] "missing_layer"]} "F verdict=missing_layer"

    # ---- Case G: UNCONNECTED PIN tooth (pin layer must be in RECT, not INST bbox) ----
    set cG {INST A lib=L cell=C origin=(0,0) orient=R0 bbox=(0,0,100,100)
RECT layer=M1 bbox=(0,0,100,100)
PIN P layer=M2 bbox=(0,0,10,10) dir=input}
    set dG [$candidate $cG]
    assert {[j $dG layers_used] eq "M1"} "G layers_used=M1"
    assert {[j $dG unconnected_pins] eq "P"} "G unconnected=P (M2 not in any RECT)"
    assert {[string equal [dget $dG verdict] "unconnected_pin"]} "G verdict=unconnected_pin"

    # ---- Case H: OVERLAP only INST vs INST (rects excluded) ----
    set cH {INST I lib=L cell=C origin=(0,0) orient=R0 bbox=(0,0,50,50)
RECT layer=M1 bbox=(0,0,100,100)
RECT layer=M1 bbox=(50,50,150,150)}
    set dH [$candidate $cH]
    assert {[dget $dH total_rects] == 2} "H total_rects=2"
    assert {[llength [llist $dH overlapping_pairs]] == 0} "H rects overlap but NOT insts -> no overlap pair"
    assert {[string equal [dget $dH verdict] "clean"]} "H verdict=clean"

    # ---- Case I: VERDICT PRIORITY (malformed beats overlap) ----
    set cI {INST A lib=L cell=C origin=(0,0) orient=R0 bbox=(0,0,100,100)
INST B lib=L cell=C origin=(50,50) orient=R0 bbox=(50,50,150,150)
INST C lib=L cell=C origin=(0,0) orient=R0 bbox=(0,0,0,10)}
    set dI [$candidate $cI]
    assert {[j $dI overlapping_pairs] eq "A<->B"} "I overlap A<->B still computed"
    assert {[j $dI malformed_entries] eq "INST:C"} "I malformed=C (zero-area)"
    assert {[string equal [dget $dI verdict] "malformed"]} "I verdict=malformed (priority malformed>overlap)"

    # ---- Case J: LEX SORT + pair order + dedup (3 mutually overlapping insts) ----
    set cJ {INST A lib=L cell=C origin=(0,0) orient=R0 bbox=(0,0,100,100)
INST B lib=L cell=C origin=(50,0) orient=R0 bbox=(50,0,150,100)
INST C lib=L cell=C origin=(0,50) orient=R0 bbox=(0,50,100,150)}
    set dJ [$candidate $cJ]
    assert {[j $dJ overlapping_pairs] eq "A<->B|A<->C|B<->C"} "J overlap pairs lex sorted, ordered, no reverse dups"
    assert {[string equal [dget $dJ verdict] "overlap"]} "J verdict=overlap"

    # ---- Case K: malformed RECT/PIN/INST mix, lex sort, zero-area tooth ----
    set cK {INST Y lib=L cell=C origin=(0,0) orient=R0 bbox=(0,0,0,50)
RECT layer=M1 bbox=(0,0,0,100)
PIN Q layer=M1 bbox=(0,0,0,10) dir=input}
    set dK [$candidate $cK]
    assert {[j $dK malformed_entries] eq "INST:Y|PIN:Q|RECT:1"} "K malformed lex sorted INST:Y|PIN:Q|RECT:1 (all zero-area)"
    assert {[string equal [dget $dK verdict] "malformed"]} "K verdict=malformed"

    # ---- Case L: malformed inst EXCLUDED from overlap (inside another) ----
    set cL {INST A lib=L cell=C origin=(0,0) orient=R0 bbox=(0,0,100,100)
INST B lib=L cell=C origin=(50,50) orient=R0 bbox=(50,50,50,60)}
    set dL [$candidate $cL]
    assert {[j $dL malformed_entries] eq "INST:B"} "L B zero-area malformed"
    assert {[llength [llist $dL overlapping_pairs]] == 0} "L malformed B inside A NOT reported as overlap"
    assert {[string equal [dget $dL verdict] "malformed"]} "L verdict=malformed"

    # ---- Case M: empty / comments only ----
    set cM {# just a comment
# another comment
}
    set dM [$candidate $cM]
    assert {[dget $dM total_instances] == 0} "M total_instances=0"
    assert {[dget $dM total_rects] == 0} "M total_rects=0"
    assert {[dget $dM pin_count] == 0} "M pin_count=0"
    assert {[llength [llist $dM missing_layers]] == 0} "M no missing (no REQUIRE line)"
    assert {[llength [llist $dM unconnected_pins]] == 0} "M no unconnected"
    assert {[llength [llist $dM layers_used]] == 0} "M no layers"
    assert {[string equal [dget $dM verdict] "clean"]} "M verdict=clean"

    return "ALL_ASSERTS_PASS"
}
if {[catch {set r [check layout_placement_audit]} err]} { puts "NAIVE FAIL: $err"; puts "TEETH PROVEN" }
