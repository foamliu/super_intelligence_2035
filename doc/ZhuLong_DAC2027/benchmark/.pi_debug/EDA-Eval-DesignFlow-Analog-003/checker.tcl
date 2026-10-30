# Single-param check(candidate) -- framework injects a wrapper that calls
# `check hspice_meas_script_parse` and captures the return value / exception
# as the DESIGN_FLOW_VERDICT. Helper procs become global in Tcl.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
# tolerant string extractor: token after a key (stops at whitespace)
proc get_str {dictstr key} {
    set re [format {%s[[:space:]]+([^[:space:]]+)} $key]
    if {![regexp -- $re $dictstr -> v]} { error "get_str: key $key not found in dict" }
    return $v
}
proc get_int {dictstr key} {
    return [expr {int([get_str $dictstr $key])}]
}
# list extractor: everything after a key to end of string (final value)
proc get_list {dictstr key} {
    set re [format {%s[[:space:]]+(.*)$} $key]
    if {![regexp -- $re $dictstr -> v]} { error "get_list: key $key not found" }
    return [regexp -all -inline -- {[^[:space:]]+} $v]
}

proc check {candidate} {
set pass 0
set fail 0

# ---------- SCRIPT A: classic trig/targ, quoted param-level exprs, td=800n ----------
# Real shape (sanitized) of EqIoF2CslR_Sec28Mat0: continuation `+` lines,
# quoted param-expr levels '0.5*pvdleq'/'0.5*pvCsl', td=800n SI, fall/rise.
set scriptA {.param pvdleq = 1.17v
.param pvCsl = 0.9v
*EqIo fall to Csl rise
.meas tran EqIoF2CslR_Sec28Mat0
+trig  v(top.a.b.EqIomid) = '0.5*pvdleq'   td=800n   fall=5
+targ  v(top.a.b.Csl<0>)  = '0.5*pvCsl'    td=800n   rise=3}

set r [$candidate $scriptA]
assert {[get_int $r param_count] == 2} "A param_count"
assert {[get_int $r measure_count] == 1} "A measure_count"
assert {[get_int $r bodiless_count] == 0} "A bodiless_count"
assert {[get_int $r mode_trig_targ] == 1} "A mode_trig_targ"
assert {[get_int $r mode_when] == 0} "A mode_when"
assert {[get_int $r mode_find_when] == 0} "A mode_find_when"
assert {[get_int $r mode_param] == 0} "A mode_param"
assert {[get_int $r mode_unknown] == 0} "A mode_unknown"
assert {[get_int $r has_differential] == 0} "A has_differential"
assert {[get_int $r has_td_reference] == 0} "A has_td_reference"
assert {[get_int $r measures_with_quoted_param_level] == 1} "A measures_with_quoted_param_level"
assert {[get_int $r dual_trig_no_targ] == 0} "A dual_trig_no_targ"
assert {[get_str $r td_references] eq "none"} "A td_references"
set na [get_list $r measure_names]
assert {[llength $na] == 1} "A measure_names count"
assert {[lindex $na 0] eq "EqIoF2CslR_Sec28Mat0"} "A measure_names_0"
incr pass

# ---------- SCRIPT B: `when`-only, TAB-separated, single time capture ----------
# Real shape (sanitized) of t_EqIoR_Sec28Mat0: `.meas\ttran\tNAME`, `+when\tv`
# tabs, single `when` clause (no trig/targ). Teeth: a line-by-line parser that
# does not merge `+` continuation sees `.meas tran NAME` with no trig/targ and
# classifies `unknown`; a single-space splitter breaks on the tabs.
set scriptB {.param pvcc = 0.75v
.meas	tran	t_EqIoR_Sec28Mat0
+when	v(top.a.b.EqIomid) =  '0.5*pvcc'   td=800n  rise=6}

set r [$candidate $scriptB]
assert {[get_int $r param_count] == 1} "B param_count"
assert {[get_int $r measure_count] == 1} "B measure_count"
assert {[get_int $r mode_trig_targ] == 0} "B mode_trig_targ"
assert {[get_int $r mode_when] == 1} "B mode_when (continuation-merged, tab-tolerant)"
assert {[get_int $r mode_find_when] == 0} "B mode_find_when"
assert {[get_int $r mode_param] == 0} "B mode_param"
assert {[get_int $r mode_unknown] == 0} "B mode_unknown"
assert {[get_int $r has_td_reference] == 0} "B has_td_reference"
assert {[get_int $r measures_with_quoted_param_level] == 1} "B measures_with_quoted_param_level"
assert {[get_str $r td_references] eq "none"} "B td_references"
set nb [get_list $r measure_names]
assert {[lindex $nb 0] eq "t_EqIoR_Sec28Mat0"} "B measure_names_0 (tab-separated name extraction)"
incr pass

# ---------- SCRIPT C: find/when DIFFERENTIAL value capture ----------
# Real shape (sanitized) of DelIo_0_Split_Sec28Mat0: `find (sig1,sig2)` then
# `+when v(...)=...`. Teeth: a trig/targ-only parser classifies `unknown`; a
# v() parser that ignores the comma pair misses has_differential.
set scriptC {.param pvdleq = 1.17v
*Io/IoN split when RdEn rise
.meas tran DelIo_0_Split_Sec28Mat0
+find (top.a.b.Io0mid<0>,top.a.b.IoN0mid<0>)
+when  v(top.a.b.RdEnmid) = '0.5*pvdleq'   td=800n   rise=1}

set r [$candidate $scriptC]
assert {[get_int $r measure_count] == 1} "C measure_count"
assert {[get_int $r mode_find_when] == 1} "C mode_find_when (find clause)"
assert {[get_int $r mode_trig_targ] == 0} "C mode_trig_targ"
assert {[get_int $r mode_when] == 0} "C mode_when (find takes precedence over when)"
assert {[get_int $r has_differential] == 1} "C has_differential (v(sig1,sig2) comma pair)"
set nc [get_list $r measure_names]
assert {[lindex $nc 0] eq "DelIo_0_Split_Sec28Mat0"} "C measure_names_0"
incr pass

# ---------- SCRIPT D: param DERIVED + td measure-reference + differential ----------
# Real shape (sanitized): t_EqIoR (when), t_IoEq0P95 (when + differential +
# td=t_RdEnF_Sec28Mat0 reference), EqIoR2IoEq0P95 (param='... - ...' derived).
# Teeth: a trig/targ-only parser classifies the param measure `unknown`; a
# td-numeric-only parser misses has_td_reference; the param arithmetic-expr
# clause must NOT count as a voltage level.
set scriptD {.meas tran t_EqIoR_Sec28Mat0
+when v(top.a.b.EqIomid) = '0.5*pvdleq' td=800n rise=6
.meas tran t_IoEq0P95_Sec28Mat0
+when v(top.a.b.Io0mid<0>,top.a.b.IoN0mid<0>) = '0.05*0.5*pvblh' td=t_RdEnF_Sec28Mat0
.meas tran EqIoR2IoEq0P95_Sec28Mat0 param='t_IoEq0P95_Sec28Mat0 - t_EqIoR_Sec28Mat0'}

set r [$candidate $scriptD]
assert {[get_int $r param_count] == 0} "D param_count"
assert {[get_int $r measure_count] == 3} "D measure_count"
assert {[get_int $r mode_when] == 2} "D mode_when (t_EqIoR + t_IoEq0P95)"
assert {[get_int $r mode_param] == 1} "D mode_param (EqIoR2IoEq0P95 derived)"
assert {[get_int $r mode_trig_targ] == 0} "D mode_trig_targ"
assert {[get_int $r mode_unknown] == 0} "D mode_unknown (param measure must NOT be unknown)"
assert {[get_int $r has_differential] == 1} "D has_differential (t_IoEq0P95 v(sig1,sig2))"
assert {[get_int $r has_td_reference] == 1} "D has_td_reference (td=t_RdEnF_Sec28Mat0)"
assert {[get_str $r td_references] eq "t_RdEnF_Sec28Mat0"} "D td_references"
# measures_with_quoted_param_level: t_EqIoR ('0.5*pvdleq') + t_IoEq0P95
# ('0.05*0.5*pvblh') = 2; the param='...' clause is NOT a voltage level.
assert {[get_int $r measures_with_quoted_param_level] == 2} "D measures_with_quoted_param_level (param clause excluded)"
set nd [get_list $r measure_names]
assert {[llength $nd] == 3} "D measure_names count"
assert {[lindex $nd 0] eq "t_EqIoR_Sec28Mat0"} "D name0"
assert {[lindex $nd 1] eq "t_IoEq0P95_Sec28Mat0"} "D name1"
assert {[lindex $nd 2] eq "EqIoR2IoEq0P95_Sec28Mat0"} "D name2"
incr pass

# ---------- SCRIPT E: dual-trig-no-targ + bodiless + comments ----------
# Real shape (sanitized): RwEnNF2RdEnR (two `+trig`, zero `+targ`), a stray
# bodiless `.meas reennf2rdenr_r1` with no continuation, a `*` comment between
# the bodiless header and the next measure, YsaEnPls (normal trig/targ).
# Teeth: single-trig-assumption parser -> dual_trig_no_targ==0; a parser that
# treats `*` comments as measures inflates measure_count; ignoring bodiless
# misses bodiless_count.
set scriptE {.param pvdleq = 1.17v
*RwEnN fall to RdEn rise
.meas tran RwEnNF2RdEnR_Sec28Mat0
+trig v(top.a.b.RwEnNmid) = '0.5*pvdleq' td=800n fall=5
+trig v(top.a.b.RdEnmid)  = '0.5*pvdleq' td=800n rise=1
.meas  reennf2rdenr_r1_Sec28Mat0
*YsaEqNloc pulse
.meas tran YsaEnPls_Sec28Mat0
+trig v(top.a.b.YsaEn) = '0.5*pvcc' td=800n rise=1
+targ v(top.a.b.YsaEn) = '0.5*pvcc' td=800n fall=1}

set r [$candidate $scriptE]
assert {[get_int $r param_count] == 1} "E param_count"
assert {[get_int $r measure_count] == 3} "E measure_count (2 real + 1 bodiless; comments NOT counted)"
assert {[get_int $r bodiless_count] == 1} "E bodiless_count (reennf2rdenr_r1 has no + body)"
assert {[get_int $r mode_trig_targ] == 2} "E mode_trig_targ (RwEnNF2RdEnR + YsaEnPls)"
assert {[get_int $r mode_unknown] == 1} "E mode_unknown (bodiless -> unknown)"
assert {[get_int $r dual_trig_no_targ] == 1} "E dual_trig_no_targ (RwEnNF2RdEnR: 2 trig 0 targ)"
set ne [get_list $r measure_names]
assert {[llength $ne] == 3} "E measure_names count"
assert {[lindex $ne 0] eq "RwEnNF2RdEnR_Sec28Mat0"} "E name0"
assert {[lindex $ne 1] eq "reennf2rdenr_r1_Sec28Mat0"} "E name1 (2-token bodiless header name)"
assert {[lindex $ne 2] eq "YsaEnPls_Sec28Mat0"} "E name2"
incr pass

# ---------- SCRIPT F: numeric quoted levels + format robustness ----------
# Real shape (sanitized): both levels are NUMERIC literals '0.625'/'0.375'
# (NOT param expressions), with double-space before the quote, a leading
# comment, and trailing whitespace on the trig line. Teeth: a parser that
# flags ANY quoted level as a param-expression (without a numeric check)
# reports measures_with_quoted_param_level==1 instead of 0; a parser that
# splits on single-space only breaks on the double space.
set scriptF {*leading comment
.param pvcc = 0.75v
.meas tran NumLvlMeas
+trig v(top.x) =  '0.625'   td=800n   rise=1   
+targ v(top.y) =  '0.375'   td=800n   fall=1}

set r [$candidate $scriptF]
assert {[get_int $r param_count] == 1} "F param_count"
assert {[get_int $r measure_count] == 1} "F measure_count"
assert {[get_int $r mode_trig_targ] == 1} "F mode_trig_targ"
assert {[get_int $r measures_with_quoted_param_level] == 0} "F measures_with_quoted_param_level (numeric literals are NOT param-expr)"
assert {[get_int $r has_differential] == 0} "F has_differential"
assert {[get_int $r has_td_reference] == 0} "F has_td_reference"
set nf [get_list $r measure_names]
assert {[lindex $nf 0] eq "NumLvlMeas"} "F measure_names_0 (double-space/tab robust)"
incr pass

return "PASS $pass / FAIL $fail (6 cases: A trig/targ-param-level, B when-tab, C find/diff, D param+tdref+diff, E dual-trig+bodiless+comments, F numeric-level teeth)"
}
