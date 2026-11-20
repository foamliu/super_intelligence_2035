# 深读 trace 记录：82iou（AetherADV 原理图层次 descend · instance-name 逐级跳转）

> 原始 messages.json 2.76MB / 570 msgs / 291 user / 279 assistant / 119 editor / 89 run_approved_command / 48 read_files。
> 已 ssh cat 到 .75 workdir 解析后清理（不入库不入 git）。

## 一、Trace 溯源（不脱敏）
- session_file: `1791966358446_82iou.messages.json`（`10.129.2.11:/home/fxian/.cline/data/sessions/1791966358446_82iou/...`，2,758,399 字节）
- user: `fxian`，host: `hfeg0pkn002`（10.129.2.11）
- summary.tsv match_count: 606；tools: schematic 1709 / pyAether 1036 / dbGet 340 / cellview 161 / netlist 49 / hspice 2
- real_task_summary: 修改 `/home/fxian/python/cxmt_lookup_app.py`，给「查找表」GUI 加一个按钮——选中一条层级路径后，**在 AetherADV 里从当前顶层原理图逐级 descend 到目标 cell**，替代手工「拷路径→开 Probe Signal→Instance from Hierarchy」三步。

## 二、用户真实意图（27 条 user_text 提炼）
- U#1 goal：选路径 → 一键 descend 进目标 cell（替换手工三步）。
- U#5（核心算法描述，原话）：「我们会打开 WOWTOP schematic，然后下一步会找到此电路里 instance name=XIctop 的 cell（schematic）..一直迭代，找到 instance name 匹配的 cell，打开电路图，再找」。即 **从顶层 schematic 起，逐级按 instance name 匹配，打开匹配 instance 的 sub-cell schematic，直到路径末级**。
- U#10 / U#12（视图约束，原话）：「必须通过 ematic[schematic] 来 descend 进入，symbol 方式不行」／「怎么反复在 symbol 里找电路？？？」→ **每级必须开 schematic 视图，禁止用 symbol 视图 descend**。
- U#14（禁直接开目标，原话）：「1 是从顶层进入到指定层，而不是打开此指定层 cell」→ **必须逐级遍历，不许直接 open 目标 cell**。
- U#13（停止约束，原话）：「进入成功后，就应该停止再调用什么函数」（否则 Aether 卡死）→ **到达末级后停止，不再继续 descend/调用**。
- 路径示例：`XIctop/XI_Channel/XI_BnkGTopX4_Top/XI_BnkGTopX4_gut/XI_BnkGTop_AC/XI_D_BankLogicx2L/XI_R_RowPreDec`，顶层当前开的是 `WOWTOP`（path[0]=XIctop 是 WOWTOP 里的 instance，不是顶层 cell 名）。
- 后半段（U#19–U#27）大量是 GUI 卡顿/子进程/X11 调试，与 descend 算法无关。

## 三、assistant 最终方案
- 最终用 `pyAether.aePush({"hierpath": "/".join(pts), "viewType": "schematic"}, da, "r")` 一把 descend；早期手写 aeDescend 逐级方案被替换。
- 入口处若 `pts[0] == 当前顶层 cellName` 则 `pts = pts[1:]`（剥离冗余顶层名）。
- viewType 固定 `"schematic"`。

## 四、建 case 提炼（「牙齿」来源）
1. 逐级 descend（从顶层起，按 instance name 匹配，开 sub-cell schematic）——禁直接 open 目标。
2. 每级开 schematic 视图——禁 symbol（sub-cell 只有 symbol 时报错，不许回退 symbol）。
3. 到达末级即停——不许多 descend。
4. path[0]==顶层 cell 名时剥离冗余首段。
5. 任一级 instance 未找到 → 清晰报错并停在出错级。
6. maxDepth 上限——超深路径截断报「maxDepth exceeded」而非死循环。
7. 跨输入守卫——不同 DB+path 产出不同 descend 链（反硬编码）。

## 五、与其他 case 的差异
- 与 SubcktExtract/NetlistChk/SubSecFilter（CDL/网表语法检查）不同：本 case 是 **OA 原理图层次遍历算法**（view 选择 + instance-name 匹配 + 逐级 open）。
- 与 RsCalcFlow（Virtuoso 工具循环编排）不同：本 case 单链路 descend，关注视图/路径语义而非迭代收敛。
