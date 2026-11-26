#===============================================================================
# FILE    : 4_read_netlist.tcl
# PURPOSE : Read the gate-level Verilog netlist(s): top design plus submodules.
#===============================================================================
puts "RM-Info: [info script] : reading gate-level netlist"

if {![info exists DATA_DIR]} { set DATA_DIR [file join $ROOT_DIR data] }

if {![info exists NETLIST_FILES]} {
    set NETLIST_FILES [glob -nocomplain [file join $DATA_DIR "netlist" "*.v"]]
    if {[llength $NETLIST_FILES] == 0} {
        set NETLIST_FILES [glob -nocomplain [file join $DATA_DIR "netlist" "*.vg"]]
    }
}
set NETLIST_FILES [string trim $NETLIST_FILES]
puts "RM-Info: NETLIST_FILES = $NETLIST_FILES"

if {$NETLIST_FILES eq ""} {
    puts "RM-Error: no gate-level netlist found under $DATA_DIR/netlist"
} else {
    foreach vf $NETLIST_FILES {
        puts "RM-Info: read_verilog $vf"
        read_verilog $vf
    }
}

puts "RM-Info: [info script] completed"