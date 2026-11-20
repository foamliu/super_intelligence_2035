#############################################################################
# innovus_fp.tcl -- Innovus stage 1 : init_design + floorplan + PM-band
#   BUGGY (qiqs7): no stamp mechanism ; geometry uses single dbGet spelling
#                  with no fallback -> "cannot query row/core geometry -- skipping"
#############################################################################
proc env_or {name default} {
    if {[info exists ::env($name)]} {
        set v [string trim $::env($name)]
        if {$v ne ""} { return $v }
    }
    return $default
}

set TOP     [env_or TOP  "hl22_porting_test_chip_v1"]
set PM_CELL [env_or INV_PM_CELL "INVD8BWP40P140LVT"]
set SITE    [env_or INV_SITE "coreSite"]
set LOG_DIR [env_or INV_LOG_DIR "logs"]

# --- required inputs (FAILED exit, NO stamp) ---
foreach f [list "pdk/tech.tlef" "pdk/stdcells.lef" "netlist/hl22_postsyn.v" "sdc/hl22.mapped.sdc"] {
    if {![file exists $f]} {
        puts "INNOVUS FP FAILED: missing required input $f"
        exit 1
    }
}
if {![file exists "mmmc.view"]} {
    puts "INNOVUS FP FAILED: missing mmmc.view"
    exit 1
}

puts "INNOVUS FP: init_design + floorplan"

# --- BUGGY PM-band geometry: single dbGet spelling, no fallback ---
set rows [dbGet top.fPlan.rows.origin_y]
if {[llength $rows] == 0} {
    puts "WARN: PM band: cannot query row/core geometry -- skipping"
} else {
    puts "INNOVUS FP: PM band cell=$PM_CELL rows=[llength $rows]"
}
set coreBox [dbGet top.fPlan.coreBox]
if {[llength $coreBox] == 0} {
    puts "WARN: PM band: cannot query coreBox -- skipping"
}

puts "INNOVUS FP DONE"
