# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc dget {d k} { return [dict get $d $k] }
proc llist {d k} { return [dict get $d $k] }
proc j {d k} { return [join [dict get $d $k] "|"] }

proc check {candidate} {
    # ---- Case A: baseline valid ----
    set cA {.subckt INV a b
.ends
X1 net1 net2 INV
X2 p q INV}
    set dA [$candidate $cA]
    assert {[dget $dA total_subckts_defined] == 1} "A total=1"
    assert {[j $dA subckts_defined] eq "INV"} "A subckts_defined"
    assert {[dget $dA instances_scanned] == 2} "A instances=2"
    assert {[llength [llist $dA arity_matches]] == 2} "A 2 matches"
    assert {[j $dA arity_matches] eq "X1 INV|X2 INV"} "A matches sorted"
    assert {[llength [llist $dA arity_mismatches]] == 0} "A no mismatches"
    assert {[llength [llist $dA unknown_subckt_instances]] == 0} "A no unknown"
    assert {[dget $dA malformed_instances] == 0} "A no malformed"
    assert {[string equal [dget $dA verdict] "pass"]} "A verdict pass"

    # ---- Case B: param-exclusion TEETH ----
    # INV 2 ports; instance has params w=1u l=1u -> pins=2 (a b), match.
    # naive counting all middle tokens -> 4 pins -> false mismatch.
    set cB {.subckt INV a b
.ends
X1 a b INV w=1u l=1u}
    set dB [$candidate $cB]
    assert {[llength [llist $dB arity_matches]] == 1} "B 1 match (params excluded)"
    assert {[j $dB arity_matches] eq "X1 INV"} "B match X1 INV"
    assert {[llength [llist $dB arity_mismatches]] == 0} "B no mismatch (naive counts 4 pins -> wrong)"
    assert {[string equal [dget $dB verdict] "pass"]} "B verdict pass"

    # ---- Case C: LAST-WINS redefinition TEETH ----
    # INV defined twice; second def has 3 ports -> portcount=3.
    # X1 x y INV -> pins=2 vs 3 -> mismatch. naive first-def -> match (wrong).
    set cC {.subckt INV a b
.ends
.subckt INV a b c
.ends
X1 x y INV}
    set dC [$candidate $cC]
    assert {[dget $dC total_subckts_defined] == 1} "C total=1 (unique, redefined)"
    assert {[llength [llist $dC arity_mismatches]] == 1} "C 1 mismatch (last-wins 3 ports)"
    assert {[j $dC arity_mismatches] eq "X1 INV 3 2"} "C mismatch X1 INV 3 2"
    assert {[llength [llist $dC arity_matches]] == 0} "C no match (naive first-def -> match WRONG)"
    assert {[string equal [dget $dC verdict] "fail"]} "C verdict fail"

    # ---- Case D: continuation-line TEETH ----
    # instance split across '+' line -> joined, nodes=[a b c d INV], pins=4.
    # MUX4 has 4 ports -> match. naive per-line -> line1 X1 a b -> unknown b; wrong.
    set cD {.subckt MUX4 a b c d
.ends
X1 a b
+ c d MUX4}
    set dD [$candidate $cD]
    assert {[dget $dD instances_scanned] == 1} "D 1 instance (continuation joined)"
    assert {[llength [llist $dD arity_matches]] == 1} "D 1 match after join"
    assert {[j $dD arity_matches] eq "X1 MUX4"} "D match X1 MUX4"
    assert {[llength [llist $dD unknown_subckt_instances]] == 0} "D no unknown (naive per-line -> unknown b WRONG)"
    assert {[string equal [dget $dD verdict] "pass"]} "D verdict pass"

    # ---- Case E: unknown subckt TEETH ----
    # GHOST never defined -> unknown_subckt_instances, NOT arity_mismatch.
    # naive 'compare with 0 ports' -> mismatch (wrong).
    set cE {.subckt INV a b
.ends
X1 a b GHOST}
    set dE [$candidate $cE]
    assert {[llength [llist $dE unknown_subckt_instances]] == 1} "E 1 unknown"
    assert {[j $dE unknown_subckt_instances] eq "X1 GHOST"} "E unknown X1 GHOST"
    assert {[llength [llist $dE arity_mismatches]] == 0} "E no mismatch (naive 0-port compare -> mismatch WRONG)"
    assert {[string equal [dget $dE verdict] "fail"]} "E verdict fail"

    # ---- Case F: malformed + lexicographic sort TEETH ----
    # X1 w=1u l=1u -> no node token -> malformed (not unknown).
    # multiple matches out of insertion order -> output sorted.
    # naive 'last token = subckt' -> sub=l=1u unknown (wrong); naive unsorted list (wrong).
    set cF {* header comment line skipped
.subckt INV a b
.ends
Xz a b INV
X1 w=1u l=1u
Xa a b INV}
    set dF [$candidate $cF]
    assert {[dget $dF instances_scanned] == 3} "F 3 instances scanned"
    assert {[dget $dF malformed_instances] == 1} "F 1 malformed (all-param instance)"
    assert {[llength [llist $dF arity_matches]] == 2} "F 2 matches"
    assert {[j $dF arity_matches] eq "Xa INV|Xz INV"} "F matches lexicographically sorted (Xa before Xz)"
    assert {[llength [llist $dF unknown_subckt_instances]] == 0} "F no unknown (naive last-token-as-subckt -> unknown l=1u WRONG)"
    assert {[string equal [dget $dF verdict] "fail"]} "F verdict fail (malformed>0)"

    return "ALL_ASSERTS_PASS"
}
