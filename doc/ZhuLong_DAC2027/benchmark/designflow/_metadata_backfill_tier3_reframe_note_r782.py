#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r782 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r738_spotcheck17.tsv (batch16, 4 keep_reframe of 12 cases).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r781 档3 batch9-15 done (reframe_note 32->98).
本轮 r782 档3 batch16 (r738 spotcheck17, 4 cases). reframe_note 98->102.

reframe_note text = spotcheck17 per_case_reasoning + cases/B trace_source(user@host) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False, round-trip identical 验过.

Driver 分类 (per per_case_reasoning, spotcheck17 4 keep_reframe of 12):
  - portability + analysis/Q&A->produce-tool 查找器: 1 case (CgMeetExactlyMissWalk, ericw@hfhds201 总结 cg_t meet_exactly 未命中 bin -> 写 find_cg_t_meet_exactly_miss.py 真跑产 out.json, L1)
  - portability + analysis/Q&A->produce-tool 元数据提取器: 1 case (CovBinMetaExtract, ericw@hfhds201 分析 cg_t covergroup bin -> 写 extract_covergroup_meta.py 真跑产 out.json, L1)
  - portability + analysis/Q&A->produce-tool 提取器: 1 case (MeasExtractCornerTrace, rongtaoy@hfeg0pkn001 DDGOA DDR6 column-timing FineSim 多 corner .meas 提取 -> 写 meas_extract_corner_trace.py 真跑 FineSim 产 report, L2)
  - portability + debug-Q&A->produce-tool 诊断器: 1 case (DQSEHFlagNoEffectDiag, tongfanl@hfhds201 DQSEH flag 无效诊断 -> 写 diag.py 真跑产 out.json, L1)

