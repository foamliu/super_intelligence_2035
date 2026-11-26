# daqqm deepread — Aether Layout Editor GUI panel-delete Q&A (C-domain, D-REJECT)

**session**: 1794223587428_daqqm · **user**: zhukais · **host**: hfeg0plg54 (10.129.35.73 / 10.129.8.237) · **mc**: 60
**fetched**: r897 via eda_flow ssh .75→10.129.35.73 scp 594KB messages.json (21 msgs, 11 user turns)
**verdict**: **C-domain (layout_aether), D-REJECT confirmed** — r578 peek REJECT 正确，r896 plan 误标 D-parked

## trace 摘要

- **U[0] (唯一真实需求轮)**: `<user_input mode="act">查看左右panel无法删除到原因</user_input>` — Aether Layout Editor GUI 左右 panel 无法删除的排障 Q&A。
- **assistant 链路**: `skills` (aether-tool-qa) → `read_files` ×9 读 Aether 文档:
  - `aether_tool_qa.md` (Aether & ARGUS 交流群问答记录, 含 guard ring / workspace / 任务栏 等 GUI Q&A)
  - `part_V_Layout_Editor.md` (Aether Reference Manual 2025.09.sp1.hf7, Layout Editor Window / Path / Rotate Right 等)
- **U[2]-U[20]**: 全为 `tool_result`（assistant read_files 返回），无新用户需求轮。
- **真实交付**: Aether Layout Editor panel 删除方法的文档检索答案（doc-search Q&A）。

## domain 判定

- **真实工作 = Aether Layout Editor GUI 排障** → `layout_aether` = **shard C** (physical_verify/layout_virtuoso/layout_aether/pg_layout)。
- **keyword 高 mc 根因**: netlist/schematic/analog 命中来自 assistant 读 `aether_tool_qa.md`（含 guard ring / netlist 等词）+ `part_V_Layout_Editor.md`（Layout Editor 文档），非用户真实做 netlist/schematic EDA 工作。
- **D-domain fit**: ✗ — 用户从未打开 design / 跑 pyAether/SKILL / 产出 netlist 或 schematic。这是 GUI doc-search Q&A，属 C 域 layout_aether。
- **r578 peek REJECT**: 正确（"debug Q&A panel-delete reason" 实指 layout_aether GUI panel）。
- **r896 plan 误判**: r896 MEMORY 称 "daqqm ... D-parked r578 ... revival per Q&A-造-able" 把 daqqm 当 D 候选 — 误读 ledger domain=layout_aether 为 D-parked。本轮 deepread 订正。

## 处置

`mark --status parked --force` + note 记录 C-domain REJECT 确认。**不造**（非 D 域，违「🚫 不碰别的 shard」+ D shard 只做 analog_context/schematic_netlist/waveform）。

## r845 revival (2026-11-20) — 2026-11-15 reaudit 后 doc-search Q&A 合法化

按 2026-11-15 用户令「旧判为 weak / analysis-only / doc-search / Q&A 的候选全部恢复为可造」，daqqm 的 layout_aether doc-search Q&A 意图现合法。本轮 revival via 档 B reframe 落库 `EDA-Eval-DesignFlow-AetherPanelDeleteDiag-001`（layout_aether, L1, 档 B, k_check=14, 子型 aether-layout-panel-delete-docsearch-diagnosis）。**C 域 layout_aether GUI doc-search 检索+诊断 reframe 子型首例**（与既有 layout_aether case 正交：AetherAutorouteTraceRuleDiag=autoroute rule / AetherPinErrorQa=pin error / AetherSePermAudit=SE perm / AetherLauncherSkill=launcher / AetherEnvBootstrap=env / AetherApiSummary=api summary — 本案=panel/window GUI 排障 doc-search）。

- **档 B reframe**：A 档 gold=助手对真实 aether_tool_qa.md(5188行)+part_V_Layout_Editor.md(8577行) free-text doc-search 诊断（prose，无 ≥8 独立硬断言牙）→ reframe 为离线纯 stdlib 检索器 `aether_panel_diag.py`，CLI `<corpus_dir> <query> [-o out.json]`，解析 `## 提问`/`**回复：**` 问答块 + `### N.N`/`Menu:`/`BindKey:` 手册章节 → 检索 panel/window 管理条目 + 抽取方法/快捷键/菜单路径 → 输出结构化 JSON 报告。
- **visible A** = aether_tool_qa_A.md + part_V_Layout_Editor_A.md（内容 faithful 摘自真实文档的 panel/window/workspace Q&A 与 LSW/Window 章节）+ prompt.txt（用户原话逐字「查看左右panel无法删除到原因」+ reframe 接口）+ task_brief.md。
- **hidden B** = aether_tool_qa_B.md + part_V_Layout_Editor_B.md（合成，同结构，不同问答条目/不同 panel 方法/不同行号/不同手册章节；B distinctive methods: Ctrl+Shift+H / Window -> Close Side Panel / Pin）。
- **判分 14 条独立条件 a-n**：zip合法+stdlib-only+B运行JSON+6顶层键+retrieved_qa四字段+line_range行界+panel关键词相关性+Ctrl+Shift+H方法+CloseSidePanel/Pin方法+corpus_files无幻觉+手册章节四字段+反硬编码A(A含add To panel/ENTER，B含Ctrl+Shift+H)+missing-path非零退出+3-seed确定性。
- **自验**：golden 14/14 PASS；4 negatives (empty/print_expected/core_deleted/hardcode_a) all FAIL DISTINCT (a,b,c,d,e,f / l,m / e,f,g,h,i,k / f,h,i,j,l)；§4.9 三假全 FAIL；roundtrip test==disk check.py sha16 cbeed5cc0640d722 ✓。
- **infra**：eda_flow open_session(task_id=shardC-r845) OK；ssh e0031982@10.129.35.73 + key OK；scp 594KB messages.json + 真实参考文档(127KB+888KB) OK。pyAether .75:8651/8652/8654 Connection refused（非 L1 必需）。
- **台账**：C ledger mark case (force, 跨 shard D 台账 parked 已 r897 订正 C-domain)；build_jsonl.py --shard C 重建 C.jsonl 525→528（含 2 既有 gap + 本案）。
