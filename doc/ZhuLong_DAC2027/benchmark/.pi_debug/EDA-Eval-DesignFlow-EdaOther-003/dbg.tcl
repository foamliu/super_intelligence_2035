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
    return "parsed: statuslines recognized. pass=$pass fail=$fail timeout=$timeout skip=$skip xpass=$xpass xfail=$xfail tests=$allTests"
}
set logA {[ RUN    ] ddr_init_test seed=111
[ PASS   ] ddr_init_test seed=111 wall=12.3s
xrun: *W,VSDBA: too few drivers on ddr.dq
[ RUN    ] ddr_write_read_test seed=222
[ FAIL   ] ddr_write_read_test seed=222 wall=45.1s exit=1}
puts [regr_log_classify $logA]
