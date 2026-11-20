# 深读笔记: 1792574756685_lond8 — SynLintFlow (cfreq_ctrl lint+综合流程)

## trace 元数据
- session: `1792574756685_lond8.messages.json` (520 msgs / 1.7MB)
- user: `lorikx` / host: `hfeg0pkn005` / match_count: 249
- tools 主导: netlist=281, synthesis=90, innovus=4 (digital/synthesis 域 → shard A)
- 项目根: `/home/lorikx/freq_calibration_model/`
- 参考流程: `/home/lorikx/freq_calibration_model/ref_syn_prj/lagat_flow_ref/{syn, digital_static_check, spyglass, fm, dft}`

## 用户真实意图轮 (A档选轮)
- **#0 (idx 0) USER_INPUT 逐字原文**:
  「我想在这个项目里做个lint的项目文件，以及综合的流程，都放在单独的文件夹（目标文件是rtl_synth里面的.v文件）」
  → 纯「提出需求」, 未给根因/修复 → **合 A档选轮规则**, 选为任务说明。
- #34 (idx 34): 「你可以参考当前文件夹下的lagat_flow_ref去完成我给你的任务, 这个代码也属于lagat项目」
  → 指向参考流程 (context, 不进 prompt, 但证明 lagat_flow_ref 是真实参考资产)。
- #54「请继续」/ #164「修改代码后怎么快速再跑综合」/ #222「再开两个文件夹, 一个做覆盖率检查, 另一个做形式验证」/ #355「syn 里面的网表支持用 Makefile 快捷打开 Verdi 观察网表吗」/ #399「学习 ref_syn_prj/dlyl_encoder/syn 优化现有综合环境, 包括 sdc」/ #480「面积是什么单位的」
  → 后续轮: 续跑/Makefile 重跑/加 cov+fm 文件夹/Verdi 网表/SDC 优化/报告解读; 均为后续扩展, 不作 A档任务说明。

## 真实任务
为 `rtl_synth/cfreq_ctrl.v` (VCO 自动校准模块, Verilog-2001 可综合, 358 行) 建立:
1. **lint 项目** (`lint/`): VC Static (原 SpyGlass) lint/CDC/RDC 静态检查, 参考 `lagat_flow_ref/digital_static_check`
2. **综合流程** (`syn/`): Design Compiler (`dcnxt_shell`) 综合流程, 参考 `lagat_flow_ref/syn` FEINT 流程
- 工艺: HL22, 综合角 ssg_0p72v_m40c (CCS), 库 `Au22_basic_{ulvt,lvt}_ssg_0p72v_m40c_ccs.db`
- PDK 根: `/apps/imctf/extpdk/HL22/LAGAT/Digital/current`
- 双时钟域 REFCLK/FBCLK 25MHz 异步; RST_N 异步复位

## 金标准 (用户实际接受的结果, 已 cat 核实)
- `syn/`: Makefile (dc_syn/verdi/report, LSF bsub + 本地 dcnxt_shell 兜底, USE_LSF 开关, DC_XARGS -x 透传变量, RTL 文件依赖自动重跑) + SourceMe + README.md + setup/common_setup.tcl + scripts/{dc.tcl, dc_setup.tcl, dc_setup_filenames.tcl} + sdc/cfreq_ctrl.sdc + data/syn_filelist.f
- `lint/`: README.md + work/{Makefile (include sc_target.mk), SourceMe, design_rtl.list, design_lib.list, cfreq_ctrl.prj, lint.tcl} + config/{waiver.tcl, cdc_sdc/cdc.sdc, rdc_sdc/rdc.sdc}
- dc.tcl 流程: set_svf(读设计前) → analyze/elaborate/current_design/link → check_design → presyn.v → source SDC → set_operating_conditions → compile_ultra -gate_clock -no_autoungroup + -incremental → uniquify/change_names/verilogout_no_tri → write mapped.{ddc,v,sdc,sdf} → 完整报告集 (qor/timing setup+hold/area/power/clock_gating/threshold_voltage_group) → set_svf -off
- 文件名: ${cur_date} (=TAG=Au22) 标签 reports, 但 ${DESIGN_NAME}.mapped.v 不带标签 (fm/verdi 下游固定引用)
- 已真跑 (flow_cfreq_ctrl/ 有真产物: cfreq_ctrl.mapped.v, *.rpt, syn.done)

## case 合成决策
- **A档 trace-faithful**: 任务说明 = #0 逐字原文; task_brief ≤3 行只写交付接口 (不写"要做什么"); 资产 = rtl_synth/cfreq_ctrl.v (真实输入) + workspace_listing.txt (真实工作区清单, 含 lagat_flow_ref 提示) — 不加合成说明性注解。
- **L1-boundary 判分**: 不在判分器里真跑 DC (无 license/太重); 静态结构断言 (a)-(u) + tclsh stub 跨输入守护 (v)-(z) 用隐藏 B (dco_trim, 端口/时钟/复位名全异) 击败硬编码 A 字面量。
- 隐藏 B: `dco_trim.v` (CLK/DIV_CLK/RSTB/TRIG/TRIM vs A 的 REFCLK/FBCLK/RST_N/LOOP_BREAK/CAP_CTRL_OUT; 8bit WIN/LIM vs 10bit; 3 状态 FSM vs 7 状态)。check.py 用 tclsh stub 注入 B 的 common_setup 跑提交的 dc.tcl, 断言 elaborate/current_design/write/analyze 用 $DESIGN 变量而非硬编码 cfreq_ctrl。

## check.py 26 条独立断言
(a)-(p) syn 流程结构 (16 条); (q)-(u) lint 流程结构 (5 条); (v)-(z) tclsh stub 跨输入守护 (5 条)。k_check=26 ≥8。
- 自验: ref PASS 26/26; 5 negative 全 FAIL (NEG_RC=0, 5 distinct labels: fake_empty→a / fake_print_expected→c / fake_core_deleted→j / naive_hardcode_a→w / naive_no_source_sdc→i); §4.9 (a)(b)(c) 三假 FAIL。
