# Single-param check(candidate) -- framework injects a wrapper that calls
# `check wv_parse_ace_batch_output` and captures the return value / exception
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

# ---------- Case A: basic scalar numeric + WVERR + WVINFO + banner/noise ----------
# Real shape (sanitized): two numeric measurements, one failed measurement
# (WVERR), one WVINFO status, plus the wv banner and a license warning that
# MUST be ignored.
set textA [join [list {WaveView CustomViewer T-2022.06-SP1} {WVRES|tb1.fsdb|delay_ps|15.234} {WVRES|tb1.fsdb|idd_ua|82.5} {WVERR|tb1.fsdb|duty_pct|no crossing found} {WVINFO|tb1.fsdb|done} {license -96: cannot connect to server}] "\n"]

set r [$candidate $textA]
assert {[get_int $r wvres_count] == 2} "A wvres_count"
assert {[get_int $r wverr_count] == 1} "A wverr_count"
assert {[get_int $r wvinfo_count] == 1} "A wvinfo_count"
assert {[get_int $r scalar_count] == 2} "A scalar_count"
assert {[get_int $r list_count] == 0} "A list_count"
assert {[get_int $r numeric_scalar_count] == 2} "A numeric_scalar_count"
assert {[get_int $r non_numeric_scalar_count] == 0} "A non_numeric_scalar_count"
assert {[get_int $r total_numeric_elements] == 2} "A total_numeric_elements"
assert {[get_str $r files_seen] eq "tb1.fsdb"} "A files_seen"
assert {[get_str $r failed_keys] eq "duty_pct"} "A failed_keys"
assert {[get_int $r has_list_value] == 0} "A has_list_value"
assert {[get_int $r has_error] == 1} "A has_error"
set ka [get_list $r result_keys]
assert {[llength $ka] == 2} "A result_keys count"
assert {[lindex $ka 0] eq "delay_ps"} "A result_keys_0"
assert {[lindex $ka 1] eq "idd_ua"} "A result_keys_1"
incr pass

# ---------- Case B: comma-list value (edge scan) teeth ----------
# Real shape (sanitized): an edge-scan measurement returns a comma-separated
# list of crossing times. Teeth: a parser that always coerces the value to a
# float CRASHES on the comma-list; a parser that counts every WVRES as a
# scalar reports scalar_count==1 instead of 0 and list_count==0.
set textB [join [list {WVRES|tb2.fsdb|edges|1.5e-9,2.3e-9,4.1e-9} {WVINFO|tb2.fsdb|done}] "\n"]

set r [$candidate $textB]
assert {[get_int $r wvres_count] == 1} "B wvres_count"
assert {[get_int $r scalar_count] == 0} "B scalar_count (comma-list is NOT scalar)"
assert {[get_int $r list_count] == 1} "B list_count"
assert {[get_int $r has_list_value] == 1} "B has_list_value"
assert {[get_int $r total_numeric_elements] == 3} "B total_numeric_elements (3 numeric tokens in list)"
assert {[get_int $r numeric_scalar_count] == 0} "B numeric_scalar_count"
assert {[get_int $r non_numeric_scalar_count] == 0} "B non_numeric_scalar_count"
assert {[get_str $r failed_keys] eq "none"} "B failed_keys"
assert {[get_int $r has_error] == 0} "B has_error"
assert {[lindex [get_list $r result_keys] 0] eq "edges"} "B result_keys_0"
incr pass

# ---------- Case C: non-numeric scalar teeth ----------
# Real shape (sanitized): measurements that returned a sentinel string
# (`failed`, `n/a`) instead of a number. Teeth: a parser that unconditionally
# float-coerces the value CRASHES on `failed`; a parser that counts any
# non-empty value as numeric over-counts numeric_scalar_count.
set textC [join [list {WVRES|tb3.fsdb|gain|failed} {WVRES|tb3.fsdb|bw|n/a} {WVINFO|tb3.fsdb|done}] "\n"]

set r [$candidate $textC]
assert {[get_int $r wvres_count] == 2} "C wvres_count"
assert {[get_int $r scalar_count] == 2} "C scalar_count"
assert {[get_int $r numeric_scalar_count] == 0} "C numeric_scalar_count (non-numeric kept as string)"
assert {[get_int $r non_numeric_scalar_count] == 2} "C non_numeric_scalar_count"
assert {[get_int $r total_numeric_elements] == 0} "C total_numeric_elements (0 numeric)"
assert {[get_int $r has_list_value] == 0} "C has_list_value"
incr pass

