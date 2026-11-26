# Reference implementation for EDA-Eval-DesignFlow-Sch-002
# Task: parse emy2netlist export headers (* Library / * Cell / * View) from a
# SPICE netlist, cross-reference a requested cell list, emit <Library> <Cell>
# pairs for schematic-view cellviews, with state-machine library scoping,
# (library,cell) dedup, unmapped + multi-library reporting.
# Runtime: Tcl on Synopsys WaveView (host=waveview). Pure Tcl builtins.

proc _sn2_hdr {body kw} {
    # If $body starts with keyword $kw followed by optional spaces then ':',
    # return the trimmed value after ':'; else return "".
    set n [string length $kw]
    if {[string length $body] < $n} { return "" }
    if {[string range $body 0 [expr {$n - 1}]] ne $kw} { return "" }
    set rest [string range $body $n end]
    set rest [string trimleft $rest]
    if {[string index $rest 0] ne ":"} { return "" }
    return [string trim [string range $rest 1 end]]
}

proc netlist_lib_cell_map {cell_list netlist} {
    # ---- parse cell_list: unique requested cells, first-occurrence order ----
    set requested {}
    array set req {}
    foreach raw [split $cell_list "\n"] {
        set line [string trim $raw]
        if {$line eq "" || [string index $line 0] ne "*"} continue
        set body [string trim [string range $line 1 end]]
        set cl [_sn2_hdr $body "Cell"]
        if {$cl eq ""} continue
        if {![info exists req($cl)]} {
            set req($cl) 1
            lappend requested $cl
        }
    }
    set total_requested [llength $requested]

    # ---- scan netlist: state machine cur_lib / cur_cell; emit on View schematic ----
    set pairs {}
    array set seen {}
    array set cellLibs {}
    set cur_lib ""
    set cur_cell ""
    foreach raw [split $netlist "\n"] {
        set line [string trim $raw]
        if {$line eq "" || [string index $line 0] ne "*"} continue
        set body [string trim [string range $line 1 end]]
        set lib [_sn2_hdr $body "Library"]
        if {$lib ne ""} { set cur_lib $lib; continue }
        set cl [_sn2_hdr $body "Cell"]
        if {$cl ne ""} { set cur_cell $cl; continue }
        set vw [_sn2_hdr $body "View"]
        if {$vw eq ""} continue
        if {$vw ne "schematic"} continue
        if {$cur_cell eq "" || $cur_lib eq ""} continue
        if {![info exists req($cur_cell)]} continue
        set key "$cur_lib|$cur_cell"
        if {[info exists seen($key)]} continue
        set seen($key) 1
        lappend pairs "$cur_lib $cur_cell"
        if {![info exists cellLibs($cur_cell)]} {
            set cellLibs($cur_cell) [list $cur_lib]
        } else {
            set found 0
            foreach L $cellLibs($cur_cell) {
                if {$L eq $cur_lib} { set found 1; break }
            }
            if {!$found} { lappend cellLibs($cur_cell) $cur_lib }
        }
    }

    set mapped_count [llength $pairs]

    # ---- unmapped + multi_lib over requested (preserve requested order) ----
    set unmapped {}
    set multi {}
    foreach c $requested {
        if {![info exists cellLibs($c)]} {
            lappend unmapped $c
        } elseif {[llength $cellLibs($c)] > 1} {
            lappend multi $c
        }
    }
    set unmapped_count [llength $unmapped]
    if {$unmapped_count == 0} {
        set verdict "complete"
    } else {
        set verdict "incomplete"
    }

    return [dict create \
        pairs            $pairs \
        mapped_count     $mapped_count \
        unmapped         $unmapped \
        unmapped_count   $unmapped_count \
        total_cell_list  $total_requested \
        multi_lib_cells  $multi \
        verdict          $verdict]
}
