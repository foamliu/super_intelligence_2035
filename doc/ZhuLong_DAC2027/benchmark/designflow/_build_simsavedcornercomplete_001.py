#!/usr/bin/env python3
"""Builder for EDA-Eval-DesignFlow-SimSavedCornerComplete-001.

A-faithful (characterization, L1) case from ynbai@hfhds201 trace
1794018867939_1qlnn: parse sim.saved.total (PVT corner case list), find cases
missing the 5 expected PVT corners, output only the supplemented (missing) lines.

Generates: assets (A + hidden B + manifest + prompt + task_brief), reference
(ref script + check.py with 17 conditions a..q + 5 negatives + selftest +
reference_submit.zip).
"""
import os, zipfile

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-SimSavedCornerComplete-001"
A_ROOT = os.path.join(BENCH, "assets", CID)
REF_ROOT = os.path.join(BENCH, "reference", CID)

P = "/proj/drvqa/V0/setup/sim/sim_vector/verilog.ddr5.drvqa.vecgen/log_20260908_newWL/vec_golden"

# 5 expected PVT corners and their path-suffix type
EXPECTED = ["FF1.3v110C", "FF1.3v-40C", "TT0.94v25C", "SS0.94v110C", "SS0.94v-40C"]
CORNER_TYPE = {"FF1.3v110C": "_FF", "FF1.3v-40C": "_FF",
               "TT0.94v25C": "_TT", "SS0.94v110C": "_SS", "SS0.94v-40C": "_SS"}

def line(base, corner, w="X4"):
    return "%s%s.%s %s %s" % (base, CORNER_TYPE[corner], w, corner, w)

# ---- Asset A (visible, faithful to real trace: long Golden paths) ----
A1 = P + "/3600_X4_BC8_OTF/Golden005_Multi4bank_redundancy_combine_WPre_4_CRC_00_1_tCH_50_BC8_OTF_4b8g_Bcd08_3600"
A2 = P + "/3600_X4_BC8_OTF/Golden012_SingleBank_Precharge_4_CRC_01_2_tCH_40_BC8_OTF_4b8g_Bcd08_3600"
A3 = P + "/4800_X4_BC8_OTF/Golden023_DualBank_WriteRead_4_CRC_02_1_tCH_60_BC8_OTF_4b8g_Bcd08_4800"
A4 = P + "/3600_X4_BC8_OTF/Golden031_QuadBank_Activate_4_CRC_03_1_tCH_55_BC8_OTF_4b8g_Bcd08_3600"

A_LINES = []
# A1 complete (the real 5-corner example from USER#0)
for c in EXPECTED:
    A_LINES.append(line(A1, c))
# A2 missing TT0.94v25C, SS0.94v-40C (has FF*2, SS0.94v110C)
for c in ["FF1.3v110C", "FF1.3v-40C", "SS0.94v110C"]:
    A_LINES.append(line(A2, c))
# A3 missing FF1.3v-40C (has FF110, TT, SS*2)
for c in ["FF1.3v110C", "TT0.94v25C", "SS0.94v110C", "SS0.94v-40C"]:
    A_LINES.append(line(A3, c))
# A4 complete
for c in EXPECTED:
    A_LINES.append(line(A4, c))

# A expected missing = 3 lines: A2 TT, A2 SS-40, A3 FF-40
A_EXPECTED = [line(A2, "TT0.94v25C"), line(A2, "SS0.94v-40C"), line(A3, "FF1.3v-40C")]

# ---- Hidden B (different cases, includes X8 width) ----
B1 = "/sim/vec/char/ProbeA_3200"
B2 = "/sim/vec/char/ProbeB_2700"
B3 = "/sim/vec/char/ProbeC_4800"
B4 = "/sim/vec/char/ProbeD_3600"
B5 = "/sim/vec/char/ProbeE_2400"
B6 = "/sim/vec/char/ProbeF_4000"

