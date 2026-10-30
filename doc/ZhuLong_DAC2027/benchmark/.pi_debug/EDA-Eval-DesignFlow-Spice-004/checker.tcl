# Single-param check(candidate) -- framework injects wrapper that calls
# `check spice_netlist_parametrize` and captures the return value / exception
# as the DESIGN_FLOW_VERDICT. Helper procs defined inside become global in Tcl.
proc check {candidate} {
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
# tolerant helpers over the returned netlist string
proc _write {path txt} { set fo [open $path w]; puts -nonewline $fo $txt; close $fo }
proc _line_idx {txt substr} {
    # return 1-based index of first line containing substr, or 0
    set i 0
    foreach ln [split $txt "\n"] {
        incr i
        if {[string first $substr $ln] >= 0} { return $i }
    }
    return 0
}
proc _line_idx_from {txt substr start} {
    # return 1-based index of first line containing substr at/after line start
    set i 0
    foreach ln [split $txt "\n"] {
        incr i
        if {$i >= $start && [string first $substr $ln] >= 0} { return $i }
    }
    return 0
}
proc _has_line_starting {txt tok} {
    foreach ln [split $txt "\n"] {
        if {[string trim $ln] ne "" && [lindex [string trim $ln] 0] eq $tok} { return 1 }
    }
    return 0
}
proc _count_substring {txt substr} {
    set n 0
    set i 0
    while {1} {
        set j [string first $substr $txt $i]
        if {$j < 0} break
        incr n
        set i [expr {$j + 1}]
    }
    return $n
}

set pass 0
set fail 0

# ---------- NETLIST A: basic -- target subckt + 4 targets + 2 decoys in same subckt ----------
set nlA "* delay cell netlist (sanitized)\n.options list acct\n.inc './models'\n.SUBCKT R_RasVdbiasDlyStd_gut_MC InN In Out vdd vss\nXMMP0 InN In netA vdd pmos_lv w=7.952e-6 l=325e-9 nf=4\nXMMN0 InN In netA vss nmos_lv w=3.976e-6 l=325e-9 nf=4\nXMMP1 netA netB vdd vdd pmos_lv w=2.0e-6 l=200e-9 nf=2\nXMMN1 netA netB vss vss nmos_lv w=1.0e-6 l=200e-9 nf=2\nXMMP10 delay1 InN inh_vcc inh_vbp ptn_lv w=8.001e-6 l=325e-9 nf=3\nXMMN15 delay1 InN inh_vcc inh_vbn ptn_lv w=3.999e-6 l=325e-9 nf=3\nR0 In Out 1k\n.ENDS R_RasVdbiasDlyStd_gut_MC\nXinst_top InN In Out vdd vss R_RasVdbiasDlyStd_gut_MC\n"
_write _nlA.sp $nlA
set rA [$candidate _nlA.sp]

# .PARAM block present BEFORE the .SUBCKT line, with correct extracted defaults
set subA [_line_idx $rA ".SUBCKT R_RasVdbiasDlyStd_gut_MC"]
assert {$subA > 0} "A subckt line found"
set pA [_line_idx_from $rA ".PARAM MP0_w=" 1]
assert {$pA > 0 && $pA < $subA} "A PARAM block before SUBCKT"
assert {[string first "MP0_w=7.952e-6" $rA] >= 0} "A MP0_w default"
assert {[string first "MP0_l=325e-9" $rA] >= 0} "A MP0_l default"
assert {[string first "MN0_w=3.976e-6" $rA] >= 0} "A MN0_w default"
assert {[string first "MP10_w=8.001e-6" $rA] >= 0} "A MP10_w default"
assert {[string first "MN15_w=3.999e-6" $rA] >= 0} "A MN15_w default"
# 4 target lines now reference the params (quoted)
assert {[string first "w='MP0_w'" $rA] >= 0} "A MP0 w param ref"
assert {[string first "l='MP0_l'" $rA] >= 0} "A MP0 l param ref"
assert {[string first "w='MP10_w'" $rA] >= 0} "A MP10 w param ref"
assert {[string first "l='MN15_l'" $rA] >= 0} "A MN15 l param ref"
# nf preserved on target lines
assert {[string first "w='MP0_w' l='MP0_l' nf=4" $rA] >= 0} "A MP0 nf preserved"
assert {[string first "w='MP10_w' l='MP10_l' nf=3" $rA] >= 0} "A MP10 nf preserved"
# TEETH: decoys XMMP1/XMMN1 keep NUMERIC w=/l= (NOT parametrized)
assert {[string first "XMMP1 netA netB vdd vdd pmos_lv w=2.0e-6 l=200e-9 nf=2" $rA] >= 0} "A decoy XMMP1 untouched"
assert {[string first "XMMN1 netA netB vss vss nmos_lv w=1.0e-6 l=200e-9 nf=2" $rA] >= 0} "A decoy XMMN1 untouched"
assert {[string first "w='XMMP1_w'" $rA] < 0} "A no spurious XMMP1 param"
# exactly one .PARAM block (4 .PARAM lines)
assert {[_count_substring $rA ".PARAM MP0_w="] == 1} "A single MP0 PARAM line"
assert {[_count_substring $rA ".PARAM MN15_w="] == 1} "A single MN15 PARAM line"
incr pass

# ---------- NETLIST B: TEETH -- second subckt with its own XMMP0 decoy ----------
set nlB ".SUBCKT R_RasVdbiasDlyStd_gut InN In Out vdd vss\nXMMP0 InN In netA vdd pmos_lv w=5.0e-6 l=300e-9 nf=2\n.ENDS R_RasVdbiasDlyStd_gut\n.SUBCKT R_RasVdbiasDlyStd_gut_MC InN In Out vdd vss\nXMMP0 InN In netA vdd pmos_lv w=7.952e-6 l=325e-9 nf=4\nXMMN0 InN In netA vss nmos_lv w=3.976e-6 l=325e-9 nf=4\nXMMP10 delay1 InN inh_vcc w=8.001e-6 l=325e-9 nf=3\nXMMN15 delay1 InN inh_vcc w=3.999e-6 l=325e-9 nf=3\n.ENDS R_RasVdbiasDlyStd_gut_MC\n"
_write _nlB.sp $nlB
set rB [$candidate _nlB.sp]
# the _MC subckt's XMMP0 IS parametrized
assert {[string first "XMMP0 InN In netA vdd pmos_lv w='MP0_w' l='MP0_l' nf=4" $rB] >= 0} "B MC XMMP0 parametrized"
# TEETH: the OTHER subckt's XMMP0 keeps numeric w=/l= (subcircuit scoping)
assert {[string first "XMMP0 InN In netA vdd pmos_lv w=5.0e-6 l=300e-9 nf=2" $rB] >= 0} "B other-subckt XMMP0 untouched"
assert {[string first "w='MP0_w' l='MP0_l' nf=2" $rB] < 0} "B no leak into other subckt"
# .PARAM block sits before the _MC .SUBCKT, NOT before the non-MC one
set subB_MC [_line_idx $rB ".SUBCKT R_RasVdbiasDlyStd_gut_MC"]
set subB_no [_line_idx $rB ".SUBCKT R_RasVdbiasDlyStd_gut "]
set pB [_line_idx_from $rB ".PARAM MP0_w=" 1]
assert {$pB > $subB_no && $pB < $subB_MC} "B PARAM block between non-MC and MC subckt"
incr pass

# ---------- NETLIST C: TEETH -- already parameterized (idempotency) ----------
set nlC ".PARAM MP0_w=7.952e-6 MP0_l=325e-9\n.PARAM MN0_w=3.976e-6 MN0_l=325e-9\n.PARAM MP10_w=8.001e-6 MP10_l=325e-9\n.PARAM MN15_w=3.999e-6 MN15_l=325e-9\n.SUBCKT R_RasVdbiasDlyStd_gut_MC InN In Out vdd vss\nXMMP0 InN In netA vdd pmos_lv w='MP0_w' l='MP0_l' nf=4\nXMMN0 InN In netA vss nmos_lv w='MN0_w' l='MN0_l' nf=4\nXMMP10 delay1 InN inh_vcc w='MP10_w' l='MP10_l' nf=3\nXMMN15 delay1 InN inh_vcc w='MN15_w' l='MN15_l' nf=3\n.ENDS R_RasVdbiasDlyStd_gut_MC\n"
_write _nlC.sp $nlC
set rC [$candidate _nlC.sp]
# no double-parametrize (no nested quotes)
assert {[string first "w=''MP0_w'_w'" $rC] < 0} "C no double parametrize"
assert {[string first "w='MP0_w'" $rC] >= 0} "C MP0 ref preserved"
# exactly one .PARAM block per param (no duplicate injected)
assert {[_count_substring $rC ".PARAM MP0_w="] == 1} "C single MP0 PARAM (idempotent)"
assert {[_count_substring $rC ".PARAM MN15_w="] == 1} "C single MN15 PARAM (idempotent)"
incr pass

# ---------- NETLIST D: TEETH -- surgical preservation of many params ----------
set nlD ".SUBCKT R_RasVdbiasDlyStd_gut_MC InN In Out vdd vss\nXMMP0 InN In netA vdd pmos_lv w=7.952e-6 l=325e-9 nf=4 m=1 ad=2.5e-12 as=2.5e-12 pd=8e-6 ps=8e-6\nXMMN15 delay1 InN inh_vcc w=3.999e-6 l=325e-9 nf=3 m=2 ad=1.0e-12 as=1.0e-12 pd=6e-6 ps=6e-6\n.ENDS R_RasVdbiasDlyStd_gut_MC\n"
_write _nlD.sp $nlD
set rD [$candidate _nlD.sp]
assert {[string first "w='MP0_w' l='MP0_l' nf=4 m=1 ad=2.5e-12 as=2.5e-12 pd=8e-6 ps=8e-6" $rD] >= 0} "D MP0 all extra params preserved"
assert {[string first "w='MN15_w' l='MN15_l' nf=3 m=2 ad=1.0e-12 as=1.0e-12 pd=6e-6 ps=6e-6" $rD] >= 0} "D MN15 all extra params preserved"
# defaults extracted correctly
assert {[string first "MP0_w=7.952e-6" $rD] >= 0} "D MP0_w default"
assert {[string first "MN15_l=325e-9" $rD] >= 0} "D MN15_l default"
incr pass

# ---------- NETLIST E: TEETH -- many decoys + value extraction correctness ----------
set nlE "* header\n.SUBCKT R_RasVdbiasDlyStd_gut_MC InN In Out vdd vss\nXMMP0 InN In n0 vdd p w=7.952e-6 l=325e-9 nf=4\nXMMN0 InN In n0 vss n w=3.976e-6 l=325e-9 nf=4\nXMMP1 n0 n1 vdd vdd p w=1.5e-6 l=150e-9 nf=2\nXMMN1 n0 n1 vss vss n w=0.8e-6 l=150e-9 nf=2\nXMMP2 n1 n2 vdd vdd p w=3.0e-6 l=200e-9 nf=2\nXMMP10 d1 InN ihc w=8.001e-6 l=325e-9 nf=3\nXMMN15 d1 InN ihc w=3.999e-6 l=325e-9 nf=3\n.ENDS R_RasVdbiasDlyStd_gut_MC\n.measure tran tdelay trig v(In) val=0.6 rise=1 targ v(Out) val=0.6 rise=1\n"
_write _nlE.sp $nlE
set rE [$candidate _nlE.sp]
# all 4 targets parametrized with correct extracted defaults
assert {[string first "w='MP0_w' l='MP0_l' nf=4" $rE] >= 0} "E MP0"
assert {[string first "w='MN0_w' l='MN0_l' nf=4" $rE] >= 0} "E MN0"
assert {[string first "w='MP10_w' l='MP10_l' nf=3" $rE] >= 0} "E MP10"
assert {[string first "w='MN15_w' l='MN15_l' nf=3" $rE] >= 0} "E MN15"
assert {[string first "MP0_w=7.952e-6" $rE] >= 0} "E MP0_w default"
assert {[string first "MN0_w=3.976e-6" $rE] >= 0} "E MN0_w default"
assert {[string first "MP10_w=8.001e-6" $rE] >= 0} "E MP10_w default"
assert {[string first "MN15_w=3.999e-6" $rE] >= 0} "E MN15_w default"
# TEETH: 3 decoys keep numeric w=/l=
assert {[string first "XMMP1 n0 n1 vdd vdd p w=1.5e-6 l=150e-9 nf=2" $rE] >= 0} "E decoy XMMP1 untouched"
assert {[string first "XMMN1 n0 n1 vss vss n w=0.8e-6 l=150e-9 nf=2" $rE] >= 0} "E decoy XMMN1 untouched"
assert {[string first "XMMP2 n1 n2 vdd vdd p w=3.0e-6 l=200e-9 nf=2" $rE] >= 0} "E decoy XMMP2 untouched"
# .measure line preserved
assert {[string first ".measure tran tdelay" $rE] >= 0} "E measure preserved"
incr pass

return "PASS $pass / FAIL $fail (5 cases: A basic, B subckt-scope-teeth, C idempotency-teeth, D surgical-params-teeth, E decoys+extraction-teeth)"
}
