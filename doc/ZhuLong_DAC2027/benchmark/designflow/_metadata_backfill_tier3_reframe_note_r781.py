#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r781 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r737_spotcheck16.tsv (batch15, 5 keep_reframe cases).
Spec: r771 bounded queue 档1→档3→档2. r772 档1 done. r773-r780 档3 batch9-14 done (reframe_note 32→93).
本轮 r781 档3 batch15 (r737 spotcheck16, 5 cases). reframe_note 93→98.

reframe_note text = spotcheck16 per_case_reasoning + cases/B trace_source(user@host) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False, round-trip identical 验过.

Driver 分类 (per per_case_reasoning, spotcheck16 5 keep_reframe of 12):
  - portability + debug-Q&A/optimization->produce-tool 优化器: 1 case (ProbeTrim, ynbai 诊断仿真慢+优化 probe 给答案->写 probe_trim.py 真跑 FineSim full/trimmed 对比)
  - portability + how-to/design->produce-tool 验证器: 1 case (DivSelDuty, wnyu 求分频器方案->写 div_sel_verify.py 真跑 HSPICE 测 freq/duty)
  - portability + retrieval/Q&A->produce-tool 查找器: 1 case (LvPmosVgVs, mengfeiz 找清单->写 lvpmos_vgvs_find.py 真跑 HSPICE 解析给清单)
  - portability + debug-Q&A->produce-tool 诊断器: 1 case (LvlshftBsubDiag, e0025768 分析原因->写 lvlshft_bsub_diag.py 诊断器+report.json, L1 不启动 HSPICE)
  - portability + analysis/Q&A->produce-tool 表征器: 1 case (NmosAgeChar, jasonw 分析 aging 数据->写 aging_char.py 生成网表+真跑+解析+report.json)
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-ProbeTrim-001":
        "PrimeSim fullchip 瞬态签核 .probe 优化器->produce-tool (portability+debug-Q&A/optimization->produce-tool 优化器 reframe, §4 有牙必要, r737 spotcheck batch15): 用户 ynbai@hfhds206 用 PrimeSim 跑 DRAM fullchip 瞬态签核, 读 si.out 诊断仿真慢(6.7h/25h-CPU)+对比 0901 快 vs 0915 慢+限制 .probe 把 probed signals 8.44M->4.19M(输出准备 312s->67s)而 .measure 保持(debug-Q&A/optimization 诊断+优化给答案), agent 在 trace 读 si.out 诊断+调 .probe(文本答案)未产出结构化优化脚本; A 不可行原因=真实 PrimeSim fullchip 仿真环境+si.out 生产日志 SUT 沙盒不可达 -> 用自包含合成 FineSim full/trimmed deck 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=debug-Q&A/optimization(诊断+优化给答案), case 收敛为 produce-tool(写 probe_trim.py 真跑 FineSim full vs trimmed 对比+report.json, method=='finesim_run')给 check() 牙(§4.2 subprocess 跑候选 python 真跑 FineSim + §4.1 hidden-B cross-input guard A full.n_probed=47 vs B=74+measure 保持一致 + §4.9 防硬编/防 print-expected); 重构为产 probe_trim.py+report.json; check.py 14 断言验 report.method==finesim_run+B full tpd/vout 等于金标准+B trimmed n_probed<B full+measure 保持+hidden-B cross-input guard 使纯 debug-Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-DivSelDuty-001":
        "DDR4 PLL 3-bit 可编程分频器验证器->produce-tool (portability+how-to/design->produce-tool 验证器 reframe, §4 有牙必要, r737 spotcheck batch15): 用户 wnyu@hfeg0plg06 原话「我想用比特位来控制它的选取…1/2/4/8/16/32，要这些分频并且duty为50%，3bit来控制，001 为1，010=2 ，......101=16 110=32，看看需要怎么改下电路」(how-to/design 求方案), agent 在 trace 帮搭 mx2 stdcell 6 选 1 mux+sweep testbench 遍历 sel_code 测 DIV8/DIV16 频率与占空比(方案+testbench)未产出结构化验证脚本; A 不可行原因=真实 foundry DFFRQ+stdcell mux 不可用+生产 netlist SUT 沙盒不可达 -> 用自包含合成 DIVCHAIN 6 抽头+SEL6TO1 6 选 1 行为级 deck 资产保留真实任务结构(asset_fidelity=synth_deck 已标); trace 用户=how-to/design(「看看需要怎么改下电路」= 求方案), case 收敛为 produce-tool(写 div_sel_verify.py 验证器真跑 HSPICE 测 6 sel_code 的 freq/duty+div_sel_report.json)给 check() 牙(§4.2 subprocess 跑候选 python 真跑 HSPICE + out_sel3.mt0 存在+freq ±0.5% + §4.1 hidden-B cross-input guard freq[sel=1]≈clk_B≠clk_A + §4.9 防硬编/防 print-expected); 重构为产 div_sel_verify.py+div_sel_report.json; check.py 10 断言验 6 results 恰好+sel_code/divide_ratio/freq_hz/duty_pct/converged 五键+HSPICE 真跑+hidden-B cross-input guard 使纯 how-to/design 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-LvPmosVgVs-001":
        "CXMT DDGOA fullchip lv/lvio PMOS Vg>Vs 查找器->produce-tool (portability+retrieval/Q&A->produce-tool 查找器 reframe, §4 有牙必要, r737 spotcheck batch15): 用户 mengfeiz@hfeg0pkn004 原话「该文件夹里的control文件是仿真的完整.sp文件…你现在需要帮我在里面找一下有没有lv和lvio类型的pmos，它们的Vg>Vs的，把这样的pmos全部找出来，给我它们在fullchip里的完整的hierachiy路径，给我清单」(retrieval/Q&A 找清单), agent 在 trace 用 HSPICE 参数条件求值 rail 电压+flat instMap+railMap 解析 46 MOS 的 vgs, 过滤满足条件的 PMOS 给 fullchip 路径清单(文本答案)未产出结构化查找脚本; A 不可行原因=真实 foundry G4B netlist+control.sp 生产文件 SUT 沙盒不可达 -> 用自包含合成 level-1 MOS corner.lib+DDGOA 风格层级 deck 资产保留真实任务结构(asset_fidelity=synth_deck 已标); trace 用户=retrieval/Q&A(「找…给我清单」= 查找给答案), case 收敛为 produce-tool(写 lvpmos_vgvs_find.py 查找器真跑 HSPICE 求 rail 电压+解析 mosfets 块+过滤 lv/lvio PMOS 且 vgs>tol+给 fullchip hierarchy 路径+result_A.json)给 check() 牙(§4.2 subprocess 跑候选 python 真跑 HSPICE + .lis job concluded+mosfets 块 + §4.1 hidden-B cross-input guard A count=8 路径 vs B count=1 路径不同 + §4.9 防硬编+类型陷阱排非 lv PMOS+极性陷阱排 NMOS+偏置陷阱 vgs>tol); 重构为产 lvpmos_vgvs_find.py+result_A.json; check.py 14 断言验 hidden-B cross-input guard+A count=8+类型/极性/偏置陷阱+HSPICE 真跑使纯 retrieval/Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-LvlshftBsubDiag-001":
        "LP5 level-shifter bsub 执行节点 hspice 缺失诊断器->produce-tool (portability+debug-Q&A->produce-tool 诊断器 reframe, §4 有牙必要, r737 spotcheck batch15): 用户 e0025768@hfeg0plg49 原话「帮我分析一下原因」(debug-Q&A 找根因, 报错 merge.py 未找到匹配 CSV), agent 在 trace 读 run_4.sh/bjobs/run_log/sim 目录/merge.py/.sp 定位三层链条: 根因=bsub 提交的 38 个 hspice 作业在执行节点 hfeg0pjn088 上 exit1/CPU0.0(裸 hspice 不在执行节点 PATH, module load 只影响提交节点)+次因=check_series_errors 假阳性+表现=merge.py 找不到 CSV(文本答案)未产出结构化诊断脚本; A 不可行原因=真实 run_4.sh/bjobs_log/run_log/sim_dir_listing/merge.py/sp_sample 生产文件 SUT 沙盒不可达 -> 用自包含合成 trace 场景快照资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=debug-Q&A(「帮我分析一下原因」= 诊断给答案), case 收敛为 produce-tool(写 lvlshft_bsub_diag.py 诊断器+diagnosis_report.json, 解析 root_cause/failed_jobs_count/exit_codes/exec_node/check_series_errors_false_positive/fix)给 check() 牙(§4.2 subprocess 跑候选 python 静态分析日志文本, L1 不启动 HSPICE + §4.1 hidden-B cross-input guard B failed_jobs=24 vs A 38+B exec_node=hfeg0pjn077 vs A 088 + §4.9 防硬编+3 次重跑确定性+不把表象当根因); 重构为产 lvlshft_bsub_diag.py+diagnosis_report.json; check.py 17 断言验 root_cause==hspice_not_on_exec_node+failed_jobs_count==B 24+exit_codes+exec_node+check_series_errors 假阳性+hidden-B cross-input guard 使纯 debug-Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-NmosAgeChar-001":
        "NMOS nlvt aging 表征器->produce-tool (portability+analysis/Q&A->produce-tool 表征器 reframe, §4 有牙必要, r737 spotcheck batch15): 用户 jasonw@hfeg0plg55 原话「分析下刚才运行的aging仿真数据」(analysis/Q&A 分析给答案, 背景 125C/TT+nrvt_age_tt.sp+.ms0/.ms1/.ms2), agent 在 trace 解析 .ms0/.ms1/.ms2 $DATA1 提取 Vtlin(52.74mV)/Idlin(53.49uA)/Idsat(342.9uA) 算每微米 Ion/Ilin 与驱动比(文本答案)未产出结构化表征脚本; A 不可行原因=真实 foundry HL22 aging PDK+nrvt_age_tt.sp 生产文件 SUT 沙盒不可达 -> 用自包含合成 level-1 NMOS aging deck 资产保留真实任务结构(asset_fidelity=synth_deck 已标); trace 用户=analysis/Q&A(「分析下…数据」= 分析给答案), case 收敛为 produce-tool(写 aging_char.py 表征工具生成网表+真跑 HSPICE .meas dc+解析 .ms $DATA1+算 Ion/Idlin 每微米+驱动比+char_report_A.json)给 check() 牙(§4.2 subprocess 跑候选 python 真跑 HSPICE + .lis/.ms 存在 + §4.1 hidden-B cross-input guard vtlin_B≠A+|idsat_B|≠A + §4.9 防硬编/防 print-expected+内部一致性 Ion=|Idsat|/W); 重构为产 aging_char.py+char_report_A.json; check.py 17 断言验 vtlin/idlin/idsat/w/l/ion_a_per_m/ilin_a_per_m/idsat+HSPICE 真跑+hidden-B cross-input guard+内部一致性使纯 analysis/Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-ProbeTrim-001": "portability+debug-Q&A/optimization->produce-tool 优化器",
    "EDA-Eval-DesignFlow-DivSelDuty-001": "portability+how-to/design->produce-tool 验证器",
    "EDA-Eval-DesignFlow-LvPmosVgVs-001": "portability+retrieval/Q&A->produce-tool 查找器",
    "EDA-Eval-DesignFlow-LvlshftBsubDiag-001": "portability+debug-Q&A->produce-tool 诊断器",
    "EDA-Eval-DesignFlow-NmosAgeChar-001": "portability+analysis/Q&A->produce-tool 表征器",
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
    print(f"=== r781 batch15 reframe_note apply: {len(REFRAME_NOTES)} cases ===")
    counts = {"OK": 0, "ALREADY": 0, "MISSING": 0}
    for cid, note in REFRAME_NOTES.items():
        status, info = apply_one(cid, note)
        counts[status] = counts.get(status, 0) + 1
        print(f"  [{status}] {info} (driver={DRIVER.get(cid,'?')})")
    print(f"\nSummary: OK={counts['OK']} ALREADY={counts['ALREADY']} MISSING={counts['MISSING']}")
    print(f"Expected reframe_note count after apply: 93 + {counts['OK']} = {93 + counts['OK']}")


if __name__ == "__main__":
    main()
