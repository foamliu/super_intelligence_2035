#!/usr/bin/env python3
"""Generator for EDA-Eval-DesignFlow-CalibreOpen1Fix-001.

A-faithful case from trace 1789545344007_xchvr (ellawu, pnr_signoff, Calibre OPEN1).
Gold: missing LAYOUT PRECISION injection. Deliverable: fix.py (CLI rule-fixer
reading precision from config) + diagnose.json. Hidden B: different process /
precision (1000) / layer names.
"""
import json, os, shutil, subprocess, sys, tempfile, zipfile

CASE = "EDA-Eval-DesignFlow-CalibreOpen1Fix-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
A_DIR = f"{BENCH}/assets/{CASE}"
HID_DIR = f"{A_DIR}/hidden"
REF_DIR = f"{BENCH}/reference/{CASE}"
NEG_DIR = f"{REF_DIR}/negative"
REF_HID = f"{REF_DIR}/hidden"

# ---------- A assets ----------
PROMPT = "ERROR: Error OPEN1 - problem with access, file type, or file open of file: calibreSTIcmp.rule.\n"

BRIEF = """交付接口：outputs/submit.zip 内含 fix.py（纯 Python 标准库）与 diagnose.json（根因诊断）。
CLI: python3 fix.py <rule_file> <config_file> <output_rule_file>   （从 config 读取 precision，将 LAYOUT PRECISION 注入 rule 文件：已存在则替换，缺失则于 LAYOUT system 行后插入；保留其余 LAYOUT 语句不动；exit 0 成功）
diagnose.json 须含字段 root_cause(str) / issues(list[str]) / fix_summary(str)，记录 OPEN1 错误根因与修复要点。
工作目录下 gen_preAA_G5_CIP_final_A.py 为出错脚本上下文（fixture，只读），calibreSTIcmp_A.rule 与 config_A.txt 为真实输入。
"""

# Buggy script (faithful to trace: no PRECISION injection, no rsync check, no file-exists check)
BUGGY_A = '''#!/apps/local/bin/python3
"""gen_preAA_G5_CIP_final_A.py  —  PG dummy + STI DRC flow (BUGGY, fixture context).

Builds deck_STI path, rsyncs calibreSTIcmp.rule into Run_Dir, sed-modifies
LAYOUT PATH/PRIMARY, then runs calibre -drc. Reproduces the OPEN1 error
trace from ellawu/cxmtG5_CIP.  DO NOT run as-is; it is context for fix.py.
"""
import os, sys

CONFIG_FILE = ".PG_DUMMY_for_Logic.config_A.txt"

def load_config(path):
    cfg = {}
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip()
    return cfg

def compute_precision(processname_new):
    # G5_CIP uses 0.1nm grid -> precision 10000; others default 1000
    if processname_new in ("cxmtG5_CIP", "cxmtG5"):
        return "10000"
    return "1000"

def run_sti_drc(cfg, Run_Dir):
    processname_new = cfg.get("process", "")
    projName = cfg.get("projName", "")
    deckName_STI = "calibreSTIcmp.rule"
    # path construction (matches /apps/imctf/runset/calibre/<proc>/current/<proj>/runset/...)
    deck_STI = "/apps/imctf/runset/calibre/" + processname_new + "/current/" + projName + "/runset/" + deckName_STI
    # BUG 1: rsync return code never checked
    os.system("rsync -avzL " + deck_STI + " " + Run_Dir)
    # BUG 2: only LAYOUT PATH / PRIMARY rewritten; PRECISION computed but never injected
    os.system("sed -i 's,\\\\(LAYOUT path\\\\).*,\\\\1 LP4TOP.gds,' " + Run_Dir + "/" + deckName_STI)
    os.system("sed -i 's,\\\\(LAYOUT primary\\\\).*,\\\\1 LP4TOP,' " + Run_Dir + "/" + deckName_STI)
    precision = compute_precision(processname_new)   # computed but unused
    # BUG 3: no file-existence verification before calibre
    os.system("cd " + Run_Dir + "; calibre -drc -hier -turbo 4 " + deckName_STI + " |& tee run_STI.log")

if __name__ == "__main__":
    cfg = load_config(CONFIG_FILE)
    run_sti_drc(cfg, "/tmp/run_sti")
'''

