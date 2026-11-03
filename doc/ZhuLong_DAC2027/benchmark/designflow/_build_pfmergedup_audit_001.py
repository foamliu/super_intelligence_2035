#!/usr/bin/env python3
# Generator for EDA-Eval-DesignFlow-PFMergeDupAudit-001
# pg_layout domain, B-档 synthesized, L1-boundary.
# Trace source: e0014566 / hfeg0pkn001 / 1783596713423_53n4v (mc=317, virtuoso+skill+dbCreateInst)
# Real user turn UI#5 (verbatim): audit relationship between original layout / auto power-fill cell /
# merged result / manual reference. Agent used SKILL dbOpenCellViewByType to inspect 4 cells and
# found: merged shapes (243) ~ 2x original (241); every layer 2:1 ratio merged vs manual;
# M1/drawing rect same bBox duplicated (2x) both VSS!; M1/pin label triplication; root cause =
# dbCopyFig flatten + Phase3 net-restore vs correct dbCreateInst instance-based merge.
# Layouts are private (austin_new lib on e0014566 workspace) -> A-档 not sandbox-reproducible ->
# B-档 synthesized L1-boundary: SUT given 4 cell inventory text files (extracted from real audit +
# synthesized B structurally different) and must produce a JSON audit report.
import os, json, zipfile, hashlib, subprocess, sys, shutil

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-PFMergeDupAudit-001"
ASSET = os.path.join(ROOT, "assets", CASE)
REF = os.path.join(ROOT, "reference", CASE)
NEG = os.path.join(REF, "negative")
for d in (ASSET, os.path.join(ASSET, "hidden"), REF, NEG):
    os.makedirs(d, exist_ok=True)

# ---------- inventory format ----------
# Lines:
#   CELL <lib> <cell>
#   SHAPES <n>
#   VIAS <n>
#   INSTANCES <n>
#   NETS <n>
#   PINS <n>
#   BBOX ((x1 y1) (x2 y2))
#   SHAPES_WITH_NET <n>
#   SHAPES_WITH_PIN <n>
#   NET <name> figs=<n> pins=<n>
#   INSTANCE <inst_name> master=<lib>/<cell> origin=<nil|coord> orient=<R0|...>
#   LAYER <layer/purpose> <count>
#   SHAPE <idx> <layer/purpose> <rect|label> bbox=((x1 y1) (x2 y2)) net=<nil|name>

def emit_cell(lib, cell, summary, nets, instances, layers, shapes):
    L = []
    L.append(f"CELL {lib} {cell}")
    L.append(f"SHAPES {summary['shapes']}")
    L.append(f"VIAS {summary['vias']}")
    L.append(f"INSTANCES {summary['instances']}")
    L.append(f"NETS {summary['nets']}")
    L.append(f"PINS {summary['pins']}")
    L.append(f"BBOX {summary['bbox']}")
    L.append(f"SHAPES_WITH_NET {summary['swn']}")
    L.append(f"SHAPES_WITH_PIN {summary['swp']}")
    for n in nets:
        L.append(f"NET {n['name']} figs={n['figs']} pins={n['pins']}")
    for inst in instances:
        L.append(f"INSTANCE {inst['name']} master={inst['master']} origin={inst['origin']} orient={inst['orient']}")
    for lp, c in layers:
        L.append(f"LAYER {lp} {c}")
    for s in shapes:
        L.append(f"SHAPE {s['idx']} {s['lp']} {s['kind']} bbox={s['bbox']} net={s['net']}")
    return "\n".join(L) + "\n"

