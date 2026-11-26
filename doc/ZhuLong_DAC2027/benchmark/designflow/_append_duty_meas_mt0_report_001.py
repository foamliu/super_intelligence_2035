#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-DutyMeasMt0Report-001 to shard B jsonl with byte-sync."""
import json, os, hashlib

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-DutyMeasMt0Report-001"
JSONL = os.path.join(BASE, "EDA-Eval-DesignFlow_B.jsonl")
CHECK = os.path.join(BASE, "reference", CASE, "check.py")

check_bytes = open(CHECK, "rb").read()
check_sha = hashlib.sha256(check_bytes).hexdigest()[:16]
check_str = check_bytes.decode("utf-8")

PROMPT = """帮我运行并且输出duty（PUP，PDN）结果，使用finesim。

（背景：bolint 在 hfeg0plg100 上做 P2S DDR PHY 的混合信号验证，需要跑一组 FineSim 瞬态仿真，提取 PUP/PDN 输出在低速时钟域（PUPN_LowSpeed / PDNN_LowSpeed）下的占空比 duty。测试台 01_TB_P2S_DQ_3200_noclktree_vintio_2phase_rf.sp 用 .measure 语句定义了 4 个 duty 量测：duty_pup = h1/p1、duty_pdn = h2/p2、duty_pup1 = h3/p3、duty_pdn1 = h4/p4，并通过 17 组 .alter .lib 切换 PVT corner（TT/SS/FF/SF/FS × RT/LT/HT 等）。FineSim 仿真后会把所有 alter 的量测结果写进 .mt0 文件。附件 sample.sp 是仿真网表（含 .measure duty 语句 + .alter corner 定义），sample.mt0 是 FineSim 产出的多 alter 量测结果文件，mt0_format_spec.txt 说明了 .mt0 的格式。由于仿真已在别处跑完，这里只需做结果解析。)

帮我写一个脚本 duty_report.py：读入 .sp 网表和 .mt0 量测文件，输出结构化 JSON 占空比报告。具体：
  1) 解析 .sp：从 .alter 后的 .lib '<path>' <CORNER> 行提取 corner 名称（顺序对应 alter 索引，base corner 是第一条非注释 .lib 行），跳过以 * 开头的注释行；
  2) 解析 .mt0：表头行（以 ",alter," 开头）给出 measure 名与列序；数据行（首 token 为 "0"，第二 token 为 alter 索引）给出每个 corner 的量测值；
  3) 输出 JSON（写到 stdout）：measure_names（全部量测名）、duty_measures（duty_pup/duty_pdn/duty_pup1/duty_pdn1）、corners（每个 corner 含 index/name 与 4 个 duty 值）、summary（每个 duty 量的 min/max/mean）。

用法：`python3 duty_report.py <sp_file> <mt0_file>`，把 JSON 报告打印到 stdout。"""

TASK_BRIEF = "交付：duty_report.py（Python3，打包进 outputs/submit.zip，zip 根目录即该 .py）。\n用法：`python3 duty_report.py <sp_file> <mt0_file>` — 读 FineSim .sp 网表 + .mt0 量测文件，打印结构化 JSON 占空比报告（measure_names/duty_measures/corners/summary）。"

RATIONALE = "15 条断言：①submit.zip 含 duty_report.py ②duty_report.py 通过 py_compile ③候选在 B1 跑出 exit0 ④B1 stdout 为合法 JSON ⑤corners 数组长度等于 B1 corner 数(6) ⑥每个 corner 含 duty_pup/duty_pdn/duty_pup1/duty_pdn1 四键 ⑦各 corner 的 duty_pup 值与 B1 期望一致(容差1e-9) ⑧各 corner 的 duty_pdn 值与 B1 期望一致 ⑨各 corner 的 duty_pup1 值与 B1 期望一致 ⑩各 corner 的 duty_pdn1 值与 B1 期望一致 ⑪corner 名称按序与 B1 .sp 的 .alter .lib corner 名一致 ⑫summary.duty_pup 的 min/max/mean 正确 ⑬summary.duty_pdn 的 min/max/mean 正确 ⑭反硬编码：在 B2 重跑候选，duty_pup 值须与 B1 不同（候选不可硬编码 B1） ⑮交叉输入：B2 的 corner 名称须与 B1 不同且等于 B2 .sp 的 corner 名"

