# 深读笔记 · 2spf5 · tongfanl@hfhds201 · WTM stimulus 结构审查

## trace 概况
- session: 1791620953988_2spf5.messages.json (dir-based, 22 msgs, 147KB)
- user: tongfanl, host: hfhds201 (10.129.32.75, .75 本机)
- spice 工具计数 33/49 ratio 0.673 (hspice 关键词来自 WTM stimulus 的 Finesim 仿真上下文)
- 工具: list_allowed_files=5, read_files=3, run_commands=1, search_codebase=1, get_agent_policy_status=1

## 对话流
- U#0-3 (msg 0-3): 同句重发 4 次: `<user_input mode="act">/home/tongfanl/DDR6/DSCQA/analogsim/WTM/WTM001_normal_check.v WTM002_normal_check.v 检查下有没有问题，不要改动</user_input>` — **任务说明轮，逐字作 prompt**（提出需求，无根因/修复方向 → 符合 A-档选轮）
- U#4 (msg 4): 另起需求 "找一下 /apps/imctf/cad/ 下关于 finesim/primesim 的 synopsys 手册" — 不入本 prompt（次要需求）
- assistant (msg 5-19): read_files 分段读 WTM001(784行)+WTM002(812行), list_allowed_files 搜 /apps/imctf/cad/ 手册, search_codebase
- assistant (msg 20): **最终审查报告**，8 条发现：
  1. [WTM002] 期望寄存器 mrdf/mre0/mre1/mre2 被覆盖/丢失（声称 MRSetting 在循环外）— ⚠️ 经复核 MRSetting 实际在 loop 内(msg113-120 在 for62 与 end133 之间)，assistant 此条判断存疑
  2. [WTM002] 循环结构不一致（3次 vs 2次，Load_Mode/MRSetting 位置）
  3. [两文件] tmrr_wtm 取整问题（floor vs ceiling，有 ceiling 注释）
  4. [两文件] nnop 参数未使用
  5. [WTM001] Write 地址模式不对称（Writes[8]/[9] 打破交替）
  6. [WTM002] MR DE/D7 op_mark 8'hff 全宽（vs WTM001 8'b0000_1111 窄）
  7. [WTM002] 第102行 Clear Error op 值不同 + 注释误导
  8. [WTM002] patinvctrl = $urandom（32-bit→6-bit 截断）
  + 确认正常: LFSR PRBS24 多项式 / DQ 偏移 XOR / seed 加载顺序
  + FineSim 手册位于 /apps/imctf/cad/doc/user_guide/Spice_Simulation/Finesim_Manual/, PrimeSim 未找到
- U#5 (msg 21): 新问题 "gen_wtm_write_data 解析" — 不入本 prompt（下一轮需求）

## 金标准复核（人工）
assistant 的 finding #1（MRSetting 在循环外）经 grep 复核不准确（WTM002 MRSetting 在 for-loop 内）。故金标准不照搬 assistant 主观判断，改用**客观可静态检测的结构事实**:
- unused_param（nnop 签名声明, body 未引用）— 两文件均有
- width_truncation_urandom（bit[5:0] patinvctrl = $urandom）— 两文件均有
- width_truncation_error（error_write = $urandom, 10-bit）— 仅 WTM002
- floor_division_ceiling（三元除法 + ceiling 注释）— 两文件均有
- full_width_op_mark（MR 8'hDE 用 8'hff op_mark）— 仅 WTM002
- load_mode_mr5_outside（MR5 Load_Mode 在 for 之前）— 仅 WTM002
- write_pattern_asymmetry（Write .bg 交替在 [8]/[9] 打破）— 两文件均有
- mrsetting_outside_loop — A 中不存在（两文件 MRSetting 均在 loop 内）；在合成 B2 中植入以构建可检测 bug

## case 设计
- prompt = U#0 逐字原文
- A = WTM001/WTM002 真实 1-140 行 excerpt（含全部结构元素：签名/声明/for-loop/MRSetting/MRR/Write）
- hidden B = 合成 WTM_B1_check.v（3-iter, MRSetting 内, narrow op_mark, nnop 引用, $urandom->patinvctrl, ceiling, 对称 Write）+ WTM_B2_check.v（4-iter, MRSetting 外, 8'hff, nnop_unused 未用, $urandom->error_write, MR5 外, Write[6][7]打破, 无 ceiling）— 不同 issue 组合
- 通用化 review_wtm.py 输出 {files:{name:{issues:[{line,category,severity,description}],loop_iterations,loop_line}}}
- check.py 15 断言（a-o），ref PASS 15/15 + 5 negative 全 FAIL + §4.9 三假全 FAIL + 断言闸门 15==15
