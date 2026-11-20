# 深读笔记：1791715561176_7kad5 — e0014566 @ hfeg0plg58 — DDR4 CVPS TB 框架生成

## trace 元数据
- user: e0014566 · host: hfeg0plg58 · session: 1791715561176_7kad5.messages.json
- size: 66KB · msgs: 20 · agent: lead · model: glm-5.2
- match_count: 13 · domain: digital · 产出目录: `/home/e0014566/Desktop/ddr4_tb_framework/`

## USER 轮（verbatim）
- **USER#0**: `可以帮我生成一段rtl的代码么`
- **ask_question 选择**: 用户在 agent 给出的选项中选 **"TB 框架代码（top.sv / Testbench 组件，面向 DRAM 验证）"**
- 后续 USER 轮: 极少，主要是 agent 主动产出的多文件 editor 创建

## A-档 CLEAN 判定
- USER#0 = 纯需求轮（"生成一段 rtl 代码"），未给方案/根因 ✓
- ask_question 选择 = 需求细化（选 TB 框架方向），是 REQUIREMENT REFINEMENT 非 fix-plan ✓
- 全 7 文件均在 session 内通过 editor tool_use 的 new_text 创建（无外部依赖/无远端产物）✓
- **A档自包含**：完整产物在 session 内创建，可直接合成 case ✓

## trace assistant 工具链 / 产物
agent 用 editor tool_use 连续创建 7 个 SystemVerilog/Verilog 文件（new_text verbatim 提取即为 reference_solution）：

| # | 文件 | 大小 | 核心内容 |
|---|------|------|----------|
| 1 | ddr4_package.sv | 2865B | package ddr4_package: DEV_WIDTH(x16/x8/x4)→DQ_WIDTH/DQS_WIDTH; BANK/BG/ROW/COL_WIDTH localparam; cmd_t enum 13 opcode(CMD_DES..CMD_SRX, 4-bit CS_n/RAS_n/CAS_n/WE_n 编码); speed_bin_t enum 4 档(TCK_3000/2667/2500/2000) |
| 2 | ddr4_interface.sv | 2071B | interface ddr4_if #(DQ=16): ck/ck_n/cs_n/ras_n/cas_n/we_n/act_n/bg/ba/a/a10/dq/dqs_t/dqs_c/dm_n; 3 modport(pg=driver/dut=input/mon=observe); 默认 ck 时钟 always #(TCK_2500/2) |
| 3 | timing_table.sv | 2479B | package ddr4_timing: ddr4_timing_t struct packed 12 字段(tRCD/tRP/tRAS/tRC/tWR/tRFC/tRRD/tRTP/tRTW/tWTR/tCCD/tREFI); get_timing(speed_bin_t) 按 3 档 case 返回; wait_tck(ref ck, n) repeat(n)@(negedge ck) |
| 4 | ddr4_tasks.sv | 4218B | 全局 CUR_T/CUR_BIN; 7 task automatic 全 negedge ck 对齐: set_speed_bin/issue_cmd(ref virtual ddr4_if.pg)/act/pre/mrs/ref_auto/sre_enter/srx_exit; act_wr_rd_seq 组合序列 |
| 5 | ddr4_model.sv | 2064B | module ddr4_external_model #(DQ=16)(ddr4_if.dut bus): expect_dq 关联数组; mismatch_count; init_model task; check_dq function(got≠exp→mismatch++); poke_expect task |
| 6 | top.sv | 2866B | module top: ck_t/ck_c/rst_n 时钟生成(always #(TCK_2500/2)); ddr4_if u_bus 例化; ddr4_external_model u_model 例化; initial init_model→set_speed_bin→run_pattern→PASS/FAIL 收敛→$finish |
| 7 | Pattern_sim.v | 1560B | task automatic run_pattern: SMOKE 序列 mrs(MR2,0x400)→act(bg0/ba0/row0x0123)+wait_tck(tRCD)→pre+wait_tck(tRP)→ref_auto+wait_tck(tRFC)→sre_enter+wait→srx_exit; run_pattern_seeded(seed) 分片占位 |

## 合成决策
- **archetype**: ddr4-tb-framework-svgen (digital, L1, A档自包含)
- **case_id**: EDA-Eval-DesignFlow-DDR4TbFramework-001
- **check.py 风格**: 结构性验证(同 CPU8bitVerilog-001)，无需 SV 仿真器
- **15 条独立断言** (k_check=k_rationale=15≥8): ①zip+7文件 ②package+cmd_t≥10 opcode ③width localparam+speed_bin_t ④interface+3 modport ⑤cmd/DQ/DQS 信号 ⑥timing_t struct≥8字段+get_timing ⑦wait_tck+negedge ck ⑧5 task(set_speed_bin/issue_cmd/act/pre/mrs) ⑨3 task(ref_auto/sre_enter/srx_exit) ⑩negedge ck 对齐 ⑪module+mismatch_count+check_dq ⑫init_model+poke_expect ⑬top 例化 ddr4_if+model ⑭时钟生成+run_pattern 调用 ⑮Pattern_sim run_pattern 含 MRS+ACT+PRE+REF+SRE/SRX
- **self-verify**: reference submit.zip(7文件)→PASS 15/15 ✓; 退化提交回归 3/3 全 FAIL(empty→[a], print-only→[b], core-removed→[b]) ✓
- **hidden/negative dirs**: 本案为结构性验证(同 r550 CPU8bitVerilog-001)，不设 hidden/ 与 negative/ 持久目录(eval driver 对缺失 graceful)；退化回归作 self-verify 已落

## claim + mark
- trace_ledger_A.tsv: 7kad5 claimed(r550 轮 578→579) → marked case/EDA-Eval-DesignFlow-DDR4TbFramework-001(r551)
- A.jsonl: 291→292
- ledger cases: 288→289
