#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r833 (2026-11-18) metadata-debt backfill 档3 (reframe_note) batch8.
Source: r825 bounded queue 提议 (reframe_note backfill 160 missing P1).
        r826 batch1 +12 (235->247, miss 160->148).
        r827 batch2 +12 (247->259, miss 148->136).
        r828 batch3 +12 (259->271, miss 136->124).
        r829 batch4 +12 (271->283, miss 124->112).
        r830 batch5 +12 (283->295, miss 112->100).
        r831 batch6 +12 (295->307, miss 100->88).
        r832 batch7 +12 (307->319, miss 88->76).
        本轮 batch8 = alphabetical 续 12 missing after PlatInvsThick (r832 batch7 末位),
        起算 PorCapSweep, P->Q->R 段.
        reframe_note 319->331, miss 76->64.

Spec: r773-r800 档3 batch9-34 完成 reframe_note 32->235 (driver 三分 portability/Q&A-analysis/harness
      互斥可枚举归类). r826-r833 await-scan 期接续 backfill reframe_note 160 missing.
      本轮 batch8 12 case = 10 keep_reframe portability + 1 keep_reframe harness + 1 keep_faithful.

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False。
       仅补 reframe_note, 不动 test_rationale/check.py/negative/asset_fidelity (asset_fidelity r824 已 100% 收口)。

Driver 分类 (12 case: 10 keep_reframe portability + 1 keep_reframe harness + 1 keep_faithful):
  - portability-driver (foundry PDK / real HSPICE/FineSim deck+netlist / real PWL export 不可沙盒复刻 -> synth_deck / synth_data):
      10 case: PorCapSweep (real HSPICE por_testbench 行为源三目比较器 timestep collapse 不可复刻->synth_data, spice_sim) /
               PostSimDeckBatch (real goldenPostSim.sp 模板+PVT CSV+FineSim env 不可复刻->synth_deck, spice_sim) /
               PostsimToggleDiag (real FineSim netlist+FSDB 波形不可复刻->synth_deck, spice_sim) /
               PowerNoiseInject (real FineSim testbench 不可复刻->synth_deck, spice_sim) /
               PulseStimTbGen (real Spectre inv_20260922 netlist+scs env 不可复刻->synth_deck, 仿真器 Spectre->HSPICE 适配, spice_sim) /
               PvtCornerSubsetGen (real tck_clk.sp+pvt_alter 不可复刻->synth_deck, spice_sim) /
               PvtInvChainDelayMeas (real delay_test.sp+netlist.sp 不可复刻->synth_deck, spice_sim) /
               PwlFormatConvert (real WaveView PWL 导出文件不可复刻->synth_data, spice_sim) /
               PwlStimTransform (real inpattern_origin.pwl+DRAM XdecGapTop netlist 不可复刻->synth_deck, spice_sim) /
               R1R4NetlistCheck (real /proj/dscqa netlist permission-denied 不可复刻->synth_deck, spice_sim)
  - harness-driver (multi-round evolution trace -> single produce-action condensation for check teeth):
      1 case: QueueCorePolicyPatch (real anasim_pro PyQt5 GUI runsim_control.py 多轮演进需求 U#1-U#5 -> 单轮 produce-action 收敛 + hidden-B cross-input, spice_sim)
  - keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful):
      1 case: ProbeStimFromSx (A-faithful, WaveView .sx session 是 ASCII 文本 scp 便携, .probe 块生成同形)

P->Q->R 段 domain-wave 观察: batch8 keep_faithful 占比 8% (1/12) 显著低于 batch7 N段 50%,
  因 P 段 (PorCapSweep/PostSim*/PowerNoise/PulseStim/Pvt*/Pwl*) 多为 real HSPICE/FineSim deck+netlist
  不可便携须合成 -> portability-driver 主流, 与 N段 Netlist* 群 (SPICE 网表文本 scp 便携 -> A-faithful) 对比.
  Q 段 (QueueCorePolicyPatch) 是 GUI source 不可复刻 + 多轮演进 -> harness-driver (本批次唯一 harness).
  R 段起 (R1R4NetlistCheck) real /proj netlist permission-denied -> portability-driver.
  portability-driver 二分族延续: P 段 deck-generator 族 (synth_deck, 生成可跑 deck) vs 后处理族 (synth_data, PorCapSweep/PwlFormatConvert 解析 real .mt0/PWL 导出).

