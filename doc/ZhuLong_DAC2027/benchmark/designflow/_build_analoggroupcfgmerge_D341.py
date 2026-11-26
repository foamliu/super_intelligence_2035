#!/usr/bin/env python3
"""Build AnalogGroupCfgMergeDummy-001 (shard D, analog_context, B-grade synthesized, L1).
trace = 1791532940009_ca92c (ziyuny, AnaWeave Group Generator cfg merge + dummy audit).

Generates:
  assets/EDA-Eval-DesignFlow-AnalogGroupCfgMergeDummy-001/
      prompt.txt, task_brief.md, base_cfg_A.json, patch_A.json,
      labels_A.txt, layout_inst_A.txt, sch_inst_A.txt
      hidden/ (base_cfg_B.json, patch_B.json, labels_B.txt, layout_inst_B.txt, sch_inst_B.txt,
              base_cfg_B2.json, patch_B2.json, labels_B2.txt, layout_inst_B2.txt, sch_inst_B2.txt,
              hidden_manifest.json)
  reference/EDA-Eval-DesignFlow-AnalogGroupCfgMergeDummy-001/
      gg_cfg_merge_verify_ref.py  (reference solution)
      check.py
      negative/ (empty_shell.py, hardcode_a.py, no_deepmerge.py, print_expected.py,
                 ref_core_deleted.py, wrong_axis.py)
      negative_selftest.py
"""
import os, json, textwrap, shutil, zipfile, subprocess, sys, hashlib

