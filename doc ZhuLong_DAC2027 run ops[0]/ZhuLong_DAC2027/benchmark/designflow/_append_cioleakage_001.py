#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator for EDA-Eval-DesignFlow-CioLeakageExtract-001 (shard B, spice_sim).
Builds assets A, hidden B1/B2, reference solution, check.py, negatives.

Trace source: 1794299323217_5oub3 (clarawu@hfeg0plg106, mc=30).
U1 (clean produce-task): 从 cio.ma0 + leakage.mt0 提取 cio leakage 信息整理成表格.
U3 refinement: 只要保留 CIO leakage 汇总表，不要 alter 列和 temper 列.
Gold standard = cio_leakage_result.csv joined on alter#, columns cdq_10g,i_leak_pu,i_leak_pd.
"""
import os, json, random, zipfile, io, base64, hashlib, subprocess, sys, shutil, tempfile

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "CioLeakageExtract-001"
A_DIR = os.path.join(BENCH, "assets", CASE)
HID_DIR = os.path.join(A_DIR, "hidden")
REF_DIR = os.path.join(BENCH, "reference", CASE)
NEG_DIR = os.path.join(REF_DIR, "negative")

for d in (A_DIR, HID_DIR, REF_DIR, NEG_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------- data generation ----------------
def fmt(v):
    return "% .5e" % v

def gen_ma0(path, alters, cdq_base, temp, seed):
    rng = random.Random(seed)
    lines = []
    lines.append("$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=0")
    lines.append(".TITLE 'sim set environment'")
    lines.append("        cdq_10g         temper         alter#")
    for a in alters:
        cdq = cdq_base * (1.0 + 0.05 * rng.gauss(0, 1))
        lines.append("   %s   %s   %s" % (fmt(cdq), fmt(temp), fmt(float(a))))
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

def gen_mt0(path, alters, pu_base, pd_base, temp, seed, shuffle=False):
    rng = random.Random(seed)
    rows = []
    for a in alters:
        pu = pu_base * (1.0 + 0.05 * rng.gauss(0, 1))
        pd = pd_base * (1.0 + 0.05 * rng.gauss(0, 1))
        rows.append((pu, pd, temp, float(a)))
    if shuffle:
        rng.shuffle(rows)
    lines = []
    lines.append("$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=0")
    lines.append(".TITLE 'sim set environment'")
    lines.append("      i_leak_pu      i_leak_pd         temper         alter#")
    for pu, pd, t, a in rows:
        lines.append("   %s   %s   %s   %s" % (fmt(pu), fmt(pd), fmt(t), fmt(a)))
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")

# Asset A (visible): 5 alters, temp=25 for cio, temp=110 for leakage (different temps, join on alter#)
A_alters = [1, 2, 3, 4, 5]
gen_ma0(os.path.join(A_DIR, "cio.ma0"), A_alters, cdq_base=1.96e-13, temp=25.0, seed=42)
gen_mt0(os.path.join(A_DIR, "leakage.mt0"), A_alters, pu_base=6.09e-04, pd_base=2.08e-05, temp=110.0, seed=43, shuffle=True)

# Hidden B1: 7 alters, different values, leakage shuffled (force join-by-alter#)
B1_alters = [1, 2, 3, 4, 5, 6, 7]
gen_ma0(os.path.join(HID_DIR, "hidden_b1_cio.ma0"), B1_alters, cdq_base=2.31e-13, temp=85.0, seed=137)
gen_mt0(os.path.join(HID_DIR, "hidden_b1_leakage.mt0"), B1_alters, pu_base=5.77e-04, pd_base=1.94e-05, temp=-40.0, seed=9913, shuffle=True)

# Hidden B2: 4 alters, different values (reverse-hardcode guard), leakage shuffled
B2_alters = [1, 2, 3, 4]
gen_ma0(os.path.join(HID_DIR, "hidden_b2_cio.ma0"), B2_alters, cdq_base=1.42e-13, temp=-40.0, seed=99)
gen_mt0(os.path.join(HID_DIR, "hidden_b2_leakage.mt0"), B2_alters, pu_base=7.21e-04, pd_base=2.55e-05, temp=125.0, seed=2024, shuffle=True)

# hidden manifest
manifest = {
    "B1": {"cio": "hidden_b1_cio.ma0", "leakage": "hidden_b1_leakage.mt0", "alters": B1_alters},
    "B2": {"cio": "hidden_b2_cio.ma0", "leakage": "hidden_b2_leakage.mt0", "alters": B2_alters},
}
with open(os.path.join(HID_DIR, "hidden_manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

# ---------------- format spec + task brief ----------------
with open(os.path.join(A_DIR, "output_format_spec.txt"), "w") as f:
    f.write("""# FineSim / HSPICE 测量输出文件格式 ($DATA1)