B_LINES = []
# B1 complete X4
for c in EXPECTED:
    B_LINES.append(line(B1, c))
# B2 missing TT, SS-40 (has FF*2, SS110)
for c in ["FF1.3v110C", "FF1.3v-40C", "SS0.94v110C"]:
    B_LINES.append(line(B2, c))
# B3 missing FF-40 (has FF110, TT, SS*2)
for c in ["FF1.3v110C", "TT0.94v25C", "SS0.94v110C", "SS0.94v-40C"]:
    B_LINES.append(line(B3, c))
# B4 missing SS*2 (has FF*2, TT)
for c in ["FF1.3v110C", "FF1.3v-40C", "TT0.94v25C"]:
    B_LINES.append(line(B4, c))
# B5 missing FF110, TT (has FF-40, SS*2)
for c in ["FF1.3v-40C", "SS0.94v110C", "SS0.94v-40C"]:
    B_LINES.append(line(B5, c))
# B6 complete X8
for c in EXPECTED:
    B_LINES.append(line(B6, c, "X8"))

# B expected missing = 7 lines (in EXPECTED order per case)
B_EXPECTED = [
    line(B2, "TT0.94v25C"),
    line(B2, "SS0.94v-40C"),
    line(B3, "FF1.3v-40C"),
    line(B4, "SS0.94v110C"),
    line(B4, "SS0.94v-40C"),
    line(B5, "FF1.3v110C"),
    line(B5, "TT0.94v25C"),
]

# ============ write asset files ============
os.makedirs(A_ROOT, exist_ok=True)
os.makedirs(os.path.join(A_ROOT, "hidden"), exist_ok=True)
os.makedirs(REF_ROOT, exist_ok=True)
os.makedirs(os.path.join(REF_ROOT, "negative"), exist_ok=True)

with open(os.path.join(A_ROOT, "sim.saved.total"), "w") as f:
    f.write("\n".join(A_LINES) + "\n")
with open(os.path.join(A_ROOT, "hidden", "sim.saved.total"), "w") as f:
    f.write("\n".join(B_LINES) + "\n")

PROMPT = """识别/proj/drvqa/V0/setup/sim/sim_vector/verilog.ddr5.drvqa.vecgen/log_20260908_newWL下的sim.saved.total文件，文件为仿真输入文件，内容例如/proj/drvqa/V0/setup/sim/sim_vector/verilog.ddr5.drvqa.vecgen/log_20260908_newWL/vec_golden/3600_X4_BC8_OTF/Golden005_Multi4bank_redundancy_combine_WPre_4_CRC_00_1_tCH_50_BC8_OTF_4b8g_Bcd08_3600_FF.X4 FF1.3v110C X4
/proj/drvqa/V0/setup/sim/sim_vector/verilog.ddr5.drvqa.vecgen/log_20260908_newWL/vec_golden/3600_X4_BC8_OTF/Golden005_Multi4bank_redundancy_combine_WPre_4_CRC_00_1_tCH_50_BC8_OTF_4b8g_Bcd08_3600_FF.X4 FF1.3v-40C X4
/proj/drvqa/V0/setup/sim/sim_vector/verilog.ddr5.drvqa.vecgen/log_20260908_newWL/vec_golden/3600_X4_BC8_OTF/Golden005_Multi4bank_redundancy_combine_WPre_4_CRC_00_1_tCH_50_BC8_OTF_4b8g_Bcd08_3600_TT.X4 TT0.94v25C X4
/proj/drvqa/V0/setup/sim/sim_vector/verilog.ddr5.drvqa.vecgen/log_20260908_newWL/vec_golden/3600_X4_BC8_OTF/Golden005_Multi4bank_redundancy_combine_WPre_4_CRC_00_1_tCH_50_BC8_OTF_4b8g_Bcd08_3600_SS.X4 SS0.94v110C X4
/proj/drvqa/V0/setup/sim/sim_vector/verilog.ddr5.drvqa.vecgen/log_20260908_newWL/vec_golden/3600_X4_BC8_OTF/Golden005_Multi4bank_redundancy_combine_WPre_4_CRC_00_1_tCH_50_BC8_OTF_4b8g_Bcd08_3600_SS.X4 SS0.94v-40C X4
为仿真case Golden005_Multi4bank_redundancy_combine_WPre_4_CRC_00_1_tCH_50_BC8_OTF_4b8g_Bcd08_3600的5个corner的输入，每一个case应该都有5个，但是文件不全，部分不是五个，帮忙补全，补全文件生成为sim.saved.total.zl，相同corner不同电压温度下前方相同，例如/proj/drvqa/V0/setup/sim/sim_vector/verilog.ddr5.drvqa.vecgen/log_20260908_newWL/vec_golden/3600

多出来的case行输出到sim.saved.total.zl.more中

（附件 sim.saved.total 为示例输入文件，格式与上述一致；请编写通用脚本，交付接口见 task_brief.md。判分在隐藏的合成输入上独立运行，不依赖 prompt 中提到的真实路径。）
"""
with open(os.path.join(A_ROOT, "prompt.txt"), "w") as f:
    f.write(PROMPT)

