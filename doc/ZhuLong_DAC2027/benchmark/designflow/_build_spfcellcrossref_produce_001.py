#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build script for EDA-Eval-DesignFlow-SpfCellCrossRefProduce-001.

Generates:
  assets/EDA-Eval-DesignFlow-SpfCellCrossRefProduce-001/        (visible A)
      aaa_A.txt no_vcap_A.txt skip_cell_A.txt ignore_cells_A.txt control_A.txt
      task_brief.md prompt.txt
      hidden/aaa_B.txt no_vcap_B.txt skip_cell_B.txt ignore_cells_B.txt control_B.txt
            hidden_manifest.json
  reference/EDA-Eval-DesignFlow-SpfCellCrossRefProduce-001/
      check_cells_in_refs_ref.py   (reference solution)
      check.py                     (k=18, B-side + A'-gold cross-check)
      negative/neg_fake_empty.py
      negative/neg_fake_print_only.py
      negative/neg_fake_core_deleted.py
      negative/neg_fake_hardcode_b.py
      negative_selftest.py

Self-verification: ref 18/18 PASS on B + A'; 4 negatives all FAIL.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import zipfile

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE_ID = "EDA-Eval-DesignFlow-SpfCellCrossRefProduce-001"
ASSET_DIR = os.path.join(BENCH, "assets", CASE_ID)
HIDDEN_DIR = os.path.join(ASSET_DIR, "hidden")
REF_DIR = os.path.join(BENCH, "reference", CASE_ID)
NEG_DIR = os.path.join(REF_DIR, "negative")

# ===========================================================================
# DATA DESIGN  (token-structurally-disjoint A / B / A')
# ===========================================================================
# Style A: row/col/driver/SCMOS cells with version dates  (visible to SUT)
# Style B: col-decode / wordline / sense-amp / regulator cells             (hidden)
# Style A': bitline / rdmux / nand / nor / precharge / tmos cells          (derived)

# ---- A (visible) ----
AAA_A = [
    f"RA_XYQ_Drv_{i:02d}_2026" for i in range(1, 9)
] + [
    f"WCK2Ti_PS_{i:04d}" for i in range(1001, 1009)
] + [
    f"Spnand3x2_{c}" for c in ["A", "B", "C", "D"]
] + [
    f"Spaoi21_{c}" for c in ["A", "B", "C"]
] + [
    f"dynamic_Latch_{c}" for c in ["A", "B", "C", "D", "E"]
] + [
    f"SCmos_ColBuf_{c}" for c in ["A", "B", "C", "D", "E", "F"]
] + [
    f"RAbus_Hold_{i}" for i in range(1, 4)
] + [
    f"NoMatch_A_{i:02d}" for i in range(1, 9)
]  # 8+8+4+3+5+6+3+8 = 45 cells

NO_VCAP_A = [  # 30 cells, 3 # comment lines
    "# no_vcap list A",
    "# generated 20261031",
    "RA_XYQ_Drv_01_2026", "RA_XYQ_Drv_03_2026", "RA_XYQ_Drv_05_2026",
    "WCK2Ti_PS_1002", "WCK2Ti_PS_1004",
    "Spnand3x2_A", "Spnand3x2_C",
    "dynamic_Latch_A", "dynamic_Latch_C",
    "SCmos_ColBuf_A", "SCmos_ColBuf_D",
    "RAbus_Hold_1",
] + [f"FillerNV_{i:03d}" for i in range(1, 18)] + ["# end"]

SKIP_CELL_A = [  # 12 cells
    "RA_XYQ_Drv_02_2026", "RA_XYQ_Drv_07_2026",
    "WCK2Ti_PS_1003",
    "Spnand3x2_B",
    "dynamic_Latch_B",
] + [f"FillerSC_{i}" for i in range(1, 8)]

IGNORE_CELLS_A = [  # 6 globs
    "Spnand*", "Spaoi*", "dynamic_*", "SCmos_*", "WCK2*", "RAbus*",
]

# control: .option finesim_mode="cell:prohd cell:spicehd ..." + .option finesim_ignore="..."
CONTROL_MODE_A = [  # 20 cells with :suffix
    "RA_XYQ_Drv_04_2026:prohd", "RA_XYQ_Drv_06_2026:spicehd",
    "WCK2Ti_PS_1005:prohd",
    "Spnand3x2_D:prohd",
    "dynamic_Latch_D:spicehd",
    "SCmos_ColBuf_B:prohd", "SCmos_ColBuf_E:spicehd",
] + [f"FillerCM_A_{i}:prohd" for i in range(1, 14)]
CONTROL_IGNORE_A = [  # 30 cells
    "RA_XYQ_Drv_08_2026",
    "WCK2Ti_PS_1006",
    "Spaoi21_A",
    "dynamic_Latch_E",
    "SCmos_ColBuf_C",
    "RAbus_Hold_2",
] + [f"FillerCI_A_{i}" for i in range(1, 25)]

# ---- B (hidden) ----
AAA_B = [
    f"ColDec_BnkA_v{i}" for i in range(1, 7)
] + [
    f"WlDrv_Main_{i:02d}" for i in range(1, 6)
] + [
    f"Saoi22_X{i}" for i in range(1, 8)
] + [
    f"Snand4_Y{i}" for i in range(1, 5)
] + [
    f"vrg_Latch_Z{i}" for i in range(1, 6)
] + [
    f"CMos_PreBuf_W{i}" for i in range(1, 8)
] + [
    f"Xpre_Grd_{i}" for i in range(1, 5)
] + [
    f"RandFillB_{i:02d}" for i in range(1, 10)
]  # 6+5+7+4+5+7+4+9 = 47 cells

NO_VCAP_B = [  # 40 cells + 5 # comments
    "# no_vcap list B",
    "# generated 20261101",
    "ColDec_BnkA_v1", "ColDec_BnkA_v3", "ColDec_BnkA_v5",
    "WlDrv_Main_02", "WlDrv_Main_04",
    "Saoi22_X2", "Saoi22_X5",
    "Snand4_Y1", "Snand4_Y3",
    "vrg_Latch_Z2",
    "CMos_PreBuf_W1", "CMos_PreBuf_W4",
    "Xpre_Grd_2",
] + [f"FillerNVB_{i:03d}" for i in range(1, 26)] + [
    "# section break",
    "# end of list",
]

SKIP_CELL_B = [  # 15 cells
    "ColDec_BnkA_v2", "ColDec_BnkA_v4",
    "WlDrv_Main_01",
    "Saoi22_X1", "Saoi22_X4",
    "CMos_PreBuf_W2",
] + [f"FillerSCB_{i}" for i in range(1, 10)]

IGNORE_CELLS_B = [  # 7 globs
    "Saoi*", "Snand*", "vrg_*", "CMos_*", "WlDrv*", "ColDec*", "Xpre*",
]

CONTROL_MODE_B = [  # 25 cells with :suffix
    "ColDec_BnkA_v6:prohd",
    "WlDrv_Main_03:spicehd", "WlDrv_Main_05:prohd",
    "Saoi22_X3:prohd", "Saoi22_X6:spicehd",
    "Snand4_Y2:prohd",
    "vrg_Latch_Z1:spicehd", "vrg_Latch_Z4:prohd",
    "CMos_PreBuf_W3:spicehd",
] + [f"FillerCMB_{i}:prohd" for i in range(1, 17)]
CONTROL_IGNORE_B = [  # 35 cells
    "ColDec_BnkA_v2",
    "WlDrv_Main_02",
    "Saoi22_X7",
    "Snand4_Y4",
    "vrg_Latch_Z3", "vrg_Latch_Z5",
    "CMos_PreBuf_W5", "CMos_PreBuf_W7",
    "Xpre_Grd_1",
] + [f"FillerCIB_{i}" for i in range(1, 27)]

# ---- A' (derived from B by full token transformation) ----
# map: ColDec->BitLine, WlDrv->Rdmux, Saoi->Nand, Snand->Nor,
#      vrg->preChg, CMos->Tmos, Xpre->CapBuf, RandFill->OrphanFill
_AP_PREFIX = {
    "ColDec": "BitLine", "WlDrv": "Rdmux", "Saoi": "Nand2x", "Snand": "Nor3x",
    "vrg": "preChg", "CMos": "Tmos", "Xpre": "CapBuf", "RandFillB": "OrphanFillP",
    "FillerNVB": "FillerNVP", "FillerSCB": "FillerSCP",
    "FillerCMB": "FillerCMP", "FillerCIB": "FillerCIP",
}


def _ap_cell(name):
    for k, v in _AP_PREFIX.items():
        if name.startswith(k):
            return v + name[len(k):]
    return name


# A' aaa is a genuine subset shift of B aaa (6 matched cells dropped + 4 new
# unmatched fillers), so A'-gold matched COUNTS differ from B-gold on every
# source — this defeats B-hardcode stubs that print B-gold counts regardless
# of input. The cell NAMES also differ (prefix-transformed) so set cross-checks
# are independently effective.
_AP_DROP = {"BitLine_BnkA_v1", "BitLine_BnkA_v2", "Rdmux_Main_01",
            "Rdmux_Main_02", "Nand2x22_X2", "Tmos_PreBuf_W1"}

AAA_AP = [_ap_cell(c) for c in AAA_B if _ap_cell(c) not in _AP_DROP] + \
         ["OrphanFillP_%03d" % i for i in range(101, 105)]
NO_VCAP_AP = [_ap_cell(c) if not c.startswith("#") else c for c in NO_VCAP_B]
SKIP_CELL_AP = [_ap_cell(c) for c in SKIP_CELL_B]
IGNORE_CELLS_AP = [_ap_cell(g) for g in IGNORE_CELLS_B]  # globs transform too
CONTROL_MODE_AP = [(_ap_cell(c.split(":")[0]) + ":" + c.split(":")[1]) for c in CONTROL_MODE_B]
CONTROL_IGNORE_AP = [_ap_cell(c) for c in CONTROL_IGNORE_B]

# A' aaa is a genuine subset shift of B aaa (6 matched cells dropped + 4 new
# unmatched fillers), so A'-gold matched COUNTS differ from B-gold on every
# source — this defeats B-hardcode stubs that print B-gold counts regardless
# of input. The cell NAMES also differ (prefix-transformed) so set cross-checks
# are independently effective.

# ===========================================================================
# ORACLE (independent matching logic; embedded in check.py too)
# ===========================================================================
import fnmatch


def parse_cell_list(lines):
    """One cell per line; skip blank and #-comment lines."""
    out = []
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        out.append(s)
    return out


def parse_glob_list(lines):
    out = []
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        out.append(s)
    return out


def parse_control(text):
    """Parse .option finesim_mode="a:prohd b:spicehd ..." + .option finesim_ignore="c d ...".
    Strip :suffix from mode entries. Return union set of cell names."""
    import re
    cells = set()
    m = re.search(r'finesim_mode\s*=\s*"([^"]*)"', text)
    if m:
        for tok in m.group(1).split():
            cells.add(tok.split(":")[0])
    m = re.search(r'finesim_ignore\s*=\s*"([^"]*)"', text)
    if m:
        for tok in m.group(1).split():
            cells.add(tok)
    return cells


def control_source_count(text):
    import re
    n = 0
    m = re.search(r'finesim_mode\s*=\s*"([^"]*)"', text)
    if m:
        n += len([t for t in m.group(1).split() if t])
    m = re.search(r'finesim_ignore\s*=\s*"([^"]*)"', text)
    if m:
        n += len([t for t in m.group(1).split() if t])
    return n


def oracle_report(aaa_lines, no_vcap_lines, skip_lines, ignore_lines, control_text):
    cells = parse_cell_list(aaa_lines)
    nv = set(parse_cell_list(no_vcap_lines))
    sc = set(parse_cell_list(skip_lines))
    globs = parse_glob_list(ignore_lines)
    ctrl = parse_control(control_text)
    ctrl_count = control_source_count(control_text)

    def exact(src_set):
        matched = sorted([c for c in cells if c in src_set])
        return {"source_count": len(src_set), "matched_count": len(matched),
                "matched_cells": matched}

    def glob_match():
        matched = sorted([c for c in cells if any(fnmatch.fnmatch(c, g) for g in globs)])
        return {"source_count": len(globs), "matched_count": len(matched),
                "matched_cells": matched}

    def ctrl_match():
        matched = sorted([c for c in cells if c in ctrl])
        return {"source_count": ctrl_count, "matched_count": len(matched),
                "matched_cells": matched}

    return {
        "no_vcap": exact(nv),
        "skip_cell": exact(sc),
        "ignore_cells": glob_match(),
        "control": ctrl_match(),
    }


def _lines(lst):
    return [l + "\n" for l in lst]


def _control_text(mode_entries, ignore_entries):
    mode_str = " ".join(mode_entries)
    ign_str = " ".join(ignore_entries)
    return (f'.option finesim_mode="{mode_str}"\n'
            f'.option finesim_ignore="{ign_str}"\n')


# compute golds
B_GOLD = oracle_report(_lines(AAA_B), _lines(NO_VCAP_B), _lines(SKIP_CELL_B),
                       _lines(IGNORE_CELLS_B), _control_text(CONTROL_MODE_B, CONTROL_IGNORE_B))
AP_GOLD = oracle_report(_lines(AAA_AP), _lines(NO_VCAP_AP), _lines(SKIP_CELL_AP),
                        _lines(IGNORE_CELLS_AP), _control_text(CONTROL_MODE_AP, CONTROL_IGNORE_AP))

print("=== B_GOLD ===")
for k, v in B_GOLD.items():
    print(f"  {k}: src={v['source_count']} matched={v['matched_count']} cells={v['matched_cells']}")
print("=== AP_GOLD ===")
for k, v in AP_GOLD.items():
    print(f"  {k}: src={v['source_count']} matched={v['matched_count']} cells={v['matched_cells']}")

# sanity: B and A' gold differ (token-disjoint)
assert B_GOLD != AP_GOLD, "B and A' gold must differ!"
for src in B_GOLD:
    assert B_GOLD[src]["matched_cells"] != AP_GOLD[src]["matched_cells"], \
        f"{src}: B and A' matched cells must differ (got {B_GOLD[src]['matched_cells']} vs {AP_GOLD[src]['matched_cells']})"

# ===========================================================================
# WRITE ASSETS
# ===========================================================================
os.makedirs(ASSET_DIR, exist_ok=True)
os.makedirs(HIDDEN_DIR, exist_ok=True)
os.makedirs(REF_DIR, exist_ok=True)
os.makedirs(NEG_DIR, exist_ok=True)


def write_lines(path, lst):
    with open(path, "w") as f:
        for l in lst:
            f.write(l + "\n")


# A (visible)
write_lines(os.path.join(ASSET_DIR, "aaa_A.txt"), AAA_A)
write_lines(os.path.join(ASSET_DIR, "no_vcap_A.txt"), NO_VCAP_A)
write_lines(os.path.join(ASSET_DIR, "skip_cell_A.txt"), SKIP_CELL_A)
write_lines(os.path.join(ASSET_DIR, "ignore_cells_A.txt"), IGNORE_CELLS_A)
with open(os.path.join(ASSET_DIR, "control_A.txt"), "w") as f:
    f.write(_control_text(CONTROL_MODE_A, CONTROL_IGNORE_A))

# B (hidden)
write_lines(os.path.join(HIDDEN_DIR, "aaa_B.txt"), AAA_B)
write_lines(os.path.join(HIDDEN_DIR, "no_vcap_B.txt"), NO_VCAP_B)
write_lines(os.path.join(HIDDEN_DIR, "skip_cell_B.txt"), SKIP_CELL_B)
write_lines(os.path.join(HIDDEN_DIR, "ignore_cells_B.txt"), IGNORE_CELLS_B)
with open(os.path.join(HIDDEN_DIR, "control_B.txt"), "w") as f:
    f.write(_control_text(CONTROL_MODE_B, CONTROL_IGNORE_B))

HIDDEN_MANIFEST = {
    "case_id": CASE_ID,
    "purpose": "hidden test input B — not visible to SUT sandbox; check() runs only on B",
    "files": {
        "aaa_B.txt": "cell list (47 cells, one per line)",
        "no_vcap_B.txt": "no_vcap source (40 cells + 5 # comments)",
        "skip_cell_B.txt": "skip_cell source (15 cells)",
        "ignore_cells_B.txt": "ignore_cells globs (7 patterns)",
        "control_B.txt": "control source (.option finesim_mode + finesim_ignore)",
    },
    "note": "B is token-structurally-disjoint from visible A (different cell prefixes); A' (anti-hardcode) is derived from B by full prefix transformation and embedded in check.py.",
}
with open(os.path.join(HIDDEN_DIR, "hidden_manifest.json"), "w") as f:
    json.dump(HIDDEN_MANIFEST, f, indent=2, ensure_ascii=False)

# prompt + task_brief
PROMPT = f"""你是 EDA 设计流自动化助手。用户 caozhang 在做 post-sim SPF (Simulation Preparation Flow) 配置核对：手上有一个电路 cell 名单文件 `aaa`（每行一个 cell 名），需要核对这份名单里的 cell 分别在 4 个 SPF 配置源中是否存在，产出一份详细的逐源 membership 报告。

## 4 个 SPF 配置源（均为纯文本）

1. **no_vcap** — 每行一个 cell 名；`#` 开头的行是注释，不计入源 cell。例：`DqIO`、`WckRcvGutV3V4`。
2. **skip_cell** — 每行一个 cell 名（无注释）。
3. **ignore_cells** — 每行一个 glob 通配模式（fnmatch 语义），如 `dlyrc*`、`Dlybias*`。一个 cell 只要匹配任一 glob 就算命中。
4. **control** — 形如：
   ```
   .option finesim_mode="cellA:prohd cellB:spicehd ..."
   .option finesim_ignore="cellC cellD ..."
   ```
   `finesim_mode` 条目带 `:prohd`/`:spicehd` 后缀，比对时**先去掉 `:` 及后缀**再比；`finesim_ignore` 条目无后缀。control 源的命中 = cell 出现在 (mode 去后缀集合 ∪ ignore 集合) 中，不重复计数。

## 你的任务

写一个 Python 脚本 `check_cells_in_refs.py`，对给定的 cell 名单 + 4 个源文件做交叉比对，产出 JSON 报告。

### CLI 接口（必须严格遵守）

```
python3 check_cells_in_refs.py \
    --cells <aaa_file> \
    --no-vcap <no_vcap_file> \
    --skip-cell <skip_cell_file> \
    --ignore-cells <ignore_cells_file> \
    --control <control_file> \
    -o <output_report.json>
```

### 输出 JSON schema（固定 4 个顶层 key，顺序无关）

```json
{{
  "no_vcap": {{"source_count": <int>, "matched_count": <int>, "matched_cells": [<str>, ...]}},
  "skip_cell": {{"source_count": <int>, "matched_count": <int>, "matched_cells": [<str>, ...]}},
  "ignore_cells": {{"source_count": <int>, "matched_count": <int>, "matched_cells": [<str>, ...]}},
  "control": {{"source_count": <int>, "matched_count": <int>, "matched_cells": [<str>, ...]}}
}}
```

字段含义：
- `source_count`：该源本身的条目数（no_vcap/skip_cell = cell 数；ignore_cells = glob 数；control = finesim_mode 条目数 + finesim_ignore 条目数）。
- `matched_count`：aaa 名单中命中该源的 cell 数。
- `matched_cells`：命中的 cell 名列表（按字典序排序）。

### 规则要点

- `#` 开头的行在 no_vcap 中是注释，不计入 `source_count`，也不参与匹配。
- ignore_cells 用 `fnmatch` 通配匹配（不是子串包含）。
- control 的 `finesim_mode` 条目去掉 `:prohd`/`:spicehd` 等后缀后参与匹配；`finesim_mode` 与 `finesim_ignore` 取并集（同一个 cell 在两个里都出现只算一次进 `source_count` 用各自条目数之和，但匹配集合取并集）。
- 全 0 命中的源也要如实报 `matched_count: 0, matched_cells: []`，不许谎报。
- 脚本必须通用——换个 cell 名单和源文件再跑也正确，不许硬编码任何 cell 名。

### 交付

把 `check_cells_in_refs.py` 打包为 `outputs/submit.zip`（zip 根目录下就是 `check_cells_in_refs.py`，不要嵌套目录）。

附件中给出了示例输入（`aaa_A.txt` / `no_vcap_A.txt` / `skip_cell_A.txt` / `ignore_cells_A.txt` / `control_A.txt`），仅供你理解格式。判分时会用**另一组隐藏输入**跑你的脚本。
"""

with open(os.path.join(ASSET_DIR, "prompt.txt"), "w") as f:
    f.write(PROMPT)

TASK_BRIEF = f"""# Task Brief — {CASE_ID}

**Domain**: analog_context (SPF sim-setup cross-reference; doc-search / cross-reference produce)
**Level**: L1 (pure Python text processing, no EDA binaries)
**Trace source**: caozhang @ hfeg0pkn003, session 1795077131085_w2fwq.messages.json (mc=31)

## Real user intent (from trace)
User caozhang had a cell list file `aaa` (145 cells) and wanted to cross-reference each cell
against 4 SPF simulation-setup config sources (no_vcap / skip_cell / ignore_cells globs /
control.nanospice_promd_spfba_common finesim_mode+finesim_ignore), producing a per-source
membership report (counts + matched cell names). This is a doc-search / cross-check Q&A
typical of analog-sim setup verification.

## Reframe rationale
The trace's real aaa / 4 sources are foundry-bound NFS large files that cannot enter the
sandbox. We synthesize three token-structurally-disjoint mock datasets (A visible, B hidden,
A' anti-hardcode derived from B) that faithfully replicate the real file formats (one cell
per line, `#` comments, fnmatch globs, `.option finesim_mode="...:suffix"` + `.option
finesim_ignore="..."`). The task form (cross-reference produce) is preserved with zero drift
from the real intent.

## Deliverable
`outputs/submit.zip` containing `check_cells_in_refs.py` (CLI as in prompt).

## Hidden test input B
Located in `assets/{CASE_ID}/hidden/` (NOT visible to SUT sandbox). check() runs only on B.

## Anti-hardcode A'
Derived from B by full prefix transformation (ColDec→BitLine, WlDrv→Rdmux, Saoi→Nand2x,
Snand→Nor3x, vrg→preChg, CMos→Tmos, Xpre→CapBuf). Embedded in check.py; SUT invisible.
check() runs the candidate on A' and verifies output == A'-gold (which differs from B-gold
on every source), breaking B-hardcode stubs that print B-gold regardless of input.
"""
with open(os.path.join(ASSET_DIR, "task_brief.md"), "w") as f:
    f.write(TASK_BRIEF)

# ===========================================================================
# REFERENCE SOLUTION
# ===========================================================================
REF_SOL = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reference solution: check_cells_in_refs.py

Cross-reference a cell list against 4 SPF config sources, produce JSON report.
"""
import argparse
import fnmatch
import json
import re
import sys


def read_stripped_lines(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.readlines()


def parse_cell_list(path):
    """One cell per line; skip blank and #-comment lines."""
    cells = []
    for ln in read_stripped_lines(path):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        cells.append(s)
    return cells


def parse_glob_list(path):
    globs = []
    for ln in read_stripped_lines(path):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        globs.append(s)
    return globs


def parse_control(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    mode_cells = set()
    ignore_cells = set()
    m = re.search(r'finesim_mode\\s*=\\s*"([^"]*)"', text)
    if m:
        for tok in m.group(1).split():
            mode_cells.add(tok.split(":")[0])
    m = re.search(r'finesim_ignore\\s*=\\s*"([^"]*)"', text)
    if m:
        for tok in m.group(1).split():
            ignore_cells.add(tok)
    return mode_cells, ignore_cells, text


def control_source_count(text):
    n = 0
    m = re.search(r'finesim_mode\\s*=\\s*"([^"]*)"', text)
    if m:
        n += len([t for t in m.group(1).split() if t])
    m = re.search(r'finesim_ignore\\s*=\\s*"([^"]*)"', text)
    if m:
        n += len([t for t in m.group(1).split() if t])
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    ap.add_argument("--no-vcap", required=True)
    ap.add_argument("--skip-cell", required=True)
    ap.add_argument("--ignore-cells", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    cells = parse_cell_list(args.cells)

    nv = set(parse_cell_list(args.no_vcap))
    sc = set(parse_cell_list(args.skip_cell))
    globs = parse_glob_list(args.ignore_cells)
    mode_cells, ignore_cells_ctrl, ctrl_text = parse_control(args.control)
    ctrl_union = mode_cells | ignore_cells_ctrl
    ctrl_count = control_source_count(ctrl_text)

    def exact(src_set):
        matched = sorted([c for c in cells if c in src_set])
        return {"source_count": len(src_set), "matched_count": len(matched),
                "matched_cells": matched}

    def glob_match():
        matched = sorted([c for c in cells if any(fnmatch.fnmatch(c, g) for g in globs)])
        return {"source_count": len(globs), "matched_count": len(matched),
                "matched_cells": matched}

    def ctrl_match():
        matched = sorted([c for c in cells if c in ctrl_union])
        return {"source_count": ctrl_count, "matched_count": len(matched),
                "matched_cells": matched}

    report = {
        "no_vcap": exact(nv),
        "skip_cell": exact(sc),
        "ignore_cells": glob_match(),
        "control": ctrl_match(),
    }
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
'''
with open(os.path.join(REF_DIR, "check_cells_in_refs_ref.py"), "w") as f:
    f.write(REF_SOL)

# ===========================================================================
# check.py  (k=18)
# ===========================================================================
# Embed B data + A' derivation + independent oracle.
CHECK_PY = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py for EDA-Eval-DesignFlow-SpfCellCrossRefProduce-001.

19 assertions (a-s), each independently failable. k_check = 19 >= 8.

Task: produce check_cells_in_refs.py that cross-references a cell list
against 4 SPF config sources (no_vcap / skip_cell / ignore_cells globs /
control finesim_mode+finesim_ignore) and emits a JSON membership report.

Hidden input B: embedded as B_SPEC data (token-structurally-disjoint from
visible A: A uses RA_XYQ/WCK2Ti/Spnand/Spaoi/dynamic_Latch/SCmos/RAbus;
B uses ColDec/WlDrv/Saoi/Snand/vrg/CMos/Xpre). check() runs only on B.

Anti-hardcode A': derived from B by full prefix transformation
(ColDec->BitLine, WlDrv->Rdmux, Saoi->Nand2x, Snand->Nor3x, vrg->preChg,
CMos->Tmos, Xpre->CapBuf). check() runs candidate on A' and verifies
output == A'-gold (differs from B-gold on every source), breaking
B-hardcode stubs that print B-gold regardless of input.

CLI:
    check.py                       # self-test on reference_submit.zip
    check.py <deliverable> <work>  # grader mode
"""
import fnmatch
import hashlib
import json
import os
import py_compile
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

CASE_ID = "EDA-Eval-DesignFlow-SpfCellCrossRefProduce-001"
HERE = os.path.dirname(os.path.abspath(__file__))

# ===========================================================================
# B SPEC — hidden test input (token-structurally-disjoint from visible A)
# ===========================================================================
B_SPEC = ''' + repr({
    "aaa": AAA_B,
    "no_vcap": NO_VCAP_B,
    "skip_cell": SKIP_CELL_B,
    "ignore_cells": IGNORE_CELLS_B,
    "control_mode": CONTROL_MODE_B,
    "control_ignore": CONTROL_IGNORE_B,
}) + '''

# A' = B transformed by full prefix swap (anti-hardcode)
_AP_PREFIX = {
    "ColDec": "BitLine", "WlDrv": "Rdmux", "Saoi": "Nand2x", "Snand": "Nor3x",
    "vrg": "preChg", "CMos": "Tmos", "Xpre": "CapBuf", "RandFillB": "OrphanFillP",
    "FillerNVB": "FillerNVP", "FillerSCB": "FillerSCP",
    "FillerCMB": "FillerCMP", "FillerCIB": "FillerCIP",
}


def _ap_cell(name):
    for k, v in _AP_PREFIX.items():
        if name.startswith(k):
            return v + name[len(k):]
    return name


# A' aaa = transformed B aaa MINUS 6 matched cells (so A'-gold counts differ
# from B-gold) PLUS 4 new unmatched fillers. See build script _AP_DROP.
_AP_DROP = {"BitLine_BnkA_v1", "BitLine_BnkA_v2", "Rdmux_Main_01",
            "Rdmux_Main_02", "Nand2x22_X2", "Tmos_PreBuf_W1"}


def _ap_spec():
    aaa = [_ap_cell(c) for c in B_SPEC["aaa"] if _ap_cell(c) not in _AP_DROP]
    aaa += ["OrphanFillP_%03d" % i for i in range(101, 105)]
    return {
        "aaa": aaa,
        "no_vcap": [(_ap_cell(c) if not c.startswith("#") else c) for c in B_SPEC["no_vcap"]],
        "skip_cell": [_ap_cell(c) for c in B_SPEC["skip_cell"]],
        "ignore_cells": [_ap_cell(g) for g in B_SPEC["ignore_cells"]],
        "control_mode": [(_ap_cell(c.split(":")[0]) + ":" + c.split(":")[1])
                         for c in B_SPEC["control_mode"]],
        "control_ignore": [_ap_cell(c) for c in B_SPEC["control_ignore"]],
    }


# ===========================================================================
# INDEPENDENT ORACLE (recomputes gold; structurally separate from ref sol)
# ===========================================================================
def _parse_cell_list(lines):
    out = []
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        out.append(s)
    return out


def _parse_control_text(mode_entries, ignore_entries):
    mode_str = " ".join(mode_entries)
    ign_str = " ".join(ignore_entries)
    return ('.option finesim_mode="' + mode_str + '"\\n'
            + '.option finesim_ignore="' + ign_str + '"\\n')


def _oracle(spec):
    """Independent oracle: given a spec dict, compute the gold report."""
    cells = _parse_cell_list(spec["aaa"])
    nv = set(_parse_cell_list(spec["no_vcap"]))
    sc = set(_parse_cell_list(spec["skip_cell"]))
    globs = _parse_cell_list(spec["ignore_cells"])
    ctrl_text = _parse_control_text(spec["control_mode"], spec["control_ignore"])
    # parse control
    mode_set = set()
    m = re.search(r'finesim_mode\\s*=\\s*"([^"]*)"', ctrl_text)
    if m:
        for tok in m.group(1).split():
            mode_set.add(tok.split(":")[0])
    ign_set = set()
    m = re.search(r'finesim_ignore\\s*=\\s*"([^"]*)"', ctrl_text)
    if m:
        for tok in m.group(1).split():
            ign_set.add(tok)
    ctrl_union = mode_set | ign_set
    # source count for control = len(mode entries) + len(ignore entries) (raw)
    ctrl_count = len([t for t in spec["control_mode"] if t]) + \\
                 len([t for t in spec["control_ignore"] if t])

    def exact(src):
        matched = sorted([c for c in cells if c in src])
        return {"source_count": len(src), "matched_count": len(matched),
                "matched_cells": matched}

    def gm():
        matched = sorted([c for c in cells if any(fnmatch.fnmatch(c, g) for g in globs)])
        return {"source_count": len(globs), "matched_count": len(matched),
                "matched_cells": matched}

    def cm():
        matched = sorted([c for c in cells if c in ctrl_union])
        return {"source_count": ctrl_count, "matched_count": len(matched),
                "matched_cells": matched}

    return {"no_vcap": exact(nv), "skip_cell": exact(sc),
            "ignore_cells": gm(), "control": cm()}


B_GOLD = _oracle(B_SPEC)
AP_GOLD = _oracle(_ap_spec())


# ===========================================================================
# helpers
# ===========================================================================
def _write_spec(tmpdir, spec, tag):
    d = os.path.join(tmpdir, tag)
    os.makedirs(d, exist_ok=True)
    paths = {}
    with open(os.path.join(d, "aaa.txt"), "w") as f:
        for c in spec["aaa"]:
            f.write(c + "\\n")
    with open(os.path.join(d, "no_vcap.txt"), "w") as f:
        for c in spec["no_vcap"]:
            f.write(c + "\\n")
    with open(os.path.join(d, "skip_cell.txt"), "w") as f:
        for c in spec["skip_cell"]:
            f.write(c + "\\n")
    with open(os.path.join(d, "ignore_cells.txt"), "w") as f:
        for c in spec["ignore_cells"]:
            f.write(c + "\\n")
    with open(os.path.join(d, "control.txt"), "w") as f:
        f.write(_parse_control_text(spec["control_mode"], spec["control_ignore"]))
    return d


def _run_sut(script_path, spec_dir, out_json):
    """Run candidate check_cells_in_refs.py on the given spec dir."""
    cmd = [sys.executable, script_path,
           "--cells", os.path.join(spec_dir, "aaa.txt"),
           "--no-vcap", os.path.join(spec_dir, "no_vcap.txt"),
           "--skip-cell", os.path.join(spec_dir, "skip_cell.txt"),
           "--ignore-cells", os.path.join(spec_dir, "ignore_cells.txt"),
           "--control", os.path.join(spec_dir, "control.txt"),
           "-o", out_json]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60)


def _extract_script(deliverable, work):
    """Unzip submit.zip into a temp dir, return path to check_cells_in_refs.py."""
    tmp = tempfile.mkdtemp(prefix="chk_")
    if not os.path.isfile(deliverable):
        raise AssertionError(f"[a] deliverable not found: {deliverable}")
    try:
        with zipfile.ZipFile(deliverable) as z:
            names = z.namelist()
            z.extractall(tmp)
    except Exception as e:
        raise AssertionError(f"[a] submit.zip is not a valid zip: {e}")
    # find check_cells_in_refs.py (at root or one level deep)
    cand = os.path.join(tmp, "check_cells_in_refs.py")
    if not os.path.isfile(cand):
        # search one level deep
        for root, dirs, files in os.walk(tmp):
            if "check_cells_in_refs.py" in files:
                cand = os.path.join(root, "check_cells_in_refs.py")
                break
    if not os.path.isfile(cand):
        raise AssertionError("[a] submit.zip does not contain check_cells_in_refs.py")
    return tmp, cand


RESULTS = []


def chk(label, cond, msg):
    RESULTS.append((label, bool(cond), msg))
    if not cond:
        raise AssertionError(f"[{label}] {msg}")


def check(deliverable, workdir=None):
    """Grader entry. Returns True on PASS; raises AssertionError on first FAIL."""
    RESULTS.clear()
    tmp_root = tempfile.mkdtemp(prefix="spfxref_")
    try:
        # (a) zip contains check_cells_in_refs.py + py_compile exit 0
        ext_tmp, script = _extract_script(deliverable, workdir)
        chk("a", True, "zip contains check_cells_in_refs.py")
        pc = subprocess.run([sys.executable, "-m", "py_compile", script],
                            capture_output=True, text=True)
        chk("a", pc.returncode == 0, f"py_compile exit {pc.returncode}: {pc.stderr[:200]}")

        # write B spec
        b_dir = _write_spec(tmp_root, B_SPEC, "B")
        b_out = os.path.join(tmp_root, "B_report.json")

        # (b) candidate runs on B exit 0
        r = _run_sut(script, b_dir, b_out)
        chk("b", r.returncode == 0, f"B run exit {r.returncode} stderr={r.stderr[:200]}")

        # (c) report file exists + valid JSON with non-empty content
        chk("c", os.path.isfile(b_out), "B report.json not produced")
        with open(b_out) as f:
            b_report = json.load(f)
        chk("c", isinstance(b_report, dict) and len(b_report) > 0, "B report empty/invalid")

        # (d) report contains 4 source keys
        need = {"no_vcap", "skip_cell", "ignore_cells", "control"}
        chk("d", need.issubset(set(b_report.keys())),
            f"B report missing keys: {need - set(b_report.keys())}")

        # (e-h) matched counts == B-gold per source
        for src, label in [("no_vcap", "e"), ("skip_cell", "f"),
                           ("ignore_cells", "g"), ("control", "h")]:
            got = b_report.get(src, {}).get("matched_count")
            exp = B_GOLD[src]["matched_count"]
            chk(label, got == exp, f"B {src} matched_count={got} expected {exp}")

        # (i) B matched_cells sets == judge oracle sets (precise, no leak/no miss)
        for src in ["no_vcap", "skip_cell", "ignore_cells", "control"]:
            got = set(b_report.get(src, {}).get("matched_cells", []))
            exp = set(B_GOLD[src]["matched_cells"])
            chk("i", got == exp, f"B {src} matched_cells set mismatch: "
                 f"got {sorted(got)} expected {sorted(exp)}")

        # (j) B no_vcap # comment lines not counted in source_count
        # B_SPEC no_vcap has 5 # comment lines; source_count must equal non-comment line count
        nv_raw = B_SPEC["no_vcap"]
        comment_cnt = sum(1 for l in nv_raw if l.strip().startswith("#"))
        non_comment = len([l for l in nv_raw if l.strip() and not l.strip().startswith("#")])
        got_sc = b_report.get("no_vcap", {}).get("source_count")
        chk("j", got_sc == non_comment,
            f"B no_vcap source_count={got_sc} expected {non_comment} (comments excluded)")
        # also verify judge oracle source_count matches (sanity)
        chk("j", B_GOLD["no_vcap"]["source_count"] == non_comment,
            "judge oracle no_vcap source_count inconsistent with comment exclusion")

        # (k) B control mode/ignore union not double-counted in matched set
        # ensure matched_cells has no duplicates and is subset of union
        ctrl_matched = b_report.get("control", {}).get("matched_cells", [])
        chk("k", len(ctrl_matched) == len(set(ctrl_matched)),
            f"B control matched_cells has duplicates: {ctrl_matched}")
        # source_count == mode_entries + ignore_entries (raw), not union size
        raw_ctrl = len([t for t in B_SPEC["control_mode"] if t]) + \\
                    len([t for t in B_SPEC["control_ignore"] if t])
        got_ctrl_sc = b_report.get("control", {}).get("source_count")
        chk("k", got_ctrl_sc == raw_ctrl,
            f"B control source_count={got_ctrl_sc} expected raw {raw_ctrl}")

        # (l) all-zero sources not falsely reported (B has no all-zero source,
        # but verify no source has matched_count>0 while matched_cells empty, or vice versa)
        for src in ["no_vcap", "skip_cell", "ignore_cells", "control"]:
            mc = b_report.get(src, {}).get("matched_count", -1)
            mcells = b_report.get(src, {}).get("matched_cells", None)
            if mc == 0:
                chk("l", mcells == [],
                    f"B {src} matched_count=0 but matched_cells={mcells} (falsely reported)")
            else:
                chk("l", len(mcells) == mc,
                    f"B {src} matched_count={mc} but len(matched_cells)={len(mcells) if mcells is not None else None}")

        # (m) 3-seed determinism: run B 3 times, md5 of report identical
        import hashlib
        md5s = []
        for seed in range(3):
            seed_out = os.path.join(tmp_root, f"B_seed{seed}.json")
            r2 = _run_sut(script, b_dir, seed_out)
            if r2.returncode != 0:
                chk("m", False, f"B seed{seed} run exit {r2.returncode}")
                break
            with open(seed_out, "rb") as f:
                md5s.append(hashlib.md5(f.read()).hexdigest())
        else:
            chk("m", len(set(md5s)) == 1, f"B 3-seed md5 differ: {md5s}")

        # (n) no __chk pollution in SUT workdir
        if workdir and os.path.isdir(workdir):
            pollution = [e for e in os.listdir(workdir) if e.startswith("__chk")]
            chk("n", len(pollution) == 0, f"workdir polluted with __chk: {pollution}")
        else:
            chk("n", True, "no workdir to check")

        # ===== A'-gold cross-check (o-r, §4.9 anti-hardcode) =====
        ap_spec = _ap_spec()
        ap_dir = _write_spec(tmp_root, ap_spec, "Ap")
        ap_out = os.path.join(tmp_root, "Ap_report.json")

        # (o) candidate runs on hidden A' exit 0 + valid JSON report
        r3 = _run_sut(script, ap_dir, ap_out)
        chk("o", r3.returncode == 0,
            f"A' run exit {r3.returncode} stderr={r3.stderr[:200]}")
        chk("o", os.path.isfile(ap_out), "A' report.json not produced")
        with open(ap_out) as f:
            ap_report = json.load(f)
        chk("o", isinstance(ap_report, dict) and need.issubset(set(ap_report.keys())),
            "A' report invalid/missing keys")

        # (p) A' no_vcap matched_count == A'-gold (core cross-check, breaks B-hardcode stub)
        got = ap_report.get("no_vcap", {}).get("matched_count")
        exp = AP_GOLD["no_vcap"]["matched_count"]
        chk("p", got == exp,
            f"A' no_vcap matched_count={got} expected A'-gold {exp} (B-gold={B_GOLD['no_vcap']['matched_count']}) — B-hardcode stub detected")

        # (q) A' ignore_cells glob matched_count == A'-gold (breaks stub printing B-gold)
        got = ap_report.get("ignore_cells", {}).get("matched_count")
        exp = AP_GOLD["ignore_cells"]["matched_count"]
        chk("q", got == exp,
            f"A' ignore_cells matched_count={got} expected A'-gold {exp} (B-gold={B_GOLD['ignore_cells']['matched_count']}) — breaks glob-not-run stub")

        # (r) A' control matched_count == A'-gold (:suffix strip holds on A')
        got = ap_report.get("control", {}).get("matched_count")
        exp = AP_GOLD["control"]["matched_count"]
        chk("r", got == exp,
            f"A' control matched_count={got} expected A'-gold {exp} (B-gold={B_GOLD['control']['matched_count']}) — :suffix strip must hold on A'")

        # (s) A' matched_cells sets == A'-gold sets for all 4 sources
        # (explicit input-dependence cross-check: names differ from B-gold,
        #  breaks any stub that prints B-gold cell names regardless of input)
        for src in ["no_vcap", "skip_cell", "ignore_cells", "control"]:
            got = set(ap_report.get(src, {}).get("matched_cells", []))
            exp = set(AP_GOLD[src]["matched_cells"])
            b_gold = set(B_GOLD[src]["matched_cells"])
            chk("s", got == exp,
                f"A' {src} matched_cells set mismatch: got {sorted(got)} expected A'-gold {sorted(exp)} (B-gold {sorted(b_gold)}) — input-dependent, not B-hardcoded")
            # confirm A'-gold genuinely differs from B-gold (anti-hardcode sanity)
            chk("s", exp != b_gold,
                f"A' {src} A'-gold == B-gold (anti-hardcode fixtures degenerate): {sorted(exp)}")

        return True
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


def _selftest():
    """Run check on reference_submit.zip (built by build script)."""
    ref_zip = os.path.join(HERE, "reference_submit.zip")
    if not os.path.isfile(ref_zip):
        # build it from ref solution
        ref_script = os.path.join(HERE, "check_cells_in_refs_ref.py")
        with zipfile.ZipFile(ref_zip, "w", zipfile.ZIP_DEFLATED) as z:
            z.write(ref_script, "check_cells_in_refs.py")
    return check(ref_zip, tempfile.mkdtemp(prefix="selftest_"))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        ok = _selftest()
        print(f"SELFTEST: {'PASS' if ok else 'FAIL'}")
        for label, cond, msg in RESULTS:
            print(f"  [{label}] {'OK' if cond else 'FAIL'} {msg[:120]}")
        sys.exit(0 if ok else 1)
    elif len(sys.argv) == 3:
        ok = check(sys.argv[1], sys.argv[2])
        print(f"CHECK: {'PASS' if ok else 'FAIL'}")
        sys.exit(0 if ok else 1)
    else:
        print("usage: check.py [deliverable workdir]")
        sys.exit(2)
'''
with open(os.path.join(REF_DIR, "check.py"), "w") as f:
    f.write(CHECK_PY)

# ===========================================================================
# NEGATIVES
# ===========================================================================
NEG_EMPTY = '''#!/usr/bin/env python3
"""neg_fake_empty: empty script that does nothing."""
import sys
sys.exit(0)
'''
with open(os.path.join(NEG_DIR, "neg_fake_empty.py"), "w") as f:
    f.write(NEG_EMPTY)

NEG_PRINT = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""neg_fake_print_only: print B-gold JSON without reading inputs / computing.

Hardcodes the expected B output. Should FAIL because:
 - it does not actually read B input files (fails if B differs)
 - on A' it still prints B-gold, which != A'-gold
"""
import argparse
import json
import sys

# hardcoded B-gold (will be wrong on A')
FAKE = {
    "no_vcap": {"source_count": 40, "matched_count": ''' + str(B_GOLD["no_vcap"]["matched_count"]) + ''',
                "matched_cells": ''' + repr(B_GOLD["no_vcap"]["matched_cells"]) + '''},
    "skip_cell": {"source_count": 15, "matched_count": ''' + str(B_GOLD["skip_cell"]["matched_count"]) + ''',
                  "matched_cells": ''' + repr(B_GOLD["skip_cell"]["matched_cells"]) + '''},
    "ignore_cells": {"source_count": 7, "matched_count": ''' + str(B_GOLD["ignore_cells"]["matched_count"]) + ''',
                     "matched_cells": ''' + repr(B_GOLD["ignore_cells"]["matched_cells"]) + '''},
    "control": {"source_count": ''' + str(B_GOLD["control"]["source_count"]) + ''', "matched_count": ''' + str(B_GOLD["control"]["matched_count"]) + ''',
                "matched_cells": ''' + repr(B_GOLD["control"]["matched_cells"]) + '''},
}

ap = argparse.ArgumentParser()
ap.add_argument("--cells", required=True)
ap.add_argument("--no-vcap", required=True)
ap.add_argument("--skip-cell", required=True)
ap.add_argument("--ignore-cells", required=True)
ap.add_argument("--control", required=True)
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()
with open(args.output, "w") as f:
    json.dump(FAKE, f, indent=2, sort_keys=True)
print(json.dumps(FAKE, sort_keys=True))
'''
with open(os.path.join(NEG_DIR, "neg_fake_print_only.py"), "w") as f:
    f.write(NEG_PRINT)

NEG_CORE = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""neg_fake_core_deleted: skeleton that reads inputs but deletes the core
matching logic — uses substring-contains instead of fnmatch for globs and
does NOT strip :suffix from control finesim_mode. Should FAIL on glob/suffix
assertions.
"""
import argparse
import json
import re

ap = argparse.ArgumentParser()
ap.add_argument("--cells", required=True)
ap.add_argument("--no-vcap", required=True)
ap.add_argument("--skip-cell", required=True)
ap.add_argument("--ignore-cells", required=True)
ap.add_argument("--control", required=True)
ap.add_argument("-o", "--output", required=True)
args = ap.parse_args()


def read_cells(path):
    out = []
    for ln in open(path):
        s = ln.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out


cells = read_cells(args.cells)
nv = set(read_cells(args.no_vcap))
sc = set(read_cells(args.skip_cell))
globs = read_cells(args.ignore_cells)
ctrl_text = open(args.control).read()

# BUG 1: substring contains instead of fnmatch (core logic deleted)
def glob_match(cells, globs):
    matched = []
    for c in cells:
        for g in globs:
            pat = g.rstrip("*")
            if pat in c:  # WRONG: substring, not fnmatch
                matched.append(c)
                break
    return sorted(matched)

# BUG 2: do NOT strip :suffix from finesim_mode
mode_set = set()
m = re.search(r'finesim_mode\\s*=\\s*"([^"]*)"', ctrl_text)
if m:
    for tok in m.group(1).split():
        mode_set.add(tok)  # WRONG: keeps :suffix
ign_set = set()
m = re.search(r'finesim_ignore\\s*=\\s*"([^"]*)"', ctrl_text)
if m:
    for tok in m.group(1).split():
        ign_set.add(tok)
ctrl_union = mode_set | ign_set

report = {
    "no_vcap": {"source_count": len(nv), "matched_count": sum(1 for c in cells if c in nv),
                "matched_cells": sorted([c for c in cells if c in nv])},
    "skip_cell": {"source_count": len(sc), "matched_count": sum(1 for c in cells if c in sc),
                  "matched_cells": sorted([c for c in cells if c in sc])},
    "ignore_cells": {"source_count": len(globs), "matched_count": len(glob_match(cells, globs)),
                     "matched_cells": glob_match(cells, globs)},
    "control": {"source_count": len(mode_set) + len(ign_set),
                "matched_count": sum(1 for c in cells if c in ctrl_union),
                "matched_cells": sorted([c for c in cells if c in ctrl_union])},
}
with open(args.output, "w") as f:
    json.dump(report, f, indent=2, sort_keys=True)
print(json.dumps(report, sort_keys=True))
'''
with open(os.path.join(NEG_DIR, "neg_fake_core_deleted.py"), "w") as f:
    f.write(NEG_CORE)

# smart §4.9(b) B-hardcode stub: detect input by content hash, print B-gold;
# on unknown input (A') fallback to B-gold.
NEG_HARDCODE_B = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""neg_fake_hardcode_b: smart §4.9(b) B-hardcode stub.

Detects input by md5 of --cells file content; if it matches B's aaa hash,
prints B-gold; otherwise (A') falls back to printing B-gold anyway.
Source carries all the static surface patterns (reads all 5 args, parses
sources, emits 4-key JSON) to pass shallow structural checks, but never
does real matching. Should FAIL A'-gold cross-check (p/q/r).
"""
import argparse
import hashlib
import json
import sys

# pre-baked B-gold (computed offline from B_SPEC)
B_GOLD = ''' + repr(B_GOLD) + '''

# md5 of B's aaa file content (joined with newlines)
B_AAA_MD5 = "''' + hashlib.md5(("\\n".join(AAA_B) + "\\n").encode()).hexdigest() + '''"


def _read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    ap.add_argument("--no-vcap", required=True)
    ap.add_argument("--skip-cell", required=True)
    ap.add_argument("--ignore-cells", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()
    # read inputs to look real (surface pattern)
    _ = (_read_text(args.no_vcap), _read_text(args.skip_cell),
         _read_text(args.ignore_cells), _read_text(args.control))
    cells_text = _read_text(args.cells)
    cells_md5 = hashlib.md5(cells_text.encode("utf-8", errors="replace")).hexdigest()
    # detect B by md5; otherwise fallback to B-gold (the hardcode)
    report = dict(B_GOLD)
    if cells_md5 != B_AAA_MD5:
        # A' or unknown: still print B-gold (the cheating fallback)
        pass
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2, sort_keys=True)
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
'''
with open(os.path.join(NEG_DIR, "neg_fake_hardcode_b.py"), "w") as f:
    f.write(NEG_HARDCODE_B)

# negative_selftest.py
NEG_SELFTEST = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""negative_selftest.py — run all 4 negatives against check.py; all must FAIL."""
import json
import os
import subprocess
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
NEG = os.path.join(HERE, "negative")
CHECK = os.path.join(HERE, "check.py")

NEGATIVES = ["neg_fake_empty.py", "neg_fake_print_only.py",
             "neg_fake_core_deleted.py", "neg_fake_hardcode_b.py"]


def _make_zip(neg_path):
    tmp = tempfile.mkdtemp(prefix="neg_")
    zip_path = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(neg_path, "check_cells_in_refs.py")
    return zip_path


def main():
    results = []
    for neg in NEGATIVES:
        neg_path = os.path.join(NEG, neg)
        zip_path = _make_zip(neg_path)
        r = subprocess.run([sys.executable, CHECK, zip_path, tempfile.mkdtemp()],
                           capture_output=True, text=True, timeout=120)
        passed = (r.returncode == 0)
        results.append((neg, passed, r.stdout.strip()[:200], r.stderr.strip()[:300]))
        print(f"  {neg}: {'PASS (BUG!)' if passed else 'FAIL (correct)'}")
    all_fail = all(not p for _, p, _, _ in results)
    print(f"NEG_RC: {'ALL FAIL' if all_fail else 'BUG: some negative passed'}")
    # distinct failure labels
    return 0 if all_fail else 1


if __name__ == "__main__":
    sys.exit(main())
'''
with open(os.path.join(REF_DIR, "negative_selftest.py"), "w") as f:
    f.write(NEG_SELFTEST)

# ===========================================================================
# SELF-VERIFICATION
# ===========================================================================
print("\n=== BUILD DONE. Running self-verification ===")

# 1. reference solution: build reference_submit.zip
ref_zip = os.path.join(REF_DIR, "reference_submit.zip")
with zipfile.ZipFile(ref_zip, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(REF_DIR, "check_cells_in_refs_ref.py"), "check_cells_in_refs.py")

# 2. run check.py selftest (ref must PASS 18/18)
print("--- ref selftest (expect PASS 18/18) ---")
r = subprocess.run([sys.executable, os.path.join(REF_DIR, "check.py")],
                   capture_output=True, text=True, timeout=180)
print("STDOUT:", r.stdout)
print("STDERR:", r.stderr[:500])
ref_pass = (r.returncode == 0)

# 3. negative selftest (all 4 must FAIL)
print("--- negative selftest (expect ALL FAIL) ---")
r2 = subprocess.run([sys.executable, os.path.join(REF_DIR, "negative_selftest.py")],
                    capture_output=True, text=True, timeout=180)
print("STDOUT:", r2.stdout)
print("STDERR:", r2.stderr[:500])
neg_pass = (r2.returncode == 0)

print(f"\n=== RESULT: ref_pass={ref_pass}  neg_all_fail={neg_pass} ===")
if not (ref_pass and neg_pass):
    print("SELF-VERIFY FAILED")
    sys.exit(1)

# report k_check
print("k_check = 19 (a-s)")
print("B_GOLD matched_counts:", {k: v["matched_count"] for k, v in B_GOLD.items()})
print("AP_GOLD matched_counts:", {k: v["matched_count"] for k, v in AP_GOLD.items()})
print("case_id:", CASE_ID)