RULE_A = """// calibreSTIcmp_A.rule  —  STI CMP DRC deck (cxmtG5_CIP / decqa), fixture
// NOTE: no LAYOUT PRECISION statement present (root cause of OPEN1)
LAYOUT path LP4TOP.gds
LAYOUT system gdsii
LAYOUT primary LP4TOP

// ----- DRC rule blocks (abridged fixture) -----
DRC CHECK {
  STI_CMP_WIDTH {
    @ STI CMP minimum width
    external STI < 0.12
  }
  STI_CMP_SPACING {
    @ STI CMP minimum spacing
    internal STI < 0.14
  }
}
INCLUDE "/apps/imctf/runset/calibre/cxmtG5_CIP/current/common/calibre.layer"
"""

CONFIG_A = """# .PG_DUMMY_for_Logic.config_A  —  fixture (cxmtG5_CIP)
process = cxmtG5_CIP
libName = ella_train
topCell = AF_FsMrgNEnCount
projName = decqa
precision = 10000
"""

# ---------- Hidden B assets (structurally different) ----------
BUGGY_B = '''#!/apps/local/bin/python3
"""gen_preAA_10G7_iejoad_B.py  —  PG dummy + STI DRC flow (BUGGY, fixture B).

Different process (cxmt10G7), projName (iejoad), layer (M2CORE), precision 1000.
Same root-cause pattern: no LAYOUT PRECISION injection. Context for fix.py.
"""
import os, sys

CONFIG_FILE = ".PG_DUMMY_for_Logic.config_B.txt"

def load_config(path):
    cfg = {}
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        cfg[k.strip()] = v.strip()
    return cfg

def compute_precision(processname_new):
    if processname_new in ("cxmt10G7", "cxmt10G6"):
        return "1000"
    return "1000"

def run_sti_drc(cfg, Run_Dir):
    processname_new = cfg.get("process", "")
    projName = cfg.get("projName", "")
    deckName_STI = "calibreSTIcmp.rule"
    deck_STI = "/apps/imctf/runset/calibre/" + processname_new + "/current/" + projName + "/runset/" + deckName_STI
    os.system("rsync -avzL " + deck_STI + " " + Run_Dir)
    os.system("sed -i 's,\\\\(LAYOUT path\\\\).*,\\\\1 M2CORE.gds,' " + Run_Dir + "/" + deckName_STI)
    os.system("sed -i 's,\\\\(LAYOUT primary\\\\).*,\\\\1 M2CORE,' " + Run_Dir + "/" + deckName_STI)
    precision = compute_precision(processname_new)
    os.system("cd " + Run_Dir + "; calibre -drc -hier -turbo 8 " + deckName_STI + " |& tee run_STI.log")

if __name__ == "__main__":
    cfg = load_config(CONFIG_FILE)
    run_sti_drc(cfg, "/tmp/run_sti_b")
'''

RULE_B = """// calibreSTIcmp_B.rule  —  STI CMP DRC deck (cxmt10G7 / iejoad), fixture B
// NOTE: no LAYOUT PRECISION statement present (root cause of OPEN1)
LAYOUT path M2CORE.gds
LAYOUT system gdsii
LAYOUT primary M2CORE

// ----- DRC rule blocks (abridged fixture, different rules) -----
DRC CHECK {
  METAL2_ENC_VIA {
    @ M2 via enclosure check
    enclosed M2 VIA2 < 0.05
  }
  METAL2_MIN_AREA {
    @ M2 minimum area
    area M2 < 0.08
  }
}
INCLUDE "/apps/imctf/runset/calibre/cxmt10G7/current/common/calibre.layer"
"""

CONFIG_B = """# .PG_DUMMY_for_Logic.config_B  —  fixture (cxmt10G7)
process = cxmt10G7
libName = vex_qa
topCell = DRAMCoreTop
projName = iejoad
precision = 1000
"""

