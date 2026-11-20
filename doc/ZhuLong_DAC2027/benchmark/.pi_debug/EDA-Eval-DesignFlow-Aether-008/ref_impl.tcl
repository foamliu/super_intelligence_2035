# Reference implementation: layout_via_enclosure_audit
# Audits a pyAether-emitted textual via-enclosure compliance report.
# Pure string + float/integer math. POSIX classes only (no Perl character classes).
proc layout_via_enclosure_audit {report_text} {
    set lines [split $report_text [format %c 10]]
    array set viaseen {}
    array set pair {}
    array set encB {}
    array set encT {}
    array set reqv {}
    array set stat {}
    array set sum {}
    set have_summary 0

    foreach line $lines {
        set t [string trim $line]
        if {$t eq ""} { continue }
        if {[string index $t 0] eq "#"} { continue }
        set toks [split $t]
        set first [lindex $toks 0]
        if {$first eq "VIA"} {
            set name [lindex $toks 1]
            set cut ""
            set eb ""
            set et ""
            set rq ""
            set st ""
            foreach tok [lrange $toks 2 end] {
                switch -glob -- $tok {
                    "cut=*"      { set cut [string range $tok 4 end] }
                    "bottom=*"   { }
                    "top=*"      { }
                    "enc_bot=*"  { set eb [string range $tok 8 end] }
                    "enc_top=*"  { set et [string range $tok 8 end] }
                    "req=*"      { set rq [string range $tok 4 end] }
                    "count=*"    { }
                    "status=*"   { set st [string range $tok 7 end] }
                }
            }
            set viaseen($name) 1
            set key "$name|$cut"
            set pair($key) 1
            # LAST occurrence WINS: replace ALL fields
            set encB($key) $eb
            set encT($key) $et
            set reqv($key) $rq
            set stat($key) $st
        } elseif {$first eq "SUMMARY"} {
            set have_summary 1
            foreach tok [lrange $toks 1 end] {
                if {[string match "vias_checked=*" $tok]}  { set sum(vias_checked)  [string range $tok 13 end] }
                if {[string match "violations=*" $tok]}    { set sum(violations)    [string range $tok 11 end] }
                if {[string match "warns=*" $tok]}         { set sum(warns)         [string range $tok 6 end] }
                if {[string match "skipped=*" $tok]}       { set sum(skipped)       [string range $tok 8 end] }
                if {[string match "min_enclosure=*" $tok]} { set sum(min_enclosure) [string range $tok 14 end] }
                if {[string match "worst_via=*" $tok]}     { set sum(worst_via)     [string range $tok 10 end] }
            }
        }
    }

    set total_nets [llength [array names viaseen]]
    set total_lines [llength [array names pair]]
    set pass 0; set warn 0; set fail 0; set skip 0
    set have_nonskip 0
    set min_enc 0.0
    set tie_names {}
    set worst_via ""

    foreach key [array names pair] {
        set name [lindex [split $key "|"] 0]
        set eb $encB($key)
        set et $encT($key)
        set rq $reqv($key)
        set st $stat($key)
        # defaults: missing enc_bot/enc_top -> 0.0 ; missing req -> 0.0
        if {$eb eq ""} { set eb 0.0 }
        if {$et eq ""} { set et 0.0 }
        if {$rq eq ""} { set rq 0.0 }
        set eb [expr {double($eb)}]
        set et [expr {double($et)}]
        set rq [expr {double($rq)}]

        # effective status: explicit (case-insensitive) wins; absent -> infer
        if {$st eq ""} {
            if {($eb < $rq) || ($et < $rq)} { set eff "FAIL" } else { set eff "PASS" }
        } else {
            set eff [string toupper $st]
        }
        switch -- $eff {
            "PASS" { incr pass }
            "WARN" { incr warn }
            "FAIL" { incr fail }
            "SKIP" { incr skip }
            default {
                # unknown status token -> infer (treat like absent)
                if {($eb < $rq) || ($et < $rq)} { set eff "FAIL"; incr fail } else { set eff "PASS"; incr pass }
            }
        }

        if {$eff ne "SKIP"} {
            set line_min [expr {$eb < $et ? $eb : $et}]
            if {!$have_nonskip} {
                set have_nonskip 1
                set min_enc $line_min
                set tie_names [list $name]
            } else {
                if {$line_min < $min_enc} {
                    set min_enc $line_min
                    set tie_names [list $name]
                } elseif {$line_min == $min_enc} {
                    lappend tie_names $name
                }
            }
        }
    }

    if {!$have_nonskip} {
        set min_enc -1.0
        set worst_via ""
    } else {
        set min_enc [expr {double($min_enc)}]
        set worst_via [lindex [lsort -dictionary $tie_names] 0]
    }

    # mismatched_summary reconciliation
    set mismatch {}
    if {$have_summary} {
        if {[info exists sum(vias_checked)]} {
            if {![expr {$sum(vias_checked) == $total_lines}]} { lappend mismatch "vias_checked" }
        }
        if {[info exists sum(violations)]} {
            if {![expr {$sum(violations) == $fail}]} { lappend mismatch "violations" }
        }
        if {[info exists sum(warns)]} {
            if {![expr {$sum(warns) == $warn}]} { lappend mismatch "warns" }
        }
        if {[info exists sum(skipped)]} {
            if {![expr {$sum(skipped) == $skip}]} { lappend mismatch "skipped" }
        }
        if {[info exists sum(min_enclosure)]} {
            # NUMERIC equality (expr ==): "0.080" matches 0.08
            if {![expr {double($sum(min_enclosure)) == $min_enc}]} { lappend mismatch "min_enclosure" }
        }
        if {[info exists sum(worst_via)]} {
            # STRING equality
            if {$sum(worst_via) ne $worst_via} { lappend mismatch "worst_via" }
        }
    }
    set mismatch [lsort -dictionary $mismatch]

    if {$fail > 0} {
        set verdict "FAIL"
    } elseif {[llength $mismatch] > 0 || !$have_summary} {
        set verdict "INCOMPLETE"
    } else {
        set verdict "PASS"
    }

    return [dict create total_via_types $total_nets total_lines $total_lines pass_count $pass warn_count $warn fail_count $fail skip_count $skip worst_via $worst_via min_enclosure $min_enc mismatched_summary $mismatch verdict $verdict]
}
