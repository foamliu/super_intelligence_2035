# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc check {candidate} {
    # ---- Case A: dedup (occurrences vs unique) + early/late split ----
    # IMPRPT-1000 fires TWICE (once early, once late) -> error_count=2, unique=1,
    # and IMPRPT-1000 is in blocking_ids (it had a late blocking occurrence).
    set logA "# Innovus flow log
# Stage: floorplan_complete
**INFO: (IMPRPT-0300) flow begin
**ERROR: (IMPRPT-1000) lib load failed
# Stage: route_complete
**ERROR: (IMPRPT-1000) lib load failed
**WARNING: (IMPRPT-0200) antenna
"
    set d [$candidate $logA]
    assert {[dict get $d total_messages] eq "4"} "A total_messages=4"
    assert {[dict get $d error_count] eq "2"} "A error_count=2 (occurrences incl repeat, NOT unique=1)"
    assert {[dict get $d warning_count] eq "1"} "A warning_count=1"
    assert {[dict get $d info_count] eq "1"} "A info_count=1"
    assert {[dict get $d no_id_count] eq "0"} "A no_id_count=0"
    assert {[dict get $d unique_msg_ids] eq "3"} "A unique_msg_ids=3 (0300,0200,1000)"
    assert {[dict get $d blocking_errors] eq "1"} "A blocking_errors=1 (the late IMPRPT-1000)"
    assert {[dict get $d early_errors] eq "1"} "A early_errors=1 (the early IMPRPT-1000)"
    assert {[dict get $d waived_errors] eq "0"} "A waived_errors=0"
    assert {[dict get $d waived_warnings] eq "0"} "A waived_warnings=0"
    assert {[dict get $d unique_ids] eq "IMPRPT-0200 IMPRPT-0300 IMPRPT-1000"} "A unique_ids sorted"
    assert {[dict get $d blocking_ids] eq "IMPRPT-1000"} "A blocking_ids=IMPRPT-1000"

    # ---- Case B: WAIVED keyword on a CONTINUATION line (teeth) ----
    # A line-1-only WAIVED check misses the waiver on the continuation -> would
    # report blocking_errors=2, waived_errors=0 (WRONG).
    set logB "# Stage: route_complete
**ERROR: (IMPRPT-9001) route DRC
   flagged WAIVED by QA team
**ERROR: (IMPRPT-9002) real route DRC
**WARNING: (IMPRPT-0042) antenna
   WAIVED layout-only
"
    set d [$candidate $logB]
    assert {[dict get $d total_messages] eq "3"} "B total=3"
    assert {[dict get $d error_count] eq "2"} "B error_count=2"
    assert {[dict get $d warning_count] eq "1"} "B warning_count=1"
    assert {[dict get $d blocking_errors] eq "1"} "B blocking_errors=1 (only IMPRPT-9002; 9001 is waived via continuation)"
    assert {[dict get $d waived_errors] eq "1"} "B waived_errors=1 (9001 WAIVED on continuation line)"
    assert {[dict get $d waived_warnings] eq "1"} "B waived_warnings=1 (0042 WAIVED on continuation)"
    assert {[dict get $d blocking_ids] eq "IMPRPT-9002"} "B blocking_ids=IMPRPT-9002"

    # ---- Case C: stage-marker prefix specificity + ordering (teeth) ----
    # A banner comment `# route_complete check will run later` is NOT a stage
    # marker (no `Stage: `). The early IMPRPT-1100 (before the real marker) is
    # EARLY even though the banner mentions route_complete. A naive
    # "route_complete appears anywhere" test marks 1100 as blocking (WRONG).
    set logC "# route_complete check will run later
**ERROR: (IMPRPT-1100) early setup error
# Stage: route_complete
**ERROR: (IMPRPT-1101) late route error
"
    set d [$candidate $logC]
    assert {[dict get $d error_count] eq "2"} "C error_count=2"
    assert {[dict get $d early_errors] eq "1"} "C early_errors=1 (1100 before real marker)"
    assert {[dict get $d blocking_errors] eq "1"} "C blocking_errors=1 (only 1101)"
    assert {[dict get $d blocking_ids] eq "IMPRPT-1101"} "C blocking_ids=IMPRPT-1101"

    # ---- Case D: no-id malformed ERROR (teeth) ----
    # `**ERROR: mystery error no id` (no parens) still counts in error_count
    # and no_id_count, is blocking (late, not waived), but NOT in unique_ids /
    # blocking_ids. A regex requiring `\((IMP...)` to recognize an ERROR drops
    # it (error_count=1, no_id_count=0 -- WRONG).
    set logD "# Stage: route_complete
