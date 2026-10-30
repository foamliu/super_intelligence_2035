# Reference implementation: layout_pgshort_audit
# Audits a pyAether-emitted PG (power/ground) short report.
proc layout_pgshort_audit {report_text} {
    set short_count 0
    set leak_count 0
    set clean_count 0
    set power_count 0
    set ground_count 0
    set mixed_pairs {}
    set max_resistance -1.0
    set worst_pair ""
    set layers_affected {}
    array set pair_data {}
    set has_summary 0
    set sum_shorts_checked ""
    set sum_shorts ""
    set sum_leaks ""
    set sum_clean ""
    set sum_max_resistance ""
    set sum_worst_pair ""

    foreach line [split $report_text "\n"] {
        set line [string trim $line]
        if {$line eq ""} continue
        if {[string index $line 0] eq "#"} continue
        if {[string match "SHORT *" $line]} {
            set rest [string range $line 6 end]
            set toks {}
            foreach t [split $rest " "] { if {$t ne ""} { lappend toks $t } }
            set net_a [lindex $toks 0]
            set net_b [lindex $toks 1]
            set key "$net_a $net_b"
            set type ""
            set resistance 0.0
            set layer ""
            set status ""
            foreach tok [lrange $toks 2 end] {
                if {[string match "type=*" $tok]} {
                    set type [string range $tok 5 end]
                } elseif {[string match "resistance=*" $tok]} {
                    set resistance [string range $tok 11 end]
                } elseif {[string match "layer=*" $tok]} {
                    set layer [string range $tok 6 end]
                } elseif {[string match "status=*" $tok]} {
                    set status [string range $tok 7 end]
                }
            }
            if {$resistance eq ""} { set resistance 0.0 }
            # LAST-WINS: overwrite (replace, not sum, not first-wins)
            set pair_data($key) [list $type $resistance $layer $status]
        } elseif {[string match "SUMMARY *" $line]} {
            set has_summary 1
            set rest [string range $line 7 end]
            set toks {}
            foreach t [split $rest " "] { if {$t ne ""} { lappend toks $t } }
            foreach tok $toks {
                if {[string match "shorts_checked=*" $tok]} {
                    set sum_shorts_checked [string range $tok 15 end]
                } elseif {[string match "shorts=*" $tok]} {
                    set sum_shorts [string range $tok 7 end]
                } elseif {[string match "leaks=*" $tok]} {
                    set sum_leaks [string range $tok 6 end]
                } elseif {[string match "clean=*" $tok]} {
                    set sum_clean [string range $tok 6 end]
                } elseif {[string match "max_resistance=*" $tok]} {
                    set sum_max_resistance [string range $tok 15 end]
                } elseif {[string match "worst_pair=*" $tok]} {
                    set sum_worst_pair [string range $tok 11 end]
                }
            }
        }
    }

    set total_shorts [llength [array names pair_data]]

    foreach key [array names pair_data] {
        lassign $pair_data($key) type resistance layer status
        set st [string tolower [string trim $status]]
        if {$st eq ""} {
            set r [expr {double($resistance)}]
            if {$r < 1.0} { set st "short"
            } elseif {$r < 100.0} { set st "leak"
            } else { set st "clean" }
        }
        if {$st eq "short"} { incr short_count
        } elseif {$st eq "leak"} { incr leak_count
        } elseif {$st eq "clean"} { incr clean_count }

        set ty [string tolower [string trim $type]]
        if {$ty eq "mixed"} {
            incr power_count
            incr ground_count
            lappend mixed_pairs [join [split $key " "] "-"]
        } else {
            if {[string match "*power*" $ty]} { incr power_count }
            if {[string match "*ground*" $ty]} { incr ground_count }
        }

        if {$st ne "clean"} {
            set r [expr {double($resistance)}]
            if {$r > $max_resistance} {
                set max_resistance $r
                set worst_pair [join [split $key " "] "-"]
            } elseif {$r == $max_resistance} {
                set cand [join [split $key " "] "-"]
                set sorted [lsort -dictionary [list $worst_pair $cand]]
                set worst_pair [lindex $sorted 0]
            }
            if {$layer ne ""} {
                if {$layer ni $layers_affected} { lappend layers_affected $layer }
            }
        }
    }

    set layers_affected [lsort -dictionary $layers_affected]
    set mixed_pairs [lsort -dictionary $mixed_pairs]

    set mismatched {}
    if {$has_summary} {
        if {$sum_shorts_checked ne "" && $sum_shorts_checked != $total_shorts} {
            lappend mismatched "shorts_checked=$sum_shorts_checked vs $total_shorts"
        }
        if {$sum_shorts ne "" && $sum_shorts != $short_count} {
            lappend mismatched "shorts=$sum_shorts vs $short_count"
        }
        if {$sum_leaks ne "" && $sum_leaks != $leak_count} {
            lappend mismatched "leaks=$sum_leaks vs $leak_count"
        }
        if {$sum_clean ne "" && $sum_clean != $clean_count} {
            lappend mismatched "clean=$sum_clean vs $clean_count"
        }
        if {$sum_max_resistance ne "" && [expr {double($sum_max_resistance)}] != $max_resistance} {
            lappend mismatched "max_resistance=$sum_max_resistance vs $max_resistance"
        }
        if {$sum_worst_pair ne "" && $sum_worst_pair ne $worst_pair} {
            lappend mismatched "worst_pair=$sum_worst_pair vs $worst_pair"
        }
    }

    if {$short_count > 0} {
        set verdict "FAIL"
    } elseif {$leak_count > 0} {
        set verdict "REVIEW"
    } elseif {!$has_summary || [llength $mismatched] > 0} {
        set verdict "INCOMPLETE"
    } else {
        set verdict "PASS"
    }

    return [dict create \
        total_shorts $total_shorts \
        short_count $short_count \
        leak_count $leak_count \
        clean_count $clean_count \
        power_count $power_count \
        ground_count $ground_count \
        mixed_pairs $mixed_pairs \
        max_resistance $max_resistance \
        worst_pair $worst_pair \
        layers_affected $layers_affected \
        mismatched_summary $mismatched \
        verdict $verdict]
}
# Checker for layout_pgshort_audit
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

    # ---- Case A: baseline (mixed short/leak/clean + power/ground/mixed + layers + summary match) ----
    set a "# PG short report
