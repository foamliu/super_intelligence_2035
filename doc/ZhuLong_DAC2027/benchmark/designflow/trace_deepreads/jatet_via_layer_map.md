# Deepread: 1793956475658_jatet — via-layer-mapping Q&A reframe candidate (r693)

**Trace**: `/home/e0024852/.cline/data/sessions/1793956475658_jatet/1793956475658_jatet.messages.json`
- host: 10.129.2.13 (hfeg0pkn004), user: e0024852, mc=143
- size: 618 KB, 172 msgs, 95 user turns, 87 tool_use
- keywords: pyaether:252; lvs:151; aether:149; drc:103; .gds:54; calibre:50; pex:28
- **cross-shard note**: session 已在 trace_ledger_B.tsv parked (2026-11-09, "wrong-shard(layout/calibre/schematic)or-vague") — B 识别为 C 域但未造；C 可拾取但 claim 被 4-shard union 排除拒绝（需 next 轮特殊处理或 B 释放）

## 用户真实意图（双意图拆分 per A r657 taxon）

**意图① (可造, via-layer-mapping Q&A)**: U#88 (verbatim)
> "V0D/V0G/V0R/V1/Vxa/Vx/Vxb represent which layer to which layer"

用户看了 LVS deck 的 VIA 层定义后，问每个 via 名对应的 from→to 层映射。助手 grep LVS deck 的 LAYER name 定义 + tran.map + metal 层排列顺序，产出 via 层映射表（V0D=AA→M0 源/漏接触孔 / V0G=GT→M0 栅极接触孔 / ...）。这是 **retrieval + structured-extraction** Q&A：fixture = LVS deck 节选（LAYER name defs + 注释 + tran.map），candidate = 解析 deck 输出结构化 JSON {via_name: {from_layer, to_layer, purpose, evidence_lines}}。

**意图② (不可造, path-dependent GDS via 修改)**: U#0 (verbatim)
> "我想做design rule 和 gds的联合优化 我理解我是需要操作gds 文件 然后在里面修改过孔的尺寸和位置 你知道我要怎么做吗"

