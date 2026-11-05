#!/usr/bin/env python3
"""Build assets + reference + check + negatives for EDA-Eval-DesignFlow-VmMhlAlterStats-001.

A-faithful trace: 1793244287787_11tjs (stephens @ hfeg0pkn002, mc=139).
User literal: "读取这个路径下的.csv文件，分析每个.alter下VMHL和VMLH的min值和max值"
Sub-skill: FineSim Monte-Carlo measure CSV per-alter vmlh/vmhl min/max/mean.
L1-boundary (offline CSV parse, no EDA tool).
"""
import os, csv, zipfile, random, hashlib, json

CASE_ID = "EDA-Eval-DesignFlow-VmMhlAlterStats-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
AST_DIR = os.path.join(BENCH, "assets", CASE_ID)
REF_DIR = os.path.join(BENCH, "reference", CASE_ID)

# ---------------- deterministic CSV generation ----------------
def gen_csv(n_alters, n_rows, col_order, seed, vbase):
    rng = random.Random(seed)
    lines = []
    lines.append("$蒙特卡洛分析输出 (FineSimPro R-2023.12)")
    lines.append(".version 1.0")
    lines.append(".mc_index mc_run alter# vmlh vmhl vmlh_lv vmhl_lv temper ramp run")
    lines.append("$ 收敛: sigma=2")
    lines.append(",".join(col_order))
    gt = {}
    for alt in range(1, n_alters + 1):
        vmlhs, vmhls = [], []
        for r in range(1, n_rows + 1):
            mc_idx = (alt - 1) * n_rows + r
            vmlh = round(vbase[0] + 0.02 * alt + rng.uniform(-0.04, 0.04), 6)
            vmhl = round(vbase[1] + 0.015 * alt + rng.uniform(-0.05, 0.05), 6)
            vmlh_lv = round(vmlh - 0.003, 6)
            vmhl_lv = round(vmhl - 0.002, 6)
            temper = [-40, 25, 85, 125][(alt - 1) % 4]
            ramp = round(rng.uniform(0.1, 0.9), 6)
            row = {"mc_index": mc_idx, "alter#": alt, "run": r, "vmlh": vmlh,
                   "vmhl": vmhl, "vmlh_lv": vmlh_lv, "vmhl_lv": vmhl_lv,
                   "temper": temper, "ramp": ramp}
            lines.append(",".join(str(row[c]) for c in col_order))
            vmlhs.append(vmlh); vmhls.append(vmhl)
        gt[alt] = {"N": n_rows, "vmlh_min": min(vmlhs), "vmlh_max": max(vmlhs),
                   "vmlh_mean": round(sum(vmlhs) / n_rows, 6),
                   "vmhl_min": min(vmhls), "vmhl_max": max(vmhls),
                   "vmhl_mean": round(sum(vmhls) / n_rows, 6)}
    return "\n".join(lines) + "\n", gt

A_COLS = ["mc_index", "alter#", "run", "vmlh", "vmhl", "vmlh_lv", "vmhl_lv", "temper"]
A_TEXT, GT_A = gen_csv(6, 120, A_COLS, seed=1011, vbase=(0.30, 0.46))
B_COLS = ["mc_index", "run", "alter#", "ramp", "vmlh", "vmlh_lv", "vmhl", "vmhl_lv", "temper"]
B_TEXT, GT_B = gen_csv(8, 80, B_COLS, seed=2027, vbase=(0.34, 0.50))