SHORT vdd vss type=power resistance=0.2 layer=M1 status=short
SHORT vdd gnd type=power resistance=5.0 layer=M2 status=leak
SHORT clk gnd type=ground resistance=200.0 layer=M3 status=clean
SHORT vss gnd type=mixed resistance=0.8 layer=M1 status=short
SUMMARY shorts_checked=4 shorts=2 leaks=1 clean=1 max_resistance=5.0 worst_pair=vdd-gnd"
    set rA [$fn $a]
    _chk A_total {[dict get $rA total_shorts] == 4}
    _chk A_short {[dict get $rA short_count] == 2}
    _chk A_leak {[dict get $rA leak_count] == 1}
    _chk A_clean {[dict get $rA clean_count] == 1}
    _chk A_power {[dict get $rA power_count] == 3}
    _chk A_ground {[dict get $rA ground_count] == 2}
    _chk A_mixed {[llength [dict get $rA mixed_pairs]] == 1}
    _chk A_mixed_val {[lindex [dict get $rA mixed_pairs] 0] eq "vss-gnd"}
    _chk A_max {[dict get $rA max_resistance] == 5.0}
    _chk A_worst {[dict get $rA worst_pair] eq "vdd-gnd"}
    _chk A_layers {[llength [dict get $rA layers_affected]] == 2}
    _chk A_layers_m1 {[lsearch [dict get $rA layers_affected] M1] >= 0}
    _chk A_layers_m2 {[lsearch [dict get $rA layers_affected] M2] >= 0}
    _chk A_mismatch_empty {[llength [dict get $rA mismatched_summary]] == 0}
    _chk A_verdict {[dict get $rA verdict] eq "FAIL"}

    # ---- Case B: status CASE-INSENSITIVE teeth ----
    set b "# mixed case status
SHORT n1 n2 type=power resistance=0.1 layer=M1 status=SHORT
SHORT n3 n4 type=ground resistance=50.0 layer=M2 status=Leak
SHORT n5 n6 type=signal resistance=150.0 layer=M3 status=CLEAN
SUMMARY shorts_checked=3 shorts=1 leaks=1 clean=1 max_resistance=50.0 worst_pair=n3-n4"
    set rB [$fn $b]
    _chk B_total {[dict get $rB total_shorts] == 3}
    _chk B_short {[dict get $rB short_count] == 1}
    _chk B_leak {[dict get $rB leak_count] == 1}
    _chk B_clean {[dict get $rB clean_count] == 1}
    _chk B_max {[dict get $rB max_resistance] == 50.0}
    _chk B_worst {[dict get $rB worst_pair] eq "n3-n4"}
    _chk B_mismatch_empty {[llength [dict get $rB mismatched_summary]] == 0}
    _chk B_verdict {[dict get $rB verdict] eq "FAIL"}

    # ---- Case C: dup (net_a, net_b) pair LAST-WINS (replace, not sum, not first-wins) ----
    set c "# dup pair: vdd-vss appears twice; last wins (leak, not short)