文件 (.ma0 / .mt0) 是 FineSim/Hspice 的 .measure 输出，纯文本，结构：

    第 1 行: $DATA1 SOURCE='FineSimPro' VERSION='...' PARAM_COUNT=0
    第 2 行: .TITLE '<title string>'
    第 3 行: 列名行（空白分隔的 column names），例如:
                 cdq_10g         temper         alter#
    第 4+ 行: 数据行（空白分隔的浮点数，科学计数法 1.9605e-13），每行对应一次 .alter

## 输入文件列定义

- cio.ma0  列: cdq_10g , temper , alter#
- leakage.mt0 列: i_leak_pu , i_leak_pd , temper , alter#

两个文件通过 `alter#` 列关联（同一次 .alter 的测量结果）。
注意：两文件的 `temper` 列可能取值不同（cio 与 leakage 来自不同温度点的仿真），
所以关联键只能是 `alter#`，不能用 temper。两文件的 alter# 顺序可能不同（leakage.mt0 行序被打乱）。

## 输出 CSV 格式

- 列头（固定，逗号分隔，无空格）: cdq_10g,i_leak_pu,i_leak_pd
- 按 alter# 升序，每个 alter# 一行
- 数值用 5 位有效数字科学计数法 (如 1.96050e-13) 或等值浮点
- 不输出 alter# 列、不输出 temper 列（用户要求：只要 CIO leakage 汇总表，不要 alter 列和 temper 列）
- 文件末尾允许单个换行
""")

with open(os.path.join(A_DIR, "task_brief.md"), "w") as f:
    f.write("""# 交付接口

交付件：`outputs/submit.zip`，内含 `cio_leakage_extract.py`（独立可运行 Python3 脚本，纯标准库）。

命令行接口：
```
python3 cio_leakage_extract.py <cio.ma0> <leakage.mt0> <out_csv>
```

- `<cio.ma0>`：FineSim 测量输出文件（列含 cdq_10g, temper, alter#）
- `<leakage.mt0>`：FineSim 测量输出文件（列含 i_leak_pu, i_leak_pd, temper, alter#）
- `<out_csv>`：输出 CSV 路径

输出 CSV 列头固定为 `cdq_10g,i_leak_pu,i_leak_pd`，按 alter# 升序排列，每个 alter# 一行；
不输出 alter# 与 temper 列。详见 output_format_spec.txt。
""")

# ---------------- reference solution ----------------
REF_SRC = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reference solution for CioLeakageExtract-001.
Parse two FineSim $DATA1 measure files, join on alter#, output CSV
with columns cdq_10g,i_leak_pu,i_leak_pd (drop alter# and temper).
"""
import sys, re