TRACE_SUMMARY = "bolint@hfeg0plg100 session 1793341757885_9e4kf：用户要求「帮我运行并且输出duty（PUP，PDN）结果，使用finesim」+附件 01_TB_P2S_DQ_3200_noclktree_vintio_2phase_rf.sp。.sp 含 .measure duty_pup=h1/p1、duty_pdn=h2/p2、duty_pup1=h3/p3、duty_pdn1=h4/p4（基于 PUPN_LowSpeed/PDNN_LowSpeed 上升/下降沿 crossing），17 组 .alter .lib PVT corner（TT/SS/FF/SF/FS × RT/LT/HT）。trace 中 agent(zhulong) 因 LD_PRELOAD 旧版 libstdc++ 缺 GLIBCXX_3.4.26 导致 finesim V-2023.12 无法启动，卡在环境诊断未完成仿真——故无真实仿真产物，按 .sp 文档化的 .measure 结构 + .mt0 格式 B-synthesized 造 L1 解析题：给定已产出的 .mt0 量测文件，解析并输出结构化 JSON duty 报告。"

entry = {
    "id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": PROMPT,
    "attachments": [
        "assets/EDA-Eval-DesignFlow-DutyMeasMt0Report-001/sample.sp",
        "assets/EDA-Eval-DesignFlow-DutyMeasMt0Report-001/sample.mt0",
        "assets/EDA-Eval-DesignFlow-DutyMeasMt0Report-001/mt0_format_spec.txt",
    ],
    "task_brief": TASK_BRIEF,
    "test": check_str,
    "metadata": {
        "domain": "spice_sim",
        "track": "synthesized",
        "layer": "L1",
        "trace_source": {
            "user": "bolint",
            "host": "hfeg0plg100",
            "session_file": "1793341757885_9e4kf.messages.json",
            "match_count": 42,
            "real_task_summary": TRACE_SUMMARY,
        },
        "test_rationale": RATIONALE,
        "k_rationale": 15,
        "k_check": 15,
        "gold_standard": "B-synthesized：trace agent 卡在 finesim 环境问题未完成仿真，无真实产物。按 .sp 文档化的 .measure duty 结构（duty_pup=h1/p1 等）+ FineSim .mt0 多 alter 量测格式合成 L1 解析题。金标准=duty_report_ref.py：解析 .sp 的 .alter .lib corner 名（跳过 * 注释行）+ 解析 .mt0 表头/数据行，输出 JSON（measure_names/duty_measures/corners/summary）。隐藏 B1=6 corner(SS_FF/TT_M40/TT_105/FF_M40/FF_105/SS_RT2) 不同 duty 值；B2=5 corner(TT_FF/SS_M55/SS_125/FS_RT/FS_LT) 反硬编码。"
    }
}

# byte-sync verify: re-read test field == disk
assert entry["test"] == open(CHECK).read(), "test field != disk check.py"
# k gate
assert entry["metadata"]["k_rationale"] == entry["metadata"]["k_check"], "k mismatch"
assert entry["metadata"]["k_check"] >= 8, "k<8"

# count conditions in check.py (labels (a)..(o))
import re
labels = set(re.findall(r'\(([a-z])\)', check_str))
assert len(labels) == 15, "expected 15 labels, got %d: %s" % (len(labels), sorted(labels))

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print("APPENDED:", CASE)
print("check.py sha256[:16]:", check_sha, "size:", len(check_bytes))
print("k_rationale=k_check=15 >=8 GATE PASS")
print("test field byte-sync: OK")
print("jsonl B lines now:", sum(1 for _ in open(JSONL)))
