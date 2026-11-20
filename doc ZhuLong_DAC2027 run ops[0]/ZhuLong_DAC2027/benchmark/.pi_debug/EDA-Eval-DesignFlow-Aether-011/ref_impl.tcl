# Reference implementation: layout_eco_audit
# Audits a pyAether-emitted ECO (Engineering Change Order) report for a layout cellview.
proc layout_eco_audit {report_text} {
    set add_count 0
    set delete_count 0
    set modify_count 0
    set swap_count 0
    set applied_count 0
    set pending_count 0
    set rejected_count 0
    set skipped_count 0
    set cells_affected {}
    set has_summary 0
    set sum_total ""
    set sum_add ""
    set sum_delete ""
    set sum_modify ""
    set sum_swap ""
    set sum_applied ""
    set sum_pending ""
    set sum_rejected ""
    set sum_skipped ""
    set total_ecos 0

    # LAST-WINS dedup on (action, inst_name): later line replaces earlier fields
    array set eco_data {}

    foreach line [split $report_text "\n"] {
        set line [string trim $line]
        if {$line eq ""} continue
        if {[string index $line 0] eq "#"} continue
        if {[string match "ECO *" $line]} {
            set rest [string range $line 4 end]
            set toks {}
            foreach t [split $rest " "] { if {$t ne ""} { lappend toks $t } }
            set action [lindex $toks 0]
            set inst_name [lindex $toks 1]
            set cell ""
            set status ""
            set delta 0
            foreach tok [lrange $toks 2 end] {
                if {[string match "cell=*" $tok]} {
                    set cell [string range $tok 5 end]
                } elseif {[string match "status=*" $tok]} {
                    set status [string range $tok 7 end]
                } elseif {[string match "delta=*" $tok]} {
                    set delta [string range $tok 6 end]
                }
            }
            if {$delta eq ""} { set delta 0 }
            # LAST-WINS: replace all fields for this (action, inst_name) key
            set eco_data($action,$inst_name) [list $cell $status $delta]
        } elseif {[string match "SUMMARY *" $line]} {
            set has_summary 1
            set rest [string range $line 7 end]
            set toks {}
            foreach t [split $rest " "] { if {$t ne ""} { lappend toks $t } }
            foreach tok $toks {
                if {[string match "total=*" $tok]} {
                    set sum_total [string range $tok 6 end]
                } elseif {[string match "add=*" $tok]} {
                    set sum_add [string range $tok 4 end]
                } elseif {[string match "delete=*" $tok]} {
                    set sum_delete [string range $tok 7 end]
                } elseif {[string match "modify=*" $tok]} {
                    set sum_modify [string range $tok 7 end]
                } elseif {[string match "swap=*" $tok]} {
                    set sum_swap [string range $tok 5 end]
                } elseif {[string match "applied=*" $tok]} {
                    set sum_applied [string range $tok 8 end]
                } elseif {[string match "pending=*" $tok]} {
                    set sum_pending [string range $tok 8 end]
                } elseif {[string match "rejected=*" $tok]} {
                    set sum_rejected [string range $tok 9 end]
                } elseif {[string match "skipped=*" $tok]} {
                    set sum_skipped [string range $tok 8 end]
                }
            }
        }
    }

    set total_ecos [llength [array names eco_data]]

    foreach key [array names eco_data] {
        set action [lindex [split $key ","] 0]
        lassign $eco_data($key) cell status delta
        set act [string tolower [string trim $action]]
        set st [string tolower [string trim $status]]
        # status absent/empty -> infer from delta
        if {$st eq ""} {
            set d [expr {double($delta)}]
            if {$d > 0.0} { set st "applied"
            } elseif {$d == 0.0} { set st "skipped"
            } else { set st "pending" }
        }
        if {$act eq "add"} { incr add_count
        } elseif {$act eq "delete"} { incr delete_count
        } elseif {$act eq "modify"} { incr modify_count
        } elseif {$act eq "swap"} { incr swap_count }

        if {$st eq "applied"} { incr applied_count
        } elseif {$st eq "pending"} { incr pending_count
        } elseif {$st eq "rejected"} { incr rejected_count
        } elseif {$st eq "skipped"} { incr skipped_count }

        if {$cell ne ""} {
            if {$cell ni $cells_affected} { lappend cells_affected $cell }
        }
    }

    set cells_affected [lsort -dictionary $cells_affected]

    # mismatched_summary
    set mismatched {}
    if {$has_summary} {
        if {$sum_total ne "" && $sum_total != $total_ecos} {
            lappend mismatched "total=$sum_total vs $total_ecos"
        }
        if {$sum_add ne "" && $sum_add != $add_count} {
            lappend mismatched "add=$sum_add vs $add_count"
        }
        if {$sum_delete ne "" && $sum_delete != $delete_count} {
            lappend mismatched "delete=$sum_delete vs $delete_count"
        }
        if {$sum_modify ne "" && $sum_modify != $modify_count} {
            lappend mismatched "modify=$sum_modify vs $modify_count"
        }
        if {$sum_swap ne "" && $sum_swap != $swap_count} {
            lappend mismatched "swap=$sum_swap vs $swap_count"
        }
        if {$sum_applied ne "" && $sum_applied != $applied_count} {
            lappend mismatched "applied=$sum_applied vs $applied_count"
        }
        if {$sum_pending ne "" && $sum_pending != $pending_count} {
            lappend mismatched "pending=$sum_pending vs $pending_count"
        }
        if {$sum_rejected ne "" && $sum_rejected != $rejected_count} {
            lappend mismatched "rejected=$sum_rejected vs $rejected_count"
        }
        if {$sum_skipped ne "" && $sum_skipped != $skipped_count} {
            lappend mismatched "skipped=$sum_skipped vs $skipped_count"
        }
    }

    # verdict priority: rejected>0 -> FAIL > pending>0 -> REVIEW >
    #   mismatched or no-summary -> INCOMPLETE > PASS
    if {$rejected_count > 0} {
        set verdict "FAIL"
    } elseif {$pending_count > 0} {
        set verdict "REVIEW"
    } elseif {!$has_summary || [llength $mismatched] > 0} {
        set verdict "INCOMPLETE"
    } else {
        set verdict "PASS"
    }

    return [dict create \
        total_ecos $total_ecos \
        add_count $add_count \
        delete_count $delete_count \
        modify_count $modify_count \
        swap_count $swap_count \
        applied_count $applied_count \
        pending_count $pending_count \
        rejected_count $rejected_count \
        skipped_count $skipped_count \
        cells_affected $cells_affected \
        mismatched_summary $mismatched \
        verdict $verdict]
}
