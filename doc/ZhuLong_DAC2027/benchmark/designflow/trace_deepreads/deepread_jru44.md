# 深读笔记: 1788853679600_jru44 (lorikx@hfeg0pkn001, mc=39, rtl:668/analog:72)

## trace 来源
- session: `/home/lorikx/.cline/data/sessions/1788853679600_jru44/1788853679600_jru44.messages.json` (337KB, 27 msgs)
- 域: digital (rtl:668 verilog:2 systemverilog:2 synthesis:3)
- 工程路径: `/proj/lagat/V0_digital/workdir/lorikx/project/sos2` (SOS 版本控制工作区)

## 对话流 (1 真实 user 轮)
- USER#0 (唯一 user_input, mode=act): **"分析这个项目，给我介绍一下，分为哪些"** — clean 需求 (A-faithful rule2 OK: 提出目标, 未给根因/修复)
- AST#1-23: assistant 用 list_allowed_files 探索目录 (units/flow/tools/verification.SVM), read_files 读 soc_chip.f + soc_chip_syn.filelist + bank_map.sv; run_commands 被 policy 禁
- AST#26 (gold, 7982 chars): 7 节完整项目结构分析

## gold (AST#26) 结构
1. **项目概述**: sos2 = lagat 项目下 DRAM Tester Chip 数字前端; 顶层 `dram_tester_chip` (units/soc_chip/rtl/dram_tester_chip.sv, 2020 行); 22nm ULL (tcbn22ullbwp40p140, LVT/ULVT); SystemVerilog+Verilog 混合; SOS Release 7.05.p4; 功能=对 DRAM Die(DIE0/DIE1) 高速数据收发测试 (DQ/DQS/CA/CS/CK), 支持 ZQ 校准/眼图搜索/PRBS-CRC-ECC 校验
2. **顶层目录 4 分**: units/ (RTL IP) + flow/ (EDA 流程) + tools/ (脚本工具) + verification.SVM/ (验证环境); 另有 SOS 日志 sos.log/update_summary.out/diff.out/history.out
3. **units/ 11 子单元** (filelist-confirmed 10): soc_chip(顶层集成) / cgu(时钟) / rgu(复位) / jtag(调试) / tx_top(TX通路) / rx_top(RX通路) / crc(校验) / ecc(纠错) / slice_wrapper(DRAM slice 包装) / common(通用库) / model(行为模型); 每单元含 doc/rtl/sim 子目录约定
4. **flow/** 5 阶段: syn(综合, soc_chip_syn.filelist, SDC, setup) / spyglass(cdc/lint/rdc 静态检查) / dft(扫描链) / fm(形式验证) / static_check(静态检查)
5. **tools/** 5 工具: addRtlHeader / csr_gen(CSR RTL 自动生成) / gen_quick_timing_model(快速时序模型) / rtlcheck / rtldev(autobbox/autoinst)
6. **verification.SVM/** + 芯片级 UVM 风格 testbench (units/soc_chip/tester_chip_tb/)
7. **芯片架构小结**: 时钟域(REF_CLK→CGU→PLL1/PLL2) / 复位域(RGU→soc_rst_top) / 配置访问(JTAG→jtag_top AXI-Lite→mem_cdc_mux 5 slave / slv_mux 7 slave) / 数据通路(TX_top→DRAM Die→RX_top) / 校验(CRC+ECC) / 地址映射(CGU 0x2000_0000, SOC 0x4000_0000 ...)

## 真实文件证据 (经 read_files tool_results)
- **soc_chip_syn.filelist** (11 行): `+define+LSYN` + 10 个 `-F $PROJECT_HOME/units/<u>/rtl/<u>.f` (crc/ecc/common/rx_top/tx_top/jtag/cgu/rgu/slice_wrapper/soc_chip)
- **soc_chip.f** (22 行): +incdir + 20 个 .sv/.v 文件 (dram_tester_chip.sv 是顶层, bank_map.sv, top_logic.sv, mem_cdc_mux.sv, slv_mux.sv, soc_rst_top.sv, soc_top_reg.sv, gpio_control.sv, gpio_reg.sv, pll2_csr.sv, pll1_reg.sv, pin_assign.sv, ft_loopback.sv, tmode_dec.v, analog_io_wrap.sv, array_1dto2d/2dto1d/2dto3d/3dto2d.sv)
- **bank_map.sv** (真实模块): `module bank_map #(parameter WIDTH_RAT=4, FUBK_DAT=30, ...)`, 把内部 write/read bank 数据映射到物理 CA/CS/CK/DQ (706~714 bank 通道)

## 资产可取性
- /proj/lagat/.../sos2 与 /home/lorikx/... 均 e0031982 Permission denied (真实工程不可取)
- 经 trace tool_results (list_allowed_files 真实目录树 + read_files 真实 filelist/bank_map.sv) + gold (AST#26 真实模块名/单元名/文件名) faithful 重建 sos2 工程

## 合成 case
- **A (faithful sos2)**: 11 units (真实名) + 5 flow stages + 5 tools + verification.SVM + soc_chip_syn.filelist (10 -F) + soc_chip.f (22 行) + 22nm ULL (tcbn22ullbwp40p140) + top=dram_tester_chip
- **B (synthesized nic_chip, 隐藏)**: 9 units (mac_engine/pcs_layer/serdes_lane/arbiter/crc32/dma_engine/regfile/xbar/top_integration, 与 A 零重叠) + 6 flow stages (syn/lint/cdc/dft/fm/sta, lint/cdc 顶级非 spyglass 子目录) + 4 tools (reggen/rtlheader/waiver_collect/timing_model_gen) + verification/ + 28nm HVT (tcbn28nephvt) + top=nic_top
- **候选** = gen_soc_project_report.py (通用): 扫任意 SoC 项目根 → 结构化 JSON (project_name/top_module[模块定义-例化关系检测]/tech_node[std-cell lib token 检测]/hdl/directory_division/units/flow_stages/tools/filelist_path/filelist_units/arch_summary/summary)
- **check.py** 16 conds (a-p): a 无禁用 import b py_compile c [B] exit0+合法JSON+12键 d [B] project_name e [B] top_module f [B] tech含28nm g [B] hdl==sv+v mix h [B] directory_division覆盖units/flow/tools/verification i [B] units覆盖9个精确一致 j [B] 每unit role非空+rtl_file k [B] flow_stages覆盖6个 l [B] tools覆盖4个 m [B] filelist_path n [B] filelist_units集合一致 o [A反硬编] sos2/dram_tester_chip p [B'确定性]
- **自验全绿**: ref PASS 16/16 + 5 negs 全 FAIL distinct {a,o,c,d,e} + §4.9 三假(empty_shell/print_expected/core_deleted)全FAIL + negative_selftest PASS + jsonl test roundtrip PASS
- **k 闸门**: k_rationale=k_check=16≥8 ✓ (16 个 ①-⑯ 断言标记)
