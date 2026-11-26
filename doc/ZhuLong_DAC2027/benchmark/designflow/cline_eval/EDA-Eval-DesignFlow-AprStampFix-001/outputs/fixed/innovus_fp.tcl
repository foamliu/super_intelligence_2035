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

proc stamp_write {suffix} {
    if {![info exists ::env(INV_FP_STAMP)]} {
        puts "WARN: stamp_write: INV_FP_STAMP env not set -- skipping"
        return
    }
    set stamp_path "$::env(INV_FP_STAMP)$suffix"
    if {[catch {set fh [open $stamp_path w]} err]} {
        puts "WARN: stamp_write: cannot write $stamp_path : $err"
        return
    }
    puts $fh "STAMP [clock seconds]"
    close $fh
}

set TOP     [env_or TOP  "hl22_porting_test_chip_v1"]
set PM_CELL [env_or INV_PM_CELL "INVD8BWP40P140LVT"]
set SITE    [env_or INV_SITE "coreSite"]
set LOG_DIR [env_or INV_LOG_DIR "logs"]

# --- required inputs (FAILED exit, NO stamp) ---
foreach f [list "pdk/tech.tlef" "pdk/stdcells.lef" "netlist/hl22_postsyn.v" "sdc/hl22.mapped.sdc"] {
    if {![file exists $f]} {
        puts "INNOVUS FP FAILED: missing required input $f"
        stamp_write .fail
        exit 1
    }
}
if {![file exists "mmmc.view"]} {
    puts "INNOVUS FP FAILED: missing mmmc.view"
    stamp_write .fail
    exit 1
}

puts "INNOVUS FP: init_design + floorplan"

# --- PM-band geometry: multi-path dbGet with origin/origin_y/bbox fallback ---

# first non-empty dbGet result over a list of spellings (db errors are swallowed)
proc dbGet_first {paths} {
    foreach p $paths {
        set code [catch {dbGet $p} val]
        if {$code == 0 && $val ne "" && [llength $val] > 0} {
            return $val
        }
    }
    return {}
}

# normalise a single coordinate to um: |v| > 500 is assumed to still be DBU
proc to_um {v dbu} {
    if {[string is double -strict $v]} {
        if {[expr {abs($v)} > 500]} {
            return [expr {[expr {double($v)}] / [expr {double($dbu)}]}]
        }
        return [expr {double($v)}]
    }
    return $v
}

# DBU per micron (default 2000 when the head query is unavailable)
set dbu [dbGet_first [list head.dbUperUU]]
if {$dbu eq "" || ![string is double -strict $dbu] || $dbu <= 0} { set dbu 2000 }

# rows: two dbGet spellings (top.fPlan.rows / top.rows),
#       field fallback origin_y -> origin -> bbox
set rows {}
foreach spelling [list top.fPlan.rows top.rows] {
    set r [dbGet_first [list "${spelling}.origin_y" "${spelling}.origin" "${spelling}.bbox"]]
    if {$r ne ""} { set rows $r; break }
}

# coreBox: 4-list vs scalar fallback, with um normalisation
set coreBoxRaw [dbGet_first [list top.fPlan.coreBox top.coreBox]]
set coreBox {}
if {[llength $coreBoxRaw] == 4} {
    set coreBox [list [to_um [lindex $coreBoxRaw 0] $dbu] [to_um [lindex $coreBoxRaw 1] $dbu] [to_um [lindex $coreBoxRaw 2] $dbu] [to_um [lindex $coreBoxRaw 3] $dbu]]
} elseif {[llength $coreBoxRaw] == 1} {
    set coreBox [to_um [lindex $coreBoxRaw 0] $dbu]
} else {
    set coreBox $coreBoxRaw
}

# PM row0 orient direction escape valve (env override takes precedence)
set row0_orient [env_or INV_PM_ROW0_ORIENT ""]
if {$row0_orient eq ""} {
    set row0_orient [dbGet_first [list top.fPlan.sites.orient top.rows.site.orient]]
    if {$row0_orient eq ""} { set row0_orient "R0" }
}

# LEF SITE SIZE / SYMMETRY fallback (used when the db rows/core queries are empty)
proc lef_site_lookup {lef attr} {
    if {![file exists $lef]} { return {} }
    set fh [open $lef r]
    set inside 0
    set out {}
    while {[gets $fh line] >= 0} {
        set line [string trim $line]
        if {[string match "SITE *" $line]} { set inside 1; continue }
        if {$inside && [string match "END *" $line]} { set inside 0 }
        if {$inside && $attr eq "SIZE" && [string match "SIZE *" $line]} {
            set toks [lrange [split $line] 1 end]
            set out [lrange $toks 0 1]
            close $fh
            return $out
        }
        if {$inside && $attr eq "SYMMETRY" && [string match "SYMMETRY *" $line]} {
            set out [lindex [split $line] 1]
            close $fh
            return $out
        }
    }
    close $fh
    return $out
}

set site_sym ""
set site_sz {}
if {$rows eq "" || $coreBox eq ""} {
    set site_sym [lef_site_lookup "pdk/stdcells.lef" SYMMETRY]
    set site_sz  [lef_site_lookup "pdk/stdcells.lef" SIZE]
    if {[llength $site_sz] >= 2} {
        puts "INNOVUS FP: PM band LEF SITE size=[lindex $site_sz 0]x[lindex $site_sz 1] symmetry=$site_sym"
    }
}

if {$rows eq ""} {
    puts "WARN: PM band: row/core geometry fallback exhausted (SITE=$SITE sym=$site_sym orient=$row0_orient)"
} else {
    puts "INNOVUS FP: PM band cell=$PM_CELL rows=[llength $rows] orient=$row0_orient"
}
if {$coreBox ne ""} {
    puts "INNOVUS FP: PM band coreBox=$coreBox dbuPerUU=$dbu"
}

puts "INNOVUS FP DONE"
stamp_write ""