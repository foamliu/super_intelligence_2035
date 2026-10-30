proc analog_judge_opamp_ac_lis {path} {
    set f [open $path r]
    set data [read $f]
    close $f

    set lines [split $data "\n"]

    # Collect every .measure result line in file order:
    #   <name>=<value> with name in dc_gain|ugf|ph_ugf|pm|bw3
    set values {}
    foreach line $lines {
        if {[regexp {^[[:space:]]*(dc_gain|ugf|ph_ugf|pm|bw3)[[:space:]]*=[[:space:]]*([^[:space:]]+)} \
                $line -> name val]} {
            lappend values $val
        }
    }

    set num_designs [expr {[llength $values] / 5}]

    set out "num_designs $num_designs"

    for {set i 1} {$i <= $num_designs} {incr i} {
        set base [expr {($i - 1) * 5}]
        set dc [normalize_val [lindex $values [expr {$base + 0}]]]
        set ug [normalize_val [lindex $values [expr {$base + 1}]]]
        set ph [normalize_val [lindex $values [expr {$base + 2}]]]
        set pm [normalize_val [lindex $values [expr {$base + 3}]]]
        set bw [normalize_val [lindex $values [expr {$base + 4}]]]

        set meets 0
        if {$dc ne "failed" && $ug ne "failed" && $pm ne "failed"} {
            if {$dc >= 60 && $ug >= 1e6 && $pm >= 60} {
                set meets 1
            }
        }

        append out " d${i}_dc_gain_db $dc"
        append out " d${i}_ugf_hz $ug"
        append out " d${i}_ph_ugf_deg $ph"
        append out " d${i}_pm_deg $pm"
        append out " d${i}_bw3_hz $bw"
        append out " d${i}_meets_spec $meets"
    }

    return $out
}

proc normalize_val {val} {
    set s [string trim $val]
    if {$s eq "failed"} {
        return "failed"
    }

    if {![regexp {^([+-]?[0-9]*\.?[0-9]+)([[:alpha:]]*)$} $s -> num suf]} {
        return "failed"
    }

    set scale 1.0
    if {$suf eq ""} {
        set scale 1.0
    } elseif {$suf eq "x"} {
        set scale 1e6
    } elseif {$suf eq "k"} {
        set scale 1e3
    } elseif {$suf eq "m"} {
        set scale 1e-3
    } elseif {$suf eq "u"} {
        set scale 1e-6
    } elseif {$suf eq "n"} {
        set scale 1e-9
    } elseif {$suf eq "p"} {
        set scale 1e-12
    } elseif {$suf eq "f"} {
        set scale 1e-15
    } elseif {$suf eq "a"} {
        set scale 1e-18
    } elseif {$suf eq "t"} {
        set scale 1e12
    } elseif {$suf eq "g"} {
        set scale 1e9
    } elseif {$suf eq "meg"} {
        set scale 1e6
    } else {
        return "failed"
    }

    return [expr {$num * $scale}]
}