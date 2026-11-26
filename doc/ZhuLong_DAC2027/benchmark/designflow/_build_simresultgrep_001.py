#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build EDA-Eval-DesignFlow-SimResultGrep-001 (spice_sim, A-faithful, L1, k=14).

Trace: tzuo @ hfhds201, session 1791448400305_kwiij (49 msgs).
USER#0 verbatim need round: write a `result_grep` CLI script with -result / -path
options to harvest finesim MatrixRun simulation results.
Deliverable: portable python3 CLI script (L1, no EDA tool needed).
"""
import os, sys, json, zipfile, shutil, subprocess, tempfile, time, stat

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-SimResultGrep-001"
A = os.path.join(BASE, "assets", CASE)
R = os.path.join(BASE, "reference", CASE)
os.makedirs(A, exist_ok=True)
os.makedirs(R, exist_ok=True)
os.makedirs(os.path.join(R, "negative"), exist_ok=True)

# ----------------------------------------------------------------------------
# 1. prompt.txt  (USER#0 verbatim, A-faithful)
# ----------------------------------------------------------------------------
PROMPT = (
    "写一个脚本实现仿真路径下到结果抓取，以及所有仿真路径到抓取，脚本放在"
    "/proj/drcpa/V0/simdir/finesim/drcpaF/MatrixRun 路径下，起名叫result_grep，"
    "规则如下1. -result选项 抓取当前path下所有folder内的zzresult*文件，"
    "folder内可能存在多个zzresult*文件，只抓取最新的一个，输出到当前path下的"
    "zzresult_YMD.list文件中，YMD为当前年月日，文件内均为绝对路径 "
    "2. -path 选项，抓取当前path下的所有MatrixRun* folder，输出到allpath_YMD.list文件中，"
    "内容为绝对路径。脚本完成后在/proj/drcpa/V0/simdir/finesim/drcpaF/MatrixRun 下执行测试，"
    "输出结果"
)
with open(os.path.join(A, "prompt.txt"), "w") as f:
    f.write(PROMPT)

# task_brief.md (<=3 lines, delivery interface only, NOT the goal)
with open(os.path.join(A, "task_brief.md"), "w") as f:
    f.write(
        "# 交付接口\n"
        "交付 `outputs/submit.zip`，内含一个可执行的 python3 CLI 脚本 `result_grep`"
        "（接受 `-result` / `-path` 选项，行为见 prompt）。\n"
        "判分时脚本会被解压后在独立的合成测试目录上运行（cwd 即测试根目录），"
        "请确保脚本不依赖 prompt 中提到的真实路径。\n"
    )

# ----------------------------------------------------------------------------
# 2. visible test dir A (for SUT self-test)  -- assets/<CASE>/testdir_A/
# ----------------------------------------------------------------------------
def make_tree(root, spec):
    """spec: list of (relpath, content, mtime_or_None). dirs auto-created."""
    os.makedirs(root, exist_ok=True)
    for rel, content, mt in spec:
        p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            f.write(content)
        if mt is not None:
            os.utime(p, (mt, mt))

# A: 2 folders with zzresult (one single, one multiple), 1 MatrixRun empty,
#    1 non-MatrixRun folder without zzresult, 1 loose file.
TD_A = os.path.join(A, "testdir_A")
if os.path.exists(TD_A):
    shutil.rmtree(TD_A)
make_tree(TD_A, [
    ("MatrixRun_Netlist_Vcap_20260601AM/zzresult_001.lis", "pass\n", 1000),
    ("MatrixRun_MMSIM_20260601AM/zzresult_a.txt", "a-result\n", 1000),
    ("MatrixRun_MMSIM_20260601AM/zzresult_b.txt", "b-result\n", 2000),  # newest
    ("MatrixRun_Other_20260501PM/notes.txt", "nothing\n", 1000),         # no zzresult
    ("scratch/tmp.log", "x\n", 1000),                                     # non-MatrixRun, no zzresult
    ("readme.txt", "hi\n", 1000),
])
# A expected -result: 2 lines (Vcap single, MMSIM newest=zzresult_b.txt); scratch has no zzresult
# A expected -path: 3 MatrixRun* dirs (Vcap, MMSIM, Other)

# ----------------------------------------------------------------------------
# 3. reference script (gold)  -- generalized from trace deliverable
# ----------------------------------------------------------------------------
REF_SCRIPT = r'''#!/usr/bin/env python3
"""
result_grep - 仿真路径下结果抓取工具