CASE = "EDA-Eval-DesignFlow-AnalogGroupCfgMergeDummy-001"
ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
A_DIR = f"{ROOT}/assets/{CASE}"
HID_DIR = f"{A_DIR}/hidden"
REF_DIR = f"{ROOT}/reference/{CASE}"
NEG_DIR = f"{REF_DIR}/negative"
for d in (A_DIR, HID_DIR, REF_DIR, NEG_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------- base cfg builder ----------------
def base_cfg(cell, dp_style, dp_mode, dp_rows, cm_style, cm_mode, cas_style, cas_mode,
             nmos_w, pmos_w):
    return {
        "LibCfg": {"libName": "AnaWeave_demo", "cellName": cell},
        "DeviceCfg": {"nmos": {"w": nmos_w, "l": "180n"}, "pmos": {"w": pmos_w, "l": "180n"}},
        "DummyCfg": {"device": "nmos18", "labelRewrite": "O"},
        "TapCfg": {"enabled": "1", "tapCell": "tap_tie"},
        "PatternCfg": {
            "DifferentPair": {"Matching": {
                "Style": dp_style, "Mode": dp_mode, "Rows": str(dp_rows),
                "Dummy": {"LeftRight": "0", "TopBottom": "0"}}},
            "CurrentMirror": {"Matching": {
                "Style": cm_style, "Mode": cm_mode,
                "Dummy": {"LeftRight": "0", "TopBottom": "0"}}},
            "Cascode": {"Matching": {
                "Style": cas_style, "Mode": cas_mode,
                "Dummy": {"LeftRight": "0", "TopBottom": "0"}}},
        },
    }

# ---------------- A inputs ----------------
base_A = base_cfg("VwlpRefAmpIP", "AB", "common-centroid", 2, "AB", "interdigitated",
                  "AB", "stacked", "2u", "4u")
patch_A = {"PatternCfg": {"DifferentPair": {"Matching": {"Dummy": {"LeftRight": "1"}}}}}
# Schematic instances (real devices). Centroid x = (200+260)/2 = 230, y=(400+400)/2=400
sch_A = [
    ("M1", "nmos18", 200, 400),
    ("M2", "nmos18", 260, 400),
    ("M3", "pmos18", 200, 520),
    ("M4", "pmos18", 260, 520),
    ("MNDUM1", "nmos18", 140, 400),   # schematic-instantiated dummy (exists in both views)
    ("MPDUM1", "pmos18", 320, 520),
]
# Layout instances: schematic ones + GG-generated placement dummies (layout-only)
lay_A = list(sch_A) + [
    # GG-generated L/R dummies for diff pair (LeftRight=1 patch)
    ("GG_DUM_DP_L1", "nmos18", 100, 400),
    ("GG_DUM_DP_L2", "nmos18",  80, 400),
    ("GG_DUM_DP_R1", "nmos18", 360, 400),
    ("GG_DUM_DP_R2", "nmos18", 380, 400),
    ("GG_TAP1", "tap_tie", 230, 300),
]
# Labels: 'O' labels at L/R of diff pair centroid (x=230). L: x<230, R: x>230
labels_A = [
    ("O", "MET1", 100, 400),
    ("O", "MET1",  80, 400),
    ("O", "MET1", 360, 400),
    ("O", "MET1", 380, 400),
    ("M1", "MET1", 200, 400),   # real device labels (not 'O')
    ("M2", "MET1", 260, 400),
    ("VDD", "MET2", 230, 580),
    ("GND", "MET2", 230, 320),
]

# ---------------- B inputs (different cell, TopBottom patch, top/bottom dummies) ----------------
base_B = base_cfg("OtaFoldCascode", "BA", "interdigitated", 4, "BA", "common-centroid",
                  "BA", "interdigitated", "3u", "6u")
patch_B = {"PatternCfg": {"DifferentPair": {"Matching": {"Dummy": {"TopBottom": "1"}}}}}
# Centroid x = (300+360)/2=330, y=(500+500)/2=500
sch_B = [
    ("Q1", "nmos18", 300, 500),
    ("Q2", "nmos18", 360, 500),
    ("Q5", "pmos18", 300, 620),
    ("Q6", "pmos18", 360, 620),
    ("QNDUM", "nmos18", 240, 500),
    ("QPDUM", "pmos18", 420, 620),
]
lay_B = list(sch_B) + [
    # GG-generated top/bottom dummies (TopBottom=1 patch). Top: y>centroid, Bottom: y<centroid
    ("GG_DUM_DP_T1", "nmos18", 330, 640),
    ("GG_DUM_DP_T2", "nmos18", 330, 660),
    ("GG_DUM_DP_B1", "nmos18", 330, 440),
    ("GG_DUM_DP_B2", "nmos18", 330, 420),
    ("GG_TAP_B", "tap_tie", 330, 700),
]
labels_B = [
    ("O", "MET1", 330, 640),
    ("O", "MET1", 330, 660),
    ("O", "MET1", 330, 440),
    ("O", "MET1", 330, 420),
    ("Q1", "MET1", 300, 500),
    ("Q2", "MET1", 360, 500),
    ("VCC", "MET2", 330, 680),
    ("VSS", "MET2", 330, 380),
]

# ---------------- B2 inputs (CurrentMirror patch, different section) ----------------
base_B2 = base_cfg("RfAmpBias", "AB", "common-centroid", 2, "AB", "interdigitated",
                   "AB", "stacked", "1.5u", "3u")
patch_B2 = {"PatternCfg": {"CurrentMirror": {"Matching": {"Dummy": {"LeftRight": "1"}}}}}
# Centroid x=(220+280)/2=250, y=(420+420)/2=420
sch_B2 = [
    ("J1", "nmos18", 220, 420),
    ("J2", "nmos18", 280, 420),
    ("J3", "pmos18", 220, 540),
    ("J4", "pmos18", 280, 540),
]
lay_B2 = list(sch_B2) + [
    # GG-generated L/R dummies for CURRENT MIRROR (not diff pair)
    ("GG_DUM_CM_L1", "nmos18", 160, 540),
    ("GG_DUM_CM_L2", "nmos18", 140, 540),
    ("GG_DUM_CM_R1", "nmos18", 340, 540),
    ("GG_DUM_CM_R2", "nmos18", 360, 540),
]
labels_B2 = [
    ("O", "MET1", 160, 540),
    ("O", "MET1", 140, 540),
    ("O", "MET1", 340, 540),
    ("O", "MET1", 360, 540),
    ("J1", "MET1", 220, 420),
    ("J2", "MET1", 280, 420),
    ("VBias", "MET2", 250, 600),
]

def fmt_inst(rows):
    return "\n".join(f"{n} {m} xy=({x},{y})" for n, m, x, y in rows) + "\n"

def fmt_sch(rows):
    return "\n".join(f"{n} {m}" for n, m, x, y in rows) + "\n"

def fmt_labels(rows):
    return "\n".join(f"text={t} layer={l} xy=({x},{y})" for t, l, x, y in rows) + "\n"

# write A assets
with open(f"{A_DIR}/base_cfg_A.json", "w") as f: json.dump(base_A, f, indent=2)
with open(f"{A_DIR}/patch_A.json", "w") as f: json.dump(patch_A, f, indent=2)
with open(f"{A_DIR}/labels_A.txt", "w") as f: f.write(fmt_labels(labels_A))
with open(f"{A_DIR}/layout_inst_A.txt", "w") as f: f.write(fmt_inst(lay_A))
with open(f"{A_DIR}/sch_inst_A.txt", "w") as f: f.write(fmt_sch(sch_A))

# write hidden B/B2
with open(f"{HID_DIR}/base_cfg_B.json", "w") as f: json.dump(base_B, f, indent=2)
with open(f"{HID_DIR}/patch_B.json", "w") as f: json.dump(patch_B, f, indent=2)
with open(f"{HID_DIR}/labels_B.txt", "w") as f: f.write(fmt_labels(labels_B))
with open(f"{HID_DIR}/layout_inst_B.txt", "w") as f: f.write(fmt_inst(lay_B))
with open(f"{HID_DIR}/sch_inst_B.txt", "w") as f: f.write(fmt_sch(sch_B))
with open(f"{HID_DIR}/base_cfg_B2.json", "w") as f: json.dump(base_B2, f, indent=2)
with open(f"{HID_DIR}/patch_B2.json", "w") as f: json.dump(patch_B2, f, indent=2)
with open(f"{HID_DIR}/labels_B2.txt", "w") as f: f.write(fmt_labels(labels_B2))
with open(f"{HID_DIR}/layout_inst_B2.txt", "w") as f: f.write(fmt_inst(lay_B2))
with open(f"{HID_DIR}/sch_inst_B2.txt", "w") as f: f.write(fmt_sch(sch_B2))

manifest = {
    "case_id": CASE,
    "hidden_inputs": ["B", "B2"],
    "B": {"base": "base_cfg_B.json", "patch": "patch_B.json", "labels": "labels_B.txt",
          "layout_inst": "layout_inst_B.txt", "sch_inst": "sch_inst_B.txt",
          "patch_section": "DifferentPair.Dummy.TopBottom", "axis": "y"},
    "B2": {"base": "base_cfg_B2.json", "patch": "patch_B2.json", "labels": "labels_B2.txt",
           "layout_inst": "layout_inst_B2.txt", "sch_inst": "sch_inst_B2.txt",
           "patch_section": "CurrentMirror.Dummy.LeftRight", "axis": "x"},
}
with open(f"{HID_DIR}/hidden_manifest.json", "w") as f: json.dump(manifest, f, indent=2)

# ---------------- prompt + task_brief ----------------
prompt = """你是模拟版图自动化工程师。我们用 Empyrean AnaWeave 的 Group Generator (GG) 流程给模拟单元生成版图，现在需要对差分对 (DifferentPair) 加左右 dummy，并验证配置合并与版图 dummy 是否正确落地。

我会给你一组文件（都在你的工作目录里）：
- base_cfg_A.json：项目默认的 group_generator_cfg 配置（含 PatternCfg.DifferentPair / CurrentMirror / Cascode 各结构的 Matching.Style/Mode/Rows/Dummy.LeftRight/TopBottom，以及 LibCfg / DeviceCfg / DummyCfg / TapCfg）。
- patch_A.json：用户对配置的部分覆盖（只给要改的叶子键，比如 {"PatternCfg":{"DifferentPair":{"Matching":{"Dummy":{"LeftRight":"1"}}}}}）。
- labels_A.txt：版图 label 扫描结果，每行 `text=<t> layer=<l> xy=(<x>,<y>)`。GG 约定：dummy 器件的 label 会被改写成 "O"，所以 "O" label 的位置就是 GG 放置 dummy 的位置。
- layout_inst_A.txt：版图 instance 列表，每行 `<name> <master> xy=(<x>,<y>)`。
- sch_inst_A.txt：原理图 instance 列表，每行 `<name> <master>`（无坐标）。

请写一个 Python3 命令行工具 `gg_cfg_merge_verify.py`，做以下事情：

1. 把 patch 深合并到 base 上（叶子覆盖，非覆盖键保留 base 原值），写出 `merged_cfg.json`。
2. 生成 `merge_report.md`：列出被 patch 改动的键路径及其旧值→新值，并声明哪些 PatternCfg 段未改动。
3. 解析 labels 文件，找出所有 text == "O" 的 label，写 `dummy_audit.json`：包含 n_labels、每个 O label 的 text/layer/xy、以及按 schematic instance 质心划分的方位分布（left/right/top/bottom 各多少个，质心 = sch_inst 所有实例 x、y 的平均值）。
4. 对比 layout_inst 与 sch_inst，写 `instance_diff.json`：schematic instances、layout-only instances（GG 生成的，名字不在 sch 里）、shared instances（名字同时在 sch 和 layout 里）。
5. 综合以上，写 `verdict.json`：包含 overall (PASS/FAIL) 和 checks 列表（每条 {name, pass}）。checks 至少含：merged_cfg 合法且深合并正确、patch 指定键已生效、被改段的兄弟键未变、其它 PatternCfg 段未变、O label 数 > 0、layout-only instance 数 > 0 且名字含 "Dum" 或以 "GG_DUM" 开头、所有 schematic instance 都出现在 layout 里。若 patch 改的是 DifferentPair.Dummy.LeftRight=1，则 verdict 还要求 left>0 且 right>0；若是 TopBottom=1 则要求 top>0 且 bottom>0。

命令行接口（必须严格按此）：
  python3 gg_cfg_merge_verify.py --base <base.json> --patch <patch.json> --labels <labels.txt> --layout-inst <li.txt> --sch-inst <si.txt> --outdir <dir>

<outdir> 里只产出这 5 个文件：merged_cfg.json, merge_report.md, dummy_audit.json, instance_diff.json, verdict.json。最后把整个工具脚本和你跑 B 输入（hidden/ 下的 B 文件）得到的 5 个输出文件一起打进 `outputs/submit.zip`（zip 内顶层就是这 6 个文件，不要带目录前缀）。

注意：判分会用 hidden/ 下的另一组输入 B、B2 重新跑你的脚本，所以不许硬编码 A 的任何具体值（单元名、坐标、patch 值、方位）。"""

with open(f"{A_DIR}/prompt.txt", "w") as f: f.write(prompt)

task_brief = """交付接口：写 gg_cfg_merge_verify.py（命令行参数 --base/--patch/--labels/--layout-inst/--sch-inst/--outdir），跑 hidden/B 的输入，把脚本 + 5 个输出文件打成 outputs/submit.zip（zip 顶层 6 文件，无目录前缀）。
判分：解 zip → py_compile → 用 hidden/B 与 B2 各跑一次脚本 → 校验 5 个输出文件结构与数值 → 反硬编码（源码不许出现 A 的单元名/坐标/patch 值字面量，B 输出必须来自 B 输入）。"""

with open(f"{A_DIR}/task_brief.md", "w") as f: f.write(task_brief)

print("assets written to", A_DIR)
print("hidden written to", HID_DIR)