# ---------------- reference solution ----------------
REF_PY = '''#!/usr/bin/env python3
"""analyze_vm.py - FineSim Monte-Carlo measure CSV per-alter vmlh/vmhl statistics."""
import csv, sys


def _read_csv(path):
    rows = []
    with open(path, "r", errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip("\\n")
            if not line or line.startswith("$") or line.startswith("."):
                continue
            rows.append(line)
    if not rows:
        raise ValueError("no data rows found")
    header = [c.strip() for c in rows[0].split(",")]
    idx = {name: i for i, name in enumerate(header)}
    for need in ("alter#", "vmlh", "vmhl"):
        if need not in idx:
            raise ValueError("missing column: %s" % need)
    data = []
    for line in rows[1:]:
        cells = [c.strip() for c in line.split(",")]
        if len(cells) < len(header):
            continue
        try:
            alt = int(float(cells[idx["alter#"]]))
            vmlh = float(cells[idx["vmlh"]])
            vmhl = float(cells[idx["vmhl"]])
        except (ValueError, KeyError):
            continue
        data.append((alt, vmlh, vmhl))
    return data


def analyze(path):
    data = _read_csv(path)
    groups = {}
    for alt, vmlh, vmhl in data:
        groups.setdefault(alt, []).append((vmlh, vmhl))
    out_rows = []
    for alt in sorted(groups.keys()):
        vmlhs = [x[0] for x in groups[alt]]
        vmhls = [x[1] for x in groups[alt]]
        out_rows.append([
            alt, len(vmlhs),
            min(vmlhs), max(vmlhs), round(sum(vmlhs) / len(vmlhs), 6),
            min(vmhls), max(vmhls), round(sum(vmhls) / len(vmhls), 6),
        ])
    return out_rows


def main():
    if len(sys.argv) < 2:
        print("usage: analyze_vm.py <mt0.csv> [out.csv]", file=sys.stderr)
        sys.exit(2)
    out = sys.argv[2] if len(sys.argv) > 2 else "vm_alter_stats.csv"
    rows = analyze(sys.argv[1])
    header = ["alter#", "N", "vmlh_min", "vmlh_max", "vmlh_mean",
              "vmhl_min", "vmhl_max", "vmhl_mean"]
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for r in rows:
            w.writerow(r)
    print("wrote %d alter rows to %s" % (len(rows), out))


if __name__ == "__main__":
    main()
'''

