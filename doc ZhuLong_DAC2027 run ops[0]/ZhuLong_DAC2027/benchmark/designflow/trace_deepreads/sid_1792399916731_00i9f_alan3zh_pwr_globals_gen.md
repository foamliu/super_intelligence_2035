# trace deepread: 1792399916731_00i9f — Innovus `gui/power.globals` 初始配置生成

- session: `1792399916731_00i9f.messages.json` · user `alan3zh` · host `hfeg0pkn003`(10.129.2.12) · mc=101 · 107 msgs · 421KB
- domain: **pg_layout**（Innovus APR 初始配置 → GUI 后续任务 handoff 文件）✓ shard C
- agent: cline · workspace `/home/alan3zh/workspace/test_chip/test_chip`

## 用户意图轮（A-档 faithful 候选）
- UI#1 (idx=0, 逐字节选): Context summary continuation note（test_chip 后端链路 → RedHawk 功耗仿真搭建；已完成 RO 反相器丢失修复 + 后仿 0 延迟修复；当前任务 pp/ RedHawk 功耗仿真）— 续轮上下文，非独立意图
- UI#2 (idx=14, 逐字): `continue` — 命令非意图
- **UI#3 (idx=29, 逐字): `将apr/innovus下的初始配置，写入apr/innovus/gui/power.globals中，使其能在innovus中进行后续任务`**
  - 规则②判定：用户表达**目标**（把 apr/innovus 初始配置固化为 `gui/power.globals`，供 Innovus GUI 后续任务复用），**未给根因/修复方案**（模型须自读 Makefile + mmmc.view + innovus_fp.tcl init_design 块，理解 init_* 全局变量 + tech-LEF-first 约定 + MMMC view + routed DEF + power domain，合成可在 GUI source 的 TCL 设置脚本）。→ **A-faithful ✓**

## 金标 = trace 助手 [30]-[104]
1. [30-44] 列 apr/innovus 目录 → 读现有 power.globals（空）+ Makefile → 查 /apps/cad/modulefiles 找 Innovus 版本（23.35 / 231_os7）→ 读 modulefile
2. [46-56] run find_power_globals.py 在 INNOVUS-23.35 安装树搜 `power.globals` 格式证据 → 写 find_in_tree.py + probe_fs.py 探沙盒可见根
3. [57-60] 列 work/ 目录确认 routed.v / .def / _inv_routed.dat / mmmc.view 齐全；列 pe/work / post_sim_sdf / results/dc 确认 SPEF/FSDB/postsyn 路径
4. [62-64] **写 gold `apr/innovus/gui/power.globals`**（Innovus TCL 设置脚本）：
   - header 注释：用途/两种用法（`innovus -files` vs GUI `source`）/VDD_PM grid TODO
   - `set ROOT/APR_DIR/WORK_DIR/PDK_ROOT/TOP`（TOP=`hl22_porting_test_chip_power`）
   - `set TECH_LEF $PDK_ROOT/Innovus_tf/Au22_1P7M_4_1X_2_2X_1_8X_withRDL_HVH.tlef`、`set CELL_LEF $PDK_ROOT/Au22_basic_lvt/lef/Au22_basic_lvt.lef`
   - `set MMMC_VIEW $WORK_DIR/mmmc.view` + fallback `$APR_DIR/gui/mmmc.view`（if not exists）
   - `set IN_V $WORK_DIR/${TOP}.routed.v`（routed netlist，与 DEF/SPEF/post-sim 一致；注释给出 postsyn 替代路径）
   - `set DEF_IN $WORK_DIR/${TOP}.def`、`set ROUTED_DB $WORK_DIR/${TOP}_inv_routed.dat`
   - `set PWR_NETS {VDD VDD_PM}`、`set GND_NET VSS`（VDD_PM=pd_pm domain，grid TODO）
   - **pre-flight**：`foreach f [list $TECH_LEF $CELL_LEF $MMMC_VIEW $IN_V $DEF_IN] { if {![file exists $f]} { puts ERROR...; return } }`
   - **design-in-memory guard**：`set have_design 0; catch { if {[llength [dbGet top.name]] > 0} { set have_design 1 } }`
   - `if {!$have_design}`：设 7 个 init_* 全局变量（`init_verilog $IN_V` / `init_lef_file [list $TECH_LEF $CELL_LEF]` **tech LEF first (IMPLF-26)** / `init_top_cell $TOP` / `init_design_settop 1` / `init_pwr_net $PWR_NETS` / `init_gnd_net $GND_NET` / `init_mmmc_file $MMMC_VIEW`）→ `catch {init_design} err` 失败则 ERROR+return → `catch {defIn $DEF_IN}` 成功 INFO / 失败 WARN（physical view 缺失）→ `catch {setMultiCpuUsage -localCpu 8}`
   - `else`：design 已加载，打印 `restoreDesign $ROUTED_DB $TOP` 替代路径
   - **INFO pointers**：TOP / power nets / routed DEF / SPEF (pe) / FSDB (sim) / next GUI 步骤（report_power；IR/EM 需 power grid + Voltus-Fi）
