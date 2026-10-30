# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc check {candidate} {
    # ---- Case A: baseline -- one library, two schematic cells, both requested ----
    set clA "* Cell    : IO_DqLdMdl
* Cell    : IO_DqLd"
    set nlA "* Library : drvqa_cmos_io
* Cell    : IO_DqLdMdl
* View    : schematic
.subckt IO_DqLdMdl Y A B
XM1 Y A B gnd
.ends
* Cell    : IO_DqLd
* View    : schematic
.subckt IO_DqLd Y A
.ends"
    set d [$candidate $clA $nlA]
    assert {[dict get $d total_cell_list] eq "2"} "A total_cell_list=2"
    assert {[llength [dict get $d pairs]] eq "2"} "A mapped_count=2"
    assert {[lindex [dict get $d pairs] 0] eq "drvqa_cmos_io IO_DqLdMdl"} "A pair0=drvqa_cmos_io IO_DqLdMdl"
    assert {[lindex [dict get $d pairs] 1] eq "drvqa_cmos_io IO_DqLd"} "A pair1=drvqa_cmos_io IO_DqLd"
    assert {[dict get $d mapped_count] eq "2"} "A mapped_count=2"
    assert {[llength [dict get $d unmapped]] eq "0"} "A unmapped_count=0"
    assert {[dict get $d unmapped_count] eq "0"} "A unmapped_count=0"
    assert {[llength [dict get $d multi_lib_cells]] eq "0"} "A multi_lib empty"
    assert {[dict get $d verdict] eq "complete"} "A verdict=complete"

    # ---- Case B: SHARED-LIBRARY state-machine tooth -- ONE library header, TWO cells ----
    # A block-based parser (one library per cell block) maps only the first cell.
    set clB "* Cell    : latrqLx1
* Cell    : ffrqLx1"
    set nlB "* Library : stdcells_ac
* Cell    : latrqLx1
* View    : schematic
.subckt latrqLx1 Q D CK
.ends
* Cell    : ffrqLx1
* View    : schematic
.subckt ffrqLx1 Q D CK
.ends"
    set d [$candidate $clB $nlB]
    assert {[dict get $d total_cell_list] eq "2"} "B total_cell_list=2"
    assert {[llength [dict get $d pairs]] eq "2"} "B mapped_count=2 (both share stdcells_ac); block-parser -> 1 (WRONG, ffrqLx1 unmapped)"
    assert {[lindex [dict get $d pairs] 0] eq "stdcells_ac latrqLx1"} "B pair0=stdcells_ac latrqLx1"
    assert {[lindex [dict get $d pairs] 1] eq "stdcells_ac ffrqLx1"} "B pair1=stdcells_ac ffrqLx1 (state machine carries library forward)"
    assert {[dict get $d unmapped_count] eq "0"} "B unmapped=0; block-parser -> 1 (WRONG)"
    assert {[dict get $d verdict] eq "complete"} "B verdict=complete"

    # ---- Case C: SCHEMATIC-VIEW-FILTER tooth -- a symbol-only cell must be unmapped ----
    # A parser that emits on `* Cell` (ignoring view) wrongly maps symOnly.
    set clC "* Cell    : symOnly
* Cell    : schCell"
    set nlC "* Library : libA
* Cell    : symOnly
* View    : symbol
* Cell    : schCell
* View    : schematic"
    set d [$candidate $clC $nlC]
    assert {[dict get $d total_cell_list] eq "2"} "C total_cell_list=2"
    assert {[llength [dict get $d pairs]] eq "1"} "C mapped_count=1 (only schCell schematic); ignore-view -> 2 (WRONG)"
    assert {[lindex [dict get $d pairs] 0] eq "libA schCell"} "C pair0=libA schCell"
    assert {[llength [dict get $d unmapped]] eq "1"} "C unmapped_count=1 (symOnly); ignore-view -> 0 (WRONG)"
    assert {[lindex [dict get $d unmapped] 0] eq "symOnly"} "C unmapped(0)=symOnly"
    assert {[dict get $d verdict] eq "incomplete"} "C verdict=incomplete"

    # ---- Case D: MULTI-LIBRARY cell tooth -- same cell defined in two libraries ----
    # A parser that dedups by cell NAME drops the second pair (WRONG).
    set clD "* Cell    : latqLx1"
    set nlD "* Library : stdcells_ac
