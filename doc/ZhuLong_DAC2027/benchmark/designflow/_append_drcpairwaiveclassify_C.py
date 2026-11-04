#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-DrcPairWaiveClassify-001 to shard C jsonl."""
import json, os, sys

CASE_ID = "EDA-Eval-DesignFlow-DrcPairWaiveClassify-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF_DIR = os.path.join(BENCH, "reference", CASE_ID)
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_C.jsonl")

with open(os.path.join(REF_DIR, "check.py"), encoding="utf-8") as f:
    check_src = f.read()

entry = {
    "task_id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["drc_pair_waive_classify.py", "pattern_check_report.json"],
    "attachments": [
        "assets/%s/task_brief.md" % CASE_ID,
        "assets/%s/pattern_rules.json" % CASE_ID,
        "assets/%s/calibre_results.json" % CASE_ID,
    ],
    "prompt": open(os.path.join(BENCH, "assets", CASE_ID, "prompt.txt"), encoding="utf-8").read(),
    "test": check_src,
    "metadata": {
        "domain": "physical_verify",
        "track": "synthesized",
        "level": "L1-boundary",
        "layer": "L2",
        "difficulty_tier": "L1-boundary",
        "direction": "generation",
        "harness": "cline",
        "task_name": "DRC pattern check 配对约束 + 三档 waive 分类 + CHECK1/2/3 执行引擎生成",
        "topic": "PDK_QA DrcPatternCheck 执行引擎: 读 pattern_rules.json(rules+cells) + calibre_results.json(per-cell CHECK1/2/3 errorCount/status/flattened) -> 配对约束校验(bad/good base 一致 + cell type 正确 + (bad,good) 配对可被多 rule 共享 + 禁止跨配对混用, 违规 exit 1) -> 三档分类(pass/failed/waive, waive 不并入 pass, USER#89) + pattern_not_found(cell 缺失) -> CHECK1(bad 必须 error)+CHECK2(good 几何 clean)+CHECK3(good reference clean) 三阶段 -> pattern_check_report.json(pairValidation/ruleResults/stageResults/reportCounts/waivedRules/verdict)",
        "scenario": "CXMT DRAM PDK_QA, xinqiaoz 维护 DrcPatternCheck.py(good/bad cell 对验证 DRC deck): 用户要求 good/bad 按 base 配对且允许共享但不许混配(USER#49), 修复 pass/failed/waive 混为一档的 bug(USER#89, waive 单独计数), 三 CHECK 阶段(bad error/good 几何 clean/good reference clean); 合成自包含分类器 drc_pair_waive_classify.py, 资产 5 rule(1 共享配对+1 waive+1 failed)/8 cell, hidden B(7 rule,共享+waive+failed+CHECK3-error)/B2(全 pass)/B3(配对混用违规)",
        "test_rationale": (
            "14 条断言：①[a]submit.zip 恰含 1 个 .py(>=400B,UTF-8 无 NUL)且 py_compile 通过 "
            "②[b]在隐藏 B 上跑 exit0 + 写 pattern_check_report.json + stdout==文件内容 + 顶层 11 键(platform/pairValidation/ruleResults/stageResults/reportCounts/waivedRules/passRules/failedRules/patternNotFoundRules/totalRules/verdict)齐全 "
            "③[c]reportCounts 四档之和 == len(rules_B) 且 totalRules == len(rules_B)(独立重计数) "
            "④[d]pairValidation.valid==True 且 pair_count == 独立重推的 unique (badCell,goodCell) 配对数 "
            "⑤[e]三档互斥: status 仅 pass/failed/waive/pattern_not_found; waived rule(其 CHECK 全过)分类为 waive 而非 pass; waivedRules 与 passRules 无交集(USER#89 修复) "
            "⑥[f]每条 rule 的 CHECK1 stage: cell==badCell + expected=='error' + errorCount/status 字段在 "
            "⑦[g]每条 rule 的 CHECK2 stage: cell==goodCell + expected=='clean' + errorCount/status 字段在 "
            "⑧[h]每条 rule 的 CHECK3 stage: cell==goodCell + expected=='clean' + errorCount/flattened/status 字段在 "
            "⑨[i]waivedRules == 独立重推的 waived rule 列表 + reportCounts['waive']==其长度 + 每个 waived rule 的 ruleResults.waived==true "
            "⑩[j]pairValidation.shared_pairs == 独立重推的共享配对(被>=2 rule 使用的 (bad,good) 对, ruleId 列表一致) "
            "⑪[k]跨输入 B2(全合法/无 waive/无共享): exit0 + verdict=='pass' + waive==0 + failed==0 + pattern_not_found==0 + 无 shared_pairs(击穿硬编码 B/always-fail) "
            "⑫[l]跨输入 B3(配对混用, bad base!=good base): exit 非零 + verdict=='pair_validation_failed' + pairValidation.valid==False + 至少一条 base_mismatch violation(击穿 always-pass) "
            "⑬[m]确定性: 在 B 上跑 3 次, pattern_check_report.json 的 md5 完全一致 "
            "⑭[n]A↔B 结构 guard: 可见 A 与隐藏 B 的 ruleId 集合不交 + 在 A 上跑的 reportCounts 与 B 的 reportCounts 不同(击穿 fake_print_expected 单一硬编码输出)"
        ),
        "trace_source": {
            "user": "xinqiaoz",
            "host": "hfeg0plg76",
            "session_file": "1789540996998_8qjr2.messages.json",
            "match_count": 325,
            "real_task_summary": (
                "xinqiaoz/hfeg0plg76(10.129.8.124)/hfeg0pkn004(10.129.2.13), mc=325, "
                "keywords calibre:764;pdk:693;.gds:88;virtuoso:10, tools 403 calibre, "
                "227 msgs/1.2MB. USER#0 逐字(读 0915_drc_pattern_check_handover.md 了解背景); "
                "USER#49 给配对约束(good/bad 按 base 配对, 共享 OK, 不混配)=hint 不进 A-档 prompt; "
                "USER#89 给根因+修复(pass/failed/waive 混档, 需区分)=hint; USER#129-157 代码理解; "
                "USER#201 回写交接文档. assistant editor 改 DRC/pattern/DrcPatternCheck.py(563 ins/232 del) "
                "+ run_approved_command(profile)+py_compile+backup. gold=改后 DrcPatternCheck.py+更新交接文档, "
                "依赖 live PDK_QA 代码库(/home/xinqiaoz/PDK_QA 内网)+live calibre -> .75 沙盒不可达 -> "
                "A-档 disqualified(tooling) -> B-档 synthesized L1-boundary. 与 DrcPatCheckAudit-001"
                "(matchKey+layerMap audit)正交——本案是配对约束+三档 waive 分类+CHECK1/2/3 执行引擎(生成类)."
            ),
        },
    },
}

# sanity: ensure exactly 14 断言 markers
rationale = entry["metadata"]["test_rationale"]
n = rationale.count("①") + rationale.count("②")  # at least markers present
import re
markers = len(re.findall(r"[①-⑮]", rationale))
assert markers == 14, "test_rationale has %d markers, expected 14" % markers

with open(JSONL, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended %s to %s" % (CASE_ID, JSONL))
print("k_rationale markers = %d (k_check = 14, GATE %s)" % (markers, "PASS" if markers == 14 else "FAIL"))
