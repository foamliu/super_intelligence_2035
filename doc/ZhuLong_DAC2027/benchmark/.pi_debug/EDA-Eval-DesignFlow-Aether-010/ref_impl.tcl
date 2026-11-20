# Reference implementation: layout_pgshort_audit
# Audits a pyAether-emitted PG (power/ground) short report.
proc layout_pgshort_audit {report_text} {
    set short_count 0
    set leak_count 0
    set clean_count 0
    set power_count 0
    set ground_count 0
    set mixed_pairs {}
    set max_resistance -1.0
    set worst_pair ""
    set layers_affected {}
    array set pair_data {}
    set has_summary 0
    set sum_shorts_checked ""
    set sum_shorts ""
    set sum_leaks ""
    set sum_clean ""
    set sum_max_resistance ""
    set sum_worst_pair ""

    foreach line [split $report_text "\n"] {
        set line [string trim $line]
        if {$line eq ""} continue
        if {[string index $line 0] eq "#"} continue
        if {[string match "SHORT *" $line]} {
            set rest [string range $line 6 end]
            set toks {}
            foreach t [split $rest " "] { if {$t ne ""} { lappend toks $t } }
            set net_a [lindex $toks 0]
            set net_b [lindex $toks 1]
            set key "$net_a $net_b"
            set type ""
            set resistance 0.0
            set layer ""
            set status ""
            foreach tok [lrange $toks 2 end] {
                if {[string match "type=*" $tok]} {
                    set type [string range $tok 5 end]
                } elseif {[string match "resistance=*" $tok]} {
                    set resistance [string range $tok 11 end]
                } elseif {[string match "layer=*" $tok]} {
                    set layer [string range $tok 6 end]
                } elseif {[string match "status=*" $tok]} {
                    set status [string range $tok 7 end]
                }
            }
            if {$resistance eq ""} { set resistance 0.0 }
            # LAST-WINS: overwrite (replace, not sum, not first-wins)
            set pair_data($key) [list $type $resistance $layer $status]
        } elseif {[string match "SUMMARY *" $line]} {
            set has_summary 1
            set rest [string range $line 7 end]
            set toks {}
            foreach t [split $rest " "] { if {$t ne ""} { lappend toks $t } }
            foreach tok $toks {
                if {[string match "shorts_checked=*" $tok]} {
                    set sum_shorts_checked [string range $tok 15 end]
                } elseif {[string match "shorts=*" $tok]} {
                    set sum_shorts [string range $tok 7 end]
                } elseif {[string match "leaks=*" $tok]} {
                    set sum_leaks [string range $tok 6 end]
                } elseif {[string match "clean=*" $tok]} {
                    set sum_clean [string range $tok 6 end]
                } elseif {[string match "max_resistance=*" $tok]} {
                    set sum_max_resistance [string range $tok 15 end]
                } elseif {[string match "worst_pair=*" $tok]} {
                    set sum_worst_pair [string range $tok 11 end]
                }
            }
        }
    }

    set total_shorts [llength [array names pair_data]]

    foreach key [array names pair_data] {
        lassign $pair_data($key) type resistance layer status
        set st [string tolower [string trim $status]]
        if {$st eq ""} {
            set r [expr {double($resistance)}]
            if {$r < 1.0} { set st "short"
            } elseif {$r < 100.0} { set st "leak"
            } else { set st "clean" }
        }
        if {$st eq "short"} { incr short_count
        } elseif {$st eq "leak"} { incr leak_count
        } elseif {$st eq "clean"} { incr clean_count }

        set ty [string tolower [string trim $type]]
        if {$ty eq "mixed"} {
            incr power_count
            incr ground_count
            lappend mixed_pairs [join [split $key " "] "-"]
        } else {
            if {[string match "*power*" $ty]} { incr power_count }
            if {[string match "*ground*" $ty]} { incr ground_count }
        }

        if {$st ne "clean"} {
            set r [expr {double($resistance)}]
            if {$r > $max_resistance} {
                set max_resistance $r
                set worst_pair [join [split $key " "] "-"]
            } elseif {$r == $max_resistance} {
                set cand [join [split $key " "] "-"]
                set sorted [lsort -dictionary [list $worst_pair $cand]]
                set worst_pair [lindex $sorted 0]
            }
            if {$layer ne ""} {
                if {$layer ni $layers_affected} { lappend layers_affected $layer }
            }
        }
    }

    set layers_affected [lsort -dictionary $layers_affected]
    set mixed_pairs [lsort -dictionary $mixed_pairs]

    set mismatched {}
    if {$has_summary} {
        if {$sum_shorts_checked ne "" && $sum_shorts_checked != $total_shorts} {
            lappend mismatched "shorts_checked=$sum_shorts_checked vs $total_shorts"
        }
        if {$sum_shorts ne "" && $sum_shorts != $short_count} {
            lappend mismatched "shorts=$sum_shorts vs $short_count"
        }
        if {$sum_leaks ne "" && $sum_leaks != $leak_count} {
            lappend mismatched "leaks=$sum_leaks vs $leak_count"
        }
        if {$sum_clean ne "" && $sum_clean != $clean_count} {
            lappend mismatched "clean=$sum_clean vs $clean_count"
        }
        if {$sum_max_resistance ne "" && [expr {double($sum_max_resistance)}] != $max_resistance} {
            lappend mismatched "max_resistance=$sum_max_resistance vs $max_resistance"
        }
        if {$sum_worst_pair ne "" && $sum_worst_pair ne $worst_pair} {
            lappend mismatched "worst_pair=$sum_worst_pair vs $worst_pair"
        }
    }

    if {$short_count > 0} {
        set verdict "FAIL"
    } elseif {$leak_count > 0} {
        set verdict "REVIEW"
    } elseif {!$has_summary || [llength $mismatched] > 0} {
        set verdict "INCOMPLETE"
    } else {
        set verdict "PASS"
    }

    return [dict create \
        total_shorts $total_shorts \
        short_count $short_count \
        leak_count $leak_count \
        clean_count $clean_count \
        power_count $power_count \
        ground_count $ground_count \
        mixed_pairs $mixed_pairs \
        max_resistance $max_resistance \
        worst_pair $worst_pair \
        layers_affected $layers_affected \
        mismatched_summary $mismatched \
        verdict $verdict]
}
