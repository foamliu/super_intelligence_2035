#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-CstViewPrecheck-001 (analog_context, B-grade synthesized L1).

Trace: nibwl (ziyuny, mc154, 10.129.32.190). User wants to check if a cellview
'cstconfig' exists in Aether and delete it if so (pre-cleanup before Group Generator
re-runs), using ae.dbCVExist + ae.dbDelCV. Real skill script + private paths not
portable -> B-grade synthesized; live Aether not needed (mock pyAether provided by
check at runtime) -> L1.

Produce: cstconfig_precheck.py CLI that checks+deletes a cellview via pyAether and
writes a status report JSON. Check runs candidate against a mock pyAether (configured
via env vars) on visible A + hidden B (view absent) + hidden B2 (delete fails).
"""
import json, os, shutil, subprocess, sys, zipfile, hashlib, py_compile, tempfile

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-CstViewPrecheck-001"
REF = os.path.join(REPO, "reference", CID)
AST = os.path.join(REPO, "assets", CID)
HID = os.path.join(AST, "hidden")
NEG = os.path.join(REF, "negative")
for d in (REF, AST, HID, NEG):
    os.makedirs(d, exist_ok=True)

# ── prompt.txt ──
PROMPT = """你在帮一位模拟版图工程师 ziyuny 维护一个 Aether「Group Generator」自动化 skill。

## 背景
她的 skill `auto-group-generator` 每次跑都会在目标 cell 上生成一个名为 `cstconfig` 的 view。下次重跑前，如果旧的 `cstconfig` 残留，会干扰新的生成结果。她在会话里提了两个需求（原话）：

> 「我在aether中有一个view叫cstconfig，我知道可以使用接口 ae.dbDelCV删除它。现在我想要先确认这个view是否存在，存在的话，就删除它，应该怎么写if判断？」

> 「在 group_generate.py 这个脚本的第121行和120行之间的步骤，加上，检查是否存在cstconfig这个view，如果存在的话，就删掉这个view」

后来她又明确指定了要用哪两个 API（原话）：

> 「这里使用 ae.dbCVExist来确认cstconfig是否存在，使用ae.dbDelCV来删除」

## 你要做的
写一个**命令行工具 `cstconfig_precheck.py`**，在跑 Group Generator 之前做「预清理」：检查指定 lib/cell 下的某个 view 是否存在，存在就删除，不存在就跳过，最后写一份状态报告 JSON。

## pyAether API 契约（你只能用这两个 API 完成检查+删除）
- `ae.dbCVExist(lib=<str>, cell=<str>, view=<str>) -> bool` —— 返回 True 表示 view 存在，False 表示不存在。三个参数都直接传 Python 字符串即可。
- `ae.dbDelCV(lib=<str>, cell=<str>, view=<str>) -> bool` —— 删除该 view，返回 True 表示删除成功，False 表示删除失败。三个参数都直接传 Python 字符串。

> ⚠️ 不要用 `emyDMIsCellViewExist` / `emyCdbaNS` / `emyScalarName` 那一套——那套参数类型是 `emyScalarName`，构造麻烦且用户已明确否决。只能用 `dbCVExist` + `dbDelCV`。
> ⚠️ 你脚本里 `import pyAether as ae` 即可；判分时会由测试框架提供一个 mock 版本的 `pyAether` 模块（通过 `PYTHONPATH` 注入），你本地自测时也可以自己写一个返回 True/False 的 `pyAether.py` 放进工作目录。

## CLI 接口
```
cstconfig_precheck.py --lib <库名> --cell <cell名> --view <view名> --report-out <报告输出路径>
```

## 行为规则
1. 调用 `ae.dbCVExist(lib=args.lib, cell=args.cell, view=args.view)` 检查 view 是否存在。
2. 如果**存在**：调用 `ae.dbDelCV(lib=args.lib, cell=args.cell, view=args.view)` 删除它。
   - 删除成功（返回 True）→ `status = "deleted"`，退出码 0。
   - 删除失败（返回 False）→ `status = "delete_failed"`，退出码 1。