def parse_measure_file(path):
    """Parse a FineSim/Hspice $DATA1 measure file.
    Returns (headers, rows) where headers is list of column names,
    rows is list of dict {col: float_value}.
    """
    with open(path) as f:
        raw = f.read()
    lines = [ln for ln in raw.split("\n") if ln.strip() != ""]
    headers = None
    rows = []
    for ln in lines:
        s = ln.strip()
        if s.startswith("$DATA1") or s.startswith(".TITLE"):
            continue
        toks = s.split()
        # header line: all tokens are identifiers (no scientific-notation floats)
        is_header = all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_#]*", t) for t in toks) and any(
            re.search(r"[A-Za-z]", t) for t in toks)
        if is_header and headers is None:
            headers = toks
            continue
        if headers is None:
            continue
        # data row: tokens parse as float
        try:
            vals = [float(t) for t in toks]
        except ValueError:
            continue
        if len(vals) != len(headers):
            continue
        rows.append(dict(zip(headers, vals)))
    return headers, rows

def main():
    if len(sys.argv) != 4:
        print("usage: cio_leakage_extract.py <cio.ma0> <leakage.mt0> <out_csv>")
        sys.exit(2)
    cio_path, leak_path, out_csv = sys.argv[1:4]
    _, cio_rows = parse_measure_file(cio_path)
    _, leak_rows = parse_measure_file(leak_path)
    # index by alter#
    cio_by_alter = {r["alter#"]: r["cdq_10g"] for r in cio_rows}
    leak_by_alter = {r["alter#"]: (r["i_leak_pu"], r["i_leak_pd"]) for r in leak_rows}
    alters = sorted(set(cio_by_alter) & set(leak_by_alter))
    out_lines = ["cdq_10g,i_leak_pu,i_leak_pd"]
    for a in alters:
        cdq = cio_by_alter[a]
        pu, pd = leak_by_alter[a]
        out_lines.append("%.5e,%.5e,%.5e" % (cdq, pu, pd))
    with open(out_csv, "w") as f:
        f.write("\n".join(out_lines) + "\n")

if __name__ == "__main__":
    main()
