# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc dget {d k} { return [dict get $d $k] }
proc llist {d k} { return [dict get $d $k] }

proc check {candidate} {
    # ---- Case A: baseline (no dup, no missing, no recovery, plain sec) -> PASS ----
    set cA "# Compile summary for tag func_basic\n\[OK] tb_a errors=0 warns=2 elapsed=10\n\[OK] tb_b errors=0 warns=1 elapsed=20\n\[SKIP] tb_c errors=0 warns=0 elapsed=0\n"
    set lA "tb_a\ntb_b\ntb_c\n"
    set dA [$candidate $cA $lA]
    assert {[dget $dA tags_compiled]       == 1} "A tags"
    assert {[dget $dA total_rows]          == 3} "A total_rows"
    assert {[dget $dA compiled_ok]         == 2} "A ok"
    assert {[dget $dA compile_fail]        == 0} "A fail"
    assert {[dget $dA skipped]             == 1} "A skip"
    assert {[dget $dA error_total]         == 0} "A err"
    assert {[dget $dA warn_total]          == 3} "A warn"
    assert {[dget $dA duplicate_compiles]  == 0} "A dup"
    assert {[llength [llist $dA missing_compiles]]    == 0} "A missing empty"
    assert {[llength [llist $dA recovered_compiles]]  == 0} "A recovered empty"
    assert {[dget $dA elapsed_total_sec]   == 30} "A elapsed_total"
    assert {[string equal [dget $dA max_elapsed_tb] "tb_b"]} "A max_tb tb_b"
    assert {[string equal [dget $dA overall_verdict] "PASS"]} "A verdict PASS"

    # ---- Case B: elapsed m:ss normalization + max_elapsed_tb tie -> lex smallest ----
    # tb_b first-seen with 1:30 (=90); tb_a also 90 sec. Tie -> lex smallest = tb_a.
    # Naive int("1:30") breaks; naive first-strict-greater returns tb_b.
    set cB "# Compile summary for tag func_basic\n\[OK] tb_b errors=0 warns=0 elapsed=1:30\n\[OK] tb_a errors=0 warns=0 elapsed=90\n"
    set lB "tb_a\ntb_b\n"
    set dB [$candidate $cB $lB]
    assert {[dget $dB elapsed_total_sec]   == 180} "B elapsed_total 90+90"
    assert {[string equal [dget $dB max_elapsed_tb] "tb_a"]} "B max_tb tb_a (lex tie-break)"

    # ---- Case C: last-wins dedup by (tb,tag); re-compile REPLACES not accumulates ----
    # tb_a FAIL(err5,w1,el10) then OK(err0,w2,el15) in SAME tag -> last-wins OK.
    # Naive accumulate -> error_total=5; naive counts compile_fail=1.
    set cC "# Compile summary for tag func_basic\n\[FAIL] tb_a errors=5 warns=1 elapsed=10\n\[OK] tb_a errors=0 warns=2 elapsed=15\n"
    set lC "tb_a\n"
    set dC [$candidate $cC $lC]
    assert {[dget $dC total_rows]          == 2} "C total_rows"
    assert {[dget $dC compiled_ok]         == 1} "C ok (last-wins)"
    assert {[dget $dC compile_fail]        == 0} "C fail 0 (replaced)"
    assert {[dget $dC error_total]         == 0} "C err 0 (replaced not 5)"
    assert {[dget $dC warn_total]          == 2} "C warn 2 (replaced not 3)"
    assert {[dget $dC duplicate_compiles]  == 1} "C dup 1"
    assert {[dget $dC elapsed_total_sec]   == 15} "C elapsed 15 (replaced)"
    assert {[string equal [dget $dC overall_verdict] "PASS"]} "C verdict PASS"

    # ---- Case D: cross-tag recovery (FAIL in tag1, OK in tag2) -> recovered ----
    # Naive "any FAIL -> not recovered" misses recovered=[tb_a].
    set cD "# Compile summary for tag tag1\n\[FAIL] tb_a errors=3 warns=0 elapsed=5\n# Compile summary for tag tag2\n\[OK] tb_a errors=0 warns=0 elapsed=8\n"
    set lD "tb_a\n"
    set dD [$candidate $cD $lD]
    assert {[dget $dD tags_compiled]       == 2} "D tags"
    assert {[dget $dD compiled_ok]         == 1} "D ok"
    assert {[dget $dD compile_fail]        == 1} "D fail"
    assert {[dget $dD error_total]         == 3} "D err 3"
    assert {[dget $dD elapsed_total_sec]   == 13} "D elapsed 13"
    assert {[dget $dD duplicate_compiles]  == 0} "D dup 0 (different tags)"
    set rcD [llist $dD recovered_compiles]
    assert {[llength $rcD] == 1 && [string equal [lindex $rcD 0] "tb_a"]} "D recovered=tb_a"
    assert {[string equal [dget $dD overall_verdict] "FAIL"]} "D verdict FAIL (fail>0)"

    # ---- Case E: missing_compiles + verdict INCOMPLETE (no FAIL, missing) ----
    # Naive PASS (missing ignored).
    set cE "# Compile summary for tag func_basic\n\[OK] tb_a errors=0 warns=1 elapsed=10\n"
    set lE "tb_a\ntb_z\n"
    set dE [$candidate $cE $lE]
    set mcE [llist $dE missing_compiles]
    assert {[llength $mcE] == 1 && [string equal [lindex $mcE 0] "tb_z"]} "E missing=tb_z"
    assert {[dget $dE compile_fail]        == 0} "E fail 0"
    assert {[string equal [dget $dE overall_verdict] "INCOMPLETE"]} "E verdict INCOMPLETE"

    # ---- Case F: same tb across DIFFERENT tags is NOT a duplicate ----
    # Naive "same tb = dup" -> duplicate_compiles=1 (wrong).
    set cF "# Compile summary for tag tag1\n\[OK] tb_a errors=0 warns=0 elapsed=5\n# Compile summary for tag tag2\n\[OK] tb_a errors=0 warns=0 elapsed=7\n"
    set lF "tb_a\n"
    set dF [$candidate $cF $lF]
    assert {[dget $dF tags_compiled]       == 2} "F tags"
    assert {[dget $dF total_rows]          == 2} "F total_rows"
    assert {[dget $dF compiled_ok]         == 2} "F ok 2"
    assert {[dget $dF duplicate_compiles]  == 0} "F dup 0 (different tags)"
    assert {[dget $dF elapsed_total_sec]   == 12} "F elapsed 12"

    # ---- Case G: empty inputs -> all zero, max_elapsed_tb "" , verdict PASS ----
    # Naive crashes on empty / wrong max_tb.
    set dG [$candidate "" ""]
    assert {[dget $dG tags_compiled]       == 0} "G tags 0"
    assert {[dget $dG total_rows]          == 0} "G rows 0"
    assert {[dget $dG compiled_ok]         == 0} "G ok 0"
    assert {[dget $dG compile_fail]        == 0} "G fail 0"
    assert {[dget $dG skipped]             == 0} "G skip 0"
    assert {[dget $dG error_total]         == 0} "G err 0"
    assert {[dget $dG warn_total]          == 0} "G warn 0"
    assert {[dget $dG duplicate_compiles]  == 0} "G dup 0"
    assert {[llength [llist $dG missing_compiles]]   == 0} "G missing empty"
    assert {[llength [llist $dG recovered_compiles]] == 0} "G recovered empty"
    assert {[dget $dG elapsed_total_sec]   == 0} "G elapsed 0"
    assert {[string equal [dget $dG max_elapsed_tb] ""]} "G max_tb empty"
    assert {[string equal [dget $dG overall_verdict] "PASS"]} "G verdict PASS"

    return "ALL_ASSERTS_PASS"
}
