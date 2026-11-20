#!/usr/bin/env python3
"""Fix remaining stale snapshot lines in MEMORY_DESIGNFLOW_A.md."""
import re

PATH = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW_A.md"
text = open(PATH, encoding="utf-8").read()

# Replace the "本轮交付" bullet (currently DeadLoopScan-001) with CalibreOpen1Fix-001
new_delivery = ("- ✅ **本轮交付**：EDA-Eval-DesignFlow-CalibreOpen1Fix-001 合成 ✓（pnr_signoff / L2 / A-faithful）。"
    "trace 1789545344007_xchvr (ellawu/hfeg0pkn005/mc122)。**A-faithful verbatim prompt**（[0] 原话逐字）："
    "`ERROR: Error OPEN1 - problem with access, file type, or file open of file: calibreSTIcmp.rule.`。"
    "金标 = 真实 trace [74] 助手诊断（根因 = calibreSTIcmp.rule 缺 LAYOUT PRECISION 语句，脚本算了 precision=10000 "
    "却从未注入；次要 rsync 返回未检查/文件未校验/sed 仅改 PATH/PRIMARY）。交付件 = fix.py（python stdlib，CLI "
    "`python3 fix.py <rule_file> <config_file> <output_rule>`，从 config 读 precision 注入 LAYOUT PRECISION："
    "replace 已存在 / insert 于 LAYOUT system 后）+ diagnose.json（root_cause/issues/fix_summary 三键）。"
    "check.py **14 条断言 (a)-(n)**，subprocess 在 A fixture rule + 隐藏 B fixture rule 上跑候选（§4.2 L2 结构判分，"
    "不需真跑 calibre）。自验：ref PASS 14/14；4 negative（fake_empty/fake_print_expected/fake_core_deleted/"
    "naive_stub）全 FAIL（NEG_SELFTEST ALL-FAIL）；§4.9 (a)(b)(c) 三假覆盖。"
    "**k_rationale=14=k_check=14≥8 GATE PASS ✓**。test==disk check.py roundtrip OK，A jsonl 33→34 条。")
text = re.sub(r"- ✅ \*\*本轮交付\*\*：EDA-Eval-DesignFlow-DeadLoopScan-001.*?A jsonl 32→33 条。", new_delivery, text, count=1)

# Fix the coverage line "A jsonl 33 条)" -> "A jsonl 34 条)"
text = text.replace("covered=33 · touched=52 · parked=19；A jsonl 33 条)",
                    "covered=33 · touched=52 · parked=19；A jsonl 34 条)")

# Fix 泄漏隔离 line to mention CalibreOpen1Fix
new_leak = ("- 🔒 泄漏隔离: CalibreOpen1Fix-001 资产仅 prompt+brief+buggy 脚本+A rule+A config"
            "（0 判分器/答案/隐藏/B）；hidden B (不同 process cxmt10G7/precision=1000/层名 M2CORE) 不进 SUT 沙箱；"
            "判分独立 /tmp，check.py+hidden 从 reference/ 复制；anti-hardcode (m)(n) 防精度硬编码。")
text = re.sub(r"- 🔒 泄漏隔离: DeadLoopScan-001.*?check\.py\+hidden 从 reference/ 复制。", new_leak, text, count=1)

open(PATH, "w", encoding="utf-8").write(text)
print("[mem] stale lines fixed; size =", len(text), "bytes")
