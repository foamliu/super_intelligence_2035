#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build EDA-Eval-DesignFlow-IMPSR1253VddPmFix-001
pnr_signoff / L2 / A-faithful
trace: 1793621923074_i9chj (alan3zh / hfeg0plg49 / mc401)
Innovus fp IMPSR-1253 VDD_PM diagnosis + innovus_fp.tcl generation-aware fix.

Generates: assets/, reference/ (check.py, gold tcl+json, hidden B, negatives)
"""
import os, json, zipfile, textwrap

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-IMPSR1253VddPmFix-001"
ASSETS = os.path.join(BENCH, "assets", CASE)
REF = os.path.join(BENCH, "reference", CASE)
HID = os.path.join(REF, "hidden")
NEG = os.path.join(REF, "negative")

for d in (ASSETS, REF, HID, NEG):
    os.makedirs(d, exist_ok=True)

def w(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# ============================ A-档 prompt (U#1 verbatim) ============================
A_PROMPT = "进入./apr/logs查看inv_fp.log，其中有告警：Begin power routing ... **WARN: (IMPSR-1253): Unable to find any standard cell pin connected to the VDD_PM net. 查询问题原因"

w(os.path.join(ASSETS, "prompt.txt"), A_PROMPT + "\n")

# ============================ task_brief.md (<=3 lines, interface only) ============================
w(os.path.join(ASSETS, "task_brief.md"), textwrap.dedent("""\
交付接口：outputs/submit.zip 内含 2 个文件——`innovus_fp.tcl`（分代网表感知的修复版 fp 脚本）与 `diagnose.json`（IMPSR-1253 根因诊断结果）。
工作目录下 `inv_fp.log`（fp 日志）、`innovus_fp.tcl`（原版，未修复）、`dc_netlist_A.v`（DC 网表片段）、`power.globals` 为真实输入（只读）。
评测只看 submit.zip；判分在独立目录解 zip，用隐藏 fixture B（不同 net 名/子树/计数/revision）跑候选 tcl 结构断言 + diagnose.json 内容断言，不跑真实 Innovus（license 不可用）。
"""))

# ============================ A: inv_fp.log ============================
A_LOG = textwrap.dedent("""\
# Innovus 22.10 FP run log
# host: hfeg0plg49  user: alan3zh  design: test_chip_v1
# DC_RESULT_DIR: /home/alan3zh/test_chip_v1/dc/dc_2026-11-02-20.29.45
# start: 2026-11-03 14:04:00
restoreDesign test_chip_v1.enc.dat test_chip_v1
...
# Power intent: UPF loaded (test_chip_v1.upf)
# DC netlist dc_2026-11-02-20.29.45 (new, power-intent included, 2007 explicit .VDD()/.VSS())
Begin power routing ...
**WARN: (IMPSR-1253): Unable to find any standard cell pin connected to the VDD_PM net.
   VERIFY (net=VDD_PM): 1 instTerm, 0 leaf std-cell pin(s), hierarchical port pin(s) only.
   PM_VDDI_Inst subtree:
     PMArrayPart(TOPPMBLK) -> PMVDDIMatrixPart(PM_VDDI_Inst) -> 21xPMVDDIRowPart(PMColBLK_Blk40xx) -> 21xINVD8(PMRowBLK_Blk40xx)
     = 441 leaf INVD8 cells, each .VDD connects to module-local VDD_PM net (NOT top-level VDD).
     Hierarchy port on PM_VDDI_Inst: .VDD_PM(VDD_PM)  (maps module-local VDD_PM to top-level VDD_PM).
   Top-level power pins: ..., VDD, VSS, VDD_PM
   GNC searched for pin named "VDD" on PMRowBLK_* -> 0 leaf std-cell pin connected.
   Verdict: IMPSR-1253 EXPECTED at floorplan (VDD_PM is netlist-level pd_pm isolation;
            leaf hookup occurs in subsequent power routing stage).
