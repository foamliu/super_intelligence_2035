#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r827 (2026-11-18) metadata-debt backfill 档3 (reframe_note) batch2.
Source: r825 bounded queue 提议 (asset_fidelity 100% 收口后下一道 bounded queue =
        reframe_note backfill 160 missing P1). r826 batch1 +12 (235->247, miss 160->148).
        本轮 batch2 = alphabetical 续 12 missing after CTLETranDeck (r826 batch1 末位).
        reframe_note 247->259, miss 148->136.

Spec: r773-r800 档3 batch9-34 完成 reframe_note 32->235 (driver 三分 portability/Q&A-analysis/harness
      互斥可枚举归类). r826-r827 await-scan 期接续 backfill reframe_note 160 missing.
      本轮 batch2 12 case = 6 keep_reframe_for_teeth + 6 keep_faithful.

reframe_note text 来源:
  - keep_reframe_for_teeth case: spotcheck per_case_reasoning + cases/B trace_source(user@host/session/mc)
    + test_rationale k_check + asset_fidelity; driver 分类(portability/Q&A-analysis/harness).
  - keep_faithful case: r825 §观点(3) disclosure 完整性 — keep_faithful case 亦补 reframe_note
    记录「无 reframe + trace 意图同形便携判据」, §5 asset_provenance disclosure 成对字段完整。
    文本以 "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r7XX spotcheck batchN)" 开头。

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False。
       仅补 reframe_note, 不动 test_rationale/check.py/negative/asset_fidelity (asset_fidelity r824 已 100% 收口)。

Driver 分类 (12 case: 6 keep_reframe + 6 keep_faithful):
  - portability-driver (foundry PDK / 完整流不可沙盒复刻 / 权限拒绝+tool_result 清空 → level-1 proxy / 合成):
      2 case: CmlDivOscDiag (权限拒绝+清空→合成 .pt0) / CmlPvtAcReport (foundry→level-1 HSPICE proxy)
  - Q&A-analysis-driver (Q&A/分析报告 → 结构化 JSON for §4 subprocess 有牙):
      1 case: CfgMemNetlistExplain
  - harness-driver (完整流已跑完→子流抽取 / 功耗数值不确定→结构提取 / deck→Python+L2):
      3 case: CabufPvtDatAudit (vam-agent 已跑完→抽 .dat 解析子流) / ClampPwrStateExtract (功耗不确定→钳位管对结构) / CmdEdgeMeasGen (deck→meas_gen.py+L2 真跑)
  - keep_faithful (无 reframe, trace 意图同形便携): 6 case:
      CTLEtranChar / CapCharProps / CgtMeetExactlyFilter / CioLeakageExtract /
      CmlDividerSweepTbGen / CmpStg1CapAdd

