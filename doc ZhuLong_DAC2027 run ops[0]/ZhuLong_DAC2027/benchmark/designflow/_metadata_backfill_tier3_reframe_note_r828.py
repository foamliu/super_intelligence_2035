#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r828 (2026-11-18) metadata-debt backfill 档3 (reframe_note) batch3.
Source: r825 bounded queue 提议 (asset_fidelity 100% 收口后下一道 bounded queue =
        reframe_note backfill 160 missing P1). r826 batch1 +12 (235->247, miss 160->148).
        r827 batch2 +12 (247->259, miss 148->136).
        本轮 batch3 = alphabetical 续 12 missing after CmpStg1CapAdd (r827 batch2 末位).
        reframe_note 259->271, miss 136->124.

Spec: r773-r800 档3 batch9-34 完成 reframe_note 32->235 (driver 三分 portability/Q&A-analysis/harness
      互斥可枚举归类). r826-r828 await-scan 期接续 backfill reframe_note 160 missing.
      本轮 batch3 12 case = 9 keep_reframe_for_teeth + 3 keep_faithful.

reframe_note text 来源:
  - keep_reframe_for_teeth case: spotcheck per_case_reasoning + cases/B trace_source(user@host/session/mc)
    + test_rationale k_check + asset_fidelity; driver 分类(portability/Q&A-analysis/harness).
  - keep_faithful case: r825 §观点(3) disclosure 完整性 — keep_faithful case 亦补 reframe_note
    记录「无 reframe + trace 意图同形便携判据」, §5 asset_provenance disclosure 成对字段完整。
    文本以 "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r828 reframe_note backfill batch3)" 开头。

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False。
       仅补 reframe_note, 不动 test_rationale/check.py/negative/asset_fidelity (asset_fidelity r824 已 100% 收口)。

Driver 分类 (12 case: 9 keep_reframe + 3 keep_faithful):
  - portability-driver (foundry PDK / /proj 网表不可沙盒复刻 / SandBox 离线 → level-1 proxy / 合成):
      5 case: CtleAcChar (foundry→level-1 HSPICE) / DblTailSlicerDeckGen (SandBox 离线→synth_data deck gen) /
              DcaStimSweepGen (/proj netlist 不可复刻→synth_deck) / DffSetupHoldChar (foundry→level-1 Shichman-Hodges) /
              DspfCapExtractValidate (real 1.7MB DSPF 不可复刻→synth_deck)
  - Q&A-analysis-driver (分析/梳理/检查 → 结构化 JSON/CSV for §4 subprocess 有牙):
      2 case: Coord3DProj (梳理 i/c/q 与 template 关系→parse_coord 结构化工具) /
              DeckConsistencyCheck (一致性检查→JSON inconsistencies 报告)
  - harness-driver (Perl→Python / skill→Python+L2 真跑 / 完整流→子流):
      2 case: CosimRunBlockOpt (Perl runBlock→Python gen_cosim.py) /
              DelayChainEdgeMeas (skill+FineSim→Python delay_chain_meas.py+L2 真跑)
  - keep_faithful (无 reframe, trace 意图同形便携): 3 case:
      CosineWaveAnalyze / DelayedBmatrixSched / DetermSeedByName

