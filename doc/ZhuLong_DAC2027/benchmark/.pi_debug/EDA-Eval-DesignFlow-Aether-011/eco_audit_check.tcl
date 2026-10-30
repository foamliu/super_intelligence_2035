# ------------------------------------------------------------------
# layout_eco_audit : audit a pyAether textual ECO report
# ------------------------------------------------------------------
proc layout_eco_audit {report_text} {
    array set records {}
    array set cells {}
    set summary [dict create]
    set summary_present 0

    foreach rawline [split $report_text "\n"] {
        set line [string trim $rawline]
        if {$line eq ""} { continue }
        if {[string index $line 0] eq "#"} { continue }
        set toks [split $line]
        if {[llength $toks] == 0} { continue }
        set t0 [lindex $toks 0]

        if {[string equal -nocase $t0 "ECO"]} {
            if {[llength $toks] < 3} { continue }
            set action [string tolower [lindex $toks 1]]
            set inst   [lindex $toks 2]
            set cell   ""
            set status ""
            set delta  ""

            foreach tok [lrange $toks 3 end] {
                set idx [string first "=" $tok]
                if {$idx < 0} { continue }
                set k [string tolower [string range $tok 0 [expr {$idx - 1}]]]
                set v [string range $tok [expr {$idx + 1}] end]
                switch -- $k {
                    "cell"   { set cell $v }
                    "status" { set status $v }
                    "delta"  { set delta $v }
                }
            }

            set dval 0.0
            if {$delta ne ""} {
                if {[catch {set dval [expr {double($delta)}]}]} {
                    set dval 0.0
                }
            }

            if {$status eq ""} {
                if {$dval > 0.0} {
                    set eff "applied"
                } elseif {$dval < 0.0} {
                    set eff "pending"
                } else {
                    set eff "skipped"
                }
            } else {
                set eff [string tolower $status]
            }

            set key "$action $inst"
            set records($key) [list $action $cell $eff]

        } elseif {[string equal -nocase $t0 "SUMMARY"]} {
            set summary_present 1
            foreach tok [lrange $toks 1 end] {
                set idx [string first "=" $tok]
                if {$idx < 0} { continue }
                set k [string tolower [string range $tok 0 [expr {$idx - 1}]]]
                set v [string range $tok [expr {$idx + 1}] end]
                dict set summary $k $v
            }
        }
    }

    set total_ecos   0
    set add_count    0
    set delete_count 0
    set modify_count 0
    set swap_count   0
    set applied_count  0
    set pending_count  0
    set rejected_count 0
    set skipped_count  0

    foreach k [array names records] {
        incr total_ecos
        set rec   $records($k)
        set act   [lindex $rec 0]
        set cellv [lindex $rec 1]
        set eff   [lindex $rec 2]

        switch -- $act {
            "add"    { incr add_count }
            "delete" { incr delete_count }
            "modify" { incr modify_count }
            "swap"   { incr swap_count }
        }
        switch -- $eff {
            "applied"  { incr applied_count }
            "pending"  { incr pending_count }
            "rejected" { incr rejected_count }
            "skipped"  { incr skipped_count }
        }
        if {$cellv ne ""} {
            set cells($cellv) 1
        }
    }

    set cells_affected [lsort -dictionary [array names cells]]

    set mismatched {}
    foreach field {"total" "add" "delete" "modify" "swap" "applied" "pending" "rejected" "skipped"} {
        if {![dict exists $summary $field]} { continue }
        set sval [dict get $summary $field]
        switch -- $field {
            "total"    { set cval $total_ecos }
            "add"      { set cval $add_count }
            "delete"   { set cval $delete_count }
            "modify"   { set cval $modify_count }
            "swap"     { set cval $swap_count }
            "applied"  { set cval $applied_count }
            "pending"  { set cval $pending_count }
            "rejected" { set cval $rejected_count }
            "skipped"  { set cval $skipped_count }
        }
        if {$sval != $cval} {
            lappend mismatched "$field=$sval vs $cval"
        }
    }

    if {$rejected_count > 0} {
        set verdict "FAIL"
    } elseif {$pending_count > 0} {
        set verdict "REVIEW"
    } elseif {!$summary_present || [llength $mismatched] > 0} {
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

set r [check layout_eco_audit]
puts "RESULT:$r"
if {$r eq "ALL_ASSERTS_PASS"} { puts "DESIGN_FLOW_VERDICT=PASS" } else { puts "DESIGN_FLOW_VERDICT=FAIL" }