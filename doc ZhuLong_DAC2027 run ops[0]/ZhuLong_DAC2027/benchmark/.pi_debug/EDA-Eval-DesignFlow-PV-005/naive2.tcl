# NAIVE2: fixes WARNING-as-error, but keeps first-wins counts, abs deltas,
# strict whitespace (no collapse), last-block-only ERROR lines.
proc lvs_summary_audit {text} {
    set layout_cell ""
    set source_cell ""
    set nl ""; set ns ""; set dl ""; set ds ""; set pl ""; set ps ""
    set err 0; set warn 0
    set last_block_err 0
    set in_block 0
    foreach line [split $text "\n"] {
        set t [string trim $line]
        if {$t eq ""} { continue }
        if {[regexp {^ERROR:\s*} $t]}      { incr err; incr last_block_err; continue }
        if {[regexp {^WARNING:\s*} $t]}    { incr warn; continue }
        if {[regexp {^# of NETS in layout = (-?\d+)$} $t -> v]}    { if {$nl eq ""} {set nl $v} }
        if {[regexp {^# of NETS in source = (-?\d+)$} $t -> v]}   { if {$ns eq ""} {set ns $v} }
        if {[regexp {^# of DEVICES in layout = (-?\d+)$} $t -> v]} { if {$dl eq ""} {set dl $v} }
        if {[regexp {^# of DEVICES in source = (-?\d+)$} $t -> v]} { if {$ds eq ""} {set ds $v} }
        if {[regexp {^# of PORTS in layout = (-?\d+)$} $t -> v]}   { if {$pl eq ""} {set pl $v} }
        if {[regexp {^# of PORTS in source = (-?\d+)$} $t -> v]}   { if {$ps eq ""} {set ps $v} }
        if {[regexp {^LAYOUT CELL NAME = (.*)$} $t -> v]}          { if {$layout_cell eq ""} {set layout_cell [string trim $v]} }
        if {[regexp {^SOURCE CELL NAME = (.*)$} $t -> v]}          { if {$source_cell eq ""} {set source_cell [string trim $v]} }
    }
    # WRONG: use only last block's errors -- emulate by counting errors after
    # the last blank line. Simpler: just trust $err for accumulation test
    # mismatch -- here we deliberately use last-block-only.
    # For the test we approximate: keep $err = total (so accumulation tooth
    # won't bite via this var). Instead we make first-wins + abs + strict
    # whitespace bite. To make last-block-only bite we'd need block tracking.
    set cm [expr {$layout_cell eq $source_cell && $layout_cell ne ""}]
    set nd [expr {abs($nl - $ns)}]
    set dd [expr {abs($dl - $ds)}]
    set pd [expr {abs($pl - $ps)}]
    set nm [expr {$nd == 0}]; set dm [expr {$dd == 0}]; set pm [expr {$pd == 0}]
    set v [expr {($nm && $dm && $pm && $cm && $err == 0) ? "clean" : "errors"}]
    return [dict create layout_cell $layout_cell source_cell $source_cell cell_name_match $cm \
        nets_delta $nd devices_delta $dd ports_delta $pd \
        nets_match $nm devices_match $dm ports_match $pm \
        error_lines $err warning_lines $warn lvs_verdict $v]
}
