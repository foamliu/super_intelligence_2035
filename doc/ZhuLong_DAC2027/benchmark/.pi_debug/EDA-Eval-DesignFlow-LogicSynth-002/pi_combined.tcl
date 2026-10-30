proc logicsynth_wlm_multibit_plan {log_summary} {
    set d [dict create {*}$log_summary]
    set mb_lib_loaded [dict get $d mb_lib_loaded]
    set has_spg [dict get $d has_spg]
    set banking_gated_behind_topo [dict get $d banking_gated_behind_topo]
    set num_mb_ff [dict get $d num_mb_ff]

    if {[string equal $mb_lib_loaded "0"]} {
        set root_cause "multibit library not loaded: WLM synthesis cannot infer multibit banks"
        set wlm_can_merge "0"
        set enable_script ""
    } elseif {[string equal $has_spg "1"]} {
        set root_cause "topographical mode active (has_spg=1): WLM multibit banking not applicable"
        set wlm_can_merge "0"
        set enable_script ""
    } elseif {[string equal $mb_lib_loaded "1"] && [string equal $has_spg "0"] && [string equal $banking_gated_behind_topo "1"] && [string equal $num_mb_ff "0"]} {
        set root_cause "placement-aware banking skipped: identify_register_banks is gated behind topographical mode in the WLM run, so no MB FF were created even though the MB library is loaded"
        set wlm_can_merge "1"
        set enable_script "hdlin_infer_multibit\nset_multibit_options\ncompile_ultra\nreport_multibit_banking"
    } else {
        set root_cause "unhandled WLM multibit scenario"
        set wlm_can_merge "0"
        set enable_script ""
    }

    return [dict create root_cause $root_cause wlm_can_merge $wlm_can_merge enable_script $enable_script expected_mb_widths "2 4" needs_topo_for_wide_bus "1"]
}


# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc contains {haystack needle} { return [expr {[string first $needle $haystack] >= 0}] }
proc notcontains {haystack needle} { return [expr {[string first $needle $haystack] < 0}] }

proc check {candidate} {
    # Case A: REAL session -- WLM, MB loaded, topo-gated banking skipped -> 0%
    set sumA "mb_lib_loaded 1 has_spg 0 banking_gated_behind_topo 1 num_candidate_banks 1128 num_single_bit_ff 15307 num_mb_ff 0 banking_pct 0.0 compile_cmd {compile_ultra -gate_clock -scan}"
    set dA [$candidate $sumA]
    set rcA [dict get $dA root_cause]
    set esA [dict get $dA enable_script]
    set wmA [dict get $dA wlm_can_merge]
    set ewA [dict get $dA expected_mb_widths]
    set ntA [dict get $dA needs_topo_for_wide_bus]
    assert {[string length $rcA] > 0} "A: root_cause empty"
    assert {[contains $rcA "topographical"]} "A: root_cause must mention topographical mode (real cause)"
    assert {[contains $rcA "identify_register_banks"]} "A: root_cause must mention identify_register_banks"
    assert {[notcontains $rcA "not loaded"]} "A: root_cause must NOT claim library not loaded (it IS loaded)"
    assert {[notcontains $rcA "missing"]} "A: root_cause must NOT claim library missing"
    assert {[string equal $wmA "1"]} "A: wlm_can_merge must be 1 (MB loaded + WLM)"
    assert {[string equal $ewA "2 4"]} "A: expected_mb_widths must be 2 4"
    assert {[string equal $ntA "1"]} "A: needs_topo_for_wide_bus must be 1"
    assert {[contains $esA "hdlin_infer_multibit"]} "A: enable_script must set hdlin_infer_multibit"
    assert {[contains $esA "set_multibit_options"]} "A: enable_script must set set_multibit_options"
    assert {[contains $esA "compile_ultra"]} "A: enable_script must run compile_ultra"
    assert {[contains $esA "report_multibit_banking"]} "A: enable_script must report_multibit_banking"
    assert {[notcontains $esA "identify_register_banks"]} "A: WLM enable_script must NOT use identify_register_banks (topo-only)"
    assert {[notcontains $esA "-spg"]} "A: WLM enable_script must NOT use -spg (topo-only flag)"

    # Case B: counter -- MB library NOT loaded -> must say library not loaded
    set sumB "mb_lib_loaded 0 has_spg 0 banking_gated_behind_topo 1 num_candidate_banks 0 num_single_bit_ff 5000 num_mb_ff 0 banking_pct 0.0 compile_cmd {compile_ultra -gate_clock -scan}"
    set dB [$candidate $sumB]
    set rcB [dict get $dB root_cause]
    set wmB [dict get $dB wlm_can_merge]
    assert {[contains $rcB "library"]} "B: root_cause must mention library"
    assert {[contains $rcB "not loaded"]} "B: root_cause must say library not loaded"
    assert {[string equal $wmB "0"]} "B: wlm_can_merge must be 0 (MB not loaded)"

    # Case C: topo mode (has_spg==1) -> identify_register_banks available, not WLM
    set sumC "mb_lib_loaded 1 has_spg 1 banking_gated_behind_topo 1 num_candidate_banks 100 num_single_bit_ff 8000 num_mb_ff 0 banking_pct 0.0 compile_cmd {compile_ultra -gate_clock -scan -spg}"
    set dC [$candidate $sumC]
    set rcC [dict get $dC root_cause]
    set wmC [dict get $dC wlm_can_merge]
    assert {[contains $rcC "topographical"]} "C: root_cause must mention topographical"
    assert {[string equal $wmC "0"]} "C: wlm_can_merge must be 0 (topo mode, not WLM)"

    return "CHECK_PASS"
}

puts [check logicsynth_wlm_multibit_plan]
