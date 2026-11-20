#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build assets/reference/negatives for EDA-Eval-DesignFlow-SiInpTokenRm-001.

Trace-faithful source: mike @ hfeg0plg05, session 1789611712575_5tdum.
A-faithful prompt (user msg #0, verbatim pinyin):
  "/rundata/dscqa_sim/.../MatrixRun_Netlist_Vcap_20260916PM_DDR6TOP.Meta
   zhegelujingxia you henduo mulu ,meige muluxia youge si.inp wenjian ,
   bangwo xiege mingling ,woyao shandiao si.inp zhong T_mBistOsc zifuchuan"
  => "Under this path there are many dirs, each has a si.inp file, write me a
     command, I want to delete the T_mBistOsc string in si.inp"

Gold = assistant msg_MTSgZiyu (3 methods; recommended):
  find <root> -name 'si.inp' -type f -exec sed -i 's/T_mBistOsc //g' {} \\;
  => remove the standalone token `T_mBistOsc ` (with trailing space) from the
     `.option finesim_ignore = "..."` line of every si.inp under root, leaving
     all other tokens / lines intact. T_mBistOsc is always followed by a space
     in the real data (middle of the token list).

Deliverable: a script in submit.zip (.py or .sh) taking a root-dir positional
arg, recursively finding all si.inp and removing T_mBistOsc in-place.
"""
import os, json, shutil, hashlib, textwrap

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-SiInpTokenRm-001"
ASETS = os.path.join(BENCH, "assets", CASE)
REF = os.path.join(BENCH, "reference", CASE)

TARGET = "T_mBistOsc"   # the token to remove
# decoy tokens that CONTAIN the substring but must be preserved (test precision).
# NOTE: gold = `s/T_mBistOsc //g` (substring + trailing space). A token with
# T_mBistOsc as a SUFFIX (e.g. PreT_mBistOsc + space) WOULD be corrupted by the
# gold, so it is NOT a valid "must-preserve" decoy. Only a token with T_mBistOsc
# as a PREFIX (T_mBistOscTail: after T_mBistOsc comes 'T', not space) is left
# intact by the gold and corrupted by naive `s/T_mBistOsc//`.
DECOY_SUB = ["T_mBistOscTail"]

def siinp(run, tokens, line_no, with_decoy_sub=False, extra_lines=()):
    """Build a synthetic FineSim si.inp with `.option finesim_ignore = "..."` line."""
    head = [
        "* FineSim deck: %s" % run,
        ".include '/pdk/models/all.mdl'",
        ".param vdd=0.9 temp=25",
        "vvdd vdd 0 0.9",
        "vgnd gnd 0 0",
        "Xtop vdd gnd in out top_circuit_%s" % run,
    ]
    # pad to reach line_no (1-indexed). line_no is where finesim_ignore goes.
    while len(head) < line_no - 1:
        head.append("* filler comment line %d" % (len(head) + 1))
    tok = list(tokens)
    if with_decoy_sub:
        tok = tok[:-1] + DECOY_SUB + [tok[-1]]
    head.append('.option finesim_ignore = "%s"' % " ".join(tok))
    tail = list(extra_lines) + [
        ".tran 1n 100n",
        ".meas tran vout_peak max v(out)",
        ".print tran v(out) v(in)",
        ".end",
    ]
    return "\n".join(head + tail) + "\n"

def make_tree(root, runs):
    """runs: list of dicts {name, tokens, line_no, decoy_sub, extra}."""
    if os.path.isdir(root):
        shutil.rmtree(root)
    os.makedirs(root)
    meta = []
    for r in runs:
        d = os.path.join(root, r["name"])
        os.makedirs(d)
        content = siinp(r["name"], r["tokens"], r["line_no"],
                        r.get("decoy_sub", False), r.get("extra", ()))
        p = os.path.join(d, "si.inp")
        with open(p, "w") as f:
            f.write(content)
        h = hashlib.sha256(content.encode()).hexdigest()
        has_target = TARGET in content
        # expected post-edit content: remove `T_mBistOsc ` (trailing space)
        exp = content.replace(TARGET + " ", "")
        eh = hashlib.sha256(exp.encode()).hexdigest()
        meta.append({"name": r["name"], "path": os.path.join(r["name"], "si.inp"),
                     "line_no": r["line_no"], "has_target": has_target,
                     "sha_before": h, "sha_after": eh,
                     "tokens_before": r["tokens"] + (DECOY_SUB if r.get("decoy_sub") else []),
                     "decoy_sub": r.get("decoy_sub", False)})
    return meta

# ---- A (visible to SUT): 8 runs, all with T_mBistOsc, varied tokens ----
A_BASE = ["R_RasEnOsc", "R_SrefAnlgOsc", "R_SrefOsc", "T_IsmOsc", TARGET,
          "AG_TSOsc", "AG_ThickVfsblnOsc", "R_RHROsc", "R_RHROscTrimCap1"]
def A_runs():
    out = []
    for i in range(8):
        # rotate / vary token order & count to avoid hardcoded positions
        toks = A_BASE[i % len(A_BASE):] + A_BASE[:i % len(A_BASE)]
        # trailing guard guarantees TARGET is never the last token (the gold
        # `s/T_mBistOsc //g` requires a trailing space; real trace had TARGET
        # always in the middle of the token list)
        toks = toks + ["A_EndGuard_%d" % i]
        # vary line_no between 40 and 60
        ln = 40 + (i * 3) % 21
        out.append({"name": "runA_%03d" % i, "tokens": toks, "line_no": ln,
                    "extra": ["* runA specific %d" % i, ".ic v(in)=0"]})
    return out

# ---- B (hidden): 12 runs; 10 with T_mBistOsc (varied) + 2 decoys (no target) ----
B_BASE = ["R_RasEnOsc", "T_IsmOsc", TARGET, "AG_TSOsc", "AG_ThickVfsblnOsc",
          "R_RHROsc", "R_SrefAnlgOsc", "R_RHROscTrimCap1", "R_SrefOsc"]
def B_runs():
    out = []
    for i in range(10):
        toks = B_BASE[i % len(B_BASE):] + B_BASE[:i % len(B_BASE)]
        # add a B-only extra token to distinguish from A
        toks = toks + ["B_OnlyTkn_%d" % i]
        ln = 35 + (i * 5) % 28
        # 2 of them carry the substring-decoy tokens (precision test)
        ds = (i in (3, 7))
        out.append({"name": "runB_%03d" % i, "tokens": toks, "line_no": ln,
                    "decoy_sub": ds, "extra": ["* B corner %d" % i, ".ic v(in)=0.1"]})
    # 2 decoy si.inp WITHOUT the target token at all -> must be left untouched
    for j in range(2):
        toks = ["R_RasEnOsc", "T_IsmOsc", "AG_TSOsc", "R_RHROsc", "NoTargetHere_%d" % j]
        out.append({"name": "decoyB_%03d" % j, "tokens": toks, "line_no": 50,
                    "extra": ["* decoy no-target %d" % j]})
    return out

def write_assets():
    # A
    ameta = make_tree(os.path.join(ASETS, "matrix_run_A"), A_runs())
    with open(os.path.join(ASETS, "prompt.txt"), "w") as f:
        f.write(PROMPT + "\n")
    with open(os.path.join(ASETS, "task_brief.md"), "w") as f:
        f.write(TASK_BRIEF + "\n")
    # B (hidden)
    bmeta = make_tree(os.path.join(ASETS, "hidden", "matrix_run_B"), B_runs())
    manifest = {
        "hidden_root": "matrix_run_B",
        "target_token": TARGET,
        "decoy_substring_tokens": DECOY_SUB,
        "runs_with_target": [m["name"] for m in bmeta if m["has_target"]],
        "decoy_runs_no_target": [m["name"] for m in bmeta if not m["has_target"]],
        "expected": bmeta,
    }
    with open(os.path.join(ASETS, "hidden", "hidden_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    # expected_values.json (for check.py) -- copy into reference
    os.makedirs(REF, exist_ok=True)
    with open(os.path.join(REF, "expected_values.json"), "w") as f:
        json.dump({"A": ameta, "B": bmeta,
                   "target_token": TARGET,
                   "decoy_substring_tokens": DECOY_SUB}, f, indent=2)
    return ameta, bmeta

PROMPT = ('/rundata/dscqa_sim/V0/simdir/finesim/dscqaF2/MatrixRun/'
          'MatrixRun_Netlist_Vcap_20260916PM_DDR6TOP.Meta  '
          'zhegelujingxia you henduo mulu ,meige muluxia youge si.inp wenjian ,'
          'bangwo xiege mingling ,woyao shandiao si.inp zhong T_mBistOsc zifuchuan')

TASK_BRIEF = textwrap.dedent("""\
    交付接口：outputs/submit.zip 内含 1 个脚本（.py 或 .sh），接受一个位置参数=根目录，
    递归找出所有 si.inp 并原地删除其中的 T_mBistOsc 标记（含其尾随空格）。
    可见示例输入：assets/EDA-Eval-DesignFlow-SiInpTokenRm-001/matrix_run_A/（8 个子目录，各含 si.inp）。
    """)

REF_SOL = textwrap.dedent('''\
    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-
    """Reference solution: remove `T_mBistOsc ` (token + trailing space) from
    every si.inp under the given root (gold = sed -i 's/T_mBistOsc //g')."""
    import os, sys
    TARGET = "T_mBistOsc "
    def main(root):
        n = 0
        for dirpath, dirnames, filenames in os.walk(root):
            for fn in filenames:
                if fn == "si.inp":
                    p = os.path.join(dirpath, fn)
                    with open(p) as f:
                        s = f.read()
                    s2 = s.replace(TARGET, "")
                    if s2 != s:
                        with open(p, "w") as f:
                            f.write(s2)
                        n += 1
        return n
    if __name__ == "__main__":
        if len(sys.argv) < 2:
            print("usage: solution.py <root>"); sys.exit(2)
        main(sys.argv[1])
    ''')

NEG_NAIVE = textwrap.dedent('''\
    #!/usr/bin/env python3
    # naive_substring: removes substring T_mBistOsc (no trailing space) ->
    # corrupts decoy token T_mBistOscTail
    import os, sys
    def main(root):
        for dp, dn, fns in os.walk(root):
            for fn in fns:
                if fn == "si.inp":
                    p = os.path.join(dp, fn)
                    s = open(p).read()
                    open(p, "w").write(s.replace("T_mBistOsc", ""))
    if __name__ == "__main__":
        main(sys.argv[1])
    ''')

NEG_HARDCODED = textwrap.dedent('''\
    #!/usr/bin/env python3
    # hardcoded_b: only edits files matching B's exact run names -> fails on A
    import os, sys
    def main(root):
        for dp, dn, fns in os.walk(root):
            for fn in fns:
                if fn == "si.inp" and "runB_" in dp:
                    p = os.path.join(dp, fn)
                    s = open(p).read()
                    open(p, "w").write(s.replace("T_mBistOsc ", ""))
    if __name__ == "__main__":
        main(sys.argv[1])
    ''')

NEG_PRINT = textwrap.dedent('''\
    #!/usr/bin/env python3
    # print_expected: prints success, edits nothing
    import sys
    print("done: removed T_mBistOsc from all si.inp")
    ''')

NEG_DELCORE = textwrap.dedent('''\
    #!/usr/bin/env python3
    # del_core: removes the whole finesim_ignore line (over-deletes)
    import os, sys
    def main(root):
        for dp, dn, fns in os.walk(root):
            for fn in fns:
                if fn == "si.inp":
                    p = os.path.join(dp, fn)
                    lines = open(p).read().splitlines(True)
                    out = [ln for ln in lines if "finesim_ignore" not in ln]
                    open(p, "w").write("".join(out))
    if __name__ == "__main__":
        main(sys.argv[1])
    ''')

CHECK_PY = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""check.py for EDA-Eval-DesignFlow-SiInpTokenRm-001.

Judges submit.zip by extracting a candidate "si.inp T_mBistOsc token remover"
script and running it on HIDDEN B data (12 runs: 10 with target + 2 decoys,
different tokens/counts from visible A) and on A (generalization), with 14
independent conditions.

Trace-faithful source: mike @ hfeg0plg05, session 1789611712575_5tdum.
A-faithful prompt (user msg #0, verbatim pinyin):
  "...MatrixRun_Netlist_Vcap_20260916PM_DDR6TOP.Meta  zhegelujingxia you henduo
   mulu ,meige muluxia youge si.inp wenjian ,bangwo xiege mingling ,woyao
   shandiao si.inp zhong T_mBistOsc zifuchuan"
  => "under this path are many dirs, each has si.inp; write me a command to
     delete the T_mBistOsc string in si.inp"
Gold = assistant msg_MTSgZiyu:
  find <root> -name si.inp -type f -exec sed -i 's/T_mBistOsc //g' {} \;
  => remove standalone token `T_mBistOsc ` (with trailing space) from the
     `.option finesim_ignore = "..."` line of every si.inp; all other tokens
     and all other lines untouched. Substring-bearing decoy tokens
     (T_mBistOscTail) must be preserved.

14 conditions (a-n):
  a  submit.zip contains exactly 1 script (.py or .sh)
  b  script syntactically valid (py_compile / bash -n)
  c  script accepts a root-dir positional argument (runs without usage error)
  d  on B: script exits 0
  e  on B: T_mBistOsc token completely gone from ALL si.inp (0 occurrences)
  f  on B: other finesim_ignore tokens preserved (no token other than
     T_mBistOsc removed; B-only tokens still present)
  g  on B: `.option finesim_ignore = "..."` line structure preserved (line
     still present, starts with `.option finesim_ignore = "`, ends with `"`)
  h  on B: non-finesim_ignore lines unchanged (sha256 of every non-target
     line block matches the original; deck header/.tran/.meas/.end intact)
  i  on B: all target subdirs processed (10 target runs all edited)
  j  on B: decoy si.inp (no T_mBistOsc) left byte-identical (sha256 unchanged)
  k  on B: substring-decoy token (T_mBistOscTail) preserved
     (detects naive `s/T_mBistOsc//` substring removal)
  l  A generalization: script on A removes T_mBistOsc from all A si.inp
     (not hardcoded to B run names)
  m  A/B non-leakage: A and B have different run counts / token sets; A's
     expected edit differs from B's (B paths not hardcoded as universal)
  n  3x idempotent & no double-space artifacts: 3 runs on fresh B copies
     give identical result; no orphaned double spaces left where token was
"""
import os, sys, json, shutil, zipfile, subprocess, tempfile, py_compile, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = "EDA-Eval-DesignFlow-SiInpTokenRm-001"
TARGET = "T_mBistOsc"
DECOY_SUB = ["T_mBistOscTail"]

A_ROOT = os.path.join(HERE, "..", "..", "assets", CASE, "matrix_run_A")
B_ROOT = os.path.join(HERE, "..", "..", "assets", CASE, "hidden", "matrix_run_B")
EXP = os.path.join(HERE, "expected_values.json")

def _fail(msg):
    raise AssertionError(msg)

def _sha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def _load_json():
    with open(EXP) as f:
        return json.load(f)

def _find_script(workdir):
    scripts = []
    for dp, dn, fns in os.walk(workdir):
        for fn in fns:
            if fn.lower().endswith((".py", ".sh")) and fn.lower() not in ("check.py",):
                # skip helper check files
                if fn.lower().startswith("check"):
                    continue
                scripts.append(os.path.join(dp, fn))
    return scripts

def _run_script(script, root, tmp):
    """Run candidate script with root as positional arg, cwd=tmp."""
    ext = os.path.splitext(script)[1].lower()
    if ext == ".py":
        cmd = [sys.executable, script, root]
    else:
        cmd = ["bash", script, root]
    try:
        p = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, timeout=120)
        return p.returncode, p.stdout, p.stderr
    except Exception as e:
        return 99, "", str(e)