3. 如果**不存在**：不调用 `dbDelCV`，`status = "skipped"`，退出码 0。
4. 每一步都要用 `print("[INFO] ...")` 打日志（检查调用、返回值、删除调用、返回值、最终状态）。

## 输出：报告 JSON（写到 `--report-out` 指定路径）
必须是合法 JSON，含这 8 个键：
- `lib`：来自 `--lib`
- `cell`：来自 `--cell`
- `view`：来自 `--view`
- `existed`：bool，`dbCVExist` 的返回值
- `deleted`：bool，是否真的执行了删除且成功（不存在时为 False）
- `delete_ret`：`dbDelCV` 的返回值（未调用时为 `null`）
- `status`：`"deleted"` / `"skipped"` / `"delete_failed"` 之一
- `timestamp`：ISO 8601 字符串（如 `2026-11-07T22:51:00`）

## 真实例子（参考）
ziyuny 实际跑过这样的预清理（**这只是参考，你交付的工具要能处理任意 lib/cell/view**）：
```
python3 cstconfig_precheck.py \\
  --lib zyTest --cell VwlpRefAmpIP --view cstconfig \\
  --report-out precheck_report.json
```
她的真实日志里能看到 `dbCVExist(zyTest/VwlpRefAmpIP/cstconfig) -> True` 然后 `dbDelCV(...) -> True`，下一次重跑时 `dbCVExist -> False` 就跳过删除。

## 交付
把 `cstconfig_precheck.py` 打包成 `outputs/submit.zip`（zip 根目录放 `cstconfig_precheck.py` 一个文件即可）。

## 附件
- `spec_A.json`：A 组测试规格（lib=zyTest, cell=VwlpRefAmpIP, view=cstconfig；判分时 mock 会让 dbCVExist 返回 True、dbDelCV 返回 True）。
- `pyAether_sample.py`：一个本地自测用的 mock 样例（把它复制成 `pyAether.py` 放在工作目录，`import pyAether` 就能跑通；dbCVExist 返回 True、dbDelCV 返回 True）。

附件只供你理解接口和本地试跑。判分会用**隐藏的规格**（不同的 lib/cell/view、有的让 view 不存在、有的让删除失败）和**隐藏配置的 mock** 来验你的工具，所以**不要硬编码**附件里的 lib/cell/view 名。
"""
with open(os.path.join(AST, "prompt.txt"), "w") as f: f.write(PROMPT)

# ── task_brief.md (≤3 lines) ──
BRIEF = """## 交付接口
- 交付物：`outputs/submit.zip`，zip 根目录含 `cstconfig_precheck.py` 一个文件。
- CLI：`cstconfig_precheck.py --lib <lib> --cell <cell> --view <view> --report-out <path>`
- 行为：`ae.dbCVExist` 检查 view，存在则 `ae.dbDelCV` 删除；写 8 键报告 JSON；删除失败退出码 1。
- 判分用隐藏规格 + 隐藏 mock 跑你的工具，独立于附件。
"""
with open(os.path.join(AST, "task_brief.md"), "w") as f: f.write(BRIEF)

# ── spec_A.json ──
spec_A = {"lib": "zyTest", "cell": "VwlpRefAmpIP", "view": "cstconfig",
          "mock_exist": True, "mock_del_ret": True,
          "expect_status": "deleted", "expect_exit": 0}
with open(os.path.join(AST, "spec_A.json"), "w") as f: json.dump(spec_A, f, indent=2)

# ── pyAether_sample.py (candidate-local test mock, NOT used by check) ──
SAMPLE_MOCK = '''#!/usr/bin/env python3
"""Sample mock pyAether for local self-test. Copy to pyAether.py in your workdir.
dbCVExist -> True, dbDelCV -> True. Records calls to /tmp/cstview_calls.log."""
import json
_calls = []
def dbCVExist(lib=None, cell=None, view=None):
    _calls.append({"func":"dbCVExist","lib":lib,"cell":cell,"view":view}); return True
def dbDelCV(lib=None, cell=None, view=None):
    _calls.append({"func":"dbDelCV","lib":lib,"cell":cell,"view":view}); return True
def emyCdbaNS(): return None
def emyScalarName(ns, s): return s
import atexit
def _f():
    with open("/tmp/cstview_calls.log","w") as f:
        for c in _calls: f.write(json.dumps(c)+"\\n")
atexit.register(_f)
'''
with open(os.path.join(AST, "pyAether_sample.py"), "w") as f: f.write(SAMPLE_MOCK)

# ── hidden B (view absent -> skip) + B2 (delete fails) + manifest ──
spec_B = {"id": "B", "lib": "analogLib", "cell": "BandgapTop", "view": "cstconfig",
          "mock_exist": False, "mock_del_ret": True,
          "expect_status": "skipped", "expect_exit": 0}
spec_B2 = {"id": "B2", "lib": "phyLib", "cell": "DDR5Clk", "view": "cstcfg_v2",
           "mock_exist": True, "mock_del_ret": False,
           "expect_status": "delete_failed", "expect_exit": 1}
with open(os.path.join(HID, "spec_B.json"), "w") as f: json.dump(spec_B, f, indent=2)
with open(os.path.join(HID, "spec_B2.json"), "w") as f: json.dump(spec_B2, f, indent=2)
manifest = {"hidden_inputs": [spec_B, spec_B2],
            "note": "B: view absent -> skip; B2: delete fails -> exit1"}
with open(os.path.join(HID, "hidden_manifest.json"), "w") as f: json.dump(manifest, f, indent=2)

print("assets written under", AST)

# ── reference solution: cstconfig_precheck_ref.py ──
REF_PY = '''#!/usr/bin/env python3
"""cstconfig_precheck.py - Aether cellview pre-cleanup: check via dbCVExist, delete via dbDelCV.