**ERROR: mystery error no id
**ERROR: (IMPRPT-1200) normal late error
"
    set d [$candidate $logD]
    assert {[dict get $d error_count] eq "2"} "D error_count=2 (incl no-id)"
    assert {[dict get $d no_id_count] eq "1"} "D no_id_count=1"
    assert {[dict get $d unique_msg_ids] eq "1"} "D unique_msg_ids=1 (only 1200 has an id)"
    assert {[dict get $d blocking_errors] eq "2"} "D blocking_errors=2 (1200 + no-id, both late not waived)"
    assert {[dict get $d unique_ids] eq "IMPRPT-1200"} "D unique_ids=IMPRPT-1200 (no-id not listed)"
    assert {[dict get $d blocking_ids] eq "IMPRPT-1200"} "D blocking_ids=IMPRPT-1200 (no-id not listed)"

    # ---- Case E: **WARNING: full word + all-early (teeth) ----
    # No `# Stage: route_complete` at all -> everything early, blocking=0.
    # A matcher accepting only `**WARN:` (not `**WARNING:`) -> warning_count=0 (WRONG).
    set logE "# Stage: place_complete
**WARNING: (IMPRPT-0250) antenna warning
**INFO: (IMPRPT-0350) info message
**ERROR: (IMPRPT-1300) early setup error
"
    set d [$candidate $logE]
    assert {[dict get $d warning_count] eq "1"} "E warning_count=1 (must match **WARNING: full word, not **WARN:)"
    assert {[dict get $d info_count] eq "1"} "E info_count=1"
    assert {[dict get $d error_count] eq "1"} "E error_count=1"
    assert {[dict get $d blocking_errors] eq "0"} "E blocking_errors=0 (no route_complete marker -> all early)"
    assert {[dict get $d early_errors] eq "1"} "E early_errors=1"
    assert {[dict get $d waived_warnings] eq "0"} "E waived_warnings=0"

    # ---- Case F: comprehensive (dedup + continuation WAIVED + no-id + ordering + WARNING) ----
    set logF "# Stage: floorplan_complete
**ERROR: (IMPRPT-1400) floorplan issue
# Stage: route_complete
**ERROR: (IMPRPT-1400) floorplan issue
**ERROR: (IMPRPT-1401) route DRC
   WAIVED known-fp
**ERROR: unlocalized glitch
**WARNING: (IMPRPT-0060) drc
   WAIVED
**WARNING: (IMPRPT-0061) real drc
**INFO: (IMPRPT-0360) summary
"
    set d [$candidate $logF]
    assert {[dict get $d total_messages] eq "7"} "F total=7"
    assert {[dict get $d error_count] eq "4"} "F error_count=4 (1400e,1400l,1401l,noid-l)"
    assert {[dict get $d warning_count] eq "2"} "F warning_count=2"
    assert {[dict get $d info_count] eq "1"} "F info_count=1"
    assert {[dict get $d no_id_count] eq "1"} "F no_id_count=1"
    assert {[dict get $d unique_msg_ids] eq "5"} "F unique_msg_ids=5 (1400,1401,0060,0061,0360)"
    assert {[dict get $d blocking_errors] eq "2"} "F blocking_errors=2 (1400-late + no-id-late; 1401 waived)"
    assert {[dict get $d waived_errors] eq "1"} "F waived_errors=1 (1401 WAIVED on continuation)"
    assert {[dict get $d waived_warnings] eq "1"} "F waived_warnings=1 (0060 WAIVED on continuation)"
    assert {[dict get $d early_errors] eq "1"} "F early_errors=1 (1400 early)"
    # invariant: blocking + waived_errors + early_errors == error_count
    set inv [expr {[dict get $d blocking_errors] + [dict get $d waived_errors] + [dict get $d early_errors]}]
    assert {$inv == [dict get $d error_count]} "F invariant blocking+waived+early == error_count"
    assert {[dict get $d unique_ids] eq "IMPRPT-0060 IMPRPT-0061 IMPRPT-0360 IMPRPT-1400 IMPRPT-1401"} "F unique_ids sorted"
    assert {[dict get $d blocking_ids] eq "IMPRPT-1400"} "F blocking_ids=IMPRPT-1400 (no-id not listed)"
    return "ALL_ASSERTS_PASS"
}

puts "CHECK_RESULT:[check pnr_signoff_report_message_audit]"