...
addStripe VDD_PM (PM band) M4: 5 special wire(s) built.
sroute VDD_PM: band rails connected.
INNOVUS FP DONE. 441 protection instances. saveDesign 0 error.
""")
w(os.path.join(ASSETS, "inv_fp.log"), A_LOG)

# ============================ A: innovus_fp.tcl (original, broken, no generation-aware) ============================
A_TCL_ORIG = textwrap.dedent("""\
# innovus_fp.tcl -- original (pre-fix) power routing for test_chip_v1
# Unconditional globalNetConnect: no generation probe, no VERIFY distinction.
globalNetConnect VDD_PM -instanceBasename PMRowBLK_* -netType power
globalNetConnect VDD -instanceBasename * -netType power
globalNetConnect VSS -instanceBasename * -netType power
addStripe -net VDD_PM -layer M4 -start_offset 5.0 -spacing 1.2 -width 0.8 -set_to_set_distance 40
addStripe -net VDD -layer M5 -start_offset 5.0 -spacing 1.2 -width 0.8 -set_to_set_distance 40
addStripe -net VSS -layer M5 -start_offset 5.0 -spacing 1.2 -width 0.8 -set_to_set_distance 40
sroute -nets VDD_PM
sroute -nets VDD
sroute -nets VSS
exit 0
""")
w(os.path.join(ASSETS, "innovus_fp.tcl"), A_TCL_ORIG)

# ============================ A: dc_netlist_A.v (PM_VDDI_Inst subtree fragment) ============================
A_NETLIST = textwrap.dedent('''\
// DC netlist fragment: dc_2026-11-02-20.29.45
// test_chip_v1 — PM_VDDI_Inst subtree (VDD_PM netlist-level isolation)
module test_chip_v1 (
    input  VDD,
    input  VSS,
    input  VDD_PM,      // top-level PM sensing supply pin
    // ... 16 top-level pins total
    output [15:0] data_out
);
  // PM array
  PMArrayPart TOPPMBLK (
    .VDD(VDD), .VSS(VSS), .VDD_PM(VDD_PM)
  );

  // PM VDDI matrix — hierarchy port maps module-local VDD_PM to top
  PMVDDIMatrixPart PM_VDDI_Inst (
    .VDD_PM(VDD_PM),   // <-- hierarchy port (NOT .VDD): maps to top-level VDD_PM
    .VDD(VDD),
    .VSS(VSS)
  );

  // Inside PM_VDDI_Inst: 21 x PMVDDIRowPart(PMColBLK_Blk40xx)
  //   each PMVDDIRowPart contains 21 x INVD8(PMRowBLK_Blk40xx)
  //   each INVD8 leaf: .VDD(local VDD_PM), .VSS(VSS)
  //   => 441 leaf INVD8 cells, .VDD connects to module-local VDD_PM net
  //   => top-level GNC searching pin "VDD" finds 0 leaf std-cell pin on VDD_PM
  //
  // (subtree expanded flat for verification)
  PMVDDIRowPart PMColBLK_Blk40xx00 ( .VDD_PM(VDD_PM), .VSS(VSS),
    .row( {PMRowBLK_Blk40xx00, PMRowBLK_Blk40xx01, ... PMRowBLK_Blk40xx20} ) );
  // ... 21 RowParts, each with 21 INVD8 = 441 leaf cells total
endmodule
''')
w(os.path.join(ASSETS, "dc_netlist_A.v"), A_NETLIST)

# ============================ A: power.globals ============================
w(os.path.join(ASSETS, "power.globals"), textwrap.dedent("""\
# power.globals — test_chip_v1
VDD    power
VSS    ground
VDD_PM power
"""))

# ============================ GOLD: innovus_fp.tcl (generation-aware fix) ============================
GOLD_TCL = textwrap.dedent("""\
# innovus_fp.tcl -- generation-aware IMPSR-1253 handling for test_chip_v1 fp
#
# IMPSR-1253 EXPECTED at floorplan when VDD_PM (or PM sensing supply) is
# netlist-level pd_pm isolation: leaf .VDD connects to module-local net,
# mapped to top via hierarchy port .VDD_PM(VDD_PM) on PM_VDDI_Inst (NOT .VDD).
# GNC searching pin "VDD" finds 0 leaf std-cell pin -> VERIFY reports
# 1 instTerm, 0 leaf std-cell pin, hierarchy port pin(s) only.
# Verdict: IMPSR-1253 EXPECTED at floorplan; leaf hookup at power routing stage.
# Manual addNet + GNC only for OLD netlists where the net is absent.
#
# Usage: innovus -files innovus_fp.tcl   (reads ./inv_fp.log to extract IMPSR-1253 net)

