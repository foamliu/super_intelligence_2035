# Checker for layout_routing_audit
# Builds fixtures inline and asserts on the returned dict.
proc _chk {name cond} {
    global _chk_pass _chk_fail _chk_first
    if {![uplevel 1 [list expr $cond]]} {
        set _chk_pass 0
        if {$_chk_fail == 0} { set _chk_first $name }
        incr _chk_fail
        puts "ASSERT FAIL: $name"
    } else {
        incr _chk_pass
    }
}
proc _chk_done {} {
    global _chk_pass _chk_fail
    if {$_chk_fail == 0} { puts "ALL_ASSERTS_PASS" } else { puts "ASSERTS_FAILED" }
}
proc check {fn} {
    global _chk_pass _chk_fail _chk_first
    set _chk_pass 1; set _chk_fail 0; set _chk_first ""

    # ---- Case A: baseline (mixed routed/partial/unrouted + vias + layers) ----
    set a "# Routing report
NET clk segments=4 vias=3 layers=M1,M2,M3 status=routed
NET data segments=2 vias=1 layers=M1,M2 status=routed
NET rst segments=1 vias=0 layers=M1 status=partial
NET vss segments=0 vias=0 layers= status=unrouted
SUMMARY nets_checked=4 routed=2 unrouted=1 missing_vias=0 max_segments=4 max_segment_net=clk"
    set rA [$fn $a]
    _chk A_total {[dict get $rA total_nets] == 4}
    _chk A_routed {[dict get $rA routed_count] == 2}
    _chk A_partial {[dict get $rA partial_count] == 1}
    _chk A_unrouted {[dict get $rA unrouted_count] == 1}
    _chk A_skipped {[dict get $rA skipped_count] == 0}
    _chk A_single {[llength [dict get $rA single_segment_nets]] == 1}
    _chk A_single_rst {[lindex [dict get $rA single_segment_nets] 0] eq "rst"}
    _chk A_missing_empty {[llength [dict get $rA missing_via_nets]] == 0}
    _chk A_max {[dict get $rA max_segments] == 4}
    _chk A_maxnet {[dict get $rA max_segment_net] eq "clk"}
    _chk A_layers {[llength [dict get $rA layers_used]] == 3}
    _chk A_mismatch_empty {[llength [dict get $rA mismatched_summary]] == 0}
    _chk A_verdict {[dict get $rA verdict] eq "FAIL"}

    # ---- Case B: status CASE-INSENSITIVE teeth ----
    set b "# lowercase + mixed-case status
NET a segments=3 vias=2 layers=M1,M2 status=routed
NET b segments=2 vias=1 layers=M1,M2 status=RoUtEd
NET c segments=0 vias=0 layers= status=UNROUTED
SUMMARY nets_checked=3 routed=2 unrouted=1 missing_vias=0 max_segments=3 max_segment_net=a"
    set rB [$fn $b]
    _chk B_routed {[dict get $rB routed_count] == 2}
    _chk B_unrouted {[dict get $rB unrouted_count] == 1}
    _chk B_maxnet {[dict get $rB max_segment_net] eq "a"}
    _chk B_verdict {[dict get $rB verdict] eq "FAIL"}

    # ---- Case C: dup net LAST-WINS teeth ----
    set c "# net 'n1' appears twice; second wins (segments=2 routed), not summed/first-wins
NET n1 segments=5 vias=2 layers=M1,M2 status=routed
NET n1 segments=2 vias=1 layers=M1 status=routed
NET n2 segments=3 vias=1 layers=M1,M2 status=routed
SUMMARY nets_checked=2 routed=2 unrouted=0 missing_vias=0 max_segments=3 max_segment_net=n2"
    set rC [$fn $c]
    _chk C_total {[dict get $rC total_nets] == 2}
    _chk C_routed {[dict get $rC routed_count] == 2}
    _chk C_max {[dict get $rC max_segments] == 3}
    _chk C_maxnet {[dict get $rC max_segment_net] eq "n2"}
    _chk C_mismatch_empty {[llength [dict get $rC mismatched_summary]] == 0}
    _chk C_verdict {[dict get $rC verdict] eq "PASS"}

    # ---- Case D: status ABSENT -> infer from segments teeth ----
    set d "# no status field; infer: 0->UNROUTED, 1->PARTIAL, >=2->ROUTED
NET p segments=2 vias=1 layers=M1,M2
NET q segments=1 vias=0 layers=M1
NET r segments=0 vias=0 layers=
SUMMARY nets_checked=3 routed=1 unrouted=1 missing_vias=0 max_segments=2 max_segment_net=p"
    set rD [$fn $d]
    _chk D_routed {[dict get $rD routed_count] == 1}
    _chk D_partial {[dict get $rD partial_count] == 1}
    _chk D_unrouted {[dict get $rD unrouted_count] == 1}
    _chk D_single_q {[lindex [dict get $rD single_segment_nets] 0] eq "q"}
    _chk D_maxnet {[dict get $rD max_segment_net] eq "p"}
    _chk D_verdict {[dict get $rD verdict] eq "FAIL"}

    # ---- Case E: missing_via = layers>=2 AND vias==0 teeth ----
    set e "# m1: multi-layer 0-via -> MISSING via ; m2: single-layer 0-via -> FINE
NET m1 segments=2 vias=0 layers=M1,M2 status=routed
NET m2 segments=2 vias=0 layers=M1 status=routed
NET m3 segments=2 vias=1 layers=M1,M2 status=routed
SUMMARY nets_checked=3 routed=3 unrouted=0 missing_vias=1 max_segments=2 max_segment_net=m1"
    set rE [$fn $e]
    _chk E_missing_one {[llength [dict get $rE missing_via_nets]] == 1}
    _chk E_missing_m1 {[lindex [dict get $rE missing_via_nets] 0] eq "m1"}
    _chk E_routed {[dict get $rE routed_count] == 3}
    _chk E_verdict {[dict get $rE verdict] eq "FAIL"}

    # ---- Case F: layers dedup + empty teeth ----
    set f "# layers=M1,M2,M1 -> 2 distinct ; layers= empty -> 0 layers (no missing_via)
NET f1 segments=2 vias=0 layers=M1,M2,M1 status=routed
NET f2 segments=2 vias=0 layers= status=routed
SUMMARY nets_checked=2 routed=2 unrouted=0 missing_vias=1 max_segments=2 max_segment_net=f1"
    set rF [$fn $f]
    _chk F_missing_one {[llength [dict get $rF missing_via_nets]] == 1}
    _chk F_missing_f1 {[lindex [dict get $rF missing_via_nets] 0] eq "f1"}
    _chk F_layers {[llength [dict get $rF layers_used]] == 2}
    _chk F_layers_m1 {[lindex [dict get $rF layers_used] 0] eq "M1"}
    _chk F_verdict {[dict get $rF verdict] eq "FAIL"}

    # ---- Case G: single_segment watchlist regardless of status teeth ----
    set g "# g1 status=routed but segments==1 -> still in single_segment; counts as routed (explicit wins)
NET g1 segments=1 vias=0 layers=M1 status=routed
NET g2 segments=3 vias=1 layers=M1,M2 status=routed
SUMMARY nets_checked=2 routed=2 unrouted=0 missing_vias=0 max_segments=3 max_segment_net=g2"
    set rG [$fn $g]
    _chk G_routed {[dict get $rG routed_count] == 2}
    _chk G_single_g1 {[llength [dict get $rG single_segment_nets]] == 1}
    _chk G_single_g1_name {[lindex [dict get $rG single_segment_nets] 0] eq "g1"}
    _chk G_missing_empty {[llength [dict get $rG missing_via_nets]] == 0}
    _chk G_verdict {[dict get $rG verdict] eq "PASS"}

    # ---- Case H: max_segments over NON-SKIP only teeth ----
    set h "# sk1 SKIPPED with segments=99 (highest) -> excluded from max; h1 segments=5 wins
NET sk1 segments=99 vias=0 layers=M1 status=skipped
NET h1 segments=5 vias=2 layers=M1,M2 status=routed
NET h2 segments=3 vias=1 layers=M1 status=routed
SUMMARY nets_checked=3 routed=2 unrouted=0 missing_vias=0 max_segments=5 max_segment_net=h1"
    set rH [$fn $h]
    _chk H_skipped {[dict get $rH skipped_count] == 1}
    _chk H_max {[dict get $rH max_segments] == 5}
    _chk H_maxnet {[dict get $rH max_segment_net] eq "h1"}
    _chk H_verdict {[dict get $rH verdict] eq "PASS"}

    # ---- Case I: max_segment_net lex tie-break (dictionary numeric-aware) teeth ----
    set i "# via2 and via10 both segments=7 -> dictionary sort: 'via2' < 'via10'
NET via10 segments=7 vias=1 layers=M1,M2 status=routed
NET via2 segments=7 vias=1 layers=M1,M2 status=routed
SUMMARY nets_checked=2 routed=2 unrouted=0 missing_vias=0 max_segments=7 max_segment_net=via2"
    set rI [$fn $i]
    _chk I_max {[dict get $rI max_segments] == 7}
    _chk I_maxnet {[dict get $rI max_segment_net] eq "via2"}
    _chk I_verdict {[dict get $rI verdict] eq "PASS"}

    # ---- Case J: mismatched_summary teeth (SUMMARY wrong values) ----
    set j "# SUMMARY claims routed=2 but actual routed=1; max_segment_net wrong
NET j1 segments=3 vias=1 layers=M1,M2 status=routed
NET j2 segments=0 vias=0 layers= status=unrouted
SUMMARY nets_checked=2 routed=2 unrouted=1 missing_vias=0 max_segments=3 max_segment_net=j2"
    set rJ [$fn $j]
    _chk J_routed {[dict get $rJ routed_count] == 1}
    _chk J_mismatch_routed {[lsearch [dict get $rJ mismatched_summary] "routed"] >= 0}
    _chk J_mismatch_maxnet {[lsearch [dict get $rJ mismatched_summary] "max_segment_net"] >= 0}
    _chk J_mismatch_count {[llength [dict get $rJ mismatched_summary]] == 2}
    _chk J_verdict {[dict get $rJ verdict] eq "FAIL"}

    # ---- Case K: verdict priority FAIL > INCOMPLETE > PASS teeth ----
    set k "# unrouted present AND summary mismatched -> FAIL wins over INCOMPLETE
NET k1 segments=2 vias=1 layers=M1,M2 status=routed
NET k2 segments=0 vias=0 layers= status=unrouted
SUMMARY nets_checked=9 routed=1 unrouted=1 missing_vias=0 max_segments=2 max_segment_net=k1"
    set rK [$fn $k]
    _chk K_mismatch_nets {[lsearch [dict get $rK mismatched_summary] "nets_checked"] >= 0}
    _chk K_verdict {[dict get $rK verdict] eq "FAIL"}
    # sub-case: no unrouted/missing_via but mismatched -> INCOMPLETE
    set k2 "NET k1 segments=2 vias=1 layers=M1,M2 status=routed
SUMMARY nets_checked=9 routed=1 unrouted=0 missing_vias=0 max_segments=2 max_segment_net=k1"
    set rK2 [$fn $k2]
    _chk K2_mismatch {[llength [dict get $rK2 mismatched_summary]] == 1}
    _chk K2_verdict {[dict get $rK2 verdict] eq "INCOMPLETE"}

    # ---- Case L: empty report, no SUMMARY -> all zero/empty, max_segments=-1, INCOMPLETE ----
    set l "# header only "
    set rL [$fn $l]
    _chk L_total {[dict get $rL total_nets] == 0}
    _chk L_routed {[dict get $rL routed_count] == 0}
    _chk L_unrouted {[dict get $rL unrouted_count] == 0}
    _chk L_single_empty {[llength [dict get $rL single_segment_nets]] == 0}
    _chk L_missing_empty {[llength [dict get $rL missing_via_nets]] == 0}
    _chk L_max_neg {[dict get $rL max_segments] == -1}
    _chk L_maxnet_empty {[dict get $rL max_segment_net] eq ""}
    _chk L_layers_empty {[llength [dict get $rL layers_used]] == 0}
    _chk L_mismatch_empty {[llength [dict get $rL mismatched_summary]] == 0}
    _chk L_verdict {[dict get $rL verdict] eq "INCOMPLETE"}

    # ---- Case M: comprehensive + invariant ----
    set m "# all features
NET netA segments=6 vias=2 layers=M2,M3 status=routed
NET netB segments=1 vias=0 layers=M2 status=routed
NET netC segments=0 vias=0 layers= status=unrouted
NET netD segments=4 vias=0 layers=M1,M3 status=routed
NET netE segments=3 vias=1 layers=M1,M2,M3 status=skipped
NET netD segments=2 vias=1 layers=M1 status=routed
SUMMARY nets_checked=5 routed=3 unrouted=1 missing_vias=1 max_segments=6 max_segment_net=netA"
    set rM [$fn $m]
    # netD last-wins: segments=2, layers=M1 (1 layer), vias=1, routed
    _chk M_total {[dict get $rM total_nets] == 5}
    _chk M_routed {[dict get $rM routed_count] == 3}
    _chk M_unrouted {[dict get $rM unrouted_count] == 1}
    _chk M_skipped {[dict get $rM skipped_count] == 1}
    _chk M_single {[llength [dict get $rM single_segment_nets]] == 1}
    _chk M_single_netB {[lindex [dict get $rM single_segment_nets] 0] eq "netB"}
    # missing_via: netD last-wins layers=M1 (1 layer, no missing); netC 0 layers; netA M2,M3 vias=2 ok; netE skipped M1,M2,M3 vias=1 ok -> only net? none missing after netD update
    _chk M_missing_zero {[llength [dict get $rM missing_via_nets]] == 0}
    _chk M_max {[dict get $rM max_segments] == 6}
    _chk M_maxnet {[dict get $rM max_segment_net] eq "netA"}
    _chk M_layers {[llength [dict get $rM layers_used]] == 3}
    _chk M_mismatch_missing_vias {[lsearch [dict get $rM mismatched_summary] "missing_vias"] >= 0}
    _chk M_verdict {[dict get $rM verdict] eq "FAIL"}

    _chk_done
    if {$_chk_fail == 0} { return "ALL_ASSERTS_PASS" } else { return "ASSERTS_FAILED:$_chk_first" }
}
