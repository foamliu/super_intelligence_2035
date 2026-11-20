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
# Checker for layout_eco_audit
# Builds fixtures inline and asserts on the returned dict.
proc _chk {name cond} {
    global _chk_pass _chk_fail _chk_first
    if {![uplevel 1 [list expr $cond]]} {
        set _chk_pass 0
        if {$_chk_fail == 0} { set _chk_first $name }
        incr _chk_fail
        puts "ASSERT FAIL: $name"
    } else {
        incr _chk_pass
    }
}
proc _chk_done {} {
    global _chk_pass _chk_fail
    if {$_chk_fail == 0} { puts "ALL_ASSERTS_PASS" } else { puts "ASSERTS_FAILED" }
}
proc check {fn} {
    global _chk_pass _chk_fail _chk_first
    set _chk_pass 1; set _chk_fail 0; set _chk_first ""

    # ---- Case A: baseline (mixed actions/status/cells + summary match) ----
    set a "# ECO report
ECO add u1 cell=NAND2 status=applied delta=1
ECO delete u2 cell=NOR2 status=applied delta=-1
ECO modify u3 cell=INV status=pending delta=2
ECO swap u4 cell=FF status=skipped delta=0
SUMMARY total=4 add=1 delete=1 modify=1 swap=1 applied=2 pending=1 rejected=0 skipped=1"
    set rA [$fn $a]
    _chk A_total {[dict get $rA total_ecos] == 4}
    _chk A_add {[dict get $rA add_count] == 1}
    _chk A_delete {[dict get $rA delete_count] == 1}
    _chk A_modify {[dict get $rA modify_count] == 1}
    _chk A_swap {[dict get $rA swap_count] == 1}
    _chk A_applied {[dict get $rA applied_count] == 2}
    _chk A_pending {[dict get $rA pending_count] == 1}
    _chk A_rejected {[dict get $rA rejected_count] == 0}
    _chk A_skipped {[dict get $rA skipped_count] == 1}
    _chk A_cells {[llength [dict get $rA cells_affected]] == 4}
    _chk A_mismatch_empty {[llength [dict get $rA mismatched_summary]] == 0}
    _chk A_verdict {[dict get $rA verdict] eq "REVIEW"}

    # ---- Case B: action CASE-INSENSITIVE teeth ----
    set b "# mixed case action
ECO ADD n1 cell=A status=applied delta=1
ECO Delete n2 cell=B status=applied delta=-1
ECO MODIFY n3 cell=C status=applied delta=2
ECO Swap n4 cell=D status=applied delta=1
SUMMARY total=4 add=1 delete=1 modify=1 swap=1 applied=4 pending=0 rejected=0 skipped=0"
    set rB [$fn $b]
    _chk B_total {[dict get $rB total_ecos] == 4}
    _chk B_add {[dict get $rB add_count] == 1}
    _chk B_delete {[dict get $rB delete_count] == 1}
    _chk B_modify {[dict get $rB modify_count] == 1}
    _chk B_swap {[dict get $rB swap_count] == 1}
    _chk B_applied {[dict get $rB applied_count] == 4}
    _chk B_mismatch_empty {[llength [dict get $rB mismatched_summary]] == 0}
    _chk B_verdict {[dict get $rB verdict] eq "PASS"}

    # ---- Case C: status CASE-INSENSITIVE teeth ----
    set c "# mixed case status
ECO add n1 cell=A status=APPLIED delta=1
ECO add n2 cell=B status=Pending delta=2
ECO add n3 cell=C status=REJECTED delta=-1
ECO add n4 cell=D status=Skipped delta=0
SUMMARY total=4 add=4 delete=0 modify=0 swap=0 applied=1 pending=1 rejected=1 skipped=1"
    set rC [$fn $c]
    _chk C_applied {[dict get $rC applied_count] == 1}
    _chk C_pending {[dict get $rC pending_count] == 1}
    _chk C_rejected {[dict get $rC rejected_count] == 1}
    _chk C_skipped {[dict get $rC skipped_count] == 1}
    _chk C_mismatch_empty {[llength [dict get $rC mismatched_summary]] == 0}
    _chk C_verdict {[dict get $rC verdict] eq "FAIL"}

    # ---- Case D: dup (action, inst_name) LAST-WINS (replace, not sum, not first-wins) ----
    set d "# dup pair: add,u1 appears twice; last wins (pending, not applied)
ECO add u1 cell=NAND2 status=applied delta=1
ECO add u1 cell=NOR2 status=pending delta=2
ECO delete u2 cell=INV status=applied delta=-1
SUMMARY total=2 add=1 delete=1 modify=0 swap=0 applied=1 pending=1 rejected=0 skipped=0"
    set rD [$fn $d]
    _chk D_total {[dict get $rD total_ecos] == 2}
    _chk D_add {[dict get $rD add_count] == 1}
    _chk D_delete {[dict get $rD delete_count] == 1}
    _chk D_applied {[dict get $rD applied_count] == 1}
    _chk D_pending {[dict get $rD pending_count] == 1}
    # cells_affected: dup replaced cell=NOR2, so NAND2 should NOT be present (last-wins)
    _chk D_cells {[llength [dict get $rD cells_affected]] == 2}
    _chk D_cells_no_nand2 {[lsearch [dict get $rD cells_affected] NAND2] < 0}
    _chk D_cells_nor2 {[lsearch [dict get $rD cells_affected] NOR2] >= 0}
    _chk D_mismatch_empty {[llength [dict get $rD mismatched_summary]] == 0}
    _chk D_verdict {[dict get $rD verdict] eq "REVIEW"}

    # ---- Case E: (action, inst_name) ORDERED: add,u1 != modify,u1 -- different keys ----
    set e "# same inst name different action -> DIFFERENT entries (not normalized)
ECO add u1 cell=A status=applied delta=1
ECO modify u1 cell=A status=applied delta=2
SUMMARY total=2 add=1 delete=0 modify=1 swap=0 applied=2 pending=0 rejected=0 skipped=0"
    set rE [$fn $e]
    _chk E_total {[dict get $rE total_ecos] == 2}
    _chk E_add {[dict get $rE add_count] == 1}
    _chk E_modify {[dict get $rE modify_count] == 1}
    _chk E_cells {[llength [dict get $rE cells_affected]] == 1}
    _chk E_mismatch_empty {[llength [dict get $rE mismatched_summary]] == 0}
    _chk E_verdict {[dict get $rE verdict] eq "PASS"}

    # ---- Case F: status absent -> infer from delta thresholds ----
    set f "# no status field; infer from delta
ECO add a1 cell=A delta=1
ECO add a2 cell=B delta=0
ECO add a3 cell=C delta=-2
SUMMARY total=3 add=3 delete=0 modify=0 swap=0 applied=1 pending=1 rejected=0 skipped=1"
    set rF [$fn $f]
    _chk F_applied {[dict get $rF applied_count] == 1}
    _chk F_pending {[dict get $rF pending_count] == 1}
    _chk F_skipped {[dict get $rF skipped_count] == 1}
    _chk F_rejected {[dict get $rF rejected_count] == 0}
    _chk F_mismatch_empty {[llength [dict get $rF mismatched_summary]] == 0}
    _chk F_verdict {[dict get $rF verdict] eq "REVIEW"}

    # ---- Case G: delta boundary (delta>0 applied, delta==0 skipped, delta<0 pending) ----
    set g "# boundary: 0.0=skipped (inclusive), positive=applied, negative=pending
ECO add p1 cell=A delta=0.0
ECO add p2 cell=B delta=0.001
ECO add p3 cell=C delta=-0.001
SUMMARY total=3 add=3 delete=0 modify=0 swap=0 applied=1 pending=1 rejected=0 skipped=1"
    set rG [$fn $g]
    _chk G_applied {[dict get $rG applied_count] == 1}
    _chk G_pending {[dict get $rG pending_count] == 1}
    _chk G_skipped {[dict get $rG skipped_count] == 1}
    _chk G_mismatch_empty {[llength [dict get $rG mismatched_summary]] == 0}
    _chk G_verdict {[dict get $rG verdict] eq "REVIEW"}

    # ---- Case H: missing delta -> default 0 -> skipped ----
    set h "# delta absent -> default 0 -> skipped (0.0 == 0.0)
ECO add x1 cell=A status=
ECO add x2 cell=B status=pending delta=-1
SUMMARY total=2 add=2 delete=0 modify=0 swap=0 applied=0 pending=1 rejected=0 skipped=1"
    set rH [$fn $h]
    _chk H_total {[dict get $rH total_ecos] == 2}
    _chk H_skipped {[dict get $rH skipped_count] == 1}
    _chk H_pending {[dict get $rH pending_count] == 1}
    _chk H_mismatch_empty {[llength [dict get $rH mismatched_summary]] == 0}
    _chk H_verdict {[dict get $rH verdict] eq "REVIEW"}

    # ---- Case I: cells_affected dedup + lex-sort ----
    set i "# multiple ECOs same cell -> dedup; sort lex
ECO add u1 cell=ZZTOP status=applied delta=1
ECO delete u2 cell=AND2 status=applied delta=-1
ECO modify u3 cell=AND2 status=applied delta=2
SUMMARY total=3 add=1 delete=1 modify=1 swap=0 applied=3 pending=0 rejected=0 skipped=0"
    set rI [$fn $i]
    _chk I_total {[dict get $rI total_ecos] == 3}
    _chk I_cells {[llength [dict get $rI cells_affected]] == 2}
    _chk I_cells_sorted {[lindex [dict get $rI cells_affected] 0] eq "AND2"}
    _chk I_cells_sorted2 {[lindex [dict get $rI cells_affected] 1] eq "ZZTOP"}
    _chk I_mismatch_empty {[llength [dict get $rI mismatched_summary]] == 0}
    _chk I_verdict {[dict get $rI verdict] eq "PASS"}

    # ---- Case J: cells_affected includes empty-cell entries (cell absent -> not added; empty cell treated as no cell) ----
    set j "# cell absent on some entries -> those not in cells_affected
ECO add u1 cell=A status=applied delta=1
ECO add u2 status=applied delta=1
ECO add u3 cell= status=applied delta=1
SUMMARY total=3 add=3 delete=0 modify=0 swap=0 applied=3 pending=0 rejected=0 skipped=0"
    set rJ [$fn $j]
    _chk J_total {[dict get $rJ total_ecos] == 3}
    _chk J_cells {[llength [dict get $rJ cells_affected]] == 1}
    _chk J_cells_only_a {[lindex [dict get $rJ cells_affected] 0] eq "A"}
    _chk J_mismatch_empty {[llength [dict get $rJ mismatched_summary]] == 0}
    _chk J_verdict {[dict get $rJ verdict] eq "PASS"}

    # ---- Case K: mismatched_summary (total wrong, add wrong; absent fields not reported) ----
    set k "# summary total wrong (99 vs 2), add wrong (5 vs 1), applied wrong (9 vs 2); delete absent not reported
ECO add u1 cell=A status=applied delta=1
ECO delete u2 cell=B status=applied delta=-1
SUMMARY total=99 add=5 applied=9"
    set rK [$fn $k]
    _chk K_total {[dict get $rK total_ecos] == 2}
    _chk K_add {[dict get $rK add_count] == 1}
    _chk K_applied {[dict get $rK applied_count] == 2}
    _chk K_mismatch_len {[llength [dict get $rK mismatched_summary]] == 3}
    _chk K_verdict {[dict get $rK verdict] eq "INCOMPLETE"}

    # ---- Case L: no SUMMARY -> verdict INCOMPLETE (0 rejected, 0 pending); mismatched empty ----
    set l "# no summary line; all applied
ECO add a1 cell=A status=applied delta=1
ECO add a2 cell=B status=applied delta=1"
    set rL [$fn $l]
    _chk L_total {[dict get $rL total_ecos] == 2}
    _chk L_applied {[dict get $rL applied_count] == 2}
    _chk L_rejected {[dict get $rL rejected_count] == 0}
    _chk L_pending {[dict get $rL pending_count] == 0}
    _chk L_mismatch_empty {[llength [dict get $rL mismatched_summary]] == 0}
    _chk L_verdict {[dict get $rL verdict] eq "INCOMPLETE"}

    # ---- Case M: verdict priority (REVIEW when pending>0 and rejected=0, even with mismatched) ----
    set m "# rejected=0, pending=1 (REVIEW beats INCOMPLETE from mismatched)
ECO add a1 cell=A status=pending delta=-1
SUMMARY total=99 applied=0 pending=1"
    set rM [$fn $m]
    _chk M_pending {[dict get $rM pending_count] == 1}
    _chk M_rejected {[dict get $rM rejected_count] == 0}
    _chk M_mismatch_len {[llength [dict get $rM mismatched_summary]] == 1}
    _chk M_verdict {[dict get $rM verdict] eq "REVIEW"}

    _chk_done
    if {$_chk_fail == 0} { return "ALL_ASSERTS_PASS" } else { return "ASSERTS_FAILED:$_chk_first" }
}
set r [check layout_eco_audit]; puts "RESULT:$r"; if {$r eq "ALL_ASSERTS_PASS"} { puts "DESIGN_FLOW_VERDICT=PASS" } else { puts "DESIGN_FLOW_VERDICT=FAIL" }
