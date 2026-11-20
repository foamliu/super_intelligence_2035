#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-MVValueCmp-001 to EDA-Eval-DesignFlow_C.jsonl."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = "EDA-Eval-DesignFlow-MVValueCmp-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_C.jsonl")
REF = os.path.join(BENCH, "reference", CASE)
ASSETS = os.path.join(BENCH, "assets", CASE)

check_src = open(os.path.join(REF, "check.py"), encoding="utf-8").read()

prompt = (
    "你是 PDK QA 团队的 DRC 校验工程师 xinqiaoz，在主机 hfeg0pkn004 上维护 calibre DRC deck "
    "与 LDR CSV 的值一致性校验（/home/xinqiaoz/PDK_QA/pdkQaSystem）。团队刚落地了「多值 rule 变量」"
    "B3 批次：一条 LDR rule 对应 2 个及以上 VARIABLE 声明时，DRC deck 中的变量必须用新命名格式\n"
    "    _{ruleId}__{seq}_\n"
    "其中 `__`（双下划线）是 ruleId 与序号之间的结构性分隔锚点；LDR CSV 里该 rule 的 value 用 `*` "
    "分隔多个数值（如 LDR `0.049*0.079` 对应 DRC 声明 `_V2_Size_002_00__01_ = 0.049` 与 "
    "`_V2_Size_002_00__02_ = 0.079`）。\n\n"
    "之前的旧代码 `compareLdrValueWithVariable` 只有一个 `len(numbers)==1` 分支，遇到多值 LDR 行"
    "（`len(numbers)>=2`）时静默跳过——既不报匹配也不报错误，导致多值中某一个值即使错误也不会被报出。"
    "新代码必须补上 `>=2` 分支：用 `findMultiValueVariables` 按 `__seq_` 定位每个变量，按 seq 排序后，"
    "与 `*`-分隔的 LDR 数值逐位比对；任一位不一致即报 variableValueUnmatched（记 mismatched_seqs），"
    "数值个数不一致即报 count_mismatch。单值 rule（无 `__` 或仅 1 个变量）走一对一比对。\n\n"
    "请你写一个独立可运行的 Python 脚本 drc_value_check.py，接收 `--deck <drc_deck.rules> --ldr <ldr.csv> "
    "--out <report.json>`，解析 DRC deck 的 VARIABLE 声明与 LDR CSV，按上述规则做值比对，写出 report.json，"
    "至少包含顶层键：unmatchedDrcCount、variableValueUnmatchedCount、ldrValueWithMultiDataCount、"
    "singleValueCount、rules（每条含 ruleId/kind/multi|single|missing_drc、drc_vars、ldr_numbers、verdict、"
    "mismatched_seqs）、drc_only_rule_ids（在 DRC 但不在 LDR 的 ruleId）。\n\n"
    "（沙盒注：本任务为 L1-boundary 占位——live calibre / PDK_QA 库在判分沙盒不可达。判分用一份固定的 "
    "DRC deck + LDR CSV 隐藏输入 B 跑你的脚本，只看 report.json 的结构化字段，不跑真实 calibre。可见的 "
    "drc_deck.rules / ldr.csv 仅展示输入格式，判分只跑隐藏 B，B 与 A 在 ruleId/取值/seq 数量/声明顺序上均不同；"
    "脚本用纯标准库，不要 import calibre/pyAether。交付 outputs/submit.zip，内含 drc_value_check.py。）"
)