# --- parse IMPSR-1253 net name from fp log (parameterized; no hardcode) ---
set _fp_log "inv_fp.log"
set _pm_net ""
if {[file exists $_fp_log]} {
    set fh [open $_fp_log r]
    set _logtxt [read $fh]
    close $fh
    regexp {WARN: \\(IMPSR-1253\\):.*connected to the (\\w+) net} $_logtxt _m _pm_net
}
if {$_pm_net eq ""} {
    # fallback: probe any VDD_* net in current design
    set _pm_net [lindex [dbGet top.nets.name -p *VDD_*] 0]
}

# --- generation probe: does the net exist in current netlist? ---
set _pm_nl ""
catch { set _pm_nl [dbGet top.nets.name $_pm_net] }

if {$_pm_nl ne ""} {
    # NEW netlist: net is netlist-level isolation, leaf hookup deferred to power routing
    puts "IMPSR-1253: $_pm_net present in netlist (new generation)."
    puts "VERIFY: 0 leaf std-cell pin, hierarchy port pin(s) only -- netlist-level pd_pm isolation."
    puts "IMPSR-1253 EXPECTED at floorplan for $_pm_net."
} else {
    # OLD netlist: manual addNet + GNC for PM row cells (fallback path)
    puts "IMPSR-1253: $_pm_net absent from netlist (old generation). Manual connect."
    catch { addNet $_pm_net -netType power }
    catch {
        globalNetConnect $_pm_net -instanceBasename *RowBLK_* \\
            -netlistOverride -netType power
    }
}

# --- preserve *VDDI_Inst* hierarchy instance reference (PM_VDDI_Inst / SENS_VDDI_Inst) ---
set _vddi_insts ""
catch { set _vddi_insts [dbGet -p top.insts.name *VDDI_Inst*] }
puts "VDDI_Inst subtree preserved: [llength $_vddi_insts] instance(s)."

# --- UPF-aware: if UPF defines the net, skip manual GNC ---
set _upf_rc ""
catch { loadUpf } _upf_rc
if {$_pm_net ne "" && [dbGet top.nets.name $_pm_net] ne ""} {
    puts "UPF-aware: $_pm_net handled by UPF/netlist, skip manual GNC."
}

# --- VERIFY: distinguish leaf std-cell pin from hierarchy port pin ---
set _leaf_cnt 0
catch {
    set _netp [dbGet top.nets.name $_pm_net -p]
    set _leaf_terms [dbGet $_netp.instTerms.name]
    if {$_leaf_terms ne ""} { set _leaf_cnt [llength $_leaf_terms] }
}
set _hier_ports ""
catch {
    set _netp [dbGet top.nets.name $_pm_net -p]
    set _hier_ports [dbGet $_netp.terms.name]
}
puts "VERIFY: $_pm_net -- leaf std-cell pin count = $_leaf_cnt, hierarchy port = $_hier_ports"
if {$_leaf_cnt == 0} {
    puts "IMPSR-1253 EXPECTED at floorplan: 0 leaf std-cell pin, hierarchy port pin(s) only."
}

