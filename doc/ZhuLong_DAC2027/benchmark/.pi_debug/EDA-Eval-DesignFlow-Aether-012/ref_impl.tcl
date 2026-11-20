# Reference implementation: layout_pgmesh_audit
# Audits a pyAether-emitted PG (power/ground) MESH strap report for a layout cellview.
proc layout_pgmesh_audit {report_text} {
    set power_straps 0
    set ground_straps 0
    set unknown_straps 0
    set short_count 0
    set open_count 0
    set skip_count 0
    set has_summary 0
    set sum_total ""
    set sum_power ""
    set sum_ground ""
    set sum_min_width ""
    set sum_max_space ""
    set sum_coverage ""
    set min_width -1.0
    set max_space -1.0
    set worst_min_width_strap ""
    set worst_max_space_strap ""

    # LAST-WINS dedup on (name, layer): later line replaces direction/width/space/vias/status.
    array set mesh {}

    foreach line [split $report_text "\n"] {
        set line [string trim $line]
        if {$line eq ""} continue
        if {[string index $line 0] eq "#"} continue
        if {[string match "MESH *" $line]} {
            set rest [string range $line 5 end]
            set toks {}
            foreach t [split $rest " "] { if {$t ne ""} { lappend toks $t } }
            set name [lindex $toks 0]
            set layer [lindex $toks 1]
            set direction [lindex $toks 2]
            set width [lindex $toks 3]
            set space [lindex $toks 4]
            set vias [lindex $toks 5]
            set status [lindex $toks 6]
            # defaults for absent/empty fields
            if {$width eq ""} { set width 0.0 }
            if {$space eq ""} { set space 0.0 }
            if {$vias eq ""} { set vias 1 }
            if {$status eq ""} { set status "ok" }
            # LAST-WINS: replace all fields for this (name, layer) key
            set mesh($name,$layer) [list $direction $width $space $vias $status]
        } elseif {[string match "SUMMARY *" $line]} {
            set has_summary 1
            set rest [string range $line 7 end]
            set toks {}
            foreach t [split $rest " "] { if {$t ne ""} { lappend toks $t } }
            foreach tok $toks {
                if {[string match "total=*" $tok]} {
                    set sum_total [string range $tok 6 end]
                } elseif {[string match "power=*" $tok]} {
                    set sum_power [string range $tok 6 end]
                } elseif {[string match "ground=*" $tok]} {
                    set sum_ground [string range $tok 7 end]
                } elseif {[string match "min_width=*" $tok]} {
                    set sum_min_width [string range $tok 10 end]
                } elseif {[string match "max_space=*" $tok]} {
                    set sum_max_space [string range $tok 10 end]
                } elseif {[string match "coverage=*" $tok]} {
                    set sum_coverage [string range $tok 9 end]
                }
            }
        }
    }

    set total_straps [llength [array names mesh]]

    # For tie-break we need lex-smallest name with dictionary numeric-aware sort.
    # Collect non-SKIP records to scan for min_width / max_space.
    set non_skip_names_min {}
    set non_skip_names_max {}

    foreach key [array names mesh] {
        set name [lindex [split $key ","] 0]
        lassign $mesh($key) direction width space vias status
        set st [string tolower [string trim $status]]

        # power/ground classification by NAME (case-insensitive substring)
        set nm [string tolower $name]
        set cls "unknown"
        if {[string match -nocase *vdd* $nm] || [string match -nocase *vcc* $nm] || [string match -nocase *power* $nm]} {
            set cls "power"
        } elseif {[string match -nocase *gnd* $nm] || [string match -nocase *vss* $nm] || [string match -nocase *ground* $nm]} {
            set cls "ground"
        }
        if {$cls eq "power"} { incr power_straps
        } elseif {$cls eq "ground"} { incr ground_straps
        } else { incr unknown_straps }

        if {$st eq "short"} { incr short_count
        } elseif {$st eq "open"} { incr open_count
        } elseif {$st eq "skip"} { incr skip_count }

        if {$st ne "skip"} {
            set w [expr {double($width)}]
            set s [expr {double($space)}]
            # min_width
            if {$min_width < 0.0 || $w < $min_width} {
                set min_width $w
                set worst_min_width_strap $name
            } elseif {$w == $min_width} {
                # tie -> lex-smallest name (dictionary numeric-aware)
                set sorted [lsort -dictionary [list $worst_min_width_strap $name]]
                set worst_min_width_strap [lindex $sorted 0]
            }
            # max_space
            if {$max_space < 0.0 || $s > $max_space} {
                set max_space $s
                set worst_max_space_strap $name
            } elseif {$s == $max_space} {
                set sorted [lsort -dictionary [list $worst_max_space_strap $name]]
                set worst_max_space_strap [lindex $sorted 0]
            }
        }
    }

    # coverage_pct = round((power+ground)*100 / total); total==0 -> 0
    if {$total_straps == 0} {
        set coverage_pct 0
    } else {
        set coverage_pct [expr {int(round(double($power_straps + $ground_straps) * 100.0 / $total_straps))}]
    }

    # mismatched_summary
    set mismatched {}
    if {$has_summary} {
        if {$sum_total ne "" && $sum_total != $total_straps} {
            lappend mismatched "total=$sum_total vs $total_straps"
        }
        if {$sum_power ne "" && $sum_power != $power_straps} {
            lappend mismatched "power=$sum_power vs $power_straps"
        }
        if {$sum_ground ne "" && $sum_ground != $ground_straps} {
            lappend mismatched "ground=$sum_ground vs $ground_straps"
        }
        if {$sum_min_width ne "" && [expr {double($sum_min_width)}] != [expr {double($min_width)}]} {
            lappend mismatched "min_width=$sum_min_width vs $min_width"
        }
        if {$sum_max_space ne "" && [expr {double($sum_max_space)}] != [expr {double($max_space)}]} {
            lappend mismatched "max_space=$sum_max_space vs $max_space"
        }
        if {$sum_coverage ne "" && $sum_coverage != $coverage_pct} {
            lappend mismatched "coverage=$sum_coverage vs $coverage_pct"
        }
    }

    # verdict priority: short>0 -> FAIL > open>0 -> REVIEW >
    #   (no summary OR mismatched) -> INCOMPLETE > PASS
    if {$short_count > 0} {
        set verdict "FAIL"
    } elseif {$open_count > 0} {
        set verdict "REVIEW"
    } elseif {!$has_summary || [llength $mismatched] > 0} {
        set verdict "INCOMPLETE"
    } else {
        set verdict "PASS"
    }

    return [dict create \
        total_straps $total_straps \
        power_straps $power_straps \
        ground_straps $ground_straps \
        unknown_straps $unknown_straps \
        short_count $short_count \
        open_count $open_count \
        skip_count $skip_count \
        min_width $min_width \
        max_space $max_space \
        worst_min_width_strap $worst_min_width_strap \
        worst_max_space_strap $worst_max_space_strap \
        coverage_pct $coverage_pct \
        mismatched_summary $mismatched \
        verdict $verdict]
}
