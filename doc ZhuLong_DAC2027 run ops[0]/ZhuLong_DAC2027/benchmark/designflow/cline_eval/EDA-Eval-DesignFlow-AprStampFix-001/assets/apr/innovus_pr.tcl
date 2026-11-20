#############################################################################
# innovus_pr.tcl -- Innovus stage 2 : place + CTS + route
#   BUGGY (qiqs7): no stamp mechanism on any FAILED exit / DONE banner
#############################################################################
proc env_or {name default} {
    if {[info exists ::env($name)]} {
        set v [string trim $::env($name)]
        if {$v ne ""} { return $v }
    }
    return $default
}

set TOP     [env_or TOP  "hl22_porting_test_chip_v1"]
set LOG_DIR [env_or INV_LOG_DIR "logs"]

# --- required inputs (FAILED, NO stamp) ---
foreach f [list "pdk/tech.tlef" "pdk/stdcells.lef" "netlist/hl22_postsyn.v" "sdc/hl22.mapped.sdc" "mmmc.view"] {
    if {![file exists $f]} {
        puts "INNOVUS PR FAILED: missing required input $f"
        exit 1
    }
}

puts "INNOVUS PR: init_design"
if {[catch {puts "init ok"} err]} {
    puts "INNOVUS PR FAILED: init_design error $err"
    exit 1
}

puts "INNOVUS PR: place"
if {[catch {puts "place ok"} err]} {
    puts "INNOVUS PR FAILED: place error $err"
    exit 1
}

puts "INNOVUS PR: CTS"
if {[catch {puts "CTS ok"} err]} {
    puts "INNOVUS PR FAILED: CTS error $err"
    exit 1
}

puts "INNOVUS PR: route"
if {[catch {puts "route ok"} err]} {
    puts "INNOVUS PR FAILED: route error $err"
    exit 1
}

puts "INNOVUS PR: output write"
if {[catch {puts "write ok"} err]} {
    puts "INNOVUS PR FAILED: output write error $err"
    exit 1
}

puts "INNOVUS PR: verify"
if {[catch {puts "verify ok"} err]} {
    puts "INNOVUS PR FAILED: verify error $err"
    exit 1
}

puts "INNOVUS PR DONE"