MANIFEST = {
    "task_id": CASE,
    "note": ("Hidden cross-input guard B. Different process (cxmt10G7 vs A's cxmtG5_CIP), "
             "different projName (iejoad vs decqa), different layer (M2CORE vs LP4TOP), "
             "different precision (1000 vs 10000). Same root-cause pattern (no LAYOUT PRECISION). "
             "check() re-runs candidate fix.py on B and asserts B output contains LAYOUT PRECISION 1000 "
             "(generalization: precision must be read from config, not hardcoded) + B LAYOUT path/primary "
             "preserved + no A/B-specific literals in source (anti-hardcoding)."),
    "files": {
        "calibreSTIcmp_B.rule": "B's fixture rule file (NOT given to SUT)",
        "config_B.txt": "B's fixture config (NOT given to SUT)",
        "gen_preAA_10G7_iejoad_B.py": "B's buggy script context (NOT given to SUT)",
    },
}

# ---------- Reference gold fix.py ----------
GOLD_FIX = '''#!/usr/bin/env python3
"""fix.py — fix Calibre OPEN1 by injecting LAYOUT PRECISION from config.

CLI: python3 fix.py <rule_file> <config_file> <output_rule_file>
Reads precision from config, injects/replaces LAYOUT PRECISION in the rule file
(replace if present; insert after LAYOUT system if absent). Preserves all other
LAYOUT statements. Exit 0 on success.
"""
import os, sys, re


def load_config(path):
    cfg = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()
    return cfg


def fix_rule(rule_text, precision):
    lines = rule_text.splitlines()
    out = []
    inserted = False
    precision_str = str(precision)
    for line in lines:
        m = re.match(r"^(\\s*LAYOUT\\s+PRECISION\\s+).*$", line, re.IGNORECASE)
        if m:
            # replace existing
            out.append(m.group(1) + precision_str)
            inserted = True
        else:
            out.append(line)
            # if no PRECISION line yet and this is LAYOUT system, insert after it
            if not inserted and re.match(r"^\\s*LAYOUT\\s+system\\s+", line, re.IGNORECASE):
                out.append("LAYOUT PRECISION " + precision_str)
                inserted = True
    if not inserted:
        # no LAYOUT system line found; prepend after first LAYOUT path line or at top
        out2 = []
        done = False
        for line in out:
            out2.append(line)
            if not done and re.match(r"^\\s*LAYOUT\\s+path\\s+", line, re.IGNORECASE):
                out2.append("LAYOUT PRECISION " + precision_str)
                done = True
        out = out2 if done else (["LAYOUT PRECISION " + precision_str] + out)
    return "\\n".join(out) + ("\\n" if rule_text.endswith("\\n") else "")


def main():
    if len(sys.argv) != 4:
        print("usage: fix.py <rule_file> <config_file> <output_rule_file>", file=sys.stderr)
        return 2
    rule_file, config_file, output_file = sys.argv[1], sys.argv[2], sys.argv[3]
    if not os.path.isfile(rule_file):
        print("ERROR: rule file not found: " + rule_file, file=sys.stderr)
        return 1
    if not os.path.isfile(config_file):
        print("ERROR: config file not found: " + config_file, file=sys.stderr)
        return 1
    cfg = load_config(config_file)
    precision = cfg.get("precision")
    if not precision:
        print("ERROR: precision missing from config", file=sys.stderr)
        return 1
    with open(rule_file) as f:
        rule_text = f.read()
    fixed = fix_rule(rule_text, precision)
    with open(output_file, "w") as f:
        f.write(fixed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

GOLD_DIAGNOSE = {
    "root_cause": "Missing LAYOUT PRECISION statement in calibreSTIcmp.rule. The script computes precision from the process but never injects it into the rule file; Calibre defaults to PRECISION 1000 and cannot open the GDS whose precision differs, raising OPEN1.",
    "issues": [
        "LAYOUT PRECISION never injected: precision variable computed but not written into the rule file",
        "rsync -avzL return code not checked: silent copy failure leaves no rule file in Run_Dir",
        "No file-existence verification before invoking calibre -drc",
        "sed only rewrites LAYOUT path / primary, never PRECISION",
    ],
    "fix_summary": "Inject LAYOUT PRECISION <precision> read from config into the rule file (replace if present, else insert after LAYOUT system); also verify rsync return code and rule-file existence before running calibre.",
}

# ---------- check.py ----------
CHECK_PY = '''#!/usr/bin/env python3
"""check.py for EDA-Eval-DesignFlow-CalibreOpen1Fix-001.

Contract: check(deliverable, workdir) -> True on PASS, raise on FAIL.

Judging layout (set up by harness):
  workdir/calibreSTIcmp_A.rule / config_A.txt / gen_preAA_G5_CIP_final_A.py  (visible A)
  workdir/hidden/calibreSTIcmp_B.rule / config_B.txt                         (hidden B)
  deliverable = path to submit.zip

k = 14 条断言 (a)-(n), each independently FAIL-able. See test_rationale in jsonl.
"""
import json, os, re, subprocess, sys, tempfile, zipfile

