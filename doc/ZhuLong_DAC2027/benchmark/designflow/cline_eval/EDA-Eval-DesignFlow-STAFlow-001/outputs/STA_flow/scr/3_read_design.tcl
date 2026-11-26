###############################################################################
# 3_read_design.tcl -- 读入网表(netlist) 并 link 顶层设计
###############################################################################
puts "RM-Info: 3_read_design: reading netlist ..."

set _netlists $NETLIST_FILES
if {[string length $_netlists] == 0} {
    set _netlists [sta_find_files $DATA_DIR {*.v *.vg *.v.gz *.vg.gz}]
}
if {[llength $_netlists] == 0} {
    puts "RM-Error: 3_read_design: no netlist found (NETLIST_FILES empty and data/ empty)."
    if {$sh_continue_on_error} {
        puts "RM-Info:  3_read_design: skipping design read."
    } else {
        exit 1
    }
} else {
    puts "RM-Info: 3_read_design: netlist files = $_netlists"
    foreach _n $_netlists {
        puts "RM-Info: 3_read_design: read_verilog $_n"
        read_verilog $_n
    }

    if {[string length $DESIGN_NAME] == 0} {
        set DESIGN_NAME [get_object_name [current_design]]
    }
    current_design $DESIGN_NAME
    link

    puts "RM-Info: 3_read_design: current_design = [get_object_name [current_design]]"
}