ericw cluster 2/4 (同 DDR5 drcpa aicov 覆盖率域, 不同 session).
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-CgMeetExactlyMissWalk-001":
        "DDR5 drcpa aicov 覆盖率 cg_t meet_exactly 未命中 bin 查找器->produce-tool (portability+analysis/Q&A->produce-tool 查找器 reframe, §4 有牙必要, r738 spotcheck batch16): 用户 ericw@hfhds201 原话「总结里面cg_t 没有命中meet_exactly的bin」(analysis/Q&A 分析给答案, table1.json 1079 covergroup + cg_t title 过滤 + meet_exactly bin All Cov + 134 条未命中 + table1->table2->table3 层级下钻), agent 在 trace 读 json 收集未命中清单(文本答案)未产出结构化查找脚本; A 不可行原因=真实 drcpa aicov cov_work json dump 生产文件 SUT 沙盒不可达 -> 用真实场景便携化的 fixture json 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=analysis/Q&A(「总结...没有命中的 bin」= 分析给答案), case 收敛为 produce-tool(写 find_cg_t_meet_exactly_miss.py 查找器真跑产 out.json)给 check() 牙(§4.1 hidden-B cross-input guard B cg_t 集合 set 相等≠A + §4.9 防硬编/防 print-expected + 挡把 HIT 误报为 miss + 挡非 cg_t covergroup + 确定性 3 重跑); 重构为产 find_cg_t_meet_exactly_miss.py+out.json; check.py 14 断言验 hidden-B cross-input guard+HIT 误报挡+非 cg_t 挡+确定性使纯 analysis/Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-CovBinMetaExtract-001":
        "DDR5 drcpa aicov 覆盖率 cg_t covergroup 元数据提取器->produce-tool (portability+analysis/Q&A->produce-tool 元数据提取器 reframe, §4 有牙必要, r738 spotcheck batch16): 用户 ericw@hfhds201 原话「分析cg_t_PREsb_TO_MPC_ZQCal_Start_1nCK_Table_85这个bin」(analysis/Q&A 分析给答案, constraint_timing_coverage.sv 22271 行 + 目标 covergroup 21635-21661 + /*name:event:source*/ 元数据头 + start_cmd=PREsb/end_cmd=MPC_ZQCal_Start/source=Table_85), agent 在 trace 读 sv 提取元数据(文本答案)未产出结构化提取脚本; A 不可行原因=真实 constraint_timing_coverage.sv 生产文件 SUT 沙盒不可达 -> 用真实场景便携化的 fixture sv 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=analysis/Q&A(「分析...这个 bin」= 分析给答案), case 收敛为 produce-tool(写 extract_covergroup_meta.py 提取器真跑产 out.json)给 check() 牙(§4.1 hidden-B cross-input guard B event.start_cmd=ACT≠A PREsb+end_cmd=RD≠A MPC + §4.9 防硬编/防 print-expected + 元数据字段齐全 + 确定性); 重构为产 extract_covergroup_meta.py+out.json; check.py 16 断言验 hidden-B cross-input guard+元数据字段齐全+确定性使纯 analysis/Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-MeasExtractCornerTrace-001":
        "DDGOA DDR6 column-timing FineSim 多 corner .meas 提取器->produce-tool (portability+analysis/Q&A->produce-tool 提取器 reframe, §4 有牙必要, r738 spotcheck batch16): 用户 rongtaoy@hfeg0pkn001 对 DDGOA DDR6 column-timing FineSim 仿真体系做实物取证+Fail 溯源(analysis/Q&A 分析给答案, .alter 多 corner + .meas tran trig_targ/when/max + .tran + .include + res/*.mt0 $DATA1 解析 + corner 标签 + Fail 性质分类系统性/单角), agent 在 trace 只读文件做提取+溯源(文本答案)未产出结构化提取脚本; A 不可行原因=真实 foundry PDK 只读证不可移植 + 生产 .sp/.mt0 SUT 沙盒不可达 -> 用自包含合成 inv_chain deck 资产保留真实任务结构(asset_fidelity=synth_deck 已标); trace 用户=analysis/Q&A(实物取证+Fail 溯源= 分析给答案), case 收敛为 produce-tool(写 meas_extract_corner_trace.py 提取器真跑 FineSim 产 report)给 check() 牙(§4.2 真跑 FineSim finesim_ran=True+.mtN>=2+log banner+Successfully Completed + §4.1 hidden-B cross-input guard B n_corners≠A + §4.9 防硬编/防 print-expected + meas_statements 含 .meas/.tran/.include 带行号 + 类型分类); 重构为产 meas_extract_corner_trace.py+report; check.py 14 断言验 FineSim 真跑+hidden-B cross-input guard+meas_statements 带行号+类型分类使纯 analysis/Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-DQSEHFlagNoEffectDiag-001":
        "DDR6 DSCQA vecgen DQSEH flag 无效诊断器->produce-tool (portability+debug-Q&A->produce-tool 诊断器 reframe, §4 有牙必要, r738 spotcheck batch16): 用户 tongfanl@hfhds201 原话「运行脚本...无论有没有定义 -d DQSEH ...都是PSD0出DQ543、PSD1出DQ210。这是为啥？」(debug-Q&A 诊断给答案, ## -d DQSEH 注释 + DQSELH/DQSEH 名错配 + undefined else 分支 + X1P6/SC0 + DQ543/DQ210), agent 在 trace 读代码诊断双根因(文本答案)未产出结构化诊断脚本; A 不可行原因=真实 vecgen 代码生产文件 SUT 沙盒不可达 -> 用真实场景便携化的合成 macro/config fixture 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=debug-Q&A(「这是为啥？」= 诊断给答案), case 收敛为 produce-tool(写 diag.py 诊断器真跑产 out.json)给 check() 牙(§4.1 hidden-B cross-input guard B flag_passed=True≠A False+B cli_macro=WRSEQ≠A DQSEH+B code_macro=WRSEQ_H≠A DQSELH+B config X2P3/SC1≠A X1P6/SC0+B psd0=DQ3210≠A DQ543 + §4.9 防硬编/防 print-expected); 重构为产 diag.py+out.json; check.py 14 断言验 hidden-B cross-input guard 5 维全区分+防硬编使纯 debug-Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-CgMeetExactlyMissWalk-001": "portability+analysis/Q&A->produce-tool 查找器",
    "EDA-Eval-DesignFlow-CovBinMetaExtract-001": "portability+analysis/Q&A->produce-tool 元数据提取器",
    "EDA-Eval-DesignFlow-MeasExtractCornerTrace-001": "portability+analysis/Q&A->produce-tool 提取器",
    "EDA-Eval-DesignFlow-DQSEHFlagNoEffectDiag-001": "portability+debug-Q&A->produce-tool 诊断器",
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
    print(f"=== r782 batch16 reframe_note apply: {len(REFRAME_NOTES)} cases ===")
    counts = {"OK": 0, "ALREADY": 0, "MISSING": 0}
    for cid, note in REFRAME_NOTES.items():
        status, info = apply_one(cid, note)
        counts[status] = counts.get(status, 0) + 1
        print(f"  [{status}] {info} (driver={DRIVER.get(cid,'?')})")
    print(f"\nSummary: OK={counts['OK']} ALREADY={counts['ALREADY']} MISSING={counts['MISSING']}")
    print(f"Expected reframe_note count after apply: 98 + {counts['OK']} = {98 + counts['OK']}")


if __name__ == "__main__":
    main()
