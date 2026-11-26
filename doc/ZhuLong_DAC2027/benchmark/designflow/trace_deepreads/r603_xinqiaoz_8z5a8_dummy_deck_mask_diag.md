# Deepread: r603 xinqiaoz 8z5a8 — Dummy Deck Mask Diagnosis

## Trace provenance
- session: `1792715254915_8z5a8.messages.json` (xinqiaoz @ hfeg0pkn002 / 10.129.2.11, mc=628, physical_verify)
- 复活池来源：pool_reaudit_C.tsv r590 新判可造（旧判 parked "gold file make_fix_gds.py+fixed deck/config" → 新判可造 analysis/script）

## 用户真实意图（trace-faithful）
- UI#1: handoff 恢复上下文（resume，非 produce-task）
- **UI#2 (核心 produce-task)**: 「排查任务：G5_CIP Dummy deck 部分 mask 无法生成 dummy GDS」+ 背景（calibreDummy.rule TVF → calibreDummy_chip.rule SVRF → calibre 跑 dummy；chip/frame 两子目录；config.ini；DummyPatternGenerator_v5.py）
- UI#3: 「最终可以使用的 config.ini 文件是哪个？」
- UI#4: 「如果想让你再补上 SOH dummy，你有实现方案吗？」
- 364 msgs，agent read_files/read drc.sum/grep SVRF/editor shell 约定文件迭代诊断。

## Agent 真实工作链 + 根因
1. 复制 71MB 现场到 qa_workspace_g5cip；读 config.ini（layers1-14）+ chip/frame TVF 对比。
2. **决定性结构对比**：chip 侧 TYPE_CMP(MT2/M0U)/2ND/SOH 全失败、TYPE_MP/MPstack(M1Z-M4Z) 全成功；frame 侧仅 CMPstack 成功。
3. drc.sum 行 123-128：`Division by zero` 10 次 @ line 34025 DFM PROPERTY。
4. 统计段对比：成功层 M3Z 的 mainPattern 各=1（config layers6 全画）；失败层 MT2b 的 `mainPattern_Extent_..._MT2b_65_8`=0（**65_8 无图形**）。
5. **根因实锤**：MT2 避让块 `BORD_NOT_defineMaskBLK_MT2_Reverse_BORD:peri = BORD NOT Reverse_BORD:peri`，而 `Reverse_BORD:peri`(LAYER MAP 301 DATATYPE 11) 在测试 GDS 无图形 → `BORD NOT 空 = BORD 全部进入避让块` → `gea_bord = (BORD NOT DefMaskBlk) NOT MainBlk` 填充区为空 → 零输出。与 DYT4E QA-18 "BORD NOT TEG" 退化同型。
6. cmpLay(datatype 8) 是 TYPE_CMP/SOH 填充锚层；config.ini layers2=`65_0 65_10 65_16 65_24 140_0 65_14` 缺 65_8 → MT2 锚层空。
7. 交付：诊断报告 + 修正 config.ini（补 65_8/66_8/15_8/47_8 等 cmpLay）。

## Case 合成（B档 mock-behavioral reframe）
- **核心算法参数化**：把「解析 SVRF deck + config.ini → 诊断失败 mask → 输出修正 config」重构为纯 Python3 `dummy_deck_diag.py <deck> <config> <out_md> <out_ini>`。
- 解析逻辑忠实 trace：mask block 以 `// MASK BLOCK: <name>`…`// END BLOCK` 分隔；cmpLay 锚 = `LAYER MAP L DATATYPE 8`；bord_not 锚 = `BORD NOT <name>` → `LAYER <name> <num>` → `LAYER MAP aL DATATYPE aD <num>`(同 num) 解析；mask 失败 iff 任一锚层不在 config.ini drawn 集合。
- **输入 A**（SUT 可见）：deck_A.svrf 6 mask(MT2/M0U/M3Z/M1Z/BWZ/NCZ)+config_A.ini(真实结构，layers2 缺 65_8、layers3 缺 66_8、layers9 缺 15_8/47_8)；4 fail(MT2/M0U/BWZ/NCZ) 2 succeed(M3Z/M1Z)。
- **隐藏 B**（check 跑）：deck_B.svrf 6 mask(TM1/TM2/GP1/GP2/SH1/SH2)+config_B.ini(71_8 缺/72_8 有/303_11 缺/25_8 缺/26_8 有)；3 fail(TM1/GP2/SH1) 3 succeed。
- **隐藏 B2**（反硬编）：deck_B2.svrf 6 mask(ZM1/ZM2/ZP1/ZP2/ZS1/ZS2)+config_B2.ini(80_8 缺/307_11 缺/82_8 缺)；3 fail(ZM1/ZP1/ZS1) 3 succeed。
- **check() 数据驱动**：18 条 a-r（结构 2 + B 失败集合精确 4 + B 缺失层 3 + B 修正 config 4 + 反硬编 A 2 + B2 一致 3 + 确定性 1）。

## 自验
- ref SELFTEST 18/18 PASS ✓
- 3 neg(empty/print_only/hardcoded_A) 全 FAIL ✓ NEGATIVE_SELFTEST ALL-FAIL-OK ✓
- §4.9 deleted_core FAIL ✓
- bool(check)=True ✓
- k_rationale=k_check=18≥8 ✓
- C.jsonl 368→369；ledger mark case ✓（pv 160→161）

## 谱系
produce-task 第十一子型 dummy-deck-anchor-diag（physical_verify，calibre dummy deck 锚层诊断），承 r594/r597/r602 parse+diagnose+structured-output 模式。复活池（pool_reaudit 306 可造）选料第 2 条（r602 后），验证 B 类误杀候选可造。
