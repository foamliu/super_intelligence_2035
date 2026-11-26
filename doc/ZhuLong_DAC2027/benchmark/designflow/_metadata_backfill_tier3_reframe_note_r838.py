#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r838 (2026-11-18) metadata-debt backfill 档3 (reframe_note) batch13.
Source: r825 bounded queue 提议 (reframe_note backfill 160 missing P1).
        r826 batch1 +12 (235->247)   r827 batch2 +12 (247->259)
        r828 batch3 +12 (259->271)   r829 batch4 +12 (271->283)
        r830 batch5 +12 (283->295)   r831 batch6 +12 (295->307)
        r832 batch7 +12 (307->319)   r833 batch8 +12 (319->331)
        r834 batch9 +12 (331->343)   r835 batch10 +12 (343->355)
        r836 batch11 +12 (355->367)  r837 batch12 +12 (367->379, miss 28->16)
        本轮 batch13 = alphabetical 续 12 missing after SvUsedModelExtract-001
        (r837 batch12 末位), 起算 Tr0TrTfMeas, T 段.
        reframe_note 379->391, miss 16->4.

Spec: r773-r800 档3 batch9-34 完成 reframe_note 32->235 (driver 三分 portability/Q&A-analysis/harness
      互斥可枚举归类). r826-r837 await-scan 期接续 backfill reframe_note 160 missing.
      本轮 batch13 12 case = 8 keep_reframe portability + 4 keep_faithful.

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False。
       仅补 reframe_note, 不动 test_rationale/check.py/negative/asset_fidelity (asset_fidelity r824 已 100% 收口)。

Driver 分类 (12 case: 8 keep_reframe portability + 4 keep_faithful):
  - portability-driver (real sim deck/netlist/PDK/tr0/V/vsim Perl 不可沙盒复刻 -> synth_*):
      8 case: Tr0TrTfMeas (real Synopsys WaveView ACE + CXMT foundry tr0 + LSF wv_queue 不可复刻->synth_deck, spice_sim, L2) /
              TscodecompTbVerify (real ALPS drcpa netlist 不可复刻->synth_deck, spice_sim, L1; **track=faithful 但 asset=synth_deck mismatch 待 @A**) /
              VSplit (real .V 含项目专属 Cell module 不可便携->synth_deck, spice_sim, L1; **track=faithful 但 asset=synth_deck mismatch 待 @A**) /
              Vcc2scPVTvar (real FineSim/HSPICE tran + CXMT foundry 模型不可复刻->synth_deck, characterization, L2; **track=faithful 但 asset=synth_deck mismatch 待 @A**) /
              Vcc2scTranGen (real CXMT foundry /proj/dscqa+/rundata/dsjqa 网表 permission denied 不可复刻->synth_deck, spice_sim, L2; **track=faithful 但 asset=synth_deck mismatch 待 @A**) /
              VcoKvcoChar (real 22nm PDK 不可复刻->synth_deck level-1 MOS model, spice_sim, L2; **track=faithful 但 asset=synth_deck mismatch 待 @A**) /
              VsimFinesimAdapt (real vsim Perl 含 /proj 路径+lpddr4/5 legacy arch 不可便携->synth_deck faithful repr, spice_sim, L1; **track 缺标应 synthesized**) /
              VtscRefR5Logic (real VtscRef 网表含 foundry subckt 不可便携->synth_deck, spice_sim, L2; **track 缺标应 synthesized**)
  - keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful):
      4 case: TranStimSync (real FineSim stimulus .list + si.inp 文本 scp 便携, produce-action sync 脚本, asset=A-faithful, **track 缺标应 faithful**, spice_sim, layer 缺标应 L1(check 仅 subprocess python 解析文本 0 EDA 二进制)) /
              TspcNetlistAnalyze (real Cadence hspiceD 导出 netlist 文本 scp 便携, produce-tool 功能分析报告, asset=A-faithful, **track=B 误标应 faithful**, spice_sim, L1) /
              Vcc2scVarJudge (real .mt0 + SPEC.sp + tran.sp 文本 scp 便携, produce-action 判定器, asset=A-faithful, track=faithful ✓, spice_sim, **layer 缺标应 L1**(check 仅 subprocess python 解析 .mt0 文本 0 EDA 二进制)) /
              VrefStepMeasure (real .tr0 经 fscript dsignal 导出 _all.tbl 文本 scp 便携, produce-tool 阶梯波步长测量, asset=A-faithful, **track 缺标应 faithful**, characterization, L2)

