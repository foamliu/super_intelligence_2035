#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r834 (2026-11-18) metadata-debt backfill 档3 (reframe_note) batch9.
Source: r825 bounded queue 提议 (reframe_note backfill 160 missing P1).
        r826 batch1 +12 (235->247, miss 160->148).
        r827 batch2 +12 (247->259, miss 148->136).
        r828 batch3 +12 (259->271, miss 136->124).
        r829 batch4 +12 (271->283, miss 124->112).
        r830 batch5 +12 (283->295, miss 112->100).
        r831 batch6 +12 (295->307, miss 100->88).
        r832 batch7 +12 (307->319, miss 88->76).
        r833 batch8 +12 (319->331, miss 76->64).
        本轮 batch9 = alphabetical 续 12 missing after R1R4NetlistCheck (r833 batch8 末位),
        起算 RcVizTreeAnalyzer, R->S 段.
        reframe_note 331->343, miss 64->52.

Spec: r773-r800 档3 batch9-34 完成 reframe_note 32->235 (driver 三分 portability/Q&A-analysis/harness
      互斥可枚举归类). r826-r834 await-scan 期接续 backfill reframe_note 160 missing.
      本轮 batch9 12 case = 7 keep_reframe portability + 1 keep_reframe harness + 4 keep_faithful
      (含 1 keep_faithful-restored-image WAVEVIEW β7 RiseEdgeMarginMeas).

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False。
       仅补 reframe_note, 不动 test_rationale/check.py/negative/asset_fidelity (asset_fidelity r824 已 100% 收口)。

Driver 分类 (12 case: 7 keep_reframe portability + 1 keep_reframe harness + 4 keep_faithful):
  - portability-driver (real PEX/HSPICE/FineSim netlist+deck+.md0 / /proj path 不可沙盒复刻 -> synth_deck / synth_data):
      7 case: RcVizTreeAnalyzer (real 多 GB Star-RC/Calibre PEX 网表不可沙盒复刻->synth_data, characterization) /
              RcurrDirClassify (real HSPICE netlist+.measure .lis 不可复刻->synth_deck, characterization) /
              ReadsigAddrTbl (real ALPS netlist 不可沙盒直读->synth_deck, characterization; **track=faithful 但 asset=synth_deck mismatch**, track≠asset_provenance 待 @A 复核) /
              RonCurveEvaluator (real FineSim netlist+.md0 不可复刻->synth_deck, spice_sim) /
              RonCurveSmoothness (real FineSim Ron.md0 不可复刻->synth_data, spice_sim) /
              SAoptPwrDly (real /proj/shdc models+/proj/dscqa testbench 不可复刻->synth_deck, spice_sim, L3) /
              SaDcSweepTbGen (real netlist+ref_test.sp+.lib 路径不可复刻->synth_deck, spice_sim)
  - harness-driver (no real artifact input -> synth_data spec for hidden-B cross-input teeth):
      1 case: SarAdc8bNetlistGen (real trace 用户仅 prompt '帮我写 8bit SAR ADC hspice 代码' 无结构化输入, case 加 spec.json 给 hidden-B cross-input 10-bit vs 8-bit, spice_sim; **from-scratch generation 亚型**, 区别 file→script / multi-round→single 亚型)
  - keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful):
      4 case: RevCali3DCoord (real Python autosim_script source 可 scp 便携->A-faithful, characterization; mc=7 边界待 @A host-verify) /
              RonMonoDiag (real FineSim 5 corner .md0 小文本可 scp 便携->A-faithful, spice_sim) /
              RsCalcAutoVia (real CXMT Virtuoso SKILL config 可 scp 便携->A-faithful, characterization, layer=L2 if check真跑) /
              RiseEdgeMarginMeas (**keep_faithful-restored-image WAVEVIEW β7**: 原意图需看 Synopsys WaveView3 波形截图, 旧规则降级为文本替身, r553 WAVEVIEW 协作恢复为 image 输入, asset=synth_deck-restored-image, spice_sim; 区别于纯 A-faithful 因 image 输入是 restored 而非 trace 原生 asset)

