# 深读笔记 — sid 1791425782404_rn6pm (yohannw, hfeg0pkn003, mc=322)

- **trace 源**：`/home/yohannw/.cline/data/sessions/1791425782404_rn6pm/1791425782404_rn6pm.messages.json`（546 msgs / 299 UI / 712KB）
- **session meta**：agent-policy-engine enforcing；readableRoots 2 个；run_commands 被禁用（须用 run_approved_command，但 owner 校验失败 uid 10741 vs 200329，故全程用 list_allowed_files + read_files + search_codebase）
- **工作根目录**：`/home/yohannw/workdir_26Q4`
- **域**：layout_virtuoso（CXMT SKILL 菜单 trigger 解析）

## 用户轮（提出需求/目标，逐字原文）

- **UI#0**：「`/apps/imctf/cad/init/settings_cdns/skill/`，这个是virtuoso脚本工具的根目录，我需要你在其中找到中心路由文件（即文件名与工具名的映射关系）」— 元任务（找中心路由）
- **UI#1(37)**：「当前会话你的工作根目录是哪里」— 元信息（非新需求）
- **UI#2(39)**：「`/apps/imctf/cad/init/settings_aether/python_ae`，这个是Aether的脚本工具目录，捕捉相关信息，以应对我后续的提问」— 元任务（Aether 目录预扫描）
- **UI#3(65)**：「我需要你定位到Virtuoso的三个工具，1、CXMT -> Fill Optimizer -> Auto Via Tool；2、CXMT -> Fill Optimizer -> Power Fill；3、CXMT -> Power Analysis -> Rscalc Flow -> Run Rscalc；注意，路径上的节点名称可能不全，因为UI显示过长的工具名称会被隐藏」— **A 档 seed 候选（提出目标未给根因/修复）**
- UI#4(103)：「`/home/yohannw/workdir_26Q4/1005_zl_owner` 目录下，读取三文件、拆解源码并拟制分析报告…IMCutGenPowerFill.il IMCutRscalcFlow.il IMCleAutoVia.il」— 后续需求（源码解读报告），不是同一目标
- UI#5(127)/UI#6(86)/UI#7(98)/UI#8(154)/UI#9(180)…均为后续代码解读/文档生成任务
- **判定**：UI#3 是提出需求+目标，未给根因/未给修复 → A 档 seed 合规 ✓（其余 UI 或为元信息，或为后续派生任务，不取作 A 档任务说明）

## agent 工具链（UI#3 排查段，msg 65–102）

agent 用 41 次 list_allowed_files（逐目录下钻）+ 11 次 read_files（分段读 trigger 文件）+ 2 次 search_codebase（确认 handler 函数定义）定位三个工具：

1. **中心路由文件**：`/apps/imctf/cad/init/settings_cdns/skill/hi/IMChiUserPullDownMenuPostInstallTrigger.il`（CXMT V3 layout 下拉菜单 trigger，2700+ 行）。读 2188–2410 行定位 layout 版 CXMT 菜单。
2. **Fill Optimizer 段**（`innoPinusMenu`，title "Fill Optimizer"，2270–2315 行）：
   - `innoMenuItem10` itemText "Auto Via Tool..." → callback `…IMCleAutoViaGUI()` → handler `IMCleAutoViaGUI` → 文件 `IMCleAutoVia.il`（在 `special/le/`）
   - `innoCXSHMenuItem38` itemText "Power Fill..." → `…IMCutGenPowerFill()` → `IMCutGenPowerFill.il`（在 `special/ut/`）
3. **Power Analysis 段**：`cxmtPowerIntegrity_Menu`（title "Power Analysis"）含 `innoRscalcMenuItem` slider（itemText "Rscalc Flow"，subMenu `cxmtRscalcMenu`），下挂：
   - `innoCXSHMenuItem39_0` itemText "Run Rscalc..." → `…IMCutRscalcFlow()` → `IMCutRscalcFlow.il`
   - `innoCXSHMenuItem39_1` itemText "Run Rscalc View..." → `…inno_rsview()` → `inno_rsview.il`
