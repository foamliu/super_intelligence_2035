```tcl
proc pnr_signoff_timing_eco_stage_plan {flow_spec} {
    set num_steps      [dict get $flow_spec num_steps]
    set steps          [dict get $flow_spec steps]
    set stages         [dict get $flow_spec stages]
    set eco_step       [dict get $flow_spec eco_step_idx]
    set resignoff_step [dict get $flow_spec resignoff_step_idx]

    set stage_runs [dict create]
    foreach stage $stages {
        set run_steps [list]
        for {set i 1} {$i <= $num_steps} {incr i} {
            set run 1
            # apply-ECO step runs ONLY for the "eco" stage
            if {$eco_step ne "" && $i == $eco_step && $stage ne "eco"} {
                set run 0
            }
            # re-signoff step runs for "eco" and "resignoff" stages only
            if {$resignoff_step ne "" && $i == $resignoff_step && $stage ne "eco" && $stage ne "resignoff"} {
                set run 0
            }
            if {$run} {
                lappend run_steps $i
            }
        }
        dict set stage_runs $stage $run_steps
    }

    return [dict create \
        num_steps                $num_steps \
        step_names               $steps \
        stage_runs               $stage_runs \
        resignoff_runs_eco       0 \
        resignoff_netlist_source "patch" \
        eco_patch_strategy       [list buffer_whitelist fixing_margin eco_netlist_handoff] \
        sta_eco_handoff          [list shared_library shared_corner shared_sdc] \
        output_dirs              [list log rpt sdc session patch] \
        run_script_lang          "cshell"]
}
```
