# Deepread r275 — 1793788828764_coodr (conn_priority_dup_check)

- **trace**: 1793788828764_coodr (yqlu @ hfeg0pkn005/10.129.2.14, mc=2195, markers 1809 calibre + 368 netlist; yqlu NEW 0 prior cases)
- **agent**: lead (deepseek), 132 msgs, 76 user turns (many tool results / context dumps)
- **archive**: messages.archive.json (3.34MB, 848 archived msgs), session dir layout `sessions/<sid>/<sid>.messages.archive.json`

## 选料路径
- r275 rescan (11/06~11/09 eda_trace logs, sid 正则规范化 + 按 sid 聚合 max tot + lay>=15 ∧ sim<=lay*1.1) → 461 fresh (excl ledger_C 478 normalized sids)
- 顶部 NEW-user layout-dominant 候选 peek 5 条：
  - albb5 (e0014566, 279 cellview+39 dbCreateInst): U1「怎么通过skill语言实现在layout上加上via cell, 生成新的layout」= prose-how-to, 仅 1 real turn → parked (thin)
  - uaas3 (chengleiy NEW, 286 virtuoso+28 dbCreateRect): context-restore 续会 (PROJECT_STATE.md dump 重复 6 次 + pinyin「duqu shangxia wen」+ 跑 updaTf.py 贴 log), 无干净单轮种子 → parked
  - bxdtw (ziyuny, 455 cellview): U1「启动业务场景:DRC/LVS」U2「DRC卡住了一直跑不出来怎么办」= DRC-hang diagnostic, 仅 2 real turns, 与 r237/r259/r266 DRC-log 系重叠 → parked
  - fz05e (colinxu, 290 cellview+272 schematic): U1「打开...schematic 插入 pin 保存」= schematic domain → wrong-shard (D) → parked
  - **coodr (yqlu NEW, 1809 calibre)**: U2/U3 真实任务 → 选用

## 真实用户意图 (U2, 逐字原文, A-faithful-eligible 但用户给出修复思路故做 B 档)
> 帮我优化一下这个Python脚本，现在不能验证TCP-CT-M1, M0U-CT-M1,这种情况，也就是同一个CT/M1，既可能连接TCP，也可能连接M0U，当版图上同一个位置同时画了TCP和M0U，这个CT/M1只能连到TCP，而不是M0U，需要在原来的脚本的基础上加一个新功能，查找所有类似CT-M1这种出现了两次的连接关系，并且仿照之前的pattern思路，创建对应的cell去检查rule里这个关系的正确性
- 附件: main.py (20866B, 530 行) + config.cfg (1357B) 来自 msv4x session uploads

## 真实 grounding (main.py + config.cfg + assistant 产物)
**main.py** = connectivity QA pattern generator:
- `load_config(config.cfg)` 解析 connectivity(A-Via-B 列表)/conn_layers(LAYER=purposes dict)/layermap/rulePath/deviceLayer/precision/deviceList/pPlug/nPlug
- `readLayerMap` → layer_table/datatype_table/lpps
- `find_all_paths`/`getPaths` BFS connectivity graph from bottomLayer
- `genMetal`/`genPath`/`mosGen`/`mosGenAll`/`genPattern` 用 gdspy 生成 good/bad1/bad2 GDS pattern cell
- `genNetlist` 生成 CDL; `runLVS` 跑 calibre -lvs subprocess; `readReport` 解析 INCORRECT; `main` 遍历 conn_layers×mode 生成→跑→读→summary

**config.cfg** connectivity 含 2 组重复 (Via,Target) 端点:
- CT-M1: TCP-CT-M1, M0U-CT-M1 (sources TCP/M0U)
- PCU-M0U: MT2-PCU-M0U, M0C-PCU-M0U (sources MT2/M0C)

**assistant 真实产物** (从 editor/run_approved_command 工具块提取):
- `priorityCheckPatternGen()` → 返回 `[(via, target, winner, loser), ...]` (检测重复端点 + 按 priority 解析 winner/loser)
- `genPriorityCell(via, tm, win, los, mode)` → 生成 `{via}_{tm}_pr_{mode}` GDS cell (good=连 winner, bad=连 loser)
- `genPriorityNetlist(via, tm, win, los, mode, DIR)` → 生成对应 netlist
- dry-run 脚本 import main.py + fake layer_table + 调 priorityCheckPatternGen/genPriorityCell/genPriorityNetlist + write_gds

## 为何 B 档离线重定义为 L2 config-结构分析
真实 calibre/gdspy/OA 不可沙盒复现; 离线核心 = 给定 config.cfg(含 connectivity/priority/conn_layers) → 解析重复 (Via,Target) 端点 → 按 priority 解析 winner/losers → 生成 good/bad pattern cell 清单 → 输出结构化 qa_plan.json。check.py 在 hidden B config 上 subprocess 真跑候选 (L2) 断言 JSON 结构 (15 条件 a-o)。

## B-track (hidden) 设计
- A config: 真实结构 (CT-M1/PCU-M0U 2 组重复, winner TCP/MT2 均首列源)
- B config: 合成层名 (TOP/SV/BOT/X1/X2/X3/VA/Y1/PWR/VP/OUT/GND/L1-L3), 3 组重复:
  - SV-BOT: TOP/ALT (winner=ALT 第 2 列, 挫败硬编码首源)
  - VA-Y1: X1/X2/X3 三源 (winner=X2 第 2 列, 多 loser [X1,X3], 挫败硬编码首源 + 测多源)
  - VP-OUT: PWR/GND (winner=PWR 首列)
- B 期望: 3 duplicate_groups, 7 pattern_cells (SV-BOT:2 + VA-Y1:3 + VP-OUT:2), total_rules=9

## case 结构
- assets/A: prompt.txt + task_brief.md + config_A.cfg + main_base.py(原脚本上下文, trimmed)
- assets/hidden: config_B.cfg + hidden_manifest.json
- reference: conn_priority_check.py(golden) + check.py(15 条件 a-o) + 5 negative{empty_shell→d, print_expected→e, core_deleted→e, naive_only_first→e, wrong_priority→k} + negative_selftest.py + reference_submit.zip

## 自验
- golden 15/15 PASS on B ✓ (CHECK: PASS)
- 3-run sha256 一致 (qa_plan_B: 6356191525e21f883bdff8a8eda1793de207383afde60883a6080463f43adca9) ✓
- 5 negative 全 FAIL (NEG_SELFTEST_RC=0): empty→d, print_expected→e(len2≠3), core_deleted→e(len0), naive_only_first→e(len1), wrong_priority→k(TOP≠ALT) ✓
- §4.9 三假 (empty/print/core) 全 FAIL ✓
- test==disk check.py sha 3ad48b57... ✓
- jsonl roundtrip (test 字段读回跑 reference_submit.zip) PASS ✓
- 断言闸门 k_rationale=k_check=15(a-o)≥8 GATE PASS ✓

## DISTINCT from 现有 physical_verify 系
r273 DummyRuleCfgParse=calibre Dummy config schema 抽取 / r266 DrcPatternGeomGen=DRC pattern 几何生成 / r259 DrcConnectGraphGen=DRC 连接图 / r256 LdrSvrfRuleGen=SVRF 规则生成 / r241 SvrfPvrsRuleTranslate=SVRF/PVRS 翻译 / r237 DrcLogTeardown=DRC log 拆解 —— 本案首次 ground on「connectivity 列表中重复 (Via,Target) 端点检测 + priority 优先级解析 + good/bad pattern cell 清单生成」, 核心是图论端点去重+优先级裁决+QA 计划结构化, 非规则翻译/log 解析/几何生成。
