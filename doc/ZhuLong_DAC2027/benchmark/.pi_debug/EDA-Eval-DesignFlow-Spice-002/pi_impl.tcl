proc spice_parse_mt0_sram {path} {
    set fh [open $path r]
    set lines [split [read $fh] "\n"]
    close $fh

    # Line 1 ($DATA1) and line 2 (.TITLE) are skipped; line 3 is column names.
    set header_tokens [regexp -all -inline {[^[:space:]]+} [lindex $lines 2]]
    set ncols [llength $header_tokens]

    set c_vdd        [lsearch -exact $header_tokens "vdd"]
    set c_iread_max  [lsearch -exact $header_tokens "iread_max"]
    set c_iread_min  [lsearch -exact $header_tokens "iread_min"]
    set c_iwrite_max [lsearch -exact $header_tokens "iwrite_max"]
    set c_iwrite_min [lsearch -exact $header_tokens "iwrite_min"]
    set c_vq_peak    [lsearch -exact $header_tokens "vq_peak"]
    set c_vq_end     [lsearch -exact $header_tokens "vq_end"]

    set result {}
    set np 0
    set max_iread_ua 0.0
    set max_iwrite_ua 0.0
    set prev_iread 0.0
    set prev_iwrite 0.0
    set iread_monotonic 1
    set iwrite_monotonic 1

    for {set idx 3} {$idx < [llength $lines]} {incr idx} {
        set line [lindex $lines $idx]
        set tokens [regexp -all -inline {[^[:space:]]+} $line]
        if {[llength $tokens] < $ncols} {
            continue
        }

        set vdd        [lindex $tokens $c_vdd]
        set iread_max  [lindex $tokens $c_iread_max]
        set iread_min  [lindex $tokens $c_iread_min]
        set iwrite_max [lindex $tokens $c_iwrite_max]
        set iwrite_min [lindex $tokens $c_iwrite_min]
        set vq_peak    [lindex $tokens $c_vq_peak]
        set vq_end     [lindex $tokens $c_vq_end]

        set a_iread_max  [expr {abs(double($iread_max))}]
        set a_iread_min  [expr {abs(double($iread_min))}]
        set a_iwrite_max [expr {abs(double($iwrite_max))}]
        set a_iwrite_min [expr {abs(double($iwrite_min))}]

        if {$a_iread_max >= $a_iread_min} {
            set iread_ua [expr {$a_iread_max * 1e6}]
        } else {
            set iread_ua [expr {$a_iread_min * 1e6}]
        }

        if {$a_iwrite_max >= $a_iwrite_min} {
            set iwrite_ua [expr {$a_iwrite_max * 1e6}]
        } else {
            set iwrite_ua [expr {$a_iwrite_min * 1e6}]
        }

        set vhalf [expr {double($vdd) / 2.0}]

        if {double($vq_peak) < $vhalf} {
            set read_stable 1
        } else {
            set read_stable 0
        }

        if {double($vq_end) < $vhalf} {
            set write_ok 1
        } else {
            set write_ok 0
        }

        lappend result "p${np}_vdd" $vdd
        lappend result "p${np}_iread_ua" $iread_ua
        lappend result "p${np}_iwrite_ua" $iwrite_ua
        lappend result "p${np}_vq_peak" $vq_peak
        lappend result "p${np}_vq_end" $vq_end
        lappend result "p${np}_read_stable" $read_stable
        lappend result "p${np}_write_ok" $write_ok

        if {$np == 0} {
            set max_iread_ua $iread_ua
            set max_iwrite_ua $iwrite_ua
        } else {
            if {$iread_ua > $max_iread_ua} {
                set max_iread_ua $iread_ua
            }
            if {$iwrite_ua > $max_iwrite_ua} {
                set max_iwrite_ua $iwrite_ua
            }
            if {$iread_ua < $prev_iread} {
                set iread_monotonic 0
            }
            if {$iwrite_ua < $prev_iwrite} {
                set iwrite_monotonic 0
            }
        }

        set prev_iread $iread_ua
        set prev_iwrite $iwrite_ua
        incr np
    }

    lappend result "num_points" $np
    lappend result "max_iread_ua" $max_iread_ua
    lappend result "max_iwrite_ua" $max_iwrite_ua
    lappend result "iread_monotonic" $iread_monotonic
    lappend result "iwrite_monotonic" $iwrite_monotonic

    return [join $result " "]
}