TASK_BRIEF = """# 交付接口
交付 `outputs/submit.zip`，内含一个可执行的 python3 CLI 脚本 `sim_saved_corner_complete.py`，用法：
`python3 sim_saved_corner_complete.py <sim_saved_total_file> <output_more_file>`
脚本读取 <sim_saved_total_file>，按 case（路径去掉末尾 `_FF|_TT|_SS` 后缀为同一 case）分组，每个 case 应有 5 个 PVT corner（FF1.3v110C / FF1.3v-40C / TT0.94v25C / SS0.94v110C / SS0.94v-40C），把缺失 corner 对应的补充行（沿用该 case 同类型 corner 的路径后缀与宽度）写入 <output_more_file>。判分用隐藏输入运行，不依赖 prompt 中的真实路径。
"""
with open(os.path.join(A_ROOT, "task_brief.md"), "w") as f:
    f.write(TASK_BRIEF)

MANIFEST = {
    "expected": {
        "more_lines_count": len(B_EXPECTED),
        "more_lines": B_EXPECTED,
        "formula": "per case: emit expected PVT corners not present, using same-type path suffix + width",
        "expected_corners": EXPECTED,
    },
    "cross_guard": {
        "B_must": ["hidden/sim.saved.total"],
        "A_only": ["sim.saved.total"],
        "A_more_lines_count": len(A_EXPECTED),
    },
}
import json
with open(os.path.join(A_ROOT, "hidden", "hidden_manifest.json"), "w") as f:
    json.dump(MANIFEST, f, ensure_ascii=False, indent=2)