CASE_ID = "EDA-Eval-DesignFlow-CalibreOpen1Fix-001"
FIX = "fix.py"
DIAG = "diagnose.json"

# A-specific literals that must NOT appear in candidate source (anti-hardcoding)
A_LITERALS = ["cxmtG5_CIP", "decqa", "LP4TOP", "ella_train", "AF_FsMrgNEnCount"]
# B-specific literals that must NOT appear in candidate source
B_LITERALS = ["cxmt10G7", "iejoad", "M2CORE", "vex_qa", "DRAMCoreTop"]
# Hardcoded precision literals forbidden in source (must read from config)
PREC_LITERALS = ["10000", "1000"]


def _find(workdir, name, extra_dirs=()):
    cands = [os.path.join(workdir, name), os.path.join(workdir, "hidden", name)]
    for d in extra_dirs:
        cands.append(os.path.join(d, name))
        cands.append(os.path.join(d, "hidden", name))
    for c in cands:
        if os.path.isfile(c):
            return c
    for root, _d, files in os.walk(workdir):
        if name in files:
            return os.path.join(root, name)
    raise FileNotFoundError(f"{name} not found under {workdir} or {extra_dirs}")


def _run_fix(script_path, rule, config, out, timeout=60):
    return subprocess.run([sys.executable, script_path, rule, config, out],
                          capture_output=True, text=True, timeout=timeout)


def _precision_lines(text):
    return [ln for ln in text.splitlines() if re.match(r"^\\s*LAYOUT\\s+PRECISION\\s+", ln, re.IGNORECASE)]


