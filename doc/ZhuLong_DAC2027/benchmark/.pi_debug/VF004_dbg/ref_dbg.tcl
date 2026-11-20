proc vflow_manifest_audit {manifest_text} {
    # Parse sections.
    set declared {}
    set steps {}            ;# step name -> dict(status, artifacts)
    set cur ""
    foreach line [split $manifest_text "\n"] {
        set line [string trim $line]
        if {$line eq ""} continue
        set c0 [string index $line 0]
        if {$c0 eq ";" || $c0 eq "#"} continue
        # section header?
        if {[regexp {^\[([^\]]+)\]$} $line -> sec]} {
            set cur $sec
            continue
        }
        # key = value
        if {![regexp {^([^=]+?)=(.*)$} $line -> rawk rawv]} continue
        set k [string trim $rawk]
        set v [string trim $rawv]
        if {$cur eq "declared_outputs"} {
            # last-wins
            dict set declared $k $v
        } elseif {[regexp {^step:(.+)$} $cur -> sname]} {
            if {![dict exists $steps $sname]} {
                dict set steps $sname [dict create status "" artifacts [list]]
            }
            if {$k eq "status"} {
                dict set steps $sname status $v
            } elseif {$k eq "artifact"} {
                # path|size|checksum|signoff
                set parts [split $v "|"]
                if {[llength $parts] == 4} {
                    lassign $parts path size checksum signoff
                    dict lappend steps $sname artifacts [list $path $size $checksum $signoff]
                }
            }
        }
        # other sections ignored
    }

    # Compute totals per (last-wins) step.
    set total 0
    set npass 0; set nfail 0; set nskip 0
    set missing {}
    set ghost {}
    set zerobyte {}
    set misschk {}
    # basename -> set of step names (track cross-step)
    set base2steps {}
    dict for {s info} $steps {
        incr total
        set st [dict get $info status]
        if {$st eq "PASS"} { incr npass } elseif {$st eq "FAIL"} { incr nfail } elseif {$st eq "SKIP"} { incr nskip }
        set arts [dict get $info artifacts]
        if {$st eq "PASS" && [llength $arts] == 0} {
            lappend missing $s
        }
        foreach a $arts {
            lassign $a path size checksum signoff
            # basename
            set lastslash [string last "/" $path]
            if {$lastslash >= 0} {
                set base [string range $path [expr {$lastslash + 1}] end]
            } else {
                set base $path
            }
            # track cross-step basename ownership (per step, dedup)
            if {![dict exists $base2steps $base]} {
                dict set base2steps $base [dict create $s 1]
            } else {
                dict set base2steps $base $s 1
            }
            if {$st eq "FAIL" || $st eq "SKIP"} {
                lappend ghost $path
            }
            if {$st eq "PASS" && $size == 0} {
                lappend zerobyte $path
            }
            if {$signoff eq "true" && $checksum eq ""} {
                lappend misschk $path
            }
        }
    }

    # name_collisions: basename owned by >=2 distinct steps
    # (owners is a dict step->1; dict size = number of distinct steps)
    set collisions {}
    dict for {base owners} $base2steps {
        if {[dict size $owners] >= 2} {
            lappend collisions $base
        }
    }

    set missing [lsort $missing]
    set ghost [lsort $ghost]
    set zerobyte [lsort $zerobyte]
    set misschk [lsort $misschk]
    set collisions [lsort $collisions]

    set verdict "clean"
    if {[llength $missing] || [llength $ghost] || [llength $zerobyte] || [llength $misschk] || [llength $collisions]} {
        set verdict "dirty"
    }

    set ::_b2s $base2steps
    return [dict create \
        total_steps                $total \
        pass_steps                 $npass \
        fail_steps                 $nfail \
        skip_steps                 $nskip \
        missing_artifacts          $missing \
        ghost_artifacts            $ghost \
        zero_byte_artifacts        $zerobyte \
        missing_checksum_signoff   $misschk \
        name_collisions            $collisions \
        verdict                    $verdict]
}
