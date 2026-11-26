# r115 shard C 候选池调研笔记（2026-11-05）

## 背景
r114 已交付 ViaFillSvrfGen-001。r115 经 `trace_ledger.py --shard C next` 取候选池（mc>=30，已排除 225 条台账），目的：为 shard C（physical_layout: layout_aether/layout_virtuoso/pg_layout/physical_verify）选一条合格 A-档 seed 做第 113 条 case。

## 调研过程（按 mc/signal 依次排查，均逐字读 prompt + 元数据 + 部分深读 messages）
1. **jason17w / 1791944224191_6i6lk**（mc=328, netlist:1518, virtuoso:1）→ 元数据 title = `[skill-creator] 创建 vps-cli skill`。netlist/virtuoso 关键词来自 VPS user guide 内容，真实任务是 skill-creation。**假阳性，跳过**。
2. **xinqiaoz / 1789874220542_wiait + 1789892820566_17cgk**（mc=321, calibre:204）→ 两条均为 `handoff` 交接会话（prompt=「请使用 handoff 技能从 HANDOFF_drc_pattern_check.md 恢复上下文」），status=failed，PDK QA DRC pattern check。与 r111 DrcPatternHandover-001 主题重叠；handoff 轮按 A-档规则禁用（用户已给根因/修复方案）。**跳过**。
3. **mike / 1789887279405_ve67l**（mc=279, innovus:100, voltus:98）→ prompt=「logic_cosim ... 执行 README.md 第一步」。logic_cosim 仿真任务，innovus/voltus 关键词来自相邻文件。**假阳性，跳过**。
4. **e0047695 / 1793155371052_v59v8**（mc=376, virtuoso:459, .lef:298, .spi:323）→ prompt=「你好」，cwd=agentdir。深读 messages：真实任务是 tkinter GUI cdslck 文件查找/删除器（cdslck_finder.py + 字体调整）。.lef/.spi 来自 Virtuoso 工作目录背景。**假阳性，跳过**。
5. **shwanlai / 1792980238183_sh05n**（mc=212, aether:2599, floorplan:109）→ prompt=「你可以做什么」，1.6MB agentdir 自动评测会话，真实任务埋在后续轮且过大。**深读成本过高，本轮跳过**。
6. **haoyut / 1787625078133_9ryp9**（mc=286, cellview:528, pyaether:211, virtuoso:109）→ prompt=「你现在连着一个virtuoso的视图...告诉我你当前链接的视图的信息」。深读 338 msgs：agent 经权限诊断(chmod o+x .cline/data)打通 SKILL 桥接，`geGetEditCellView()` 取得 `iejoal_top/LOGICTOP/schematic`（2504 inst/1557 nets），并下钻 ChannelLogic_22ull→SetIDDAmpOIP_22ull。**连接视图是 schematic 不是 maskLayout → domain=schematic_netlist（shard A/B），非 shard C physical_layout。跳过**。
7. **e0014566 / 1783056984013_albb5**（mc=244, virtuoso:1005）→ prompt=「我有一个layout，以及需要加上去的一个via cell, 怎么通过skill语言实现在这个layout上加上这个via cell, 并且生成新的layout」。clean A-档 seed，但与 **r108 AutoViaLayoutMerge-001**（trace=1783342909947_149bq，同用户 e0014566、同 via-cell→layout merge 主题）上游重叠；且 shard C 已有 4 条 AutoVia 系案例（AutoViaGen/AutoViaLayoutMerge/AutoViaPFAudit/RsCalcAutoVia）。**主题饱和，跳过**。
8. **e0014566 / 1782905118695_h80lc**（mc=225, virtuoso:470, .gds:142, calibre:225）→ prompt=「请你描述一下这个打开的layout」。深读 148 msgs：agent 全程未能桥接到运行中的 Virtuoso（pyAether 端口 refused、SKILL 沙箱是裸 SKILL35 未加载 MDE/hiGetCurrentWindow），仅从 CDS.log 读到 `ddsServOpen("stdcells_ac" "and2LVSDx1" "layout" "edit" nil)` 历史记录，从未取得版图几何/实例/图形内容；最终输出是 USER#3 的工艺节点查询（cxmt10G3_LP, 1p4m1x2y1z），**gold 污染（原目标=版图描述未达成，最终产物=工艺查询）**。**parked**（ledger 已 mark）。

## 结论与下轮改进
- r115 **未交付 case**（候选池 physical_layout 真 seed 稀缺，本轮调研的 8 条高分候选全部不合格）。
- 根因：当前 keyword 过滤（tools 列含 calibre|virtuoso|aether|layout|lvs|drc）假阳性率高——用户在 EDA 工作目录下常发通用编程/schematic/cosim/handoff/skill-creator 请求；纯 calibre 命中多为 physical_verify（已 46 条饱和）或 PDK QA DRC（与现有 DrcPattern* 重叠）；virtuoso/cellview 命中多为 schematic 视图（shard A/B）；auto-via 主题已 4 条饱和。
- **下轮筛选改进**：
  1. 在 .75 上批量抓候选 session 的 `prompt`/`title` 文本，正则要求含 `layout|maskLayout|版图|.gds|.lef|.def|PG|power|via|placement|route|floorplan` 之一，且**不含** `schematic|原理图|cosim|skill-creator|handoff|README`；
  2. 优先 user=e0014566 之外的新用户（e0014566 已 3 条 case）；
  3. 对通过 prompt 过滤的候选，先 `scp` messages.json 抽 user#1 + 最终 assistant gold 文本，确认 (a) 连接视图是 maskLayout（非 schematic）(b) gold 是版图相关真实产物，再 claim；
  4. 可把 mc 阈值进一步降到 30（已降）并扩大扫描到 mc>=20 的 layout 关键词强匹配池。
- **parked**：1782905118695_h80lc（gold 污染）。
- **claimed→parked**：本轮无遗留 claimed。

## 心跳口径
- shard C 累计 case 仍 112（r115 未新增）。
- 通过率口径不变（B 档 20–30%）。
- 本轮为调研轮，非「连续两轮只深读」（r114 已交付 case）。
