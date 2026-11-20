#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r787 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r743_spotcheck22.tsv (batch21, 10 keep_reframe of 12 cases).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r786 档3 batch9-20 done (reframe_note 32->134).
本轮 r787 档3 batch21 (r743 spotcheck22, 10 cases 待 apply). reframe_note 134->144.

reframe_note text = spotcheck22 per_case_reasoning + cases/B trace_source(user@host) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False.

Driver 分类 (per per_case_reasoning, spotcheck22 10 keep_reframe):
  - Q&A/diag/explain->produce-tool explainer/诊断器 (Q&A-driver): 5 cases
    SimSetupExplainQA (t0002965@hfhds201, 问文件用途+找目录 -> 产 sim_setup_explainer.py+report) /
    MrSelfClearExpDiag (tongfanl@hfhds201, 问 MR7 OP2 后 exp 值 -> 产 diag.py+out.json) /
    SioutMemRootcauseDiag (kli@hfhds201, 问 si.out memory 爆炸根因 -> 产 siout_mem_diag.py+report) /
    TwoStageLogExplainQA (e0024852@hfeg0pkn005, 问两阶段日志各自内容 -> 产 two_stage_log_explainer.py+report.json) /
    NandfpMissingArgDiag (tongfanl@hfhds201, 问 NANDFP 报错原因 -> 产 diag.py+outB.json)
  - analysis/Q&A->produce-tool 分析器/诊断器+报告 (analysis-driver): 2 cases
    SrcPy3Analyze (yansonw@hfeg0pfn108, analysis coding in src_py3 -> 产 src_py3_analysis.json 结构化报告) /
    Mt0MetastabDiag (e0029495@hfeg0pkn002, 问 mt0 是否亚稳态 -> 产 metastab_diag.py+out.json)
  - produce-action file/dir->script harness (harness-driver): 3 cases
    SpTemplateOpt (reedchen@hfeg0pkn002, 给优化版 .sp -> 产 optimized.sp harness for hidden-B) /
    GmidLutRunSelect (t0002801@hfeg0plg49, 建立 gmid LUT+目录 -> 产 build_gmid_lut.py harness) /
    TrimSweepSpGen (joeyl@hfeg0pkn004, 创建 7 个 trim .sp -> 产 gen_trim_sps.py harness)

2 keep_faithful (Mt0TskewCalc 用户显式要"用脚本帮我处理" + HierarchyTrace 用户显式要"写一个python脚本") 零偏移, 不需 reframe_note.
spotcheck22 关键发现: 6 例 layer=None 误缺标应补 L1 (SimSetupExplainQA/SpTemplateOpt/SioutMemRootcauseDiag/GmidLutRunSelect/TwoStageLogExplainQA/Mt0MetastabDiag),
  - reframe_note backfill scope 限定不修 layer, 在 note 文本标注 layer bug 待 @A 档1 补 sweep.
