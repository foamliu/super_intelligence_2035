# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc dget {d k} { return [dict get $d $k] }
proc llist {d k} { return [dict get $d $k] }

proc check {candidate} {
    # ---- Case A: baseline valid flow -> verdict valid, clean topo order ----
    set cA {[global]
process = cxmt10G4plus
libName  = austin
cellName = testcell
viewName = layout
[steps]
rscalc pe autovia
[step:rscalc]
cmd = run_rscalc
[step:pe]
cmd = run_pe
depends = rscalc
[step:autovia]
cmd = run_autovia
depends = pe
}
    set dA [$candidate $cA]
    assert {[llength [llist $dA missing_global_keys]] == 0} "A no missing global"
    assert {[llength [llist $dA undeclared_steps]]    == 0} "A no undeclared"
    assert {[llength [llist $dA missing_step_blocks]] == 0} "A no missing blocks"
    assert {[llength [llist $dA steps_no_cmd]]        == 0} "A no no-cmd"
    assert {[llength [llist $dA undefined_deps]]      == 0} "A no undef deps"
    assert {[llength [llist $dA cycle_members]]       == 0} "A no cycle"
    assert {[llist $dA exec_order] eq {rscalc pe autovia}} "A exec_order"
    assert {[string equal [dget $dA verdict] "valid"]} "A verdict valid"

    # ---- Case B: undefined-dep TEETH -> reported, but step still ordered ----
    # autovia depends on `rscalc` (valid) and `ghost` (not in registry). Correct
    # behavior: undefined_deps = {autovia:ghost}; the valid dep rscalc still
    # satisfies, so autovia IS emitted in exec_order after rscalc. Naive
    # "dep not found -> step never ready -> dropped from exec_order" is wrong.
    set cB {[global]
process = p
libName = L
cellName = C
viewName = V
[steps]
rscalc autovia
[step:rscalc]
cmd = run_rscalc
[step:autovia]
cmd = run_autovia
depends = rscalc, ghost
}
    set dB [$candidate $cB]
    assert {[llist $dB undefined_deps] eq {autovia:ghost}} "B undef deps (TEETH)"
    assert {[llength [llist $dB cycle_members]] == 0} "B no cycle"
    assert {[llist $dB exec_order] eq {rscalc autovia}} "B exec_order keeps autovia (TEETH: undef dep does not drop step)"
    assert {[string equal [dget $dB verdict] "invalid"]} "B verdict invalid"

    # ---- Case C: cycle TEETH (alpha<->beta) -> cycle_members, empty order ----
    set cC {[global]
process = p
libName = L
cellName = C
viewName = V
[steps]
alpha beta
[step:alpha]
cmd = run_a
depends = beta
[step:beta]
cmd = run_b
depends = alpha
}
    set dC [$candidate $cC]
    assert {[llist $dC cycle_members] eq {alpha beta}} "C cycle members (TEETH: 2-cycle)"
    assert {[llength [llist $dC exec_order]] == 0} "C exec_order empty (TEETH: cyclic -> no order)"
    assert {[string equal [dget $dC verdict] "invalid"]} "C verdict invalid"

    # ---- Case D: multi-error (missing global + undeclared + missing block + no-cmd) ----
    set cD {[global]
process = p
libName  = L
[steps]
rscalc autovia ghost
[step:rscalc]
cmd = run_rscalc
[step:autovia]
depends = rscalc
[step:decoy]
cmd = run_decoy
}
    set dD [$candidate $cD]
    assert {[llist $dD missing_global_keys] eq {cellName viewName}} "D missing global (TEETH: 2 of 4 absent)"
    assert {[llist $dD undeclared_steps] eq {decoy}} "D undeclared (decoy block, not in registry)"
    assert {[llist $dD missing_step_blocks] eq {ghost}} "D missing block (ghost in registry, no block)"
    assert {[llist $dD steps_no_cmd] eq {autovia}} "D no-cmd (autovia block has no cmd)"
    assert {[llength [llist $dD undefined_deps]] == 0} "D no undef deps"
    assert {[llength [llist $dD cycle_members]] == 0} "D no cycle"
    # exec_order: registry={rscalc,autovia,ghost}; edges autovia->rscalc;
    #   rscalc no deps; ghost no block -> no deps. ready: ghost,rscalc (lex) ->
    #   emit ghost, rscalc, then autovia.
    assert {[llist $dD exec_order] eq {ghost rscalc autovia}} "D exec_order (lex tie-break, blockless step included)"
    assert {[string equal [dget $dD verdict] "invalid"]} "D verdict invalid"

    # ---- Case E: duplicate-block last-wins + self-loop TEETH ----
    # [steps] lists rscalc twice -> registry dedup {rscalc, pe}. TWO [step:rscalc]
    # blocks: first cmd=run_rscalc_v1 (no depends); second cmd=run_rscalc_v2,
    # depends=rscalc (self-loop). last-wins -> cmd=v2, depends=rscalc -> self-
    # loop cycle of 1. Naive "first block wins" keeps v1 / no depends -> no
    # cycle -> wrong; naive "merge blocks" keeps v1 cmd + v2 depends -> wrong cmd.
    set cE {[global]
process = p
libName = L
cellName = C
viewName = V
[steps]
rscalc, pe, rscalc
[step:rscalc]
cmd = run_rscalc_v1
[step:rscalc]
cmd = run_rscalc_v2
depends = rscalc
[step:pe]
cmd = run_pe
depends = rscalc
}
    set dE [$candidate $cE]
    assert {[llength [llist $dE missing_global_keys]] == 0} "E global ok"
    assert {[llength [llist $dE undeclared_steps]]    == 0} "E registry dedup (TEETH: rscalc listed twice)"
    assert {[llength [llist $dE missing_step_blocks]] == 0} "E blocks ok"
    assert {[llength [llist $dE steps_no_cmd]]        == 0} "E has cmd (last-wins v2)"
    assert {[llength [llist $dE undefined_deps]]      == 0} "E rscalc in registry -> self-dep not undefined"
    assert {[llist $dE cycle_members] eq {rscalc}} "E self-loop cycle (TEETH: last-wins block + self-dep)"
    assert {[llength [llist $dE exec_order]] == 0} "E exec_order empty (cyclic)"
    assert {[string equal [dget $dE verdict] "invalid"]} "E verdict invalid"

    # ---- Case F: comprehensive + lex tie-break + unknown-section ignored ----
    set cF {[global]
process = p
libName = L
cellName = C
viewName = V
[steps]
zebra, alpha, mid, omega
[step:zebra]
cmd = run_z
depends = alpha, mid
[step:alpha]
cmd = run_a
[step:mid]
cmd = run_m
depends = alpha
[step:omega]
cmd = run_o
depends = zebra, ghost2
[global_extra]
foo = bar
}
    set dF [$candidate $cF]
    assert {[llength [llist $dF missing_global_keys]] == 0} "F global ok"
    assert {[llength [llist $dF undeclared_steps]]    == 0} "F unknown section [global_extra] ignored (TEETH: not a step block)"
    assert {[llength [llist $dF missing_step_blocks]] == 0} "F blocks ok"
    assert {[llength [llist $dF steps_no_cmd]]        == 0} "F all have cmd"
    assert {[llist $dF undefined_deps] eq {omega:ghost2}} "F undef dep"
    assert {[llength [llist $dF cycle_members]] == 0} "F acyclic"
    # topo: alpha(0 deps) -> mid(needs alpha) -> zebra(needs alpha,mid) ->
    #   omega(needs zebra; ghost2 ignored for ordering)
    assert {[llist $dF exec_order] eq {alpha mid zebra omega}} "F exec_order lex tie-break"
    assert {[string equal [dget $dF verdict] "invalid"]} "F verdict invalid (undef dep)"

    return "CHECK_PASS"
}
