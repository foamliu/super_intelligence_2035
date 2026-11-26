# reference implementation for def_net_connectivity_audit
proc def_net_connectivity_audit {nets_text specialnets_text} {
    # --- parse SPECIALNETS names ---
    set special_names {}
    foreach line [split $specialnets_text "\n"] {
        set line [string trim $line]
        if {[string match "- *" $line]} {
            set nm [lindex [split [string range $line 2 end]] 0]
            if {$nm ne ""} { lappend special_names $nm }
        }
    }
    set power_re {^(VDD|VSS|GND|VCC|VEE)$}

    set total_nets 0
    set power_nets {}
    set single_pin_signal {}
    set unconnected_signal {}
    set connected_count 0
    set duplicate_connections 0

    set cur_name ""
    set cur_use ""
    set cur_conns {}
    set cur_raw 0
    set in_block 0

    foreach line [split $nets_text "\n"] {
        set line [string trim $line]
        if {$line eq ""} continue
        if {[string match "- *" $line]} {
            set rest [split [string range $line 2 end]]
            set cur_name [lindex $rest 0]
            set cur_use ""
            set use_idx [lsearch -exact $rest "USE"]
            if {$use_idx >= 0 && $use_idx + 1 < [llength $rest]} {
                set cur_use [lindex $rest [expr {$use_idx + 1}]]
            }
            set cur_conns {}
            set cur_raw 0
            set in_block 1
        } elseif {[string match "( *" $line] && $in_block} {
            set inner [string range $line 1 end]
            set inner [string trim $inner]
            set inner [string trim $inner "()"]
            set inner [string trim $inner]
            set inst [lindex $inner 0]
            set pin [lindex $inner 1]
            if {$inst ne ""} {
                lappend cur_conns "$inst $pin"
                incr cur_raw
            }
        } elseif {$line eq ";" && $in_block} {
            incr total_nets
            # unique connections
            set seen {}
            set uniq 0
            foreach c $cur_conns {
                if {$c ni $seen} { lappend seen $c; incr uniq }
            }
            incr duplicate_connections [expr {$cur_raw - $uniq}]
            # power classification (precedence: special > USE > pattern)
            set is_power 0
            if {$cur_name in $special_names} {
                set is_power 1
            } elseif {$cur_use eq "POWER" || $cur_use eq "GROUND"} {
                set is_power 1
            } elseif {$cur_use eq "" && [regexp $power_re $cur_name]} {
                set is_power 1
            }
            if {$is_power} {
                if {$cur_name ni $power_nets} { lappend power_nets $cur_name }
            } else {
                if {$uniq >= 2} {
                    incr connected_count
                } elseif {$uniq == 1} {
                    lappend single_pin_signal $cur_name
                } else {
                    lappend unconnected_signal $cur_name
                }
            }
            set cur_name ""; set cur_use ""; set cur_conns {}; set cur_raw 0
            set in_block 0
        }
    }

    set signal_nets_count [expr {$total_nets - [llength $power_nets]}]
    set single_pin_signal [lsort $single_pin_signal]
    set unconnected_signal [lsort $unconnected_signal]
    set power_nets [lsort $power_nets]
    set verdict "clean"
    if {[llength $single_pin_signal] > 0 || [llength $unconnected_signal] > 0} {
        set verdict "dangling"
    }
    return [dict create total_nets $total_nets power_nets $power_nets \
        signal_nets_count $signal_nets_count connected_count $connected_count \
        single_pin_signal $single_pin_signal unconnected_signal $unconnected_signal \
        duplicate_connections $duplicate_connections verdict $verdict]
}
