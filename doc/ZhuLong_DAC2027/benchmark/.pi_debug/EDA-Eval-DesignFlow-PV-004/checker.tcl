# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc check {candidate} {
    # ---- Case A: baseline -- two violations, one exact-match waiver, one remaining ----
    set vA "MET2.SP\tTOP\t10\t20\tM2
MET3.SP\tTOP\t5\t6\tM3"
    set wA "MET2.SP\tTOP\t10\t20\tM2\tfixed-by-design"
    set d [$candidate $vA $wA]
    assert {[dict get $d total_violations] eq "2"} "A total_violations=2"
    assert {[dict get $d waived_count] eq "1"} "A waived_count=1 (exact match)"
    assert {[dict get $d remaining_count] eq "1"} "A remaining_count=1"
    assert {[dict get $d orphan_waivers] eq "0"} "A orphan=0"
    assert {[dict get $d duplicate_waivers] eq "0"} "A duplicate=0"
    assert {[dict get $d remaining_by_rule MET3.SP] eq "1"} "A remaining_by_rule(MET3.SP)=1"
    assert {[dict get $d audit_verdict] eq "violations"} "A audit_verdict=violations (remaining>0, no audit issues)"

    # ---- Case B: WILDCARD tooth -- waiver with x=* / y=* waives a coordinate-mismatched violation ----
    # A strict-equality matcher fails to waive -> remaining=1 (WRONG), waived=0 (WRONG).
    set vB "MET2.SP\tTOP\t10\t20\tM2"
    set wB "MET2.SP\tTOP\t*\t*\tM2\tcoordinate-agnostic waiver"
    set d [$candidate $vB $wB]
    assert {[dict get $d waived_count] eq "1"} "B waived_count=1 (wildcard x=* y=* matches); strict-equality -> 0 (WRONG)"
    assert {[dict get $d remaining_count] eq "0"} "B remaining_count=0"
    assert {[dict get $d audit_verdict] eq "clean"} "B audit_verdict=clean"

    # ---- Case C: RULE CASE-INSENSITIVITY tooth -- waiver `met2.sp` waives violation `MET2.SP` ----
    # A case-sensitive compare fails -> remaining=1 (WRONG), orphan=1 (WRONG).
    set vC "MET2.SP\tTOP\t1\t2\tM2"
    set wC "met2.sp\tTOP\t1\t2\tM2\tcase-variant rule waiver"
    set d [$candidate $vC $wC]
    assert {[dict get $d waived_count] eq "1"} "C waived_count=1 (rule case-insensitive match: waiver met2.sp vs violation MET2.SP); case-sensitive rule compare -> 0 (WRONG)"
    assert {[dict get $d remaining_count] eq "0"} "C remaining_count=0"
    assert {[dict get $d orphan_waivers] eq "0"} "C orphan=0 (matched despite case difference); case-sensitive -> 1 (WRONG)"
    assert {[dict get $d audit_verdict] eq "clean"} "C audit_verdict=clean"

    # ---- Case D: ORPHAN + DUPLICATE tooth ----
    # 3 violations of rule R. Waiver1 (cell=*) waives all 3 fresh.
    # Waiver2 (cell=*) matches the SAME 3 violations -> all already waived -> DUPLICATE.
    # Waiver3 (rule NOPE) matches nothing -> ORPHAN.
    # remaining=0, orphan=1, duplicate=1 -> audit_verdict=audit_issues.
    set vD "R\tA\t1\t1\tL
R\tB\t2\t2\tL
R\tC\t3\t3\tL"
    set wD "R\t*\t*\t*\tL\tbulk waiver
R\t*\t*\t*\tL\tduplicate bulk waiver
NOPE\t*\t*\t*\tL\tstale typo waiver"
    set d [$candidate $vD $wD]
    assert {[dict get $d total_violations] eq "3"} "D total_violations=3"
    assert {[dict get $d waived_count] eq "3"} "D waived_count=3 (waiver1 waived all 3 fresh); re-apply-every-waiver -> 6 (WRONG double count)"
    assert {[dict get $d remaining_count] eq "0"} "D remaining_count=0"
    assert {[dict get $d orphan_waivers] eq "1"} "D orphan=1 (waiver3 NOPE matched nothing); only-applied-tracking -> 0 (WRONG, hides stale)"
    assert {[dict get $d duplicate_waivers] eq "1"} "D duplicate=1 (waiver2 matched only already-waived); no-first-match-flag -> 0 (WRONG)"
    assert {[dict get $d remaining_by_rule] eq "none"} "D remaining_by_rule=none (all waived)"
    assert {[dict get $d audit_verdict] eq "audit_issues"} "D audit_verdict=audit_issues (remaining=0 but orphan+dup>0)"

    # ---- Case E: CELL SCOPE + LAYER RESTRICTION tooth ----
    # Waiver cell=TOP layer=M2 must ONLY waive the TOP/M2 violation -- NOT the
    # SUB/M2 (wrong cell) and NOT the TOP/M3 (wrong layer). A script ignoring
    # cell/layer over-waives all 3.
    set vE "MET2.SP\tTOP\t1\t1\tM2