# ============ A (visible) — faithful subset of real audit ============
# Original test_20260528: 241 shapes, 4 vias, 0 inst, 1 net VSS! figs=1
A_orig_layers = [
    ("M3/track",28),("M3/drawing",2),("M5/track",24),("M5/mark",18),("M2/mark",20),
    ("M2/track",20),("M2/drawing",4),("M3/mark",28),("M4/track",16),("M4/drawing",2),
    ("M4/mark",16),("M1/mark",30),("M1/pin",7),("M1/drawing",4),("M1/track",22),
]
# Real M1 shapes (original), trimmed to a representative set that still shows the duplicate pattern.
# Key: M1/drawing rect ((0.0 0.0) (54.35 2.5)) appears 1x in original (VSS!), 2x in merged (both VSS!).
# M1/pin label ((0.095 1.025) (0.905 1.275)) appears 3x original, 5x merged.
A_orig_m1 = [
    (1,"M1/track","rect","((0.0 -5.7) (54.325 -3.2))","nil"),
    (2,"M1/drawing","rect","((0.0 0.0) (54.35 2.5))","VSS!"),
    (3,"M1/track","rect","((0.0 -9.95) (54.4 -7.45))","nil"),
    (4,"M1/pin","rect","((0.0 0.9) (1.0 1.4))","VSS!"),
    (5,"M1/pin","label","((0.095 1.025) (0.905 1.275))","nil"),
    (6,"M1/mark","label","((-0.33475 -4.775) (1.28475 -4.275))","nil"),
    (7,"M1/mark","label","((-0.33475 -9.275) (1.28475 -8.775))","nil"),
    (8,"M1/track","rect","((0.0 -19.85) (54.475 -17.35))","nil"),
    (9,"M1/mark","label","((-0.33475 -19.2) (1.28475 -18.7))","nil"),
    (10,"M1/drawing","rect","((81.875 0.0) (144.375 2.5))","nil"),
    (11,"M1/pin","label","((81.7915 1.0) (83.4585 1.5))","nil"),
    (12,"M1/track","rect","((81.875 -7.775) (144.375 -5.275))","nil"),
    (13,"M1/mark","label","((81.7915 -6.85) (83.4585 -6.35))","nil"),
    (14,"M1/pin","label","((0.095 1.025) (0.905 1.275))","nil"),
    (15,"M1/pin","label","((0.095 1.025) (0.905 1.275))","nil"),
]
A_orig = emit_cell(
    "austin_new", "test_20260528",
    {"shapes":241,"vias":4,"instances":0,"nets":1,"pins":0,
     "bbox":"((-0.33475 -96.525) (144.375 5.175))","swn":2,"swp":1},
    [{"name":"VSS!","figs":1,"pins":1}],
    [],
    A_orig_layers,
    [{"idx":i,"lp":lp,"kind":k,"bbox":b,"net":n} for (i,lp,k,b,n) in A_orig_m1],
)

# Power Fill Cell test_20260528_auto_pgfill: 47 shapes, 231 vias, 0 inst, 0 nets
A_pgfill_layers = [
    ("M5/drawing",4),("M4/drawing",8),("M3/drawing",14),("M2/drawing",10),("M1/drawing",11),
]
A_pgfill = emit_cell(
    "austin_new", "test_20260528_auto_pgfill",
    {"shapes":47,"vias":231,"instances":0,"nets":0,"pins":0,
     "bbox":"((0.0 -86.95) (144.375 5.175))","swn":0,"swp":0},
    [],
    [],
    A_pgfill_layers,
    [{"idx":i,"lp":"M1/drawing","kind":"rect","bbox":b,"net":"nil"}
     for i,b in enumerate(["((0.0 0.0) (54.35 2.5))","((81.875 0.0) (144.375 2.5))",
                           "((0.0 -5.7) (54.325 -3.2))","((0.0 -9.95) (54.4 -7.45))"],1)],
)

