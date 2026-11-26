proc analog_pex_netlist_audit {inst_path net_path} {
    set instSet {}
    if {[file exists $inst_path]} {
        set fh [open $inst_path r]
        set data [read $fh]
        close $fh
        foreach line [split $data "\n"] {
            set line [string trim $line]
            if {$line eq ""} { continue }
            dict set instSet $line 1
        }
    }

    set pexType {}
    if {[file exists $net_path]} {
        set fh [open $net_path r]
        set data [read $fh]
        close $fh
        foreach line [split $data "\n"] {
            set line [string trim $line]
            if {$line eq ""} { continue }
            if {[string match "*.cdl.spf" $line]} {
                set cell [string range $line 0 end-8]
                set type cdl_spf
            } elseif {[string match "*.spf_RC" $line]} {
                set cell [string range $line 0 end-7]
                set type spf_rc
            } else {
                continue
            }
            if {![dict exists $pexType $cell]} {
                dict set pexType $cell $type
            }
        }
    }

    set num_inst [dict size $instSet]
    set num_with [dict size $pexType]
    set num_cdl 0
    set num_rc 0
    dict for {cell type} $pexType {
        if {$type eq "cdl_spf"} {
            incr num_cdl
        } else {
            incr num_rc
        }
    }
    set num_no [expr {$num_inst - $num_with}]

    set noPex {}
    dict for {cell _} $instSet {
        if {![dict exists $pexType $cell]} {
            lappend noPex $cell
        }
    }
    set noPexJoined [join [lsort $noPex] " "]

    return [dict create num_inst_cells $num_inst \
        num_with_pex $num_with \
        num_no_pex $num_no \
        num_cdl_spf $num_cdl \
        num_spf_rc $num_rc \
        no_pex_cells $noPexJoined]
}
