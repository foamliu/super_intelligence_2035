# Deepread — 1789630642152_8b8wk (ghyang @ 10.129.2.12, mc=69)

- **session_file**: 1789630642152_8b8wk.messages.json (目录式 `/home/ghyang/.cline/data/sessions/1789630642152_8b8wk/1789630642152_8b8wk.messages.json`, size≈537KB)
- **keywords**: cmos:155;netlist:152;schematic:114;hspice:74;synopsys:17;mosfet:13;aether:4;analog:3
- **assistant tools**: read_files=15, list_allowed_files=4, run_commands=4, search_codebase=6 (analysis-heavy，无 write_to_file/create_file，纯解释)
- **domain**: schematic_netlist（SPICE 仿真激励/网表分析）

## 用户轮（逐字，A-faithful 评估）
- **U#0**：「帮我分析这份仿真文件，按不同部分的功能来介绍，然后再介绍他引用的文件是什么作用： /proj/ddgoa/V0/workdir/ghyang/DDGOA/Yiotwist/sim_w0w1r1w0r0_twistYio.sp」
  → 提需求（分析仿真文件按功能分部介绍）·**未给根因/修复** → A-faithful eligible（但纯解释非 produce）
- **U#1**：「介绍主要激励信号和读写公共信号，另外我如果修改了激励文件，可以怎么快速看到波形，帮助直观分析我改的对不对，还是说只能跑个仿真看看」
  → 细化（介绍激励信号 + 如何快速看波形）·A-faithful eligible（解释类）
- **U#2**：「这里的激励文件中是否能看到控制w0w1r1w0r0的过程，另外sweep data = yioloading是怎么工作的」
  → 细化（解释 w0w1r1w0r0 控制过程 + sweep data 机制）·A-faithful eligible
- **U#3**：「解释这一句.meas tran tcsl_w1   when v(xi_msaq_fbcc_02.cslcon0<0>)  val='0.5*pvcsl'  td=tmeas  rise=c_csl_w1  print=0」
  → **核心 .meas 语句**（典型 SPICE measure 指令：tran 分析 + when 条件 + val 表达式(带单引号) + td + rise + print）·A-faithful eligible

## 关键产物（user-accepted）
- 用户全程为**解释/分析请求**，agent 用 read_files/search_codebase 读 .sp 文件后**文字解释**各部分功能 + 解释 .meas 语句含义。无脚本/文件 produce。
- 真实 .meas 样本（U#3 原句）：`.meas tran tcsl_w1 when v(xi_msaq_fbcc_02.cslcon0<0>) val='0.5*pvcsl' td=tmeas rise=c_csl_w1 print=0`
  - 典型形式：`.meas <analysis> <name> when <v(sig)> val='<expr>' td=<t> rise=<n> print=<0/1>`
  - 含嵌套实例路径 `v(xi_msaq_fbcc_02.cslcon0<0>)`、单引号 val 表达式、变量引用(pvcsl/tmeas/c_csl_w1)

## 合成决策（B 档 synthesized，L1 真跑候选）
- 原始 trace 为纯解释类（无 produce），不可直接做 A 档 produce 任务。
- **B 档任务**：把「解释 .meas 语句」升级为「写脚本把整份 SPICE deck 的所有 .meas 指令**结构化提取**为 JSON 数组」——服务用户真实分析目标（要理解 deck 里所有 .meas 在测什么）。
- 金标准 = 结构化 .meas 解析器（Python，纯文件 in/out），断言只对**可客观验证的解析事实**（计数/字段名/字段值/续行合并/注释跳过/反硬编码/确定性），🚫 不对措辞。
- L1 真跑候选：check.py 用 subprocess 在隐藏 B/B2/empty deck 上跑候选脚本，断言输出 JSON 结构。
- **真实输入**：合成 SPICE deck（A 含 7 条 .meas，覆盖 when/param/avg/max/cross 修饰/续行/单引号 val；真实 .sp 路径在 /proj 不可附加）。A deck 嵌套实例路径风格取自 U#3 真实句式 `v(x.sig<idx>)`。
- **隐藏 B**：不同 9 条 .meas（when/param/avg/min/max/rms + dc/ac/无 analysis 三类）。
- **隐藏 B2**：边界（无引号 val、param、续行 2 行、零 .meas deck）。
- **反硬编码三轴**：A/B/B2 .meas 名完全不相交 + 字段值不同 + 续行结构不同；硬编 A 名者在 B 上 d/f/o 条件 FAIL。
- 与现有 case 去重：shard D 已有 5kcuw「检查激励文件 R 循环/for 循环」(同用户不同 session/不同任务)；「FineSim Measure 脚本检测 CLK 上升沿」「fscript 测量 write→dq 间隔」均为**写 measure 脚本**，本 case 为**解析/提取 .meas 指令到结构化表**，方向相反，不重复。