# ---------------- check.py ----------------
CHECK_PY = '''#!/usr/bin/env python3
"""check.py for EDA-Eval-DesignFlow-VmMhlAlterStats-001. 15 conditions (a)-(o)."""
import os, sys, csv, zipfile, subprocess, tempfile, shutil, hashlib, re

EXPECTED_HEADER = ["alter#", "N", "vmlh_min", "vmlh_max", "vmlh_mean",
                   "vmhl_min", "vmhl_max", "vmhl_mean"]
TOL = 1e-4


def _cond(label, ok, msg):
    if not ok:
        raise AssertionError("[%s] %s" % (label, msg))


def _gt_from_csv(path):
    rows = []
    with open(path, "r", errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip("\\n")
            if not line or line.startswith("$") or line.startswith("."):
                continue
            rows.append(line)
    header = [c.strip() for c in rows[0].split(",")]
    idx = {n: i for i, n in enumerate(header)}
    data = {}
    for line in rows[1:]:
        cells = [c.strip() for c in line.split(",")]
        if len(cells) < len(header):
            continue
        try:
            alt = int(float(cells[idx["alter#"]]))
            vmlh = float(cells[idx["vmlh"]])
            vmhl = float(cells[idx["vmhl"]])
        except (ValueError, KeyError):
            continue
        data.setdefault(alt, []).append((vmlh, vmhl))
    gt = {}
    for alt in sorted(data):
        vmlhs = [x[0] for x in data[alt]]
        vmhls = [x[1] for x in data[alt]]
        gt[alt] = {"N": len(vmlhs), "vmlh_min": min(vmlhs), "vmlh_max": max(vmlhs),
                   "vmlh_mean": round(sum(vmlhs) / len(vmlhs), 6),
                   "vmhl_min": min(vmhls), "vmhl_max": max(vmhls),
                   "vmhl_mean": round(sum(vmhls) / len(vmhls), 6)}
    return gt, header, idx


def _run_cand(cand_path, csv_arg, out_dir):
    return subprocess.run([sys.executable, cand_path, csv_arg,
                           os.path.join(out_dir, "vm_alter_stats.csv")],
                          cwd=out_dir, capture_output=True, text=True, timeout=120)


def _read_out(out_dir):
    p = os.path.join(out_dir, "vm_alter_stats.csv")
    if not os.path.exists(p):
        return None, None
    with open(p, newline="") as fh:
        rows = list(csv.reader(fh))
    return (rows[0] if rows else None), (rows[1:] if len(rows) > 1 else [])


def check(deliverable, workdir):
    b_csv = a_csv = ""
    for n in ("hidden/mt0_B.csv", "mt0_B.csv"):
        p = os.path.join(workdir, n)
        if os.path.exists(p):
            b_csv = p; break
    for n in ("hidden/mt0_A.csv", "mt0_A.csv"):
        p = os.path.join(workdir, n)
        if os.path.exists(p):
            a_csv = p; break
    if not b_csv:
        raise AssertionError("judge: hidden B csv not found under " + workdir)
    if not a_csv:
        raise AssertionError("judge: hidden A csv not found under " + workdir)
    b_csv = os.path.abspath(b_csv)
    a_csv = os.path.abspath(a_csv)

    tmp = tempfile.mkdtemp(prefix="vmchk_")
    try:
        # (a) zip + analyze_vm.py
        _cond("a", zipfile.is_zipfile(deliverable), "deliverable not a zip")
        with zipfile.ZipFile(deliverable) as z:
            names = z.namelist()
            _cond("a", any(n.endswith("analyze_vm.py") for n in names), "analyze_vm.py missing")
            py_name = next(n for n in names if n.endswith("analyze_vm.py"))
            z.extract(py_name, tmp)
        cand_path = os.path.join(tmp, py_name)

        # (b) py_compile
        rc = subprocess.run([sys.executable, "-m", "py_compile", cand_path],
                            capture_output=True)
        _cond("b", rc.returncode == 0, "py_compile failed: %s" % rc.stderr.decode("utf-8", "replace"))

        gt_b, hdr_b, idx_b = _gt_from_csv(b_csv)
        gt_a, hdr_a, idx_a = _gt_from_csv(a_csv)

        # (c) run on B -> exit 0 + output produced
        r = _run_cand(cand_path, b_csv, tmp)
        _cond("c", r.returncode == 0, "candidate exit=%d stderr=%s" % (r.returncode, r.stderr[:300]))
        out_hdr, out_rows = _read_out(tmp)
        _cond("c", out_hdr is not None, "vm_alter_stats.csv not produced")

        # (d) header exact 8 cols in order
        got_hdr = [c.strip() for c in out_hdr]
        _cond("d", got_hdr == EXPECTED_HEADER, "header %r != %r" % (got_hdr, EXPECTED_HEADER))

        # (e) 8 rows, alter# 1..8 ascending integer
        _cond("e", len(out_rows) == 8, "expected 8 rows got %d" % len(out_rows))
        try:
            alts = [int(r[0]) for r in out_rows]
        except ValueError:
            _cond("e", False, "alter# not integer")
        _cond("e", alts == list(range(1, 9)), "alter# not 1..8: %r" % alts)

        def _row(alt):
            for r in out_rows:
                if int(r[0]) == alt:
                    return r
            return None

        r1 = _row(1)

        # (f) every row N == 80
        for r in out_rows:
            _cond("f", int(r[1]) == 80, "row %s N=%s != 80" % (r[0], r[1]))

        # (m) name-based parse guard (runs before value checks): B vmlh at shuffled
        # idx; a positional parser reading A's fixed index would grab the ramp col.
        # alt1 vmlh_min must NOT equal ramp_min of alter 1.
        ramp_alt1 = []
        skip = True
        with open(b_csv, "r", errors="replace") as fh:
            for raw in fh:
                line = raw.rstrip("\\n")
                if not line or line.startswith("$") or line.startswith("."):
                    continue
                cells = [c.strip() for c in line.split(",")]
                if skip:
                    skip = False; continue
                try:
                    if int(float(cells[idx_b["alter#"]])) == 1 and "ramp" in idx_b:
                        ramp_alt1.append(float(cells[idx_b["ramp"]]))
                except (ValueError, KeyError, IndexError):
                    continue
        _cond("m", len(ramp_alt1) > 0, "no ramp data for alter 1")
        _cond("m", abs(float(r1[2]) - min(ramp_alt1)) > 1e-6,
              "alt1 vmlh_min == ramp_min -> positional parser read ramp col")

        # (g) alter 1: vmlh_min/max, vmhl_min/max == GT
        _cond("g", r1 is not None, "alter 1 row missing")
        _cond("g", abs(float(r1[2]) - gt_b[1]["vmlh_min"]) < TOL, "alt1 vmlh_min")
        _cond("g", abs(float(r1[3]) - gt_b[1]["vmlh_max"]) < TOL, "alt1 vmlh_max")
        _cond("g", abs(float(r1[5]) - gt_b[1]["vmhl_min"]) < TOL, "alt1 vmhl_min")
        _cond("g", abs(float(r1[6]) - gt_b[1]["vmhl_max"]) < TOL, "alt1 vmhl_max")

        # (h) alter 5 vmlh_min
        r5 = _row(5)
        _cond("h", r5 is not None, "alter 5 row missing")
        _cond("h", abs(float(r5[2]) - gt_b[5]["vmlh_min"]) < TOL, "alt5 vmlh_min")

        # (i) alter 8 vmhl_max
        r8 = _row(8)
        _cond("i", r8 is not None, "alter 8 row missing")
        _cond("i", abs(float(r8[6]) - gt_b[8]["vmhl_max"]) < TOL, "alt8 vmhl_max")

        # (j) alter 3 vmlh_mean (defeats minmax-only)
        r3 = _row(3)
        _cond("j", r3 is not None, "alter 3 row missing")
        _cond("j", abs(float(r3[4]) - gt_b[3]["vmlh_mean"]) < TOL, "alt3 vmlh_mean")

        # (k) alter 3 vmhl_mean
        _cond("k", abs(float(r3[7]) - gt_b[3]["vmhl_mean"]) < TOL, "alt3 vmhl_mean")

        # (l) cross-input guard: rerun on A -> 6 alters, A alt1 vmlh_min != B alt1
        tmp_a = tempfile.mkdtemp(prefix="vmchkA_")
        try:
            rA = _run_cand(cand_path, a_csv, tmp_a)
            _cond("l", rA.returncode == 0, "candidate failed on A")
            _, rows_a = _read_out(tmp_a)
            _cond("l", len(rows_a) == 6, "A should have 6 alters got %d" % len(rows_a))
            a1 = next((r for r in rows_a if int(r[0]) == 1), None)
            _cond("l", a1 is not None, "A alter 1 missing")
            _cond("l", abs(float(a1[2]) - gt_a[1]["vmlh_min"]) < TOL, "A alt1 vmlh_min wrong")
            _cond("l", abs(float(r1[2]) - float(a1[2])) > 1e-9, "A==B alt1 vmlh_min (hardcoded)")
        finally:
            shutil.rmtree(tmp_a, ignore_errors=True)

        # (n) determinism: rerun B, sha256 identical
        tmp_n = tempfile.mkdtemp(prefix="vmchkN_")
        try:
            _run_cand(cand_path, b_csv, tmp_n)
            out_b = os.path.join(tmp, "vm_alter_stats.csv")
            out_n = os.path.join(tmp_n, "vm_alter_stats.csv")
            h1 = hashlib.sha256(open(out_b, "rb").read()).hexdigest()
            h2 = hashlib.sha256(open(out_n, "rb").read()).hexdigest() if os.path.exists(out_n) else ""
            _cond("n", h1 and h1 == h2, "non-deterministic: %s != %s" % (h1[:12], h2[:12]))
        finally:
            shutil.rmtree(tmp_n, ignore_errors=True)

        # (o) sanity: max >= min for every row
        for r in out_rows:
            _cond("o", float(r[3]) >= float(r[2]), "alter %s vmlh_max < vmlh_min" % r[0])
            _cond("o", float(r[6]) >= float(r[5]), "alter %s vmhl_max < vmhl_min" % r[0])

        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        print("CHECK:", "PASS" if check(sys.argv[1], sys.argv[2]) is True else "FAIL")
    else:
        print("usage: check.py <submit.zip> <workdir>")
'''

