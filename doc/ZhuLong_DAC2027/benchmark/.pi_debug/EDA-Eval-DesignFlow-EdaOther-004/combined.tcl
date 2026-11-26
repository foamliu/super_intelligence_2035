# Reference implementation: vsim_pattern_coverage_audit
# Mined from real cliu session (vsim_report_new + pattern.list A_Summary.rpt flow).
# POSIX char classes only (waveview tcl safe); no \s \d \b.
proc vsim_pattern_coverage_audit {reports_text pattern_list_text} {
    # ---- parse reference pattern list: unique, non-blank, non-comment, trimmed (CR/space) ----
    array set expSeen {}
    set expected {}
    foreach raw [split $pattern_list_text "\n"] {
        set line [string map {"\r" ""} $raw]
        set t [string trim $line]
        if {$t eq ""} continue
        if {[string index $t 0] eq "#"} continue
        if {![info exists expSeen($t)]} {
            set expSeen($t) 1
            lappend expected $t
        }
    }
    set expected_count [llength $expected]

    # ---- parse reports ----
    set runs_parsed 0
    set total_pattern_reported 0
    set total_failed_reported 0
    set pattern_list_entries 0
    set pastSep 0
    array set bytemodeSeen {}
    array set regSeen {}
    array set ranSeen {}
    foreach raw [split $reports_text "\n"] {
        set line [string map {"\r" ""} $raw]
        # section header: === <simdir> ===
        if {[regexp -- {^===[[:space:]]+([^[:space:]]+)[[:space:]]+===[[:space:]]*$} $line -> simdir]} {
            incr runs_parsed
            set pastSep 0
            set bm "unknown"
            set reg $simdir
            if {[regexp -- {\.x([0-9]+)(\.|$)} $simdir -> digits]} {
                set bm "x$digits"
                set idx [string first ".x$digits" $simdir]
                set reg [string range $simdir 0 [expr {$idx - 1}]]
            }
            set bytemodeSeen($bm) 1
            set regSeen($reg) 1
            continue
        }
        if {!$runs_parsed} continue
        set t [string trim $line]
        if {[regexp -- {^-{3,}$} $t]} { set pastSep 1; continue }
        if {$t eq ""} continue
        if {!$pastSep} {
            # header lines BEFORE separator: counts only (not pattern names)
            if {[regexp -- {^Total[[:space:]]+Pattern[[:space:]]*:[[:space:]]*([0-9]+)} $t -> n]} {
                incr total_pattern_reported $n
            } elseif {[regexp -- {^Failed[[:space:]]+Pattern[[:space:]]*:[[:space:]]*([0-9]+)} $t -> n]} {
                incr total_failed_reported $n
            }
            # Global_Seed and any other header line: ignored
            continue
        }
        # past separator: a real pattern name line
        incr pattern_list_entries
        set ranSeen($t) 1
    }

    set bytemodes [lsort [array names bytemodeSeen]]
    set regressions [lsort [array names regSeen]]
    set ran_list [lsort [array names ranSeen]]
    set ran_unique [llength $ran_list]

    set missing {}
    set extra {}
    foreach p $ran_list {
        if {![info exists expSeen($p)]} { lappend extra $p }
    }
    foreach p $expected {
        if {![info exists ranSeen($p)]} { lappend missing $p }
    }
    set missing_count [llength $missing]
    set extra_count [llength $extra]

    if {$missing_count == 0 && $extra_count == 0} {
        set verdict "complete"
    } elseif {$missing_count > 0 && $extra_count == 0} {
        set verdict "missing"
    } elseif {$missing_count == 0 && $extra_count > 0} {
        set verdict "extra"
    } else {
        set verdict "missing_and_extra"
    }

    set out "runs_parsed $runs_parsed"
    append out " total_pattern_reported $total_pattern_reported"
    append out " total_failed_reported $total_failed_reported"
    append out " pattern_list_entries $pattern_list_entries"
    append out " bytemodes [join $bytemodes ,]"
    append out " regressions [join $regressions ,]"
    append out " ran_unique $ran_unique"
    append out " expected_count $expected_count"
    append out " missing_count $missing_count"
    append out " missing_patterns [join $missing " "]"
    append out " extra_count $extra_count"
    append out " extra_patterns [join $extra " "]"
    append out " coverage_verdict $verdict"
    return $out
}
# Verification harness: run reference impl on 6 cases, print outputs.

