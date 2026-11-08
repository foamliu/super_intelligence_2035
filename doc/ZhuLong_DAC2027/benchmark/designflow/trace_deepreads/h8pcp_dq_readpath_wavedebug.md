# 深读 h8pcp — DDR5 DQ read-path 波形比对 debug

- **trace**: `1793348917218_h8pcp.messages.json` · jinhaoli@hfeg0pkn004 · mc=156 · 76 msgs (51 user / 25 assistant) · deepseek-v4-flash
- **domain**: waveform（DQ 读数据路径波形比对定位）
- **资产可读性**: `/rundata/drgqx/...` 全私有（Permission denied）→ **B-grade synthesized**（DEBT④）

## 用户意图（原话逐字，仅掩码）
> /rundata/.../debugtt_1019_2/write_pattern_basic.x16_9200/xcelium.shm/xcelium.trn 是理想的波形数据，/rundata/.../jinhaoli/gqx_cp/write_pattern_basic_new/write_pattern_basic.x16_9200/xcelium.shm/xcelium.trn 里 read 的数据 dq_exp[15:0] 和总线读出来的数据 UPDQP[7:0], LPDQPad[7:0] 对不上，请帮忙查找电路里哪里出现了问题

- **任务**：给定 golden（理想）与 actual（出错）两份 xcelium.trn 波形 + 设计网表，定位 **电路中** dq_exp[15:0] 与读总线 UPDQP[7:0]/LPDQPad[7:0] 不一致的根因（哪一级 / 哪个信号）。
- **关键**：用户要的是"电路里哪里出问题"（根因定位），不是简单报 mismatch。

## assistant 工具链（76 msgs）
list_allowed_files（两 run 目录）→ read_files（A_Pattern_Sim.v / Pattern_tasks.v / probe.tcl / A_Compare.rpt / sdf.tcl）→ list_allowed_files（gqx_cp / patterns / netlist）→ read_files（write_pattern_basic.v / xrun.log）→ read_files（ddr5_interface.sv / ddr5_tasks.sv / ddr5_test.sv / ddr5_specdef.sv / ddr5_package.sv / compare_tasks.sv / ddr5_in_house.sv）→ search_codebase（UPDQP|LPDQPad / dq_exp / PDRIVER）→ read_files（netlist / netlist_v1 / netlist_v2）→ read_files（A_Summary.rpt / A_Compare.rpt golden+actual）→ run_approved_command（grep 信号，被 profile 拒绝多次）→ trace 末尾仍在读 ddr5_test.sv / xrun.log，**未给出明确结论**（agent 卡在 shell 工具被禁、只能 read_files）。

## 数据路径（从 SV/网表文件名推断）
dq_exp[15:0]（期望数据）→ pattern buffer → read mux（rd_en 门控）→ strobe 对齐 → pad driver → UPDQP[7:0]（高 8 位）/ LPDQPad[7:0]（低 8 位）。
典型 bug 类：① 门控使能被错误常量禁用（条件性 mismatch，子集 cycle）② 位切片反转（结构性 mismatch，全部 active cycle）③ 选错数据源。

## 合成方案（B-grade）
- **A（可见）**：16-bit dq_exp，UPDQP[7:0]=dq_exp[15:8] / LPDQPad[7:0]=dq_exp[7:0]；门控 rd_en，bug = `fix_disable_b2=1'b1` 在 burst_id==2 时禁用 rd_en_gate → 条件性 mismatch（cycle 2/6/10/14/18）。网表 dq_readpath_A.v 含 culprit 常量 + stage 注释。
- **隐藏 B**：32-bit dq_data，HI_DQ[15:0]/LO_DQ[15:0]；bug = `slice_swap_sel=1'b1` 反转切片 → 结构性 mismatch（全部 read_valid 且两半不等 cycle）。信号名/位宽/bug 类/阶段名/cycle 数全不同（反硬编码）。
- **候选** `dq_waveform_debug.py --golden --actual --netlist --out`：解析 CSV trace + 网表 → 比对 golden/actual → 定位 root_cause_signal + root_cause_kind + failing_stage + first_fail_cycle + mismatch_cycles → diagnosis.json。
- **判分**：check.py 只跑 B（subprocess 候选），≥15 条独立断言（含反硬编码：A 信号名 UPDQP 不得硬编码，B 用 HI_DQ/LO_DQ）。

## 选料
cand_1109.tsv 池枯竭（全被 shard B/D 占）→ .75 跑 summary.tsv awk(mc≥30 D-domain) → 本地 4-ledger 排除 → 363 fresh → 取 h8pcp（jinhaoli mc=156 netlist:302/schematic:76 完美 schematic_netlist/waveform 匹配，trace 实为 waveform 比对 debug）→ claim ledger_D 1364→1365。
