#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r788 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r744_spotcheck23.tsv (batch22, 11 keep_reframe of 12 cases).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r787 档3 batch9-21 done (reframe_note 32->144).
本轮 r788 档3 batch22 (r744 spotcheck23, 11 cases 待 apply). reframe_note 144->155.

reframe_note text = spotcheck23 per_case_reasoning + cases/B trace_source(user@host) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False.

Driver 分类 (per per_case_reasoning, spotcheck23 11 keep_reframe):
  - produce-action file/list->script harness (harness-driver): 1 case
    LatchSubcktLocate (zxtu@hfeg0pkn001, 用户要"找出"latch subckt 列表 -> 产 find_latch_subckt.py harness for hidden-B)
  - Q&A/analysis/explain/diag/how-to/what-is->produce-tool (Q&A-driver): 10 cases
    RunCodeGuardConfigExplain (e0042624@hfeg0pkn005, 4 轮问 config/演示/raw/audit -> 产 runcode_guard_explain.py+JSON) /
    SshHostAlgDiag (steveny@hfeg0pnd001, 问 ssh no hostkey alg 报错原因+修法 -> 产 ssh_hostalg_diag.py+report) /
    OdtCtrlLogicAnalyze (clarawu@hfeg0pkn003, 分析 netlist ODT 控制逻辑 -> 产 odt_ctrl_analyze.py+JSON) /
    FinesimForceNodeAdvise (zqzhan@hfeg0plg58, 问 force 节点怎么加 -> 产 finesim_force_advise.py+JSON) /
    CircuitIdentPromptGuide (e0022089@hfeg0pkn002, 问识别电路的提示词怎么写 -> 产 circuit_prompt_guide_gen.py+JSON) /
    IddStimHowtoGuide (thqu@hfeahpc501, 问 IDD 仿真激励怎么写 -> 产 idd_stim_guide.py+report) /
    VtscMcDeckExplain (junweix@hfeg0pkn002, 讲解 HSPICE MC 瞬态网表 -> 产 vtsc_mc_deck_explain.py+JSON) /
    TermInvestigationReport (jiashengz@hfeg0plg92, 问 anasimpro GUI 术语含义 -> 产 term_investigation_report.py+JSON) /
    MBistTopAnalyze (t0002805@hfeg0pgn145, 从上往下分析 MBIST 顶层网表 -> 产 mbist_top_analyze.py+JSON) /
    NonOverlapClockDiag (zhililu@hfeg0pkn001, 分析不交叠时钟电路+问怎么改 -> 产 diag 脚本+out.json)

