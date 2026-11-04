#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-DrcLegacyFallback-001 to EDA-Eval-DesignFlow_C.jsonl."""
import json, os, sys

CASE_ID = "EDA-Eval-DesignFlow-DrcLegacyFallback-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
HERE = os.path.join(BENCH, "reference", CASE_ID)
ASSET_DIR = os.path.join(BENCH, "assets", CASE_ID)
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_C.jsonl")

# read check.py source
with open(os.path.join(HERE, "check.py"), encoding="utf-8") as f:
    check_src = f.read()

prompt = open(os.path.join(ASSET_DIR, "prompt.txt"), encoding="utf-8").read()

entry = {
    "task_id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["legacy_fallback_matcher.py", "legacy_match_report.json"],
    "attachments": [
        f"assets/{CASE_ID}/task_brief.md",
        f"assets/{CASE_ID}/pattern_manifest.json",
    ],
    "prompt": prompt,
    "test": check_src,
    "metadata": {
        "domain": "physical_verify",
        "track": "synthesized",
        "level": "L1-boundary",
        "layer": "L2",
        "difficulty_tier": "L1-boundary",
        "direction": "generation",
        "harness": "cline",
        "task_name": "DrcLegacyFallback",
        "topic": "DRC pattern check legacy cell-name fallback matching",
        "scenario": "PDK QA DRC pattern check: support legacy cell names (no _F/_P, no good_/bad_) as fallback matching, with Step 5b prefix fallback + ambiguity guard + goodExisting default 0 for legacy bad-only + matchType classification (new_pair/legacy_bad_only/pattern_not_found)",
        "test_rationale": (
            "16 条断言：①[a]submit.zip 恰含 1 个 .py(>=400B,UTF-8 无 NUL)且 py_compile 通过 "
            "②[b]在隐藏 B 上跑 exit0 + stdout 为合法 JSON + 顶层 15 键(verdict/reportCounts/ruleResults/"
            "resultTable/passRules/failedRules/waivedRules/skipRules/patternNotFoundRules/"
            "patternNotFoundCount/unusedCells/unusedCellCount/cellsByBase/legacyCells/matchTypeCounts)齐全 "
            "③[c]reportCounts.total==len(rules_B) 且 pass+failed+waived+skip+pattern_not_found==total 且与 ruleResults 独立重计数一致 "
            "④[d]parsePatternCell 分类：legacyCells==独立重算(无 _F/_P 后缀且无 BAD_/GOOD_ 前缀) 且 cellsByBase 键覆盖其余 new-style cell 按规范化 base 分组 "
            "⑤[e]buildCellsByBase 正确：每个 base 的 bad=_F cell/good=_P cell 对账；规范化键('.'=='_')使 rule M3.W.5 命中 BAD_M3.W.5_F 的 base "
            "⑥[f]Strategy 1-4 new-pair 匹配：FS.S.11/M3.W.5/A9.Q.2/LDO_CORE_VRG 均为 new_pair 且 bad/good 非空 "
            "⑦[g]Step 5 legacy 匹配：NOR3X_nope 经前缀兜底为 legacy_bad_only(badCell=NOR3X, goodCell='') "
            "⑧[h]Step 5b legacy 前缀兜底(剥尾 _C/_P)：BUF4_TRG 为 legacy_bad_only(badCell=BUF4) "
            "⑨[i]goodExisting：legacy_bad_only 规则 goodExisting==0(不检查不 fail)，new_pair 规则 goodExisting 非零 "
            "⑩[j]matchType 互斥：每个 ruleResult matchType∈{new_pair,legacy_bad_only,pattern_not_found}；new_pair 要求 goodCell 非空，legacy_bad_only 要求 goodCell 空，pattern_not_found 要求 badCell 空；三者计数和==total "
            "⑪[k]patternNotFound 紧凑列表无重复 且 patternNotFoundCount==len(list)==reportCounts.pattern_not_found==matchTypeCounts.pattern_not_found "
            "⑫[l]跨输入 B2(全 new-style 无 legacy)：exit0 + legacy_bad_only==0 + new_pair==len(rules_B2) + legacyCells==[](击穿 always-legacy/always-bad-only) "
            "⑬[m]跨输入 B3(全 legacy 无 new-style)：exit0 + new_pair==0 + legacy_bad_only==len(rules_B3) + cellsByBase=={}(击穿 always-new-pair) "
            "⑭[n]跨输入 B4(FOO 与 FOO_BAR 同为 FOO_BAR_X 干净前缀歧义)：FOO_BAR_X 为 pattern_not_found(Step 5b 恰 1 匹配闸门) + BAZ_Y 为 legacy_bad_only(BAZ) + Q_X 为 new_pair(击穿 always-first/always-match) "
            "⑮[o]确定性：B 上重跑 3 次 md5 一致 "
            "⑯[p]A↔B 结构 guard：rules_A 的 ruleId 集合≠rules_B 且 A 的 reportCounts≠B 的 reportCounts(击穿 fake_print_expected 硬编码单一期望)"
        ),
        "trace_source": {
            "user": "xinqiaoz",
            "host": "hfeg0plg76",
            "session_file": "1789892841041_i4c8d.messages.json",
            "match_count": 321,
            "real_task_summary": (
                "xinqiaoz/hfeg0plg76(10.129.8.124), mc=321, keywords pdk:714;calibre:414;.gds:113;virtuoso:9, "
                "tools read_files:34/run_approved_command:31/editor:29/search_codebase:2, 206 msgs/1.1MB. "
                "USER#1 逐字(handoff 恢复 HANDOFF_drc_pattern_check.md); USER#6 逐字(A-档 seed 提出目标)「我们需要同时支持原来的无 _F/_P，无 good_/bad_ 的 cell 名称，作为匹配时的兜底机制」; "
                "USER#7 给 3 点修复方案(收集旧式 cell+Step 5 兜底+goodExisting 默认)=hint 不进 prompt; USER#12-14 给 TSV_S_03 前缀匹配根因+修复(Step 5b 前缀兜底)=hint; "
                "USER#15 最终接受(回写 proposal 文档). assistant editor 改 DRC/pattern/DrcPatternCheck.py(7 次: 收集 legacy cell+getTargetCellPair Step 5 兜底+Step 5b 前缀兜底+goodExisting 默认 0+report patternNotFound 紧凑列表) + py_compile + run_approved_command(profile)+backup. "
                "gold=改后 DrcPatternCheck.py+更新 proposal 文档, 依赖 live PDK_QA 代码库(/home/xinqiaoz/PDK_QA 内网)+live calibre -> .75 沙盒不可达 -> A-档 disqualified(tooling) -> B-档 synthesized L1-boundary. "
                "与 DrcPatCheckAudit-001(matchKey+layerMap audit)/DrcPairWaiveClassify-001(配对约束+三档 waive 分类)正交——本案是 legacy cell 名兜底匹配+前缀兜底+matchType 分类(生成类)."
            ),
        },
    },
}

# append
with open(JSONL, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False, sort_keys=False) + "\n")
print(f"appended {CASE_ID} to {JSONL}")

# verify roundtrip: last line parses and test==disk
with open(JSONL, encoding="utf-8") as f:
    last = f.readlines()[-1]
d = json.loads(last)
disk = open(os.path.join(HERE, "check.py"), encoding="utf-8").read()
print("task_id=", d["task_id"], "test==disk:", d["test"] == disk, "test_len=", len(d["test"]))
print("metadata.domain=", d["metadata"]["domain"], "rationale head=", d["metadata"]["test_rationale"][:60])

# count total
with open(JSONL, encoding="utf-8") as f:
    n = sum(1 for _ in f)
print("jsonl_C total entries=", n)
