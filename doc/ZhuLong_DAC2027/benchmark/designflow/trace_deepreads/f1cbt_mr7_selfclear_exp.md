# f1cbt deepread — MrSelfClearExpDiag (MR7 OP2 ZQ Reset exp-value diagnosis)

## trace
- session: `1791961682094_f1cbt` (dir-based, 33 msgs, 224KB)
- user: tongfanl @ hfhds201
- model: glm-5.3-flash
- cwd: /home/tongfanl/.cline/skills/eda_agent/tcl
- started: 2026-10-14T07:08:02Z, ended: 2026-10-15T09:03:41Z (interactive, completed)
- prompt (U#0 verbatim, 提出需求 no root-cause/fix → A-faithful CLEAN ✓):
  ```
  /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local
  帮我看下，在Load_Mode MR7 的 OP2后，一段时间后该位的exp值是什么值？
  ```

## assistant tool chain (33 msgs)
- M#1: skills(eda_agent) + get_agent_policy_status → route to tcl sub-skill
- M#4: list_allowed_files(/proj/dscqa/.../sim_vector) + read SKILL.md
- M#7: list_allowed_files(vecgen_local dir, depth 2) → found ddr6_test.sv / ddr6_specdef.sv / ddr6_package.sv / ddr6_genvector.sv / ddr6_tasks.sv / timing_load.sv (symlinks)
- M#9: search_codebase(MR7/Load_Mode/OP2) + read_files(ddr6_test.sv 1-200, ddr6_specdef.sv 1-200)
- M#12: read existing grep_mr7_psd.py / grep_mr7_psd2.py + specdef MR7 region
- M#14: run_approved_command(python-runner, grep_mr7_psd.py / grep_mr7_psd2.py) → MRSetting occurrences
- M#17: read_files(ddr6_test.sv 2500-2575, ddr6_specdef.sv 283-315) + search(tZQ/ZQRESET/MA_zq_rst/OP_zq_rst) → found self-clear block
- M#20-30: editor + run_approved_command(mr7_zq_exp.py) 3 iterations → MRSetting task body / MRSettingDirect / functional_mode_enable callers / tZQ timing params
- M#32: **gold-standard conclusion**

## gold standard (M#32 verbatim conclusion)
**MR7 的 OP[2] 是 ZQ Reset 位（自清零位）。在 Load_Mode（MRW）MR7 OP2=1 发出之后，无论过多久（包括等满 tZQRESET 之后），该位的期望值 exp 都是 0。**

也就是说：写 1 触发 ZQ Reset 后，该位会自动清零；之后任何时刻（MRR 回读 MR7 时）OP2 的期望值都是 **0**。同时 **OP[3]（ZQ Stop）也会被这次 ZQ Reset 强制清成 0**。

### 代码证据
1. **MR7 OP2 定义** — `ddr6_specdef.sv:297-301` / `ddr6_package.sv:487-491`:
   ```systemverilog
   //7  (R/W) - DIRECT
   // ZQ Reset, OP[2]
   parameter bit[MODEMA_BITS-1:0] MA_zq_rst  = 7;
   parameter bit[MODEOP_BITS-1:0] OP_zq_rst_BITS = 8'b0000_0100;  // OP[2]
   parameter bit[MODEOP_BITS-1:0] OP_zq_rst_En   = 8'b0000_0100;
   parameter bit[MODEOP_BITS-1:0] OP_zq_rst_Dis  = 8'b0000_0000;
   ```
   MR7 字段：OP[0]=ZQ Update Flag(RO)、OP[1]=ZQ Initiator(RO)、**OP[2]=ZQ Reset(RW)**、OP[3]=ZQ Stop(RW)、OP[6:4]=ZQ Interval。

2. **Testbench 自清零建模** — `ddr6_test.sv:2541-2546`（`functional_mode_enable` 任务内）:
   ```systemverilog
   // MR7 zq_rst will self clear, and zq_stop will be set 0 by
   // zq_rst.
   if(ma==MA_zq_rst & mrwenable & ((op_int&OP_zq_rst_BITS)==OP_zq_rst_En)) begin
       MRSetting(.ma(MA_zq_rst),  .op(OP_zq_rst_Dis),  .op_mark(OP_zq_rst_BITS));   // OP2 -> 0
       MRSetting(.ma(MA_zq_stop), .op(OP_zq_stop_Dis), .op_mark(OP_zq_stop_BITS));  // OP3 -> 0
   end
   ```

3. **调用时序** — MRW 流程：`ddr6_test.sv:2854` 先按命令写入 OP2=1，随后 `ddr6_test.sv:2893` 调 `functional_mode_enable`；`MRSettingDirect`（`timing_load.sv:2313-2323`）是阻塞赋值、无 `#delay` 地更新 `ShareDRIVER.mr_direct[7]` 和 `MR7_zq_rst`。所以从该 MRW 完成的时刻起，模型里 OP2 就已经是 0，之后 MRR 比对的期望值恒为 0。

4. **时序参数** — `timing_load.sv:1224`：`tZQRESET_min = max(50ns, 3×tCK)`。TB 不会在 tZQRESET 期间保持 OP2=1——写入后立即按 0 作为期望。

## 合成 (case EDA-Eval-DesignFlow-MrSelfClearExpDiag-001)
- **通用化** `diag.py`：解析 specdef 的 `MA_<name>=<int>` / `OP_<name>_BITS|_En|_Dis=8'b...` 参数定义 + test.sv 的自清零 if-block 模式 `if(ma==MA_<x> & mrwenable & ((op_int&OP_<x>_BITS)==OP_<x>_En)) begin MRSetting(.ma(MA_<x>),.op(OP_<x>_Dis),...); MRSetting(.ma(MA_<y>),.op(OP_<y>_Dis),...); end` + timing_load.sv 的 MRSettingDirect 阻塞赋值确认。输出 JSON `{self_clear_bits:[{mr_ma, mr_index, op_bit, op_bits_value, trigger_en_value, cleared_to_value, self_clearing, exp_value_after, side_effects:[{target_ma, target_op_set_to}], evidence:{self_clear_block_file, mrsetting_direct_blocking}}]}`。
- **A**（真实 trace-time 代码节选）：A_specdef.sv（MR7 ZQ Reset/Stop/Interval 定义 + decoy MR1 wr_crc_error_status / MR4 rd_preamble）+ A_test.sv（functional_mode_enable 自清零块 + decoy trigger_wr_crc_error_status / set_rd_preamble 常规 MRW）+ A_timing_load.sv（MRSetting + MRSettingDirect 阻塞赋值）。
- **hidden B**（合成，结构不同）：MR12 cal_rst（OP[5] 非 OP[2]）自清零，副作用清 cal_latch OP[6]（非 zq_stop OP[3]），不同二进制字面量 `8'b0010_0000` / `8'b0100_0000`，不同字段名；decoy MR3 vref_error_status / MR9 gear_ratio。挡硬编码。
- **判分** 18 断言 (a-r)：含交叉输入守卫（diag.py 在 A 上 mr_index=7/op_bit=2 证泛化，o）+ A-only 标记未泄漏（p）+ 阻塞赋值确认（q）+ 3 次幂等 sha256（r）。
- **自验**：ref PASS 18/18 ✓ + 6 negative 全 FAIL distinct（core_deleted→c / empty_shell→b / naive_hardcode_a→d / naive_hardcode_b→o / print_expected→b / wrong_pattern→c）✓ + NEG_RC=0 ✓ + §4.9 三假（空壳→b / 打印期望→b / 删核心→c）全 FAIL ✓ + 断言闸门 k_rationale=18==k_check=18≥8 ✓ + jsonl test==disk roundtrip ✓ → 追加 EDA-Eval-DesignFlow_B.jsonl(163→164) + mark ledger。
