# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc check {candidate} {
    # ---- Case A: violated setup + met hold + macro=0 (baseline) ----
    set repA "# Genus Synthesis QoR Report
# Design: aes_cipher
# Corner: tt_0p9v_125c
=== TIMING (setup) ===
WNS = -0.234 ns
TNS = -1.456 ns
Violated endpoints = 12
Total endpoints = 8421
=== TIMING (hold) ===
WNS = 0.000 ns
TNS = 0.000 ns
Violated endpoints = 0
Total endpoints = 8421
=== AREA ===
Combinational area = 800.50 um^2
Sequential area = 434.06 um^2
Macro area = 0.00 um^2
Total area = 1234.56 um^2
=== INSTANCE ===
Number of leaf cells = 1450
Number of hierarchical cells = 50
Number of registers = 420
Number of nets = 2300
"
    set d [$candidate $repA]
    assert {[dict get $d design] eq "aes_cipher"} "A design"
    assert {[dict get $d corner] eq "tt_0p9v_125c"} "A corner"
    assert {[dict get $d setup_wns] eq "-0.234"} "A setup_wns sign preserved (-0.234); naive regex dropping '-' -> 0.234"
    assert {[dict get $d setup_tns] eq "-1.456"} "A setup_tns sign preserved"
    assert {[dict get $d setup_violated] eq "12"} "A setup_violated"
    assert {[dict get $d setup_total] eq "8421"} "A setup_total"
    assert {[dict get $d hold_wns] eq "0.000"} "A hold_wns"
    assert {[dict get $d hold_violated] eq "0"} "A hold_violated"
    assert {[dict get $d hold_total] eq "8421"} "A hold_total"
    assert {[dict get $d combo_area] eq "800.50"} "A combo_area"
    assert {[dict get $d seq_area] eq "434.06"} "A seq_area"
    assert {[dict get $d macro_area] eq "0.00"} "A macro_area"
    assert {[dict get $d total_area] eq "1234.56"} "A total_area (explicit line)"
    assert {[dict get $d area_unit] eq "um^2"} "A area_unit"
    assert {[dict get $d leaf_cells] eq "1450"} "A leaf_cells"
    assert {[dict get $d hier_cells] eq "50"} "A hier_cells"
    assert {[dict get $d total_cells] eq "1500"} "A total_cells = leaf+hier = 1500 (registers NOT subtracted)"
    assert {[dict get $d registers] eq "420"} "A registers"
    assert {[dict get $d nets] eq "2300"} "A nets"
    assert {[dict get $d timing_met] eq "0"} "A timing_met=0 (setup violated); naive sign-drop -> 1 (WRONG)"
    assert {[dict get $d area_check] eq "1"} "A area_check=1 (800.50+434.06+0.00=1234.56)"

    # ---- Case B: slack-sign + setup/hold separation tooth ----
    # setup MET (WNS=0.150 positive), hold VIOLATED (WNS=-0.080 negative).
    # A sign-dropping parser reads hold_wns=0.080 -> timing_met=1 (WRONG).
    # A last-WNS-wins parser overwrites setup -> loses setup_violated=0.
    set repB "# Genus Synthesis QoR Report
# Design: uart_top
# Corner: ss_0p7v_125c
=== TIMING (setup) ===
WNS = 0.150 ns
TNS = 0.000 ns
Violated endpoints = 0
Total endpoints = 512
=== TIMING (hold) ===
WNS = -0.080 ns
TNS = -0.240 ns
Violated endpoints = 3
Total endpoints = 512
=== AREA ===
Combinational area = 220.00 um^2
Sequential area = 80.00 um^2
Macro area = 0.00 um^2
Total area = 300.00 um^2
=== INSTANCE ===
Number of leaf cells = 600
Number of hierarchical cells = 10
Number of registers = 200
Number of nets = 950
"
    set d [$candidate $repB]
    assert {[dict get $d setup_wns] eq "0.150"} "B setup_wns=0.150 (met)"
    assert {[dict get $d hold_wns] eq "-0.080"} "B hold_wns=-0.080 (sign preserved); naive drop -> 0.080 (WRONG)"
    assert {[dict get $d hold_violated] eq "3"} "B hold_violated=3 (section separation; last-WNS-wins loses this)"
    assert {[dict get $d setup_violated] eq "0"} "B setup_violated=0"
    assert {[dict get $d timing_met] eq "0"} "B timing_met=0 (hold violated even though setup met)"
    assert {[dict get $d total_cells] eq "610"} "B total_cells=610"

    # ---- Case C: macro-area total + nm^2 unit + hyphenated corner tooth ----
    # total = combo+seq+macro = 10500 (macro=2500 MUST be included).
    # A compute-total-from-parts (combo+seq only) parser -> 8000 (WRONG).
    # Hardcoded um^2 -> wrong on nm^2. corner `ff_1p1v_-40c` has a hyphen.
    set repC "# Genus Synthesis QoR Report
