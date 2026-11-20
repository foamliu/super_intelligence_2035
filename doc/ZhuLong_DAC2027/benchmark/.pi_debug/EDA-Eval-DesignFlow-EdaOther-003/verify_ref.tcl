#!/usr/bin/env tclsh
proc regr_log_classify {log} {
    set lines [split $log "\n"]
    array set outcomeSeq {}
    array set hadRun {}
    array set hadRerun {}
    set pass 0
    set fail 0
    set timeout 0
    set skip 0
    set xpass 0
    set xfail 0
    set seeds {}
    set allTests {}
    foreach line $lines {
        set line [string trim $line]
        if {$line eq ""} { continue }
        if {![regexp {^\[ +([A-Z]+) *\] (.*)$} $line -> status rest]} { continue }
        set rest [string trim $rest]
        set isRerun [regexp {\(rerun #[0-9]+\)} $line]
        set parts [split $rest]
        set testname [lindex $parts 0]
        if {$testname eq ""} { continue }
        if {$testname ni $allTests} { lappend allTests $testname }
        set sd ""
        regexp {seed=([0-9]+)} $rest -> sd
        if {$sd ne ""} { lappend seeds $sd }
        if {$isRerun} { set hadRerun($testname) 1 }
        switch -- $status {
            RUN { set hadRun($testname) 1 }
            PASS { incr pass; lappend outcomeSeq($testname) PASS }
            FAIL { incr fail; lappend outcomeSeq($testname) FAIL }
            TIMEOUT { incr timeout; lappend outcomeSeq($testname) TIMEOUT }
            SKIP { incr skip; lappend outcomeSeq($testname) SKIP }
            XPASS { incr xpass; lappend outcomeSeq($testname) XPASS }
            XFAIL { incr xfail; lappend outcomeSeq($testname) XFAIL }
            default { continue }
        }
    }
    set failCount [expr {$fail + $xpass}]
    set totalRuns [expr {$pass + $fail + $timeout + $xpass + $xfail}]
    set uniqueTests [llength $allTests]
    set uniqueSeeds [llength [lsort -unique $seeds]]
    set incomplete 0
    foreach t $allTests {
        if {[info exists hadRun($t)]} {
            set outs {}
            if {[info exists outcomeSeq($t)]} { set outs $outcomeSeq($t) }
            if {[llength $outs] == 0} { incr incomplete }
        }
    }
    set rerunList {}
    foreach t [lsort $allTests] {
        if {[info exists hadRerun($t)]} { lappend rerunList $t }
    }
    set flakyList {}
    foreach t [lsort $allTests] {
        set outs {}
        if {[info exists outcomeSeq($t)]} { set outs $outcomeSeq($t) }
        set seenBad 0
        set isFlaky 0
        foreach o $outs {
            if {$o eq "FAIL" || $o eq "TIMEOUT"} { set seenBad 1 }
            if {$o eq "PASS" && $seenBad} { set isFlaky 1 }
        }
        if {$isFlaky} { lappend flakyList $t }
    }
    set denom [expr {$pass + $failCount + $timeout}]
    if {$denom > 0} {
        set rate [format "%.4f" [expr {double($pass) / double($denom)}]]
    } else {
        set rate "0.0000"
    }
    set out "total_runs $totalRuns unique_tests $uniqueTests pass_count $pass fail_count $failCount timeout_count $timeout skipped_count $skip xpass_count $xpass xfail_ok_count $xfail incomplete_runs $incomplete rerun_tests"
    foreach t $rerunList { append out " $t" }
    append out " flaky_tests"
    foreach t $flakyList { append out " $t" }
    append out " unique_seeds $uniqueSeeds pass_rate $rate"
    return $out
}

# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc L {args} {
    # build a multi-line log from event lines (args passed as braces to avoid [..] command-substitution)
    return [join $args "\n"]
}
proc check {candidate} {
    # ---- Case A: full fixture mirroring a real DV regression session ----
    # 7 tests: init(pass), write_read(fail->rerun pass = flaky+rerun),
    # stress(timeout), ca(skip, no RUN), ecc(xpass->fail), power(xfail->ok),
    # dqs(RUN only -> incomplete). Plus 2 noise lines that must be ignored.
    set logA [L \
        {# Regression run 2026-10-29 14:23:11} \
        {[ RUN    ] ddr_init_test seed=111} \
        {[ PASS   ] ddr_init_test seed=111 wall=12.3s} \
        {xrun: *W,VSDBA: too few drivers on ddr.dq} \
        {[ RUN    ] ddr_write_read_test seed=222} \
        {[ FAIL   ] ddr_write_read_test seed=222 wall=45.1s exit=1} \
        {[ RUN    ] ddr_write_read_test seed=222 (rerun #2)} \
        {[ PASS   ] ddr_write_read_test seed=222 wall=44.0s (rerun #2)} \
        {[ RUN    ] ddr_stress_test seed=333} \
        {[ TIMEOUT] ddr_stress_test seed=333 wall=3600.0s} \
        {[ SKIP   ] ddr_ca_test reason=dependency_failed} \
        {[ RUN    ] ddr_ecc_test seed=444} \
        {[ XPASS  ] ddr_ecc_test seed=444 wall=22.0s} \
        {[ RUN    ] ddr_power_test seed=555} \
        {[ XFAIL  ] ddr_power_test seed=555 wall=18.0s} \
        {[ RUN    ] ddr_dqs_test seed=666} \
        {# Regression summary: see report.txt} \
    ]
    set out [$candidate $logA]
    assert {[regexp {total_runs[[:space:]]+6} $out]} "Case A total_runs must be 6 (PASS,FAIL,PASS,TIMEOUT,XPASS,XFAIL); RUN/SKIP not counted"
    assert {[regexp {unique_tests[[:space:]]+7} $out]} "Case A unique_tests must be 7"
    assert {[regexp {pass_count[[:space:]]+2} $out]} "Case A pass_count must be 2 (init + write_read rerun)"
    assert {[regexp {fail_count[[:space:]]+2} $out]} "Case A fail_count must be 2 (raw FAIL + XPASS); naive that puts XPASS in pass would report 1"
    assert {[regexp {timeout_count[[:space:]]+1} $out]} "Case A timeout_count must be 1"
    assert {[regexp {skipped_count[[:space:]]+1} $out]} "Case A skipped_count must be 1"
    assert {[regexp {xpass_count[[:space:]]+1} $out]} "Case A xpass_count must be 1"
    assert {[regexp {xfail_ok_count[[:space:]]+1} $out]} "Case A xfail_ok_count must be 1 (XFAIL is OK, NOT in fail_count)"
    assert {[regexp {incomplete_runs[[:space:]]+1} $out]} "Case A incomplete_runs must be 1 (ddr_dqs_test RUN with no outcome)"
    assert {[regexp {rerun_tests[[:space:]]+ddr_write_read_test[[:space:]]+flaky_tests} $out]} "Case A rerun_tests must list ddr_write_read_test then flaky_tests"
    assert {[regexp {flaky_tests[[:space:]]+ddr_write_read_test[[:space:]]+unique_seeds} $out]} "Case A flaky_tests must list ddr_write_read_test (FAIL-then-PASS)"
    assert {[regexp {unique_seeds[[:space:]]+6} $out]} "Case A unique_seeds must be 6 (111,222,333,444,555,666; SKIP has no seed)"
    assert {[regexp {pass_rate[[:space:]]+0\.4000} $out]} "Case A pass_rate must be 0.4000 = 2/(2+2+1); naive XPASS-in-pass gives 2/(2+1+1)=0.5000"

    # ---- Case B: XPASS-is-failure tooth ----
    # t1 PASS, t2 XPASS, t3 FAIL. XPASS must inflate fail_count, not pass_count.
    set logB [L \
        {[ RUN ] t1 seed=1} \
        {[ PASS ] t1 seed=1 wall=1s} \
        {[ RUN ] t2 seed=2} \
        {[ XPASS ] t2 seed=2 wall=1s} \
        {[ RUN ] t3 seed=3} \
        {[ FAIL ] t3 seed=3 wall=1s exit=1} \
    ]
    set outB [$candidate $logB]
    assert {[regexp {pass_count[[:space:]]+1} $outB]} "Case B pass_count must be 1 (only t1); XPASS must NOT count as pass"
    assert {[regexp {fail_count[[:space:]]+2} $outB]} "Case B fail_count must be 2 (t3 FAIL + t2 XPASS); naive XPASS-as-pass reports 1"
    assert {[regexp {xpass_count[[:space:]]+1} $outB]} "Case B xpass_count must be 1"
    assert {[regexp {total_runs[[:space:]]+3} $outB]} "Case B total_runs must be 3"
    assert {[regexp {pass_rate[[:space:]]+0\.3333} $outB]} "Case B pass_rate must be 0.3333 = 1/(1+2+0); naive reports 0.6667"

    # ---- Case C: XFAIL-is-OK tooth ----
    # t1 PASS, t2 XFAIL, t3 FAIL. XFAIL must NOT inflate fail_count.
    set logC [L \
        {[ RUN ] t1 seed=1} \
        {[ PASS ] t1 seed=1 wall=1s} \
        {[ RUN ] t2 seed=2} \
        {[ XFAIL ] t2 seed=2 wall=1s} \
        {[ RUN ] t3 seed=3} \
        {[ FAIL ] t3 seed=3 wall=1s exit=1} \
    ]
    set outC [$candidate $logC]
    assert {[regexp {pass_count[[:space:]]+1} $outC]} "Case C pass_count must be 1"
    assert {[regexp {fail_count[[:space:]]+1} $outC]} "Case C fail_count must be 1 (only t3 FAIL; XFAIL is OK); naive XFAIL-as-fail reports 2"
    assert {[regexp {xfail_ok_count[[:space:]]+1} $outC]} "Case C xfail_ok_count must be 1"
    assert {[regexp {pass_rate[[:space:]]+0\.5000} $outC]} "Case C pass_rate must be 0.5000 = 1/(1+1+0); naive reports 0.3333"

    # ---- Case D: TIMEOUT != FAIL + RUN-not-outcome + incomplete tooth ----
    # t1 RUN+PASS, t2 RUN+TIMEOUT, t3 RUN only (incomplete). No FAIL anywhere.
    set logD [L \
        {[ RUN ] t1 seed=1} \
        {[ PASS ] t1 seed=1 wall=1s} \
        {[ RUN ] t2 seed=2} \
        {[ TIMEOUT ] t2 seed=2 wall=3600s} \
        {[ RUN ] t3 seed=3} \
    ]
    set outD [$candidate $logD]
    assert {[regexp {total_runs[[:space:]]+2} $outD]} "Case D total_runs must be 2 (PASS+TIMEOUT); RUN lines must NOT count as outcomes"
    assert {[regexp {pass_count[[:space:]]+1} $outD]} "Case D pass_count must be 1"
    assert {[regexp {fail_count[[:space:]]+0} $outD]} "Case D fail_count must be 0 (TIMEOUT is not FAIL); naive timeout-as-fail reports 1"
    assert {[regexp {timeout_count[[:space:]]+1} $outD]} "Case D timeout_count must be 1"
    assert {[regexp {incomplete_runs[[:space:]]+1} $outD]} "Case D incomplete_runs must be 1 (t3 RUN, no outcome)"
    assert {[regexp {unique_tests[[:space:]]+3} $outD]} "Case D unique_tests must be 3 (t3 counts even though incomplete)"
    assert {[regexp {pass_rate[[:space:]]+0\.5000} $outD]} "Case D pass_rate must be 0.5000 = 1/(1+0+1)"

    # ---- Case E: flaky-direction-order tooth ----
    # t1 PASS then FAIL(rerun) = REGRESSION (final FAIL), rerun but NOT flaky.
    # t2 FAIL then PASS(rerun) = FLAKY, rerun.  t3 PASS = normal.
    set logE [L \
        {[ RUN ] t1 seed=1} \
        {[ PASS ] t1 seed=1 wall=1s} \
        {[ RUN ] t1 seed=1 (rerun #2)} \
        {[ FAIL ] t1 seed=1 wall=1s exit=1 (rerun #2)} \
        {[ RUN ] t2 seed=2} \
        {[ FAIL ] t2 seed=2 wall=1s exit=1} \
        {[ RUN ] t2 seed=2 (rerun #2)} \
        {[ PASS ] t2 seed=2 wall=1s (rerun #2)} \
        {[ RUN ] t3 seed=3} \
        {[ PASS ] t3 seed=3 wall=1s} \
    ]
    set outE [$candidate $logE]
    assert {[regexp {rerun_tests[[:space:]]+t1[[:space:]]+t2[[:space:]]+flaky_tests} $outE]} "Case E rerun_tests must list BOTH t1 and t2 (both had rerun marker)"
    # flaky_tests must contain t2 but NOT t1 (order matters)
    assert {[regexp {flaky_tests[[:space:]]+t2[[:space:]]+unique_seeds} $outE]} "Case E flaky_tests must list ONLY t2 (FAIL-then-PASS)"
    assert {![regexp {flaky_tests[[:space:]]+t1[[:space:]]} $outE]} "Case E flaky_tests must NOT include t1 (PASS-then-FAIL is a regression, not flaky); naive order-blind impl marks t1 flaky"
    assert {[regexp {pass_count[[:space:]]+3} $outE]} "Case E pass_count must be 3 (t1 first PASS, t2 rerun PASS, t3 PASS)"
    assert {[regexp {fail_count[[:space:]]+2} $outE]} "Case E fail_count must be 2 (t1 rerun FAIL, t2 first FAIL)"
    assert {[regexp {total_runs[[:space:]]+5} $outE]} "Case E total_runs must be 5 (PASS,FAIL,FAIL,PASS,PASS)"

    # ---- Case F: comprehensive + SKIP-not-in-denominator + invariant + noise ----
    set logF [L \
        {# Regression run 2026-10-29 16:00:00} \
        {xrun(64): 05.0047 ns: *W,VSDBA:} \
        {[ RUN    ] a1 seed=1} \
        {[ PASS   ] a1 seed=1 wall=2.0s} \
        {[ RUN    ] a2 seed=2} \
        {[ FAIL   ] a2 seed=2 wall=5.0s exit=1} \
        {[ RUN    ] a2 seed=2 (rerun #2)} \
        {[ PASS   ] a2 seed=2 wall=4.0s (rerun #2)} \
        {[ RUN    ] a3 seed=3} \
        {[ TIMEOUT] a3 seed=3 wall=3600.0s} \
        {[ SKIP   ] a4 reason=dep_not_ready} \
        {[ RUN    ] a5 seed=5} \
        {[ XPASS  ] a5 seed=5 wall=3.0s} \
        {[ RUN    ] a6 seed=6} \
        {[ XFAIL  ] a6 seed=6 wall=2.0s} \
        {[ RUN    ] a7 seed=7} \
        {[ RUN    ] a8 seed=8} \
        {[ PASS   ] a8 seed=8 wall=2.0s} \
        {# End of regression} \
    ]
    set outF [$candidate $logF]
    # invariant: total_runs == pass + fail + timeout + xpass + xfail
    set m {}
    regexp {total_runs[[:space:]]+([0-9]+)} $outF -> m
    set tr $m
    set p {}; set fraw {}; set to {}; set xp {}; set xf {}
    regexp {pass_count[[:space:]]+([0-9]+)} $outF -> p
    regexp {^.*fail_count[[:space:]]+([0-9]+)} $outF -> fraw
    regexp {timeout_count[[:space:]]+([0-9]+)} $outF -> to
    regexp {xpass_count[[:space:]]+([0-9]+)} $outF -> xp
    regexp {xfail_ok_count[[:space:]]+([0-9]+)} $outF -> xf
    # pass_count + (raw fail = fail_count - xpass) + timeout + xpass + xfail == total_runs
    set rawFail [expr {$fraw - $xp}]
    assert {($p + $rawFail + $to + $xp + $xf) == $tr} "Case F invariant total_runs == pass+rawfail+timeout+xpass+xfail (got tr=$tr p=$p rawfail=$rawFail to=$to xp=$xp xf=$xf)"
    assert {[regexp {total_runs[[:space:]]+7} $outF]} "Case F total_runs must be 7"
    assert {[regexp {unique_tests[[:space:]]+8} $outF]} "Case F unique_tests must be 8 (a1..a8)"
    assert {[regexp {pass_count[[:space:]]+3} $outF]} "Case F pass_count must be 3 (a1, a2 rerun, a8)"
    assert {[regexp {fail_count[[:space:]]+2} $outF]} "Case F fail_count must be 2 (a2 FAIL + a5 XPASS)"
    assert {[regexp {timeout_count[[:space:]]+1} $outF]} "Case F timeout_count must be 1"
    assert {[regexp {skipped_count[[:space:]]+1} $outF]} "Case F skipped_count must be 1 (a4)"
    assert {[regexp {xpass_count[[:space:]]+1} $outF]} "Case F xpass_count must be 1"
    assert {[regexp {xfail_ok_count[[:space:]]+1} $outF]} "Case F xfail_ok_count must be 1"
    assert {[regexp {incomplete_runs[[:space:]]+1} $outF]} "Case F incomplete_runs must be 1 (a7 RUN, no outcome)"
    assert {[regexp {rerun_tests[[:space:]]+a2[[:space:]]+flaky_tests} $outF]} "Case F rerun_tests must list a2"
    assert {[regexp {flaky_tests[[:space:]]+a2[[:space:]]+unique_seeds} $outF]} "Case F flaky_tests must list a2"
    assert {[regexp {unique_seeds[[:space:]]+7} $outF]} "Case F unique_seeds must be 7 (1,2,3,5,6,7,8; a4 SKIP has no seed)"
    assert {[regexp {pass_rate[[:space:]]+0\.5000} $outF]} "Case F pass_rate must be 0.5000 = 3/(3+2+1); SKIP/XFAIL/incomplete excluded from denominator"
    return "ALL_ASSERTS_PASS"
}


if {[catch {set r [check regr_log_classify]} err]} {
    puts "CHECK_ERROR: $err"
    exit 1
}
puts "RESULT:$r"
if {$r eq "ALL_ASSERTS_PASS"} { puts "DESIGN_FLOW_VERDICT=PASS" } else { puts "DESIGN_FLOW_VERDICT=FAIL" }
