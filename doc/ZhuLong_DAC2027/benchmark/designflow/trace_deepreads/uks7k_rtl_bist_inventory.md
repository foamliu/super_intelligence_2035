# 深读笔记 · uks7k (lorikx@hfeg0pkn004, mc44, digital)

## trace_source
- user: lorikx
- host: hfeg0pkn004 (10.129.2.13) [11/07 scan; 11/05 scan 记录在 hfeg0pkn001/10.129.2.10 — 同一 session 文件在不同日扫描镜像到不同 host]
- session_file: 1791774991665_uks7k.messages.json (247 KB, 22 msgs)
- match_count: 44 (kw: rtl:61;verilog:7;synthesis:4)
- agent: zhulong lead, version 1
- started 2026-10-12T11:16Z, ended ~11:19Z (单轮交互 ~3 分钟)
- real_task_summary: TV1 测试芯片 SRAM Group2 EDA-BIST 前端 RTL 结构分析——用户上传 SramEDABistGrp2 顶层（27 颗 SRAM 阵列封装）+ cxmbist_1p/cxmbist_2p MBIST 控制器 + decode 译码器，要求「仅分析、不修改」。

## 对话流（单轮闭环：USER#0 提需求 → assistant 多次 read_files → 输出结构功能报告）

- USER#0（逐字原文，A 档候选）: 「请分析当前目录下的代码，给我讲解一下结构及功能，仅作分析，不要做任何修改」
  → 干净的「提出需求」轮，无根因/无修复方案，符合 A 档选轮规则。
- A#1: 制定 4 步计划（查看策略/读核心代码/搜索模块/总结），调 get_agent_policy_status + list_allowed_files（root=/proj/lacaa/TV1_TestChips/CXTV1_FS001A/frontend/SramEDABistGrp2，rtl/sim 两目录）。
- A#4-A#19: 多轮 read_files 分段读取（SramEDABistGrp2.v 1179 行分 6 段、cxmbist_1p.v 546 行、cxmbist_2p.v 900 行、decode.v 10 行、两个 _old/_bk 备份各 40 行、update.csh 9 行）。search_codebase 返回 0 文件（目录未索引），改纯 read_files。run_commands 被策略禁用（仅 hello_world profile）。
- A#21: 输出完整结构功能分析（markdown 报告）：目录总览 + 顶层模块端口分组（TAP/DFT/SRAM 阵列）+ 内部三层架构（ISEL→decoder→inst_selection one-hot）+ 27 颗 SRAM 实例清单（i0-i26，20 颗 CXN4HC1/HC2/HD2 PS 系列 + 7 颗 pl35h_fs 系列，vmux Nto16 选 16-bit 输出）+ 两个 MBIST 控制器（cxmbist_1p March C- P1-P7 单口、cxmbist_2p March C- P1-P14 双口，vec_match 比对函数）+ decode.v（参数化 one-hot 译码器）+ 备份文件性质说明。

## 关键产物与金标准

- **真实 RTL 文件**（从 trace tool_result content 完整重建，存 assets/rtl/）：
  - SramEDABistGrp2.v (1179 行, 62KB)：顶层 `module SramEDABistGrp2(...)`，37 input / 5 output / 2 inout；27 颗 SRAM 实例（`u_CXN4HC1PS1024X144M2B2C1R1W1BW1RE1_FS` 等 20 颗 + `u_pl35h_fs_hd1prf_svt_*` 等 7 颗）；23 个 `vmux<N>to16` 实例；1 个 `decoder #(.WIDTH(5))` 实例。
  - cxmbist_1p.v (546 行)：`module cxmbist_1p(...)`，March C- 状态机（state 名 S3_P2_CMP/S6_P2_CMP/.../S29_P7_CMP_up，注释 `// P1: WA up`…`// P7: RA up`，7 个 March 元件 P1-P7），vec_match 函数。
  - cxmbist_2p.v (900 行)：`module cxmbist_2p(...)`，March C- 双口状态机（P1-P14，14 个 March 元件）。
  - decode.v (10 行)：`module decoder #(parameter WIDTH=5)(...)`，one-hot 译码器。
- **金标准**（B 档 synthesized 接口固化）：交付 `analyze_rtl.py <rtl_dir> <out_json>` 自动结构化清单工具，金标准=对真实 RTL 的结构事实（top_module / sram_count / files / mbist march_elements / top_ports / vmux_count / decoder_count）。隐藏 B 用全不同的 SramBistGrp5（10 颗 RAMBIST*NxM + mbist_sp March B P1-P5 + dec5）反硬编 A。

## 为什么本 case 用 A 档

- USER#0 是逐字原文「请分析当前目录下的代码，给我讲解一下结构及功能，仅作分析，不要做任何修改」——干净的「提出需求」轮，无根因/无修复方案。
- 接口固化为 `analyze_rtl.py + report.json` 不改意图（用户要「分析结构」，交付工具把分析自动化 + 结构化）。
- 判分对事实（模块名/SRAM 计数/March 元件序列/端口方向/vmux/decoder 计数），不对措辞。

## check.py 设计要点

- 19 条独立可失败条件 (a-s)：a zip 含两件 / b py_compile / c report.json 合法 + 8 顶层键 / d B 真跑 exit0 + 合法 JSON / e B top_module=SramBistGrp5 / f B sram_count=10 / g B files 集合 + modules / h B sram inst_names={u_ram0..u_ram9} / i B mbist 数量=1 / j B march=[P1-P5] March B / k B top_ports 18/4/2 / l B vmux=6 / m B decoder=1 / n 反硬编 A（B 名出现 + A 名不出现）/ o 3-seed 决定性 / p 反作弊（含解析逻辑）/ q report_A top=SramEDABistGrp2 / r report_A sram=27 / s 无泄漏（不含 check.py 工件 + B 常量）。
- §4.2 真跑候选：subprocess 在隐藏 B 上执行 analyze_rtl.py（cond d-q 真跑）。
- §4.5 随机化：3-seed 决定性（cond o）。
- §4.9 三假提交：neg1 naive_noop（空壳）FAIL cond e / neg2 always_pass_stub（硬编 A）FAIL cond e / neg3 gutted（删 SRAM/MBIST/port 解析）FAIL cond f——全 FAIL NEG_RC=3/3。
- §4.8 泄漏隔离：assets/ 仅 prompt+task_brief+rtl(A)+hidden_manifest，无 check.py/reference/jsonl。