def check(deliverable, workdir):
    here = os.path.dirname(os.path.abspath(__file__))
    extra = (here, os.path.join(here, "hidden"),
             os.path.dirname(here), os.path.join(os.path.dirname(here), "assets", CASE_ID))
    rule_a = _find(workdir, "calibreSTIcmp_A.rule", extra)
    cfg_a = _find(workdir, "config_A.txt", extra)
    rule_b = _find(workdir, "calibreSTIcmp_B.rule", extra)
    cfg_b = _find(workdir, "config_B.txt", extra)

    with tempfile.TemporaryDirectory() as td:
        if not os.path.isfile(deliverable):
            raise AssertionError(f"(a) deliverable not found: {deliverable}")
        with zipfile.ZipFile(deliverable) as z:
            names = [n for n in z.namelist() if not n.endswith("/")]
            base = sorted(n.split("/")[-1] for n in names)
            if base != sorted([FIX, DIAG]):
                raise AssertionError(f"(a) submit.zip must contain exactly {FIX} and {DIAG}; got {names}")
            z.extractall(td)
        fix_path = os.path.join(td, FIX)
        diag_path = os.path.join(td, DIAG)
        if not os.path.isfile(fix_path):
            raise AssertionError(f"(a) {FIX} missing in zip")
        if not os.path.isfile(diag_path):
            raise AssertionError(f"(a) {DIAG} missing in zip")

        # (b) py_compile fix.py
        import py_compile
        try:
            py_compile.compile(fix_path, doraise=True)
        except py_compile.PyCompileError as e:
            raise AssertionError(f"(b) {FIX} does not compile: {e}")

        src = open(fix_path).read()

        out_a = os.path.join(td, "out_A.rule")
        pa = _run_fix(fix_path, rule_a, cfg_a, out_a)
        if pa.returncode != 0:
            raise AssertionError(f"(c) A run exit={pa.returncode}; stderr={pa.stderr[:400]}")
        if not os.path.isfile(out_a):
            raise AssertionError(f"(c) A run produced no output rule file")
        text_a = open(out_a).read()
        pla = _precision_lines(text_a)
        if not pla:
            raise AssertionError(f"(c) A output rule has no LAYOUT PRECISION line")
        if "10000" not in pla[0]:
            raise AssertionError(f"(c) A LAYOUT PRECISION != 10000; got {pla}")

        # (d) A preserves LAYOUT path / system / primary
        if not re.search(r"^\\s*LAYOUT\\s+path\\s+LP4TOP\\.gds\\s*$", text_a, re.MULTILINE | re.IGNORECASE):
            raise AssertionError(f"(d) A output missing LAYOUT path LP4TOP.gds")
        if not re.search(r"^\\s*LAYOUT\\s+system\\s+gdsii\\s*$", text_a, re.MULTILINE | re.IGNORECASE):
            raise AssertionError(f"(d) A output missing LAYOUT system gdsii")
        if not re.search(r"^\\s*LAYOUT\\s+primary\\s+LP4TOP\\s*$", text_a, re.MULTILINE | re.IGNORECASE):
            raise AssertionError(f"(d) A output missing LAYOUT primary LP4TOP")

        out_b = os.path.join(td, "out_B.rule")
        pb = _run_fix(fix_path, rule_b, cfg_b, out_b)
        if pb.returncode != 0:
            raise AssertionError(f"(e) B run exit={pb.returncode}; stderr={pb.stderr[:400]}")
        if not os.path.isfile(out_b):
            raise AssertionError(f"(e) B run produced no output rule file")
        text_b = open(out_b).read()
        plb = _precision_lines(text_b)
        if not plb:
            raise AssertionError(f"(e) B output rule has no LAYOUT PRECISION line")
        if "1000" not in plb[0]:
            raise AssertionError(f"(e) B LAYOUT PRECISION != 1000; got {plb}")

        # (f) B preserves B's LAYOUT path / system / primary
        if not re.search(r"^\\s*LAYOUT\\s+path\\s+M2CORE\\.gds\\s*$", text_b, re.MULTILINE | re.IGNORECASE):
            raise AssertionError(f"(f) B output missing LAYOUT path M2CORE.gds")
        if not re.search(r"^\\s*LAYOUT\\s+system\\s+gdsii\\s*$", text_b, re.MULTILINE | re.IGNORECASE):
            raise AssertionError(f"(f) B output missing LAYOUT system gdsii")
        if not re.search(r"^\\s*LAYOUT\\s+primary\\s+M2CORE\\s*$", text_b, re.MULTILINE | re.IGNORECASE):
            raise AssertionError(f"(f) B output missing LAYOUT primary M2CORE")

        # (g) A output has exactly one PRECISION line (no duplicates)
        if len(pla) != 1:
            raise AssertionError(f"(g) A output has {len(pla)} PRECISION lines (expected 1); {pla}")
        # (h) B output has exactly one PRECISION line
        if len(plb) != 1:
            raise AssertionError(f"(h) B output has {len(plb)} PRECISION lines (expected 1); {plb}")

        # (i) diagnose.json valid JSON with required keys
        try:
            diag = json.load(open(diag_path))
        except Exception as e:
            raise AssertionError(f"(i) diagnose.json not valid JSON: {e}")
        for k in ("root_cause", "issues", "fix_summary"):
            if k not in diag:
                raise AssertionError(f"(i) diagnose.json missing key '{k}'")

        # (j) root_cause mentions PRECISION (the real root cause)
        rc = str(diag.get("root_cause", "")).upper()
        if "PRECISION" not in rc:
            raise AssertionError(f"(j) diagnose.root_cause does not mention PRECISION: {diag.get('root_cause','')[:200]}")

        # (k) issues is a list with >=2 entries
        issues = diag.get("issues")
        if not isinstance(issues, list) or len(issues) < 2:
            raise AssertionError(f"(k) diagnose.issues must be a list with >=2 entries; got {type(issues)} len={len(issues) if isinstance(issues,list) else 'NA'}")

        # (l) fix_summary mentions PRECISION injection semantics
        fs = str(diag.get("fix_summary", "")).upper()
        if "PRECISION" not in fs:
            raise AssertionError(f"(l) diagnose.fix_summary does not mention PRECISION: {diag.get('fix_summary','')[:200]}")

        # (m) anti-hardcode: source has no A-specific literals
        hit_a = [lit for lit in A_LITERALS if lit in src]
        if hit_a:
            raise AssertionError(f"(m) {FIX} source contains A-specific literals {hit_a} (hardcoding)")
        hit_b = [lit for lit in B_LITERALS if lit in src]
        if hit_b:
            raise AssertionError(f"(m) {FIX} source contains B-specific literals {hit_b} (hardcoding)")

        # (n) anti-hardcode: source does not hardcode precision literals 10000/1000
        hit_p = [lit for lit in PREC_LITERALS if lit in src]
        if hit_p:
            raise AssertionError(f"(n) {FIX} source contains hardcoded precision literals {hit_p} (must read from config)")

    return True


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        ok = check(sys.argv[1], sys.argv[2])
        print("PASS" if ok else "FAIL")
    else:
        print("usage: check.py <submit.zip> <workdir>", file=sys.stderr)
