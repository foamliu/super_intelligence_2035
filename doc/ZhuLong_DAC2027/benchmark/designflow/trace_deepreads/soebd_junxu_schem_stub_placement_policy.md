# trace_deepread: 1788916632467_soebd (junxu / hfeg0pkn005, mc=400)

**session**: `/home/junxu/.cline/data/sessions/1788916632467_soebd/1788916632467_soebd.messages.json` (1.7MB, 307 msgs; opencode `lead` agent, model glm-5.2, provider cxmt-glm52)
**user/host**: junxu @ 10.129.2.14 (hfeg0pkn005)
**cwd**: `/home/junxu/.cline/skills/virtuoso-cli`
**status**: failed (exit 1, ran 2026-09-09 01:17 → 2026-09-10 05:06 ≈ 28h)
**domain**: layout_virtuoso (schematic auto-wiring policy + 摆放密度)

## real_task_summary（用户原话，仅掩码 key/token）
junxu `/brainstorming` 一份先前的 virtuoso-cli 原理图自动连线 session（`1788845188396_c4wsu`）：

> 我在 block-design 和 virtuoso-cli skill 中都明确说明了 connect_by_name 或者 stub
> 只在无法物理连线的时候才使用，但是这位 agent 从头到尾都在用 stub 连线，明明两个器件
> 很接近但还是在用 stub 桥接。另外 agent 摆放的器件有时候太密造成连线和器件的 symbol
> 有重叠，有时又放的太开，导致观感不佳。分析一下原因以及改进的方法。

即两个**可判分**子问题：(1) stub/connect_by_name 滥用——应当只在物理连线不可行时才用 stub；
(2) 摆放密度——过密(symbol 重叠) / 过开。

## agent 实际行为
- 工具：read_files(58) / run_commands(46) / editor(30) / search_codebase(5) / skills(2) / ask_question(3) / RAG search(5)。
- 深入 `virtuoso-cli/scripts/virtuoso_cli/api/schematic.py`（2854 行 pyAether SKILL 包装器）的 `wire_pin` 方法，调试 `to` / `to_inst` 两个分支的 SKILL `let` 作用域 bug：`to` 分支用 `tgt_x = b.let("tgt_x")`，`to_inst` 分支用 `tgt_x = tx`（Python 串重赋值，未 `b.let`），后续 `has_label` 的 `foreach`/`when` 深嵌套引用 `src_x` 时报 `*Error* eval: unbound variable src_x`。agent 反复试括号匹配 / let 作用域 / `evalstring` 理论，28h 未收敛，**failed**。
- 编辑落盘：`schematic.py`(wire_pin) × 多次 + `block-design/SKILL.md` + `py-reference-schematic.md`（policy 文档）。
- ask_question(3) 向用户索取 CXMT 环境的 `Generate Boundary` / `snap origin` SKILL 函数名（用户未答全）。

## trace 价值（case 抽取点）
session 本身 brainstorming + failed 调试，**但用户的真实需求含两个干净可判分的几何策略子问题**，可纯 Python 离线判定（沙盒无需 Virtuoso/SKILL）：
1. **stub 策略**：给定 instance 绝对坐标 + pin 坐标 + net 连接，按「manhattan ≤ D_max 且 route_rect 不被第三方 instance body 严格相交 → physical；否则 stub_required」逐条判定，并标 `overused = (used_stub ∧ physical)`。
2. **摆放密度**：bbox 严格相交 → overlap 对；最近邻边到边欧氏 gap > sparse_max → sparse。

## case 抽取（EDA-Eval-DesignFlow-SchemStubPlacementPolicy-001, layout_virtuoso）
抽取「stub 滥用策略判定 + 摆放密度违规检测」两个独立可判分子流，**不要求 SUT 真跑 Virtuoso/SKILL**。
- A = `scenario_a.json`（6 instance / 4 net，faithful：近距误用 stub 的 overuse 对、3-instance 密集重叠簇、1 个 far sparse instance；config D_max=3 / sparse_max=5）。
- 隐藏 B = `scenario_b.json`（J0..J5 / K0..K3，坐标与 config 全不同但同构：1 physical-overuse、2 far stub、1 blocked-within-distance stub；3-instance 重叠簇 + 1 far sparse；D_max=4 / sparse_max=6）。
- 交付 `stub_policy.py` + `placement_check.py` + `report_a.json`；check 在 B 上独立复算期望，k=12 断言（physical/stub 分类、overused、blocker 命名、manhattan 数值、overlap 对集合、sparse 最近邻+gap、clean、反硬编码 B≠A），3 negative（always-physical / hardcoded-A / empty-output）+ §4.9(a)(b)(c) 全 FAIL。

## 难度定位
L2（真跑候选模块在隐藏 B 上判定，独立复算逐字段比对，击败硬编码 A / always-physical / print-expected）；非 L1（非离线复刻 A 固定数值，B 主动换坐标+config+net 名）；非 L3（单工具静态几何判定，无需多工具链路 + 修复 + 回归，沙盒无 Virtuoso）。
