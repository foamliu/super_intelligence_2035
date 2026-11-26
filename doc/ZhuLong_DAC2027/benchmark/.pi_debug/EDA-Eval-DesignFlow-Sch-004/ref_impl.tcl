# Reference implementation for EDA-Eval-DesignFlow-Sch-004
# Task: netlist_fanout_floating_audit -- parse an emy2netlist-style SPICE
# fragment (X-subckt instantiations + .subckt/.ends/.global/.param dot-commands
# + '*' comments) and audit NET connectivity: per-net connection counts,
# floating nets (==1 conn, not power/ground), power/ground nets (name rule +
# SPICE '0' + .global declarations), max fanout (lex-smallest tie-break),
# and a verdict combining floating + sparse-power.
# Runtime: Tcl on Synopsys WaveView (host=waveview). Pure Tcl builtins.

# Is a net name a power/ground-class net BY NAME RULE?
#   - exactly "0" (SPICE global ground)
#   - lowercased name with a single trailing "!" stripped matches any glob:
#         gnd* vdd* vss* vcc* avdd* avss* dvdd* dvss*
proc _sn4_is_pg_name {n} {
    if {$n eq "0"} { return 1 }
    set lo [string tolower $n]
    # strip a single trailing "!"
    if {[string index $lo end] eq "!"} {
        set lo [string range $lo 0 end-1]
    }
    foreach pat {gnd* vdd* vss* vcc* avdd* avss* dvdd* dvss*} {
        if {[string match $pat $lo]} { return 1 }
    }
    return 0
}

proc netlist_fanout_floating_audit {netlist_text} {
    # connection counts: array cnt($net) = integer
    array set cnt {}
    array set pgdecl {}              ;# .global-declared nets (set)
    set total_connections 0

    set lines [split $netlist_text "\n"]
    set n [llength $lines]
    set i 0
    while {$i < $n} {
        set raw [lindex $lines $i]
        # strip CR
        set raw [string map [list "\r" ""] $raw]
        set line [string trim $raw]
        # blank line -> breaks continuation
        if {$line eq ""} { incr i; continue }
        # comment (col1 '*') -> breaks continuation
        if {[string index $line 0] eq "*"} { incr i; continue }

        # join '+' continuations: subsequent lines whose first non-space char
        # is '+' are appended (after removing the '+'); a blank or comment or
        # dot-command line BREAKS the continuation.
        set buf $line
        while {1} {
            set j [expr {$i + 1}]
            if {$j >= $n} break
            set nraw [string map [list "\r" ""] [lindex $lines $j]]
            set nline [string trim $nraw]
            if {$nline eq ""} break
            if {[string index $nline 0] ne "+"} break
            set cont [string trim [string range $nline 1 end]]
            append buf " " $cont
            incr i
        }

        # dot-commands: .subckt/.ends/.global/.param/.option/.lib/.include ...
        if {[string index $buf 0] eq "."} {
            # record .global declarations
            set lower [string tolower [string range $buf 0 end]]
            if {[string match ".global*" $lower]} {
                set toks [split $buf " \t"]
                # toks(0) = ".global"
                for {set k 1} {$k < [llength $toks]} {incr k} {
                    set t [string trim [lindex $toks $k]]
                    if {$t ne ""} { set pgdecl($t) 1 }
                }
            }
            incr i
            continue
        }

        # Only X-instantiations count as instance lines for the net map.
        if {[string index $buf 0] ne "X" && [string index $buf 0] ne "x"} {
            incr i
            continue
        }

        # tokenize
        set toks [split $buf " \t"]
        # remove empty tokens from split
        set clean {}
        foreach t $toks {
            if {$t ne ""} { lappend clean $t }
        }
        # need at least: Xname + 1 node + subname => >=3 tokens
        if {[llength $clean] < 3} { incr i; continue }

        # instance name = clean(0); drop it
        set clean [lrange $clean 1 end]

        # separate non-param tokens and param tokens
        set nonparam {}
        foreach t $clean {
            if {[string match *=* $t]} {
                # param token: contains '=' -> not a node, not subname
                continue
            }
            lappend nonparam $t
        }
        # need at least 1 node + 1 subname
        if {[llength $nonparam] < 2} { incr i; continue }

        # subname = LAST nonparam token; nodes = all but last
        set sub [lindex $nonparam end]
        set nodes [lrange $nonparam 0 end-1]

        # count each node occurrence (duplicates within one instance count
        # separately -> per-occurrence increment)
        foreach nd $nodes {
            if {![info exists cnt($nd)]} { set cnt($nd) 0 }
            incr cnt($nd)
            incr total_connections
        }

        incr i
    }

    # build net lists
    set allnets [lsort -dictionary [array names cnt]]
    set total_nets [llength $allnets]

    set floating {}
    set pgnets {}
    set multi 0
    set max_count 0
    set max_net ""
    set sparse_power 0

    foreach nd $allnets {
        set c $cnt($nd)
        # power/ground class?
        set ispg 0
        if {[_sn4_is_pg_name $nd]} { set ispg 1 }
        if {[info exists pgdecl($nd)]} { set ispg 1 }

        if {$ispg} {
            lappend pgnets $nd
            if {$c < 2} { set sparse_power 1 }
        }

        if {$c == 1 && !$ispg} {
            lappend floating $nd
        }
        if {$c >= 2} { incr multi }

        # max fanout: highest count; tie -> lex smallest.
        # allnets is already lex sorted (lsort -dictionary), so iterate in
        # lex order and keep STRICTLY-greater updates -> first (lex smallest)
        # among ties wins.
        if {$c > $max_count} {
            set max_count $c
            set max_net $nd
        }
    }

    set floating [lsort -dictionary $floating]
    set pgnets   [lsort -dictionary $pgnets]
    set floating_count [llength $floating]
    set pg_count [llength $pgnets]

    # verdict
    if {$floating_count == 0 && !$sparse_power} {
        set verdict "clean"
    } elseif {$floating_count > 0 && !$sparse_power} {
        set verdict "floating"
    } elseif {$floating_count == 0 && $sparse_power} {
        set verdict "sparse_power"
    } else {
        set verdict "both"
    }

    if {$total_nets == 0} {
        set max_net ""
        set max_count 0
    }

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
