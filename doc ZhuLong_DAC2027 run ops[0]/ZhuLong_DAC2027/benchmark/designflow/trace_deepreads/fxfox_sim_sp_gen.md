# 深读笔记 — fxfox (tongni@hfeg0pkn001, mc=496, sid 1793326532932)

## trace 来源
- session: `/home/tongni/.cline/data/sessions/1793326532932_fxfox/1793326532932_fxfox.messages.json`
- 用户: tongni @ hfeg0pkn001 (10.129.2.10)
- mc=496, tools: hspice×470 netlist×470 schematic×5 calibre (L2 真跑仿真)
- 模型: GLM-5.2 (本会话被测), 214 msgs

## 用户意图（逐字原话，A 档候选）
- msg#0 (act): 调用 `sim-sp-gen` skill，要求"给出 testbench 原理图 netlist，生成对应 Tran / AC / DC / Monte Carlo 仿真 .sp 文件"。附 SPEC 指标清单 + 5 个参考模板 (`/home/tongni/Desktop/1_Vcc2sc_stdby/template/`)。
- msg#86 (act): "所有的仿真怎么都退出了" — 用户指出 5 个 job 全 EXIT（但已给根因，不可作 A 档任务说明，仅作 hint）。
- msg#124 (act): 调用 `skill-creator` 要求把上述教训写入 sim-sp-gen skill。
- msg#143 (act): "更新进去" — 要求更新 skill 文件。

A 档任务说明候选 = msg#0（提出需求，未给根因/方案）。

## assistant 工具链（关键产物）
1. read SPEC.sp + 5 个模板 .sp（Vcc2scstdby_tran/ac/ac_load/dc_capbi/tran_mc）
2. read DUT 网表 (`tongni_DSCQA_2nd_sim_AG_Vcc2scALDOAct_sim_schematic.netlist`)
3. ask_question ×11（逐项确认：仿真类型清单/上电/PVT/hspiceconfig/testmode 信号/Vcc2scRef/使能/Vcc2sc2Vcc/AC 轻载/netlist .inc 路径/输出路径/tran_mc PVT）
4. editor ×6 在 `Vcc2scAct_sim_sp/{ac,ac_load,dc,tran,tran_mc}/Vcc2scAct_*.sp` 生成 5 个 .sp 文件
5. editor `submit_all.sh`（bsub -q hqueue3 hspice / bsub -q fqueue3 finesim -np 8）
6. run_approved_command `submit_all.sh` → bjobs 全 EXIT（计算节点访问不了 /home/tongni/Desktop 路径）
7. 诊断：job 在 hfednd077/hfeg0pfn119 跑，路径不在共享 FS → 修复方案：改 .inc 路径到 /proj/，但用户 msg#122 说"暂时不跑了"
8. agent 总结教训：① netlist 路径需对 LSF 节点可见 ② SPEC→仿真文件映射需 SPEC 驱动无遗漏

## 产物结构（5 个 .sp + submit_all.sh）
每个 .sp 结构：option(.inc hspiceconfig) → netlist(.inc DUT) → power(.inc power_tran + .param res_*) → stimulus(.GLOBAL + v<ref> + v<bias> + iload + .tran/.ac/.dc) → measurement(.MEAS 按 SPEC 指标) → pvt(.inc pvt 或 .LIB volt/corner + .TEMP)

5 个 .sp 测量指标（来自 SPEC.sp）：
- tran: Vcc2sc_unload, Vcc2sc_load1mA, Vcc2sc_undershot, Vcc2sc_undrmag, Vcc2sc_overshot, Vcc2sc_Rspon, Vcc2sc_tsetting, ring_ratio
- ac (轻载 0.05mA): Vcc2sc_Gain, Vcc2sc_PM, Vcc2sc_GM, Vcc2sc_GBW, Vcc2sc_f_3db
- ac_load (1mA): Vcc2sc_Gain_load1mA, Vcc2sc_PM_load1mA, Vcc2sc_GM_load1mA, Vcc2sc_GBW_load1mA, Vcc2sc_f_3db_load1mA
- dc_capbi: IVcc2sc
- tran_mc (monte=500): Vcc2sc_unload_mc, Vcc2sc_1mA_mc

submit_all.sh: 3 个 hqueue3/hspice (ac/ac_load/dc) + 2 个 fqueue3/finesim -np 8 (tran/tran_mc)

## 资产可读性
- ✅ 可读 (NFS): `/home/tongni/Desktop/1_Vcc2sc_stdby/template/Vcc2scstdby_{tran,ac,ac_load,dc_capbi,tran_mc}.sp` (5 个模板原文已 scp 到 .75 workdir)
- ✅ 可读: `SPEC.sp` (28 行指标清单)
- ✅ 可读: `gen_vcc2sc_tb.py` (trace 中的生成器参考)
- 🚫 不可读: `/proj/dscqa/V0/simdir/hspice/corner/` (e0031982 无读权限)
- 🚫 不可读: DUT 网表 `/proj/dscqa/V0/workdir/tongni/simulation/...netlist`

## 合成决策
**B-grade synthesized**（资产部分可读但 DUT 网表不可读 → 合成 DUT 配置 + 共享模板骨架）：
- A 输入（SUT 可见）: `SPEC_A.sp`（真实 SPEC 原文）+ `template/`（5 个真实模板原文）+ `DUT_A.json`（合成 DUT 配置：dut_name/netlist_path/power_nets/vref/output_net/bias_signals/load/tran/ac/dc/mc 参数）+ `task_brief.md`
- B 输入（隐藏）: `SPEC_B.sp`（指标名 Vwlp_*，值不同）+ `DUT_B.json`（wellesc/AG_VwlpLdoAct，vdd2!/VwlpRef/1.2V/Vwlp!/2mA/250u/monte=300/.TEMP 25）— 每维度反硬编码
- 候选任务: 写 `gen_sim_sp.py` 通用生成器，读 SPEC+DUT 配置+模板骨架 → 输出 5 .sp + submit_all.sh

## 断言设计（15 条 a-o，对 B 校验）
a zip 7 文件 / b py_compile+argparse / c 跑通 B 出 6 文件 / d tran netlist 路径=B(反 A tongni) / e vref=VwlpRef/1.2+输出 Vwlp! / f tran .MEAS 覆盖 7 B 指标 / g ac 轻载=0.02mA / h ac_load 重载=2mA+PM/GM meas 非退化 / i dc sweep=B+meas at=1.05 / j tran_mc monte=300+.TEMP 25 / k submit 5 bsub+队列/工具/-np / l .ac DEC 50 1 1G / m res_params=2 / n .tran 2n 250u / o 3-seed 确定性

## 关键反硬编码点（B≠A）
| 维度 | A | B |
|---|---|---|
| DUT 名 | AG_Vcc2scALDOAct (tongni) | AG_VwlpLdoAct (wellesc) |
| 电源网 | vdd1! | vdd2! |
| vref | Vcc2scRef/0.9 | VwlpRef/1.2 |
| 输出 | Vcc2sc! | Vwlp! |
| 轻载 | 0.05mA | 0.02mA |
| 重载 | 1mA | 2mA |
| tran | 1n 300u | 2n 250u |
| dc | 0.7 0.95 0.002 at=0.87 | 0.8 1.1 0.005 at=1.05 |
| ac freq | DEC 100 1 10G | DEC 50 1 1G |
| mc | monte=500 .TEMP 85 | monte=300 .TEMP 25 |
| res_params | =1 | =2 |
| SPEC 指标 | Vcc2sc_* | Vwlp_* |
