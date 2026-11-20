#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-DrcPatternReportComposer-001 to shard C jsonl."""
import hashlib
import json
import os

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-DrcPatternReportComposer-001"
REF_DIR = os.path.join(ROOT, "reference", CASE)
ASSET_DIR = os.path.join(ROOT, "assets", CASE, "inputs")

check_path = os.path.join(REF_DIR, "check.py")
with open(check_path, "r", encoding="utf-8") as f:
    check_src = f.read()
check_md5 = hashlib.md5(check_src.encode("utf-8")).hexdigest()

with open(os.path.join(ASSET_DIR, "prompt.md"), "r", encoding="utf-8") as f:
    prompt = f.read()

entry = {
    "id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": check_src,
    "prompt": prompt,
    "attachments": [
        "assets/{}/inputs/prompt.md".format(CASE),
        "assets/{}/inputs/task_brief.md".format(CASE),
        "assets/{}/inputs/run_A.json".format(CASE),
    ],
    "metadata": {
        "trace_source": {
            "user": "xinqiaoz",
            "host": "hfeg0pkn004",
            "session_file": "1789959794365_pet0x.messages.json",
            "match_count": 310,
            "real_task_summary": (
                "PDK QA Pattern DRC (DrcPatternCheck.py) 维护会话：诊断 legacy bad-only cell "
                "报告显示 Good Existing=-1 的根因（无 good cell 配对→good 侧 second calibre 未跑），"
                "将报告段 goodExisting 初值 -1→0 以统一 bad-only 语义；并按交接文档回退 "
                "symlinkFileToDir/drcSelectCheck 两处改动、校准 calibre edaTurbo 参数。"
            ),
        },
        "domain": "physical_verify",
        "track": "synthesized",
        "difficulty": "L1",
        "test_rationale": (
            "14 条断言：①[a]submit.zip 解压成功且 drc_pattern_report.py py_compile 通过 "
            "②[b]无参数调用退出码非 0 ③[c]不存在的输入文件退出码非 0 "
            "④[d]malformed JSON 输入退出码非 0 ⑤[e]隐藏 B1 上跑 exit 0 且 stdout 为含 "
            "rows+summary 的合法 JSON、rows 数==B1 规则数 "
            "⑥[f]B1 中 bad-only legacy 规则 good_existing==0（修正语义，非 -1）"
            " ⑦[g]B1 中成对规则 good_existing==解析得到的 good 侧 CHECK1 "
            "⑧[h]B1 中每个非 error 规则 bad_missing==解析得到的 bad 侧 CHECK1 "
            "⑨[i]B1 中每条规则三态 status(fail/waive/pass/error)与独立参考实现一致 "
            "⑩[j]B1 summary 的 fail/waive/pass/error/total 计数全对 "
            "⑪[k]跨输入守卫 B2(全成对、不同 rule 名)每条 good_existing 正确且 stdout 不含 "
            "A 的任何 rule 名 ⑫[l]B3 边界：bad-only 且 bad_summary 缺 CHECK2/3→incomplete==-1、"
            "good_existing==0；成对但 good_summary 缺 CHECK1 行→good_existing==-1（与 bad-only 的 0 区分）；"
            "bad-only 且无 bad_summary→bad_missing==-1 ⑬[m]确定性：B1 跑两次 stdout 逐字节一致 "
            "⑭[n]退化：rules 为空数组→非 0 退出；rule 缺 'rule' 字段→非 0 退出"
        ),
        "check_md5": check_md5,
        "harness": "cline",
    },
}

jsonl = os.path.join(ROOT, "EDA-Eval-DesignFlow_C.jsonl")
with open(jsonl, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# integrity: re-read and verify test md5 matches disk
with open(jsonl, "r", encoding="utf-8") as f:
    lines = [l for l in f if l.strip()]
last = json.loads(lines[-1])
assert last["id"] == CASE, last["id"]
assert hashlib.md5(last["test"].encode("utf-8")).hexdigest() == check_md5
assert last["metadata"]["check_md5"] == check_md5
print("appended {} (check_md5={}) -> total entries: {}".format(CASE, check_md5, len(lines)))
