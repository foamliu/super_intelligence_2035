# Deepread: 1794549413194_eoxs4 (gracew / hfeg0plg92, mc=333)

> trace-faithful A档候选 · domain=verification (verilog-dominant LPDDR5)
> 扫描源 ssh_eda_search_20261114_184938, fresh-diff(11/14 vs 11/13) 命中, 4-shard ledger 未收录
> 深读轮: r535 (2026-11-14). **DEBT: 1 deepread 未合成** — trace 2.7MB + 628msgs 双超阈值(>2MB & >600msgs), §3 允许本轮只深读, 下轮必须先交付 case.

## 1. Trace 元数据
- session_file: `1794549413194_eoxs4.messages.json` (subdir layout: `sessions/1794549413194_eoxs4/1794549413194_eoxs4.messages.json`)
- size: 2,734,342 bytes (2.7MB) · mtime 2026-11-14 15:16 · 文件 ALIVE (6 host 全有, 经 subdir 路径 ssh cat 取回)
- user: gracew · host: hfeg0plg92 (10.129.2.x 负载均衡池, flat ls 会误判, 须用 `sessions/<sid>/<sid>.messages.json` 子目录路径)
- 628 msgs / 324 user msgs / **44 real user inputs** (rest = tool_result) / 280 assistant tool_use
  - tool_use 分布: run_approved_command=122, editor=71, read_files=52, list_allowed_files=29, ask_question=4, get_agent_policy_status=2
- keywords: verilog:1871; netlist:530; pex:419; analog:69; cmos:34; systemverilog:28; rtl:14; aether:5

## 2. 真实任务流 (44 real user inputs, 按主题归并)

### 主题 A — cpforce 修改 (R0/R1, 核心produce-task)
- **R0**: "/proj/ddcpc/V0/simdir/verilog/linnaw/verilog.lpddr5.ddcpc.compress/proj_special.sv 请仿照最高文件写一个符合ddgoa网表到相同文件，只需要修改现有文件/proj/ddgoa/V0/simdir/verilog/gracew/verilog.lpddr5.ddgoa.1013/proj_special.sv的cpforce部分"
  → 仿照 ddcpc compress 版本的 proj_special.sv, 修改 ddgoa.1013 版 proj_special.sv 的 **cpforce 部分**, 使其符合 ddgoa 网表。
- **R1**: 用户粘贴 CP_FORCE bind 块 (9713 字符):
  `ifdef CP_FORCE
  bind msax512      hdl_msa_error_inject #(.csl_num(129)) I_hdl_msa_error_inject(.WrEn,.Csl,.Yio0,.Yio1);
  bind msax512_left hdl_msa_error_inject #(.csl_num(129)) ...
  bind msax512_right hdl_msa_error_inject #(.csl_num(129)) ...
  bind msax320      hdl_msa_error_inject #(.csl_num(80))  ...
  `celldefine module hdl_msa_error_inject(WrEn,Csl,Yio0,Yio1); parameter csl_num=129; ... (error injection module, 注错 MSA CP)
  → 即把 CP_FORCE bind + hdl_msa_error_inject 模块注入 proj_special.sv 的 cpforce 段。
- **关键路径修正**: R0 给的 ddcpc 路径 ENOENT (agent read_files 报错); agent 经 list_allowed_files + search 定位到真实文件:
  `/proj/ddgoa/V0/workdir/gracew/sos_manage_lpddr5/lpddr5/ddgoa/proj_special.sv` (大文件, 分块读 1-200 / 1570-1800 / 3050-3150 ...)
- **M109/M126**: agent 问 "能否提供 ddcpc compress 版本中 cpforce 部分的代码内容?" → 用户答 "我粘贴 ddcpc compress 版本的 cpforce 代码" (参考代码由用户粘贴, 非文件直读)

### 主题 B — cpforce 机理分析 (R3-R5, analysis, 非produce)
- R3: "你还记得我之前给你到BL8的errorcode表格吗"
- R4: 贴 2cp fail 错误码表 (CP0..CP31 / ECC0,ECC1 / RED_U,RED_V / errcode bit6~0 十六进制值 0/7/B/D/E/13/.../78)
- R5: "阅读 /rundata/ddgoa/V0/simdir/verilog/gracew/verilog.lpddr5.ddgoa.net1105/proj_special.sv 然后分析cpforce的作用机理与判断代码是否正确"

### 主题 C — TM_CompDataOut pattern 生成 (R6-R43, 第二个produce-task, 占session大半)
- R6/R8: 找/建 pattern: "对ECC&RED CP的8bit依次注错, 确认每bit检验正确", AbusDmEvDnW/E_BG2 映射 Abus_Ecc0/Ecc1/REDU/REDV<7:0>
- R9: TM_CompDataOut.v 循环上限说明 + 是否遍历 cm0_ts_CompDataSel<4:0> 表 (00000=CompError<7:0> ... 10011=CP0 ... 等)
- R12-R26: 调试 BG0 输出 x态 (除 BG_ECC 外输出 x态), bankbg0 错, bg0输出在pattern显示bg0时x态/bg1显示bg2时x态... 错位
- R27: 仿照 qi3wang 的 TM_CompDataOut_bk.v + TM_Comp_Exp_function_bk.v 写新版到 home
- R33: "if((n>8)&&(n<16)) 这个合法吗" (SV 语法)
- R35-R43: dq0 版 bg 遍历全 x态 原因分析, seeddata 产生/端口/预期输出, compdatasel 表对照, dataout=普通写+压缩读 原因

