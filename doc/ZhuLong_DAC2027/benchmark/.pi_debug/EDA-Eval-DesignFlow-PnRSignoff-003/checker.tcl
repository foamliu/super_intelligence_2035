# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}

proc check {candidate} {
    # Fixtures use @D@ for '$' and @B@ for backtick so they can sit inside Tcl
    # braces (the real launchers carry $vars and ${braces} and backticks).
    # dch/btk are global so the mk helper (own scope) can read them.
    set ::dch [format %c 36]
    set ::btk [format %c 96]
    proc mk {tmpl} {string map [list @D@ $::dch @B@ $::btk] $tmpl}

    # ---- Case A: csh -f, module purge/load, NO bootstrap -> BROKEN (R1).
    # The real mined trap. A validator that only checks "has module load ds/pt"
    # says OK -> wrong.
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

    # ---- Case B: csh -f, alias module ... BEFORE module purge -> OK.
    # The real fix from the session.
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

    # ---- Case C: csh -f, bootstrap via `source .../modules.csh` -> OK.
    # Proves the alternative bootstrap form is recognised.
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

    # ---- Case D: csh -f, bootstrap AFTER module purge (wrong order) -> BROKEN (R1).
    # Order teeth: a validator that checks bootstrap presence but not order says OK.
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

    # ---- Case E: #!/bin/bash, module load (no bootstrap) -> OK.
    # bash teeth: bash inherits the module function from .bashrc, so no
    # bootstrap is required. A validator that demands a bootstrap for EVERY
    # launcher says BROKEN -> wrong.
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

    # ---- Case F: csh -f, bootstrap ok, but -x preset omits set MODE -> BROKEN (R4).
    # x-preset teeth: the corner/mode never reach common_setup.tcl, so the run
    # uses the DEFAULT corner -- a silent wrong-corner STA run.
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


# --- run the check and emit a verdict line ---
setchk [catch {check pnr_signoff_audit_pt_launcher} chkmsg]
if {$setchk == 0} {
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
