#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r778 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r733_spotcheck12.tsv (batch12, 10 keep_reframe cases).
Spec: r771 bounded queue 档1→档3→档2. r772 档1 done. r773 batch9 / r774 batch10 / r777 batch11 done (reframe_note 49→61).
本轮 r778 档3 batch12 (r733 spotcheck12, 10 cases). reframe_note 61→71.

reframe_note text = r733 spotcheck12 per_case_reasoning + cases/B trace_source(user@host) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False, round-trip identical 验过.

Driver 分类 (per per_case_reasoning):
  - portability + produce-action→produce-plan: 1 case (DcSimSetupFromRef, 跑仿真→配置方案, check 无法真跑 HSPICE)
  - portability + Q&A/diag/explain/how-to→produce-report: 9 cases (trace 用户问 Q&A/how-to/explain/diag, 助手给文本答案未产出脚本,
    case 重构为 produce structured report 给 check() 牙; "candidate" = 待 trace 全文确认, 参照 batch10/11 先例)
"""
import json, os, io

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-DcSimSetupFromRef-001":
        "DC 仿真设置参考->produce-plan (portability+produce-action→produce-plan reframe, §4 有牙必要, r733 spotcheck batch12): 用户 qijingx@hfeg0pjn200 做 Vdleq Stdby LDO 仿真, 先问能否访问 zoeyyuan 的 04_VdleqStdby 目录, 比对 4 处 TB 外围差异, 最终请求(未完成)「我想先做个 dc 仿真, 你参考一下…端口设置到 pvcc/vss/vdd1, Fin/Fout 短接」(produce-action 想跑 DC 仿真); A 不可行原因=真实 /proj 工程目录+HSPICE/ALPS license SUT 沙盒不可达 -> 用自包含合成 ref_testbench.sp/dut_ports.json 保留真实任务结构(asset_fidelity=B-synthesized 已正确标注); trace 用户想跑 DC 仿真= produce-action, trace 请求未完成, case 收敛为 produce-plan(配置方案 JSON, 不同产物, 因 check 无法真跑 HSPICE); 重构为产 dc_sim_setup_plan.json; check.py 18 断言验 端口 pvcc/vss/vdd1 + Fin/Fout 短接 + hidden-B cross-input guard pvcc=0.9/vdd1=1.2 使原 produce-action 无法有牙 => 收敛为 produce-plan 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-FinesimConvDiag-001":
        "FineSim 瞬态不收敛根因诊断->produce (portability+Q&A/diag->produce candidate reframe, §4 有牙必要, r733 spotcheck batch12): 用户 curryxu@hfeg0pkn001 问 FineSim 报错原因, 报错日志 diverged at node 逐字保留; A 不可行原因=真实 /proj 工程+FineSim 环境 SUT 沙盒不可达 -> 用自包含合成 error_log.txt/run_cmd.txt/netlist_snippet.sp/option_finesim.sp 保留真实任务结构(asset_fidelity=synth_deck, 待 @A apply 标); trace 用户问「原因」= Q&A, 助手做分析未产出脚本, case 要求产诊断报告给 check() 牙(Q&A/diag->produce reframe, 待 trace 全文确认, 参照 batch11 先例); 重构为产 finesim_conv_diag.json; check.py 16 断言验 error_type/diverged_node/node_is_root_cause=false/circuit_module/diverged_techniques+hidden-B cross-input guard 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SpiceDeckExplain-001":
        "spice deck 共模跟踪精度解释->produce (portability+explain->produce candidate reframe, §4 有牙必要, r733 spotcheck batch12): 用户 junweix@hfeg0pkn002 要解释 8_commode.sp; A 不可行原因=真实 /proj/commonIP 工程目录+PrimeSim/HSPICE 环境 SUT 沙盒不可达 -> 用自包含合成 8_commode.sp/Setting.sp/.mt0/.log/.pd0 保留真实任务结构(asset_fidelity=synth_deck, 待 @A apply 标); trace 用户问「解释 sp 文件」= Q&A-explain, 助手在 trace 逐段讲解未产出结构化脚本, case 要求产解释报告给 check() 牙(explain->produce reframe, 待 trace 全文确认); 重构为产 spice_deck_explain.json; check.py 27 断言验 analysis_types/dc_sweep/monte_carlo/offset_meas+hidden-B cross-input guard 使纯 explain 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-ManualSectionExtract-001":
        "Aether 手册网表抽取章节提取->produce (portability+Q&A-how-to->produce-script-different-artifact candidate reframe, §4 有牙必要, r733 spotcheck batch12): 用户 t0002614@hfeg0pkn004 问抽取网表方法 + config view 作用; A 不可行原因=真实 Aether DM 手册(内网 OCR 片段) SUT 沙盒不可达 -> 用自包含合成 section.md 保留真实任务结构(asset_fidelity=synth_data, 待 @A apply 标); trace 用户问「怎么抽取+config view 作用」= Q&A-how-to, 助手在 trace 检索手册回答未产出解析脚本, case 要求产 section 解析脚本(Q&A->produce-script, 不同产物, 但手册主题 trace-faithful); 重构为产 manual_section_extract.py + manual_section_extract.json; check.py 35 断言验 解析脚本+结构化提取+hidden-B cross-input guard 使纯 Q&A 无法有牙 => 重构为 produce-script 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-AetherHowToGuide-001":
        "Aether MDE 仿真设置流程指南->produce (portability+Q&A-how-to->produce-guide candidate reframe, §4 有牙必要, r733 spotcheck batch12): 用户 t0002062@hfeg0pkn002 问怎么仿真电路; A 不可行原因=真实 Aether MDE 环境+手册(内网不可达) SUT 沙盒不可达 -> 用自包含合成 scenario.txt/manual 片段保留真实任务结构(asset_fidelity=synth_data, 待 @A apply 标); trace 用户问「怎么仿真电路」= Q&A-how-to, 助手在 trace 检索手册产出流程回答未产出结构化脚本, case 要求产 howto guide 给 check() 牙(Q&A->produce-guide reframe, 待 trace 全文确认); 重构为产 howto_guide_gen.py + howto_guide.json; check.py 16 断言验 view_type/purpose/creation_path+hidden-B cross-input guard 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-PwrNoiseDeckExplain-001":
        "电源噪声注入 deck 分析->produce (portability+explain->produce candidate reframe, §4 有牙必要, r733 spotcheck batch12): 用户 junweix@hfeg0pjn185 要分析 5_pnoise.sp 仿真过程和测量信号; A 不可行原因=真实 /proj 工程目录+HSPICE 环境 SUT 沙盒不可达 -> 用自包含合成 netlist.sp(从助手 MSG6 逐字重建) 保留真实任务结构(asset_fidelity=B-synthesized-from-trace 已正确标注); trace 用户「分析仿真过程和测量信号」= explain, 助手在 trace 逐句讲解 deck 未产出结构化脚本, case 要求产解释报告给 check() 牙(explain->produce reframe, 待 trace 全文确认); 重构为产 pwr_noise_deck_explain.json; check.py 24 断言验 simulator_family/analysis_type=tran/tran step/temperature+hidden-B cross-input guard(hidden B 合成结构不同的 Hspice deck)使纯 explain 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SimResultDirExplain-001":
        "HSPICE vtgm 结果目录逐文件解释->produce (portability+explain->produce candidate reframe, §4 有牙必要, r733 spotcheck batch12): 用户 e0039122@hfeg0pkn003 要分析 vtgm result 目录下每个文件; A 不可行原因=真实 /proj HSPICE 结果目录 SUT 沙盒不可达 -> 用自包含合成 .lis/.ms0/.ms1/logFile/.st0/.pa0(从助手 MSG27 逐文件讲解逐字重建)保留真实任务结构(asset_fidelity=B-synthesized-from-trace 已正确标注); trace 用户「逐文件解释」= explain, 助手在 trace 逐文件讲解未产出结构化脚本, case 要求产解释报告给 check() 牙(explain->produce reframe, 待 trace 全文确认); 重构为产 sim_result_explain.py + sim_result_explain.json; check.py 24 断言验 simulator/simulator_version/test_name/device_type/W/L/NF/corner/vtgm/gm_max+hidden-B cross-input guard(hidden B 合成 NanoSpice vtgm run)使纯 explain 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-PipeStdinBlockDiag-001":
        "perl STDOUT 接 python stdin 阻塞诊断->produce (portability+debug-Q&A->produce-diag-report candidate reframe, §4 有牙必要, r733 spotcheck batch12): 用户 zxtu@hfeg0pkn001 问 perl STDOUT 接 python stdin + sys.stdin 没内容 + 不能改 perl; A 不可行原因=真实 runsim.pl(2456 行生产脚本)+LSF 环境 SUT 沙盒不可达 -> 用自包含合成 doc/runsim.pl 真实节选(2456 行 fork/exec/Running in/sleep 10/exit 1 + bsub/pick_best_queue + 真实命令参数 -q fqueue3 -p ddgoa -v V0 -s finesim -Y Primesim_2023)+clprojinfo.py 真实 6 行保留真实任务结构(asset_fidelity=B-synthesized-from-trace 已正确标注); trace 用户问「为什么 stdin 没内容+怎么解决」= debug-Q&A, 助手在 trace 读代码诊断未产出结构化脚本, case 要求产诊断报告给 check() 牙(debug-Q&A->produce reframe, 待 trace 全文确认); 重构为产 pipe_diag.py + pipe_diag.json; check.py 18 断言验 root_cause.primary=stdout_self_redirect/cross-input guard != fork_inherit_stdout_no_eof+hidden-B cross-input guard(hidden B 合成 NanoSpice 场景 stdout 自重定向根因)使纯 debug-Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-VirtuosoPreSimNetlistLocate-001":
        "Virtuoso ADE 前仿网表定位->produce-plan (portability+Q&A-how-to->produce-plan candidate reframe, §4 有牙必要, r733 spotcheck batch12): 用户 zhililu@hfeg0pkn002 问前仿网表路径怎么找; A 不可行原因=真实 /proj ADE L/Spectre 环境 SUT 沙盒不可达 -> 用自包含合成 ade_scenario.md(还原真实 trace 的知识结构: ADE L/Spectre/inv_test/simulation 目录结构/网表文件名/GUI 找法/重生成警告/4 种修改方式)保留真实任务结构(asset_fidelity=B-synthesized-from-trace 已正确标注); trace 用户问「网表在哪怎么找」= Q&A-how-to, 助手在 trace 基于标准行为回答未产出结构化脚本, case 要求产 locate plan 给 check() 牙(Q&A->produce-plan reframe, 待 trace 全文确认); 重构为产 netlist_locate_plan.py + netlist_locate_plan.json; check.py 18 断言验 cross-input guard scenario.simulator==hspice/design_name/网表路径+hidden-B cross-input guard(hidden B 合成 ADE XL/HSPICE/amp_tb/IC6.1.7 场景)使纯 Q&A 无法有牙 => 重构为 produce-plan 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SkillPkgCapabilityExplain-001":
        "skill 包功能+SOP 解释->produce-explain-report (portability+Q&A-explain->produce candidate reframe, §4 有牙必要, r733 spotcheck batch12): 用户 shunlinp@hfeg0pkn002 问 skill 功能+怎么用+SOP; A 不可行原因=真实 skills_v0.2 包(内网 /proj) SUT 沙盒不可达 -> 用自包含合成 doc/(还原真实 skill 包知识结构: 6 子模块/流程顺序/4 缺陷类型/sim_template/run_finesim_sim.sh/.current_run 串联机制/SOP-A/B/C)保留真实任务结构(asset_fidelity=B-synthesized-from-trace 已正确标注); trace 用户问「功能+怎么用」= Q&A-explain, 助手在 trace 产出功能全景+SOP 回答未产出结构化脚本, case 要求产解释报告给 check() 牙(Q&A-explain->produce reframe, 待 trace 全文确认); 重构为产 skill_pkg_explain.py + skill_pkg_explain.json; check.py 18 断言验 cross-input guard package.name==skills_v1.0/work_dir/primary_cell/sim_config/prerequisites+hidden-B cross-input guard(hidden B 合成 skills_v1.0 包参数不同 cell Lp5Top/lib hbt_top/queue spqueue2/temp 85)使纯 Q&A-explain 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-DcSimSetupFromRef-001": "portability+produce-action→produce-plan",
    "EDA-Eval-DesignFlow-FinesimConvDiag-001": "portability+Q&A/diag->produce(candidate)",
    "EDA-Eval-DesignFlow-SpiceDeckExplain-001": "portability+explain->produce(candidate)",
    "EDA-Eval-DesignFlow-ManualSectionExtract-001": "portability+Q&A-how-to->produce-script-different-artifact(candidate)",
    "EDA-Eval-DesignFlow-AetherHowToGuide-001": "portability+Q&A-how-to->produce-guide(candidate)",
    "EDA-Eval-DesignFlow-PwrNoiseDeckExplain-001": "portability+explain->produce(candidate)",
    "EDA-Eval-DesignFlow-SimResultDirExplain-001": "portability+explain->produce(candidate)",
    "EDA-Eval-DesignFlow-PipeStdinBlockDiag-001": "portability+debug-Q&A->produce(candidate)",
    "EDA-Eval-DesignFlow-VirtuosoPreSimNetlistLocate-001": "portability+Q&A-how-to->produce-plan(candidate)",
    "EDA-Eval-DesignFlow-SkillPkgCapabilityExplain-001": "portability+Q&A-explain->produce(candidate)",
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
        # insert reframe_note as last key, preserving order
        m["reframe_note"] = note
        # round-trip check: parse new text, ensure no other keys changed
        new_text = json.dumps(j, ensure_ascii=False, indent=2)
        # reparse for safety
        j2 = json.loads(new_text)
        # ensure reframe_note is last key in metadata dict
        # (Python 3.7+ preserves insertion order; appending to dict places it last)
        with io.open(path, "w", encoding="utf-8") as f:
            f.write(new_text)
            if not new_text.endswith("\n"):
                f.write("\n")
        results.append((cid, DRIVER[cid], "APPLIED"))
    for r in results:
        print("\t".join(r))
    print(f"\nApplied: {sum(1 for r in results if r[2]=='APPLIED')}/{len(results)}")

if __name__ == "__main__":
    main()
