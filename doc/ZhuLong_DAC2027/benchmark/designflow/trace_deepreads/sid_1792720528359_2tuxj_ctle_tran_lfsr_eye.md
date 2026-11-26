# 深读笔记 — trace 2tuxj (kaixuanx @ hfeg0pkn001, mc=91, spice_sim)

- **session**: 1792720528359_2tuxj.messages.json (186 msgs: 102 user / 84 assistant)
- **真实任务**: kaixuanx 设计了 CTLE_active_ind（DDR RX 均衡器，交叉耦合电容 XC1 + XR3 实现"有源电感"式高频峰值增强），已跑完 AC 性能，现在要仿真瞬态性能 → T0 逐字「我设计了一个CTLE电路…现在我想仿真相关的瞬态性能ctle_act_ind_tran.sp，我需要你帮我总结一下需要仿真的各项性能指标，并帮我重新写一个仿真脚本」(纯需求轮，A-档合规)。
- **真实流**: agent 读 ctle_act_ind.sp / netlist / run → 写 ctle_act_ind_tran_v2.sp → HSPICE V-2023.12 跑通 → **踩坑**: HSPICE 伪随机源是 **LFSR 不是 PRBS**（`PRBS(...)` 报 `Undefined parameter "prbs"`），正确语法 `LFSR(vlow vhigh tdelay trise tfall rate seed <taps>)`，taps 必须内联（`[15,14]` 不能经 .param 字符串传，报 `No taps or lfsrfile found`）→ 修后跑通 14+ .MEAS TRAN：eye_vmax/eye_vmin/eye_amp/eye_mid/outcm_avg/outcm_wnd/td_plh/td_phl/out_trise/out_tfall/out_peak/out_valley/ovsh/unsh/i_vdd_avg/pwr_avg，得 eye_amp≈0.45Vpp / td≈12.4ps / pwr≈0.40mW / outcm≈0.353V。
- **后续轮**: [109]「仿真已经跑完」(状态确认) → [119]/[139] 改要版图（virtuoso layout，非 spice_sim，弃）。
- **distinct vs 已有 B case**: wb03t=CTLE **AC** spec 合规、CTLEAC/CTLESpec=CTLE 信道均衡 AC、NmosAgeChar=单管表征、VihTripTune=DC 翻转点调优、OtaAcReport=WaveView AC、TaperBufOpt=buffer DOE、PFDdeadZone=dead-zone sweep、Sram6tDcChar=SRAM DC —— 本条=**CTLE 瞬态 LFSR PRBS + .MEAS TRAN 眼图/时延/边沿/过冲/功耗表征**（tran eye-diagram 子技能，shard B 此前未覆盖）。

## 便携化（已交付 EDA-Eval-DesignFlow-CtleTranChar-001）

- **DUT**: foundry netlist 不可移植 → 自包含 level-1 Shichman-Hodges CTLE 子电路 `XCTLE`（NMOS diff pair + source �退化电阻 + PMOS diode 负载对称 + 交叉耦合电容 + 负载电容，用 global .param 取 wn/wp/ln/lp/RL/CC/CL/ibias）。corner.lib = level-1 NCH/PCH（KP=120u/50u, VTO=0.5/-0.45）。
- **testbench** (ctle_tran_tb_ref.sp): `.inc DUT + .lib corner + .inc params.inc`，LFSR 差分输入（VINP/VINN 互补），EDM/EIN POLY(2) 做差分，.TRAN tstep/sim_time，19 条 .MEAS TRAN 覆盖 6 类度量（眼图/单端共模/时延/边沿/过冲/功耗）。
- **harness** (run_tran_ref.py): `python3 run_tran.py <params.json> <tb.sp> <wd> <metrics_out>` → 读 params 生成 params.inc（13 直接 + 8 派生 ui/amp_high/amp_low/sim_time/tstep/twarm/trin/tdelay）→ 拷 DUT/corner/tb → 调 hspice → 解析 .mt0 $DATA1 → metrics.json。
- **.75 HSPICE V-2023.12-SP1-1 真跑 GT**:
  - A(vdd=0.8,CL=20f,RL=3k,CC=15f,ibias=30u,wn=wp=4u,data_rate=7.2e9,swing=0.2,num_bits=256): eye_amp=0.1804V / eye_mid=0.0005 / outcm_avg=0.286V / |pwr|=8.27uW / td_plh=-1.43ns / td_phl=8.10ns
  - B(vdd=1.0,CL=50f,RL=5k,CC=30f,ibias=50u,wn=6u/wp=3u,data_rate=5e9,swing=0.3,num_bits=200): eye_amp=0.4552V / outcm_avg=0.404V / |pwr|=52.2uW —— A/B 全异（eye_amp 差 2.5x，跨输入守卫成立）
- **.75 排雷 4 处**: (1) `.SUBCKT name nodes PARAMS: ...` 的 PARAMS 必须与 .SUBCKT 同行（`+ PARAMS:` 续行被当成 subckt 名报 not found）→ 改用 global .param；(2) corner.lib 须 `.lib 'corner.lib' tt` 选择（`.inc 'corner.lib'` 只定义不激活，MOS model not found）；(3) LFSR taps 内联 `[15,14]`，不能 `.param prbs_taps='[15,14]'` 传入；(4) td/edge 的 .MEAS TRIG/TAG 在 PRBS 上脆弱（RISE=1 可能跨不同 bit，td 可能为负或 >ui）→ check 用"有限(<1ms)"而非紧上界，warm-up 用 tdelay=8*ui + FROM='twarm'。
- **check.py 16 条断言 a-p**: a 三件齐 / b py_compile / c 14 键有限 / d LFSR 非 PRBS / e eye_amp∈(0,vdd] / f |eye_mid|<0.5*eye_amp / g outcm∈[0.1,0.9]vdd / h |pwr|∈[1nW,10mW] / i td<1ms / j edge<1ms / k |ovsh/unsh|<3*eye_amp / l .MEAS≥12 / m .TRAN 存在 / n 反打印期望(±5%) / o 跨输入守卫(B≠A 10% + B≈ref 30%) / p 反空壳。
- **自验 (.75 端到端)**: ref **PASS**(16/16) + 5 neg 全 FAIL(NEG_RC=0): naive_empty→d / naive_hardcode_a→o(跨输入) / naive_prbs→d / naive_no_meas→l / naive_fabricate→e(eye_amp=1.0>vdd)。§4.9 三假(空壳/打印期望/掏空.MEAS)全 FAIL。test 字段==disk check.py md5 281427ce1c6abfbbcbc834bd08a86976, 9820B, roundtrip OK。断言闸门 k_rationale=k_check=16≥8 ✓。

## 候选池（下轮选 fresh trace）
trace_ledger.py --shard B next 已排除 2tuxj。候选（kaixuanx 其他 spice 会话 + 高 mc spice_sim）：g48q/b86q7/qr1lv/z6mt7/j8vf6/i5ae7/j8f3i 等。
