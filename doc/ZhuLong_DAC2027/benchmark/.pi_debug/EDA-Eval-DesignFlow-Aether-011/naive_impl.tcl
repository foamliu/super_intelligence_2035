# Naive implementation: layout_eco_audit (intentionally WRONG on many traps)
proc layout_eco_audit {report_text} {
    set add 0
    set del 0
    set mod 0
    set sw 0
    set appl 0
    set pend 0
    set rej 0
    set skip 0
    set cells {}
    set total 0
    array set eco {}
    foreach line [split $report_text "\n"] {
        set line [string trim $line]
        if {$line eq ""} continue
        if {[string index $line 0] eq "#"} continue
        if {[string match "ECO *" $line]} {
            set rest [string range $line 4 end]
            set toks {}
            foreach t [split $rest " "] { if {$t ne ""} { lappend toks $t } }
            set action [lindex $toks 0]
            set inst [lindex $toks 1]
            set key "$action $inst"
            # naive: FIRST-WINS (don't replace on dup)
            if {![info exists eco($key)]} {
                set eco($key) 1
                incr total
                # naive: case-SENSITIVE action
                if {$action eq "add"} {
                    incr add
                } elseif {$action eq "delete"} {
                    incr del
                } elseif {$action eq "modify"} {
                    incr mod
                } elseif {$action eq "swap"} {
                    incr sw
                }
                set status ""
                set cell ""
                set delta 0
                foreach tok [lrange $toks 2 end] {
                    if {[string match "status=*" $tok]} {
                        set status [string range $tok 7 end]
                    } elseif {[string match "cell=*" $tok]} {
                        set cell [string range $tok 5 end]
                    } elseif {[string match "delta=*" $tok]} {
                        set delta [string range $tok 6 end]
                    }
                }
                # naive: case-SENSITIVE status, absent -> skipped (no inference)
                if {$status eq "applied"} {
                    incr appl
                } elseif {$status eq "pending"} {
                    incr pend
                } elseif {$status eq "rejected"} {
                    incr rej
                } else {
                    incr skip
                }
                # naive: always add cell even if empty
                lappend cells $cell
            }
        }
    }
    # naive: no summary reconciliation (mismatched always empty)
    # naive verdict: INCOMPLETE before REVIEW (wrong priority)
    if {$rej > 0} {
        set verdict "FAIL"
    } elseif {[info exists sum_has] && $sum_has} {
        set verdict "INCOMPLETE"
    } elseif {$pend > 0} {
        set verdict "REVIEW"
    } else {
        set verdict "PASS"
    }
    return [dict create \
        total_ecos $total \
        add_count $add \
        delete_count $del \
        modify_count $mod \
        swap_count $sw \
        applied_count $appl \
        pending_count $pend \
        rejected_count $rej \
        skipped_count $skip \
        cells_affected $cells \
        mismatched_summary {} \
        verdict $verdict]
}
