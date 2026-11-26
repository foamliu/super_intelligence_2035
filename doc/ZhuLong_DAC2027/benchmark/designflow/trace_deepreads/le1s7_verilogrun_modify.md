# le1s7 — Verilogrun 脚本批量修改（jason17w / hfeg0pnd002 / mc=506）

**session**: 1791941227075_le1s7.messages.json（742 msgs / 30 substantive user turns / cline + deepseek）
**user/host**: jason17w @ hfeg0pnd002
**domain**: schematic_netlist（DDR5 verilog 回归仿真 verilogrun 脚本编辑）
**match_count**: 506（netlist:1546 / schematic:0 / hspice:0 / pyAether:11）

## 真实场景
jason17w 在 DRAM DDR5 项目 `/rundata/drcoa/V0/simdir/verilog/jason17w/case_collect_for_vendor/verilog.ddr5.drcoa.netlist_jason/` 跑 VPS/UVS verilog 回归。`bin/vsim_test`（perl）每次执行 `genrunfile` 会用 `open(RUNFILE,">verilogrun")` 重新生成一份「原始版」verilogrun 脚本（csh 调 `uvs` 仿真器），含 `-noerror 120343` 与 `-v libs/simlib_base.sv`。用户先让助手注释掉 vsim_test 里删除 verilogrun 的代码（保留 verilogrun），再跑一轮回归 `uvs_20261012_run_step1_bk`，得到 5 个 checkin_* case 目录各保留一份 verilogrun。

## 关键用户轮（U[435]，选料原话）
> 「把这5个case的verilogrun中的-noerror 120343去掉，并且把-v libs/simlib_base.sv 换成-v libs.bak20260416/simlib_base.svp。做一份verilogrun的备份。」

5 个目标 case（均为 `checkin_*`，排除 `noregression.x8` 软链目录）：
- checkin_bl16_fixed_cai=_mir=.x8_8000
- checkin_crc_bc8_cai=_mir=.x8_8000
- checkin_crc_cai=_mir=.x8_8000
- checkin_read_training_pattern_test_cai=_mir=.x8_8000
- checkin_th_win_loop_cai=_mir=.x8_8000

## 真实 verilogrun 内容（取自 trace read_files msg[447]，checkin_crc_cai=_mir=.x8_8000）
`#!/bin/csh -f` 脚本，调用 `uvs`（Synopsys 类 verilog 仿真器）：
- L9 长行：`uvs \ -config .../sim_tfile.cfg -pstat -verbose -f .../temp_option.list -uvs_xlrm BMode -noerror 120343 -ddb -debug cbk,f -debug_cell -sv -logfile uvs.cmp_log \`
- L10–41 续行：`-sdf_annotate_cfg` / `+xmnostdout` / `+xmtypdelays` / `+define+X8` / `+define+TS_8000` / `+define+DISODTMON` / `+mir=` / `+cai=` / `-v libs/simlib_TECHLIB.sv` / **`-v libs/simlib_base.sv`** / `-v libs/simlib_drcoa_analog.sv` / ... / `+incdir+.../V0_DDR5TOP_2026May25.163821` / `top.sv`
- L42：`./uvsim -Xair xb.edge_clock_opt_enhancement -cli -do probe.tcl -usdb=all,cell,delta -logfile uvs.sim_log`

## 助手解法（U[436–460]）
写 `modify_verilogrun.sh`：对 5 个 checkin_* case：
1. `cp -a verilogrun verilogrun.bak`（备份）
2. `sed` 去掉 `-noerror 120343`
3. `sed` 把 `-v libs/simlib_base.sv` → `-v libs.bak20260416/simlib_base.svp`
4. 验证：`grep -c` 确认 5 case 的 `-noerror 120343 count=0`、`-v libs/simlib_base.sv count=0`、`-v libs.bak20260416/simlib_base.svp count=1`

`libs.bak20260416/simlib_base.svp` 真实存在（98224B，4月20日版本，对比 `libs/simlib_base.sv` 71785B 9月4日版本）。

## 后续演进（不进本题，但说明任务真实背景）
- U[461–504]：用户发现 vsim_test 重跑会覆盖改好的 verilogrun → 选方案 B 改 vsim_test `genrunfile`，仅对 5 个 case 从旧目录复制改好的 verilogrun 复用 → 跑 v2 回归
- U[505–589]：v2 5 case 全报错（`libs.bak20260416/simlib_base.svp` 在新 case 目录找不到 → Warning-121507）→ 用户令改回 `simlib_base.sv` + 保留去 noerror 跑 v3 → 后续多轮 noerror 加回/去掉对照（v4/v5/v6）做故障注入演示

## 合成决策
- **B 档 L1**：选 U[435] 这一段自包含的脚本编辑任务，金标准 = 助手 `modify_verilogrun.sh` 的 sed 改写 + 验证产物。
- **资产 A**：从真实 verilogrun（msg[447]）派生 5 个 checkin_* case（同模板，不同 GLOBAL_SEED）。
- **隐藏 B**（cross-input guard）：4 个 checkin_* case + 1 noregression.x8（须排除），注入边界：双 `simlib_base.sv` 出现、`simlib_base.sv.bak` 不可替换、已清洁 case、case 数 ≠ A。
- **判分**：subprocess 真跑候选 `modify_verilogrun.py` 于 B，解 modify_report.json + 比对改后 verilogrun 文件结构（非文本相似）。