# ---- Case A: baseline mirroring real cliu session ----
set plistA "avl_ca_odt\nbasic_BurstOrderLengthType\nbasic_allbank_bc8\nmbist_three_deep\n# this is a comment\n\ntm_multirow\ntm_pretest\nmbist_three_deep"
set repA "=== basic.x4 ===\nTotal Pattern : 3\n Failed Pattern: 1\nGlobal_Seed : 100\n-----------------\navl_ca_odt\nbasic_BurstOrderLengthType\nbasic_allbank_bc8\n=== checkin.x8 ===\nTotal Pattern : 2\n Failed Pattern: 0\nGlobal_Seed : 200\n-----------------\nmbist_three_deep\ntm_multirow\n=== misc.x16 ===\nTotal Pattern : 2\n Failed Pattern: 0\nGlobal_Seed : 300\n-----------------\ntm_pretest\nextra_pattern_x"
puts "CASE A: [vsim_pattern_coverage_audit $repA $plistA]"

# ---- Case B: colon-spacing tooth (both forms) + cross-rpt dup ----
set plistB "p1\np2\np3\np4\np5\np6"
set repB "=== r1.x4 ===\nTotal Pattern : 4\n Failed Pattern: 2\n-----------------\np1\np2\np3\np4\n=== r2.x8 ===\nTotal Pattern: 3\n  Failed Pattern: 1\n-----------------\np1\np5\np6"
puts "CASE B: [vsim_pattern_coverage_audit $repB $plistB]"

# ---- Case C: reference-list hygiene tooth (dup + comment + blank + CR + trailing space) ----
set plistC "p1\np2\n# comment line\n\np3\r\np2\np4  "
set repC "=== only.x4 ===\nTotal Pattern : 5\n Failed Pattern: 0\n-----------------\np1\np2\np3\np4\np5"
puts "CASE C: [vsim_pattern_coverage_audit $repC $plistC]"

# ---- Case D: bytemode/regression extraction tooth (.rerun suffix, nosuffix) ----
set plistD "pa\npb\npc"
set repD "=== basic.x4.rerun ===\nTotal Pattern : 1\n Failed Pattern: 0\n-----------------\npa\n=== misc.x16 ===\nTotal Pattern : 1\n Failed Pattern: 0\n-----------------\npb\n=== nosuffix ===\nTotal Pattern : 1\n Failed Pattern: 0\n-----------------\npc"
puts "CASE D: [vsim_pattern_coverage_audit $repD $plistD]"

# ---- Case E: header-vs-list mismatch + separator/header-exclusion tooth ----
set plistE "pa\npb\npc\npd\npe\npf"
set repE "=== r1.x4 ===\nTotal Pattern : 5\n Failed Pattern: 1\nGlobal_Seed : 42\n-----------------\npa\npb\npc\npd\n=== r2.x8 ===\nTotal Pattern : 2\n Failed Pattern: 0\n-----------------\npe\npf"
puts "CASE E: [vsim_pattern_coverage_audit $repE $plistE]"

# ---- Case F: comprehensive + dup-within-rpt + missing_and_extra + invariant ----
set plistF "avl_ca_odt\nbasic_allbank_bc8\ntm_multirow\ntm_pretest\n# dup below\ntm_pretest"
set repF "=== basic.x4 ===\nTotal Pattern : 3\n Failed Pattern: 1\n-----------------\navl_ca_odt\nbasic_allbank_bc8\navl_ca_odt\n=== checkin.x8 ===\nTotal Pattern : 2\n Failed Pattern: 0\n-----------------\ntm_multirow\nghost_pattern"
puts "CASE F: [vsim_pattern_coverage_audit $repF $plistF]"