# Design: soc_top
# Corner: ff_1p1v_-40c
=== TIMING (setup) ===
WNS = -1.200 ns
TNS = -12.500 ns
Violated endpoints = 30
Total endpoints = 12000
=== TIMING (hold) ===
WNS = -0.050 ns
TNS = -0.900 ns
Violated endpoints = 5
Total endpoints = 12000
=== AREA ===
Combinational area = 5000.00 nm^2
Sequential area = 3000.00 nm^2
Macro area = 2500.00 nm^2
Total area = 10500.00 nm^2
=== INSTANCE ===
Number of leaf cells = 8000
Number of hierarchical cells = 200
Number of registers = 1500
Number of nets = 16000
"
    set d [$candidate $repC]
    assert {[dict get $d corner] eq "ff_1p1v_-40c"} "C corner full hyphenated token; naive alnum-underscore-only class stops at the hyphen -> ff_1p1v_ (WRONG)"
    assert {[dict get $d macro_area] eq "2500.00"} "C macro_area"
    assert {[dict get $d total_area] eq "10500.00"} "C total_area explicit line (NOT combo+seq=8000)"
    assert {[dict get $d area_unit] eq "nm^2"} "C area_unit=nm^2; hardcoded um^2 fails"
    assert {[dict get $d area_check] eq "1"} "C area_check=1 (5000+3000+2500=10500)"
    assert {[dict get $d total_cells] eq "8200"} "C total_cells=8200"
    assert {[dict get $d timing_met] eq "0"} "C timing_met=0 (both setup & hold violated)"

    # ---- Case D: area_check FAILS (explicit total != sum of parts) tooth ----
    # total_area=95.00 but combo+seq+macro=100.00 -> area_check=0.
    # A parser that sets total=combo+seq+macro reports total=100.00 (WRONG,
    # should be the explicit 95.00) AND area_check=1 (WRONG).
    set repD "# Genus Synthesis QoR Report
# Design: small_pll
# Corner: tt_1p0v_25c
=== TIMING (setup) ===
WNS = 0.420 ns
TNS = 0.000 ns
Violated endpoints = 0
Total endpoints = 88
=== TIMING (hold) ===
WNS = 0.030 ns
TNS = 0.000 ns
Violated endpoints = 0
Total endpoints = 88
=== AREA ===
Combinational area = 60.00 um^2
Sequential area = 40.00 um^2
Macro area = 0.00 um^2
Total area = 95.00 um^2
=== INSTANCE ===
Number of leaf cells = 120
Number of hierarchical cells = 0
Number of registers = 60
Number of nets = 180
"
    set d [$candidate $repD]
    assert {[dict get $d total_area] eq "95.00"} "D total_area=95.00 (explicit, NOT computed 100.00)"
    assert {[dict get $d area_check] eq "0"} "D area_check=0 (60+40+0=100 != 95); compute-from-parts -> 1 (WRONG)"
    assert {[dict get $d timing_met] eq "1"} "D timing_met=1 (both setup & hold met)"
    assert {[dict get $d total_cells] eq "120"} "D total_cells=120 (hier=0)"

    # ---- Case E: design-prefix specificity + absent hold section (defaults) tooth ----
    # `# Design notes: ...` must NOT set design (only `# Design: ` does).
    # No hold section -> hold_wns/tns/violated/total default to "0.000"/"0".
    set repE "# Genus Synthesis QoR Report