T 段 domain-wave 观察: batch13 keep_faithful 占比 33%(4/12) 与 batch12 25% 持平偏高, 
  因 T 段含四类文本便携 asset(real FineSim .list/.inp / Cadence hspiceD netlist / .mt0 measure / fscript .tbl 导出) -> A-faithful 主流可便携群;
  portability-heavy 67%(8/12, 8 synth_deck); Q&A-analysis 0/12=0% + harness-driver 0/12=0% (本段无 diagnosis/多轮交互形态);
  T 段 spice_sim 域 10/12=83% + characterization 域 2/12=17%(Vcc2scPVTvar + VrefStepMeasure), 与 batch12 67%/33% 相比 spice_sim 域回流主流.
  track≠asset_provenance mismatch 累计: batch13 内 5 例(TscodecompTbVerify/VSplit/Vcc2scPVTvar/Vcc2scTranGen/VcoKvcoChar track=faithful 但 asset=synth_deck 应 synthesized), r837 累计 68 -> 73 待 @A 档2 sweep.
  另 track 缺标/误标 4 例(TranStimSync/VrefStepMeasure track 缺标应 faithful; VsimFinesimAdapt/VtscRefR5Logic track 缺标应 synthesized; TspcNetlistAnalyze track=B 误标应 faithful) 待 @A.