# ============ reference solution ============
REF_SCRIPT = '''#!/usr/bin/env python3
"""sim_saved_corner_complete.py -- reference solution for SimSavedCornerComplete-001.

Usage: python3 sim_saved_corner_complete.py <sim_saved_total_file> <output_more_file>

Reads <sim_saved_total_file>; each non-empty line has the form:
    <base_path>_<FF|TT|_SS>.X<4|8> <PVT_TAG> X<4|8>
Lines for the same case (base_path = path with the trailing _FF/_TT/_SS.Xn suffix
removed) appear consecutively. Each case should have all 5 PVT corners:
    FF1.3v110C, FF1.3v-40C, TT0.94v25C, SS0.94v110C, SS0.94v-40C
For every missing corner, emit a supplemented line using the path suffix of the
same corner TYPE already seen for that case (or the case's width if that type was
never seen). Only the supplemented (missing) lines are written to <output_more_file>.
"""
import re, sys

EXPECTED_CORNERS = ["FF1.3v110C", "FF1.3v-40C", "TT0.94v25C", "SS0.94v110C", "SS0.94v-40C"]
CORNER_TYPE = {"FF1.3v110C": "_FF", "FF1.3v-40C": "_FF",
               "TT0.94v25C": "_TT", "SS0.94v110C": "_SS", "SS0.94v-40C": "_SS"}
LINE_RE = re.compile(r"^(\\S+) (\\S+) (X\\d+)$")
SUFFIX_RE = re.compile(r"(_FF|_TT|_SS)(\\.X[48])$")


def complete(input_file, more_file):
    with open(input_file) as f:
        lines = [ln.rstrip("\\n") for ln in f]
    added = []
    i = 0
    n = len(lines)
    while i < n:
        m = LINE_RE.match(lines[i])
        if not m:
            i += 1
            continue
        full_path, _first, width = m.groups()
        sm = SUFFIX_RE.search(full_path)
        if not sm:
            i += 1
            continue
        base_path = full_path[:sm.start()]
        ext = sm.group(2)
        corners_seen = set()
        path_suffixes = {}
        j = i
        while j < n:
            m2 = LINE_RE.match(lines[j])
            if not m2:
                break
            fp, c, w = m2.groups()
            sm2 = SUFFIX_RE.search(fp)
            if not sm2:
                break
            bp = fp[:sm2.start()]
            if bp != base_path:
                break
            ct = sm2.group(1)
            ext_j = sm2.group(2)
            corners_seen.add(c)
            if ct not in path_suffixes:
                path_suffixes[ct] = ct + ext_j
            j += 1
        for ec in EXPECTED_CORNERS:
            if ec not in corners_seen:
                ct = CORNER_TYPE[ec]
                suffix = path_suffixes.get(ct, ct + ext)
                added.append("%s%s %s %s" % (base_path, suffix, ec, width))
        i = j
    with open(more_file, "w") as f:
        for ln in added:
            f.write(ln + "\\n")
    return added


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write("usage: sim_saved_corner_complete.py <input> <output>\\n")
        sys.exit(2)
    a = complete(sys.argv[1], sys.argv[2])
    print("Total added lines: %d" % len(a))
'''
with open(os.path.join(REF_ROOT, "sim_saved_corner_complete_ref.py"), "w") as f:
    f.write(REF_SCRIPT)

# ============ check.py (17 conditions a..q) ============
# Embed B and A inline as line lists (anti-hardcode: hidden B not in SUT sandbox).
B_LINES_PY = repr(B_LINES)
A_LINES_PY = repr(A_LINES)
B_EXPECTED_PY = repr(B_EXPECTED)
A_EXPECTED_PY = repr(A_EXPECTED)