# Merged test_20260528_powerfill: 243 shapes, 4 vias, 1 inst, 1 net VSS! figs=3 pins=1
# Layer dist: every layer 2x manual (the 2:1 duplication pattern). M1/pin=9 (manual 3), M1/drawing=4 (manual 2).
A_merged_layers = [
    ("M3/track",28),("M3/drawing",2),("M5/track",24),("M5/mark",18),("M2/mark",20),
    ("M2/track",20),("M2/drawing",4),("M3/mark",28),("M4/track",16),("M4/drawing",2),
    ("M4/mark",16),("M1/mark",30),("M1/pin",9),("M1/drawing",4),("M1/track",22),
]
# Merged M1 shapes — duplicates evident: drawing rect 2x (both VSS!), pin label 5x (orig 3x)
A_merged_m1 = [
    (1,"M1/track","rect","((0.0 -5.7) (54.325 -3.2))","nil"),
    (2,"M1/drawing","rect","((0.0 0.0) (54.35 2.5))","VSS!"),
    (3,"M1/track","rect","((0.0 -9.95) (54.4 -7.45))","nil"),
    (4,"M1/pin","rect","((0.0 0.9) (1.0 1.4))","VSS!"),
    (5,"M1/pin","label","((0.095 1.025) (0.905 1.275))","nil"),
    (6,"M1/pin","label","((0.095 1.025) (0.905 1.275))","nil"),
    (7,"M1/mark","label","((-0.33475 -4.775) (1.28475 -4.275))","nil"),
    (8,"M1/mark","label","((-0.33475 -9.275) (1.28475 -8.775))","nil"),
    (9,"M1/drawing","rect","((81.875 0.0) (144.375 2.5))","nil"),
    (10,"M1/pin","label","((81.7915 1.0) (83.4585 1.5))","nil"),
    (11,"M1/track","rect","((0.0 -5.7) (54.325 -3.2))","nil"),
    (12,"M1/drawing","rect","((0.0 0.0) (54.35 2.5))","VSS!"),
    (13,"M1/pin","rect","((0.0 0.9) (1.0 1.4))","VSS!"),
    (14,"M1/pin","label","((0.095 1.025) (0.905 1.275))","nil"),
    (15,"M1/pin","label","((0.095 1.025) (0.905 1.275))","nil"),
    (16,"M1/pin","label","((0.095 1.025) (0.905 1.275))","nil"),
    (17,"M1/mark","label","((-0.33475 -4.775) (1.28475 -4.275))","nil"),
    (18,"M1/drawing","rect","((81.875 0.0) (144.375 2.5))","nil"),
]
A_merged = emit_cell(
    "austin_new", "test_20260528_powerfill",
    {"shapes":243,"vias":4,"instances":1,"nets":1,"pins":0,
     "bbox":"((-0.33475 -96.525) (144.375 5.175))","swn":4,"swp":1},
    [{"name":"VSS!","figs":3,"pins":1}],
    [{"name":"test_20260528_auto_pgfill","master":"austin_new/test_20260528_auto_pgfill",
      "origin":"nil","orient":"R0"}],
    A_merged_layers,
    [{"idx":i,"lp":lp,"kind":k,"bbox":b,"net":n} for (i,lp,k,b,n) in A_merged_m1],
)

# Manual test_20260708: 120 shapes, 4 vias, 1 inst, 1 net VSS! figs=1
A_manual_layers = [
    ("M3/track",14),("M3/drawing",1),("M5/track",12),("M5/mark",9),("M2/mark",10),
    ("M2/track",10),("M2/drawing",2),("M3/mark",14),("M4/track",8),("M4/drawing",1),
    ("M4/mark",8),("M1/mark",15),("M1/pin",3),("M1/drawing",2),("M1/track",11),
]
A_manual_m1 = [
    (1,"M1/track","rect","((0.0 -5.7) (54.325 -3.2))","nil"),
    (2,"M1/drawing","rect","((0.0 0.0) (54.35 2.5))","VSS!"),
    (3,"M1/pin","rect","((0.0 0.9) (1.0 1.4))","VSS!"),
    (4,"M1/pin","label","((0.095 1.025) (0.905 1.275))","nil"),
    (5,"M1/mark","label","((-0.33475 -4.775) (1.28475 -4.275))","nil"),
    (6,"M1/drawing","rect","((81.875 0.0) (144.375 2.5))","nil"),
    (7,"M1/pin","label","((81.7915 1.0) (83.4585 1.5))","nil"),
    (8,"M1/track","rect","((0.0 -9.95) (54.4 -7.45))","nil"),
]
A_manual = emit_cell(
    "austin_new", "test_20260708",
    {"shapes":120,"vias":4,"instances":1,"nets":1,"pins":0,
     "bbox":"((-0.33475 -96.525) (144.375 5.175))","swn":2,"swp":1},
    [{"name":"VSS!","figs":1,"pins":1}],
    [{"name":"I1","master":"austin_new/test_20260528_auto_pgfill","origin":"nil","orient":"R0"}],
    A_manual_layers,
    [{"idx":i,"lp":lp,"kind":k,"bbox":b,"net":n} for (i,lp,k,b,n) in A_manual_m1],
)