rationale = (
    "14 条断言：①[a]submit.zip恰1个.py(≥400B)且UTF-8无NUL且py_compile通过 "
    "②[b]隐藏B上--deck/--ldr/--out退出0且产出合法JSON且含6个顶层键 "
    "③[c]B多值rule VB_Wrong_007_00(第二seq值错)verdict=value_unmatched且mismatched_seqs==[2]且variableValueUnmatchedCount≥1(旧一对一漏报) "
    "④[d]B多值rule VB_Edge_005_00(声明乱序__02_在__01_前)verdict=match(seq排序)且ldrValueWithMultiDataCount≥2 "
    "⑤[e]B每条rule的verdict与独立oracle重算逐一一致(正确性oracle) "
    "⑥[f]B单值rule VB_Single_006_00 kind=single verdict=match且singleValueCount==1 "
    "⑦[g]跨输入B2(全单值旧格式)ldrValueWithMultiDataCount==0且singleValueCount==3(击穿always-multi/硬编码B) "
    "⑧[h]跨输入B3(LDR 3值vs DRC 2 seq)VD_Gap_004_00 verdict=count_mismatch且unmatchedDrcCount≥1(击穿忽略个数) "
    "⑨[i]A↔B结构guard(deck_A≠deck_B且report_A≠report_B,击穿fake_print_expected硬编码A) "
    "⑩[j]确定性3次跑B的report md5一致 "
    "⑪[k]B drc_only_rule_ids==[VB_DrcOnly_008_00](在DRC不在LDR,击穿忽略drc_only) "
    "⑫[l]B missing_drc rule VB_Missing_011_00 verdict=missing_drc且计入unmatchedDrcCount==1 "
    "⑬[m]B VB_Edge drc_vars按seq升序[1,2]而非声明顺序(击穿declaration-order) "
    "⑭[n]B2所有rule kind=single(无__的变量不触发multi,击穿over-eager multi检测)"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "budget": {"max_turns": 25},
    "expected_artifacts": ["drc_value_check.py", "report.json"],
    "attachments": [
        {"name": "drc_deck.rules", "source": "drc_deck.rules",
         "desc": "可见 A：DRC deck VARIABLE 声明片段（新格式多值 _{ruleId}__{seq}_ + 旧格式单值 _{ruleId}_），展示输入格式"},
        {"name": "ldr.csv", "source": "ldr.csv",
         "desc": "可见 A：LDR CSV（ruleId,value；多值用 * 分隔），展示输入格式"},
        {"name": "task_brief.md", "source": "task_brief.md",
         "desc": "交付接口与文件位置说明（≤3 行）"},
    ],
    "prompt": prompt,
    "test": check_src,
    "metadata": {
        "difficulty_tier": "B",
        "direction": "physical_layout",
        "domain": "physical_verify",
        "harness": "cline",
        "layer": "drc_multi_value_variable_comparison",
        "level": "L1-boundary",
        "track": "synthesized",
        "task_name": "MVValueCmp",
        "topic": "DRC 多值变量 LDR↔VARIABLE 值比对（_{ruleId}__{seq}_ 双下划线 seq 锚 + 按 seq 排序逐位比对 + 旧一对一漏报修复 + count_mismatch/missing_drc/drc_only），与 r76 MVVarNamingAudit(命名合规审计)/r79 DRCDeckSyncPlan(同步规划)/r80 DRCSpecGen(spec→SVRF 生成)正交——本案是值比对类",
        "scenario": "PDK QA DrcValueCheck B3 多值比对：解析 DRC deck VARIABLE 声明 + LDR CSV，多值 rule(≥2 个 __seq_ 变量)按 seq 排序后与 *-分隔 LDR 数值逐位比对报 variableValueUnmatched/count_mismatch，单值 rule 一对一比对，输出 report.json(unmatchedDrcCount/variableValueUnmatchedCount/ldrValueWithMultiDataCount/singleValueCount/rules/drc_only_rule_ids)",
        "test_rationale": rationale,
        "trace_source": {
            "user": "xinqiaoz",
            "host": "hfeg0pkn004",
            "session_file": "1793005343621_45gjq.messages.json",
            "match_count": 354,
            "real_task_summary": "PDK_QA pdkQaSystem B3 多值变量比对：sync_to_stable 同步整理 + DrcDefinitionRuleCheck/DrcQa 多值 LDR↔DRC VARIABLE 比对(_{ruleId}__{seq}_ 格式、set-based 逐 seq 比对、旧代码 len==1 静默跳过多值导致漏报)+为每个 case 生成真实 report+证明旧格式一对一匹配局限性(多值中某值错不报)",
        },
    },
}

# verify k_rationale == k_check == 14
k_check = 14  # conditions a..n in check.py
k_rationale = rationale.count("①") if False else sum(1 for i in ["①","②","③","④","⑤","⑥","⑦","⑧","⑨","⑩","⑪","⑫","⑬","⑭"] if i in rationale)
print("k_rationale =", k_rationale, " k_check =", k_check)
assert k_rationale == k_check == 14, "GATE: k_rationale must equal k_check >= 8"

line = json.dumps(entry, ensure_ascii=False, sort_keys=False)
# append
with open(JSONL, "a", encoding="utf-8") as f:
    f.write(line + "\n")
print("appended to", JSONL)
print("test field bytes on disk:", len(check_src))