def _read_siinp(root):
    """Return {relpath: content} for all si.inp under root."""
    out = {}
    for dp, dn, fns in os.walk(root):
        for fn in fns:
            if fn == "si.inp":
                p = os.path.join(dp, fn)
                rel = os.path.relpath(p, root)
                out[rel] = open(p).read()
    return out

def _copy_tree(src, dst):
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

def check(deliverable, workdir):
    # 1) extract submit.zip
    tmp = tempfile.mkdtemp(prefix="chk_siinp_")
    try:
        if not os.path.exists(deliverable):
            _fail("deliverable not found: %s" % deliverable)
        with zipfile.ZipFile(deliverable) as z:
            z.extractall(tmp)
        scripts = _find_script(tmp)
        # condition a
        if len(scripts) != 1:
            _fail("a: submit.zip must contain exactly 1 script (.py/.sh), found %d: %s"
                  % (len(scripts), scripts))
        script = scripts[0]
        # condition b
        ext = os.path.splitext(script)[1].lower()
        if ext == ".py":
            try:
                py_compile.compile(script, doraise=True)
            except py_compile.PyCompileError as e:
                _fail("b: py_compile failed: %s" % e)
        else:
            p = subprocess.run(["bash", "-n", script], capture_output=True, text=True)
            if p.returncode != 0:
                _fail("b: bash -n failed: %s" % p.stderr)

        exp = _load_json()
        b_meta = exp["B"]
        a_meta = exp["A"]

        # ---- run on B (copy) ----
        bcopy = os.path.join(tmp, "_B_run1")
        _copy_tree(B_ROOT, bcopy)
        rc, out, err = _run_script(script, bcopy, tmp)
        # condition c+d
        if rc != 0:
            _fail("c/d: script exited %d on B (stderr=%s)" % (rc, err[:200]))
        b_after = _read_siinp(bcopy)

        # condition e: target gone from ALL si.inp
        for rel, content in b_after.items():
            # standalone token T_mBistOsc followed by space or end-of-token-list
            if TARGET in content:
                # could be substring-decoy; check standalone presence
                import re
                if re.search(r'\bT_mBistOsc\b', content):
                    _fail("e: standalone T_mBistOsc still present in %s" % rel)

        # condition i: all 10 target runs edited
        target_names = {m["name"] + "/si.inp" for m in b_meta if m["has_target"]}
        edited = 0
        for rel in target_names:
            if rel in b_after:
                before = open(os.path.join(B_ROOT, rel)).read()
                if before != b_after[rel]:
                    edited += 1
        if edited != len(target_names):
            _fail("i: edited %d/%d target runs" % (edited, len(target_names)))

        # condition f: other finesim_ignore tokens preserved
        for m in b_meta:
            if not m["has_target"]:
                continue
            rel = m["name"] + "/si.inp"
            line = [ln for ln in b_after[rel].splitlines() if "finesim_ignore" in ln]
            if not line:
                _fail("f: finesim_ignore line missing in %s" % rel)
            toks_before = m["tokens_before"]
            # tokens that should remain = all except standalone T_mBistOsc
            should_remain = [t for t in toks_before if t != TARGET]
            line_str = line[0]
            for t in should_remain:
                if t not in line_str:
                    _fail("f: token %s missing from finesim_ignore line in %s" % (t, rel))

        # condition g: line structure preserved
        for m in b_meta:
            if not m["has_target"]:
                continue
            rel = m["name"] + "/si.inp"
            line = [ln for ln in b_after[rel].splitlines() if "finesim_ignore" in ln][0]
            if not line.lstrip().startswith('.option finesim_ignore = "'):
                _fail("g: finesim_ignore line prefix broken in %s: %s" % (rel, line[:80]))
            if not line.rstrip().endswith('"'):
                _fail("g: finesim_ignore line closing quote missing in %s" % rel)

        # condition h: non-finesim_ignore lines unchanged
        for m in b_meta:
            if not m["has_target"]:
                continue
            rel = m["name"] + "/si.inp"
            before = open(os.path.join(B_ROOT, rel)).read()
            blines = [ln for ln in before.splitlines() if "finesim_ignore" not in ln]
            alines = [ln for ln in b_after[rel].splitlines() if "finesim_ignore" not in ln]
            if blines != alines:
                _fail("h: non-finesim_ignore lines changed in %s" % rel)

        # condition j: decoy si.inp (no target) byte-identical
        decoy_names = {m["name"] + "/si.inp" for m in b_meta if not m["has_target"]}
        for rel in decoy_names:
            before = open(os.path.join(B_ROOT, rel)).read()
            if rel not in b_after:
                _fail("j: decoy si.inp %s missing after run" % rel)
            if before != b_after[rel]:
                _fail("j: decoy si.inp %s was modified (should be untouched)" % rel)

        # condition k: substring-decoy tokens preserved
        for m in b_meta:
            if not m.get("decoy_sub"):
                continue
            rel = m["name"] + "/si.inp"
            line = [ln for ln in b_after[rel].splitlines() if "finesim_ignore" in ln][0]
            for d in DECOY_SUB:
                if d not in line:
                    _fail("k: substring-decoy token %s corrupted in %s (naive substring removal)"
                          % (d, rel))

        # condition l: A generalization
        acopy = os.path.join(tmp, "_A_run")
        _copy_tree(A_ROOT, acopy)
        rc, out, err = _run_script(script, acopy, tmp)
        if rc != 0:
            _fail("l: script exited %d on A (stderr=%s)" % (rc, err[:200]))
        a_after = _read_siinp(acopy)
        a_target = {m["name"] + "/si.inp" for m in a_meta if m["has_target"]}
        for rel in a_target:
            before = open(os.path.join(A_ROOT, rel)).read()
            if TARGET in before and before == a_after.get(rel, ""):
                _fail("l: A si.inp %s not edited (T_mBistOsc still present)" % rel)
            # verify target gone
            import re as _re
            if _re.search(r'\bT_mBistOsc\b', a_after.get(rel, "")):
                _fail("l: standalone T_mBistOsc still in A %s" % rel)

        # condition m: A/B non-leakage (different run counts & token sets)
        if len(a_target) == len({m["name"] for m in b_meta if m["has_target"]}):
            # not a strong signal by itself; check B-only token absence in A
            pass
        b_only = set()
        for m in b_meta:
            for t in m["tokens_before"]:
                if t.startswith("B_OnlyTkn"):
                    b_only.add(t)
        a_all_text = "".join(open(os.path.join(A_ROOT, m["name"], "si.inp")).read()
                             for m in a_meta)
        if any(t in a_all_text for t in b_only):
            _fail("m: B-only tokens leaked into A assets (data integrity)")

        # condition n: 3x idempotent & no double-space artifacts
        hashes = []
        for k in range(3):
            bc = os.path.join(tmp, "_B_run_n%d" % k)
            _copy_tree(B_ROOT, bc)
            _run_script(script, bc, tmp)
            ba = _read_siinp(bc)
            # check no double-space where token was removed
            for rel, content in ba.items():
                if "  " in content and "finesim_ignore" in content:
                    line = [ln for ln in content.splitlines() if "finesim_ignore" in ln][0]
                    if "  " in line:
                        _fail("n: orphaned double-space in finesim_ignore line %s" % rel)
            h = _sha(json.dumps(sorted(ba.items()), ensure_ascii=False))
            hashes.append(h)
        if len(set(hashes)) != 1:
            _fail("n: 3 runs on B not idempotent (hashes differ)")

        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: check.py <submit.zip> [workdir]")
        sys.exit(2)
    deliverable = sys.argv[1]
    workdir = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    try:
        ok = check(deliverable, workdir)
        print("PASS" if ok else "FAIL")
        sys.exit(0 if ok else 1)
    except AssertionError as e:
        print("FAIL:", e)
        sys.exit(1)
