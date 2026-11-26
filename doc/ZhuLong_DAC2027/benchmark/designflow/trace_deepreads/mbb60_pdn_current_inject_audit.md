# 深读笔记 — mbb60 (1792748499142_mbb60, jxwang@hfeg0pkn005, mc=99)

## 会话概况
- 129 msgs, 70 user / 59 assistant, agent=lead
- **2 个真实任务**（其余 user 轮为 tool_result）：
  - U#1 (idx 0): skill_instructions waveview-fsdb-readerV2-2（skill 加载，非任务）
  - **U#9 (idx 14)**: `/proj/drgqx/.../Act_pre_TT98.fsdb，要看wren信号` — FSDB 波形读 wren（**失败**：252 万信号深层层级，裸名 wren 找不到，wv 严格全名匹配，通配超时，user 让停 → 不适合做 case）
  - **U#49 (idx 88)**: `/proj/.../vblen.sp 分析一下这个仿真文件，是怎么把电流挂进去的，有没有错误` — SPICE PDN 电流注入机制分析 + 查错（**成功**，产出完整分析报告 → 本 case 金标准）

## 选用的任务（U#49）
- **域**: analog_context（SPICE deck 分析，PDN 电流激励）
- **用户原话**: 「分析一下这个仿真文件，是怎么把电流挂进去的，有没有错误」(clean goal-expression，非 root-cause)
- **资产**: vblen.sp + include(idf0_vblen_current, PDN_vblen_light.cdl 156MB, FPA_vss_port.spi) — 原文件在 .75 /rundata/drgqx 与 /home/ruolinz/Desktop，**shell 不可读**（权限），故 B-grade synthesized

## 金标准机制（assistant 报告，三层电流注入）
1. **PWL 电流源** `Ii_vblen_bank i_vblen_bank 0 PWL(... R 0 TD 1E-06)` — 周期~4.8ns 带 SPIKE 的激励电流，R=repeat, TD=delay 1us
2. **零值电压源感测** `Vblen_bank i_vblen_bank 0 0` — 钳 0V + 感测支路电流 I(Vblen_bank)
3. **F 型电流控制电流源 (CCCS)** `F_vblen1..56 vblen_CMOS_* 0 Vblen_bank ratio`，`ratio=-1/56` — 总电流÷56 均摊到 56 个 PDN 节点；负号保证方向
- 另: Rvblen* 挂 Vout→PDN, VVSS* 0V 源接 vss PDN
- `.tran 10p 20u`, `.temp 85`, corner tt, `.option finesim_mode=spicead method=gear2only`

## assistant 审计要点（→ check.py 断言来源）
- F_vblen 56 个目标节点在 PDN_vblen_light.cdl 全部 FOUND（不悬空）
- PWL 语法完整（R 0 + TD 收尾）
- include 文件都存在
- ratio 数量配平（56 节点 / -1/56）
- ratio 负号方向正确（必须为负）
- 未使用 .param（cload/esr/Cgatein）隐患
- vss_FPA_* 与 vss 强短路语义风险

## 合成设计（B-grade synthesized, PdnCurrentInjectAudit-001）
- **SUT** `pdn_current_audit.py <deck.sp> <pdn.cdl> <outdir>`: 纯 stdlib(argparse/re/os/sys/json/csv) SPICE deck 解析器
  - 解析 .tran(tstep/tstop 带单位 p/n/u/m/k) / .temp / .param ratio(求值 -1/N) 
  - 识别零值电压源(Vxxx node 0 0 感测源) / PWL 电流源(Ixxx...PWL + R/TD 标志) / F 型 CCCS(Fxxx target 0 sense ratio) / R-Vout 连接
  - F 目标节点在 .cdl 节点集校验
  - 输出 audit_report.json(10+键) + injection_summary.csv
- **A**(SUT 可见): vblen_A.sp(.tran 5p 10u, .temp 85, ratio=-1/8, 8×F_vblen_A*) + pdn_A.cdl(10 节点) + FPA_vss_A.spi + idd0_vblen_A_current + task_brief
- **B**(hidden, 不进沙箱): vblen_B.sp(.tran 2p 15u, .temp 105, ratio=-1/12, 12×F_vblen_B*) + pdn_B.cdl(14 节点) + FPA_vss_B.spi + idd0_vblen_B_current
- **C**(嵌入 check.py 字面量): vblen_C.sp(.tran 8p 12u, .temp 125, ratio=-1/6, 6×F_vblen_C*) + pdn_C.cdl(8 节点) — 反硬编码
- A/B/C: tran(temp/ratio/F数/节点前缀全不相交
- **check.py 13 条件 a-m**: a zip含+无禁import/eval/B-C泄漏 / b py_compile / c 跑B退0+两输出文件 / d JSON≥10必需键 / e tran_tstep/tstop对B / f temp对B / g ratio对B(求值) / h sense源识别 / i PWL源识别(R+TD) / j F源数对B / k F目标节点全在cdl / l 反硬编码C≠B / m 3-seed sha256一致
- 难度 L1（SUT 纯 stdlib SPICE 文本解析，无 EDA 工具运行时，与 r520/r519/r518/r521 一致）

## dup 检查
vs SpfRccShieldDiff/SpfCapResAnomaly/SpfResPathTrace/SpfMosCapRatio/IddTreeAnalyze/IddMeasPostProcess/SpiceUndefParamScan/LeakageCellPvtAudit — 机制（PDN F 型 CCCS + PWL + 零压感测 三层电流注入审计）全不同 → 非 dup ✓