# ---------------- negatives ----------------
NEGATIVES = {
    "naive_empty.py": "# empty shell (syntax error)\ndef (\n",
    "naive_hardcode_A.py": (
        "# prints A's alter1 values for all 8 B rows -> fails (g) alt1 vmlh_min != GT_B\n"
        "import csv, sys\n"
        "def main():\n"
        "    out = sys.argv[2] if len(sys.argv) > 2 else 'vm_alter_stats.csv'\n"
        "    h = ['alter#','N','vmlh_min','vmlh_max','vmlh_mean','vmhl_min','vmhl_max','vmhl_mean']\n"
        "    av = [0.280501,0.358430,0.318048,0.425508,0.524103,0.468007]\n"
        "    with open(out,'w',newline='') as fh:\n"
        "        w=csv.writer(fh); w.writerow(h)\n"
        "        for alt in range(1,9):\n"
        "            w.writerow([alt,80]+av)\n"
        "if __name__=='__main__': main()\n"
    ),
    "minmax_only.py": (
        "import csv, sys\n"
        "def read(path):\n"
        "    rows=[]\n"
        "    with open(path,errors='replace') as fh:\n"
        "        for raw in fh:\n"
        "            l=raw.rstrip('\\n')\n"
        "            if not l or l.startswith('$') or l.startswith('.'): continue\n"
        "            rows.append(l)\n"
        "    hdr=[c.strip() for c in rows[0].split(',')]\n"
        "    idx={n:i for i,n in enumerate(hdr)}\n"
        "    data={}\n"
        "    for l in rows[1:]:\n"
        "        c=[x.strip() for x in l.split(',')]\n"
        "        if len(c)<len(hdr): continue\n"
        "        try:\n"
        "            alt=int(float(c[idx['alter#']])); vmlh=float(c[idx['vmlh']]); vmhl=float(c[idx['vmhl']])\n"
        "        except: continue\n"
        "        data.setdefault(alt,[]).append((vmlh,vmhl))\n"
        "    return data\n"
        "def main():\n"
        "    d=read(sys.argv[1])\n"
        "    out=sys.argv[2] if len(sys.argv)>2 else 'vm_alter_stats.csv'\n"
        "    h=['alter#','N','vmlh_min','vmlh_max','vmlh_mean','vmhl_min','vmhl_max','vmhl_mean']\n"
        "    with open(out,'w',newline='') as fh:\n"
        "        w=csv.writer(fh); w.writerow(h)\n"
        "        for alt in sorted(d):\n"
        "            vmlhs=[x[0] for x in d[alt]]; vmhls=[x[1] for x in d[alt]]\n"
        "            w.writerow([alt,len(vmlhs),min(vmlhs),max(vmlhs),0,min(vmhls),max(vmhls),0])\n"
        "if __name__=='__main__': main()\n"
    ),
    "positional_parse.py": (
        "# finds alter# by name (8 groups) but reads vmlh/vmhl by FIXED A-index 3,4\n"
        "# on B: idx3=ramp, idx4=vmlh -> vmlh_min==ramp_min -> fails (m)\n"
        "import csv, sys\n"
        "def main():\n"
        "    rows=[]\n"
        "    with open(sys.argv[1],errors='replace') as fh:\n"
        "        for raw in fh:\n"
        "            l=raw.rstrip('\\n')\n"
        "            if not l or l.startswith('$') or l.startswith('.'): continue\n"
        "            rows.append(l)\n"
        "    hdr=[c.strip() for c in rows[0].split(',')]\n"
        "    idx={n:i for i,n in enumerate(hdr)}\n"
        "    data={}\n"
        "    for l in rows[1:]:\n"
        "        c=[x.strip() for x in l.split(',')]\n"
        "        if len(c)<5: continue\n"
        "        try:\n"
        "            alt=int(float(c[idx['alter#']])); vmlh=float(c[3]); vmhl=float(c[4])\n"
        "        except: continue\n"
        "        data.setdefault(alt,[]).append((vmlh,vmhl))\n"
        "    out=sys.argv[2] if len(sys.argv)>2 else 'vm_alter_stats.csv'\n"
        "    h=['alter#','N','vmlh_min','vmlh_max','vmlh_mean','vmhl_min','vmhl_max','vmhl_mean']\n"
        "    with open(out,'w',newline='') as fh:\n"
        "        w=csv.writer(fh); w.writerow(h)\n"
        "        for alt in sorted(data):\n"
        "            vmlhs=[x[0] for x in data[alt]]; vmhls=[x[1] for x in data[alt]]\n"
        "            w.writerow([alt,len(vmlhs),min(vmlhs),max(vmlhs),round(sum(vmlhs)/len(vmlhs),6),min(vmhls),max(vmhls),round(sum(vmhls)/len(vmhls),6)])\n"
        "if __name__=='__main__': main()\n"
    ),
    "no_output.py": (
        "import sys\n"
        "def main():\n"
        "    print('analyzing', sys.argv[1])\n"
        "if __name__=='__main__': main()\n"
    ),
    "fake_core_deleted.py": (
        "import csv, sys\n"
        "def read(path):\n"
        "    rows=[]\n"
        "    with open(path,errors='replace') as fh:\n"
        "        for raw in fh:\n"
        "            l=raw.rstrip('\\n')\n"
        "            if not l or l.startswith('$') or l.startswith('.'): continue\n"
        "            rows.append(l)\n"
        "    hdr=[c.strip() for c in rows[0].split(',')]\n"
        "    idx={n:i for i,n in enumerate(hdr)}\n"
        "    data={}\n"
        "    for l in rows[1:]:\n"
        "        c=[x.strip() for x in l.split(',')]\n"
        "        if len(c)<len(hdr): continue\n"
        "        try:\n"
        "            alt=int(float(c[idx['alter#']])); vmlh=float(c[idx['vmlh']]); vmhl=float(c[idx['vmhl']])\n"
        "        except: continue\n"
        "        data.setdefault(alt,[]).append((vmlh,vmhl))\n"
        "    return data\n"
        "def main():\n"
        "    d=read(sys.argv[1])\n"
        "    out=sys.argv[2] if len(sys.argv)>2 else 'vm_alter_stats.csv'\n"
        "    h=['alter#','N','vmlh_min','vmlh_max','vmlh_mean','vmhl_min','vmhl_max','vmhl_mean']\n"
        "    with open(out,'w',newline='') as fh:\n"
        "        w=csv.writer(fh); w.writerow(h)\n"
        "        for alt in sorted(d):\n"
        "            vmlhs=[x[0] for x in d[alt]]; vmhls=[x[1] for x in d[alt]]\n"
        "            w.writerow([alt,len(vmlhs),min(vmlhs),max(vmlhs),round(sum(vmlhs)/len(vmlhs),6),min(vmhls),max(vmhls),min(vmhls)])\n"
        "if __name__=='__main__': main()\n"
    ),
}

