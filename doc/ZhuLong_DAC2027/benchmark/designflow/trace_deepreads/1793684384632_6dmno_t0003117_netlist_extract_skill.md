# Deepread · 1793684384632_6dmno · t0003117 · Virtuoso SKILL SPICE netlist extraction skill

> shard C candidate (r392 selection round). SEED picked, deepread complete.
> 本轮（r392）基于本 deepread 合成 case：`EDA-Eval-DesignFlow-NetlistExtractSkill-001`（layout_virtuoso, B档 synthesized）。

## trace_source

- session_file: `1793684384632_6dmno.messages.json`（路径 `/home/t0003117/.cline/data/sessions/1793684384632_6dmno/1793684384632_6dmno.messages.json`）
- user: t0003117（ Virtuoso SKILL 开发工程师 / analog flow 自动化）
- host: hfeg0pkn005 (10.129.2.14)
- mc: 611 (mc≥10 口径, 11/11 snapshot)
- keywords: `virtuoso:88;skill:42;calibre:5` — virtuoso/skill 关键词均为 true-positive（trace 真在做 SKILL 脚本开发），calibre 5 次是误判（来自 BatchExtractHspiceNetlist.il 框架路径字符串里的 "calibre" 子串）
- match_count: 611
- 4 user turns, 395 messages total
- 日期：2026-11-04

## real_task_summary

t0003117 是 Virtuoso SKILL 自动化工程师，本 trace 是一个 **build-skill 工作流**（不是 issue-handler）：用户要求 agent 把一段"从当前 schematic cellview 导出 SPICE netlist"的对话封装成一个可复用的 SKILL 技能（3 个文件：导出函数 + 编排脚本 + 文档）。

**关键对话节点**：
- USER#0 (act): 「执行 SKILL.md」 — 用户要求 agent 按已存在的 SKILL.md 步骤跑一次 netlist 导出
- USER#1 (act): agent 连上 Virtuoso bridge，用 `SandBox_MCP_Server__run_code` (lang=skill) 在 SKILL 沙箱执行代码，加载公司框架 `BatchExtractHspiceNetlist.il`，写 `exportNetlistNoGUI.il` + `extract_current_netlist.il`，从 cellview `lwdrx8_2d5T`（库 `IMCXX_RAM_LIB`）导出 hspiceD SPICE netlist
- USER#2 (act): agent 报告导出成功，netlist 落到 `finesim_data/lwdrx8_2d5T_*/netlist/lwdrx8_2d5T.sp`
- USER#3 (plan): 「把这个 chat 做成一个 skill」 — 用户要求 agent 把整段对话沉淀成可复用技能（写 SKILL.md 文档化前提/步骤/陷阱）

**trace 域判定**：trace 全程在 Virtuoso SKILL 沙箱里做 schematic→netlist 导出 + 技能封装。属于 **layout_virtuoso** 域（schematic cellview 操作 + SKILL 脚本开发），不是 physical_verify（无 drc/lvs/xrc 动作），不是 schematic_netlist（不是分析 netlist 内容/语法，而是生成 netlist 的 SKILL 工具）。

## agent 实际产物（trace msg flow）

agent 走了 build-skill 路径，最终产出 3 个文件：

| step | 动作 | 输出 |
|---|---|---|
| 1 | 接 USER#0「执行 SKILL.md」，连 Virtuoso bridge，`geGetEditCellView()` 拿到当前 cellview = `IMCXX_RAM_LIB/lwdrx8_2d5T/schematic` | cv 对象 |
| 2 | `isCallable('ExtractHspiceNetlist)` 检测公司框架未加载 → `load("/apps/imctf/cad/init/settings_cdns/skill/se/BatchExtractHspiceNetlist.il")` | 框架就绪 |
| 3 | 写 `exportNetlistNoGUI.il`：定义 `procedure(InnoExportNetlistNoGUI())`，内部 `geGetEditCellView()` 拿 cv → `cv~>libName/cellName/viewName` 动态获取 → `system("mkdir -p ...")` 建目录 → `ExtractHspiceNetlist(?lib ?cell ?view ?sim "hspiceD" ?out simDir)` 导出 → `system("cp -f ...")` 拷贝 netlist | 导出函数文件 |
| 4 | 写 `extract_current_netlist.il`：7 步编排（load→detect cv→mkdir→export→cp→verify→summary），调用 `InnoExportNetlistNoGUI()` | 编排脚本文件 |
| 5 | 在 SKILL 沙箱 `load()` 两个 .il，跑 `InnoExportNetlistNoGUI()`，实测 netlist 落到 `finesim_data/lwdrx8_2d5T_<ts>/netlist/lwdrx8_2d5T.sp` | 实跑成功 |
| 6 | 接 USER#3「做成 skill」，写 `SKILL.md`：元数据 + 前提条件（Virtuoso 已开 + Bridge 已启动 + cd 到项目根）+ 7 步表 + 关键 API 表 + 已知陷阱表（5 条）+ 文件清单 | 技能文档 |

## 为什么选本 trace 做 seed（B档 synthesized）

**真 seed 价值**：
1. 真实的 build-skill 工作流（不是 issue-handler），完整覆盖 layout_virtuoso 域 SKILL 开发场景，本 shard C 此前 case 多为 physical_verify，layout_virtuoso 案例偏少
2. agent 产物（3 个 .il/.md 文件）结构清晰、可复制，是理想的可判分 deliverable
3. trace 内含真实公司框架 API 名（`ExtractHspiceNetlist`、`BatchExtractHspiceNetlist.il`、`geGetEditCellView`），合成 case 时可保留这些真实 API 名
4. 关键陷阱「硬编码 cell 名 lwdrx8_2d5T」是真实 SKILL 开发常见错误，适合做 cross-input guard

