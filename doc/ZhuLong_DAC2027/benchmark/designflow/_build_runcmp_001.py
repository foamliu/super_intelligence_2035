#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build script for EDA-Eval-DesignFlow-RunsetPairCmpGen-001 (shard C, layout_virtuoso, A-faithful).
Real seed: k9nnk (gokuguo @ hfeg0plg53, mc=123, 94 msgs/47 turns, status=completed).
U#0 verbatim: compare two 35HFS.layermap files, report differences, read-only (no deletion).
Gold: assistant wrote difflib+hashlib comparator; session extended to LVS/PEX runset pairs
(both identical and 3-line-diff tran.map) + a missing-file (case-sensitivity) case.
Reframed as generic generator cmp_runset.py <fileA> <fileB> <out_report.json>.
14 conditions a-n. Hidden B/B2/B3 structurally different (3-line diff / missing / line-count diff).
"""
import os, sys, json, zipfile, shutil, subprocess, hashlib, tempfile, io

CASE = "EDA-Eval-DesignFlow-RunsetPairCmpGen-001"
ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
AST = os.path.join(ROOT, "assets", CASE)
REF = os.path.join(ROOT, "reference", CASE)
HID = os.path.join(AST, "hidden")
for d in (AST, REF, HID):
    os.makedirs(d, exist_ok=True)

# ---------------- file content literals ----------------
# A pair: identical synthetic 35HFS.layermap (46 lines)
LAYERMAP_A = """; 35HFS layermap (TV1_FS_Virtuoso)
; PDK layer -> GDS layer:purpose mapping
; generated for runset comparison
; columns: layer_name  gds_layer:gds_purpose
; --- drawing layers ---
AA        1:0
PP        2:0
CT        3:0
PO        4:0
CO        5:0
NW        6:0
SN        7:0
SP        8:0
HV        9:0
M1        10:0
M2        20:0
M3        30:0
M4        40:0
M5        50:0
M6        60:0
V1        11:0
V2        21:0
V3        31:0
V4        41:0
V5        51:0
V6        61:0
OX        100:0
TM        90:0
PA        91:0
MTOP      70:0
MBOT      71:0
RPO       72:0
; --- pin purposes ---
M1PIN    10:1
M2PIN    20:1
M3PIN    30:1
M4PIN    40:1
M5PIN    50:1
M6PIN    60:1
V1PIN    11:1
V2PIN    21:1
V3PIN    31:1
V4PIN    41:1
V5PIN    51:1
V6PIN    61:1
; end of layermap
"""

# B pair: two runset files identical except 3 lines (TITLE / LAYOUT PATH / SOURCE PATH)
RUNSET_B_BASE = [
    "# 35H LVS runset",
    "TITLE S11",
    "LAYOUT PATH \"/proj/lacaa/TV1/lvs.gds\"",
    "LAYOUT PRIMARY \"top\"",
    "LAYOUT SYSTEM GDSII",
    "SOURCE PATH \"/proj/lacaa/TV1/lvs.cdl\"",
    "SOURCE PRIMARY \"top\"",
    "SOURCE SYSTEM SPICE",
    "LVS POWER NAME GROUND",
    "LVS FILTERS OPEN",
    "LVS REPORT \"lvs.rep\"",
    "LVS RECOGNIZE GATES ALL",
    "LVS IGNORE TRAPS YES",
    "LVS BOX YES",
    "LVS RECOGNIZE MULTIPORT YES",
    "// encrypted SVRF block below",
    "#DECRYPT",
    "ENCRYPTED_PAYLOAD_A1B2C3D4E5F6",
    "ENCRYPTED_PAYLOAD_G7H8I9J0K1L2",
    "# end of runset",
]
RUNSET_B_A = "\n".join(RUNSET_B_BASE)
# B file_b: 3 lines changed (line 2 TITLE, line 3 LAYOUT PATH, line 6 SOURCE PATH)
_bmod = list(RUNSET_B_BASE)
_bmod[1] = "TITLE S12"
_bmod[2] = "LAYOUT PATH \"/proj/lacaa/V0/lvs.gds\""
_bmod[5] = "SOURCE PATH \"/proj/lacaa/V0/lvs.cdl\""
RUNSET_B_B = "\n".join(_bmod)
# expected differing lines (1-indexed): 2, 3, 6
B_DIFF_LINES = [2, 3, 6]

# B2: fileA exists, fileB MISSING
RUNSET_B2_A = """# calibre empty subckt FS runset
TITLE EMPTY_SUBCKT
LAYOUT PATH \"/proj/lacaa/TV1/empty.gds\"
SOURCE PATH \"/proj/lacaa/TV1/empty.cdl\"
SOURCE SYSTEM SPICE
LVS REPORT \"empty.rep\"
# end
"""
# fileB_B2 is intentionally NOT created (missing path)

# B3: line-count diff (fileA 12 lines, fileB 15 lines: 3 extra lines inserted after line 7)
RUNSET_B3_A = [
    "# tran.map runset",
    "TITLE TRAN_MAP_V0D1",
    "LAYOUT PATH \"/proj/TV1/tran.map\"",
    "MAP LAYER M1 10 0",
    "MAP LAYER M2 20 0",
    "MAP LAYER M3 30 0",
    "MAP LAYER V1 11 0",
    "MAP LAYER V2 21 0",
    "MAP LAYER V3 31 0",
    "MAP LAYER M4 40 0",
    "MAP LAYER M5 50 0",
    "# end tran.map",
]
RUNSET_B3_A_S = "\n".join(RUNSET_B3_A)
_b3b = list(RUNSET_B3_A)
# insert 3 extra lines after index 7 (line 8: "MAP LAYER V2 21 0")
_b3b[7:7] = [
    "MAP LAYER V4 41 0",
    "MAP LAYER V5 51 0",
    "MAP LAYER V6 61 0",
]
RUNSET_B3_B_S = "\n".join(_b3b)

# ---------------- write asset files ----------------
with open(os.path.join(AST, "fileA_A.layermap"), "w") as f: f.write(LAYERMAP_A)
with open(os.path.join(AST, "fileB_A.layermap"), "w") as f: f.write(LAYERMAP_A)  # identical
with open(os.path.join(HID, "fileA_B.runset"), "w") as f: f.write(RUNSET_B_A)
with open(os.path.join(HID, "fileB_B.runset"), "w") as f: f.write(RUNSET_B_B)
with open(os.path.join(HID, "fileA_B2.runset"), "w") as f: f.write(RUNSET_B2_A)
# fileB_B2.runset intentionally absent (missing)
with open(os.path.join(HID, "fileA_B3.runset"), "w") as f: f.write(RUNSET_B3_A_S)
with open(os.path.join(HID, "fileB_B3.runset"), "w") as f: f.write(RUNSET_B3_B_S)
hidden_manifest = {
    "hidden_inputs": ["fileA_B.runset", "fileB_B.runset", "fileA_B2.runset", "fileA_B3.runset", "fileB_B3.runset"],
    "note": "B = 3-line diff runset pair; B2 = fileB missing (path given, file absent); B3 = line-count diff (fileA 12 lines, fileB 15 lines). Not in SUT sandbox; check() runs candidate on these (written from literals).",
    "expected": {"B": {"verdict": "different", "diff_count": 3, "diff_lines": B_DIFF_LINES},
                 "B2": {"verdict": "error", "missing": "fileB_B2.runset"},
                 "B3": {"verdict": "different", "lines_a": 12, "lines_b": 15}}
}
with open(os.path.join(HID, "hidden_manifest.json"), "w") as f: json.dump(hidden_manifest, f, indent=2, ensure_ascii=False)

PROMPT = """# 任务：版图 runset/layermap 文件对比报告生成器（通用）

