# Deepread: o6j6c — OSC checker enable in fsmchk flow (config-setup produce)

> **r995 (2026-11-20)** · session `1794827268223_o6j6c` · jingjiew@hfeg0plg97 (10.129.8.229) · mc=373
> domain: schematic_netlist (D-pure: netlist:544, analog:789, verilog:886; also cmos/synopsys/schematic/waveview)
> **trace access**: ✅ accessible at `/home/jingjiew/.cline/data/sessions/1794827268223_o6j6c/1794827268223_o6j6c.messages.json` (2.1 MB, 233 msgs)
> ⚠️ **r994 "trace-inaccessible" 结论推翻**: r994/r989 误把 `sessions/<sid>.messages.json` 当文件直查，实际是 `sessions/<sid>/<sid>.messages.json`（sid 是目录）。同路径 bug 亦影响 rwced（tongfanl@hfhds206, 10.129.32.80, mc=12, 实际可达，r994 误记 user/host）。

## 真实用户意图（逐轮）

| U# | 用户原话（verbatim, 掩码无） | 意图类别 |
|:--|:--|:--|
| 0 | `/proj/.../OSC001_..._FF.X2P3_11600这是我跑完FSHCHK的波形目录，其XRUN。log是不是没有报错` | log error check (debug-Q&A) |
| 28 | `/proj/.../primesim.OSC001_..._FF1.23V-40C.X2P3说错了，这才是我的文件` | 路径修正 |
| 68 | `为什么没有fsmchk结果` | diagnose missing output |
| 76 | `我在/proj/dscqa/V0/workdir/jingjiew/script/ddr6_fsm_autcheck.sv里写了OSC的checker，为什么fsmchk没有相应的输出宝宝` | diagnose + 自定义 checker |
| 88 | `这个checker需要在ddr6-test.sv里定义吗` | setup Q&A |
| 104 | `这里是tb的环/proj/.../verilog.ddr6.dscqa.vecgen境，如何调用OSC fsm check` | setup Q&A |
| 140 | `怎么加` | setup Q&A |
| 180 | `这是我/proj/.../script/的fsm check的目录，里面有fsm check的配置文件，ddr6_fsm_autcheck.sv里已经有osc checker了，就在文件最后，我应该怎样在test.sv中定义` | setup Q&A + 路径线索 |
| 194 | `我应该怎样调用这个OSC checker，能否回答我，我已经把FSM CHK的路径以及TB的路径给你了` | setup Q&A (用户开始 frustrated) |
| 196 | `可以说详细一点吗` | setup Q&A |
| 204 | `我难得不需要在ddr6_fsm_autcheck.sv中定义\`define OSC——CHK来进行调用吗` | setup Q&A (用户提假设) |
| 206 | `看看我这个fsmchk命令/proj/.../fsm_check/fsmchk` | 路径线索 |
| 220 | `你读这个命令吗#!/bin/bash ...` (贴 fsmchk 脚本) | 给出 fsmchk 脚本 |
| 222 | `我在问你` | frustrated |
| 223 | `我在问你，我要怎样样调用这个OSC CHECK，是不是需要在auto check 文件里面添加define，然后通过fsmchk -d 加定义的check名字来执行OSC check` | **关键意图：用户提假设要 confirm** |
| 225 | `那我应该怎样才能输出fsm chk报告呢，直接执行fsmchk命令没有` | setup Q&A |
| 227 | `我需要第二种` | **决策：选 option 2（加 ifdef + -d 调用）** |
| 229 | `119行后面是一个】呀，可以加你的代码吗` | 精确改法追问 |
| 232 | (assistant 最终交付) | **金标准交付** |

## 金标准交付（U#232 assistant 最终回答，用户接受）

用户选「方式二：加 `ifdef OSC_CHK`，精细控制」。assistant 给出**3 步精确改法**：

