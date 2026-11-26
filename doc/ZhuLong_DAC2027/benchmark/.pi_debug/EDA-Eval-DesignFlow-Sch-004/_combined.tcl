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
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
proc dget {d k} { return [dict get $d $k] }
proc llist {d k} { return [dict get $d $k] }
proc j {d k} { return [join [dict get $d $k] "|"] }

proc check {candidate} {
    # ---- Case A: baseline mixed netlist, no floating ----
    set cA {.subckt INV a b
.ends
.global vdd gnd
X1 n1 vdd INV
X2 n1 gnd INV
X3 n2 n1 INV}
    set dA [$candidate $cA]
    assert {[dget $dA total_nets] == 4} "A total_nets=4 (n1 n2 vdd gnd)"
    assert {[dget $dA total_connections] == 6} "A total_connections=6"
    assert {[j $dA floating_nets] eq "n2"} "A floating_nets=n2 (1 conn, not pg)"
    assert {[dget $dA floating_count] == 1} "A floating_count=1"
    assert {[j $dA power_ground_nets] eq "gnd|vdd"} "A pg_nets=gnd|vdd (lex sorted)"
    assert {[dget $dA power_ground_count] == 2} "A pg_count=2"
    assert {[dget $dA multi_connect_count] == 1} "A multi=1 (only n1 has>=2)"
    assert {[dget $dA max_fanout_net] eq "n1"} "A max_fanout_net=n1 (3 conns)"
    assert {[dget $dA max_fanout_count] == 3} "A max_fanout_count=3"
    assert {[string equal [dget $dA verdict] "both"]} "A verdict=both (floating n2 + sparse_power vdd/gnd each 1)"

    # ---- Case B: PARAM EXCLUSION tooth ----
    set cB {.subckt INV a b
.ends
X1 a b INV w=1u l=1u}
    set dB [$candidate $cB]
    assert {[dget $dB total_nets] == 2} "B total_nets=2 (a b only; w/l are params)"
    assert {[dget $dB total_connections] == 2} "B total_connections=2"
    assert {[llength [llist $dB floating_nets]] == 2} "B both a,b floating"
    assert {[j $dB floating_nets] eq "a|b"} "B floating=a|b"
    assert {[dget $dB max_fanout_count] == 1} "B max_count=1"
    assert {[string equal [dget $dB verdict] "floating"]} "B verdict=floating"

    # ---- Case C: SUBCKT NAME = last non-param token (excluded from nodes) ----
    set cC {X1 p q r INV}
    set dC [$candidate $cC]
    assert {[dget $dC total_nets] == 3} "C total_nets=3 (p q r; INV is subname)"
    assert {[dget $dC total_connections] == 3} "C total_connections=3"
    assert {[j $dC floating_nets] eq "p|q|r"} "C floating=p|q|r"
    assert {[dget $dC max_fanout_count] == 1} "C max=1"

    # ---- Case D: power/ground NAME RULE case-insensitive + '!' strip + glob ----
    set cD {X1 AVDD gnd! vss0 vcc INV}
    set dD [$candidate $cD]
    assert {[dget $dD total_nets] == 4} "D total_nets=4"
    assert {[llength [llist $dD floating_nets]] == 0} "D no floating (all pg by name)"
    assert {[j $dD power_ground_nets] eq "AVDD|gnd!|vcc|vss0"} "D all 4 are pg (case-insens, ! strip, glob)"
    assert {[string equal [dget $dD verdict] "sparse_power"]} "D verdict=sparse_power (each pg has 1 conn, no floating)"

    # ---- Case E: SPICE node '0' is always ground ----
    set cE {X1 0 n1 INV
X2 0 n1 INV}
    set dE [$candidate $cE]
    assert {[j $dE power_ground_nets] eq "0"} "E '0' is pg"
    assert {[llength [llist $dE floating_nets]] == 0} "E '0' (1 conn) NOT floating"
    assert {[dget $dE max_fanout_count] == 2} "E max_count=2"
    assert {[dget $dE max_fanout_net] eq "0"} "E max_fanout_net=0 (tie 0 vs n1, lex smallest)"
    assert {[string equal [dget $dE verdict] "clean"]} "E verdict=clean (0 is pg w/2 conn, n1 2 conn, no floating, no sparse)"

    # ---- Case F: .global declared net is power/ground-class even if name doesn't match ----
    set cF {.global vddx
X1 vddx n1 INV
X2 vddx n1 INV}
    set dF [$candidate $cF]
    assert {[j $dF power_ground_nets] eq "vddx"} "F vddx is pg via .global"
    assert {[llength [llist $dF floating_nets]] == 0} "F no floating"
    assert {[dget $dF floating_count] == 0} "F floating_count=0"
    assert {[string equal [dget $dF verdict] "clean"]} "F verdict=clean (vddx pg w/2, n1 w/2)"

    # ---- Case G: '+' CONTINUATION JOIN ----
    set cG {X1 a b
+ c d INV}
    set dG [$candidate $cG]
    assert {[dget $dG total_nets] == 4} "G total_nets=4 (a b c d joined)"
    assert {[dget $dG total_connections] == 4} "G total_connections=4"
    assert {[j $dG floating_nets] eq "a|b|c|d"} "G floating=a|b|c|d"
    assert {[dget $dG max_fanout_count] == 1} "G max=1"

    # ---- Case H: DUPLICATE NODE IN ONE INSTANCE counts as 2 connections ----
    set cH {X1 a a INV}
    set dH [$candidate $cH]
    assert {[dget $dH total_nets] == 1} "H total_nets=1 (a)"
    assert {[dget $dH total_connections] == 2} "H total_connections=2 (a counted twice)"
    assert {[dget $dH multi_connect_count] == 1} "H multi=1 (a has 2 conns)"
    assert {[dget $dH max_fanout_net] eq "a"} "H max_fanout_net=a"
    assert {[dget $dH max_fanout_count] == 2} "H max_fanout_count=2"
    assert {[llength [llist $dH floating_nets]] == 0} "H a is NOT floating (2 conns)"
    assert {[string equal [dget $dH verdict] "clean"]} "H verdict=clean"

    # ---- Case I: COMMENT/BLANK breaks '+' continuation ----
    set cI {X1 a b
* a comment breaks the continuation
+ c d INV}
    set dI [$candidate $cI]
    assert {[dget $dI total_nets] == 1} "I total_nets=1 (only a; 'b' became subname, '+...' ignored)"
    assert {[dget $dI total_connections] == 1} "I total_connections=1"
    assert {[j $dI floating_nets] eq "a"} "I floating=a"
    assert {[dget $dI max_fanout_count] == 1} "I max=1"

    # ---- Case J: MAX_FANOUT TIE-BREAK lexicographic smallest ----
    set cJ {X1 zzz mid INV
X2 aaa mid INV}
    set dJ [$candidate $cJ]
    assert {[dget $dJ max_fanout_count] == 2} "J max_count=2 (mid has 2)"
    assert {[dget $dJ max_fanout_net] eq "mid"} "J max_fanout_net=mid (the only net w/2)"
    # now a real tie: aaa and zzz each 2
    set cJ2 {X1 aaa aaa INV
X2 zzz zzz INV}
    set dJ2 [$candidate $cJ2]
    assert {[dget $dJ2 max_fanout_count] == 2} "J2 max_count=2"
    assert {[dget $dJ2 max_fanout_net] eq "aaa"} "J2 max_fanout_net=aaa (lex smallest tie-break)"
    assert {[llength [llist $dJ2 floating_nets]] == 0} "J2 no floating"

    # ---- Case K: LEX SORT floating_nets + power_ground_nets, comprehensive ----
    set cK {.global vdd gnd
.subckt BUF a b
.ends
X1 zebra vdd BUF
X2 apple gnd BUF
X3 apple gnd BUF
X4 mango gnd BUF}
    set dK [$candidate $cK]
    assert {[dget $dK total_nets] == 5} "K total_nets=5 (zebra apple gnd vdd mango)"
    assert {[j $dK floating_nets] eq "mango|zebra"} "K floating lex sorted mango|zebra (gnd/vdd are pg)"
    assert {[j $dK power_ground_nets] eq "gnd|vdd"} "K pg lex sorted gnd|vdd"
    assert {[dget $dK multi_connect_count] == 2} "K multi=2 (apple 2, gnd 3)"
    assert {[dget $dK max_fanout_net] eq "gnd"} "K max_fanout_net=gnd (3)"
    assert {[dget $dK max_fanout_count] == 3} "K max_count=3"
    assert {[string equal [dget $dK verdict] "both"]} "K verdict=both (floating mango/zebra + sparse_power vdd 1conn)"

    # ---- Case L: empty / no X-instances ----
    set cL {.subckt INV a b
.ends
.global vdd
* just comments and dot-commands, no instances}
    set dL [$candidate $cL]
    assert {[dget $dL total_nets] == 0} "L total_nets=0"
    assert {[dget $dL total_connections] == 0} "L total_connections=0"
    assert {[llength [llist $dL floating_nets]] == 0} "L no floating"
    assert {[llength [llist $dL power_ground_nets]] == 0} "L no pg (vdd declared but never instantiated)"
    assert {[dget $dL max_fanout_net] eq ""} "L max_fanout_net empty"
    assert {[dget $dL max_fanout_count] == 0} "L max_count=0"
    assert {[string equal [dget $dL verdict] "clean"]} "L verdict=clean"

    return "ALL_ASSERTS_PASS"
}
set r [check netlist_fanout_floating_audit]; puts "RESULT:$r"
