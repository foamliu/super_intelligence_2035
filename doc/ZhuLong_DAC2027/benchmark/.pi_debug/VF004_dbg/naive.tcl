# NAIVE: merges artifact lists across duplicate blocks (no last-wins reset),
# gates verdict on missing_artifacts ALONE, treats per-step dup as collision.
proc vflow_manifest_audit {manifest_text} {
    set declared {}
    set steps {}
    set cur ""
    foreach line [split $manifest_text "\n"] {
        set line [string trim $line]
        if {$line eq ""} continue
        set c0 [string index $line 0]
        if {$c0 eq ";" || $c0 eq "#"} continue
        if {[regexp {^\[([^\]]+)\]$} $line -> sec]} { set cur $sec; continue }
        if {![regexp {^([^=]+?)=(.*)$} $line -> rawk rawv]} continue
        set k [string trim $rawk]; set v [string trim $rawv]
        if {$cur eq "declared_outputs"} { dict set declared $k $v
        } elseif {[regexp {^step:(.+)$} $cur -> sname]} {
            if {![dict exists $steps $sname]} { dict set steps $sname [dict create status "" arts [list]] }
            if {$k eq "status"} { dict set steps $sname status $v
            } elseif {$k eq "artifact"} {
                set parts [split $v "|"]
                if {[llength $parts]==4} {
                    lassign $parts p sz ck sf
                    # NAIVE: dict lappend nested (flattens) -- but keep arts as flat path list
                    dict lappend steps $sname arts $p
                }
            }
        }
    }
    set total 0; set np 0; set nf 0; set ns 0
    set missing {}; set ghost {}; set zb {}; set mc {}; set coll {}
    set bases {}
    dict for {s info} $steps {
        incr total
        set st [dict get $info status]
        if {$st eq "PASS"} { incr np } elseif {$st eq "FAIL"} { incr nf } elseif {$st eq "SKIP"} { incr ns }
        set arts [dict get $info arts]
        if {$st eq "PASS" && [llength $arts]==0} { lappend missing $s }
        foreach p $arts {
            set ls [string last "/" $p]
            set base [expr {$ls>=0 ? [string range $p [expr {$ls+1}] end] : $p}]
            lappend bases $base  ;# NAIVE: global basename count, no per-step dedup
            if {$st eq "FAIL" || $st eq "SKIP"} { lappend ghost $p }
            if {$st eq "PASS"} { lappend zb $p }  ;# NAIVE: any PASS artifact treated as zero-byte check (wrong gate)
        }
    }
    # NAIVE collisions: basename seen >1 globally
    set coll {}
    foreach b [lsort -unique $bases] {
        set cnt 0
        foreach x $bases { if {$x eq $b} { incr cnt } }
        if {$cnt > 1} { lappend coll $b }
    }
    set missing [lsort $missing]; set ghost [lsort $ghost]; set zb [lsort $zb]; set mc [lsort $mc]; set coll [lsort $coll]
    # NAIVE verdict: only missing gates
    set verdict [expr {[llength $missing]==0 ? "clean" : "dirty"}]
    return [dict create total_steps $total pass_steps $np fail_steps $nf skip_steps $ns missing_artifacts $missing ghost_artifacts $ghost zero_byte_artifacts $zb missing_checksum_signoff $mc name_collisions $coll verdict $verdict]
}
