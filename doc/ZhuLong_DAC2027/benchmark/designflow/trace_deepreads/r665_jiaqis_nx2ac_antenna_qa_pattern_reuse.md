# trace_deepread r665 — jiaqis nx2ac (天线 QA pattern 复用性评估)

- **session**: `1793264574506_nx2ac.messages.json` (jiaqis @ hfeg0plg09 / 172.16.8.175)
- **scan**: ssh_eda_search_20261116_072610, mc=96, keywords `drc:1607; .gds:65; calibre:15; transistor:2; gdsii:1`
- **trace size**: 936 KB, 99 msgs, 6 user turns
- **domain**: physical_verify (Calibre 天线 DRC deck + GDS QA pattern)
- **ledger**: r537 旧判 `REJECT (Q&A/sim/run-existing/done)` → r665 revival per 2026-11-15 用户令 (旧 weak 筛子作废, pool_reaudit 标 `可造`) → claimed → case

## 用户真实意图 (逐字)

- MSG#0: 「打开FS文件夹，你看一下是不是有一个gds文件」
- MSG#6: 「你能读取ANT_FS.gds这个文件吗」
- MSG#13: 「你是不是不能写脚本文件，查看原因」
- **MSG#23 (核心 produce-task, A档合规)**: 「你结合 `/home/jiaqis/work/zl/ANT/drc_old/ANT/wuliang_SF_update/35H_FS_DRC_Cal_V0d1_Rev02.drc.ant` 这个deck分析一下这个FS文件夹下面的FS的q pattern，现在由于deck的更新需要重新绘制一下qa pattern。你看一下有什么东西是可以复用的」
- MSG#67: 「继续」

## assistant 工具链 + 产物

list_allowed_files → read_files(ANT_FS.gds 13.4MB) → editor 写 6 个脚本:
- `parse_gds.py` (GDS II 解析: 1982 cells / 209470 shapes / lib 0_ANT_FS)
- `compare_decks.py` (Rev01 vs Rev02 deck diff: 400 check blocks 全同, 唯一功能变更 L4171)
- `analyze_deck.py` / `analyze_factors.py` (SF/DF 因子 + LAYER MAP 提取)
- `verify_aai.py` (AA 1104/0 直接映射确认, 无 SIZE)
+ 4 个报告 txt (deck_analysis_report / deck_factors_report / deck_layermap_report / aai_def_report)

## 金标准 (MSG#98 最终报告, 用户隐式接受)

1. **Deck diff**: Rev01 20,653 行 / Rev02 20,654 行; 400 check blocks 名称内容全同; **唯一功能变更** L4171 `SF_GATE = GATE INTERACT (AAi WITH WIDTH <= 0.025)` → `<= 0.055`; 其余仅 `#ENDIF // WITH_4MZ` 位置移动 (WITH_4MZ 未启用, 无功能影响)。
2. **阈值变更含义**: 栅极按 AA 宽度分 SF/DF, 加权有效栅面积 `AREA(SF_GATE)×4.2 + AREA(DF_GATE)×1.2`; 阈值 0.025→0.055 后, 栅宽在 (0.025, 0.055] µm 区间的栅极从 DF(×1.2) 翻转为 SF(×4.2), 有效栅面积变 3.5 倍, 影响所有 A_R 天线比值。
3. **AA 层映射**: AA = GDS 1104/0 (`LAYER AAi AA_drawingi` 直接映射, 无 SIZE), 宽度测量准确; GATE = AAi AND GTi。
4. **GDS pattern 受影响分析**:
   - ANT_FS.gds (1616 顶层 pattern): 2,217 AA shapes → 106 SF(≤0.025) / **0 翻转区** / 2,111 DF(>0.055) → **0 受影响**
   - ANT_COMMON.gds (115 顶层 pattern): 82 AA shapes → 41 SF / **0 翻转** / 41 DF → **0 受影响**
   - Pattern 设计刻意只用 0.025 (正好旧阈值, 新旧都判 SF) 和 ≥0.119 (新旧都判 DF) 两档, 避开模糊区间。
5. **结论**: ✅ 100% 可复用, 无需重画; 22 个 miss-cell (A_R_1/2/3/5, V1~V9_R_13) 是历史分工问题 (在 COMMON 数据集), 与 deck 更新无关。
6. **建议**: 用 Rev02 重跑 QA 归档; 可选新画边界探测 pattern (AA 宽 0.054/0.056) 验证 0.055 阈值。

## 资产可达性

- live GDS 13.4MB (jiaqis 私有, e0031982 身份 scp 可读但二进制不宜进 SUT)
- deck Rev01/Rev02 20K+ 行 (路径 `/home/jiaqis/work/zl/ANT/drc_old/ANT/wuliang_SF_update/`)
- **trace 内 MSG#98 完整保留金标准数值** → reframe 为自包含文本资产, 无需 live 文件。

## B档 mock-behavioral reframe (r665)

- **新子型**: `calibre-antenna-qa-pattern-reuse` (distinct vs ge424 `calibre-drc-deck-structure-stats` = deck 结构统计; 本 case = deck 版本 diff + GDS AA 宽度分类 + 复用性裁决, 跨 deck/GDS 两数据源)
- **deliverable**: `antenna_qa_pattern_reuse_analyzer.py` (纯 stdlib), 读 `<deck_old> <deck_new> <aa_shapes>`, JSON 到 stdout
- **asset A** = 真实衍生: deck_old/new (Rev01/Rev02 切片, 含真实 0.025→0.055 阈值变更 + #ENDIF 位置移动陷阱) + aa_shapes (120 形状, 6 SF / 0 flip / 114 DF, 复刻 ANT_FS 分布) → verdict=reusable (匹配金标准)
- **hidden B** = 合成变体: 阈值 0.030→0.060, 90 形状 (8 SF / **12 flip** / 70 DF) → verdict=**redraw_needed** (方向反转, 防硬编码); check_blocks 5 (≠A 的 6)
- **check() 16 条件 a-p**: zip+compile / B 跑通 JSON / 键齐全 / check_blocks / SF_GATE 功能变更识别 / 阈值+flip_interval / 因子+area_ratio / total / sf_old / **flip_region(关键)** / df / affected_cells / verdict / anti-hardcode(B≠A) / 非功能变更排除 / 确定性3x
- **4 negatives**: empty_shell / print_A_expected / always_redraw_stub / wrong_threshold(DF_GATE) → 全 FAIL
- **自验**: gold 16/16 PASS, 4 negatives 全 FAIL ✓

## 区分性 vs 已交付 jiaqis cases

- DrcDeckStatsAnalyzer-001 (ge424): 通用 SVRF deck 结构统计 (rule blocks / families / #DEFINE / 金属层)
- DrcEnclosureTripleExtract-001: enclosure rule 三元组提取
- DrcVsDrmRuleAudit-001: DRC vs DRM 审计
- **AntennaQaPatternReuse-001 (本 case, nx2ac)**: 跨 deck 版本 diff + GDS AA 宽度翻转区分类 + 复用性裁决 — 独立子型 ✓
