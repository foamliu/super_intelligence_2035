# Deepread: 1794308420196_3hfbw (aether auto-routing Q&A + error diagnosis)

**Source**: eric9zhu @ hfeg0plg52 (10.129.35.68), mc=84, 44 msgs, 20 tool_use
**Keywords**: aether:1276;floorplan:303;schematic:77;lvs:57;analog:45;transistor:38;techfile:26;mixed-signal:16
**Domain**: layout_aether (C-shard)
**Date**: 2026-11-10 (session), r691 deepread

## User turns (2)

1. **U#0** (msg[0]): `aether可以实现模拟device的自动绕线嘛`
   - Intent: Q&A — "Can Aether do auto-routing for analog devices?"
   - 形态: doc-search Q&A (查 Aether Reference Manual 找自动布线能力)

2. **U#1** (msg[20]): `Error: Constraint group 'foundry' does not have valid trace rule. (Route All)`
   - Intent: error diagnosis — 用户执行 Route All 遇到 foundry constraint group 缺 trace rule 报错
   - 形态: debug-Q&A (查手册定位根因 + 给修复方案)

## Assistant work

- search_codebase × 8: 搜 "auto route / 自动绕线 / trace rule / constraint group foundry / Technology Manager"
- read_files × 8: 读 Aether Reference Manual:
  - `part_IV_Floorplan_Editor.md` (Floorplan Editor, auto-routing 功能入口)
  - `part_V_Layout_Editor.md` (Layout Editor, Autodesign mode, Route All/Route Selected)
  - `part_IX_Tools.md` (Technology Manager, Trace Rule 定义)
  - `part_XIV_Appendix.md` (附录, 约束组)
- skills × 1: `aether-tool-qa` (Aether 工具 Q&A skill)

## Assistant deliverable

### 回答 U#0 (auto-routing 能力)
- ✅ Aether 支持模拟 device 自动绕线
- 功能入口: Floorplan Editor (FPV) + Layout Editor
- 前置: 开启 Autodesign 模式 (Window -> Layout Window -> Autodesign)
- 步骤: Route All / Route Selected, 支持 digital + analog
- 约束: Wire Constraint Group (foundry/user), Trace Rule 定义层连通规则

### 回答 U#1 (error 诊断)
- 根因: `foundry` constraint group 缺少有效 Trace Rule 定义
- Trace Rule 定义位置: Technology Manager → Trace Rule (Chapter 97)
- 影响: Route All 需要约束组有有效 trace rule 才能执行布线
- 解决方案:
  1. 打开 Technology Manager
  2. 进入 Trace Rule 配置
  3. 为 `foundry` constraint group 添加有效 trace rule (定义层连通性)
  4. 重新执行 Route All

## Reframe 分析 (per 2026-11-15 新标准)

**旧标准判定**: Q&A + doc-search → weak, 不可造
**新标准判定**: Q&A + doc-search + error-diagnosis = 真实用户意图 → **可造**

### 拟造任务形态: doc-search + error-diagnosis produce-task

**输入 (A)**:
- Aether Reference Manual 节选 (Floorplan Editor / Layout Editor / Technology Manager / Trace Rule 相关章节)
- Error message: `Constraint group 'foundry' does not have valid trace rule. (Route All)`
- 用户问题原文: `aether可以实现模拟device的自动绕线嘛`

**交付物**: JSON 结构化诊断报告:
```json
{
  "auto_routing_supported": true/false,
  "auto_routing_entry_points": [...],
  "autodesign_mode_steps": [...],
  "error_cause": "...",
  "error_affected_component": "foundry constraint group",
  "trace_rule_location": "Technology Manager",
  "solution_steps": [...],
  "manual_references": [...]
}
```

**check() 8+ 条件**:
① auto_routing_supported == true
② auto_routing_entry_points 包含 Floorplan Editor + Layout Editor
③ autodesign_mode_steps 包含 Autodesign 开启步骤
④ error_cause 正确识别 foundry constraint group 缺 trace rule
⑤ error_affected_component == "foundry"
⑥ trace_rule_location == Technology Manager
⑦ solution_steps 包含添加 trace rule 步骤
⑧ manual_references 包含正确章节引用
⑨ JSON 结构合法
⑩ 隐藏 B: 不同 error message + 不同 constraint group → 验证非硬编码

**隐藏 B**: 换 error message (如 "Constraint group 'user' does not have valid trace rule") + 换 manual 节选 → 验证 SUT 真正理解而非硬编码

**负样本**:
- naive: 空 JSON / 全 false
- stub: 只 print 期望串
- 参考解删核心: 去掉 error_cause 字段

## 判定

**VIABLE for next round build** — strongest C-domain fresh candidate in r691 peek batch.
- 真实 trace ✓ (eric9zhu @ hfeg0plg52, session 1794308420196_3hfbw)
- C-domain ✓ (layout_aether: aether:1276, floorplan:303, lvs:57)
- 可写 toothed check() ✓ (8+ 结构化字段验证)
- 新标准合法 ✓ (Q&A + doc-search + error-diagnosis = 真实用户意图 per 2026-11-15)
- 退化提交可 FAIL ✓ (空壳/只 print/删核心 全 FAIL)

**Build deferred to r692** (r691 时间耗于选料 14 候选 peek + 13 park)