'''
with open(os.path.join(REF_DIR, "cio_leakage_extract_ref.py"), "w") as f:
    f.write(REF_SRC)

# ---------------- check.py ----------------
CHECK_SRC = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py for EDA-Eval-DesignFlow-CioLeakageExtract-001.

Two-arg design_flow contract:
    from check import check
    check(deliverable, workdir)   # deliverable = submit.zip path, workdir = temp dir

Unzips submit.zip, finds cio_leakage_extract.py, runs it on hidden B1 and B2
(parse FineSim .ma0/.mt0, join on alter#, output CSV), and asserts >=8 conditions.
"""
import os, sys, re, json, zipfile, subprocess, tempfile, shutil, hashlib

HIDDEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "CioLeakageExtract-001", "hidden")

def _parse_measure_file(path):
    with open(path) as f:
        raw = f.read()
    lines = [ln for ln in raw.split("\n") if ln.strip() != ""]
    headers = None
    rows = []
    for ln in lines:
        s = ln.strip()
        if s.startswith("$DATA1") or s.startswith(".TITLE"):
            continue
        toks = s.split()
        is_header = all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_#]*", t) for t in toks) and any(
            re.search(r"[A-Za-z]", t) for t in toks)
        if is_header and headers is None:
            headers = toks
            continue
        if headers is None:
            continue
        try:
            vals = [float(t) for t in toks]
        except ValueError:
            continue
        if len(vals) != len(headers):
            continue
        rows.append(dict(zip(headers, vals)))
    return headers, rows

def _expected(cio_path, leak_path):
    """Independently recompute the expected CSV content."""
    _, cio_rows = _parse_measure_file(cio_path)
    _, leak_rows = _parse_measure_file(leak_path)
    cio_by = {r["alter#"]: r["cdq_10g"] for r in cio_rows}
    leak_by = {r["alter#"]: (r["i_leak_pu"], r["i_leak_pd"]) for r in leak_rows}
    alters = sorted(set(cio_by) & set(leak_by))
    lines = ["cdq_10g,i_leak_pu,i_leak_pd"]
    for a in alters:
        cdq = cio_by[a]; pu, pd = leak_by[a]
        lines.append("%.5e,%.5e,%.5e" % (cdq, pu, pd))
    return "\n".join(lines) + "\n", len(alters)

def _fail(msg):
    raise AssertionError(msg)

def _run(script, cio, leak, out, cwd):
    return subprocess.run([sys.executable, script, cio, leak, out],
                          capture_output=True, text=True, cwd=cwd, timeout=120)

def check(deliverable, workdir):
    if not os.path.exists(deliverable):
        _fail("deliverable not found: %s" % deliverable)
    tmp = tempfile.mkdtemp(prefix="chk_cioleak_", dir=workdir if os.path.isdir(workdir) else None)
    try:
        with zipfile.ZipFile(deliverable) as z:
            z.extractall(tmp)
        # a. zip contains cio_leakage_extract.py
        script = os.path.join(tmp, "cio_leakage_extract.py")
        if not os.path.isfile(script):
            _fail("a: cio_leakage_extract.py not in zip")
        # b. py_compile succeeds
        r = subprocess.run([sys.executable, "-m", "py_compile", script], capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            _fail("b: py_compile failed: %s" % r.stderr[:300])
        manifest = json.load(open(os.path.join(HIDDEN_DIR, "hidden_manifest.json")))
        # ---- B1 ----
        b1 = manifest["B1"]
        cio1 = os.path.join(HIDDEN_DIR, b1["cio"])
        leak1 = os.path.join(HIDDEN_DIR, b1["leakage"])
        out1 = os.path.join(tmp, "out_b1.csv")
        rr = _run(script, cio1, leak1, out1, tmp)
        # c. B1 exit 0
        if rr.returncode != 0:
            _fail("c: B1 exit=%d stderr=%s" % (rr.returncode, rr.stderr[:300]))
        # d. B1 out csv exists
        if not os.path.isfile(out1):
            _fail("d: B1 out csv not produced")
        got1 = open(out1).read()
        exp1, n1 = _expected(cio1, leak1)
        # e. B1 header correct (no alter/temper)
        hdr = got1.splitlines()[0] if got1 else ""
        if hdr.strip() != "cdq_10g,i_leak_pu,i_leak_pd":
            _fail("e: B1 header wrong: %r" % hdr)
        # f. B1 row count == n1
        got_rows = [ln for ln in got1.splitlines()[1:] if ln.strip() != ""]
        if len(got_rows) != n1:
            _fail("f: B1 row count %d != %d" % (len(got_rows), n1))
        # g. B1 cdq values match cio.ma0 (parsed independently)
        _, cio_rows1 = _parse_measure_file(cio1)
        cio_by1 = {r["alter#"]: r["cdq_10g"] for r in cio_rows1}
        _, leak_rows1 = _parse_measure_file(leak1)
        leak_by1 = {r["alter#"]: (r["i_leak_pu"], r["i_leak_pd"]) for r in leak_rows1}
        for ln in got_rows:
            parts = ln.split(",")
            if len(parts) != 3:
                _fail("g: B1 row not 3 cols: %r" % ln)
            try:
                cdq_got = float(parts[0]); pu_got = float(parts[1]); pd_got = float(parts[2])
            except ValueError:
                _fail("g: B1 row non-float: %r" % ln)
            matched = any(abs(cio_by1[a] - cdq_got) < 1e-18 for a in cio_by1)
            if not matched:
                _fail("g: B1 cdq %g not found in cio.ma0" % cdq_got)
        # h. B1 leak values match leakage.mt0
        for ln in got_rows:
            parts = ln.split(",")
            pu_got = float(parts[1]); pd_got = float(parts[2])
            m1 = any(abs(leak_by1[a][0] - pu_got) < 1e-18 for a in leak_by1)
            m2 = any(abs(leak_by1[a][1] - pd_got) < 1e-18 for a in leak_by1)
            if not (m1 and m2):
                _fail("h: B1 leak pu=%g pd=%g not in leakage.mt0" % (pu_got, pd_got))
        # i. B1 join correctness: each row's cdq+pu+pd correspond to the same alter#
        alters_sorted = sorted(set(cio_by1) & set(leak_by1))
        for idx, ln in enumerate(got_rows):
            parts = ln.split(",")
            cdq_got = float(parts[0]); pu_got = float(parts[1]); pd_got = float(parts[2])
            a = alters_sorted[idx]
            if abs(cio_by1[a] - cdq_got) >= 1e-18 or abs(leak_by1[a][0] - pu_got) >= 1e-18 or abs(leak_by1[a][1] - pd_got) >= 1e-18:
                _fail("i: B1 row %d join mismatch for alter# %g" % (idx, a))
        # ---- B2 (reverse-hardcode guard) ----
        b2 = manifest["B2"]
        cio2 = os.path.join(HIDDEN_DIR, b2["cio"])
        leak2 = os.path.join(HIDDEN_DIR, b2["leakage"])
        out2 = os.path.join(tmp, "out_b2.csv")
        rr2 = _run(script, cio2, leak2, out2, tmp)
        # j. B2 exit 0 + header + row count + values match B2 (not B1)
        if rr2.returncode != 0:
            _fail("j: B2 exit=%d" % rr2.returncode)
        if not os.path.isfile(out2):
            _fail("j: B2 out csv not produced")
        got2 = open(out2).read()
        exp2, n2 = _expected(cio2, leak2)
        hdr2 = got2.splitlines()[0] if got2 else ""
        if hdr2.strip() != "cdq_10g,i_leak_pu,i_leak_pd":
            _fail("j: B2 header wrong: %r" % hdr2)
        got_rows2 = [ln for ln in got2.splitlines()[1:] if ln.strip() != ""]
        if len(got_rows2) != n2:
            _fail("j: B2 row count %d != %d" % (len(got_rows2), n2))
        if got2.strip() != exp2.strip():
            _fail("j: B2 content mismatch (reverse-hardcode guard): expected %r got %r" % (exp2[:120], got2[:120]))
        if got2.strip() == exp1.strip():
            _fail("j: B2 output equals B1 expected (hardcoded)")
        # k. determinism: 3x run md5 consistent
        md5s = []
        for _ in range(3):
            outd = os.path.join(tmp, "out_det.csv")
            _run(script, cio1, leak1, outd, tmp)
            md5s.append(hashlib.md5(open(outd, "rb").read()).hexdigest())
        if len(set(md5s)) != 1:
            _fail("k: non-deterministic output across 3 runs: %s" % md5s)
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        print(check(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "."))
'''
with open(os.path.join(REF_DIR, "check.py"), "w") as f:
    f.write(CHECK_SRC)