4. search_codebase 确认 `IMCleAutoViaGUI`（`IMCleAutoVia.il` 行 76）、`IMCutGenPowerFill`（`IMCutGenPowerFill.il` 行 47）、`IMCutRscalcFlow`（`IMCutRscalcFlow.il` 行 98）三处函数定义均存在。
5. 顶层 CXMT 菜单 = `TrLayoutPulldownMenu`（title "CXMT"，行 2687–2710），通过 `TrUserPostInstallTriggerLay` 挂到 `maskLayout`/`maskLayoutXL`/`maskLayoutGXL`（行 2789–2791）。

## gold 不可复现原因

gold 依赖私有 `/apps/imctf/cad/init/settings_cdns/skill/` skill 树（agent-policy-engine readableRoots 限 e0031982 用户无权访问），且 trigger 文件 2700+ 行含完整菜单结构，沙盒无法复现 → **A 档 disqualified → B 档 synthesized L1-boundary**。

## 合成锚点

合成 `skill_menu_routemap.py`（Python3 标准库 re/json/os/sys，纯离线）：解析 `hiCreateMenuItem`/`hiCreatePulldownMenu`/`hiCreateSliderMenuItem` 三类块（平衡括号扫描 + SKILL 字符串转义感知）→ items/pulldowns/sliders 三表 → 解析 `;; @query [...]` 查询 → 从顶层菜单（`;; @top_menu VAR` 或「未被 slider ?subMenu 引用的 pulldown」）逐段下降，每步匹配 itemText（去 `...`），命中 slider 下降进 subMenu，命中 item 必须是终点返回 handler/file/item_var → handler→.il 推断（GUI 后缀剥离 / IMCle·IMCut·CXMTle·cxmt_·inno_ 前缀加 .il / 否则 null）→ 审计 duplicate_labels/dangling_submenus/empty_callbacks/non_inferable_handlers → JSON 输出 + verdict OK/HAS_ISSUES。

## 与既有 shard C case 的区别

- AutoCellClassify = case-sensitive 命名分类器
- AutoCellFlowValidate = AutoCell TCL flow 8-文件依赖校验
- RNodeCovAudit = RTEXT/RNODE 探针覆盖审计
- PFMergeAudit = layout figure merge 完整性
- MVVarNamingAudit = DRC deck 多值变量命名
- **本案 = SKILL pull-down menu trigger 路由解析 + handler→.il 推断 + 结构审计**，主题/断言独立

## A 输入 / hidden B / B2 / B3

- A = route_menu_A.il（CXMT-A planar clean，7 items/4 pulldowns/3 sliders，3 queries 全解析，verdict OK）
- B = route_menu_B.il（CXMT-B finfet，9 items/5 pulldowns/5 sliders，3 queries 全解析；植入重复 "Power Fill" label、danglingSliderB→noSuchMenuB、空 callback innoMenuItemFillB3、不可推断 handler unknownHelperFoo；verdict HAS_ISSUES）
- B2 = route_menu_B2.il（CXMT-B2，仅 query1 解析，resolved_count=1；杀硬编码 B 解析数）
- B3 = route_menu_B3.il（CXMT-B3，3 queries 全解析，handlers 与 B 不同，无任何 audit issue，verdict OK；杀 always-FAIL/always-issues）

## 14 条断言（k=14=k_check≥8，GATE PASS）

a(zip+py_compile+A 全解析+verdict OK) / b(B 顶层键≥6) / c(B q1 handler/file/item_var) / d(B q2 首次 handler + 重复 label Power Fill count=2 occs) / e(B q3 深度4 handler/file) / f(B dangling noSuchMenuB) / g(B empty_cb innoMenuItemFillB3) / h(B non_inf unknownHelperFoo + file=null/inferable=False) / i(B total_items=9 + 独立重计数) / j(B total_pulldowns=5 + 独立重计数) / k(B total_sliders=5 + 独立重计数) / l(B2 resolved_count=1 守卫) / m(B3 handlers 不同 + 无 issue + verdict OK 守卫) / n(B 跑 3 次 md5 一致)

## 自验

- ref PASS 14/14 ✓
- 4 neg（empty→a / hardcode_B→l / core_deleted→c / hardcode_handler→c）全 FAIL ✓
- NEG_RC=0 ✓
- §4.9 (a)空壳(b)只 print(c)删核心 三假提交全 FAIL ✓
- test==disk check.py roundtrip OK
- layout_virtuoso 域 12→13