用户原始需求（逐字原文，来自真实 cline trace `1794191825241_k9nnk`，user `gokuguo` @ host `hfeg0plg53`，mc=123，94 msgs/47 turns，status=completed）：

> "只阅读一下：/proj/lacaa/TV1_FS_Virtuoso/libs/35HFS/35HFS.layermap和/proj/lacaa/V0_FS_Virtuoso_test/libs/35HFS/35HFS.layermap，比较一下两者的区别，注意不要有任何删除的动作"

真实 assistant 写出 `diff_layermap.py`（用 `difflib.SequenceMatcher` 逐行比对）与 `hash_layermap.py`（用 `hashlib` 算 MD5/SHA1 做字节级校验），对两个 2253 行的 layermap 文件做了"逐行 diff + 多层哈希校验"，结论为完全相同（0 处差异、MD5/SHA1 一致）。该 session 后续又用同样方法对比了 LVS/PEX runset 文件（`.sp`/`.lvs`/`hcell_list`/`tran.map`），既报过"完全相同"，也报过"3 行不同"（tran.map），还遇到过一个"文件名大小写写错导致路径不存在"（`V0D1` vs `V0d1`）的情形。整个过程严格只读，从不修改/删除输入文件。

本任务把它改造成**通用生成器**：写一个 Python 脚本，接收两个文件路径与一个输出报告路径，产出一份结构化 JSON 对比报告（完全相同 / 有差异列出差异行 / 文件缺失），并严格保持只读（不得修改或删除任何输入文件）。

