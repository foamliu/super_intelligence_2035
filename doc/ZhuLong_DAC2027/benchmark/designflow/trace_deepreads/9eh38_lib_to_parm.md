# 9eh38 deepread — e0046686 @ hfeg0plg80, lib→parm (Liberty timing 抽取 → 反标 parm)

## trace meta
- session: `1792376325408_9eh38.messages.json` (e0046686@10.129.8.120/hfeg0plg80, mc=874, 338 msgs, 2.68MB)
- domain: **verification** (后仿反标 back-annotation simulation)
- daily eda_trace 2026110*.log fresh (11/03), markers: `874 netlist  55 calibre  6 schematic  3 hspice  2 spectre  2 pyAether  1 "lang": "pyAether"`
- ledger: claimed (verification, mc=874)

## user 意图 (A 档规则② 合格判定)
- U#1: "当前目录下有两个文件夹分别是组内两个同事的代码工程...生成一个适合刚入职新人阅读的readme" — README 文档任务（非本 case scope）。
- U#47-57: AutoSim/cx_cm characterization 流程分析追问。
- **U#68（本 case 任务说明）**：「当前接到一个任务：【从lib提取timing给反标跑仿真】，需要在zk或者np的哪个工程的什么地方，如何进行修改？先给出任务梳理对任务进行拆解分析，给出修改目标内容给我，由我确认后再决定是否开始修改」 — **clean 提需求**（接到新任务，给反标跑仿真），未给根因/修复 → **A 档规则② 合格 → A 档 faithful**。
- U#74: 「按照方案 B推进：在 np/autosim_script 下做 lib→SDF + 集成到后仿全流程」 — 选方案 B。
- U#79: 「开始前请先将这个任务拆解和梳理完整记录下来」 — 要拆解文档。
- U#100: 「开始编码实现」 — 开始编码。
- U#181-183: 「将剩余的步骤7-9也完成」 — 完成剩余步骤。

> U#68 是 clean 提需求（"接到一个任务：从lib提取timing给反标跑仿真"），用户未给根因/修复方案 → A 档规则② 合格。金标准 = 助手实际交付并被用户接受的工具 `extract_lib_timing.py`（lib→parm，用户 U#181-183 接受 "完成剩余步骤"）。

## 助手真实交付（金标准，已 ssh 10.129.8.120 验证可读）
- 工具位置：`/home/e0046686/new/np/autosim_script/lib_timing_tools/extract_lib_timing.py`（772L/31KB，纯 stdlib Python3）
- 需求文档：`/home/e0046686/new/np/autosim_script/lib_timing_tools/REQ_LIB_TIMING.md`（112L，完整 spec）
- README：`/home/e0046686/new/np/autosim_script/lib_timing_tools/README.md`（171L，CLI 用法）
- 映射表：`config/lib_timing_map.txt`（25 parm → Liberty 时序弧映射）
- 参考 .lib：`/home/e0046686/new/tmp_scan_data/cxn4s1p2048x72m4b2c1r1w1bw1re1_tt0p75v25c.lib`（真实 SRAM 2048×72 liberty，巨大非便携）

## 任务核心（REQ_LIB_TIMING.md 摘要）
- **输入**：单个 `.lib`（Liberty NLDM 7×7 网格），CLI `--lib <path>`
- **输出**：`timing_stress.parm`（25 行 `.param name = value`，单位秒），供 `timing_stress.sp` 第 10 行 `.inc` 引用
- **25 parm 映射**（固定顺序）：clkh, clkl, tcsr, tcsf, tchr, tchf, twsr, twsf, twhr, twhf, tasr, tasf, tahr, tahf, tdsr, tdsf, tdhr, tdhf, tbwsr, tbwsf, trtsr, trtsf, twtsr, twtsf, tcyc
- **parm → lib 弧**：
  - clkh/clkl = CLK min_pulse_width rise/fall_constraint（CLK_TRAN 7×1）
  - tcyc = CLK minimum_period rise_constraint（CLK_TRAN 7×1）
  - tcsr/tcsf/tchr/tchf = CEB setup_rising/hold_rising rise/fall_constraint（CONSTRAINT 7×7）
  - twsr/twsf/twhr/twhf = WEB setup/hold rise/fall（CONSTRAINT 7×7）
  - tasr/tasf/tahr/tahf = A[10:0] setup/hold rise/fall（CONSTRAINT 7×7, bus 11）
  - tdsr/tdsf/tdhr/tdhf = D[71:0] setup/hold rise/fall（CONSTRAINT 7×7, bus 72）
  - tbwsr/tbwsf = BWEB[71:0] setup rise/fall（CONSTRAINT 7×7, bus 72, **仅 setup**）
  - trtsr/trtsf = RT[1:0] setup rise/fall（CONSTRAINT 7×7, bus 2, 仅 setup）
  - twtsr/twtsf = WT[1:0] setup rise/fall（CONSTRAINT 7×7, bus 2, 仅 setup）
