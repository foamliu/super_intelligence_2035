# Reference implementation: layout_routing_audit
# Audits a pyAether-emitted textual routing-connectivity report.
# Pure string + integer math. POSIX classes only (no Perl character classes).
proc layout_routing_audit {routing_text} {
    set lines [split $routing_text [format %c 10]]
    array set seen {}
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
            set sg ""
            set vi ""
            set ly ""
            set st ""
            foreach tok [lrange $toks 2 end] {
                switch -glob -- $tok {
                    "segments=*" { set sg [string range $tok 9 end] }
                    "vias=*"     { set vi [string range $tok 5 end] }
                    "layers=*"   { set ly [string range $tok 7 end] }
                    "status=*"   { set st [string range $tok 7 end] }
                }
            }
            set seen($name) 1
            # LAST occurrence WINS: replace ALL fields
            set seg($name) $sg
            set via($name) $vi
            set lyr($name) $ly
            set stat($name) $st
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

    set total_nets [llength [array names seen]]
    set routed 0; set partial 0; set unrouted 0; set skipped 0
    set single_seg {}
    set missing_via {}
    set have_nonskip 0
    set max_seg -1
    set tie_names {}
    set max_segment_net ""

    foreach name [array names seen] {
        set sg $seg($name)
        set vi $via($name)
        set lyraw $lyr($name)
        set st $stat($name)
        # defaults: missing segments -> 0 ; missing vias -> 0
        if {$sg eq ""} { set sg 0 }
        if {$vi eq ""} { set vi 0 }
        set sg [expr {int($sg)}]
        set vi [expr {int($vi)}]

        # layers list: comma-split, dedup, drop empties
        set lyrset {}
        if {$lyraw ne ""} {
            foreach L [split $lyraw ","] {
                set L [string trim $L]
                if {$L eq ""} { continue }
                # dedup
                set found 0
                foreach e $lyrset { if {$e eq $L} { set found 1; break } }
                if {!$found} { lappend lyrset $L }
            }
        }
        set layer_count [llength $lyrset]
        # accumulate layers_used (union over ALL nets)
        foreach L $lyrset {
            set found 0
            foreach e $layers_used { if {$e eq $L} { set found 1; break } }
            if {!$found} { lappend layers_used $L }
        }

        # effective status: explicit (case-insensitive) wins; absent -> infer from segments
        if {$st eq ""} {
            if {$sg == 0} { set eff "UNROUTED" } elseif {$sg == 1} { set eff "PARTIAL" } else { set eff "ROUTED" }
        } else {
            set eff [string toupper $st]
        }
        switch -- $eff {
            "ROUTED"   { incr routed }
            "PARTIAL"   { incr partial }
            "UNROUTED" { incr unrouted }
            "SKIPPED"  { incr skipped }
            default {
                # unknown status token -> infer (treat like absent)
                if {$sg == 0} { set eff "UNROUTED"; incr unrouted } elseif {$sg == 1} { set eff "PARTIAL"; incr partial } else { set eff "ROUTED"; incr routed }
            }
        }

        # single_segment watchlist: segments==1 regardless of status
        if {$sg == 1} { lappend single_seg $name }

        # missing_via: layer_count>=2 AND vias==0 (layer change requires via)
        if {$layer_count >= 2 && $vi == 0} { lappend missing_via $name }

        if {$eff ne "SKIPPED"} {
            if {!$have_nonskip} {
                set have_nonskip 1
                set max_seg $sg
                set tie_names [list $name]
            } else {
                if {$sg > $max_seg} {
                    set max_seg $sg
                    set tie_names [list $name]
                } elseif {$sg == $max_seg} {
                    lappend tie_names $name
                }
            }
        }
    }

    if {!$have_nonskip} {
        set max_seg -1
        set max_segment_net ""
    } else {
        set max_seg [expr {int($max_seg)}]
        set max_segment_net [lindex [lsort -dictionary $tie_names] 0]
    }

    set single_seg [lsort -dictionary $single_seg]
    set missing_via [lsort -dictionary $missing_via]
    set layers_used [lsort -dictionary $layers_used]
    set missing_via_count [llength $missing_via]

    # mismatched_summary reconciliation
    set mismatch {}
    if {$have_summary} {
        if {[info exists sum(nets_checked)]} {
            if {![expr {$sum(nets_checked) == $total_nets}]} { lappend mismatch "nets_checked" }
        }
        if {[info exists sum(routed)]} {
            if {![expr {$sum(routed) == $routed}]} { lappend mismatch "routed" }
        }
        if {[info exists sum(unrouted)]} {
            if {![expr {$sum(unrouted) == $unrouted}]} { lappend mismatch "unrouted" }
        }
        if {[info exists sum(missing_vias)]} {
            if {![expr {$sum(missing_vias) == $missing_via_count}]} { lappend mismatch "missing_vias" }
        }
        if {[info exists sum(max_segments)]} {
            # NUMERIC equality (expr ==)
            if {![expr {double($sum(max_segments)) == $max_seg}]} { lappend mismatch "max_segments" }
        }
        if {[info exists sum(max_segment_net)]} {
            # STRING equality
            if {$sum(max_segment_net) ne $max_segment_net} { lappend mismatch "max_segment_net" }
        }
    }
    set mismatch [lsort -dictionary $mismatch]

    if {$unrouted > 0 || $missing_via_count > 0} {
        set verdict "FAIL"
    } elseif {[llength $mismatch] > 0 || !$have_summary} {
        set verdict "INCOMPLETE"
    } else {
        set verdict "PASS"
    }

    return [dict create total_nets $total_nets routed_count $routed partial_count $partial unrouted_count $unrouted skipped_count $skipped single_segment_nets $single_seg missing_via_nets $missing_via max_segments $max_seg max_segment_net $max_segment_net layers_used $layers_used mismatched_summary $mismatch verdict $verdict]
}
