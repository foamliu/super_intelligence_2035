# Deepread: 1795000940649_06m8h (binwenh @ hfeg0pkn005) — DQSIB slicer .sp deck diff

**trace_source**: user=binwenh, host=hfeg0pkn005 (10.129.2.14), session=1795000940649_06m8h.messages.json, mc=27 (hspice:150;netlist:75;aether:49;cmos:45;schematic:34;pyaether:26;mixed-signal:24), NEW-user, domain=spice_sim.
**fetched**: scp 10.129.2.14:/home/binwenh/.cline/data/sessions/1795000940649_06m8h/1795000940649_06m8h.messages.json (353850 B, 24 msgs).

## 会话流（3 个 user turn）

### Turn 1 (msg 0–6) — 主任务，有交付
- **user原话 (msg0)**: `<user_input mode="act">帮我分析/proj/drgqa/V0/workdir/zanezang/SP_new/01_trannoise/路径下的.sp文件之间的区别</user_input>`
- assistant list_dir (msg2) → 15 个 `.sp` + 1 个 `run` 脚本；read_file 全部 15 deck (msg5 给出 001_slicer.sp 1–148 行 verbatim) → 产出 3975 字对比报告 (msg6)。
- **真实意图**: 对一组 HSPICE deck 做结构化差异分析。
- **关键产物 (msg6) 内容**:
  - 15 个文件 = 同一顶层激励（DQSIB slicer 灵敏度校验, 目标 `avg_data_Qout=0.92543`）的变体，85–90% 一致，差异集中在 ① corner(tt/ff/ss) ② temp(25/98) ③ 仿真控制(手动 SWING 扫描 vs OPTIMIZE + trannoise) ④ SWING 范围/步长 ⑤ 少量 measure 差异。
  - 命名规律: 006–015 = corner+温度 (TTHT/FFRT/FFHT/SSRT/SSHT)。
  - 4 组: (1) 001/002/003 tt-25 手动扫描 trannoise 关; (2) 004/005 tt-25 trannoise+OPTIMIZE; (3) 006–010 各角温手动扫描; (4) 011–015 各角温 trannoise+OPTIMIZE。
  - corner 取自 **drvqa 模型** `.lib '/proj/drvqa/V0/model/current_D5_v0d1_Rev02/model.sp' tt/ff/ss` (第22–26行); **drga 模型** (第16–20行) 001/002 注释未生效、003+ 生效。
  - 002_slicer2 特异点: tran 60n(其它510n)、扫描注释仅单点、PWL 激励 `vDATA_IN_B_0`、`DATA_IN_T_0='VREF'`、measure TO=60n。
  - run 脚本笔误: 引用 `006_slicer_TTHV.sp` 但实际文件是 `006_slicer_TTHT.sp`。
  - verbatim deck 结构 (msg5, 001_slicer.sp): `******` banner 注释; `.inc '.../finesim_option_new'`; `*.lib`(注释)/`.lib`(活动) model; `.temp 25`; `.param pvddq/VREF/SWING/VIH/VIL`; `.tran 1p 510n`; `*.trannoise`(注释); `.measure avg_data_q FROM=10n TO=510n`。

### Turn 2 (msg 7–8) — Q&A，无交付
- **user原话 (msg7)**: `你支持mix signal仿真吗？` — assistant 回答能力边界（无独立混合信号引擎沙箱，但有 Aether/FineSim/WaveView 分析能力）。无产物。

### Turn 3 (msg 9–23) — 失败的"打开项目"
- **user原话 (msg9)**: `打开dejoa项目电路` — assistant 搜 `/home/binwenh/zhulong` 未果，写 find_dejoa.py 搜索 `/proj`/`/rundata` 超时 SIGKILL (msg16)，再试 find_dejoa2.py 被 abort (msg23)。**无交付，无产物**。

## 合成决策
- **主线 = Turn 1**（有真实交付、有可复现子技能、spice_sim 域）。
- **reframe = harness-for-teeth**（Q&A/analysis → produce reusable tool）: 把"人工逐文件对比 15 deck"固化成 `sp_deck_diff_analyzer.py --deck-dir <dir> --out <report.json>`，纯 python 解析每 deck 活动（非注释）行，输出 per-deck 字段 (corner/temp/trannoise/sweep_mode/swing_range/v_sweep/tran_time/measure_type/goal_value/drga_lib/pwl) + summary。
- **layer = L1**（纯解析，无 EDA 二进制调用）。
- **track = faithful**，asset_fidelity = A=format-faithful（deck 差异段 verbatim-styled 自 msg5/6：.lib corner 活动/注释、.temp、.tran +sweep SWING/OPTIMIZE、.trannoise 活动/注释、.measure plain/goal、.param SWING=v_sweep、002 PWL+tran60n、run TTHV 笔误 trap；一致 85–90% 压缩成共享 header）。
- **asset A (visible, design_A)**: 8 代表性 deck (001/002/004/006/007/008/011/012) + run 脚本。
- **hidden B (design_B, 结构性差异)**: 8 deck，corner 混合 tt:5/ff:1/ss:2（A 无 ss）、goal=0.90（A=0.92543）、特异 102 tran=80n（A=002 tran=60n）、不同 SWING/v_sweep 值。
- **hidden B2 (anti-stub, design_B2)**: 4 deck trap —— ① 文件名 corner ≠ 活动 .lib corner（201_TTHT 实际 ff、207_FFRT 实际 ss）② trannoise 用 `* .trannoise`（星号后带空格）注释 = 关，但 naive 子串匹配 `.trannoise` 的 stub 会误判为开。corner-by-filename stub 同样误判。
- **check.py**: 16 条独立断言 (a–p)，真跑 SUT 工具于 B+B2+A，逐字段校验 + summary 计数 + 确定性 + 退化回归（empty_shell/print_only/core_deleted 全 FAIL）。
- **自验**: negative_selftest.py → ref 16/16 PASS, 5/5 neg FAIL ✓。

## 选料防 dup
- 弃 fppmi（已 case DeckConsistencyCheck-001, 2026-11-13）；弃 2xqbx（sibling dup IbisZqCalibMerge-001 per r872 note）；选 06m8h（NEW-user binwenh, mc27, hspice:150 dominant）。