5. [70-78] check_tcl_balance.py 校验 power.globals / redhawk.tcl / probe.tcl 三份 Tcl 平衡 ✓；lint_makefile.py
6. [79-96] 回读 power.globals；patch_pp_makefile.py 适配 pp/Makefile（RedHawk-SC→classic redhawk -b + GSR）；write_readmes.py 同步 README；fix_phony_and_verify.py 修 .PHONY 加 probe target
7. [98-104] cleanup_tmp.py 清理临时脚本

## 源文件（已从远端核实，将固化为 assets A）
- `apr/innovus/Makefile`：`TOP=hl22_porting_test_chip_power`、`PDK_ROOT_PATH=/apps/imctf/extpdk/HL22/LAGAT/Digital/current`、`TECH_LEF=.../Innovus_tf/Au22_1P7M_4_1X_2_2X_1_8X_withRDL_HVH.tlef`、`LEF_FILE=.../Au22_basic_lvt/lef/Au22_basic_lvt.lef`、`LIB_FILE=.../Au22_basic_lvt_ssg_0p72v_m40c_ccs.lib`、`INV_POWER_NET=VDD`、`INV_GROUND_NET=VSS`、`WORK_DIR=$(CURDIR)/work`、`MMMC_VIEW=$(WORK_DIR)/mmmc.view`、`NETLIST=$(DC_RESULT_DIR)/$(TOP)_postsyn.v`、`DC_RESULT_DIR=$(PRJ_ROOT)/results/dc_2026-10-13-13.08.17`、tech-LEF-first 注释（IMPLF-26）
- `apr/innovus/work/mmmc.view`：单 corner `ssg_0p72v_m40c`，`create_library_set libs_typ -timing {...Au22_basic_lvt_ssg_0p72v_m40c_ccs.lib}`、`create_constraint_mode mode_func -sdc_files {<sdc> <cts_clk.sdc>}`、`set_analysis_view -setup {av_func_typ} -hold {av_func_typ}`
- `apr/innovus/innovus_fp.tcl` (init_design 块 71-90)：`set init_verilog $NETLIST`、`set init_lef_file [list $TECH_LEF $LEF_FILE]`（tech FIRST IMPLF-26）、`init_top_cell/init_design_settop 1/init_pwr_net $PWR_NET/init_gnd_net $GND_NET/init_mmmc_file $VIEW_FILE`、`catch {init_design}`；pre-flight `foreach f [list $NETLIST $LEF_FILE $TECH_LEF $VIEW_FILE]`
- power domain：Makefile `INV_POWER_NET=VDD`（单），gold 扩展为 `{VDD VDD_PM}`（VDD_PM=pd_pm domain，grid TODO，来自 power/IR handoff 上下文，非 Makefile）

## case 设计
- task_id: `EDA-Eval-DesignFlow-PwrGlobalsGen-001` · pg_layout · L1-boundary · **B-档 synthesized**（A-disqualified：gold 依赖 live workspace `/home/alan3zh/workspace/test_chip` + live Innovus 23.35 安装树，.75 沙盒不可达；与 r82 PGReproGuide/r80 DRCSpecGen/r79 DRCDeckSyncPlan 同模式）
- A-档 seed: UI#3 逐字 `将apr/innovus下的初始配置，写入apr/innovus/gui/power.globals中，使其能在innovus中进行后续任务`
- 资产 A：`Makefile` + `mmmc.view` + `innovus_fp_init.tcl` + `power_domain_spec.json`（faithful 复刻 alan3zh 真实文件）
- 隐藏 B：换设计（HL28 / TOP=adc_testchip_top / 单 {VDD} / innovus 23.41 / 无 grid_todo）；B2（3 power nets {VDD,VDD_PLL,VDD_IO} + postsyn netlist kind）；B3（无 SPEF stage → pointers 须 omit SPEF）
- 候选 `gen_power_globals.py <input_dir> <out_file>`：解析 Makefile（TOP/PDK_ROOT/TECH_LEF/LEF_FILE/WORK_DIR/MMMC_VIEW/DC_RESULT_DIR/NETLIST）+ power_domain_spec.json（power_nets/ground_net/grid_todo/innovus_version/netlist_kind/spef_rel/fsdb_rel）→ 合成 power.globals TCL（pre-flight + design-in-memory guard + 7 init_* vars tech-first + defIn + restoreDesign alt + INFO pointers）
- 与 r82 PGReproGuide（全流复现指南 JSON）/ r59 PRBoundary / r80 DRCSpecGen（spec→SVRF）正交——**本案是 Innovus APR 初始配置→GUI handoff TCL 设置文件合成**（init_* globals + MMMC + routed DEF + power domain guard），pg_layout 新子主题，新用户 alan3zh
