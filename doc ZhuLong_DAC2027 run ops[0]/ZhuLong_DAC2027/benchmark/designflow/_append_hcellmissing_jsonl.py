#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-HcellMissingFind-001 to EDA-Eval-DesignFlow_B.jsonl."""
import json, os

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-HcellMissingFind-001"
JSONL = os.path.join(BASE, "EDA-Eval-DesignFlow_B.jsonl")
A = os.path.join(BASE, "assets", CASE)
R = os.path.join(BASE, "reference", CASE)

with open(os.path.join(R, "check.py")) as f:
    test_field = f.read()
with open(os.path.join(A, "prompt.txt")) as f:
    prompt_field = f.read()

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": test_field,
    "prompt": prompt_field,
    "attachments": [
        f"assets/{CASE}/hcell_A",
        f"assets/{CASE}/netlist_A",
        f"assets/{CASE}/task_brief.md",
        f"assets/{CASE}/prompt.txt",
    ],
    "metadata": {
        "trace_source": {
            "user": "zjqiao",
            "host": "hfhds201",
            "session_file": "1793347412273_nq8l2.messages.json",
            "match_count": 98,
            "real_task_summary": (
                "用户提供 hcell 映射文件（每行两列，第一列为 block 名）与 SPICE netlist"
                "（AETHER-SE 导出，148MB，drvqa_top/WOWTOP_1C2A），要求把 hcell 第一列逐行"
                "在 netlist 中检索，找出 netlist 中找不到的 block（缺失/改过名字）。trace 中"
                " assistant 写 check_hcell_in_netlist.py，扫 netlist 三类命中位置（.SUBCKT 定义名、"
                "* Cell header 值、X 实例引用末 token），报告 not-found blocks，并 deep_search 查"
                " rename。USER#1 转新需求（交互式 agent + topjob），USER#0 已完成。"
                "金标准=USER#0 spec 正确实现：exact-token 匹配三类位置、hcell 去重保序、rename 报 missing。"
            ),
        },
        "domain": "spice_sim",
        "level": "L1",
        "track": "faithful",
        "harness": "cline",
        "test_rationale": (
            "12 条断言：①submit.zip 有效且含 .py 脚本 ②脚本可编译(py_compile exit0) "
            "③--help exit0 且提及 hcell 与 netlist 参数 ④在隐藏 B(hcell_B+netlist_B)上运行 exit0 "
            "⑤B 输出非空且每行为单 token(block name) ⑥B missing 集合==期望 5 个(完整且正确) "
            "⑦B 输出无重复行 ⑧B 输出保持 hcell_B 顺序(==期望顺序) "
            "⑨* Cell header 检测:AG_PhonyVibCom(仅 * Cell header 命中,.SUBCKT 改名为 _v2)不在 B 输出 "
            "⑩X 实例引用检测:T_DDR5IsmTop(仅 X 实例引用命中,无 .SUBCKT/无 * Cell)不在 B 输出 "
            "⑪rename 陷阱:AG_PhonyActSpare(改名 AG_PhonyActSpare_v2,exact 匹配失败→missing)必须在 B 输出(substring 匹配会假阳性漏报) "
            "⑫跨输入护栏:在 A 上运行 A missing==期望 5 行且 A≠B;A 含 rename 陷阱 AG_VdivActTopSpare 且不含重复 FOUND AG_VdivActTop(去重)"
        ),
    },
}

# verify k_rationale == k_check == 12
assert entry["metadata"]["test_rationale"].count("断言：") == 1
# count ①..⑫ markers
import re
n_rationale = len(re.findall(r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫]', entry["metadata"]["test_rationale"]))
# count check.py conditions (a-l)
n_check = len(re.findall(r'# --- [a-l]:', test_field))
print("k_rationale =", n_rationale, " k_check =", n_check)
assert n_rationale == 12 and n_check == 12, "k mismatch!"

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("Appended. New line count:")
os.system("wc -l " + JSONL)
