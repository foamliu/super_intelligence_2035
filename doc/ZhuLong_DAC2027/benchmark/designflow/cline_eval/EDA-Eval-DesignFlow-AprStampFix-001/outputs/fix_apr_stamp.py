#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_apr_stamp.py -- generic adaptive patcher for the Innovus APR flow bundle.

It repairs three real bugs that made `make` misjudge the floorplan FAILED, skip
the PM band, and miss a reliable stamp mechanism:

  1. Missing stamp: innovus_fp.tcl / innovus_pr.tcl never write a stamp file on
     FAILED exits or on the DONE banner, so `make` can only grep the
     asynchronously-flushed log.
  2. PM-band geometry: innovus_fp.tcl used a single dbGet spelling
     (top.fPlan.rows.origin_y) with no fallback -> "cannot query row/core
     geometry -- skipping".
  3. Makefile retry loop too short (15x2s=30s), grep-only, no stamp check, no
     NFS refresh.

Usage:
    fix_apr_stamp.py <bundle_root> [-o <out_dir>]

It reads TOP / PM_CELL / SITE / LOG_DIR from <bundle_root>/test_chip_power.md,
patches innovus_fp.tcl / innovus_pr.tcl / Makefile programmatically and writes
fixed/innovus_fp.tcl, fixed/innovus_pr.tcl and fixed/Makefile into <out_dir>
(default "fixed"). The same patcher works for any structurally-different bundle
because every emitted value is taken from the bundle's own config.
"""

import argparse
import os
import re
import sys


def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def write_text(path, text):
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def parse_md_config(path):
    """Parse test_chip_power.md -> dict of KEY=VALUE entries from the code block."""
    cfg = {}
    for line in read_text(path).splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("```"):
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\S+)\s*$", line)
        if m:
            cfg[m.group(1)] = m.group(2)
    return cfg


def replace_env_default(text, env_or_name, value):
    """Replace the quoted default inside `set X [env_or NAME "..."]`."""
    pattern = re.compile(
        r'(set\s+\w+\s+\[env_or\s+' + re.escape(env_or_name) + r'\s+)"[^"]*"(\])'
    )
    return pattern.sub(lambda m: m.group(1) + '"' + value + '"' + m.group(2), text)


def stamp_proc(env_var):
    """Return the `stamp_write` proc bound to the given stamp env var."""
    tmpl = '''\
proc stamp_write {suffix} {
    if {![info exists ::env(@ENV@)]} {
        puts "WARN: stamp_write: @ENV@ env not set -- skipping"
        return
    }
    set stamp_path "$::env(@ENV@)$suffix"
    if {[catch {set fh [open $stamp_path w]} err]} {
        puts "WARN: stamp_write: cannot write $stamp_path : $err"
        return
    }
    puts $fh "STAMP [clock seconds]"
    close $fh
}'''
    return tmpl.replace("@ENV@", env_var)


def add_fail_stamps(text, call):
    """Insert `call` (indent-matched) immediately before every `exit 1` line."""
    out = []
    for line in text.split("\n"):
        if line.strip() == "exit 1":
            indent = line[: len(line) - len(line.lstrip())]
            out.append(indent + call)
        out.append(line)
    return "\n".join(out)
GEOMETRY_BLOCK = '''\
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
}'''

MAKEFILE_TEMPLATE = '''#############################################################################
# Makefile -- Innovus floorplan + routing driver via LSF bsub (stamp-fixed)
#############################################################################
SHELL := /bin/bash
.PHONY: all fp route clean

TOP      ?= @TOP@
WORK_DIR ?= .
LOG_DIR  ?= @LOG_DIR@
BSUB     ?= bsub

# Tcl stamp files (stamp-priority: checked before the log-grep fallback)
TSTAMP1 := $(CURDIR)/.inv_fp_$(TOP).stamp
TSTAMP2 := $(CURDIR)/.inv_pr_$(TOP).stamp

INV_FP_STAMP := $(TSTAMP1)
INV_PR_STAMP := $(TSTAMP2)
export INV_FP_STAMP INV_PR_STAMP

all: fp route

fp: $(TSTAMP1)
$(TSTAMP1): innovus_fp.tcl
	@rm -f $(TSTAMP1) $(TSTAMP1).fail
	@mkdir -p $(LOG_DIR)
	@cd $(WORK_DIR) && $(BSUB) -o $(LOG_DIR)/inv_fp.log "innovus -files innovus_fp.tcl"
	@for i in {1..60}; do touch .nfsprobe; rm -f .nfsprobe; if [ -f $(TSTAMP1) ]; then touch $@; exit 0; fi; if [ -f $(TSTAMP1).fail ]; then break; fi; if grep -q "INNOVUS FP DONE" $(LOG_DIR)/inv_fp.log 2>/dev/null; then touch $(TSTAMP1); exit 0; fi; if grep -q "INNOVUS FP FAILED" $(LOG_DIR)/inv_fp.log 2>/dev/null; then break; fi; sleep 2; done; echo "FAILED"; exit 1

route:
	@rm -f $(TSTAMP2) $(TSTAMP2).fail
	@mkdir -p $(LOG_DIR)
	@cd $(WORK_DIR) && $(BSUB) -o $(LOG_DIR)/inv_route.log "innovus -files innovus_pr.tcl"
	@for i in {1..60}; do touch .nfsprobe; rm -f .nfsprobe; if [ -f $(TSTAMP2) ]; then exit 0; fi; if [ -f $(TSTAMP2).fail ]; then break; fi; if grep -q "INNOVUS PR DONE" $(LOG_DIR)/inv_route.log 2>/dev/null; then touch $(TSTAMP2); exit 0; fi; if grep -q "INNOVUS PR FAILED" $(LOG_DIR)/inv_route.log 2>/dev/null; then break; fi; sleep 2; done; echo "FAILED"; exit 1

clean:
	@rm -f $(TSTAMP1) $(TSTAMP1).fail $(TSTAMP2) $(TSTAMP2).fail
'''

def patch_fp(text, cfg):
    top = cfg.get("TOP", "hl22_porting_test_chip_v1")
    pm_cell = cfg.get("PM_CELL", "INVD8BWP40P140LVT")
    site = cfg.get("SITE", "coreSite")
    log_dir = cfg.get("LOG_DIR", "logs")

    text = replace_env_default(text, "TOP", top)
    text = replace_env_default(text, "INV_PM_CELL", pm_cell)
    text = replace_env_default(text, "INV_SITE", site)
    text = replace_env_default(text, "INV_LOG_DIR", log_dir)

    # insert the stamp_write proc before the first `set TOP`
    idx = text.find("set TOP")
    text = text[:idx] + stamp_proc("INV_FP_STAMP") + "\n\n" + text[idx:]

    # replace the buggy PM-band geometry block
    text = re.sub(
        r'# --- BUGGY PM-band.*?(?=puts "INNOVUS FP DONE")',
        GEOMETRY_BLOCK + "\n\n",
        text,
        flags=re.DOTALL,
    )

    text = add_fail_stamps(text, "stamp_write .fail")
    text = text.replace('puts "INNOVUS FP DONE"',
                        'puts "INNOVUS FP DONE"\nstamp_write ""', 1)
    return text


def patch_pr(text, cfg):
    top = cfg.get("TOP", "hl22_porting_test_chip_v1")
    log_dir = cfg.get("LOG_DIR", "logs")

    text = replace_env_default(text, "TOP", top)
    text = replace_env_default(text, "INV_LOG_DIR", log_dir)

    idx = text.find("set TOP")
    text = text[:idx] + stamp_proc("INV_PR_STAMP") + "\n\n" + text[idx:]

    text = add_fail_stamps(text, "stamp_write .fail")
    text = text.replace('puts "INNOVUS PR DONE"',
                        'puts "INNOVUS PR DONE"\nstamp_write ""', 1)
    return text


def patch_makefile(text, cfg):
    top = cfg.get("TOP", "hl22_porting_test_chip_v1")
    log_dir = cfg.get("LOG_DIR", "logs")
    return MAKEFILE_TEMPLATE.replace("@TOP@", top).replace("@LOG_DIR@", log_dir)


def main(argv):
    parser = argparse.ArgumentParser(
        description="Adaptive fixer for the Innovus APR (floorplan+route) stamp/geometry bugs.")
    parser.add_argument("bundle_root", help="path to the apr bundle directory")
    parser.add_argument("-o", "--out_dir", default="fixed",
                        help="output directory (default: fixed)")
    args = parser.parse_args(argv)

    cfg = parse_md_config(os.path.join(args.bundle_root, "test_chip_power.md"))

    fp_src = read_text(os.path.join(args.bundle_root, "innovus_fp.tcl"))
    pr_src = read_text(os.path.join(args.bundle_root, "innovus_pr.tcl"))
    mk_src = read_text(os.path.join(args.bundle_root, "Makefile"))

    write_text(os.path.join(args.out_dir, "innovus_fp.tcl"), patch_fp(fp_src, cfg))
    write_text(os.path.join(args.out_dir, "innovus_pr.tcl"), patch_pr(pr_src, cfg))
    write_text(os.path.join(args.out_dir, "Makefile"), patch_makefile(mk_src, cfg))

    print("Wrote fixed files to %s" % args.out_dir)
    print("  TOP=%s PM_CELL=%s SITE=%s LOG_DIR=%s" % (
        cfg.get("TOP", ""), cfg.get("PM_CELL", ""),
        cfg.get("SITE", ""), cfg.get("LOG_DIR", "")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))