# ---------------- negative_selftest.py ----------------
NEG_SELFTEST = '''#!/usr/bin/env python3
"""negative_selftest.py - ref must PASS, all 6 negatives must FAIL. Exit 0 iff all-good."""
import os, sys, re, zipfile, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
CASE_DIR_NAME = os.path.basename(HERE)
ASSETS_HIDDEN = os.path.normpath(os.path.join(HERE, "..", "..", "assets", CASE_DIR_NAME, "hidden"))
CHECK = os.path.join(HERE, "check.py")
REF_ZIP = os.path.join(HERE, "reference_submit.zip")
NEG_DIR = os.path.join(HERE, "negative")
NEGATIVES = ["naive_empty.py", "naive_hardcode_A.py", "minmax_only.py",
             "positional_parse.py", "no_output.py", "fake_core_deleted.py"]


def _setup_hidden():
    dst = os.path.join(HERE, "hidden")
    os.makedirs(dst, exist_ok=True)
    for n in ("mt0_A.csv", "mt0_B.csv"):
        s = os.path.join(ASSETS_HIDDEN, n)
        d = os.path.join(dst, n)
        if os.path.exists(s) and not os.path.exists(d):
            shutil.copy(s, d)


def _run(submit_zip):
    r = subprocess.run([sys.executable, CHECK, submit_zip, HERE],
                       capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout, r.stderr


def _zip_one(p):
    tmp = os.path.join(HERE, "_neg_tmp.zip")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(p, arcname="analyze_vm.py")
    return tmp


def main():
    _setup_hidden()
    rc, out, err = _run(REF_ZIP)
    ref_pass = (rc == 0)
    print("REF: %s" % ("PASS" if ref_pass else "FAIL rc=%d" % rc))
    if not ref_pass:
        print("  stderr:", err[:400])
    neg_fail = 0
    for n in NEGATIVES:
        z = _zip_one(os.path.join(NEG_DIR, n))
        rc, out, err = _run(z)
        failed = (rc != 0)
        label = "?"
        if failed:
            m = re.search(r"\\[([a-z])\\]", err)
            label = m.group(1) if m else "?"
            neg_fail += 1
        os.remove(z)
        print("NEG %-22s -> %s first-fail=[%s]" % (n, "FAIL(ok)" if failed else "PASS(BAD)", label))
    rc_bad = len(NEGATIVES) - neg_fail
    print("NEG_RC=%d (want 0)  ref=%s" % (rc_bad, "PASS" if ref_pass else "FAIL"))
    ok = ref_pass and rc_bad == 0
    print("RESULT:", "ALL-GOOD" if ok else "BAD")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
'''

