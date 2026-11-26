# Trace deepread: njt15 (DatatPrintOrderDiag)

- **session**: `1793427492496_njt15` (tongfanl @ hfhds201, dir-based, 254 msgs, 1.38MB, 2026-10-31)
- **domain**: spice_sim (DDR6 DSCQA analogsim WTM004 sim_vector / xrun 调试)
- **shard**: B (spice_char)
- **case**: EDA-Eval-DesignFlow-DatatPrintOrderDiag-001 (A-faithful L1, k=14)

## 选轮 (A-档)
- **U#0 (任务说明轮, 逐字作 prompt)**:
  `/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local/log/stimulus_tongfanl/WTM_fsm_1030/WTM004_block_check_SC1_WPre_4s4t_WPst_4p5_RPre_2s6t_RPst_4p5_MD_OFF_CRC_11_tCH50_2b16g_BL02_12800_SS_DQSELH.X2P6_12800`
  `这个路径中的结果，为什么xrun.log中的DATAT0（3189行）和波形中的数值对不上。`
  `你可以向我提问以保证准确交付。`
  → 提出需求 (问"为什么对不上"), 无根因/修复方向 → 符合 A-档选轮
- U#1 (idx146)「我抽激励的脚本是...为啥UI16~23 的 DQ2 会被 pad 清零？」→ 后续追问, 不入 prompt
- U#2 (idx216)「DQ5的最后几位，CRC注错是随机的吗？」→ 后续追问, 不入 prompt

## 关键工具链
- read_files: 读 WTM004_block_check.v / WTM001_normal_check.v / A_Pattern_Sim.v / A_Compare.rpt / xrun.log / stimulus.vec / ddr6_test.sv / ddr6_tasks.sv / ddr6_model.v / cfg_WTM
- run_approved_command (profile=python-runner): python 探针脚本 probe_access.py 在 /proj 源码树 grep+sed+os.walk 定位代码
- editor: 迭代修改 probe_access.py
- SandBox_MCP_Server__run_code: pyAether 沙箱 (未启动, 弃用)

## 金标准 (assistant 结论)
**DATAT0 和波形都没错 —— 是「打印顺序反序」+「CRC/pad 占位」造成的视觉错位**

### 主因: DATAT 打印顺序与波形时间顺序正好相反
- 实际调用 `patterns/analogsim/WTM/WTM001_normal_check.v:164` 的 `gen_wtm_write_data` (WTM004 里的 `gen_wtm_write_data_004` 未被调用)
- 打包/打印循环 **j 从 23 递减到 0** (WTM001_normal_check.v:713-720):
  ```systemverilog
  for(int j = 23; j >=0 ; j--) begin
      write_data_array[i] = {write_data_array[i], UI_data[j]};  // UI0 最终落在最低 6 位
      print_str = ...UI_data[j]...;                              // 但先打印 UI23
  end
  ```
- 驱动侧 `load_fifo` (ddr6_tasks.sv:2854-2857) `dq_fifo[dq_index+i] = val[i*6 +: 6]`, FIFO 槽位随时间递增 → **UI0 最先上引脚**
- → **DATAT0={...} 从左到右是 UI23→UI0, 波形从左到右是 UI0→UI23, 整个序列是镜像关系**
- Write0 波形期望 (时间序 UI0→UI23): `26 13 1b 1c 28 2e 22 24 17 2c 26 2c 17 13 24 28`

### 次因: 写 CRC 使能, UI16~23 的 DQ5 被 CRC 码字占用, DQ2 是 pad 位被清零
- MR1 写 OP_CRC_11=8'b0000_1100 → bit3=1 → MR1_wr_crc_en=1 (CRC_8_D64 模式)
- ddr6_test.sv:1252-1261 (X2P6+MD_OFF): randcase ALL_ZERO(weight 100) → `for(int i=0;i<8;i++) dq[140-6*i]='b0` (UI23~UI16 DQ2 清零)
- ddr6_test.sv:1496-1500 (X2P6+MD_OFF): `for(int i=0;i<8;i++) dq[143-6*i]=crc_dq[7-i]` (UI23~UI16 DQ5 ← CRC-8 码字)

### 验证
- Python 逐位复算两组 DATAT0 与日志 3189/3315 行**完全一致** (连 Generated write data hex 都一致)
- 用 stimulus.vec (2.5MB, 11256 行) 逐 UI 验证 UI0~23 全 PASS

## 合成 (case 资产)
- 通用化 `diag_datat_print_order.py <wtm_file> <tasks_file> -o out.json`:
  - 解析 WTM .v 的 DATAT 打包/打印 for 循环 (var/start/end/op/step/direction/first_ui/ui_count)
  - 解析 tasks .sv 的 loaddq_fifo/load_fifo for 循环 + val[...+:...] 切片 (direction/first_ui/slice_expr)
  - 比较 print_first_ui vs pin_first_ui → reversed / matched
- A = A_wtm (WTM001_normal_check.v 真实节选 708-721 + ddr6_tasks.sv 真实节选 876-889/2646-2857) → 期望 reversed (print_first_ui=23, pin_first_ui=0)
- hidden B = B_wtm (WTM_B_check.v 合成: 打印循环 `for(int j=0;j<16;j++)` 递增 16 UI/8-bit; ddr6_tasks_B.sv 递增 FIFO) → 双递增 → matched (与 A 反序结构相反, 挡硬编码)
- 判分 14 断言 (a-n): 含交叉输入守卫 + A-only 泄漏闸门 + 3 次幂等 sha256

## 自验
- ref PASS 14/14 ✓
- 4 negative (naive_hardcode_a FAIL e / print_expected_b FAIL l / empty_shell FAIL a / core_deleted FAIL i) 全 FAIL distinct ✓
- §4.9 三假 (空壳 FAIL a / 打印期望 FAIL l / 删核心 FAIL i) 全 FAIL ✓
- 断言闸门 k_rationale=14 == k_check=14 ≥ 8 ✓
- jsonl test==disk check.py roundtrip sha 14f4c9e9cca6f49b9a1aedabbbe91909e45d80da953dd92f628200177f842bec ✓
- 追加 EDA-Eval-DesignFlow_B.jsonl (155→156) + mark ledger (157→158 covered, spice_sim 121→122)