**改动 1 — `ddr6_fsm_autcheck.sv`**（OSC checker 加 ifdef 包裹）:
- 第 1863 行（`// OSC internal check` 之前）加 `` `ifdef OSC_CHK ``
- 第 1936 行（文件末尾）加 `` `endif ``

**改动 2 — `runsim.pl`** `@extra_files` 数组（第 45 行 `top.sv` 后）加一行 `ddr6_fsm_autcheck.sv`

**改动 3 — 跑命令**:
```bash
cd /proj/dscqa/V0/workdir/jingjiew/script
./fsmchk -q "你的队列名" -d "OSC_CHK"
```

assistant 中段（U#226）还解释了根因：用户直接跑 `./fsmchk` 无输出，是因为 `runsim.pl` 没改 → `ddr6_fsm_autcheck.sv` 没被复制/编译 → `FSM_CHK` 宏虽开但 checker 代码不存在 → 无输出。

## Case 设计草案（next round synthesis）

**子型**: config-setup produce（fsmchk flow 启用自定义 checker），D 域 schematic_netlist + flow-driving。**新规则（2026-11-15 用户令）下合法**：setup/env-config/flow-driving 全部恢复可造。

**A 档 trace-faithful reframe**:
- 任务说明 = U#223 verbatim「我要怎样样调用这个OSC CHECK，是不是需要在auto check 文件里面添加define，然后通过fsmchk -d 加定义的check名字来执行OSC check」+ U#227「我需要第二种」（option 2: ifdef + -d）
- 资产 A: 合成 `runsim_A.pl`（保留真实结构：`@extra_files=(...top.sv)` 第 45 行结束 + 第 119 行 print + 第 121 行 symlink 注释，无 ddr6_fsm_autcheck.sv）+ `ddr6_fsm_autcheck_A.sv`（保留真实结构：OSC checker 在末尾 unwrapped，前面有 `ifdef WTM` 包的 WTM checker 作对照）+ `fsmchk_A`（bash 脚本，bsub -K -q -d 解析）
- task_brief.md: ≤3 行「交付接口：`enable_osc_chk.py` 接受 runsim.pl + ddr6_fsm_autcheck.sv + fsmchk 路径，输出修改后的 3 文件到 outputs/」

**隐藏 B**: `runsim_B.pl`（不同 @extra_files 内容/不同行号/不同 print 文本）+ `ddr6_fsm_autcheck_B.sv`（不同 checker 名如 `DDRCHK_PLLLOCK` 在不同行号，前面有 `ifdef CATM` 包的 CATM checker 作对照）+ `fsmchk_B`（不同队列名/不同 getcsv 路径）。token 与 A 完全不相交。

**candidate_ref.py**（纯 stdlib）: parse `runsim.pl` 找 `@extra_files=(...);` 数组并在末元素后插入指定 .sv 文件名；parse `ddr6_fsm_autcheck.sv` 找目标 checker 块（按注释/关键词）前后加 `ifdef CHECKER_NAME`/`endif`；parse `fsmchk` bash 脚本提取 `-d` 解析逻辑并 verify 调用命令含 `-d CHECKER_NAME`。输出 3 个修改后文件 + 1 个 JSON manifest（记录每处改动的行号+内容+原内容）。

