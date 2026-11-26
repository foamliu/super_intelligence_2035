# trace_deepread: 1792720528359_2tuxj (CTLE transient sim script)

- **user**: kaixuanx @ 10.129.2.10, mc=91, n_msgs=186, n_user=102, n_asst=84
- **round picked**: U#0 (唯一真实 user_input 提需求轮；其余 user 轮多为工具结果；U#57「仿真已经跑完」、U#62/U#63/U#74+ 转为版图生成，不同任务不计入)

## U#0 逐字（A-faithful 任务说明）
> 我设计了一个CTLE电路，仿真激励和网表都在这个文件夹里/proj/m2701/V0_DDR4/workdir/kaixuanx/simulation/CTLE_active_ind  ，我已经仿真了CLTE的AC性能ctle_act_ind.sp，现在我想仿真相关的瞬态性能ctle_act_ind_tran.sp，我需要你帮我总结一下需要仿真的各项性能指标，并帮我重新写一个仿真脚本

判断：纯提需求（写瞬态仿真脚本），未给根因/修复 → A-faithful。

## trace 演化（msg1–msg120 = 仿真脚本任务）
- msg1: list_allowed_files CTLE_active_ind 目录 + get_agent_policy_status
- msg4: read_files ctle_act_ind.sp(AC) / ctle_act_ind_tran.sp(原) / ctle_act_ind_mc.sp(MC)
- msg6: list hspiceD/schematic + read_files run/run1/run2
- msg9: read_files hspiceD/schematic/netlist/netlist
- msg11: run_approved_command 探活 hspice/finesim + 列 model 目录
- msg14–18: editor check_tools.py + run + read_files /home/adaml/MySimuSettings/option_hspice.sp + model corners_0p8.env / corners_voltage_pre.sp
- msg23: editor ctle_act_ind_tran_legacy.sp（备份原 tran）
- msg25–29: editor ctle_act_ind_tran_v2.sp（v2 重写）：header + .inc option/switch + .lib corners_0p8.env tt_25_pre + .inc netlist + VDD/VSS/IBIAS + EDM OUT_DM POLY(2) + EIN IN_DM + .param data_rate=7.2e9/ui/vcm/swing/amp_high/low/num_bits/sim_time/tstep/twarm/trin/prbs_seed + VINP/VINN LFSR(amp_low amp_high 0 trin trin data_rate prbs_seed [15,14]) + .TRAN + .MEAS(eye/outcm/delay/overshoot/power) + .PROBE + .END
- msg31–35: editor run_validation.py（quick-run override 少 bits）+ run + read tran_check.lis
- msg37–51: editor test_prbs.py 探 PRBS source → 发现 HSPICE 用 LFSR() 非 PRBS()，taps 须 inline → read prbs.sp / search LFSR doc
- msg54–64: editor find_lfsr_docs.py + read pseudo_random_bit_generator_source_lfsr.html
- msg66–90: editor 修正 ctle_act_ind_tran_v2.sp：.param trin/prbs_seed/prbs_taps → LFSR source inline taps [15,14]；run_validation + read tran_check2.lis 反复验证
- msg92–102: editor 修 .MEAS（overshoot/power）+ run_validation 验证
- msg104: editor 试写 /proj/.../ctle_act_ind_tran_v2.sp（placeholder）
- msg110–116: list results/tran + read ctle_25_0p8.mt0.csv / .lis（仿真产物）
- **U#57「仿真已经跑完」= 用户接受**（金标准 = 真实产物 ctle_act_ind_tran_v2.sp 已验证可跑）

## 后续（msg120+ = 版图生成，不同任务，不计入本 case）
- U#62「能不能根据电路图来生成版图」→ U#63 eda_agent skill → U#74 指定 virtuoso 环境 → agent 写 gen_layout_from_sch.il (SKILL lxGenFromSource)

## 金标准（B-grade synthesized）
真实 /proj/m2701/.../netlist 与 /rundata 路径不可附加 → B-grade synthesized。
金标 = gen_tran_ref.py（数据驱动 CLI `<config.json> [--out <sp>]`），按 config 生成 CTLE 瞬态 .sp：
- .OPTION post=2 probe=1
- .lib model_lib corner
- .inc netlist_inc
- VDD/VSS/IBIAS + .param vdd_sup/CL/RL/ibias_val
- EDM diff_out POLY(2) outp/outn ; EIN diff_in POLY(2) inp/inn
- LFSR(amp_low amp_high 0 trin trin data_rate prbs_seed [taps]) × 2（差分）
- .TRAN tstep sim_time START=0ns
- .MEAS 按 metrics 列表选择：eye(eye_vmax/vmin/amp/mid) / outcm(outp_hi/lo/avg/wnd) / delay(td_plh/phl,out_trise/tfall) / overshoot(out_peak/valley,ovsh/unsh) / power(i_vdd_avg/max,pwr_avg)
- .PROBE save_signals + I(VDD) + .END

## A / B 差异（反硬编码双轴）
| 字段 | A (SUT 可见, 匹配 prompt) | B (hidden) |
|---|---|---|
| circuit | CTLE_active_ind | DFE_rx_eq |
| rate | 7.2 Gbps | 5.4 Gbps |
| prbs_taps | [15,14] (PRBS-15) | [7,6] (PRBS-7) |
| seed/num_bits | 1 / 1024 | 3 / 512 |
| vdd/swing/vcm | 0.8 / 0.2 / 0.4 | 1.0 / 0.3 / 0.5 |
| 信号名 | INP/INN/OUTP/OUTN/OUT_DM/IN_DM | in_p/in_n/out_p/out_n/diff_o/diff_i |
| metrics | eye,delay,**overshoot**,power,outcm | eye,delay,power,outcm（**无 overshoot**） |
| model_lib/corner/netlist_inc | model.env / tt_25_pre / netlist.sp | rx_corner.env / ss_m40_pre / rx_netlist.sp |

**核心难度点**：(1) HSPICE 伪随机源是 LFSR() 非 PRBS()，taps 须 inline（trace 内 agent 反复挣扎）；(2) metrics 列表数据驱动测量集选择（B 排除 overshoot → SUT 不可硬编码全测量）。

## 教训
- peek 经 .75 ssh 串行 + `python3 - <sid> <user> < reader.py` stdin 注入 sid（避 `%` format）。
- A-faithful prompt = U#0 逐字，task_brief 只写交付接口（gen_tran.py CLI + 隐藏 config_B 判分），不写「要做什么」。
- 反硬编码用 metrics 子集差异（B 无 overshoot）+ 全信号名/速率/抽头/电压双轴差异交叉检验。
- check (o) B-only 字面量检查须排除 diff_o/diff_i（⊂ diff_out/diff_in 配置键）与 out_p/out_n（⊂ out_peak 测量名）。
