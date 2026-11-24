# 8e4wm — jmgu @ hfeg0plg79 — M3 DRC QA pattern GDS generation

- session: `1795052208789_8e4wm.messages.json` (256 msgs, 1.37 MB)
- user: jmgu ; host: hfeg0plg79 ; match_count: 78 ; domain: physical_verify
- ledger: claimed r1045 (2026-11-24 08:20)
- cwd of trace: `/rundata/lacaa/TV1_DBC/ALS_PDK/drc/jmgu/aiqa/`

## 用户真实意图
jmgu 要为 ALS PDK DRM 里 M3 (drawingA "Mxa") 的二类规则（SIZING / 派生区域）做 QA pattern deck：
complete 23 条二类规则 → 用 qa-pattern-engine skill 生成好/坏 pattern GDS + measure 断言，跑 engine 校验 0 fail，再 final_verify。

## Assistant 工具链 / 关键产物
1. dump DRM records (drc:940, pdk:356, techfile:263 条)
2. read Rev11/Rev13 QA decks，解码 LAYER MAP：
   - APR_Boundary=301,540 ; M4=95,353 ; M5=103,353 ; M3_drawingA_xai=93,482
3. 写 11 个 pattern-generation 脚本（boundary_empty_width / island_empty_area /
   empty_area_via / via_array_region / via_edge_space / empty_high_density /
   small_group_space / identical_mark / p40_cap / boundary_enclosure /
   thin_stack / three_metal_density / corner_projected_count）
4. 注册到 `_index.json`，build `calls_v9` (174 calls)
5. run engine → 5067 checks, 0 failed ; final_verify PASS (348 cells, 4601 polygons)
- measure 类型：bbox_dim / pair_gap / edge_gap / area
- engine config: `engine_config.json` (layers, rules)

## 选料子任务（r1045 case）
取 `boundary_empty_width.py` 家族（W.19.1/W.19.2/W.20.1 empty-width 规则，
bbox_dim measure on axis）→ 合成为 **offline Python deliverable**：
`gen_empty_width_patterns.py <spec.json> <out_manifest.json>`
- 输入 spec: rule_id / layer / measure_type=bbox_dim / axis / min_width /
  violation_delta / n_cells / cell_basename / origin_step
- 输出 manifest: cells[] 每个 cell 2 variant (good/bad)，每 variant 含
  polygons (axis-aligned rect on target layer) + measures (bbox_dim value)
- 自洽：good.width >= min_width (pass) ; bad.width < min_width (fail) ;
  measure.value == bbox extent on axis (从 points 计算)

## 合成理由
- 纯 Python 几何计算，无需 GDS 渲染 / pyAether / EDA 沙盒 → 可完全离线判分
- 与 r1044 AetherStandaloneInstList 的 mock-pyAether 离线判分范式同族
- 与现有 C 域 pattern-gen case (CornerSpacePatternGen / DnwPatternGen /
  AntennaQaPatternReuse) 正交：本例聚焦 "empty-width 规则 + bbox_dim measure +
  good/bad variant pair" 这条 DRM QA 子型，trace 来源是真实 DRC QA deck 工程
- k>=8 易达，可加 B2 anti-hardcode + 3 stub + 确定性