## 交付接口（详见 task_brief.md）
- deliverable = `outputs/submit.zip`，内含且仅含 `cmp_runset.py`
- 命令行：`python3 cmp_runset.py <fileA> <fileB> <out_report.json>`
- check(submit.zip, workdir) 双参判分：在隐藏文件对 B/B2/B3 上运行候选生成器，解析输出 JSON，验证 verdict / 哈希 / diff 行枚举 / 缺失文件处理 / 只读守卫（跨输入守卫，反硬编码）。
"""
with open(os.path.join(AST, "prompt.txt"), "w") as f: f.write(PROMPT)

TASK_BRIEF = """# task_brief.md — EDA-Eval-DesignFlow-RunsetPairCmpGen-001

## 交付物
- `outputs/submit.zip`，内含且仅含一个文件 `cmp_runset.py`（可执行 Python3 脚本）。

## 命令行接口
```
python3 cmp_runset.py <fileA> <fileB> <out_report.json>
```
- `fileA`、`fileB`：待对比的两个文本文件（layermap / runset / .lvs / .sp / .map 等）路径。
- `out_report.json`：输出报告路径，脚本须把对比结果写成一份 JSON 文件到该路径。

## 输出报告 JSON schema
```json
{
  "file_a": "<fileA 路径>",
  "file_b": "<fileB 路径>",
  "verdict": "identical" | "different" | "error",
  "md5_a": "<fileA 的 MD5 hex>", "md5_b": "<fileB 的 MD5 hex>",
  "sha1_a": "<fileA 的 SHA1 hex>", "sha1_b": "<fileB 的 SHA1 hex>",
  "lines_a": <fileA 行数>, "lines_b": <fileB 行数>,
  "diff_count": <差异行数，identical 时为 0>,
  "diffs": [ {"line_a": <1-indexed 或 null>, "line_b": <1-indexed 或 null>,
              "content_a": "<该行内容 或 null>", "content_b": "<该行内容 或 null>"} ],
  "missing": "<缺失文件路径，仅 verdict=error 时存在>"
}
```

## 行为规约
1. **读两个文件**（文本模式，utf-8，errors='replace'）。
2. **算哈希**：对每个文件的原始字节算 MD5 与 SHA1（hexdigest）。
3. **判定 verdict**：
   - 两文件 MD5 相等 → `"identical"`，`diff_count=0`，`diffs=[]`。
   - 两文件 MD5 不等 → `"different"`，用 `difflib`（如 `SequenceMatcher.get_opcodes`）逐行比对，把每一处 `replace`/`delete`/`insert` 的差异行枚举进 `diffs`（每条带 1-indexed 行号与对应行内容），`diff_count = len(diffs)`。
   - 任一文件路径不存在 → `"error"`，`missing` 填缺失的那一个路径；存在的那一个仍照常算哈希/行数，缺失的那个对应字段为 `null`；`diff_count=0`，`diffs=[]`。**不得抛异常崩溃**，须正常退出码 0 并写出 JSON。
