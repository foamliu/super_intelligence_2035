# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc check {candidate} {
    # ---- Case A: full fixture mirroring the real cliu vsim_report session ----
    # 3 rpts (basic.x4/checkin.x8/misc.x16), pattern.list with 1 comment + 1 blank
    # + 1 dup (mbist_three_deep x2) -> expected_count=6 unique. One extra ran pattern.
    set plistA "avl_ca_odt\nbasic_BurstOrderLengthType\nbasic_allbank_bc8\nmbist_three_deep\n# this is a comment\n\ntm_multirow\ntm_pretest\nmbist_three_deep"
    set repA "=== basic.x4 ===\nTotal Pattern : 3\n Failed Pattern: 1\nGlobal_Seed : 100\n-----------------\navl_ca_odt\nbasic_BurstOrderLengthType\nbasic_allbank_bc8\n=== checkin.x8 ===\nTotal Pattern : 2\n Failed Pattern: 0\nGlobal_Seed : 200\n-----------------\nmbist_three_deep\ntm_multirow\n=== misc.x16 ===\nTotal Pattern : 2\n Failed Pattern: 0\nGlobal_Seed : 300\n-----------------\ntm_pretest\nextra_pattern_x"
    set out [$candidate $repA $plistA]
    assert {[regexp {runs_parsed[[:space:]]+3} $out]} "Case A runs_parsed must be 3"
    assert {[regexp {total_pattern_reported[[:space:]]+7} $out]} "Case A total_pattern_reported must be 7 (3+2+2 header sum)"
    assert {[regexp {total_failed_reported[[:space:]]+1} $out]} "Case A total_failed_reported must be 1"
    assert {[regexp {pattern_list_entries[[:space:]]+7} $out]} "Case A pattern_list_entries must be 7 (actual list lines)"
    assert {[regexp {bytemodes[[:space:]]+x16,x4,x8} $out]} "Case A bytemodes must be sorted x16,x4,x8"
    assert {[regexp {regressions[[:space:]]+basic,checkin,misc} $out]} "Case A regressions must be sorted basic,checkin,misc"
    assert {[regexp {ran_unique[[:space:]]+7} $out]} "Case A ran_unique must be 7"
    assert {[regexp {expected_count[[:space:]]+6} $out]} "Case A expected_count must be 6 (unique; dup mbist_three_deep + comment + blank skipped); naive line-count gives 8"
    assert {[regexp {missing_count[[:space:]]+0} $out]} "Case A missing_count must be 0 (all 6 expected ran)"
    assert {[regexp {extra_count[[:space:]]+1} $out]} "Case A extra_count must be 1 (extra_pattern_x)"
    assert {[regexp {extra_patterns[[:space:]]+extra_pattern_x[[:space:]]+coverage_verdict} $out]} "Case A extra_patterns must list extra_pattern_x"
    assert {[regexp {coverage_verdict[[:space:]]+extra} $out]} "Case A coverage_verdict must be extra (missing=0, extra>0)"

    # ---- Case B: colon-spacing asymmetry tooth + cross-rpt duplicate ----
    # r1 uses 'Total Pattern : 4' (space before colon) + ' Failed Pattern: 2' (leading
    # space, NO space before colon). r2 uses 'Total Pattern: 3' (NO space before colon)
    # + '  Failed Pattern: 1' (two leading spaces). A parser keyed on ONE form misses
    # the other. p1 appears in BOTH rpts -> entries counts it twice, ran_unique once.
    set plistB "p1\np2\np3\np4\np5\np6"
    set repB "=== r1.x4 ===\nTotal Pattern : 4\n Failed Pattern: 2\n-----------------\np1\np2\np3\np4\n=== r2.x8 ===\nTotal Pattern: 3\n  Failed Pattern: 1\n-----------------\np1\np5\np6"
    set outB [$candidate $repB $plistB]
    assert {[regexp {total_pattern_reported[[:space:]]+7} $outB]} "Case B total_pattern_reported must be 7 (4+3); naive single-colon-form regex misses one rpt -> 4 or 3"
    assert {[regexp {total_failed_reported[[:space:]]+3} $outB]} "Case B total_failed_reported must be 3 (2+1); naive single-form misses -> 2 or 1"
    assert {[regexp {pattern_list_entries[[:space:]]+7} $outB]} "Case B pattern_list_entries must be 7 (4+3 actual list lines)"
    assert {[regexp {ran_unique[[:space:]]+6} $outB]} "Case B ran_unique must be 6 (p1 dup across rpts collapsed); naive entries-as-unique gives 7"
    assert {[regexp {coverage_verdict[[:space:]]+complete} $outB]} "Case B coverage_verdict must be complete"

    # ---- Case C: reference-list hygiene tooth (dup + comment + blank + CR + trailing space) ----
    # pattern.list: p1, p2, '# comment', blank, 'p3\r', p2(dup), 'p4  '(trailing spaces).
    # expected_count = 4 unique (p1,p2,p3,p4). A naive that doesn't strip \r sees 'p3\r'
    # != 'p3' -> mis-classifies p3 as both missing AND extra; line-count gives 6.
    set plistC "p1\np2\n# comment line\n\np3\r\np2\np4  "
    set repC "=== only.x4 ===\nTotal Pattern : 5\n Failed Pattern: 0\n-----------------\np1\np2\np3\np4\np5"
    set outC [$candidate $repC $plistC]
    assert {[regexp {expected_count[[:space:]]+4} $outC]} "Case C expected_count must be 4 (unique non-blank non-comment, CR/space trimmed); naive line-count=6, naive-no-dedup=5"
    assert {[regexp {ran_unique[[:space:]]+5} $outC]} "Case C ran_unique must be 5"
    assert {[regexp {missing_count[[:space:]]+0} $outC]} "Case C missing_count must be 0 (p3 matched after CR strip); naive-no-CR-strip reports p3 missing"
    assert {[regexp {extra_count[[:space:]]+1} $outC]} "Case C extra_count must be 1 (p5)"
    assert {[regexp {extra_patterns[[:space:]]+p5[[:space:]]+coverage_verdict} $outC]} "Case C extra_patterns must list p5"
    assert {[regexp {coverage_verdict[[:space:]]+extra} $outC]} "Case C coverage_verdict must be extra"
    assert {![regexp {missing_patterns[[:space:]]+p3} $outC]} "Case C p3 must NOT be missing (CR stripped); naive-no-CR-strip falsely marks p3 missing"

    # ---- Case D: bytemode/regression extraction tooth (.rerun suffix + nosuffix) ----
    # 'basic.x4.rerun' -> bytemode x4 (the .xN token, .rerun IGNORED), reg 'basic'.
    # 'misc.x16' -> x16, reg 'misc'. 'nosuffix' -> bytemode unknown, reg 'nosuffix'.
    # Naive split-by-'.' + last token: basic.x4.rerun -> 'rerun' (WRONG).
    set plistD "pa\npb\npc"
    set repD "=== basic.x4.rerun ===\nTotal Pattern : 1\n Failed Pattern: 0\n-----------------\npa\n=== misc.x16 ===\nTotal Pattern : 1\n Failed Pattern: 0\n-----------------\npb\n=== nosuffix ===\nTotal Pattern : 1\n Failed Pattern: 0\n-----------------\npc"
    set outD [$candidate $repD $plistD]
    assert {[regexp {bytemodes[[:space:]]+unknown,x16,x4} $outD]} "Case D bytemodes must be unknown,x16,x4; naive split-last gives rerun,x16,nosuffix"
    assert {[regexp {regressions[[:space:]]+basic,misc,nosuffix} $outD]} "Case D regressions must be basic,misc,nosuffix"
    assert {[regexp {runs_parsed[[:space:]]+3} $outD]} "Case D runs_parsed must be 3"
    assert {[regexp {coverage_verdict[[:space:]]+complete} $outD]} "Case D coverage_verdict must be complete"

    # ---- Case E: header-vs-list-length mismatch + separator/header-exclusion tooth ----
    # r1 header says 'Total Pattern : 5' but ONLY 4 pattern lines follow the separator.
    # pattern_list_entries counts ACTUAL list lines (4+2=6), NOT the header sum (7).
    # Header lines (Total/Failed/Global_Seed) before the separator must NOT count as
    # pattern names; the '---' separator must NOT count. A parser conflating header
    # count with list entries, or counting all non-blank section lines, is wrong.
    set plistE "pa\npb\npc\npd\npe\npf"
    set repE "=== r1.x4 ===\nTotal Pattern : 5\n Failed Pattern: 1\nGlobal_Seed : 42\n-----------------\npa\npb\npc\npd\n=== r2.x8 ===\nTotal Pattern : 2\n Failed Pattern: 0\n-----------------\npe\npf"
    set outE [$candidate $repE $plistE]
    assert {[regexp {total_pattern_reported[[:space:]]+7} $outE]} "Case E total_pattern_reported must be 7 (header sum 5+2)"
    assert {[regexp {pattern_list_entries[[:space:]]+6} $outE]} "Case E pattern_list_entries must be 6 (ACTUAL list lines 4+2, NOT header sum 7); naive header-trust gives 7, naive count-all-non-blank gives 11"
    assert {[regexp {ran_unique[[:space:]]+6} $outE]} "Case E ran_unique must be 6"
    assert {[regexp {total_failed_reported[[:space:]]+1} $outE]} "Case E total_failed_reported must be 1"
    assert {[regexp {coverage_verdict[[:space:]]+complete} $outE]} "Case E coverage_verdict must be complete"

    # ---- Case F: comprehensive + dup-within-rpt + missing_and_extra + invariant ----
    # r1 lists avl_ca_odt TWICE -> pattern_list_entries counts 3 (raw), ran_unique
    # counts avl_ca_odt once. pattern.list has tm_pretest twice + a comment ->
    # expected_count=4 unique. tm_pretest never ran -> missing. ghost_pattern ran but
    # not in reference -> extra. verdict = missing_and_extra.
    # Invariant: missing_count + ran_unique - extra_count == expected_count.
    set plistF "avl_ca_odt\nbasic_allbank_bc8\ntm_multirow\ntm_pretest\n# dup below\ntm_pretest"
    set repF "=== basic.x4 ===\nTotal Pattern : 3\n Failed Pattern: 1\n-----------------\navl_ca_odt\nbasic_allbank_bc8\navl_ca_odt\n=== checkin.x8 ===\nTotal Pattern : 2\n Failed Pattern: 0\n-----------------\ntm_multirow\nghost_pattern"
    set outF [$candidate $repF $plistF]
    set m {}; regexp {missing_count[[:space:]]+([0-9]+)} $outF -> m
    set e {}; regexp {extra_count[[:space:]]+([0-9]+)} $outF -> e
    set ru {}; regexp {ran_unique[[:space:]]+([0-9]+)} $outF -> ru
    set ec {}; regexp {expected_count[[:space:]]+([0-9]+)} $outF -> ec
    assert {($m + $ru - $e) == $ec} "Case F invariant missing_count + ran_unique - extra_count == expected_count (got m=$m ru=$ru e=$e ec=$ec)"
    assert {[regexp {total_pattern_reported[[:space:]]+5} $outF]} "Case F total_pattern_reported must be 5 (3+2 header sum)"
    assert {[regexp {pattern_list_entries[[:space:]]+5} $outF]} "Case F pattern_list_entries must be 5 (raw list lines incl intra-rpt dup)"
    assert {[regexp {ran_unique[[:space:]]+4} $outF]} "Case F ran_unique must be 4 (avl_ca_odt dup-within-rpt collapsed); naive entries-as-unique gives 5"
    assert {[regexp {expected_count[[:space:]]+4} $outF]} "Case F expected_count must be 4 (tm_pretest dup + comment skipped); naive line-count gives 6"
    assert {[regexp {missing_count[[:space:]]+1} $outF]} "Case F missing_count must be 1 (tm_pretest)"
    assert {[regexp {missing_patterns[[:space:]]+tm_pretest[[:space:]]+extra_count} $outF]} "Case F missing_patterns must list tm_pretest"
    assert {[regexp {extra_count[[:space:]]+1} $outF]} "Case F extra_count must be 1 (ghost_pattern)"
    assert {[regexp {extra_patterns[[:space:]]+ghost_pattern[[:space:]]+coverage_verdict} $outF]} "Case F extra_patterns must list ghost_pattern"
    assert {[regexp {coverage_verdict[[:space:]]+missing_and_extra} $outF]} "Case F coverage_verdict must be missing_and_extra (both missing>0 and extra>0)"
    return "ALL_ASSERTS_PASS"
}