# --- power routing: addStripe (PM band M4) + sroute ---
catch { addStripe -net $_pm_net -layer M4 -start_offset 5.0 -spacing 1.2 -width 0.8 -set_to_set_distance 40 }
catch { sroute -nets $_pm_net }

exit 0
""")
w(os.path.join(REF, "innovus_fp.tcl"), GOLD_TCL)

# ============================ GOLD: diagnose.json ============================
GOLD_JSON = {
    "net_name": "VDD_PM",
    "impsr1253_verdict": "EXPECTED at floorplan",
    "root_cause": (
        "VDD_PM is netlist-level pd_pm isolation. PM row cells (PMRowBLK_Blk40xx, INVD8, "
        "441 leaf) have leaf .VDD connecting to module-local VDD_PM net (NOT top-level VDD), "
        "mapped to top-level VDD_PM via hierarchy port .VDD_PM(VDD_PM) on PM_VDDI_Inst "
        "(the instance port is .VDD_PM, not .VDD). GNC searching for a pin named VDD on "
        "PMRowBLK_* finds 0 leaf std-cell pin -> VERIFY reports 1 instTerm, 0 leaf std-cell pin, "
        "hierarchy port pin(s) only. IMPSR-1253 is expected at floorplan; leaf hookup occurs "
        "in the subsequent power routing stage, not at fp."
    ),
    "pm_subtree": (
        "PMArrayPart(TOPPMBLK) -> PMVDDIMatrixPart(PM_VDDI_Inst) -> "
        "21xPMVDDIRowPart(PMColBLK_Blk40xx) -> 21xINVD8(PMRowBLK_Blk40xx) = 441 leaf cells"
    ),
    "dc_revision": "dc_2026-11-02-20.29.45",
    "leaf_pin_count": 0,
    "hierarchy_port": ".VDD_PM(VDD_PM) on PM_VDDI_Inst",
}
w(os.path.join(REF, "diagnose.json"), json.dumps(GOLD_JSON, ensure_ascii=False, indent=2))

# ============================ reference_submit.zip (gold tcl + gold json) ============================
with zipfile.ZipFile(os.path.join(REF, "reference_submit.zip"), "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(os.path.join(REF, "innovus_fp.tcl"), "innovus_fp.tcl")
    zf.write(os.path.join(REF, "diagnose.json"), "diagnose.json")

# ============================ HIDDEN B (different net/subtree/count/revision) ============================
B_LOG = textwrap.dedent("""\
# Innovus 22.10 FP run log
# host: hfeg0plg49  user: claire1l  design: sense_chip_v2
# DC_RESULT_DIR: /home/claire1l/sense_chip_v2/dc/dc_2026-11-01-10.15.00
# start: 2026-11-03 09:22:00
restoreDesign sense_chip_v2.enc.dat sense_chip_v2
...
# Power intent: UPF loaded (sense_chip_v2.upf)
# DC netlist dc_2026-11-01-10.15.00 (new, power-intent included)
Begin power routing ...
**WARN: (IMPSR-1253): Unable to find any standard cell pin connected to the VDD_SENS net.
   VERIFY (net=VDD_SENS): 1 instTerm, 0 leaf std-cell pin(s), hierarchical port pin(s) only.
   SENS_VDDI_Inst subtree:
     SENSArrayPart(TOPSENSBLK) -> SENSVDDIMatrixPart(SENS_VDDI_Inst) -> 12xSENSVDDIRowPart(SENSColBLK_Blk22xx) -> 18xINVD8(SENSRowBLK_Blk22xx)
     = 216 leaf INVD8 cells, each .VDD connects to module-local VDD_SENS net (NOT top-level VDD).
     Hierarchy port on SENS_VDDI_Inst: .VDD_SENS(VDD_SENS)  (maps module-local VDD_SENS to top-level VDD_SENS).
   Top-level power pins: ..., VDD, VSS, VDD_SENS
   GNC searched for pin named "VDD" on SENSRowBLK_* -> 0 leaf std-cell pin connected.
   Verdict: IMPSR-1253 EXPECTED at floorplan (VDD_SENS is netlist-level isolation;
            leaf hookup occurs in subsequent power routing stage).
