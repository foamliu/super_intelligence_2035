#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Code-gen WaveView cases V0/V1/V2 comparison runner (task book 2026-11-17 16:3x redo).

Runs the THREE-ARM对照 on a SAMPLE of the 182 code_gen WaveView cases, graded by
designflow's ACTUAL check.py (hidden input B, local — no .75 sandbox needed).

Arms (single variable = whether a VQA tool is available to the coding agent):
  V0  baseline   = pi (deepseek-v4-pro-cloud) writes code with NO VQA tool.
  V1  +VQA base  = pi + vqa_ask.sh -> Qwen3.5-2B base  (:30001) available as a shell tool.
  V2  +VQA rft2  = pi + vqa_ask.sh -> Qwen3.5-2B rft2  (:30003) available as a shell tool.

The coding agent is `pi` (the designflow line's agent, deepseek-v4-pro-cloud), run with
--no-mcp (no eda_flow/.75 sandbox; these cases are pure-Python) and built-in bash/read/write
tools, so it develops + tests the deliverable script locally in the workdir.  VQA is exposed
as a plain shell script `vqa_ask.sh` (pi already has a bash tool) -> the agent may call it to
ask a vision model about a waveform/plot image.  This is the user's intended mechanism
("agent 调 VQA 问细节问题 -> 通过率是否上升"), NOT reduced to OCR.

Grading: imports each real designflow check.py from reference/<case>/check.py; oracles + hidden
B input are co-located there, so check.py runs locally on 36.15 with no external files.

Runner never decodes any image (vqa_ask.sh just forwards an HTTP call) -> audit stays clean.
"""
import json, os, re, sys, time, shutil, subprocess, importlib.util, zipfile

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
OUTD = "/tmp/wv_cg"
RESULTS = os.path.join(OUTD, "results.json")
LOG = os.path.join(OUTD, "runner.log")
PI = "/nasdata/app.e0031982/.local/node-22/bin/pi"
NODE22 = "/nasdata/app.e0031982/.local/node-22/bin"
VQA = {"V1": "http://127.0.0.1:30001/vqa", "V2": "http://127.0.0.1:30003/vqa"}
PER_TIMEOUT = 480
MODEL = "deepseek-v4-pro-cloud"

CASES = [
    "EDA-Eval-DesignFlow-DqTrtfMeasure-001",
    "EDA-Eval-DesignFlow-NandMcuAsm-001",
    "EDA-Eval-DesignFlow-FsdbMeasRunGen-001",
    "EDA-Eval-DesignFlow-VerdiFsdbLoadDiagnose-001",
]


def log(msg):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")



def load_full_records():
    recs = {}
    with open(os.path.join(BASE, "EDA-Eval-DesignFlow.jsonl")) as f:
        for l in f:
            o = json.loads(l)
            recs[o.get("task_id")] = o
    return recs


def vqa_script(arm):
    url = VQA[arm]
    return '#!/bin/bash\n# VQA tool: ask the Qwen3.5-2B vision model a question about a waveform/plot IMAGE.\n# Usage: bash vqa_ask.sh "<image_path_on_server>" "<question>"\nset -e\npython3 - "$1" "$2" <<\'PYEOF\'\nimport sys, json, urllib.request\nimg, q = sys.argv[1], sys.argv[2]\nbody = json.dumps({"image_path": img, "question": q, "max_new_tokens": 200, "temperature": 0.0}).encode()\nreq = urllib.request.Request("%s", data=body, headers={"Content-Type": "application/json"})\ntry:\n    print(json.loads(urllib.request.urlopen(req, timeout=120).read()).get("answer", ""))\nexcept Exception as e:\n    print("VQA_ERROR:", e, file=sys.stderr); sys.exit(2)\nPYEOF\n' % url


VQA_NOTE = """
## 可选 VQA 工具（vision 模型问答）
你还可以调用一个 VQA 视觉问答工具：`bash vqa_ask.sh "<image_path>" "<question>"`，
它会用 Qwen3.5-2B 视觉模型回答关于一张波形/plot 图像的问题（读数、pattern、细节）。
image_path 必须是 VQA 服务器可读的路径（.17 NFS）。当前可用的真题波形 PNG 在：
`/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/real_waveview_images/<case_id>/*.png`
（这些是其它 WaveView 题的波形图，未必与本题数据一致）。如果本题有波形数据文件，
你也可先用 python/matplotlib 把它画成 PNG 存到一个 .17 NFS 可读路径，再问 VQA。
是否使用 VQA 完全由你决定；不用也完全可以。
"""


def setup_workdir(case, arm, full):
    wd = os.path.join(OUTD, case, arm)
    if os.path.isdir(wd):
        shutil.rmtree(wd)
    os.makedirs(os.path.join(wd, "outputs"))
    adir = os.path.join(BASE, "assets", case)
    if os.path.isdir(adir):
        for fn in os.listdir(adir):
            src = os.path.join(adir, fn)
            if os.path.isfile(src) and fn != "hidden" and not fn.startswith("."):
                shutil.copy2(src, os.path.join(wd, fn))
    if arm in VQA:
        with open(os.path.join(wd, "vqa_ask.sh"), "w") as f:
            f.write(vqa_script(arm))
        os.chmod(os.path.join(wd, "vqa_ask.sh"), 0o755)
        with open(os.path.join(wd, "VQA_TOOL.md"), "w") as f:
            f.write(VQA_NOTE)
    return wd


def build_prompt(case, arm, full):
    brief = ""
    bf = os.path.join(BASE, "assets", case, "task_brief.md")
    if os.path.isfile(bf):
        brief = open(bf).read()
    req = ""
    rf = os.path.join(BASE, "assets", case, "requirements.json")
    if os.path.isfile(rf):
        req = open(rf).read()
    arms_extra = VQA_NOTE if arm in VQA else ""
    return """你在当前工作目录里完成一道 EDA 设计流评测题。工作目录里有题目说明文件 task_brief.md、
requirements.json，以及题目输入文件（A 组，可见）。判分器会在一个**不同的**隐藏输入 B 上跑你的脚本。

## 题目
%s

## 接口要求（requirements.json）
%s

## 工作步骤
1. 用 read 工具读 task_brief.md / requirements.json 及所有输入文件，弄清交付件要求。
2. 按要求写交付脚本（纯 Python，可用 bash 工具 `python3` 本地测试）。务必写成**通用**逻辑，
   不得硬编码 A 组的具体值（B 组的版本/路径/数值/用户/主机全不同）。
3. 用工作目录里的 A 组输入文件本地测试你的脚本（`python3 <script> <args>`），确认能跑、输出合法。
4. 把交付脚本（及 task_brief 要求的 method.md 等辅助文件）打包成 `outputs/submit.zip`。
   打包示例：`cd outputs && python3 -c "import zipfile; z=zipfile.ZipFile('submit.zip','w'); z.write('../<script>','<script>'); z.close()"`
   submit.zip 内文件名须与 task_brief 要求一致（平铺，不要嵌套目录）。
5. 完成后回复一行：`DONE: outputs/submit.zip`。

## 约束
- 只用工作目录；不要改 /nasdata 下任何源文件。
- 纯 Python，无需 EDA 商用工具。
%s
现在开始：先读 task_brief.md，再实现、本地测试、打包 outputs/submit.zip。
""" % (brief, req, arms_extra)


def run_pi(case, arm, wd, prompt):
    env = dict(os.environ)
    env["PATH"] = NODE22 + ":" + env.get("PATH", "")
    sess = os.path.join(wd, ".pisess")
    os.makedirs(sess, exist_ok=True)
    cmd = [PI, "--print", "--no-approve", "--no-mcp", "--no-context-files",
           "--model", MODEL, "--thinking", "medium",
           "--session-dir", sess, "--no-skills", "--no-prompt-templates",
           "--no-extensions", prompt]
    log("  pi launch (timeout %ds)..." % PER_TIMEOUT)
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=wd, env=env, capture_output=True,
                           text=True, timeout=PER_TIMEOUT)
        dt = time.time() - t0
        with open(os.path.join(wd, "pi_stdout.txt"), "w") as f:
            f.write(p.stdout or "")
        with open(os.path.join(wd, "pi_stderr.txt"), "w") as f:
            f.write(p.stderr or "")
        log("  pi done in %.1fs rc=%s" % (dt, p.returncode))
        return dt, p.returncode
    except subprocess.TimeoutExpired:
        log("  pi TIMEOUT after %.1fs" % (time.time() - t0))
        return (time.time() - t0), -99
    except Exception as e:
        log("  pi ERROR %s" % e)
        return (time.time() - t0), -1


def _zip_n(p):
    try:
        with zipfile.ZipFile(p) as z:
            return len(z.namelist())
    except Exception:
        return 0


def grade(case, arm, wd):
    submit = os.path.join(wd, "outputs", "submit.zip")
    if not os.path.isfile(submit):
        for root, _d, files in os.walk(wd):
            if "submit.zip" in files and ".pisess" not in root:
                submit = os.path.join(root, "submit.zip"); break
    if not os.path.isfile(submit):
        return {"verdict": False, "k_pass": 0, "k_total": 0,
                "detail": "no submit.zip produced", "submit_path": None, "n_zip_members": 0}
    cp = os.path.join(BASE, "reference", case, "check.py")
    if not os.path.isfile(cp):
        return {"verdict": False, "k_pass": 0, "k_total": 0,
                "detail": "check.py not found", "submit_path": submit, "n_zip_members": _zip_n(submit)}
    grader = ("import importlib.util, json, sys\n"
              "spec = importlib.util.spec_from_file_location('chk', %r)\n"
              "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
              "try:\n    r = m.check(%r, %r)\n"
              "except AssertionError as e:\n    print(json.dumps({'pass': False, 'err': str(e)})); sys.exit()\n"
              "except Exception as e:\n    print(json.dumps({'pass': False, 'err': 'RUNTIME:' + str(e)[:300]})); sys.exit()\n"
              "if isinstance(r, dict):\n    print(json.dumps(r, default=str))\n"
              "elif r is True:\n    print(json.dumps({'pass': True}))\n"
              "else:\n    print(json.dumps({'pass': False, 'ret': str(r)}))\n"
              % (cp, submit, wd))
    try:
        p = subprocess.run([sys.executable, "-c", grader], capture_output=True,
                           text=True, timeout=120)
        out = (p.stdout or "").strip()
        res = json.loads(out.splitlines()[-1]) if out else {"pass": False, "err": "no output"}
    except Exception as e:
        res = {"pass": False, "err": "grade error: " + str(e)[:200]}
    verdict = bool(res.get("pass") or res.get("ok"))
    conds = res.get("conditions") or []
    k_total = len(conds) if conds else 0
    k_pass = sum(1 for c in conds if c.get("ok")) if conds else (1 if verdict else 0)
    detail = res.get("err") or res.get("detail") or ""
    if conds:
        ff = next((c.get("detail") for c in conds if not c.get("ok")), "")
        detail = ff or detail
    return {"verdict": verdict, "k_pass": k_pass, "k_total": k_total,
            "detail": str(detail)[:200], "submit_path": submit,
            "n_zip_members": _zip_n(submit)}


def summarize(rows):
    by_arm = {"V0": [], "V1": [], "V2": []}
    [by_arm[r["arm"]].append(r) for r in rows]
    s = {}
    for arm, rs in by_arm.items():
        n = len(rs)
        npass = sum(1 for r in rs if r["verdict"])
        kt = sum(r["k_total"] for r in rs if r["k_total"])
        kp = sum(r["k_pass"] for r in rs if r["k_total"])
        s[arm] = {"n": n, "pass": npass, "rate": round(npass / n, 4) if n else None,
                  "k_pass": kp, "k_total": kt, "k_rate": round(kp / kt, 4) if kt else None}
    return s


def main():
    os.makedirs(OUTD, exist_ok=True)
    open(LOG, "w").close()
    full = load_full_records()
    sub = {}
    try:
        sub = {json.loads(l)["task_id"]: json.loads(l)
               for l in open(os.path.join(BASE, "EDA-Eval-DesignFlow-WaveView.jsonl"))}
    except Exception:
        pass
    log("RUNNER start | %d cases x 3 arms | model=%s" % (len(CASES), MODEL))
    rows = []
    for case in CASES:
        k_sub = (sub.get(case) or {}).get("k_conditions", "?")
        for arm in ["V0", "V1", "V2"]:
            log("=== %s / %s (k=%s) ===" % (case, arm, k_sub))
            wd = setup_workdir(case, arm, full.get(case, {}))
            prompt = build_prompt(case, arm, full.get(case, {}))
            dt, rc = run_pi(case, arm, wd, prompt)
            g = grade(case, arm, wd)
            row = {"case_id": case, "arm": arm, "k_conditions": k_sub,
                   "pi_seconds": round(dt, 1), "pi_rc": rc, **g}
            rows.append(row)
            log("  VERDICT=%s k=%s/%s n_zip=%s | %s"
                % (g["verdict"], g["k_pass"], g["k_total"], g["n_zip_members"], g["detail"][:80]))
            with open(RESULTS, "w") as fp:
                json.dump({"cases": CASES, "rows": rows}, fp, ensure_ascii=False, indent=2)
    summ = summarize(rows)
    log("SUMMARY: " + json.dumps(summ, ensure_ascii=False))
    with open(RESULTS) as fp:
        data = json.load(fp)
    data["summary"] = summ
    with open(RESULTS, "w") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)
    log("RUNNER done. results=%s" % RESULTS)


if __name__ == "__main__":
    main()


