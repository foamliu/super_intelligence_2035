# Reference solution for EDA-Eval-DesignFlow-PV-005
# proc lvs_summary_audit {lvs_report_text} -> dict (12 keys)
proc lvs_summary_audit {text} {
    set layout_cell ""
    set source_cell ""
    set nets_layout ""
    set nets_source ""
    set devices_layout ""
    set devices_source ""
    set ports_layout ""
    set ports_source ""
    set error_lines 0
    set warning_lines 0
    foreach line [split $text "\n"] {
        set t [string trim $line]
        if {$t eq ""} continue
        # ERROR: / WARNING: lines (anchored prefix, case-sensitive keyword)
        if {[regexp {^ERROR:\s*} $t]} { incr error_lines; continue }
        if {[regexp {^WARNING:\s*} $t]} { incr warning_lines; continue }
        # Collapse internal whitespace so "LAYOUT  CELL  NAME  =  TOP" matches.
        set ts [regsub -all {\s+} $t " "]
        if {[regexp {^# of NETS in layout = (-?\d+)$} $ts -> v]}       { set nets_layout $v }
        if {[regexp {^# of NETS in source = (-?\d+)$} $ts -> v]}      { set nets_source $v }
        if {[regexp {^# of DEVICES in layout = (-?\d+)$} $ts -> v]}   { set devices_layout $v }
        if {[regexp {^# of DEVICES in source = (-?\d+)$} $ts -> v]}   { set devices_source $v }
        if {[regexp {^# of PORTS in layout = (-?\d+)$} $ts -> v]}     { set ports_layout $v }
        if {[regexp {^# of PORTS in source = (-?\d+)$} $ts -> v]}     { set ports_source $v }
        if {[regexp {^LAYOUT CELL NAME = (.*)$} $ts -> v]}            { set layout_cell [string trim $v] }
        if {[regexp {^SOURCE CELL NAME = (.*)$} $ts -> v]}            { set source_cell [string trim $v] }
    }
    # Per-cell counts use LAST-WINS (later block supersedes); error lines already accumulated.
    set cell_name_match [expr {$layout_cell eq $source_cell && $layout_cell ne ""}]
    set nets_delta    [expr {$nets_layout    - $nets_source}]
    set devices_delta [expr {$devices_layout - $devices_source}]
    set ports_delta   [expr {$ports_layout   - $ports_source}]
    set nets_match    [expr {$nets_delta    == 0}]
    set devices_match [expr {$devices_delta == 0}]
    set ports_match   [expr {$ports_delta   == 0}]
    set lvs_verdict [expr {($nets_match && $devices_match && $ports_match && $cell_name_match && $error_lines == 0) ? "clean" : "errors"}]
    return [dict create \
        layout_cell $layout_cell source_cell $source_cell cell_name_match $cell_name_match \
        nets_delta $nets_delta devices_delta $devices_delta ports_delta $ports_delta \
        nets_match $nets_match devices_match $devices_match ports_match $ports_match \
        error_lines $error_lines warning_lines $warning_lines lvs_verdict $lvs_verdict]
}
