proc pnr_signoff_audit_pt_launcher {launcher} {
    set lines [split $launcher "\n"]

    # --- shebang_csh_f: first non-empty line is a csh/tcsh shebang with -f ---
    set shebang_csh_f 0
    foreach raw $lines {
        set s [string trim $raw]
        if {$s eq ""} { continue }
        if {[regexp {^#![[:space:]]*\S*(csh|tcsh)([[:space:]]|$)} $s]} {
            if {[regexp {(^|[[:space:]])-f([[:space:]]|$)} $s]} {
                set shebang_csh_f 1
            }
        }
        break
    }

    set has_module_bootstrap 0
    set has_module_load_pt 0
    set has_pt_shell_x_preset 0
    set module_first_idx -1
    set bootstrap_first_idx -1
    set preset_lines {}
    set has_run_tag 0

    set i 0
    foreach raw $lines {
        set l [string trim $raw]

        # module command calls: purge|load|unload|avail|list
        if {[regexp {^module[[:space:]]+(purge|load|unload|avail|list)([[:space:]]|$)} $l]} {
            if {$module_first_idx < 0} { set module_first_idx $i }
        }
        # PrimeTime module load
        if {[regexp {^module[[:space:]]+load[[:space:]]+ds/pt/} $l]} {
            set has_module_load_pt 1
        }
        # module bootstrap: alias module ... OR source ...modules.csh
        if {[regexp {alias[[:space:]]+module} $l] || [regexp {source[[:space:]]+\S*modules[.]csh} $l]} {
            set has_module_bootstrap 1
            if {$bootstrap_first_idx < 0} { set bootstrap_first_idx $i }
        }
        # pt_shell with both -f and -x
        if {[regexp {pt_shell} $l] && [regexp {(^|[[:space:]])-f([[:space:]]|$)} $l] && [regexp {(^|[[:space:]])-x([[:space:]]|$)} $l]} {
            set has_pt_shell_x_preset 1
        }
        # lines that build/pass the -x preset
        if {[regexp {XVAR} $l] || [regexp {(^|[[:space:]])-x([[:space:]]|$)} $l]} {
            append preset_lines $l "\n"
        }
        # run tag joining DESIGN/CORNER/MODE by _
        if {[string first {${DESIGN}_${CORNER}_${MODE}} $l] >= 0 || [string first {${DESIGN}_${PT_CORNER}_${MODE}} $l] >= 0} {
            set has_run_tag 1
        }

        incr i
    }

    # --- bootstrap_before_first_module_call ---
    set bootstrap_before 1
    if {$module_first_idx >= 0 && $shebang_csh_f == 1} {
        if {$bootstrap_first_idx >= 0 && $bootstrap_first_idx < $module_first_idx} {
            set bootstrap_before 1
        } else {
            set bootstrap_before 0
        }
    }

    # --- x_preset_has_design_corner_mode ---
    set x_preset_has_dcm 0
    if {$has_pt_shell_x_preset == 1} {
        if {[regexp {set[[:space:]]+DESIGN[[:space:]]+\$} $preset_lines] &&
            [regexp {set[[:space:]]+PT_CORNER[[:space:]]+\$} $preset_lines] &&
            [regexp {set[[:space:]]+MODE[[:space:]]+\$} $preset_lines]} {
            set x_preset_has_dcm 1
        }
    }

    # --- critical rules ---
    set reasons {}
    if {$shebang_csh_f == 1 && $module_first_idx >= 0 && !($has_module_bootstrap == 1 && $bootstrap_before == 1)} {
        lappend reasons R1
    }
    if {$has_module_load_pt == 0} { lappend reasons R2 }
    if {$has_pt_shell_x_preset == 0} { lappend reasons R3 }
    if {$has_pt_shell_x_preset == 1 && $x_preset_has_dcm == 0} { lappend reasons R4 }

    if {[llength $reasons] == 0} {
        set verdict "ok"
        set fail_reasons "none"
    } else {
        set verdict "broken"
        set fail_reasons [join $reasons ";"]
    }

    return [dict create \
        shebang_csh_f $shebang_csh_f \
        has_module_bootstrap $has_module_bootstrap \
        bootstrap_before_first_module_call $bootstrap_before \
        has_module_load_pt $has_module_load_pt \
        has_pt_shell_x_preset $has_pt_shell_x_preset \
        x_preset_has_design_corner_mode $x_preset_has_dcm \
        has_run_tag_suffix $has_run_tag \
        verdict $verdict \
        fail_reasons $fail_reasons]
}

# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}

proc check {candidate} {
    set ::dch [format %c 36]
    set ::btk [format %c 96]
    proc mk {tmpl} {string map [list @D@ $::dch @B@ $::btk] $tmpl}

    set fa [mk {
#!/bin/csh -f
# PrimeTime STA launcher (BROKEN: no module bootstrap under csh -f).
set DESIGN  = mac
set CORNER  = tt0p8v25c
set MODE    = func
set RUNDIR  = @B@dirname @D@0@B@
set STA_ROOT = @D@RUNDIR:h
module purge
module load ds/pt/2022.12-SP5
set PTBIN = @B@which pt_shell@B@
set XVAR  = "set STA_ROOT @D@STA_ROOT; set DESIGN @D@DESIGN; set PT_CORNER @D@CORNER;"
set XVAR  = "@D@XVAR set MODE @D@MODE; set LIB_PROFILE tutorial;"
set TAG  = @D@{DESIGN}_@D@{CORNER}_@D@{MODE}
pt_shell -f @D@STA_ROOT/scr/sta_main.tcl -x "@D@XVAR" |& tee @D@LOGF
}]
    set d [$candidate $fa]
    assert {[dict get $d shebang_csh_f] eq "1"} "A shebang_csh_f"
    assert {[dict get $d has_module_bootstrap] eq "0"} "A has_module_bootstrap"
    assert {[dict get $d bootstrap_before_first_module_call] eq "0"} "A bootstrap_before"
    assert {[dict get $d has_module_load_pt] eq "1"} "A has_module_load_pt"
    assert {[dict get $d has_pt_shell_x_preset] eq "1"} "A has_pt_shell_x_preset"
    assert {[dict get $d x_preset_has_design_corner_mode] eq "1"} "A x_preset_vars"
    assert {[dict get $d has_run_tag_suffix] eq "1"} "A has_run_tag_suffix"
    assert {[dict get $d verdict] eq "broken"} "A verdict"
    assert {[dict get $d fail_reasons] eq "R1"} "A fail_reasons"

    set fb [mk {
#!/bin/csh -f
# PrimeTime STA launcher (FIXED: module alias defined before module purge).
set DESIGN  = mac
set CORNER  = tt0p8v25c
set MODE    = func
if (! @D@?TC_INITIALIZED) then
    alias module 'eval /apps/cad/Modules/bin/modulecmd csh !*'
endif
module purge
module load ds/pt/2022.12-SP5
set PTBIN = @B@which pt_shell@B@
set XVAR  = "set STA_ROOT @D@STA_ROOT; set DESIGN @D@DESIGN; set PT_CORNER @D@CORNER;"
set XVAR  = "@D@XVAR set MODE @D@MODE; set LIB_PROFILE tutorial;"
set TAG  = @D@{DESIGN}_@D@{CORNER}_@D@{MODE}
pt_shell -f @D@STA_ROOT/scr/sta_main.tcl -x "@D@XVAR" |& tee @D@LOGF
}]
    set d [$candidate $fb]
    assert {[dict get $d shebang_csh_f] eq "1"} "B shebang_csh_f"
    assert {[dict get $d has_module_bootstrap] eq "1"} "B has_module_bootstrap"
    assert {[dict get $d bootstrap_before_first_module_call] eq "1"} "B bootstrap_before"
    assert {[dict get $d has_module_load_pt] eq "1"} "B has_module_load_pt"
    assert {[dict get $d has_pt_shell_x_preset] eq "1"} "B has_pt_shell_x_preset"
    assert {[dict get $d x_preset_has_design_corner_mode] eq "1"} "B x_preset_vars"
    assert {[dict get $d has_run_tag_suffix] eq "1"} "B has_run_tag_suffix"
    assert {[dict get $d verdict] eq "ok"} "B verdict"
    assert {[dict get $d fail_reasons] eq "none"} "B fail_reasons"

    set fc [mk {
#!/bin/csh -f
# PrimeTime STA launcher (bootstrap via source modules.csh).
source /etc/profile.d/modules.csh
module purge
module load ds/pt/2022.12-SP5
set PTBIN = @B@which pt_shell@B@
set XVAR  = "set STA_ROOT @D@STA_ROOT; set DESIGN @D@DESIGN; set PT_CORNER @D@CORNER; set MODE @D@MODE;"
set TAG  = @D@{DESIGN}_@D@{CORNER}_@D@{MODE}
pt_shell -f @D@STA_ROOT/scr/sta_main.tcl -x "@D@XVAR" |& tee @D@LOGF
}]
    set d [$candidate $fc]
    assert {[dict get $d shebang_csh_f] eq "1"} "C shebang_csh_f"
    assert {[dict get $d has_module_bootstrap] eq "1"} "C has_module_bootstrap"
    assert {[dict get $d bootstrap_before_first_module_call] eq "1"} "C bootstrap_before"
    assert {[dict get $d has_module_load_pt] eq "1"} "C has_module_load_pt"
    assert {[dict get $d has_pt_shell_x_preset] eq "1"} "C has_pt_shell_x_preset"
    assert {[dict get $d x_preset_has_design_corner_mode] eq "1"} "C x_preset_vars"
    assert {[dict get $d verdict] eq "ok"} "C verdict"
    assert {[dict get $d fail_reasons] eq "none"} "C fail_reasons"

    set fd [mk {
#!/bin/csh -f
# PrimeTime STA launcher (WRONG ORDER: module purge before bootstrap).
module purge
alias module 'eval /apps/cad/Modules/bin/modulecmd csh !*'
module load ds/pt/2022.12-SP5
set XVAR  = "set STA_ROOT @D@STA_ROOT; set DESIGN @D@DESIGN; set PT_CORNER @D@CORNER; set MODE @D@MODE;"
set TAG  = @D@{DESIGN}_@D@{CORNER}_@D@{MODE}
pt_shell -f @D@STA_ROOT/scr/sta_main.tcl -x "@D@XVAR" |& tee @D@LOGF
}]
    set d [$candidate $fd]
    assert {[dict get $d shebang_csh_f] eq "1"} "D shebang_csh_f"
    assert {[dict get $d has_module_bootstrap] eq "1"} "D has_module_bootstrap"
    assert {[dict get $d bootstrap_before_first_module_call] eq "0"} "D bootstrap_before"
    assert {[dict get $d has_module_load_pt] eq "1"} "D has_module_load_pt"
    assert {[dict get $d has_pt_shell_x_preset] eq "1"} "D has_pt_shell_x_preset"
    assert {[dict get $d x_preset_has_design_corner_mode] eq "1"} "D x_preset_vars"
    assert {[dict get $d verdict] eq "broken"} "D verdict"
    assert {[dict get $d fail_reasons] eq "R1"} "D fail_reasons"

    set fe [mk {
#!/bin/bash
# PrimeTime STA launcher (bash: module function inherited from .bashrc).
DESIGN=mac
CORNER=tt0p8v25c
MODE=func
module purge
module load ds/pt/2022.12-SP5
XVAR="set STA_ROOT @D@STA_ROOT; set DESIGN @D@DESIGN; set PT_CORNER @D@CORNER; set MODE @D@MODE;"
TAG=@D@{DESIGN}_@D@{CORNER}_@D@{MODE}
pt_shell -f @D@STA_ROOT/scr/sta_main.tcl -x "@D@XVAR" |& tee @D@LOGF
}]
    set d [$candidate $fe]
    assert {[dict get $d shebang_csh_f] eq "0"} "E shebang_csh_f"
    assert {[dict get $d has_module_bootstrap] eq "0"} "E has_module_bootstrap"
    assert {[dict get $d bootstrap_before_first_module_call] eq "1"} "E bootstrap_before"
    assert {[dict get $d has_module_load_pt] eq "1"} "E has_module_load_pt"
    assert {[dict get $d has_pt_shell_x_preset] eq "1"} "E has_pt_shell_x_preset"
    assert {[dict get $d x_preset_has_design_corner_mode] eq "1"} "E x_preset_vars"
    assert {[dict get $d verdict] eq "ok"} "E verdict"
    assert {[dict get $d fail_reasons] eq "none"} "E fail_reasons"

    set ff [mk {
#!/bin/csh -f
# PrimeTime STA launcher (BROKEN: -x preset omits set MODE).
if (! @D@?TC_INITIALIZED) then
    alias module 'eval /apps/cad/Modules/bin/modulecmd csh !*'
endif
module purge
module load ds/pt/2022.12-SP5
set XVAR  = "set STA_ROOT @D@STA_ROOT; set DESIGN @D@DESIGN; set PT_CORNER @D@CORNER;"
set TAG  = @D@{DESIGN}_@D@{CORNER}_@D@{MODE}
pt_shell -f @D@STA_ROOT/scr/sta_main.tcl -x "@D@XVAR" |& tee @D@LOGF
}]
    set d [$candidate $ff]
    assert {[dict get $d shebang_csh_f] eq "1"} "F shebang_csh_f"
    assert {[dict get $d has_module_bootstrap] eq "1"} "F has_module_bootstrap"
    assert {[dict get $d bootstrap_before_first_module_call] eq "1"} "F bootstrap_before"
    assert {[dict get $d has_module_load_pt] eq "1"} "F has_module_load_pt"
    assert {[dict get $d has_pt_shell_x_preset] eq "1"} "F has_pt_shell_x_preset"
    assert {[dict get $d x_preset_has_design_corner_mode] eq "0"} "F x_preset_vars"
    assert {[dict get $d verdict] eq "broken"} "F verdict"
    assert {[dict get $d fail_reasons] eq "R4"} "F fail_reasons"

    return "PASS 6 cases"
}

set chk [catch {check pnr_signoff_audit_pt_launcher} chkmsg]
if {$chk == 0} {
    puts "CHECK_RESULT: $chkmsg"
    if {[string match "PASS *" $chkmsg]} {
        puts "DESIGN_FLOW_VERDICT=PASS"
    } else {
        puts "DESIGN_FLOW_VERDICT=FAIL"
    }
} else {
    puts "CHECK_ERROR: $::errorInfo"
    puts "DESIGN_FLOW_VERDICT=FAIL"
}