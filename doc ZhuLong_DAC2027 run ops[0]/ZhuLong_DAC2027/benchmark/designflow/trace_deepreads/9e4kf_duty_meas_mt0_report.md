# Deepread: 9e4kf — finesim duty PUP/PDN measurement

## Trace
- session: `1793341757885_9e4kf` (bolint@hfeg0plg100, 10.129.8.232)
- summary.tsv: mc=42, keywords `netlist:94;synopsys:78;hspice:51;pex:36;schematic:21`, tools `94 netlist 39 hspice 21 schematic`
- file: `.cline/data/sessions/1793341757885_9e4kf/` (dir: .json 2587B + .messages.json 121476B + uploads/)
- 43 msgs (23 user / 20 assistant), 2026-10-30 14:29–19:32

## User intent (U#1, msg0, the only text user turn)
> 帮我运行并且输出duty（PUP，PDN）结果，使用finesim
+ attached `01_TB_P2S_DQ_3200_noclktree_vintio_2phase_rf.sp` (13235B, 286 行)

**选轮合规 (A 档规则)**：U#1 是「提出需求 / 表达目标」轮，未给根因、未给修复方案 → CLEAN produce-task ✓。其余 22 个 user turn 全为 tool_result（无文本）。

## .sp 结构（真实附件，286 行）
- FineSim testbench，P2S DDR PHY DQ 通道，低速时钟域 duty 量测
- 关键 .param：p_datarate=10.667G / p_datarate_ls=3.2G / UI_ls=312.5ps / twck_ls=625ps / pvdd2c / tr=tf=20p
- 4 个探测电容 C1..C4 on PUP/PDN/PUPN_LowSpeed/PDNN_LowSpeed
- `.tran 1p 'tdly+13*twck_ls+3n'`；`.probe v(PUP) v(PDN) v(PUPN_LowSpeed) v(PDNN_LowSpeed) ...`
- **.measure duty 语句**（line 183-219）：
  - `duty_pup = h1/p1`：t1 when V(PUPN_lowspeed)='pvdd2c/2' rise=4；p1 trig rise=1→targ rise=2；h1 trig rise=1→targ fall=1
  - `duty_pdn = h2/p2`：t2 when V(PDNN_lowspeed)='pvdd2c/2' fall=4；p2 trig fall=1→targ fall=2；h2 trig rise=1→targ fall=2
  - `duty_pup1 = h3/p3`：t3 rise=5；类似 duty_pup
  - `duty_pdn1 = h4/p4`：t4 fall=5；类似 duty_pdn
  - 另外 PU_tr/PU_tf/PD_tr/PD_tf（10%↔90% 上升/下降时间）
- **.alter PVT corner**（line 238-284）：base `.lib '...G4B_CIP_pvt_corner_DLDO_05_rf.sp' TT_RT` + 16 个 .alter：TT_RT_25/TT_LT/TT_HT/SS_RT/SS_LT/SS_HT/SS_LT_vdd2h/FF_RT/FF_LT/FF_HT/SF_RT/SF_LT/SF_HT/FS_RT/FS_LT/FS_HT = **17 corner**（1 base + 16 alter）
- PEX 网表 `.inc` 指向 /proj/ddgoa（e0031982 无权限读）

## Agent 行为（zhulong, 全程卡在环境）
- msg1 计划：检查环境 → 确认 .measure duty 语句 → 跑 finesim → 解析 .mt0/.ms0 输出 duty
- msg5-15：写 check_env.py 检查 finesim 路径 (/apps/synopsys/SRB/finesim/V-2023.12-1/bin/finesim) + 网表依赖 + 设计规模（PEX 12.6MB/12.4万行/96核/17 corner pass）
- **msg21-41 卡死**：finesim `-h` 报 `GLIBCXX_3.4.26 not found`。诊断：agent 环境 `LD_PRELOAD` 预载了旧版 libstdc++（系统只到 GLIBCXX_3.4.25），finesim V-2023.12 需要 3.4.26。尝试清 LD_PRELOAD + 全盘找新版 libstdc++，但 `find /apps` 递归 glob 超时。**session 在 msg41 仍在搜索 libstdc++，仿真从未启动 → 无真实 .mt0 产物。**

## 金标准裁定
- trace 无用户接受的结果（agent 未完成）→ 不取 trace 末尾产物
- 按 .sp 文档化的 .measure duty 结构 + FineSim .mt0 多 alter 量测格式 → **B-synthesized L1**：给定已产出的 .mt0 量测文件 + .sp，解析并输出结构化 JSON duty 报告
- 真实 .sp 的 .measure 语句 + .alter corner 结构完整可读 → 资产 A 的 .sp 按真实结构精简（保留 .measure duty_pup/duty_pdn/duty_pup1/duty_pdn1 + .alter .lib corner），.mt0 按真实格式合成
- 隐藏 B1/B2：不同 corner 名 + 不同 duty 值 + 不同 corner 数，反硬编码

## Case
- **EDA-Eval-DesignFlow-DutyMeasMt0Report-001**（spice_sim / B-synthesized / L1, k=15）
- deliverable: duty_report.py（读 .sp + .mt0 → JSON duty 报告）
- check.py 15 断言 (a)-(o)：zip 含脚本/py_compile/exit0/合法JSON/corner数/4 duty键/duty_pup·pdn·pup1·pdn1值/corner名/summary统计/反硬编码B2/交叉输入B2
- 自验: ref PASS 15/15 + 6neg 全 FAIL + §4.9 三假(empty_shell/only_print/ref_core_deleted)全 FAIL + 断言门 15≥8 + byte-sync ✓
- jsonl B 234→235, ledger covered 235→236 (spice_sim 188→189), parked 585→584