CHECK = '''#!/usr/bin/env python3
"""check.py -- SimSavedCornerComplete-001 judge.

Deliverable: submit.zip with a python3 CLI script `sim_saved_corner_complete.py`:
    python3 sim_saved_corner_complete.py <sim_saved_total_file> <output_more_file>

Behavior (per prompt): read the sim.saved.total input; group consecutive lines by
case (base_path = path with trailing _FF/_TT/_SS.Xn removed); each case should have
5 PVT corners (FF1.3v110C, FF1.3v-40C, TT0.94v25C, SS0.94v110C, SS0.94v-40C);
write only the supplemented (missing) corner lines to <output_more_file>, using the
same-type path suffix + width already seen for that case.

check() builds a HIDDEN input B (and a visible A as anti-hardcode guard), runs the
submitted script, and asserts 17 independent conditions (a..q).
"""
import os, sys, shutil, zipfile, tempfile, subprocess, re

PY = sys.executable or "python3"

EXPECTED_CORNERS = ["FF1.3v110C", "FF1.3v-40C", "TT0.94v25C", "SS0.94v110C", "SS0.94v-40C"]
CORNER_TYPE = {"FF1.3v110C": "_FF", "FF1.3v-40C": "_FF",
               "TT0.94v25C": "_TT", "SS0.94v110C": "_SS", "SS0.94v-40C": "_SS"}
LINE_RE = re.compile(r"^(\\S+) (\\S+) (X\\d+)$")

# Hidden B (judge-only, never in SUT sandbox) and visible A (anti-hardcode).
B_LINES = %(B_LINES_PY)s
A_LINES = %(A_LINES_PY)s
B_EXPECTED = %(B_EXPECTED_PY)s   # 7 lines
A_EXPECTED = %(A_EXPECTED_PY)s   # 3 lines


def _extract_script(zippath, tmp):
    if not os.path.exists(zippath):
        raise AssertionError("a: deliverable not found")
    with zipfile.ZipFile(zippath) as z:
        names = z.namelist()
    py = [n for n in names if n.endswith(".py") and "__pycache__" not in n]
    if not py:
        raise AssertionError("a: submit.zip has no python script file")
    py.sort(key=lambda n: (0 if "sim_saved" in n else 1, n))
    target = py[0]
    with zipfile.ZipFile(zippath) as z:
        z.extract(target, tmp)
    return os.path.join(tmp, target)


def _run(script, args, cwd):
    return subprocess.run([PY, script] + args, cwd=cwd, capture_output=True, text=True, timeout=120)


def _read_lines(p):
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return [ln.rstrip("\\n") for ln in f if ln.strip() != ""]


def check(deliverable, workdir):
    tmp = tempfile.mkdtemp(prefix="chk_simsaved_")
    try:
        script = _extract_script(deliverable, tmp)

        # b: script compiles
        r = subprocess.run([PY, "-m", "py_compile", script], capture_output=True, text=True)
        if r.returncode != 0:
            raise AssertionError("b: script does not compile: %%s" %% r.stderr[:200])

        # c: no-args / wrong-arg-count must exit non-zero
        rc = _run(script, [], tmp).returncode
        if rc == 0:
            raise AssertionError("c: no-args must exit non-zero")
        rc = _run(script, ["only_one"], tmp).returncode
        if rc == 0:
            raise AssertionError("c: wrong-arg-count must exit non-zero")

        # write hidden B to a file (not in SUT workdir; in judge tmp)
        B = os.path.join(tmp, "B_sim.saved.total")
        with open(B, "w") as f:
            f.write("\\n".join(B_LINES) + "\\n")
        out = os.path.join(tmp, "B_more.txt")
        rd = _run(script, [B, out], tmp)
        if rd.returncode != 0:
            raise AssertionError("d: run on B exited %%d: %%s" %% (rd.returncode, rd.stderr[:200]))
        lines = _read_lines(out)
        if lines is None:
            raise AssertionError("d: output more-file not created on B")

        # e: every line format <path> <PVT> X<4|8>, PVT in 5 expected
        for ln in lines:
            m = LINE_RE.match(ln)
            if not m:
                raise AssertionError("e: line %%r not in '<path> <PVT> X<w>' format" %% ln)
            _, pvt, w = m.groups()
            if pvt not in EXPECTED_CORNERS:
                raise AssertionError("e: PVT tag %%r not one of the 5 expected" %% pvt)
            if not re.match(r"^X[48]$", w):
                raise AssertionError("e: width %%r not X4/X8" %% w)

        # f: line count == 7, no blank lines
        if len(lines) != len(B_EXPECTED):
            raise AssertionError("f: output line count %%d != expected %%d" %% (len(lines), len(B_EXPECTED)))

        # g: no output line duplicates an existing B line (supplemented = NEW missing corners)
        bset = set(B_LINES)
        for ln in lines:
            if ln in bset:
                raise AssertionError("g: output line %%r already present in B (must be a missing corner)" %% ln)

        def _has(base_frag, pvt):
            for ln in lines:
                m = LINE_RE.match(ln)
                if m and base_frag in m.group(1) and m.group(2) == pvt:
                    return True
            return False

        # h,i: ProbeB_2700 missing TT + SS-40
        if not _has("ProbeB_2700", "TT0.94v25C"):
            raise AssertionError("h: ProbeB_2700 TT0.94v25C supplemented line missing")
        if not _has("ProbeB_2700", "SS0.94v-40C"):
            raise AssertionError("i: ProbeB_2700 SS0.94v-40C supplemented line missing")
        # j: ProbeC_4800 missing FF-40
        if not _has("ProbeC_4800", "FF1.3v-40C"):
            raise AssertionError("j: ProbeC_4800 FF1.3v-40C supplemented line missing")
        # k,l: ProbeD_3600 missing SS*2
        if not _has("ProbeD_3600", "SS0.94v110C"):
            raise AssertionError("k: ProbeD_3600 SS0.94v110C supplemented line missing")
        if not _has("ProbeD_3600", "SS0.94v-40C"):
            raise AssertionError("l: ProbeD_3600 SS0.94v-40C supplemented line missing")
        # m,n: ProbeE_2400 missing FF110 + TT
        if not _has("ProbeE_2400", "FF1.3v110C"):
            raise AssertionError("m: ProbeE_2400 FF1.3v110C supplemented line missing")
        if not _has("ProbeE_2400", "TT0.94v25C"):
            raise AssertionError("n: ProbeE_2400 TT0.94v25C supplemented line missing")

        # o: complete cases ProbeA_3200 / ProbeF_4000 produce NO output line
        for ln in lines:
            m = LINE_RE.match(ln)
            if m and ("ProbeA_3200" in m.group(1) or "ProbeF_4000" in m.group(1)):
                raise AssertionError("o: complete case leaked into output: %%r" %% ln)

        # p: path-suffix correctness -- missing FF uses _FF.Xn, SS uses _SS.Xn, TT uses _TT.Xn
        for ln in lines:
            m = LINE_RE.match(ln)
            path, pvt, w = m.groups()
            want_suffix = CORNER_TYPE[pvt] + "." + w
            if not path.endswith(want_suffix):
                raise AssertionError("p: %%r path suffix != expected %%r for PVT %%r" %% (path, want_suffix, pvt))

        # q: anti-hardcode -- run on visible A; A output must differ from B output
        A = os.path.join(tmp, "A_sim.saved.total")
        with open(A, "w") as f:
            f.write("\\n".join(A_LINES) + "\\n")
        aout = os.path.join(tmp, "A_more.txt")
        ra = _run(script, [A, aout], tmp)
        if ra.returncode != 0:
            raise AssertionError("q: run on A exited %%d: %%s" %% (ra.returncode, ra.stderr[:200]))
        a_lines = _read_lines(aout)
        if a_lines is None:
            raise AssertionError("q: A output not created")
        if set(a_lines) == set(lines):
            raise AssertionError("q: A output == B output (anti-hardcode failed: script ignores input)")
        if len(a_lines) != len(A_EXPECTED):
            raise AssertionError("q: A output line count %%d != expected %%d (A must yield 3 Golden missing lines)" %% (len(a_lines), len(A_EXPECTED)))

        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "submit.zip"
    print(check(d, os.path.dirname(os.path.abspath(d)) or "."))
''' % {"B_LINES_PY": B_LINES_PY, "A_LINES_PY": A_LINES_PY,
       "B_EXPECTED_PY": B_EXPECTED_PY, "A_EXPECTED_PY": A_EXPECTED_PY}