用法:
    ./result_grep -result          # 抓取当前path下所有folder内的zzresult*文件(每个folder取最新一个)
    ./result_grep -path            # 抓取当前path下所有MatrixRun* folder的路径

输出:
    -result: zzresult_YYYYMMDD.list  (当前目录, 每行一个绝对路径)
    -path:   allpath_YYYYMMDD.list   (当前目录, 每行一个绝对路径)
"""

import os
import sys
import glob
from datetime import datetime


def get_ymd():
    return datetime.now().strftime("%Y%m%d")


def find_zzresult_files(root_dir):
    result_paths = []
    try:
        entries = os.listdir(root_dir)
    except PermissionError:
        return result_paths
    for entry in sorted(entries):
        folder_path = os.path.join(root_dir, entry)
        if not os.path.isdir(folder_path):
            continue
        zz_files = glob.glob(os.path.join(folder_path, "zzresult*"))
        if not zz_files:
            continue
        if len(zz_files) == 1:
            result_paths.append(os.path.abspath(zz_files[0]))
        else:
            latest = max(zz_files, key=os.path.getmtime)
            result_paths.append(os.path.abspath(latest))
    return result_paths


def find_matrixrun_folders(root_dir):
    matrixrun_paths = []
    try:
        entries = os.listdir(root_dir)
    except PermissionError:
        return matrixrun_paths
    for entry in sorted(entries):
        full_path = os.path.join(root_dir, entry)
        if os.path.isdir(full_path) and entry.startswith("MatrixRun"):
            matrixrun_paths.append(os.path.abspath(full_path))
    return matrixrun_paths


def write_list_file(filepath, paths):
    with open(filepath, "w", encoding="utf-8") as f:
        for p in paths:
            f.write(p + "\n")
    print("[INFO] wrote %d entries to %s" % (len(paths), filepath))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    option = sys.argv[1]
    current_dir = os.getcwd()
    ymd = get_ymd()
    if option == "-result":
        result_files = find_zzresult_files(current_dir)
        outfile = os.path.join(current_dir, "zzresult_%s.list" % ymd)
        write_list_file(outfile, result_files)
    elif option == "-path":
        matrixrun_dirs = find_matrixrun_folders(current_dir)
        outfile = os.path.join(current_dir, "allpath_%s.list" % ymd)
        write_list_file(outfile, matrixrun_dirs)
    else:
        print("[ERROR] unknown option: %s" % option, file=sys.stderr)
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
with open(os.path.join(R, "result_grep_ref.py"), "w") as f:
    f.write(REF_SCRIPT)

# ----------------------------------------------------------------------------
# 4. check.py  (self-contained judge, embeds hidden B + visible A inline)
# ----------------------------------------------------------------------------
CHECK_PY = r'''#!/usr/bin/env python3
"""check.py -- SimResultGrep-001 judge.

Deliverable: submit.zip with a python3 CLI script `result_grep` implementing
two modes (per prompt):
  -result : scan every direct subfolder of CWD, in each find zzresult* files,
            keep only the NEWEST (by mtime) per folder, write their ABSOLUTE
            paths (one per line) to ./zzresult_YYYYMMDD.list
  -path   : scan CWD for MatrixRun* directories, write their ABSOLUTE paths
            (one per line) to ./allpath_YYYYMMDD.list

