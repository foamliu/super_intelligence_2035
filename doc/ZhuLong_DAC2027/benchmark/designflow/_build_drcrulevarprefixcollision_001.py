#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-DrcRuleVarPrefixCollision-001.

Case type: mock-behavioral, physical_verify (Calibre DRC deck / LDR CSV analysis).
Trace source: 1794307210079_xnd0q (xinqiaoz @ 10.129.2.11, mc=249).
Real user intent (U#17): diagnose why DRC report flags "variable with unmatched value"
for variables like _V1_ENC_007_00_AUTO_ when the base rule V1_ENC_007_00 has no deck
VARIABLE — root cause is rule-name prefix collision (V1_ENC_007_00 is a prefix of
V1_ENC_007_00_Auto, so the matcher falsely associates the base LDR rule's value with
the Auto rule's variable).

Reframe: given a synthetic DRC QA report + LDR CSV + DRC deck (mirroring the prefix
collision structure but with different rule names/values), produce a structured JSON
diagnosis identifying (a) unmatched variables, (b) undefined DRC rules, (c) prefix
collisions (false mismatches), (d) genuine unmatched, (e) root cause.
"""
import os, json, shutil, zipfile, subprocess, sys, tempfile

CASE = "EDA-Eval-DesignFlow-DrcRuleVarPrefixCollision-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSET_DIR = os.path.join(BENCH, "assets", CASE)
REF_DIR   = os.path.join(BENCH, "reference", CASE)

# ---------- asset A (visible, sample_input/) ----------
REPORT_A = """# DRC QA Report
# product: G5_CIP_DEMO
# deckVersion: v0d5_Rev12
# prepOption: LPDRC_CHECK,CHECK_PRODUCT
# toolVersion: 1.1.0
# date: 2026-11-10
# ldrFile: G5_CIP_General_v0d9_Rev01_LDR_LPDDR.csv
# deckFile: calibreDRC_LP6.rule
[info] ldrCount=512
[warn] variableUndefinedDrc (variableUndefinedDrcCount=3, rules with no active deck VARIABLE, expected warn):
  M1_ENC_005_00
  M2_ENC_005_00
  M3_ENC_005_00
[error] variable with unmatched value (variableValueUnmatchedCount=4):
  _AT2_WMAX_001_05_B_
  _M1_ENC_005_00_AUTO_
  _M2_ENC_005_00_AUTO_
  _M3_ENC_005_00_AUTO_
[info] unmatchedDrcCount=1
[result] drcValue=fail
"""

LDR_A = """layer,sheet,category,rule_name,value1,value2,value3,value4,op1,op2,description
M1,LDR_AUTO_0.256,ENC,M1_ENC_005_00_Auto,0.015,0.015,0.004,0.004,>=,>=,Min - Enclosure of M1 by M2
M2,LDR_AUTO_0.256,ENC,M2_ENC_005_00_Auto,0,0,0,0,>=,>=,Min - Enclosure of M2 by M3
M3,LDR_AUTO_0.256,ENC,M3_ENC_005_00_Auto,0,0,0,0,>=,>=,Min - Enclosure of M3 by M4
NW,LDR_RULE_0.256,ENC,NW_ENC_007_00,0.56,0.82,0.143,0.21,>=,>=,Min - NW enclose Active
M1,LDR_RULE_0.256,ENC,M1_ENC_005_00,-0.020,-0.020,-0.006,-0.006,>=,>=,Min - Enclosure of M1 by M2
M2,LDR_RULE_0.256,ENC,M2_ENC_005_00,-0.060,-0.060,-0.015,-0.015,>=,>=,Min - Enclosure of M2 by M3
M3,LDR_RULE_0.256,ENC,M3_ENC_005_00,-0.060,-0.060,-0.015,-0.015,>=,>=,Min - Enclosure of M3 by M4
PL,LDR_RULE_0.256,ENC,PL_ENC_007_00,0.4815,0.66,0.123,0.169,>=,>=,Min - P LDD implant enclose
"""

DECK_A = """// DRC deck: calibreDRC_LP6.rule (preprocessed, LPDRC_CHECK)
// INCLUDE calibre.layer
// INCLUDE calibreDRC_main.rule

// ===== M1_ENC_005_00 (no active VARIABLE — commented out) =====
M1_ENC_005_00 {
  // VARIABLE _M1_ENC_005_00_ = -0.020
  chkenc M1 layer M2 min = -0.020
}

M1_ENC_005_00_Auto {
  VARIABLE _M1_ENC_005_00_AUTO_ = 0.015
  chkenc M1 layer M2 min = 0.015
}

// ===== M2_ENC_005_00 (no active VARIABLE) =====
M2_ENC_005_00 {
  // VARIABLE _M2_ENC_005_00_ = -0.060
  chkenc M2 layer M3 min = -0.060
}

M2_ENC_005_00_Auto {
  VARIABLE _M2_ENC_005_00_AUTO_ = 0
  chkenc M2 layer M3 min = 0
}

// ===== M3_ENC_005_00 (no active VARIABLE) =====
M3_ENC_005_00 {
  // VARIABLE _M3_ENC_005_00_ = -0.060
  chkenc M3 layer M4 min = -0.060
}

M3_ENC_005_00_Auto {
  VARIABLE _M3_ENC_005_00_AUTO_ = 0
  chkenc M3 layer M4 min = 0
}

// ===== NW_ENC_007_00 (has active VARIABLE, matches LDR — no collision) =====
NW_ENC_007_00 {
  VARIABLE _NW_ENC_007_00_ = 0.56
  chkenc NW layer active min = 0.56
}

// ===== AT2_WMAX_001_05_B (genuine unmatched — variable defined, no LDR rule) =====
AT2_WMAX_001_05_B {
  VARIABLE _AT2_WMAX_001_05_B_ = 0.123
  chkwidth AT2 max = 0.123
}
"""

RULE_SNIPPET_A = """# Rule snippet (excerpt from deck + LDR showing the prefix-collision structure)
#
# LDR CSV (two sheets):
#   LDR_RULE_0.256  -> M1_ENC_005_00      value -0.020   (manual rule)
#   LDR_AUTO_0.256  -> M1_ENC_005_00_Auto value 0.015    (auto rule)
#
# DRC deck:
#   M1_ENC_005_00       { // VARIABLE _M1_ENC_005_00_ = -0.020   (COMMENTED, no active var) }
#   M1_ENC_005_00_Auto  { VARIABLE _M1_ENC_005_00_AUTO_ = 0.015  (ACTIVE) }
#
# Report error:
#   [error] variable with unmatched value: _M1_ENC_005_00_AUTO_
#   [warn]  variableUndefinedDrc: M1_ENC_005_00
#
# Hypothesis: the QA matcher prefix-matches LDR rule names to deck VARIABLE names.
# M1_ENC_005_00 (base, no variable) is a prefix of M1_ENC_005_00_Auto (has variable
# _M1_ENC_005_00_AUTO_), so the matcher falsely expects M1_ENC_005_00's LDR value
# (-0.020) to match _M1_ENC_005_00_AUTO_'s value (0.015) -> false unmatched error.
"""

# ---------- hidden B (reverse, different names + a no-collision control) ----------
REPORT_B = """# DRC QA Report
# product: G7_XIP_DEMO
# deckVersion: v0d3_Rev07
# prepOption: LPDRC_CHECK,CHECK_PRODUCT
# toolVersion: 1.1.0
# date: 2026-11-12
# ldrFile: G7_XIP_General_v0d3_Rev07_LDR.csv
# deckFile: calibreDRC_XIP7.rule
[info] ldrCount=438
[warn] variableUndefinedDrc (variableUndefinedDrcCount=2, rules with no active deck VARIABLE, expected warn):
  V4_SP_002_10
  V5_SP_002_10
[error] variable with unmatched value (variableValueUnmatchedCount=3):
  _AT7_DRW_003_02_A_
  _V4_SP_002_10_AUTO_
  _V5_SP_002_10_AUTO_
[info] unmatchedDrcCount=1
[result] drcValue=fail
"""

LDR_B = """layer,sheet,category,rule_name,value1,value2,value3,value4,op1,op2,description
V4,LDR_AUTO_0.256,SP,V4_SP_002_10_Auto,0.030,0.030,0.008,0.008,>=,>=,Min - Spacing of V4 by M5
V5,LDR_AUTO_0.256,SP,V5_SP_002_10_Auto,0.040,0.040,0.010,0.010,>=,>=,Min - Spacing of V5 by M6
PL,LDR_RULE_0.256,ENC,PL_ENC_009_00,0.4815,0.66,0.123,0.169,>=,>=,Min - P LDD enclose
V4,LDR_RULE_0.256,SP,V4_SP_002_10,0.150,0.150,0.038,0.038,>=,>=,Min - Spacing of V4 by M5
V5,LDR_RULE_0.256,SP,V5_SP_002_10,0.200,0.200,0.050,0.050,>=,>=,Min - Spacing of V5 by M6
NL,LDR_RULE_0.256,ENC,NL_ENC_007_00,0.4815,0.66,0.123,0.169,>=,>=,Min - NL enclose channel
"""

DECK_B = """// DRC deck: calibreDRC_XIP7.rule (preprocessed, LPDRC_CHECK)
// INCLUDE calibre.layer
// INCLUDE calibreDRC_main.rule

// ===== V4_SP_002_10 (no active VARIABLE — commented out) =====
V4_SP_002_10 {
  // VARIABLE _V4_SP_002_10_ = 0.150
  chkspacing V4 layer M5 min = 0.150
}

V4_SP_002_10_Auto {
  VARIABLE _V4_SP_002_10_AUTO_ = 0.030
  chkspacing V4 layer M5 min = 0.030
}

// ===== V5_SP_002_10 (no active VARIABLE) =====
V5_SP_002_10 {
  // VARIABLE _V5_SP_002_10_ = 0.200
  chkspacing V5 layer M6 min = 0.200
}

V5_SP_002_10_Auto {
  VARIABLE _V5_SP_002_10_AUTO_ = 0.040
  chkspacing V5 layer M6 min = 0.040
}

// ===== PL_ENC_009_00 (has active VARIABLE, matches LDR — no collision) =====
PL_ENC_009_00 {
  VARIABLE _PL_ENC_009_00_ = 0.4815
  chkenc PL layer active min = 0.4815
}

// ===== NL_ENC_007_00 (has active VARIABLE, matches LDR — no collision) =====
NL_ENC_007_00 {
  VARIABLE _NL_ENC_007_00_ = 0.4815
  chkenc NL layer channel min = 0.4815
}

// ===== AT7_DRW_003_02_A (genuine unmatched — variable defined, no LDR rule) =====
AT7_DRW_003_02_A {
  VARIABLE _AT7_DRW_003_02_A_ = 0.077
  chkwidth AT7 max = 0.077
}
"""

# ---------- hidden B2 (minimal, cross-input guard) ----------
REPORT_B2 = """# DRC QA Report
# product: L1_CHIP_DEMO
# deckVersion: v1d0_Rev01
# prepOption: LPDRC_CHECK
# toolVersion: 1.1.0
# date: 2026-11-13
[info] ldrCount=64
[warn] variableUndefinedDrc (variableUndefinedDrcCount=1, rules with no active deck VARIABLE, expected warn):
  L1_DRW_001_00
[error] variable with unmatched value (variableValueUnmatchedCount=1):
  _L1_DRW_001_00_AUTO_
[info] unmatchedDrcCount=0
[result] drcValue=fail
"""

LDR_B2 = """layer,sheet,category,rule_name,value1,value2,value3,value4,op1,op2,description
L1,LDR_AUTO_0.256,DRW,L1_DRW_001_00_Auto,0.005,0.005,0.001,0.001,>=,>=,Min - Draw of L1
L1,LDR_RULE_0.256,DRW,L1_DRW_001_00,-0.010,-0.010,-0.002,-0.002,>=,>=,Min - Draw of L1
"""

DECK_B2 = """// DRC deck: calibreDRC_L1.rule (preprocessed)
// ===== L1_DRW_001_00 (no active VARIABLE — commented out) =====
L1_DRW_001_00 {
  // VARIABLE _L1_DRW_001_00_ = -0.010
  chkwidth L1 max = -0.010
}

L1_DRW_001_00_Auto {
  VARIABLE _L1_DRW_001_00_AUTO_ = 0.005
  chkwidth L1 max = 0.005
}
"""

PROMPT = """drcQa_G5_CIP_DECQA_v0d5_Rev12.report，这是问题出现的 report。注意第 78~80 行的报错，我下面以第 70 行的报错为例。
在 ldr 中，有 M1_ENC_005_00，M1_ENC_005_00_Auto 这两条 rule，在 DRC deck 中，也同样有这两条 rule。drc deck 中 M1_ENC_005_00 这条 rule 没有定义 variable，M1_ENC_005_00_Auto 定义了 variable _M1_ENC_005_00_AUTO_。
在最终的 report 中，有可能 M1_ENC_005_00 这条 ldr 误匹配到了 _M1_ENC_005_00_AUTO_ 这个 variable，导致最终报错。

请你写一个 Python 脚本（纯标准库，不依赖 calibre 或第三方 EDA 工具），读入三个文件——DRC QA report、LDR CSV、DRC deck——交叉验证，判断 report 里每个 "variable with unmatched value" 报错是不是因为这种 rule-name 前缀碰撞导致的误报，并输出 JSON 诊断报告。

具体要求：
1. 从 report 里解析出 variableValueUnmatchedCount 以及后面跟着的所有报错变量名（如 _M1_ENC_005_00_AUTO_、_AT2_WMAX_001_05_B_ 等），再解析出 variableUndefinedDrcCount 以及后面跟着的所有 rule 名（如 M1_ENC_005_00）。
2. 从 LDR CSV 里解析出每条 rule 的 sheet（LDR_RULE_0.256 还是 LDR_AUTO_0.256）、rule_name 和 value1。
3. 从 DRC deck 里解析出每个 rule block，以及 block 内"活跃的"VARIABLE 定义（不以 // 开头）和"被注释掉的"VARIABLE 定义（以 // 开头）。
4. 对 report 里每个报错的变量 _X_：
   - 找到 deck 里定义了这个变量的 rule。
   - 如果这个 rule 名以 _Auto 结尾，则取 base rule 名（去掉 _Auto 后缀），检查 base rule 是否在 deck 里"没有活跃 VARIABLE"且在 LDR_RULE sheet 里存在 —— 若是，则判定为「前缀碰撞误报」(prefix_collision)，并记录 base rule、auto rule、变量名、LDR 里 base 的 value1、LDR 里 auto 的 value1。
   - 否则判定为「真未匹配」(genuine_unmatched)。
5. 输出 JSON（打印到 stdout），包含以下顶层键：
   - "unmatched_variables": report 里所有报错变量名的列表（按出现顺序）
   - "undefined_drc_rules": report 里 variableUndefinedDrc 的 rule 名列表
   - "prefix_collisions": 前缀碰撞误报列表，每条含 base_rule, auto_rule, variable, ldr_base_value, ldr_auto_value
   - "genuine_unmatched": 真未匹配变量名列表
   - "root_cause": 若存在任何 prefix_collision 则为 "rule_name_prefix_collision"，否则为 "genuine_variable_mismatch"
   - "counts": {variableValueUnmatchedCount, variableUndefinedDrcCount, prefix_collision_count, genuine_unmatched_count}
   - "reproduction_confirmed": 布尔，当 prefix_collision 数量 > 0 且与 report 里 _AUTO_ 结尾的报错变量数量一致时为 true

接口：python3 solve.py <report_path> <ldr_csv_path> <drc_deck_path>
把结果以 JSON 打印到 stdout。
"""

TASK_BRIEF = """# 交付接口
- 入参（可见样例 A）：`sample_input/drc.report`（DRC QA 报告）、`sample_input/ldr.csv`（LDR 规则表）、`sample_input/drc.deck`（Calibre DRC deck 预处理文件）；判分时换用 hidden/b/ 下的三个文件（不同 rule 名、不同 value、含一个无碰撞对照）。
- 出参：把你写的 `solve.py`（纯标准库 Python3，CLI: `python3 solve.py <report> <ldr.csv> <drc.deck>`）和 `report.json`（你在 sample_input 三个文件上跑出的结果）打包成 `outputs/submit.zip`。
- `solve.py` 必须从命令行三个位置参数读取 report、ldr.csv、drc.deck 路径，把诊断 JSON 打印到 stdout。
- 不要在沙箱里调用 calibre 或任何 EDA 工具；只解析文本。
"""

MANIFEST = {
  "case_id": CASE,
  "hidden_inputs": [
    {
      "id": "b",
      "files": {"report": "hidden/b/drc.report_B", "ldr": "hidden/b/ldr_B.csv", "deck": "hidden/b/drc.deck_B"},
      "description": "primary hidden variant — different rule family (V4/V5_SP_002_10), different values, includes a no-collision control pair (PL_ENC_009_00 / NL_ENC_007_00 with matching variables)",
      "expected": {
        "unmatched_variables": ["_AT7_DRW_003_02_A_", "_V4_SP_002_10_AUTO_", "_V5_SP_002_10_AUTO_"],
        "undefined_drc_rules": ["V4_SP_002_10", "V5_SP_002_10"],
        "prefix_collision_count": 2,
        "genuine_unmatched_count": 1,
        "root_cause": "rule_name_prefix_collision"
      }
    },
    {
      "id": "b2",
      "files": {"report": "hidden/b2/drc.report_B2", "ldr": "hidden/b2/ldr_B2.csv", "deck": "hidden/b2/drc.deck_B2"},
      "description": "minimal cross-input variant — 1 collision pair (L1_DRW_001_00), 0 genuine unmatched",
      "expected": {
        "unmatched_variables": ["_L1_DRW_001_00_AUTO_"],
        "undefined_drc_rules": ["L1_DRW_001_00"],
        "prefix_collision_count": 1,
        "genuine_unmatched_count": 0,
        "root_cause": "rule_name_prefix_collision"
      }
    }
  ]
}

SOLVE_PY = r'''#!/usr/bin/env python3
"""Reference solution: diagnose DRC rule-name prefix collision.

CLI: python3 solve.py <report_path> <ldr_csv_path> <drc_deck_path>
Prints JSON diagnosis to stdout.
"""
import sys, json, csv, re

def parse_report(path):
    with open(path) as f:
        lines = [ln.rstrip("\n") for ln in f]
    unmatched = []
    undefined = []
    counts = {}
    i = 0
    n = len(lines)
    while i < n:
        s = lines[i].strip()
        # variableValueUnmatchedCount=N
        m = re.search(r"variableValueUnmatchedCount=(\d+)", s)
        if m and ("unmatched value" in s or "error" in s.lower()):
            counts["variableValueUnmatchedCount"] = int(m.group(1))
            # following indented lines starting with _ are variable names
            j = i + 1
            while j < n:
                t = lines[j]
                ts = t.strip()
                if not ts:
                    j += 1; continue
                if t.startswith(" ") or t.startswith("\t"):
                    if re.match(r"^_[A-Za-z0-9_]+_$", ts):
                        unmatched.append(ts)
                    j += 1
                else:
                    break
            i = j; continue
        # variableUndefinedDrcCount=N
        m = re.search(r"variableUndefinedDrcCount=(\d+)", s)
        if m and ("undefined" in s.lower() or "warn" in s.lower()):
            counts["variableUndefinedDrcCount"] = int(m.group(1))
            j = i + 1
            while j < n:
                t = lines[j]
                ts = t.strip()
                if not ts:
                    j += 1; continue
                if t.startswith(" ") or t.startswith("\t"):
                    if re.match(r"^[A-Za-z][A-Za-z0-9_]*$", ts):
                        undefined.append(ts)
                    j += 1
                else:
                    break
            i = j; continue
        i += 1
    return {"unmatched_variables": unmatched, "undefined_drc_rules": undefined, "counts": counts}

def parse_ldr(path):
    rules = {}
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("rule_name", "").strip()
            if not name:
                continue
            sheet = row.get("sheet", "").strip()
            try:
                v1 = float(row.get("value1", "0") or "0")
            except ValueError:
                v1 = 0.0
            rules[name] = {"sheet": sheet, "value1": v1, "category": row.get("category","").strip()}
    return rules

def parse_deck(path):
    rules = {}
    with open(path) as f:
        lines = [ln.rstrip("\n") for ln in f]
    i = 0
    n = len(lines)
    cur = None
    depth = 0
    while i < n:
        s = lines[i].strip()
        # rule block header: NAME {
        m = re.match(r"^([A-Za-z][A-Za-z0-9_]*)\s*\{", s)
        if m and not s.startswith("//"):
            cur = m.group(1)
            rules[cur] = {"active_variables": [], "commented_variables": []}
            depth = 1
            i += 1; continue
        if cur is not None and depth > 0:
            # track braces on this line
            for ch in s:
                if ch == "{": depth += 1
                elif ch == "}": depth -= 1
            if depth <= 0:
                cur = None
                depth = 0
                i += 1; continue
            # active VARIABLE
            mv = re.match(r"^VARIABLE\s+(_[A-Za-z0-9_]+_)\s*=\s*(-?[\d.]+)", s)
            if mv:
                rules[cur]["active_variables"].append({"name": mv.group(1), "value": mv.group(2)})
            # commented VARIABLE
            mcv = re.match(r"^//\s*VARIABLE\s+(_[A-Za-z0-9_]+_)\s*=\s*(-?[\d.]+)", s)
            if mcv:
                rules[cur]["commented_variables"].append({"name": mcv.group(1), "value": mcv.group(2)})
        i += 1
    return rules

def diagnose(report, ldr, deck):
    unmatched = report["unmatched_variables"]
    undefined = report["undefined_drc_rules"]
    counts = dict(report["counts"])
    prefix_collisions = []
    genuine_unmatched = []
    # map variable -> deck rule that defines it (active)
    var_to_rule = {}
    for rname, rinfo in deck.items():
        for av in rinfo["active_variables"]:
            var_to_rule[av["name"]] = rname
    for var in unmatched:
        rule = var_to_rule.get(var)
        if rule is None:
            genuine_unmatched.append(var); continue
        if rule.endswith("_Auto"):
            base = rule[:-len("_Auto")]
            base_deck = deck.get(base)
            base_ldr = ldr.get(base)
            auto_ldr = ldr.get(rule)
            # base rule in deck with no active variables, and base in LDR_RULE sheet
            base_no_active = base_deck is not None and len(base_deck["active_variables"]) == 0
            base_in_ldr_rule = base_ldr is not None and base_ldr["sheet"].startswith("LDR_RULE")
            if base_no_active and base_in_ldr_rule:
                prefix_collisions.append({
                    "base_rule": base,
                    "auto_rule": rule,
                    "variable": var,
                    "ldr_base_value": base_ldr["value1"] if base_ldr else None,
                    "ldr_auto_value": auto_ldr["value1"] if auto_ldr else None
                })
            else:
                genuine_unmatched.append(var)
        else:
            genuine_unmatched.append(var)
    auto_unmatched = [v for v in unmatched if v.endswith("_AUTO_")]
    reproduction_confirmed = len(prefix_collisions) > 0 and len(prefix_collisions) == len(auto_unmatched)
    root_cause = "rule_name_prefix_collision" if prefix_collisions else "genuine_variable_mismatch"
    counts["prefix_collision_count"] = len(prefix_collisions)
    counts["genuine_unmatched_count"] = len(genuine_unmatched)
    return {
        "unmatched_variables": unmatched,
        "undefined_drc_rules": undefined,
        "prefix_collisions": prefix_collisions,
        "genuine_unmatched": genuine_unmatched,
        "root_cause": root_cause,
        "counts": counts,
        "reproduction_confirmed": reproduction_confirmed
    }

def main():
    if len(sys.argv) != 4:
        print("usage: solve.py <report> <ldr.csv> <drc.deck>", file=sys.stderr)
        sys.exit(2)
    report = parse_report(sys.argv[1])
    ldr = parse_ldr(sys.argv[2])
    deck = parse_deck(sys.argv[3])
    result = diagnose(report, ldr, deck)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
'''

CHECK_PY = r'''#!/usr/bin/env python3
"""Check function for EDA-Eval-DesignFlow-DrcRuleVarPrefixCollision-001.

判分接口: check(deliverable, workdir) -> True/raise
- deliverable: path to submit.zip produced by SUT
- workdir: judge working directory containing hidden/b/ and hidden/b2/ files + this check.py

判分策略:
- 解 submit.zip 拿到 SUT 的 solve.py（在独立临时目录）
- 用 subprocess 在 hidden B 和 B2 上跑 SUT 的 solve.py（真跑候选，§4.2）
- 断言 ≥8 个独立条件（每条可单独 FAIL），标签 a-n
- 退化提交回归（§4.9）：空壳 / 只 print / 硬编码 A 数据 三种假提交必须全 FAIL
"""
import sys, os, json, zipfile, subprocess, tempfile, shutil

class CheckFail(Exception):
    pass

def _cond(idx, ok, msg):
    if not ok:
        raise CheckFail(f"  cond {idx} FAIL: {msg}")

# ---- expected ground truth for hidden B and B2 (independent of reference solve) ----
B_EXPECTED = {
    "unmatched_variables": ["_AT7_DRW_003_02_A_", "_V4_SP_002_10_AUTO_", "_V5_SP_002_10_AUTO_"],
    "undefined_drc_rules": ["V4_SP_002_10", "V5_SP_002_10"],
    "prefix_collisions": [
        {"base_rule": "V4_SP_002_10", "auto_rule": "V4_SP_002_10_Auto", "variable": "_V4_SP_002_10_AUTO_", "ldr_base_value": 0.150, "ldr_auto_value": 0.030},
        {"base_rule": "V5_SP_002_10", "auto_rule": "V5_SP_002_10_Auto", "variable": "_V5_SP_002_10_AUTO_", "ldr_base_value": 0.200, "ldr_auto_value": 0.040},
    ],
    "genuine_unmatched": ["_AT7_DRW_003_02_A_"],
    "root_cause": "rule_name_prefix_collision",
    "counts": {"variableValueUnmatchedCount": 3, "variableUndefinedDrcCount": 2, "prefix_collision_count": 2, "genuine_unmatched_count": 1},
    "reproduction_confirmed": True,
}
B2_EXPECTED = {
    "unmatched_variables": ["_L1_DRW_001_00_AUTO_"],
    "undefined_drc_rules": ["L1_DRW_001_00"],
    "prefix_collisions": [
        {"base_rule": "L1_DRW_001_00", "auto_rule": "L1_DRW_001_00_Auto", "variable": "_L1_DRW_001_00_AUTO_", "ldr_base_value": -0.010, "ldr_auto_value": 0.005},
    ],
    "genuine_unmatched": [],
    "root_cause": "rule_name_prefix_collision",
    "counts": {"variableValueUnmatchedCount": 1, "variableUndefinedDrcCount": 1, "prefix_collision_count": 1, "genuine_unmatched_count": 0},
    "reproduction_confirmed": True,
}

def _run_sut(solve_py, report, ldr, deck, tmpdir):
    proc = subprocess.run(
        [sys.executable, solve_py, report, ldr, deck],
        capture_output=True, text=True, timeout=60, cwd=tmpdir,
    )
    if proc.returncode != 0:
        raise CheckFail(f"SUT solve.py exited {proc.returncode}; stderr={proc.stderr[:400]}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise CheckFail(f"SUT output not JSON: {e}; head={proc.stdout[:300]}")

def _as_set_names(coll, key=None):
    s = set()
    for item in coll:
        if key and isinstance(item, dict):
            s.add(item.get(key))
        else:
            s.add(item)
    return s

def _collisions_match(got, exp):
    """Compare prefix_collisions by (base_rule, auto_rule, variable, ldr_base_value, ldr_auto_value)."""
    g = set((c.get("base_rule"), c.get("auto_rule"), c.get("variable"), round(float(c.get("ldr_base_value", 0)), 6), round(float(c.get("ldr_auto_value", 0)), 6)) for c in got)
    e = set((c.get("base_rule"), c.get("auto_rule"), c.get("variable"), round(float(c.get("ldr_base_value", 0)), 6), round(float(c.get("ldr_auto_value", 0)), 6)) for c in exp)
    return g == e

def check(deliverable, workdir):
    # extract submit.zip into a temp dir
    tmp = tempfile.mkdtemp(prefix="chk_drcpc_")
    try:
        if not os.path.isfile(deliverable):
            _cond("a", False, f"deliverable not a file: {deliverable}")
        try:
            with zipfile.ZipFile(deliverable) as z:
                z.extractall(tmp)
        except Exception as e:
            _cond("a", False, f"submit.zip not extractable: {e}")
        _cond("a", os.path.isfile(os.path.join(tmp, "solve.py")), "zip missing solve.py")

        # hidden B / B2 paths
        b_report = os.path.join(workdir, "hidden", "b", "drc.report_B")
        b_ldr    = os.path.join(workdir, "hidden", "b", "ldr_B.csv")
        b_deck   = os.path.join(workdir, "hidden", "b", "drc.deck_B")
        b2_report = os.path.join(workdir, "hidden", "b2", "drc.report_B2")
        b2_ldr    = os.path.join(workdir, "hidden", "b2", "ldr_B2.csv")
        b2_deck   = os.path.join(workdir, "hidden", "b2", "drc.deck_B2")
        _cond("b", all(os.path.isfile(p) for p in [b_report, b_ldr, b_deck, b2_report, b2_ldr, b2_deck]),
              "hidden B/B2 files missing in workdir")

        solve_py = os.path.join(tmp, "solve.py")

        # run SUT on hidden B
        outB = _run_sut(solve_py, b_report, b_ldr, b_deck, tmp)
        _cond("c", isinstance(outB, dict) and all(k in outB for k in
              ["unmatched_variables","undefined_drc_rules","prefix_collisions","genuine_unmatched","root_cause","counts","reproduction_confirmed"]),
              "output JSON missing required top-level keys")

        _cond("d", outB.get("unmatched_variables") == B_EXPECTED["unmatched_variables"],
              f"unmatched_variables mismatch: got {outB.get('unmatched_variables')}")

        _cond("e", outB.get("undefined_drc_rules") == B_EXPECTED["undefined_drc_rules"],
              f"undefined_drc_rules mismatch: got {outB.get('undefined_drc_rules')}")

        _cond("f", _collisions_match(outB.get("prefix_collisions", []), B_EXPECTED["prefix_collisions"]),
              f"prefix_collisions mismatch: got {outB.get('prefix_collisions')}")

        _cond("g", outB.get("genuine_unmatched") == B_EXPECTED["genuine_unmatched"],
              f"genuine_unmatched mismatch: got {outB.get('genuine_unmatched')}")

        _cond("h", outB.get("root_cause") == B_EXPECTED["root_cause"],
              f"root_cause mismatch: got {outB.get('root_cause')}")

        cB = outB.get("counts", {})
        _cond("i", cB.get("variableValueUnmatchedCount") == 3 and cB.get("variableUndefinedDrcCount") == 2
              and cB.get("prefix_collision_count") == 2 and cB.get("genuine_unmatched_count") == 1,
              f"counts mismatch for B: {cB}")

        _cond("j", outB.get("reproduction_confirmed") == True,
              f"reproduction_confirmed should be true for B: got {outB.get('reproduction_confirmed')}")

        # run SUT on hidden B2 (cross-input guard, anti-hardcoding)
        outB2 = _run_sut(solve_py, b2_report, b2_ldr, b2_deck, tmp)
        _cond("k", outB2.get("unmatched_variables") == B2_EXPECTED["unmatched_variables"]
              and outB2.get("undefined_drc_rules") == B2_EXPECTED["undefined_drc_rules"],
              f"B2 unmatched/undefined mismatch (anti-hardcode): got {outB2.get('unmatched_variables')} / {outB2.get('undefined_drc_rules')}")
        _cond("l", _collisions_match(outB2.get("prefix_collisions", []), B2_EXPECTED["prefix_collisions"])
              and outB2.get("genuine_unmatched") == [],
              f"B2 prefix_collisions/genuine mismatch: got {outB2.get('prefix_collisions')}")
        _cond("m", outB2.get("counts",{}).get("prefix_collision_count") == 1
              and outB2.get("counts",{}).get("genuine_unmatched_count") == 0
              and outB2.get("root_cause") == "rule_name_prefix_collision",
              f"B2 counts/root_cause mismatch: {outB2.get('counts')} / {outB2.get('root_cause')}")

        # degeneration guard: B's prefix_collision_count must be 2 (not A's 3) — anti-hardcode of A
        _cond("n", cB.get("prefix_collision_count") == 2,
              f"B prefix_collision_count=={cB.get('prefix_collision_count')} (must be 2, not A's 3 — anti-hardcode)")

        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
'''

# ---- negatives ----
NEG_EMPTY = r'''#!/usr/bin/env python3
import sys, json
# empty stub: produces nothing
print("")
'''
NEG_PRINT = r'''#!/usr/bin/env python3
import sys, json
# hardcode A's expected output (3 collisions) regardless of input
out = {
  "unmatched_variables": ["_AT2_WMAX_001_05_B_","_M1_ENC_005_00_AUTO_","_M2_ENC_005_00_AUTO_","_M3_ENC_005_00_AUTO_"],
  "undefined_drc_rules": ["M1_ENC_005_00","M2_ENC_005_00","M3_ENC_005_00"],
  "prefix_collisions": [
    {"base_rule":"M1_ENC_005_00","auto_rule":"M1_ENC_005_00_Auto","variable":"_M1_ENC_005_00_AUTO_","ldr_base_value":-0.020,"ldr_auto_value":0.015},
    {"base_rule":"M2_ENC_005_00","auto_rule":"M2_ENC_005_00_Auto","variable":"_M2_ENC_005_00_AUTO_","ldr_base_value":-0.060,"ldr_auto_value":0},
    {"base_rule":"M3_ENC_005_00","auto_rule":"M3_ENC_005_00_Auto","variable":"_M3_ENC_005_00_AUTO_","ldr_base_value":-0.060,"ldr_auto_value":0}
  ],
  "genuine_unmatched": ["_AT2_WMAX_001_05_B_"],
  "root_cause": "rule_name_prefix_collision",
  "counts": {"variableValueUnmatchedCount":4,"variableUndefinedDrcCount":3,"prefix_collision_count":3,"genuine_unmatched_count":1},
  "reproduction_confirmed": True
}
print(json.dumps(out, indent=2))
'''
NEG_DEL_CORE = r'''#!/usr/bin/env python3
import sys, json, csv, re
# delete core: parse report but skip the prefix-collision detection (always genuine)
def parse_report(path):
    unmatched=[]; undefined=[]; counts={}
    with open(path) as f:
        lines=[ln.rstrip("\n") for ln in f]
    i=0
    while i<len(lines):
        s=lines[i].strip()
        m=re.search(r"variableValueUnmatchedCount=(\d+)",s)
        if m and ("unmatched value" in s or "error" in s.lower()):
            counts["variableValueUnmatchedCount"]=int(m.group(1))
            j=i+1
            while j<len(lines) and (lines[j].startswith(" ") or lines[j].startswith("\t")):
                ts=lines[j].strip()
                if re.match(r"^_[A-Za-z0-9_]+_$",ts): unmatched.append(ts)
                j+=1
            i=j; continue
        m=re.search(r"variableUndefinedDrcCount=(\d+)",s)
        if m and ("undefined" in s.lower() or "warn" in s.lower()):
            counts["variableUndefinedDrcCount"]=int(m.group(1))
            j=i+1
            while j<len(lines) and (lines[j].startswith(" ") or lines[j].startswith("\t")):
                ts=lines[j].strip()
                if re.match(r"^[A-Za-z][A-Za-z0-9_]*$",ts): undefined.append(ts)
                j+=1
            i=j; continue
        i+=1
    return {"unmatched_variables":unmatched,"undefined_drc_rules":undefined,"counts":counts}
report=parse_report(sys.argv[1])
# DELETED CORE: no deck/ldr parsing, no prefix-collision detection -> everything is genuine
out={
  "unmatched_variables": report["unmatched_variables"],
  "undefined_drc_rules": report["undefined_drc_rules"],
  "prefix_collisions": [],
  "genuine_unmatched": report["unmatched_variables"],
  "root_cause": "genuine_variable_mismatch",
  "counts": {**report["counts"], "prefix_collision_count":0, "genuine_unmatched_count":len(report["unmatched_variables"])},
  "reproduction_confirmed": False
}
print(json.dumps(out,indent=2))
'''
NEG_HARDCODE_B = r'''#!/usr/bin/env python3
import sys, json
# hardcode B's expected (cheating): would pass B but fail B2 cross-input guard
out = {
  "unmatched_variables": ["_AT7_DRW_003_02_A_","_V4_SP_002_10_AUTO_","_V5_SP_002_10_AUTO_"],
  "undefined_drc_rules": ["V4_SP_002_10","V5_SP_002_10"],
  "prefix_collisions": [
    {"base_rule":"V4_SP_002_10","auto_rule":"V4_SP_002_10_Auto","variable":"_V4_SP_002_10_AUTO_","ldr_base_value":0.150,"ldr_auto_value":0.030},
    {"base_rule":"V5_SP_002_10","auto_rule":"V5_SP_002_10_Auto","variable":"_V5_SP_002_10_AUTO_","ldr_base_value":0.200,"ldr_auto_value":0.040}
  ],
  "genuine_unmatched": ["_AT7_DRW_003_02_A_"],
  "root_cause": "rule_name_prefix_collision",
  "counts": {"variableValueUnmatchedCount":3,"variableUndefinedDrcCount":2,"prefix_collision_count":2,"genuine_unmatched_count":1},
  "reproduction_confirmed": True
}
print(json.dumps(out,indent=2))
'''

NEG_SELFTEST = r'''#!/usr/bin/env python3
"""negative_selftest: every negative must FAIL check(). Exit 0 = all FAIL (good)."""
import sys, os, json, zipfile, subprocess, tempfile, shutil, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
# HERE = reference/<CASE>/
# assets dir = ../../assets/<CASE>/  (sibling of reference/)
CASE_ASSET = os.path.normpath(os.path.join(HERE, "..", "..", "assets", os.path.basename(HERE)))
def setup_workdir():
    tmp = tempfile.mkdtemp(prefix="negtest_")
    hid = os.path.join(tmp, "hidden")
    os.makedirs(os.path.join(hid, "b"), exist_ok=True)
    os.makedirs(os.path.join(hid, "b2"), exist_ok=True)
    # find hidden files from assets
    src_hidden = os.path.join(CASE_ASSET, "hidden")
    for sub in ["b","b2"]:
        sd = os.path.join(src_hidden, sub)
        if os.path.isdir(sd):
            for fn in os.listdir(sd):
                shutil.copy(os.path.join(sd, fn), os.path.join(hid, sub, fn))
    return tmp

def load_check():
    spec = importlib.util.spec_from_file_location("check_mod", os.path.join(HERE, "check.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def make_submit(neg_py_text, tmpdir):
    zp = os.path.join(tmpdir, "submit.zip")
    with zipfile.ZipFile(zp, "w") as z:
        z.writestr("solve.py", neg_py_text)
    return zp

def run_one(name, neg_text, check_mod, workdir):
    t2 = tempfile.mkdtemp(prefix="negrun_")
    try:
        zp = make_submit(neg_text, t2)
        try:
            ok = check_mod.check(zp, workdir)
            return name, ("PASS-BAD", ok)  # negative should NOT pass
        except Exception as e:
            return name, ("FAIL-GOOD", str(e)[:200])
    finally:
        shutil.rmtree(t2, ignore_errors=True)

def main():
    negs = {
        "solve_empty": open(os.path.join(HERE, "negative", "solve_empty.py")).read(),
        "solve_print_expected": open(os.path.join(HERE, "negative", "solve_print_expected.py")).read(),
        "solve_delete_core": open(os.path.join(HERE, "negative", "solve_delete_core.py")).read(),
        "solve_hardcode_B": open(os.path.join(HERE, "negative", "solve_hardcode_B.py")).read(),
    }
    check_mod = load_check()
    workdir = setup_workdir()
    try:
        all_good = True
        for name, txt in negs.items():
            n, (status, detail) = run_one(name, txt, check_mod, workdir)
            print(f"{n}: {status} ({detail})")
            if status != "FAIL-GOOD":
                all_good = False
        if not all_good:
            print("NEGATIVE SELFTEST FAILED: at least one negative passed check (BAD)")
            sys.exit(1)
        print("NEGATIVE SELFTEST OK: all negatives FAIL check (good)")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

if __name__ == "__main__":
    main()
'''

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print("wrote", path)

def main():
    # asset A (visible)
    si = os.path.join(ASSET_DIR, "sample_input")
    write(os.path.join(si, "drc.report"), REPORT_A)
    write(os.path.join(si, "ldr.csv"), LDR_A)
    write(os.path.join(si, "drc.deck"), DECK_A)
    write(os.path.join(si, "rule.snippet"), RULE_SNIPPET_A)
    write(os.path.join(ASSET_DIR, "prompt.txt"), PROMPT)
    write(os.path.join(ASSET_DIR, "task_brief.md"), TASK_BRIEF)
    # hidden B
    hb = os.path.join(ASSET_DIR, "hidden", "b")
    write(os.path.join(hb, "drc.report_B"), REPORT_B)
    write(os.path.join(hb, "ldr_B.csv"), LDR_B)
    write(os.path.join(hb, "drc.deck_B"), DECK_B)
    # hidden B2
    hb2 = os.path.join(ASSET_DIR, "hidden", "b2")
    write(os.path.join(hb2, "drc.report_B2"), REPORT_B2)
    write(os.path.join(hb2, "ldr_B2.csv"), LDR_B2)
    write(os.path.join(hb2, "drc.deck_B2"), DECK_B2)
    write(os.path.join(ASSET_DIR, "hidden", "hidden_manifest.json"), json.dumps(MANIFEST, indent=2))
    # reference
    write(os.path.join(REF_DIR, "solve.py"), SOLVE_PY)
    write(os.path.join(REF_DIR, "check.py"), CHECK_PY)
    # negatives
    ng = os.path.join(REF_DIR, "negative")
    write(os.path.join(ng, "solve_empty.py"), NEG_EMPTY)
    write(os.path.join(ng, "solve_print_expected.py"), NEG_PRINT)
    write(os.path.join(ng, "solve_delete_core.py"), NEG_DEL_CORE)
    write(os.path.join(ng, "solve_hardcode_B.py"), NEG_HARDCODE_B)
    write(os.path.join(REF_DIR, "negative_selftest.py"), NEG_SELFTEST)
    print("\n=== BUILD COMPLETE ===")

if __name__ == "__main__":
    main()
