# Reference implementation: layout_placement_audit (no-backslash-regex edition)
# Audits a textual pyAether-style layout cellview placement report.
# Returns a flat Tcl dict with EXACTLY these 10 keys in order:
#   total_instances total_rects pin_count duplicate_inst_names
#   malformed_entries overlapping_pairs missing_layers unconnected_pins
#   layers_used verdict

proc _toks {line} {
    # split on runs of whitespace (no backslash regex)
    return [regexp -all -inline -- {[^[:space:]]+} $line]
}
proc _strip_prefix {tok prefix} {
    return [string range $tok [string length $prefix] end]
}
proc _strip_parens {s} {
    # s like "(0,1800)" -> "0,1800"
    return [string range $s 1 end-1]
}

proc layout_placement_audit {placement_text} {
    set nl [format %c 10]
    set cr [format %c 13]
    set lines [split [string map [list $cr ""] $placement_text] $nl]

    set insts {}; set rects {}; set pins {}
    array set req {}; set reqSeen 0

    foreach raw $lines {
        set line [string trim $raw]
        if {$line eq ""} { continue }
        if {[string index $line 0] eq "#"} { continue }
        set toks [_toks $line]
        if {[llength $toks] == 0} { continue }
        set kw [lindex $toks 0]

        if {$kw eq "INST"} {
            # INST <name> lib=.. cell=.. origin=(ox,oy) orient=.. bbox=(llx,lly,urx,ury)
            set name [lindex $toks 1]
            set ox ""; set oy ""; set orient ""; set llx ""; set lly ""; set urx ""; set ury ""
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
        # unrecognized -> ignore
    }

    set total_instances [llength $insts]
    set total_rects [llength $rects]
    set pin_count [llength $pins]

    # duplicate inst names
    array set nameCount {}
    foreach rec $insts { set nm [lindex $rec 0]; incr nameCount($nm) }
    set dups {}
    foreach nm [array names nameCount] { if {$nameCount($nm) > 1} { lappend dups $nm } }
    set duplicate_inst_names [lsort -dictionary $dups]

    # malformed entries (zero-area or inverted bbox: urx<=llx OR ury<=lly)
    set malformed {}
    foreach rec $insts {
        lassign $rec name ox oy orient llx lly urx ury
        if {$urx <= $llx || $ury <= $lly} { lappend malformed "INST:$name" }
    }
    set ridx 0
    foreach rec $rects {
        incr ridx
        lassign $rec layer llx lly urx ury
        if {$urx <= $llx || $ury <= $lly} { lappend malformed "RECT:$ridx" }
    }
    foreach rec $pins {
        lassign $rec name layer llx lly urx ury
        if {$urx <= $llx || $ury <= $lly} { lappend malformed "PIN:$name" }
    }
    set malformed [lsort -dictionary $malformed]

    # layers used (from RECT only)
    array set rectLayer {}
    foreach rec $rects { set rectLayer([lindex $rec 0]) 1 }
    set layers_used [lsort -dictionary [array names rectLayer]]

    # missing layers (REQUIRE - RECT layers)
    set missing {}
    if {$reqSeen} {
        foreach L [array names req] { if {![info exists rectLayer($L)]} { lappend missing $L } }
    }
    set missing_layers [lsort -dictionary $missing]

    # unconnected pins (pin layer not in any RECT)
    set unconnected {}
    foreach rec $pins {
        lassign $rec name layer
        if {![info exists rectLayer($layer)]} { lappend unconnected $name }
    }
    set unconnected_pins [lsort -dictionary $unconnected]

    # overlapping pairs (INST vs INST, STRICT interior, well-formed only)
    set wf {}
    foreach rec $insts {
        lassign $rec name ox oy orient llx lly urx ury
        if {$urx > $llx && $ury > $lly} {
            lappend wf [list $name [expr {$llx+0}] [expr {$lly+0}] [expr {$urx+0}] [expr {$ury+0}]]
        }
    }
    array set pairSet {}
    for {set i 0} {$i < [llength $wf]} {incr i} {
        lassign [lindex $wf $i] na ax1 ay1 ax2 ay2
        for {set j [expr {$i+1}]} {$j < [llength $wf]} {incr j} {
            lassign [lindex $wf $j] nb bx1 by1 bx2 by2
            set ov [expr {($ax1 < $bx2) && ($ax2 > $bx1) && ($ay1 < $by2) && ($ay2 > $by1)}]
            if {$ov} {
                if {[string compare $na $nb] <= 0} { set p "$na<->$nb" } else { set p "$nb<->$na" }
                set pairSet($p) 1
            }
        }
    }
    set overlapping_pairs [lsort -dictionary [array names pairSet]]

    # verdict priority: malformed > overlap > missing_layer > unconnected_pin > clean
    set verdict "clean"
    if {[llength $malformed] > 0} { set verdict "malformed"
    } elseif {[llength $overlapping_pairs] > 0} { set verdict "overlap"
    } elseif {[llength $missing_layers] > 0} { set verdict "missing_layer"
    } elseif {[llength $unconnected_pins] > 0} { set verdict "unconnected_pin" }

    return [dict create \
        total_instances $total_instances \
        total_rects $total_rects \
        pin_count $pin_count \
        duplicate_inst_names $duplicate_inst_names \
        malformed_entries $malformed \
        overlapping_pairs $overlapping_pairs \
        missing_layers $missing_layers \
        unconnected_pins $unconnected_pins \
        layers_used $layers_used \
        verdict $verdict]
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
set r [check layout_placement_audit]; puts "RESULT:$r"; if {$r eq "ALL_ASSERTS_PASS"} { puts "DESIGN_FLOW_VERDICT=PASS" } else { puts "DESIGN_FLOW_VERDICT=FAIL" }
