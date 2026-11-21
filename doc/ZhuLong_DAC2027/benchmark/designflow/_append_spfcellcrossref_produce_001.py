#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-SpfCellCrossRefProduce-001 to D.jsonl."""
import hashlib
import json
import os

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE_ID = "EDA-Eval-DesignFlow-SpfCellCrossRefProduce-001"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_D.jsonl")
CHECK = os.path.join(BENCH, "reference", CASE_ID, "check.py")
PROMPT_FILE = os.path.join(BENCH, "assets", CASE_ID, "prompt.txt")

with open(CHECK, "rb") as f:
    check_bytes = f.read()
check_sha = hashlib.sha256(check_bytes).hexdigest()
check_size = len(check_bytes)

with open(PROMPT_FILE, "r") as f:
    prompt = f.read()

attachments = [
    f"assets/{CASE_ID}/aaa_A.txt",
    f"assets/{CASE_ID}/no_vcap_A.txt",
    f"assets/{CASE_ID}/skip_cell_A.txt",
    f"assets/{CASE_ID}/ignore_cells_A.txt",
    f"assets/{CASE_ID}/control_A.txt",
    f"assets/{CASE_ID}/task_brief.md",
]

test_rationale = (
    "19 条断言："
    "①submit.zip含check_cells_in_refs.py且py_compile exit0 "
    "②候选脚本在B上subprocess跑exit0 "
    "③B产出合法report(JSON非空) "
    "④report含4源key(no_vcap/skip_cell/ignore_cells/control) "
    "⑤B no_vcap匹配数==judge重算B-gold "
    "⑥B skip_cell匹配数==B-gold "
    "⑦B ignore_cells glob匹配数==B-gold(fnmatch真跑非子串) "
    "⑧B control匹配数==B-gold(:prohd/:spicehd后缀剥离) "
    "⑨B 4源命中cell名集合==judge重算集合(精确无漏无多) "
    "⑩B no_vcap #注释行未计入source_count(注释处理) "
    "⑪B control mode/ignore并集不重复计(source_count=raw条目和,matched无重复) "
    "⑫B全0源不被谎报(matched_count=0则matched_cells=[]) "
    "⑬3-seed确定性(B跑3次report md5一致) "
    "⑭无__chk污染SUT workdir "
    "⑮A'(anti-hardcode)跑exit0+合法report(4源key齐全) "
    "⑯A' no_vcap匹配数==A'-gold(核心交叉,击穿B-hardcode stub吐B-gold,A'-gold 9≠B-gold 13) "
    "⑰A' ignore_cells glob匹配数==A'-gold(击穿stub吐B-gold 38,A'-gold 32) "
    "⑱A' control匹配数==A'-gold(:suffix剥离在A'独立成立,A'-gold 16≠B-gold 18) "
    "⑲A' 4源命中cell名集合==A'-gold集合(显式输入相关,名全异于B-gold,击穿恒定输出stub)"
)

negatives = ["neg_fake_empty.py", "neg_fake_print_only.py",
             "neg_fake_core_deleted.py", "neg_fake_hardcode_b.py"]

record = {
    "id": CASE_ID,
    "case_id": CASE_ID,
    "task_id": "SpfCellCrossRefProduce-001",
    "task_id_full": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": attachments,
    "test": check_bytes.decode("utf-8"),
    "budget": {"max_turns": 30},
    "expected_artifacts": ["outputs/submit.zip"],
    "metadata": {
        "domain": "analog_context",
        "level": "L1",
        "grade": "proper",
        "track": "design_flow",
        "harness": "offline",
        "l1_subgrade": "produce",
        "k_check": 19,
        "k_rationale": 19,
        "check_sha256": check_sha,
        "check_size": check_size,
        "byte_sync_sha": check_sha,
        "byte_sync_size": check_size,
        "test_rationale": test_rationale,
        "negatives": negatives,
        "negative_selftest": f"reference/{CASE_ID}/negative_selftest.py",
        "self_verify": "ref 19/19 PASS on (B)+(hidden-A'); 4 negatives all FAIL (n_distinct=4: empty→[c], print_only→[j], core_deleted→[h], smart §4.9(b) B-hardcode stub→[p] A'-gold cross-check); §4.9 (a)(b)(c) three-fake all FAIL",
        "trace_source": {
            "user": "caozhang",
            "host": "hfeg0pkn003",
            "session_file": "1795077131085_w2fwq.messages.json",
            "match_count": 31,
            "real_task_summary": "用户caozhang做post-sim SPF配置核对:cell名单文件aaa(145 cell)交叉比对4个SPF配置源(no_vcap/skip_cell/ignore_cells globs/control.nanospice_promd_spfba_common的finesim_mode+finesim_ignore),产per-source membership报告(命中数+cell名)。doc-search/cross-check Q&A,analog-sim setup验证。assistant产check_cells_in_refs.py(精确匹配+fnmatch glob+:prohd/:spicehd后缀剥离+#注释跳过+mode/ignore并集)。",
        },
        "asset_fidelity": "synthesized-reframe: 真实aaa/4源=foundry NFS大文件(/proj/ddgoa/...)不可入沙盒,合成A/B/A'三集token结构性不相交mock(A:RA_XYQ/WCK2Ti/Spnand/Spaoi/dynamic_Latch/SCmos/RAbus行列驱动SCMOS类;B:ColDec/WlDrv/Saoi/Snand/vrg/CMos/Xpre列译码字线sense-amp类;A':BitLine/Rdmux/Nand2x/Nor3x/preChg/Tmos/CapBuf派生+aaa子集偏移6cell移除+4filler使A'-gold计数9/4/32/16≠B-gold 13/6/38/18)。格式100%复刻真实:每行一cell/#注释/fnmatch glob/.option finesim_mode=...:suffix + .option finesim_ignore=...。任务形态(cross-reference produce)零偏移。",
    },
}

# verify k_check == k_rationale == 19
assert record["metadata"]["k_check"] == 19
assert record["metadata"]["k_rationale"] == 19
# count test_rationale entries (① ... ⑲)
import re
rationale_count = len(re.findall(r"[①-⑲]", test_rationale))
assert rationale_count == 19, f"rationale entries {rationale_count} != 19"

# flock-guarded append: verify working tree == HEAD before append, count lines
import subprocess
head_lines = int(subprocess.check_output(["wc", "-l", JSONL]).split()[0])
print(f"D.jsonl lines before append: {head_lines}")

# check for duplicate case_id
with open(JSONL) as f:
    for i, line in enumerate(f, 1):
        rec = json.loads(line)
        if rec.get("case_id") == CASE_ID:
            raise SystemExit(f"DUPLICATE case_id {CASE_ID} already at line {i}!")

line = json.dumps(record, ensure_ascii=False)
with open(JSONL, "a") as f:
    f.write(line + "\n")

after_lines = int(subprocess.check_output(["wc", "-l", JSONL]).split()[0])
print(f"D.jsonl lines after append: {after_lines}")
assert after_lines == head_lines + 1, "line count mismatch!"

# verify the appended record parses
with open(JSONL) as f:
    lines = f.readlines()
last = json.loads(lines[-1])
assert last["case_id"] == CASE_ID
assert last["metadata"]["k_check"] == 19
print(f"OK: appended {CASE_ID} as line {after_lines}")
print(f"  check_sha256={check_sha[:16]}... size={check_size}")
print(f"  test_rationale: 19 entries ✓")
print(f"  k_check=k_rationale=19 ✓")
