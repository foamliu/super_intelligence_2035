#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-SiOutWarnDiag-001 to EDA-Eval-DesignFlow_B.jsonl."""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = "EDA-Eval-DesignFlow-SiOutWarnDiag-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")
REF = os.path.join(BENCH, "reference", CASE)
CHECK_PY = os.path.join(REF, "check.py")
ASSETS = os.path.join(BENCH, "assets", CASE)

check_src = open(CHECK_PY, "r").read()
disk_md5 = hashlib.md5(check_src.encode()).hexdigest()
disk_sz = os.path.getsize(CHECK_PY)

prompt = open(os.path.join(ASSETS, "prompt.txt")).read().strip()
task_brief = open(os.path.join(ASSETS, "task_brief.md")).read().strip()

rationale = (
    "14 条断言："
    "①(a) zip 含 si_out_warn_diag.py 且 py_compile 通过 "
    "②(b) B 运行 exit 0 且产出 diagnostic_report.json "
    "③(c) schema 完整（顶层 {header,tool_version,outcome,warnings,summary} + summary 7 子键 + header {version,start_time,host,design} 齐全） "
    "④(d) B summary.total==20 "
    "⑤(e) B by_category=={convergence:5,numerical:4,license:3,model:3,io:2,non_physical:1,memory:1,other:1} "
    "⑥(f) B by_severity=={warning:17,error:2,fatal:1} "
    "⑦(g) B top_category==convergence "
    "⑧(h) B has_errors==True 且 has_fatal==True "
    "⑨(i) B outcome==aborted（从 Job aborted 行派生） "
    "⑩(j) B header.version==X-2024.12-SP1-1/host==hfeg0plg77/design 前缀 Golden012 且 tool_version==header.version "
    "⑪(k) warnings 长度==20 且每条含 line_no(>0)/severity(三类)/category(八类)/message(非空) "
    "⑫(l) 分类正确性：fatal 行 category==license 且 message 含 exhausted；timestep 行→convergence；non-physical 行→non_physical "
    "⑬(m) 跨输入护栏 A 重跑 by_category==A GT{convergence:5,model:3,non_physical:2,numerical:2,license:2,memory:2,other:2,io:1}+outcome==completed+has_fatal==False+A≠B 且无 B 名（Golden012/hfeg0plg77）泄漏（击败 hardcode-B） "
    "⑭(n) 确定性 B 重跑两次 sha256 一致"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        "assets/%s/si_A.out" % CASE,
        "assets/%s/task_brief.md" % CASE,
    ],
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "zxtu",
            "host": "hfeg0pkn002",
            "session_file": "1791966728738_ad3nu.messages.json",
            "match_count": 19,
            "real_task_summary": (
                "FineSim/PrimeSim si.out 报告 warning 分析（A-faithful U@0 逐字「分析这个报告的warnning："
                "finesim.golden004_all_perbank_daily_4b4g_.../si.out」；trace 实为 agent 在文件系统定位 si.out "
                "未果的 file-search saga，从未读到文件；便携子技能=si.out 单文件 warning/error/fatal 按 8 类分类 + "
                "每条结构化（行号/严重度/类别/消息）+ summary（per-category count/by-severity/top_category/"
                "has_errors/has_fatal）+ outcome 派生）"
            ),
        },
        "domain": "spice_sim",
        "track": "faithful",
        "test_rationale": rationale,
    },
}

# byte-sync check
assert entry["test"] == check_src, "test field not byte-synced with disk check.py"
line = json.dumps(entry, ensure_ascii=False)
# verify round-trip
parsed = json.loads(line)
test_md5 = hashlib.md5(parsed["test"].encode()).hexdigest()
assert test_md5 == disk_md5, "md5 mismatch: test=%s disk=%s" % (test_md5, disk_md5)
assert len(parsed["test"]) == disk_sz, "size mismatch: test=%d disk=%d" % (len(parsed["test"]), disk_sz)

# count conditions in test rationale
import re
k_rat = rationale.count("①") + rationale.count("②") + rationale.count("③") + \
        rationale.count("④") + rationale.count("⑤") + rationale.count("⑥") + \
        rationale.count("⑦") + rationale.count("⑧") + rationale.count("⑨") + \
        rationale.count("⑩") + rationale.count("⑪") + rationale.count("⑫") + \
        rationale.count("⑬") + rationale.count("⑭")
# count check conditions (a-n)
k_check = len(re.findall(r'\b([a-n]):\s', check_src.split('def check')[1].split('return')[0]))
# more robust: count the conds keys
k_check2 = check_src.count('conds["')
print("k_rationale=%d  k_check(conds keys)=%d  disk_md5=%s  disk_sz=%d" %
      (k_rat, k_check2, disk_md5, disk_sz))
assert k_rat == 14 and k_check2 == 14, "GATE FAIL k_rat=%d k_check=%d" % (k_rat, k_check2)

with open(JSONL, "a") as f:
    f.write(line + "\n")
print("APPENDED to %s: %s" % (JSONL, CASE))
print("rationale head:", rationale[:80])
