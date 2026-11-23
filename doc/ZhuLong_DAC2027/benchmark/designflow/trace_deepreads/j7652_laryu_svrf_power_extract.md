# deepread: j7652 laryu SVRF power/ground net extraction deck 解读

- **session**: `1795412906029_j7652.messages.json`
- **user / host**: laryu @ hfeg0plg92
- **match_count**: 317 (layout_aether: aether:1149;pyaether:579;schematic;dbopencv;lvs)
- **domain**: physical_verify (Calibre SVRF)
- **case_id**: SvrfPowerNetExtract-001
- **round**: r1038 (shard C)

## 会话总体

Q&A/学习型会话，229 条消息，多个子任务串联：
1. MSG 0-157：检查 pyAether 环境是否可用于 PyCharm（env-config / debug Q&A）。
2. MSG 158-161：解释 SVRF `getPower.rule` 语法（doc-search / analysis Q&A）← **本 case 取此子任务**。
3. MSG 162-228：解释 pyAether 代码片段（`global` 关键字、`IMCutHierarchyTraverserResultTable` 定义位置、`InnoutHierarchyTraverser` 机制、`validLib` 数据流、`etMakeTable` API、`cellTbl` 二次赋值、`member` 函数、`CXMTleSearchDupInstance_GetLibrary` 递归）。

## 选定子任务（MSG 158-161）

laryu 贴出完整 Calibre SVRF 电源/地网络提取 deck `/home/laryu/study_try/SVRF_study/getPower.rule`，问「帮我逐段解读这个文件」。

### deck 结构（A，verbatim 入 asset）

- **LAYER MAP 18 条**：M1-M5 drawing/pin + V1-V4 drawing + M2_term/M2_CLOSE/M2_open + text_drawing，物理层号 88/90/91(×4)/92/93/94/95/102/103/230 → 内部号 8801-8818。
- **PRECISION 10000**。
- **TEXT LAYER** ×5（M1-M5 pin）。
- **M2NET_SWITCH = OR M2_drawing M2_CLOSE M2_open**（M2 三子层合并）。
- **ATTACH** ×5（pin 文本 → 金属层）。
- **CONNECT** ×4：M1→V1→M2→V2→M3→V3→M4→V4→M5 完整堆叠链。
- **NET** ×18：「vss!」×9 + 「vcc!」×9（每层每网络一条）。
- **out_put_vcc / out_put_vss** 两个 DFM RDB GDS 输出块：每块 9 条 `<层名> <layer> <datatype>` 写回原层号，PROPERTIES APPEND _auto_vcc / _auto_vss。

### agent 产出（MSG 161）

结构化 markdown 逐段解读：①层号映射表 ②精度 ③文本层 ④逻辑运算/层合并 ⑤ATTACH/CONNECT ⑥NET 按名抓取 ⑦结果导出（DFM RDB GDS + 层号还原 + 属性标记）⑧设计意图总结（电源/地网络提取）。纯分析 Q&A，无文件交付。

## reframe

Q&A → 通用 SVRF 电源/地网络提取 deck 结构化分析工具 `svrf_power_extract_analyzer.py`：解析 precision / layer_map / text_layers / derive_ops / attach_ops / connect_ops / net_extractions / output_blocks / net_names / counts → JSON。纯标准库正则行解析，输出块用 `{...}` 状态机配对 entry/PROPERTIES/APPEND。

## 隐藏变体（反硬编）

- **deck_b.svrf**：3-metal M1-M3 + V1-V2，PRECISION 2000，M3NET=OR(M3_drawing,M3_term,M3_label)，CONNECT 2 边 M1-V1-M2-V2-M3NET，nets VDD/GND，out_vdd/out_gnd 块带 _pg_vdd/_pg_gnd。
- **deck_b2.svrf**：2-metal M1-M2 + V1，PRECISION 1000，**无 derive**，CONNECT 1 边，nets AVDD/AVSS，out_avdd/out_avss 块带 _avdd_tag/_avss_tag。

## 质量门

- GOLD selftest 19/19 PASS；3 fakes（empty/print-A/deleted-core）全 FAIL；3-seed 确定性字节一致。
- test_rationale 19 条断言（①-⑲），k_rationale==k_check==19≥8。
- 反硬编：B 不含 A 专属层名/网络/属性/精度；B2 derive_ops 为空（与 A/B 的 1 条不同）。
