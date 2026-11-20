# 95hv8 deepread — mea-cross-section 技能分析与算法复刻

- **session**: `1792494760058_95hv8` · user `jxwang` · host `hfeg0pkn005` (10.129.2.14) · mc=30
- **domain profile**: pyaether:54; aether:47; waveview:6; dbshape:6; rtl:5; netlist:3; .lef:2 → **layout_aether**
- **nmsgs**: 85 (4 real user_input turns)
- **真实意图**: 分析 `/home/jxwang/Desktop/skills/mea-cross-section` 技能 → 注册并跑一次 → 落盘
- **D 旧判**: parked 2026-11-05 "peek_D270 unfit (Q&A/doc/root-cause/mid-conv/skill-scaffold/NOFILE/boilerplate)" —— 按 2026-11-15 reaudit，skill-scaffold/flow-driving 合法，且本 session 是 C 域 layout_aether（D 误判 shard + 类别）， revival。

## 用户轮（逐字）

- U#0 `<user_input mode="act">`：`你现在能调用skill吗`
- U#2 `<user_input mode="act">`：`/home/jxwang/Desktop/skills/mea-cross-section分析这个skill如何使用`
- U#10 `<user_input mode="act">`：`直接注册调用，跑一次`
- U#33 `<user_input mode="act">`：`落盘`

## 助手 gold 链

1. `list_allowed_files` `/home/jxwang/Desktop/skills/mea-cross-section` → 见 `SKILL.md` + `references/CODE.md`
2. `read_files` SKILL.md + CODE.md（含 cross_section / cross_section_y 算法 + measure_*_at_X/Y 模板 + setup_measure_functions）
3. `skills` 调 `mea-cross-section` → **not found**（未注册到服务端索引）
4. `skills` 调 `skill-creator` 注册 → 服务端不允许临时注册
5. `SandBox_MCP_Server__run_code` pyAether `aeGetCurDesign()` → **Connection refused** (10.129.8.224:21513，沙箱未启动)
6. 决策：pyAether 不可用 → 用纯 Python 复刻 cross_section 算法 + 模拟多边形跑一次
7. `editor` 建 `/home/jxwang/Desktop/skills/mea-cross-section/demo_validate.py`（cross_section / cross_section_y / measure_x / measure_y / dump / main，含 H1-H3 横条 + V1-V3 竖条 mock SHAPES）
8. `run_approved_command` python-runner 跑 demo_validate.py → exit0，输出 4 个演示（m4_y@150 → 3 lines w1；m4_x@-50 → 3 lines w1；m4_x@-50 y>=200 → 2 lines；m4_x@-50 y∈[150,250] → 1 line）
9. 优化 mock 数据（H/V 坐标互不干扰）+ 修正演示坐标
10. `落盘`：demo_validate.py 已写入磁盘（U#21 editor 成功）

## 核心算法（来自 CODE.md）

- `cross_section(pts, x)`：竖直线 X=x 与多边形求交 → 半开区间 `(x1<=x<x2)|(x2<=x<x1)`，跳过 x1==x2 边；ys 排序后两两配对成 (center_y, width, y_lo, y_hi) band
- `cross_section_y(pts, y)`：水平线 Y=y，对称
- measure 主流程：bbox 过滤 → 逐 shape 求 band → 按 lo 排序合并重叠 band → 窗口过滤（band 中心 ∈ [lo,hi]）→ 排序 → Total lines + Sum
- 输出格式：`Layout/Layer/Direction/Coordinate` 头 + `Line[i] <axis>=<start> width=<w> (<axis>: <lo> ~ <hi>)` + `Total lines: N` + `Sum: %.4f`

## gold 最终产物

`/home/jxwang/Desktop/skills/mea-cross-section/demo_validate.py`（164 行，纯 stdlib，含 mock SHAPES + measure_x/measure_y + dump + main 4 演示）—— A#read_files 校验通过。

## reframe 设计（档 B）

A 档 gold = live pyAether `aeGetCurDesign()` + 真实 Aether cellview（依赖 live Aether 库不可复现，无 ≥8 硬断言牙）→ reframe 为**离线 fixture 驱动**的 parametric 截面测量器：
- 候选交付 `mea_cross_section.py`（单文件 stdlib），实现 `measure(shapes, direction, coordinate, lo, hi)` + CLI `<fixture.json> <direction> <coordinate> [--lo L] [--hi H] [-o out]`
- A fixture = trace 真实 mock shapes（H1-H3/V1-V3, M4, LAYOUT_1）入 SUT 沙箱作数据形状示例
- B fixture = 隐藏（不同 cell/layer/形状，含重叠 band 测合并 + 不跨越 shape 测 bbox 过滤 + 负坐标测 edge case + 窗口过滤）
- check.py 含**独立参考实现**计算 B 期望值，subprocess 跑候选 CLI + import 调 measure()，比对 band/width/sum；反硬编 A guard；3-seed 确定性

## 意图审计

**keep** —— jxwang 真实意图（分析技能 + 跑一次 + 落盘）完全保留。reframe 是 grounding：把「live Aether cellview 上测截面」沉淀为「fixture 驱动 + 算法等价校验」，单文件化 + 离线化，未引入用户未要求的内容。所有规则来自 SKILL.md/CODE.md（用户指定分析的技能）。2026-11-15 reaudit 后 skill-scaffold/flow-driving/script-completion 合法。
