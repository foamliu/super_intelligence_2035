# trace_deepreads/sh8uf_xprop_testmode_r573.md — B档合成记录

## meta
- session: 1789893226302_sh8uf (shanliny @ 10.129.2.10, mc23)
- domain: verification (A shard)
- 旧判定: parked (2026-11-11, "analysis-only/Q&A, 0 write/edit, no deliverable")
- 新判定: 可造 (2026-11-15 候选池重审, debug-Q&A 合法)

## 用户意图（逐字）
U#0: 「这个model在启动了testmode的情况下何时会导致输出结果为x，见timing.vcd中qut_q和log文件，在有正常写和只触发了时钟长度违例的情况下，为什么后续的正常读无法读出结果？」

= **debug 诊断 Q&A**：问"何时 X 传播到输出" + "为什么正常读失败"。
旧 weak 筛子判 analysis-only/Q&A REJECT；新标准 debug-Q&A 合法。

## B档合成决策
- trace 内 assistant 0 write/edit（纯解释），无可复刻的 golden 产物。
- 但**核心 capability 明确**：静态分析 Verilog model → 识别 testmode 下的 X 传播路径。
- r561 SvClockblockAudit (g7hcn) 同型方法论成功：将 SV 静态审计能力固化为 Python 解析器。
- 本 case 固化：x-propagation static diagnosis → Python Verilog parser。
  - 输入：Verilog 模型（含 testmode/rst_n/clk + always blocks）
  - 输出：JSON 诊断报告（no_reset_regs / xprop_outputs / safe_outputs / testmode_gated_paths）
  - 判分：在隐藏 model_B.v 上验证诊断正确性

## 隐藏 B 设计
- model_B.v: DDR read model, 3 个无复位寄存器 (rd_latch_b/addr_pipe_b/parity_calc_b) → testmode 下 X 传播到 rd_data/parity_err/bank_state
- model_A.v: SRAM controller, 2 个无复位寄存器 (hold_b/guard_b) → testmode 下 X 传播到 dout/chk_fail/mode_cnt
- 两模型结构完全不同（module name / 信号名 / 寄存器数量 / 输出宽度全异）

## 判分 14 条断言 (①-⑭)
① zip 含 xprop_diag.py ② 脚本在 model_B 无错产出 JSON ③ module_name 正确 ④ total_regs>=5 ⑤ no_reset_regs 含全部 3 X 源 ⑥ no_reset_regs=3 ⑦ reset_regs 含 4 个 ⑧ xprop_outputs 含 3 个 ⑨ xprop_outputs=3 ⑩ safe_outputs 含 busy+rd_valid ⑪ safe∩xprop=∅ ⑫ testmode_gated_paths>=4+结构正确 ⑬ 3x 确定性 ⑭ 反硬编码(A≠B)

## 自验
- ref selftest 14/14 PASS
- 4/4 negative FAIL (naive_empty→③, print_expected→⑭, core_deleted→④, hardcoded_A→③)
- §4.9 三假提交全 FAIL (空壳/只print/删核心 = naive_empty/print_expected/core_deleted)
- 3x sha256 确定性一致
- jsonl test roundtrip PASS (test field == check.py on disk 8030 bytes)
- k_rationale=14 == k_check=14 >= 8 GATE PASS

## ledger
sh8uf parked → case (EDA-Eval-DesignFlow-XPropTestmodeDiag-001)