* Cell    : latqLx1
* View    : schematic
* Library : drvqa_cmos_io
* Cell    : latqLx1
* View    : schematic"
    set d [$candidate $clD $nlD]
    assert {[dict get $d total_cell_list] eq "1"} "D total_cell_list=1"
    assert {[llength [dict get $d pairs]] eq "2"} "D mapped_count=2 (two libs); dedup-by-cell -> 1 (WRONG)"
    assert {[lindex [dict get $d pairs] 0] eq "stdcells_ac latqLx1"} "D pair0=stdcells_ac latqLx1"
    assert {[lindex [dict get $d pairs] 1] eq "drvqa_cmos_io latqLx1"} "D pair1=drvqa_cmos_io latqLx1"
    assert {[dict get $d unmapped_count] eq "0"} "D unmapped=0"
    assert {[llength [dict get $d multi_lib_cells]] eq "1"} "D multi_lib has 1; dedup-by-cell -> 0 (WRONG)"
    assert {[lindex [dict get $d multi_lib_cells] 0] eq "latqLx1"} "D multi_lib(0)=latqLx1"
    assert {[dict get $d verdict] eq "complete"} "D verdict=complete"

    # ---- Case E: HEADER-STRICTNESS + cell-list dup + unmapped tooth ----
    # `* Library catalog : fake` is NOT a Library header (strict). A substring
    # matcher sets cur_lib=fake and emits a bogus (fake, latrqLx1) pair (WRONG).
    # cell_list has latrqLx1 twice -> total_cell_list=2 (unique). ghost unmapped.
    set clE "* Cell    : latrqLx1
* Cell    : latrqLx1
* Cell    : ghost"
    set nlE "* Library : stdcells_ac
* Cell    : latrqLx1
* View    : schematic
* Library catalog : fake_lib
* Cell    : latrqLx1
* View    : schematic"
    set d [$candidate $clE $nlE]
    assert {[dict get $d total_cell_list] eq "2"} "E total_cell_list=2 (unique: latrqLx1, ghost); count-lines -> 3 (WRONG)"
    assert {[llength [dict get $d pairs]] eq "1"} "E mapped_count=1 (strict: fake_lib not a header -> dupe); substring-match -> 2 (WRONG)"
    assert {[lindex [dict get $d pairs] 0] eq "stdcells_ac latrqLx1"} "E pair0=stdcells_ac latrqLx1"
    assert {[llength [dict get $d unmapped]] eq "1"} "E unmapped_count=1 (ghost)"
    assert {[lindex [dict get $d unmapped] 0] eq "ghost"} "E unmapped(0)=ghost"
    assert {[llength [dict get $d multi_lib_cells]] eq "0"} "E multi_lib empty (strict: fake_lib rejected); substring-match -> 1 (WRONG)"
    assert {[dict get $d verdict] eq "incomplete"} "E verdict=incomplete (ghost unmapped)"

    # ---- Case F: comprehensive (state machine + view filter + multi-lib + strictness + dup + unmapped) ----
    set clF "* Cell    : latrqLx1
* Cell    : ffrqLx1
* Cell    : symOnly
* Cell    : latrqLx1
* Cell    : missing"
    set nlF "* Library : stdcells_ac
* Cell    : latrqLx1
* View    : schematic
* Cell    : ffrqLx1
* View    : schematic
* Cell    : symOnly
* View    : symbol
* Library Notes : decoy_lib
* Cell    : latrqLx1
* View    : schematic
* Library : drvqa_cmos_io
* Cell    : latrqLx1
* View    : schematic"
    set d [$candidate $clF $nlF]
    assert {[dict get $d total_cell_list] eq "4"} "F total_cell_list=4 (unique: latrqLx1, ffrqLx1, symOnly, missing); count-lines -> 5 (WRONG)"
    assert {[llength [dict get $d pairs]] eq "3"} "F mapped_count=3 (stdcells_ac latrqLx1, stdcells_ac ffrqLx1, drvqa_cmos_io latrqLx1); block-parser/dedup-by-cell/substring -> wrong"
    assert {[lindex [dict get $d pairs] 0] eq "stdcells_ac latrqLx1"} "F pair0=stdcells_ac latrqLx1"
    assert {[lindex [dict get $d pairs] 1] eq "stdcells_ac ffrqLx1"} "F pair1=stdcells_ac ffrqLx1 (state machine carries stdcells_ac forward past symOnly symbol block)"
    assert {[lindex [dict get $d pairs] 2] eq "drvqa_cmos_io latrqLx1"} "F pair2=drvqa_cmos_io latrqLx1 (strict: * Library Notes decoy rejected, so cur_lib stays stdcells_ac for the dupe; only the real * Library : drvqa_cmos_io flips it)"
    assert {[llength [dict get $d unmapped]] eq "2"} "F unmapped_count=2 (symOnly symbol-only + missing not in netlist); ignore-view -> 1 (WRONG)"
    assert {[lindex [dict get $d unmapped] 0] eq "symOnly"} "F unmapped(0)=symOnly (requested order)"
    assert {[lindex [dict get $d unmapped] 1] eq "missing"} "F unmapped(1)=missing"
    assert {[llength [dict get $d multi_lib_cells]] eq "1"} "F multi_lib has 1 (latrqLx1 in stdcells_ac + drvqa_cmos_io); dedup-by-cell -> 0 (WRONG)"
    assert {[lindex [dict get $d multi_lib_cells] 0] eq "latrqLx1"} "F multi_lib(0)=latrqLx1"
    assert {[dict get $d verdict] eq "incomplete"} "F verdict=incomplete (symOnly + missing unmapped)"
    return "ALL_ASSERTS_PASS"
}
