#===============================================================================
# FILE    : 2_read_constraint.tcl
# PURPOSE : Read timing constraints (SDC) for the selected corner/mode.
#           The SDC is read in before link_design so all clocks / input-output
#           delays / timing exceptions are applied to the linked design.
#===============================================================================
puts "RM-Info: [info script] : reading timing constraints"

if {![info exists DATA_DIR]} { set DATA_DIR [file join $ROOT_DIR data] }

# Determine the SDC file(s). The mode allows a dedicated test/hold SDC directory
# to be picked automatically; otherwise the flat sdc/ directory is used.
if {![info exists CONSTRAINT_FILES]} {
    set CONSTRAINT_FILES ""
    set sdc_search_dirs [list \
        [file join $DATA_DIR "sdc" $PT_MODE] \
        [file join $DATA_DIR "sdc"] ]

    foreach sdir $sdc_search_dirs {
        if {$CONSTRAINT_FILES eq ""} {
            set CONSTRAINT_FILES [glob -nocomplain [file join $sdir "*.sdc"]]
        }
    }
}
set CONSTRAINT_FILES [string trim $CONSTRAINT_FILES]
puts "RM-Info: CONSTRAINT_FILES = $CONSTRAINT_FILES"

if {$CONSTRAINT_FILES eq ""} {
    puts "RM-Warning: no SDC found; the design will be unconstrained"
} else {
    foreach sdc $CONSTRAINT_FILES {
        if {[file exists $sdc]} {
            puts "RM-Info: read_sdc $sdc"
            read_sdc $sdc
        } else {
            puts "RM-Warning: SDC not found: $sdc"
        }
    }
}

# Mode specific extra-constraint handling (kept as extension points).
switch -exact -- $PT_MODE {
    "test" {
        # Typical scan mode: relax/ignore scan-enable & shift timing here.
        puts "RM-Info: PT_MODE=test  -> apply scan-mode timing exceptions"
    }
    "hold" {
        # Hold closure: hold margins are reported in step 8/10.
        puts "RM-Info: PT_MODE=hold  -> hold-corner analysis"
    }
    default {
        puts "RM-Info: PT_MODE=func  -> functional setup/hold analysis"
    }
}

puts "RM-Info: [info script] completed"