MET2.SP\tSUB\t1\t1\tM2
MET2.SP\tTOP\t1\t1\tM3"
    set wE "MET2.SP\tTOP\t*\t*\tM2\tscoped waiver"
    set d [$candidate $vE $wE]
    assert {[dict get $d total_violations] eq "3"} "E total=3"
    assert {[dict get $d waived_count] eq "1"} "E waived_count=1 (only TOP/M2); ignore-cell-layer -> 3 (WRONG over-waive)"
    assert {[dict get $d remaining_count] eq "2"} "E remaining_count=2 (SUB/M2 + TOP/M3)"
    assert {[dict get $d orphan_waivers] eq "0"} "E orphan=0 (waiver matched the TOP/M2)"
    assert {[dict get $d remaining_by_rule MET2.SP] eq "2"} "E remaining_by_rule(MET2.SP)=2"
    assert {[dict get $d audit_verdict] eq "violations"} "E audit_verdict=violations (remaining=2, no audit issues)"

    # ---- Case F: comprehensive (wildcard + case + orphan + duplicate + scope + remaining_by_rule multi-rule) ----
    # Violations: 2x MET2.SP (TOP/M2, SUB/M2), 1x met3.sp (TOP/M3), 1x ANT.DIFF (TOP/M1).
    # Waivers in order:
    #   w1 met2.sp  cell=*  x=* y=* layer=*  -> waives BOTH MET2.SP (fresh)  [APPLIED, 2 fresh]
    #   w2 MET2.SP  cell=TOP x=* y=* layer=M2 -> matches TOP/M2 only, already waived [DUPLICATE]
    #   w3 ANT.DIFF cell=*  x=* y=* layer=*  -> waives ANT.DIFF (fresh)        [APPLIED, 1 fresh]
    #   w4 nope     cell=*  x=* y=* layer=*  -> matches nothing               [ORPHAN]
    # remaining: met3.sp (TOP/M3) un-waived -> 1
    # waived=3, remaining=1, orphan=1, duplicate=1 -> verdict=both
    set vF "MET2.SP\tTOP\t1\t1\tM2
MET2.SP\tSUB\t2\t2\tM2
met3.sp\tTOP\t3\t3\tM3
ANT.DIFF\tTOP\t4\t4\tM1"
    set wF "met2.sp\t*\t*\t*\t*\tbulk MET2 waiver (case-variant)
MET2.SP\tTOP\t*\t*\tM2\tduplicate scoped waiver
ANT.DIFF\t*\t*\t*\t*\tantenna waiver
nope\t*\t*\t*\t*\tstale orphan"
    set d [$candidate $vF $wF]
    assert {[dict get $d total_violations] eq "4"} "F total_violations=4"
    assert {[dict get $d waived_count] eq "3"} "F waived_count=3 (w1:2 + w3:1); re-apply-every -> 4 (WRONG, w2 double-counts TOP/M2)"
    assert {[dict get $d remaining_count] eq "1"} "F remaining_count=1 (met3.sp TOP/M3 un-waived)"
    assert {[dict get $d orphan_waivers] eq "1"} "F orphan=1 (w4 nope)"
    assert {[dict get $d duplicate_waivers] eq "1"} "F duplicate=1 (w2 matched only already-waived TOP/M2)"
    assert {[dict get $d remaining_by_rule met3.sp] eq "1"} "F remaining_by_rule(met3.sp)=1 (original-case key from violation)"
    assert {[dict get $d audit_verdict] eq "both"} "F audit_verdict=both (remaining>0 AND audit issues>0)"
    return "ALL_ASSERTS_PASS"
}
