#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build + self-verify + append EDA-Eval-DesignFlow-DcDontuseGen-001 (shard A).

Case: Liberty .lib + cell allowlist -> DC dont_use TCL generator.
Verb: lib-allowlist-to-dc-dontuse-script (digital, B-grade synthesized,
A-grade faithful task statement verbatim from trace tzth7 USER#2).
Real lib (/proj/lacaa/.../DBCP51H180L6W25T5_BASE_LVT_...ccs.lib) is
permission-denied -> synthesized faithful Liberty bundles A + hidden B.
"""
import os, sys, json, re, zipfile, shutil, subprocess, tempfile, py_compile

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-DcDontuseGen-001"
A_DIR = os.path.join(BENCH, "assets", CID)
HID = os.path.join(A_DIR, "hidden")
REF = os.path.join(BENCH, "reference", CID)
NEG = os.path.join(REF, "negative")
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")

A_LIB = os.path.join(A_DIR, "lib_A.lib")
A_ALLOW = os.path.join(A_DIR, "allow_A.txt")
B_LIB = os.path.join(HID, "lib_B.lib")
B_ALLOW = os.path.join(HID, "allow_B.txt")
for d in (A_DIR, HID, REF, NEG):
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------- bundles
LIB_NAME_A = "DBCP51H180L6W25T5_BASE_LVT_tt_typical_v0p75_85c_ccs"
LIB_NAME_B = "XXYN40H120L4W20T4_BASE_SVT_ff_typical_v0p55_125c_ccs"

ALLOW_A = ["xorX1","nandx1","nandx2","norx1","norx2","invx1","invx2","invx16",
           "bufx1","bufx3","bufx8","bufx128","tiehx1","tielx1","icgx1","dffx1",
           "latx1","muxx1","delayx1"]
DISAL_A = ["xorX2","xorX3","nandx3","nandx4","norx3","norx4","invx3","invx4",
           "bufx2","bufx4","icgx2","dffx2","dffx4","latx2","muxx2","muxx4",
           "delayx2","andx1","andx2","orx1","orx2","aoi21x1","oai21x1",
           "fillx1","antennax1","tiezx1","boundaryNcorner"]

ALLOW_B = ["xorX2","nandx3","invx3","bufx4","tiehx1","tielx1","icgx2","dffx2",
           "muxx2","delayx2","andx1","orx1","aoi21x1","oai21x1","muxx4"]
DISAL_B = ["xorX1","xorX3","nandx1","nandx2","invx1","invx2","invx16","bufx1",
           "bufx8","icgx1","dffx1","dffx4","latx1","muxx1","delayx1","andx2",
           "orx2","aoi22x1","oai22x1","fillx2","antennax2","tiezx2",
           "boundaryPcorner"]

def liberty(lib_name, allowed, disallowed):
    """Synthesize a minimal but valid Liberty file. Cell names = UPPER(name).
    Allowed and disallowed cells interleave; pins are minimal."""
    cells = [(n, True) for n in allowed] + [(n, False) for n in disallowed]
    out = []
    out.append('library (%s) {' % lib_name)
    out.append('  delay_model : table_lookup;')
    out.append('  time_unit : "1ns";')
    out.append('  voltage_unit : "1V";')
    out.append('  current_unit : "1mA";')
    out.append('  capacitance_unit : "1pf";')
    out.append('  noise_margin_low("0.4 * VDD");')
    out.append('  noise_margin_high("0.4 * VDD");')
    # a couple templates so the lib looks real
    out.append('  lu_table_template(TRANS) {')
    out.append('    variable_1 : input_net_transition;')
    out.append('    index_1("0.01 0.05 0.1 0.2 0.4");')
    out.append('  }')
    for name, _allowed in cells:
        u = name.upper()
        out.append('  cell (%s) {' % u)
        out.append('    area : %.1f;' % (2.0 + (len(name) % 5)))
        out.append('    pg_pin(VDD) { voltage_name : VDD; pg_type : primary_power; }')
        out.append('    pg_pin(VSS) { voltage_name : VSS; pg_type : primary_ground; }')
        if u.startswith("XOR"):
            out.append('    pin(Z) { direction : output; function : "(A^B)"; }')
            out.append('    pin(A) { direction : input; }')
            out.append('    pin(B) { direction : input; }')
        elif u.startswith("NAND"):
            out.append('    pin(Z) { direction : output; function : "!(A&B)"; }')
            out.append('    pin(A) { direction : input; }')
            out.append('    pin(B) { direction : input; }')
        elif u.startswith("NOR"):
            out.append('    pin(Z) { direction : output; function : "!(A|B)"; }')
            out.append('    pin(A) { direction : input; }')
            out.append('    pin(B) { direction : input; }')
        elif u.startswith("INV"):
            out.append('    pin(Z) { direction : output; function : "!(A)"; }')
            out.append('    pin(A) { direction : input; }')
        elif u.startswith("BUF") or u.startswith("FILL") or u.startswith("ANTENNA"):
            out.append('    pin(Z) { direction : output; function : "(A)"; }')
            out.append('    pin(A) { direction : input; }')
        elif u.startswith("TIEH"):
            out.append('    pin(Z) { direction : output; function : "1\'b1"; }')
        elif u.startswith("TIEL"):
            out.append('    pin(ZN) { direction : output; function : "1\'b0"; }')
        elif u.startswith("TIEZ"):
            out.append('    pin(Z) { direction : output; function : "1\'bz"; }')
        elif u.startswith("DFF"):
            out.append('    pin(CK) { direction : input; clock : true; }')
            out.append('    pin(D) { direction : input; }')
            out.append('    pin(Q) { direction : output; function : "D"; }')
        elif u.startswith("LAT"):
            out.append('    pin(EN) { direction : input; }')
            out.append('    pin(D) { direction : input; }')
            out.append('    pin(Q) { direction : output; }')
        elif u.startswith("ICG"):
            out.append('    pin(CK) { direction : input; clock : true; }')
            out.append('    pin(EN) { direction : input; }')
            out.append('    pin(CKG) { direction : output; clock : true; }')
        elif u.startswith("MUX"):
            out.append('    pin(S) { direction : input; }')
            out.append('    pin(A) { direction : input; }')
            out.append('    pin(B) { direction : input; }')
            out.append('    pin(Z) { direction : output; function : "(S?B:A)"; }')
        elif u.startswith("DELAY"):
            out.append('    pin(A) { direction : input; }')
            out.append('    pin(Z) { direction : output; function : "(A)"; }')
        elif u.startswith("AND"):
            out.append('    pin(Z) { direction : output; function : "(A&B)"; }')
            out.append('    pin(A) { direction : input; }')
            out.append('    pin(B) { direction : input; }')
        elif u.startswith("OR"):
            out.append('    pin(Z) { direction : output; function : "(A|B)"; }')
            out.append('    pin(A) { direction : input; }')
            out.append('    pin(B) { direction : input; }')
        elif u.startswith("AOI"):
            out.append('    pin(ZN) { direction : output; function : "!((A&B)|C)"; }')
            out.append('    pin(A) { direction : input; }')
            out.append('    pin(B) { direction : input; }')
            out.append('    pin(C) { direction : input; }')
        elif u.startswith("OAI"):
            out.append('    pin(ZN) { direction : output; function : "!((A|B)&C)"; }')
            out.append('    pin(A) { direction : input; }')
            out.append('    pin(B) { direction : input; }')
            out.append('    pin(C) { direction : input; }')
        elif u.startswith("BOUNDARY"):
            out.append('    pin(TIE) { direction : output; function : "1\'b1"; }')
        else:
            out.append('    pin(Z) { direction : output; }')
            out.append('    pin(A) { direction : input; }')
        out.append('  }')
    out.append('}')
    return "\n".join(out) + "\n"

write_file = lambda p, c: open(p, "w", encoding="utf-8").write(c)

# A bundle
write_file(os.path.join(A_DIR, "lib_A.lib"), liberty(LIB_NAME_A, ALLOW_A, DISAL_A))
write_file(os.path.join(A_DIR, "allow_A.txt"), "\n".join(ALLOW_A) + "\n")
# B (hidden) bundle
write_file(os.path.join(HID, "lib_B.lib"), liberty(LIB_NAME_B, ALLOW_B, DISAL_B))
write_file(os.path.join(HID, "allow_B.txt"), "\n".join(ALLOW_B) + "\n")
write_file(os.path.join(HID, "hidden_manifest.json"), json.dumps({
    "B_lib": "lib_B.lib",
    "B_allow": "allow_B.txt",
    "cross_input_guard": ("different LIB_NAME (XXYN...SVT vs DBCP...LVT), "
                          "different allowlist (15 vs 19 members, different "
                          "cells), different disallowed set; a candidate that "
                          "hardcodes A's LIB_NAME or A's enable list will fail "
                          "on B (k/l/m)."),
}, ensure_ascii=False, indent=2))

# ---------------------------------------------------------------- prompt + brief
PROMPT = """从 Liberty(.lib) 的允许单元白名单生成 DC `dont_use` 策略脚本 (digital, DC synthesis 单元禁用策略)。

用户原话（逐字，A 档 faithful，trace 1793324309763_tzth7 / e0045144 @ hfeg0pkn004，用户轮 #2）：
「这个lib : `/proj/lacaa/TV1_digital/workdir/Data_Transfer/to_HF/e0037828_20261025/LIB/DBCP51H180L6W25T5_BASE_LVT_tt_typical_v0p75_85c_ccs.lib` 只允许用 `xorX1,nandx1,nandx2,norx1,norx2,invx1,invx2,invx16,bufx1,bufx3,bufx8,bufx128,tiehx1,tielx1,icgx1,dffx1,latx1,muxx1,delayx1` 这些类型cell，帮我产生个DC脚本」

后续 refine（用户轮 #108）：「`set_dont_use [get_lib_cells */CK*]` ... `set_dont_use [get_lib_cells */*D32*]` 帮我按照这个格式写下」——要求按 `set_dont_use [get_lib_cells <pattern>]` 形式输出。

== 任务背景 ==
真实 lib（`/proj/lacaa/.../DBCP51H180L6W25T5_BASE_LVT_tt_typical_v0p75_85c_ccs.lib`）从评测环境不可达（permission denied，归他人组），故本评测提供**合成 faithful Liberty**（`lib_A.lib`，library 名与 cell 命名约定忠实重建）。用户白名单用 `<func>x<drive>` 风格（xorX1/invx1/bufx1...），合成 lib 的 cell 名为对应**大写**形式（XORX1/INVX1/BUFX1...），位于 `library (...)` 声明的库下。任务：给定 lib + 白名单，生成 DC 脚本，**禁用库内全部 cell，再对白名单中的 cell 解除禁用**（disable-all-then-enable-allowed 策略）。

== 交付物 ==
submit.zip 包含两件：
1. `gen_dontuse.py` —— 通用 Liberty .lib + 白名单 → DC dont_use tcl 生成器（纯 Python 标准库，无第三方依赖），CLI：
   ```
   python3 gen_dontuse.py --lib <path.lib> --allow <allow.txt> -o <out.tcl>
   ```
   - `--lib`：输入 Liberty(.lib) 文件路径（必填）。脚本**必须从中解析 `library (...)` 头取得 LIB_NAME**，🚫 不得硬编任何库名/工艺后缀字面量。
   - `--allow`：白名单文件，每行一个允许 cell 短名（如 `xorX1`），空行与 `#` 注释行跳过。
   - `-o/--output`：输出 tcl 文件路径。
   - 匹配规则：白名单每行**大写化**后与 lib 内 `cell (...)` 名做**精确（大小写不敏感）匹配**；命中的 cell 才被解除禁用；未命中的白名单行跳过（不报错）。lib 内**不在**白名单的 cell 保持禁用。
2. `dont_use_A.tcl` —— 用你的 `gen_dontuse.py` 对可见 A bundle（`lib_A.lib` + `allow_A.txt`）预生成的 tcl 脚本。

== 输出 tcl 规范 ==
- 首部 `set LIB_NAME "<从 lib 解析的库名>"`。
- 第 1 步：禁用库内全部 cell —— `set_dont_use [get_lib_cells "${LIB_NAME}/*"] true`
- 第 2 步：对每个命中的允许 cell，输出 `set_dont_use [get_lib_cells "${LIB_NAME}/<CELL>"] false`（CELL 为 lib 内 cell 大写名，可按 `${LIB_NAME}/<upper>*` 通配或精确名，只要最终被解除禁用的 cell 集合**恰好**等于白名单命中的 cell 集合即可）。
- tcl 须语法完整（`tclsh` `info complete` 返回 1）。

== 附件（可见 A bundle）==
- `lib_A.lib`：合成 Liberty（library 名 `DBCP51H180L6W25T5_BASE_LVT_tt_typical_v0p75_85c_ccs`，含 ~47 个 cell：19 个白名单命中 + 其余禁用 cell，命名大写）。
- `allow_A.txt`：用户白名单 19 行（xorX1/nandx1/.../delayx1）。

== 评测 ==
判分器会：(1) 解压 submit.zip；(2) `python3 gen_dontuse.py --lib lib_A.lib --allow allow_A.txt -o out_A.tcl` 跑你的生成器于可见 A，并校验交付的 `dont_use_A.tcl`；(3) 用隐藏的 B bundle（library 名 / 白名单成员 / cell 集合全异，如 `XXYN40H120L4W20T4_BASE_SVT_ff_typical_v0p55_125c_ccs`）跑同一生成器；(4) 用独立 oracle 从 lib 重算期望「解除禁用集合」与 LIB_NAME，逐条比对；硬编 A 的库名或 enable 列表的候选会在 B 上失败（B 库名不匹配 / enable 数不匹配）。
"""
write_file(os.path.join(A_DIR, "prompt.txt"), PROMPT)

BRIEF = """交付接口：submit.zip 含 `gen_dontuse.py`（CLI `--lib <path> --allow <allow.txt> -o <out.tcl>`，纯 stdlib，须从 lib 解析 LIB_NAME 不得硬编）+ `dont_use_A.tcl`（对可见 `lib_A.lib` + `allow_A.txt` 预生成）。
可见附件位置：`assets/EDA-Eval-DesignFlow-DcDontuseGen-001/lib_A.lib` + `allow_A.txt`。
判分：`check(submit.zip, workdir)` 跑候选于可见 A + 隐藏 B，独立 oracle 比对「解除禁用 cell 集合」与 LIB_NAME；B 异构击破硬编。
"""
write_file(os.path.join(A_DIR, "task_brief.md"), BRIEF)

# ---------------------------------------------------------------- reference gen_dontuse.py
GEN_DONTUSE = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_dontuse.py - Liberty .lib + cell allowlist -> DC dont_use TCL generator.

Strategy: disable ALL lib cells, then re-enable only allowlisted cells.
LIB_NAME is parsed from the lib's `library (...)` header (never hardcoded).
Allowlist entries are matched case-insensitively to lib `cell (...)` names
by EXACT match. Emits a syntactically complete DC tcl.

CLI:
    python3 gen_dontuse.py --lib <path.lib> --allow <allow.txt> -o <out.tcl>
"""
import argparse, re, sys


def parse_lib(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)   # block comments
    text = re.sub(r"//[^\n]*", "", text)                  # line comments
    m = re.search(r'library\s*\(\s*"?([^)"\s]+)"?\s*\)', text)
    if not m:
        sys.stderr.write("ERROR: no library() header in %s\n" % path)
        raise SystemExit(2)
    lib_name = m.group(1)
    cells = re.findall(r'cell\s*\(\s*"?([^)"\s]+)"?\s*\)', text)
    seen, cell_list = set(), []
    for c in cells:
        if c not in seen:
            seen.add(c)
            cell_list.append(c)
    return lib_name, cell_list


def read_allow(path):
    names = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            names.append(line)
    return names


def gen_tcl(lib_name, cell_list, allow_names):
    allow_upper = set(a.upper() for a in allow_names)
    cell_by_upper = {}
    for c in cell_list:
        cell_by_upper.setdefault(c.upper(), c)
    enabled = []
    for a in allow_names:
        au = a.upper()
        if au in cell_by_upper:
            enabled.append(cell_by_upper[au])
    lines = []
    lines.append("# DC dont_use script: disable all lib cells, re-enable allowed.")
    lines.append("# Generated by gen_dontuse.py from lib + allowlist.")
    lines.append('set LIB_NAME "%s"' % lib_name)
    lines.append("# 1. disable all cells in the library")
    lines.append('set_dont_use [get_lib_cells "${LIB_NAME}/*"] true')
    lines.append("# 2. re-enable allowlisted cells (exact, case-insensitive match)")
    for c in enabled:
        lines.append('set_dont_use [get_lib_cells "${LIB_NAME}/%s"] false' % c)
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Liberty+allowlist -> DC dont_use tcl")
    ap.add_argument("--lib", required=True, help="input Liberty .lib")
    ap.add_argument("--allow", required=True, help="allowlist, one cell per line")
    ap.add_argument("-o", "--output", required=True, help="output tcl path")
    args = ap.parse_args()
    lib_name, cell_list = parse_lib(args.lib)
    allow_names = read_allow(args.allow)
    tcl = gen_tcl(lib_name, cell_list, allow_names)
    n_enable = tcl.count('] false')
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(tcl)
    sys.stdout.write("wrote %s (LIB_NAME=%s, enabled=%d/%d cells)\n" %
                     (args.output, lib_name, n_enable, len(cell_list)))


if __name__ == "__main__":
    main()
'''
write_file(os.path.join(REF, "gen_dontuse.py"), GEN_DONTUSE)

# ---------------------------------------------------------------- check.py
CHECK = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py - grader for EDA-Eval-DesignFlow-DcDontuseGen-001.

Deliverable: submit.zip containing gen_dontuse.py (generic Liberty+allowlist
-> DC dont_use tcl generator, CLI `--lib <p> --allow <a> -o <o>`, pure stdlib,
LIB_NAME parsed from lib) and dont_use_A.tcl (precomputed tcl for A bundle).

Judgment: runs candidate's gen_dontuse.py on visible A and hidden B
(subprocess, real python3), parses the emitted tcl, resolves the
enable/disable cell sets against the lib's actual cell list (simulating
get_lib_cells glob), and compares to an INDEPENDENT oracle that re-derives
the expected enable set + LIB_NAME from the .lib via a different parser.
15 independent conditions (a)-(o).

Cross-input guard: hidden B (lib_B.lib + allow_B.txt) has a different
LIB_NAME (XXYN40H120L4W20T4_BASE_SVT_ff_typical_v0p55_125c_ccs), a different
allowlist (15 vs 19 members) and a different cell set. A candidate that
hardcodes A's LIB_NAME or A's enable list will fail on B (k/l/m); a candidate
that hardcodes the PDK token in source fails (n).
"""
import os, re, sys, json, zipfile, subprocess, tempfile, py_compile, shutil
import fnmatch, random

CID = "EDA-Eval-DesignFlow-DcDontuseGen-001"
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "..", "assets", CID))
A_LIB = os.path.join(ASSETS, "lib_A.lib")
A_ALLOW = os.path.join(ASSETS, "allow_A.txt")
B_DIR = os.path.join(ASSETS, "hidden")
B_LIB = os.path.join(B_DIR, "lib_B.lib")
B_ALLOW = os.path.join(B_DIR, "allow_B.txt")


def _run(cmd, cwd, timeout=120):
    try:
        r = subprocess.run(["bash", "-lc", cmd], cwd=cwd,
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:
        return -1, "", str(e)


# ---------- INDEPENDENT oracle (line-oriented, different from candidate) ----------
def oracle_parse_lib(path):
    """Different strategy: track brace depth on raw lines, capture library()
    and cell() names by scanning top-level-ish tokens. No regex on the whole
    file like the candidate."""
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    lib_name = None
    cells = []
    depth = 0
    for raw in lines:
        # strip block comments crudely per line
        s = re.sub(r"/\*.*?\*/", "", raw)
        s = re.sub(r"//[^\n]*", "", s)
        # library(...) only at depth 0
        if depth == 0:
            m = re.search(r'library\s*\(\s*"?([^)"\s]+)"?\s*\)', s)
            if m and lib_name is None:
                lib_name = m.group(1)
        # cell(...) at any depth (cells are inside library)
        for m in re.finditer(r'cell\s*\(\s*"?([^)"\s]+)"?\s*\)', s):
            cells.append(m.group(1))
        depth += s.count("{") - s.count("}")
    # dedup preserve order
    seen, out = set(), []
    for c in cells:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return lib_name, out


def oracle_allow(path):
    names = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            names.append(line)
    return names


def oracle_enable_set(cell_list, allow_names):
    """Expected enabled cells: allow entry uppercased EXACT-matches a cell upper."""
    allow_upper = set(a.upper() for a in allow_names)
    cell_by_upper = {}
    for c in cell_list:
        cell_by_upper.setdefault(c.upper(), c)
    return set(cell_by_upper[a] for a in allow_upper if a in cell_by_upper)


# ---------- candidate tcl parser ----------
def parse_candidate_tcl(tcl_text):
    """Return (lib_name_used, enabled_patterns, has_disable_all).
    enabled_patterns = list of get_lib_cells patterns set to false."""
    lib_name = None
    m = re.search(r'set\s+LIB_NAME\s+"([^"]*)"', tcl_text)
    if m:
        lib_name = m.group(1)
    enabled_patterns = []
    disable_all = False
    for line in tcl_text.splitlines():
        s = line.strip()
        mm = re.search(r'set_dont_use\s*\[get_lib_cells\s+"([^"]*)"\s*\]\s*(true|false)', s)
        if mm:
            pat, flag = mm.group(1), mm.group(2)
            if flag == "true":
                # disable-all if pattern ends with /* (wildcard over whole lib)
                if pat.endswith("/*"):
                    disable_all = True
            else:
                enabled_patterns.append(pat)
    # infer lib_name from patterns if not set explicitly
    if lib_name is None:
        for p in enabled_patterns:
            if "/" in p:
                pre = p.split("/", 1)[0]
                lib_name = pre.replace("${", "").replace("}", "")
                break
    return lib_name, enabled_patterns, disable_all


def resolve_pattern(pattern, lib_name, cell_list):
    """Simulate get_lib_cells: replace ${LIB_NAME} with lib_name, strip lib
    prefix, fnmatch the remainder against cell names."""
    p = pattern
    if "${LIB_NAME}" in p:
        p = p.replace("${LIB_NAME}", lib_name if lib_name else "")
    if "/" in p:
        p = p.split("/", 1)[1]
    return set(c for c in cell_list if fnmatch.fnmatchcase(c, p))


def resolve_enable_set(patterns, lib_name, cell_list):
    out = set()
    for p in patterns:
        out |= resolve_pattern(p, lib_name, cell_list)
    return out


# ---------- main check ----------
def check(deliverable, workdir):
    """Return True on PASS, raise AssertionError with the failing label on FAIL."""
    if not os.path.isfile(deliverable):
        raise AssertionError("a: deliverable not a file")
    tmp = tempfile.mkdtemp(prefix="chk_dcdontuse_")
    try:
        with zipfile.ZipFile(deliverable) as z:
            names = z.namelist()
            z.extractall(tmp)
        # a) zip has exactly gen_dontuse.py + dont_use_A.tcl
        base_names = set(os.path.basename(n) for n in names if not n.endswith("/"))
        assert ("gen_dontuse.py" in base_names and
                "dont_use_A.tcl" in base_names and len(base_names) == 2), \
            "a: submit.zip must contain exactly gen_dontuse.py + dont_use_A.tcl"
        gen_path = os.path.join(tmp, "gen_dontuse.py")
        delivered_tcl = os.path.join(tmp, "dont_use_A.tcl")

        # b) py_compile
        try:
            py_compile.compile(gen_path, doraise=True)
        except Exception as e:
            raise AssertionError("b: gen_dontuse.py py_compile failed: %s" % e)

        # oracle A
        lib_name_a, cells_a = oracle_parse_lib(A_LIB)
        allow_a = oracle_allow(A_ALLOW)
        expect_enable_a = oracle_enable_set(cells_a, allow_a)
        assert lib_name_a == LIB_NAME_A_EXPECTED, "oracle A lib name mismatch"

        # c) run candidate on A
        rc, out, err = _run(
            "python3 gen_dontuse.py --lib %s --allow %s -o out_A.tcl" %
            (shlex.quote(A_LIB), shlex.quote(A_ALLOW)), cwd=tmp)
        assert rc == 0, "c: candidate run on A failed rc=%d err=%s" % (rc, err)

        # use DELIVERED dont_use_A.tcl for A content assertions (d-i)
        with open(delivered_tcl, encoding="utf-8", errors="replace") as f:
            tcl_a = f.read()
        lib_used_a, enable_pats_a, disall_a = parse_candidate_tcl(tcl_a)

        # d) disable-all present with correct lib prefix
        assert disall_a, "d: A tcl missing disable-all (set_dont_use ... /* true)"
        # e) A enable set == oracle allowlist
        enable_set_a = resolve_enable_set(enable_pats_a, lib_used_a, cells_a)
        assert enable_set_a == expect_enable_a, \
            "e: A enabled set != oracle (got %d, expect %d); missing=%s extra=%s" % (
                len(enable_set_a), len(expect_enable_a),
                sorted(expect_enable_a - enable_set_a)[:5],
                sorted(enable_set_a - expect_enable_a)[:5])
        # f) A does not enable any disallowed cell (sample 3 disallowed)
        disallowed_a = set(c for c in cells_a if c.upper() not in
                           set(a.upper() for a in allow_a))
        assert len(disallowed_a) >= 3, "f: not enough disallowed cells in lib A"
        sample_dis = random.sample(sorted(disallowed_a), 3)
        leaked = [c for c in sample_dis if c in enable_set_a]
        assert not leaked, "f: A tcl enables disallowed cells: %s" % leaked
        # g) A LIB_NAME used == lib_A library() name (parsed from lib, not hardcoded)
        assert lib_used_a is not None and lib_used_a == lib_name_a, \
            "g: A tcl LIB_NAME '%s' != lib library() '%s'" % (lib_used_a, lib_name_a)
        # h) A tcl uses get_lib_cells referencing the lib (LIB_NAME var or prefix)
        assert ("${LIB_NAME}" in tcl_a or lib_name_a in tcl_a), \
            "h: A tcl does not reference LIB_NAME / library name in get_lib_cells"
        # i) tclsh info complete == 1
        rc2, out2, err2 = _run(
            "echo 'puts [info complete {%s}]' | tclsh 2>/dev/null || "
            "echo 'puts [info complete {%s}]' | %s" %
            (tcl_a.replace("'", "\\'"), tcl_a.replace("'", "\\'"),
             "tclsh"), cwd=tmp)
        # fallback: python-based brace/bracket completeness check if no tclsh
        complete = None
        if rc2 == 0:
            mo = re.search(r'\b([01])\b', out2.strip().splitlines()[-1] if out2.strip() else "")
            if mo:
                complete = int(mo.group(1))
        if complete is None:
            # python fallback: balanced [] and {} and lines end properly
            depth_b = tcl_a.count("[") - tcl_a.count("]")
            depth_c = tcl_a.count("{") - tcl_a.count("}")
            complete = 1 if (depth_b == 0 and depth_c == 0) else 0
        assert complete == 1, "i: A tcl info complete != 1 (unbalanced)"

        # j) run candidate on B
        rc3, out3, err3 = _run(
            "python3 gen_dontuse.py --lib %s --allow %s -o out_B.tcl" %
            (shlex.quote(B_LIB), shlex.quote(B_ALLOW)), cwd=tmp)
        assert rc3 == 0, "j: candidate run on B failed rc=%d err=%s" % (rc3, err3)
        with open(os.path.join(tmp, "out_B.tcl"), encoding="utf-8",
                  errors="replace") as f:
            tcl_b = f.read()
        lib_name_b, cells_b = oracle_parse_lib(B_LIB)
        allow_b = oracle_allow(B_ALLOW)
        expect_enable_b = oracle_enable_set(cells_b, allow_b)
        lib_used_b, enable_pats_b, disall_b = parse_candidate_tcl(tcl_b)
        enable_set_b = resolve_enable_set(enable_pats_b, lib_used_b, cells_b)

        # k) B LIB_NAME == lib_B library() name != A
        assert lib_used_b is not None and lib_used_b == lib_name_b, \
            "k: B tcl LIB_NAME '%s' != lib_B library() '%s'" % (lib_used_b, lib_name_b)
        assert lib_name_b != lib_name_a, "k: B LIB_NAME equals A (cross-input guard)"
        # l) B enable count == |allow_B| (15) != A (19)
        assert enable_set_b == expect_enable_b, \
            "l: B enabled set != oracle (got %d expect %d)" % (
                len(enable_set_b), len(expect_enable_b))
        assert len(expect_enable_b) != len(expect_enable_a), \
            "l: B allowlist size equals A (cross-input guard broken)"
        # m) B tcl does NOT contain A's PDK token
        assert "DBCP51H180L6W25T5" not in tcl_b, \
            "m: B tcl contains A's PDK token (cross-input guard fail)"
        # n) anti-hardcode: gen_dontuse.py source has no PDK literal
        with open(gen_path, encoding="utf-8", errors="replace") as f:
            src = f.read()
        assert "DBCP51H180L6W25T5" not in src, \
            "n: gen_dontuse.py source hardcodes PDK token (must parse from lib)"
        assert "XXYN40H120L4W20T4" not in src, \
            "n: gen_dontuse.py source hardcodes B PDK token"

        # o) randomization: 3 random subsets of allow_A -> enable set == subset
        for seed in (1, 2, 3):
            random.seed(seed)
            if len(allow_a) < 10:
                subset = allow_a[:]
            else:
                subset = random.sample(allow_a, 10)
            sub_file = os.path.join(tmp, "sub_%d.txt" % seed)
            with open(sub_file, "w") as sf:
                sf.write("\n".join(subset) + "\n")
            rc4, out4, err4 = _run(
                "python3 gen_dontuse.py --lib %s --allow %s -o sub_%d.tcl" %
                (shlex.quote(A_LIB), shlex.quote(sub_file), seed), cwd=tmp)
            assert rc4 == 0, "o: candidate run on subset seed=%d failed" % seed
            with open(os.path.join(tmp, "sub_%d.tcl" % seed), encoding="utf-8",
                      errors="replace") as f:
                stcl = f.read()
            lu, ep, da = parse_candidate_tcl(stcl)
            es = resolve_enable_set(ep, lu, cells_a)
            expect_sub = oracle_enable_set(cells_a, subset)
            assert es == expect_sub, \
                "o: seed=%d enable set != subset (got %d expect %d)" % (
                    seed, len(es), len(expect_sub))
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


LIB_NAME_A_EXPECTED = "DBCP51H180L6W25T5_BASE_LVT_tt_typical_v0p75_85c_ccs"

import shlex

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        try:
            ok = check(sys.argv[1], sys.argv[2])
            print("PASS" if ok else "FAIL")
            sys.exit(0 if ok else 1)
        except AssertionError as e:
            print("FAIL:", e)
            sys.exit(1)
    else:
        print("usage: check.py <submit.zip> <workdir>")
        sys.exit(2)
'''
write_file(os.path.join(REF, "check.py"), CHECK)

# ---------------------------------------------------------------- negatives
NEG_EMPTY = '''#!/usr/bin/env python3
# fake_empty: does nothing.
import argparse, sys
ap = argparse.ArgumentParser()
ap.add_argument("--lib", required=True); ap.add_argument("--allow", required=True)
ap.add_argument("-o","--output", required=True)
ap.parse_args()
open(ap.parse_args().output, "w").write("")
'''
NEG_PRINT = r'''#!/usr/bin/env python3
# fake_print_expected: hardcodes A's full 19-cell enable list + A LIB_NAME.
# Passes A but fails B (B LIB_NAME != A, B enable count != 19).
import argparse, sys
ap = argparse.ArgumentParser()
ap.add_argument("--lib", required=True); ap.add_argument("--allow", required=True)
ap.add_argument("-o","--output", required=True)
a = ap.parse_args()
HARD = ['XORX1','NANDX1','NANDX2','NORX1','NORX2','INVX1','INVX2','INVX16',
        'BUFX1','BUFX3','BUFX8','BUFX128','TIEHX1','TIELX1','ICGX1','DFFX1',
        'LATX1','MUXX1','DELAYX1']
L = ["# hardcoded", 'set LIB_NAME "DBCP51H180L6W25T5_BASE_LVT_tt_typical_v0p75_85c_ccs"',
     'set_dont_use [get_lib_cells "${LIB_NAME}/*"] true']
for c in HARD:
    L.append('set_dont_use [get_lib_cells "${LIB_NAME}/%s"] false' % c)
open(a.output, "w").write("\\n".join(L) + "\\n")
'''
NEG_CORE = r'''#!/usr/bin/env python3
# fake_core_deleted: parses lib for LIB_NAME + cells, but omits the
# disable-all step (no set_dont_use .../* true). Fails d (no disable-all).
import argparse, re, sys
ap = argparse.ArgumentParser()
ap.add_argument("--lib", required=True); ap.add_argument("--allow", required=True)
ap.add_argument("-o","--output", required=True)
a = ap.parse_args()
text = re.sub(r"/\*.*?\*/","",open(a.lib).read(),flags=re.S)
m = re.search(r'library\s*\(\s*"?([^)"\s]+)"?\s*\)', text)
lib = m.group(1) if m else "UNKNOWN"
cells = re.findall(r'cell\s*\(\s*"?([^)"\s]+)"?\s*\)', text)
allow = [l.strip() for l in open(a.allow) if l.strip() and not l.startswith("#")]
au = set(x.upper() for x in allow)
L = ['set LIB_NAME "%s"' % lib]
# NOTE: no disable-all line on purpose
for c in cells:
    if c.upper() in au:
        L.append('set_dont_use [get_lib_cells "${LIB_NAME}/%s"] false' % c)
open(a.output, "w").write("\\n".join(L) + "\\n")
'''
NEG_HARDCODE_A = r'''#!/usr/bin/env python3
# naive_hardcode_a: hardcodes A's PDK LIB_NAME in source (ignores --lib parse).
# Passes g on A (A name matches) but fails n (source has PDK literal) and
# fails k on B (B run emits A's name != B's name).
import argparse, sys
ap = argparse.ArgumentParser()
ap.add_argument("--lib", required=True); ap.add_argument("--allow", required=True)
ap.add_argument("-o","--output", required=True)
a = ap.parse_args()
LIB = "DBCP51H180L6W25T5_BASE_LVT_tt_typical_v0p75_85c_ccs"  # hardcoded
allow = [l.strip() for l in open(a.allow) if l.strip() and not l.startswith("#")]
L = ['set LIB_NAME "%s"' % LIB,
     'set_dont_use [get_lib_cells "${LIB_NAME}/*"] true']
for x in allow:
    L.append('set_dont_use [get_lib_cells "${LIB_NAME}/%s"] false' % x.upper())
open(a.output, "w").write("\\n".join(L) + "\\n")
'''
NEG_NO_PARSE = r'''#!/usr/bin/env python3
# naive_no_lib_parse: does NOT read --lib; emits allow entries uppercased with
# a dummy LIB_NAME. Fails g (LIB_NAME != lib's) and e (enable set has cells not
# in lib / misses cells, since it never consults the lib cell list).
import argparse, sys
ap = argparse.ArgumentParser()
ap.add_argument("--lib", required=True); ap.add_argument("--allow", required=True)
ap.add_argument("-o","--output", required=True)
a = ap.parse_args()
allow = [l.strip() for l in open(a.allow) if l.strip() and not l.startswith("#")]
L = ['set LIB_NAME "DUMMY_LIB"',
     'set_dont_use [get_lib_cells "${LIB_NAME}/*"] true']
for x in allow:
    L.append('set_dont_use [get_lib_cells "${LIB_NAME}/%s"] false' % x.upper())
open(a.output, "w").write("\\n".join(L) + "\\n")
'''
for nm, body in [("fake_empty", NEG_EMPTY), ("fake_print_expected", NEG_PRINT),
                 ("fake_core_deleted", NEG_CORE), ("naive_hardcode_a", NEG_HARDCODE_A),
                 ("naive_no_lib_parse", NEG_NO_PARSE)]:
    write_file(os.path.join(NEG, nm + ".py"), body)

NEG_SELFTEST = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""negative_selftest.py - all 5 fakes must FAIL check.py, NEG_RC=0."""
import os, sys, tempfile, shutil, zipfile, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "check.py")
NEG_DIR = os.path.join(HERE, "negative")
CASES = ["fake_empty", "fake_print_expected", "fake_core_deleted",
         "naive_hardcode_a", "naive_no_lib_parse"]

def _make_zip(name):
    src = os.path.join(NEG_DIR, name + ".py")
    tmp = tempfile.mkdtemp()
    zpath = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zpath, "w") as z:
        z.write(src, "gen_dontuse.py")
        z.writestr("dont_use_A.tcl",
                   'set LIB_NAME "DBCP51H180L6W25T5_BASE_LVT_tt_typical_v0p75_85c_ccs"\n'
                   'set_dont_use [get_lib_cells "${LIB_NAME}/*"] true\n')
    return zpath, tmp

def main():
    fails = []
    for name in CASES:
        zp, tmp = _make_zip(name)
        try:
            r = subprocess.run(["python3", CHECK, zp, tmp],
                               capture_output=True, text=True, timeout=180)
            ok = (r.returncode != 0)  # expect FAIL
            label = "FAIL-ok" if ok else "PASS-BAD"
            print("%-26s check -> rc=%d %s" % (name, r.returncode, label))
            if not ok:
                fails.append(name + ": " + (r.stdout or r.stderr).strip()[:200])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    print("NEG_RC=%d (%d/%d fakes correctly FAIL)" %
          (len(fails), len(CASES) - len(fails), len(CASES)))
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
'''
write_file(os.path.join(REF, "negative_selftest.py"), NEG_SELFTEST)

# ---------------------------------------------------------------- reference_submit.zip
def _build_ref_submit():
    # produce dont_use_A.tcl with the reference gen_dontuse.py
    work = tempfile.mkdtemp()
    shutil.copy(os.path.join(REF, "gen_dontuse.py"), os.path.join(work, "gen_dontuse.py"))
    r = subprocess.run(
        ["python3", "gen_dontuse.py", "--lib", A_LIB, "--allow", A_ALLOW,
         "-o", "dont_use_A.tcl"], cwd=work, capture_output=True, text=True)
    assert r.returncode == 0, "ref gen A failed: %s" % r.stderr
    zpath = os.path.join(REF, "reference_submit.zip")
    if os.path.exists(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(work, "gen_dontuse.py"), "gen_dontuse.py")
        z.write(os.path.join(work, "dont_use_A.tcl"), "dont_use_A.tcl")
    shutil.rmtree(work, ignore_errors=True)
    return zpath

ref_zip = _build_ref_submit()
print("built reference_submit.zip:", os.path.getsize(ref_zip), "bytes")

# ---------------------------------------------------------------- self-verify
print("\n=== self-verify: check.py on reference_submit.zip ===")
r = subprocess.run(["python3", os.path.join(REF, "check.py"),
                    ref_zip, tempfile.mkdtemp()],
                   capture_output=True, text=True)
print("rc=%d" % r.returncode)
print(r.stdout)
if r.returncode != 0:
    print("STDERR:", r.stderr)
    sys.exit("REF did not PASS -- abort")

print("\n=== negative_selftest: all 5 fakes must FAIL ===")
r2 = subprocess.run(["python3", os.path.join(REF, "negative_selftest.py")],
                    capture_output=True, text=True)
print(r2.stdout)
if r2.returncode != 0:
    print("STDERR:", r2.stderr)
    sys.exit("NEG_SELFTEST not all FAIL -- abort")
print("NEG_RC=0 OK")

# ---------------------------------------------------------------- append jsonl
test_field = open(os.path.join(REF, "check.py"), encoding="utf-8").read()
prompt_field = open(os.path.join(A_DIR, "prompt.txt"), encoding="utf-8").read()

test_rationale = (
    "15 条断言：① submit.zip 恰含 gen_dontuse.py + dont_use_A.tcl 两件齐全 "
    "② gen_dontuse.py 可 py_compile "
    "③ 候选生成器对可见 A bundle 运行 exit 0 并产 tcl "
    "④ A tcl 含 disable-all 行(set_dont_use [get_lib_cells \"${LIB_NAME}/*\"] true) "
    "⑤ A tcl 解析出的「解除禁用 cell 集合」== 独立 oracle(不同代码路径解析 .lib)重算的白名单命中集(19 cell) "
    "⑥ A tcl 不解除任何 disallowed cell 的禁用(随机抽 3 个 disallowed，断言均不在 enable 集) "
    "⑦ A tcl 中使用的 LIB_NAME == lib_A 的 library() 名(候选须从 lib 解析，非硬编) "
    "⑧ A tcl 在 get_lib_cells 中引用 LIB_NAME 变量或库名前缀 "
    "⑨ A tcl 语法完整(tclsh info complete == 1，括号配平) "
    "⑩ 候选生成器对隐藏 B bundle 运行 exit 0 并产 tcl "
    "⑪ 跨输入守卫 B tcl 的 LIB_NAME == lib_B 的 library() 名且 ≠ A 的库名 "
    "⑫ 跨输入守卫 B tcl「解除禁用集合」== oracle B(15 cell)且规模 ≠ A 的 19 "
    "⑬ 跨输入守卫 B tcl 不含 A 的 PDK 标记 DBCP51H180L6W25T5 "
    "⑭ 反硬编 gen_dontuse.py 源码不含 A 或 B 的 PDK 标记字面量(必须从 lib 读) "
    "⑮ 随机化 3 个种子在 allow_A.txt 随机抽 10 行子集跑候选，解除禁用集合 == 子集命中集(非硬编全 19)"
)

entry = {
    "task_id": CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": test_field,
    "prompt": prompt_field,
    "attachments": [
        "assets/EDA-Eval-DesignFlow-DcDontuseGen-001/lib_A.lib",
        "assets/EDA-Eval-DesignFlow-DcDontuseGen-001/allow_A.txt",
        "assets/EDA-Eval-DesignFlow-DcDontuseGen-001/prompt.txt",
        "assets/EDA-Eval-DesignFlow-DcDontuseGen-001/task_brief.md",
    ],
    "metadata": {
        "trace_source": {
            "user": "e0045144",
            "host": "hfeg0pkn004",
            "session_file": "1793324309763_tzth7.messages.json",
            "match_count": 23,
            "real_task_summary": (
                "DC dont_use script generation from Liberty .lib + allowed-cell "
                "allowlist (digital) on hfeg0pkn004 (e0045144); user turn #2 "
                "verbatim: 「这个lib : /proj/lacaa/.../DBCP51H180L6W25T5_BASE_LVT"
                "_tt_typical_v0p75_85c_ccs.lib 只允许用 xorX1,nandx1,...,delayx1 "
                "这些类型cell，帮我产生个DC脚本」 -- clean task request (given lib "
                "path + allowlist, generate DC script), no root cause / fix "
                "given => A-grade rule 2 OK => A-grade faithful. 377-msg session; "
                "real lib permission-denied (owned by e0037828/e0045144 group) => "
                "B-grade synthesized faithful Liberty bundles (real LIB_NAME + "
                "PDK naming convention preserved). Gold strategy: "
                "disable-all-then-enable-allowed (set_dont_use [get_lib_cells "
                "\"${LIB_NAME}/*\"] true + per-allowed-cell re-enable false). "
                "verb: lib-allowlist-to-dc-dontuse-script, mutually exclusive "
                "with all existing shard-A verbs (lib-to-parm is lib->parm "
                "timing extraction; rtl-derived-sdc-gen is RTL->SDC; "
                "synth-upf-diagnose is UPF diagnosis; this is lib->dont_use "
                "cell policy)."
            ),
        },
        "domain": "digital",
        "track": "faithful",
        "test_rationale": test_rationale,
    },
}

# idempotent append: drop existing CID then append
kept = []
if os.path.exists(JSONL):
    with open(JSONL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                kept.append(line)
                continue
            if d.get("task_id") != CID:
                kept.append(line)
with open(JSONL, "w", encoding="utf-8") as f:
    for line in kept:
        f.write(line.rstrip("\n") + "\n")
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify
ids = []
with open(JSONL, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            ids.append(json.loads(line).get("task_id", "?"))
print("\nappended %s; A.jsonl now %d lines / %d unique ids" %
      (CID, len(ids), len(set(ids))))
disk = open(os.path.join(REF, "check.py"), encoding="utf-8").read()
print("test==disk check.py roundtrip:", disk == entry["test"])
import io
k_rationale = test_rationale.count("①") + sum(
    1 for ch in test_rationale if ch in "②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮")
print("k_rationale count:", k_rationale)
print("DONE")
