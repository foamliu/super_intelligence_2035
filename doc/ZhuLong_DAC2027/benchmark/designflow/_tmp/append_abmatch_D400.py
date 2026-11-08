#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-ABMatchPlacementCheck-001 to D.jsonl."""
import json, os, sys

CASE = "EDA-Eval-DesignFlow-ABMatchPlacementCheck-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSETS = os.path.join(BENCH, "assets", CASE)
REF = os.path.join(BENCH, "reference", CASE)
D_JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_D.jsonl")

prompt = open(os.path.join(ASSETS, "prompt.txt"), encoding="utf-8").read()
check_py = open(os.path.join(REF, "check.py"), encoding="utf-8").read()

test_rationale = (
    "15 条断言：①submit.zip 可解压且恰含 1 个 .py(≥400B)、UTF-8 无 NUL、py_compile 通过 "
    "②候选在隐藏 B 上运行 exit0、写出 match_check_report.json、stdout==文件内容、顶层含 {verdict,groups,manifest_lib,manifest_cell,n_groups} "
    "③B 的 verdict==\"HAS_ISSUES\"(5 处植入摆放错误被检出) "
    "④report.n_groups==len(B.manifest.groups)(独立从 B 文件重数) "
    "⑤B pmirror seq_match_bot==False 且 actual_seq_bot!=sketch.bot(植入 bot 行 A/B 互换被序列层检出) "
    "⑥B inp share_aa_ok==False(植入非共享 AA 区被检出) "
    "⑦B pmirror label_align_ok==False(植入 text label 错位被检出) "
    "⑧B inp step_mirror_ok==False(植入行间关系破坏、非 mirror 被检出) "
    "⑨B pmirror match_method==\"common_centroid\" 且所有 group 的 method∈{common_centroid,simple_pair}(分类按草图自洽) "
    "⑩B 所有 group unit_count_parity_ok==True(尽管有摆放错、计数仍配对) "
    "⑪B 所有 group dummy_endpoints_ok==True(dummy 仍在行首尾) "
    "⑫B 每个 group 报告 dict 含全部必需字段{group_id,seq_match_top/bot,actual_seq_top/bot,share_aa_ok,match_method,inter_row_type,step_mirror_ok,label_align_ok,unit_count_parity_ok,dummy_endpoints_ok,sd_ct_ok,group_ok} "
    "⑬跨输入守卫:候选重跑隐藏 B2(全对、不同器件前缀/cell)verdict==\"OK\"(击穿 hardcoded-A 与 always-FAIL) "
    "⑭结构守卫:B.manifest_cell!=B2.manifest_cell 且 B.groups JSON!=B2.groups JSON(候选读 manifest 而非写死、击穿 print-expected) "
    "⑮B pmirror sd_ct_ok==False(植入匹配 unit ct_count=0；USER#2 检查项 4：匹配管的 S/D metal width + CT 孔数必须齐)"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        "assets/%s/prompt.txt" % CASE,
        "assets/%s/task_brief.md" % CASE,
        "assets/%s/match_manifest.json" % CASE,
    ],
    "test": check_py,
    "expected_artifacts": ["outputs/submit.zip"],
    "budget": {"max_turns": 20},
    "metadata": {
        "trace_source": {
            "user": "ziyuny",
            "host": "10.129.32.190",
            "session_file": "1791617131890_5kh50.messages.json",
            "match_count": 67,
            "real_task_summary": (
                "Aether 原理图 AB 匹配标注 vs 版图 unit 摆放校验：用户 ziyuny 在 train/ddgoa_test 项目对带隙基准放大器 "
                "VwlpRefAmpIP 做「原理图人工标注的 AB 匹配草图」与「版图实际 unit 摆放」逐列比对，已用 pyAether 把两 view 的实例/坐标/ort/bbox/w/l/nf、"
                "版图字母 text label、每 unit 的 AA bbox + S/D metal width + CT 孔数提取成离线 phase5.json（比对脚本只吃该 JSON，不连 Aether）。"
                "USER#0=续传笔记（phase5.json 已就绪、final_check2.py 序列比对已 PASS 三方一致 OABABO/OBABAO 等）；"
                "USER#2 逐字提新增 4 检查项「1 是否share AA 2 采用哪种匹配方式 3 mos管是step还是mirror 4 source/drain的metal width以及CT孔个数」（提需求、未给根因/修复→合格 seed）。"
                "助手 editor 写 probe6.py/device_match_phase6.py 解层名(AA/PG.NCH/PCH/PC=CT/M1)提 per-unit AA 范围/每节点 CT 数/M1 宽度+顶层 M1 连通性追踪判 step/mirror。"
                "gold 依赖 live pyAether + live OA layout（在 10.129.2.11，.75 沙盒不可达）→ A 档 disqualified，取 B 档 synthesized L1-boundary：把 phase5.json 结构固化为 match_manifest.json，候选 ab_match_check.py 跑 8 per-group 检查。"
            ),
        },
        "domain": "analog_context",
        "grade": "B",
        "track": "synthesized",
        "L_level": "L1",
        "test_rationale": test_rationale,
    },
}

# assertion gate self-check
k_check = check_py.count("_fail(") + check_py.count("_cond(")
# count labeled conditions by scanning the docstring a-o
import re
conds = re.findall(r'^\s+([a-o])\s', check_py, re.M)
# fallback: count distinct condition letters used in _fail(...) first-arg string
fail_conds = re.findall(r'_fail\(\s*"([a-o])', check_py)
k_rationale = test_rationale.count("①") + test_rationale.count("②") + test_rationale.count("③") + \
              test_rationale.count("④") + test_rationale.count("⑤") + test_rationale.count("⑥") + \
              test_rationale.count("⑦") + test_rationale.count("⑧") + test_rationale.count("⑨") + \
              test_rationale.count("⑩") + test_rationale.count("⑪") + test_rationale.count("⑫") + \
              test_rationale.count("⑬") + test_rationale.count("⑭") + test_rationale.count("⑮")
print("k_rationale(①..⑮) =", k_rationale)
print("distinct fail-cond letters =", sorted(set(fail_conds)), "n=", len(set(fail_conds)))
print("GATE: k_rationale==k_check==15 and >=8:", k_rationale == 15 and len(set(fail_conds)) == 15)

# byte-sync guard: test field == disk check.py
assert check_py == open(os.path.join(REF, "check.py"), encoding="utf-8").read(), "test!=disk check.py"
print("byte-sync test==disk check.py: OK")

# append
line = json.dumps(entry, ensure_ascii=False)
# sanity: valid json single line
json.loads(line)
with open(D_JSONL, "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("APPENDED to", D_JSONL)
