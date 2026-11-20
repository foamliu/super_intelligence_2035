# Single-param check(candidate) -- framework injects wrapper that calls
# `check xa_log_diagnose` and captures the return value / exception as the
# DESIGN_FLOW_VERDICT. Helper procs defined inside become global in Tcl.
proc check {candidate} {
# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
# tolerant string extractor for the returned flat dict string
proc get_str {dictstr key} {
    set re [format {^%s[[:space:]]+(\S+)} $key]
    if {![regexp -line -- $re $dictstr -> v]} {
        set re2 [format {[[:space:]]%s[[:space:]]+(\S+)} $key]
        if {![regexp -- $re2 $dictstr -> v]} { error "get_str: key $key not found in dict" }
    }
    return $v
}
proc get_int {dictstr key} {
    set v [get_str $dictstr $key]
    return [expr {int($v)}]
}

proc _write_xa_log {path lines} {
    set fo [open $path w]
    foreach ln $lines { puts $fo $ln }
    close $fo
}

# ---------- LOG A: failure, BSIM-CMG version unsupported (old CustomSim) ----------
# Real shape (sanitized) from CCK_include_rshort1M_1016 xa.log: old CustomSim
# banner, CMI warning table declares BSIM-CMG 111.2 unsupported, downstream
# "Unable to create mosfet with CMI" Error: lines, XA failed.
set logA [list \
    {CustomSim XA linux64 P-2019.06-SP1-BETA-20190515 (built May 15 2019 14:22:03)} \
    {Command line: xa -mt 8 -o xa_results/CCK_inc_1016 -c config/xa_conly} \
    {opening model_setup_fs.lib} \
    {loading nsvt_3_fs.mdl} \
    {loading psvt_fs.mdl} \
    {Warnings/Messages from CMI:} \
    {(psvt_fs:xi0.mpm3.m1)**warning**: Version = 111.2 in BSIM-CMG model is not supported. Reset it to version = 110} \
    {(nsvt_fs:xi0.mnm3.m1)**warning**: Version = 111.2 in BSIM-CMG model is not supported. Reset it to version = 110} \
    {Error: (model_setup_fs.lib:465) model error for xtop.xbio.mnm3.m1, model nsvt_fs.8 (nsvt_3_fs.mdl:1415): Unable to create mosfet with CMI.} \
    {Error: (model_setup_fs.lib:465) model error for xtop.xbio.mpm3.m1, model psvt_fs.8 (psvt_fs.mdl:1119): Unable to create mosfet with CMI.} \
    {Error: (model_setup_fs.lib:465) model error for xtop.xbio.mnm3.m2, model nsvt_fs.8 (nsvt_3_fs.mdl:1415): Unable to create mosfet with CMI.} \
    {XA failed (Fri Oct 16 10:34:21 2026).} \
]
_write_xa_log _xa_A.log $logA

# ---------- LOG B: success (new PrimeSim XA) ----------
set logB [list \
    {PrimeSim XA linux64 V-2023.12 (built Nov 24 2023 06:12:45)} \
    {Command line: xa -mt 1 -o xa_results/CCK_inc_1009 -c config/xa_conly_cck} \
    {opening model_setup_fs.lib} \
    {loading nsvt_3_fs.mdl} \
    {loading psvt_fs.mdl} \
    {setting up BSIM-CMG version 111.2 (supported)} \
    {transient analysis 0 to 100n} \
    {writing xa.fsdb} \
    {XA done (Fri Oct 09 10:14:13 2026).} \
]
_write_xa_log _xa_B.log $logB

# ---------- LOG C: convergence failure (no CMI version warning) ----------
set logC [list \
    {PrimeSim XA linux64 V-2023.12 (built Nov 24 2023 06:12:45)} \
    {Command line: xa -mt 4 -o xa_results/amp_1020 -c config/amp_tran} \
    {opening model_setup_fs.lib} \
    {loading nch_mac.mdl} \
    {loading pch_mac.mdl} \
    {transient analysis 0 to 50n} \
    {Error: time step too small in transient at time 1.234e-09} \
    {Error: transient convergence failed at node net14 at time 1.234e-09} \
    {Error: time step too small in transient at time 1.235e-09} \
    {XA failed (Tue Oct 20 15:22:01 2026).} \
]
_write_xa_log _xa_C.log $logC

# ---------- LOG D: missing model failure (no CMI version warning) ----------
set logD [list \
    {CustomSim XA linux64 P-2019.06-SP1-BETA-20190515 (built May 15 2019 14:22:03)} \
    {Command line: xa -mt 2 -o xa_results/inv_1021 -c config/inv_dc} \
    {opening model_setup_fs.lib} \
    {Error: model nch_mac not found in library} \
    {Error: cannot find model pch_mac in any referenced library} \
    {XA failed (Wed Oct 21 09:11:00 2026).} \
]
_write_xa_log _xa_D.log $logD

# ---------- LOG E: TEETH -- mixed CMI warning + convergence errors ----------
# The BSIM-CMG-unsupported warning is present AND there are "time step too
# small" convergence errors. model_version_unsupported MUST take precedence
# over convergence. A naive impl that classifies by "first error type seen"
# or "convergence keyword present" (without parsing CMI) returns convergence
# (or unknown) and FAILS.
set logE [list \
    {CustomSim XA linux64 P-2019.06-SP1-BETA-20190515 (built May 15 2019 14:22:03)} \
    {Command line: xa -mt 8 -o xa_results/mix_1022 -c config/mix} \
    {opening model_setup_fs.lib} \
    {Warnings/Messages from CMI:} \
    {(nsvt_fs:xi0.mnm3.m1)**warning**: Version = 111.2 in BSIM-CMG model is not supported. Reset it to version = 110} \
    {Error: time step too small in transient at time 5.0e-09} \
    {Error: (model_setup_fs.lib:465) model error for xtop.mnm3.m1, model nsvt_fs.8: Unable to create mosfet with CMI.} \
    {XA failed (Sat Oct 22 11:00:00 2026).} \
]
_write_xa_log _xa_E.log $logE

# ---------- run candidate on each log + assert ----------
set pass 0
set fail 0

# --- Case A: BSIM-CMG unsupported failure ---
set r [$candidate _xa_A.log]
assert {[get_str $r xa_tool_name] eq "CustomSim"} "A xa_tool_name"
assert {[get_str $r xa_version] eq "P-2019.06-SP1-BETA-20190515"} "A xa_version"
assert {[get_str $r final_status] eq "failed"} "A final_status"
assert {[get_int $r total_lines] == 12} "A total_lines"
assert {[get_int $r error_line_count] == 3} "A error_line_count"
assert {[get_str $r cmi_unsupported_version] eq "111.2"} "A cmi_unsupported_version"
assert {[get_str $r version_reset_to] eq "110"} "A version_reset_to"
assert {[get_int $r unsupported_model_version] == 1} "A unsupported_model_version"
assert {[get_str $r root_cause] eq "model_version_unsupported"} "A root_cause"
incr pass

# --- Case B: success ---
set r [$candidate _xa_B.log]
assert {[get_str $r xa_tool_name] eq "PrimeSim"} "B xa_tool_name"
assert {[get_str $r xa_version] eq "V-2023.12"} "B xa_version"
assert {[get_str $r final_status] eq "done"} "B final_status"
assert {[get_int $r total_lines] == 9} "B total_lines"
assert {[get_int $r error_line_count] == 0} "B error_line_count"
assert {[get_str $r cmi_unsupported_version] eq "none"} "B cmi_unsupported_version"
assert {[get_str $r version_reset_to] eq "none"} "B version_reset_to"
assert {[get_int $r unsupported_model_version] == 0} "B unsupported_model_version"
assert {[get_str $r root_cause] eq "success"} "B root_cause"
incr pass

# --- Case C: convergence failure ---
set r [$candidate _xa_C.log]
assert {[get_str $r final_status] eq "failed"} "C final_status"
assert {[get_int $r total_lines] == 10} "C total_lines"
assert {[get_int $r error_line_count] == 3} "C error_line_count"
assert {[get_str $r cmi_unsupported_version] eq "none"} "C cmi_unsupported_version"
assert {[get_str $r version_reset_to] eq "none"} "C version_reset_to"
assert {[get_int $r unsupported_model_version] == 0} "C unsupported_model_version"
assert {[get_str $r root_cause] eq "convergence"} "C root_cause"
incr pass

# --- Case D: missing model failure ---
set r [$candidate _xa_D.log]
assert {[get_str $r final_status] eq "failed"} "D final_status"
assert {[get_int $r total_lines] == 6} "D total_lines"
assert {[get_int $r error_line_count] == 2} "D error_line_count"
assert {[get_str $r cmi_unsupported_version] eq "none"} "D cmi_unsupported_version"
assert {[get_int $r unsupported_model_version] == 0} "D unsupported_model_version"
assert {[get_str $r root_cause] eq "missing_model"} "D root_cause"
incr pass

# --- Case E: TEETH -- precedence model_version_unsupported > convergence ---
set r [$candidate _xa_E.log]
assert {[get_str $r final_status] eq "failed"} "E final_status"
assert {[get_int $r total_lines] == 8} "E total_lines"
assert {[get_int $r error_line_count] == 2} "E error_line_count"
assert {[get_str $r cmi_unsupported_version] eq "111.2"} "E cmi_unsupported_version"
assert {[get_str $r version_reset_to] eq "110"} "E version_reset_to"
assert {[get_int $r unsupported_model_version] == 1} "E unsupported_model_version"
assert {[get_str $r root_cause] eq "model_version_unsupported"} "E root_cause (precedence over convergence)"
incr pass

return "PASS $pass / FAIL $fail (5 cases: A BSIM-CMG-unsupported, B success, C convergence, D missing_model, E precedence-teeth)"
}


# framework-style wrapper: capture verdict
set err ""
if {[catch {check xa_log_diagnose} verdict]} { set err $verdict; set verdict "" }
if {$err eq ""} { puts "DESIGN_FLOW_VERDICT=PASS"; puts "DETAIL=$verdict" } else { puts "DESIGN_FLOW_VERDICT=FAIL"; puts "DETAIL=$err" }
