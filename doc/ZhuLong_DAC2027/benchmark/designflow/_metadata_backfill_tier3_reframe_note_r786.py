#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r786 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r742_spotcheck21.tsv (batch20, 9 keep_reframe of 12 cases).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r785 档3 batch9-19 done (reframe_note 32->125).
本轮 r786 档3 batch20 (r742 spotcheck21, 9 cases 待 apply). reframe_note 125->134.

reframe_note text = spotcheck21 per_case_reasoning + cases/B trace_source(user@host) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False.

Driver 分类 (per per_case_reasoning, spotcheck21 9 keep_reframe):
  - portability produce-action->produce-tool (portability-driver): 5 cases
    GmidSizingSearch (t0002801@hfeg0plg99, aether LUT 提取 foundry PDK 不可便携 -> 便携 LUT CSV) /
    Tr0JitterRemeas (joeyl@hfeg0pkn004, FineSim .tr0 + 私有 PDK .inc 不可便携 -> HSPICE synth_deck) /
    JitterTieRerun (joeyl@hfeg0plg53, 私有 PDK .inc tb 不可便携 -> synth HSPICE PWL tb) /
    McPvtVmEval (reedchen@hfeg0plg93, 私有 template.sp+netlist 不可便携 -> synth template deck 生成器) /
    WvFmFreqExtract (e0023936@hfeg0plg52, 真实 foundry 波形不可便携 -> synth WDF + ACE Tcl harness)
  - Q&A/diag->produce-tool 诊断器 (Q&A-driver): 2 cases
    VecgenProbeEmptyDiag (tongfanl@hfhds201, 粘贴 vsim 日志问诊断 -> 产结构化诊断脚本) /
    WtmDanglingElseMre0Diag (tongfanl@hfhds201, 问为什么 mre0 全 0 -> 产 dangling-else 诊断脚本)
  - analysis/Q&A->produce-tool 诊断器+报告 (analysis-driver): 2 cases
    McFailModeDiag (e0024852@hfeg0pkn004, read_files 诊断 MC run -> 产失败模式诊断器+报告) /
    PostsimPortAudit (rongtaoy@hfeg0pkn001, 真实 post-sim run 审计 不可便携 -> synth fixtures + 产 audit 脚本; 双驱动 portability+analysis)

3 keep_faithful (SimResultGrep/DetermSeedByName/LibCellListGen) 零偏移, 不需 reframe_note.
spotcheck21 关键发现: 2 例 layer=None 误缺标应补 (GmidSizingSearch 应 L1, JitterTieRerun 应 L2),
  - reframe_note backfill scope 限定不修 layer, 在 note 文本标注 layer bug 待 @A 档1 补 sweep.
