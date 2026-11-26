# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc dget {d k} { return [dict get $d $k] }
proc llist {d k} { return [dict get $d $k] }
proc j {d k} { return [join [dict get $d $k] "|"] }

proc check {candidate} {
    # ---- Case A: baseline all PASS, no retry, no gaps -> wall == sum ----
    set cA {[flow] start 03:00:00
[step:rscalc] start 03:00:00
[step:rscalc] PASS 03:00:10
[step:pe] start 03:00:10
[step:pe] PASS 03:00:25
[step:autovia] start 03:00:25
[step:autovia] PASS 03:00:40
[flow] end 03:00:40}
    set dA [$candidate $cA]
    assert {[j $dA steps_seen] eq "rscalc|pe|autovia"} "A steps_seen first-appearance"
    assert {[j $dA step_status] eq "autovia:PASS|pe:PASS|rscalc:PASS"} "A all PASS"
    assert {[j $dA step_attempts] eq "autovia:1|pe:1|rscalc:1"} "A attempts all 1"
    assert {[j $dA step_duration_sec] eq "autovia:15|pe:15|rscalc:10"} "A durations"
    assert {[llength [llist $dA skip_reasons]] == 0} "A no skips"
    assert {[dget $dA total_wall_sec] == 40} "A wall == sum (no gaps)"
    assert {[llength [llist $dA retried_steps]] == 0} "A no retries"
    assert {[llength [llist $dA skipped_steps]] == 0} "A no skips"
    assert {[llength [llist $dA failed_steps]] == 0} "A no fails"
    assert {[string equal [dget $dA overall_verdict] "PASS"]} "A verdict PASS"

    # ---- Case B: RETRY + dedup TEETH ----
    # autovia fails then retries then PASSES -> attempts=2 (block count, NOT 1
    # retry-line); steps_seen has autovia ONCE; final status PASS; retried.
    set cB {[flow] start 03:00:10
[step:rscalc] start 03:00:10
[step:rscalc] PASS 03:00:20
[step:autovia] start 03:00:20
[step:autovia] ERROR via-insertion-failed 03:00:25
[step:autovia] retry
[step:autovia] start 03:00:25
[step:autovia] PASS 03:00:30
[flow] end 03:00:30}
    set dB [$candidate $cB]
    assert {[j $dB steps_seen] eq "rscalc|autovia"} "B steps_seen dedup (autovia once, TEETH)"
    assert {[j $dB step_attempts] eq "autovia:2|rscalc:1"} "B attempts=2 block count (TEETH: not retry-line count)"
    assert {[j $dB step_status] eq "autovia:PASS|rscalc:PASS"} "B final status PASS (retry succeeded)"
    assert {[j $dB step_duration_sec] eq "autovia:5|rscalc:10"} "B final-block duration (TEETH: not sum of attempts)"
    assert {[llength [llist $dB retried_steps]] == 1} "B one retried"
    assert {[j $dB retried_steps] eq "autovia"} "B retried is autovia"
    assert {[llength [llist $dB failed_steps]] == 0} "B no final fail (transient fail does not count)"
    assert {[llength [llist $dB skipped_steps]] == 0} "B no skips"
    assert {[dget $dB total_wall_sec] == 20} "B wall"
    assert {[string equal [dget $dB overall_verdict] "PASS"]} "B verdict PASS"

    # ---- Case C: SKIP reason coverage TEETH ----
    # rscalc FAILs; pe SKIP upstream-failed:rscalc; qa SKIP user. skipped_steps
    # must include BOTH pe and qa (ALL reasons), not only upstream-failed.
    set cC {[flow] start 03:00:00
[step:rscalc] start 03:00:00
[step:rscalc] FAIL 03:00:05
[step:pe] start 03:00:05
[step:pe] SKIP reason=upstream-failed:rscalc 03:00:06
[step:qa] start 03:00:06
[step:qa] SKIP reason=user 03:00:07
[flow] end 03:00:07}
    set dC [$candidate $cC]
    assert {[j $dC steps_seen] eq "rscalc|pe|qa"} "C steps_seen"
    assert {[j $dC step_status] eq "pe:SKIP|qa:SKIP|rscalc:FAIL"} "C status"
    assert {[j $dC skipped_steps] eq "pe|qa"} "C skipped BOTH reasons (TEETH: not only upstream-failed)"
    assert {[j $dC skip_reasons] eq "pe:upstream-failed:rscalc|qa:user"} "C skip_reasons both"
    assert {[j $dC failed_steps] eq "rscalc"} "C failed rscalc"
    assert {[llength [llist $dC retried_steps]] == 0} "C no retries"
    assert {[dget $dC total_wall_sec] == 7} "C wall"
    assert {[string equal [dget $dC overall_verdict] "ERROR"]} "C verdict ERROR (fail beats skip)"

    # ---- Case D: total_wall vs sum-of-durations TEETH ----
    # 30s setup gap between [flow] start and first step -> wall=40 but
    # sum of per-step final-block durations = 10. Wall is NOT the sum.
    set cD {[flow] start 03:00:00
[step:rscalc] start 03:00:30
[step:rscalc] PASS 03:00:40
[flow] end 03:00:40}
    set dD [$candidate $cD]
    assert {[j $dD steps_seen] eq "rscalc"} "D steps_seen"
    assert {[j $dD step_duration_sec] eq "rscalc:10"} "D step duration 10"
    assert {[dget $dD total_wall_sec] == 40} "D wall=40 (TEETH: NOT sum of durations=10)"
    assert {[string equal [dget $dD overall_verdict] "PASS"]} "D verdict PASS"

    # ---- Case E: MIDNIGHT rollover TEETH ----
    # start 23:59:50, step 23:59:55->00:00:05, end 00:00:10. Durations must
    # wrap +86400, not go negative.
    set cE {[flow] start 23:59:50
[step:rscalc] start 23:59:55
[step:rscalc] PASS 00:00:05
[flow] end 00:00:10}
    set dE [$candidate $cE]
    assert {[j $dE step_duration_sec] eq "rscalc:10"} "E step duration 10 (midnight wrap, TEETH: not negative)"
    assert {[dget $dE total_wall_sec] == 20} "E wall 20 (midnight wrap)"
    assert {[string equal [dget $dE overall_verdict] "PASS"]} "E verdict PASS"

    # ---- Case F: LAST-WINS + verdict priority TEETH ----
    # pe block emits PASS then later ERROR -> final ERROR (last wins, not
    # first). qa SKIP. Verdict = ERROR (FAIL/ERROR priority OVER SKIP), not
    # SKIPPED.
    set cF {[flow] start 03:00:00
[step:pe] start 03:00:00
[step:pe] PASS 03:00:10
[step:pe] ERROR boom 03:00:12
[step:qa] start 03:00:12
[step:qa] SKIP reason=user 03:00:13
[flow] end 03:00:13}
    set dF [$candidate $cF]
    assert {[j $dF step_status] eq "pe:ERROR|qa:SKIP"} "F pe last-wins ERROR (TEETH: not first-wins PASS)"
    assert {[j $dF step_duration_sec] eq "pe:12|qa:1"} "F pe duration to last terminal"
    assert {[j $dF failed_steps] eq "pe"} "F failed pe"
    assert {[j $dF skipped_steps] eq "qa"} "F skipped qa"
    assert {[string equal [dget $dF overall_verdict] "ERROR"]} "F verdict ERROR (TEETH: ERROR priority OVER SKIP, not SKIPPED)"

    return "ALL_ASSERTS_PASS"
}