metadata bug 待 @A 档1/档2 sweep (reframe_note scope 限定不修, 仅在 note 文本标注):
  - layer 缺标应补: TranStimSync=L1(check 仅 subprocess python 解析文本) / Vcc2scVarJudge=L1(check 仅 subprocess python 解析 .mt0) / VcoKvcoChar=L2(候选真跑 HSPICE) / VsimFinesimAdapt=L1(check 仅 subprocess python 编辑 Perl 文本) / VtscRefR5Logic=L2(已标 ✓ check 解析网表文本 0 EDA 二进制 实为 L1 待 @A 复核)
  - k_check/k_rationale 缺标应补: TscodecompTbVerify=None 应补 / VSplit=None 应补 / Vcc2scVarJudge=14(已标) / VcoKvcoChar=14(已标) / VrefStepMeasure=None 应补 / VsimFinesimAdapt=14(已标) / VtscRefR5Logic=None 应补 / TranStimSync=14(已标 r825 修复)
  - track 缺标或 mismatch 应补: 见上 mismatch+缺标 9 例
  - shard 缺标应 B (全 12 case shard=None 或缺标, TspcNetlistAnalyze shard=B ✓, TranStimSync shard=B ✓)
  - 与 r773-r800/r826-r837 档3 同口径: reframe_note backfill 不动其他字段
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    # ===== 8 keep_reframe_for_teeth (portability-driver) =====
    "EDA-Eval-DesignFlow-Tr0TrTfMeas-001":
        "HSPICE .tr0 波形批量 tr/tf 提取(读 .option post=2 ASCII 固定宽格式 .tr0, 对每个 toggle 电压信号逐条边测 tr(10-90%)/tf(90-10%), 输出结构化 JSON 报告)->produce (portability-driver reframe, real Synopsys WaveView ACE + CXMT foundry tr0 + LSF wv_queue 不可沙盒复刻->synth_deck, §4 有牙必要, r838 reframe_note backfill batch13): 用户 adaml@hfeg0pkn001 (sess 1792215882223_qv6pl, mc=324, spice_sim 域) 用 glm-5.3-flash 构建 waveview-ace-batch skill(WaveView ACE Tcl wv -ace_no_gui 批量波形分析), msg[162] 原话「这个目录下有tr0的波形文件，尝试用这个skill验证一下，要求提取所有toggle波形的tr/tf」在真实 HSPICE tr0(m2701 DDR4 hold tb)上验证; 真实流用 CXMT foundry tr0 + WaveView license + LSF wv_queue(不可移植 .75); A 不可行原因=real WaveView GUI + foundry tr0 + LSF wv_queue 不可沙盒复刻 -> 收敛为 tr0_trtf_meas.py(读 hidden B synth_deck, .75 hspice 产 tr0 + 纯 python 解析复现, asset_fidelity=synth_deck); reframe 由 portability-driver(real WaveView + foundry tr0 不可复刻); 意图核心(从 .tr0 ASCII 固定宽格式批量提取所有 toggle 电压信号逐条边 tr/tf + 10-90%/90-10% 摆幅 + 结构化 JSON)完整保留; check.py 14 断言验 zip 含 tr0_trtf_meas.py + py_compile + 候选在 hidden B 上 exit0 + hspice 真跑产 tr0 + tr/tf 逐边测量 + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 ✓(候选真跑 hspice), k_check=14==k_rationale=14 ✓, track=synthesized ✓(资产 synth_deck 一致), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-TscodecompTbVerify-001":
        "Ras_Tscodecomp 3-bit 比较器 testbench 生成(给 netlist, 写 tb 验证 A/B vs C→HT/LT/NT, 跑 finesim 仿真全 PASS)->produce (portability-driver reframe, real ALPS drcpa netlist 不可沙盒复刻->synth_deck, §4 有牙必要, r838 reframe_note backfill batch13): 用户 dsgao@hfhds201 (sess 1793260818025_aw9d7, mc=273, spice_sim 域) 原话「写一个tb去验证这个电路用finesim仿真」, 网表在 /proj/drcpa/V0/workdir/dsgao/simulation/drcpa_work_Ras_Tscodecomp_schematic_ALPS/netlist; assistant 创建 3 个 TM_verify TB 跑 Finesim 全 PASS; A 不可行原因=real ALPS drcpa netlist 不可沙盒复刻(项目路径) -> 收敛为 gen_tscodecomp_tb.py(读 hidden B synth_deck DUT, asset_fidelity=synth_deck); reframe 由 portability-driver(real ALPS netlist 不可复刻); 意图核心(3-bit 比较器 A/B vs C → HT/LT/NT 验证 testbench + finesim 仿真 + 全 PASS)完整保留; check.py 断言验 zip 含 gen_tscodecomp_tb.py + py_compile + 候选在 hidden B 上 exit0 产 tb.sp + 3-bit 比较器真值表覆盖 + cross-input guard(A≠B netlist 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L1 ✓(check 仅 subprocess 跑候选 python 生成 deck 文本 0 EDA 二进制), k_check/k_rationale 缺标应补, **track=faithful 但 asset=synth_deck mismatch**(track≠asset_provenance, real ALPS netlist 不可便携故 asset=synth_deck, track 应为 synthesized), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-VSplit-001":
        "Verilog .V 文件按 module 拆分(读完整 .V 含多 module, 按 module 切分成每 Cell 单独 tb.v 放对应路径, 只切割不注入任何额外设置)->produce (portability-driver reframe, real .V 含项目专属 Cell module 不可沙盒复刻->synth_deck, §4 有牙必要, r838 reframe_note backfill batch13): 用户 e0029308@hfeg0pkn001 (sess 1793600858808_la00c, mc=339, spice_sim 域) 原话「我现在有一个完整的。V文件，我需要你写一个脚本，可以自动切割成一个一个的Cell单独的Verilog，就是上面你说的这个tb.v文件。并可以自动放在你说的这些个对应路径下」, 明确要求「只切割不要任何额外操作」(不要注入电压/tstop 等设置); A 不可行原因=real .V 含项目专属 Cell module(AMS 批量仿真流程项目 IP) 不可沙盒复刻 -> 收敛为 vsplit.py(读 hidden B synth_deck 多 module .V, asset_fidelity=synth_deck); reframe 由 portability-driver(real .V 含项目专属 module 不可便携); 意图核心(按 module 拆分 .V + 每 Cell 单独 tb.v + 放对应路径 + 只切割不注入)完整保留; check.py 断言验 zip 含 vsplit.py + py_compile + 候选在 hidden B 上 exit0 产拆分文件 + module 数量正确 + 无注入(只切割) + cross-input guard(A≠B .V 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L1 ✓(check 仅 subprocess 跑候选 python 编辑 Verilog 文本 0 EDA 二进制), k_check/k_rationale 缺标应补, **track=faithful 但 asset=synth_deck mismatch**(track≠asset_provenance, real .V 含项目专属 module 不可便携故 asset=synth_deck, track 应为 synthesized), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-Vcc2scPVTvar-001":
        "Vcc2scstdby 待机电源多 PVT corner 瞬态表征(用 .alter 逐 corner 扫 pt, measure Vout_stdby/Vout_1ma, 聚合跨 corner 电压分布(max-min)<5mV 做 spec 判定 + worst corner + 优化策略)->produce (portability-driver reframe, real FineSim/HSPICE tran + CXMT foundry 模型不可沙盒复刻->synth_deck, §4 有牙必要, r838 reframe_note backfill batch13): 用户 tongni@hfeg0pfn119 (sess 1792372786960_4ujp9, mc=155, characterization 域) U[0] 核心 spec「Vcc2scstdby_tran.sp ... variation 是所有 corner 的电压的分布范围要小于 5mV ... 读取 measure 的文件, 做判断, 并给出优化策略」; agent 用 .alter 逐 corner 扫 pt, measure Vout_stdby/Vout_1ma, 聚合跨 corner 电压分布(max-min)<5mV 做 spec 判定 + worst corner + 优化策略; 真实流用 FineSim/HSPICE tran + CXMT foundry 模型(foundry 模型权限不可移植 .75); A 不可行原因=real foundry 模型 + tran run 不可沙盒复刻 -> 收敛为 vcc2sc_pvt_var.py(读 hidden B synth_deck 自包含线性待机稳压器, asset_fidelity=synth_deck); reframe 由 portability-driver(real foundry 模型不可复刻); 意图核心(多 PVT corner .alter + measure Vout_stdby/Vout_1ma + 跨 corner 电压分布 max-min<5mV spec 判定 + worst corner + 优化策略)完整保留; check.py 14 断言验 zip 含 vcc2sc_pvt_var.py + 候选在 hidden B 上 exit0 产 report.json + HSPICE 真跑 + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 ✓(候选真跑 HSPICE), k_check=14==k_rationale=14 ✓, **track=faithful 但 asset=synth_deck mismatch**(track≠asset_provenance, real foundry 模型不可便携故 asset=synth_deck, track 应为 synthesized), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-Vcc2scTranGen-001":
        "Vcc2scstdby tran testbench 参数化生成器(从结构化 spec 合成完整 tran deck: option/netlist/power/stimulus/.tran/.ic/.probe/measurement/pvt/.END 分段顺序, 真跑 HSPICE 解析 .measure 报负载调整率/功耗)->produce (portability-driver reframe, real CXMT foundry /proj/dscqa+/rundata/dsjqa 网表 permission denied 不可沙盒复刻->synth_deck, §4 有牙必要, r838 reframe_note backfill batch13): 用户 tongni@hfeg0pfn119 (sess 1792375390057_aq0vc, mc=254, spice_sim 域) 把 Vcc2scstdby_tran.sp testbench(HSPICE/FineSim tran 分段结构)教给 agent, 要求能根据 testbench netlist 产生仿真文件, 后续补 measure 按自然语言生成 .MEASURE + 瞬态响应+功耗 + 未归类信号兜底 vss, 固化成 skill tran-sim-gen; 真实流用 CXMT foundry /proj/dscqa+/rundata/dsjqa 网表(permission denied); A 不可行原因=real foundry 网表不可沙盒复刻 -> 收敛为 gen_vcc2sc_tb.py(读 hidden B synth_deck 自包含线性 VCCS 模型, asset_fidelity=synth_deck); reframe 由 portability-driver(real foundry 网表不可复刻); 意图核心(从结构化 spec 合成完整 tran deck 分段顺序 + 真跑 HSPICE + 解析 .measure + 报负载调整率/功耗)完整保留; check.py 18 断言验 zip 含 gen_vcc2sc_tb.py + 候选在 hidden B 上 exit0 产 deck + HSPICE 真跑 + .measure 解析 + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 ✓(候选真跑 HSPICE), k_check=18==k_rationale=18 ✓, **track=faithful 但 asset=synth_deck mismatch**(track≠asset_provenance, real foundry 网表不可便携故 asset=synth_deck, track 应为 synthesized), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-VcoKvcoChar-001":
        "ring 4-phase 6GHz VCO 搭建 + KVCO 表征(current-starved N-stage ring VCO, Vtune sweep, .meas fosc/tper/phases, KVCO=dF/dVtune)->produce (portability-driver reframe, real 22nm PDK 不可沙盒复刻->synth_deck level-1 MOS model, §4 有牙必要, r838 reframe_note backfill batch13): 用户 wnyu@hfeg0pkn004 (sess 1792119838262_chbpp, mc=629, spice_sim 域) IDX17 verbatim「你先自己搭建一个VCO 这个模块，不管前后级，只管从 Vtune 进来 → 四相 6 GHz 出去；看看能不能仿真成功，再看看KVCO」, 22nm 工艺节点环形 ring 四相位 VCO, PLL 要跑到 6GHz, 输入参考频率 19.2MHz; trace 末尾用户接受 4-phase ring-VCO + KVCO 表征流程; A 不可行原因=real 22nm PDK 不可沙盒复刻 -> 收敛为 vco_kvco.py(读 hidden B synth_deck level-1 Shichman-Hodges MOS model, asset_fidelity=synth_deck); reframe 由 portability-driver(real 22nm PDK 不可复刻); 意图核心(current-starved N-stage ring VCO + Vtune sweep + .meas fosc/tper/phases + KVCO=dF/dVtune + 四相位 6GHz)完整保留; check.py 14 断言验 zip 含 vco_kvco.py + py_compile + 候选在 hidden B 上 exit0 产 kvco_result.json + HSPICE 真跑 + fosc/KVCO 数值 + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标应 L2(候选真跑 HSPICE), k_check=14==k_rationale=14 ✓, **track=faithful 但 asset=synth_deck mismatch**(track≠asset_provenance, real 22nm PDK 不可便携故 asset=synth_deck, track 应为 synthesized), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-VsimFinesimAdapt-001":
        "LPDDR6 vsim(Perl) TB 构建脚本适配 FineSim(删 lpddr4/lpddr5 老 arch filelist 块 + 默认项目 DBRMA/V0 改 DECQA/V0 + 默认架构 lpddr4 改 lpddr6 + 加 local workarea fallback)->produce (portability-driver reframe, real vsim Perl 含 /proj 路径+lpddr4/5 legacy arch 不可沙盒复刻->synth_deck faithful repr, §4 有牙必要, r838 reframe_note backfill batch13): 用户 mike@hfeg0plg49 (sess 1794378055746_1s79t, mc=517, spice_sim 域) 把 lpddr6 的 vsim(Perl) TB 构建脚本适配给 FineSim, 删 lpddr4/lpddr5 老架构 filelist 块, 默认项目 DBRMA/V0 改 DECQA/V0, 默认架构 lpddr4 改 lpddr6, 加 local workarea fallback(vsim -c 用绝对路径时从 vsim 自身目录推 TB/proj 目录); 67 个工具调用, 交付 vsim.decqa 重构脚本 + diff; A 不可行原因=real vsim Perl 含 /proj 路径 + lpddr4/5 legacy arch 不可沙盒复刻 -> 收敛为 vsim_adapt.py(读 hidden B synth_deck faithful ~150 行 vsim-like Perl, asset_fidelity=synth_deck); reframe 由 portability-driver(real vsim Perl 不可便携); 意图核心(删老 arch filelist + 改默认项目/架构 + local workarea fallback + 通用重构)完整保留; check.py 14 断言验 zip 含 vsim_adapt.py + py_compile + 候选在 hidden B 上 exit0 产适配后 vsim + lpddr4/5 块删除 + 默认改 lpddr6/DECQA + cross-input guard(A≠B vsim 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标应 L1(check 仅 subprocess 跑候选 python 编辑 Perl 文本 0 EDA 二进制), k_check=14==k_rationale=14 ✓, **track 缺标应 synthesized**(资产 synth_deck 一致), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-VtscRefR5Logic-001":
        "VtscRef 网表 R5 功能推导(从网表连接关系推导顶层逻辑输出 Vtsc2Vcc/VtscAmpDis 布尔等式与真值表, 识别运放核 AG_VnocVdleqVtscRefAmpCore 拓扑, 区分电压修调/偏置电流修调两路径, 写可复用 r5_functional_report.py)->produce (portability-driver reframe, real VtscRef 网表含 foundry subckt 不可沙盒复刻->synth_deck, §4 有牙必要, r838 reframe_note backfill batch13): 用户 tongni@hfeg0pkn004 (sess 1794470412317_0wqbh, mc=38, spice_sim 域) 对 zmh_AI_VtscRef_standard_tb 网表做 R5 功能推导: 从网表连接关系推导顶层逻辑输出 Vtsc2Vcc/VtscAmpDis 的布尔等式与真值表(Vtsc2Vcc=PwrOn3&shft<2>&shft<1>&!shft<0>=code110, VtscAmpDis=PwrOn3&shft<2>&shft<1>=codes110,111), 识别运放核 AG_VnocVdleqVtscRefAmpCore 拓扑(NMOS 输入差分对+cascode+PMOS 电流镜, 两级折叠), 区分 cm1_ag_AdjVtsc→电压修调与 cm1_ag_RegLbias→偏置电流修调两条路径, 写成可复用 r5_functional_report.py 脚本集成进 sim-sp-gen skill; A 不可行原因=real VtscRef 网表含 foundry subckt 不可沙盒复刻 -> 收敛为 r5_functional_report.py(读 hidden B synth_deck VtscRef 风格网表, asset_fidelity=synth_deck); reframe 由 portability-driver(real 网表含 foundry subckt 不可便携); 意图核心(R5 五段报告: 顶层 I/O 识别 + 逻辑输出布尔等式 + 真值表 + 运放核拓扑识别 + 修调路径区分)完整保留; check.py 断言验 zip 含 r5_functional_report.py + py_compile + 候选在 hidden B 上 exit0 产 R5 报告 + 布尔等式正确 + 真值表覆盖 + cross-input guard(A≠B netlist 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 待复核(check 仅 subprocess 跑候选 python 解析网表文本 0 EDA 二进制 应 L1), k_check/k_rationale 缺标应补, **track 缺标应 synthesized**(资产 synth_deck 一致), shard 缺标应 B。",

    # ===== 4 keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful) =====
    "EDA-Eval-DesignFlow-TranStimSync-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r838 reframe_note backfill batch13): 用户 mike@hfeg0plg05 (sess 1790840542058_430uk, mc=1117, spice_sim 域) FineSim cosim .tran stop 与 stimulus .list 末行 timestamp 同步场景, 原话「.tran 10ps 95552114ps 还有一步,zhegcanshu xuyao tihuan ,要查看DSDM_TRAIN_stimulus.list ,这个激励最后一行是 89186489 ，单位是ps，我们在这个基础上加上500 000 然后替换掉之前的参数」; 金标准=assistant data-driven 解析(不轻信用户原话数值): 读 .list 最后一行非空数据行首列整数 timestamp, +500000, 替换 si.inp .tran stop; trace 中用户口述 89186489 实为 CS_TRAIN 的值(DSDM_TRAIN 真值 40470239), assistant 按文件实际值修正; 意图形态=produce-action(写 tran_sync.py 接受 finesim 目录参数, 解析 .list 末行 timestamp + 500000 替换 si.inp .tran stop, 写 si_synced.inp + tran_sync_report.txt); 可便携性=高(real FineSim stimulus .list + si.inp 文本 scp 便携, asset_fidelity=A-faithful, track=faithful); case 交付 tran_sync.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-action 是合法任务形态, trace 意图「data-driven 解析 .list 末行 timestamp + 500000 替换 .tran stop」与 case 交付 tran_sync.py 同形映射, asset A-faithful 因 .list/.inp 文本 scp 便携); check.py 14 断言验 zip 含 tran_sync.py + py_compile + 候选在 hidden B 上 exit0 产 si_synced.inp + tran_sync_report.txt + timestamp 正确替换 + cross-input guard(A≠B timestamp 不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L1 ✓(check 仅 subprocess 跑候选 python 解析文本 0 EDA 二进制), k_check=14==k_rationale=14 ✓(r825 硬闸门修复 test_rationale 空→14 断言), 无 reframe, 保留。**metadata bug 待 @A**: layer 缺标应 L1, k_check=14==k_rationale=14 ✓, **track 缺标应 faithful**(资产 A-faithful 一致), shard=B ✓。",

    "EDA-Eval-DesignFlow-TspcNetlistAnalyze-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r838 reframe_note backfill batch13): 用户 adaml@hfeg0pkn002 (sess 1791980431476_gsmj2, mc=58, spice_sim 域) 用 Cadence hspiceD 导出单元级原理图网表 TSPC_RVT(/proj/m2701/V0_DDR4/workdir/adaml/simulation/TSPC_RVT/hspiceD/schematic/netlist, 37 行=2 switch subckt + 20 MOS), 原话「读取这个电路网表，给出这个电路的功能分析和原理报告」; 助手 read_files 读完整网表 + list_allowed_files 查仿真目录 + read_files amap hlmc22ull_prvt_ckt/nrvt_ckt_hspiceD.inst 确认管脚顺序, editor 写开关级行为仿真器 tspc_switch_sim.py + run_approved_command 跑 5 场景(S1 D=!Q 二分频/S2 D=0 保持/S3 D=1 置1/S4 RST 17ps 复位/S5 3.3GHz) + 写 TSPC_R 功能分析报告; 意图形态=produce-tool(读网表给功能分析和原理报告, netlist 文本 scp 便携); 可便携性=高(real Cadence hspiceD 导出 netlist 文本 scp 便携, asset_fidelity=A-faithful, track=faithful); case 交付功能分析脚本同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-tool 分析是合法任务形态, trace 意图「读网表给功能分析+原理报告+5 场景行为仿真」与 case 交付分析脚本产 JSON 报告同形映射, asset A-faithful 因 netlist 文本 scp 便携); check.py 18 断言验 zip 含分析脚本 + py_compile + 候选在 hidden B 上 exit0 产 JSON 报告 + 5 场景齐全 + 二分频功能正确 + cross-input guard(A≠B netlist 不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L1 ✓(check 仅 subprocess 跑候选 python 解析网表文本 0 EDA 二进制), k_check=18==k_rationale=18 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer=L1 ✓, k_check=18==k_rationale=18 ✓, **track=B 误标应 faithful**(资产 A-faithful 一致, track 字段误填 shard 名), shard=B ✓。",

    "EDA-Eval-DesignFlow-Vcc2scVarJudge-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r838 reframe_note backfill batch13): 用户 tongni@hfeg0pkn001 (sess 1792373325953_z6mt7, mc=83, spice_sim 域) 对 Vcc2scStdby(待机电源切换)做多 PVT corner 瞬态仿真后要求读取 measure 文件、判断 variation(所有 corner 电压分布范围)<5mV 的 SPEC、并给出优化策略, 首轮逐字「用 bsub finesim 跑 Vcc2scstdby_tran.sp, SPEC 在 Vcc2scstdby_tran_SPEC.sp, variation<5mV, 读取 measure 的文件做判断并给优化策略」; trace 里 agent 读 SPEC.sp(2 行: Vcc2sc_unload/Vcc2sc_load1mA Variation<5mV) + tran.sp(.tran 1n 300u, iload PWL 0→0.1mA→1mA, 两条 .MEASURE TRAN AVG V(Vcc2sc!) FROM=60u/110u) + check_vcc2sc_stdby_var.py(金标准判定器), 修 LSF/LD_PRELOAD 环境坑 + license 转发后跑通 finesim job 993022(121 PVT corner, 2.8h), 修判定器大小写敏感 bug; 意图形态=produce-action(写判定器读 measure 文件判断 variation spec + 优化策略); 可便携性=高(real .mt0 + SPEC.sp + tran.sp 文本 scp 便携, asset_fidelity=A-faithful, track=faithful); case 交付判定器脚本同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-action 是合法任务形态, trace 意图「读 measure 文件判断 variation<5mV spec + 优化策略」与 case 交付判定器脚本产 JSON 报告同形映射, asset A-faithful 因 .mt0/SPEC.sp/tran.sp 文本 scp 便携); check.py 14 断言验 zip 含判定器 .py + py_compile + 候选在 hidden B 上 exit0 产判定报告 + variation<5mV 判定 + worst corner + 优化策略 + cross-input guard(A≠B .mt0 不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L1(check 仅 subprocess 跑候选 python 解析 .mt0 文本 0 EDA 二进制), k_check=14==k_rationale=14 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 缺标应 L1, k_check=14==k_rationale=14 ✓, track=faithful ✓(资产 A-faithful 一致), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-VrefStepMeasure-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r838 reframe_note backfill batch13): 用户 alenxu@hfeg0pkn134 (sess 1794378329165_cli7p, mc=21, characterization 域) 要求对 vrefDQ_linerty.tr0 的 v(vref_dq<0>) 阶梯波做逐档步长测量, 原话「v(vref_dq<0>) vrefDQ_linerty.tr0，为 vrefdq0，档位切换曲线，每个档位时间为 150ns，计算每档的步长，步长为相邻两个档位的插值，第一个档位的点取在 290ns，第二个点取在 290+150=440ns，以此类推」; 原始 .tr0 经 fscript dsignal 导出为 _all.tbl(2451 点), A=真实 27 档上升 0.343→0.485V ~5.47mV/档, B=合成 18 档下降 0.850→0.425V -25mV/档, 结构同构取值不同; 意图形态=produce-tool(纯 Python 标准库计算阶梯波步长测量, 无需 fscript/EDA license); 可便携性=高(real .tr0 经 fscript dsignal 导出 _all.tbl 文本 scp 便携, asset_fidelity=A-faithful, track=faithful); case 交付 vref_step_measure.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-tool 测量是合法任务形态, trace 意图「按 start_ns + k*period_ns 逐点线性插值取值 + 计算相邻档位步长」与 case 交付 vref_step_measure.py 产 vref_steps.json 同形映射, asset A-faithful 因 .tbl 导出文本 scp 便携); check.py 断言验 zip 含 vref_step_measure.py + py_compile + 候选在 hidden B 上 exit0 产 vref_steps.json + 档位数正确 + 步长数值正确 + cross-input guard(A≠B .tbl 不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L2 ✓(check 仅 subprocess 跑候选 python 解析 .tbl 文本 0 EDA 二进制, 实为 L1 待 @A 复核), k_check/k_rationale 缺标应补, **track 缺标应 faithful**(资产 A-faithful 一致), shard 缺标应 B。",
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