Used before re-running Group Generator to remove a stale 'cstconfig' (or any) view so
the old config does not interfere with the new generation.

CLI: cstconfig_precheck.py --lib <lib> --cell <cell> --view <view> --report-out <path>
Exit 0 = ok (absent, or existed+deleted); 1 = delete failed.
"""
import argparse, datetime, json, sys


def main():
    ap = argparse.ArgumentParser(description="Aether cellview pre-cleanup check+delete")
    ap.add_argument("--lib", required=True)
    ap.add_argument("--cell", required=True)
    ap.add_argument("--view", required=True)
    ap.add_argument("--report-out", required=True)
    args = ap.parse_args()

    import pyAether as ae

    existed = False
    deleted = False
    delete_ret = None
    status = "skipped"

    print("[INFO] dbCVExist(lib=%s, cell=%s, view=%s) ..." % (args.lib, args.cell, args.view))
    existed = bool(ae.dbCVExist(lib=args.lib, cell=args.cell, view=args.view))
    print("[INFO] dbCVExist -> %r" % existed)

    if existed:
        print("[INFO] dbDelCV(lib=%s, cell=%s, view=%s) ..." % (args.lib, args.cell, args.view))
        delete_ret = ae.dbDelCV(lib=args.lib, cell=args.cell, view=args.view)
        print("[INFO] dbDelCV -> %r" % delete_ret)
        deleted = bool(delete_ret)
        status = "deleted" if deleted else "delete_failed"
    else:
        status = "skipped"
        print("[INFO] view absent, skip delete")

    report = {
        "lib": args.lib,
        "cell": args.cell,
        "view": args.view,
        "existed": existed,
        "deleted": deleted,
        "delete_ret": delete_ret,
        "status": status,
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
    }
    with open(args.report_out, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("[INFO] report written to %s (status=%s)" % (args.report_out, status))

    sys.exit(1 if status == "delete_failed" else 0)


if __name__ == "__main__":
    main()
'''
with open(os.path.join(REF, "cstconfig_precheck_ref.py"), "w") as f: f.write(REF_PY)

# ── check.py (16 conditions a-p) ──
CHECK_PY = r"""#!/usr/bin/env python3
'''check.py - CstViewPrecheck-001 grader (16 conditions a-p).

check(deliverable, workdir):
  deliverable = submit.zip (contains cstconfig_precheck.py)
  workdir     = assets dir (spec_A.json + hidden/)
Returns "PASS 16/16" or raises AssertionError(failing condition).
Uses a runtime-generated mock pyAether (configured via env vars) so no live Aether.
'''
import json, os, shutil, subprocess, sys, tempfile, zipfile, hashlib, py_compile