4. **只读守卫**：脚本绝不以写模式打开 `fileA`/`fileB`，绝不修改或删除任何输入文件。
5. **退出码**：成功写出报告（含 `verdict=error` 的缺失情形）退出码 0；参数错误或内部异常可非 0。
6. 报告须为合法 JSON，包含上述字段（`diffs`/`missing` 按 verdict 取舍）。

## 可见样例（A 对）
附件 `fileA_A.layermap` 与 `fileB_A.layermap` 是一对**完全相同**的 35HFS layermap，供你理解输入格式与"identical"情形的期望输出。

## 隐藏判分（B/B2/B3，结构不同，不在 SUT 沙盒内）
- **B**：一对 runset 文件，有 **3 行**内容不同（行号已知）→ 期望 `verdict=different`、`diff_count=3`、`diffs` 精确枚举这 3 行（含行号与内容）。
- **B2**：`fileA` 存在、`fileB` 路径指向一个**不存在**的文件 → 期望 `verdict=error`、`missing` 指向缺失文件、退出码 0（不崩溃）。
- **B3**：`fileA` 12 行、`fileB` 15 行（中间插入 3 行）→ 期望 `verdict=different`、`lines_a=12`、`lines_b=15`、`diff_count>0`。

判分器还会在所有运行前后校验输入文件哈希不变（只读守卫，反"修改/删除输入"的假解）。
"""
with open(os.path.join(AST, "task_brief.md"), "w") as f: f.write(TASK_BRIEF)

# ---------------- reference solution ----------------
REF_SOL = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reference solution: cmp_runset.py <fileA> <fileB> <out_report.json>"""
import sys, os, json, hashlib, difflib

