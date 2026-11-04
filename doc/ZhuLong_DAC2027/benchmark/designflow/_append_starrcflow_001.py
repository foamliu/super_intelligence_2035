#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-StarRCFlow-001 to EDA-Eval-DesignFlow_A.jsonl."""
import os, json

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-StarRCFlow-001"
JSONL = os.path.join(ROOT, "EDA-Eval-DesignFlow_A.jsonl")
R_DIR = os.path.join(ROOT, "reference", CASE)
A_DIR = os.path.join(ROOT, "assets", CASE)

# de-dup guard
existing = set()
with open(JSONL) as f:
    for line in f:
        line = line.strip()
        if not line: continue
        try:
            o = json.loads(line)
            existing.add(o.get("task_id"))
        except Exception: pass
if CASE in existing:
    print("ALREADY_PRESENT:", CASE); raise SystemExit(0)

with open(os.path.join(R_DIR, "check.py")) as f:
    check_src = f.read()

prompt = open(os.path.join(A_DIR, "prompt.txt")).read()

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": [
        "assets/%s/prompt.txt" % CASE,
        "assets/%s/task_brief.md" % CASE,
        "assets/%s/feint/run_gxtr_MULTI_CORNER_template.csh" % CASE,
        "assets/%s/feint/CCI_cmd_sample" % CASE,
        "assets/%s/feint/extract_rc_sample.py" % CASE,
        "assets/%s/CCI_data/cell.list" % CASE,
        "assets/%s/hidden/hidden_manifest.json" % CASE,
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": [
        "setup_and_run.sh",
        "run_gxtr_MULTI_CORNER.csh",
        "autorun_gxtr_v0d1.csh",
        "extract_rc.py",
        "extract_net_info.py",
    ],
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "simplec",
            "host": "hfeg0pkn002",
            "session_file": "1792031425233_njd2w.messages.json",
            "match_count": 118,
            "real_task_summary": "StarRC multi-corner RC extraction flow automation: version switch / cell.list management / timestamp output dir / SPF RC parsing"
        },
        "domain": "pnr_signoff",
        "verb": "starrc-rc-extract-flow",
        "level": "L2",
        "track": "B",
        "test_rationale": ("16 \u6761\u65ad\u8a00\uff1a\u2460 zip \u542b 5 \u4ea4\u4ed8\u811a\u672c \u2461 setup_and_run.sh \u8bed\u6cd5 OK \u4e14\u53ef\u6267\u884c "
            "\u2462 --show-version \u62a5 StarXtract \u8def\u5f84+module \u2463 --cell-list first 5 \u6070 5 \u884c\u4e14\u6e90\u81ea B CCI_data "
            "\u2464 --cell-list random 3 \u6070 3 \u884c\u4e14\u968f\u673a \u2465 run_gxtr/autorun \u4ee5\u771f\u5b9e\u547d\u4ee4\u8c03 StarXtract \u4e14\u6709\u5faa\u73af "
            "\u2466 run_gxtr \u4ea7 done.list \u2467 run_gxtr \u65f6\u95f4\u6233\u76ee\u5f55\u540d\u5339\u914d yymmddHHMMSS "
            "\u2468 extract_rc.py \u4ea7\u5408\u6cd5 CSV \u4e14\u884c\u6570==B *|NET \u603b\u6570 \u2469 extract_net_info.py per-cell cap \u6c47\u603b\u4e0e SPF \u4e00\u81f4 "
            "\u246a --clean \u4fdd\u7559\u65e7 rundata \u246b --version \u5207\u6362\u540e\u62a5\u65b0 module \u246c \u8de8\u8f93\u5165\u62a4\u536b B token \u4e0d\u5728 A feint "
            "\u246d 3 \u79cd\u5b50\u91cd\u8dd1\u7ed3\u6784\u4e00\u81f4 \u246e SPF RC \u91cf\u7eb2\u5408\u7406 \u246f \u4e09\u5047\u63d0\u4ea4\uff08\u7a7a\u58f3/print-stub/core-deleted\uff09\u5747 FAIL"),
        "hidden_input": {
            "b_path": "hidden/%s/" % CASE,
            "b_files": ["cell.list", "sample.spf"],
            "diff_dims": ["pdk", "corner", "cell_names", "cell_count", "net_values"]
        },
        "l2_real_run": "check.py L2 真跑 = subprocess 真exec候选脚本 on hidden B: (c)(d)(e)(l)(k) 真跑 bash flow driver setup_and_run.sh (with fake module/StarXtract fixture in judge env; ALSO verified on .75 against REAL StarXtract binary -- module load ds/star/2020.09-SP5-4 -> /apps/synopsys/SRB/.../StarXtract; --version ds/star/2022.03-SP3 -> T-2022.03-SP3 path; cell-list first/random; --clean preserve old rundata all confirmed); (i)(j)(o) 真跑 pure-stdlib extract_rc.py/extract_net_info.py on B's real-format SPF; (f)(g)(h) static-assert run_gxtr/autorun structure (timestamp format + real StarXtract command) since actual StarXtract extraction needs full PDK DEF/LEF/TF not buildable in budget.",
        "harness": "pi",
        "notes": "B档 synthesized (A档 faithful 14轮太散，单轮闭环选 StarRC multi-corner flow driver with cell.list mgmt + version switch + SPF RC extract). SUT 沙盒不含 reference/hidden/jsonl/check.py (泄漏隔离 OK). negatives: 5 (fake_empty->c, fake_print_expected->d, fake_core_deleted->f, naive_no_version->c/l, naive_no_timestamp->h) + §4.9 three-fake (empty_shell->c, print_expected->d, core_deleted->f) all FAIL."
    }
}

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("APPENDED:", CASE)
print("jsonl lines now:", sum(1 for _ in open(JSONL)))