SHORT vdd vss type=power resistance=0.3 layer=M1 status=short
SHORT vdd vss type=power resistance=50.0 layer=M2 status=leak
SHORT clk rst type=signal resistance=0.4 layer=M1 status=short
SUMMARY shorts_checked=2 shorts=1 leaks=1 clean=0 max_resistance=50.0 worst_pair=vdd-vss"
    set rC [$fn $c]
    _chk C_total {[dict get $rC total_shorts] == 2}
    _chk C_short {[dict get $rC short_count] == 1}
    _chk C_leak {[dict get $rC leak_count] == 1}
    _chk C_clean {[dict get $rC clean_count] == 0}
    _chk C_max {[dict get $rC max_resistance] == 50.0}
    _chk C_worst {[dict get $rC worst_pair] eq "vdd-vss"}
    _chk C_mismatch_empty {[llength [dict get $rC mismatched_summary]] == 0}
    _chk C_verdict {[dict get $rC verdict] eq "FAIL"}

    # ---- Case D: status absent -> infer from resistance thresholds ----
    set d "# no status field; infer from resistance
SHORT a b type=power resistance=0.5 layer=M1
SHORT c d type=ground resistance=50.0 layer=M2
SHORT e f type=signal resistance=200.0 layer=M3
SUMMARY shorts_checked=3 shorts=1 leaks=1 clean=1 max_resistance=50.0 worst_pair=c-d"
    set rD [$fn $d]
    _chk D_total {[dict get $rD total_shorts] == 3}
    _chk D_short {[dict get $rD short_count] == 1}
    _chk D_leak {[dict get $rD leak_count] == 1}
    _chk D_clean {[dict get $rD clean_count] == 1}
    _chk D_max {[dict get $rD max_resistance] == 50.0}
    _chk D_worst {[dict get $rD worst_pair] eq "c-d"}
    _chk D_mismatch_empty {[llength [dict get $rD mismatched_summary]] == 0}
    _chk D_verdict {[dict get $rD verdict] eq "FAIL"}

    # ---- Case E: resistance boundary (R==1.0 -> leak inclusive, R==100.0 -> clean inclusive) ----
    set e "# boundary: 1.0=leak, 100.0=clean, 0.999=short, 99.999=leak, 100.001=clean
SHORT p1 p2 type=power resistance=1.0 layer=M1 status=
SHORT p3 p4 type=power resistance=100.0 layer=M2 status=
SHORT p5 p6 type=power resistance=0.999 layer=M1
SHORT p7 p8 type=power resistance=99.999 layer=M2
SHORT p9 p10 type=power resistance=100.001 layer=M3
SUMMARY shorts_checked=5 shorts=1 leaks=2 clean=2 max_resistance=99.999 worst_pair=p7-p8"
    set rE [$fn $e]
    _chk E_total {[dict get $rE total_shorts] == 5}
    _chk E_short {[dict get $rE short_count] == 1}
    _chk E_leak {[dict get $rE leak_count] == 2}
    _chk E_clean {[dict get $rE clean_count] == 2}
    _chk E_max {[dict get $rE max_resistance] == 99.999}
    _chk E_worst {[dict get $rE worst_pair] eq "p7-p8"}
    _chk E_mismatch_empty {[llength [dict get $rE mismatched_summary]] == 0}
    _chk E_verdict {[dict get $rE verdict] eq "FAIL"}

    # ---- Case F: missing resistance -> default 0.0 -> short ----
    set f "# resistance absent -> 0.0 -> short (0.0 < 1.0)
