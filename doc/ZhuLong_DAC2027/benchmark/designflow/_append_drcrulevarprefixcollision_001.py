#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-DrcRuleVarPrefixCollision-001 to EDA-Eval-DesignFlow_C.jsonl."""
import json, os, hashlib

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-DrcRuleVarPrefixCollision-001"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_C.jsonl")
CHECK = os.path.join(BENCH, "reference", CASE, "check.py")
PROMPT = os.path.join(BENCH, "assets", CASE, "prompt.txt")

with open(CHECK) as f:
    check_content = f.read()
with open(PROMPT) as f:
    prompt_content = f.read()

case = {
  "task_id": CASE,
  "mode": "design_flow",
  "entry_point": "outputs/submit.zip",
  "prompt": prompt_content,
  "attachments": [
    f"assets/{CASE}/prompt.txt",
    f"assets/{CASE}/task_brief.md",
    f"assets/{CASE}/sample_input/drc.report",
    f"assets/{CASE}/sample_input/ldr.csv",
    f"assets/{CASE}/sample_input/drc.deck",
    f"assets/{CASE}/sample_input/rule.snippet",
    f"assets/{CASE}/hidden/hidden_manifest.json",
  ],
  "test": check_content,
  "metadata": {
    "trace_source": {
      "user": "xinqiaoz",
      "host": "10.129.2.11",
      "session_file": "1794307210079_xnd0q",
      "match_count": 249,
      "real_task_summary": "DRC QA report shows 'variable with unmatched value' errors for _V1_ENC_007_00_AUTO_ etc.; user suspects LDR rule V1_ENC_007_00 (no deck VARIABLE) prefix-matched the Auto rule's variable, causing false error. Cross-validate report + LDR CSV + DRC deck to diagnose rule-name prefix collision."
    },
    "domain": "physical_verify",
    "track": "mock-behavioral",
    "tier": "L1",
    "test_rationale": (
      "14 条断言：①submit.zip 合法且包含 solve.py "
      "②隐藏输入 hidden/b（drc.report_B/ldr_B.csv/drc.deck_B）与 hidden/b2（drc.report_B2/ldr_B2.csv/drc.deck_B2）齐全 "
      "③输出 JSON 含顶层键 unmatched_variables/undefined_drc_rules/prefix_collisions/genuine_unmatched/root_cause/counts/reproduction_confirmed "
      "④unmatched_variables 与 B 真值一致（3 个变量，含 1 个真未匹配 + 2 个 _AUTO_ 前缀碰撞） "
      "⑤undefined_drc_rules 与 B 真值一致（V4_SP_002_10/V5_SP_002_10） "
      "⑥prefix_collisions 每条含 base_rule/auto_rule/variable/ldr_base_value/ldr_auto_value 且与 B 真值一致（2 条） "
      "⑦genuine_unmatched 与 B 真值一致（仅 _AT7_DRW_003_02_A_） "
      "⑧root_cause == 'rule_name_prefix_collision' "
      "⑨counts 四项（variableValueUnmatchedCount=3/variableUndefinedDrcCount=2/prefix_collision_count=2/genuine_unmatched_count=1）与 B 真值一致 "
      "⑩reproduction_confirmed == true（前缀碰撞数 == _AUTO_ 结尾报错变量数） "
      "⑪B2 跨输入泛化：unmatched_variables/undefined_drc_rules 与 B2 真值一致（反硬编码 A 或 B） "
      "⑫B2 prefix_collisions（1 条 L1_DRW_001_00）与 genuine_unmatched（空）与真值一致 "
      "⑬B2 counts（prefix_collision_count=1/genuine_unmatched_count=0）与 root_cause 与真值一致 "
      "⑭退化守卫：B 的 prefix_collision_count 必须 == 2（不是 A 的 3），反硬编码 A 的答案"
    )
  }
}

# byte-iden check
on_disk_md5 = hashlib.md5(check_content.encode()).hexdigest()
embedded_md5 = hashlib.md5(case["test"].encode()).hexdigest()
assert on_disk_md5 == embedded_md5, f"test field != check.py: {on_disk_md5} vs {embedded_md5}"

# count rationale assertions
import re
k_rationale = len(re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭]", case["metadata"]["test_rationale"]))
k_check = len(set(re.findall(r'_cond\("([a-z])"', check_content)))
print(f"k_rationale={k_rationale}  k_check={k_check}  md5={on_disk_md5}")
assert k_rationale == k_check, f"k_rationale({k_rationale}) != k_check({k_check})"
assert k_check >= 8, f"k_check({k_check}) < 8"

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(case, ensure_ascii=False) + "\n")
print("appended to", JSONL)