...
addStripe VDD_SENS (SENS band) M4: 4 special wire(s) built.
sroute VDD_SENS: band rails connected.
INNOVUS FP DONE. 216 protection instances. saveDesign 0 error.
""")
w(os.path.join(HID, "inv_fp.log"), B_LOG)

B_NETLIST = textwrap.dedent('''\
// DC netlist fragment: dc_2026-11-01-10.15.00
// sense_chip_v2 — SENS_VDDI_Inst subtree (VDD_SENS netlist-level isolation)
module sense_chip_v2 (
    input  VDD,
    input  VSS,
    input  VDD_SENS,    // top-level sensing supply pin
    output [11:0] sense_out
);
  SENSArrayPart TOPSENSBLK (
    .VDD(VDD), .VSS(VSS), .VDD_SENS(VDD_SENS)
  );
  SENSVDDIMatrixPart SENS_VDDI_Inst (
    .VDD_SENS(VDD_SENS),   // <-- hierarchy port (NOT .VDD)
    .VDD(VDD),
    .VSS(VSS)
  );
  // Inside SENS_VDDI_Inst: 12 x SENSVDDIRowPart(SENSColBLK_Blk22xx)
  //   each SENSVDDIRowPart contains 18 x INVD8(SENSRowBLK_Blk22xx)
  //   => 216 leaf INVD8 cells, .VDD connects to module-local VDD_SENS net
  SENSVDDIRowPart SENSColBLK_Blk22xx00 ( .VDD_SENS(VDD_SENS), .VSS(VSS),
    .row( {SENSRowBLK_Blk22xx00, ... SENSRowBLK_Blk22xx17} ) );
  // ... 12 RowParts, each with 18 INVD8 = 216 leaf cells total
endmodule
''')
w(os.path.join(HID, "dc_netlist_B.v"), B_NETLIST)

w(os.path.join(HID, "power.globals"), textwrap.dedent("""\
# power.globals — sense_chip_v2
VDD      power
VSS      ground
VDD_SENS power
"""))

B_MANIFEST = {
    "purpose": (
        "cross-input fixture B: different net name (VDD_SENS vs A's VDD_PM), "
        "different subtree instance (SENS_VDDI_Inst vs PM_VDDI_Inst), "
        "different row basename (SENSRowBLK_* vs PMRowBLK_*), "
        "different leaf count (216=12x18 vs 441=21x21), "
        "different DC revision (dc_2026-11-01-10.15.00 vs dc_2026-11-02-20.29.45). "
        "Defeats hardcoding A net name VDD_PM, A subtree PM_VDDI_Inst, A row basename PMRowBLK_*, "
        "A leaf count 441, or A dc revision."
    ),
    "log_relpath": "inv_fp.log",
    "netlist_relpath": "dc_netlist_B.v",
    "net_name": "VDD_SENS",
    "subtree_instance": "SENS_VDDI_Inst",
    "row_basename_glob": "SENSRowBLK_*",
    "leaf_count": 216,
    "dc_revision": "dc_2026-11-01-10.15.00",
    "differs_from_A": {
        "A_net_name": "VDD_PM",          "B_net_name": "VDD_SENS",
        "A_subtree":  "PM_VDDI_Inst",     "B_subtree":  "SENS_VDDI_Inst",
        "A_row_glob": "PMRowBLK_*",       "B_row_glob": "SENSRowBLK_*",
        "A_leaf":     441,                "B_leaf":     216,
        "A_dc_rev":   "dc_2026-11-02-20.29.45", "B_dc_rev": "dc_2026-11-01-10.15.00"
    }
}
w(os.path.join(HID, "hidden_manifest.json"), json.dumps(B_MANIFEST, ensure_ascii=False, indent=2))

# ============================ NEGATIVES ============================
# (1) fake_empty: empty tcl + empty json
w(os.path.join(NEG, "fake_empty.tcl"), "# empty\nexit 0\n")
w(os.path.join(NEG, "fake_empty.json"), "{}")
with zipfile.ZipFile(os.path.join(NEG, "fake_empty.zip"), "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(os.path.join(NEG, "fake_empty.tcl"), "innovus_fp.tcl")
    zf.write(os.path.join(NEG, "fake_empty.json"), "diagnose.json")

# (2) fake_print_expected: just prints expected strings, no real structure
FAKE_PRINT_TCL = textwrap.dedent("""\
# fake: just prints expected strings
puts "IMPSR-1253 EXPECTED at floorplan"
puts "VERIFY: 0 leaf std-cell pin, hierarchy port pin(s) only"
exit 0
""")
FAKE_PRINT_JSON = {
    "net_name": "VDD_PM",
    "impsr1253_verdict": "EXPECTED at floorplan",
    "root_cause": "leaf .VDD module-local hierarchy port netlist isolation 0 leaf std-cell pin",
    "pm_subtree": "441 leaf",
    "dc_revision": "dc_2026-11-02-20.29.45",
    "leaf_pin_count": 0,
    "hierarchy_port": ".VDD_PM(VDD_PM)"
}
w(os.path.join(NEG, "fake_print_expected.tcl"), FAKE_PRINT_TCL)
w(os.path.join(NEG, "fake_print_expected.json"), json.dumps(FAKE_PRINT_JSON, ensure_ascii=False))
with zipfile.ZipFile(os.path.join(NEG, "fake_print_expected.zip"), "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(os.path.join(NEG, "fake_print_expected.tcl"), "innovus_fp.tcl")
    zf.write(os.path.join(NEG, "fake_print_expected.json"), "diagnose.json")

# (3) fake_core_deleted: tcl does GNC but no probe / no VERIFY distinction (core logic stripped)
FAKE_CORE_TCL = textwrap.dedent("""\
# fake: GNC present but no generation probe, no VERIFY leaf/hierarchy distinction
set _pm_net VDD_PM
globalNetConnect $_pm_net -instanceBasename *RowBLK_* -netlistOverride -netType power
addStripe -net $_pm_net -layer M4
sroute -nets $_pm_net
exit 0
""")
w(os.path.join(NEG, "fake_core_deleted.tcl"), FAKE_CORE_TCL)
with zipfile.ZipFile(os.path.join(NEG, "fake_core_deleted.zip"), "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(os.path.join(NEG, "fake_core_deleted.tcl"), "innovus_fp.tcl")
    zf.write(os.path.join(REF, "diagnose.json"), "diagnose.json")  # valid json, but tcl fails

# (4) naive_stub: hardcodes VDD_PM (no log parse), fails anti-hardcode on B
NAIVE_TCL = textwrap.dedent("""\
# naive: hardcodes VDD_PM, no log parse, no parameterization
set pm_net VDD_PM
globalNetConnect $pm_net -instanceBasename PMRowBLK_* -netType power
puts "IMPSR-1253 EXPECTED at floorplan for $pm_net"
puts "VERIFY: 0 leaf std-cell pin, hierarchy port pin(s) only"
exit 0
""")
w(os.path.join(NEG, "naive_stub.tcl"), NAIVE_TCL)
with zipfile.ZipFile(os.path.join(NEG, "naive_stub.zip"), "w", zipfile.ZIP_DEFLATED) as zf:
    zf.write(os.path.join(NEG, "naive_stub.tcl"), "innovus_fp.tcl")
    zf.write(os.path.join(REF, "diagnose.json"), "diagnose.json")

print("BUILD OK")
print("assets:", os.listdir(ASSETS))
print("ref:", os.listdir(REF))
print("hidden:", os.listdir(HID))
print("negative:", os.listdir(NEG))
