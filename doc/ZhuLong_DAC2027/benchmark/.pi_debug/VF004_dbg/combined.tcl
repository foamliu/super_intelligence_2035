proc vflow_manifest_audit {manifest_text} {
    # Parse sections. NOTE: do NOT use nested-path `dict lappend ... a b c $val`
    # -- it SPLITS a list-valued $val into its elements (Tcl quirk). Use explicit
    # get / lappend (single arg -> one element) / dict set instead.
    set declared {}
    set step_status {}    ;# step -> status (last-wins)
    set step_arts {}      ;# step -> list of artifact records (each: path size checksum signoff)
    set cur ""
    foreach line [split $manifest_text "\n"] {
        set line [string trim $line]
        if {$line eq ""} continue
        set c0 [string index $line 0]
        if {$c0 eq ";" || $c0 eq "#"} continue
        # section header?
        if {[regexp {^\[([^\]]+)\]$} $line -> sec]} {
            set cur $sec
            # A NEW [step:<name>] block header RESETS this step's status and
            # artifact list to empty (last-wins: the earlier block is entirely
            # discarded, NOT merged). Runs on every block header, including
            # duplicates, so the LAST block fully overwrites earlier ones.
            if {[regexp {^step:(.+)$} $sec -> sname]} {
                dict set step_status $sname ""
                dict set step_arts $sname [list]
            }
            continue
        }
        # key = value
        if {![regexp {^([^=]+?)=(.*)$} $line -> rawk rawv]} continue
        set k [string trim $rawk]
        set v [string trim $rawv]
        if {$cur eq "declared_outputs"} {
            dict set declared $k $v
        } elseif {[regexp {^step:(.+)$} $cur -> sname]} {
            if {![dict exists $step_status $sname]} {
                dict set step_status $sname ""
                dict set step_arts $sname [list]
            }
            if {$k eq "status"} {
                dict set step_status $sname $v
            } elseif {$k eq "artifact"} {
                # path|size|checksum|signoff
                set parts [split $v "|"]
                if {[llength $parts] == 4} {
                    lassign $parts path size checksum signoff
                    set rec [list $path $size $checksum $signoff]
                    set cur_arts [dict get $step_arts $sname]
                    lappend cur_arts $rec
                    dict set step_arts $sname $cur_arts
                }
            }
        }
        # other sections ignored
    }

    # Compute totals per step.
    set total 0
    set npass 0; set nfail 0; set nskip 0
    set missing {}
    set ghost {}
    set zerobyte {}
    set misschk {}
    # basename -> dict(step -> 1) tracking cross-step ownership
    set base2steps {}
    dict for {s st} $step_status {
        incr total
        if {$st eq "PASS"} { incr npass } elseif {$st eq "FAIL"} { incr nfail } elseif {$st eq "SKIP"} { incr nskip }
        set arts [dict get $step_arts $s]
        if {$st eq "PASS" && [llength $arts] == 0} {
            lappend missing $s
        }
        foreach a $arts {
            lassign $a path size checksum signoff
            # basename
            set lastslash [string last "/" $path]
            if {$lastslash >= 0} {
                set base [string range $path [expr {$lastslash + 1}] end]
            } else {
                set base $path
            }
            # track cross-step basename ownership (per step, dedup via dict)
            if {![dict exists $base2steps $base]} {
                dict set base2steps $base [dict create $s 1]
            } else {
                dict set base2steps $base $s 1
            }
            if {$st eq "FAIL" || $st eq "SKIP"} {
                lappend ghost $path
            }
            if {$st eq "PASS" && $size == 0} {
                lappend zerobyte $path
            }
            if {$signoff eq "true" && $checksum eq ""} {
                lappend misschk $path
            }
        }
    }

    # name_collisions: basename owned by >=2 distinct steps
    # (owners is a dict step->1; dict size = number of distinct steps)
    set collisions {}
    dict for {base owners} $base2steps {
        if {[dict size $owners] >= 2} {
            lappend collisions $base
        }
    }

    set missing [lsort $missing]
    set ghost [lsort $ghost]
    set zerobyte [lsort $zerobyte]
    set misschk [lsort $misschk]
    set collisions [lsort $collisions]

    set verdict "clean"
    if {[llength $missing] || [llength $ghost] || [llength $zerobyte] || [llength $misschk] || [llength $collisions]} {
        set verdict "dirty"
    }

    return [dict create \
        total_steps                $total \
        pass_steps                 $npass \
        fail_steps                 $nfail \
        skip_steps                 $nskip \
        missing_artifacts          $missing \
        ghost_artifacts            $ghost \
        zero_byte_artifacts        $zerobyte \
        missing_checksum_signoff   $misschk \
        name_collisions            $collisions \
        verdict                    $verdict]
}

# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc dget {d k} { return [dict get $d $k] }
proc llist {d k} { return [dict get $d $k] }
proc j {d k} { return [join [dict get $d $k] "|"] }

proc check {candidate} {
    # ---- Case A: baseline clean manifest -> verdict clean ----
    set cA {[declared_outputs]
rscalc = /out/rscalc/
pe = /out/pe/
autovia = /out/autovia/
[step:rscalc]
status = PASS
artifact = /out/rscalc/rscalc.csv|4096|a1b2c3|false
[step:pe]
status = PASS
artifact = /out/pe/pe.log|2048|d4e5f6|false
[step:autovia]
status = PASS
artifact = /out/autovia/autovia.gds|8192|9a8b7c|true
}
    set dA [$candidate $cA]
    assert {[dget $dA total_steps] == 3} "A total_steps"
    assert {[dget $dA pass_steps] == 3} "A pass_steps"
    assert {[dget $dA fail_steps] == 0} "A fail_steps"
    assert {[dget $dA skip_steps] == 0} "A skip_steps"
    assert {[llength [llist $dA missing_artifacts]] == 0} "A no missing"
    assert {[llength [llist $dA ghost_artifacts]] == 0} "A no ghost"
    assert {[llength [llist $dA zero_byte_artifacts]] == 0} "A no zero-byte"
    assert {[llength [llist $dA missing_checksum_signoff]] == 0} "A no missing-checksum"
    assert {[llength [llist $dA name_collisions]] == 0} "A no collisions"
    assert {[string equal [dget $dA verdict] "clean"]} "A verdict clean"

    # ---- Case B: missing_artifact TEETH + ghost TEETH ----
    # rscalc PASS but ZERO artifacts (silently dropped) -> missing_artifacts.
    # pe SKIP but lists an artifact (stale leftover) -> ghost_artifacts.
    # autovia PASS with a real artifact -> fine.
    # Naive "count total artifacts > 0 -> ok" misses BOTH the per-step missing
    # AND the ghost (it does not gate artifacts on step status).
    set cB {[declared_outputs]
rscalc = /out/rscalc/
pe = /out/pe/
autovia = /out/autovia/
[step:rscalc]
status = PASS
[step:pe]
status = SKIP
artifact = /out/pe/pe.log|2048|d4e5f6|false
[step:autovia]
status = PASS
artifact = /out/autovia/autovia.gds|8192|9a8b7c|true
}
    set dB [$candidate $cB]
    assert {[llist $dB missing_artifacts] eq {rscalc}} "B missing_artifacts (TEETH: PASS with zero artifacts)"
    assert {[llist $dB ghost_artifacts] eq {/out/pe/pe.log}} "B ghost_artifacts (TEETH: artifact under SKIP)"
    assert {[llength [llist $dB zero_byte_artifacts]] == 0} "B no zero-byte"
    assert {[string equal [dget $dB verdict] "dirty"]} "B verdict dirty"

    # ---- Case C: zero-byte TEETH + missing-checksum-signoff TEETH ----
    # rscalc PASS but artifact size 0 (truncated write) -> zero_byte_artifacts.
    # autovia PASS, artifact signoff=true but checksum EMPTY -> missing_checksum_signoff.
    # Naive "size >= 0 ok" misses the zero-byte; naive "checksum present
    # somewhere ok" misses the signoff-gated requirement.
    set cC {[declared_outputs]
rscalc = /out/rscalc/
autovia = /out/autovia/
[step:rscalc]
status = PASS
artifact = /out/rscalc/rscalc.csv|0||false
[step:autovia]
status = PASS
artifact = /out/autovia/autovia.gds|8192||true
}
    set dC [$candidate $cC]
    assert {[llist $dC zero_byte_artifacts] eq {/out/rscalc/rscalc.csv}} "C zero_byte (TEETH: PASS + size 0)"
    assert {[llist $dC missing_checksum_signoff] eq {/out/autovia/autovia.gds}} "C missing-checksum-signoff (TEETH: signoff=true, checksum empty)"
    assert {[llength [llist $dC missing_artifacts]] == 0} "C no missing (has artifacts)"
    assert {[string equal [dget $dC verdict] "dirty"]} "C verdict dirty"

    # ---- Case D: name_collision TEETH (cross-step) vs per-step dup (NOT collision) ----
    # rscalc writes /out/rscalc/result.gds; autovia writes /out/autovia/result.gds.
    # Basename `result.gds` under TWO DISTINCT steps -> name_collisions.
    # pe writes /out/pe/pe.log TWICE under the SAME step -> per-step duplicate,
    # NOT a cross-step collision (basename pe.log appears under only ONE step).
    # Naive "basename seen >1 -> collision" wrongly flags pe.log.
    set cD {[declared_outputs]
rscalc = /out/rscalc/
pe = /out/pe/
autovia = /out/autovia/
[step:rscalc]
status = PASS
artifact = /out/rscalc/result.gds|100|aa|false
[step:pe]
status = PASS
artifact = /out/pe/pe.log|10|bb|false
artifact = /out/pe/pe.log|10|bb|false
[step:autovia]
status = PASS
artifact = /out/autovia/result.gds|200|cc|true
}
    set dD [$candidate $cD]
    assert {[llist $dD name_collisions] eq {result.gds}} "D name_collisions (TEETH: cross-step, NOT per-step dup)"
    assert {[string equal [dget $dD verdict] "dirty"]} "D verdict dirty"

    # ---- Case E: last-wins TEETH (duplicate [step:X] block) ----
    # rscalc has TWO blocks: first PASS with an artifact, second FAIL with NO
    # artifacts. last-wins -> status FAIL, artifact list EMPTY. Therefore:
    #   pass_steps excludes rscalc; fail_steps includes rscalc;
    #   missing_artifacts does NOT include rscalc (FAIL, not PASS);
    #   ghost_artifacts does NOT include rscalc's first-block artifact (the
    #   first block is entirely discarded, NOT merged).
    # Naive "merge artifact lists across blocks" wrongly keeps the first
    # artifact and either flags it as ghost (FAIL+artifact) or mis-counts.
    set cE {[declared_outputs]
rscalc = /out/rscalc/
[step:rscalc]
status = PASS
artifact = /out/rscalc/rscalc.csv|4096|a1b2c3|false
[step:rscalc]
status = FAIL
}
    set dE [$candidate $cE]
    assert {[dget $dE total_steps] == 1} "E total_steps (dedup across blocks)"
    assert {[dget $dE pass_steps] == 0} "E pass_steps (TEETH: last-wins FAIL not PASS)"
    assert {[dget $dE fail_steps] == 1} "E fail_steps"
    assert {[llength [llist $dE missing_artifacts]] == 0} "E no missing (FAIL not PASS)"
    assert {[llength [llist $dE ghost_artifacts]] == 0} "E no ghost (TEETH: first-block artifact discarded by last-wins, NOT merged)"
    assert {[string equal [dget $dE verdict] "clean"]} "E verdict clean (FAIL with zero artifacts is consistent -> clean; only the 5 violation lists gate verdict)"

    # ---- Case F: verdict-clean-requires-ALL-clean ----
    # A manifest with one real violation (a missing_artifact) but everything
    # else clean -> dirty. AND a manifest that is genuinely all-clean -> clean.
    # Naive "verdict = clean if missing_artifacts empty" (ignoring the other
    # four lists) wrongly returns clean when only ghost/zero-byte/etc. present.
    set cF1 {[declared_outputs]
rscalc = /out/rscalc/
[step:rscalc]
status = FAIL
artifact = /out/rscalc/rscalc.csv|4096|a1b2c3|false
}
    set dF1 [$candidate $cF1]
    assert {[llength [llist $dF1 missing_artifacts]] == 0} "F1 no missing (FAIL not PASS)"
    assert {[llist $dF1 ghost_artifacts] eq {/out/rscalc/rscalc.csv}} "F1 ghost present"
    assert {[string equal [dget $dF1 verdict] "dirty"]} "F1 verdict dirty (ghost alone -> dirty, TEETH: not only-missing-gates-verdict)"

    set cF2 {[declared_outputs]
rscalc = /out/rscalc/
[step:rscalc]
status = SKIP
}
    set dF2 [$candidate $cF2]
    assert {[dget $dF2 skip_steps] == 1} "F2 skip_steps"
    assert {[llength [llist $dF2 missing_artifacts]] == 0} "F2 no missing (SKIP not PASS)"
    assert {[llength [llist $dF2 ghost_artifacts]] == 0} "F2 no ghost"
    assert {[string equal [dget $dF2 verdict] "clean"]} "F2 verdict clean (SKIP with no artifacts is clean)"

    # ---- Case G: no declared_outputs section + unknown section ignored ----
    # No [declared_outputs] at all (prefixes empty, fine). An [other] section
    # must be ignored. A PASS step with a signoff artifact bearing a checksum
    # -> clean.
    set cG {[other]
foo = bar
[step:rscalc]
status = PASS
artifact = /out/rscalc/rscalc.csv|4096|a1b2c3|true
}
    set dG [$candidate $cG]
    assert {[dget $dG total_steps] == 1} "G total_steps (unknown section ignored)"
    assert {[dget $dG pass_steps] == 1} "G pass_steps"
    assert {[llength [llist $dG missing_checksum_signoff]] == 0} "G signoff has checksum -> not missing"
    assert {[string equal [dget $dG verdict] "clean"]} "G verdict clean"
}
# Run the checker against the reference implementation bundled below.
check vflow_manifest_audit
puts "RESULT:ALL_ASSERTS_PASS"
