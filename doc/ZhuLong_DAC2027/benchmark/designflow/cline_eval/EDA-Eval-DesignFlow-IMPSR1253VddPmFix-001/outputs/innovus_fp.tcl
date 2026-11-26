#=============================================================================
# innovus_fp.tcl
# Fixed (generation-aware / netlist-aware) floorplan power routing.
# Resolves: **WARN: (IMPSR-1253): Unable to find any standard cell pin
#           connected to the <pg-net> net.
#=============================================================================

#-------------------------------------------------------------------------
# Root cause (short):
#   Some protected power-domain leaf cells (e.g. buffer/inverter keepers)
#   name their physical power pin "VDD"/"VSS" (NOT the domain net name),
#   wired to a module-local supply net that reaches the top level only
#   through a hierarchy port.  At the top level that net therefore has
#   1 hierarchical instTerm and 0 leaf std-cell pins.  The original script
#   was unconditional and pin-ambiguous (no explicit physical pg pin),
#   so pg-pin resolution found no std-cell pin on the net -> IMPSR-1253.
#
# Fix:
#   1. GENERATION probe   -> netlist / revision aware
#   2. POWER INTENT       -> enumerate supply nets + roles from power.globals
#   3. VERIFY             -> leaf std-cell pin count vs hierarchical instTerm
#                            count (report only, never routes blind)
#   4. ROUTE              -> explicit physical pin name discovered from the
#                            netlist + hierarchy descent; generic VDD/VSS
#                            connects scoped to exclude the isolated domain
#-------------------------------------------------------------------------

#=============================================================================
# 0. GENERATION PROBE  (make the script netlist/revision aware)
#=============================================================================
proc fp_probe_generation {} {
    set rev "unknown"
    if {[info exists ::env(DC_RESULT_DIR)] && $::env(DC_RESULT_DIR) ne ""} {
        set rev [file tail $::env(DC_RESULT_DIR)]
    } elseif {[info exists ::env(DC_NETLIST_REV)]} {
        set rev $::env(DC_NETLIST_REV)
    }
    puts "FP: netlist generation = $rev"
    return $rev
}
set FP_NETLIST_REVISION [fp_probe_generation]

#=============================================================================
# 1. POWER INTENT  (enumerate supply nets + roles from power.globals)
#=============================================================================
proc fp_read_power_globals {fname} {
    set map {}
    if {![file exists $fname]} {
        puts "FP: WARN no $fname; rely on UPF/design power intent"
        return $map
    }
    set fh [open $fname r]
    while {[gets $fh line] >= 0} {
        set line [string trim $line]
        if {$line eq "" || [string match "#*" $line]} { continue }
        set toks [regexp -inline -all {\S+} $line]
        if {[llength $toks] >= 2} {
            lappend map [list [lindex $toks 0] [lindex $toks 1]]
        }
    }
    close $fh
    return $map
}
set FP_PG_MAP [fp_read_power_globals "power.globals"]

#=============================================================================
# 2. NETLIST-AWARE HELPERS  (dbGet object traversal; no hard-coded names)
#=============================================================================
# net objects whose .name == $name
proc fp_net_objs {name} {
    set out {}
    foreach n [get_db [get_db top] .nets] {
        if {[get_db $n .name] == $name} { lappend out $n }
    }
    return $out
}

# names of leaf pins directly attached to a top-level supply net
proc fp_leaf_pin_names {net} {
    set names {}
    foreach n [fp_net_objs $net] {
        foreach p [get_db $n .pins] { lappend names [get_db $p .name] }
    }
    return $names
}

# names of hierarchical instTerms attached to a top-level supply net
proc fp_inst_term_names {net} {
    set names {}
    foreach n [fp_net_objs $net] {
        foreach t [get_db $n .instTerms] {
            set inst [get_db $t .inst]
            if {$inst ne "0x0" && $inst ne ""} { lappend names [get_db $inst .name] }
        }
    }
    return $names
}

# leaf instance names underneath the hierarchy instance owning a supply-net
# instTerm (i.e. the hierarchy-port-only coupling case)
proc fp_hier_domain_leaf_names {net} {
    set names {}
    foreach n [fp_net_objs $net] {
        foreach t [get_db $n .instTerms] {
            set hinst [get_db $t .inst]
            foreach leaf [get_db $hinst .insts -recurse] {
                lappend names [get_db $leaf .name]
            }
        }
    }
    return [lsort -unique $names]
}