# ---------------- assemble ----------------
def build():
    os.makedirs(AST_DIR, exist_ok=True)
    os.makedirs(os.path.join(AST_DIR, "hidden"), exist_ok=True)
    os.makedirs(REF_DIR, exist_ok=True)
    os.makedirs(os.path.join(REF_DIR, "negative"), exist_ok=True)

    with open(os.path.join(AST_DIR, "mt0_A.csv"), "w") as fh:
        fh.write(A_TEXT)
    with open(os.path.join(AST_DIR, "hidden", "mt0_B.csv"), "w") as fh:
        fh.write(B_TEXT)
    with open(os.path.join(AST_DIR, "hidden", "mt0_A.csv"), "w") as fh:
        fh.write(A_TEXT)

    prompt = (
        "FineSim 蒙特卡洛仿真产出一个 .csv 测量结果文件（FineSim mt0 格式："
        "开头若干 `$`/`.` 注释/指令行，之后是表头行，再后是数据行；列含 "
        "mc_index / alter# / run / vmlh / vmhl / vmlh_lv / vmhl_lv / temper，"
        "每行一次蒙特卡洛采样，alter# 标识 .alter 分组）。\n\n"
        "用户原话（trace-faithful，逐字保留）：\n"
        "  读取这个路径下的.csv文件，分析每个.alter下VMHL和VMLH的min值和max值\n\n"
        "请写一个 Python 脚本 analyze_vm.py，它：\n"
        "1. 命令行 `python3 analyze_vm.py <mt0.csv> [out.csv]`，从给定 csv 路径读取；\n"
        "2. 跳过 `$` / `.` 开头的注释/指令行，定位表头行；\n"
        "3. 按列名（header name）定位 alter# / vmlh / vmhl 列（不能按固定列下标，"
        "输入文件的列顺序可能与示例不同）；\n"
        "4. 按 alter#（整数）分组，对每组的 vmlh 和 vmhl 各算 min、max、mean；\n"
        "5. 写出 out.csv（默认 vm_alter_stats.csv），表头固定为 "
        "alter#,N,vmlh_min,vmlh_max,vmlh_mean,vmhl_min,vmhl_max,vmhl_mean，"
        "按 alter# 升序（整数排序）一行一个 alter；\n"
        "6. 纯 ASCII，可在 `python3 analyze_vm.py <csv>` 下运行。\n\n"
        "关键约束：\n"
        "- 列定位必须按表头名字（vmlh/vmhl/alter#），不要写死列下标；隐藏输入 B 的列顺序与 A 不同。\n"
        "- 必须算 mean，不能只算 min/max。\n"
        "- 交付：outputs/submit.zip，内含 analyze_vm.py。\n"
    )
    with open(os.path.join(AST_DIR, "prompt.txt"), "w") as fh:
        fh.write(prompt)
    with open(os.path.join(AST_DIR, "task_brief.md"), "w") as fh:
        fh.write("交付：outputs/submit.zip，内含 analyze_vm.py（CLI `python3 analyze_vm.py <mt0.csv> [out.csv]`，按列名解析 FineSim mt0 csv，按 alter# 分组算 vmlh/vmhl 的 min/max/mean，写出 vm_alter_stats.csv）。\n判分：check(submit.zip, workdir)。\n")

    manifest = {
        "input": {"csv": "mt0_B.csv"},
        "ground_truth_B": {"n_alters": 8, "rows_per_alter": 80, "col_order": B_COLS,
                           "gt": {str(k): v for k, v in GT_B.items()}},
        "visible_A": {"csv": "mt0_A.csv"},
        "ground_truth_A": {"n_alters": 6, "rows_per_alter": 120, "col_order": A_COLS,
                           "gt": {str(k): v for k, v in GT_A.items()}},
    }
    with open(os.path.join(AST_DIR, "hidden", "hidden_manifest.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)

    with open(os.path.join(REF_DIR, "analyze_vm.py"), "w") as fh:
        fh.write(REF_PY)
    with zipfile.ZipFile(os.path.join(REF_DIR, "reference_submit.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("analyze_vm.py", REF_PY)
    with open(os.path.join(REF_DIR, "check.py"), "w") as fh:
        fh.write(CHECK_PY)
    for name, body in NEGATIVES.items():
        with open(os.path.join(REF_DIR, "negative", name), "w") as fh:
            fh.write(body)
    with open(os.path.join(REF_DIR, "negative_selftest.py"), "w") as fh:
        fh.write(NEG_SELFTEST)
    return GT_A, GT_B


if __name__ == "__main__":
    gta, gtb = build()
    print("built", CASE_ID)
    print("A: 6 alters x 120; B: 8 alters x 80")
    print("GT_A alter1:", gta[1])
    print("GT_B alter1:", gtb[1])
    print("GT_B alter8:", gtb[8])