# ---------- Case D: WVINFO with pipe-in-msg teeth ----------
# Real shape (sanitized): a WVINFO status message that itself contains a pipe
# (`processing: stage|2`). Teeth: a parser that splits WVINFO with a uniform
# split("|") (no maxsplit) gets 4 parts and, requiring 3, DROPS the line ->
# wvinfo_count==0. The correct parser splits into at most 3 parts (maxsplit 2)
# so the message is preserved and the line is counted.
set textD [join [list {WVRES|tb4.fsdb|delay|12.5} {WVINFO|tb4.fsdb|processing: stage|2}] "\n"]

set r [$candidate $textD]
assert {[get_int $r wvres_count] == 1} "D wvres_count"
assert {[get_int $r wvinfo_count] == 1} "D wvinfo_count (pipe-in-msg preserved via maxsplit=2)"
assert {[get_int $r wverr_count] == 0} "D wverr_count"
incr pass

# ---------- Case E: WVERR with pipe-in-msg teeth ----------
# Real shape (sanitized): a WVERR error message that contains a pipe
# (`invalid signal: top.a|b`). Teeth: a parser that splits WVERR with a
# uniform split("|") (no maxsplit) gets 5 parts and, requiring 4, DROPS the
# line -> wverr_count==0, failed_keys==none, has_error==0. The correct parser
# splits into at most 4 parts (maxsplit 3) so the message is preserved and
# the line is counted. Also: a file that only had an error is still "seen".
set textE [join [list {WVRES|tb5.fsdb|delay|10.0} {WVERR|tb5.fsdb|sig_x|invalid signal: top.a|b} {WVINFO|tb5.fsdb|done}] "\n"]

set r [$candidate $textE]
assert {[get_int $r wvres_count] == 1} "E wvres_count"
assert {[get_int $r wverr_count] == 1} "E wverr_count (pipe-in-msg preserved via maxsplit=3)"
assert {[get_int $r has_error] == 1} "E has_error"
assert {[get_str $r failed_keys] eq "sig_x"} "E failed_keys"
assert {[get_str $r files_seen] eq "tb5.fsdb"} "E files_seen (file with error is seen)"
incr pass

# ---------- Case F: multi-file comprehensive ----------
# Real shape (sanitized): a multi-file batch run with two FSDBs, mixing
# numeric scalars, a comma-list, two errors (one per file), two WVINFO lines
# (one with a pipe in the message), plus a banner, a blank line, and a noise
# line that MUST be ignored. Exercises every key at once.
set textF [join [list {WaveView banner} {WVRES|fa.fsdb|delay|15.0} {WVRES|fa.fsdb|edges|1e-9,2e-9} {WVERR|fa.fsdb|bad|err msg} {WVINFO|fa.fsdb|stage|1} {WVRES|fb.fsdb|tr|3.5e-9} {WVRES|fb.fsdb|tf|4.2e-9} {WVERR|fb.fsdb|missing|no toggle} {WVINFO|fb.fsdb|done} {} {noise line without pipe prefix}] "\n"]

set r [$candidate $textF]
assert {[get_int $r wvres_count] == 4} "F wvres_count"
assert {[get_int $r wverr_count] == 2} "F wverr_count"
assert {[get_int $r wvinfo_count] == 2} "F wvinfo_count"
assert {[get_int $r scalar_count] == 3} "F scalar_count"
assert {[get_int $r list_count] == 1} "F list_count"
assert {[get_int $r numeric_scalar_count] == 3} "F numeric_scalar_count"
assert {[get_int $r total_numeric_elements] == 5} "F total_numeric_elements (3 scalar + 2 list)"
assert {[get_str $r files_seen] eq "fa.fsdb,fb.fsdb"} "F files_seen (2 files comma-joined, first-seen order)"
assert {[get_str $r failed_keys] eq "bad,missing"} "F failed_keys (2 errors in order)"
assert {[get_int $r has_list_value] == 1} "F has_list_value"
assert {[get_int $r has_error] == 1} "F has_error"
set kf [get_list $r result_keys]
assert {[llength $kf] == 4} "F result_keys count"
assert {[lindex $kf 0] eq "delay"} "F rk0"
assert {[lindex $kf 1] eq "edges"} "F rk1"
assert {[lindex $kf 2] eq "tr"} "F rk2"
assert {[lindex $kf 3] eq "tf"} "F rk3"
incr pass

return "PASS $pass / FAIL $fail (6 cases: A basic-scalar+err+info, B comma-list teeth, C non-numeric-scalar teeth, D WVINFO pipe-in-msg teeth, E WVERR pipe-in-msg teeth, F multi-file comprehensive)"
}
