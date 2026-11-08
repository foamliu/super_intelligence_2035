# 深读笔记 · woanw · SRAM CD-mode sim FAIL FSDB 探针诊断

- **trace_source**: user=lorikx, host=hfeg0pkn001 (10.129.2.10), session_file=1793169357173_woanw.messages.json, match_count=108
- **_msgs_: 73（1 个 user 轮 + 72 assistant/tool_result）· 文件 576KB · 2026-10-28
- **域名判定**: waveform（FSDB 波形读取 + 信号探针诊断；waveview:144 关键词）；兼涉 schematic_netlist（RTL/TB 静态分析）

## 用户原始意图（唯一 user 轮，逐字）
> 请检查最新一次的仿真结果FAIL原因并修复

## 真实任务脉络
1. **工作区**: `/home/lorikx/1prfbv_refer/v_model/CXMT_SPSRAM_1028_v21/`（SPSRAM 1024x144 verilog model v21）
2. **最新 run**: `sim/sim_logs/run__1024x144_cd_20261028_140504.log`（CD = CENTER_DECODE=1 模式）
3. **FAIL 定位**: Test 21h · TEST write-through · 时间 1363000 · 期望 `Q=E7` · 实际 `Q=x`（仅 1 个错误）
4. **RTL/TB**: `rtl/sp_sram.v`（3895 行）、`sim/tb_sp_sram.v`（4630 行）
5. **关键参数**: `test_op_type=3'd4` = TEST write-through；`tckhtr=0.109ns`、`ttons=0.1ns`、`tcdt=0.1ns`；CLK 周期 3ns；timescale 1ns/1ps；内部时钟 1GHz
6. **静态分析结论**: CD 模式 posedge 写透传 + negedge 仲裁 `3'd4` 分支逻辑自洽；`q_fast_update` 是死信号（只写不读）排除；静态时序 `tckhtr/ttons << 时钟高电平` 不应 violation → 需动态数据
7. **FSDB 探针**: 波形 `sim/tb_sram_sp__1024x144_cd.fsdb`；时段 1358000~1363000；信号 `tb_sram_sp.dut.{Q_force_x, test_op_type, test_violation_pos, test_violation_clk, test_mode, BYP_eff, samp_BYP, test_read_data, Q_r, ttons_violation, ttons_pending}`
8. **工具**: `wv`（/apps/synopsys/SRB/wv/T-2022.06-SP1/bin/wv）、`vcs` 可用；cline skill `waveview-fsdb-readerV2-2`；shell-runner profile 仅允许 .sh 脚本
9. **结尾**: msg 72 assistant 空串 —— 会话在读 timing_check TEST 模式 violation 分支（RTL 3538-3575 / 2612-2740）时中断，**未给出修复、无用户接受结果**

## 合成判断
- **不适用 A 档**：trace 末尾无用户接受结果（会话中断于调查中），用户唯一轮过于泛化（"检查FAIL原因并修复"）
- **适用 B 档**：提取语义主题 = 「给定 FSDB 波形 + sim FAIL 日志，用 waveview Tcl API 在 FAIL 时窗探针关键信号 → 导出快照 → 计边沿 → 写结构化诊断报告」
- **可离线判分**：waveview `sx_*` API（sx_open_sim_file_read/sx_signal/sx_export_range/sx_export_data/sx_scan_data_points/sx_jump_to_x/sx_x_value/sx_y_value/sx_close_sim_file）可被 Tcl mock 录制 stub 替换；判分用 subprocess `tclsh` 跑候选 + mock，断言录制 + 诊断 JSON 结构
- **真跑候选**: mock 录制 = 候选确调用真 waveview API 调用链（L2，非纯离线文本匹配）
- **反硬编码**: 隐藏 B 换 fsdb_path / fail_time / 探针信号 / 根因 / 边沿计数，候选须读 spec 参数化执行 + 读 mock 导出值判根因

## 金标准（合成）
- A: fsdb=`tb_sram_sp__1024x144_cd.fsdb`, fail_test=21h, fail_time=1363000ps, 窗口 1340000~1370000, key_edge=test_op_type/CHANGE, mock 在 fail_time 注入 `Q_force_x=1` → 根因 `Q_force_x_stuck_high`, 边沿计数=4
- B (hidden): fsdb=`tb_sram_sp__1024x128_byp.fsdb`, fail_test=07h, fail_time=742000ps, 窗口 730000~760000, key_edge=BYP_eff/FALL, mock 在 fail_time 注入 `test_violation_pos=1` → 根因 `test_violation_pos_asserted`, 边沿计数=6（与 A 全不同）

## 选料决策
- fresh（台账无 woanw）· mc=108 · waveform 域（覆盖最低 45，本 case 增 1）· 真实 SRAM TEST 写透传 FAIL 场景保真度高