with open(os.path.join(ASSET, "cell_original_A.txt"),"w") as f: f.write(A_orig)
with open(os.path.join(ASSET, "cell_pgfill_A.txt"),"w") as f: f.write(A_pgfill)
with open(os.path.join(ASSET, "cell_merged_A.txt"),"w") as f: f.write(A_merged)
with open(os.path.join(ASSET, "cell_manual_A.txt"),"w") as f: f.write(A_manual)

# prompt.txt — verbatim UI#5 (A-档 faithful task description)
PROMPT = """请你检查下原始的输入layout:  austin_new/test_20260528/layout. 输出的power fill cell: austin_new/test_20260528_auto_pgfill/layout. 以及 将原来的输入layout 和 power fill cell merge 过后的结果：austin_new/test_20260528_powerfill/layout。 能帮忙审查下他们之间的关系嘛.另外我给你一个参考是我手动调入 power fill cell 到原layout 中的：test_20260708

---
附件给出 4 个 cell 的清单文本（cell_original_A.txt 原始输入、cell_pgfill_A.txt 自动 power fill cell、cell_merged_A.txt 合并结果、cell_manual_A.txt 手动参考）。请写一个 Python3 审查脚本读取这 4 个清单并产出 JSON 审查报告，判断合并结果是否正确、是否存在重复图形、与手动参考的差异，并给出合并策略判定（instance-based 正确 / buggy flatten 错误）。

交付接口：
- 提交 outputs/submit.zip，内含一个 Python3 脚本 pfmerge_dup_audit.py（仅标准库）。
- 脚本 CLI: python3 pfmerge_dup_audit.py <cell_original.txt> <cell_pgfill.txt> <cell_merged.txt> <cell_manual.txt>
- 把 JSON 审查报告打印到 stdout。
"""
with open(os.path.join(ASSET, "prompt.txt"),"w") as f: f.write(PROMPT)

TASK_BRIEF = """# 交付接口
- 提交 `outputs/submit.zip`，内含 `pfmerge_dup_audit.py`（Python3 仅标准库）。
- CLI: `python3 pfmerge_dup_audit.py <original> <pgfill> <merged> <manual>`，JSON 审查报告打印到 stdout。
- 输入：4 个 cell 清单文本（CELL/SHAPES/VIAS/NET/LAYER/SHAPE 行）。
"""
with open(os.path.join(ASSET, "task_brief.md"),"w") as f: f.write(TASK_BRIEF)