with open(os.path.join(REF_ROOT, "check.py"), "w") as f:
    f.write(CHECK)

# ============ negatives ============
NEG = os.path.join(REF_ROOT, "negative")

# 1. empty shell
with open(os.path.join(NEG, "fake_empty.py"), "w") as f:
    f.write("#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n")

# 2. only print expected string, write nothing
with open(os.path.join(NEG, "fake_print_expected.py"), "w") as f:
    f.write('''#!/usr/bin/env python3
import sys
print("Total added lines: 7")
sys.exit(0)
''')

# 3. hardcode B's 7 expected lines (ignores input) -> fails q (A==B)
hardcode = "#!/usr/bin/env python3\nimport sys\nrows = [\n"
for ln in B_EXPECTED:
    hardcode += "    %r,\n" % ln
hardcode += "]\nwith open(sys.argv[2],'w') as f:\n    for r in rows: f.write(r+'\\n')\nsys.exit(0)\n"
with open(os.path.join(NEG, "fake_hardcode_B.py"), "w") as f:
    f.write(hardcode)

# 4. wrong count: writes 5 of 7 (drops 2) -> fails f + h-o
with open(os.path.join(NEG, "fake_wrong_count.py"), "w") as f:
    f.write("#!/usr/bin/env python3\nimport sys\nrows=[\n")
    for ln in B_EXPECTED[:5]:
        f.write("    %r,\n" % ln)
    f.write("]\nwith open(sys.argv[2],'w') as fh:\n    for r in rows: fh.write(r+'\\n')\nsys.exit(0)\n")