'''

# ---------- negatives ----------
NEG_EMPTY = '# fake_empty\nimport sys\nsys.exit(0)\n'
NEG_PRINT = '''# fake_print_expected: prints expected strings, no real logic
import sys, json
print("LAYOUT PRECISION 10000")
print(json.dumps({"root_cause":"PRECISION","issues":["a","b"],"fix_summary":"inject PRECISION"}))
sys.exit(0)
'''
NEG_CORE_DELETED = '''# fake_core_deleted: gold fix.py with PRECISION injection removed (only copies rule)
import os, sys, shutil
def main():
    if len(sys.argv) != 4:
        return 2
    rule_file, config_file, output_file = sys.argv[1], sys.argv[2], sys.argv[3]
    shutil.copyfile(rule_file, output_file)  # NO precision injection
    return 0
if __name__ == "__main__":
    sys.exit(main())
'''
NEG_NAIVE = '''# naive_stub: hardcodes 10000 (passes A, fails B + anti-hardcode)
import os, sys, re
def main():
    if len(sys.argv) != 4:
        return 2
    rule_file, config_file, output_file = sys.argv[1], sys.argv[2], sys.argv[3]
    text = open(rule_file).read()
    lines = text.splitlines()
    out = []
    inserted = False
    for line in lines:
        out.append(line)
        if not inserted and re.match(r"^\\s*LAYOUT\\s+system\\s+", line, re.IGNORECASE):
            out.append("LAYOUT PRECISION 10000")
            inserted = True
    open(output_file, "w").write("\\n".join(out) + "\\n")
    return 0
if __name__ == "__main__":
    sys.exit(main())
'''

NEG_SELFTEST = '''#!/usr/bin/env python3
"""negative_selftest.py — all 4 negatives must FAIL check()."""
import json, os, shutil, subprocess, sys, tempfile, zipfile

CASE = "EDA-Eval-DesignFlow-CalibreOpen1Fix-001"
HERE = os.path.dirname(os.path.abspath(__file__))

NEGATIVES = {
    "fake_empty": ("fix.py", "diagnose.json"),
    "fake_print_expected": ("fix.py", "diagnose.json"),
    "fake_core_deleted": ("fix.py", "diagnose.json"),
    "naive_stub": ("fix.py", "diagnose.json"),
}

