# trace_deepread — 1793103982380_vdwab (tongni @ hfeg0plg63, mc=236, hspice=445/netlist=783/schematic=273)

**agent**: lead (cline). 185 msgs (104 user / 81 assistant). tools: editor 26 / read_files 22 / ask_question 22 / list_allowed_files 10 / run_approved_command 12 / search_codebase 3.

## 用户意图（提出需求轮，A档候选）
- **U[0]**（主需求）: `[sim-sp-gen] /rundata/dscqa/V0/simdir/hspice/tongni/00_AI_sim_gen/zmh_drvqa_sim_DRVQA_VwlpRef_sim_schematic_ALPS/netlist.presim 生成所有的仿真文件` —— 给 testbench 原理图 netlist，生成**全部**仿真文件（Tran/AC/DC/Monte Carlo）。
- **U[106]**: `psrr也是一个考虑项` —— 追加 PSRR 分析（第 5 个 deck）。
- **U[130]**: `继续`。
- 第二个 testbench（Vcc2scAct，U[137]+）: 同一 skill 生成 Vcc2sc active LDO 的 5-deck set。本 case 取第一个 testbench **VwlpRef**（reference voltage buffer/LDO）。

## skill = sim-sp-gen（DomainSkill, Workflow）
- 给 testbench netlist → 生成 Tran/AC/DC/Monte Carlo `.sp` 文件。
- 参考模板 `/home/tongni/Desktop/1_Vcc2sc_stdby/template/`（SPEC 全套指标：ac_load/ac/dc_capbi/tran_mc/tran 各段）。
- corner 文件在 `/proj/dscqa/V0/simdir/hspice/corner/`（hspiceconfig.sp / power_tran.sp / pvt.sp / volt.sp / corner.sp）—— **foundry 权限不可移植 .75**。

## 真实产物（agent 用 editor 生成，replay 还原）
agent 生成 5 个 .sp 到 `/home/tongni/Desktop/1_Vcc2sc_stdby/VwlpRef_sim_sp/`，共享 header（.inc hspiceconfig / vwlpref_pwrfix.netlist / power_tran / stimulus）+ 分析专属 body：

1. **VwlpRef_tran.sp** — `.tran 1n 300u` + step-load iLoadVwlpRef pwl(0→0.1mA→1mA→0.1mA) + `.ic v(VwlpRef)=0` + 9 个 .MEASURE（unload AVG / load1mA AVG / undershot MIN / undrmag=unload-undershot / overshot MAX / overmag=overshot-load1mA / tvalley WHEN / Rspon=tvalley-100u / tsetting / pp_front / pp_back / ring_ratio=pp_back/pp_front）。改 2 版（U[85] 把恒定 DC_load 换成 step pwl，U[97] 重写 measure 段为 SPEC 4 段）。
2. **VwlpRef_ac.sp** — `.ac DEC 100 1 10G` + `.lstb VwlpRef mode=single vsource=V0` + `.probe ac Lstb(DB:VwlpRef) lstb(P:VwlpRef)` + 5 measure（Gain=max DB / PM=find P when DB=0 cross=last / GM=find DB when P=0 / GBW=when DB=0 / f_3db=when DB=Gain-3）。恒定 iload_wlp 0.05mA。
3. **VwlpRef_dc.sp** — `.dc pvalue 0.6 1.0 0.002` + vVwlpRef=VwlpRef pvalue + `.meas dc IVwlpRef find i(vVwlpRef) at=0.85`。
4. **VwlpRef_tran_mc.sp** — `.tran 1n 300u sweep monte=500` + `.meas find v(VwlpRef) at=70u/120u` + **内联 .LIB volt typ + corner ttt（不走 .alter）**。这是 trace 的明确设计选择（MC 用 inline .LIB，非 .alter）。
5. **VwlpRef_psrr.sp**（U[106] 后加）— `.ac DEC 10 1 10G` + `.probe ac vdb(*)` + 3 measure（PSRR100Hz/1kHz/1MHz find vdb(VwlpRef) at=）。

## 可复现子技能（取此做 case）
**multi-analysis SPICE deck-set 生成**：给定 DUT testbench netlist + SPEC，emit 5 个分析专属 deck（tran step-load / ac 稳定度 / dc 静态电流 / tran_mc Monte Carlo / psrr 电源抑制），每个 deck 共享 common header（.inc corner/dut/power + stimulus）但分析语句 + .measure 构造 + load 接法 + pvt 接法各不同。核心 discriminator：
- tran: step-load pwl + AVG/MIN/MAX/WHEN/PP measure 组合 + ring_ratio
- ac: 稳定度 measure（.lstb loop-gain 或 closed-loop bandwidth/peaking）
- dc: .dc sweep + find i at=
- mc: `sweep monte=` + **内联 .LIB（无 .alter）** —— naive 用 .alter 必败
- psrr: AC on supply + vdb at 多频点 + PSRR 随频率退化
- 共享 header 一致性（5 deck 同 GlbRef stimulus + 同 X1 instantiation + 同 .GLOBAL）

## distinct vs 已有 B case
- Vcc2scTranGen(aq0vc)=单 tran deck 生成 + measure 窗口回贴 —— 本条=**5-deck SET** 多分析类型。
- PVTalterChar/AlterDeckSplit=PVT 多角 .alter 分析（单分析类型多角）—— 本条=多**分析类型**（tran/ac/dc/mc/psrr）。
- OpampACSpec=开环 AC gain/pm/gbw —— 本条 ac 是 regulator 闭环 + 加上 tran/dc/mc/psrr 一整套。

## 不可移植部分 / 合成化
- real netlist `/rundata/dscqa/.../netlist.presim` + corner `/proj/dscqa/...` = CXMT foundry 权限 denied，不可移植 .75。
- 取自包含 level-1 MOS LDO DUT（5T OTA + PMOS pass + Miller Cc + CL）+ 自包含 corner（.option/.model）+ power（rails）+ pvt，.75 HSPICE V-2023.12-SP1-1 真跑。
- **AC 适配**：trace 用 `.lstb`（loop-gain，需 real netlist 有外置 feedback vsource V0 可断）；自包含 DUT 是 .SUBCKT 内闭环（无外置 vsource），.lstb 无 loop-break element → measure 全 failed。改取 **closed-loop AC 响应**（AC 激励 GlbRef085，测 vdb(VwlpRef) 闭环 gain + f_3db 带宽 + Peak peaking）。这是 B档 synthesized 的合理适配（保留 AC 分析 deck 生成子技能，measure 选择因 DUT 拓扑调整）。
- .75 HSPICE level-1 gotcha：gamma=0 → `nsub<=ni` abort，须显式 `nsub=1e16 phi=0.7`。

## .75 HSPICE 自验 GT（set A: pvcc=1.2, GlbRef085=0.85, kp_n=120u/kp_p=40u, vto±0.5, Mpass W=80u, CL=10p, Cc=0.5p, Itail=20u）
- tran: VwlpRef_unload=0.8500V / load1mA=0.7749V / undershot=0.6202V @100.005u / undrmag=0.2298 / Rspon=5.33n / ring_ratio≈0
- dc: IVwlpRef=634.74uA
- psrr: PSRR100Hz=-113.88dB / 1kHz=-93.88dB / 1MHz=-33.86dB（随频率退化）
- ac(closed-loop): Gain≈0dB / f_3db=37.59MHz / Peak=8.05dB@23.99MHz
- mc(sweep monte=50, 无 mismatch 参数 → 各样本同): unload_mc=0.8500 / 1mA_mc=0.7749（结构验证）
