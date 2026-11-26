# Deepread: vagnh (tabtao@hfeg0pkn004, mc29) — DC synthesis log error diagnosis

**Session**: `1793861357108_vagnh.messages.json` (hfeg0pkn004, /home/tabtao/.cline/data/sessions/1793861357108_vagnh/)
**Size**: 275KB, 47 msgs (~24 user turns incl. tool_results, 8 assistant reasoning+action turns)
**User**: tabtao (new — first trace from this user in shard A; diversity)
**Keywords**: netlist:142;rtl:72;icc2:49;verilog:46;synthesis:31;floorplan:22;pdk:15;synopsys:10 (digi 291 vs ana 15 — digital-dominant)
**Domain**: pnr_signoff → case filed as **digital** (DC synthesis flow; dc_shell/compile_ultra/write_qor_data; icc2 mention is DC NXT ICC2-link option, not PnR). Reassessed: this is a DC synthesis log-diagnosis trace → digital.

## Conversation flow (2 user task turns)

### USER#0 (msg#0) — A-faithful 选轮 ✓ (干净需求, rule2 未违反)
> `@dc.tcl @Makefile @common_setup.tcl @dc.log 调用上述路径中的makefile make dc_syn跑flow的时候发现上述路径中的dc.log中1821行出现的Error信息，请问下如何解决`

用户只描述症状（dc.log 第 1821 行 Error）+ 提问如何解决。**未给根因、未给修复** → A-faithful rule2 通过。

**Gold = msg#26** (assistant 完整诊断):
1. **结论**: RPT-181 为**良性（benign）**错误，`make dc_syn` **已成功跑完**：
   - `flow_cfreq_ctrl/results/syn.done` 已生成（make 最后 `touch`）
   - `cfreq_ctrl.mapped.v`(35KB)/`.mapped.ddc`/`.first_compile.ddc` 都已写出
   - dc.log 执行到 `exit` + `Thank you...`（2626~2633 行），`dcnxt_shell` 正常退出
2. **错误来源**: dc.tcl 的 `write_qor_data`（764/766 行 compile, 897/899 行 compile_incremental）内部依次调用子报表，其中 `report_threshold_voltage_groups` 抛 RPT-181:
   ```
   Information: Running write_qor_data ... report 'report_threshold_voltage_groups'  (RPT-190)
   Error: Errors occurred during write_qor_data while running the 'report_threshold_voltage_groups' report.  (RPT-181)
   ```
   报错后不中断，继续跑 report_qor/report_constraints/report_clock_gating/performance。
3. **根因**: `report_threshold_voltage_groups` 需按 cell 的 `threshold_voltage_group` 属性分组，但标准单元库 `DBCP51H180L6W25T5_BASE_*_tt_v0p75_25c.db`(LVT/SVT/ULVT) + `_MB_*` **未在 cell 上填该属性**。证据：
   - compile 反复出现 `>> lvt 0.00%, ulvt 0.00%, undefined 100.00%`
   - RM 单独报表 `reports/cfreq_ctrl.mapped.threshold.voltage.group.rpt`: `undefined 320 (93.02%), lvt 24 (6.98%)`（IP/MB 库单元带属性，Bulk 库不带）
   - **库/PDK 侧数据问题**，非约束/RTL 问题
4. **解决方案**: ①忽略（推荐，QoR 子报表失败不影响网表）②根治改库（让 PDK 补 `threshold_voltage_group` 属性）③流程内 `catch` 包 `write_qor_data` 4 处（764/766/897/899）

### USER#27 (msg#27) — 第二个任务轮（不同 flow，致命错误，**B 档合成灵感**）
> `@dc.log @Makefile 调用上述路径中的Makefile make dc_syn跑flow的时候发现上述路径中的dc.log中22294行出现的Error信息，请问下如何解决`

不同 flow: `syn_SramEDABistGrp2/flow_DESIGN`。**Gold = msg#34/43**:
- Error: `The power pin VDD on the cell u_CLKA00_mux/u_ckmux is unconnected. (UPF-581)` (line 22294)
- `PG netlist mode enabled` (UPF-711) — 因 SRAM macro 在 Verilog 有显式 PG pin 连接
- `Warning: PG netlist to UPF conversion is not done, as there is no UPF data. (UPF-440)` — UPF_MODE=none
- `check_mv_design -power_nets` 返回 false → `RM-error: One or more supply nets are missing a defined voltage.` → `This script will now exit.` → `exit 1`
- **流程失败（hard failure）**，与 USER#0 的良性错误形成鲜明对比
- 根因: PG-aware（SRAM macro 显式 PG pin）+ 非 PG（普通 mapped cell / clock mux 无 PG）混合，在非 UPF 流程下综合

## Case 设计决策

- **A-faithful**: prompt = USER#0 逐字原文；gold = msg#26 诊断
- **真实附件不可达**: e0031982 无 tabtao 权限（`Permission denied` on /proj/lagat/V0_digital/workdir/tabtao/syn_bk1/）→ 用 trace gold 文本（msg#26 引用了实际 log 内容: RPT-181/undefined 100%/syn.done/exit+Thank you/库名）重建代表性 `dc.log`/`dc.tcl`/`Makefile`/`common_setup.tcl`（r200 ckulq fm.tcl 同样手法）
- **交付形态** = `gen_dc_log_diagnosis.py`（通用 DC 日志错误诊断器，输出结构化 JSON: errors/code/line/trigger + flow_completed + is_fatal + root_cause_category + evidence + recommendation）—— 让隐藏 B 可泛化判分，而非静态文本
- **隐藏 B** = 合成**致命** UPF-581 PG 失败（AxiDspGrp3，u_dpath/mux_pd VDD 未连，check_mv_design 失败，RM exit 1，无 syn.done/无 mapped.v）—— 与 A 的良性 RPT-181 形成致命 vs 良性对比（灵感取自 USER#27 同 trace 的真实致命模式，但 design/cell/supply 全部合成不同）
- **b2** = b1 随机化变体（u_clkdiv/div_ck/VDD_IO，块序打乱）—— 验顺序无关 + 通用化
- **L2-static**: trace 是真实 DC 综合流程（dc_shell/compile_ultra/write_qor_data/check_mv_design），case 为静态日志解析（subprocess 真跑候选，无 EDA 工具真跑）
- **判分 15 conds (a-o)**: B 致命性 + UPF-581 + pg_connection 根因 + PG 修复建议 + 反硬编守卫(A 须诊断 RPT-181 良性 missing_cell_property，与 B 的 is_fatal 相反) + 源码无 A/B 内容字面量 + B' 结构一致 + line 整数 + error_count 整数

## 自验
- ref PASS 15/15（reference_submit.zip 本地独立目录）
- 5 negs 全 FAIL，3 distinct first-fail {c, d, k}：naive_empty→c / naive_always_ok→d / core_deleted→d / naive_always_fatal→k / fake_print_expected→k
- §4.9 三假: naive_empty(空壳)→c / fake_print_expected(print期望)→k / core_deleted(删核心)→d 全 FAIL
- negative_selftest PASS (ALL_FAIL True, REF_PASS True, DISTINCT_CONDS=3≥2)
- k_rationale=k_check=15≥8 闸门 PASS