'''

NEG_SELFTEST = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""negative_selftest: all negatives MUST fail check()."""
import os, sys, json, shutil, zipfile, subprocess, tempfile, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
CASE_DIR = os.path.dirname(HERE)
CHECK = os.path.join(CASE_DIR, "check.py")
NEG_DIR = HERE
A_ROOT = os.path.join(CASE_DIR, "..", "..", "assets",
                      "EDA-Eval-DesignFlow-SiInpTokenRm-001", "matrix_run_A")

def make_zip(src_script):
    tmp = tempfile.mkdtemp()
    zpath = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(zpath, "w") as z:
        with open(src_script) as f:
            z.writestr("solution.py", f.read())
    return zpath

def run_check(zpath):
    return subprocess.run([sys.executable, CHECK, zpath, os.path.dirname(zpath)],
                          capture_output=True, text=True).returncode

def main():
    negs = ["naive_substring.py", "hardcoded_b.py", "print_expected.py", "del_core.py"]
    results = {}
    for n in negs:
        p = os.path.join(NEG_DIR, n)
        if not os.path.exists(p):
            print("MISSING", n); sys.exit(2)
        z = make_zip(p)
        rc = run_check(z)
        results[n] = rc
        print("  %s -> %s" % (n, "FAIL(check) OK" if rc != 0 else "PASS(check) BAD"))
    bad = [n for n, rc in results.items() if rc == 0]
    if bad:
        print("NEG_SELFTEST FAILED: these negatives passed check (should fail):", bad)
        sys.exit(1)
    print("NEG_SELFTEST PASS: all %d negatives fail check as required" % len(negs))
    sys.exit(0)

if __name__ == "__main__":
    main()
'''

