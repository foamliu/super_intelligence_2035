# Deepread: v97a4 — steveny / "获取当前design"

- **session**: `1794882398353_v97a4.messages.json`
- **user/host**: steveny / hfeg0pnd001 (10.129.2.14)
- **match_count**: 40 (pyaether:197; aether:60; virtuoso:34; dbcreatepath:19; cellview:17; dbcreaterect:15; waveview:10; cadence:8)
- **size**: 98KB / 31 msgs
- **domain 判定**: schematic_netlist (pyAether/Virtuoso 主导)
- **结论**: **parked — 不适合造可判定 case（stateful task 违反 intent 铁律）**

## 对话流

1. [0] user "hello" → greet
2. [2] user 触发 `eda_agent` skill（技能定义注入）→ assistant 主动验证 RAG 知识库健康度
   - search_apis(lang=pyAether) "highlight net in layout editor" → aeSeRemoveNetHighlight 0.676 ✅
   - search_apis(lang=skill) "create rectangle in layout" → dbCreateRect 0.711 ✅
   - get_api_details(dbCreateRect/dbCreatePath) 返回完整签名 ✅
   - search_apis(lang=tcl) "add spectrum" → sx_display_wave ✅
   - 发现部署副本 `~/.cline/skills/eda_agent/` 比源 `rules/skills/eda_agent/` 旧一代（drift）
3. [24] **user 真实意图**: "获取当前design"
   - assistant 查 aeGetCurDesign API 文档
   - run_code(pyAether): `ae.emyInitAether("-adv"); cv=ae.aeGetCurDesign()` → **Connection refused by sandbox [pyAether] at 172.16.8.106:58048**（pyAether 沙箱服务未起）
   - 回退 run_code(skill): `geGetEditCellView()` → 成功: `stdcells_ac/and2CSx2/schematic`
4. [30] assistant 报告: 当前 design = stdcells_ac/and2CSx2/schematic（Virtuoso 侧），并说明 pyAether 沙箱连不上是故障非用法问题

## 为什么不适合造 case

用户真实意图 = "查询 EDA 工具里当前打开的 design（lib/cell/view）"。这是 **stateful task**：
- 答案（lib/cell/view）取决于 check 时刻 EDA 沙箱里打开的是哪个 cellview，**不是附件文件里的固定数据**。
- `check(deliverable, workdir)` 在独立 workdir 跑，无法保证沙箱里打开了某个特定 design。
- hidden B 无法构造：B 需要一个"不同的当前 design"，但这需要控制 live EDA 状态，脆弱且不可复现。
- 强行改成"解析一个 mock sandbox 响应文件"违背 intent 铁律（任务形态=用户意图；用户要的是查 live design，不是解析文件）。
- 属 env-config / flow-driving 类真实意图，但该具体实例的 stateful 性质使其无法满足 §4（有牙判分 + 隐藏 B + 确定性）。

## 可复用片段（供后续 case 参考）
- pyAether 沙箱连接失败 → 回退 SKILL 的容错模式（可作为某 case 的一个断言维度，但非独立 case）
- `geGetEditCellView()` + `cv~>libName/cellName/viewName` 是 Virtuoso 取当前 cellview 的标准 API
- skill drift 检测（部署副本 vs 源）是 env-config 类意图的典型模式
