# Trace 深读笔记：1792139236507_7jzqb (reedchen / hfeg0plg93)

- **user**: reedchen ; **host**: hfeg0plg93 ; **session**: 1792139236507_7jzqb.messages.json (2.6MB, 911 msgs)
- **domain**: waveform (FineSim .mt0.csv 测量数据 Tskew 后处理)
- **match_count**: 200 (summary.tsv: 300 netlist + 3055 schematic 关键词 — 实为 FineSim 仿真输出 CSV 处理，netlist/schematic 关键词来自 .TITLE/.option/schematic_ALPS 路径命中)

## 用户需求轮（26 轮非工具 user 文本）
- **msg[0]**（A 档任务说明，逐字原文）：「/rundata/ddgoa/V0/simdir/finesim/workdir/reedchen/simulation/ReedChenWork_Dbus_tball_0929_Rev0_schematic_ALPS/sim_vintcore_normal/output/output_SS_9V-40C.mt0.csv 请你用脚本帮我处理一下这个csv文件，这个文件有PP 和 WP 两组数据，每组数据又分为Tr和Tf两份，先将所有数据向1.5ns取余，然后你需要找到Tr和Tf各自的最大值和最小值，然后用公式：Tskew = max(tf_slow,tr_slow) - min(tf_fast,tr_fast)得到PP 和 WP 两组数据的Tskew」
- msg[45] 纠正：「你算的不太对，WP和PP 是两种情况，应该得到两种Skew，修改一下你的脚本，另外写清楚你的脚本该怎么用」
- msg[65] 增强：英文注释 + 递归批处理 + PVT 解析 + log 文件
- msg[223] 3x 数据 L1/L2/L3，三批取最小
- msg[330] summary 去掉 TrTf 列；电压 74V→0.74V, 9V→0.9V；多行横向对比
- msg[396] 4 个 sim 文件夹
- msg[416] 跳过 error 数据
- msg[458] 忽略取余后 = 0 or 1.5n 的点
- msg[499] 发现脚本只算了一行（max=min=avg 全同），要求逐行统计
- msg[530] 参考 GenSkewMea.py，编写 DbusOutPP/WP tr/tf 量测脚本（normal 128 / mc 14，10 samples each）+ 分析脚本
- msg[883] 最终结构化表格 PVT 为列

## FineSim .mt0.csv 格式（trace msg[2] read_files 结果）
- 第 1 行：`$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=0`
- 第 2 行：`.TITLE '.option PARHIER = LOCAL'`
- 第 3 行：逗号分隔列名 `epp000_r01, epp000_r02, ..., epp000_r48, epp000_f01, ..., epp000_f48, epp001_r01, ..., ewp000_r01, ...`
  - `e<group><idx>_<dir><sample>`：group=pp/wp, idx=3位(000-127), dir=r(Tr)/f(Tf), sample=2位(01-48)
  - 真实：128 索引 × 48 r + 48 f × 2 组 = 24576+ 列（agent msg[64] 报告 24578 数值/行）
- 第 4 行起：逗号分隔数据值（秒，科学计数法，如 4.1936e-09），真实文件**单行数据**

## agent 工具链
- read_files 读 CSV → editor 写 tskew_calc.py → run_approved_command 跑脚本
- msg[49] 首版脚本：skip 2 行, line 3=headers, line 4=data; epp→PP, ewp→WP, _r→Tr, _f→Tf; modulo 1.5e-9; Tskew = max(Tf_max,Tr_max)-min(Tf_min,Tr_min)
- msg[62-64] 修正版（PP/WP 分别独立 Tskew）→ 用户接受

## 用户接受的金标准（msg[64]）
| 组 | Tskew | Tr 范围 | Tf 范围 |
|----|-------|---------|---------|
| PP (epp) | **83.00 ps** | 1177~1253 ps | 1170~1220 ps |
| WP (ewp) | **296.50 ps** | 1087.5~1144 ps | 1246~1384 ps |
- PP: slow_max=max(1220,1253)=1253, fast_min=min(1170,1177)=1170, Tskew=83
- WP: slow_max=max(1384,1144)=1384, fast_min=min(1246,1087.5)=1087.5, Tskew=296.5

## 资产合成决策
- /rundata 原路径 reedchen-owned，e0031982 无权读 → 按 trace 公开事实合成 A 资产
- A: FineSim 头/列名约定/取余算法/真实 Tskew 数值原值；列数降采样 4 索引×6 r/f 每组（24+24+24+24=96 列，控体积）；单行数据
- hidden B: 不同 PVT(TT/0.8V/25C) + 5 索引×8 r/f 每组(40×4=160 列) + **3 行 monte-carlo** + 不同数值范围（PP Tr 1450~1490/Tf 1380~1420, WP Tr 920~980/Tf 1310~1370 → row0 PP Tskew=110, WP=450）→ 杀硬编码 + 测多行支持

## 合成 case
- EDA-Eval-DesignFlow-FineSimTskew-001 (waveform, L2, track=faithful)
- 16 条件 a-p: zip+py_compile / A subprocess / A 列计数 / A PP / A WP / 源码静态 / B subprocess / B 列计数 / B row0 tskew / B aggregate 多行 / B 行完整 / 跨输入护栏 / 周期强制 / 确定性 / 行序不变 / 退化提交护栏
- 自验：ref PASS 16/16; 4 negatives ALL-FAIL distinct{empty_shell→b, print_fixed→f, core_deleted→d, naive_concat→d}
- A Tskew 与真实 msg[64] 完全一致：PP 83.0ps, WP 296.5ps