用户要批量修改私有 GDS (`/rundata/lacaa/.../CH231_HDT_Bitcell_FS_WiPin.gds`) 的 via 尺寸/位置。助手用 pyAether 写了 `gds_sweep_export.py`（绕中心缩放+平移重建 V0D/V0G 矩形）。path-dependent：私有 GDS 不可入沙盒 + pyAether sandbox 连接 refused (USER#44) + correctness 需真跑 pyAether 验证几何变换 → 按排除标准(2)「写不出能区分真假交付的 check()」剔除。

**判定**: 双意图拆分 — ①可造+②不可造 ⇒ 固化①=keep（per A r657 taxon，①是用户真实子意图，②本就 path-dependent 剔除）。非 downgraded。

## 助手工作流（trace 实证）

1. U#0 produce GDS via 修改 → 助手 search_apis (dbGdsIn/dbGdsOut/dbShapeQueryEx) + 写 parse_gds.py (GDS 二进制 parser) + via_optim_gds.py + gds_sweep_export.py
2. U#53 "tell me in chinese" + U#54 paste parse_gds.py WARN output → 调试 GDS parser (bad record at offset 5884)
3. U#63 "gds 是二进制吗" + U#64 "gds 是二进制 是不是不好解析" → Q&A (concept)
4. U#65 "我要批量的导出GDS" → 写 gds_sweep_export.py (批量 GDS 变体导出)
5. U#88 "V0D/V0G/V0R/V1/Vxa/Vx/Vxb represent which layer to which layer" → grep LVS deck (grep_via.sh / grep_via2.sh / grep_via3.sh) 找 LAYER name defs + tran.map，产出 via 层映射表

## Reframe 方案（r694 build）

**case_id**: ViaLayerMapExtract-001 (physical_verify, L1-boundary)
**子型**: `lvs-deck-via-layer-map-extract`（C 域 mock-behavioral reframe 家族，knowledge-retrieval + structured-extraction 子向，承 r692 manual-retrieval+error-diagnose 同 sub-family 但 distinct：r692 diagnose error / 本例 extract via mapping）

**asset A** = lvs_deck_A.svrf（35H 1P18M 流程 LVS deck 节选，含 LAYER name defs + 注释 + LAYER MAP + tran.map，V0D/V0G/V0R/V1/Vxa/Vx/Vxb 7 via + AA/M0/GT/M1/M2 等金属层）+ prompt.md + task_brief.md
**hidden B** = lvs_deck_B.svrf（全异流程 28H 1P12M，全异 via 名 VA0/VA1/VB0/VC0/VD0 + 全异层名，反硬编）+ prompt_B.md
**hidden B2** = lvs_deck_B2.svrf（退化：0 VIA 定义，0 层映射）

**candidate**: via_layer_map.py（纯 stdlib）— 解析 LVS deck 节选，提取 via→layer 映射，输出 JSON：
```json
{
  "summary": {"total_vias": N, "mapped_vias": M, "unmapped_vias": K},
  "via_map": [
    {"via_name": "V0D", "from_layer": "AA", "to_layer": "M0", "purpose": "source/drain contact hole", "evidence_lines": ["L736:LAYER V0D_drawing 10060 //..."], "confidence": "high"},
    ...
  ]
}
```

**check() 16 条件 a-p**（草案）：
- (a) zip 含 via_layer_map.py + py_compile
- (b) B 运行 exit 0
- (c) stdout 合法 JSON 含 summary + via_map
- (d) summary.total_vias == B 的 via 数（非 A 硬编）
- (e) summary.mapped_vias == B 实际映射数
- (f) 每条 via_map 含 via_name/from_layer/to_layer/purpose/evidence_lines/confidence
- (g) B 的 via_name 集合 == B deck 实际 VIA 名（非 A 硬编 V0D/V0G/...）
- (h) B 至少一条 via 的 from_layer/to_layer 正确（从 B deck 注释解析）
- (i) B evidence_lines 非空且引用 B deck 行（非 A deck 行）
- (j) B purpose 从 B deck 注释提取（非硬编 A 的 "source/drain contact"）
- (k) confidence 字段为 high/medium/low 之一
- (l) B2 退化（0 VIA）summary.total_vias==0 且 via_map 空
- (m) 同一 B 输入两次运行 stdout 字节一致（确定性）
- (n) B via_map 按 via_name 排序（确定性顺序）
- (o) B via_map 不含任何 A 特有 via 名（V0D/V0G/V0R/V1/Vxa/Vx/Vxb）
- (p) B via_map 不含任何 A 特有层名（AA/M0/GT 等）

**negatives** (4): empty_shell / only_print_A (硬编 A via 名) / no_core_logic (全 unmapped) / always_pass_stub — 全 FAIL distinct

## C 域 reframe 家族定位（补 discuss r693）

C 域 mock-behavioral reframe 2 sub-family：
- (a) source-to-source transformation 4-向（r682 classify / r685 validate / r687 generate / r688 translate / r690 diagnose）— fixture=源码，candidate=fixture→target
- (b) knowledge-retrieval + structured-extraction/diagnose 2 向（r692 manual-retrieval+error-diagnose / r694 本例 deck-retrieval+via-map-extract）— fixture=知识库/deck，candidate=retrieval+extraction

本例属 (b) sub-family，与 r692 distinct：r692 diagnose error（输入 error.txt），本例 extract via mapping（输入 deck 节选，无 error）。

## DEBT

- r694 build ViaLayerMapExtract-001（本 deepread 已完成，build deferred r694）
- jatet 在 B ledger parked — r694 需用 next 命令选 fresh candidate（jatet 无法 claim），或从 267 truly-fresh C-keyword candidates 选其他 viable produce-task
