#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-GdsBump2-001 (shard D, schematic_netlist).

A-faithful trace: xxchen/hfeg0plg53 session 1792323159551_toezr U#0
"用tcl+skipper 写 gds_bump2 脚本，把gds中所有层次按用户指定number增加值".
Real skipper binary degrades to config-driven Python generator that emits
gds_bump2.tcl (skipper TCL) + layer_bump_plan.json.
"""
import json, os, hashlib, shutil, zipfile, subprocess, sys, tempfile

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-GdsBump2-001"
A = os.path.join(ROOT, "assets", CID)
H = os.path.join(A, "hidden")
R = os.path.join(ROOT, "reference", CID)
N = os.path.join(R, "negative")
for d in (A, H, R, N):
    os.makedirs(d, exist_ok=True)

# ---------- config A (visible to SUT) ----------
A_LAYERS = [1,2,3,10,11,12,20,21,22,30,31,40,41,50,51,60,61,62,70,71,80,81,
            90,91,100,101,110,111,120,130,140,150,160]  # 34 lpp
A_FIGS = [18,12,9,42,30,21,55,33,17,48,22,61,28,14,39,52,19,26,44,31,58,23,
          37,16,49,27,34,41,29,38,46,53,24,32]
config_A = {
    "tool": "skipper",
    "script_name": "gds_bump2.tcl",
    "input_gds": "A1_CA2_connection_check_A1.gds",
    "bump2": 20000,
    "output_gds": "A1_CA2_connection_check_A1_bump20000.gds",
    "gdsii_layer_max": 65535,
    "hierarchy_depth": 100000,
    "top_cells": ["A1_CA2_connection_check_A1"],
    "cells": 24,
    "lpps": [{"layer": l, "datatype": 0, "fig_count": c} for l, c in zip(A_LAYERS, A_FIGS)],
}

# ---------- config B (hidden, different gds/bump/lpps, WITH collisions) ----------
B_LAYERS = [1,50,62,75,88,100,113,125,138,150,163,175,188,200,213,225,238,250,263,275,288,300]  # 22
B_FIGS = [15,28,19,42,33,21,37,14,48,26,31,44,22,39,17,35,29,41,18,34,27,46]
config_B = {
    "tool": "skipper",
    "script_name": "gds_bump2.tcl",
    "input_gds": "X2_DB1_via_chain_check_B1.gds",
    "bump2": 12,
    "output_gds": "X2_DB1_via_chain_check_B1_bump12.gds",
    "gdsii_layer_max": 65535,
    "hierarchy_depth": 100000,
    "top_cells": ["X2_DB1_via_chain_check_B1"],
    "cells": 18,
    "lpps": [{"layer": l, "datatype": 0, "fig_count": c} for l, c in zip(B_LAYERS, B_FIGS)],
}

with open(os.path.join(A, "config_A.json"), "w") as f:
    json.dump(config_A, f, indent=2)
with open(os.path.join(H, "config_B.json"), "w") as f:
    json.dump(config_B, f, indent=2)

# ---------- hidden_manifest ----------
def recompute(cfg):
    bump = cfg["bump2"]; lpps = cfg["lpps"]; lmax = cfg["gdsii_layer_max"]
    mapping = []
    for e in lpps:
        l, dt = e["layer"], e["datatype"]; nl = l + bump
        mapping.append({"old_lpp": f"{l}.{dt}", "new_lpp": f"{nl}.{dt}",
                        "old_layer": l, "datatype": dt, "new_layer": nl,
                        "fig_count": e["fig_count"]})
    old_set = {m["old_lpp"] for m in mapping}
    range_errs = [m["old_lpp"] for m in mapping if m["new_layer"] < 0 or m["new_layer"] > lmax]
    cols = [{"old_lpp": m["old_lpp"], "collides_with": m["new_lpp"]}
            for m in mapping if m["new_lpp"] in old_set and m["new_lpp"] != m["old_lpp"]]
    return mapping, range_errs, cols

mA, rA, cA = recompute(config_A)
mB, rB, cB = recompute(config_B)
hidden_manifest = {
    "case_id": CID,
    "input_variant": "B",
    "config_B": config_B,
    "expected_mapping": mB,
    "expected_range_errors": rB,
    "expected_collisions": cB,
    "expected_sort_order": "descending",
    "expected_fig_total": sum(e["fig_count"] for e in config_B["lpps"]),
    "expected_lpp_count": len(config_B["lpps"]),
    "cross_guard": {
        "A_only_tokens": ["A1_CA2_connection_check_A1", "20000", "A1_CA2_connection_check_A1_bump20000"],
        "B_must_appear": ["X2_DB1_via_chain_check_B1", "12", "X2_DB1_via_chain_check_B1_bump12"],
    },
}
with open(os.path.join(H, "hidden_manifest.json"), "w") as f:
    json.dump(hidden_manifest, f, indent=2)

# ---------- reference generator gen_gds_bump2.py ----------
GEN_SRC = r'''#!/usr/bin/env python3
"""Generate gds_bump2.tcl (skipper TCL) + layer_bump_plan.json from config.json.

