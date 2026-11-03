#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-AprStampFix-001 (pnr_signoff, L3).

Innovus APR flow *fix*: stamp-mechanism + PM-band geometry (battery dbGet +
LEF SITE fallback + DBU normalization) + Makefile retry-loop rewrite.

B-grade synthesized, faithful to trace 1793706326923_qiqs7 (alan3zh,
hfeg0pkn001, mc=470, pnr_signoff) where the user's first real turn was a
debug report ("innovus floorplan FAILED -- see inv_fp.log, no route log"),
which violates A-grade rule 2 (root-cause-pointed), so we synthesize a
self-contained buggy bundle and ask the SUT to write a generic adaptive
patcher that fixes the 3 real bugs.

Distinct from:
- AprLogAudit-001 (z5wxj, r40)  : audit post-run LOGS      (verb: audit-log)
- AprSetupAudit-001 (97tse, r41): audit pre-flight INPUTS   (verb: audit-setup)
- AprStampFix-001   (qiqs7, r45): FIX the flow (verb: fix)   -- this case

Creates:
  assets/<id>/                  (A bundle, buggy)
  assets/<id>/hidden/           (B bundle, buggy, structurally different)
  reference/<id>/fix_apr_stamp.py
  reference/<id>/fixed/{innovus_fp.tcl, innovus_pr.tcl, Makefile}
  reference/<id>/reference_submit.zip
  reference/<id>/check.py
  reference/<id>/negative/*.zip  (5)
  reference/<id>/negative_selftest.py
"""
import os, sys, re, json, zipfile, subprocess, tempfile, shutil, py_compile

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID  = "EDA-Eval-DesignFlow-AprStampFix-001"
A_DIR   = os.path.join(ROOT, "assets", CID)
B_DIR   = os.path.join(A_DIR, "hidden")
REF_DIR = os.path.join(ROOT, "reference", CID)

# ---------------------------------------------------------------------------
# Configs (faithful to qiqs7 real test_chip_v1; B is synthesized, structurally
# different TOP / PM cell / SITE / log dir).
# ---------------------------------------------------------------------------
A_CFG = dict(TOP="hl22_porting_test_chip_v1",
             PM_CELL="INVD8BWP40P140LVT",
             SITE="coreSite",
             LOG_DIR="logs")
B_CFG = dict(TOP="hl22_porting_test_chip_v2",
             PM_CELL="INVD16BWP40P140LVT",
             SITE="coreSite_v2",
             LOG_DIR="run_logs")

def md_text(cfg):
    return (
        "# test_chip_power -- HL22 porting Innovus APR config\n\n"
        "```sh\n"
        "TOP=%(TOP)s\n"
        "PM_CELL=%(PM_CELL)s\n"
        "SITE=%(SITE)s\n"
        "LOG_DIR=%(LOG_DIR)s\n"
        "PDK_ROOT_PATH=pdk\n"
        "NETLIST=netlist/hl22_postsyn.v\n"
        "TECH_LEF=pdk/tech.tlef\n"
        "LEF_FILE=pdk/stdcells.lef\n"
        "SDC_FILE=sdc/hl22.mapped.sdc\n"
        "```\n" % cfg
    )

# ---------------------------------------------------------------------------
# BUGGY bundle files (faithful to qiqs7 real bugs)
# ---------------------------------------------------------------------------
def buggy_fp_tcl(cfg):
    return """\
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

set TOP     [env_or TOP  "%(TOP)s"]
set PM_CELL [env_or INV_PM_CELL "%(PM_CELL)s"]
set SITE    [env_or INV_SITE "%(SITE)s"]
set LOG_DIR [env_or INV_LOG_DIR "%(LOG_DIR)s"]

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
""" % cfg

def buggy_pr_tcl(cfg):
    return """\
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

set TOP     [env_or TOP  "%(TOP)s"]
set LOG_DIR [env_or INV_LOG_DIR "%(LOG_DIR)s"]

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
""" % cfg

def buggy_makefile(cfg):
    return """\
#############################################################################
# Makefile -- Innovus floorplan + routing driver via LSF bsub
#   BUGGY (qiqs7): 30s grep-only retry loop (no stamp check, no NFS refresh)
#############################################################################
SHELL := /bin/bash
.PHONY: all fp route clean

TOP      ?= %(TOP)s
WORK_DIR ?= .
LOG_DIR  ?= %(LOG_DIR)s
BSUB     ?= bsub

S1 := $(CURDIR)/.inv_fp_$(TOP).stamp

all: fp route

fp: $(S1)
$(S1): innovus_fp.tcl
	@rm -f $(S1)
	@mkdir -p $(LOG_DIR)
	@cd $(WORK_DIR) && $(BSUB) -o $(LOG_DIR)/inv_fp.log "innovus -files innovus_fp.tcl"
	@for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do \\
	  if grep -q "INNOVUS FP DONE" $(LOG_DIR)/inv_fp.log 2>/dev/null; then touch $@; exit 0; fi; \\
	  if grep -q "INNOVUS FP FAILED" $(LOG_DIR)/inv_fp.log 2>/dev/null; then break; fi; \\
	  sleep 2; \\
	done; \\
	echo "FAILED"; exit 1

route:
	@mkdir -p $(LOG_DIR)
	@cd $(WORK_DIR) && $(BSUB) -o $(LOG_DIR)/inv_route.log "innovus -files innovus_pr.tcl"
	@for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do \\
	  if grep -q "INNOVUS PR DONE" $(LOG_DIR)/inv_route.log 2>/dev/null; then exit 0; fi; \\
	  if grep -q "INNOVUS PR FAILED" $(LOG_DIR)/inv_route.log 2>/dev/null; then break; fi; \\
	  sleep 2; \\
	done; \\
	echo "FAILED"; exit 1

clean:
	@rm -f $(S1)
""" % cfg

# Minimal supporting files so the buggy bundle is self-consistent
TECH_TLEF = "MACRO BLOCK 0.0 0.0 ;\n"
STDCELLS_LEF = (
    "MACRO INVD8BWP40P140LVT\n  CLASS CORE ;\n  SIZE 0.48 BY 1.44 ;\n  SYMMETRY X Y R90 ;\n  SITE coreSite ;\nEND INVD8BWP40P140LVT\n"
    "MACRO INVD16BWP40P140LVT\n  CLASS CORE ;\n  SIZE 0.96 BY 1.44 ;\n  SYMMETRY X Y R90 ;\n  SITE coreSite_v2 ;\nEND INVD16BWP40P140LVT\n"
    "SITE coreSite\n  SIZE 0.24 BY 1.44 ;\n  SYMMETRY Y ;\nEND coreSite\n"
    "SITE coreSite_v2\n  SIZE 0.24 BY 2.88 ;\n  SYMMETRY Y ;\nEND coreSite_v2\n"
)
NETLIST_V = "module hl22_porting_test_chip_v1(input clk, input rst_n);\nendmodule\n"
NETLIST_V_B = "module hl22_porting_test_chip_v2(input clk, input rst_n);\nendmodule\n"
SDC = "create_clock -name clk -period 2 [get_ports clk]\n"
MMMC = "set TOP hl22_porting_test_chip_v1\n"

# ---------------------------------------------------------------------------
# FIXED files (the patcher's output target; reference for self-test)
# ---------------------------------------------------------------------------
STAMP_PROC_FP = """\
proc stamp_write {suffix} {
    if {[info exists ::env(INV_FP_STAMP)] && $::env(INV_FP_STAMP) ne ""} {
        if {[catch {close [open "$::env(INV_FP_STAMP)$suffix" w]} err]} {
            puts "WARN: cannot write stamp $::env(INV_FP_STAMP)$suffix : $err"
        }
    }
}
"""
STAMP_PROC_PR = """\
proc stamp_write {suffix} {
    if {[info exists ::env(INV_PR_STAMP)] && $::env(INV_PR_STAMP) ne ""} {
        if {[catch {close [open "$::env(INV_PR_STAMP)$suffix" w]} err]} {
            puts "WARN: cannot write stamp $::env(INV_PR_STAMP)$suffix : $err"
        }
    }
}
"""


def _sub(tpl, cfg):
    return (tpl.replace("__TOP__", cfg["TOP"])
              .replace("__PM_CELL__", cfg["PM_CELL"])
              .replace("__SITE__", cfg["SITE"])
              .replace("__LOG_DIR__", cfg["LOG_DIR"]))

def fixed_fp_tcl(cfg):
    return """\
#############################################################################
# innovus_fp.tcl -- FIXED (qiqs7): stamp mechanism + PM-band geometry
#   battery dbGet (rows + coreBox, multi-spelling) + LEF SITE fallback +
#   DBU -> um normalization + direction escape valve
#############################################################################
proc env_or {name default} {
    if {[info exists ::env($name)]} {
        set v [string trim $::env($name)]
        if {$v ne ""} { return $v }
    }
    return $default
}

%(stamp)s
set TOP     [env_or TOP  "__TOP__"]
set PM_CELL [env_or INV_PM_CELL "__PM_CELL__"]
set SITE    [env_or INV_SITE "__SITE__"]
set LOG_DIR [env_or INV_LOG_DIR "__LOG_DIR__"]

# --- required inputs (FAILED exit WITH stamp) ---
foreach f [list "pdk/tech.tlef" "pdk/stdcells.lef" "netlist/hl22_postsyn.v" "sdc/hl22.mapped.sdc"] {
    if {![file exists $f]} {
        stamp_write .fail
        puts "INNOVUS FP FAILED: missing required input $f"
        exit 1
    }
}
if {![file exists "mmmc.view"]} {
    stamp_write .fail
    puts "INNOVUS FP FAILED: missing mmmc.view"
    exit 1
}
if {![file exists "$LEF_FILE"] && ![file exists "pdk/stdcells.lef"]} {
    stamp_write .fail
    puts "INNOVUS FP FAILED: missing LEF"
    exit 1
}
if {![file exists "$TECH_LEF"] && ![file exists "pdk/tech.tlef"]} {
    stamp_write .fail
    puts "INNOVUS FP FAILED: missing TECH_LEF"
    exit 1
}

puts "INNOVUS FP: init_design + floorplan"

if {[catch {puts "floorplan ok"} err]} {
    stamp_write .fail
    puts "INNOVUS FP FAILED: floorplan error $err"
    exit 1
}

# --- PM-band geometry: battery dbGet (rows multi-path + coreBox multi-form) ---
set _dbu_per_um [expr {[dbGet head.dbUperUU] > 0 ? [dbGet head.dbUperUU] : 2000}]
set _dbu_per_um [expr {double($_dbu_per_um)}]

proc _row_get {row} {
    set ox [dbGet $row.origin_x]
    if {$ox eq ""} { set ox [lindex [dbGet $row.origin] 0] }
    set oy [dbGet $row.origin_y]
    if {$oy eq ""} { set oy [lindex [dbGet $row.origin] 1] }
    if {$oy eq ""} { set bbox [dbGet $row.bbox]; set oy [lindex $bbox 1] }
    set or_ [dbGet $row.orient]
    if {$or_ eq ""} { set or_ [dbGet $row.orientation] }
    return [list $ox $oy $or_]
}

set rows {}
if {![catch {dbGet top.fPlan.rows} _r] && [llength $_r] > 0} {
    foreach row $_r { lappend rows [_row_get $row] }
}
if {[llength $rows] == 0 && ![catch {dbGet top.rows} _r2] && [llength $_r2] > 0} {
    foreach row $_r2 { lappend rows [_row_get $row] }
}

# core box: 4-list then scalar fallback
set cb {}
if {![catch {dbGet top.fPlan.coreBox} _cb] && [llength $_cb] >= 4} { set cb $_cb }
if {[llength $cb] != 4} {
    if {![catch {dbGet top.fPlan.coreBox.lx} _lx]} {
        set cb [list $_lx [dbGet top.fPlan.coreBox.ly] [dbGet top.fPlan.coreBox.ux] [dbGet top.fPlan.coreBox.uy]]
    }
}
# DBU -> um normalization (coords > 500 treated as DBU)
set _cb_um {}
foreach c $cb {
    if {[string is double -strict $c] && $c > 500} {
        lappend _cb_um [expr {$c / $_dbu_per_um}]
    } else {
        lappend _cb_um $c
    }
}

# LEF SITE fallback (deterministic derivation from floorPlan + LEF SIZE/SYMMETRY)
set _site $SITE
if {![catch {lefGet $_site SIZE} _sz] && [llength $_sz] >= 2} {
    puts "INNOVUS FP: LEF SITE $_site SIZE $_sz"
}
if {![catch {lefGet $_site SYMMETRY} _sym]} {
    puts "INNOVUS FP: LEF SITE $_site SYMMETRY $_sym"
}

# direction escape valve (env override first, then row0 orient)
set _row0_orient [env_or INV_PM_ROW0_ORIENT ""]
if {$_row0_orient eq "" && [llength $rows] > 0} {
    set _row0_orient [lindex [lindex $rows 0] 2]
}
if {$_row0_orient eq ""} {
    puts "WARN: PM band: cannot resolve row0 orientation -- skipping PM band (safe)"
} else {
    puts "INNOVUS FP: PM band cell=$PM_CELL orient=$_row0_orient rows=[llength $rows] corebox_um=$_cb_um"
}

puts "INNOVUS FP DONE"
stamp_write ""
""" % dict(stamp=STAMP_PROC_FP)

def fixed_pr_tcl(cfg):
    return """\
#############################################################################
# innovus_pr.tcl -- FIXED (qiqs7): stamp mechanism on all FAILED exits + DONE
#############################################################################
proc env_or {name default} {
    if {[info exists ::env($name)]} {
        set v [string trim $::env($name)]
        if {$v ne ""} { return $v }
    }
    return $default
}

%(stamp)s
set TOP     [env_or TOP  "__TOP__"]
set LOG_DIR [env_or INV_LOG_DIR "__LOG_DIR__"]

# --- required inputs (FAILED WITH stamp) ---
foreach f [list "pdk/tech.tlef" "pdk/stdcells.lef" "netlist/hl22_postsyn.v" "sdc/hl22.mapped.sdc" "mmmc.view"] {
    if {![file exists $f]} {
        stamp_write .fail
        puts "INNOVUS PR FAILED: missing required input $f"
        exit 1
    }
}

puts "INNOVUS PR: init_design"
if {[catch {puts "init ok"} err]} {
    stamp_write .fail
    puts "INNOVUS PR FAILED: init_design error $err"
    exit 1
}

puts "INNOVUS PR: place"
if {[catch {puts "place ok"} err]} {
    stamp_write .fail
    puts "INNOVUS PR FAILED: place error $err"
    exit 1
}

puts "INNOVUS PR: CTS"
if {[catch {puts "CTS ok"} err]} {
    stamp_write .fail
    puts "INNOVUS PR FAILED: CTS error $err"
    exit 1
}

puts "INNOVUS PR: route"
if {[catch {puts "route ok"} err]} {
    stamp_write .fail
    puts "INNOVUS PR FAILED: route error $err"
    exit 1
}

puts "INNOVUS PR: output write"
if {[catch {puts "write ok"} err]} {
    stamp_write .fail
    puts "INNOVUS PR FAILED: output write error $err"
    exit 1
}

puts "INNOVUS PR: verify"
if {[catch {puts "verify ok"} err]} {
    stamp_write .fail
    puts "INNOVUS PR FAILED: verify error $err"
    exit 1
}

puts "INNOVUS PR DONE"
stamp_write ""
""" % dict(stamp=STAMP_PROC_PR)

def fixed_makefile(cfg):
    return """\
#############################################################################
# Makefile -- Innovus floorplan + routing driver (FIXED, qiqs7)
#   60x2s=120s retry window ; stamp-priority (Tcl stamp first, log-grep guard)
#   .fail break ; NFS refresh (touch+rm .nfsprobe)
#############################################################################
SHELL := /bin/bash
.PHONY: all fp route clean

TOP      ?= __TOP__
WORK_DIR ?= .
LOG_DIR  ?= __LOG_DIR__
BSUB     ?= bsub

S1 := $(CURDIR)/.inv_fp_$(TOP).stamp
TSTAMP1 := $(WORK_DIR)/.inv_fp_$(TOP).tclstamp
INV_FP_STAMP := $(TSTAMP1)
export INV_FP_STAMP

S2 := $(CURDIR)/.inv_pr_$(TOP).stamp
TSTAMP2 := $(WORK_DIR)/.inv_pr_$(TOP).tclstamp
INV_PR_STAMP := $(TSTAMP2)
export INV_PR_STAMP

all: fp route

fp:
	@rm -f $(S1) $(TSTAMP1) $(TSTAMP1).fail
	@mkdir -p $(LOG_DIR)
	@cd $(WORK_DIR) && $(BSUB) -o $(LOG_DIR)/inv_fp.log "innovus -files innovus_fp.tcl"
	@for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60; do \\
	  if [ -f "$(TSTAMP1)" ]; then touch $(S1) && echo "done (tcl stamp)"; exit 0; fi; \\
	  if grep -q "INNOVUS FP DONE" $(LOG_DIR)/inv_fp.log 2>/dev/null; then touch $(S1); echo "done (log grep)"; exit 0; fi; \\
	  if [ -f "$(TSTAMP1).fail" ] || grep -q "INNOVUS FP FAILED" $(LOG_DIR)/inv_fp.log 2>/dev/null; then break; fi; \\
	  touch $(WORK_DIR)/.nfsprobe $(LOG_DIR)/.nfsprobe 2>/dev/null; \\
	  rm -f $(WORK_DIR)/.nfsprobe $(LOG_DIR)/.nfsprobe 2>/dev/null; \\
	  sleep 2; \\
	done; \\
	echo "FAILED"; exit 1

route:
	@rm -f $(S2) $(TSTAMP2) $(TSTAMP2).fail
	@mkdir -p $(LOG_DIR)
	@cd $(WORK_DIR) && $(BSUB) -o $(LOG_DIR)/inv_route.log "innovus -files innovus_pr.tcl"
	@for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60; do \\
	  if [ -f "$(TSTAMP2)" ]; then touch $(S2) && echo "done (tcl stamp)"; exit 0; fi; \\
	  if grep -q "INNOVUS PR DONE" $(LOG_DIR)/inv_route.log 2>/dev/null; then touch $(S2); echo "done (log grep)"; exit 0; fi; \\
	  if [ -f "$(TSTAMP2).fail" ] || grep -q "INNOVUS PR FAILED" $(LOG_DIR)/inv_route.log 2>/dev/null; then break; fi; \\
	  touch $(WORK_DIR)/.nfsprobe $(LOG_DIR)/.nfsprobe 2>/dev/null; \\
	  rm -f $(WORK_DIR)/.nfsprobe $(LOG_DIR)/.nfsprobe 2>/dev/null; \\
	  sleep 2; \\
	done; \\
	echo "FAILED"; exit 1

clean:
	@rm -f $(S1) $(TSTAMP1) $(TSTAMP1).fail $(S2) $(TSTAMP2) $(TSTAMP2).fail
"""

# ---------------------------------------------------------------------------
# Reference patcher (fix_apr_stamp.py) -- adaptive generator
# ---------------------------------------------------------------------------
def _build_patcher():
    # Templates with __TOP__ / __PM_CELL__ / __SITE__ / __LOG_DIR__ placeholders.
    fp_tpl = fixed_fp_tcl(None)
    pr_tpl = fixed_pr_tcl(None)
    mk_tpl = fixed_makefile(None)
    # The stamp proc is injected via %(stamp)s in fixed_*_tcl; in the patcher we
    # embed STAMP_PROC_FP / STAMP_PROC_PR as their own string literals and
    # substitute into the template at gen time.
    fp_tpl_nostamp = fp_tpl.replace(STAMP_PROC_FP, "__STAMP_FP__")
    pr_tpl_nostamp = pr_tpl.replace(STAMP_PROC_PR, "__STAMP_PR__")

    header = '''#!/usr/bin/env python3
"""fix_apr_stamp.py -- generic adaptive Innovus APR flow fixer (qiqs7 style).

Reads a buggy bundle (test_chip_power.md + apr/{innovus_fp.tcl, innovus_pr.tcl,
Makefile}) and emits FIXED versions of the three files into fixed/.

Fixes 3 real qiqs7 bugs:
  1. stamp mechanism : add stamp_write proc + stamp_write .fail at every FAILED
                       exit + stamp_write "" before DONE banner.
  2. PM-band geometry: battery dbGet (top.fPlan.rows + top.rows multi-path,
                       origin/origin_y/bbox fallback) + coreBox multi-form +
                       DBU -> um normalization (dbGet head.dbUperUU) +
                       LEF SITE SIZE/SYMMETRY fallback + direction escape valve.
  3. Makefile retry  : 60x2s=120s window, stamp-priority (Tcl stamp first,
                       log-grep guard), .fail break, NFS refresh (.nfsprobe).

The patcher is ADAPTIVE: it reads TOP / PM_CELL / SITE / LOG_DIR from the
bundle's test_chip_power.md and bakes those into the emitted fixed files, so
the same patcher fixes any structurally-different bundle (cross-input guard).

CLI:  fix_apr_stamp.py <bundle_root> [-o <out_dir>]
"""
import os, re, sys, argparse

VAR_RE = re.compile(r"^\\s*([A-Z_][A-Z0-9_]*)\\s*=\\s*(.+?)\\s*$")
CFG_FENCE_RE = re.compile(r"^```sh\\s*$", re.MULTILINE)


def parse_cfg(md_path):
    cfg = dict(TOP="hl22_porting_test_chip_v1", PM_CELL="INVD8BWP40P140LVT",
               SITE="coreSite", LOG_DIR="logs")
    if not os.path.isfile(md_path):
        return cfg
    txt = open(md_path, errors="replace").read()
    m = CFG_FENCE_RE.search(txt)
    block = txt[m.end():] if m else txt
    end = block.find("```")
    if end != -1:
        block = block[:end]
    for ln in block.splitlines():
        mm = VAR_RE.match(ln)
        if mm:
            cfg[mm.group(1)] = mm.group(2).strip()
    cfg["PM_CELL"] = cfg.get("PM_CELL", "INVD8BWP40P140LVT")
    cfg["SITE"] = cfg.get("SITE", "coreSite")
    cfg["LOG_DIR"] = cfg.get("LOG_DIR", "logs")
    cfg["TOP"] = cfg.get("TOP", "hl22_porting_test_chip_v1")
    return cfg


def _sub(tpl, cfg):
    return (tpl.replace("__TOP__", cfg["TOP"])
              .replace("__PM_CELL__", cfg["PM_CELL"])
              .replace("__SITE__", cfg["SITE"])
              .replace("__LOG_DIR__", cfg["LOG_DIR"]))
'''

    # Embed stamp procs and templates as triple-single-quoted raw strings.
    # None of them contain ''' or backslashes, so r''' is safe.
    stamp_fp_lit = "r'''" + STAMP_PROC_FP + "'''"
    stamp_pr_lit = "r'''" + STAMP_PROC_PR + "'''"
    fp_lit = "r'''" + fp_tpl_nostamp + "'''"
    pr_lit = "r'''" + pr_tpl_nostamp + "'''"
    mk_lit = "r'''" + mk_tpl + "'''"

    body = '''
STAMP_FP = %(stamp_fp)s
STAMP_PR = %(stamp_pr)s
_FP_TEMPLATE = %(fp)s
_PR_TEMPLATE = %(pr)s
_MK_TEMPLATE = %(mk)s


def gen_fp(cfg):
    return _sub(_FP_TEMPLATE, cfg).replace("__STAMP_FP__", STAMP_FP)


def gen_pr(cfg):
    return _sub(_PR_TEMPLATE, cfg).replace("__STAMP_PR__", STAMP_PR)


def gen_makefile(cfg):
    return _sub(_MK_TEMPLATE, cfg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle_root")
    ap.add_argument("-o", "--out", default="fixed")
    args = ap.parse_args()

    root = os.path.abspath(args.bundle_root)
    cfg = parse_cfg(os.path.join(root, "test_chip_power.md"))

    out_dir = args.out
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "innovus_fp.tcl"), "w") as f:
        f.write(gen_fp(cfg))
    with open(os.path.join(out_dir, "innovus_pr.tcl"), "w") as f:
        f.write(gen_pr(cfg))
    with open(os.path.join(out_dir, "Makefile"), "w") as f:
        f.write(gen_makefile(cfg))
    print("fixed written for TOP=%%s PM_CELL=%%s SITE=%%s LOG_DIR=%%s"
          %% (cfg["TOP"], cfg["PM_CELL"], cfg["SITE"], cfg["LOG_DIR"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
''' % dict(stamp_fp=stamp_fp_lit, stamp_pr=stamp_pr_lit,
           fp=fp_lit, pr=pr_lit, mk=mk_lit)
    return header + body


FIX_PATCHER = _build_patcher()

# ---------------------------------------------------------------------------
# Build assets
# ---------------------------------------------------------------------------
def write_assets():
    # A bundle
    os.makedirs(os.path.join(A_DIR, "apr"), exist_ok=True)
    os.makedirs(os.path.join(A_DIR, "pdk"), exist_ok=True)
    os.makedirs(os.path.join(A_DIR, "netlist"), exist_ok=True)
    os.makedirs(os.path.join(A_DIR, "sdc"), exist_ok=True)
    with open(os.path.join(A_DIR, "test_chip_power.md"), "w") as f:
        f.write(md_text(A_CFG))
    with open(os.path.join(A_DIR, "apr", "innovus_fp.tcl"), "w") as f:
        f.write(buggy_fp_tcl(A_CFG))
    with open(os.path.join(A_DIR, "apr", "innovus_pr.tcl"), "w") as f:
        f.write(buggy_pr_tcl(A_CFG))
    with open(os.path.join(A_DIR, "apr", "Makefile"), "w") as f:
        f.write(buggy_makefile(A_CFG))
    with open(os.path.join(A_DIR, "apr", "mmmc.view.template"), "w") as f:
        f.write(MMMC)
    with open(os.path.join(A_DIR, "pdk", "tech.tlef"), "w") as f:
        f.write(TECH_TLEF)
    with open(os.path.join(A_DIR, "pdk", "stdcells.lef"), "w") as f:
        f.write(STDCELLS_LEF)
    with open(os.path.join(A_DIR, "netlist", "hl22_postsyn.v"), "w") as f:
        f.write(NETLIST_V)
    with open(os.path.join(A_DIR, "sdc", "hl22.mapped.sdc"), "w") as f:
        f.write(SDC)

    # B bundle (hidden, structurally different)
    os.makedirs(os.path.join(B_DIR, "apr"), exist_ok=True)
    os.makedirs(os.path.join(B_DIR, "pdk"), exist_ok=True)
    os.makedirs(os.path.join(B_DIR, "netlist"), exist_ok=True)
    os.makedirs(os.path.join(B_DIR, "sdc"), exist_ok=True)
    with open(os.path.join(B_DIR, "test_chip_power.md"), "w") as f:
        f.write(md_text(B_CFG))
    with open(os.path.join(B_DIR, "apr", "innovus_fp.tcl"), "w") as f:
        f.write(buggy_fp_tcl(B_CFG))
    with open(os.path.join(B_DIR, "apr", "innovus_pr.tcl"), "w") as f:
        f.write(buggy_pr_tcl(B_CFG))
    with open(os.path.join(B_DIR, "apr", "Makefile"), "w") as f:
        f.write(buggy_makefile(B_CFG))
    with open(os.path.join(B_DIR, "apr", "mmmc.view.template"), "w") as f:
        f.write("set TOP hl22_porting_test_chip_v2\n")
    with open(os.path.join(B_DIR, "pdk", "tech.tlef"), "w") as f:
        f.write(TECH_TLEF)
    with open(os.path.join(B_DIR, "pdk", "stdcells.lef"), "w") as f:
        f.write(STDCELLS_LEF)
    with open(os.path.join(B_DIR, "netlist", "hl22_postsyn.v"), "w") as f:
        f.write(NETLIST_V_B)
    with open(os.path.join(B_DIR, "sdc", "hl22.mapped.sdc"), "w") as f:
        f.write(SDC)


def write_reference():
    if os.path.isdir(REF_DIR):
        shutil.rmtree(REF_DIR)
    os.makedirs(os.path.join(REF_DIR, "fixed"), exist_ok=True)
    os.makedirs(os.path.join(REF_DIR, "negative"), exist_ok=True)
    with open(os.path.join(REF_DIR, "fix_apr_stamp.py"), "w") as f:
        f.write(FIX_PATCHER)
    # reference fixed files (for self-test / inspection)
    with open(os.path.join(REF_DIR, "fixed", "innovus_fp.tcl"), "w") as f:
        f.write(_sub(fixed_fp_tcl(A_CFG), A_CFG))
    with open(os.path.join(REF_DIR, "fixed", "innovus_pr.tcl"), "w") as f:
        f.write(_sub(fixed_pr_tcl(A_CFG), A_CFG))
    with open(os.path.join(REF_DIR, "fixed", "Makefile"), "w") as f:
        f.write(_sub(fixed_makefile(A_CFG), A_CFG))
    # reference_submit.zip = patcher + fixed files (what a correct SUT submits)
    zpath = os.path.join(REF_DIR, "reference_submit.zip")
    if os.path.isfile(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(REF_DIR, "fix_apr_stamp.py"), "fix_apr_stamp.py")
        z.write(os.path.join(REF_DIR, "fixed", "innovus_fp.tcl"), "fixed/innovus_fp.tcl")
        z.write(os.path.join(REF_DIR, "fixed", "innovus_pr.tcl"), "fixed/innovus_pr.tcl")
        z.write(os.path.join(REF_DIR, "fixed", "Makefile"), "fixed/Makefile")


# ---------------------------------------------------------------------------
# check.py
# ---------------------------------------------------------------------------
CHECK_PY = r'''#!/usr/bin/env python3
"""check.py - grader for EDA-Eval-DesignFlow-AprStampFix-001.

Deliverable: submit.zip containing fix_apr_stamp.py (generic adaptive Innovus
APR flow *fixer*, CLI `fix_apr_stamp.py <bundle_root> [-o out_dir]`) and a
fixed/ tree with the 3 patched files (innovus_fp.tcl, innovus_pr.tcl, Makefile)
for the VISIBLE A bundle.

Judgment: runs the candidate's fix_apr_stamp.py on visible A and hidden B
(subprocess, real interpreter), then `tclsh info complete` on the emitted Tcl
(real tclsh) and `make -n` dry-run on the emitted Makefile (real make). 15
independent conditions (a)-(o).

Distinct from AprLogAudit-001 (audit LOGS) and AprSetupAudit-001 (audit
SETUP INPUTS): this case asks the SUT to FIX the flow -- emit patched
Tcl/Makefile that add the stamp mechanism, rewrite the PM-band geometry block,
and rewrite the Makefile retry loop. The patcher must be ADAPTIVE (read
TOP/PM_CELL/SITE/LOG_DIR from the bundle config) so the same patcher fixes a
structurally-different hidden B (cross-input guard).
"""
import os, re, sys, zipfile, subprocess, tempfile, py_compile, shutil

CID = "EDA-Eval-DesignFlow-AprStampFix-001"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "..", "assets", CID))
A_DIR = ASSETS
B_DIR = os.path.join(ASSETS, "hidden")


def _run(cmd, cwd, timeout=120):
    try:
        r = subprocess.run(["bash", "-lc", cmd], cwd=cwd,
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)


def _extract(zip_path, dest):
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(dest)


def check(deliverable, workdir):
    """deliverable: 'outputs/submit.zip' (path rel to workdir). workdir: session cwd."""
    p = os.path.join(workdir, deliverable)
    if not os.path.isfile(p):
        raise FileNotFoundError("deliverable not found: " + deliverable)

    tmp = tempfile.mkdtemp(prefix="chk_aprfix_")
    try:
        _extract(p, tmp)
        # (a) submit.zip contains fix_apr_stamp.py + fixed/{fp.tcl, pr.tcl, Makefile}
        need = ["fix_apr_stamp.py", "fixed/innovus_fp.tcl",
                "fixed/innovus_pr.tcl", "fixed/Makefile"]
        missing = [n for n in need if not os.path.isfile(os.path.join(tmp, n))]
        assert not missing, "(a) submit.zip missing: " + ", ".join(missing)

        patcher = os.path.join(tmp, "fix_apr_stamp.py")
        fixedA = os.path.join(tmp, "fixed")  # A fixed tree already in zip

        # (b) fix_apr_stamp.py compiles
        py_compile.compile(patcher, doraise=True)

        # (c) subprocess run patcher on A bundle -> exit0 + produces fixed files
        runA = tempfile.mkdtemp(prefix="runA_")
        rc, out, err = _run("python3 %s %s -o %s" % (patcher, A_DIR, runA), tmp)
        assert rc == 0, "(c) patcher on A failed rc=%d err=%s" % (rc, err[:300])
        for fn in ("innovus_fp.tcl", "innovus_pr.tcl", "Makefile"):
            assert os.path.isfile(os.path.join(runA, fn)), \
                "(c) patcher on A did not emit %s" % fn

        # (d) tclsh info complete on fixed/innovus_fp.tcl (A) -> COMPLETE-OK
        fpA = os.path.join(runA, "innovus_fp.tcl")
        _tcl = 'set fd [open %s r]; set s [read $fd]; close $fd; puts [info complete $s]' % fpA
        rc, out, err = _run('echo %s | tclsh' % __import__("shlex").quote(_tcl), runA)
        assert rc == 0 and "1" in out, \
            "(d) tclsh info complete on fixed fp.tcl(A) failed: rc=%d out=%s err=%s" % (rc, out, err[:200])

        # (e) tclsh info complete on fixed/innovus_pr.tcl (A) -> COMPLETE-OK
        prA = os.path.join(runA, "innovus_pr.tcl")
        _tcl2 = 'set fd [open %s r]; set s [read $fd]; close $fd; puts [info complete $s]' % prA
        rc, out, err = _run('echo %s | tclsh' % __import__("shlex").quote(_tcl2), runA)
        assert rc == 0 and "1" in out, \
            "(e) tclsh info complete on fixed pr.tcl(A) failed: rc=%d out=%s err=%s" % (rc, out, err[:200])

        fpA_txt = open(fpA).read()
        prA_txt = open(prA).read()
        mkA = open(os.path.join(runA, "Makefile")).read()

        # (f) fixed fp.tcl has `proc stamp_write` + >=5 `stamp_write .fail`
        assert re.search(r"proc\s+stamp_write", fpA_txt), "(f) fp.tcl missing proc stamp_write"
        n_fail_fp = len(re.findall(r"stamp_write\s+\.fail", fpA_txt))
        assert n_fail_fp >= 5, "(f) fp.tcl stamp_write .fail count=%d <5" % n_fail_fp

        # (g) fixed fp.tcl geometry block: battery dbGet (top.fPlan.rows + top.rows)
        #     + LEF SITE fallback (lefGet + SIZE + SYMMETRY) + DBU normalization
        assert "top.fPlan.rows" in fpA_txt and "top.rows" in fpA_txt, \
            "(g) fp.tcl geometry missing battery dbGet (top.fPlan.rows + top.rows)"
        assert re.search(r"lefGet\s+\$_site\s+SIZE", fpA_txt) or "lefGet" in fpA_txt, \
            "(g) fp.tcl geometry missing LEF SITE fallback (lefGet)"
        assert "SYMMETRY" in fpA_txt, "(g) fp.tcl geometry missing LEF SYMMETRY"
        assert "dbUperUU" in fpA_txt and re.search(r"/\s*\$_dbu_per_um", fpA_txt), \
            "(g) fp.tcl geometry missing DBU normalization (dbUperUU / /$_dbu_per_um)"

        # (h) fixed pr.tcl has stamp_write proc + >=7 stamp_write .fail
        assert re.search(r"proc\s+stamp_write", prA_txt), "(h) pr.tcl missing proc stamp_write"
        n_fail_pr = len(re.findall(r"stamp_write\s+\.fail", prA_txt))
        assert n_fail_pr >= 7, "(h) pr.tcl stamp_write .fail count=%d <7" % n_fail_pr

        # (i) fixed Makefile retry loop: stamp-priority (TSTAMP1 first) +
        #     window>=120s (60x2 or sleep >=120) + NFS refresh (.nfsprobe touch+rm) +
        #     .fail break
        assert "TSTAMP1" in mkA and re.search(r'if\s+\[\s*-f\s+"\$\(TSTAMP1\)"', mkA), \
            "(i) Makefile missing stamp-priority (TSTAMP1 first check)"
        # window: 60x2 or sleep 2 with 60 iterations, or total >=120
        has_60 = bool(re.search(r"\b60\b", mkA)) and "sleep 2" in mkA
        assert has_60, "(i) Makefile retry window < 120s (need 60x2)"
        assert ".nfsprobe" in mkA and "touch" in mkA and "rm -f" in mkA, \
            "(i) Makefile missing NFS refresh (.nfsprobe touch+rm)"
        assert ".fail" in mkA and "break" in mkA, "(i) Makefile missing .fail break"

        # (j) make -n dry-run on fixed Makefile (stub vars) -> no syntax error
        mkA_dir = tempfile.mkdtemp(prefix="mkdryA_")
        shutil.copy(os.path.join(runA, "Makefile"), os.path.join(mkA_dir, "Makefile"))
        # create stub innovus_fp.tcl so target can be considered (phony, but safe)
        open(os.path.join(mkA_dir, "innovus_fp.tcl"), "w").write("# stub\n")
        rc, out, err = _run("make -n fp", mkA_dir)
        assert rc == 0, "(j) make -n on fixed Makefile failed rc=%d err=%s out=%s" % (rc, err[:200], out[:200])

        # (k) cross-input guard: run patcher on hidden B -> exit0; fixed B fp.tcl
        #     references B's TOP (hl22_porting_test_chip_v2), NOT A's TOP
        runB = tempfile.mkdtemp(prefix="runB_")
        rc, out, err = _run("python3 %s %s -o %s" % (patcher, B_DIR, runB), tmp)
        assert rc == 0, "(k) patcher on B failed rc=%d err=%s" % (rc, err[:300])
        fpB = os.path.join(runB, "innovus_fp.tcl")
        assert os.path.isfile(fpB), "(k) patcher on B did not emit fp.tcl"
        fpB_txt = open(fpB).read()
        assert "hl22_porting_test_chip_v2" in fpB_txt, \
            "(k) fixed B fp.tcl does not reference B's TOP (v2)"
        assert "hl22_porting_test_chip_v1" not in fpB_txt, \
            "(k) fixed B fp.tcl still references A's TOP (v1) -- hardcode leak"

        # (l) cross-input guard: fixed B Makefile references B's stamp/log paths,
        #     NOT A's (.inv_fp_hl22_porting_test_chip_v1)
        mkB = open(os.path.join(runB, "Makefile")).read()
        assert "hl22_porting_test_chip_v2" in mkB, "(l) fixed B Makefile missing B's TOP"
        assert "hl22_porting_test_chip_v1" not in mkB, \
            "(l) fixed B Makefile still references A's stamp path (v1) -- hardcode leak"
        assert B_DIR.endswith("hidden") and "run_logs" in mkB or "LOG_DIR" in mkB

        # (m) anti-hardcode: fixed A fp.tcl does NOT contain B's TOP; fixed B fp.tcl
        #     does NOT contain A's TOP
        assert "hl22_porting_test_chip_v2" not in fpA_txt, \
            "(m) fixed A fp.tcl contains B's TOP -- hardcode leak"
        assert "hl22_porting_test_chip_v1" not in fpB_txt, \
            "(m) fixed B fp.tcl contains A's TOP -- hardcode leak"

        # (n) fixed fp.tcl DONE banner has stamp_write (success stamp)
        #     find the DONE line and require a stamp_write call near it (after DONE)
        m_done = re.search(r'puts\s+"INNOVUS\s+FP\s+DONE"', fpA_txt)
        assert m_done, "(n) fp.tcl missing INNOVUS FP DONE banner"
        after = fpA_txt[m_done.end():]
        assert re.search(r'stamp_write\s+""', after), \
            "(n) fp.tcl DONE banner not followed by stamp_write \"\" (success stamp)"

        # (o) patcher adaptive: fixed A geometry references A's SITE/cell;
        #     fixed B references B's SITE/cell (different)
        assert "coreSite\"" in fpA_txt or "coreSite" in fpA_txt, \
            "(o) fixed A fp.tcl does not reference A's SITE (coreSite)"
        assert "INVD8BWP40P140LVT" in fpA_txt, \
            "(o) fixed A fp.tcl does not reference A's PM_CELL (INVD8BWP40P140LVT)"
        assert "coreSite_v2" in fpB_txt, \
            "(o) fixed B fp.tcl does not reference B's SITE (coreSite_v2)"
        assert "INVD16BWP40P140LVT" in fpB_txt, \
            "(o) fixed B fp.tcl does not reference B's PM_CELL (INVD16BWP40P140LVT)"

        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        # reference self-test mode: check('reference_submit.zip', REF_DIR)
        ref = os.path.join(HERE, "reference_submit.zip")
        if os.path.isfile(ref):
            print("self-test:", check("reference_submit.zip", HERE))
        else:
            print("no reference_submit.zip for self-test")
    else:
        print("usage: check.py  (self-test against reference_submit.zip)")
'''


def write_check():
    with open(os.path.join(REF_DIR, "check.py"), "w") as f:
        f.write(CHECK_PY)


# ---------------------------------------------------------------------------
# Negatives
# ---------------------------------------------------------------------------
def _zip_from_files(zpath, files):
    """files: dict arcname -> content (str)."""
    if os.path.isfile(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)


def build_negatives():
    neg_dir = os.path.join(REF_DIR, "negative")
    FP_A = _sub(fixed_fp_tcl(A_CFG), A_CFG)
    PR_A = _sub(fixed_pr_tcl(A_CFG), A_CFG)
    MK_A = _sub(fixed_makefile(A_CFG), A_CFG)

    # 1. fake_empty: empty zip (no files)
    _zip_from_files(os.path.join(neg_dir, "fake_empty.zip"), {"readme.txt": ""})

    # 2. fake_print_expected: patcher ignores bundle, always emits A's fixed files
    fake_print = (
        "#!/usr/bin/env python3\n"
        "import os, sys\n"
        "out = sys.argv[sys.argv.index('-o')+1] if '-o' in sys.argv else 'fixed'\n"
        "os.makedirs(out, exist_ok=True)\n"
        "# hardcoded A fixed files (ignore bundle)\n"
        + "open(os.path.join(out,'innovus_fp.tcl'),'w').write(" + repr(FP_A) + ")\n"
        + "open(os.path.join(out,'innovus_pr.tcl'),'w').write(" + repr(PR_A) + ")\n"
        + "open(os.path.join(out,'Makefile'),'w').write(" + repr(MK_A) + ")\n"
        "print('done')\n"
    )
    _zip_from_files(os.path.join(neg_dir, "fake_print_expected.zip"), {
        "fix_apr_stamp.py": fake_print,
        "fixed/innovus_fp.tcl": FP_A,
        "fixed/innovus_pr.tcl": PR_A,
        "fixed/Makefile": MK_A,
    })

    # 3. fake_core_deleted: patcher adds stamp but does NOT rewrite geometry block
    #    (keep buggy fp.tcl, only inject stamp_write proc + .fail + success stamp)
    def fp_no_geom(cfg):
        # take buggy fp.tcl and inject stamp_write proc + .fail calls + success stamp
        buggy = buggy_fp_tcl(cfg)
        buggy = buggy.replace("puts \"INNOVUS FP FAILED: missing required input $f\"",
                              "stamp_write .fail\n        puts \"INNOVUS FP FAILED: missing required input $f\"")
        buggy = buggy.replace("puts \"INNOVUS FP FAILED: missing mmmc.view\"",
                              "stamp_write .fail\n        puts \"INNOVUS FP FAILED: missing mmmc.view\"")
        # add stamp proc after env_or
        buggy = buggy.replace("proc env_or {name default} {\n    if {[info exists ::env($name)]} {\n        set v [string trim $::env($name)]\n        if {$v ne \"\"} { return $v }\n    }\n    return $default\n}\n",
                              "proc env_or {name default} {\n    if {[info exists ::env($name)]} {\n        set v [string trim $::env($name)]\n        if {$v ne \"\"} { return $v }\n    }\n    return $default\n}\n\n" + STAMP_PROC_FP)
        # add success stamp after DONE
        buggy = buggy.replace('puts "INNOVUS FP DONE"', 'puts "INNOVUS FP DONE"\nstamp_write ""')
        return buggy
    fake_core = (
        "#!/usr/bin/env python3\n"
        "import os, sys, re\n"
        "out = sys.argv[sys.argv.index('-o')+1] if '-o' in sys.argv else 'fixed'\n"
        "root = sys.argv[1]\n"
        "os.makedirs(out, exist_ok=True)\n"
        "# add stamp but keep buggy geometry (no rewrite)\n"
        + "open(os.path.join(out,'innovus_fp.tcl'),'w').write(" + repr(fp_no_geom(A_CFG)) + ")\n"
        + "open(os.path.join(out,'innovus_pr.tcl'),'w').write(" + repr(PR_A) + ")\n"
        + "open(os.path.join(out,'Makefile'),'w').write(" + repr(MK_A) + ")\n"
        "print('done')\n"
    )
    _zip_from_files(os.path.join(neg_dir, "fake_core_deleted.zip"), {
        "fix_apr_stamp.py": fake_core,
        "fixed/innovus_fp.tcl": fp_no_geom(A_CFG),
        "fixed/innovus_pr.tcl": PR_A,
        "fixed/Makefile": MK_A,
    })

    # 4. naive_hardcode_a: patcher just writes pre-baked A fixed files (no bundle read)
    naive_a = (
        "#!/usr/bin/env python3\n"
        "import os, sys\n"
        "out = sys.argv[sys.argv.index('-o')+1] if '-o' in sys.argv else 'fixed'\n"
        "os.makedirs(out, exist_ok=True)\n"
        + "open(os.path.join(out,'innovus_fp.tcl'),'w').write(" + repr(FP_A) + ")\n"
        + "open(os.path.join(out,'innovus_pr.tcl'),'w').write(" + repr(PR_A) + ")\n"
        + "open(os.path.join(out,'Makefile'),'w').write(" + repr(MK_A) + ")\n"
        "print('done')\n"
    )
    _zip_from_files(os.path.join(neg_dir, "naive_hardcode_a.zip"), {
        "fix_apr_stamp.py": naive_a,
        "fixed/innovus_fp.tcl": FP_A,
        "fixed/innovus_pr.tcl": PR_A,
        "fixed/Makefile": MK_A,
    })

    # 5. naive_no_stamp: patcher rewrites geometry but does NOT add stamp_write
    def fp_no_stamp(cfg):
        # take fixed fp.tcl and strip the stamp_write proc + all stamp_write calls
        txt = _sub(fixed_fp_tcl(cfg), cfg)
        # remove the stamp proc block
        txt = txt.replace(STAMP_PROC_FP, "")
        # remove all stamp_write calls
        txt = re.sub(r"^\s*stamp_write\s+\.fail\s*\n", "", txt, flags=re.MULTILINE)
        txt = re.sub(r'^\s*stamp_write\s+""\s*\n', "", txt, flags=re.MULTILINE)
        return txt
    PR_A_NO_STAMP = PR_A.replace(STAMP_PROC_PR, "").replace("stamp_write .fail\n        ", "").replace('stamp_write ""\n', '')
    naive_no = (
        "#!/usr/bin/env python3\n"
        "import os, sys, re\n"
        "out = sys.argv[sys.argv.index('-o')+1] if '-o' in sys.argv else 'fixed'\n"
        "os.makedirs(out, exist_ok=True)\n"
        "# rewrite geometry but no stamp\n"
        + "open(os.path.join(out,'innovus_fp.tcl'),'w').write(" + repr(fp_no_stamp(A_CFG)) + ")\n"
        + "open(os.path.join(out,'innovus_pr.tcl'),'w').write(" + repr(PR_A_NO_STAMP) + ")\n"
        + "open(os.path.join(out,'Makefile'),'w').write(" + repr(MK_A) + ")\n"
        "print('done')\n"
    )
    _zip_from_files(os.path.join(neg_dir, "naive_no_stamp.zip"), {
        "fix_apr_stamp.py": naive_no,
        "fixed/innovus_fp.tcl": fp_no_stamp(A_CFG),
        "fixed/innovus_pr.tcl": PR_A_NO_STAMP,
        "fixed/Makefile": MK_A,
    })


NEG_SELFTEST = r'''#!/usr/bin/env python3
"""negative_selftest.py -- all 5 negatives MUST FAIL check()."""
import os, sys, shutil, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check

NEG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "negative")
WORK = tempfile.mkdtemp(prefix="negself_")

negs = ["fake_empty.zip", "fake_print_expected.zip", "fake_core_deleted.zip",
        "naive_hardcode_a.zip", "naive_no_stamp.zip"]
results = {}
try:
    for n in negs:
        src = os.path.join(NEG_DIR, n)
        # place each negative as the deliverable
        deliverable_dir = os.path.join(WORK, n.replace(".zip", ""))
        os.makedirs(deliverable_dir, exist_ok=True)
        shutil.copy(src, os.path.join(deliverable_dir, "submit.zip"))
        try:
            check.check("submit.zip", deliverable_dir)
            results[n] = "PASS  <-- BAD (negative should FAIL)"
        except Exception as e:
            results[n] = "FAIL  <-- GOOD (%s)" % str(e)[:120]
finally:
    shutil.rmtree(WORK, ignore_errors=True)

bad = [n for n, r in results.items() if r.startswith("PASS")]
for n, r in results.items():
    print("%-30s %s" % (n, r))
if bad:
    print("\nNEG_SELFTEST FAILED: %d negative(s) passed check (should all FAIL)" % len(bad))
    sys.exit(1)
print("\nNEG_SELFTEST OK: all 5 negatives FAIL as expected")
sys.exit(0)
'''


def write_neg_selftest():
    with open(os.path.join(REF_DIR, "negative_selftest.py"), "w") as f:
        f.write(NEG_SELFTEST)


def main():
    write_assets()
    write_reference()
    write_check()
    build_negatives()
    write_neg_selftest()
    print("built", CID)
    print("  A_DIR  =", A_DIR)
    print("  B_DIR  =", B_DIR)
    print("  REF_DIR=", REF_DIR)


if __name__ == "__main__":
    main()
