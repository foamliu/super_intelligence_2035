# 深读笔记 — 1783596713423_53n4v (e0014566 / hfeg0pkn001)

- session: 1783596713423_53n4v.messages.json (712KB, 270 msgs, 6 user turns)
- user: e0014566, host: hfeg0pkn001 (10.129.2.10), match_count=317
- tools: virtuoso 255 + cellview 73 + dbCreateInst 64 + skill 27 + dbCreateRect 1 + calibre 1 → 真 layout 创建/审查会话
- domain: pg_layout (power fill merge audit) / layout_virtuoso

## 用户轮（UI#）逐字
- UI#0 (msg 0): `hello` (meta)
- UI#1 (msg 2): `read the prompt_powerfill.md and do the job in it.` (meta — 引用文件执行预设任务，不取作 A 档)
- UI#2 (msg 99): `所有的修复都固化了吗` (追问修复状态，非新需求)
- UI#3 (msg 132): `不要在 SKILL.md 中记录历史修复信息` (过程指令)
- UI#4 (msg 140): `另外，每次你都要找 run_powerfill_agent.py 这个脚本，不要瞎找，直接到 skill 里面去拿。` (过程指令)
- **UI#5 (msg 146): `请你检查下原始的输入layout: austin_new/test_20260528/layout. 输出的power fill cell: austin_new/test_20260528_auto_pgfill/layout. 以及 将原来的输入layout 和 power fill cell merge 过后的结果：austin_new/test_20260528_powerfill/layout。 能帮忙审查下他们之间的关系嘛.另外我给你一个参考是我手动调入 power fill cell 到原layout 中的：test_20260708`** ← **A 档 seed 合规**（提出需求+目标，未给根因/修复）

## UI#5 agent 工具链（msg 147-161）
- SandBox_MCP_Server__run_code (SKILL/Virtuoso) 多次调用：
  - AuditCell(lib,cell,label): dbOpenCellViewByType → 统计 shapes/labels/vias/instances/nets/pins/blockages/bbox/shapes-with-net/shapes-with-pin + 列 nets(figs/pins) + vias bBox
  - LayerAudit: 逐 layer/purpose 计数
  - Merged-vs-Manual 详细对比: instance(同 master? t) + net(VSS! figs 对比) + 逐层 shape 计数表 + diff 标记
  - M1 shape 明细: 逐 shape 列 layer/purpose + rect|label + bBox + net
- 中途 fprintf format spec 错误、makeTable 语法错 → 改 list 实现，最终成功
- read_files run_powerfill_nogui.il (526-795) 读合并代码
- editor 改 run_powerfill_nogui.il（替换 dbCopyFig 展平逻辑为 instance-based）

## 真实审查结论（gold = msg 161 报告）
| 属性 | 原始 test_20260528 | pgfill test_20260528_auto_pgfill | 合并 test_20260528_powerfill | 手动 test_20260708 |
|------|-----|-----|-----|-----|
| Shapes | 241 | 47 | **243** | 120 |
| Vias | 4 | 231 | 4 | 4 |
| Instances | 0 | 0 | 1 | 1 |
| Nets | 1 (VSS!) | 0 | 1 (VSS!) | 1 (VSS!) |
| BBox | ((-0.33475 -96.525)(144.375 5.175)) | 较小 | 同原始 | 同原始 |

正确之处：instance 引用 austin_new/test_20260528_auto_pgfill orient=R0 origin 一致；BBox 一致；pgfill 47 shapes+231 vias 全 drawing 无 net。
严重问题：合并 shapes(243)≈原始(241)×2；逐层 Merged:Manual 精确 2:1（M1/mark 30:15、M1/pin 9:3、M1/drawing 4:2、M1/track 22:11、M2-M5 同）。
具体证据：M1/drawing rect bBox=((0.0 0.0)(54.35 2.5)) 在合并出现 2 次且都被赋 VSS!（原始 1 次）；M1/pin label bBox=((0.095 1.025)(0.905 1.275)) 合并 3 次。
根因：合并代码 dbCopyFig 逐个展平复制 + foreach labels 再复制 + Phase3 net restore 关联到所有匹配 shape（含重复）；手动参考用 dbCreateInst 直接实例化只 1 份。

## A-档 disqualified → B-档 synthesized L1-boundary
- gold 依赖私有 austin_new lib（e0014566 workspace on hfeg0pkn001），沙盒(.75 / e0031982)无权访问该 lib/cell → 不可真跑 SKILL dbOpenCellViewByType 复现
- 合成锚点：把 4 cell 的审查清单（summary + layer 分布 + M1 shape 明细，从真实 SKILL print_log 提取）写成行式文本清单，SUT 写离线 Python 解析器做重复图形检测 + 逐层比率分析 + 合并策略判定
- case_id: EDA-Eval-DesignFlow-PFMergeDupAudit-001
- A 输入：cell_original_A / cell_pgfill_A / cell_merged_A / cell_manual_A（2:1 dup 模式，VSS!）
- hidden B：3:1 triplication，VDD!，lib austin_new_B（结构 != A）
- hidden B2：clean 1:1，verdict OK（跨输入守卫杀 always-HAS_DUPLICATES / 硬编码 B 脏 JSON）
- check.py 14 条断言 (a)-(n)，k_check=14=k_rationale>=8 GATE PASS
- ref PASS 14/14 ✓；5 negatives（empty/print_expected/core_deleted/count_only/always_ok）全 FAIL ✓