SHORT x y type=power layer=M1 status=
SHORT z w type=ground resistance=50.0 layer=M2 status=leak
SUMMARY shorts_checked=2 shorts=1 leaks=1 clean=0 max_resistance=50.0 worst_pair=z-w"
    set rF [$fn $f]
    _chk F_total {[dict get $rF total_shorts] == 2}
    _chk F_short {[dict get $rF short_count] == 1}
    _chk F_leak {[dict get $rF leak_count] == 1}
    _chk F_clean {[dict get $rF clean_count] == 0}
    _chk F_max {[dict get $rF max_resistance] == 50.0}
    _chk F_worst {[dict get $rF worst_pair] eq "z-w"}
    _chk F_mismatch_empty {[llength [dict get $rF mismatched_summary]] == 0}
    _chk F_verdict {[dict get $rF verdict] eq "FAIL"}

    # ---- Case G: max_resistance over NON-CLEAN only (clean excluded even if higher R); all-clean -> -1.0 ----
    set g "# clean has highest R (300) but excluded; non-clean max is 50
SHORT a b type=power resistance=0.5 layer=M1 status=short
SHORT c d type=ground resistance=50.0 layer=M2 status=leak
SHORT e f type=signal resistance=300.0 layer=M3 status=clean
SUMMARY shorts_checked=3 shorts=1 leaks=1 clean=1 max_resistance=50.0 worst_pair=c-d"
    set rG [$fn $g]
    _chk G_max {[dict get $rG max_resistance] == 50.0}
    _chk G_worst {[dict get $rG worst_pair] eq "c-d"}
    _chk G_layers {[llength [dict get $rG layers_affected]] == 2}
    _chk G_layers_no_m3 {[lsearch [dict get $rG layers_affected] M3] < 0}
    _chk G_verdict {[dict get $rG verdict] eq "FAIL"}

    # ---- Case G2: ALL clean -> max_resistance=-1.0, worst_pair="", layers empty, verdict PASS ----
    set g2 "# all clean
SHORT a b type=power resistance=200.0 layer=M1 status=clean
SHORT c d type=ground resistance=300.0 layer=M2 status=clean
SUMMARY shorts_checked=2 shorts=0 leaks=0 clean=2 max_resistance=-1.0 worst_pair="
    set rG2 [$fn $g2]
    _chk G2_max {[dict get $rG2 max_resistance] == -1.0}
    _chk G2_worst {[dict get $rG2 worst_pair] eq ""}
    _chk G2_layers {[llength [dict get $rG2 layers_affected]] == 0}
    _chk G2_mismatch_empty {[llength [dict get $rG2 mismatched_summary]] == 0}
    _chk G2_verdict {[dict get $rG2 verdict] eq "PASS"}

    # ---- Case H: worst_pair tie-break lex smallest (dict-numeric-aware: via2-vss < via10-vss) ----
    set h "# tie at max_resistance=50.0: via10-vss, via2-vss, aaa-vss -> lex smallest = aaa-vss
SHORT via10 vss type=power resistance=50.0 layer=M1 status=leak
SHORT via2 vss type=power resistance=50.0 layer=M2 status=leak
SHORT aaa vss type=power resistance=50.0 layer=M3 status=leak
SUMMARY shorts_checked=3 shorts=0 leaks=3 clean=0 max_resistance=50.0 worst_pair=aaa-vss"
    set rH [$fn $h]
    _chk H_max {[dict get $rH max_resistance] == 50.0}
    _chk H_worst {[dict get $rH worst_pair] eq "aaa-vss"}
    _chk H_mismatch_empty {[llength [dict get $rH mismatched_summary]] == 0}
    _chk H_verdict {[dict get $rH verdict] eq "REVIEW"}

    # ---- Case H2: dict-numeric tie-break: via2-vss < via10-vss (no aaa) ----
    set h2 "# tie: via10-vss vs via2-vss -> via2 < via10 (numeric-aware dict sort)
SHORT via10 vss type=power resistance=50.0 layer=M1 status=leak
SHORT via2 vss type=power resistance=50.0 layer=M2 status=leak
SUMMARY shorts_checked=2 shorts=0 leaks=2 clean=0 max_resistance=50.0 worst_pair=via2-vss"
    set rH2 [$fn $h2]
    _chk H2_worst {[dict get $rH2 worst_pair] eq "via2-vss"}
    _chk H2_mismatch_empty {[llength [dict get $rH2 mismatched_summary]] == 0}

    # ---- Case I: type "mixed" counts in BOTH power_count AND ground_count ----
    set i "# mixed counts in both power and ground