CID = "EDA-Eval-DesignFlow-CstViewPrecheck-001"
# A-specific anti-hardcode literals (must NOT appear in candidate source)
A_TOKENS = ["zyTest", "VwlpRefAmpIP"]


def _cond(label, ok, msg):
    if not ok:
        raise AssertionError("[%s] %s" % (label, msg))


MOCK_SRC = '''import os, json
_calls = []
def dbCVExist(lib=None, cell=None, view=None):
    _calls.append({"func":"dbCVExist","lib":lib,"cell":cell,"view":view})
    return os.environ.get("MOCK_EXIST","true").lower()=="true"
def dbDelCV(lib=None, cell=None, view=None):
    _calls.append({"func":"dbDelCV","lib":lib,"cell":cell,"view":view})
    return os.environ.get("MOCK_DEL_RET","true").lower()=="true"
def emyCdbaNS(): return None
def emyScalarName(ns, s): return s
def emyDMIsCellViewExist(*a, **k):
    _calls.append({"func":"emyDMIsCellViewExist"})
    return os.environ.get("MOCK_EXIST","true").lower()=="true"
import atexit
def _f():
    p=os.environ.get("MOCK_LOG")
    if p:
        with open(p,"w") as fh:
            for c in _calls: print(json.dumps(c), file=fh)
atexit.register(_f)
'''


def _make_mock(tmpdir):
    md = os.path.join(tmpdir, "mockpkg")
    os.makedirs(md, exist_ok=True)
    open(os.path.join(md, "pyAether.py"), "w").write(MOCK_SRC)
    return md


def _run(candidate_py, mock_dir, spec, report_out, log_path):
    env = dict(os.environ)
    env["PYTHONPATH"] = mock_dir + os.pathsep + env.get("PYTHONPATH", "")
    env["MOCK_EXIST"] = "true" if spec["mock_exist"] else "false"
    env["MOCK_DEL_RET"] = "true" if spec["mock_del_ret"] else "false"
    env["MOCK_LOG"] = log_path
    cmd = [sys.executable, candidate_py,
           "--lib", spec["lib"], "--cell", spec["cell"],
           "--view", spec["view"], "--report-out", report_out]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)


