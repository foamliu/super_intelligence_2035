# 深读笔记：1792389346933_uiykd（DDR5 analogsim pattern VrefCS→MRR 序列查找）

## trace meta
- session: 1792389346933_uiykd.messages.json (246 msgs / 136 user)
- user: t0002470 / host: hfeg0pkn004
- match_count: 379 · domain: analog_context
- 真实 pattern 源：.75 `/home/coverage/DDR5/DDR5_Common_Pattern/analogsim/`（e0031982 可读）
- 合成 case：EDA-Eval-DesignFlow-DDR5CmdSeqFind-001（A 档 trace-faithful，L1 analog_context/schematic_netlist/waveform）

## 会话主线
用户要求从 DDR5 analogsim pattern 目录下查找 VrefCS 到 MRR 的连续命令序列。agent 用 grep/python 解析真实 .v pattern 文件中的 task/endtask 块、提取命令名序列、匹配相邻命令对。

## 关键用户轮（A-faithful 选料）
- **[0] 主任务（A 档选料，verbatim 逐字）**：「你能否从/proj/drcoa/V0/simdir/verilog/ydhe/verilog.ddr5.drcpa.aicov/patterns/analogsim目录下找到VrefCS到MRR的连续序列」 — 干净提需求轮 ✓（用户未给根因/修复方案，规则②不命中）

→ 选 [0] 作 A 档 task 说明（verbatim 逐字，仅 mask 路径 token）。

## A-faithful 合成要点
- 用户字面 VrefCS→MRR 严格相邻在真实语料 = 0 匹配（已验证）→ intentional A-faithful fidelity：case 验证 parser 正确报 0 for impossible queries + 正确找高频对 + 正确应用 bank/bg 约束子集。
- 真实 .v 文件 e0031982 可读 → 直接 scp 8+8 真实文件做 A_set/B_set（非合成）。A≠B on Active_TO_Write(49≠48) 杀硬编码 + 跨输入护栏。
- 11 query 覆盖：0-match 字面（VrefCS_TO_MRR/VrefCA_TO_MRR/MRR_TO_MPC_ZQCal_Latch）+ 高频对（Active_TO_Write/Write_TO_Read/MRR_TO_MRR）+ 约束子集（*_ba_diff/*_bg_same）。
- check.py 19 条件 a–s；k_rationale=k_check=19。