metadata bug 待 @A 档1/档2 sweep (reframe_note scope 限定不修, 仅在 note 文本标注):
  - 多 case layer/level 缺标或误判 (应 L1/L2), k_check 字段缺标, shard 缺标, asset_fidelity 个别应微调
  - 与 r773-r800/r826 档3 同口径: reframe_note backfill 不动其他字段
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    # ===== 6 keep_reframe_for_teeth =====
    "EDA-Eval-DesignFlow-CabufPvtDatAudit-001":
        "IO_CABufCore PVT corner 时序表征审核报告生成->produce (harness-driver reframe, B档 sub-task extraction + asset_fidelity, §4 有牙必要, r727 spotcheck batch7): 用户 e03179@hfeg0pkn002 (sess 1791786108086_vumhg, mc=274) 调 vam-agent 对 IO_CABufCore 做 PVT corner 时序表征建模(FineSim 后端), 跑完产 cosim_timing_param/IO_CABufCore/ 下 TT/FF/SS × df0/dr0/tf0/tr0 共 12 个 .dat 角点结果文件, 真实意图=把这份 PVT corner .dat 结果整理成可机读的表征审核报告; A 不可行原因=完整流用 vam-agent 建模仿真已跑完不可重跑 → 抽「.dat 解析 + spec 合规审核报告生成」子流(A=trace 真实 .dat 12 文件, B=5 corner 合成变体 + 更紧 spec, asset_fidelity=synth_data); reframe 由 harness-driver(已跑完→子流抽取) 非 portability/Q&A; check.py 16 断言验 build_pvt_audit.py 在 A/B 上解析 .dat + 按 spec.json 判 PASS/FAIL + worst corner + 跨输入 A vs B 反硬编码 => 收敛为 produce-harness 子流抽取是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标(应 L1, check 仅 subprocess 跑候选 python 解析 .dat 文本+产报告), k_check 字段缺标应 16, level 缺标应 L1。",

    "EDA-Eval-DesignFlow-CfgMemNetlistExplain-001":
        "配置存储器网表结构化分析报告->produce (Q&A-analysis-driver reframe, 自然语言报告→结构化 JSON for §4 subprocess 有牙, r722 spotcheck batch3): 用户 eva1wu@hfeg0plg52 (sess 1793875415367_oue4a, mc=49) 就一份 HSPICE/CDL 配置存储器网表提结构化分析咨询(先问「什么是 cm」+「analysis dft cm」指向 /home/eva1wu/netlist), 助手读 711 行 T1_CM 配置存储器网表(AETHER-SE 导出, 24 位移位寄存器 T1_CM_Fram_Shift + 3-to-8 译码 T_Cm3to8DecClk + 512 位锁存阵列)产 6126 字自然语言结构化报告, 用户原话「给我一份结构化的分析报告」; A 不可行(为 §4 有牙)原因=自然语言报告不可被 subprocess 确定性判分 → 收敛为结构化 JSON(cfg_mem_netlist_analysis.json 含 file_overview/device_stats/structural_params/key_findings/risks/suggestions, JSON 替代自然语言文本为可解析有牙形式, A_netlist=真实还原 trace tool_result verbatim 711 行全网表, hidden_B=合成 T3_PM 16 位移位+4-to-16 译码+64 位锁存, 尺寸全异); reframe 由 Q&A-analysis-driver(analysis-Q&A→produce-JSON); check.py 31 断言验候选脚本在 hidden B 上 subprocess 退出 0 + 产合法 JSON + file_overview/device_stats/structural_params/key_findings/risks/suggestions 必需键齐全 + 跨输入 guard => 收敛为 produce-JSON 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确, level 缺标应 L1。",

    "EDA-Eval-DesignFlow-ClampPwrStateExtract-001":
        "DecEn_PwrUpLock 电源钳位块静态功耗分析->结构提取 (harness-driver reframe, 功耗数值跨 HSPICE 版本不确定→钳位管对结构提取可确定性判分, §4 有牙必要, r726 spotcheck batch6): 用户 harrywu@hfeg0pkn002 (sess 1794133519350_pchuf, mc=1005) U0 逐字「对 Cell DecEn_PwrUpLock 进行功耗分析，主要分析 MP4 和 MN4 造成的静态功耗」+「修改testbench，加入电流分析以及meas脚本」, agent 识别钳位管对(PMOS XMMP4 gate=PwrOn3 + NMOS XMMN4 gate=PwrOn3F, 上电反相器 XI8 产 PwrOn3F=·PwrOn3) 跑 FineSim TT/1.025V/98℃ 静态功耗(SecEn=1/0); A 不可行原因=功耗绝对数值跨 HSPICE 版本/收敛不确定 → 抽「钳位管对结构 + 正常态偏置逻辑」可确定性判分子流(非功耗数值), asset_fidelity=synth_deck; reframe 由 harness-driver(数值不确定→结构提取); check.py 15 断言验 .py 提取 clamp_pmos/clamp_nmos 子对象(instance/gate/gate_off_logic/off_state) + 正常态偏置(非功耗数值) + 跨输入 guard => 收敛为 produce-结构提取是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标(应 L1, check 仅 subprocess 跑候选 python 解析 .sp 文本提取结构, 不真跑 FineSim 二进制验功耗数值), level 缺标应 L1, k_check 字段缺标应 15。",

    "EDA-Eval-DesignFlow-CmdEdgeMeasGen-001":
        "命令门控 Nth-edge .measure deck 生成->produce (harness-driver reframe, 纯 deck 生成→Python meas_gen.py + L2 真跑 FineSim, §4 有牙必要, r724 spotcheck batch5): 用户 wenwenl@hfeg0plg74 (sess 1790841917726_hgfso, mc=59) 要求生成「检测 wr command 的第 4 个 CLK 上升沿」的测量脚本, agent 用 search_codebase/list_allowed_files/editor 在 DDR6 DSCQA sim_setup 上下文下生成 meas_wr4thck.fscr/.sp(命令门控 Nth-edge .measure deck), 单轮纯 spice 意图; A 不可行(为 §4 有牙)原因=纯 deck 文本生成无 subprocess 真跑牙 → 扩展为「meas_gen.py 读 spec.json 自动生成 .measure deck + 跑 FineSim + 解析 .mt0 + 输出 report.json」L2 runnable + Python 化(asset_fidelity=synth_deck); reframe 由 harness-driver(deck→Python script for hidden-B + L2 真跑); 意图核心(命令门控 Nth-edge .measure deck 生成)完整保留; check.py 14 断言真跑 FineSim hidden B + B t_Nthck 匹配 .75 标定 GT(1.604e-8, 2% 容差) + t_dsu=t_Nthck-t_data_edge 匹配 GT(5% 容差) + 跨输入 guard => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确, level 缺标应 L2, k_check 字段缺标应 14。",

    "EDA-Eval-DesignFlow-CmlDivOscDiag-001":
        "DDR4 DQSIR CML ÷2 分频器不振荡诊断器->produce (portability-driver reframe, 权限拒绝+tool_result 清空→合成忠实自包含 .pt0, §4 有牙必要, r728 spotcheck batch8): 用户 joeyl@hfeg0pkn004 (sess 1794460479085_wqh78, mc=235, 10.129.2.13) 给 2_TRAN.sp 路径让 agent 修复不振荡的 CML ÷2 分频器(ResCtr0=0 PMOS 负载过强根因), agent 在 /ai_sandbox 建副本跑 FineSim .print tran; A 不可行原因=/rundata/m2701 项目目录对 e0031982 权限拒绝 + FineSim tool_result 已清空 → B 档合成忠实自包含 .pt0 振荡诊断器(asset_fidelity=synth_deck); reframe 由 portability-driver(权限+asset 不可复刻→合成), 非 Q&A→produce; check.py 10 断言验 cml_divider_osc_diag.py 在 hidden B 上输出合法 JSON(signals/clock_freq_GHz/divide_ratio/verdict + 4 信号 swing_mV/rising_edges/freq_GHz/status) + verdict==divide_by_2_ok + 分频比量化 + 跨输入 guard => 收敛为 produce-诊断器是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确, level 缺标应 L2, k_check 字段缺标应 10。",

    "EDA-Eval-DesignFlow-CmlPvtAcReport-001":
        "CML PMOS 差分对 PVT AC 表征报告生成->produce (portability-driver reframe, foundry 模型不可沙盒复刻→level-1 HSPICE proxy, B档 sub-task + asset_fidelity, §4 有牙必要, r727 spotcheck batch7): 用户 lvyy@10.129.2.13 (sess 1793669959152_3123n, mc=576) 在 /proj/m2701/V0_DDR4/workdir/lvyy/simulation/LP6/small_schematic/ 搭电流镜偏置+PMOS 输入对+负载电阻 CML 差分对, 要求跑 PVT(tt/ss/ff × -40/25/130 × 0.79/0.96/0.875) AC 仿真给 100M/4G/4.4G 增益 + -3dB 带宽 + 电流 max/min; A 不可行原因=完整流用 CXMT foundry 模型不可沙盒复刻 → 便携 level-1 网表 + HSPICE proxy(asset_fidelity=synth_deck); reframe 由 portability-driver(foundry 不可复刻); check.py 14 断言验 cml_pvt_ac_report.py 在 hidden B 上 subprocess 真跑 HSPICE + 4 corner 全跑 + current_min/max + .lis 解析 + hspice_ran==true + 跨输入 guard => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确, level 缺标应 L2, k_check 字段缺标应 14。",

    # ===== 6 keep_faithful (无 reframe, trace 意图同形便携) =====
    "EDA-Eval-DesignFlow-CTLEtranChar-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r722 spotcheck batch3): 用户 kaixuanx@hfeg0pkn001 (sess 1792720528359_2tuxj, mc=91) T0 原话「我设计了一个CTLE电路...现在我想仿真相关的瞬态性能...帮我重新写一个仿真脚本」(CTLE_active_ind DDR RX 均衡器 NMOS 差分对 + R||C 源简并有源电感式高频 peaking, AC 表征已跑完要做瞬态), 意图形态=produce-action(写仿真脚本做瞬态表征), 可便携性=中(HSPICE 真跑, .75 上 HSPICE 可跑便携 deck); trace agent 踩关键坑 HSPICE 伪随机源是 LFSR 而非 PRBS(PRBS() 报错→改 LFSR()), 产 ctle_act_ind_tran_v2.sp(.TRAN 1024 bit@7.2Gbps + 5 类 .MEAS), case 交付 ctle_tran.py(瞬态表征工具, 生成 + 真跑 HSPICE deck) 同形(用户原话「仿真脚本」直接映射到该 Python harness, harness 即更可复用的仿真脚本, 核心意图 + 核心陷阱 LFSR非PRBS 完整保留, 零偏移); reframe_note=None→补(faithful 无 reframe, trace 意图与 case 交付同形映射); check.py 16 断言验 ctle_tran.py + tran_report_A.json + 14 必需度量键齐全(eye_vmax/eye_vmin/eye_amp/eye_mid/outcm) + 候选 fresh A 实跑一致(防造假) + L2 真跑 HSPICE + 跨输入 guard => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑 HSPICE 保证, layer=L2, k_check=16==k_rationale=16 ✓, 无 reframe, 保留。**metadata bug 待 @A**: level 缺标应 L2(与 layer=L2 一致)。",

    "EDA-Eval-DesignFlow-CapCharProps-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r724 spotcheck batch5): 用户 owench@hfeg0pkn002 (sess 1793702295738_4bsmv, mc=14) A-faithful verbatim U0 逐字「新建一个Capacitance2文件夹... 能在已有功能的基础上计算Ceff Cch Cgd0这三个性质吗？」(MOS 电容 Cgg characterization, 给 Capacitance 目录 4 份 Cgg 数据 ntn/ptn × G4BCIP/V1), 意图形态=produce-action(写脚本计算 Ceff/Cch/Cgd0), 可便携性=高(纯文本后处理, 无 EDA 二进制); trace agent 写 compute_properties.py(积累区法 Cd_acc/W=Cgd0, Cg_acc-2Cd=Cch, Cch/(WL)=Cox, eps0*3.9/Cox=EOT), case 交付 compute_properties.py 同形(零偏移); reframe_note=None→补(faithful 无 reframe); check.py 14 断言验 zip 含 compute_properties.py + py_compile + B 运行 exit 0 产非空 CSV + CSV 13 列(file/dtype/corner/temp/w/l/vg_acc/cgd0_fFperum/cch_fF/cox_fFperum2/eot_nm/ceff_fF) + 行数==B 组合数(16) + NMOS cgd0 独立重算容差 1e-6 + cch 容差 + cross-input guard => §4 牙由 hidden-B cross-input 保证, asset_fidelity=A-faithful, k_check=14==k_rationale=14 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 缺标(应 L1, check 仅 subprocess 跑候选 python 解析电容数据产 CSV, 0 EDA 二进制), level 缺标应 L1。",

    "EDA-Eval-DesignFlow-CgtMeetExactlyFilter-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r738 spotcheck batch17): 用户 ericw@hfhds201 (sess 1791768325372_y91i6, mc=34) A-faithful verbatim USER#1 逐字「给我做一个表格 并且把VrefCA VrefCS SRX REF RFM 相关得去除」(在已分析的 cg_t/3型 covergroup 过滤出 meet_exactly bin 未命中 134 条基础上, 按关键词去除 VrefCA/VrefCS/SRX/REF/RFM 相关项, 得 kept=29/removed=105 过滤表, 分布 0/3=61,1/3=48,2/3=25), 意图形态=produce-table(显式要求产表格 + 关键词过滤是表格内容要求), 可便携性=高(纯文本 CSV 后处理); trace agent 读 table1/table2/table3 按 meet_exactly bin All Cov 0/1 判未命中输出 134 行表, case 忠实复刻 produce-table(写 cgt_filter.py 产 cgt_meet_exactly_filter.csv 表格) 同形(零偏移, 交付物=过滤表与用户意图一致); reframe_note=None→补(faithful 无 reframe); check.py 16 断言验 cgt_filter.py + cgt_meet_exactly_filter.csv + §4.1 hidden B cross-input guard(B csv 行数/分布≠A)+§4.9 防硬编 + 列名/coverage 集合/kept-removed 计数确定性 => §4 牙由 hidden-B cross-input 保证, layer=L1, k_check=16==k_rationale=16 ✓, 无 reframe, 保留。**metadata bug 待 @A**: asset_fidelity 缺标(应 real-from-trace, 用真实 cov_work dump 场景便携化为 fixture json)。",

    "EDA-Eval-DesignFlow-CioLeakageExtract-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r755 spotcheck batch34): 用户 clarawu@hfeg0plg106 (sess 1794299323217_5oub3, mc=30) A-faithful verbatim U0 逐字「帮我写一个python脚本，从 cio.ma0 和 leakage.mt0 中提取 cio 的 leakage 的信息，整理成表格」(FineSim 仿真后 .measure 输出 cio.ma0(cdq_10g/temper/alter#)+leakage.mt0(i_leak_pu/i_leak_pd/temper/alter#), 按 alter# 关联两文件, 输出 CSV 无 alter/temper 列), 意图形态=produce-action(verb「写脚本」显式要 script + 提取整理表格), 可便携性=高(纯 .ma0/.mt0 文本后处理, 无 EDA 二进制); trace agent 写 extract_all.py, case 交付 cio_leakage_extract.py 同形(零偏移); reframe_note=None→补(faithful 无 reframe); check.py 11 断言验候选 cio_leakage_extract.py + §4.1 hidden B cross-input + py_compile + B1 exit 0 + CSV 列头==cdq_10g,i_leak_pu,i_leak_pd(无 alter/temper) + 行数==B alter 数 + cdq_10g 一致性 + 跨输入 guard => §4 牙由 hidden-B cross-input 保证, layer 应 L1(check 仅 subprocess 跑候选 python 解析 .ma0/.mt0 文本 + 验 CSV 结构, 0 EDA 二进制, check.py 实读仅 subprocess.run([sys.executable,script])), k_check=11==k_rationale=11 ✓, track=faithful, 无 reframe, 保留。**metadata bug 待 @A**: layer/level 缺标应 L1, k_check 字段缺标应 11, asset_fidelity 缺标(应 real-from-trace), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-CmlDividerSweepTbGen-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r618 audit keep): 用户 joeyl@hfeg0pkn004 (sess 1794481033621_h3vpf, mc=131, 10.129.2.13) 在已锁定 ResCtr0=0+nl_tail8 胜出配置(全速率 8.8GHz 5-corner 全部 ÷2 锁定)基础上做 SWING×Vref 二维扫描看 skew 变化(swing 0.05~0.2 步进 0.05, Vref 0.4~0.7 步进 0.1), 意图形态=produce-tool(显式要求生成扫描 TB), 可便携性=中(生成 .sp deck 文本); trace agent 写 run_swvref.py 生成 16 个 5-corner 扫描 TB(移 .probe + 激活 5corner .inc + 保留 .measure), case 交付 cml_divider_sweep_tbgen.py 同形(零偏移, A-faithful); reframe_note=None→补(faithful 无 reframe); check.py 10 断言验 cml_divider_sweep_tbgen.py + §4.1 hidden B cross-input(subprocess 真跑候选 exit=0 产 .sp 文件) + TB 数量==B 网格 swing_count*vref_count(12) + VREF/SWING 参数与文件名编码一致 + 5corner .inc + 跨输入 guard => §4 牙由 hidden-B cross-input 保证, asset_fidelity=A-faithful, k_check=10, 无 reframe, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 跑候选 python 产 .sp 文本, 是否真跑 FineSim 二进制待核; 若仅产 .sp 则应 L1), level 缺标, k_check 字段缺标应 10。",

    "EDA-Eval-DesignFlow-CmpStg1CapAdd-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r618 audit keep): 用户 jiangbaol@hfeg0pkn003 (sess 1793344639876_ig5hm, mc=3, legacy 低于 mc>=10 阈值审计判意图非判 mc 保留) DDR5 DQ slicer strong-arm 比较器 testbench 添加参数化输出电容(给 004_onlySlicer_delay_dejoa_test_cmdm.sp 路径, 要求在比较器 out_stg1 两端 outp_stg1/outn_stg1 添加电容, value 设为参数并在 .param 中定义, 以新 .sp 输出), 意图形态=produce-action(verb 添加电容=action 产新 .sp), 可便携性=高(纯 .sp 文本编辑, 无 EDA 二进制); trace 金标准 add_cap.sh(.param cthin 行后插 .param Cout_stg1=1f, .end 前插两对地电容 Coutp/Coutn_stg1), case 交付 add_outstg1_cap.py 同形(零偏移, A-faithful); reframe_note=None→补(faithful 无 reframe); check.py 13 断言验 zip 含 add_outstg1_cap.py + py_compile + hidden B(cmdm_B.sp) exit 0 产非空 .sp + 新增 .param 电容参数(输入 B 不存在) + ≥2 条电容元件行(非注释 C 开头) + 电容引用 B 真实差分对节点 + 跨输入 guard => §4 牙由 hidden-B cross-input 保证, asset_fidelity=A-faithful, k_check=13==k_rationale=13 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 缺标(应 L1, check 仅 subprocess 跑候选 python 编辑 .sp 文本, 0 EDA 二进制), level 缺标应 L1。",
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