def _load_log(p):
    if not os.path.isfile(p):
        return []
    return [json.loads(l) for l in open(p) if l.strip()]


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check(deliverable, workdir):
    tmp = tempfile.mkdtemp(prefix="chk_cstview_")
    try:
        # (a) zip integrity + no leak + py_compile + has cstconfig_precheck.py
        _cond("a.zip-exists", os.path.isfile(deliverable), "submit.zip missing")
        names = zipfile.ZipFile(deliverable).namelist()
        _cond("a.no-leak",
              not any(os.path.basename(n) == "check.py" or "/reference/" in n
                      or n.endswith(".jsonl") or "/negative/" in n for n in names),
              "leak: check.py/reference/jsonl/negative in submit.zip")
        cand_name = None
        for n in names:
            if n.endswith("cstconfig_precheck.py") and not n.startswith("__"):
                cand_name = n; break
        _cond("a.has-cand", cand_name is not None, "no cstconfig_precheck.py in zip")
        zipfile.ZipFile(deliverable).extractall(tmp)
        cand_py = os.path.join(tmp, cand_name)
        try:
            py_compile.compile(cand_py, doraise=True)
        except py_compile.PyCompileError as e:
            _cond("a.py-compile", False, "compile error: %s" % e)

        src = open(cand_py).read()

        mock_dir = _make_mock(tmp)

        # locate specs
        spec_A = json.load(open(os.path.join(workdir, "spec_A.json")))
        hidden_dir = os.path.join(workdir, "hidden")
        manifest = json.load(open(os.path.join(hidden_dir, "hidden_manifest.json")))
        spec_B = [x for x in manifest["hidden_inputs"] if x["id"] == "B"][0]
        spec_B2 = [x for x in manifest["hidden_inputs"] if x["id"] == "B2"][0]

        # ── A run (existed -> deleted) ──
        a_out = os.path.join(tmp, "A_report.json")
        a_log = os.path.join(tmp, "A_log.jsonl")
        rA = _run(cand_py, mock_dir, spec_A, a_out, a_log)
        # (b) A-run exit0 + report file exists
        _cond("b.A-exit0", rA.returncode == 0,
              "A run exit=%d stderr=%s" % (rA.returncode, rA.stderr[:200]))
        _cond("b.A-report", os.path.isfile(a_out), "A report.json not created")
        repA = json.load(open(a_out))
        logA = _load_log(a_log)

        # (c) report JSON has 8 required keys
        need = {"lib", "cell", "view", "existed", "deleted", "delete_ret", "status", "timestamp"}
        _cond("c.report-keys", need <= set(repA.keys()),
              "report missing keys: %s" % (need - set(repA.keys())))

        # (d) A dbCVExist called once with correct lib/cell/view
        cv_calls = [c for c in logA if c.get("func") == "dbCVExist"]
        _cond("d.A-dbCVExist-called", len(cv_calls) == 1,
              "dbCVExist called %d times (expect 1)" % len(cv_calls))
        if cv_calls:
            c = cv_calls[0]
            _cond("d.A-dbCVExist-args",
                  c.get("lib") == spec_A["lib"] and c.get("cell") == spec_A["cell"]
                  and c.get("view") == spec_A["view"],
                  "dbCVExist args wrong: %r" % c)

        # (e) A existed == True
        _cond("e.A-existed-true", repA["existed"] is True,
              "A existed=%r != True" % repA["existed"])

        # (f) A dbDelCV called once with correct args
        del_calls = [c for c in logA if c.get("func") == "dbDelCV"]
        _cond("f.A-dbDelCV-called", len(del_calls) == 1,
              "dbDelCV called %d times (expect 1)" % len(del_calls))
        if del_calls:
            c = del_calls[0]
            _cond("f.A-dbDelCV-args",
                  c.get("lib") == spec_A["lib"] and c.get("cell") == spec_A["cell"]
                  and c.get("view") == spec_A["view"],
                  "dbDelCV args wrong: %r" % c)

        # (g) A deleted==True + delete_ret==True
        _cond("g.A-deleted-true", repA["deleted"] is True,
              "A deleted=%r != True" % repA["deleted"])
        _cond("g.A-delret-true", repA["delete_ret"] is True,
              "A delete_ret=%r != True" % repA["delete_ret"])

        # (h) A status == "deleted"
        _cond("h.A-status-deleted", repA["status"] == "deleted",
              "A status=%r != deleted" % repA["status"])

        # ── B run (view absent -> skip) ──
        b_out = os.path.join(tmp, "B_report.json")
        b_log = os.path.join(tmp, "B_log.jsonl")
        rB = _run(cand_py, mock_dir, spec_B, b_out, b_log)
        _cond("i.B-exit0", rB.returncode == 0, "B run exit=%d" % rB.returncode)
        logB = _load_log(b_log)
        cvB = [c for c in logB if c.get("func") == "dbCVExist"]
        delB = [c for c in logB if c.get("func") == "dbDelCV"]
        _cond("i.B-dbCVExist-called", len(cvB) == 1, "B dbCVExist not called once")
        _cond("i.B-dbDelCV-not-called", len(delB) == 0,
              "B dbDelCV called %d times (expect 0, view absent)" % len(delB))

        repB = json.load(open(b_out))
        # (j) B existed==False + deleted==False + status=="skipped"
        _cond("j.B-existed-false", repB["existed"] is False, "B existed=%r != False" % repB["existed"])
        _cond("j.B-deleted-false", repB["deleted"] is False, "B deleted=%r != False" % repB["deleted"])
        _cond("j.B-status-skipped", repB["status"] == "skipped",
              "B status=%r != skipped" % repB["status"])

        # ── B2 run (delete fails -> exit1) ──
        b2_out = os.path.join(tmp, "B2_report.json")
        b2_log = os.path.join(tmp, "B2_log.jsonl")
        rB2 = _run(cand_py, mock_dir, spec_B2, b2_out, b2_log)
        logB2 = _load_log(b2_log)
        delB2 = [c for c in logB2 if c.get("func") == "dbDelCV"]
        # (k) B2 dbDelCV called + returned False (mock_del_ret=False)
        _cond("k.B2-dbDelCV-called", len(delB2) == 1, "B2 dbDelCV not called")
        repB2 = json.load(open(b2_out))
        _cond("k.B2-delret-false", repB2["delete_ret"] is False,
              "B2 delete_ret=%r != False" % repB2["delete_ret"])

        # (l) B2 exit != 0 + status=="delete_failed"
        _cond("l.B2-exit-nonzero", rB2.returncode != 0,
              "B2 exit=%d (expect nonzero on delete fail)" % rB2.returncode)
        _cond("l.B2-status-failed", repB2["status"] == "delete_failed",
              "B2 status=%r != delete_failed" % repB2["status"])

        # (m) cross-input guard: B report lib/cell/view == B spec (not A's)
        _cond("m.B-lib", repB["lib"] == spec_B["lib"],
              "B report lib=%r != %r" % (repB["lib"], spec_B["lib"]))
        _cond("m.B-cell", repB["cell"] == spec_B["cell"],
              "B report cell=%r != %r" % (repB["cell"], spec_B["cell"]))
        _cond("m.B-view", repB["view"] == spec_B["view"],
              "B report view=%r != %r" % (repB["view"], spec_B["view"]))

        # (n) anti-hardcode: candidate source has no A-specific lib/cell literals
        found = [t for t in A_TOKENS if t in src]
        _cond("n.no-hardcode", not found,
              "candidate source hardcodes A tokens: %s" % found)

        # (o) determinism: run A 3x, mock call-log sha256 identical
        sha_set = set()
        for i in range(3):
            lo = os.path.join(tmp, "det_log_%d.jsonl" % i)
            ro = os.path.join(tmp, "det_rep_%d.json" % i)
            _run(cand_py, mock_dir, spec_A, ro, lo)
            sha_set.add(_sha(lo))
        _cond("o.deterministic", len(sha_set) == 1,
              "A mock-call-log sha256 not stable across 3 runs: %s" % sha_set)

        # (p) B2 report.view == "cstcfg_v2" (view read from CLI, not hardcoded "cstconfig")
        _cond("p.B2-view-cstcfg_v2", repB2["view"] == "cstcfg_v2",
              "B2 report view=%r != cstcfg_v2 (view not read from CLI)" % repB2["view"])

        return "PASS 16/16"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