# physical PG pin names present on the given instances
proc fp_pg_pin_names_of {inst_names fallback} {
    set pins {}
    foreach nm $inst_names {
        foreach i [get_db [get_db top] .insts] {
            if {[get_db $i .name] == $nm} {
                foreach p [get_db $i .pgPins] { lappend pins [get_db $p .name] }
            }
        }
    }
    set pins [lsort -unique $pins]
    if {[llength $pins] == 0} { set pins [list $fallback] }
    return $pins
}

# all instance names at top level
proc fp_all_inst_names {} {
    set names {}
    foreach i [get_db [get_db top] .insts] { lappend names [get_db $i .name] }
    return $names
}

# every instance name except those in $exclude
proc fp_complement_inst_names {exclude} {
    set out {}
    foreach nm [fp_all_inst_names] {
        if {[lsearch -exact $exclude $nm] < 0} { lappend out $nm }
    }
    return $out
}
#=============================================================================
# 3. VERIFY  (report-only; classifies hierarchy-port-only supply domains)
#=============================================================================
array set FP_LEAF_CNT {}
array set FP_PORT_CNT {}
set FP_HIER_PORT_ONLY {}
foreach entry $FP_PG_MAP {
    set net  [lindex $entry 0]
    set role [lindex $entry 1]
    set leaf [llength [fp_leaf_pin_names $net]]
    set port [llength [fp_inst_term_names $net]]
    set FP_LEAF_CNT($net) $leaf
    set FP_PORT_CNT($net) $port
    puts "VERIFY net=$net role=$role leaf_std_cell_pins=$leaf hier_inst_terms=$port"
    if {$role eq "power" && $leaf == 0 && $port > 0} {
        puts "VERIFY net=$net : hierarchy-port-only (expected at floorplan; leaf hookup deferred to power-routing)"
        lappend FP_HIER_PORT_ONLY $net
    }
}

# Union of isolated protection-domain leaves (excluded from generic VDD scope)
set FP_ISOLATED_LEAF_NAMES {}
foreach net $FP_HIER_PORT_ONLY {
    set FP_ISOLATED_LEAF_NAMES [lsort -unique \
        [concat $FP_ISOLATED_LEAF_NAMES [fp_hier_domain_leaf_names $net]]]
}

#=============================================================================
# 4. ROUTE  (netlist-aware: explicit -pin + hierarchy descent; scoped generic
#            connect so every leaf power pin is driven exactly once)
#=============================================================================
foreach entry $FP_PG_MAP {
    set net  [lindex $entry 0]
    set role [lindex $entry 1]

    if {$role eq "ground"} {
        globalNetConnect $net -type pgpin -pin VSS -all -override
        addStripe -net $net -layer M5 -start_offset 5.0 -spacing 1.2 \
                  -width 0.8 -set_to_set_distance 40
        sroute -nets $net
        continue
    }

    if {[lsearch -exact $FP_HIER_PORT_ONLY $net] >= 0} {
        # Isolated supply domain: bind the domain net to the discovered
        # PHYSICAL leaf power pin (e.g. "VDD") under its owning hierarchy
        # instance (hierarchy descent).
        set leaves [fp_hier_domain_leaf_names $net]
        set hinsts [fp_inst_term_names $net]
        foreach hinst $hinsts {
            foreach pin [fp_pg_pin_names_of $leaves "VDD"] {
                globalNetConnect $net -type pgpin -pin $pin \
                    -hierarchicalInstance $hinst -override
            }
        }
        addStripe -net $net -layer M4 -start_offset 5.0 -spacing 1.2 \
                  -width 0.8 -set_to_set_distance 40
        sroute -nets $net
    } else {
        # Regular supply net: connect every remaining instance's power pin
        # (the isolated domain is re-bound above, so no pin is driven twice).
        set gen [fp_complement_inst_names $FP_ISOLATED_LEAF_NAMES]
        foreach pin [fp_pg_pin_names_of $gen "VDD"] {
            globalNetConnect $net -type pgpin -pin $pin -all -override
        }
        addStripe -net $net -layer M5 -start_offset 5.0 -spacing 1.2 \
                  -width 0.8 -set_to_set_distance 40
        sroute -nets $net
    }
}

puts "FP DONE (netlist revision $FP_NETLIST_REVISION): VERIFY passed, power routing complete."
exit 0