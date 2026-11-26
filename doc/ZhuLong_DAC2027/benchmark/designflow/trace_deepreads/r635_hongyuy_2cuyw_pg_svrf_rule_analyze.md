# r635 deepread — hongyuy / 2cuyw — Calibre SVRF PG DRC rule analysis Q&A

**session**: `1792549371930_2cuyw` (hongyuy@hfeg0plg64, mc=37, physical_verify)
**fetched via**: .75 ssh `10.129.8.102` → `/home/hongyuy/.cline/data/sessions/1792549371930_2cuyw/1792549371930_2cuyw.messages.json` (139KB, 36 msgs, 11 real user turns)
**ledger**: claimed + marked case (PgSvrfRuleAnalyze-001)

## user intent (verbatim, 7 distinct PG rules)

用户逐条粘贴 Calibre SVRF PG DRC 规则代码，每条问「这个DRC 怎么修」/「怎么修理这个DRC」：

1. **PG_S_016_00** — Min, value 0.09, PG_NCH/PCH PG-to-PG space opposite direction. ops: A0=EXT GPOLY (PG NOT PG_HH) <... ABUT<90 SINGULAR OPPOSITE REGION; A0 INTERACT DIF_TR; A1=GPOLY TOUCH EDGE GATEW; EXT A1 (PG NOT PG_HH) <...
2. **PG_EXT_031_00** — Min, value 0.05, G_PG extension from {AT4 NOT DEVTR;mark20}. 例外: G_PG width>=0.05 inside SA/SWD; G_PG inside Efuse. ops: A1=GPOLY NOT (...); ENC (DIF_ALL NOT DEVTR_mark20) A1 <...; (EXPAND EDGE ...) NOT PG
3. **PG_F_012_60** — Check, value check, Not allow PG wiring overlap of AT4. ops: PG_drawing AND (AT4 NOT DEVTR_mark20)
4. **PG_L_009_00** — Exact, value 0.097, Gate length of NTNLVIO_SA. ops: A1=GATEL COIN EDGE (OR GATE_NTNLVIO_SA GATE_NTNLVIO_CSL); LENGTH A1 != _PG_L_009_00_
5. **PG_F_0131_04** — Insert, dummy PG insertion between Tr actives. 复杂多步 A00..A04
6. **PG_L_013_00** — Exact, value 0.097, Gate length of PTNLVIO_SA. ops: A1=GATEL COIN EDGE GATE_PTNLVIO_SA; LENGTH A1 != _PG_L_013_00_
7. **PG_S_0105_05** — Max, value 0.24, Space between PG_DUMMY in channel direction. 复杂多步 A0..A4 + D0..D3

## agent response pattern

每条规则，agent 产出结构化 markdown 分析（无文件交付，沙盒仅 `check_pyaether.py` 无关 + shell 禁用）：
- 规则完整解读（原文 code block）
- 各层含义表（层名 | 含义）
- 规则本质 / 分步解析（每步几何含义 + ASCII 示意图）
- 修复方法（多种策略 1️⃣2️⃣3️⃣4️⃣，含 before/after 示意图）
- 诊断表 / 总结

## case synthesis (B档 mock-behavioral grounded-extraction-tool reframe)

承 r617 TvfSetlayerExpl / r630 LvsHcellFailReportExtract / r633 MaskBlkSvrfWriteExtract 模式：纯分析 Q&A 在 2026-11-15 新标准下为合法用户意图（旧规则误判 weak）；reframe 为**grounded-extraction-tool**——把"分析规则结构"做成可判分的解析工具，每个 JSON 字段都从规则文本本身 parse 出来，不凭领域知识编造。

- **deliverable**: `pg_svrf_rule_analyzer.py <rule.svrf> <output.json>`
- **asset A** = `rule_a.svrf`（PG_S_016_00 逐字，Min/0.09/4 op steps/layers GPOLY+PG+PG_HH+DIF_TR+GATEW）
- **隐藏 B** = `rule_b.svrf`（合成 PG_X_042_07，Max/0.18/6 op steps/layers DIF_TR+GATEL_HV+PG_DUMMY/exceptions 2 条）——与 A 在 check_type/value/intent/layers/op_steps 全不同
- **隐藏 B2** = `rule_b2.svrf`（合成 PG_Y_055_02，Check/check/1 op step/layers M1_drawing+PG+PG_HH）——反硬编交叉校验

## check.py — 23 条断言 (a-w)

结构3(a:zip含py / b:py_compile / c:B运行exit0+合法JSON) + schema1(d:8顶层键) + B反硬编7(e:rule_id==PG_X_042_07 / f:check_type==Max / g:value==0.18 / h:intent含PG_DUMMY+channel不含PG_NCH / i:exceptions==2 / j:layers含PG_DUMMY+GATEL_HV / k:layers不含A专属GATEW+GPOLY) + B ops3(l:op_steps==6 / m:vars==[A0..A4,空] / n:INTERACT==4) + B op_inventory2(o:SIZE==1 / p:EXT==1) + B2反硬编6(q:运行 / r:rule_id==PG_Y_055_02 / s:check_type==Check / t:value==check / u:op_steps==1 / v:layers含M1_drawing) + 确定性1(w:两跑字节一致)

## self-verify

- ref 23/23 PASS ✓（disk check.py 真实路径）
- 3 neg (naive_empty/print_expected/deleted_core) 全 FAIL ✓ NEGATIVE_SELFTEST ALL-FAIL-OK ✓
- §4.9 (a)(b)(c) 三假全 FAIL ✓（即上述 3 neg）
- k_rationale == k_check == 23 ≥ 8 ✓
- bool(check)=True ✓
- C.jsonl 394→395

## 意义

新标准（2026-11-15）下又一例 analysis-Q&A grounded-extraction-tool reframe 落地，证明 fresh-pool mid-mc(30-55) 段经 reframe 仍可造出有牙 case。2cuyw 在旧规则下会被判 "analysis-Q&A thin, no produce-task, weak" 而 REJECT；新标准下恢复为合法用户意图。