其余 7 例 layer 已正确标 (VecgenProbeEmptyDiag/WtmDanglingElseMre0Diag/McFailModeDiag/McPvtVmEval=L1, Tr0JitterRemeas/WvFmFreqExtract/PostsimPortAudit=L2).
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-GmidSizingSearch-001":
        "gm/id 自动化 sizing 搜索器->produce-tool (portability produce-action->produce-tool sizing 搜索器 reframe, §4 有牙必要, r742 spotcheck batch20): 用户 t0002801@hfeg0plg99 原话「我想做一个自动化sizing电路的程序，需要用到gm/id方法。你可以读取PDF吗」(produce-action 写 sizing 搜索程序, deepread 1791420858846_g3ud6 mc172), trace agent 写 gmid_engine.py 工具构建 + aether NMOS/PMOS LUT 提取(foundry PDK 在 .75), trace 未给完整 sizing 闭环; A 不可行原因=aether foundry LUT 提取依赖 foundry PDK 不可便携 .75 -> case 抽取「便携 LUT CSV 输入 + spec JSON -> sizing 搜索选最优」子技能, B 档 synthesized 合规, reframe 由 portability 驱动非配额驱动; asset_fidelity=synth_deck ✓(已标); trace 用户=produce-action(「自动化sizing电路的程序...gm/id方法」= 写搜索程序), case 收敛为 produce-tool(写 gmid_sizing_search.py 解析 CSV/过滤可行解/选最优) 给 check() 牙(§4.1 hidden-B cross-input guard B LUT CSV + spec JSON 不同规模/取值 + sizing_report.json + candidates.csv, B 值与 A 反 + §4.9 反硬编); 重构为产 gmid_sizing_search.py+sizing_report.json+candidates.csv; check.py 15 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(aether foundry LUT 不可便携)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑候选 python 解析 LUT CSV, 不启动 SPICE/aether, 与 sizing 搜索同型), level 缺标应 L1, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-VecgenProbeEmptyDiag-001":
        "DDR6 vecgen probe-empty 诊断器->produce-tool (Q&A/diag->produce-tool 诊断器 reframe, §4 有牙必要, r742 spotcheck batch20): 用户 tongfanl@hfhds201 原话粘贴 ./runsti/gen_stimulus_ltf 三 vsim submission(TT/FF/SS) 终端输出 + d6vecgen 'width==X2P3 bank array must start with 2b16g' warning 问诊断(Q&A/diag 粘贴日志问根因, trace 1791457291368_k7hc6 mc76), 未给根因/修复; A 不可行原因=纯 Q&A/diag(粘贴日志问诊断)无 runnable artifact 无 check 牙 -> case 抽取「解析 vsim log 产结构化诊断报告」子技能, B 档 synthesized 合规, reframe 由 Q&A/diag→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (verbatim 终端日志作可见 A, 待 @A apply 档2); layer=L1 ✓(已标, check 仅 subprocess 跑候选 python 解析 vsim log, 不启动 EDA 工具); trace 用户=Q&A/diag(粘贴终端输出问诊断), case 收敛为 produce-tool(写 diag_vecgen_probe_empty.py 产 out.json) 给 check() 牙(§4.1 hidden-B cross-input guard B outB.json pass_count/error_count/corners/error_corner/root_cause/vsim_has_skip_empty_bug/bug_location, A 7 PASS vs B 5 PASS 反硬编 + §4.9 反硬编); 重构为产 diag_vecgen_probe_empty.py+out.json; check.py 16 断言验 hidden-B cross-input guard+防硬编使纯 Q&A/diag 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-Tr0JitterRemeas-001":
        "FineSim .tr0 波形逆向 jitter 重测器->produce-tool (portability produce-action->produce-tool .tr0 重测器 reframe, §4 有牙必要, r742 spotcheck batch20): 用户 joeyl@hfeg0pkn004 原话「3_RJ.sp+4phase8000.inc+tt25 结果已出，旧 4phase.inc 有问题致 csv 全 error，用新 measure 文件重算输出 csv」(produce-tool 逆向 .tr0 重测 jitter, deepread 1791772987381_dckp0 mc69), trace agent 跑 16 个 parse_rj*.py 逆向 612GB FineSim .tr0 二进制波形 + 私有 PDK .inc; A 不可行原因=FineSim .tr0 + 私有 PDK .inc 不可便携 .75 -> case 抽取「HSPICE level-1 真跑产 .tr0 + 逆向重测 jitter」子技能, B 档 synthesized 合规, reframe 由 portability 驱动非配额驱动; asset_fidelity=synth_deck ✓(已标); layer=L2 ✓(已标, check 真跑 HSPICE subprocess, hdr 14 conditions); trace 用户=produce-tool(「用新 measure 文件重算输出 csv」= 逆向重测), case 收敛为 produce-tool(写 tr0_jitter_remeas.py hspice 真跑 run.lis 'job concluded'/死时钟陷阱 no_edges/跨阈值 jitter 计算) 给 check() 牙(§4.1 hidden-B cross-input guard B remeasure_report.json + hspice 真跑 + 死时钟陷阱, B 值与 A 反 + §4.9 反硬编); 重构为产 tr0_jitter_remeas.py+HSPICE 真跑; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(FineSim .tr0+私有 PDK 不可便携)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-JitterTieRerun-001":
        "DQS jitter TIE 仿真 rerun 器->produce-tool (portability produce-action->produce-tool TIE rerun 器 reframe, §4 有牙必要, r742 spotcheck batch20): 用户 joeyl@hfeg0plg53 原话要求用新 4phase8000.inc (speed=2GHz) 重跑 DQS jitter TIE 仿真(produce-tool 改 .tran 窗口重跑 TIE, deepread 1791784036591_y9y0f mc34), 旧 4phase.inc (2.375GHz) 与 data rate 不匹配 -> TIE 线性漂移 -> rms_tie 全 fail, TB 1_tran.sp 含私有 PDK .inc; A 不可行原因=私有 PDK .inc tb 不可便携 .75 -> case 抽取「合成 HSPICE 可移植 4 路 PWL DQS buffer + 改 .tran 窗口重跑 TIE」子技能, B 档 synthesized 合规, reframe 由 portability 驱动非配额驱动; asset_fidelity=synth_deck ✓(已标); trace 用户=produce-tool(「用新 4phase8000.inc 重跑 DQS jitter TIE 仿真」= 改窗口重跑), case 收敛为 produce-tool(写 jitter_rerun.py 4 参签名/report.json 必需键/sim.ran==True/.lis 存在 HSPICE 真跑/selected_meas 4phase8000.inc/tran 延长 58n→63n/rms_tie PASS) 给 check() 牙(§4.1 hidden-B cross-input guard B sim.ran + .lis + selected_meas + tran 窗口 + rms_tie, B 值与 A 反 + §4.9 反硬编); 重构为产 jitter_rerun.py+HSPICE 真跑; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(私有 PDK 不可便携)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L2(check 真跑 HSPICE subprocess, hdr 14 conditions), level 缺标应 L2, k_check=14/k_rationale=14 ✓ 已标(本批唯一 k 字段完整), metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-WtmDanglingElseMre0Diag-001":
        "WTM mre0 expdata 全 0 dangling-else 诊断器->produce-tool (Q&A/diag->produce-tool 诊断器 reframe, §4 有牙必要, r742 spotcheck batch20): 用户 tongfanl@hfhds201 原话(msg#26)「帮我看下这个文件夹下抽出的激励，明明xun.log中gen_wtm_write_data中的dq0 UI1和UI2都有错，为啥mre0的expdata是全0？」(Q&A/diag 问为什么, deepread 1792993730194_cyua2 mc98, 80 msgs), gold-standard(msg#42)=dangling-else 死代码根因, 未给根因; A 不可行原因=纯 Q&A/diag(问为什么)无 runnable artifact 无 check 牙 -> case 抽取「解析 xun.log 检测 dangling-else 死代码产结构化诊断报告」子技能, B 档 synthesized 合规, reframe 由 Q&A/diag→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (verbatim 路径+问句作可见 A, 待 @A apply 档2); layer=L1 ✓(已标, check 仅 subprocess 跑候选 python 解析 xun.log, 不启动 SPICE); trace 用户=Q&A/diag(「为啥mre0的expdata是全0」= 问为什么), case 收敛为 produce-tool(写 diag_wtm_dangling_else.py 产 out.json is4phase/phase_mode/dangling_else_detected/dead_code_branch/error_ui_mask/root_cause) 给 check() 牙(§4.1 hidden-B cross-input guard B out.json, B 值与 A 反 + §4.9 反硬编); 重构为产 diag_wtm_dangling_else.py+out.json; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 Q&A/diag 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-McFailModeDiag-001":
        "Monte Carlo 失败模式 + 状态聚合一致性诊断器->produce-tool (analysis/Q&A->produce-tool 诊断器+报告 reframe, §4 有牙必要, r742 spotcheck batch20): 用户 e0024852@hfeg0pkn004 原话「see variation_designer_7, find data bug, and how to debug」「check testbench」「how to fix each bug」(analysis/Q&A read_files 诊断, deepread 1793065824220_rigwz mc72), trace agent 读 engine.log/summary.json/project_setup.xml 发现 Bug#1(所有 run Failed 但 yield +infinity, 状态/聚合不一致), 全程未真跑 FineSim; A 不可行原因=纯 read-only analysis(读文件诊断)无 runnable artifact 无 check 牙 -> case 抽取「MC/corner-sweep 失败模式诊断器 + 状态/聚合一致性审计器」子技能, B 档 synthesized 合规, reframe 由 analysis/Q&A→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 synth_deck (B 档 synthesized run fixtures, 待 @A apply 档2); layer=L1 ✓(已标, check 仅 subprocess 跑候选 python 解析日志, 不启动 FineSim); trace 用户=analysis/Q&A(「find data bug...check testbench...how to fix」= 读文件诊断), case 收敛为 produce-tool(写 mc_faildiag.py 产 mc_faildiag_report.json 10 条 run verdict 全匹配 GT/non_convergence 计数/measure_error/port_mismatch_abort/license_fail/timeout/env_error) 给 check() 牙(§4.1 hidden-B cross-input guard B report 10 verdict 全匹配 GT, B 值与 A 反 + §4.9 反硬编); 重构为产 mc_faildiag.py+mc_faildiag_report.json; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 analysis/Q&A(无 runnable artifact)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-McPvtVmEval-001":
        "PVT 蒙卡 Vm 评估 deck 生成器->produce-tool (portability produce-action->produce-tool deck 生成器 reframe, §4 有牙必要, r742 spotcheck batch20): 用户 reedchen@hfeg0plg93 原话「我现在希望你在这个目录下帮我跑多个 PVT 的蒙卡仿真，并且收集 Vm 数据评估达标成果，你可以参考 skill 来加快理解需求，输入件：template、vm_target.csv、netlist。先构建计划，和我确认后开始执行」(produce-action 写 deck 生成器 gen_sp_mc.py, deepread 1793082564833_dhqmb mc102), trace agent 写 gen_sp_mc.py(按 vm_target.csv 每个 corner 在 template.sp 正则替换 .temp/.param ptemp/pvcc + bsub 提交 LSF fqueue2h); A 不可行原因=私有 template.sp + netlist 在 .75 不可便携 -> case 抽取「synth template + 按 vm_target.csv 生成 mc_<tag>.sp deck」子技能, B 档 synthesized 合规, reframe 由 portability 驱动非配额驱动; asset_fidelity 缺标应 synth_deck (B 档 synthesized template, 待 @A apply 档2); layer=L1 ✓(已标, check 验 deck 生成, subprocess 跑 python 产 .sp, 未真跑 FineSim 蒙卡); trace 用户=produce-action(「跑多个 PVT 蒙卡...收集 Vm 数据评估达标」= 写 deck 生成器), case 收敛为 produce-tool(写 mc_pvt_vm_eval.py B1 产 4 个 mc_<tag>.sp/.tran 100p 6u sweep monte=300/.param mis_flag=1 sigmaflag=5.45/Vm 收集评估达标) 给 check() 牙(§4.1 hidden-B cross-input guard B 4 mc_<tag>.sp + .tran sweep + monte=300 + Vm 评估, B 值与 A 反 + §4.9 反硬编); 重构为产 mc_pvt_vm_eval.py+mc_<tag>.sp; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(私有 template 不可便携)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-WvFmFreqExtract-001":
        "WaveView ACE Tcl FM 信号瞬时频率提取器->produce-tool (portability produce-tool->produce-tool 波形便携化 reframe, §4 有牙必要, r742 spotcheck batch20): 用户 e0023936@hfeg0plg52 原话 trace 全程 sandbox run_code lang=tcl 真跑 WaveView ACE Tcl(produce-tool 写 ACE Tcl 频率提取脚本, deepread 1793095651315_qb1ua mc103), 定义 f_vs_t(sig,v_thr) -> RISE 扫描+阈值 -> 遍历上升沿 f=1/(t2-t1) -> sx_append_data -> sx_write_open 写 WDF; A 不可行原因=真实 foundry 波形文件不可便携 .75 -> case 抽取「synth WDF wave_A.dat FM 信号 + ACE Tcl 频率提取」子技能, B 档 synthesized 合规, reframe 由 portability 驱动非配额驱动; asset_fidelity 缺标应 synth_deck (B 档 synthesized WDF, 待 @A apply 档2); layer=L2 ✓(已标, check 真跑 WaveView wv -ace_no_gui subprocess, log 含 WaveView banner); trace 用户=produce-tool(写 ACE Tcl 频率提取脚本), case 收敛为 produce-tool(写 fm_freq_vs_t.tcl tcl 纯 ASCII/真跑 wv -ace_no_gui rc==0/WDF 可 sx_open_sim_file_read 回读 frequency 信号点/载波频率范围) 给 check() 牙(§4.1 hidden-B cross-input guard B wave_B.dat + 载波频率范围 + 频率点, B 值与 A 反 + §4.9 反硬编); 重构为产 fm_freq_vs_t.tcl+真跑 WaveView; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 produce-tool(真实 foundry 波形不可便携)无法有牙 => 收敛为 produce-tool(便携化波形)是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-PostsimPortAudit-001":
        "post-sim run 引用/delvtobl/端口审计器->produce-tool (portability+analysis 双驱动 produce-action->produce-tool audit 脚本 reframe, §4 有牙必要, r742 spotcheck batch20): 用户 rongtaoy@hfeg0pkn001 原话「我来看一下 0812BK 里 0-group1/0-BL0 这次跑的 log 和 mt0,验证三件事:①引用网表/SPF 是否正确;②delvtobl 参数是否对;③mt0 是否体现 4 种失配方向」(analysis/Q&A 审计 post-sim run, deepread 1793101460874_7bqzr mc220), trace agent read_files+editor 写 check_run0812.py/probe_match2.py/scan_msaq_log.py 核对 deck .inc 引用; A 不可行原因=真实 post-sim run 文件(deck/netlist/SPF 在 .75)不可便携 + 纯 analysis 无 runnable artifact 无 check 牙 -> case 抽取「synth deck/netlist/spf fixtures + 真跑 FineSim + 产 audit 脚本+report」子技能, B 档 synthesized 合规, reframe 由 portability + analysis→produce-tool 双驱动非配额驱动; asset_fidelity=synth_deck ✓(已标); layer=L2 ✓(已标, check 真跑 FineSim subprocess, log.finesim_ran=True); trace 用户=analysis/Q&A(「验证三件事①引用网表/SPF②delvtobl③mt0 4 种失配」= 审计), case 收敛为 produce-tool(写 postsim_port_audit.py report.json 顶层键 deck_includes/delvtobl/port_audit/log/verdict/真跑 FineSim/.inc 引用核对/delvtobl 参数值/.subckt 端口一一对应/duplicated subckt log/port size mismatch ERROR 检测) 给 check() 牙(§4.1 hidden-B cross-input guard B report.json + .inc 引用 + delvtobl + 端口一一对应, B 值与 A 反 + §4.9 反硬编); 重构为产 postsim_port_audit.py+真跑 FineSim; check.py 15 断言验 hidden-B cross-input guard+防硬编使纯 analysis(真实 run 不可便携 + 无 runnable artifact)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-GmidSizingSearch-001": "portability produce-action->produce-tool sizing 搜索器",
    "EDA-Eval-DesignFlow-VecgenProbeEmptyDiag-001": "Q&A/diag->produce-tool 诊断器",
    "EDA-Eval-DesignFlow-Tr0JitterRemeas-001": "portability produce-action->produce-tool .tr0 重测器",
    "EDA-Eval-DesignFlow-JitterTieRerun-001": "portability produce-action->produce-tool TIE rerun 器",
    "EDA-Eval-DesignFlow-WtmDanglingElseMre0Diag-001": "Q&A/diag->produce-tool 诊断器",
    "EDA-Eval-DesignFlow-McFailModeDiag-001": "analysis/Q&A->produce-tool 诊断器+报告",
    "EDA-Eval-DesignFlow-McPvtVmEval-001": "portability produce-action->produce-tool deck 生成器",
    "EDA-Eval-DesignFlow-WvFmFreqExtract-001": "portability produce-tool->produce-tool 波形便携化",
    "EDA-Eval-DesignFlow-PostsimPortAudit-001": "portability+analysis 双驱动 produce-action->produce-tool audit 脚本",
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
    print(f"=== r786 batch20 reframe_note apply: {len(REFRAME_NOTES)} cases (target) ===")
    counts = {"OK": 0, "ALREADY": 0, "MISSING": 0}
    for cid, note in REFRAME_NOTES.items():
        status, info = apply_one(cid, note)
        counts[status] = counts.get(status, 0) + 1
        print(f"  [{status}] {info} (driver={DRIVER.get(cid,'?')})")
    print(f"\nSummary: OK={counts['OK']} ALREADY={counts['ALREADY']} MISSING={counts['MISSING']}")
    print(f"Expected reframe_note count after apply: 125 + {counts['OK']} = {125 + counts['OK']}")


if __name__ == "__main__":
    main()
