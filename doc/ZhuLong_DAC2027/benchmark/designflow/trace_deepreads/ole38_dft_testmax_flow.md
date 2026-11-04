# Deepread: ole38 — DFT TestMAX demo flow (verification, L2, B档)

## trace
- session: `1793081732674_ole38.messages.json`
- user/host: e0030085 @ hfeg0pkn005
- mc=21, 60 msgs, 141KB
- keywords: `dc_shell:12;synopsys:19;pyaether:14;aether:8;virtuoso:7;netlist:5;cadence:5;pdk:2`
- tools histogram note: summary.tsv tools 列对数字前端工具(vcs/verdi/dc_shell/primetime/formality)不记录，需走 keywords 列严格 df 工具名筛

## 用户意图（逐字原话）
- turn 0: `gvim me a DFT testmax demo`
- 单轮生成型任务：用户要一个 DFT TestMAX 演示项目，无后续修复轮

## assistant 工具链 / 产物
1. list_allowed_files / get_agent_policy_status / skills(eda_agent, ask-eda) / search_codebase / run_commands —— 环境探查
2. editor 写 14 个文件到 `/home/e0030085/Documents/dft_testmax_demo/`:
   - rtl/{adder_top.v(8 位累加器带 scan 端口), add_sub_unit.v(16 位加减), dft_top.v(顶层), tb_dft_top.v(功能+扫描 testbench)}
   - scripts/{dft_compile.tcl(dc_shell DFT Compiler 扫描链插入), atpg.tcl(TetraMAX ATPG), run_all.tcl}
   - run/{run_dft.sh, generate_demo_results.sh(假结果生成), sim_filelist.f}
   - README.md, setup.sh, create_dirs.sh, chmod.sh, cleanup.sh
3. run_approved_command 跑 create_dirs.sh / chmod

## 金标准评估（诚实）
- ✅ 完整 DFT flow 骨架：dft_compile.tcl 含 set_dft_configuration/set_scan_configuration/5 类 set_dft_signal/compile -scan/insert_dft/dft_drc/report_scan_path/create_test_protocol/write verilog；atpg.tcl 含 read_netlist/run_build_model/read_test_protocol/run_drc/set_fault_type/add_faults/create_patterns/write_patterns
- ❌ 硬编码绝对路径 `/home/e0030085/Documents/dft_testmax_demo/...`（不可复用）
- ❌ dft_compile.tcl 用 `elaborate dft_top` 字面量（非参数化）
- ❌ RTL 功能 bug：adder_top `sum_reg <= sum_w` 用旧 a_reg/b_reg，testbench 期望 10+5=15 但首拍得 0（demo 从未真跑 VCS，用 generate_demo_results.sh 造假结果）
- ❌ testbench 扫描测试段不校验值（只 shift in/out 不比对）

## case 合成决策
- 重构为 design_flow：给定 rtl_A（修正功能 bug，sum_reg<=data_a+data_b 当前输入），SUT 交付参数化 DFT flow 5 文件
- L2 真跑 VCS 验证功能(10+5=15)+扫描+bug 注入检测+交叉输入(隐藏 B 异构同端口)
- 隐藏 B = shift_acc+mult_core 异构实现，同 dft_top 端口同功能(led_out=key_in+5)
- feint = 残缺脚本+残缺 tb（TODO + 硬编码路径），引导 SUT 修复

## .75 infra 发现
- VCS: `module load ds/vcs/2023.12-SP2-3`（默认 vcs/R-2020.12 license 池耗尽；ds/ 池可用）
- RTL 无 `timescale + tb 有 → VCS [ITSFM] 错 → 加 `-timescale=1ns/1ps`
- testbench `sys_en=1; @(posedge clk); sys_en=0;` 与 DUT 同沿采样 race → load 丢失 → negedge 驱动 + #1 延迟 deassert 修复

## 选料教训
- BLOCKER③ 应验：mc≥30 fresh viable shard-A 候选枯竭（全 analog/innovus:4 噪声）
- 降级 mc<30，keywords 严格 df 工具(dc_shell/icc2/innovus/primetime 主导计数)筛 → ole38(dc_shell:12) viable
- saz5l(mc=6, e0046913) 纯 Q&A career advice（无工具执行无交付）→ parked