# Design notes: synthetic sanity check
# Design: alu
# Corner: tt_0p9v_25c
=== TIMING (setup) ===
WNS = -0.500 ns
TNS = -2.000 ns
Violated endpoints = 4
Total endpoints = 200
=== AREA ===
Combinational area = 150.00 um^2
Sequential area = 50.00 um^2
Macro area = 0.00 um^2
Total area = 200.00 um^2
=== INSTANCE ===
Number of leaf cells = 300
Number of hierarchical cells = 5
Number of registers = 90
Number of nets = 400
"
    set d [$candidate $repE]
    assert {[dict get $d design] eq "alu"} "E design=alu (NOT 'notes: synthetic sanity check'); naive ^# Design match -> WRONG"
    assert {[dict get $d corner] eq "tt_0p9v_25c"} "E corner"
    assert {[dict get $d hold_wns] eq "0.000"} "E hold_wns default 0.000 (section absent)"
    assert {[dict get $d hold_tns] eq "0.000"} "E hold_tns default"
    assert {[dict get $d hold_violated] eq "0"} "E hold_violated default"
    assert {[dict get $d hold_total] eq "0"} "E hold_total default"
    assert {[dict get $d setup_wns] eq "-0.500"} "E setup_wns sign preserved"
    assert {[dict get $d timing_met] eq "0"} "E timing_met=0 (setup violated; hold default met)"
    assert {[dict get $d area_check] eq "1"} "E area_check=1 (150+50+0=200)"
    assert {[dict get $d total_cells] eq "305"} "E total_cells=305"

    # ---- Case F: comprehensive (sign + setup/hold + macro + nm^2 + design-notes decoy + register subset) ----
    set repF "# Genus Synthesis QoR Report
# Design notes: full-chip QoR
# Design: ddr_controller
# Corner: tt_0p9v_125c
=== TIMING (setup) ===
WNS = -0.650 ns
TNS = -8.200 ns
Violated endpoints = 18
Total endpoints = 6400
=== TIMING (hold) ===
WNS = 0.012 ns
TNS = 0.000 ns
Violated endpoints = 0
Total endpoints = 6400
=== AREA ===
Combinational area = 4500.00 nm^2
Sequential area = 2700.00 nm^2
Macro area = 1800.00 nm^2
Total area = 9000.00 nm^2
=== INSTANCE ===
Number of leaf cells = 5200
Number of hierarchical cells = 80
Number of registers = 1100
Number of nets = 10100
"
    set d [$candidate $repF]
    assert {[dict get $d design] eq "ddr_controller"} "F design (notes decoy ignored)"
    assert {[dict get $d corner] eq "tt_0p9v_125c"} "F corner"
    assert {[dict get $d setup_wns] eq "-0.650"} "F setup_wns sign"
    assert {[dict get $d hold_wns] eq "0.012"} "F hold_wns (met, small positive)"
    assert {[dict get $d setup_violated] eq "18"} "F setup_violated"
    assert {[dict get $d hold_violated] eq "0"} "F hold_violated"
    assert {[dict get $d combo_area] eq "4500.00"} "F combo"
    assert {[dict get $d seq_area] eq "2700.00"} "F seq"
    assert {[dict get $d macro_area] eq "1800.00"} "F macro"
    assert {[dict get $d total_area] eq "9000.00"} "F total explicit (NOT combo+seq=7200)"
    assert {[dict get $d area_unit] eq "nm^2"} "F area_unit"
    assert {[dict get $d area_check] eq "1"} "F area_check=1 (4500+2700+1800=9000)"
    assert {[dict get $d leaf_cells] eq "5200"} "F leaf"
    assert {[dict get $d hier_cells] eq "80"} "F hier"
    assert {[dict get $d total_cells] eq "5280"} "F total_cells=5280 (registers NOT subtracted: 5200+80, not 5200-1100+80)"
    assert {[dict get $d registers] eq "1100"} "F registers"
    assert {[dict get $d nets] eq "10100"} "F nets"
    assert {[dict get $d timing_met] eq "0"} "F timing_met=0 (setup violated despite hold met)"
    return "ALL_ASSERTS_PASS"
}
