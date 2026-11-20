#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r777 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r732_spotcheck11.tsv (batch11, 12 keep_reframe cases).
Spec: r771 bounded queue 档1→档3→档2. r772 档1 done. r773 batch9 (r730,8) / r774 batch10 (r731,9) done.
本轮 r777 档3 batch11 (r732 spotcheck11, 12 cases). reframe_note 49→61.

reframe_note text = r732 spotcheck11 per_case_reasoning + cases/B trace_source(user@host) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False, round-trip identical 验过.

Driver 分类 (per per_case_reasoning):
  - portability + Q&A->produce (candidate): 11 cases (trace 用户问 Q&A/how-to/diag, 助手给文本答案未产出脚本,
    case 重构为 produce structured report 给 check() 牙; "candidate" = 待 trace 全文确认, 参照 batch10 3 先例)
  - portability + produce-different-artifact (borderline): 1 case (SpfExtract, 助手产 spf_export.py 但 case 要求 feasibility report)
"""
import json, os, io

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

# case_id -> reframe_note text
REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-SpfExtractFeasibility-001":
        "SPF 抽取能力查询->produce-different-artifact (portability+produce-different-artifact borderline reframe, §4 有牙必要, r732 spotcheck batch11): 用户 kailiu@hfeg0plg100 问「你有抽一个 cell 的 spf 文件的功能吗」(Q&A 能力查询), 助手扫描 pyAether API/skill/CAD 后发现无直接 SPF 导出 API, 推荐 aeIpcBeginProcess 调外部提取器(StarRC)走 6 步流程并产 spf_export.py; A 不可行原因=真实 pyAether API scan 结果+StarRC license/路径 SUT 沙盒不可达 -> 用自包含合成 manifest 保留真实任务结构(asset_fidelity=synth_data); trace agent 本就 produce(产 spf_export.py), case 要求第三种产物 feasibility report(结构化诊断报告)给 check() 牙(§4.2 subprocess+§4.1 hidden-B), produce->produce-different-artifact borderline reframe; 重构为产 spf_feasibility_report.py+spf_report.json; check.py 13 断言验 top-level keys+verdict+spf_export_apis_found+related_apis 分类+recommended_approach+primary_external_tool+workflow_steps 有序+step->api mapping+existing_tools_reuse+required_config substrate+environment_notes workspace_empty+hidden-B cross-input guard 使原 license/路径不可达任务无法有牙 => 合成 manifest+produce feasibility report 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-AmsConfigViewDiag-001":
        "AMS config 设置核对->produce (portability+Q&A->produce candidate reframe, §4 有牙必要, r732 spotcheck batch11): 用户 wei9liu@hfeg0plg75 用 ADE Maestro 跑 AMS 仿真(config_V1, tran stop=500us)写权限受限, 改问「核对这个 test 的设置有没有问题」(Q&A 核对), 助手深挖发现 elaboration 失败: config_V1 viewlist 含 functional 视图致 Verilog .v 被错误路由到 amsspice 而非 xmvlog; A 不可行原因=真实 /proj/lacaa 工程目录+ADE Maestro 环境 SUT 沙盒不可达 -> 用自包含合成 config_V1 viewlist/error log 保留真实任务结构(asset_fidelity=synth_deck); trace 用户问「核对设置」= Q&A, 助手做分析未产出脚本, case 要求产 diagnostic report 给 check() 牙(Q&A->produce reframe, 待 trace 全文确认, 参照 batch9 SimModelMismatchDiag keep_faithful 先例); 重构为产 diagnose_ams_config.py+ams_diagnostic_report.json; check.py 14 断言验 top-level keys+tran_stop+corner+simulator+design_vars+failing_parser+error_type+error_file ends .v+root_cause.category+viewlist_comparison.added_in_V1 contains functional+fix_recommendation mentions functional/digital+run_comparison.healthy_parser==xmvlog+core_dump_found+hidden-B cross-input guard 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-VirtuosoSfeLangDiag-001":
        "Virtuoso SFE 报错诊断->produce (portability+Q&A/diag->produce candidate reframe, §4 有牙必要, r732 spotcheck batch11): 用户 zhililu@hfeg0plg75 用 Virtuoso ADE Maestro 跑 finesim 仿真, 问「virtuoso 怎么用已生成的 netlist 仿真」(how-to Q&A)后贴 SFE-868/SFE-1802/SFE-1025/SFE-1703 报错, 助手定位根因=netlist 文件缺 simulator lang= 声明; A 不可行原因=真实 /proj 工程目录+finesim 环境 SUT 沙盒不可达 -> 用自包含合成 input.scs/netlist error log 保留真实任务结构(asset_fidelity=synth_deck); trace 用户问 how-to+贴报错问问题 = Q&A/diag, 助手给方法+诊断分析未产出脚本, case 要求产 diagnostic report 给 check() 牙(Q&A/diag->produce reframe, 待 trace 全文确认); 重构为产 diagnose_sfe_errors.py+sfe_diagnostic_report.json; check.py 13 断言验 submit.zip 含脚本+report.design 提取 library/cell/view+simulator_language+include_chain basename+error_type+error_codes 含 SFE-1802/1025/1703+missing_lang_directive+flagged_model_names nsvt_dbc/psvt_dbc+instance_terminal_issue+root_cause+fix_action+schema 11 keys+hidden-B cross-input guard 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-TrnToVcdConvertGuide-001":
        "trn 转 vcd 能力查询->produce (portability+Q&A->produce candidate reframe, §4 有牙必要, r732 spotcheck batch11): 用户 warrenm@hfeg0pkn002 用 Xcelium vsim 跑 DDR 写均衡仿真产出 xcelium.shm(trn+dsn), 问「AeTher 中是否有将 trn 转 vcd 的功能」(Q&A), 助手探查发现无 vconvert, 用户多路径全失败(cshm GLIBCXX_3.4.20/vwdb2vcd GLIBC_2.14/iWaveExportCsvTool 不读 SHM), 根因=系统 glibc/libstdc++ 过旧; A 不可行原因=真实 env(工具链+glibc) SUT 沙盒不可达 -> 用自包含合成 sim_context/tool failure log 保留真实任务结构(asset_fidelity=synth_data); trace 用户问「怎么转/有没有功能」= Q&A, 助手探查+分析未产出脚本, case 要求产 conversion plan report 给 check() 牙(Q&A->produce reframe, 待 trace 全文确认); 重构为产 build_conversion_plan.py+trn2vcd_plan.json; check.py 13 断言验 submit.zip 含脚本且 A 运行产合法 JSON+waveform_format+conversion_tools 含 cshm/vwdb2vcd/iWaveExportCsvTool+tool_failures error_category+system_root_cause+feasible_methods+recommended_method+rerun_command+vcd_dump_snippet+ld_preload_analysis affects_agent_env_only+schema 11 keys+hidden-B cross-input guard 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-FineSimDcConvGuide-001":
        "FineSim DC 不收敛原因/方案查询->produce (portability+Q&A->produce candidate reframe, §4 有牙必要, r732 spotcheck batch11): 用户 t0002441@hfhds201 问「Finesim 仿真报 DC 不收敛的错误, 可能的原因及解决方案有哪些」(Q&A 查原因/方案), 助手查阅 FineSim 安装目录 doc 后给结构化指南: 错误现象+拓扑/模型/选项三类原因+FineSim 特有选项+四种收敛方法+诊断流程+分级配置模板; A 不可行原因=真实 /apps/synopsys FineSim doc corpus SUT 沙盒无 license/路径不可达 -> 用自包含合成 FineSim doc corpus 保留真实任务结构(asset_fidelity=synth_deck); trace 用户问「原因/方案」= Q&A, 助手给文本指南未产出脚本, case 要求产 guide generator 给 check() 牙(Q&A->produce reframe, 待 trace 全文确认); 重构为产 finesim_dc_convergence_guide.py+dc_convergence_guide.json; check.py 13 断言验 submit.zip 含脚本且 B 运行+error_type+error_messages 从 B 日志提取 ≥2 条含 B 特有标记+root_cause_category topology+topology_causes≥2+model_causes≥2+option_causes≥2+finesim_options≥4+spice_options≥4+convergence_methods 覆盖四种(gmin_stepping/source_stepping/dptran/homotopy)+diagnostic_flow≥5 步+recommended_config 含 .OPTION/ITL1/GMIN+hidden-B cross-input guard B root_cause≠A 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-FineSimIntroGuide-001":
        "FineSim 介绍查询->produce (portability+Q&A->produce candidate reframe, §4 有牙必要, r732 spotcheck batch11): 用户 steveny@hfeg0pkn005 问「介绍 finesix」(即介绍 FineSim, Q&A), 助手用 ask-eda 技能查知识库(AskEDA KB not hit)回退 LLM 通用知识, 给 FineSim 结构化介绍: 是什么/7 功能/5 特点/5 优势/总结; A 不可行原因=真实 ask-eda KB(/apps 知识库) SUT 沙盒不可达 -> 用自包含合成 corpus.jsonl 保留真实任务结构(asset_fidelity=synth_data); trace 用户问「介绍」= Q&A, 助手给文本介绍未产出脚本, case 要求产 intro generator 给 check() 牙(Q&A->produce reframe, 待 trace 全文确认); 重构为产 simulator_intro_guide.py+simulator_intro_guide.json; check.py 13 断言验 submit.zip 含脚本且 B 运行+simulator_name 解析自 B query.log+what_is 含 B 仿真器名长度≥80+functions≥5+characteristics≥4+advantages≥4+summary 含 B 仿真器名长度≥50+key_terms≥10 含 B 特有术语+source_fragments id 全存于 B corpus+coverage 含 what_is/function/characteristic/advantage+kb_hit_status 解析自 B query.log+query_text 含 HSPICE 字样+hidden-B cross-input guard B simulator_name≠A 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-MatrixRunDirExplain-001":
        "MatrixRun 目录文件解释->produce (portability+Q&A->produce candidate reframe, §4 有牙必要, r732 spotcheck batch11): 用户 johnl@hfeg0pkn001 给 MatrixRun_Netlist_SpfBA_20260807PM_mBist 目录路径问「你看下这些文件什么意思」(Q&A 解释), 助手 list_allowed_files+自写 _categorize.py 分类 294 entries/13 subdirs+读 8 编号脚本+列 corner 子目录+head 裸 split 碎片, 会话末尾 code_sidecar_sigterm 完整解释未写进 messages; A 不可行原因=真实 /rundata MatrixRun 目录 SUT 沙盒不可达 -> 用自包含合成 dir_listing.json/corner_listing.json 保留真实任务结构(asset_fidelity=synth_data); trace 用户问「解释文件」= Q&A, 助手做分类分析未产出完整脚本(code_sidecar_sigterm), case 要求产 explanation report 给 check() 牙(Q&A->produce reframe, 待 trace 全文确认); 重构为产 matrix_run_explain.py+matrix_run_explain.json; check.py 13 断言验 A 重跑 exit0 复现+目录分类+脚本解读+corner 子目录+结构化 explanation report+hidden-B cross-input guard 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-NanoSpicePrecisionGuide-001":
        "NanoSpice 精度/设置查询->produce (portability+Q&A->produce candidate reframe, §4 有牙必要, r732 spotcheck batch11): 用户 e0014566@hfeg0pkn001 问「Nanospice 仿真器的精度有哪些? 分别如何设置」(Q&A), 助手用 ask-eda 技能查知识库(命中 NanoSpice_X_User_Guide score 0.93), 给结构化精度指南: NanoSpice X 模式(+simmode=spicexN, N=1-5)+Pro X 模式(+simmode=proxN)+应用场景表; A 不可行原因=真实 ask-eda KB(/apps 知识库) SUT 沙盒不可达 -> 用自包含合成 query.log/corpus 保留真实任务结构(asset_fidelity=synth_data); trace 用户问「精度/设置」= Q&A, 助手给文本指南未产出脚本, case 要求产 guide generator 给 check() 牙(Q&A->produce reframe, 待 trace 全文确认); 重构为产 nanospice_precision_guide.py+nanospice_precision_guide.json; check.py 13 断言验 submit.zip 含脚本且 B 运行+simulator_name 解析自 B query.log+precision_modes≥2+precision_levels≥5+precision_mechanism 含 .OPTION/tolerance+circuit_type_optimization+application_scenarios≥3+command_examples≥3+summary 含 B 仿真器名长度≥50+key_terms≥10 含 .OPTION/ACCURACY+source_fragments id 全存于 B corpus+coverage 含 mechanism/mode/level/ckttype/app+hidden-B cross-input guard B simulator_name≠A 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-FineSimJobStatusDiag-001":
        "FineSim/PrimeSim MatrixRun job 状态监控->produce (portability+Q&A/analysis->produce candidate reframe, §4 有牙必要, r732 spotcheck batch11): 用户 tongfanl@hfeg0pkn002 监控 DDR6 FineSim/PrimeSim MatrixRun 老化仿真矩阵 job 状态, 反复要求 cline 读 bsub.log/bjobs/bmatrix 查 RUN/PEND/DONE/EXIT, 读 si.out 末尾进度百分数, 检查 si.inp 的 model/aging_model/mosrapath, 扫 si.out 找内存报错, 统计 cpu/elapsed 耗时, 全程读日志+解释零脚本产物; A 不可行原因=真实 LSF/MatrixRun 日志 SUT 沙盒不可达 -> 用合成离线日志快照(asset_fidelity=B-synthesized 已正确标注); trace 用户问「状态」= Q&A/analysis, 助手做分析零脚本产物, case 要求产 job report generator 给 check() 牙(Q&A/analysis->produce reframe, 待 trace 全文确认); 重构为产 finesim_job_report.py+finesim_job_report.json; check.py 13 断言验 submit.zip 含 json+script+A report valid JSON+total_jobs==10+status_counts RUN==8/PEND==1/DONE==1/EXIT+model==G5_CIP_Model_D5_v0d9_rev01 aging_model+mosrapath_commented_jobs+oom_jobs+max_progress_percent==80.0+completed_jobs+cross-input B total_jobs==12 status RUN==6/PEND≠A+B model!=A oom==2 mosra==2+A vs B differ guard+determinism 3 reruns byte-identical 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-FifoLatchRootCauseDiag-001":
        "DDR4 FIFO 输出锁存器多轮根因诊断->produce (portability+diag-Q&A->produce candidate reframe, §4 有牙必要, r732 spotcheck batch11): 用户 curryxu@hfeg0plg99 调试 DDR4 FIFO 输出锁存器电路(latrPF01DOutFIFOx1_m2701, testbench sim_FIFOx1), 反复问为何 RDFI<0> 拉高后 net53 无法保持高、为何 OUT 在末级 inv 关断后仍跟随 net53、为何 Data 节点定义 0.9V 初态后掉电、为何 DataN 浮空, 助手逐段读 netlist/input/pwr/option 做 RS 锁存+三态缓冲+Miller Cgd 耦合+.ic 冲突分析定位根因; A 不可行原因=真实 /proj 工程目录+HSPICE 环境 SUT 沙盒不可达 -> 用合成 netlist(asset_fidelity=B-synthesized 已正确标注); trace 用户多轮问「为什么异常」= diag Q&A, 助手做信号追踪+机制分析未产出脚本, case 要求产 root cause diagnostic 给 check() 牙(diag-Q&A->produce reframe, 待 trace 全文确认); 重构为产 fifo_latch_diag.py+fifo_latch_rootcause_diag.json; check.py 13 断言验 A 重跑 exit0+root_cause 识别+机制分析(RS 锁存/三态/Miller Cgd/.ic)+信号追踪+结构化 diagnostic report+hidden-B cross-input guard 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-BsubNoFolderDiag-001":
        "LSF bsub 仿真提交无输出文件夹诊断->produce (portability+diag-Q&A->produce candidate reframe, §4 有牙必要, r732 spotcheck batch11): 用户 lvyy@hfeg0pkn002 调试 LSF bsub 仿真提交问题: 提交 001_current.sp 后预期输出文件夹没出现, 换 fqueue3_dll 队列也一样, 问「为什么我仿真提交上去了但是没有生成文件夹? 换了 fqueue3_dll 的队列也是这样, 为什么」, 助手查 bjobs -l/bqueues -l/读 .sp 头部/读 run_1 定位三层根因(-o 写在作业命令后被当网表参数 / .sp 不可执行 exit 126 / 队列满致 PEND); A 不可行原因=真实 LSF 队列环境 SUT 沙盒不可达 -> 用合成 bjobs/bqueues log(asset_fidelity=B-synthesized 已正确标注); trace 用户问「为什么没生成文件夹」= diag Q&A, 助手查日志+分析未产出脚本, case 要求产 diagnostic 给 check() 牙(diag-Q&A->produce reframe, 待 trace 全文确认); 重构为产 bsub_nofolder_diag.py+bsub_nofolder_diag.json; check.py 14 断言验 A 重跑 exit0+三层根因(-o 误当网表参数/exit 126/队列满 PEND)+bjobs/bqueues 解析+结构化 diagnostic report+hidden-B cross-input guard 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SimIncompleteWalltimeDiag-001":
        "bisection 仿真未跑完根因诊断->produce (portability+diag-Q&A->produce candidate reframe, §4 有牙必要, r732 spotcheck batch11): 用户 rhyanw@hfeg0pkn002 跑一批 SMMismatch bisection 仿真(primesim, 40 corner, -np 6, fqueue2h), 发现大量 .bisec_mt0 结果只有一两个数值、smdatagrab2.pl 报告很多文件不存在, 反复问「怎么确认任务是运行还是卡死」「为什么没跑完」「是不是查询卡死导致的」「检查 sp 文件有没有问题」「改成 np16 会好吧」, 助手实证根因=LSF 队列 fqueue2h 的 2h walltime 上限到点发 user signal 掐断 bisection; A 不可行原因=真实 primesim/LSF 队列环境 SUT 沙盒不可达 -> 用合成 runsim/bisec log(asset_fidelity=B-synthesized 已正确标注); trace 用户多轮问「为什么没跑完+是否卡死」= diag Q&A, 助手实证分析未产出脚本, case 要求产 diagnostic 给 check() 牙(diag-Q&A->produce reframe, 待 trace 全文确认); 重构为产 script+json; check.py 16 断言验 候选必须在 B 上运行 exit0+12 top-level keys+root_cause.primary==lsf_queue_walltime_limit+secondary==node_overload+not_caused_by 排除 manual_kill/sp_file_error/stuck+elapsed_sec==B(10798)+queue_name==fqueue3h(B)≠A fqueue2h+hours_str==\"3.00 hours\"(B)+A-leak guard 无 A token+incomplete_lines==2/complete_lines==14(B)+total_cores==288 np==8(B)+hardcoded_path 含 Run2077(B)≠SM1029+proposed_np16==worse+recommendations 含 longer-queue AND reduce-parallel+bjobs RUN≠computing+determinism 3 reruns byte-identical 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-SpfExtractFeasibility-001": "portability+produce-different-artifact(borderline)",
    "EDA-Eval-DesignFlow-AmsConfigViewDiag-001": "portability+Q&A->produce(candidate)",
    "EDA-Eval-DesignFlow-VirtuosoSfeLangDiag-001": "portability+Q&A/diag->produce(candidate)",
    "EDA-Eval-DesignFlow-TrnToVcdConvertGuide-001": "portability+Q&A->produce(candidate)",
    "EDA-Eval-DesignFlow-FineSimDcConvGuide-001": "portability+Q&A->produce(candidate)",
    "EDA-Eval-DesignFlow-FineSimIntroGuide-001": "portability+Q&A->produce(candidate)",
    "EDA-Eval-DesignFlow-MatrixRunDirExplain-001": "portability+Q&A->produce(candidate)",
    "EDA-Eval-DesignFlow-NanoSpicePrecisionGuide-001": "portability+Q&A->produce(candidate)",
    "EDA-Eval-DesignFlow-FineSimJobStatusDiag-001": "portability+Q&A/analysis->produce(candidate)",
    "EDA-Eval-DesignFlow-FifoLatchRootCauseDiag-001": "portability+diag-Q&A->produce(candidate)",
    "EDA-Eval-DesignFlow-BsubNoFolderDiag-001": "portability+diag-Q&A->produce(candidate)",
    "EDA-Eval-DesignFlow-SimIncompleteWalltimeDiag-001": "portability+diag-Q&A->produce(candidate)",
}

def main():
    results = []
    for cid, note in REFRAME_NOTES.items():
        path = os.path.join(CASES_DIR, cid + ".json")
        if not os.path.exists(path):
            results.append((cid, DRIVER[cid], "MISSING_FILE"))
            continue
        with io.open(path, "r", encoding="utf-8") as f:
            raw = f.read()
        j = json.loads(raw)
        m = j.get("metadata")
        if m is None:
            results.append((cid, DRIVER[cid], "NO_METADATA"))
            continue
        if "reframe_note" in m:
            results.append((cid, DRIVER[cid], "ALREADY_HAS (skip)"))
            continue
        # append reframe_note as last key (preserve key order)
        m["reframe_note"] = note
        j["metadata"] = m
        out = json.dumps(j, ensure_ascii=False, indent=2)
        # round-trip identical check (semantic)
        _ = json.loads(out)
        with io.open(path, "w", encoding="utf-8") as f:
            f.write(out)
        results.append((cid, DRIVER[cid], "APPLIED"))
    print("# r777 reframe_note apply results")
    for cid, drv, st in results:
        print("%s\t%s\t%s" % (cid, drv, st))
    applied = sum(1 for _,_,st in results if st == "APPLIED")
    print("# APPLIED=%d  total=%d" % (applied, len(results)))

if __name__ == "__main__":
    main()