def _hash(path, algo):
    h = hashlib.new(algo)
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def _lines(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.read().splitlines()

def main():
    if len(sys.argv) != 4:
        print("usage: cmp_runset.py <fileA> <fileB> <out_report.json>", file=sys.stderr)
        sys.exit(2)
    fileA, fileB, out = sys.argv[1], sys.argv[2], sys.argv[3]
    rep = {"file_a": fileA, "file_b": fileB}
    ma, mb = os.path.exists(fileA), os.path.exists(fileB)
    rep["md5_a"] = _hash(fileA, 'md5') if ma else None
    rep["md5_b"] = _hash(fileB, 'md5') if mb else None
    rep["sha1_a"] = _hash(fileA, 'sha1') if ma else None
    rep["sha1_b"] = _hash(fileB, 'sha1') if mb else None
    rep["lines_a"] = len(_lines(fileA)) if ma else None
    rep["lines_b"] = len(_lines(fileB)) if mb else None
    if not (ma and mb):
        rep["verdict"] = "error"
        rep["missing"] = fileB if not mb else fileA
        rep["diff_count"] = 0
        rep["diffs"] = []
        json.dump(rep, open(out, 'w'), ensure_ascii=False, indent=2)
        sys.exit(0)
    if rep["md5_a"] == rep["md5_b"]:
        rep["verdict"] = "identical"
        rep["diff_count"] = 0
        rep["diffs"] = []
    else:
        rep["verdict"] = "different"
        la, lb = _lines(fileA), _lines(fileB)
        diffs = []
        sm = difflib.SequenceMatcher(None, la, lb, autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                continue
            if tag == 'replace':
                n = max(i2 - i1, j2 - j1)
                for k in range(n):
                    ia = i1 + k if k < (i2 - i1) else None
                    jb = j1 + k if k < (j2 - j1) else None
                    diffs.append({"line_a": ia + 1 if ia is not None else None,
                                  "line_b": jb + 1 if jb is not None else None,
                                  "content_a": la[ia] if ia is not None else None,
                                  "content_b": lb[jb] if jb is not None else None})
            elif tag == 'delete':
                for k in range(i1, i2):
                    diffs.append({"line_a": k + 1, "line_b": None, "content_a": la[k], "content_b": None})
            elif tag == 'insert':
                for k in range(j1, j2):
                    diffs.append({"line_a": None, "line_b": k + 1, "content_a": None, "content_b": lb[k]})
        rep["diff_count"] = len(diffs)
        rep["diffs"] = diffs
    json.dump(rep, open(out, 'w'), ensure_ascii=False, indent=2)
    sys.exit(0)

if __name__ == '__main__':
    main()
'''
with open(os.path.join(REF, "cmp_runset_ref.py"), "w") as f: f.write(REF_SOL)

# ---------------- check.py (self-contained, writes A/B/B2/B3 from literals) ----------------
CHECK_PY = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py for EDA-Eval-DesignFlow-RunsetPairCmpGen-001
Verifies candidate cmp_runset.py on hidden pairs B/B2/B3 (+ visible A).
14 conditions a-n, each independently failable.
Usage: check.py <deliverable> <workdir>
"""
import sys, os, json, zipfile, subprocess, tempfile, re, shutil, hashlib

LAYERMAP_A = ''' + repr(LAYERMAP_A) + r'''

RUNSET_B_A = ''' + repr(RUNSET_B_A) + r'''
RUNSET_B_B = ''' + repr(RUNSET_B_B) + r'''
B_DIFF_LINES = ''' + repr(B_DIFF_LINES) + r'''

RUNSET_B2_A = ''' + repr(RUNSET_B2_A) + r'''

RUNSET_B3_A = ''' + repr(RUNSET_B3_A_S) + r'''
RUNSET_B3_B = ''' + repr(RUNSET_B3_B_S) + r'''

def _unzip(deliverable, workdir):
    if os.path.isdir(deliverable):
        return deliverable
    d = os.path.join(workdir, "__cand_extract")
    if os.path.exists(d): shutil.rmtree(d)
    os.makedirs(d, exist_ok=True)
    with zipfile.ZipFile(deliverable) as z:
        z.extractall(d)
    return d

def _find_cmp(d):
    for root, _, files in os.walk(d):
        for fn in files:
            if fn == "cmp_runset.py":
                return os.path.join(root, fn)
    return None

def _md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(8192), b''):
            h.update(c)
    return h.hexdigest()

def _run(cmp, fa, fb, outdir):
    outj = os.path.join(outdir, "out_%s.json" % hashlib.md5((fa+fb).encode()).hexdigest()[:8])
    if os.path.exists(outj): os.remove(outj)
    try:
        p = subprocess.run([sys.executable, cmp, fa, fb, outj],
                           capture_output=True, text=True, timeout=30)
        return p.returncode, outj, p.stdout, p.stderr
    except Exception as e:
        return -999, outj, "", str(e)

def _loadj(p):
    try:
        return json.load(open(p)), True
    except Exception:
        return None, False

def check(deliverable, workdir):
    CONDITIONS = []
    tmp = tempfile.mkdtemp(prefix="chk_runcmp_", dir=workdir if os.path.exists(workdir) else None)
    try:
        # write input files from literals (self-contained; hidden data NOT in SUT sandbox)
        faA = os.path.join(tmp, "fileA_A.layermap"); open(faA, "w").write(LAYERMAP_A)
        fbA = os.path.join(tmp, "fileB_A.layermap"); open(fbA, "w").write(LAYERMAP_A)
        faB = os.path.join(tmp, "fileA_B.runset"); open(faB, "w").write(RUNSET_B_A)
        fbB = os.path.join(tmp, "fileB_B.runset"); open(fbB, "w").write(RUNSET_B_B)
        faB2 = os.path.join(tmp, "fileA_B2.runset"); open(faB2, "w").write(RUNSET_B2_A)
        fbB2 = os.path.join(tmp, "fileB_B2.runset")  # intentionally NOT created (missing)
        faB3 = os.path.join(tmp, "fileA_B3.runset"); open(faB3, "w").write(RUNSET_B3_A)
        fbB3 = os.path.join(tmp, "fileB_B3.runset"); open(fbB3, "w").write(RUNSET_B3_B)

        # record input hashes BEFORE runs (read-only guard)
        inputs_before = {}
        for p in (faA, fbA, faB, fbB, faB2, faB3, fbB3):
            if os.path.exists(p):
                inputs_before[p] = _md5(p)

        d = _unzip(deliverable, tmp)
        py_files = [fn for _, _, fs in os.walk(d) for fn in fs if fn.endswith(".py")]
        CONDITIONS.append(("a", "submit contains exactly one cmp_runset.py",
                           len(py_files) == 1 and py_files[0] == "cmp_runset.py"))
        cmp = _find_cmp(d)
        if cmp is None:
            for lbl, desc in [("b",""),("c",""),("d",""),("e",""),("f",""),("g",""),("h",""),("i",""),("j",""),("k",""),("l",""),("m",""),("n","")]:
                CONDITIONS.append((lbl, desc, False))
            return _finalize(CONDITIONS)
        try:
            subprocess.run([sys.executable, "-m", "py_compile", cmp], check=True, capture_output=True, timeout=30)
            compile_ok = True
        except Exception:
            compile_ok = False
        CONDITIONS.append(("b", "cmp_runset.py compiles", compile_ok))

        rcA, ojA, _, _ = _run(cmp, faA, fbA, tmp)
        rcB, ojB, _, _ = _run(cmp, faB, fbB, tmp)
        rcB2, ojB2, _, _ = _run(cmp, faB2, fbB2, tmp)
        rcB3, ojB3, _, _ = _run(cmp, faB3, fbB3, tmp)
        jA, okA = _loadj(ojA)
        jB, okB = _loadj(ojB)
        jB2, okB2 = _loadj(ojB2)
        jB3, okB3 = _loadj(ojB3)

        # (c) A run exits 0 and out_report.json is valid JSON
        CONDITIONS.append(("c", "A run exits 0 and out_report.json valid JSON", rcA == 0 and okA))
        # (d) A verdict == identical
        CONDITIONS.append(("d", "A verdict == identical", okA and jA.get("verdict") == "identical"))
        # (e) A md5_a == md5_b (both present non-null)
        CONDITIONS.append(("e", "A md5_a == md5_b (both non-null)",
                           okA and jA.get("md5_a") and jA.get("md5_b") and jA.get("md5_a") == jA.get("md5_b")))
        # (f) A diff_count == 0 and diffs empty
        CONDITIONS.append(("f", "A diff_count == 0 and diffs empty",
                           okA and jA.get("diff_count") == 0 and (not jA.get("diffs"))))
        # (g) A lines_a == lines_b == 46 (correct line count)
        CONDITIONS.append(("g", "A lines_a == lines_b == 46 (correct count)",
                           okA and jA.get("lines_a") == 46 and jA.get("lines_b") == 46))
        # (h) B verdict == different
        CONDITIONS.append(("h", "B verdict == different", okB and jB.get("verdict") == "different"))
        # (i) B diff_count == 3 (exact count)
        CONDITIONS.append(("i", "B diff_count == 3", okB and jB.get("diff_count") == 3))
        # (j) B diffs enumerate the 3 expected differing lines (content match, anti-hardcode)
        j_ok = False
        if okB:
            diffs = jB.get("diffs") or []
            # expected differing line contents (from literals)
            la = RUNSET_B_A.splitlines()
            lb = RUNSET_B_B.splitlines()
            exp = []
            for ln in B_DIFF_LINES:
                exp.append((ln, la[ln-1], lb[ln-1]))
            got = set()
            for dd in diffs:
                ca = dd.get("content_a"); cb = dd.get("content_b")
                la_ = dd.get("line_a"); lb_ = dd.get("line_b")
                got.add((la_, ca, lb_, cb))
            j_ok = all((ln, la[ln-1], ln, lb[ln-1]) in got for ln in B_DIFF_LINES)
        CONDITIONS.append(("j", "B diffs enumerate the 3 expected differing lines (content match)", j_ok))
        # (k) B2 verdict == error AND missing present
        CONDITIONS.append(("k", "B2 verdict == error and missing field present",
                           okB2 and jB2.get("verdict") == "error" and jB2.get("missing")))
        # (l) B2 run exits 0 (graceful, not crash)
        CONDITIONS.append(("l", "B2 run exits 0 (graceful missing-file handling)", rcB2 == 0))
        # (m) B3 verdict == different AND lines_a != lines_b (line-count handling)
        CONDITIONS.append(("m", "B3 verdict == different and lines_a(12) != lines_b(15)",
                           okB3 and jB3.get("verdict") == "different" and jB3.get("lines_a") == 12 and jB3.get("lines_b") == 15))
        # (n) READ-ONLY guard: all input files unchanged after all runs
        ro_ok = True
        for p, h0 in inputs_before.items():
            if os.path.exists(p):
                if _md5(p) != h0:
                    ro_ok = False; break
            else:
                ro_ok = False; break
        CONDITIONS.append(("n", "read-only guard: all input files unchanged after runs", ro_ok))
        return _finalize(CONDITIONS)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def _finalize(CONDITIONS):
    failed = [(l, d) for (l, d, ok) in CONDITIONS if not ok]
    report = "RunsetPairCmpGen: %d/%d conditions PASS" % (len(CONDITIONS) - len(failed), len(CONDITIONS))
    if failed:
        report += "\nFAILED: " + ", ".join("%s(%s)" % (l, d) for l, d in failed)
        raise AssertionError(report)
    return report

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: check.py <deliverable> <workdir>"); sys.exit(2)
    try:
        print(check(sys.argv[1], sys.argv[2]))
    except AssertionError as e:
        print("FAIL:", e); sys.exit(1)
'''
with open(os.path.join(REF, "check.py"), "w") as f: f.write(CHECK_PY)

# ---------------- negatives ----------------
NEG_DIR = os.path.join(REF, "negative"); os.makedirs(NEG_DIR, exist_ok=True)
negatives = {
"naive_hardcode.py": r'''#!/usr/bin/env python3
# always outputs identical regardless of input
import sys, os, json
fileA, fileB, out = sys.argv[1], sys.argv[2], sys.argv[3]
rep = {"file_a":fileA,"file_b":fileB,"verdict":"identical","md5_a":"x","md5_b":"x",
       "sha1_a":"y","sha1_b":"y","lines_a":0,"lines_b":0,"diff_count":0,"diffs":[]}
json.dump(rep, open(out,'w'))
''',
"print_only.py": r'''#!/usr/bin/env python3
# prints report to stdout, never writes out_report.json
import sys, os, json, hashlib
fileA, fileB, out = sys.argv[1], sys.argv[2], sys.argv[3]
print(json.dumps({"verdict":"identical","diff_count":0}))
''',
"deleted_core.py": r'''#!/usr/bin/env python3
# does diff but skips hash computation (no md5/sha1)
import sys, os, json, difflib
fileA, fileB, out = sys.argv[1], sys.argv[2], sys.argv[3]
la = open(fileA).read().splitlines() if os.path.exists(fileA) else []
lb = open(fileB).read().splitlines() if os.path.exists(fileB) else []
rep = {"file_a":fileA,"file_b":fileB,"verdict":"different" if la!=lb else "identical",
       "md5_a":None,"md5_b":None,"sha1_a":None,"sha1_b":None,
       "lines_a":len(la),"lines_b":len(lb),"diff_count":0,"diffs":[]}
json.dump(rep, open(out,'w'))
''',
"modify_input.py": r'''#!/usr/bin/env python3
# violates read-only: appends to input fileA
import sys, os, json
fileA, fileB, out = sys.argv[1], sys.argv[2], sys.argv[3]
with open(fileA,'a') as f: f.write("\n# tampered\n")
rep = {"file_a":fileA,"file_b":fileB,"verdict":"identical","md5_a":"x","md5_b":"x",
       "sha1_a":"y","sha1_b":"y","lines_a":1,"lines_b":1,"diff_count":0,"diffs":[]}
json.dump(rep, open(out,'w'))
''',
"crash_on_missing.py": r'''#!/usr/bin/env python3
# crashes (raises) on missing file instead of reporting error
import sys, os, json
fileA, fileB, out = sys.argv[1], sys.argv[2], sys.argv[3]
a = open(fileA).read()
b = open(fileB).read()  # raises FileNotFoundError -> non-zero exit
rep = {"verdict":"identical"}
json.dump(rep, open(out,'w'))
''',
"wrong_diff_count.py": r'''#!/usr/bin/env python3
# reports diff_count but miscounts (counts ALL lines, not just diffs)
import sys, os, json, difflib
fileA, fileB, out = sys.argv[1], sys.argv[2], sys.argv[3]
la = open(fileA).read().splitlines()
lb = open(fileB).read().splitlines()
rep = {"file_a":fileA,"file_b":fileB,"verdict":"different" if la!=lb else "identical",
       "diff_count": len(la),  # WRONG: counts all lines, not diff lines
       "diffs": [], "lines_a":len(la),"lines_b":len(lb)}
json.dump(rep, open(out,'w'))
''',
}
for fn, content in negatives.items():
    with open(os.path.join(NEG_DIR, fn), "w") as f: f.write(content)

# §4.9 three fakes (also must FAIL)
fakes = {
"empty_shell.py": "# empty no-op\nimport sys\nsys.exit(0)\n",
"print_expected.py": r'''#!/usr/bin/env python3
# prints the expected answer for B but doesn't write out_report.json
import sys
print('{"verdict":"different","diff_count":3}')
''',
"name_only.py": r'''#!/usr/bin/env python3
# only checks if filenames are equal (no real content comparison)
import sys, os, json
fileA, fileB, out = sys.argv[1], sys.argv[2], sys.argv[3]
rep = {"verdict":"identical" if os.path.basename(fileA)==os.path.basename(fileB) else "different",
       "diff_count":0,"diffs":[]}
json.dump(rep, open(out,'w'))
''',
}
for fn, content in fakes.items():
    with open(os.path.join(NEG_DIR, fn), "w") as f: f.write(content)

# ---------------- negative_selftest.py ----------------
NEG_SELFTEST = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run check.py against reference (must PASS) and all negatives/fakes (must FAIL)."""
import os, sys, json, zipfile, subprocess, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "check.py")
REF_PY = os.path.join(HERE, "cmp_runset_ref.py")
NEG = os.path.join(HERE, "negative")

def make_zip(py_path, tmp):
    z = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(z, 'w') as zf:
        zf.write(py_path, arcname="cmp_runset.py")
    return z

def run_check(z):
    wd = tempfile.mkdtemp(prefix="negst_")
    try:
        p = subprocess.run([sys.executable, CHECK, z, wd], capture_output=True, text=True, timeout=60)
        return p.returncode, p.stdout, p.stderr
    finally:
        shutil.rmtree(wd, ignore_errors=True)

def main():
    tmp = tempfile.mkdtemp(prefix="negst_zip_")
    results = []
    try:
        # reference must PASS
        z = make_zip(REF_PY, tmp)
        rc, so, se = run_check(z)
        results.append(("REFERENCE", "PASS" if rc == 0 else "FAIL", rc, so.strip()[:120]))
        # each negative/fake must FAIL
        for fn in sorted(os.listdir(NEG)):
            if not fn.endswith(".py"): continue
            z = make_zip(os.path.join(NEG, fn), tmp)
            rc, so, se = run_check(z)
            results.append((fn, "FAIL" if rc != 0 else "UNEXPECTED-PASS", rc, so.strip()[:120]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    allok = True
    for name, status, rc, msg in results:
        mark = "OK" if ((name == "REFERENCE" and status == "PASS") or (name != "REFERENCE" and status == "FAIL")) else "BAD"
        if mark == "BAD": allok = False
        print("[%s] %-22s %-16s rc=%d  %s" % (mark, name, status, rc, msg))
    print("\nNEGATIVE_SELFTEST:", "ALL OK" if allok else "HAS BAD")
    sys.exit(0 if allok else 1)

if __name__ == '__main__':
    main()
'''
with open(os.path.join(REF, "negative_selftest.py"), "w") as f: f.write(NEG_SELFTEST)

# ---------------- build reference_submit.zip ----------------
zpath = os.path.join(REF, "reference_submit.zip")
if os.path.exists(zpath): os.remove(zpath)
with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(os.path.join(REF, "cmp_runset_ref.py"), arcname="cmp_runset.py")

print("Build complete. Files written to:")
print("  assets:", AST)
print("  reference:", REF)
print("  reference_submit.zip:", zpath, os.path.getsize(zpath), "bytes")
