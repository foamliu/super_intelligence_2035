#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-FineSimWorkflowRunner-001 to EDA-Eval-DesignFlow_B.jsonl.

Reads case files from disk (no manual transcription) and writes a single
jsonl line. Idempotency: skips if id already present.
"""
import json
import os
import sys

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-FineSimWorkflowRunner-001"
ASSET_DIR = os.path.join(BENCH, "assets", CASE)
REF_DIR = os.path.join(BENCH, "reference", CASE)
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")

CASE_ID = CASE

# idempotency
existing_ids = set()
with open(JSONL) as fh:
    for line in fh:
        if line.strip():
            d = json.loads(line)
            existing_ids.add(d.get("id") or d.get("task_id"))
if CASE_ID in existing_ids:
    print("SKIP: %s already in jsonl" % CASE_ID)
    sys.exit(0)

prompt = open(os.path.join(ASSET_DIR, "prompt.txt")).read()
task_brief = open(os.path.join(ASSET_DIR, "task_brief.md")).read()
check_py = open(os.path.join(REF_DIR, "check.py")).read()

# 14 条断言 (a)-(n) — one per independently-failable check.py condition
test_rationale = (
    "14 条断言："
    "①(a) submit.zip 是合法 zip 且含 finesim_workflow.py "
    "②(b) finesim_workflow.py 可 py_compile 编译通过 "
    "③(c) 在隐藏 B 上跑 workflow 退出 0 且产出 workflow_report.json + detail.csv + summary.csv "
    "④(d) finesim 真跑了：report.finesim_ran==true 且 out_dir/run.log 存在且含 \"FineSim\"(反 fake_no_rerun/fake_core_deleted) "
    "⑤(e) analyses_run == B 分析类型排序 [ac, dc, tran](反 naive_no_analyses 丢分析) "
    "⑥(f) measures dict 含全部 5 个 B measure 名(nb_voh/nb_vol/nb_vtrip/nb_tpd/nb_gain)且为数值(反 naive_empty) "
    "⑦(g) converged==true 且 run.log 含 \"Successfully Completed\" 且无 non-conv/error!/abort 标记(反不真跑 sim 的 stub) "
    "⑧(h) B 的 5 个 measure 数值匹配 .75 标定 GT(nb_voh=1.0±0.05, nb_vol≤1e-3, nb_vtrip=0.51±0.05, nb_tpd=1.2879e-10±20%, nb_gain=-43.625±3.0)(反 naive_print_expected 印 A 值/naive_hardcode_a) "
    "⑨(i) 跨输入守卫：A-token(na_*)不出现在 B 输出；B-token(nb_*/nb_a/nb_y/nb_vpx)出现(反 naive_hardcode_a) "
    "⑩(j) detail.csv 表头 [analysis,name,value] 且每行一个 B measure、value 非空(反 naive_partial 丢行/off-by-one) "
    "⑪(k) summary.csv 表头 [analysis,n_measures,converged] 且每行一个 B 分析 "
    "⑫(l) workflow_report.json 字段齐全(simulator/sim_mode/analyses_run/converged/finesim_ran/measures/csv_paths/sim_log_path/deck_path) "
    "⑬(m) 确定性：判分器重跑 B，两次 measures 在 1% 内一致 "
    "⑭(n) 非退化：在 A 配置(netlist_A/spec_A)上跑产出与 B 不同(measures 不同且 A measure 名 na_voh/na_vol/na_gain 出现于 A report)，证明生成器不忽略输入"
)

entry = {
    "id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "test": check_py,
    "attachments": [
        "assets/%s/netlist_A.sp" % CASE,
        "assets/%s/spec_A.json" % CASE,
        "assets/%s/prompt.txt" % CASE,
        "assets/%s/task_brief.md" % CASE,
    ],
    "metadata": {
        "domain": "spice_sim",
        "track": "synthesized",
        "level": "L2",
        "hidden_B": True,
        "selftest": {
            "ref_pass": "14/14",
            "negatives_all_fail": True,
            "three_fake_regression": "empty/print-expected/core-deleted all FAIL",
            "neg_count": 6,
            "neg_mutual_exclusivity": "labels union >= 4 distinct",
        },
        "test_rationale": test_rationale,
        "trace_source": {
            "user": "zjqiao",
            "host": "hfhds206",
            "session_file": "1791017602459_fwgyy.messages.json",
            "match_count": 221,
            "real_task_summary": (
                "用户(zjqiao @ hfhds206)逐字「你能否自己形成一个工作流进行finesim仿真」——"
                "纯目标表达未给根因/修复(符合 A 档选轮规则,但 trace 末尾用户未明确接受→B 档 synthesized,金标准 .75 标定)。"
                "真实 agent 全程 run_commands 被禁 + run_approved_command DENIED→从未真跑 sim,仅靠 RAG 检索 pyAether MDE API 全集 + editor 拼出"
                "finesim_simulation_workflow.SKILL.md(验收 5 条/API 速查 9 个/7 陷阱) + finesim_workflow.py(FineSimWorkflow 类 8 阶段 init_aether→open_session→add_model_file→"
                "configure_dc/tran/ac/stb/noise→run_simulation(netlistAndRun)→save_results CSV→create_netlist→close_session)。"
                "本 case 取其可移植子技能=自主 FineSim 仿真工作流生成器/运行器(给定 netlist+spec→subprocess 调 finesim -spice→配置 DC/Tran/AC 多分析→"
                "解析 .m{d,t,a}0 + .log→落 detail.csv/summary.csv/workflow_report.json)(B-档 synthesized,便携化:FineSimPro V-2023.12-1 -spice 模式,level-1 Shichman-Hodges MOS 反相器,shard B 首个 workflow generator/runner 子技能,distinct vs 已有 FineSim 四修复器/诊断器 case)。"
                ".75 端到端标定:ref 跑隐藏 B 得 nb_voh=1.0/nb_vol=1.675e-08/nb_vtrip=0.51/nb_tpd=1.2879e-10/nb_gain=-43.625,converged=true,'FineSim Successfully Completed'。"
            ),
        },
    },
}

# validate k_rationale == k_check
import re
k_check = len(re.findall(r"\[(a-n|a|b|c|d|e|f|g|h|i|j|k|l|m|n)\]", check_py))
# count distinct labels (a)-(n) in check.py header docstring
labels_in_check = set(re.findall(r"^\s+([a-n])\s+", check_py, re.MULTILINE))
k_check = len(labels_in_check)
k_rationale = len(re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]", test_rationale))
print("k_check(labels in check.py)=", k_check, "k_rationale=", k_rationale)
assert k_rationale == k_check >= 8, "GATE FAIL: k_rationale=%d k_check=%d" % (k_rationale, k_check)
print("GATE PASS: k_rationale=k_check=%d >=8" % k_check)

line = json.dumps(entry, ensure_ascii=False)
with open(JSONL, "a") as fh:
    fh.write(line + "\n")
print("APPENDED:", CASE_ID, "test_len=%d prompt_len=%d" % (len(check_py), len(prompt)))

# verify roundtrip + count
n = 0
with open(JSONL) as fh:
    for line in fh:
        if line.strip():
            n += 1
print("jsonl now has %d lines" % n)
