# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc dget {d k} { return [dict get $d $k] }
proc llist {d k} { return [dict get $d $k] }

proc check {candidate} {
    # ---- Case A: baseline (no flaky, no missing, no dup) -> PASS ----
    set sA "=== func_basic ===\ntest_a P\ntest_b P\ntest_c S\n=== func_checkin ===\ntest_a P\ntest_d P\n"
    set lA "test_a\ntest_b\ntest_c\ntest_d\n"
    set dA [$candidate $sA $lA]
    assert {[dget $dA tags_scanned]   == 2} "A tags"
    assert {[dget $dA total_tests_run] == 5} "A total_runs"
    assert {[dget $dA passed]  == 4} "A passed"
    assert {[dget $dA failed]  == 0} "A failed"
    assert {[dget $dA skipped] == 1} "A skipped"
    assert {[dget $dA timeout] == 0} "A timeout"
    assert {[dget $dA pending] == 0} "A pending"
    assert {[llength [llist $dA flaky_tests]]   == 0} "A flaky empty"
    assert {[llength [llist $dA missing_tests]] == 0} "A missing empty"
    assert {[dget $dA duplicate_runs] == 0} "A dup"
    assert {[dget $dA pass_rate] == 100} "A pass_rate"
    assert {[string equal [dget $dA overall_verdict] "PASS"]} "A verdict PASS"

    # ---- Case B: flaky TEETH (P in one tag, F in another) -> FAIL ----
    # Real run from the mined session: dqs_osc_manual passed in func_basic but
    # failed in func_checkin. Naive per-tag dedup / "any pass -> pass" misses
    # the cross-tag flakiness and would not flag it.
    set sB "=== func_basic ===\ndqs_osc_manual P\navl_no_act_wr P\n=== func_checkin ===\ndqs_osc_manual F\navl_no_act_wr P\n"
    set lB "dqs_osc_manual\navl_no_act_wr\n"
    set dB [$candidate $sB $lB]
    assert {[dget $dB passed] == 3 && [dget $dB failed] == 1} "B counts"
    assert {[llist $dB flaky_tests] eq "dqs_osc_manual"} "B flaky (TEETH: cross-tag P+F)"
    assert {[string equal [dget $dB overall_verdict] "FAIL"]} "B verdict FAIL (TEETH: flaky -> FAIL even pass_rate=75)"
    assert {[dget $dB pass_rate] == 75} "B pass_rate 75"

    # ---- Case C: outcome-code TEETH (pending . , skip S, timeout T) ----
    # pass_rate denominator EXCLUDES skipped and pending; timeout counts as a
    # scoring failure. Naive "non-P = fail" overcounts (skips+pending) and
    # naive "pass/total" undercounts.
    set sC "=== func_basic ===\ntest_a P\ntest_b F\ntest_c S\ntest_d T\ntest_e .\n"
    set lC "test_a\ntest_b\ntest_c\ntest_d\ntest_e\n"
    set dC [$candidate $sC $lC]
    assert {[dget $dC passed] == 1 && [dget $dC failed] == 1 && [dget $dC skipped] == 1 && [dget $dC timeout] == 1 && [dget $dC pending] == 1} "C counts"
    assert {[dget $dC pass_rate] == 33} "C pass_rate 33 (TEETH: denom=1+1+1 excludes skip+pending)"
    assert {[llength [llist $dC flaky_tests]] == 0} "C no flaky (test_b only F, no P)"
    assert {[string equal [dget $dC overall_verdict] "FAIL"]} "C verdict FAIL (timeout counts as failure)"

    # ---- Case D: missing-test TEETH -> INCOMPLETE (not PASS) ----
    # test_z is declared but never run in any tag. Naive "if no row, skip"
    # silently drops it and reports PASS at 100% pass_rate -- wrong.
    set sD "=== func_basic ===\ntest_a P\ntest_b P\n"
    set lD "test_a\ntest_b\ntest_z\n"
    set dD [$candidate $sD $lD]
    assert {[dget $dD pass_rate] == 100} "D pass_rate 100"
    assert {[llist $dD missing_tests] eq "test_z"} "D missing (TEETH: declared but absent)"
    assert {[string equal [dget $dD overall_verdict] "INCOMPLETE"]} "D verdict INCOMPLETE (TEETH: not PASS despite 100%)"

    # ---- Case E: duplicate-rerun TEETH (P then F inside one tag) ----
    # test_a re-ran inside func_basic: row1 P, row2 F. last-wins -> F for the
    # aggregate count; duplicate_runs=1. RAW flaky detection still sees both
    # P and F -> flaky. Naive "first row wins" keeps P (wrong count) and naive
    # "dedup kills flaky" misses the rerun flip.
    set sE "=== func_basic ===\ntest_a P\ntest_a F\ntest_b P\n"
    set lE "test_a\ntest_b\n"
    set dE [$candidate $sE $lE]
    assert {[dget $dE total_tests_run] == 3} "E total_runs raw"
    assert {[dget $dE duplicate_runs] == 1} "E dup (TEETH: rerun)"
    assert {[dget $dE passed] == 1 && [dget $dE failed] == 1} "E counts last-wins (test_a=F, test_b=P)"
    assert {[llist $dE flaky_tests] eq "test_a"} "E flaky from rerun (TEETH: raw P+F coexist)"
    assert {[dget $dE pass_rate] == 50} "E pass_rate 50"
    assert {[string equal [dget $dE overall_verdict] "FAIL"]} "E verdict FAIL"

    # ---- Case F: comprehensive + invariant ----
    set sF "=== func_basic ===\ntest_a P\ntest_b F\ntest_a P\n=== func_checkin ===\ntest_a F\ntest_c S\ntest_d T\n"
    set lF "test_a\ntest_b\ntest_c\ntest_d\ntest_e\n"
    set dF [$candidate $sF $lF]
    assert {[dget $dF tags_scanned] == 2} "F tags"
    assert {[dget $dF total_tests_run] == 6} "F total_runs"
    assert {[dget $dF duplicate_runs] == 1} "F dup (test_a rerun in basic)"
    assert {[dget $dF passed] == 1 && [dget $dF failed] == 2 && [dget $dF skipped] == 1 && [dget $dF timeout] == 1 && [dget $dF pending] == 0} "F counts last-wins"
    assert {[llist $dF flaky_tests] eq "test_a"} "F flaky (test_a P in basic, F in checkin)"
    assert {[llist $dF missing_tests] eq "test_e"} "F missing (test_e declared, absent)"
    assert {[dget $dF pass_rate] == 25} "F pass_rate 25 (1/(1+2+1))"
    assert {[string equal [dget $dF overall_verdict] "FAIL"]} "F verdict FAIL (failed+timeout)"
    # invariant: duplicate_runs + unique(test,tag) == total_tests_run
    set uniq [expr {[dget $dF passed] + [dget $dF failed] + [dget $dF skipped] + [dget $dF timeout] + [dget $dF pending]}]
    assert {([dget $dF duplicate_runs] + $uniq) == [dget $dF total_tests_run]} "F invariant dup+unique==total"

    return "CHECK_PASS"
}