R->S 段 domain-wave 观察: batch9 keep_faithful 占比 33% (4/12) 介于 batch8 P段 8% 与 batch7 N段 50% 之间,
  因 R 段 mixed: PEX/HSPICE netlist 不可便携群 (5 portability) 与 .md0/Python/SKILL 可便携群 (3 A-faithful) 并存,
  与 N段 Netlist* 群 (网表文本 scp 便携 -> A-faithful 主流) 对比 R 段更 hetero.
  R 段 characterization 域占比 5/12=42% (RcViz/Rcurr/Readsig/RevCali/RsCalc), 显著高于 batch8 P段 0% (P段全 spice_sim),
  R 段是 characterization 域回流段.
  WAVEVIEW restored-image 1 case (RiseEdgeMarginMeas β7) 落 R 段, 是 designflow 与 vision 协作的 restored-image 群成员.
  harness-driver 新亚型: SarAdc8bNetlistGen 是 from-scratch generation 亚型 (real trace 无结构化输入, case 加 spec.json for hidden-B teeth),
  与 batch8 QueueCorePolicyPatch multi-round→single 亚型、r827/r828 file→script 亚型并列, 三个 harness 亚型现均已有实例.

metadata bug 待 @A 档1/档2 sweep (reframe_note scope 限定不修, 仅在 note 文本标注):
  - 多 case layer 缺标或 k_check 缺标应补 (rc_viz_tool/RonCurveEvaluator/RonCurveSmoothness/SAoptPwrDly/SaDcSweepTbGen/RsCalcAutoVia k_check=None)
  - track 缺标 (RcVizTreeAnalyzer/RonCurveEvaluator/RonCurveSmoothness/RonMonoDiag track=None 应补)
  - track≠asset_provenance mismatch: ReadsigAddrTbl track=faithful 但 asset=synth_deck
  - 与 r773-r800/r826-r833 档3 同口径: reframe_note backfill 不动其他字段
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    # ===== 7 keep_reframe_for_teeth (portability-driver) =====
    "EDA-Eval-DesignFlow-RcVizTreeAnalyzer-001":
        "Star-RC/Calibre 后仿 PEX 网表 RC 走线可视化工具(层次树+自然排序+寄生统计+等效电阻)->produce (portability-driver reframe, real 多 GB Star-RC/Calibre PEX 网表不可沙盒复刻->synth_data, §4 有牙必要, r834 reframe_note backfill batch9): 用户 shanliny@hfeg0pkn005 (sess 1794453941272_vxf3o, mc=175, characterization 域) 迭代改进 rc_viz_tool2.py(U1 加 GUI/U2 自动检索网表填充 device 节点/U3 自然排序 NET1,NET2,NET10 非 NET1,NET10,NET100/U4 修误报/U5 多 GB 网表流式读取防卡死/U6 树状分层显示 xtop/XBKB/xlio 逐层展开/U7 节点电阻选择框逻辑修正); 本 case 取其可独立测试的分析核心=解析 PEX 网表+层次树+自然排序+寄生统计+等效电阻; A 不可行原因=real 多 GB PEX 网表不可沙盒复刻 -> 收敛为 rc_viz_tool.py(读 hidden B synth PEX 网表, asset_fidelity=synth_data); reframe 由 portability-driver(real PEX 网表不可复刻, 多 GB 体积沙盒无法容纳); 意图核心(netlist 流式逐行 parse + 层次化路径 '.' 分层树展开 + 自然排序 natsort + device/节点选择 + 寄生 R/C 统计 + 等效电阻计算 + JSON 结构化输出 nodes/devices/tree/stats/eff_resistance)完整保留; check.py 14 断言验 zip 含 rc_viz_tool.py 且非空>100B + py_compile 通过 + subprocess 在 hidden B 上 --nodes NET1 NET3 --json exit0 输出有效 JSON + JSON 含 nodes/devices/tree/stats/eff_resistance 五键 + nodes 自然排序==[NET1,NET2,NET3,NET10,NET20] + cross-input guard(A≠B 网表不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(若 check 仅 subprocess 跑候选 python 解析网表文本 0 EDA 二进制应 L1), level 缺标, k_rationale/k_check 缺标应 14, track 缺标应 synthesized, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-RcurrDirClassify-001":
        "DRAM FIT EM 可靠性: 电阻支路电流方向分类(ratio-gated, near-tol caveat fix)+RMS 排序+几何表->produce (portability-driver reframe, real HSPICE netlist+.measure .lis 不可沙盒复刻->synth_deck, §4 有牙必要, r834 reframe_note backfill batch9): 用户 e0045488@hfeg0pkn002 (sess 1792459158095_dfaqe, mc=211, characterization 域) 在 method2 上发现 pkpos/pkneg 都在 i_tol 附近时被误判单方向, 提出新 ratio 算法(只 below-tol 当双峰都<=tol, 否则纯 ratio 判), 要求 critique+实现; 用户已把每个电阻支路用 0V vprobe 串联做安培计写进 HSPICE 网表, 对每个电阻写三行 .measure i_pkpos_<R>/i_pkneg_<R>/i_rms_<R>; A 不可行原因=real HSPICE netlist+.measure .lis 不可沙盒复刻 -> 收敛为 curr_dir_classify.py(CLI <netlist.sp> <spec.json> <out_dir>, 读 hidden B synth HSPICE netlist+spec, asset_fidelity=synth_deck); reframe 由 portability-driver(real netlist+.lis 不可复刻); 意图核心(subprocess 真跑 HSPICE 拿 .lis + 6 电阻 pkpos/pkneg/rms 数值解析 + ratio-gated 方向分类 near-tol caveat 修复 + RMS 排序 + direction_table.csv 几何表)完整保留; check.py 14 断言验 zip 含 curr_dir_classify.py+direction_table_B.csv + py_compile + 候选在 hidden B 真跑 HSPICE(hspice_ran=True) + B 全 6 电阻 pkpos/pkneg/rms 数值解析齐 + cross-input guard(A≠B netlist 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess(含 HSPICE 真跑)结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确(check 验 HSPICE 真跑含 EDA 二进制), level 缺标应 L2, k_rationale/k_check 缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-ReadsigAddrTbl-001":
        "DRAM readout 地址表提取 skill(netlist 解析版 TransferInfoToReport: T_ReadSigDecVcc/Vccp/Vdd1 实例扫+7-bit 排序+fnReadSigGrpSel10 过滤+剥 fnReadSig 前缀)->produce (portability-driver reframe, real ALPS netlist 不可沙盒直读->synth_deck, §4 有牙必要, r834 reframe_note backfill batch9): 用户 jasonxu@hfeahpc501 (sess 1792551272867_jnf1q, mc=470, characterization 域) 把 pyAether 原理图版 TransferInfoToReport(drvqa_cmos_digital,T_ReadSigLeft) 改造成 netlist 解析版 skill 'jasonxu-analogkit/readsigCM': 扫 ALPS netlist 里 T_ReadSigDecVcc/Vccp/Vdd1 readout 实例, 按引脚列序抽 A7 选通+A6..A0 位编码(D<n>->1)+DecOut, 按 fnReadSigGrpSel10 过滤、7-bit 排序、剥 fnReadSig 前缀, 输出 digitalPinInfo_final_*.csv; A 不可行原因=real ALPS netlist 不可沙盒直读(原理图不可直读, 项目环境里 netlist 路径权限) -> 收敛为 readsig_addr_tbl.py(读 hidden B synth ALPS netlist, asset_fidelity=synth_deck); reframe 由 portability-driver(real netlist 不可沙盒直读); 意图核心(T_ReadSigDecVcc/Vccp/Vdd1 实例扫描 + A7 选通+A6..A0 位编码 D<n>->1 + fnReadSigGrpSel10 过滤 + 7-bit 二进制升序 + 剥 fnReadSig 前缀 + digitalPinInfo_final CSV 9-token 行输出)完整保留; check.py 15 断言验 zip 含 .py 工具 + 工具在 hidden B 清单上 exit0 + 产恰好 1 个 digitalPinInfo_final_*.csv + CSV 行数==gold_B 23 + 每行 9 token(7 位+type+DecOut) + 行按 A6..A0 7-bit 二进制升序 + cross-input guard(A≠B netlist 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: **track=faithful 但 asset=synth_deck mismatch** (track≠asset_provenance, track 应为 synthesized 或 asset 应为 A-faithful; 因 real netlist 不可直读, 实际 asset=synth_deck, track=synthesized 更准), layer=L1 正确(check 仅 subprocess 跑候选 python 解析网表文本 0 EDA 二进制), level 缺标应 L1, k_check=15 已标 ✓, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-RonCurveEvaluator-001":
        "DDR4 DQ FinalDrv Ron 曲线评估: rpu_50/rpd_50 vs zqdec 解析+穿 230ohm 水平线 cross_code+单调性 violation+光滑度残差->produce (portability-driver reframe, real FineSim netlist+.md0 不可沙盒复刻->synth_deck, §4 有牙必要, r834 reframe_note backfill batch9): 用户 clarawu@hfeg0pkn003 (sess 1794467464751_xsocp, mc=310, spice_sim 域) 在 DDR4 DQ FinalDrv Ron/cio_leakage 电路优化 session 要求 '优化电路使 Ron 曲线穿过 230ohm 水平线, 保证单调性, 尽量光滑(残差小), CIO 尽量小, PVT 下都穿 230ohm 时优化 CIO/mismatch'; agent L3 迭代链 read_files(netlist_delvto/stimulus_{Ron,cio,leakage}.sp)+HSPICE 跑+解析 .md0+评估曲线; A 不可行原因=real FineSim netlist+.md0 不可沙盒复刻 -> 收敛为 ron_curve_evaluator.py(读 hidden B synth .md0+spec, asset_fidelity=synth_deck); reframe 由 portability-driver(real netlist+.md0 不可复刻); 意图核心(rpu_50/rpd_50 vs zqdec 曲线 parse + 穿 230ohm 水平线 cross_code 检测 + 单调性 mono_violations + 光滑度残差 + PVT corner 多曲线评估)完整保留; check.py 12 断言验 zip 含 ron_curve_evaluator.py + 跑 hidden B 输出合法 JSON 含 rpu_50/rpd_50 曲线 + rpu_50.crosses 与 oracle 一致 + rpu_50.cross_code 容差内 + rpu_50.mono_violations==oracle + rpd_50.mono_violations==oracle + cross-input guard(A≠B .md0 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(若 check 仅 subprocess 跑候选 python 解析 .md0 文本 0 EDA 二进制应 L1), level 缺标, k_rationale/k_check 缺标应 12, track 缺标应 synthesized, shard 缺标应 B。与 RonCurveSmoothness-001(synth_data, 同 clarawu@hfeg0pkn003 不同 sess ua9tu)/RonMonoDiag-001(A-faithful, clarawu@hfeg0pkn004)不同 session+不同交付物, 非近重复, 各自保留。",

    "EDA-Eval-DesignFlow-RonCurveSmoothness-001":
        "FineSim .md0 Ron 曲线光滑度分析: 折行 .md0 parse+相邻步长/二阶差分 rms/单调性跳变检测/1/(a+b·z) 拟合+报告->produce (portability-driver reframe, real FineSim Ron.md0 不可沙盒复刻->synth_data, §4 有牙必要, r834 reframe_note backfill batch9): 用户 clarawu@hfeg0pkn003 (sess 1794465241456_ua9tu, mc=29, spice_sim 域) 让 agent 写 Python 脚本从 FineSim .md0 测量文件(Ron.md0)中提取 rpu_50/rpd_50 随 zqdec 变化的曲线光滑度; agent 写 analyze_ron_smoothness.py(11811B) 首跑 parser 找不到列头 FAIL 后修复 PASS, 输出 rpu_50 64 点 2 跳变(15->16,47->48); A 不可行原因=real FineSim .md0 不可沙盒复刻 -> 收敛为 ron_smoothness_analyzer.py(读 hidden B synth .md0+manifest, asset_fidelity=synth_data); reframe 由 portability-driver(real .md0 不可复刻); 意图核心(折行 .md0 parse + x_col/y_cols manifest 驱动 + 相邻步长/二阶差分 rms + 单调性 nonmono_count 跳变检测 + 1/(a+b·z) 拟合 + 报告 JSON curves[rpu_50,rpd_50])完整保留; check.py 13 断言验 zip 含 ron_smoothness_analyzer.py 且非空>100B + py_compile + subprocess 在 hidden B 上 exit0 产含 curves[rpu_50,rpd_50] 有效 JSON + rpu_50.n==48(ground truth) + rpu_50.nonmono_count==3(独立复算) + cross-input guard(A≠B .md0 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 仅 subprocess 跑候选 python 解析 .md0 文本 0 EDA 二进制应 L1), level 缺标, k_rationale/k_check 缺标应 13, track 缺标应 synthesized, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SAoptPwrDly-001":
        "StrongARM comparator(DqIb_strongarm_pmos)power-constrained delay 优化: 8 sizing knobs sweep 最小化 slicer2nd_dly_r0/r1 受 Cur_slicer_latch_avg<=target 约束, HSPICE 真跑->produce (portability-driver reframe, real /proj/shdc models+/proj/dscqa testbench 不可沙盒复刻->synth_deck, §4 有牙必要, r834 reframe_note backfill batch9): 用户 jiangbaol@hfeg0pkn002 (sess 1790245155745_i5ae7, mc=119, spice_sim 域) 在 DqIb_strongarm_pmos 上提 '优化该电路功耗至 534uA, 同时 delay 最小', 后续 460uA->380uA 递进; sweep 8 sizing knobs(pmoswidth/finger, nmoswidth/finger, itailwidth/finger, inwidth/finger)最小化 slicer2nd_dly_r0/r1 受 Cur_slicer_latch_avg<=target; A 不可行原因=real /proj/shdc/models/G4B 路径+/proj/dscqa/V0_LP6/simdir/finesim workdir testbench 不可沙盒复刻 -> 收敛为 sa_opt.py(读 hidden B synth HSPICE deck+spec, asset_fidelity=synth_deck); reframe 由 portability-driver(real models+testbench 不可复刻); 意图核心(8 sizing knobs sweep + power target 约束 + HSPICE 真跑 slicer2nd_dly_r0/r1 量测 + Cur_slicer_latch_avg 量测 + best 设计选取 + sweep_log)完整保留; check.py 12 断言验 zip 含 sa_opt.py + py_compile + 候选在 A 上 exit0 产 opt_report_A.json + opt_report_A 含 6 必需键(baseline/power_target/n_designs/n_feasible/best/sweep_log) + A best 非空且独立复跑 HSPICE 一致 + cross-input guard(A≠B spec 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess(含 HSPICE 真跑)结构性必要, layer=L3 multi-tool chain(HSPICE 多次真跑+sizing sweep+约束优化), 保留。**metadata bug 待 @A**: layer=L3 正确, level 缺标应 L3, k_rationale/k_check 缺标应 12, track=faithful 但 asset=synth_deck **mismatch**(track≠asset_provenance, track 应为 synthesized), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SaDcSweepTbGen-001":
        "CXSA sense-amplifier 直流扫描仿真 testbench 生成(TT 工艺角/125°C/vad2=1.4V/Iso 关闭/Sel 栅压 1.77V/OC/PreEq 栅压扫描 1.17-1.77V/观测 BL 电压)->produce (portability-driver reframe, real netlist+ref_test.sp+.lib 路径不可复刻->synth_deck, §4 有牙必要, r834 reframe_note backfill batch9): 用户 t0002614@hfeg0plg105 (sess 1794290579357_trnx0, mc=35, spice_sim 域) 在 /home/t0002614/workspace/ZhuLong/TestSA 下维护 CXSA sense-amplifier 仿真验证流程, 目录含真实网表(顶层 subckt sim_sa_dc_check, 含 Iso/Sel/OC/PreEq 四组控制管与 BL 位线节点、vad2! 隔离电源)+参考测试网表 ref_test.sp(HSPICE/FineSim deck, 含 .lib 路径、netlist .inc); A 不可行原因=real netlist+ref_test.sp+.lib 路径不可沙盒复刻 -> 收敛为 sa_dc_sweep_tb_gen.py(读 hidden B synth netlist+ref deck, asset_fidelity=synth_deck); reframe 由 portability-driver(real netlist+deck 不可复刻); 意图核心(netlist 顶层 subckt 例化 + .lib corner 替换 + .temp 设置 + vad2! 电源 + Iso 关闭/Sel栅压/OC栅压/PreEq 栅压扫描参数替换 + .dc 扫描 + .print v(BL) 观测)完整保留; check.py 15 断言验 zip 含 sa_dc_sweep_tb_gen.py + 候选脚本 py_compile + 候选在 hidden B1 上 exit0 产 out_tb.sp+out_report.json + B1 out_tb.sp 含 .lib ... ff(corner 正确) + .temp -40(温度正确) + vad2 + cross-input guard(A≠B netlist 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L1 正确(check 仅 subprocess 跑候选 python 生成 deck 文本 0 EDA 二进制), level 缺标应 L1, k_rationale/k_check 缺标应 15, shard 缺标应 B。",

    # ===== 1 keep_reframe_for_teeth (harness-driver, from-scratch generation 亚型) =====
    "EDA-Eval-DesignFlow-SarAdc8bNetlistGen-001":
        "8bit SAR ADC HSPICE 网表 from-scratch 生成(电荷再分配架构 Vcm-based switching, 0.18um CMOS/1.8V/1MS/s, bootstrap_switch/inv/StrongARM comparator/unit cap array)->produce (harness-driver reframe, real trace 用户仅 prompt 无结构化输入, case 加 spec.json 给 hidden-B cross-input 8-bit vs 10-bit for check teeth, spice_sim; **from-scratch generation 亚型**, r834 reframe_note backfill batch9): 用户 leo7c@hfeg0plg95 (sess 1793847690294_guobm, mc=159, spice_sim 域) 提 '帮我写一个 8bit SAR ADC 的 hspice 代码'; 金标准=assistant msg#15 write_sar_adc.py 生成完整 8 位 SAR ADC HSPICE 网表 sar_adc_8b.sp(电荷再分配架构 Vcm-based switching, 0.18um CMOS/1.8V/1MS/s, 含 bootstrap_switch 晶体管级自举采样开关/inv/StrongARM comparator 差分对+再生锁存+复位/unit cap array/SAR logic); A 不可行原因=real trace 无结构化 spec 输入(仅 prompt 文字描述), A-faithful 单 prompt 形态 check 无牙(无法 cross-input guard) -> 收敛为 gen_sar_adc.py(读 hidden B synth spec.json, asset_fidelity=synth_data); reframe 由 harness-driver(no real artifact input -> synth_data spec for hidden-B cross-input teeth, **from-scratch generation 亚型**: real trace 用户仅 prompt 无结构化输入, case 加 spec.json 给 8-bit vs 10-bit cross-input 让 check 能区分真假交付; 区别 file→script 亚型(r827/r828 real file 不可便携->script)与 multi-round→single 亚型(batch8 QueueCorePolicyPatch 多轮演进->单轮收缩)); 意图核心(SAR ADC 架构选择 Vcm-based switching + 位数/电源/采样率/单位电容参数驱动 + bootstrap_switch/StrongARM comparator/unit cap array/SAR logic 子电路例化 + .tran + .measure)完整保留; check.py 14 断言验候选脚本在 B1(10-bit)跑出 exit0 产 .sp + 网表含 .options+.tran+.END + 4 组电源 VDD/VREF/VCM/GND 齐全 + bootstrap_switch 子电路含>=6 MOSFET + comparator 子电路含>=8 MOSFET + cross-input guard(A≠B spec 8-bit vs 10-bit 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness+cross-input-spec 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, layer=L1, 保留。**metadata bug 待 @A**: layer=L1 正确(check 仅 subprocess 跑候选 python 生成网表文本 0 EDA 二进制), level 缺标应 L1, k_check=14 已标 ✓, shard 缺标应 B。**注**: 本 case 是 batch9 唯一 harness-driver, from-scratch generation 亚型首实证, 与 batch8 QueueCorePolicyPatch multi-round→single 亚型并列。",

    # ===== 4 keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful / restored-image) =====
    "EDA-Eval-DesignFlow-RevCali3DCoord-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r834 reframe_note backfill batch9): 用户 e0046686@hfeg0pkn001 (sess 1794221449278_bqqtk, mc=7, characterization 域) 要求在 autosim_script/rev_cali_tools 反标后端脚本中, 让 lib_timing_tools 抽 timing 按 (i_slew,c_slew,q_load) 三维坐标传递, 匹配 template table 后抽值; 先梳理 i/c/q 与 table 的关系(不同 template table 取 1 或 2 个坐标), 再开发; 优先索引传递, 值传递先精确匹配; 意图形态=produce-action(extract_lib_timing.py+rev_cali.py 两脚本开发, 三维坐标->template table 匹配抽值); 可便携性=高(real autosim_script Python source 可 scp 便携, asset_fidelity=A-faithful); case 交付两脚本同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-action 是合法任务形态, trace 意图 'i/c/q 三维坐标传递+template table 匹配抽值' 与 case 交付 axis_for_var 映射+table 匹配同形映射, asset A-faithful 因 Python source 便携); check.py 15 断言验 zip 含 extract_lib_timing.py+rev_cali.py 两文件 + axis_for_var('related_pin_transition')->c + axis_for_var('input_net_transition')->i + axis_for_var('total_output_net_capacitance')->q + cross-input guard(A≠B table 不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L1, k_check=15==k_rationale=15 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer=L1 正确(check 仅 subprocess 跑候选 python 解析+匹配文本 0 EDA 二进制), level 缺标应 L1, k_check=15 已标 ✓, shard 缺标应 B, **mc=7 在 mc>=10 阈值边界以下 host-verify 待 @A 复核**(可能应为 parked 或下线, 但 reframe_note backfill scope 限定不动 status)。",

    "EDA-Eval-DesignFlow-RonMonoDiag-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r834 reframe_note backfill batch9): 用户 clarawu@hfeg0pkn004 (sess 1793338010547_r06g9, mc=461, spice_sim 域) 在 CXMT ddgoa_cmos_stdcells RON characterization 流程中用 FineSim 对 zq-decoder RON 曲线做 5-corner ALTER 仿真(v5_all/v5.md0..v5#4.md0, temper 25/-40/110/-40/110C, alter#1..5, zqdec 0..63 sweep), 用 .measure rpd_50 取每个 zqcode 的 pulldown on-resistance; 用户首要意图: 检查 rpd_50 随 zqcode 变化的单调性, 若不单调就优化电路; 意图形态=produce-action(analyze_ron.py 5 corner .md0 parse+单调性检查+非单调过渡点定位+report); 可便携性=高(real FineSim 5 corner .md0 是小文本测量输出可 scp 便携, asset_fidelity=A-faithful, 非 FSDB 二进制); case 交付 analyze_ron.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-action 是合法任务形态, trace 意图 '检查 rpd_50 随 zqcode 单调性' 与 case 交付 5 corner 单调性诊断同形映射, asset A-faithful 因 .md0 小文本 scp 便携, 与 RonCurveSmoothness-001/RonCurveEvaluator-001 的 real .md0 不可便携判 synth_* 形成对比——本 case 的 .md0 是 5 corner 小文件 scp 可行, 而 RonCurveSmoothness/RonCurveEvaluator 涉及完整 DDR4 netlist+.md0 不可整体便携); check.py 14 断言验 zip 含 analyze_ron.py 且 py_compile + B 运行 exit0 且 out_B.json 合法 JSON + 5 corners 全覆盖 + B 全部非单调 + B 非单调过渡点匹配 GT_B(7->8,23->24,39->40,55->56) + direction==decreasing + cross-input guard(A≠B .md0 不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L2, k_check=14==k_rationale=14 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 subprocess 跑候选 python 解析 .md0 文本 0 EDA 二进制应 L1), level 缺标应 L2 或 L1, k_check=14 已标 ✓, track 缺标应 faithful, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-RsCalcAutoVia-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r834 reframe_note backfill batch9): 用户 e0014566@hfeg0plg58 (sess 1785810906841_m2vah, mc=975, characterization 域) 在 /home/e0014566/test_layout_rscalc_flow_3 下用两个 CXMT Virtuoso SKILL skill 包做版图电阻降低流: virtuoso-rscalc-runner(RsCalc, 跑 CXMTutRscalc_run 经 bsub/LSF 算每个 check point 的 parasitic resistance, 输出 .rvn, 第 12 列为电阻值)与 virtuoso-autovia-runner(AutoVia, 插 via+Calibre DRC+写 merged layout); 用户意图: 分析 2 skill+梳理配置+形成共有 config+构建 rscalc->autovia 工作流->写 prompt_flow.md 复用; 意图形态=produce-action(gen_rscalc_agent.py+gen_autovia_agent.py+common.config+rscalc.config+run_autovia_config.il+prompt_flow.md 六交付件); 可便携性=高(real CXMT Virtuoso SKILL config/script 是文本可 scp 便携, asset_fidelity=A-faithful); case 交付六文件同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-action 是合法任务形态, trace 意图 'rscalc 算电阻->autovia 优化版图降电阻 工作流' 与 case 交付 rscalc+autovia agent+config+flow.md 同形映射, asset A-faithful 因 SKILL config 文本 scp 便携); check.py 14 断言验 zip 含 6 必交文件(gen_rscalc/gen_autovia/common.config/rscalc.config/run_autovia_config.il/prompt_flow.md) + gen_rscalc_agent.py py_compile + gen_autovia_agent.py py_compile + 在隐藏 B 上 exit0 + cross-input guard(A≠B config 不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L2(check 真跑 SKILL/Virtuoso 二进制), k_check=14==k_rationale=14 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer=L2 正确(若 check 真跑 SKILL/Virtuoso/bsub 二进制), level 缺标应 L2, k_rationale 缺标应 14, track=faithful 一致 asset=A-faithful ✓, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-RiseEdgeMarginMeas-001":
        "keep_faithful-restored-image 无 reframe (WAVEVIEW β7 restored-image, vision协作 designflow; 原意图需看 Synopsys WaveView3 波形截图, 旧规则降级为文本替身, r553 WAVEVIEW 协作恢复为 image 输入; §4 无需重构, r834 reframe_note backfill batch9): 用户 yunfat@hfeahpc505 (sess 1794460481537_xr6sg, mc=35, spice_sim 域) 对 cline 提需求 '测量 waveview3 中两个信号的上升沿 margin 标注出来'——在 Synopsys WaveView3 中测量两个信号(clk_a 与 data_a)上升沿之间的 margin(时间差)并标注; agent 经 search_apis 检索 sx_gmeas_delay(图形化 delay 测量带标注)/sx_meas_delay2/sx_gmeas_risefall/sx_set_threshold 等 Tcl API, 定位用 sx_gmeas_delay 在两条 line 的上升沿中点测 delay 并标注; 意图形态=produce-action(看波形截图+量上升沿中点+算 margin+生成标注 report); 可便携性=中(image 输入需 restored, asset_fidelity=synth_deck-restored-image, track=synthesized-image-restored); **WAVEVIEW 协作 restore**: 原意图需看图, 旧规则降级为文本替身(纯文字描述波形), r553 WAVEVIEW 协作(α4+β7=11 题)恢复为 image 输入(rise_margin_A.png 给 SUT, hidden B 给不同截图); reframe_note=None->补(faithful-restored-image, produce-action 是合法任务形态, trace 意图 '看 waveview3 波形测上升沿 margin' 与 case 交付 看图算 margin+JSON report 同形映射, asset=synth_deck-restored-image 因 image 是 restored 而非 trace 原生 scp 便携 asset; **区别纯 A-faithful**: 纯 A-faithful 的 asset 是 trace 原生 scp 便携, 本 case image 输入是 restored-from-text-substitute, 是 WAVEVIEW 协作的产物); check.py 12 断言验 zip 含 rise_margin_report.json + report 合法 JSON + JSON 含全部必需键(ref_signal/target_signal/ref_edge_time/target_edge_time/margin_ns/signals/annotation) + ref_signal==clk_a + cross-input guard(A≠B 截图不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input(不同截图)+ §4.2 subprocess 真跑保证, layer=L2, k_check=12==k_rationale=12 ✓, 无 reframe(restored-image 是 asset 还原非意图 reframe), 保留。**metadata bug 待 @A**: layer=L2 正确, level 缺标应 L2, k_check=12 已标 ✓, track=synthesized-image-restored 一致 asset=synth_deck-restored-image ✓, shard 缺标应 B。**注**: 本 case 是 batch9 唯一 WAVEVIEW restored-image keep_faithful, designflow 与 vision 协作的 β7 群成员, 11 题 restored-image 之一。**WAVEVIEW 边界**: 无多模态能力者 fail 是正确结果, 不许降级成文本替身(2026-11-14 用户令)。",
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