# ============ hidden B (structurally different: 3:1 ratio, VDD!, triplication) ============
B_orig_layers = [
    ("M2/track",18),("M2/drawing",3),("M4/track",14),("M4/mark",10),("M3/mark",16),
    ("M3/track",16),("M3/drawing",2),("M2/mark",12),("M1/mark",20),("M1/pin",5),("M1/drawing",3),("M1/track",14),
]
B_orig_m1 = [
    (1,"M1/track","rect","((0.0 -4.0) (40.0 -1.5))","nil"),
    (2,"M1/drawing","rect","((0.0 0.0) (40.0 2.0))","VDD!"),
    (3,"M1/pin","rect","((0.0 0.8) (1.0 1.3))","VDD!"),
    (4,"M1/pin","label","((0.1 1.0) (0.9 1.2))","nil"),
    (5,"M1/mark","label","((-0.3 -3.5) (1.2 -3.0))","nil"),
    (6,"M1/drawing","rect","((60.0 0.0) (120.0 2.0))","nil"),
    (7,"M1/pin","label","((60.1 1.0) (60.9 1.2))","nil"),
    (8,"M1/track","rect","((0.0 -8.0) (40.5 -5.5))","nil"),
]
B_orig = emit_cell(
    "austin_new_B", "layoutB",
    {"shapes":180,"vias":6,"instances":0,"nets":1,"pins":0,
     "bbox":"((-0.3 -80.0) (120.0 4.0))","swn":2,"swp":1},
    [{"name":"VDD!","figs":1,"pins":1}],
    [],
    B_orig_layers,
    [{"idx":i,"lp":lp,"kind":k,"bbox":b,"net":n} for (i,lp,k,b,n) in B_orig_m1],
)
B_pgfill_layers = [
    ("M4/drawing",6),("M3/drawing",10),("M2/drawing",8),("M1/drawing",9),
]
B_pgfill = emit_cell(
    "austin_new_B", "layoutB_autopf",
    {"shapes":60,"vias":180,"instances":0,"nets":0,"pins":0,
     "bbox":"((0.0 -70.0) (120.0 4.0))","swn":0,"swp":0},
    [],
    [],
    B_pgfill_layers,
    [{"idx":i,"lp":"M1/drawing","kind":"rect","bbox":b,"net":"nil"}
     for i,b in enumerate(["((0.0 0.0) (40.0 2.0))","((60.0 0.0) (120.0 2.0))",
                           "((0.0 -4.0) (40.0 -1.5))"],1)],
)
# B merged: 3x original (540 shapes), 1 inst, VDD! figs=5 pins=1 (orig 1, manual 1)
B_merged_layers = [
    ("M2/track",54),("M2/drawing",9),("M4/track",42),("M4/mark",30),("M3/mark",48),
    ("M3/track",48),("M3/drawing",6),("M2/mark",36),("M1/mark",60),("M1/pin",15),("M1/drawing",9),("M1/track",42),
]
# B merged M1: triplication — drawing rect ((0.0 0.0) (40.0 2.0)) appears 3x (all VDD!);
# pin label ((0.1 1.0) (0.9 1.2)) appears 6x (orig 1, manual 1)
B_merged_m1 = [
    (1,"M1/track","rect","((0.0 -4.0) (40.0 -1.5))","nil"),
    (2,"M1/drawing","rect","((0.0 0.0) (40.0 2.0))","VDD!"),
    (3,"M1/pin","rect","((0.0 0.8) (1.0 1.3))","VDD!"),
    (4,"M1/pin","label","((0.1 1.0) (0.9 1.2))","nil"),
    (5,"M1/mark","label","((-0.3 -3.5) (1.2 -3.0))","nil"),
    (6,"M1/drawing","rect","((60.0 0.0) (120.0 2.0))","nil"),
    (7,"M1/pin","label","((60.1 1.0) (60.9 1.2))","nil"),
    (8,"M1/track","rect","((0.0 -8.0) (40.5 -5.5))","nil"),
    (9,"M1/drawing","rect","((0.0 0.0) (40.0 2.0))","VDD!"),
    (10,"M1/pin","rect","((0.0 0.8) (1.0 1.3))","VDD!"),
    (11,"M1/pin","label","((0.1 1.0) (0.9 1.2))","nil"),
    (12,"M1/mark","label","((-0.3 -3.5) (1.2 -3.0))","nil"),
    (13,"M1/drawing","rect","((60.0 0.0) (120.0 2.0))","nil"),
    (14,"M1/drawing","rect","((0.0 0.0) (40.0 2.0))","VDD!"),
    (15,"M1/pin","rect","((0.0 0.8) (1.0 1.3))","VDD!"),
    (16,"M1/pin","label","((0.1 1.0) (0.9 1.2))","nil"),
    (17,"M1/pin","label","((0.1 1.0) (0.9 1.2))","nil"),
    (18,"M1/pin","label","((0.1 1.0) (0.9 1.2))","nil"),
    (19,"M1/pin","label","((0.1 1.0) (0.9 1.2))","nil"),
    (20,"M1/pin","label","((0.1 1.0) (0.9 1.2))","nil"),
    (21,"M1/track","rect","((0.0 -4.0) (40.0 -1.5))","nil"),
    (22,"M1/track","rect","((0.0 -8.0) (40.5 -5.5))","nil"),
]
B_merged = emit_cell(
    "austin_new_B", "layoutB_pf",
    {"shapes":540,"vias":6,"instances":1,"nets":1,"pins":0,
     "bbox":"((-0.3 -80.0) (120.0 4.0))","swn":8,"swp":1},
    [{"name":"VDD!","figs":5,"pins":1}],
    [{"name":"layoutB_autopf","master":"austin_new_B/layoutB_autopf","origin":"nil","orient":"R0"}],
    B_merged_layers,
    [{"idx":i,"lp":lp,"kind":k,"bbox":b,"net":n} for (i,lp,k,b,n) in B_merged_m1],
)
# B manual: 180 shapes (== orig), 1 inst, VDD! figs=1
B_manual_layers = B_orig_layers  # same as orig (instance-based, no flatten)
B_manual = emit_cell(
    "austin_new_B", "layoutB_manual",
    {"shapes":180,"vias":6,"instances":1,"nets":1,"pins":0,
     "bbox":"((-0.3 -80.0) (120.0 4.0))","swn":2,"swp":1},
    [{"name":"VDD!","figs":1,"pins":1}],
    [{"name":"I1","master":"austin_new_B/layoutB_autopf","origin":"nil","orient":"R0"}],
    B_manual_layers,
    [{"idx":i,"lp":lp,"kind":k,"bbox":b,"net":n} for (i,lp,k,b,n) in B_orig_m1],
)

