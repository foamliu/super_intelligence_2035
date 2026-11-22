# Deepread: 1795072827714_iqfr1 — stipple dot pattern generator (GDS viewer Fill panel)

- **session**: `1795072827714_iqfr1` · user `xxchen` · host `hfeg0plg06` (10.129.32.13 reachable via .75) · mc=358 · agent `lead`
- **fetched**: 2026-11-22 via eda_flow `ssh 172.16.8.13 'cat /home/xxchen/.cline/data/sessions/1795072827714_iqfr1/1795072827714_iqfr1.messages.json'` → 1.5MB / 294 msgs
- **kw profile**: drc:769 ; .gds:192 ; techfile:125 ; gdsii:23 ; cadence:18 ; binary:16 ; aether:16 ; pdk:10 ; .lef:9 ; pyaether:1 → C-domain (layout_aether / physical_verify borderline; user's own GDS viewer for DRC pattern work)

## Real task (user intent)

xxchen 维护一个自研 PyQt5 GDS viewer (`/home/xxchen/workspace/DRC_pattern_tool/0.6/device_rule1/temp_qt_gdsView/`),用于 DRC pattern 调试。本 session 聚焦 **Fill 画板的三项增强**(U#162 act 模式):

1. 新增由圆点组成、密度不同的稀疏点阵 pattern (vs. 仅有 slash/solid/dots 三种粗 pattern)
2. Fill 增加闪烁开关(1s 一次灰亮闪动)
3. 斜线条 pattern 用更细线条 + 更密集密度

随后**两次用户纠正**(关键意图):

- **U#199**: "你的 dots dense 为什么都连在一起了,需要的是独立的小圆点,圆点和其他圆点间保持一个稀疏的距离。不要连成一条线或者一片。"
- **U#227**: "你这个 dots dense pattern 我看到的实际效果是很多个 + 有的还连在了一块,并不是圆点形状。是设置的图标太大了吗,能否用更小的分辨率?"

## Assistant 工具链 / 关键产物

- `gds_scene.py` — stipple pattern 生成 + `StipplePolygonItem` paint
- `ui_mainwindow.py` — Fill palette (16 色 + 8 pattern 按钮 + blink checkbox)
- `test_features.py` — 特征测试(compile / pattern count / dot isolation / blink toggle)
- `_dev_probe/_probe_dots.py` + `run_probe_text.sh` — ASCII dump 验证 dot 形状
- 调试循环: editor 改 `_p_dots` → compile_check → run_features.sh → run_probe_text.sh → 用户视觉确认 → 再纠正

## 根因 + 修复(关键算法)

**根因**(U#227 assistant 总结):
1. 16×16 binary tile 里 "圆"(radius=1)只能画成四邻域 "+" 形,天然不是圆
2. 每 bit 一律按 `_STIPPLE_CELL = 8 device-px` 渲染,导致单个 dot 占 8×8 像素块,又大又粗
3. dots_dense 用 `_p_dots(3, 1)` —— 半径 1 的 "+" 点只隔 3px 摆放,边缘相接 → 合并成连续线段/色块

**修复**(分两步):
- **Step 1 (U#199 fix)**: `_p_dots` 增加 isolation guard (spacing > dot diameter),三种密度改为 5/7/9 px 间距
- **Step 2 (U#227 fix,真圆点)**: 引入 per-pattern **cell** 参数(打破固定 8px/格),`_p_dots(step, radius, n)` 在更大 tile (e.g. 24×24) 内画半径 2 的真圆盘,通过 `builtin_cell(style)` 把 cell 传到 `StipplePolygonItem.paint` 的 `QTransform` 缩放;`_p_dots` 用 **torus-wrapped 距离**(`(dx+cell/2)%cell - cell/2`)生成,确保边缘 dot 完整圆且 tile 无缝拼接;`build_swatch` 也按真实 cell 渲染图标

**验证**: ASCII dump `=== dots_dense (bits=208) ===` 显示独立小圆点 + 清晰间隙;feature test 用 torus-wrap connected-components 检查 dot 独立性;compile + integration + mouse 三套 regression 全绿。

## 合成方向(reframe 档 B)

**子型**: `stipple_dot_pattern_gen` — 给定 density/cell/radius 参数,生成 2D binary tile + metadata,断言"真圆点 + 独立 + 多密度 + 无缝 tile"。

**agent 任务**: 写 `stipple_dot_pattern_gen.py`(纯标准库)读 pattern manifest JSON,对每个 pattern spec {name, cell, radius, step, target_count} 生成 binary tile (list-of-lists of 0/1) + 计算统计 (dot_components_count, mean_dot_area, min_gap, roundness_ratio, tile_wraps_seamlessly),emit JSON {patterns:[{name, cell, radius, step, tile, stats}], summary}。

**visible A**: 3 pattern (dots_dense cell=24 r=2 step=8 / dots_mid cell=20 r=2 step=10 / dots_sparse cell=16 r=1 step=7)
**hidden B** (check.py inline): 4 pattern,不同 cell/radius/step/cell×cell 规模,不同 target_count,要求 candidate 在 B 上跑出独立圆点 + 无缝 tile。

**check.py ≥8 独立断言**(逐条可 FAIL,不文本相似):
1. py_compile 通过
2. no-arg 调用 exit 0 + JSON 输出 + 顶层键齐全 (`patterns`, `summary`)
3. 反硬编码: B 的 pattern name 全部出现,A name 零泄漏
4. 每 pattern tile 是 list-of-lists,维度 = cell×cell,值 ∈ {0,1}
5. 每 pattern dot_components_count (4-conn torus-wrap) == 期望 count(target_count)
6. 每 pattern mean_dot_area 在期望范围(圆面积 πr² ± 容差)
7. 每 pattern min_gap ≥ 1 (独立 —— 任意两 dot 间至少 1 个 0 bit)
8. roundness: 每 dot component 的 filled_area / bbox_area ≥ 0.6 (排除 "+" 形)
9. tile 无缝: 把 tile 拼 3×3,跨边界 connected-components 数 == 9 × 单 tile count (边 dot 不被裁切)
10. 多密度单调: dots_dense count > dots_mid count > dots_sparse count
11. 3-seed 确定性: PYTHONHASHSEED=1/2/3 字节级一致

**3 neg** (naive_stub / always_solid / hardcode_envA) 各卡不同 tooth FAIL。
**§4.9 三假**: (a) 空壳 (b) 只 print 期望 JSON (c) 删 generate 核心 → 全 FAIL。
**test_rationale**: 11 条断言清单(对上 check.py 11 个独立条件)。

## 跨 shard 串台检查

- 4-shard ledger: iqfr1 仅 C claimed (本轮 `trace_ledger.py --shard C claim` 直接收)
- 4-shard jsonl: 无 iqfr1
- 同 domain 已落库 case: GtJumperPathAnalyzer(layout 连通图) / StdcellLibFifoSuitClassifier(stdcell 分类) / LvsDeckPairDiff(SVRF diff) / CalibreDrcRunsetConfigValidator(runset) / AetherLayerPurposeExplainer(layer 用途) / SpacePatternPlanner(DRC space pattern) —— 全正交
- **子型 `stipple_dot_pattern_gen` 首例**(Qt GDS viewer Fill panel stipple 生成器,与 SpacePatternPlanner 的 DRC space-check 是不同对象:前者是 GDS 渲染 pattern 生成,后者是 DRC rule space 检查)

## 状态

- **DEBT**: deepread 完成,ready-synth。下轮直接合成(参考本笔记 §合成方向),ETA 1 轮。
- 本轮 0-case(冷启动 session,40-min 预算不足以走完 synth + 自验 + pi + commit)。