metadata bug 待 @A 档1/档2 sweep (reframe_note scope 限定不修, 仅在 note 文本标注):
  - 多 case layer 缺标或标 L2 待复核(check 仅 subprocess 跑候选 python 解析文本/生成 deck, 0 EDA 二进制, 应 L1)
  - level/k_check/shard 字段缺标
  - 与 r773-r800/r826-r832 档3 同口径: reframe_note backfill 不动其他字段
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    # ===== 10 keep_reframe_for_teeth (portability-driver) =====
    "EDA-Eval-DesignFlow-PorCapSweep-001":
        "POR 上电延迟 vs MIM/MOM 电容值扫描仿真 pattern 生成->produce (portability-driver reframe + 收敛安全子技能提取, real HSPICE por_testbench 行为源三目比较器 timestep collapse 不可沙盒复刻->synth_data, §4 有牙必要, r833 reframe_note backfill batch8): 用户 karlwang@hfeg0plg71 (sess 1792722208192_uqv1k, mc=312, spice_sim 域) 要 'nicap值对上电速度影响的parttern', 澄清为 MIM/MOM 电容研究容值对 POR 延迟影响; real trace cline 用 HSPICE 生成 por_testbench, 但行为 B 源三目比较器 (V='V(vcap)>vref?vdd:0') 导致 timestep collapse 全 abort, 仅 minimal RC 测试跑通; A 不可行原因=real HSPICE testbench 行为源三目比较器收敛失败不可沙盒复刻 -> 收敛为 por_cap_sweep_gen.py(读 hidden B synth RC cap sweep spec, asset_fidelity=synth_data); reframe 由 portability-driver(real testbench 不可复刻) + 收敛安全子技能提取(取纯 RC + .measure WHEN V(vcap)=vref + .alter cap sweep 子技能, 弃行为源三目比较器); 意图核心(容值扫描 .alter + RC 上电 + .measure WHEN V(vcap)=vref 测 trip delay + delay_vs_cap 数据收集)完整保留; check.py 14 断言验 zip 含 por_cap_sweep_gen.py+delay_vs_cap_A.json + py_compile + gen.py 在 hidden B 上 exit0 产 delay_vs_cap.json + deck 含 .measure tran t_trip 且直接测 V(vcap)(收敛安全非行为源) + deck 无行为 B 源三目比较器 + .alter cap sweep + delay_vs_cap 数据点数=cap 值数 + cross-input guard(A≠B spec 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 仅 subprocess 跑候选 python 生成 deck 文本+解析 JSON, 0 EDA 二进制 run, 应 L1), level 缺标应 L1, k_check 字段缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-PostSimDeckBatch-001":
        "后仿仿真环境批量生成: GenSPPostSim.py 读 PVT CSV 对 goldenPostSim.sp 模板做参数替换批量生成后仿 FineSim deck->produce (portability-driver reframe, real goldenPostSim.sp 模板+PVT CSV+FineSim env 不可沙盒复刻->synth_deck, §4 有牙必要, r833 reframe_note backfill batch8): 用户 reedchen@hfeg0pkn002 (sess 1792390745145_31s8i, mc=37, spice_sim 域) 在 /rundata/ddgoa/.../simulation/ 做 DbusDriver 模块级后仿, 仿照前仿 GenSP.py 用 goldenPostSim.sp 模板批量生成后仿 FineSim deck(PVT 角点替换+stress/MC 开关+Read/Write 段重写); trace 282 msgs 单 prompt 闭环, agent 探索 GenSP.py/goldenPostSim.sp/PVT CSV 后 editor 分块写出 GenSPPostSim.py(含 apply_pvt/apply_stress/apply_mc/rename); A 不可行原因=real goldenPostSim.sp 模板+PVT CSV+FineSim env 不可沙盒复刻 -> 收敛为 GenSPPostSim.py(读 hidden B synth golden 模板+PVT CSV, asset_fidelity=synth_deck); reframe 由 portability-driver(real 模板+env 不可复刻); 意图核心(PVT CSV parse + golden 模板参数替换 + stress/MC 开关 + Read/Write 段重写 + 批量 deck 生成)完整保留; check.py 15 断言验 zip 含 GenSPPostSim.py + py_compile + B config1(read/wp/stress) exit0 产 5 个 deck 文件 + 文件名符合 pvt_tag 约定(TT_1.2V25C.sp/SS_1.08V-40C.sp/...) + cross-input guard(A≠B PVT 表不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 生成 deck 文本, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 15, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-PostsimToggleDiag-001":
        "FineSim post-sim FSDB 波形诊断+netlist cross-ref: 读 .pt0/.fsdb 提 signal list+per-signal toggle, 识别 stuck/active/missing net->produce (portability-driver reframe, real FineSim netlist+FSDB 波形不可沙盒复刻->synth_deck, §4 有牙必要, r833 reframe_note backfill batch8): 用户 easont@hfhds207 (sess 1793078405436_t0aom, mc=650, spice_sim 域) 跑完 DDR6 DDGOA 子模块 FineSim 后仿(tt0.94v45c corner), 用 .option post=1+.print tran v(...) 把关注节点打到 .pt0, 看波形怀疑信号 stuck + 网表声明却未 .print 探测(missing); A 不可行原因=real FineSim netlist+FSDB 波形不可沙盒复刻 -> 收敛为 postsim_toggle_diag.py(读 hidden B synth netlist+spec, asset_fidelity=synth_deck); reframe 由 portability-driver(real netlist+FSDB 不可复刻); 意图核心(FineSim 真跑 + .pt0 parse + per-signal toggle 统计 + stuck/active/missing 分类 + report.json 结构化)完整保留; check.py 15 断言验 zip 含 postsim_toggle_diag.py + py_compile + 候选在 hidden B 上真跑 FineSim(simB.log 含 banner+Successfully Completed) + report.json schema 完整 + cross-input guard(A≠B netlist 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess(含 FineSim 真跑)结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确(check 验 FineSim 真跑含 EDA 二进制), level 缺标应 L2, k_check=15 已标 ✓, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-PowerNoiseInject-001":
        "VSS 电源噪声生成+注入 FineSim .sp testbench(原 sine Vsource 替换为 VPWL 噪声源)->produce (portability-driver reframe, real FineSim testbench 不可沙盒复刻->synth_deck, §4 有牙必要, r833 reframe_note backfill batch8): 用户 joeyl@hfeg0plg74 (sess 1790580241881_fbdaa, mc=10, spice_sim 域) 在 /home/joeyl/noise_generator/ 要求生成 vss! 电源噪声并注入仿真 testbench .sp(noise_spec.json 给目标 net/幅度/频率分量/时长/步长, target_tb.sp 待注入 FineSim testbench, vss! 节点当前由 sine 源驱动); A 不可行原因=real FineSim testbench 不可沙盒复刻 -> 收敛为 noise_inject.py(读 hidden B synth spec+deck, asset_fidelity=synth_deck); reframe 由 portability-driver(real testbench 不可复刻); 意图核心(PWL 噪声数据生成 + sine Vsource 替换为 VPWL + 目标 net 定位 + .tran 保留 + 其他电路元件保留)完整保留; check.py 12 断言验 zip 含 noise_inject.py 且 py_compile 通过 + 候选在 B(spec+deck)上 exit0 产 out.sp + out.sp 含 VPWL 源在 B 目标 net 上 + B 目标 net 原 sine 源已移除 + PWL 点数=duration/timestep+1 + PWL 时间覆盖[0,duration] + PWL 幅度在 spec 界限内 + .tran 语句保留 + 其他电路元件保留 + cross-input guard(A≠B spec 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标应 L1(check 仅 subprocess 跑候选 python 生成 deck 文本, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 12, shard 缺标应 B, mc=10 在阈值边界 host-verify 待 @A 复核。",

    "EDA-Eval-DesignFlow-PulseStimTbGen-001":
        "脉冲瞬态 testbench 生成: 反相器网表加 1v pulse(pulse width 1us/period 2us/tran 10us)+.measure tpd->produce (portability-driver reframe + 仿真器适配, real Spectre inv_20260922 netlist+scs env 不可沙盒复刻->synth_deck, Spectre->HSPICE 适配, §4 有牙必要, r833 reframe_note backfill batch8): 用户 qifanli@hfeg0plg101 (sess 1790143934595_0nar3, mc=41, spice_sim 域) 对 Spectre 反相器网表(inv_20260922, ntn/ptn, W=150nm L=36nm) 提脉冲瞬态 testbench 生成请求 'add 1v pulse signal to the above inverter, pulse width 1us, period 2us, and transient simulation time 10us'; trace agent read_files 找既有 sim_inv.scs 后 editor 写 inv_20260922_tb.scs; A 不可行原因=real Spectre netlist+scs env 不可沙盒复刻 -> 收敛为 pulse_stim_tb_gen.py(读 hidden B synth HSPICE level-1 inv netlist+spec, asset_fidelity=synth_deck); reframe 由 portability-driver(real Spectre netlist+env 不可复刻) + 仿真器适配(Spectre scs->HSPICE .sp); 意图核心(脉冲 vsource pulse 参数 + .tran + 负载电容 + .measure tpd + inv 网表例化)完整保留; check.py 15 断言验 zip 含 pulse_stim_tb_gen.py + py_compile + 候选在 hidden B 产 testbench.sp 含 .tran + B deck input 脉冲 vsource 参数正确 + cross-input guard(A≠B spec 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(若 check 验 HSPICE 真跑则 L2 正确, 若仅生成 deck 文本应 L1), level 缺标应 L2 或 L1, k_check 字段缺标应 15, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-PvtCornerSubsetGen-001":
        "PVT 角点子集选取: 从 tck_clk.sp+pvt_alter 选 10 corner 生成 tck_clk_10corner.sp+run 仿真->produce (portability-driver reframe, real tck_clk.sp+pvt_alter 不可沙盒复刻->synth_deck, §4 有牙必要, r833 reframe_note backfill batch8): 用户 sophiaw@hfeg0plg09 (sess 1788513689914_ayl62, mc=46, spice_sim 域) 在 tck_clk(PumpOsc Vdd1)PVT 角点仿真验证任务上(/rundata/ieda_agent_test/weihan/v1_vddsoc/), U#2 原话 '请从tck_clk.sp 中选出10个corner, 生成一个新的命名为tck_clk_10corner.sp'; trace agent 先读 tck_clk.sp(119行)+tck_clk_alter(779行/65 PVT 角点)后选 10 corner 生成新 deck+run; A 不可行原因=real tck_clk.sp+pvt_alter 不可沙盒复刻 -> 收敛为 pvt_corner_subset_gen.py(读 hidden B synth tck_clk.sp+alter, asset_fidelity=synth_deck); reframe 由 portability-driver(real deck+alter 不可复刻); 意图核心(.alter 块 parse + 10 corner 选取 + 新 deck 生成 + run script 生成)完整保留; check.py 13 断言验 zip 含 pvt_corner_subset_gen.py + py_compile + 候选在 hidden B1 exit0 产 out_alter+out_sp+out_runsim.sh + B1 out_alter 含恰好 K=10 个 .alter 块 + cross-input guard(A≠B 选 corner 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 生成 deck 文本, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 13, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-PvtInvChainDelayMeas-001":
        "25 级反相器链 IN->OUT PVT 传播延迟测量: delay_test.sp 单脉冲激励+空 .measure 改为连续方波+多边沿 .measure tran->produce (portability-driver reframe, real delay_test.sp+netlist.sp 不可沙盒复刻->synth_deck, §4 有牙必要, r833 reframe_note backfill batch8): 用户 curryxu@hfeg0plg07 (sess 1794292585610_1ojna, mc=148, spice_sim 域) 测量 25 级 invFx1_sub_Fifo 反相器链 IN->OUT 在不同 PVT corner(TT/FF/SS × -40/25/125℃)下的传播延迟, delay_test.sp 当前单脉冲激励+空 .measure 段需改为连续方波+多边沿 .measure tran 量测; A 不可行原因=real delay_test.sp+netlist.sp 不可沙盒复刻 -> 收敛为 pvt_delay_meas_gen.py(读 hidden B synth delay_test.sp+netlist, asset_fidelity=synth_deck); reframe 由 portability-driver(real deck+netlist 不可复刻); 意图核心(连续方波激励 + .measure trig v(IN)/targ v(OUT) + rise=/fall= 量测 + 5 PVT corner .alter 链)完整保留; check.py 12 断言验 zip 含 pvt_delay_meas_gen.py + py_compile + 候选在 hidden B1 exit0 产 out_deck.sp+out_report.json + B1 deck 含 .measure trig v(IN)/targ v(OUT) + B1 deck 同时含 rise=/fall= 量测 + cross-input guard(A≠B spec 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 生成 deck 文本, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 12, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-PwlFormatConvert-001":
        "Custom WaveView SPICE PWL 导出文件批量格式转换(去 header/PWL 包裹/时间归零/电流取反)->produce (portability-driver reframe, real WaveView PWL 导出文件不可沙盒复刻->synth_data, §4 有牙必要, r833 reframe_note backfill batch8): 用户 hauserz@hfeg0pkn006 (sess 1793705585219_k1vy6, mc=131, spice_sim 域) 让 cline 将 Custom WaveView SPICE PWL 导出文件(iddd0_vintlp_current_TT_1p1v 等)转化为与 idd0_vblhh_current_ipwl 相同的纯数据格式; 后续逐轮细化: 时间从 0 开始(减首点偏移)+电流方向反向(乘 -1)+批量处理工作目录下所有 *1p1v 文件; 金标准 batch_all_1p1v.py 去 *** header/PWL( 包裹/+ 前缀/+) 尾, 时间归零, 电流取反, 输出 <name>_ipwl; A 不可行原因=real WaveView PWL 导出文件不可沙盒复刻 -> 收敛为 batch_pwl_convert.py(读 hidden B synth PWL 导出文件, asset_fidelity=synth_data); reframe 由 portability-driver(real PWL 导出文件不可复刻); 意图核心(纯数据格式去 header/PWL 包裹 + 时间归零减首点 + 电流取反 + 批量处理)完整保留; check.py 12 断言验 zip 含可执行 .py + py_compile + B1 上 exit0 产输出目录含 _ipwl 文件 + 输出纯数据格式(无 ***/PWL(/+ 前缀/+)尾) + 首行时间=0.00000E+00 + 电流反转(输出=-输入, 容差 1e-12) + cross-input guard(A≠B 文件不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标应 L1(check 仅 subprocess 跑候选 python 解析+转换文本数据, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 12, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-PwlStimTransform-001":
        "DRAM XdecGapTop DRCOA schematic ALPS 仿真 PWL 激励变换: net 名匹配+高电平 x*pvwlp/pvcc 表达式+噪声阈值裁剪+保留中间产物->produce (portability-driver reframe, real inpattern_origin.pwl+DRAM XdecGapTop netlist 不可沙盒复刻->synth_deck, §4 有牙必要, r833 reframe_note backfill batch8): 用户 hairuizh@hfeg0pkn002 (sess 1793677026220_gm1z2, mc=193, spice_sim 域) 为 DRAM XdecGapTop DRCOA schematic ALPS 仿真做 PWL 激励变换: 给 inpattern_origin.pwl, 要求 4 步——改 net 名匹配 netlist 顶层信号并记录映射; 高电平~3.2V 写成 x*pvwlp 形式(单引号)、~1.1V 用 pvcc; <0.1*pvwlp→0、>0.9*pvwlp→pvwlp(pvcc 同); 保留中间产物 inpattern_map.pwl/inpattern_map_vol.pwl/inpattern_map_vol_nonoise.pwl; A 不可行原因=real inpattern_origin.pwl+netlist 不可沙盒复刻 -> 收敛为 pwl_stim_transform.py(读 hidden B synth pwl+netlist, asset_fidelity=synth_deck); reframe 由 portability-driver(real pwl+netlist 不可复刻); 意图核心(net 名映射 + x*pvwlp/pvcc 表达式替换 + 噪声阈值裁剪 + 中间产物保留)完整保留; check.py 12 断言验 zip 含 pwl_stim_transform.py + py_compile + --help exit0 打印 usage + 在 A 上 exit0 产 4 个非空产物 + cross-input guard(A≠B pwl 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 仅 subprocess 跑候选 python 变换 PWL 文本, 0 EDA 二进制 run, 应 L1), level 缺标应 L1, k_check 字段缺标应 12, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-R1R4NetlistCheck-001":
        "netlist R1-R4 静态检查(电压域枚举/跨域驱动/扇出/备件充足性)统一脚本 run_netlist_checks.py->produce (portability-driver reframe, real /proj/dscqa netlist permission-denied 不可沙盒复刻->synth_deck, §4 有牙必要, r833 reframe_note backfill batch8): 用户 tongni@hfeg0plg001 (sess 1794217104209_s97ck, mc=160, spice_sim 域) 调用 sim-sp-gen skill 对 dscqa_analog_AG_VisoRef_schematic.netlist 与 AI_test_sim_logic_test_1_schematic.netlist 做 R1-R4 静态检查, agent 运行 run_netlist_checks.py 产合并报告 .txt; A 不可行原因=real /proj/dscqa+/rundata/dscqa netlist 对 e0031982 permission-denied 不可沙盒复刻 -> 收敛为 run_netlist_checks.py(读 hidden B synth netlist, asset_fidelity=synth_deck); reframe 由 portability-driver(real netlist permission-denied 不可复刻); 意图核心(R1 顶层 cell 电压域枚举 + R2 跨域直接驱动风险 + R3 stdcell 扇出 + R4 spare 充足性 + 合并报告 stdout)完整保留; check.py 13 断言验 zip 含可执行 .py + 脚本对 B1/B2/B3 三隐藏 netlist 均 exit0 且 stdout 非空 + stdout 含 R1/R2/R3/R4 四 section + B1 R1 检出 AG_Spare/invLx1/nand2Lx1 三顶层 cell 全 VCC 域 + B2 R1 检出 invVx2 含 vdd1 + cross-input guard(A≠B netlist 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 解析网表文本+规则检查, 0 EDA 二进制), level 缺标应 L1, k_check=13 已标 ✓, shard 缺标应 B。与 NetlistStaticCheck-001(batch7, tongni@hfeg0pkn004/sess nj8q4/mc=150)不同 session+不同设计 netlist, 非近重复, 各自保留。",

    # ===== 1 keep_reframe_for_teeth (harness-driver) =====
    "EDA-Eval-DesignFlow-QueueCorePolicyPatch-001":
        "anasim_pro PyQt5 HSPICE 仿真提交 GUI runsim_control.py 队列->核心数策略 patch->produce (harness-driver reframe, real 多轮演进 U#1-U#5 trace -> 单轮 produce-action 收敛 + hidden-B cross-input for check teeth, real anasim_pro source 不可沙盒复刻->synth_deck, §4 有牙必要, r833 reframe_note backfill batch8): 用户 yanxvwei@hfeg0pkn002 (sess 1793957358059_v5icx, mc=71, spice_sim 域) 在 anasim_pro(PyQt5 HSPICE 仿真提交 GUI) 的 runsim_control.py 上多轮演进需求: U#1 问 Run 按钮执行什么命令/线程数如何定义(诊断咨询); U#2 'queue 为 fqueue2h 时 core_spinbox 设为 1, 先告诉我改哪些代码'; U#3 '做修改1,2, 只做选中 fqueue2h 时设为 1, 用户仍可手动改大, 权限已开'; U#4 '继续改, 如果不是 fqueue2h 默认为 6'; U#5 '将 fqueue3_ams2 的 core 也设为 1, 权限已开'; A 不可行原因=多轮演进非单轮自包含提需求(真实 trace 是 U#1 诊断咨询+U#2-U#5 增量 patch 5 轮交互, 非 A-faithful 可单轮复刻形态) + real anasim_pro source 不可沙盒复刻 -> 收敛为 runsim_control.py 单轮 produce-action patch(hidden B 给完整 source+policy spec, asset_fidelity=synth_deck); reframe 由 harness-driver(多轮演进->单轮 produce-action 收缩 + hidden-B cross-input 让 check() 能区分真假 patch, 真实 trace 多轮交互无法 A-faithful 单轮化); 意图核心(on_queue_selected 队列->core 策略 + refresh_lsf_queues 重选后重新应用策略 + fqueue2h/fqueue3_ams2->1 + 非 fqueue2h 默认 6 + 用户可手动改大)完整保留; check.py 20 断言验 zip 含 runsim_control.py + py_compile + 存在 on_queue_selected 方法 + 存在 refresh_lsf_queues 方法 + refresh_lsf_queues 内调用 on_queue_selected + fqueue2h 选中 core 设 1 + fqueue3_ams2 选中 core 设 1 + 非 fqueue2h 默认 6 + 用户可手动改大(权限不锁死) + cross-input guard(A≠B policy spec 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 真跑结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 解析+patch GUI 源码文本, 0 EDA 二进制), level 缺标应 L1, k_check=20 已标 ✓, shard 缺标应 B。**注**: 本 case 是 batch8 唯一 harness-driver, 区别于 portability-driver(real artifact 不可复刻)——harness-driver 的 reframe 主因是多轮演进 trace 无法 A-faithful 单轮化, 须收缩为单轮 produce-action + hidden-B 让 check 有牙。",

    # ===== 1 keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful) =====
    "EDA-Eval-DesignFlow-ProbeStimFromSx-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r833 reframe_note backfill batch8): 用户 reneeg@hfeg0plg53 (sess 1793273304598_nunyc, mc=117, spice_sim 域) 做 Finesim 后仿 zq 校准电路, 原 input.sp 用 .probe V(*) 存所有电压致 FSDB 过大, 要求改成只存 WaveView session(4DP_2.sx)里实际查看的信号; 金标准=从 .sx 的 cvt_a2d name=v(sig) 提取信号->逐 bit 展开总线(去 <hi:lo>)->V(...) 包裹、层次用 . 分隔->生成 Finesim 选择性 .probe 块替换 .probe V(*); trace 首版误用向量 <5:0>/嵌套 v() 触发 Finesim syntax error, 修正为逐 bit+V(path.sig); 意图形态=produce-action(选择性 .probe 激励块生成), 可便携性=高(WaveView .sx session 是 ASCII 文本可 scp 便携, 非 FSDB 二进制, asset_fidelity=A-faithful); case 交付 gen_probe_stim.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-action 是合法任务形态, trace 意图 '改 .probe V(*) 为只存 .sx 里查看的信号' 与 case 交付 .probe 块生成器同形映射, asset A-faithful 因 .sx ASCII 便携); check.py 14 断言验 zip 含 gen_probe_stim.py + py_compile + 候选在 B1(hidden_b1.sx)跑出非空输出 + 输出为 Finesim .probe 格式(首行 .probe 起始, 续行 + 起始) + 输出不含 .probe V(*) 全存通配 + 输出不含向量 <hi:lo> 写法(总线已逐 bit 展开) + 每个信号 V(...) 包裹 + 层次用 . 分隔 + cross-input guard(A≠B .sx 不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L1, k_check=14==k_rationale=14 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 解析 .sx 文本生成 .probe 块, 0 EDA 二进制), level 缺标应 L1, k_check=14 已标 ✓, shard 缺标应 B。",
}


def main():
    applied = 0
    skipped = []
    for case_id, note in REFRAME_NOTES.items():
        path = os.path.join(CASES_DIR, f"{case_id}.json")
        if not os.path.exists(path):
            skipped.append((case_id, "MISSING FILE"))
            continue
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        md = d.get("metadata", {})
        if "reframe_note" in md:
            skipped.append((case_id, "ALREADY HAS reframe_note"))
            continue
        # insert reframe_note as last metadata key, preserve existing order
        md["reframe_note"] = note
        d["metadata"] = md
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        applied += 1
        print(f"  APPLY {case_id}")
    print(f"\nApplied: {applied} / Skipped: {len(skipped)}")
    for cid, why in skipped:
        print(f"  SKIP {cid}: {why}")


if __name__ == "__main__":
    main()