# ---------------- negatives ----------------
negatives = {
    "naive_empty.py": "# naive empty\nimport sys\nsys.exit(0)\n",
    "hardcoded_a.py": (
        "# hardcoded to B1 values (will fail on B2)\n"
        "import sys\n"
        "out=sys.argv[3]\n"
        "open(out,'w').write('cdq_10g,i_leak_pu,i_leak_pd\\n'\n"
        "+ '2.31000e-13,5.77000e-04,1.94000e-05\\n'*7)\n"
    ),
    "no_join.py": (
        "# outputs rows without join-by-alter (wrong pairing)\n"
        "import sys,re\n"
        "def parse(p):\n"
        "    H=None;R=[]\n"
        "    for ln in open(p):\n"
        "        s=ln.strip()\n"
        "        if s.startswith('$DATA1') or s.startswith('.TITLE') or not s: continue\n"
        "        t=s.split()\n"
        "        if H is None and all(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_#]*',x) for x in t):\n"
        "            H=t;continue\n"
        "        if H:\n"
        "            try: v=[float(x) for x in t]\n"
        "            except: continue\n"
        "            if len(v)==len(H): R.append(dict(zip(H,v)))\n"
        "    return H,R\n"
        "c=parse(sys.argv[1]); l=parse(sys.argv[2])\n"
        "# zip by row position (WRONG: must join by alter#)\n"
        "lines=['cdq_10g,i_leak_pu,i_leak_pd']\n"
        "for i in range(min(len(c[1]),len(l[1]))):\n"
        "    lines.append('%.5e,%.5e,%.5e'%(c[1][i]['cdq_10g'],l[1][i]['i_leak_pu'],l[1][i]['i_leak_pd']))\n"
        "open(sys.argv[3],'w').write('\\n'.join(lines)+'\\n')\n"
    ),
    "empty_shell.py": (
        "# empty shell: just exit 0, no output\nimport sys\nsys.exit(0)\n"
    ),
    "only_print.py": (
        "# only prints to stdout, no file\nimport sys\nprint('cdq_10g,i_leak_pu,i_leak_pd')\nsys.exit(0)\n"
    ),
    "ref_core_deleted.py": (
        "# ref with join logic deleted (outputs only cdq, leak zeros)\n"
        "import sys,re\n"
        "def parse(p):\n"
        "    H=None;R=[]\n"
        "    for ln in open(p):\n"
        "        s=ln.strip()\n"
        "        if s.startswith('$DATA1') or s.startswith('.TITLE') or not s: continue\n"
        "        t=s.split()\n"
        "        if H is None and all(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_#]*',x) for x in t):\n"
        "            H=t;continue\n"
        "        if H:\n"
        "            try: v=[float(x) for x in t]\n"
        "            except: continue\n"
        "            if len(v)==len(H): R.append(dict(zip(H,v)))\n"
        "    return H,R\n"
        "c=parse(sys.argv[1])\n"
        "lines=['cdq_10g,i_leak_pu,i_leak_pd']\n"
        "for r in sorted(c[1],key=lambda x:x['alter#']):\n"
        "    lines.append('%.5e,0.0,0.0'%r['cdq_10g'])\n"
        "open(sys.argv[3],'w').write('\\n'.join(lines)+'\\n')\n"
    ),
}
for nm, src in negatives.items():
    with open(os.path.join(NEG_DIR, nm), "w") as f:
        f.write(src)