其余 4 例 layer 已正确标 L1 (SrcPy3Analyze/MrSelfClearExpDiag/NandfpMissingArgDiag/TrimSweepSpGen).
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-SimSetupExplainQA-001":
        "LPDDR6 sim_setup 文件用途解释器->produce-tool (Q&A/explain->produce-tool explainer+report reframe, §4 有牙必要, r743 spotcheck batch21): 用户 t0002965@hfhds201 原话 U190「分析LPDDR6/DECQA/sim_setup下面的文件是干什么的？」+ U197「能不能找到finesim仿真相关的文件目录」(Q&A/explain 问文件用途+找目录, deepread 1791875313313_ztoza mc142, 214 msgs); A 不可行原因=纯 Q&A/explain(问文件用途+找目录)无 runnable artifact 无 check 牙 -> case 抽取「解析 sim_setup/ 产结构化 explainer+report」子技能, B 档 synthesized 合规, reframe 由 Q&A/explain→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (sim_setup/ 真实文件作可见 A, 待 @A apply 档2); trace 用户=Q&A/explain(问文件用途+找目录), case 收敛为 produce-tool(写 sim_setup_explainer.py 产 sim_setup_report.json 顶层 dict/9 必填键/sim_setup_files 列表/finesim_related_files) 给 check() 牙(§4.1 hidden-B cross-input guard B report, B 值与 A 反 + §4.9 反硬编); 重构为产 sim_setup_explainer.py+sim_setup_report.json; check.py 23 断言验 hidden-B cross-input guard+防硬编使纯 Q&A/explain 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 解析 sim_setup/ 文件, 不启动 FineSim), level 缺标应 L1, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-SrcPy3Analyze-001":
        "src_py3 15 模块结构化代码分析器->produce-tool (analysis->produce-tool structured report reframe, §4 有牙必要, r743 spotcheck batch21): 用户 yansonw@hfeg0pfn108 原话 U0「analysis coding in src_py3 folder」(analysis 代码分析, deepread 1791945162141_qo7xn mc35), 真实读取 15 个 .py 模块做结构化代码分析; A 不可行原因=纯 read-only analysis(代码分析)无 runnable artifact 无 check 牙 -> case 抽取「静态分析 15 模块产结构化分析报告 JSON」子技能, B 档 synthesized 合规, reframe 由 analysis→produce-tool 驱动非配额驱动; asset_fidelity ✓ 已标(A=trace-verbatim 15 .py 模块真实 scp 自 hfeg0pfn108 AutoModelSimulation/src_py3 + hidden B=synthesized 7 模块); layer=L1 ✓(已标, check 仅 subprocess 跑 python 静态分析, 不启动 EDA 工具); trace 用户=analysis(「analysis coding in src_py3」= 代码分析), case 收敛为 produce-tool(写 src_py3_analysis.py 产 src_py3_analysis.json 9 必填顶层键/包名/架构/数据流/优点/风险缺陷/改进建议) 给 check() 牙(§4.1 hidden-B cross-input guard A 15 模块 vs B 7 合成模块反硬编 + §4.9 反硬编); 重构为产 src_py3_analysis.py+src_py3_analysis.json; check.py 34 断言验 hidden-B cross-input guard+防硬编使纯 analysis(无 runnable artifact)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: k_check=34/k_rationale=34 ✓ 已标(本批唯一 k 字段完整 + 唯一 asset_fidelity 完整)。",
    "EDA-Eval-DesignFlow-SpTemplateOpt-001":
        "control_template.sp 模板优化器->produce-tool (harness produce-action file->script reframe, §4 有牙必要, r743 spotcheck batch21): 用户 reedchen@hfeg0pkn002 原话 U0「请你帮我分析一下这个/proj/ddgoa/V0/.../control_template.sp这个模板，看看有没有优化空间，如果有请你给一个优化的版本在你的工作目录下」(produce-action 分析+给优化版, deepread 1791945700744_chg46 mc134); A 不可行原因=produce-action 交付 .sp 文件(file-based)无法支撑 §4.1 hidden-B cross-input guard -> case 抽取「harness-wrap: script 产 optimized.sp 以支撑 B 不同规模/取值 cross-input guard」子技能, B 档 synthesized 合规, reframe 由 harness-driven 非配额驱动; asset_fidelity 缺标应 real-from-trace (control_template.sp 真实模板作可见 A, 待 @A apply 档2); trace 用户=produce-action(「给一个优化的版本」= 交付 .sp 文件), case 收敛为 produce-tool(写优化器脚本产 optimized.sp, GenSP 锚 .param/.lib/V 源 active 行保留 + .probe 收窄 + .option probe 补 + .end 补) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 optimized.sp 生成脚本; check.py 16 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(file-based)无法有牙 => 收敛为 produce-tool harness 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python regex 处理 .sp, 不启动 FineSim), level 缺标应 L1, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-MrSelfClearExpDiag-001":
        "DDR6 Load_Mode MR7 OP2 self-clear exp 静态诊断器->produce-tool (Q&A/diag->produce-tool 诊断器 reframe, §4 有牙必要, r743 spotcheck batch21): 用户 tongfanl@hfhds201 原话 U0「/proj/dscqa/V0/.../verilog.ddr6.dscqa.vecgen_local 帮我看下，在Load_Mode MR7 的 OP2后，一段时间后该位的exp值是什么值？」(Q&A/diag 问 exp 值未给根因/fix, deepread 1791961682094_f1cbt mc33); A 不可行原因=纯 Q&A/diag(问 exp 值)无 runnable artifact 无 check 牙 -> case 抽取「解析 SV 静态诊断 self-clear exp 产 out.json」子技能, B 档 synthesized 合规, reframe 由 Q&A/diag→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (A_specdef.sv/A_test.sv/A_timing_load.sv verbatim 作可见 A, 待 @A apply 档2); layer=L1 ✓(已标, check 仅 subprocess 跑 python 静态 SV 解析, 不启动 SPICE); trace 用户=Q&A/diag(「该位的exp值是什么值」= 问值), case 收敛为 produce-tool(写 diag.py 产 out.json self_clear_bits list 恰 1 条/mr_ma==MA_cal_rst 非 A 的 MA_zq_rst/mr_index==12 非 A 的 7) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 diag.py+out.json; check.py 18 断言验 hidden-B cross-input guard+防硬编使纯 Q&A/diag 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SioutMemRootcauseDiag-001":
        "FineSim si.out memory 爆炸根因诊断器->produce-tool (Q&A/debug-Q&A->produce-tool 诊断器+报告 reframe, §4 有牙必要, r743 spotcheck batch21): 用户 kli@hfhds201 原话 U0 对比两次 FineSim DRAM Fullchip 仿真 si.out 问「仿真时间为什么变长 + memory 为什么变大 + Total memory usage peak=38698.2 MB 与 Peak Virtual Memory=1383493.4 MB 的区别及为何 Peak 这么大 + 网表相同时 memory 爆炸的具体原因」(Q&A/debug-Q&A 问为什么+问区别+问根因, deepread 1792031875998_68gc9 mc40); A 不可行原因=纯 Q&A/debug-Q&A(问根因)无 runnable artifact 无 check 牙 -> case 抽取「解析两次 si.out 日志产结构化 memory 诊断报告」子技能, B 档 synthesized 合规, reframe 由 Q&A/debug-Q&A→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (两次 si.out 真实日志作可见 A, 待 @A apply 档2); trace 用户=Q&A/debug-Q&A(「为什么变大...具体原因」= 问根因), case 收敛为 produce-tool(写 siout_mem_diag.py 产 report corner=SS/ic_matches/elapsed/peak memory/peak virtual/根因) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编 + 3 次 rerun exit 0 确定性); 重构为产 siout_mem_diag.py+report; check.py 25 断言验 hidden-B cross-input guard+防硬编使纯 Q&A/debug-Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 解析 si.out log, 不启动 FineSim), level 缺标应 L1, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-GmidLutRunSelect-001":
        "PlatRun 结果选中+gmid LUT 构建器->produce-tool (harness produce-action file/dir->script reframe, §4 有牙必要, r743 spotcheck batch21): 用户 t0002801@hfeg0plg49 原话 U0「我重新跑了仿真，结果在/proj/ddaop/V0/.../Results/，帮我看看能否建立gmid查找表？如果可以，在这个路径下面创建/home/t0002801/gmid_LUT/」(produce-action 建立 LUT+创建目录, deepread 1792041709940_x5fd4 mc119), 4 个 PlatRun 1 成功 3 失败的选中逻辑; A 不可行原因=produce-action 交付 LUT 目录+文件(file/dir-based)无法支撑 §4.1 hidden-B cross-input guard -> case 抽取「harness-wrap: script 选中成功 PlatRun + 解析 dc.op OP 块 + 产 gmid_LUT/(json+csv+README)」子技能, B 档 synthesized 合规, reframe 由 harness-driven 非配额驱动; asset_fidelity 缺标应 real-from-trace (4 个 PlatRun 真实结果作可见 A, 待 @A apply 档2); trace 用户=produce-action(「建立gmid查找表...创建目录」= 交付 LUT), case 收敛为 produce-tool(写 build_gmid_lut.py 产 gmid_LUT/ 选中成功 PlatRun.7/解析 dc.op mosfetLevel77 OP 块/必需键 ids/gm/gmoverid/vth/vdsat/l_n) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 build_gmid_lut.py+gmid_LUT/; check.py 16 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(file/dir-based)无法有牙 => 收敛为 produce-tool harness 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 解析 PlatRun results, 不启动 HSPICE), level 缺标应 L1, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-TwoStageLogExplainQA-001":
        "two_stage_test.sh 两阶段日志解释器->produce-tool (Q&A/explain->produce-tool explainer+report reframe, §4 有牙必要, r743 spotcheck batch21): 用户 e0024852@hfeg0pkn005 原话 U0「you can see run_two_stage_test.sh when i run this commond i find the log has two ... explain ... what stage1.log and stage2.log each contain」(Q&A/explain 问两阶段日志各自内容, deepread 1792056845394_o8w1u mc18); A 不可行原因=纯 Q&A/explain(问日志内容)无 runnable artifact 无 check 牙 -> case 抽取「解析 shell 脚本+两阶段日志产结构化 explainer+report」子技能, B 档 synthesized 合规, reframe 由 Q&A/explain→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (run_two_stage_test.sh + stage1.log/stage2.log 真实作可见 A, 待 @A apply 档2); trace 用户=Q&A/explain(「explain what stage1.log and stage2.log each contain」= 问日志内容), case 收敛为 produce-tool(写 two_stage_log_explainer.py 产 two_stage_log_report.json 4 顶层键 overview/stages/config_variables/log_files/num_stages=2/flow_type/stage1=streaming conly DSPF-level/stage2=full process+XA detect+tailor parallel testbench-level) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 two_stage_log_explainer.py+two_stage_log_report.json; check.py 17 断言验 hidden-B cross-input guard+防硬编使纯 Q&A/explain 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 解析 shell+日志, 不启动 SPICE), level 缺标应 L1, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-NandfpMissingArgDiag-001":
        "DDR6 vecgen NANDFP 报错静态诊断器->produce-tool (Q&A/diag->produce-tool 诊断器 reframe, §4 有牙必要, r743 spotcheck batch21): 用户 tongfanl@hfhds201 原话 U0「抽激励报错，帮我看下啥原因。抽激励脚本：./runsti/gen_stimulus_Aging 报错信息：[COMMAND] ... 23 xmvlog *E,NANDFP errors on Poststress002/003/005 .v files」(Q&A/diag 问报错原因未给根因/fix, deepread 1792201884887_c39j4 mc67); A 不可行原因=纯 Q&A/diag(问报错原因)无 runnable artifact 无 check 牙 -> case 抽取「解析 SV 静态诊断 NANDFP 形参缺失产 outB.json」子技能, B 档 synthesized 合规, reframe 由 Q&A/diag→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (.v 文件 + 报错日志 verbatim 作可见 A, 待 @A apply 档2); layer=L1 ✓(已标, check 仅 subprocess 跑 python 静态 SV 解析, 不启动 SPICE); trace 用户=Q&A/diag(「帮我看下啥原因」= 问报错原因), case 收敛为 produce-tool(写 diag.py 产 outB.json NANDFP 错误解析==15 条/Load_Cfg 形参==10 个无 dqs_sel/Read_Cfg 形参含 dqs_sel) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 diag.py+outB.json; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 Q&A/diag 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-TrimSweepSpGen-001":
        "skew_trim_range 7 个 trim .sp deck 生成器->produce-tool (harness produce-action file->script reframe, §4 有牙必要, r743 spotcheck batch21): 用户 joeyl@hfeg0pkn004 原话 U0「在这个目录中，/proj/drgqa/V0/.../008_FullPath_skew_trim_range 目前只有0_000.sp，我需要你创建到7_111,文件更改对应这里：000时，V_Div_4p_trim_F0<0> ... '0*pvddq' ...」(produce-action 创建 7 个 .sp deck, deepread 1792389569188_qry8l mc34, 3 位二进制 N 映射规则); A 不可行原因=produce-action 交付 7 个 .sp 文件(file-based)无法支撑 §4.1 hidden-B cross-input guard -> case 抽取「harness-wrap: script 按 N_BBB 二进制映射产 7 个 trim .sp」子技能, B 档 synthesized 合规, reframe 由 harness-driven 非配额驱动; asset_fidelity 缺标应 real-from-trace (0_000.sp 真实模板作可见 A, 待 @A apply 档2); layer=L1 ✓(已标, check 仅 subprocess 跑 python regex 处理 .sp, 不启动 FineSim); trace 用户=produce-action(「创建到7_111」= 交付 7 个 .sp), case 收敛为 produce-tool(写 gen_trim_sps.py 产 7 个 N_BBB.sp 文件名集合正确/trim 值=<bit_i>*pvddq 按 N 映射/各文件除 trim 值域外与模板逐字节一致/B2 trim 源序倒置+decoy) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 gen_trim_sps.py+7 个 .sp; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(file-based)无法有牙 => 收敛为 produce-tool harness 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-Mt0MetastabDiag-001":
        "HSPICE .mt0 亚稳态检测诊断器->produce-tool (analysis/Q&A->produce-tool 诊断器+out.json reframe, §4 有牙必要, r743 spotcheck batch21): 用户 e0029495@hfeg0pkn002 原话 U0「分析这份mt0文件，看看是否发生亚稳态」(analysis/Q&A 问是否亚稳态, deepread 1792399658249_w4b6q mc66), 真实附件 mt0 140KB/66 $DATA1 块, 63/66 含 failed, tcq 27/q50 29 失败 → 亚稳态; A 不可行原因=纯 analysis/Q&A(问是否亚稳态)无 runnable artifact 无 check 牙 -> case 抽取「解析 .mt0 多 $DATA1 块检测亚稳态产 out.json」子技能, B 档 synthesized 合规, reframe 由 analysis/Q&A→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (mt0_A/mt0.mt0 真实 140KB 作可见 A, 待 @A apply 档2); trace 用户=analysis/Q&A(「看看是否发生亚稳态」= 问是否), case 收敛为 produce-tool(写 metastab_diag.py 产 out.json 8 键/n_blocks/blocks_with_failures/blocks_clean/total_failures/tcq_failures/q50_failures/metastability_detected=True) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 metastab_diag.py+out.json; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 analysis/Q&A(无 runnable artifact)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 解析 .mt0, 不启动 HSPICE), level 缺标应 L1, metadata bug 待 @A apply 档1 补 sweep。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-SimSetupExplainQA-001": "Q&A/explain->produce-tool explainer+report",
    "EDA-Eval-DesignFlow-SrcPy3Analyze-001": "analysis->produce-tool structured report",
    "EDA-Eval-DesignFlow-SpTemplateOpt-001": "harness produce-action file->script",
    "EDA-Eval-DesignFlow-MrSelfClearExpDiag-001": "Q&A/diag->produce-tool 诊断器",
    "EDA-Eval-DesignFlow-SioutMemRootcauseDiag-001": "Q&A/debug-Q&A->produce-tool 诊断器+报告",
    "EDA-Eval-DesignFlow-GmidLutRunSelect-001": "harness produce-action file/dir->script",
    "EDA-Eval-DesignFlow-TwoStageLogExplainQA-001": "Q&A/explain->produce-tool explainer+report",
    "EDA-Eval-DesignFlow-NandfpMissingArgDiag-001": "Q&A/diag->produce-tool 诊断器",
    "EDA-Eval-DesignFlow-TrimSweepSpGen-001": "harness produce-action file->script",
    "EDA-Eval-DesignFlow-Mt0MetastabDiag-001": "analysis/Q&A->produce-tool 诊断器+out.json",
}


def apply_one(case_id, note):
    path = os.path.join(CASES_DIR, case_id + ".json")
    if not os.path.exists(path):
        return ("MISSING", path)
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    d = json.loads(raw)
    m = d.get("metadata", {})
    if "reframe_note" in m:
        return ("ALREADY", case_id)
    m["reframe_note"] = note
    d["metadata"] = m
    out = json.dumps(d, ensure_ascii=False, indent=2)
    json.loads(out)  # verify parseable
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    return ("OK", case_id)


def main():
    print(f"=== r787 batch21 reframe_note apply: {len(REFRAME_NOTES)} cases (target) ===")
    counts = {"OK": 0, "ALREADY": 0, "MISSING": 0}
    for cid, note in REFRAME_NOTES.items():
        status, info = apply_one(cid, note)
        counts[status] = counts.get(status, 0) + 1
        print(f"  [{status}] {info} (driver={DRIVER.get(cid,'?')})")
    print(f"\nSummary: OK={counts['OK']} ALREADY={counts['ALREADY']} MISSING={counts['MISSING']}")
    print(f"Expected reframe_note count after apply: 134 + {counts['OK']} = {134 + counts['OK']}")


if __name__ == "__main__":
    main()
