# Deepread: u03z0 + qikhb (xxchen@hfeg0pkn003, physical_verify/drcpv QA-pattern tool) · r1239

> 2026-11-26 r1239 审视 r1215 parked-rrpe6 note 留的 5 fresh leads 中剩余 2 条 (u03z0, qikhb)。
> 结论：u03z0 near-dup park；qikhb distinct-but-asset-too-large park。两轮均 0 case 交付。

## session 元信息
- u03z0: `1795583544010_u03z0` xxchen@hfeg0pkn003, mc=1795583544010(pool tag), 434 msgs, 1.15MB, AGENT=lead
- qikhb: `1795585155081_qikhb` xxchen@hfeg0pkn003, 906 msgs, 2.28MB, AGENT=lead

## u03z0 — near-dup park
- 主题：优化 QA pattern GUI「选择function页面」示意图准确性。5 个 user turn 覆盖 4 个 function：
  - HOLE_AREA：蓝色图形改斜线条纹（hole 更明显）
  - INSIDE_SURROUND_RING：NW 黄色透明条纹应在 DNW 上面
  - PRL_SPACE：蓝左长/黄右长，PRL 正对区域，黄标线挪中间标正对长度
  - METAL_TO_UNRELATED_VIA_SPACE：via 黄色在 metal 蓝色里，斜线+透明度，标右侧蓝边到左侧黄 via 边距离
- 编辑目标：`drcpv/gui/schematic/examples.py`（与 r1238 RectSizeSchematicFix-001 同文件同工具）
- 工具：editor×117 / run_approved_command×76 / read_files×40
- near-dup 判定：与 RectSizeSchematicFix-001（draw_rectangle_size）+ PrlSpaceQaFix-001（prl_space 缺陷修复，session xbcoz）属同一家族——「user 描述视觉修复 → agent 编辑 examples.py 的 draw_<func>」同模板。PRL_SPACE 已有 case；再做 METAL_TO_UNRELATED_VIA_SPACE/HOLE_AREA = 第 5 个同结构实例 = 饱和。pool 3245 余候选，优先找结构不同的题。
- ledger: parked (r1239)

## qikhb — distinct-but-asset-too-large park
- 两个 user task：
  - msg#0：补上剩下没有示意图的 function（用 skill）
  - msg#391：**重构** examples.py（1099 行/52KB/42 draw fn）→ 拆成 per-function 多文件包，目录结构 + 自动发现 + 拼接，支持多人同步更新
- msg#391 是与 draw-function-visualization 家族**结构不同**的真实意图（代码重构/架构任务），判分可验证：包结构 + 自动发现 + DRAW 输出等价 + 公开 API 保留 + 可扩展性。
- agent 实际产出（已落盘 hfeg0pkn003）：
  - `examples/__init__.py`(78L) 公开 API（DRAW/draw_example/RECT/ARROW/TEXT/prims + reload hook）
  - `examples/_prims.py`(180L) 原语逐字复制
  - `examples/_registry.py`(180L) 自动发现（按浏览组顺序收集 10 组 42 draw）
  - `examples/_common/` 共享辅助
  - per-group 模块（10 组）+ 修正 7 处 file-path loader
  - 验证：42 draw 集合一致，primitives 逐 draw 等价，仅组内顺序按浏览组重排
- **不可单轮 self-contained synth**：asset 需 52KB examples.py + _prims + function_group.py + renderer palette 依赖链；42 draw fn 太大无法做 hidden-B（需不同规模/取值的 B 防背题）。需 scope reduction（如提供缩减版 8-function examples.py）或多轮。
- ledger: claimed + parked (r1239)

## 下一轮 fresh lead 建议（非 xxchen/drcpv）
- e0031668@hfhds201 ukkn7 mc1627 (aether:1496/drc:1004/netlist:811) — 真实 C 域 physical_verify，fetchable on .75 本机（hfhds201）。但 mc>1000 大 session，需评估可分性。
- junxu virtuoso 系列（508od/sjzm0/1hkwu/sstk3）多 schematic，可能 D 域，需 domain 再判。
