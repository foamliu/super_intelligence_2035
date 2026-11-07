#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-LvsRptAnalyze-001 to EDA-Eval-DesignFlow_D.jsonl."""
import json, os, sys

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-LvsRptAnalyze-001"
REF = os.path.join(REPO, "reference", CID)

# Read check.py source bytes for the test field
check_py = os.path.join(REF, "check.py")
test_src = open(check_py).read()

PROMPT = open(os.path.join(REPO, "assets", CID, "prompt.txt")).read()

entry = {
    "task_id": CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": PROMPT,
    "attachments": [
        "assets/%s/prompt.txt" % CID,
        "assets/%s/task_brief.md" % CID,
        "assets/%s/lvs_report_A.txt" % CID,
        "assets/%s/lvs_report_A.txt.ext" % CID,
        "assets/%s/erc_summary_A.txt" % CID,
    ],
    "test": test_src,
    "expected_artifacts": ["outputs/submit.zip"],
    "budget": {"max_turns": 20},
    "metadata": {
        "trace_source": {
            "user": "fhwang",
            "host": "10.129.2.14",
            "session_file": "1792223414540_erhym.messages.json",
            "match_count": 50,
            "real_task_summary": "DRAM 物理验证组 LVS 排障：用户 fhwang 跑完 Calibre LVS（Cell: Array3G_TOP_L，260MB 报告，INCORRECT），要求分析结果文件错误类型+解决方案方向并生成文本报告。助手读取 .lvs.report/.ext/.erc.summary，用 grep+Python 脚本统计错误（Connectivity errors、Property errors W=2.717u vs 1.476u、1224 missing smashed mosfet、Open circuit SecEnGapN/vap2!、Unattached label viso!/VncsgnEn、Stamping conflict vss!），生成 LVS_ANALYSIS_REPORT.md（基本信息+Rule设置+错误摘要+错误分类+提取警告+根因分析+解决方案方向）+ analyze_lvs.py 解析脚本。"
        },
        "domain": "schematic_netlist",
        "grade": "B",
        "track": "synthesized",
        "L_level": "L1",
        "test_rationale": (
            "16 条断言："
            "①submit.zip 可解压且无泄漏(不含 check/reference/negative/jsonl)且含 analyze_lvs.py 且 py_compile 通过 "
            "②B(隐藏输入,DDR5_PHY_TOP INCORRECT)运行 exit0 且产出 lvs_analysis_report.md/error_summary.json 两文件 "
            "③error_summary.json 含全部 7 个顶层键(top_cell/lvs_result/tool_version/rule_settings/error_counts/property_errors/ext_warnings) "
            "④B 的 lvs_result==\"INCORRECT\"(B 是 INCORRECT case) "
            "⑤report.md 含基本信息节且含 top_cell(DDR5_PHY_TOP)+tool_version(v2022.4) "
            "⑥report.md 含 Rule 设置节且含 RECOGNIZE GATES+FILTER UNUSED+VIRTUAL CONNECT COLON 三个关键词 "
            "⑦B 的 ext_warnings 计数正确(open_circuit==7, unattached_label==12, stamping_conflict==2) "
            "⑧B 的 property_errors 是 3 元素 list 且首元素 layout_w≈0.84/source_w≈0.42/diff_pct≥50 "
            "⑨report.md 含错误类型分类节且含 Connectivity/连接 + Property/属性 两类 "
            "⑩B 的 error_counts.missing_smashed_mosfet==856(从报告 'missing smashed mosfet: N occurrences' 提取) "
            "⑪report.md 含根因分析节(根因/根本原因/Root Cause) "
            "⑫report.md 含解决方案节(解决方案/Solution)且含可操作建议(label/命名/svdb/RVE 之一) "
            "⑬跨输入守卫 B2(CORRECT case,AES_CORE)重跑 → lvs_result==\"CORRECT\" + error_counts 全 0 + ext_warnings 空/全 0 "
            "⑭反硬编码:候选源码无 A 专属标记(Array/2.717/1.476/1224/SecEnGapN/vap2!/viso!/v2020.1) 且 A-run top_cell==Array3G_TOP_L ≠ B top_cell "
            "⑮确定性:B 的 error_summary.json 跑 3 次 sha256 完全一致 "
            "⑯error_counts 是 dict 且含 connectivity_errors+property_errors+missing_smashed_mosfet 三键 且 missing_smashed_mosfet==856"
        ),
    },
}

jsonl_path = os.path.join(REPO, "EDA-Eval-DesignFlow_D.jsonl")
# verify CID not already present
existing = open(jsonl_path).read().splitlines()
for line in existing:
    if line.strip():
        d = json.loads(line)
        if d.get("task_id") == CID:
            print("!!! CID already in jsonl — aborting"); sys.exit(1)

with open(jsonl_path, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

n = sum(1 for l in open(jsonl_path) if l.strip())
print("appended %s to %s (now %d lines)" % (CID, jsonl_path, n))

# verify roundtrip: last line parses + test field == disk check.py
last = [l for l in open(jsonl_path) if l.strip()][-1]
d = json.loads(last)
assert d["task_id"] == CID
disk_test = open(check_py).read()
assert d["test"] == disk_test, "test field != disk check.py"
print("jsonl roundtrip OK: test field == disk check.py (%d bytes)" % len(disk_test))