# 5. dup existing: echo B's own lines as output -> fails g + f + h-o
with open(os.path.join(NEG, "fake_dup_existing.py"), "w") as f:
    f.write('''#!/usr/bin/env python3
import sys
with open(sys.argv[1]) as inp, open(sys.argv[2],'w') as out:
    for ln in inp:
        if ln.strip():
            out.write(ln)
sys.exit(0)
''')

SELFTEST = '''#!/usr/bin/env python3
"""negative_selftest.py -- run all negative stubs against check.py; all must FAIL."""
import os, sys, subprocess, tempfile, shutil, zipfile

PY = sys.executable or "python3"
HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.dirname(HERE)
CHECK = os.path.join(REF, "check.py")

STUBS = ["fake_empty.py", "fake_print_expected.py", "fake_hardcode_B.py",
         "fake_wrong_count.py", "fake_dup_existing.py"]


def _make_zip(stub, tmp):
    zpath = os.path.join(tmp, os.path.basename(stub).replace(".py", "_submit.zip"))
    with zipfile.ZipFile(zpath, "w") as z:
        with open(os.path.join(HERE, stub)) as f:
            z.writestr("sim_saved_corner_complete.py", f.read())
    return zpath


def main():
    fails = []
    for stub in STUBS:
        tmp = tempfile.mkdtemp(prefix="neg_")
        try:
            zpath = _make_zip(stub, tmp)
            r = subprocess.run([PY, CHECK, zpath], cwd=tmp, capture_output=True, text=True, timeout=120)
            out = (r.stdout + r.stderr).strip()
            if r.returncode == 0 and "True" in out and "False" not in out:
                fails.append((stub, "PASSED (must FAIL!) out=%s" % out[:200]))
            else:
                print("[OK] %s correctly FAILED" % stub)
        except Exception as e:
            fails.append((stub, "exception: %s" % e))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    if fails:
        print("[FAIL] negative_selftest: %d stub(s) passed when they should fail:" % len(fails))
        for s, msg in fails:
            print("  - %s: %s" % (s, msg))
        return 1
    print("[PASS] all %d negative stubs correctly fail check()" % len(STUBS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
with open(os.path.join(NEG, "negative_selftest.py"), "w") as f:
    f.write(SELFTEST)

# ============ reference_submit.zip ============
with zipfile.ZipFile(os.path.join(REF_ROOT, "reference_submit.zip"), "w") as z:
    z.write(os.path.join(REF_ROOT, "sim_saved_corner_complete_ref.py"),
            arcname="sim_saved_corner_complete.py")

print("Built", CID)
print("A lines:", len(A_LINES), "A expected missing:", len(A_EXPECTED))
print("B lines:", len(B_LINES), "B expected missing:", len(B_EXPECTED))
print("B_EXPECTED:")
for ln in B_EXPECTED:
    print("  ", ln)
print("A_EXPECTED:")
for ln in A_EXPECTED:
    print("  ", ln)
