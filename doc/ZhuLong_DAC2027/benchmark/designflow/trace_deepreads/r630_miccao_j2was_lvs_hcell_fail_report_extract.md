# r630 deepread — miccao j2was LVS hcell-fail report read-and-explain

- trace: `1790227470128_j2was` @ miccao hfeg0plg37 (10.129.32.47), mc=10
- keywords: lvs:61;calibre:14;pdk:4;cmos:3;.spi:2;.gds:2;.cdl:2
- file: `/home/miccao/.cline/data/sessions/1790227470128_j2was/1790227470128_j2was.messages.json` (35628 B, 7 msgs)
- session: 2 user turns (1 real), 3 assistant turns (1 read + 1 read-more + 1 present)

## 用户意图（逐字）
U#0: `<user_input mode="act">/home/ziyuny/lvsdebug/reports/20260921_Ary_1BK_2piece_WLx448_add_device_layer_deep_v2.md 我要看这个报告</user_input>`

单轮、提需求未给根因/方案 → A档合格 produce-task (read-and-explain)。

## 报告内容（gold artifact，232 行 markdown）
- 标题: Ary_1BK_2piece_WLx448_add_device_layer
- 工具: Argus 2025.06.sp1.hf9，层级化模式，64 CPU，53 分钟，**LVS FAIL**
- 根因: hcell 对应关系匹配失败 — device `switch_close`，device layer `dev_in_layers_98_h.oas`，
  layer PCB，device code `$D=98`；图形跨越 `BL_Connection_*` 子单元边界，被提取到
  `Ary_10sec`/`Ary_90sec`/顶层 `Ary_1BK`
- device 总量 767,379 版图=源网表精确闭合（真错非假错）
- 首个 FAIL: `Ary_10sec_WLx488_scheme1`；叶子单元 10 个全 PASS
- 伴随: 地网短路 4,016 条；未附着文本 18.9 万行；电源-地直连/属性错误未发现
- 顶层 flat switch_close = 74,640（应为 0）
- 修复方案 A(快速/PDK) / B(根治首选/PDK) / C(根治备选/版图 device layer 输入文件)
- 行动清单 7 条（优先级 × 针对 × 行动 × 验证）

## 判定
2026-11-15 新标准：doc-view/read-and-explain 是合法用户意图（旧规则误判 weak）。
miccao 是已知 C 作者 (r624 9pcjd AutoCell security check)。
→ ACCEPT，B档 mock-behavioral grounded-extraction-tool reframe（承 r602-r617 TvfSetlayerExpl 模式）。

## case: LvsHcellFailReportExtract-001
- deliverable: `lvs_report_analyzer.py <report.md> <output.json>` 解析 LVS 分析报告 → 结构化 JSON
- asset A: lvs_report_a.md（真实报告逐字）
- hidden B: lvs_report_b.md（变体：设计名 Ary_2BK_4piece_WLx896 / 工具 2025.07.sp2.hf1 / 器件 switch_open /
  层 PCD / file dev_in_layers_72_h.oas / 总量 1,534,758 / 首FAIL Ary_20sec_WLx896_scheme2 /
  地网短路 8,032 / 顶层 flat 149,280 — 9 个标量字段全不同，结构同 A）
- k=15 a-o: 结构2 + B运行1 + 9 个 B 标量 anti-hardcode(c-l) + fix 3 + actions 7 + 确定性1
- 自验: ref 15/15 PASS✓；3 neg(naive_empty/print_expected_A/deleted_core)全FAIL✓；
  §4.9 三假 FAIL✓；embedded test==disk roundtrip✓；bool(check)=True✓；k=15≥8✓
- C.jsonl 389→390；mark case✓ (pv, ledger_C case 390→391)
