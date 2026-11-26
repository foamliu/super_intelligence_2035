# Test harness for EDA-Eval-DesignFlow-PV-005
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc check {candidate} {
    # ---- Case A: baseline -- single block, all match, 1 warning, 0 errors -> CLEAN ----
    set A "LAYOUT CELL NAME = TOP
SOURCE CELL NAME = TOP
# of NETS in layout = 100
# of NETS in source = 100
# of DEVICES in layout = 500
# of DEVICES in source = 500
# of PORTS in layout = 32
# of PORTS in source = 32
WARNING: device M1 has different size (benign)"
    set d [$candidate $A]
    assert {[dict get $d layout_cell] eq "TOP"} "A layout_cell=TOP"
    assert {[dict get $d source_cell] eq "TOP"} "A source_cell=TOP"
    assert {[dict get $d cell_name_match] eq "1"} "A cell_name_match=1"
    assert {[dict get $d nets_delta] eq "0"} "A nets_delta=0"
    assert {[dict get $d devices_delta] eq "0"} "A devices_delta=0"
    assert {[dict get $d ports_delta] eq "0"} "A ports_delta=0"
    assert {[dict get $d nets_match] eq "1"} "A nets_match=1"
    assert {[dict get $d devices_match] eq "1"} "A devices_match=1"
    assert {[dict get $d ports_match] eq "1"} "A ports_match=1"
    assert {[dict get $d error_lines] eq "0"} "A error_lines=0"
    assert {[dict get $d warning_lines] eq "1"} "A warning_lines=1"
    assert {[dict get $d lvs_verdict] eq "clean"} "A lvs_verdict=clean"

    # ---- Case B: LAST-WINS counts tooth ----
    # Block1 reports devices 500 vs 498 (delta +2, mismatch). Block2 (re-run)
    # reports devices 500 vs 500 (delta 0, match). All other counts match in
    # both blocks, no ERROR lines. Correct: counts LAST-WINS -> devices_delta=0,
    # devices_match=1 -> verdict=clean. A first-wins impl -> devices_delta=+2,
    # devices_match=0 -> verdict=errors (WRONG).
    set B "LAYOUT CELL NAME = A
SOURCE CELL NAME = A
# of NETS in layout = 100
# of NETS in source = 100
# of DEVICES in layout = 500
# of DEVICES in source = 498
# of PORTS in layout = 32
# of PORTS in source = 32

LAYOUT CELL NAME = A
SOURCE CELL NAME = A
# of NETS in layout = 100
# of NETS in source = 100
# of DEVICES in layout = 500
# of DEVICES in source = 500
# of PORTS in layout = 32
# of PORTS in source = 32"
    set d [$candidate $B]
    assert {[dict get $d devices_delta] eq "0"} "B devices_delta=0 (LAST-WINS, not first-wins +2)"
    assert {[dict get $d devices_match] eq "1"} "B devices_match=1 (LAST-WINS)"
    assert {[dict get $d nets_match] eq "1"} "B nets_match=1"
    assert {[dict get $d ports_match] eq "1"} "B ports_match=1"
    assert {[dict get $d error_lines] eq "0"} "B error_lines=0"
    assert {[dict get $d lvs_verdict] eq "clean"} "B lvs_verdict=clean (LAST-WINS counts -> all match)"

    # ---- Case C: ERROR vs WARNING tooth ----
    # All counts match (delta 0 everywhere), but 2 ERROR lines + 3 WARNING lines.
    # Correct: error_lines=2, warning_lines=3, verdict=errors (ERROR lines drive
    # verdict even when deltas are 0). Naive (a) counts WARNING as error ->
    # error_lines=5 (WRONG); naive (b) only checks deltas -> verdict=clean (WRONG).
    set C "LAYOUT CELL NAME = C
SOURCE CELL NAME = C
# of NETS in layout = 50
# of NETS in source = 50
# of DEVICES in layout = 200
# of DEVICES in source = 200
# of PORTS in layout = 16
# of PORTS in source = 16
ERROR: port clk is unmatched
ERROR: net vdd is unmatched
WARNING: device M1 size differs
WARNING: device M2 size differs
WARNING: net gnd floating"
    set d [$candidate $C]
    assert {[dict get $d error_lines] eq "2"} "C error_lines=2 (NOT 5 -- WARNING is benign)"
    assert {[dict get $d warning_lines] eq "3"} "C warning_lines=3"
    assert {[dict get $d nets_match] eq "1"} "C nets_match=1 (deltas 0)"
    assert {[dict get $d devices_match] eq "1"} "C devices_match=1"
    assert {[dict get $d ports_match] eq "1"} "C ports_match=1"
    assert {[dict get $d lvs_verdict] eq "errors"} "C lvs_verdict=errors (ERROR lines > 0 despite delta 0)"

    # ---- Case D: SIGNED delta direction tooth ----
    # nets layout=100 source=102 -> delta = -2 (source extra). devices layout=500
    # source=498 -> delta = +2 (layout extra). Correct: nets_delta=-2,
    # devices_delta=+2. Naive abs-value -> nets_delta=+2 (WRONG sign).
    set D "LAYOUT CELL NAME = D
SOURCE CELL NAME = D
# of NETS in layout = 100
# of NETS in source = 102
# of DEVICES in layout = 500
# of DEVICES in source = 498
# of PORTS in layout = 32
# of PORTS in source = 32"
    set d [$candidate $D]
    assert {[dict get $d nets_delta] eq "-2"} "D nets_delta=-2 (SIGNED, source extra; abs -> +2 WRONG)"
    assert {[dict get $d devices_delta] eq "2"} "D devices_delta=+2 (SIGNED, layout extra)"
    assert {[dict get $d ports_delta] eq "0"} "D ports_delta=0"
    assert {[dict get $d nets_match] eq "0"} "D nets_match=0"
    assert {[dict get $d devices_match] eq "0"} "D devices_match=0"
    assert {[dict get $d ports_match] eq "1"} "D ports_match=1"
    assert {[dict get $d lvs_verdict] eq "errors"} "D lvs_verdict=errors"

    # ---- Case E: cell-name whitespace-collapse tooth ----
    # Both cell names are "TOP" and all counts match, 0 errors -> CLEAN. BUT the
    # LAYOUT CELL NAME line has double internal spaces ("LAYOUT  CELL  NAME  =  TOP").
    # A strict-whitespace matcher fails to recognize the line -> layout_cell="" ->
    # cell_name_match=0 -> verdict=errors (WRONG). Correct (whitespace collapsed)
    # -> cell_name_match=1 -> verdict=clean.
    set E "LAYOUT  CELL  NAME  =  TOP
SOURCE CELL NAME = TOP
# of NETS  in  layout = 50
# of NETS in source = 50
# of DEVICES in layout = 200
# of DEVICES in source = 200
# of PORTS in layout = 16
# of PORTS in source = 16"
    set d [$candidate $E]
    assert {[dict get $d layout_cell] eq "TOP"} "E layout_cell=TOP (whitespace collapsed)"
    assert {[dict get $d source_cell] eq "TOP"} "E source_cell=TOP"
    assert {[dict get $d cell_name_match] eq "1"} "E cell_name_match=1 (whitespace-collapse required)"
    assert {[dict get $d nets_delta] eq "0"} "E nets_delta=0 (whitespace-collapse on NETS line)"
    assert {[dict get $d lvs_verdict] eq "clean"} "E lvs_verdict=clean (strict-whitespace impl -> errors WRONG)"

    # ---- Case F: ERROR-line ACCUMULATION across blocks tooth ----
    # Two blocks, both clean on counts (all delta 0, cells match). Block1 (older
    # run) has 1 ERROR line; block2 (re-run) has 0 ERROR lines. Counts use
    # LAST-WINS (so block2's counts are authoritative) BUT ERROR lines ACCUMULATE
    # across ALL blocks. Correct: error_lines=1 -> verdict=errors. A naive impl
    # that takes ERROR lines from only the last block -> error_lines=0 ->
    # verdict=clean (WRONG).
    set F "LAYOUT CELL NAME = F
SOURCE CELL NAME = F
# of NETS in layout = 80
# of NETS in source = 80
# of DEVICES in layout = 400
# of DEVICES in source = 400
# of PORTS in layout = 24
# of PORTS in source = 24
ERROR: net vcc unmatched

LAYOUT CELL NAME = F
SOURCE CELL NAME = F
# of NETS in layout = 80
# of NETS in source = 80
# of DEVICES in layout = 400
# of DEVICES in source = 400
# of PORTS in layout = 24
# of PORTS in source = 24"
    set d [$candidate $F]
    assert {[dict get $d devices_delta] eq "0"} "F devices_delta=0 (LAST-WINS counts)"
    assert {[dict get $d error_lines] eq "1"} "F error_lines=1 (ACCUMULATE across blocks; last-block-only -> 0 WRONG)"
    assert {[dict get $d lvs_verdict] eq "errors"} "F lvs_verdict=errors (accumulated ERROR; last-block-only -> clean WRONG)"

    return "ALL_ASSERTS_PASS"
}
source naive.tcl
puts [check lvs_summary_audit]
