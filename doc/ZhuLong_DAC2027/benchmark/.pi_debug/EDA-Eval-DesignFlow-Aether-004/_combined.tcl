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
# checker.tcl for layout_gds_layermap_audit
# Builds fixtures inline and asserts on the returned dict. Pure text analysis.
# Prints "RESULT:ALL_ASSERTS_PASS" if every assertion passes, else
# "RESULT:ASSERTS_FAILED" with the first failing assert name.
#
# Keys asserted: total_layers total_shapes drawing_layers pin_layers label_layers
# dup_gdsno missing_purpose_layers max_shape_layer mismatched_summary verdict

if {![info exists _chk_pass]} {
    set _chk_pass 1
    set _chk_fail ""
}
proc _chk {name cond} {
    global _chk_pass _chk_fail
    if {$_chk_pass} {
        if {![uplevel 1 [list expr $cond]]} {
            set _chk_pass 0
            set _chk_fail $name
            puts "ASSERT FAIL: $name"
        }
    }
}
proc _chk_done {} {
    global _chk_pass _chk_fail
    if {$_chk_pass} {
        puts "RESULT:ALL_ASSERTS_PASS"
    } else {
        puts "RESULT:ASSERTS_FAILED:$_chk_fail"
    }
}

proc check {fn} {
    global _chk_pass _chk_fail

    # ---- Case A: clean, distinct gdsnos, has SUMMARY -> PASS
    set a "# GDS layer map INVX1 at 2026-10-30 06:00:00
LAYER M1 gdsno=1 datatype=0 purpose=drawing count=10
LAYER M2 gdsno=2 datatype=0 purpose=drawing count=5
LAYER M1PIN gdsno=1 datatype=10 purpose=pin count=3
SUMMARY total_layers=3 total_shapes=18"
    set rA [$fn $a]
    _chk A_total_layers {[dict get $rA total_layers] == 3}
    _chk A_total_shapes {[dict get $rA total_shapes] == 18}
    _chk A_drawing_len {[llength [dict get $rA drawing_layers]] == 2}
    _chk A_drawing_sorted {[lindex [dict get $rA drawing_layers] 0] eq "M1" && [lindex [dict get $rA drawing_layers] 1] eq "M2"}
    _chk A_pin_len {[llength [dict get $rA pin_layers]] == 1}
    _chk A_pin_val {[lindex [dict get $rA pin_layers] 0] eq "M1PIN"}
    _chk A_label_empty {[llength [dict get $rA label_layers]] == 0}
    _chk A_dup_empty {[llength [dict get $rA dup_gdsno]] == 0}
    _chk A_missing_empty {[llength [dict get $rA missing_purpose_layers]] == 0}
    _chk A_max {[dict get $rA max_shape_layer] eq "M1"}
    _chk A_mismatch_empty {[llength [dict get $rA mismatched_summary]] == 0}
    _chk A_verdict {[dict get $rA verdict] eq "PASS"}

    # ---- Case B: purpose CASE-INSENSITIVE (DRAWING/Drawing/drawing all drawing)
    set b "LAYER A gdsno=1 datatype=0 purpose=DRAWING count=2
LAYER B gdsno=2 datatype=0 purpose=Drawing count=3
LAYER C gdsno=3 datatype=0 purpose=drawing count=1
SUMMARY total_layers=3 total_shapes=6"
    set rB [$fn $b]
    _chk B_drawing_len {[llength [dict get $rB drawing_layers]] == 3}
    _chk B_drawing_sorted {[lindex [dict get $rB drawing_layers] 0] eq "A"}
    _chk B_pin_empty {[llength [dict get $rB pin_layers]] == 0}
    _chk B_total_shapes {[dict get $rB total_shapes] == 6}
    _chk B_verdict {[dict get $rB verdict] eq "PASS"}

    # ---- Case C: duplicate layer NAME -> last-wins (replace, not sum)
    set c "LAYER M1 gdsno=1 datatype=0 purpose=drawing count=2
LAYER M1 gdsno=1 datatype=0 purpose=drawing count=8
SUMMARY total_layers=1 total_shapes=8"
    set rC [$fn $c]
    _chk C_total_layers {[dict get $rC total_layers] == 1}
    _chk C_total_shapes {[dict get $rC total_shapes] == 8}
    _chk C_drawing_len {[llength [dict get $rC drawing_layers]] == 1}
    _chk C_mismatch_empty {[llength [dict get $rC mismatched_summary]] == 0}
    _chk C_verdict {[dict get $rC verdict] eq "PASS"}

    # ---- Case D: dup_gdsno = shared (gdsno,datatype) pair -> FAIL, all names listed
    set d "LAYER A gdsno=5 datatype=0 purpose=drawing count=2
LAYER B gdsno=5 datatype=0 purpose=drawing count=3
LAYER C gdsno=5 datatype=0 purpose=drawing count=1
SUMMARY total_layers=3 total_shapes=6"
    set rD [$fn $d]
    set dd [dict get $rD dup_gdsno]
    _chk D_dup_len {[llength $dd] == 3}
    _chk D_dup_sorted {[lindex $dd 0] eq "A" && [lindex $dd 1] eq "B" && [lindex $dd 2] eq "C"}
    _chk D_verdict {[dict get $rD verdict] eq "FAIL"}

    # ---- Case E: same gdsno but DIFFERENT datatype -> NOT dup
    set e "LAYER A gdsno=5 datatype=0 purpose=drawing count=2
LAYER B gdsno=5 datatype=10 purpose=pin count=3
SUMMARY total_layers=2 total_shapes=5"
    set rE [$fn $e]
    _chk E_dup_empty {[llength [dict get $rE dup_gdsno]] == 0}
    _chk E_verdict {[dict get $rE verdict] eq "PASS"}

    # ---- Case F: missing purpose -> INCOMPLETE, layer not in drawing/pin/label
    set f "LAYER M1 gdsno=1 datatype=0 count=4
LAYER M2 gdsno=2 datatype=0 purpose=drawing count=3
SUMMARY total_layers=2 total_shapes=7"
    set rF [$fn $f]
    _chk F_missing_len {[llength [dict get $rF missing_purpose_layers]] == 1}
    _chk F_missing_val {[lindex [dict get $rF missing_purpose_layers] 0] eq "M1"}
    _chk F_drawing_len {[llength [dict get $rF drawing_layers]] == 1}
    _chk F_drawing_val {[lindex [dict get $rF drawing_layers] 0] eq "M2"}
    _chk F_total_layers {[dict get $rF total_layers] == 2}
    _chk F_verdict {[dict get $rF verdict] eq "INCOMPLETE"}

    # ---- Case G: verdict priority dup > missing (dup present even with missing -> FAIL)
    set g "LAYER A gdsno=1 datatype=0 purpose=drawing count=2
LAYER B gdsno=1 datatype=0 count=3
SUMMARY total_layers=2 total_shapes=5"
    set rG [$fn $g]
    _chk G_dup_len {[llength [dict get $rG dup_gdsno]] == 2}
    _chk G_missing_len {[llength [dict get $rG missing_purpose_layers]] == 1}
    _chk G_verdict {[dict get $rG verdict] eq "FAIL"}

    # ---- Case H: max_shape_layer tie-break -> lex smallest name
    set h "LAYER Z gdsno=10 datatype=0 purpose=drawing count=5
LAYER A gdsno=11 datatype=0 purpose=drawing count=5
LAYER M gdsno=12 datatype=0 purpose=drawing count=2
SUMMARY total_layers=3 total_shapes=12"
    set rH [$fn $h]
    _chk H_max {[dict get $rH max_shape_layer] eq "A"}
    _chk H_total_shapes {[dict get $rH total_shapes] == 12}

    # ---- Case I: label purpose collected
    set i "LAYER L1 gdsno=1 datatype=0 purpose=drawing count=2
LAYER L2 gdsno=2 datatype=0 purpose=label count=1
LAYER L3 gdsno=3 datatype=0 purpose=pin count=4
SUMMARY total_layers=3 total_shapes=7"
    set rI [$fn $i]
    _chk I_label_len {[llength [dict get $rI label_layers]] == 1}
    _chk I_label_val {[lindex [dict get $rI label_layers] 0] eq "L2"}
    _chk I_pin_len {[llength [dict get $rI pin_layers]] == 1}
    _chk I_drawing_len {[llength [dict get $rI drawing_layers]] == 1}
    _chk I_verdict {[dict get $rI verdict] eq "PASS"}

    # ---- Case J: no SUMMARY -> verdict INCOMPLETE (even with no errors), mismatch empty
    set j "LAYER M1 gdsno=1 datatype=0 purpose=drawing count=2"
    set rJ [$fn $j]
    _chk J_verdict {[dict get $rJ verdict] eq "INCOMPLETE"}
    _chk J_mismatch_empty {[llength [dict get $rJ mismatched_summary]] == 0}
    _chk J_total_shapes {[dict get $rJ total_shapes] == 2}

    # ---- Case K: mismatched_summary detects wrong total_layers & total_shapes
    set k "LAYER M1 gdsno=1 datatype=0 purpose=drawing count=3
LAYER M2 gdsno=2 datatype=0 purpose=drawing count=2
SUMMARY total_layers=99 total_shapes=99"
    set rK [$fn $k]
    set mm [dict get $rK mismatched_summary]
    _chk K_mismatch_len {[llength $mm] == 2}
    _chk K_mismatch_has_total_layers {"total_layers" in $mm}
    _chk K_mismatch_has_total_shapes {"total_shapes" in $mm}

    # ---- Case L: mismatched_summary empty when SUMMARY correct
    set l "LAYER M1 gdsno=1 datatype=0 purpose=drawing count=3
LAYER M2 gdsno=2 datatype=0 purpose=pin count=2
SUMMARY total_layers=2 total_shapes=5"
    set rL [$fn $l]
    _chk L_mismatch_empty {[llength [dict get $rL mismatched_summary]] == 0}
    _chk L_verdict {[dict get $rL verdict] eq "PASS"}

    # ---- Case M: count default 0 when missing; empty report -> 0/INCOMPLETE
    set m "LAYER M1 gdsno=1 datatype=0 purpose=drawing
SUMMARY total_layers=1 total_shapes=0"
    set rM [$fn $m]
    _chk M_total_shapes {[dict get $rM total_shapes] == 0}
    _chk M_total_layers {[dict get $rM total_layers] == 1}
    _chk M_mismatch_empty {[llength [dict get $rM mismatched_summary]] == 0}
    _chk M_verdict {[dict get $rM verdict] eq "PASS"}

    _chk_done
    if {$_chk_pass} { return "ALL_ASSERTS_PASS" } else { return "ASSERTS_FAILED" }
}
set r [check layout_gds_layermap_audit]; puts "RESULT:$r"; if {$r eq "ALL_ASSERTS_PASS"} { puts "DESIGN_FLOW_VERDICT=PASS" } else { puts "DESIGN_FLOW_VERDICT=FAIL" }
