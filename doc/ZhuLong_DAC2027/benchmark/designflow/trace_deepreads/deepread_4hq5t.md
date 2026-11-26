# Deepread: 4hq5t (shanliny@hfeg0pkn001, mc72)

- session: /home/shanliny/.cline/data/sessions/1791946331811_4hq5t/ (6.2MB, 183 msgs, dict format with messages list)
- keywords: systemverilog:1240, verilog:370, rtl:26, synthesis:2 (digi=1638, ana=22, pure digital)
- domain: verification (UVM-like SV testbench for SRAM with redundancy CXN4HC1PS8X16M1B1C1R1W1BW1RE1_FS.v)

## 对话流（user 轮）
- #0 分享 UVM-like 验证程序（11 SV 文件，driver/env/interface/monitor/package/ref_model/strategy_base/strategy_ext/top/transaction_base/transaction_ext）"理解结构"
- #2 分享 makefile + file.list "面向用户的调度接口"
- #4 分享 DUT (CXN4HC1PS8X16M1B1C1R1W1BW1RE1_FS.v) "待测 dut"
- #6 **核心问题（Bug 1, build_readwrite）**："make DEPTH=8 DATA_WIDTH=16 MUX=1 build_readwrite vcheck timing_validation timing_debug all > log... timing.vcd 中 Q_REF 和 dut_q 全为 x... 你帮我看看我的 vec 验证程序错在哪"
- #70 "把你的修改2详细一点，直接放完整代码"
- #74 **本轮取（Bug 2, build_rand）**："build_readwrite、bitwrite、redundancy_all_states确实被你修复了，但我现在用 make DEPTH=8 DATA_WIDTH=16 MUX=1 build_rand vcheck timing_debug all > log 命令，还是要报不少错，这是新的log和timing.vcd，你看看错误在哪，怎么修复"
- #86 "你错了，绝对另有病因，仔细检查"
- #126 "在random模式下我怀疑是monitor的对比有问题... error_flag就是变为1了"
- #170-182 反复要求"让monitor在输出稳定的时候再对比结果"（Bug 3, CR desync + monitor glitch）

## 三个 Bug（assistant 诊断）
1. **Bug 1 (build_readwrite, all-x)**：drive_transaction TIMING 路径 rdata_valid 驱动时序竞争 + init_driver 缺 9 信号初始化 → scoreboard 比对 0，Q_REF/dut_q 全 x。修复：negedge 先驱动 + 补全 init。用户 #74 确认修复。
2. **Bug 2 (build_rand, 155 mismatch)**：TIMING 路径 `vif_tm.test <= op.test`，事务约束 test=='1（write/bitwrite/CR），execute() 设 test<=1'b0 但 TIMING 路径不调 execute → DUT 进 TEST 模式，Q 时序 posedge→negedge，monitor 采样错 → 155 DATA_MISMATCH。修复：强制 `vif_tm.test <= 1'b0`。**本轮 case 取此 Bug。**
3. **Bug 3 (random monitor, error_flag)**：CR 信号 crs0e/crs1e 从随机事务字段驱动 → ref_model 与 DUT CR 状态不同步 + 输出跳变瞬间 monitor 误比。修复：driver 维护 CR 全局状态 + monitor 稳定时再比。trace 末尾未闭环（#182 用户重问，无 assistant 最终答复）。

## 资产保全情况
- driver.sv：uploads 已是全修复版（Oct 13 19:01）。#74 时刻（Bug1 修/Bug2 在）= 当前版回退 test 修复（test<=op.test，去 3 注释）→ 本轮 A 资产用此重建（来自 messages.json editor old_text 校验）。
- log：uploads 是 build_rand log（408 cmp/253 pass/155 fail/RANDOM/FAIL），即 #74 的真实 log。**A 资产用此真实 log（trim 保留关键行）。**
- transaction_ext.sv / strategy_base.sv：真实原文（含 test=='1 约束 + execute test<=1'b0 覆盖 + strategy execute 调度）。

## 本轮 case
EDA-Eval-DesignFlow-VecRandfailDiagnose-001 (verification, A档 faithful, L1-static, 15 conds a-o)
- 任务说明 = #74 逐字原文
- 交付 = diagnose_vec_randfail.py（读 driver.sv + transaction_ext.sv + log → diagnosis.json 结构化根因）
- A 资产 = 重建 #74 时刻 driver.sv(test<=op.test) + 真实 transaction_ext.sv + 真实 strategy_base.sv + 真实 build_rand log(trim)
- 隐藏 B = driver.sv(test<=op.test 泄漏 + init 缺 byp) + 同 transaction_ext + 不同 log(600/220/380) → 测脚本泛化（动态读 log + init 分析）
- check 15 conds: leak 检测 + 约束证据 + execute 覆盖证据 + log 6 统计 + init_missing + fix 目标 + root_cause 关键词 + 反硬编(A 字面量 408/155/253)
- 自验全绿：REF PASS 15/15 + 4 negs FAIL distinct{c,d,h} + §4.9 三假全 FAIL + negative_selftest PASS(DISTINCT=3≥2)
- k=15 闸门 PASS(k_rationale=k_check=15≥8)，test 字段 sha8 1c0e5cce 与 disk 同步
