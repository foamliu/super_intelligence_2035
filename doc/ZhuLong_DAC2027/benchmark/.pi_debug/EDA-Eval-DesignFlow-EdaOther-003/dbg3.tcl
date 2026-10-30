proc L {args} { return [join $args "\n"] }
proc regr_log_classify {log} {
    set lines [split $log "\n"]
    array set outcomeSeq {}
    array set hadRun {}
    array set hadRerun {}
    set pass 0; set fail 0; set timeout 0; set skip 0; set xpass 0; set xfail 0
    set seeds {}; set allTests {}
    foreach line $lines {
        set line [string trim $line]
        if {$line eq ""} { continue }
        if {![regexp {^\[ +([A-Z]+) +\] (.*)$} $line -> status rest]} { continue }
        set rest [string trim $rest]
        set isRerun [regexp {\(rerun #[0-9]+\)} $line]
        set parts [split $rest]
        set testname [lindex $parts 0]
        if {$testname eq ""} { continue }
        if {$testname ni $allTests} { lappend allTests $testname }
        set sd ""; regexp {seed=([0-9]+)} $rest -> sd
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
        set seenBad 0; set isFlaky 0
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
puts "OUT:|[regr_log_classify $logA]|"