1 keep_faithful (ShmooCfgParser 用户 U#185 显式要"使其能够输入shmoocfg文件"= 改脚本吃 cfg, produce-native 交付同形 parse_shmoo_cfg 函数) 零偏移, 不需 reframe_note.
spotcheck23 关键发现: 5 例 layer=None 误缺标应补 L1 (LatchSubcktLocate/SshHostAlgDiag/OdtCtrlLogicAnalyze/IddStimHowtoGuide/NonOverlapClockDiag, 全 check 仅 subprocess 跑候选 python 解析 netlist/cfg/.sp/.mt0/log/shell, 0 例启动 EDA 二进制),
  - reframe_note backfill scope 限定不修 layer, 在 note 文本标注 layer bug 待 @A 档1 补 sweep.
其余 6 例 layer 已正确标 L1 (RunCodeGuardConfigExplain/FinesimForceNodeAdvise/CircuitIdentPromptGuide/VtscMcDeckExplain/TermInvestigationReport/MBistTopAnalyze).
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-LatchSubcktLocate-001":
        "LPDDR6 118MB 网表 latch subckt 定位器->produce-tool (harness produce-action list->script reframe, §4 有牙必要, r744 spotcheck batch22): 用户 zxtu@hfeg0pkn001 原话 U#2「找出这份网表文件中的latch subckt：.../netlist.presim」(produce-action locate/find, 118MB 网表, deepread 1791969171304_w3eav mc37); A 不可行原因=produce-action 交付 latch subckt 列表(list-based)无法支撑 §4.1 hidden-B cross-input guard -> case 抽取「harness-wrap: script regex 扫描 ^\\s*\\.subckt\\s+(\\S+) + name 含 latch 产 52 latch subckt 列表」子技能, B 档 synthesized 合规, reframe 由 harness-driven 非配额驱动; asset_fidelity 缺标应 real-from-trace (netlist.presim 真实 118MB 作可见 A, 待 @A apply 档2); trace 用户=produce-action(「找出」= 要结果列表), case 收敛为 produce-tool(写 find_latch_subckt.py 产 out.json JSON 数组/每元素 line+name/name 含 latch 无假阳/条数==B 真值 9/跨输入 A vs B 反硬编/确定性) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 find_latch_subckt.py+out.json; check.py 15 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(list-based)无法有牙 => 收敛为 produce-tool harness 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python regex 解析网表, 不启动 FineSim), level 缺标应 L1, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-RunCodeGuardConfigExplain-001":
        "runCodeGuard 配置/演示/raw/audit log 解释器->produce-tool (Q&A/explain->produce-tool explainer+JSON reframe, §4 有牙必要, r744 spotcheck batch22): 用户 e0042624@hfeg0pkn005 原话连问 4 轮「show me runcodeGuard config」+「yes」+「show me raw runCodeGuard」+「show me audit log」(explain-Q&A 4 轮, deepread 1792541695111_m40h5 mc19); A 不可行原因=纯 Q&A/explain(问 config/演示/raw/audit log)无 runnable artifact 无 check 牙 -> case 抽取「解析 agent-policy.json + 审计日志产结构化 explainer+JSON」子技能, B 档 synthesized 合规, reframe 由 Q&A/explain→produce-tool 驱动非配额驱动; asset_fidelity ✓ 已标(B-synthesized-from-trace, 7 destructive + 1 suspicious + 3 测试脚本 + 15 审计事件); layer=L1 ✓(已标, check 仅 subprocess 跑 python 解析 agent-policy.json, 不启动 EDA 工具); trace 用户=Q&A/explain(4 轮问 config/演示/raw/audit log), case 收敛为 produce-tool(写 runcode_guard_explain.py 产 JSON 12 必填顶层键/analysis_type/cross-input guard/确定性) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 runcode_guard_explain.py+JSON; check.py 18 断言验 hidden-B cross-input guard+防硬编使纯 Q&A/explain 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SshHostAlgDiag-001":
        "ssh no hostkey alg 报错静态诊断器+报告->produce-tool (Q&A/diag->produce-tool diag+report reframe, §4 有牙必要, r744 spotcheck batch22): 用户 steveny@hfeg0pnd001 原话 U0「我想要跳转到10.129.6.205」+ 后续报错「no hostkey alg」(Q&A/diag 问为何 ssh 失败 + 间接求修法, deepread 1792550155026_cn4bl mc21); A 不可行原因=纯 Q&A/diag(问报错原因+求修法)无 runnable artifact 无 check 牙 -> case 抽取「解析 ssh 版本/算法静态诊断产 report」子技能, B 档 synthesized 合规, reframe 由 Q&A/diag→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (host_inventory/ssh_config/版本信息 真实诊断产出作可见 A, 待 @A apply 档2); trace 用户=Q&A/diag(「no hostkey alg」= 问报错原因+求修法), case 收敛为 produce-tool(写 ssh_hostalg_diag.py 产 report 17 顶层键/target_host/source_host/openssh 版本代差/共同算法集/根因/建议方案/跨输入 A vs B 反硬编/确定性) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 ssh_hostalg_diag.py+report; check.py 22 断言验 hidden-B cross-input guard+防硬编使纯 Q&A/diag 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 解析 ssh 版本/算法, 不启动 EDA 工具), level 缺标应 L1, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-OdtCtrlLogicAnalyze-001":
        "netlist ODT 控制逻辑分析器->produce-tool (analysis/Q&A->produce-tool analyze+JSON reframe, §4 有牙必要, r744 spotcheck batch22): 用户 clarawu@hfeg0pkn003 原话 U0「学习一下 @/proj/m2701/.../netlist，告诉我这里面 ODT 相关的控制逻辑」(analysis-Q&A 分析 ODT 控制逻辑, deepread 1792563327292_besij mc25, 2276 行 netlist); A 不可行原因=纯 analysis/Q&A(分析 ODT 控制逻辑)无 runnable artifact 无 check 牙 -> case 抽取「静态分析 netlist 枚举 .subckt + 按栈算归属产结构化 JSON」子技能, B 档 synthesized 合规, reframe 由 analysis/Q&A→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (DqOutTopM6 netlist 真实 2276 行作可见 A, 待 @A apply 档2); trace 用户=analysis/Q&A(「分析 ODT 控制逻辑」= 电路分析), case 收敛为 produce-tool(写 odt_ctrl_analyze.py 产 JSON 17 顶层键/top_cell/total_lines/subckt_count/all_subckt_names/odt_ctrl_subckts/跨输入 A vs B 反硬编/确定性, 定位 12 个 ODT 端接腿 + 3 挡使能布尔式) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 odt_ctrl_analyze.py+JSON; check.py 21 断言验 hidden-B cross-input guard+防硬编使纯 analysis/Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 解析 netlist, 不启动 HSPICE), level 缺标应 L1, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-FinesimForceNodeAdvise-001":
        "FineSim fullchip force 节点添加建议器->produce-tool (how-to-Q&A->produce-tool advise+JSON reframe, §4 有牙必要, r744 spotcheck batch22): 用户 zqzhan@hfeg0plg58 原话 U0「这个是 fullchip 仿真文件 si.inp，我现在想要对电路里某个节点进行 force，应该怎么加进去，节点是这个 XI_Array6G_T_0...cm0_ts_RedRowDis_B0i，force 为 0 就行，也就是 pvss」(how-to-Q&A 问 force 语句怎么写+放哪, deepread 1792567034258_hasla mc28); A 不可行原因=纯 how-to-Q&A(问怎么加 force)无 runnable artifact 无 check 牙 -> case 抽取「解析 .sp deck + 惯例文件产结构化 advise+JSON」子技能, B 档 synthesized 合规, reframe 由 how-to-Q&A→produce-tool 驱动非配额驱动; asset_fidelity ✓ 已标(A=trace-verbatim deck.sp+ts_code_force.sp+output_force.sp + hidden B=synthesized drcpb/V2 FF X16); layer=L1 ✓(已标, check 仅 subprocess 跑 python 处理 .sp, 不启动 FineSim); trace 用户=how-to-Q&A(「应该怎么加进去」= 问怎么写), case 收敛为 produce-tool(写 finesim_force_advise.py 产 JSON 10 必填顶层键/project_overview 5 cross-input/parsed_convention_files ts+op v/pwl line count/recommended_force force_type+node+value/statement 含 node+value+pwl/static-no-pwl/src-starts-V/src-unique/static+pwl convention detected) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 finesim_force_advise.py+JSON; check.py 43 断言验 hidden-B cross-input guard+防硬编使纯 how-to-Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: rationale header 文本「49 条断言」与实际 circled 计数 43 不符(用 ㉠-㉧ circled-Hangul 续 36-43), k_check 字段=43==circled 43 ✓ 硬闸门满足, header 文本「49」应改「43」, doc-text bug 非 field-missing, 待 @A apply 修。",
    "EDA-Eval-DesignFlow-CircuitIdentPromptGuide-001":
        "电路识别提示词指南生成器->produce-tool (how-to-Q&A->produce-tool guide+JSON reframe, §4 有牙必要, r744 spotcheck batch22): 用户 e0022089@hfeg0pkn002 原话 U0「请问需要你识别某个路径下的电路，需要如何输入提示词」(how-to-Q&A 问 prompt 写法, deepread 1792572197494_0rj7b mc18); A 不可行原因=纯 how-to-Q&A(问 prompt 写法)无 runnable artifact 无 check 牙 -> case 抽取「RAG API 检索 + 产四要素+五场景模板指南」子技能, B 档 synthesized 合规, reframe 由 how-to-Q&A→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (真实 RAG API 检索结果 + 真实可读根/配置作可见 A, 待 @A apply 档2); layer=L1 ✓(已标, check 仅 subprocess 跑 python 产 guide JSON, 不启动 EDA 工具); trace 用户=how-to-Q&A(「需要如何输入提示词」= 问 prompt 写法), case 收敛为 produce-tool(写 circuit_prompt_guide_gen.py 产 JSON 12 顶层键/readable_root cross-input/env_user cross-input/env_host cross-input/四要素/五场景模板/跨输入 A vs B 反硬编/确定性) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 circuit_prompt_guide_gen.py+JSON; check.py 16 断言验 hidden-B cross-input guard+防硬编使纯 how-to-Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-IddStimHowtoGuide-001":
        "IDD 仿真激励编写指南器->produce-tool (how-to-Q&A->produce-tool guide+report reframe, §4 有牙必要, r744 spotcheck batch22): 用户 thqu@hfeahpc501 原话 U0「IDD仿真的激励要怎么写啊」(how-to-Q&A 问 IDD stimulus 怎么写, deepread 1792649502711_qrr6j mc37); A 不可行原因=纯 how-to-Q&A(问 IDD 激励怎么写)无 runnable artifact 无 check 牙 -> case 抽取「解析 stimulus.sp + power table 产 IDD 定义/激励三要素/PWL 两写法/JEDEC 测试项/testbench 模板/WaveView→PWL 工作流指南」子技能, B 档 synthesized 合规, reframe 由 how-to-Q&A→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (stimulus.sp/gen_stimulus_v2.py/analyze_power.py/TECHLIB_ALL_power_voltage_table.md 真实作可见 A, 待 @A apply 档2); trace 用户=how-to-Q&A(「IDD仿真的激励要怎么写」= 问怎么写), case 收敛为 produce-tool(写 idd_stim_guide.py 产 report 14 顶层键/idd_definition 提 idd+current+ma+dram/stimulus_components 3 子键/pwl_writing_styles>=2/jedec_idd_items>=7 覆盖 11 项/testbench_template 含 .tran+.meas+Vxxx/waveview_workflow 4 gen_*/pwl_simplification 阈值/measurement_methods>=4 含 AVG/MAX/FIND/RMS/project_power_domains>=3/voltage_table_ref>=5/caveats>=2) 给 check() 牙(§4.1 hidden-B cross-input guard A real-run+valid+project==drcpa + B-grounded + §4.9 反硬编 + 3 次 rerun 确定性); 重构为产 idd_stim_guide.py+report; check.py 55 断言验 hidden-B cross-input guard+防硬编使纯 how-to-Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 解析 stimulus.sp + 产 guide JSON, 不启动 HSPICE), level 缺标应 L1, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-VtscMcDeckExplain-001":
        "HSPICE MC 瞬态网表讲解解释器->produce-tool (explain-Q&A->produce-tool explainer+JSON reframe, §4 有牙必要, r744 spotcheck batch22): 用户 junweix@hfeg0pkn002 原话 U0 给路径无附加上下文, 意图=读文件讲解(explain-Q&A 讲解 HSPICE MC 瞬态网表在做什么, deepread 1792732271802_olayh mc17); A 不可行原因=纯 explain-Q&A(讲解仿真 deck)无 runnable artifact 无 check 牙 -> case 抽取「解析 .sp 网表逐段产结构化 explainer+JSON」子技能, B 档 synthesized 合规, reframe 由 explain-Q&A→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (mc_iload.sp 真实 HSPICE MC 瞬态网表作可见 A, 待 @A apply 档2); layer=L1 ✓(已标, check 仅 subprocess 跑 python 解析 .sp, 不启动 HSPICE); trace 用户=explain-Q&A(讲解 deck), case 收敛为 produce-tool(写 vtsc_mc_deck_explain.py 产 JSON 14 顶层键/file_overview top_function cross-input/电源域/参数/激励/分析语句/.meas/.dcmatch/跨输入 A vs B 反硬编/确定性, 讲解=什么仿真/电源域/参数/激励/测了什么/分析语句/控制负载短接信号/仿真意图) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 vtsc_mc_deck_explain.py+JSON; check.py 25 断言验 hidden-B cross-input guard+防硬编使纯 explain-Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-TermInvestigationReport-001":
        "术语调研报告生成器->produce-tool (what-is-Q&A->produce-tool investigation+JSON reframe, §4 有牙必要, r744 spotcheck batch22): 用户 jiashengz@hfeg0plg92 原话 U0「anasimpro GUI means what」(what-is Q&A 问术语含义, deepread 1792744686252_m8y0q mc17); A 不可行原因=纯 what-is-Q&A(术语咨询)无 runnable artifact 无 check 牙 -> case 抽取「环境探 + 知识库检索 + 词素拆解产结构化调研报告」子技能, B 档 synthesized 合规, reframe 由 what-is-Q&A→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (真实调研输入 + 真实环境/策略作可见 A, 待 @A apply 档2); layer=L1 ✓(已标, check 仅 subprocess 跑 python 产 report, 不启动 EDA 工具); trace 用户=what-is-Q&A(「anasimpro GUI means what」= 问术语含义), case 收敛为 produce-tool(写 term_investigation_report.py 产 JSON 14 顶层键 term/user/host/env_summary/search_methodology/local_hits/kb_results/term_hypothesis/词素拆解/best_hypothesis/confidence, best hypothesis=Analog Simulation Professional confidence=low) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 term_investigation_report.py+JSON; check.py 17 断言验 hidden-B cross-input guard+防硬编使纯 what-is-Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-MBistTopAnalyze-001":
        "MBIST 顶层网表分层分析器->produce-tool (analysis/Q&A->produce-tool analyze+JSON reframe, §4 有牙必要, r744 spotcheck batch22): 用户 t0002805@hfeg0pgn145 原话 U0「你可以帮我分析电路吗」+「这个电路图在 /proj/ddgoa/V0/libs/ddgoa_cmos_digital/mBistPat 下」+「你从上往下帮我详细的说一下」(analysis-Q&A 从上往下分析 MBIST 顶层网表, deepread 1793017339067_jhdvn mc24); A 不可行原因=纯 analysis/Q&A(电路/网表分析报告)无 runnable artifact 无 check 牙 -> case 抽取「分层 netlist 静态分析定位 5 子模块 + 地址计数器 + 6 计数时钟产结构化 JSON」子技能, B 档 synthesized 合规, reframe 由 analysis/Q&A→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (mBistPat/mBistTop 真实分层网表作可见 A, 待 @A apply 档2); layer=L1 ✓(已标, check 仅 subprocess 跑 python 解析 netlist, 不启动 SPICE); trace 用户=analysis/Q&A(「从上往下帮我详细的说一下」= 电路分析), case 收敛为 produce-tool(写 mbist_top_analyze.py 产 JSON 顶层必需键/top_cell==MbistTopInt cross-input/submodule_count/各子模块职责/命令状态机输出计数时钟/RA-CA 复位/写图案数据产生器/读回比对电路/跨输入 A vs B 反硬编/确定性) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 mbist_top_analyze.py+JSON; check.py 22 断言验 hidden-B cross-input guard+防硬编使纯 analysis/Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-NonOverlapClockDiag-001":
        "两相不交叠时钟电路诊断器->produce-tool (analysis/Q&A->produce-tool diag+out.json reframe, §4 有牙必要, r744 spotcheck batch22): 用户 zhililu@hfeg0pkn001 原话 U0「这是一个生成两组两相不交叠时钟的电路，CK1_CH和CK2_CH，CK1_NF和CK2_NF这两组的问题就是不交叠的时间太短，只有8ps，我打算做到100ps左右，帮我分析一下电路，该怎么改」(analysis-Q&A 分析电路+求改法, deepread 1793078120457_omrsw mc19); A 不可行原因=纯 analysis/Q&A(分析电路+问怎么改)无 runnable artifact 无 check 牙 -> case 抽取「解析 spectre 网表静态分析拓扑/根因=反馈支路无显式延迟/改法=4 条反馈支路插延迟缓冲产 out.json」子技能, B 档 synthesized 合规, reframe 由 analysis/Q&A→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (nonoverlap_clk_A.sp 真实 spectre 网表 VS_CH_CK_sim 作可见 A, 待 @A apply 档2); trace 用户=analysis/Q&A(「分析电路，该怎么改」= 分析+求改法), case 收敛为 produce-tool(写 diag 脚本产 out.json 8 必需键/时钟组数/反馈网/根因/修复点数/延迟预算/跨输入 A vs B 反硬编/确定性, 含真实 8ps→100ps 指标) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 diag 脚本+out.json; check.py 17 断言验 hidden-B cross-input guard+防硬编使纯 analysis/Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 解析 spectre 网表, 不启动 SPICE), level=L1 ✓ 已标, metadata bug 待 @A apply 档1 补 sweep。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-LatchSubcktLocate-001": "harness produce-action list->script",
    "EDA-Eval-DesignFlow-RunCodeGuardConfigExplain-001": "Q&A/explain->produce-tool explainer+JSON",
    "EDA-Eval-DesignFlow-SshHostAlgDiag-001": "Q&A/diag->produce-tool diag+report",
    "EDA-Eval-DesignFlow-OdtCtrlLogicAnalyze-001": "analysis/Q&A->produce-tool analyze+JSON",
    "EDA-Eval-DesignFlow-FinesimForceNodeAdvise-001": "how-to-Q&A->produce-tool advise+JSON",
    "EDA-Eval-DesignFlow-CircuitIdentPromptGuide-001": "how-to-Q&A->produce-tool guide+JSON",
    "EDA-Eval-DesignFlow-IddStimHowtoGuide-001": "how-to-Q&A->produce-tool guide+report",
    "EDA-Eval-DesignFlow-VtscMcDeckExplain-001": "explain-Q&A->produce-tool explainer+JSON",
    "EDA-Eval-DesignFlow-TermInvestigationReport-001": "what-is-Q&A->produce-tool investigation+JSON",
    "EDA-Eval-DesignFlow-MBistTopAnalyze-001": "analysis/Q&A->produce-tool analyze+JSON",
    "EDA-Eval-DesignFlow-NonOverlapClockDiag-001": "analysis/Q&A->produce-tool diag+out.json",
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
    print(f"=== r788 batch22 reframe_note apply: {len(REFRAME_NOTES)} cases (target) ===")
    counts = {"OK": 0, "ALREADY": 0, "MISSING": 0}
    for cid, note in REFRAME_NOTES.items():
        status, info = apply_one(cid, note)
        counts[status] = counts.get(status, 0) + 1
        print(f"  [{status}] {info} (driver={DRIVER.get(cid,'?')})")
    print(f"\nSummary: OK={counts['OK']} ALREADY={counts['ALREADY']} MISSING={counts['MISSING']}")
    print(f"Expected reframe_note count after apply: 144 + {counts['OK']} = {144 + counts['OK']}")


if __name__ == "__main__":
    main()