**为何 B档 synthesized**（不直接 A档 faithful）：
- 原 trace 的真实输入是「Virtuoso 当前打开的 cellview 状态」+「已存在的 SKILL.md 内容」，这些是 EDA session 上下文，无法直接附入 SUT 沙盒
- 真 trace 395 msg 中 90% 是 bridge 调试噪声（多次 `isCallable` 探测、路径试错、SKILL 沙箱连接重试），核心有效信号 < 30 msg
- 故合成「小而精」输入：visible A 给 cellview 配置 JSON + 半成品 .il 模板（带 TODO）+ SKILL.md 模板；hidden B 给不同 cellview 配置（`ANALOG_IP_LIB/sa_v2/schematic`），考验 agent 写出的脚本是否动态通用（不硬编码 A 的 cell 名）
- 保留真 trace 的核心 API 名、目录结构（`finesim_data/{cell}_{ts}/netlist/`）、7 步流程拓扑

## 合成 case 设计（B档）

### visible A 输入
- `cellview_config_A.json`：library=`IMCXX_RAM_LIB`, cell=`lwdrx8_2d5T`, view=`schematic`, netlist_format=`hspiceD`
- `extract_current_netlist_broken.il`：半成品 7 步脚本，Step 3-6 是 TODO 占位，Step 1 load()、Step 2 geGetEditCellView() 已写好
- `SKILL_template.md`：半成品文档，含元数据 + 前提条件 + 步骤骨架 + 已知陷阱表 + TODO 列表

### hidden B 输入（cross-input guard）
- `cellview_config_B.json`：library=`ANALOG_IP_LIB`, cell=`sa_v2`, view=`schematic`, netlist_format=`hspiceD`
- 判分器用 cond i 验证提交脚本不含字面量 `"lwdrx8_2d5T"`，cond j 验证用了 `cv~>cellName` 动态访问 → 保证脚本对 hidden B 也通用

### Gold/reference
- `exportNetlistNoGUI.il`：`procedure(InnoExportNetlistNoGUI())`，`geGetEditCellView()` → `cv~>libName/cellName/viewName` → `mkdir -p` → `ExtractHspiceNetlist(?lib ?cell ?view ?sim "hspiceD" ?out)` → `cp -f`
- `extract_current_netlist.il`：7 步编排，load() + geGetEditCellView() + mkdir + InnoExportNetlistNoGUI() + verify + summary
- `SKILL.md`：元数据 + 前提条件 + 7 步表 + 关键 API 表 + 已知陷阱表 + 文件清单

### check.py 12 条断言（a–l）
| tag | 断言 | 守护目标 |
|---|---|---|
| a | zip 含且仅含 3 个预期文件 | deliverable 结构 |
| b | exportNetlistNoGUI.il 定义 `procedure(InnoExportNetlistNoGUI` | 导出函数存在 |
| c | exportNetlistNoGUI.il 调用 `geGetEditCellView()` | 动态获取 cellview |
| d | exportNetlistNoGUI.il 调用 netlist 导出函数（`ExtractHspiceNetlist(`/`axlExportNetlist(`/`sesExportNetlist(`），且非注释/isCallable 提及 | 真实导出动作 |
| e | extract_current_netlist.il 用 `load("...exportNetlistNoGUI.il")` 加载 | 编排脚本加载导出函数 |
| f | extract_current_netlist.il 调用 `geGetEditCellView()` | 编排脚本动态检测 |
| g | extract_current_netlist.il 用 `mkdir`/`createDir` 建目录 | 目录创建步骤 |
| h | extract_current_netlist.il 用 `cp`/`copyFile` 拷贝 netlist | 拷贝步骤 |
| i | 两脚本均不硬编码 A 的 cell 名 `lwdrx8_2d5T`（不出现为字面量或独立 token） | cross-input guard |
| j | 脚本用 `cv~>cellName`/`cv~>libName` 动态访问 | 动态 cellview 通用性 |
| k | SKILL.md 含「前提条件」+「步骤」章节 | 文档完整性 |
| l | subprocess SKILL linter：括号平衡 + ≥1 个 `procedure(` 定义 | 语法静态检查 |

### §4.9 三假覆盖
- neg1 `empty_shell`（空壳脚本）→ fail cond b
- neg2 `print_expected`（只 printf 期望结果不真导出）→ fail cond b
- neg3 `hardcode_a`（硬编码 `lwdrx8_2d5T`）→ fail cond i
- neg4 `omit_export`（注释里提 ExtractHspiceNetlist 但不真调用）→ fail cond d（bonus 第 4 个负样本）

## 域归属与去重

- 域：**layout_virtuoso**（schematic cellview 操作 + SKILL 脚本开发）
- shard C 第 120 条 case（layout_virtuoso 域第 54 条）
- t0003117 首条 case（此前无）
- 与 r387 StarrcReleaseNoteGen-001（physical_verify）域不同，无重复
- 与 r390 DrcEnclosureTripleExtract-001（physical_verify, Calibre SVRF）域不同，无重复
- 与 r391 DrcQaMergeBloatDiagnose-001（physical_verify, DRC QA diagnosis）域不同，无重复