def _make_zip(neg_name, td):
    fix_src = open(os.path.join(HERE, "negative", neg_name + ".py")).read()
    diag = {"root_cause": "PRECISION missing", "issues": ["a", "b"], "fix_summary": "inject PRECISION"}
    zpath = os.path.join(td, f"{neg_name}.zip")
    with zipfile.ZipFile(zpath, "w") as z:
        z.writestr("fix.py", fix_src)
        z.writestr("diagnose.json", json.dumps(diag))
    return zpath

def main():
    # workdir = HERE (has calibreSTIcmp_A.rule? no — copy assets)
    results = {}
    for neg in NEGATIVES:
        with tempfile.TemporaryDirectory() as td:
            zpath = _make_zip(neg, td)
            # workdir = HERE/.. (reference dir parent) so check finds A via extra dirs
            wd = os.path.join(HERE, "workdir_stub")
            os.makedirs(wd, exist_ok=True)
            r = subprocess.run([sys.executable, os.path.join(HERE, "check.py"), zpath, wd],
                               capture_output=True, text=True, timeout=120)
            # PASS = check returned 0 with "PASS"; we expect FAIL (non-zero or "FAIL" / AssertionError)
            passed = (r.returncode == 0 and "PASS" in r.stdout)
            results[neg] = "PASS(BAD)" if passed else "FAIL(ok)"
            if passed:
                print(f"  {neg}: UNEXPECTED PASS — BUG")
    print("negative_selftest results:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    all_fail = all(v == "FAIL(ok)" for v in results.values())
    print("ALL-FAIL" if all_fail else "SOME-PASS-BUG")
    return 0 if all_fail else 1

if __name__ == "__main__":
    sys.exit(main())
'''


def main():
    os.makedirs(A_DIR, exist_ok=True)
    os.makedirs(HID_DIR, exist_ok=True)
    os.makedirs(REF_DIR, exist_ok=True)
    os.makedirs(NEG_DIR, exist_ok=True)
    os.makedirs(REF_HID, exist_ok=True)

    # A assets
    with open(f"{A_DIR}/prompt.txt", "w") as f:
        f.write(PROMPT)
    with open(f"{A_DIR}/task_brief.md", "w") as f:
        f.write(BRIEF)
    with open(f"{A_DIR}/gen_preAA_G5_CIP_final_A.py", "w") as f:
        f.write(BUGGY_A)
    with open(f"{A_DIR}/calibreSTIcmp_A.rule", "w") as f:
        f.write(RULE_A)
    with open(f"{A_DIR}/config_A.txt", "w") as f:
        f.write(CONFIG_A)

    # Hidden B (in assets/.../hidden/ — NOT given to SUT)
    with open(f"{HID_DIR}/calibreSTIcmp_B.rule", "w") as f:
        f.write(RULE_B)
    with open(f"{HID_DIR}/config_B.txt", "w") as f:
        f.write(CONFIG_B)
    with open(f"{HID_DIR}/gen_preAA_10G7_iejoad_B.py", "w") as f:
        f.write(BUGGY_B)
    with open(f"{HID_DIR}/hidden_manifest.json", "w") as f:
        json.dump(MANIFEST, f, indent=2, ensure_ascii=False)

    # Reference
    with open(f"{REF_DIR}/check.py", "w") as f:
        f.write(CHECK_PY)
    with open(f"{REF_DIR}/gold_fix.py", "w") as f:
        f.write(GOLD_FIX)
    # hidden B copy in reference/.../hidden/
    shutil.copyfile(f"{HID_DIR}/calibreSTIcmp_B.rule", f"{REF_HID}/calibreSTIcmp_B.rule")
    shutil.copyfile(f"{HID_DIR}/config_B.txt", f"{REF_HID}/config_B.txt")
    shutil.copyfile(f"{HID_DIR}/gen_preAA_10G7_iejoad_B.py", f"{REF_HID}/gen_preAA_10G7_iejoad_B.py")

    # negatives
    with open(f"{NEG_DIR}/fake_empty.py", "w") as f:
        f.write(NEG_EMPTY)
    with open(f"{NEG_DIR}/fake_print_expected.py", "w") as f:
        f.write(NEG_PRINT)
    with open(f"{NEG_DIR}/fake_core_deleted.py", "w") as f:
        f.write(NEG_CORE_DELETED)
    with open(f"{NEG_DIR}/naive_stub.py", "w") as f:
        f.write(NEG_NAIVE)
    with open(f"{REF_DIR}/negative_selftest.py", "w") as f:
        f.write(NEG_SELFTEST)

    # reference_submit.zip = fix.py + diagnose.json (from gold)
    with tempfile.TemporaryDirectory() as td:
        with open(f"{td}/fix.py", "w") as f:
            f.write(GOLD_FIX)
        with open(f"{td}/diagnose.json", "w") as f:
            json.dump(GOLD_DIAGNOSE, f, indent=2)
        with zipfile.ZipFile(f"{REF_DIR}/reference_submit.zip", "w") as z:
            z.write(f"{td}/fix.py", "fix.py")
            z.write(f"{td}/diagnose.json", "diagnose.json")

    print(f"[gen] wrote assets/{CASE}, reference/{CASE}")

    # ---------- self-validation ----------
    # ref dry-run: check(reference_submit.zip, workdir with A + hidden/B)
    with tempfile.TemporaryDirectory() as td:
        # workdir layout: A rule/config/script at top, hidden/B under hidden/
        shutil.copyfile(f"{A_DIR}/calibreSTIcmp_A.rule", f"{td}/calibreSTIcmp_A.rule")
        shutil.copyfile(f"{A_DIR}/config_A.txt", f"{td}/config_A.txt")
        shutil.copyfile(f"{A_DIR}/gen_preAA_G5_CIP_final_A.py", f"{td}/gen_preAA_G5_CIP_final_A.py")
        os.makedirs(f"{td}/hidden", exist_ok=True)
        shutil.copyfile(f"{REF_HID}/calibreSTIcmp_B.rule", f"{td}/hidden/calibreSTIcmp_B.rule")
        shutil.copyfile(f"{REF_HID}/config_B.txt", f"{td}/hidden/config_B.txt")
        r = subprocess.run([sys.executable, f"{REF_DIR}/check.py",
                            f"{REF_DIR}/reference_submit.zip", td],
                           capture_output=True, text=True, timeout=120)
        print(f"[selfval] ref dry-run: rc={r.returncode}")
        print(f"[selfval] stdout: {r.stdout}")
        if r.returncode != 0 or "PASS" not in r.stdout:
            print(f"[selfval] stderr: {r.stderr}")
            print("!!! REF SELF-VALIDATION FAILED !!!")
            sys.exit(1)
        print("[selfval] ref PASS ✓")

    # negative selftest
    # negative_selftest expects a workdir_stub under reference dir with A assets
    stub = f"{REF_DIR}/workdir_stub"
    os.makedirs(stub, exist_ok=True)
    shutil.copyfile(f"{A_DIR}/calibreSTIcmp_A.rule", f"{stub}/calibreSTIcmp_A.rule")
    shutil.copyfile(f"{A_DIR}/config_A.txt", f"{stub}/config_A.txt")
    shutil.copyfile(f"{A_DIR}/gen_preAA_G5_CIP_final_A.py", f"{stub}/gen_preAA_G5_CIP_final_A.py")
    os.makedirs(f"{stub}/hidden", exist_ok=True)
    shutil.copyfile(f"{REF_HID}/calibreSTIcmp_B.rule", f"{stub}/hidden/calibreSTIcmp_B.rule")
    shutil.copyfile(f"{REF_HID}/config_B.txt", f"{stub}/hidden/config_B.txt")
    r = subprocess.run([sys.executable, f"{REF_DIR}/negative_selftest.py"],
                       capture_output=True, text=True, timeout=300, cwd=REF_DIR)
    print(f"[selfval] negative_selftest: rc={r.returncode}")
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        print("!!! NEGATIVE SELFTEST FAILED !!!")
        sys.exit(1)
    print("[selfval] negatives ALL-FAIL ✓")

    # cleanup workdir_stub (not part of deliverable)
    shutil.rmtree(stub, ignore_errors=True)

    print("[gen] ALL SELF-VALIDATION PASSED")


if __name__ == "__main__":
    main()
