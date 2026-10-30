# NAIVE implementation -- intentionally makes the common mistakes, to prove
# the checker's teeth bite. Each mistake is annotated.
proc _sn4_is_pg_name_naive {n} {
    # NAIVE mistake #1: exact-case match against fixed set only; misses
    # 'gnd!', 'AVDD', 'vss0', and node '0'.
    return [expr {$n eq "gnd" || $n eq "vdd" || $n eq "vss" || $n eq "vcc"}]
}

proc netlist_fanout_floating_audit {netlist_text} {
    array set cnt {}
    set total_connections 0
    set pgspec {}
    # NAIVE: ignore .global declarations entirely (mistake #2)

    # NAIVE: process line-by-line, NO '+' continuation join (mistake #3)
    foreach raw [split $netlist_text "\n"] {
        set line [string map [list "\r" ""] $raw]
        set line [string trim $line]
        if {$line eq ""} continue
        if {[string index $line 0] eq "*"} continue
        if {[string index $line 0] eq "."} continue
        if {[string index $line 0] ne "X" && [string index $line 0] ne "x"} continue

        set toks [split $line " \t"]
        set clean {}
        foreach t $toks { if {$t ne ""} { lappend clean $t } }
        if {[llength $clean] < 3} continue
        # NAIVE mistake #4: keep ALL non-param tokens as nodes INCLUDING the
        # subname (last token), and do NOT exclude params properly -- here we
        # do exclude params but include subname as a node.
        set nodes {}
        foreach t [lrange $clean 1 end] {
            if {[string match *=* $t]} continue
            lappend nodes $t
        }

        # NAIVE mistake #5: dedup nodes within one instance (count each net
        # at most once per instance)
        array unset seen
        foreach nd $nodes {
            if {[info exists seen($nd)]} continue
            set seen($nd) 1
            if {![info exists cnt($nd)]} { set cnt($nd) 0 }
            incr cnt($nd)
            incr total_connections
        }
    }

    set allnets [array names cnt]
    set total_nets [llength $allnets]
    set floating {}
    set pgnets {}
    set multi 0
    set max_count 0
    set max_net ""
    set sparse_power 0

    # NAIVE mistake #6: first-seen for max_fanout (no lex tie-break) -- iterate
    # array names in arbitrary order.
    foreach nd $allnets {
        set c $cnt($nd)
        set ispg [_sn4_is_pg_name_naive $nd]
        if {$ispg} {
            lappend pgnets $nd
            if {$c < 2} { set sparse_power 1 }
        }
        if {$c == 1 && !$ispg} { lappend floating $nd }
        if {$c >= 2} { incr multi }
        if {$c > $max_count} { set max_count $c; set max_net $nd }
    }

    # NAIVE mistake #7: do NOT lex-sort output lists (leave in iteration order)
    set floating_count [llength $floating]
    set pg_count [llength $pgnets]
    if {$floating_count == 0 && !$sparse_power} { set verdict "clean"
    } elseif {$floating_count > 0 && !$sparse_power} { set verdict "floating"
    } elseif {$floating_count == 0 && $sparse_power} { set verdict "sparse_power"
    } else { set verdict "both" }

    if {$total_nets == 0} { set max_net ""; set max_count 0 }
    return [dict create \
        total_nets $total_nets \
        total_connections $total_connections \
        floating_nets $floating \
        floating_count $floating_count \
        power_ground_nets $pgnets \
        power_ground_count $pg_count \
        multi_connect_count $multi \
        max_fanout_net $max_net \
        max_fanout_count $max_count \
        verdict $verdict]
}