check() builds a HIDDEN test tree B (and the visible A as anti-hardcode guard)
in an independent temp dir with controlled mtimes, runs the submitted script
there, parses the produced .list files, and asserts each condition.
"""
import os, sys, json, shutil, zipfile, tempfile, subprocess
from datetime import datetime

PY = sys.executable or "python3"
YMD = datetime.now().strftime("%Y%m%d")

# ---- hidden test tree B (embedded) ----
# (reldir, filename, content, mtime)
B_SPEC = [
    ("MatrixRun_Drift_20260927PM", "zzresult_x.log", "drift-ok\n", 1000),
    ("MatrixRun_Heat_20261015AM", "zzresult_1.rpt", "h1\n", 1000),
    ("MatrixRun_Heat_20261015AM", "zzresult_2.rpt", "h2-newest\n", 3000),  # newest
    ("MatrixRun_Heat_20261015AM", "zzresult_3.rpt", "h3\n", 2000),
    ("MatrixRun_Empty_20261020AM", "notes.txt", "n\n", 1000),              # no zzresult
    ("analysis", "zzresult_decoy.txt", "decoy\n", 1000),                    # non-MatrixRun w/ zzresult
    (".", "readme.txt", "hi\n", 1000),
]
# B -result expected: 3 lines, folders-with-zzresult sorted by name:
#   MatrixRun_Drift_..., MatrixRun_Heat_..., analysis   (uppercase M < lowercase a)
#   Heat newest = zzresult_2.rpt
# B -path expected: 3 MatrixRun* dirs sorted: Drift, Empty, Heat
B_RESULT_EXPECTED_FOLDERS = ["MatrixRun_Drift_20260927PM",
                             "MatrixRun_Heat_20261015AM",
                             "analysis"]
B_RESULT_HEAT_NEWEST = "zzresult_2.rpt"
B_PATH_EXPECTED = ["MatrixRun_Drift_20260927PM",
                   "MatrixRun_Empty_20261020AM",
                   "MatrixRun_Heat_20261015AM"]

# ---- visible test tree A (anti-hardcode guard) ----
A_SPEC = [
    ("MatrixRun_Netlist_Vcap_20260601AM", "zzresult_001.lis", "p\n", 1000),
    ("MatrixRun_MMSIM_20260601AM", "zzresult_a.txt", "a\n", 1000),
    ("MatrixRun_MMSIM_20260601AM", "zzresult_b.txt", "b-newest\n", 2000),
    ("MatrixRun_Other_20260501PM", "notes.txt", "n\n", 1000),
    ("scratch", "tmp.log", "x\n", 1000),
]
# A -result expected: 2 lines (Vcap single, MMSIM newest=zzresult_b.txt); scratch no zzresult
A_RESULT_EXPECTED_FOLDERS = ["MatrixRun_MMSIM_20260601AM",
                             "MatrixRun_Netlist_Vcap_20260601AM"]
A_RESULT_MMSIM_NEWEST = "zzresult_b.txt"
A_PATH_EXPECTED = ["MatrixRun_MMSIM_20260601AM",
                   "MatrixRun_Netlist_Vcap_20260601AM",
                   "MatrixRun_Other_20260501PM"]


def _build(root, spec):
    os.makedirs(root, exist_ok=True)
    for d, fn, content, mt in spec:
        sub = os.path.join(root, d) if d != "." else root
        os.makedirs(sub, exist_ok=True)
        p = os.path.join(sub, fn)
        with open(p, "w") as f:
            f.write(content)
        os.utime(p, (mt, mt))


def _extract_script(zip_path, dest):
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        # find the script: prefer result_grep, else first .py at top level
        cand = [n for n in names if os.path.basename(n) == "result_grep"]
        if not cand:
            cand = [n for n in names if n.endswith(".py") and "/" not in n.strip("/")]
        if not cand:
            cand = [n for n in names if n.endswith(".py")]
        if not cand:
            raise AssertionError("a: submit.zip has no python script file")
        z.extract(cand[0], dest)
        return os.path.join(dest, cand[0])


def _run(script, option, cwd):
    return subprocess.run([PY, script, option], cwd=cwd,
                          capture_output=True, text=True, timeout=60)


def _read_list(cwd, name):
    p = os.path.join(cwd, name)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return [ln.rstrip("\n") for ln in f if ln.strip()]


def check(deliverable, workdir):
    tmp = tempfile.mkdtemp(prefix="simresultgrep_chk_")
    try:
        # --- a: zip valid + contains a script ---
        if not os.path.exists(deliverable):
            raise AssertionError("a: deliverable not found")
        script = _extract_script(deliverable, tmp)

        # --- b: script compiles ---
        r = subprocess.run([PY, "-c", "import py_compile,sys; py_compile.compile(sys.argv[1], doraise=True)", script],
                           capture_output=True, text=True)
        if r.returncode != 0:
            raise AssertionError("b: script does not compile: %s" % r.stderr[:200])

        # --- c: no-args exits non-zero ---
        r0 = _run(script, "", tmp)  # empty arg still treated as unknown -> non-zero
        # call with truly no args:
        rn = subprocess.run([PY, script], capture_output=True, text=True)
        if rn.returncode == 0:
            raise AssertionError("c: no-args must exit non-zero")

        # --- d: unknown option exits non-zero ---
        ru = subprocess.run([PY, script, "--bogus"], capture_output=True, text=True)
        if ru.returncode == 0:
            raise AssertionError("d: unknown option must exit non-zero")

        # build B
        B = os.path.join(tmp, "B")
        _build(B, B_SPEC)

        # --- e: -result B exit0 + creates zzresult_YMD.list ---
        re1 = _run(script, "-result", B)
        if re1.returncode != 0:
            raise AssertionError("e: -result on B exited %d: %s" % (re1.returncode, re1.stderr[:200]))
        res_lines = _read_list(B, "zzresult_%s.list" % YMD)
        if res_lines is None:
            raise AssertionError("e: -result did not create zzresult_%s.list" % YMD)

        # --- f: -result B has exactly 3 lines (folders with zzresult) ---
        if len(res_lines) != 3:
            raise AssertionError("f: -result B expected 3 lines, got %d: %s" % (len(res_lines), res_lines))

        # --- g: all lines are absolute paths ---
        if not all(os.path.isabs(ln) for ln in res_lines):
            raise AssertionError("g: -result B has non-absolute paths: %s" % res_lines)

        # --- h: Heat folder newest = zzresult_2.rpt (mtime-based selection) ---
        heat_line = [ln for ln in res_lines if "MatrixRun_Heat_20261015AM" in ln]
        if len(heat_line) != 1:
            raise AssertionError("h: Heat folder not exactly once in -result B: %s" % heat_line)
        if not heat_line[0].endswith("zzresult_2.rpt"):
            raise AssertionError("h: Heat newest must be zzresult_2.rpt, got %s" % heat_line[0])

        # --- i: Empty folder (no zzresult) excluded ---
        if any("MatrixRun_Empty_20261020AM" in ln for ln in res_lines):
            raise AssertionError("i: MatrixRun_Empty (no zzresult) must not appear in -result B")

        # --- j: non-MatrixRun 'analysis' folder with zzresult included ---
        ana = [ln for ln in res_lines if ln.endswith("analysis/zzresult_decoy.txt") or "/analysis/zzresult_decoy.txt" in ln]
        if len(ana) != 1:
            raise AssertionError("j: analysis/zzresult_decoy.txt (non-MatrixRun w/ zzresult) must appear once in -result B: %s" % ana)

        # --- k: -path B exit0 + creates allpath_YMD.list ---
        rp1 = _run(script, "-path", B)
        if rp1.returncode != 0:
            raise AssertionError("k: -path on B exited %d: %s" % (rp1.returncode, rp1.stderr[:200]))
        path_lines = _read_list(B, "allpath_%s.list" % YMD)
        if path_lines is None:
            raise AssertionError("k: -path did not create allpath_%s.list" % YMD)

        # --- l: -path B lists exactly the 3 MatrixRun* dirs ---
        path_basenames = sorted(os.path.basename(ln.rstrip("/")) for ln in path_lines)
        if path_basenames != sorted(B_PATH_EXPECTED):
            raise AssertionError("l: -path B expected %s, got %s" % (sorted(B_PATH_EXPECTED), path_basenames))

        # --- m: -path B excludes non-MatrixRun (analysis, readme.txt) ---
        if any("analysis" in ln for ln in path_lines):
            raise AssertionError("m: non-MatrixRun 'analysis' must not appear in -path B")
        if any(ln.endswith("readme.txt") for ln in path_lines):
            raise AssertionError("m: loose file readme.txt must not appear in -path B")

        # --- n: cross-input guard on visible A (anti-hardcode) ---
        Adir = os.path.join(tmp, "A")
        _build(Adir, A_SPEC)
        ra = _run(script, "-result", Adir)
        if ra.returncode != 0:
            raise AssertionError("n: -result on A exited %d" % ra.returncode)
        a_lines = _read_list(Adir, "zzresult_%s.list" % YMD)
        if a_lines is None or len(a_lines) != 2:
            raise AssertionError("n: -result A expected 2 lines, got %s" % a_lines)
        a_bases = sorted(os.path.basename(os.path.dirname(ln)) for ln in a_lines)
        if a_bases != sorted(A_RESULT_EXPECTED_FOLDERS):
            raise AssertionError("n: -result A folders expected %s, got %s" % (sorted(A_RESULT_EXPECTED_FOLDERS), a_bases))
        mmsim = [ln for ln in a_lines if "MatrixRun_MMSIM_20260601AM" in ln]
        if len(mmsim) != 1 or not mmsim[0].endswith(A_RESULT_MMSIM_NEWEST):
            raise AssertionError("n: A MMSIM newest must be %s, got %s" % (A_RESULT_MMSIM_NEWEST, mmsim))
        # A != B (different folder counts 2 vs 3)
        if len(a_lines) == len(res_lines):
            raise AssertionError("n: A and B -result must differ in line count (anti-hardcode)")

        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "submit.zip"
    print(check(d, os.path.dirname(os.path.abspath(d)) or "."))
'''
with open(os.path.join(R, "check.py"), "w") as f:
    f.write(CHECK_PY)

# ----------------------------------------------------------------------------
# 5. reference_submit.zip  (ref script named `result_grep`)
# ----------------------------------------------------------------------------
ref_zip = os.path.join(R, "reference_submit.zip")
with zipfile.ZipFile(ref_zip, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("result_grep", REF_SCRIPT)

# ----------------------------------------------------------------------------
# 6. negatives  (5 stubs + selftest)
# ----------------------------------------------------------------------------
NEG = os.path.join(R, "negative")
stubs = {
    "fake_empty.py": "#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n",
    "fake_print_expected.py": (
        "#!/usr/bin/env python3\nimport sys\n# just print the expected files, no scanning\n"
        "print('MatrixRun_Drift_20260927PM/zzresult_x.log')\nsys.exit(0)\n"
    ),
    "fake_hardcode_A.py": (
        "#!/usr/bin/env python3\nimport sys,os\n# hardcode the A answer (wrong on B)\n"
        "if sys.argv[1:]==['-result']:\n"
        "  open('zzresult_'+__import__('datetime').datetime.now().strftime('%Y%m%d')+'.list','w').write("
        "'MatrixRun_MMSIM_20260601AM/zzresult_b.txt\\nMatrixRun_Netlist_Vcap_20260601AM/zzresult_001.lis\\n')\n"
        "elif sys.argv[1:]==['-path']:\n"
        "  open('allpath_'+__import__('datetime').datetime.now().strftime('%Y%m%d')+'.list','w').write("
        "'MatrixRun_MMSIM_20260601AM\\nMatrixRun_Netlist_Vcap_20260601AM\\nMatrixRun_Other_20260501PM\\n')\n"
    ),
    "fake_core_deleted.py": (
        "#!/usr/bin/env python3\nimport sys,os,glob\n# missing the 'newest per folder' logic + missing -path MatrixRun filter\n"
        "opt=sys.argv[1] if len(sys.argv)>1 else ''\n"
        "if opt=='-result':\n"
        "  out=[]\n"
        "  for e in sorted(os.listdir('.')):\n"
        "    d=os.path.join('.',e)\n"
        "    if os.path.isdir(d):\n"
        "      for f in glob.glob(os.path.join(d,'zzresult*')): out.append(os.path.abspath(f))  # ALL not newest\n"
        "  open('zzresult_'+__import__('datetime').datetime.now().strftime('%Y%m%d')+'.list','w').write('\\n'.join(out)+'\\n')\n"
        "elif opt=='-path':\n"
        "  out=[os.path.abspath(os.path.join('.',e)) for e in sorted(os.listdir('.')) if os.path.isdir(os.path.join('.',e))]  # ALL dirs not MatrixRun\n"
        "  open('allpath_'+__import__('datetime').datetime.now().strftime('%Y%m%d')+'.list','w').write('\\n'.join(out)+'\\n')\n"
        "else:\n  sys.exit(1)\n"
    ),
    "fake_no_abs.py": (
        "#!/usr/bin/env python3\nimport sys,os,glob\n# correct logic but writes relative paths (violates absolute-path spec)\n"
        "opt=sys.argv[1] if len(sys.argv)>1 else ''\n"
        "if opt=='-result':\n"
        "  out=[]\n"
        "  for e in sorted(os.listdir('.')):\n"
        "    d=os.path.join('.',e)\n"
        "    if os.path.isdir(d):\n"
        "      zs=glob.glob(os.path.join(d,'zzresult*'))\n"
        "      if zs: out.append(zs[0] if len(zs)==1 else max(zs,key=os.path.getmtime))  # relative!\n"
        "  open('zzresult_'+__import__('datetime').datetime.now().strftime('%Y%m%d')+'.list','w').write('\\n'.join(out)+'\\n')\n"
        "elif opt=='-path':\n"
        "  out=[os.path.join('.',e) for e in sorted(os.listdir('.')) if os.path.isdir(os.path.join('.',e)) and e.startswith('MatrixRun')]\n"
        "  open('allpath_'+__import__('datetime').datetime.now().strftime('%Y%m%d')+'.list','w').write('\\n'.join(out)+'\\n')\n"
        "else:\n  sys.exit(1)\n"
    ),
}
for name, body in stubs.items():
    with open(os.path.join(NEG, name), "w") as f:
        f.write(body)
    zname = name.replace(".py", "_submit.zip")
    with zipfile.ZipFile(os.path.join(NEG, zname), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("result_grep", body)

SELFTEST = r'''#!/usr/bin/env python3
"""negative_selftest.py -- all 5 stubs must FAIL check()."""
import os, sys, shutil, tempfile, zipfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import check

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEG = os.path.join(R, "negative")
stubs = ["fake_empty.py", "fake_print_expected.py", "fake_hardcode_A.py",
         "fake_core_deleted.py", "fake_no_abs.py"]
fails = []
for s in stubs:
    zpath = os.path.join(NEG, s.replace(".py", "_submit.zip"))
    tmp = tempfile.mkdtemp()
    try:
        ok = check.check(zpath, tmp)
        if ok:
            fails.append((s, "PASS (expected FAIL)"))
    except Exception as e:
        pass  # expected FAIL
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
if fails:
    print("NEGATIVE SELFTEST FAILED:")
    for s, why in fails:
        print("  ", s, "->", why)
    sys.exit(1)
print("NEGATIVE SELFTEST PASS: all 5 stubs correctly FAIL")
'''
with open(os.path.join(NEG, "negative_selftest.py"), "w") as f:
    f.write(SELFTEST)

print("Build complete:", CASE)
print(" assets:", os.listdir(A))
print(" reference:", os.listdir(R))