metadata bug 待 @A 档1/档2 sweep (reframe_note scope 限定不修, 仅在 note 文本标注):
  - 多 case layer/level 缺标或误判 (应 L1/L2), k_check 字段缺标, shard 缺标
  - 与 r773-r800/r826/r827 档3 同口径: reframe_note backfill 不动其他字段
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    # ===== 9 keep_reframe_for_teeth =====
    "EDA-Eval-DesignFlow-Coord3DProj-001":
        "lib_timing_tools 三维坐标 (i_slew,c_slew,q_load) 索引/值传递兼容工具->produce (Q&A-analysis-driver reframe, 梳理 i/c/q 与 lu_table_template 关系的 analysis→parse_coord 结构化工具 for §4 subprocess 有牙, r828 reframe_note backfill batch3): 用户 e0046686@hfhds201 (sess 1794221449278_bqqtk, mc=530) U#0 原话「autosim_script/rev_cali_tools 反标后端脚本中 lib_timing_tools 抽 timing 需按 (i_slew,c_slew,q_load) 三维坐标传递，先梳理 i/c/q 与各 template table 的关系(每个 table 只取三维中 1~2 个)，再开发索引/值传递兼容」, 意图=梳理 template 关系(analysis)+开发传递兼容逻辑(codegen); A 不可行(为 §4 有牙)原因=「梳理关系」自然语言分析不可被 subprocess 确定性判分 → 收敛为 parse_coord 结构化坐标解析工具(3 段索引/3 段值/2 段 legacy/1 段 legacy 补 0/4 段 ValueError 五语义, A=trace 模板关系便携化 fixture, hidden_B=合成变体坐标, asset_fidelity=synth_deck); reframe 由 Q&A-analysis-driver(analysis-Q&A→produce-tool); check.py 14 断言验 parse_coord 五输入语义 + 跨输入 guard => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标(应 L1, check 仅 subprocess 跑候选 python 解析坐标字符串, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-CosimRunBlockOpt-001":
        "DDR6 Array block ALPS+VCS-AD 数模混合联合仿真 runBlock(Perl) 优化->produce (harness-driver reframe, Perl runBlock→Python gen_cosim.py for §4 subprocess 真跑有牙, r828 reframe_note backfill batch3): 用户 mike@hfhds201 (sess 1793862569889_ezcgh, mc=235, =.75 local) U#0 原话「/ai_sandbox/dscqa/V0/agentdir/mike/dscqa_array_m0d5G_YS_Bot_sub_schematic_ALPS/runBlock 理解这个脚本和这个项目文件，我需要做一个联合仿真的工作，需要优化下这个脚本」(纯需求轮给目标=优化联合仿真脚本, 未给根因/修复); A 不可行(为 §4 有牙)原因=Perl 脚本优化文本不可被 subprocess 结构性判分 → 收敛为 gen_cosim.py(Python 重构, 读 port_in/port_io/stimulus/netlist 产 stimulus.v+vcsAD.init+netlist_out+stimulus_trimmed 四文件, asset_fidelity=synth_script); reframe 由 harness-driver(Perl→Python harness for hidden-B subprocess); 意图核心(优化联合仿真脚本生成 stimulus/netlist)完整保留; check.py 13 断言验 gen_cosim.py + py_compile + 5 参数校验 + hidden B 四文件产出 + stimulus.v 端口齐全 + 跨输入 guard => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确, level 缺标应 L1, k_check 字段缺标应 13, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-CtleAcChar-001":
        "DFE CTLE AC 频率响应表征工具->produce (portability-driver reframe, foundry 模型不可沙盒复刻→level-1 HSPICE proxy, B档 sub-task + asset_fidelity, §4 有牙必要, r828 reframe_note backfill batch3): 用户 alenxu@hfeg0pkn003 (sess 1790142100320_n91pk, mc=755) 对 DFE_alenxu 的 CTLE 做 AC 频率响应表征与重设计(T0/T1453 扫描 DQC1/DQR1 电容/电阻阵列测 ac 曲线+眼图+单脉冲; T11243 重设计 CTLE 新增 spec dc_gain=6dB/peaking=6dB@5.2GHz/BW>8GHz; T13459 定义 bw=-3dB 带宽), 本 case 取其可移植子技能=.ac 扫频→提取 dc_g/nyq_g/peak_g/fpeak/peaking/bw/idd + spec PASS/FAIL; A 不可行原因=完整流用 CXMT foundry 模型不可沙盒复刻 → 便携 level-1 网表 + HSPICE proxy(asset_fidelity=synth_deck); reframe 由 portability-driver(foundry 不可复刻); check.py 18 断言验 ctle_ac_char.py + result.json 7 度量键 + A HSPICE 真跑(.lis job concluded) + dc_g/nyq_g/peak_g/fpeak/peaking/bw GT 容差 + 跨输入 guard => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 真跑 HSPICE 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确, level 缺标应 L2, k_check 字段缺标应 18, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-DblTailSlicerDeckGen-001":
        "double-tail (StrongARM) slicer deck 生成器->produce (portability-driver reframe, SandBox run_code(pyAether+skill) 离线失败→synth_data deck generator, §4 有牙必要, r828 reframe_note backfill batch3): 用户 cynthiaz@hfeg0pkn005 (sess 1790229492123_m7hxu, mc=409) U#2 原话逐字「design a double-tail slicer,meet target data rate 2.9Ghz」(纯目标轮给拓扑+目标速率, 未给根因/修复), trace agent 先 list_allowed_files/RAG 检索 pyAether 建图 API, SandBox run_code(pyAether+skill) 因 sandbox 离线失败, 转用 editor; A 不可行原因=SandBox 离线 + pyAether 建图不可沙盒复刻 → 收敛为 gen_slicer_deck.py(读 spec 产 slicer.sp+sizing.json+README, asset_fidelity=synth_data); reframe 由 portability-driver(SandBox 离线+schema 不可复刻→synth deck gen); 意图核心(设计 double-tail slicer 满足目标速率)完整保留; check.py 12 断言验 gen_slicer_deck.py + py_compile + 参数校验 + hidden B(4.5GHz) 产 slicer.sp 含 .subckt double_tail_slicer 7 端口 + ≥8 MOS 实例 + 跨输入 guard => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(产 .sp 文本, 0 EDA 二进制真跑), level 缺标应 L1, k_check 字段缺标应 12, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-DcaStimSweepGen-001":
        "PLL_GDCA 延迟链 .sp 激励扫描 deck 生成器->produce (portability-driver reframe, /proj 网表不可沙盒复刻→synth_deck, §4 有牙必要, r828 reframe_note backfill batch3): 用户 curryxu@hfeg0pkn002 (sess 1794471268159_nh28n, mc=205, 10.129.2.11) PLL_GDCA 可控延迟链 hspice 仿真, 要求为 DCA 延迟链写 .sp 激励脚本(6GHz 方波输入, P<2:0> 先全 0 再扫描 000→111, 后追加输出占空比检测), agent 读 netlist/header/footer/model.sp 按 spice_tb_stimulus skill 13-section 骨架产 PLL_GDCA_tb_6G.sp(8 行 .data sweep + 传播延迟+占空比 .measure); A 不可行原因=/proj real netlist 不可沙盒复刻 → 收敛为 gen_stim.py(读 netlist 产 stim_A.sp, asset_fidelity=synth_deck); reframe 由 portability-driver(/proj 网表不可复刻→synth); 意图核心(写 .sp 激励扫描 deck)完整保留; check.py 13 断言验 gen_stim.py + stim_A.sp .inc 引用 netlist + 6GHz 方波 + .data 8 行 P<2:0> 全组合 + 首 sweep 全 0 基线 + .tran sweep + 电源 vcc!/vss! + 传播延迟+占空比 .measure + 跨输入 guard => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(产 .sp 文本, 0 EDA 二进制真跑), level 缺标应 L1, k_check 字段缺标应 13, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-DeckConsistencyCheck-001":
        "rj/psij 仿真 run 脚本/.sp/corner 名称一致性检查器->produce (Q&A-analysis-driver reframe, 只报告不修改的 consistency check→结构化 JSON inconsistencies 报告 for §4 subprocess 有牙, r828 reframe_note backfill batch3): 用户 witterfu@hfeg0pkn005 (sess 1794448818017_fppmi, mc=372) 在 /proj/ddgot/V0/workdir/witterfu/simulation/wck/jitter/ 下检查 random jitter (rj) 与 psij 两类仿真在 12800/17600 两速率下的 run 脚本/.sp 文件/corner 名称是否一一对应正确(drate vs 文件名、run 脚本 .sp 引用、corner 名三类一致性), 要求只报告不修改; A 不可行(为 §4 有牙)原因=「只报告」自然语言报告不可被 subprocess 确定性判分 → 收敛为 deck_consistency_checker.py(输出 JSON inconsistencies 列表, asset_fidelity=synth_deck); reframe 由 Q&A-analysis-driver(analysis-检查→produce-JSON 报告); 意图核心(三类一致性检查只报告)完整保留; check.py 10 断言验 hidden B subprocess 真跑 exit=0 + JSON 含 inconsistencies + 三类(drate_vs_filename/run_ref_mismatch/corner_name_mismatch)ground-truth 全检出无漏报 + 无误报 + 总数==ground truth + 跨输入 guard => 收敛为 produce-JSON 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 跑候选 python 检文件名一致性, 是否真跑 EDA 二进制待核; 若仅文件名/corner 字符串比对应 L1), level 缺标, k_check 字段缺标应 10, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-DelayChainEdgeMeas-001":
        "DRAM RasBnkLogic 延迟链上升/下降沿延迟测量工具->produce (harness-driver reframe, skill+FineSim→Python delay_chain_meas.py+L2 真跑, §4 有牙必要, r828 reframe_note backfill batch3): 用户 harrywu@hfeg0pkn002 (sess 1792831256137_6qt0a, mc=319) 用 cline(deepseek-v4-flash) 执行 DRAM RasBnkLogic 延迟链分析流: msg[0] 读懂网表功能 → msg[20] 开发仅含 delay cell 信号链工具 → msg[80] 做成 Skill(dram-delay-chain) → msg[120] 修订(SapEn2 未回溯输入端口、cm 常量屏蔽路径) → msg[325] 关键转折: 延迟链须判定对上升/下降沿有效, 纯网表无法判定, 改用静态仿真方案 → msg[361] 用 FineSim 自跑仿真并集成进 skill; A 不可行原因=skill 形态+纯网表无法判沿 → 收敛为 delay_chain_meas.py(Python+FineSim L2 真跑, 边沿判定+级延迟, asset_fidelity=synth_deck); reframe 由 harness-driver(skill→Python+L2 真跑); 意图核心(延迟链级延迟测量+沿判定)完整保留; check.py 14 断言验 delay_chain_meas.py + py_compile + hidden B subprocess exit=0 + report.json 含 stim_signal/stim_edge/t_stim/target_signal/target_edge/t_target/total_delay/stages + stages 长度==B 级数(5) + 每级 cell_type/polarity/in_edge + 跨输入 guard => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 真跑 FineSim 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确, level 缺标应 L2, k_check 字段缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-DffSetupHoldChar-001":
        "TSPC DFF setup/hold/tCQ 时间表征工具->produce (portability-driver reframe, foundry 模型不可沙盒复刻→level-1 Shichman-Hodges + harness(分析 bug 修复→Python+L2 真跑), §4 有牙必要, r828 reframe_note backfill batch3): 用户 kaixuanx@hfeg0pkn001 (sess 1792386804961_6tiy7, mc=250) 分析 TSPC DFF 的 setup/hold 仿真结果, 发现「保持时间为什么还是 0ps,是不是分析错数据了」, 并要求「把建立和保持时间放在一个 testbench 里跑」; 根因=hold 观测窗口跨过下一个 CLK 沿, Q 被下一沿正确捕获永不违例得假 tH=0, 且 setup/hold 用单 tskew 联动(跷跷板)两临界都够不着; A 不可行原因=完整流用 foundry 模型不可沙盒复刻 + 分析 bug 修复需可重跑验证 → 便携 level-1 Shichman-Hodges + char_gen.py(HSPICE L2 真跑, hold 观测窗口派生+两独立扫描变量, asset_fidelity=synth_deck); reframe 由 portability-driver(foundry→level-1)+harness(分析 bug→Python+L2 真跑验证); 意图核心(setup/hold/tCQ 表征+假 tH=0 bug 修复)完整保留; check.py 14 断言验 char_gen.py + py_compile + HSPICE subprocess 调用(真跑非 stub) + hold 观测窗口 tclk 派生(非裸固定字面量, 否则跨下一 CLK 沿得假 tH=0——trace 主 bug) + setup/hold 两独立扫描变量(tsu_lead/th_lag 非单 tskew 跷跷板) + SI 后缀 parser + 跨输入 guard => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 真跑 HSPICE 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确, level 缺标应 L2, k_check 字段缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-DspfCapExtractValidate-001":
        "DSPF 寄生电容参数提取与准确性校验工具->produce (portability-driver + Q&A-analysis-driver reframe, real 1.7MB/27971 行 DSPF 不可沙盒复刻→synth_deck + 检查电容值准确→结构化 CSV 校验 for §4 subprocess 有牙, r828 reframe_note backfill batch3): 用户 haoliu@hfeg0pkn004 (sess 1794272818268_ckhfh, mc=0, legacy 低于 mc>=10 阈值审计判意图非判 mc 保留) U#0 原话「在 /home/haoliu/Desktop/AI_Project/01_spf 下分析后仿网表 /rundata/.../00_spf/DqIb_2stg_DfeM6V2IP.spf.TYP_98_RCC 理清电路架构，用 skill 提取寄生电容参数并检查电容值是否准确」, assistant 读 DSPF 1.3 网表(1.70MB/27971 行, StarRC, 无 *|CAP/*|RES 区块头, 电容内联 4-token 行, 子节点 net:NN) 写 skill 提取; A 不可行原因=real 1.7MB DSPF 不可沙盒复刻 + 「检查准确」自然语言报告不可确定性判分 → 收敛为 dspf_cap_extract.py(提取对地/耦合电容产 3 CSV + 逐网声明值 vs 提取值 rel_err + 全局电荷守恒 ratio, asset_fidelity=synth_deck); reframe 由 portability-driver(real DSPF 不可复刻)+Q&A-analysis(检查准确→CSV 校验); 意图核心(提取寄生电容+校验准确)完整保留; check.py 14 断言验 dspf_cap_extract.py + py_compile + hidden B exit=0 产 3 CSV + 对地电容数/耦合电容数/总和对地/总和耦合/网络数==参考值 + 逐网 |rel_err|<1e-3 + 电荷守恒 ratio + 跨输入 guard => 收敛为 produce-CSV 校验是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标(应 L1, check 仅 subprocess 跑候选 python 解析 DSPF 文本+验 CSV, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 14, shard 缺标应 B。",

    # ===== 3 keep_faithful (无 reframe, trace 意图同形便携) =====
    "EDA-Eval-DesignFlow-CosineWaveAnalyze-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r828 reframe_note backfill batch3): 用户 e0023936@hfhds201 (sess 1793842177177_bqszj, mc=26) WaveView ACE Tcl 任务(generate cosine wave + compute zero-crossings + estimate frequency and peak), 意图形态=produce-script(写 .tcl 波形生成+分析脚本), 可便携性=高(纯 Tcl 自包含, tclsh stub 兼容跑, 无 EDA 二进制依赖, asset_fidelity=no-asset); trace agent 写 .tcl(sx_add_wave 波形创建 + sx_append_real 数据点追加 + 过零点检测符号翻转 + 频率估算 1/T + 峰值估算 abs/max), case 交付 .tcl 同形(零偏移, 用户意图「写 Tcl 脚本」直接映射到 case 交付 .tcl 脚本); reframe_note=None→补(faithful 无 reframe, trace 意图与 case 交付同形映射); check.py 14 断言验 zip 含且仅含 1 个 .tcl + proc 定义 + sx_add_wave/sx_append_real API + 过零点检测逻辑 + 频率估算逻辑 + 峰值估算逻辑 + 结构化结果返回 + tclsh 运行 exit=0 + B 参数 zero_crossings==2*np(16) + frequency≈ + 跨输入 guard => §4 牙由 hidden-B cross-input + §4.2 subprocess(tclsh stub 真跑)保证, layer 应 L1, k_check=14==k_rationale=14 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 缺标(应 L1, check 仅 tclsh stub 跑 .tcl 文本, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-DelayedBmatrixSched-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r828 reframe_note backfill batch3): 用户 ynbai@hfeg0pkn005 (sess 1794224252917_ls7n4, mc=16) 要求写脚本到 /proj/drgqa/V0/simdir/finesim/drgqaF/local_script/run_crg, 实现四个半小时后 linux 进入 MatrixRun_..._CRG_Sec2 目录执行 bmatrix -a -rerun -q fqueue3_V2(finesim coverage matrix run 延迟调度), agent 读旧 run_crg(sleep10+旧目录)与 matrixrun_0d85/1d15 perl 模板, 经 write_run_crg.py 安装器(policy writableRoot 限制 /home/yn); 意图形态=produce-action(verb「写脚本」显式要 scheduler script), 可便携性=高(纯 Python sleep+chdir+os.system, 无 EDA 二进制, fake bmatrix stub 可验调用, asset_fidelity=A-faithful); trace agent 写 run_crg(Python sleep+chdir+os.system bmatrix), case 交付 run_crg 同形(零偏移, A-faithful); reframe_note=None→补(faithful 无 reframe); check.py 17 断言验 zip 含 run_crg + shebang python + import os/time + time.sleep + os.chdir + os.system bmatrix + 语法合法 B 变体 subprocess exit=0 + fake bmatrix 被调用(日志含 CWD=/ARGV=) + cwd==B target_dir + 跨输入 guard => §4 牙由 hidden-B cross-input + §4.2 subprocess(fake bmatrix 真调用)保证, layer=L1, k_check=17==k_rationale=17 ✓, 无 reframe, 保留。**metadata bug 待 @A**: level 缺标应 L1(与 layer=L1 一致), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-DetermSeedByName-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r828 reframe_note backfill batch3): 用户 xuebaok@hfhds201 (sess 1791463574990_um5we, mc=50) U#0 原话「/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen/run_compres 分析这个命令，每次生成的 pattern 都用不同的 seed，我想要相同名字开头的 pattern 共用一个 seed」(纯需求轮给目标+方法=相同名字 pattern 共用确定性 seed, 未给根因/修复), 意图形态=produce-action(verb「分析命令+想要共用 seed」=改 run_compress/vsim 使 seed 按名确定), 可便携性=高(纯 Python hash-to-seed, 无 EDA 二进制, asset_fidelity=A-faithful); trace agent 改 run_compress/vsim, case 交付 seed_from_name.py(按 pattern_name hash 产确定性 seed, 同名跨 corner 共用) 同形(零偏移, A-faithful); reframe_note=None→补(faithful 无 reframe); check.py 12 断言验 seed_from_name.py + py_compile + 参数校验 + hidden manifest B exit=0 + 输出行数==manifest 行数 + seed 字段 [0,2^31) 整数 + 同 pattern_name 跨 corner 同 seed(核心不变量) + 不同 pattern_name 不同 seed(无碰撞) + 跨输入 guard => §4 牙由 hidden-B cross-input 保证, layer=L1, k_check=12==k_rationale=12 ✓, 无 reframe, 保留。**metadata bug 待 @A**: level 缺标应 L1(与 layer=L1 一致), k_check 字段缺标应 12, shard 缺标应 B。",
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