**check.py 断言草案（≥8, subprocess-on-B + recompute-ground-truth-from-B）**:
- a. zip 含 `enable_osc_chk.py` + py_compile pass
- b. B 跑通 exit 0 + 有效 JSON manifest
- c. B manifest 含 3 个文件键（runsim/ddr6_fsm_autcheck/fsmchk）
- d. B modified `runsim.pl` 的 `@extra_files` 数组含目标 .sv 文件名（recompute: 独立解析 B 原文件 → 期望插入位置 → 比对）
- e. B modified `ddr6_fsm_autcheck.sv` 在目标 checker 块前有 `` `ifdef <NAME> ``、后有 `` `endif ``（recompute: 独立解析 B 原文件找 checker 块边界 → 期望 ifdef/endif 位置 → 比对）
- f. B modified `ddr6_fsm_autcheck.sv` 其他 checker（如 `ifdef CATM` 包的）未被破坏（recompute: 独立解析 B 原文件其他 ifdef 块 → 比对 modified 文件中这些块仍完整）
- g. B manifest 的 fsmchk 调用建议含 `-d <NAME>`（recompute: 独立解析 B `fsmchk` 脚本 getopts -d → 比对）
- h. 反硬编码: B 输出 + 源码零 A-only token（runsim_A / ddr6_fsm_autcheck_A / WTM / OSC_CHK 等 A 专有 token 词边界）
- i. 退化守护: 空/无 checker 块输入不 traceback，优雅退出非 0
- j. 3-seed md5 一致
- k. zip 卫生: 无 reference/hidden/.jsonl 泄漏
- l. 无写源文件（candidate 不能 open(w/a/x) 原 A/B 文件，只读 + 写 outputs/）

**判分牙类型**: (i-a) 阈值判 + (i-d) 集合 recompute（@extra_files 数组成员集合 + ifdef 块位置集合）混合，新子型 **config-setup produce with recompute-ground-truth-from-B**。

**与既有 D 域 case 区分**:
- r984 NetlistInstHierTrace = top-down instance climb（Verilog 网表）
- r986 SchHierParentLocateProduce = reverse parent-lookup（schematic cell 库）
- r988 Net2FsdbPathMapProduce = signal-path-map（SPICE .subckt pin 剥离）
- r990 PatternHierResolverProduce = pattern-signal→netlist-hierarchy（per-query 集合）
- r992 NetlistStructureGraphProduce = netlist→structure-graph（DAG 角色）
- **本案 = config-setup produce（fsmchk flow 启用 checker，改 runsim.pl + ddr6_fsm_autcheck.sv + fsmchk 调用）**，**D 域首例 flow-driving/config-setup 子型**（r772 pool_reaudit_D 复活 setup/flow-driving 类后的首个落地候选）

**真实性约束**:
- 真实 `runsim.pl` / `ddr6_fsm_autcheck.sv` / `fsmchk` 路径在 `/proj/dscqa/V0/...`，体积可控但属内部资产不可直引入沙盒 → synthesized-reframe（保留真实结构特征：`@extra_files=(...);` 数组、`ifdef ... endif` 块、`bsub -K -q -d` getopts）
- 真实 OSC checker 名保留（`OSC_CHK`），B 用对偶名（如 `PLLLOCK_CHK`）

## 状态

- ✅ trace accessible confirmed (overturns r994 false blocker)
- ✅ ledger claimed (r995, mc=373, schematic_netlist)
- ✅ user intent map complete (22 user turns)
- ✅ 金标准 identified (U#232 3-step modification, U#227 chose option 2)
- ⏳ **DEBT: case synthesis deferred to r996** — 233-msg trace + 3-file config-setup produce + 12-断言 check.py + 3 negatives + selftest 不能在 r995 剩余 ~20 min 内合规完成；deepread 已就绪，r996 第一件事即合成 + 自验 + 落库
- 📊 trace 覆盖率: cases/D 527 (unchanged this round, mc≥10, 快照 1119)

## 跨 shard 影响

**r994「D-pure fresh 池结构性枯竭」结论推翻**：2 个所谓 "trace-inaccessible" 候选实际都可达（同路径 bug: sid 是目录不是文件）。这意味着：
1. D-pure fresh 池至少 +2 条 truly fresh（o6j6c mc373 + rwced mc12），其中 o6j6c 是 clean config-setup produce 形态（r989 误判为 "FSHCHK XRUN.log diagnose" — 实际是 config-setup produce，U#227 用户明确选 option 2）
2. r994「需扩选料面」结论需修正：先修路径 bug 重扫，再判是否真枯竭
3. **next 轮优先**: (a) r996 合成 o6j6c case; (b) 建议扫描脚本修 `sessions/<sid>` 目录化路径 bug，重扫 mc≥10 D-pure 池
