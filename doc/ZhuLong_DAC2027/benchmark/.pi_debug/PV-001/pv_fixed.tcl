proc pv_summarize_drc_report {path} {
    set total_rule_checks 0
    set total_violations 0
    set num_failing 0
    set num_passing 0
    set worst_rule ""
    set worst_count -1

    set fh [open $path r]
    while {[gets $fh line] >= 0} {
        set line [string trim $line]
        if {$line eq ""} {
            continue
        }
        if {[string index $line 0] eq "#"} {
            continue
        }

        # Only accept fully-qualified data lines of the form:
        #   RULECHECK <name> <non-negative-integer>
        if {![regexp {^RULECHECK\s+(\S+)\s+([0-9]+)\s*$} $line -> name count]} {
            continue
        }

        incr total_rule_checks
        incr total_violations $count

        if {$count > 0} {
            incr num_failing
        } else {
            incr num_passing
        }

        # Ties are broken by the first-encountered rule.
        if {$count > $worst_count} {
            set worst_count $count
            set worst_rule $name
        }
    }
    close $fh

    if {$total_rule_checks == 0} {
        set pass_rate 0.000
        set worst_count 0
    } else {
        set pass_rate [format "%.3f" [expr {double($num_passing) / $total_rule_checks}]]
    }

    return "total_rule_checks $total_rule_checks total_violations $total_violations num_failing $num_failing num_passing $num_passing worst_rule $worst_rule worst_count $worst_count pass_rate $pass_rate"
}