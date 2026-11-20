# Naive (wrong) implementation: layout_routing_audit
# Plausible but fails the real traps (case-sensitive status, first-wins dedup,
# absent->always-ROUTED, vias==0 ignore layers, raw layer split, single_segment
# only when status=partial, max over ALL incl SKIP, ASCII tie-break, string
# max_segments compare, watchlist-as-FAIL verdict).
proc layout_routing_audit {routing_text} {
    set lines [split $routing_text [format %c 10]]
    array set seg {}
    array set via {}
    array set lyr {}
    array set stat {}
    array set sum {}
    set have_summary 0
    set layers_used {}

    foreach line $lines {
        set t [string trim $line]
        if {$t eq ""} { continue }
        if {[string index $t 0] eq "#"} { continue }
        set toks [split $t]
        set first [lindex $toks 0]
        if {$first eq "NET"} {
            set name [lindex $toks 1]
            if {![info exists seg($name)]} {
                # FIRST-wins (wrong): keep first occurrence
                set sg ""; set vi ""; set ly ""; set st ""
                foreach tok [lrange $toks 2 end] {
                    switch -glob -- $tok {
                        "segments=*" { set sg [string range $tok 9 end] }
                        "vias=*"     { set vi [string range $tok 5 end] }
                        "layers=*"   { set ly [string range $tok 7 end] }
                        "status=*"   { set st [string range $tok 7 end] }
                    }
                }
                set seg($name) $sg
                set via($name) $vi
                set lyr($name) $ly
                set stat($name) $st
            }
        } elseif {$first eq "SUMMARY"} {
            set have_summary 1
            foreach tok [lrange $toks 1 end] {
                if {[string match "nets_checked=*" $tok]}    { set sum(nets_checked)    [string range $tok 13 end] }
                if {[string match "routed=*" $tok]}          { set sum(routed)          [string range $tok 7 end] }
                if {[string match "unrouted=*" $tok]}        { set sum(unrouted)        [string range $tok 9 end] }
                if {[string match "missing_vias=*" $tok]}    { set sum(missing_vias)    [string range $tok 13 end] }
                if {[string match "max_segments=*" $tok]}    { set sum(max_segments)    [string range $tok 13 end] }
                if {[string match "max_segment_net=*" $tok]} { set sum(max_segment_net) [string range $tok 16 end] }
            }
        }
    }

    set total_nets [llength [array names seg]]
    set routed 0; set partial 0; set unrouted 0; set skipped 0
    set single_seg {}
    set missing_via {}
    set max_seg -1
    set max_segment_net ""

    foreach name [array names seg] {
        set sg $seg($name)
        set vi $via($name)
        set lyraw $lyr($name)
        set st $stat($name)
        if {$sg eq ""} { set sg 0 }
        if {$vi eq ""} { set vi 0 }
        set sg [expr {int($sg)}]
        set vi [expr {int($vi)}]

        # layers: raw comma-split, NO dedup, empty string counts as a layer (wrong)
        set lyrset [split $lyraw ","]
        if {$lyraw eq ""} { set lyrset {""} }
        foreach L $lyrset {
            set found 0
            foreach e $layers_used { if {$e eq $L} { set found 1; break } }
            if {!$found} { lappend layers_used $L }
        }
        set layer_count [llength $lyrset]

        # status case-SENSITIVE (wrong); absent -> always ROUTED (wrong)
        switch -- $st {
            "routed"   { set eff "ROUTED"; incr routed }
            "partial"  { set eff "PARTIAL"; incr partial }
            "unrouted" { set eff "UNROUTED"; incr unrouted }
            "skipped"  { set eff "SKIPPED"; incr skipped }
            default    { set eff "ROUTED"; incr routed }
        }

        # single_segment only when status=partial (wrong: ignores segments==1 with other status)
        if {$st eq "partial" && $sg == 1} { lappend single_seg $name }

        # missing_via = vias==0 ignoring layer count (wrong)
        if {$vi == 0} { lappend missing_via $name }

        # max over ALL nets including SKIP (wrong); ASCII string tie-break (wrong)
        if {$sg > $max_seg} {
            set max_seg $sg
            set max_segment_net $name
        } elseif {$sg == $max_seg} {
            if {$name ne $max_segment_net && ($max_segment_net eq "" || [string compare $name $max_segment_net] < 0)} {
                set max_segment_net $name
            }
        }
    }

    set single_seg [lsort -dictionary $single_seg]
    set missing_via [lsort -dictionary $missing_via]
    set layers_used [lsort -dictionary $layers_used]
    set missing_via_count [llength $missing_via]

    set mismatch {}
    if {$have_summary} {
        if {[info exists sum(nets_checked)]} { if {$sum(nets_checked) != $total_nets} { lappend mismatch "nets_checked" } }
        if {[info exists sum(routed)]} { if {$sum(routed) != $routed} { lappend mismatch "routed" } }
        if {[info exists sum(unrouted)]} { if {$sum(unrouted) != $unrouted} { lappend mismatch "unrouted" } }
        if {[info exists sum(missing_vias)]} { if {$sum(missing_vias) != $missing_via_count} { lappend mismatch "missing_vias" } }
        if {[info exists sum(max_segments)]} {
            # STRING equality (wrong: "2" != "2.0")
            if {$sum(max_segments) ne $max_seg} { lappend mismatch "max_segments" }
        }
        if {[info exists sum(max_segment_net)]} { if {$sum(max_segment_net) ne $max_segment_net} { lappend mismatch "max_segment_net" } }
    }
    set mismatch [lsort -dictionary $mismatch]

    # verdict: watchlist (partial or single_segment) -> FAIL (wrong)
    if {$unrouted > 0 || $missing_via_count > 0 || $partial > 0 || [llength $single_seg] > 0} {
        set verdict "FAIL"
    } elseif {[llength $mismatch] > 0 || !$have_summary} {
        set verdict "INCOMPLETE"
    } else {
        set verdict "PASS"
    }

    return [dict create total_nets $total_nets routed_count $routed partial_count $partial unrouted_count $unrouted skipped_count $skipped single_segment_nets $single_seg missing_via_nets $missing_via max_segments $max_seg max_segment_net $max_segment_net layers_used $layers_used mismatched_summary $mismatch verdict $verdict]
}
