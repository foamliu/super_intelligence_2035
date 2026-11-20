# Naive impl: only checks "contains module load ds/pt + pt_shell -f -x" -> says ok.
# Misses the csh -f module-bootstrap trap (R1), order (R1), and preset vars (R4).
proc pnr_signoff_audit_pt_launcher {launcher} {
    set hLP 0; set hPX 0
    foreach ln [split $launcher "\n"] {
        if {[regexp {module[[:space:]]+load[[:space:]]+ds/pt/} $ln]} { set hLP 1 }
        if {[regexp {pt_shell} $ln] && [regexp -- {-f[[:space:]]} $ln] && [regexp -- {-x[[:space:]]} $ln]} { set hPX 1 }
    }
    set v "ok"; set r "none"
    if {!$hLP || !$hPX} { set v "broken"; set r "" }
    if {!$hLP} { set r "R2" }
    if {!$hPX} { set r [expr {$hLP?"R3":"R2;R3"}] }
    return [dict create shebang_csh_f 1 has_module_bootstrap 1 \
        bootstrap_before_first_module_call 1 has_module_load_pt $hLP \
        has_pt_shell_x_preset $hPX x_preset_has_design_corner_mode 1 \
        has_run_tag_suffix 1 verdict $v fail_reasons $r]
}
