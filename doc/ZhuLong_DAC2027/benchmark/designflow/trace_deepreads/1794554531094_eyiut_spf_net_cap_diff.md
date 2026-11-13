# Deepread: 1794554531094_eyiut — DSPF/SPF cross-file net-capacitance diff comparator

- **session**: 1794554531094_eyiut · user han1li @ hfeg0pkn001[10.129.2.10] · mc30 (netlist:17 first-keyword) · 457KB
- **source**: 11/14 daily log `eda_trace_20261114.log` (NOT in 11/13 summary — genuinely fresh)
- **domain**: pnr_signoff (PEX/DSPF parasitic netlist cap comparison)
- **archetype**: dspf-spf-cross-file-net-capacitance-diff-comparator (distinct from r483 SpfRcSummaryGen single-file RC summary)

## User intent (real turns)
- U#1 (核心 produce-task): 「我给你两个路径 是spf网表 帮我比较net电容」 + 两个 .dspf.TYPICAL_0 / .spf_RC 路径 (同 cell AIOI21D1DBCP51H180L6W25T5ULVT, 不同 PEX 提取 Rev03 vs Rev07, 不同温度 98°C vs 0°C)
- U#2: 追问如何知道 captab 版本 (答: 从文件头 `** CAPTAB_FILE ...Rev07...` 注释行读)
- U#3: 换一对 LVT cell 的两个 SPF 文件再比 (Rev03/98°C vs Rev07/0°C)
- U#4: file1 不变, 给新 file2 (TYPICAL_98, 同温 98°C vs Rev07) 再比 → 发现同温下 cap 值与 0°C 完全一致

## Agent tool chain
list_allowed_files → read_files (分段读两文件) → editor 写 compare_net_cap.py / compare_lvt.py → run_approved_command (python-runner) 跑 → 文本报告 (表格). 中途 editor 多次把文件改坏, 用 python-runner 直跑恢复.

## 关键解析逻辑 (agent 自创, A-faithful)
1. **net cap 提取**: regex `^\s*\*\|\s*NET\s+(\S+)\s+([0-9eE.+\-]+)PF` (IGNORECASE) 匹配 `*|NET <name> <cap>PF` 行 → {net_name: cap_pF}
2. **header 提取**: `*|PROGRAM "..."`, `*|VERSION "..."`, `*|DIVIDER`, `** CAPTAB_FILE .../RevXX_...` (正则抽 RevXX), `*|OPERATING_TEMPERATURE <int>`, `** CAPTAB_TIME_STAMP`
3. **net 匹配**: case-insensitive (net3 vs NET3 视为同 net) — 真实场景 file1 小写 file2 大写
4. **diff 计算**: per-net delta=cap2-cap1, diff_pct=delta/cap1*100, ratio=cap2/cap1; total cap per file; total_diff_pct
5. **added/removed**: in file2 not file1 / in file1 not file2 (case-insensitive 集合差)
6. **报告**: 总体统计表 + 逐 net 对比表 (按 diff% 排序) + header 对比表

## A-faithful 判定
用户给: 两个 SPF 路径 + 「比较 net 电容」. 用户未给: `*|NET ...PF` regex / header 提取规则 / case-insensitive 匹配 / diff% 公式 / added-removed 集合逻辑 / 报告版式. → 合格 (WHAT 给了, HOW 全 agent 自创).

## deliverable 可行性
读/写私有 `/proj/lacaa/...` + `/home/han1li/compare_*.py` → .75 SUT 沙盒 Permission denied → **INFEASIBLE → B 档合成**.

## 合成方案 (B 档)
- SUT 交 `spf_net_cap_diff.py` (纯 stdlib CLI `--file1 --file2 --out`): parse `*|NET` cap + header + case-insensitive 匹配 + diff + added/removed → report.json
- A 可见: file1_A (Rev03/98°C/6net) + file2_A (Rev07/0°C/7net, NET3 case-trap, gndA removed, auxA+extraA added)
- B 隐藏: file1_B (Rev05/25°C/5net) + file2_B (Rev09/85°C/6net, CLKB case-trap, gndB removed, scanB+auxB added), 零名重叠 A
- check.py 18-20 条件 (a-t): zip/stdlib/CLI/keys/counts/matched/added/removed/totals/diff_pct/case-trap/captab_rev/temp/cross-input-guard/3-seed/per-net-diff/ratio
- negatives: naive_empty / print_only / hardcoded_A / core_removed / no_casefold