- **网格轴**：CONSTRAINT `index_1`=CLK slew(0.010…0.070ns 7 点), `index_2`=信号 slew(0.050…0.350ns 7 点); CLK_TRAN `index_1`=constrained_pin_transition(0.010…0.070ns 7 点)
- **坐标选取**：`--coord i,j`（0..6，7×7 取 [i,j]，7×1 取 [i]）；`--coord-val x,y`（ns 值反查最近 index）
- **bit 选取**：`--bit max|min|avg`（总线 bit 聚合，默认 max）
- **单位换算**：lib 内 ns → parm 秒，`×1e-9`；负值原样保留（setup 可为负）
- **placeholder 0.1**：全网格恒 0.1（cxmt 占位）→ WARN + 仍输出 `1e-10`
- **输出格式**：每行 `.param <name> = <value>`，value 用 `f"{v:.10g}"`；25 行固定顺序；末尾单换行；无注释/空行

## case scope（本轮合成）
- **case_id**: `EDA-Eval-DesignFlow-LibToParm-001`（verification, A 档 faithful, L2 纯 stdlib）
- **verb** = `lib-to-parm`（Liberty timing 抽取 → 反标 parm），与所有已有 shard-A case verb 互斥
- **交付**: submit.zip { `lib_to_parm.py`（通用 lib→parm 转换器, CLI `--lib <path> --coord 3,3 --bit max --output <path>`, 纯 stdlib）+ `timing_stress_A.parm`（对可见 A bundle 预计算的 parm）}
- **A 可见 bundle**：合成小 Liberty `sram_demo_A.lib`（1 cell, 8 pins: CLK/CEB/WEB/A[1:0]/D[1:0]/BWEB[1:0]/RT[1:0]/WT[1:0], NLDM 7×7 CONSTRAINT + 7×1 CLK_TRAN 表, 忠实 Liberty 语法, 非常量值测 index 解析, tasr/tasf 占位 0.1）+ `lib_timing_map.txt`（25 parm 映射）
- **B 隐藏 bundle**（异构, cross-input guard 击破硬编 A）：`sram_demo_B.lib`（不同 cell 名 sram_demo_B, 不同 timing 值, placeholder 在 tdsr/tdsf 而非 tasr/tasf, 不同 bus bit 值 → bit=max 选不同 bit）
- **判分**：check.py `--coord 3,3 --bit max` 跑候选于 A+B（subprocess 真跑 python3），独立 oracle（不同代码路径）重算期望 parm 值，逐条断言 25 行顺序/格式/单位换算/bit 聚合/placeholder/[3,3] index/跨输入守卫 B≠A/反硬编
- **判分环境等价**：纯 stdlib python3（无 VCS/DC/license 依赖），本地 PASS == 判分环境

## A/B 异构设计（cross-input guard）
| 维度 | A (sram_demo_A) | B (sram_demo_B) |
|---|---|---|
| cell 名 | sram_demo_A | sram_demo_B |
| 7×7 base 值 | 各弧 distinct base (10..560 ns 量级) | 全异 base (shifted) |
| 7×1 base 值 | clkh=130,clkl=230,tcyc=530 | clkh=170,clkl=210,tcyc=480 |
| placeholder 位置 | tasr/tasf (A setup) | tdsr/tdsf (D setup) |
| bus bit max 选取 | A[1]>A[0] | A[0]>A[1]（反转，测 bit 聚合方向） |
| setup 负值 | tchr 段 hold 取负 | twhr 段 hold 取负（不同弧） |

## 与已有 case verb 互斥
已有 shard-A verb: synth-upf-diagnose, apr-stamp-fix, flat-net, apr-setup-audit, apr-log-audit, vcs-equiv, itf-compare, calibre-pdf2md, flow-guide, tlef-rules, innovus-launch-diag, deadloop-scan, ostrich-spef-rc, impsr1253-vddpm-fix, redhawk-gen-inputs, pwr-globals, dc-synth, simlib-idx, power-fill, pf-merge-dup-audit, apr-stamp-geometry-fix, etc.
**lib-to-parm** = Liberty timing 抽取 → 反标 parm，全新 verb，无重叠。

## 合成计划
1. build script `designflow/_build_libtoparm_001.py` 生成 A/B .lib + map + reference lib_to_parm.py + check.py + 5 negatives + negative_selftest.py + reference_submit.zip
2. 自验：ref PASS（check.py 跑 reference_submit.zip on A+B 全过）+ 5 negatives 全 FAIL + §4.9 (a)(b)(c) 三假全 FAIL
3. 断言闸门：k_rationale == k_check ≥ 8
4. append A.jsonl + mark case + 日报