# negative_selftest.py
NEG_TEST = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""negative_selftest.py — every negative must FAIL check().
Run: python3 negative_selftest.py
"""
import os, sys, json, zipfile, tempfile, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "check.py")
NEG = os.path.join(HERE, "negative")
REF = os.path.join(HERE, "cio_leakage_extract_ref.py")

def _zip_script(script_path):
    z = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    with zipfile.ZipFile(z, "w") as zf:
        zf.write(script_path, arcname="cio_leakage_extract.py")
    z.close()
    return z.name

def run_check(script_path):
    zp = _zip_script(script_path)
    try:
        r = subprocess.run([sys.executable, "-c",
                            "import sys; sys.path.insert(0,%r); from check import check; print(check(%r, %r))" % (HERE, zp, HERE)],
                           capture_output=True, text=True, timeout=180)
        return r.returncode, r.stdout, r.stderr
    finally:
        os.unlink(zp)

def main():
    results = {}
    for nm in sorted(os.listdir(NEG)):
        if not nm.endswith(".py"):
            continue
        path = os.path.join(NEG, nm)
        rc, out, err = run_check(path)
        # we expect FAIL (exception -> rc!=0 or "False" in out)
        failed = (rc != 0) or ("False" in out)
        results[nm] = failed
        print("%s : %s" % (nm, "FAIL(ok)" if failed else "PASS(BAD!)"))
    # ref must PASS
    rc, out, err = run_check(REF)
    ref_pass = (rc == 0) and ("True" in out)
    print("REF : %s" % ("PASS(ok)" if ref_pass else "FAIL(BAD!)"))
    neg_ok = all(results.values())
    print("NEG_RC=%d" % (1 if (neg_ok and ref_pass) else 0))
    sys.exit(0 if (neg_ok and ref_pass) else 1)

if __name__ == "__main__":
    main()
'''
with open(os.path.join(REF_DIR, "negative_selftest.py"), "w") as f:
    f.write(NEG_TEST)

print("assets + hidden + reference + check + negatives written")
