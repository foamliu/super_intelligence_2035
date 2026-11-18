#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r837 (2026-11-18) metadata-debt backfill 档3 (reframe_note) batch12.
Source: r825 bounded queue 提议 (reframe_note backfill 160 missing P1).
        r826 batch1 +12 (235->247)   r827 batch2 +12 (247->259)
        r828 batch3 +12 (259->271)   r829 batch4 +12 (271->283)
        r830 batch5 +12 (283->295)   r831 batch6 +12 (295->307)
        r832 batch7 +12 (307->319)   r833 batch8 +12 (319->331)
        r834 batch9 +12 (331->343)   r835 batch10 +12 (343->355)
        r836 batch11 +12 (355->367, miss 40->28)
        本轮 batch12 = alphabetical 续 12 missing after SpfAutosimSetup-001
        (r836 batch11 末位), 起算 Sram6tDcChar, S->T 段.
        reframe_note 367->379, miss 28->16.

Spec: r773-r800 档3 batch9-34 完成 reframe_note 32->235 (driver 三分 portability/Q&A-analysis/harness
      互斥可枚举归类). r826-r837 await-scan 期接续 backfill reframe_note 160 missing.
      本轮 batch12 12 case = 9 keep_reframe portability + 3 keep_faithful.

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False。
       仅补 reframe_note, 不动 test_rationale/check.py/negative/asset_fidelity (asset_fidelity r824 已 100% 收口)。

Driver 分类 (12 case: 9 keep_reframe portability + 3 keep_faithful):
  - portability-driver (real sim deck/netlist/PDK/.sx 不可沙盒复刻 -> synth_*; 或 WaveView GUI 不可复刻但导出文本便携 -> A-faithful export-header-real):
      9 case: Sram6tDcChar (real Solido+HSPICE 6T SRAM DC char deck 不可复刻->synth_deck, characterization, L2) /
              SramIreadGen (real PDK hspiceD+SRAM netlist 不可复刻->synth_deck, characterization, L2) /
              StimLoopComplianceFix (real FineSim stimulus deck 不可复刻->synth_deck, spice_sim, L2) /
              StimPWL (real WaveView GUI 不可复刻但 PWL 导出文本便携->A-faithful export-header-real sub-family, spice_sim, L2; **track=synthesized 但 asset=A-faithful mismatch 待 @A**) /
              SwitchChgDchVerif (real DRAM power switch netlist+HSPICE run 不可复刻->synth_deck, spice_sim, L2) /
              SwitchTbGen (real R_GidlAryCtrl_switch netlist 不可复刻->synth_deck, spice_sim, L1) /
              TaperBufOpt (real DRAM taper buffer netlist+HSPICE run 不可复刻->synth_deck, spice_sim, L2) /
              ThoxVthExtract (real CXMT V1_HKMG PDK 模型 65K+行 不可复刻->synth_deck, characterization, L2) /
              TimingMeasGen (real .sx 信号文件含项目专属信号名 不可复刻->synth_data, spice_sim, L2)
  - keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful):
      3 case: StrongarmBaselineAnalyze (FineSim .mt0 baseline 导出文本便携, produce-tool 分析, asset=A-faithful, track=faithful, characterization, L1) /
              SubcktInstParamInj (用户显式要 Python 脚本注入参数, real netlist 文本便携, produce-action, asset=A-faithful, track=faithful, spice_sim, L1) /
              SvUsedModelExtract (real .v/.sv 文本便携, produce-tool 提取 used model, asset=A-faithful, track=faithful, spice_sim, L1)

S->T 段 domain-wave 观察: batch12 keep_faithful 占比 25%(3/12) 高于 batch11 17% + batch8/batch10 P/S 段 8%,
  因 S->T 段含三类文本便携 asset(.mt0 FineSim 导出 / netlist 文本 / .v/.sv 文本) -> A-faithful 主流可便携;
  portability-heavy 75%(9/12, 7 synth_deck + 1 synth_data + 1 A-faithful export-header-real);
  Q&A-analysis 0/12=0% + harness-driver 0/12=0% (本段无 diagnosis/多轮交互形态);
  S->T 段 spice_sim 域 8/12=67% + characterization 域 4/12=33% (characterization 回流显著高于 batch11 8%,
  因 Sram6tDcChar/SramIreadGen/StrongarmBaselineAnalyze/ThoxVthExtract 四 case 均为 characterization 域).
  track≠asset_provenance mismatch 累计: batch12 内 6 例(Sram6tDcChar/StimPWL/SwitchChgDchVerif/SwitchTbGen/TaperBufOpt/TimingMeasGen), r836 累计 62 -> 68 待 @A 档2 sweep.
  export-header-real sub-family 延续(承 r829 §观点(3) + r836): StimPWL WaveView PWL 导出文本便携但 WaveView GUI 不可复刻 -> asset A-faithful + track=synthesized, 与 r813/r818/r819 DSIM/AETHER-SE/StarRC DSPF export header 族同构.