Reads ./config.json (tool, script_name, input_gds, bump2, output_gds,
gdsii_layer_max, hierarchy_depth, top_cells, cells, lpps[]).
Emits <script_name> and layer_bump_plan.json in the current directory.

The TCL script bumps every GDS layer number by bump2 (datatype unchanged):
    new_layer = old_layer + bump2
using skipper dbImport / dbLibLayers / dbLibTopCell / dbLayerMove -depth /
dbLibExport, with upfront GDSII range validation, collision warning,
descending/ascending ordering, and a post-move verification sweep.
"""
import json
import sys


def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)


def compute_mapping(lpps, bump):
    out = []
    for e in lpps:
        l = e["layer"]; dt = e["datatype"]; nl = l + bump
        out.append({"old_lpp": "%d.%d" % (l, dt),
                    "new_lpp": "%d.%d" % (nl, dt),
                    "old_layer": l, "datatype": dt, "new_layer": nl,
                    "fig_count": e.get("fig_count", 0)})
    return out


def validate_range(mapping, lmax):
    errs = []
    for m in mapping:
        if m["new_layer"] < 0 or m["new_layer"] > lmax:
            errs.append({"old_lpp": m["old_lpp"], "new_layer": m["new_layer"]})
    return errs


def detect_collisions(mapping):
    old_set = {m["old_lpp"] for m in mapping}
    cols = []
    for m in mapping:
        if m["new_lpp"] in old_set and m["new_lpp"] != m["old_lpp"]:
            cols.append({"old_lpp": m["old_lpp"], "collides_with": m["new_lpp"]})
    return cols


def sort_order(bump):
    return "descending" if bump >= 0 else "ascending"


def emit_tcl(cfg):
    depth = cfg["hierarchy_depth"]
    lmax = cfg["gdsii_layer_max"]
    L = []
    L.append("# gds_bump2.tcl -- bump all GDS layer numbers by a user value")
    L.append("# generated by gen_gds_bump2.py (config-driven)")
    L.append("# Tool: skipper | new_layer = old_layer + bump2, datatype unchanged")
    L.append("# GDSII layer range [0,%d] | hierarchy depth %d" % (lmax, depth))
    L.append("proc gb2_log {msg} { puts \"gds_bump2: $msg\" }")
    L.append("proc gb2_die {msg} { puts \"gds_bump2: ERROR: $msg\"; exit 1 }")
    L.append("proc gb2_lpp_split {lpp} { return [list [lindex [split $lpp \".\"] 0] [lindex [split $lpp \".\"] 1]] }")
    L.append("proc gb2_lpp_desc {a b} { set la [lindex [gb2_lpp_split $a] 0]; set lb [lindex [gb2_lpp_split $b] 0]; if {$la == $lb} {return 0}; return [expr {$la < $lb ? 1 : -1}] }")
    L.append("proc gb2_lpp_asc {a b} { set la [lindex [gb2_lpp_split $a] 0]; set lb [lindex [gb2_lpp_split $b] 0]; if {$la == $lb} {return 0}; return [expr {$la > $lb ? 1 : -1}] }")
    L.append("proc gb2_env {name} { if {[info exists ::env($name)]} {return $::env($name)}; return \"\" }")
    L.append("proc gb2_parse_args {} {")
    L.append("    set pos {}")
    L.append("    foreach a $::argv { if {[string index $a 0] eq \"-\" && ![regexp {^-[0-9]+$} $a]} {continue}; lappend pos $a }")
    L.append("    set in [lindex $pos 0]; set bump [lindex $pos 1]; set out [lindex $pos 2]")
    L.append("    if {$in eq \"\"} {set in [gb2_env GDS_IN]}")
    L.append("    if {$bump eq \"\"} {set bump [gb2_env BUMP2]}")
    L.append("    if {$out eq \"\"} {set out [gb2_env GDS_OUT]}")
    L.append("    if {$in eq \"\" || $bump eq \"\"} {gb2_die \"usage: skipper gds_bump2.tcl <input.gds> <bump2> \\[output.gds\\] -noterm\"}")
    L.append("    if {![file exists $in]} {gb2_die \"input gds not found: $in\"}")
    L.append("    if {![regexp {^[+-]?[0-9]+$} $bump]} {gb2_die \"bump2 must be an integer\"}")
    L.append("    if {$out eq \"\"} {set dir [file dirname $in]; set stem [file rootname [file tail $in]]; set out [file join $dir \"${stem}_bump${bump}.gds\"]}")
    L.append("    return [list $in [expr {$bump + 0}] $out]")
    L.append("}")
    L.append("proc gb2_own_figs {libId cellName} {")
    L.append("    set cell [dbCellGetByName -libId $libId -cellName $cellName]")
    L.append("    if {$cell == \"\"} {return {}}")
    L.append("    if {[catch {dbCellGetBBox -cell $cell -withLabel} bbox]} {return {}}")
    L.append("    if {$bbox == \"\"} {return {}}")
    L.append("    if {[catch {dbFigQuery $cell $bbox -stopLvl 0 -maxFigNum -1} figs]} {return {}}")
    L.append("    return $figs")
    L.append("}")
    L.append("lassign [gb2_parse_args] inGds bump outGds")
    L.append("gb2_log \"input gds: $inGds\"")
    L.append("gb2_log \"bump2 value: $bump\"")
    L.append("gb2_log \"output gds: $outGds\"")
    L.append("set lib [dbImport \"$inGds\"]")
    L.append("if {$lib == \"\"} {gb2_die \"dbImport failed for $inGds\"}")
    L.append("set libId [dbLibGetId $lib]")
    L.append("if {$libId == \"\"} {gb2_die \"dbLibGetId failed\"}")
    L.append("if {[catch {set allLpps [dbLibLayers -libId $libId]} err]} {gb2_die \"dbLibLayers failed: $err\"}")
    L.append("gb2_log \"library contains [llength $allLpps] layer.purpose entries\"")
    L.append("set rangeErr 0")
    L.append("foreach lpp $allLpps { lassign [gb2_lpp_split $lpp] l dt; set nl [expr {$l + $bump}]; if {$nl < 0 || $nl > %d} {gb2_log \"ERROR: layer $l.$dt out of range -> $nl\"; set rangeErr 1}; if {[lsearch -exact $allLpps \"$nl.$dt\"] >= 0} {gb2_log \"WARNING: $l.$dt + $bump = $nl.$dt collision\"} }" % lmax)
    L.append("if {$rangeErr} {gb2_die \"layer number out of GDSII range [0,%d], nothing changed\"}" % lmax)
    L.append("set tops [dbLibTopCell -libId $libId]")
    L.append("if {[llength $tops] == 0} {set tops [dbLibGetAllCells -libId $libId]}")
    L.append("gb2_log \"layer-direct conversion from [llength $tops] entry cell(s)\"")
    L.append("set cells [dbLibGetAllCells -libId $libId]")
    L.append("set figTotal0 0")
    L.append("foreach cellName $cells { set figTotal0 [expr {$figTotal0 + [llength [gb2_own_figs $libId $cellName]]}] }")
    L.append("set lpps $allLpps")
    L.append("if {$bump >= 0} {set lpps [lsort -command gb2_lpp_desc $lpps]} else {set lpps [lsort -command gb2_lpp_asc $lpps]}")
    L.append("array unset moveMap")
    L.append("set moveErr 0")
    L.append("foreach lpp $lpps { lassign [gb2_lpp_split $lpp] l dt; set newLpp \"[expr {$l + $bump}].$dt\"; foreach top $tops { set rc [dbLayerMove -libId $libId -cellName $top -lpp1 $lpp -lpp2 $newLpp -depth %d]; if {$rc != 1} {gb2_log \"ERROR: dbLayerMove failed: $top $lpp -> $newLpp\"; incr moveErr} }; set moveMap($lpp) $newLpp }" % depth)
    L.append("if {$moveErr > 0} {gb2_die \"$moveErr dbLayerMove call(s) failed\"}")
    L.append("gb2_log \"layer number mapping (old -> new):\"")
    L.append("foreach old [lsort -command gb2_lpp_desc [array names moveMap]] { gb2_log [format \"    %-12s -> %s\" $old $moveMap($old)] }")
    L.append("array unset oldNum; array unset targetNum")
    L.append("foreach lpp $allLpps { lassign [gb2_lpp_split $lpp] l dt; set oldNum($l) 1; set targetNum([expr {$l + $bump}]) 1 }")
    L.append("set figTotal1 0; array unset leftover")
    L.append("foreach cellName $cells { foreach fig [gb2_own_figs $libId $cellName] { incr figTotal1; set l [dbFigGet $fig -attr layer]; if {$l eq \"\"} {continue}; if {[info exists oldNum($l)] && ![info exists targetNum($l)]} { set p [dbFigGet $fig -attr purpose]; incr leftover($cellName,$l.$p) } } }")
    L.append("if {$figTotal1 != $figTotal0} {gb2_die \"verify failed: figure count changed $figTotal0 -> $figTotal1\"}")
    L.append("if {[array size leftover] > 0} { foreach key [array names leftover] { set cellName [lindex [split $key \",\"] 0]; set lpp [string range $key [string length \"$cellName,\"] end]; lassign [gb2_lpp_split $lpp] l dt; set newLpp \"[expr {$l + $bump}].$dt\"; set rc [dbLayerMove -libId $libId -cellName $cellName -lpp1 $lpp -lpp2 $newLpp -depth 0]; if {$rc != 1} {incr moveErr} } }")
    L.append("gb2_log \"verify passed: figure total unchanged ($figTotal1)\"")
    L.append("set outDir [file dirname $outGds]")
    L.append("if {![file isdirectory $outDir]} {file mkdir $outDir}")
    L.append("set exportOk [dbLibExport $lib \"$outGds\"]")
    L.append("if {$exportOk eq \"\" || $exportOk eq \"0\"} {gb2_die \"dbLibExport failed for $outGds\"}")
    L.append("if {![file exists $outGds] || [file size $outGds] == 0} {gb2_die \"exported gds missing or empty\"}")
    L.append("gb2_log \"exported: $outGds ([file size $outGds] bytes)\"")
    L.append("gb2_log \"DONE. all layer numbers bumped by $bump\"")
    L.append("exit 0")
    return "\n".join(L) + "\n"


def main():
    cfg = load_config()
    bump = cfg["bump2"]
    lmax = cfg["gdsii_layer_max"]
    lpps = cfg["lpps"]
    mapping = compute_mapping(lpps, bump)
    range_errs = validate_range(mapping, lmax)
    collisions = detect_collisions(mapping)
    order = sort_order(bump)
    fig_total = sum(e.get("fig_count", 0) for e in lpps)
    plan = {
        "tool": cfg["tool"],
        "script_name": cfg["script_name"],
        "input_gds": cfg["input_gds"],
        "bump2": bump,
        "output_gds": cfg.get("output_gds", ""),
        "gdsii_layer_max": lmax,
        "hierarchy_depth": cfg["hierarchy_depth"],
        "sort_order": order,
        "cells": cfg["cells"],
        "fig_total": fig_total,
        "lpp_count": len(lpps),
        "mapping": mapping,
        "range_errors": range_errs,
        "collisions": collisions,
        "top_cells": cfg["top_cells"],
    }
    with open(cfg["script_name"], "w") as f:
        f.write(emit_tcl(cfg))
    with open("layer_bump_plan.json", "w") as f:
        json.dump(plan, f, indent=2)
    print("emitted %s + layer_bump_plan.json" % cfg["script_name"])


if __name__ == "__main__":
    main()
'''
with open(os.path.join(R, "gen_gds_bump2.py"), "w") as f:
    f.write(GEN_SRC)

# ---------- prompt.txt (U#0 verbatim) ----------
PROMPT = (
"帮我用tcl+skipper工具 写一个脚本，脚本名称 gds_bump2，\n"
"功能：把gds中的所有层次按照用户指定的number增加一个值。\n"
"如原本 gds number 为100 ，用户给bump2=20000, 导出的gds number 既为 20100\n"
"你可以参考下面目录下的tcl脚本写法：\n"
"module_checkFlow\n"
"测试GDS为：\n"
"A1_CA2_connection_check_A1.gds\n"
)
with open(os.path.join(A, "prompt.txt"), "w") as f:
    f.write(PROMPT)

# ---------- task_brief.md (deliverable interface only, <=3 lines) ----------
BRIEF = (
"交付：outputs/submit.zip，内含 gen_gds_bump2.py（读同目录 config.json，"
"生成 gds_bump2.tcl + layer_bump_plan.json）。\n"
"config.json 字段：tool/script_name/input_gds/bump2/output_gds/"
"gdsii_layer_max/hierarchy_depth/top_cells/cells/lpps[{layer,datatype,fig_count}]。\n"
)
with open(os.path.join(A, "task_brief.md"), "w") as f:
    f.write(BRIEF)

print("built assets + reference for", CID)
print("A lpps:", len(config_A["lpps"]), "B lpps:", len(config_B["lpps"]), "B collisions:", len(cB))