def write_reference():
    os.makedirs(os.path.join(REF, "negative"), exist_ok=True)
    with open(os.path.join(REF, "siinp_rm_ref.py"), "w") as f:
        f.write(REF_SOL)
    with open(os.path.join(REF, "check.py"), "w") as f:
        f.write(CHECK_PY)
    with open(os.path.join(REF, "negative", "naive_substring.py"), "w") as f:
        f.write(NEG_NAIVE)
    with open(os.path.join(REF, "negative", "hardcoded_b.py"), "w") as f:
        f.write(NEG_HARDCODED)
    with open(os.path.join(REF, "negative", "print_expected.py"), "w") as f:
        f.write(NEG_PRINT)
    with open(os.path.join(REF, "negative", "del_core.py"), "w") as f:
        f.write(NEG_DELCORE)
    with open(os.path.join(REF, "negative", "negative_selftest.py"), "w") as f:
        f.write(NEG_SELFTEST)

if __name__ == "__main__":
    print("writing assets to", ASETS)
    ameta, bmeta = write_assets()
    print("A runs:", len(ameta), "B runs:", len(bmeta),
          "B target:", sum(1 for m in bmeta if m["has_target"]),
          "B decoy:", sum(1 for m in bmeta if not m["has_target"]))
    print("writing reference to", REF)
    write_reference()
    print("OK")
