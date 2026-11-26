#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r779 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r734_spotcheck13.tsv (batch13, 9 keep_reframe cases).
Spec: r771 bounded queue 档1→档3→档2. r772 档1 done. r773-r778 档3 batch9-12 done (reframe_note 32→71).
本轮 r779 档3 batch13 (r734 spotcheck13, 9 cases). reframe_note 71→80.

reframe_note text = r734 spotcheck13 per_case_reasoning + cases/B trace_source(user@host) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False, round-trip identical 验过.

Driver 分类 (per per_case_reasoning):
  - portability + produce-action→produce-tool (different artifact, check 无法真跑仿真/须确定性跑候选): 7 cases
    (LvlShftSpecCompliance/LvlShftSoaSizing/AnalogOptPipeline/Md0MeasureExtract/SiInpTokenRm/ShrinkExtract/SetNetlistParam)
  - portability + debug-Q&A→produce-diag-report: 1 case (SaNPsimDiag)
  - portability + explain→produce-report: 1 case (WlvlShmooLoopAnalyze)
"""
import json, os, io

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-LvlShftSpecCompliance-001":
        "lvlshft 电平转换器规格合规验证->produce-tool (portability+produce-action→produce-tool reframe, §4 有牙必要, r734 spotcheck batch13): 用户 e0025730@10.129.8.86 维护 lvlshft Case 3 Vss2VkbVcc 负压电平转换器, 跑 run_test_only.py 注入 .param s=0.05/W=1.00/L=1.30um/beta1=70 到 5 个 .sp 文件, result_summary.txt 含 Rise 0.573ns/Fall 0.304ns/Duty; A 不可行原因=真实 lvlshft 工具链+HSPICE/FineSim license SUT 沙盒不可达 -> 用自包含合成 lvlshft bundle(.sp/.param/result_summary)保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=produce-action(跑优化+验合规), trace 已跑完产出 result_summary.txt, case 收敛为 produce-tool(写合规检查器+报告)给 check() 牙(§4.2 subprocess 跑候选 python compliance_checker.py 解析 .sp/result + §4.1 hidden-B cross-input guard); 重构为产 compliance_checker.py+compliance_report.json; check.py 12 断言验 injected_2_delay.sp 参数+合规阈值+hidden-B cross-input guard 使原 produce-action 无法有牙(无法真跑 HSPICE) => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-LvlShftSoaSizing-001":
        "lvlshft 6 Case SOA 选型->produce-tool (portability+produce-action→produce-tool reframe, §4 有牙必要, r734 spotcheck batch13): 用户 e0025730@10.129.8.86 维护 lvlshft 工具链, 跑 soa_selector.py 对 6 个 Case 各选代表拓扑(Vcc2Vdleq/Vss2VkbVcc/Vss2VkbVdd1/Vdd12Vwlp/Vint2VdleqAryA+Vcc2Vdd1)做 SOA 选型, 产出器件型号(input_n=ntn_m/600e-9 等)+沟道宽度+电压参数(pvnn/pvdd); A 不可行原因=真实 lvlshft 工具链+仿真环境 SUT 沙盒不可达 -> 用自包含合成 6 拓扑选型 JSON 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=produce-action(跑 SOA 选型), trace 已跑完产出 netlist_sizing.yaml, case 收敛为 produce-tool(写选型检查器+报告)给 check() 牙; 重构为产 soa_sizing_checker.py+soa_sizing_report.json; check.py 12 断言验 topology→case 映射+器件型号+voltage_params+hidden-B cross-input guard 使原 produce-action 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-AnalogOptPipeline-001":
        "CS amp 模拟退火优化->produce-tool (portability+produce-action→produce-tool reframe, §4 有牙必要, r734 spotcheck batch13): 用户 e0044979@hfeg0pkn001 用模拟退火引擎对共源放大器(CMOS 0.18um, NMOS M1+PMOS M2+R1+C1, vdd=1.8V)做 M1_w/M1_l/M2_w/M2_l/R1 五变量尺寸优化, 一阶 gm/Id 代理模型评估 gain/bandwidth/power 逼近目标(40dB/100MHz/1mW), 产出 optimization_results.json; A 不可行原因=真实 HSPICE/FineSim 环境+代理模型 SUT 沙盒不可达 -> 用自包含合成 CS amp 参数+gm/Id 代理模型资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=produce-action(用现有引擎跑优化, 非构建引擎), case 收敛为 produce-tool(实现优化引擎)给 check() 牙(§4.2 subprocess 跑候选 python run_optimization.py 用 gm/Id 解析代理模型, 须确定性可重复); 重构为产 run_optimization.py+optimization_results.json; check.py 16 断言验 5 变量+3 目标 gain 40dB/BW 100MHz/power 1mW+结果结构+hidden-B cross-input guard 使原 produce-action 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SaNPsimDiag-001":
        "SRAM sense-amp noise sim 仿真诊断->produce-diag-report (portability+debug-Q&A→produce-diag-report candidate reframe, §4 有牙必要, r734 spotcheck batch13): 用户 ming1w@hfeg0pkn005 跑 SRAM sense-amplifier noise performance 仿真, FineSim 报 .trannoise requires spice mode (not promd), 换 PrimeSim HSPICE 后 .trannoise malformed(missing command data), DC 后 abort 无 .tr0; A 不可行原因=真实 FineSim/HSPICE 环境+仿真日志 SUT 沙盒不可达 -> 用自包含合成 sanp_result.log/Check_SaNP_tb.sp/.lis/.st0/run.sh 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=debug-Q&A(问原因+修复), 助手在 trace 读 log 诊断未产出结构化脚本, case 要求产出诊断报告给 check() 牙(debug-Q&A→produce-diag-report reframe, 待 trace 全文确认, 参照 batch11/12 先例); 重构为产 sanp_diag.py+diagnosis_report_A.json; check.py 15 断言验 simulator/mode/fatal_errors/root_cause/fixes/verdict+hidden-B cross-input guard 使纯 debug-Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-Md0MeasureExtract-001":
        "ModelQA .md0 measure 解析扩展->produce-tool (portability+produce-action→produce-tool reframe, §4 有牙必要, r734 spotcheck batch13): 用户 rongjiez@hfhds201 为 ModelQA QA 工具扩展 runModelQA_new.pl 解析 6 measure(vtgm/vtsat/vtlin/idsat/idlin/ioff), vtsat/vtlin 匹配 idlin=/idsat=, 电流 normalize(idsat/(w*nf)) 电压不 normalize; A 不可行原因=真实 Perl 生产脚本+HSPICE .md0 输出 SUT 沙盒不可达 -> 用自包含合成真实 .md0 measure 文件资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=produce-action(改 Perl 脚本), case 收敛为 produce-tool(写 Python 脚本做 .md0 解析)给 check() 牙(Perl→Python, 同解析逻辑不同实现语言); 重构为产 .py 脚本+CSV(devkey/corner/temp/vdd/type/total/normalized); check.py 15 断言验 6 measure regex+normalized 公式+hidden-B cross-input guard 使原 produce-action 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SiInpTokenRm-001":
        "FineSim si.inp 标记删除命令->produce-tool (portability+produce-action→produce-tool reframe, §4 有牙必要, r734 spotcheck batch13): 用户 mike@hfeg0plg05 在 FineSim MatrixRun 目录下多子目录各含 si.inp, 原话(pinyin)「bangwo xiege mingling ,woyao shandiao si.inp zhong T_mBistOsc zifuchuan」(写命令删 T_mBistOsc 字符串); A 不可行原因=真实 FineSim MatrixRun 多子目录+si.inp 生产文件 SUT 沙盒不可达 -> 用自包含合成 si.inp finesim_ignore 行资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=produce-action(写命令), 助手在 trace 给 sed 命令, case 收敛为 produce-tool(写脚本)给 check() 牙(脚本可 subprocess 跑+验文件级 diff); 重构为产 .py/.sh 脚本(删 T_mBistOsc+保留其他标记+保留 .option 行结构+非目标行不变); check.py 14 断言验 删除标记+保留结构+hidden-B cross-input guard 使原 produce-action 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-ShrinkExtract-001":
        "MPQA model .lib SHRINK 提取->produce-tool (portability+produce-action→produce-tool reframe, §4 有牙必要, r734 spotcheck batch13): 用户 rongjiez@hfeg0pkn005 为 MPQA model QA 工具修改 runModelQA_new.pl, 从 model 文件经 .lib 'incFile_G5_CIP' 同级目录解析第一个 SHRINK=; A 不可行原因=真实 Perl 生产脚本+HSPICE model 文件 SUT 沙盒不可达 -> 用自包含合成 model.sp/incFile_G5_CIP 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=produce-action(改 Perl 脚本), case 收敛为 produce-tool(写 Python 提取脚本)给 check() 牙(Perl→Python, 同提取逻辑); 重构为产 extract_shrink.py; check.py 14 断言验 单行数字+跳过 * SHRINK=9.999 注释陷阱+只取第一个+容空格变长+cross-input guard A≠B 使原 produce-action 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-WlvlShmooLoopAnalyze-001":
        "DDR5 write-leveling shmoo loop 分析->produce-report (portability+explain→produce-report candidate reframe, §4 有牙必要, r734 spotcheck batch13): 用户 ericw@hfhds201 做 DDR5 DRCPA write-leveling shmoo loop 分析, 原话「Writeleveling001_external_writeleveling_preamble2_shmoo ... 分析这个路径下的这个文件 里面的循环是干什么的 如何循环的」(explain/analysis 问循环语义); A 不可行原因=真实 DDR5 shmoo C 代码片段+FineSim 环境 SUT 沙盒不可达 -> 用自包含合成 shmoo C 代码片段资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=explain(分析循环语义), 助手在 trace 逐行讲解未产出结构化脚本, case 要求产出分析报告给 check() 牙(explain→produce-report reframe, 待 trace 全文确认); 重构为产 analyze_wlvl_shmoo_loop.py+out.json; check.py 15 断言验 loop.var/scale/step/start_offset/end_offset/iter_count+cross-input guard B≠A 使纯 explain 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SetNetlistParam-001":
        "SKILL 修改 Netlist 参数并运行->produce-tool (portability+produce-action→produce-tool reframe, §4 有牙必要, r734 spotcheck batch13): 用户 zjqiao@hfhds201 要求写 SKILL, 原话「编写一个skill，用户指定 netlist 名称，SKILL 修改/rundata/drvqa/.../Run_Compress_Netlist shell 脚本中的 Netlist参数，然后运行该 shell 脚本执行转换」; A 不可行原因=真实 SKILL/Virtuoso 环境+Run_Compress_Netlist shell 脚本 SUT 沙盒不可达 -> 用自包含合成 Run_Compress_Netlist shell 脚本资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=produce-action(写 SKILL), 助手用 editor 写 SetNetl, case 收敛为 produce-tool(写 Python 脚本做参数修改)给 check() 牙(SKILL→Python, 同修改+运行逻辑不同实现语言); 重构为产 set_netlist_param.py; check.py 12 断言验 替换活动 Netlist= 行+保留 # 注释+保留 # 空格陷阱+cross-input guard A≠B 使原 produce-action 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-LvlShftSpecCompliance-001": "portability+produce-action→produce-tool",
    "EDA-Eval-DesignFlow-LvlShftSoaSizing-001": "portability+produce-action→produce-tool",
    "EDA-Eval-DesignFlow-AnalogOptPipeline-001": "portability+produce-action→produce-tool",
    "EDA-Eval-DesignFlow-SaNPsimDiag-001": "portability+debug-Q&A->produce-diag-report(candidate)",
    "EDA-Eval-DesignFlow-Md0MeasureExtract-001": "portability+produce-action→produce-tool(Perl->Python)",
    "EDA-Eval-DesignFlow-SiInpTokenRm-001": "portability+produce-action→produce-tool(cmd->script)",
    "EDA-Eval-DesignFlow-ShrinkExtract-001": "portability+produce-action→produce-tool(Perl->Python)",
    "EDA-Eval-DesignFlow-WlvlShmooLoopAnalyze-001": "portability+explain->produce-report(candidate)",
    "EDA-Eval-DesignFlow-SetNetlistParam-001": "portability+produce-action→produce-tool(SKILL->Python)",
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
    # round-trip baseline (preserve formatting identical except new key)
    m["reframe_note"] = note
    d["metadata"] = m
    out = json.dumps(d, ensure_ascii=False, indent=2)
    # verify parseable
    json.loads(out)
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    return ("OK", case_id)


def main():
    print(f"=== r779 batch13 reframe_note apply: {len(REFRAME_NOTES)} cases ===")
    counts = {"OK": 0, "ALREADY": 0, "MISSING": 0}
    for cid, note in REFRAME_NOTES.items():
        status, info = apply_one(cid, note)
        counts[status] = counts.get(status, 0) + 1
        print(f"  [{status}] {info} (driver={DRIVER.get(cid,'?')})")
    print(f"\nSummary: OK={counts['OK']} ALREADY={counts['ALREADY']} MISSING={counts['MISSING']}")
    print(f"Expected reframe_note count after apply: 71 + {counts['OK']} = {71 + counts['OK']}")


if __name__ == "__main__":
    main()