with open(os.path.join(ASSET, "hidden", "cell_original_B.txt"),"w") as f: f.write(B_orig)
with open(os.path.join(ASSET, "hidden", "cell_pgfill_B.txt"),"w") as f: f.write(B_pgfill)
with open(os.path.join(ASSET, "hidden", "cell_merged_B.txt"),"w") as f: f.write(B_merged)
with open(os.path.join(ASSET, "hidden", "cell_manual_B.txt"),"w") as f: f.write(B_manual)

# ============ hidden B2 (clean instance-based merge -> verdict OK) ============
B2_orig_layers = [
    ("M2/track",10),("M2/drawing",2),("M1/mark",8),("M1/pin",2),("M1/drawing",2),("M1/track",6),
]
B2_orig_m1 = [
    (1,"M1/track","rect","((0.0 -3.0) (30.0 -1.0))","nil"),
    (2,"M1/drawing","rect","((0.0 0.0) (30.0 2.0))","VSS!"),
    (3,"M1/pin","rect","((0.0 0.8) (1.0 1.3))","VSS!"),
    (4,"M1/pin","label","((0.1 1.0) (0.9 1.2))","nil"),
    (5,"M1/mark","label","((-0.2 -2.5) (1.0 -2.0))","nil"),
    (6,"M1/drawing","rect","((50.0 0.0) (90.0 2.0))","nil"),
]
B2_orig = emit_cell(
    "austin_new_C", "layoutC",
    {"shapes":60,"vias":2,"instances":0,"nets":1,"pins":0,
     "bbox":"((-0.2 -50.0) (90.0 3.0))","swn":2,"swp":1},
    [{"name":"VSS!","figs":1,"pins":1}],
    [],
    B2_orig_layers,
    [{"idx":i,"lp":lp,"kind":k,"bbox":b,"net":n} for (i,lp,k,b,n) in B2_orig_m1],
)
B2_pgfill_layers = [("M2/drawing",3),("M1/drawing",4)]
B2_pgfill = emit_cell(
    "austin_new_C", "layoutC_autopf",
    {"shapes":20,"vias":40,"instances":0,"nets":0,"pins":0,
     "bbox":"((0.0 -40.0) (90.0 3.0))","swn":0,"swp":0},
    [],[],
    B2_pgfill_layers,
    [{"idx":i,"lp":"M1/drawing","kind":"rect","bbox":"((0.0 0.0) (30.0 2.0))","net":"nil"} for i in range(1,5)],
)
# B2 merged: clean — same as orig (60 shapes) + 1 instance, NO duplicates, VSS! figs=1
B2_merged_layers = B2_orig_layers  # 1:1 with manual
B2_merged_m1 = B2_orig_m1  # no duplication
B2_merged = emit_cell(
    "austin_new_C", "layoutC_pf",
    {"shapes":60,"vias":2,"instances":1,"nets":1,"pins":0,
     "bbox":"((-0.2 -50.0) (90.0 3.0))","swn":2,"swp":1},
    [{"name":"VSS!","figs":1,"pins":1}],
    [{"name":"layoutC_autopf","master":"austin_new_C/layoutC_autopf","origin":"nil","orient":"R0"}],
    B2_merged_layers,
    [{"idx":i,"lp":lp,"kind":k,"bbox":b,"net":n} for (i,lp,k,b,n) in B2_merged_m1],
)
B2_manual = emit_cell(
    "austin_new_C", "layoutC_manual",
    {"shapes":60,"vias":2,"instances":1,"nets":1,"pins":0,
     "bbox":"((-0.2 -50.0) (90.0 3.0))","swn":2,"swp":1},
    [{"name":"VSS!","figs":1,"pins":1}],
    [{"name":"I1","master":"austin_new_C/layoutC_autopf","origin":"nil","orient":"R0"}],
    B2_orig_layers,
    [{"idx":i,"lp":lp,"kind":k,"bbox":b,"net":n} for (i,lp,k,b,n) in B2_orig_m1],
)
with open(os.path.join(ASSET, "hidden", "cell_original_B2.txt"),"w") as f: f.write(B2_orig)
with open(os.path.join(ASSET, "hidden", "cell_pgfill_B2.txt"),"w") as f: f.write(B2_pgfill)
with open(os.path.join(ASSET, "hidden", "cell_merged_B2.txt"),"w") as f: f.write(B2_merged)
with open(os.path.join(ASSET, "hidden", "cell_manual_B2.txt"),"w") as f: f.write(B2_manual)

manifest = {
    "hidden_inputs": [
        "cell_original_B.txt","cell_pgfill_B.txt","cell_merged_B.txt","cell_manual_B.txt",
        "cell_original_B2.txt","cell_pgfill_B2.txt","cell_merged_B2.txt","cell_manual_B2.txt"
    ],
    "note": "B=3:1 ratio (540/180), VDD!, triplication (drawing rect 3x all VDD!, pin label 6x), verdict HAS_DUPLICATES, strategy buggy_flatten. B2=clean 1:1 (60/60), VSS!, no duplicates, verdict OK, strategy instance_based. Both structurally different from A (2:1, VSS!, 241/120).",
    "cross_guard": "B uses VDD!/3:1/triplication/different libs (austin_new_B) to kill hardcoded-A output; B2 clean (verdict OK) kills always-HAS_DUPLICATES / hardcoded-B-dirty-JSON; B dirty kills always-OK; deterministic 3-run md5 kills nondeterminism."
}
with open(os.path.join(ASSET, "hidden", "hidden_manifest.json"),"w") as f: json.dump(manifest,f,indent=2)

print("assets written to", ASSET)