SHORT a b type=mixed resistance=0.3 layer=M1 status=short
SHORT c d type=power resistance=50.0 layer=M2 status=leak
SHORT e f type=ground resistance=200.0 layer=M3 status=clean
SUMMARY shorts_checked=3 shorts=1 leaks=1 clean=1 max_resistance=50.0 worst_pair=c-d"
    set rI [$fn $i]
    _chk I_power {[dict get $rI power_count] == 2}
    _chk I_ground {[dict get $rI ground_count] == 2}
    _chk I_mixed {[llength [dict get $rI mixed_pairs]] == 1}
    _chk I_mixed_val {[lindex [dict get $rI mixed_pairs] 0] eq "a-b"}
    _chk I_mismatch_empty {[llength [dict get $rI mismatched_summary]] == 0}

    # ---- Case J: ordered pairs (a,b) != (b,a) -- different keys, both counted ----
    set j "# (vdd,vss) and (vss,vdd) are DIFFERENT pairs (not normalized)
SHORT vdd vss type=power resistance=0.3 layer=M1 status=short
SHORT vss vdd type=power resistance=50.0 layer=M2 status=leak
SUMMARY shorts_checked=2 shorts=1 leaks=1 clean=0 max_resistance=50.0 worst_pair=vss-vdd"
    set rJ [$fn $j]
    _chk J_total {[dict get $rJ total_shorts] == 2}
    _chk J_short {[dict get $rJ short_count] == 1}
    _chk J_leak {[dict get $rJ leak_count] == 1}
    _chk J_max {[dict get $rJ max_resistance] == 50.0}
    _chk J_worst {[dict get $rJ worst_pair] eq "vss-vdd"}
    _chk J_mismatch_empty {[llength [dict get $rJ mismatched_summary]] == 0}
    _chk J_verdict {[dict get $rJ verdict] eq "FAIL"}

    # ---- Case K: mismatched_summary numeric equality (max_resistance 5.0==5) + absent fields not reported ----
    set k "# summary says max_resistance=5 (int) but computed 5.0 -> NUMERIC equal, NOT mismatched
# summary omits worst_pair (absent -> not reported); shorts wrong -> mismatched
SHORT a b type=power resistance=0.3 layer=M1 status=short
SHORT c d type=ground resistance=5.0 layer=M2 status=leak
SUMMARY shorts_checked=2 shorts=0 leaks=1 clean=0 max_resistance=5"
    set rK [$fn $k]
    _chk K_mismatch_len {[llength [dict get $rK mismatched_summary]] == 1}
    _chk K_mismatch_shorts {[lindex [dict get $rK mismatched_summary] 0] eq "shorts=0 vs 1"}
    _chk K_verdict {[dict get $rK verdict] eq "FAIL"}

    # ---- Case L: no SUMMARY -> verdict INCOMPLETE (0 short, 0 leak); mismatched empty ----
    set l "# no summary line; all clean
SHORT a b type=power resistance=200.0 layer=M1 status=clean
SHORT c d type=ground resistance=300.0 layer=M2 status=clean"
    set rL [$fn $l]
    _chk L_total {[dict get $rL total_shorts] == 2}
    _chk L_short {[dict get $rL short_count] == 0}
    _chk L_leak {[dict get $rL leak_count] == 0}
    _chk L_clean {[dict get $rL clean_count] == 2}
    _chk L_mismatch_empty {[llength [dict get $rL mismatched_summary]] == 0}
    _chk L_verdict {[dict get $rL verdict] eq "INCOMPLETE"}

    # ---- Case M: verdict priority (REVIEW when leak>0 and short=0, even with mismatched) ----
    set m "# short=0, leak=1 (REVIEW beats INCOMPLETE from mismatched)
SHORT a b type=power resistance=50.0 layer=M1 status=leak
SUMMARY shorts_checked=1 shorts=99 leaks=1 clean=0 max_resistance=50.0 worst_pair=a-b"
    set rM [$fn $m]
    _chk M_leak {[dict get $rM leak_count] == 1}
    _chk M_short {[dict get $rM short_count] == 0}
    _chk M_mismatch_len {[llength [dict get $rM mismatched_summary]] == 1}
    _chk M_verdict {[dict get $rM verdict] eq "REVIEW"}

    _chk_done
    if {$_chk_fail == 0} { return "ALL_ASSERTS_PASS" } else { return "ASSERTS_FAILED:$_chk_first" }
}
set r [check layout_pgshort_audit]; puts "RESULT:$r"; if {$r eq "ALL_ASSERTS_PASS"} { puts "DESIGN_FLOW_VERDICT=PASS" } else { puts "DESIGN_FLOW_VERDICT=FAIL" }
