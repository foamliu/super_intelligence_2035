#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-SimResultGrep-001 to EDA-Eval-DesignFlow_B.jsonl."""
import json, os, re

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-SimResultGrep-001"
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
        f"assets/{CASE}/testdir_A",
        f"assets/{CASE}/task_brief.md",
        f"assets/{CASE}/prompt.txt",
    ],
    "metadata": {
        "trace_source": {
            "user": "tzuo",
            "host": "hfhds201",
            "session_file": "1791448400305_kwiij.messages.json",
            "match_count": 49,
            "real_task_summary": (
                "tzuo 在 hfhds201 上要求写一个仿真结果抓取脚本 result_grep。USER#0 原话"
                "「写一个脚本实现仿真路径下到结果抓取…起名叫result_grep，规则如下 1. -result选项 "
                "抓取当前path下所有folder内的zzresult*文件，folder内可能存在多个zzresult*文件，"
                "只抓取最新的一个，输出到当前path下的zzresult_YMD.list文件中，YMD为当前年月日，"
                "文件内均为绝对路径 2. -path 选项，抓取当前path下的所有MatrixRun* folder，输出到"
                "allpath_YMD.list文件中，内容为绝对路径」——纯需求轮(给目标+两选项规则，未给根因/修复)。"
                "trace 中 assistant 用 editor 写 python3 CLI 脚本 result_grep：os.listdir+glob 抓 zzresult*，"
                "多文件取 max(mtime) 最新，sorted(entries) 排序，os.path.abspath 转绝对路径，"
                "datetime.now().strftime('%Y%m%d') 生成 YMD 后缀，写 zzresult_<YMD>.list / allpath_<YMD>.list。"
                "金标准=USER#0 spec 正确实现(L1 离线 python，cwd 即扫描根)。"
            ),
        },
        "domain": "spice_sim",
        "level": "L1",
        "track": "faithful",
        "harness": "cline",
        "test_rationale": (
            "14 条断言：①submit.zip 有效且含可执行 python 脚本 ②脚本可编译(py_compile exit0) "
            "③无参数调用必非零退出(打印用法) ④未知选项必非零退出 "
            "⑤-result 在隐藏 B 上 exit0 且生成 zzresult_YYYYMMDD.list "
            "⑥-result B 恰好 3 行(有 zzresult 的 folder 数: Drift/Heat/analysis) "
            "⑦-result B 全行为绝对路径 ⑧-result B 中 Heat folder 取最新 zzresult_2.rpt(按 mtime 选,非 _1/_3) "
            "⑨-result B 排除无 zzresult 的 MatrixRun_Empty folder ⑩-result B 包含非 MatrixRun 的 analysis/zzresult_decoy.txt(-result 扫所有 folder 非 only MatrixRun) "
            "⑪-path 在隐藏 B 上 exit0 且生成 allpath_YYYYMMDD.list ⑫-path B 恰好列出 3 个 MatrixRun* 目录(Drift/Empty/Heat) "
            "⑬-path B 排除非 MatrixRun 目录(analysis)与散文件(readme.txt) ⑭跨输入护栏: -result 在可见 A 上得 2 行且 MMSIM 取最新 zzresult_b.txt, A 行数≠B(防硬编码)"
        ),
    },
}

# verify k_rationale == k_check == 14
assert entry["metadata"]["test_rationale"].count("断言：") == 1
n_rationale = len(re.findall(r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭]', entry["metadata"]["test_rationale"]))
n_check = len(set(re.findall(r'AssertionError\("([a-n]):', test_field)))
print("k_rationale =", n_rationale, " k_check =", n_check)
assert n_rationale == 14 and n_check == 14, "k mismatch!"

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("Appended. New line count:")
os.system("wc -l " + JSONL)