## 3. 涉及文件 (均在 /proj 或 /rundata, e0031982 权限 denied, 须从 session tool_result 提取内容)
1. `/proj/ddgoa/V0/workdir/gracew/sos_manage_lpddr5/lpddr5/ddgoa/proj_special.sv` — **目标文件** (大, 分块读; cpforce 段在 ~1570-1800 / 3050-3150 区域)
2. ddcpc compress proj_special.sv — **参考模板** (R0路径ENOENT, 用户粘贴 cpforce 代码, 内容在 M126 附近 tool_result)
3. CP_FORCE bind 块 + hdl_msa_error_inject 模块 — **注入内容** (R1, 9713字符, 已抓到首600字符)
4. `/rundata/ddgoa/.../verilog.lpddr5.ddgoa.net1105/patterns/.../cmds_compress/TM_CompDataOut.v`
5. qi3wang `TM_CompDataOut_bk.v` / `TM_Comp_Exp_function_bk.v` (参考)

## 4. 合成计划 (下轮 r536 执行, 必须先交付)
- **archetype**: lpddr5-cpforce-bind-inject-modifier (verification, L1 离线 Python, A档 trace-faithful)
- **核心交付**: 给定 proj_special.sv (含旧 cpforce 段) + CP_FORCE bind 块文本 → 生成新 proj_special.sv (cpforce 段替换为 CP_FORCE bind + hdl_msa_error_inject 模块, 其余逐字保留)
- **可见 A**: proj_special_A.sv (ddgoa.1013 风格, 旧 cpforce 段) + cpforce_bind_A.txt (CP_FORCE bind 块, msax512/left/right csl_num=129, msax320 csl_num=80) + task_brief.md
- **隐藏 B**: proj_special_B.sv (不同 cpforce 旧段结构, 不同模块实例名/msa 尺寸) + cpforce_bind_B.txt (不同 csl_num, e.g. msax256 csl_num=64) + hidden_manifest.json
- **reference**: replace_cpforce.py — 定位 `cpforce`/`CP_FORCE` 区段 (起止标记), 替换为给定 bind 块, 保留区段外内容逐字一致
- **check ≥8 断言** (k_check=k_rationale≥8): a zip valid+文件齐 / b 输出 SV 行数==输入行数-delta+bind行数 / c cpforce 旧段已移除 (旧标记不在) / d CP_FORCE bind 4 个 bind 语句齐全 (msax512/left/right/320) / e csl_num 参数正确 (129×3 + 80) / f hdl_msa_error_inject 模块定义齐全 (端口 WrEn/Csl/Yio0/Yio1) / g 区段外内容逐字一致 (md5 of non-cpforce region) / h subprocess 跑 B exit0 + 产文件 / i 3-seed 确定性 / j 非硬编码 A (A/B csl_num 集合不同) / k `ifdef CP_FORCE ... `endif 结构完整 / l bind 实例名 I_hdl_msa_error_inject 齐全
- **negative**: naive_empty (空壳→d), print_only (只 print→h), hardcoded_A (硬编码 A 的 csl_num→j), core_removed (删 bind 语句→d)
- **取材**: 从 session tool_result 提取 proj_special.sv cpforce 段原文 + CP_FORCE bind 块全文 (M126 区域) 作为 A; 派生 B (改 msa 尺寸/csl_num/实例名)。**关键风险**: proj_special.sv 很大, 须裁剪到 cpforce 段周边 (起止标记内) 做自包含 case, 不带整个 3000+ 行网表。
- **L1 理由**: 真 LPDDR5 仿真不在 .75 sandbox (无 vcs/xrun host), 与 A shard 现有 verification 案例风格一致 (VerilogPatternMerge-001/VpsRegrCfgGen-001 同为 L1)。

## 5. 本轮结论
- eoxs4 = 真实 verilog-dominant produce-task (cpforce 修改 + pattern 生成), **fresh + unledgered + 文件 ALIVE**, 是 r534 strict-A-STRONG 过滤漏掉的高质量候选 (r534 把 verilog 关键词当假阳剔除, 但 eoxs4 verilog:1871 是真 dominant)。
- **纠正 r534 方法论**: r534 strict-A-STRONG 过滤去掉 verilog/rtl/synopsys/tcl/sdc 导致漏检真正 verilog-dominant 的 fresh session。fresh-diff broad-A-domain (含 verilog) 应保留, 用 first-keyword-dominance 而非剔除关键词来判断 A-domain。
- trace 双超阈值 (2.7MB & 628msgs) → 本轮 deepread-only, DEBT:1, 下轮 r536 必须先合成交付 eoxs4 case。
