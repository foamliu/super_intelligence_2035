# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}

proc check {candidate} {
    # The real waive list from the mined PDK-QA emptyDeriveLayer session.
    set WL {FB_CMP POWER_SINGLE VOLTAGE_L VOLTAGE_H PROBEPAD}

    # ---- Case A: mixed -- has-shapes + empty-unwaived + empty-waived.
    # The realistic mixed tape-out: M1/M2/VOLTAGE_H have shapes (OK); VIA1/VIA2
    # are empty and NOT waived (real defects); FB_CMP/POWER_SINGLE/VOLTAGE_L/
    # PROBEPAD are empty but waived (expected). verdict = FAIL.
    # A naive "0 errors = PASS" classifier flags M1/M2/VOLTAGE_H as broken and
    # VIA1/VIA2/FB_CMP/... as clean -> wrong on every axis.
    set sa {
RULE: deriveCheck_M1            ERRORS: 42
RULE: deriveCheck_M2            ERRORS: 18
RULE: deriveCheck_VIA1          ERRORS: 0
RULE: deriveCheck_VIA2          ERRORS: 0
RULE: deriveCheck_FB_CMP        ERRORS: 0
RULE: deriveCheck_POWER_SINGLE  ERRORS: 0
RULE: deriveCheck_VOLTAGE_L     ERRORS: 0
RULE: deriveCheck_VOLTAGE_H     ERRORS: 12
RULE: deriveCheck_PROBEPAD      ERRORS: 0
}
    set d [$candidate $sa $WL]
    assert {[dict get $d total_derive_layers] eq "9"} "A total"
    assert {[dict get $d has_shapes_count] eq "3"} "A has_shapes"
    assert {[dict get $d empty_count] eq "6"} "A empty"
    assert {[dict get $d waived_empty_count] eq "4"} "A waived_empty"
    assert {[dict get $d empty_unwaived] eq "VIA1,VIA2"} "A empty_unwaived"
    assert {[dict get $d verdict] eq "fail"} "A verdict"
    assert {[dict get $d fail_reasons] eq "empty_unwaived:VIA1;empty_unwaived:VIA2"} "A fail_reasons"

    # ---- Case B: all layers have shapes -> verdict PASS.
    # Verdict-inversion teeth: naive "0 errors = PASS" says every layer FAILS
    # (errors>0) -> verdict FAIL. Correct answer is PASS (all layers non-empty).
    set sb {
RULE: deriveCheck_M1   ERRORS: 42
RULE: deriveCheck_M2   ERRORS: 18
RULE: deriveCheck_M3   ERRORS: 7
}
    set d [$candidate $sb]
    assert {[dict get $d total_derive_layers] eq "3"} "B total"
    assert {[dict get $d has_shapes_count] eq "3"} "B has_shapes"
    assert {[dict get $d empty_count] eq "0"} "B empty"
    assert {[dict get $d waived_empty_count] eq "0"} "B waived_empty"
    assert {[dict get $d empty_unwaived] eq "none"} "B empty_unwaived"
    assert {[dict get $d verdict] eq "pass"} "B verdict"
    assert {[dict get $d fail_reasons] eq "none"} "B fail_reasons"

    # ---- Case C: all empty, ALL waived -> verdict PASS (waive handling).
    # Waive teeth: every layer is empty, but every one is waived -> no real
    # defect -> PASS. A classifier that ignores the waive list says FAIL.
    set sc {
RULE: deriveCheck_FB_CMP        ERRORS: 0
RULE: deriveCheck_POWER_SINGLE  ERRORS: 0
RULE: deriveCheck_PROBEPAD      ERRORS: 0
}
    set d [$candidate $sc $WL]
    assert {[dict get $d total_derive_layers] eq "3"} "C total"
    assert {[dict get $d has_shapes_count] eq "0"} "C has_shapes"
    assert {[dict get $d empty_count] eq "3"} "C empty"
    assert {[dict get $d waived_empty_count] eq "3"} "C waived_empty"
    assert {[dict get $d empty_unwaived] eq "none"} "C empty_unwaived"
    assert {[dict get $d verdict] eq "pass"} "C verdict"
    assert {[dict get $d fail_reasons] eq "none"} "C fail_reasons"

    # ---- Case D: all empty, NONE waived -> verdict FAIL (core inversion).
    # The core teeth: every layer is empty and none waived -> every layer is a
    # real defect -> FAIL. Naive "0 errors = PASS" says every layer is clean
    # -> verdict PASS (exactly backwards).
    set sd {
RULE: deriveCheck_M1    ERRORS: 0
RULE: deriveCheck_M2    ERRORS: 0
RULE: deriveCheck_VIA1  ERRORS: 0
}
    set d [$candidate $sd]
    assert {[dict get $d total_derive_layers] eq "3"} "D total"
    assert {[dict get $d has_shapes_count] eq "0"} "D has_shapes"
    assert {[dict get $d empty_count] eq "3"} "D empty"
    assert {[dict get $d waived_empty_count] eq "0"} "D waived_empty"
    assert {[dict get $d empty_unwaived] eq "M1,M2,VIA1"} "D empty_unwaived"
    assert {[dict get $d verdict] eq "fail"} "D verdict"
    assert {[dict get $d fail_reasons] eq "empty_unwaived:M1;empty_unwaived:M2;empty_unwaived:VIA1"} "D fail_reasons"

    # ---- Case E: format robustness (lower-case, leading ws, extra spaces) +
    # one empty-unwaived defect. Tests the regex tolerates cosmetic variance
    # and still isolates the single real defect (VIA1) while FB_CMP is waived.
    set se {
   rule:  deriveCheck_M1   errors:  42
rule:  deriveCheck_M2  errors: 18
   rule: deriveCheck_VIA1   errors: 0
rule: deriveCheck_FB_CMP   errors: 0
}
    set d [$candidate $se {FB_CMP}]
    assert {[dict get $d total_derive_layers] eq "4"} "E total"
    assert {[dict get $d has_shapes_count] eq "2"} "E has_shapes"
    assert {[dict get $d empty_count] eq "2"} "E empty"
    assert {[dict get $d waived_empty_count] eq "1"} "E waived_empty"
    assert {[dict get $d empty_unwaived] eq "VIA1"} "E empty_unwaived"
    assert {[dict get $d verdict] eq "fail"} "E verdict"
    assert {[dict get $d fail_reasons] eq "empty_unwaived:VIA1"} "E fail_reasons"

    return "PASS 5 cases"
}