metadata bug 待 @A 档1/档2 sweep (reframe_note scope 限定不修, 仅在 note 文本标注):
  - layer 缺标应补: Sram6tDcChar=L2(check 真跑 HSPICE) / SvUsedModelExtract=L1(check 仅 subprocess python) / TaperBufOpt=L2(check 真跑 HSPICE)
  - k_check/k_rationale 缺标应补: Sram6tDcChar=14/SramIreadGen=13/StimLoopComplianceFix=15/StimPWL=15/StrongarmBaselineAnalyze=16(已标)/SubcktInstParamInj=12/SvUsedModelExtract=14(已标)/SwitchChgDchVerif=14/SwitchTbGen=12/TaperBufOpt=16/ThoxVthExtract=14/TimingMeasGen=14
  - track 缺标或 mismatch 应补: Sram6tDcChar track=faithful 但 asset=synth_deck 应 synthesized / SramIreadGen track 缺标应 synthesized / StimPWL track=synthesized 但 asset=A-faithful (两轴正交, mismatch 待 @A) / SwitchChgDchVerif track=faithful 但 asset=synth_deck 应 synthesized / SwitchTbGen track=faithful 但 asset=synth_deck 应 synthesized / TaperBufOpt track=faithful 但 asset=synth_deck 应 synthesized / ThoxVthExtract track=synthesized ✓ / TimingMeasGen track=faithful 但 asset=synth_data 应 synthesized / StrongarmBaselineAnalyze track=faithful ✓ / SubcktInstParamInj track=faithful ✓ / SvUsedModelExtract track=faithful ✓
  - shard 缺标应 B (全 12 case shard=None 或缺标)
  - 与 r773-r800/r826-r836 档3 同口径: reframe_note backfill 不动其他字段
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    # ===== 9 keep_reframe_for_teeth (portability-driver) =====
    "EDA-Eval-DesignFlow-Sram6tDcChar-001":
        "6T SRAM bitcell DC 表征(Solido+HSPICE 跨 PVT 角测 WNM 蝴蝶曲线两方向/iread/iwrite/ileak, 修正 Solido stimulus 多 bug)->produce (portability-driver reframe, real Solido+HSPICE 6T SRAM DC char deck+netlist 不可沙盒复刻->synth_deck, §4 有牙必要, r837 reframe_note backfill batch12): 用户 e0030760@hfeg0pkn002 (sess 1793177580229_11fst, mc=175, characterization 域) 用 Solido+HSPICE 给 SRAM 6T bitcell(BitCell_FS_CH336)做 DC 表征, 跨 PVT 角跑 .alter, 测 WNM(wnm_1/wnm_2 蝴蝶曲线两方向)/iread/iwrite/ileak, 修正 Solido 自动 stimulus 多 bug(corner 缺 localMC/IV7 悬空/.tran 残留/wnm_2 测量失败/iwrite 探针 BL 恒定); A 不可行原因=real Solido+HSPICE 6T SRAM DC char deck+netlist 不可沙盒复刻(项目路径+foundry PDK+Solido 工具链) -> 收敛为 sram_6t_dc_char.py(读 hidden B synth_deck, asset_fidelity=synth_deck); reframe 由 portability-driver(real Solido+HSPICE deck 不可复刻); 意图核心(6T bitcell DC 表征 + WNM 蝴蝶曲线两方向 + iread/iwrite/ileak + PVT .alter + Solido stimulus bug 修正)完整保留; check.py 14 断言验 zip 含生成器 .py + 30 个 deck(6 PVT×5 metric) + report.json per_corner 6 条 + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标应 L2(check 真跑 HSPICE 二进制 subprocess.run([HSPICE,...])), k_rationale/k_check 缺标应 14, **track=faithful 但 asset=synth_deck mismatch**(track≠asset_provenance, real Solido+HSPICE deck 不可便携故 asset=synth_deck, track 应为 synthesized), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SramIreadGen-001":
        "SRAM 6T bitcell Iread 仿真 deck 生成(6T bitcell, .ic v(q)=0 v(qb)=vdd 读'0', .tran, .measure iread avg i(vbl))->produce (portability-driver reframe, real PDK hspiceD+SRAM netlist 不可沙盒复刻->synth_deck, §4 有牙必要, r837 reframe_note backfill batch12): 用户 e0017832@hfeg0pkn001 (sess 1793707646524_71h8j, mc=54, characterization 域) USER#4 原话「帮我做一个SRAM bitcell Iread 仿真」, 经 ask_question 确认为 6T SRAM bitcell; assistant 遍历 ~/Desktop/SRAM(35H DBC/FS 工艺, PDK 在 SRAM_0818/TF/0.1.9_test/dbc_vir/35HDBC/ hspiceD 目录), raw run_commands 被 policy 禁用, session 在 msg#47 ask_question 后结束(incomplete session 无用户接受产物); A 不可行原因=real PDK hspiceD+SRAM netlist 不可沙盒复刻(项目 PDK 路径+policy 禁用) -> 收敛为 sram_iread_gen.py(读 hidden B synth_deck 便携 model-free 6T bitcell, asset_fidelity=synth_deck); reframe 由 portability-driver(real PDK hspiceD 不可复刻); 意图核心(6T bitcell Iread 仿真 + .ic 读'0' + .tran + .measure iread avg i(vbl) + VDD corner sweep)完整保留; check.py 13 断言验 zip 含 sram_iread_gen.py + iread_result.json + py_compile + 候选在 hidden B 上 exit0 + hspice_ran=True + iread 数值正确 + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 ✓(候选真跑 HSPICE hspice_ran flag), k_rationale/k_check 缺标应 13, track 缺标应 synthesized(资产 synth_deck 一致), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-StimLoopComplianceFix-001":
        "FineSim stimulus 合规修复(.for/.while 循环展开+PWL R repeat-keyword 单独成行改写+仿真器验证)->produce (portability-driver reframe, real FineSim stimulus deck 不可沙盒复刻->synth_deck, §4 有牙必要, r837 reframe_note backfill batch12): 用户 ghyang@hfeg0pkn003 (sess 1790241654352_5kcuw, mc=41, spice_sim 域) 对 cline 提 FineSim stimulus 合规问题: stimulus 用 .for/.while 循环生成多路输入脉冲+PWL 时钟用 R 重复关键字单独成行, FineSim -spice 把 .for/.while 当 'Unknown command' WARNING 静默忽略(循环体不展开+节点浮空+仿真 Successfully Completed 但结果错), 又把单独成行 R 当 'incomplete resistor r' ERROR 致 Completed with error(s) 终止; A 不可行原因=原 trace 多轮且用户接受分析性输出无 runnable artifact(违反 design_flow submit.zip 契约)+real FineSim stimulus deck 不可复刻 -> 收敛为 stim_loop_compliance.py(读 hidden B synth_deck, DUT=level-1 NMOS/PMOS 反相器链, asset_fidelity=synth_deck); reframe 由 portability-driver(real FineSim deck 不可复刻+原 trace 无 runnable artifact); 意图核心(.for/.while 循环展开为显式 PWL 点 + R repeat-keyword 合规改写 + FineSim -spice 真跑验证)完整保留; check.py 15 断言验 zip 含 stim_loop_compliance.py + py_compile + 候选在 hidden B 上 exit0 产合规 deck + FineSim -spice 真跑无 'Unknown command'/'incomplete resistor' + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 ✓(check 真跑 finesim 二进制 subprocess.run(['finesim','-spice',...])), k_rationale/k_check 缺标应 15, track=synthesized ✓(资产 synth_deck 一致), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-StimPWL-001":
        "LPDDR5 ddgoa 输入激励生成(读 WaveView PWL 导出 si1/si2/si3.sp + signal_map.json, 生成 HSPICE stimulus.sp 8 个 V 源, 紧凑 pwl 格式+固定 DC 直线)->produce (portability-driver reframe, WaveView GUI 不可沙盒复刻但 PWL 导出文本 scp 便携->asset A-faithful export-header-real sub-family, §4 有牙必要, r837 reframe_note backfill batch12): 用户 thqu@hfeg0plg99 (sess 1792495939340_13fwy, mc=211, spice_sim 域) 用 cline(deepseek-v4-flash) 从 WaveView 提取 LPDDR5 ddgoa 设计 R_NegVssIdd_opt_qyh 输入激励: si1/si2/si3.sp 是 WaveView PWL 导出(grensec55/ra16l/ra16h), 指定输入信号 GrEn/SanEn2G/SapEn2GP/Ra16L<1:0>/Ra16H<1:0>/PwrOnLsVwlp, 要求写成 pwl 激励, SanEn2G/SapEn2GP/PwrOnLsVwlp 映射+pwr 拉平 2.71V 直线, 产出 stimulus.sp(8 个 V 源); A 不可行原因=real WaveView GUI 交互不可沙盒复刻(波形提取需 WaveView GUI), 但 PWL 导出文本 si1/si2/si3.sp 是 ASCII scp 便携 -> 收敛为 gen_stimulus.py(读 hidden B A-faithful PWL 导出, asset_fidelity=A-faithful export-header-real sub-family); reframe 由 portability-driver(WaveView GUI 不可复刻, 但 PWL 导出文本便携故 asset A-faithful, 与 r813/r818/r819 export-header-real 族同构); 意图核心(读 PWL 导出 + signal_map 映射 + 8 个 V 源 + 紧凑 pwl 格式 + 固定 DC 直线 + 逐点忠实搬运不截断)完整保留; check.py 15 断言验 zip 含 gen_stimulus.py + py_compile + 候选在 hidden B 上 exit0 产 stimulus.sp + 8 个 V 源 + method=hspice_run + cross-input guard(A≠B PWL 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 ✓(候选真跑 HSPICE method=hspice_run), k_rationale/k_check 缺标应 15, **track=synthesized 但 asset=A-faithful mismatch**(track≠asset_provenance, WaveView GUI 不可便携故 track=synthesized, 但 PWL 导出文本便携故 asset=A-faithful, 两轴正交), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SwitchChgDchVerif-001":
        "DRAM row-decode power switch 充放电功能验证(给 netlist, 构建 transient testbench .ic+多阶段 PWL charge/hold/discharge+.measure FIND v(node) AT, 跑 HSPICE, 解析 .lis 报告各节点充电/放电稳态电压)->produce (portability-driver reframe, real DRAM power switch netlist+HSPICE run 不可沙盒复刻->synth_deck, §4 有牙必要, r837 reframe_note backfill batch12): 用户 dsgao@hfeg0pkn001 (sess 1793934576448_kk5tf, mc=52, spice_sim 域) 为 DRAM row-decode power switch(R_GidlAryCtrl_switch)做功能验证: 给 netlist 文件, 要求验证充放电过程并 print 所有节点电压; trace 中 agent 构建 transient testbench(.ic+多阶段 PWL charge/hold/discharge+.measure FIND v(node) AT), 跑 HSPICE, 解析 .lis 报告各节点充电/放电稳态时刻电压; A 不可行原因=real DRAM power switch netlist+HSPICE 仿真运行不可沙盒复刻(项目路径+真跑) -> 收敛为 switch_chg_dch_verif.py(读 hidden B synth_deck, asset_fidelity=synth_deck); reframe 由 portability-driver(real netlist+HSPICE run 不可复刻); 意图核心(充放电功能验证 + transient testbench + .ic + 多阶段 PWL charge/hold/discharge + .measure FIND v(node) AT + 全节点电压报告)完整保留; check.py 14 断言验 zip 含 switch_chg_dch_verif.py + py_compile + 3 参签名(netlist,config,out_dir) + 候选在 hidden B 上 exit0 产 report + HSPICE 真跑 hspice_ran + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 ✓(check 真跑 HSPICE 二进制 subprocess.run([hspice,'-i',...])), k_rationale/k_check 缺标应 14, **track=faithful 但 asset=synth_deck mismatch**(track≠asset_provenance, real netlist 不可便携故 asset=synth_deck, track 应为 synthesized), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SwitchTbGen-001":
        "SPICE 验证 testbench 生成(为 R_GidlAryCtrl_switch 网表写验证 tb, 观察 GrDecPwr 在 ACT/PRE 下的上拉/下拉电位变化, .tran 130n+secHV PULSE+cm1 反相控制+cgr 负载+.measure)->produce (portability-driver reframe, real R_GidlAryCtrl_switch netlist 不可沙盒复刻->synth_deck, §4 有牙必要, r837 reframe_note backfill batch12): 用户 dsgao@hfhds201 (sess 1793878609339_lywbf, mc=229, spice_sim 域) 为 R_GidlAryCtrl_switch 网表编写 spice 验证 testbench, 观察 GrDecPwr 在 ACT/PRE(secHV 上升沿=ACT 下降沿=PRE)下的上拉/下拉电位变化; USER#6 原话「@<sim_schematic.netlist> 写一个验证tb」纯需求轮; trace 229 msgs/762KB, assistant 产 R_GidlAryCtrl_switch_tb.sp(.tran 130n+secHV PULSE+cm1 反相控制+cgr 100f 负载+Xswitch 例化+.measure), 真跑 finesim 迭代; A 不可行原因=real R_GidlAryCtrl_switch netlist 不可沙盒复刻(项目路径) -> 收敛为 gen_verify_tb.py(读 hidden B synth_deck DUT, asset_fidelity=synth_deck); reframe 由 portability-driver(real netlist 不可复刻); 意图核心(testbench 结构: .tran + secHV PULSE + cm1 反相控制 + cgr 负载 + Xswitch 例化 + .measure + ACT/PRE 双周期 GrDecPwr 充放电观察)完整保留; check.py 12 断言验 zip 含 gen_verify_tb.py + py_compile + 2 参签名(netlist,output) + 候选在 hidden B 上 exit0 产 tb.sp + .tran/.measure/.ic 结构 + cross-input guard(A≠B DUT 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L1 ✓(check 仅 subprocess 跑候选 python 生成 deck 文本 0 EDA 二进制), k_rationale/k_check 缺标应 12, **track=faithful 但 asset=synth_deck mismatch**(track≠asset_provenance, real netlist 不可便携故 asset=synth_deck, track 应为 synthesized), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-TaperBufOpt-001":
        "DRAM 4 级锥形缓冲器驱动比优化(DOE 枚举器件尺寸组合+HSPICE tran 测 tpd/power+PDP=tpd×power×vdd 排序选 best_pdp/best_delay/Pareto+Solido MC 诊断)->produce (portability-driver reframe, real DRAM taper buffer netlist+HSPICE run 不可沙盒复刻->synth_deck, §4 有牙必要, r837 reframe_note backfill batch12): 用户 thqu@hfeg0plg99 (sess 1792565482572_2gmli, mc=231, spice_sim 域) 对 DRAM R_Ra210Rpt_G4C 4 级锥形缓冲器(NAND2+3 INV)做驱动比优化: 读原理图确认 R_Ra210Rpt 需优化驱动比 → DOE 枚举器件尺寸组合 → 写枚举脚本对每组合跑 HSPICE tran 测 tpd/power → 按 PDP=tpd×power×vdd 排序选 best_pdp/best_delay/Pareto → Solido MC 诊断 corner 误差; A 不可行原因=real DRAM taper buffer netlist+HSPICE 仿真运行不可沙盒复刻(项目路径+真跑+Solido) -> 收敛为 taper_buf_opt.py(读 hidden B synth_deck, asset_fidelity=synth_deck); reframe 由 portability-driver(real netlist+HSPICE run 不可复刻); 意图核心(DOE 枚举 + HSPICE tran 实跑 + tpd/power 测量 + PDP 排序 + best_pdp/best_delay/Pareto + Solido MC 诊断)完整保留; check.py 16 断言验 zip 含优化器 .py + 候选在 A 上跑通产 report.json + 9 键齐全 + HSPICE 真跑 + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标应 L2(check 真跑 HSPICE 二进制 run_hspice subprocess.run), k_rationale/k_check 缺标应 16, **track=faithful 但 asset=synth_deck mismatch**(track≠asset_provenance, real netlist 不可便携故 asset=synth_deck, track 应为 synthesized), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-ThoxVthExtract-001":
        "厚氧 MOS Vth 提取器(从 PDK 提 1.8V VGS 下 Id-VG, ntk/ptk 线性区+饱和区双扫描, max-gm 线性外推含 Vds/2 修正 + constant-current 插值 + spec 窗口 accept 判定)->produce (portability-driver reframe, real CXMT V1_HKMG G6 PDK 模型文件 65K+行 不可沙盒复刻->synth_deck, §4 有牙必要, r837 reframe_note backfill batch12): 用户 qiong1w@hfeg0pkn003 (sess 1789693148853_0tfi2, mc=146, characterization 域) 需求轮逐字原文「从PDK中提取厚氧器件在1.8V VGS下的Id-VG,check if Vth is acceptable」, agent 在 CXMT V1_HKMG G6 PDK 模型文件 incFile_V1_HKMG(65K+行)里定位厚氧器件 ntk/ptk 模型卡, 创建 thk_io_idvg.sp(4 个 DC 测试:ntk/ptk 线性区+饱和区 Id-VG 扫描提 Vth), 对话超时用户未明确接受 → B 档 synthesized; A 不可行原因=real CXMT V1_HKMG PDK 模型文件 65K+行不可沙盒复刻(foundry PDK 路径) -> 收敛为 thox_vth_extract.py(读 hidden B synth_deck, level-1 Shichman-Hodges MOS+theta, asset_fidelity=synth_deck); reframe 由 portability-driver(real PDK 模型文件不可复刻); 意图核心(厚氧 ntk/ptk Id-VG 双扫描 + max-gm 线性外推含 Vds/2 修正 + constant-current 插值 + spec 窗口 accept 判定)完整保留; check.py 14 断言验 zip 含 thox_vth_extract.py + py_compile + 候选在 hidden B 上 exit0 + HSPICE/PrimeSim 真跑 + Vth 数值正确 + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 ✓(候选真跑 HSPICE/PrimeSim hspice_log_excerpt), k_rationale/k_check 缺标应 14, track=synthesized ✓(资产 synth_deck 一致), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-TimingMeasGen-001":
        "FineSim timing_measure 文件生成(测 check_signal.sx 中 san*/sap* 信号第1上升沿50%与参考信号时间差, 参考电压 pvint/san=pvnoc/sap=pvpcsg)->produce (portability-driver reframe, real .sx 信号文件含项目专属信号名不可沙盒复刻->synth_data, §4 有牙必要, r837 reframe_note backfill batch12): 用户 kerwind@hfeg0pkn002 (sess 1793971631579_gvexo, mc=54, spice_sim 域) 要求用 finesim measure 语法写 timing_measure 文件, 测量 check_signal.sx 中各 san*/sap* 信号第1上升沿50%与参考信号的时间差, 参考电压 pvint/san=pvnoc/sap=pvpcsg; A 不可行原因=real .sx 信号文件含项目专属信号名不可沙盒复刻(项目信号命名) -> 收敛为 gen_timing_measure.py(读 hidden B synth_data 信号列表, asset_fidelity=synth_data); reframe 由 portability-driver(real .sx 信号文件不可复刻, hidden-B cross-input 须不同信号名故 synth_data); 意图核心(finesim measure 语法 + san*/sap* 信号第1上升沿50% + 参考信号时间差 + 参考电压 pvint/pvnoc/pvpcsg)完整保留; check.py 14 断言验 zip 含 gen_timing_measure.py + timing_measure.sp + py_compile + 候选在 hidden B 上 exit0 产 measure 文件 + HSPICE 真跑 + .measure 语句结构 + cross-input guard(A≠B 信号不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 ✓(check 真跑 HSPICE 二进制 subprocess.run), k_rationale/k_check 缺标应 14, **track=faithful 但 asset=synth_data mismatch**(track≠asset_provenance, real .sx 信号文件不可便携故 asset=synth_data, track 应为 synthesized), shard 缺标应 B。",

    # ===== 3 keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful) =====
    "EDA-Eval-DesignFlow-StrongarmBaselineAnalyze-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r837 reframe_note backfill batch12): 用户 jiangbaol@hfeg0pkn004 (sess 1793955284770_l2j22, mc=228, characterization 域) DqIb_strongarm_pmos strongarm PMOS 比较器尺寸优化, 解析 FineSim .mt0 baseline measure(6 corner)计算 per-corner 电流/延迟, 识别 worst-case corner/min latch current/bottleneck stage; 意图形态=produce-tool(分析 .mt0 数据产 JSON 报告, .mt0 是 FineSim 导出 ASCII 文本 scp 便携); 可便携性=高(real .mt0 baseline measure 导出文本 scp 便携, asset_fidelity=A-faithful, track=faithful); case 交付 gen_strongarm_analyze.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-tool 分析 .mt0 是合法任务形态, trace 意图「解析 .mt0 计算 per-corner 电流/延迟+识别 worst-case」与 case 交付 gen_strongarm_analyze.py 产 JSON 报告同形映射, asset A-faithful 因 .mt0 文本 scp 便携); check.py 16 断言验 zip 含 gen_strongarm_analyze.py + 脚本在 hidden B .mt0 上运行无错 + stdout 合法 JSON + alter_count==6 + corners 齐全 + per-corner 电流/延迟 + worst-case + cross-input guard(A≠B .mt0 不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L1 ✓(check 仅 subprocess 跑候选 python 解析 .mt0 文本 0 EDA 二进制), k_check=16==k_rationale=16 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer=L1 ✓, k_check=16==k_rationale=16 ✓, track=faithful ✓(资产 A-faithful 一致), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SubcktInstParamInj-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r837 reframe_note backfill batch12): 用户 clarawu@hfeg0pkn004 (sess 1792573855361_rbllu, mc=279, spice_sim 域) USER#6 原话「帮我写一个python脚本，将@/proj/m2701/.../netlist 中Cell name: DqFinalDrvPu里的nulvt_ckt管delvto_user=0后面加上_delvto=-0.2」纯需求轮; trace 中 assistant 写 add_delvto_mrodt.py: 正则定位 .subckt <cell>.../.ends <cell> 块, 遍历块内行, 对含 nulvt_ckt 且含 delvto_user=0 的行幂等注入 _delvto=-0.2; 意图形态=produce-action(用户显式要 Python 脚本注入参数, A-档①verbatim 用户原话); 可便携性=高(real netlist 文本 scp 便携, asset_fidelity=A-faithful, track=faithful); case 交付 gen_param_inject.py 同形(零偏移, A-faithful, 通用化为 <netlist> <cell> <device> <anchor> <inject> <outdir>); reframe_note=None->补(faithful 无 reframe, produce-action 是合法任务形态, trace 意图「subckt 块内器件实例行参数注入(幂等+scope 隔离)」与 case 交付 gen_param_inject.py 同形映射, asset A-faithful 因 netlist 文本 scp 便携); check.py 12 断言验 zip 含 gen_param_inject.py + py_compile + 无参/错参非零退出 + 候选在 hidden B 上 exit0 产注入后 netlist + nulvt_ckt 行含 _delvto=-0.2 + 幂等(二次运行无 diff) + scope 隔离(块外/decoy 不注入) + cross-input guard(A≠B netlist 不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L1 ✓(check 仅 subprocess 跑候选 python 编辑 netlist 文本 0 EDA 二进制), k_check=12==k_rationale=12 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer=L1 ✓, k_rationale/k_check 缺标应 12, track=faithful ✓(资产 A-faithful 一致), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SvUsedModelExtract-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r837 reframe_note backfill batch12): 用户 e0039602@hfeg0pkn004 (sess 1793956185129_xyou8, mc=116, spice_sim 域) 给 3 对(netlist.v, simlib.sv), 要求提取 SV 里被网表用到的 model(名字在网表 module 定义中出现), 舍弃未用的, 合并成规范 SV 文件, 保留 `celldefine/`endcelldefine 包裹; 金标准=assistant _extract2.py: HDR_RE module 名, used=sv_names&v_names, extract_cell 向后搜未闭合 `celldefine+向前搜 `endcelldefine, 跨 3 对去重合并 1543 models; 意图形态=produce-tool(提取 used model 产规范 SV 文件, .v/.sv 文本 scp 便携); 可便携性=高(real .v/.sv 文本 scp 便携, asset_fidelity=A-faithful, track=faithful); case 交付 extract 脚本同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-tool 提取 used model 是合法任务形态, trace 意图「提取 SV 里被网表用到的 model+`celldefine 包裹+跨 3 对去重合并」与 case 交付 extract 脚本产 out.json 同形映射, asset A-faithful 因 .v/.sv 文本 scp 便携); check.py 14 断言验 zip 含 .py 提取脚本 + py_compile + 脚本在 B(3 对 netlist/sv)上运行 exit0 产 out.json + out.json 含 4 个必需键 + used model 集合正确 + `celldefine/`endcelldefine 包裹 + cross-input guard(A≠B 文件不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L1(check 仅 subprocess 跑候选 python 解析 .v/.sv 文本 0 EDA 二进制), k_check=14==k_rationale=14 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 缺标应 L1(check 仅 subprocess 跑候选 python 解析 .v/.sv 文本 0 EDA 二进制), k_check=14==k_rationale=14 ✓, track=faithful ✓(资产 A-faithful 一致), shard 缺标应 B。",
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
