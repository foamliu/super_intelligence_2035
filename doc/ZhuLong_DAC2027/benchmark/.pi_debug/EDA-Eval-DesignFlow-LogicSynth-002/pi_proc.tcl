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
