# NAIVE (wrong) impl: first-wins counts, abs deltas, WARNING counted as error,
# strict whitespace (no collapse), last-block-only ERROR lines.
proc lvs_summary_audit {text} {
    set layout_cell ""
    set source_cell ""
    set nl ""; set ns ""; set dl ""; set ds ""; set pl ""; set ps ""
    set err 0; set warn 0
    foreach line [split $text "\n"] {
        set t [string trim $line]
        if {$t eq ""} continue
        if {[regexp {^ERROR:\s*} $t]}      { incr err; continue }
        if {[regexp {^WARNING:\s*} $t]}    { incr err; continue ;# WRONG: count warning as error }
        if {[regexp {^# of NETS in layout = (-?\d+)$} $t -> v]}    { if {$nl eq ""} {set nl $v} ;# first-wins }
        if {[regexp {^# of NETS in source = (-?\d+)$} $t -> v]}   { if {$ns eq ""} {set ns $v} }
        if {[regexp {^# of DEVICES in layout = (-?\d+)$} $t -> v]} { if {$dl eq ""} {set dl $v} }
        if {[regexp {^# of DEVICES in source = (-?\d+)$} $t -> v]} { if {$ds eq ""} {set ds $v} }
        if {[regexp {^# of PORTS in layout = (-?\d+)$} $t -> v]}   { if {$pl eq ""} {set pl $v} }
        if {[regexp {^# of PORTS in source = (-?\d+)$} $t -> v]}   { if {$ps eq ""} {set ps $v} }
        if {[regexp {^LAYOUT CELL NAME = (.*)$} $t -> v]}          { if {$layout_cell eq ""} {set layout_cell [string trim $v]} }
        if {[regexp {^SOURCE CELL NAME = (.*)$} $t -> v]}          { if {$source_cell eq ""} {set source_cell [string trim $v]} }
    }
    set cm [expr {$layout_cell eq $source_cell && $layout_cell ne ""}]
    set nd [expr {abs($nl - $ns)}]   ;# WRONG: abs
    set dd [expr {abs($dl - $ds)}]
    set pd [expr {abs($pl - $ps)}]
    set nm [expr {$nd == 0}]; set dm [expr {$dd == 0}]; set pm [expr {$pd == 0}]
    set v [expr {($nm && $dm && $pm && $cm && $err == 0) ? "clean" : "errors"}]
    return [dict create layout_cell $layout_cell source_cell $source_cell cell_name_match $cm \
        nets_delta $nd devices_delta $dd ports_delta $pd \
        nets_match $nm devices_match $dm ports_match $pm \
        error_lines $err warning_lines $warn lvs_verdict $v]
}