"""
with open(os.path.join(REF, "check.py"), "w") as f: f.write(CHECK_PY)

# ── reference_submit.zip ──
submit_zip = os.path.join(REF, "reference_submit.zip")
if os.path.exists(submit_zip): os.remove(submit_zip)
with zipfile.ZipFile(submit_zip, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(REF, "cstconfig_precheck_ref.py"), arcname="cstconfig_precheck.py")
print("reference_submit.zip built")

# ── negatives (6 fakes) ──
NEG_EMPTY = '#!/usr/bin/env python3\nimport sys\n# empty shell: does nothing, no report\nsys.exit(0)\n'
NEG_PRINT = '''#!/usr/bin/env python3
# print_expected: calls the mock (so dbCVExist/dbDelCV recorded) but ALWAYS writes a
# HARDCODED "success" report (existed=True/deleted=True/status=deleted) regardless of
# what the mock actually returned. On B (view absent) report.existed=True -> j fails.
import argparse, datetime, json, sys
ap=argparse.ArgumentParser(); ap.add_argument("--lib",required=True); ap.add_argument("--cell",required=True)
ap.add_argument("--view",required=True); ap.add_argument("--report-out",required=True); a=ap.parse_args()
import pyAether as ae
ae.dbCVExist(lib=a.lib,cell=a.cell,view=a.view); ae.dbDelCV(lib=a.lib,cell=a.cell,view=a.view)
rep={"lib":a.lib,"cell":a.cell,"view":a.view,"existed":True,"deleted":True,
     "delete_ret":True,"status":"deleted","timestamp":datetime.datetime.now().isoformat(timespec="seconds")}
open(a.report_out,"w").write(json.dumps(rep)); sys.exit(0)
'''
NEG_CORE_DEL = '''#!/usr/bin/env python3
# core_deleted: real flow but dbDelCV call removed (only checks, never deletes)
import argparse, datetime, json, sys
ap=argparse.ArgumentParser(); ap.add_argument("--lib",required=True); ap.add_argument("--cell",required=True)
ap.add_argument("--view",required=True); ap.add_argument("--report-out",required=True); a=ap.parse_args()
import pyAether as ae
existed=bool(ae.dbCVExist(lib=a.lib,cell=a.cell,view=a.view))
deleted=False; delete_ret=None; status="skipped" if not existed else "delete_failed"
rep={"lib":a.lib,"cell":a.cell,"view":a.view,"existed":existed,"deleted":deleted,
     "delete_ret":delete_ret,"status":status,"timestamp":datetime.datetime.now().isoformat(timespec="seconds")}
open(a.report_out,"w").write(json.dumps(rep)); sys.exit(0)
'''
NEG_HARDCODE_A = '''#!/usr/bin/env python3
# naive_hardcode_a: hardcodes lib/cell, ignores --lib/--cell args
import argparse, datetime, json, sys
ap=argparse.ArgumentParser(); ap.add_argument("--lib",required=True); ap.add_argument("--cell",required=True)
ap.add_argument("--view",required=True); ap.add_argument("--report-out",required=True); a=ap.parse_args()
import pyAether as ae
LIB="zyTest"; CELL="VwlpRefAmpIP"  # hardcoded, ignore a.lib/a.cell
existed=bool(ae.dbCVExist(lib=LIB,cell=CELL,view=a.view))
deleted=False; delete_ret=None; status="skipped"
if existed:
    delete_ret=ae.dbDelCV(lib=LIB,cell=CELL,view=a.view); deleted=bool(delete_ret)
    status="deleted" if deleted else "delete_failed"
rep={"lib":LIB,"cell":CELL,"view":a.view,"existed":existed,"deleted":deleted,
     "delete_ret":delete_ret,"status":status,"timestamp":datetime.datetime.now().isoformat(timespec="seconds")}
open(a.report_out,"w").write(json.dumps(rep)); sys.exit(1 if status=="delete_failed" else 0)
'''
NEG_DEL_IGNORED = '''#!/usr/bin/env python3
# naive_delete_ignored: calls dbDelCV but ignores its return, always deleted=True + status="deleted"
import argparse, datetime, json, sys
ap=argparse.ArgumentParser(); ap.add_argument("--lib",required=True); ap.add_argument("--cell",required=True)
ap.add_argument("--view",required=True); ap.add_argument("--report-out",required=True); a=ap.parse_args()
import pyAether as ae
existed=bool(ae.dbCVExist(lib=a.lib,cell=a.cell,view=a.view))
deleted=False; delete_ret=None; status="skipped"
if existed:
    delete_ret=ae.dbDelCV(lib=a.lib,cell=a.cell,view=a.view)
    deleted=True  # ignore actual return
    status="deleted"  # always deleted, never delete_failed
rep={"lib":a.lib,"cell":a.cell,"view":a.view,"existed":existed,"deleted":deleted,
     "delete_ret":delete_ret,"status":status,"timestamp":datetime.datetime.now().isoformat(timespec="seconds")}
open(a.report_out,"w").write(json.dumps(rep)); sys.exit(0)  # always exit 0
'''
NEG_USE_EMYDM = '''#!/usr/bin/env python3
# naive_use_emyDM: uses emyDMIsCellViewExist instead of dbCVExist (wrong API per spec)
import argparse, datetime, json, sys
ap=argparse.ArgumentParser(); ap.add_argument("--lib",required=True); ap.add_argument("--cell",required=True)
ap.add_argument("--view",required=True); ap.add_argument("--report-out",required=True); a=ap.parse_args()
import pyAether as ae
ns=ae.emyCdbaNS()
existed=bool(ae.emyDMIsCellViewExist(ae.emyScalarName(ns,a.lib),ae.emyScalarName(ns,a.cell),ae.emyScalarName(ns,a.view)))
deleted=False; delete_ret=None; status="skipped"
if existed:
    delete_ret=ae.dbDelCV(lib=a.lib,cell=a.cell,view=a.view); deleted=bool(delete_ret)
    status="deleted" if deleted else "delete_failed"
rep={"lib":a.lib,"cell":a.cell,"view":a.view,"existed":existed,"deleted":deleted,
     "delete_ret":delete_ret,"status":status,"timestamp":datetime.datetime.now().isoformat(timespec="seconds")}
open(a.report_out,"w").write(json.dumps(rep)); sys.exit(1 if status=="delete_failed" else 0)
'''

negs = {
    "empty_shell.py": NEG_EMPTY,
    "print_expected.py": NEG_PRINT,
    "core_deleted.py": NEG_CORE_DEL,
    "naive_hardcode_a.py": NEG_HARDCODE_A,
    "naive_delete_ignored.py": NEG_DEL_IGNORED,
    "naive_use_emyDM.py": NEG_USE_EMYDM,
}
for nm, body in negs.items():
    with open(os.path.join(NEG, nm), "w") as f: f.write(body)
print("negatives written:", list(negs))

# ── negative_selftest.py ──
SELFTEST = r'''#!/usr/bin/env python3
"""negative_selftest.py - all 6 fakes must FAIL check(); 3 §4.9 fakes included."""
import json, os, shutil, sys, tempfile, zipfile, importlib.util

REF = os.path.dirname(os.path.abspath(__file__))
CID_DIR = REF
AST = os.path.join(os.path.dirname(REF), "..", "assets", "EDA-Eval-DesignFlow-CstViewPrecheck-001")
AST = os.path.abspath(AST)
NEG = os.path.join(REF, "negative")

spec = importlib.util.spec_from_file_location("check_mod", os.path.join(REF, "check.py"))
chk = importlib.util.module_from_spec(spec); spec.loader.exec_module(chk)

fakes = ["empty_shell.py", "print_expected.py", "core_deleted.py",
         "naive_hardcode_a.py", "naive_delete_ignored.py", "naive_use_emyDM.py"]

def make_zip(py_path):
    z = tempfile.mktemp(suffix=".zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(py_path, arcname="cstconfig_precheck.py")
    return z

results = {}
for fk in fakes:
    fp = os.path.join(NEG, fk)
    z = make_zip(fp)
    try:
        chk.check(z, AST)
        results[fk] = "PASS(BUG!)"
    except AssertionError as e:
        results[fk] = "FAIL @ " + str(e).splitlines()[0][:80]

print("=== negative_selftest ===")
allok = True
for fk, r in results.items():
    print("  %s -> %s" % (fk, r))
    if r.startswith("PASS"):
        allok = False
# distinct first_fail check
ff = [v.split("@")[1].strip().split()[0].strip("[") for v in results.values() if "FAIL" in v]
print("first_fails:", ff)
if len(set(ff)) != len(ff):
    print("WARN: non-distinct first_fails"); allok = False
print("NEG_RC=%d" % (0 if allok else 1))
sys.exit(0 if allok else 1)
'''
with open(os.path.join(REF, "negative_selftest.py"), "w") as f: f.write(SELFTEST)

# ── self-verify: ref PASS + negs FAIL ──
import importlib.util
spec = importlib.util.spec_from_file_location("check_mod", os.path.join(REF, "check.py"))
chk = importlib.util.module_from_spec(spec); spec.loader.exec_module(chk)
res = chk.check(submit_zip, AST)
print("REF CHECK:", res)
if not res.startswith("PASS"):
    print("!!! REF FAILED — aborting"); sys.exit(1)

# negatives selftest
r = subprocess.run([sys.executable, os.path.join(REF, "negative_selftest.py")],
                   capture_output=True, text=True)
print("NEG SELFTEST stdout:", r.stdout)
print("NEG SELFTEST stderr:", r.stderr[:500])
if r.returncode != 0:
    print("!!! NEG SELFTEST FAILED — aborting"); sys.exit(1)

# §4.9 three fakes (subset of negatives): empty_shell, print_expected, core_deleted
print("§4.9 three-fake check (empty/print/core): all in negative_selftest -> ALL FAIL verified above")

print("=== BUILD + SELFVERIFY OK ===")
print("REF:", REF)
print("AST:", AST)
