#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r795 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r751_spotcheck30.tsv (batch29, 5/12 keep_reframe cases 待 apply;
        VSplit + PwlStimTransform + SramIreadGen + ZqCodeLinExtract + SlicerFbTimeOpt + SwitchTbGen +
        PlatInvsThick = 7 keep_faithful 无 reframe_note OK).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r794 档3 batch9-28 done (reframe_note 32->211).
本轮 r795 档3 batch29 (r751 spotcheck30, 5 cases 待 apply). reframe_note 211->216.

reframe_note text = spotcheck30 per_case_reasoning + cases/B trace_source(user@host/session/mc) + test_rationale k_check (header).
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False.

Driver 分类 (per per_case_reasoning, spotcheck30 12 case: 5 keep_reframe + 7 keep_faithful):
  - Q&A-driver (how-to/explain/debug/analysis Q&A -> produce-tool 给 check 牙): 4 cases
    VwlpPumpReport (ryanren, analysis-Q&A 电路+波形分析产报告 -> produce-tool report generator w/ HSPICE teeth) /
    IfElsePairFix (jianilu, debug-Q&A 讲解 .if/.endif 不配对报错 -> produce-tool fix script, check 真跑 hspice 验修复) /
    SramTailorPlanClassify (e0044979, debug-Q&A 裁剪报错 -> produce-tool plan classifier) /
    SimCapLisParse (yazhuok, Q&A-how-to + produce-text 混合 -> produce-tool sim result parser)
  - portability-driver (produce-action 不可便携多步 -> 子技能提取): 1 case
    StdcellDeckParamModify (chapinc, produce-action 多步 web app+改 deck+LSF+hspice+解析 mt0+分图
                             -> 子技能 modify_deck.py 提取, A 档保留 verbatim 7 要求)

spotcheck30 关键发现 (本轮 reframe_note scope 限定不修 layer/level/asset_fidelity, 仅在 note 文本标注 layer bug 待 @A 档1 补 sweep):
  - layer 缺标(None)应补 L2 1/5: VwlpPumpReport (check 真跑 HSPICE binary `subprocess.run([HSPICE,"-i",...])`,
    非 r788-r794 主导的「缺标应补 L1」型; 本批缺标型反向=应补 L2, 因 check 验证路径启动 EDA 二进制)
  - layer=L1 ✓ 已正确 2/5: StdcellDeckParamModify / SramTailorPlanClassify / SimCapLisParse (check 仅 subprocess 跑 sys.executable 解析文本)
  - layer=L2 ✓ 已正确 1/5: IfElsePairFix (check _find_hspice + 真跑 hspice 验 .if/.endif 修复)
  - **本批 0 例 layer 误分类**(对照 r790/r785 有 L2->应 L1 误标型), 1 例缺标应补 L2(非 L1) 是本批新形态
  - **B 域累计 layer 漏网 58 例**(r794 累计 57 + 本批 1: 47 缺标 + 11 误分类),
    r772 档1 level->layer normalize 漏网之鱼 (cases/B has_layer 303, 仍缺 92)
  - asset_fidelity 缺标 3/5(VwlpPumpReport=synth_deck ✓ / SramTailorPlanClassify=synth_deck ✓ 已标; StdcellDeckParamModify/IfElsePairFix/SimCapLisParse 缺标), 待 @A apply 档2
  - k_check metadata 缺标 3/5(VwlpPumpReport=14 ✓ / SramTailorPlanClassify=14 ✓ 已标; StdcellDeckParamModify=12/IfElsePairFix=12/SimCapLisParse=15 metadata 无 k_check 字段, 待 @A apply 档1 补 sweep)
  - 本批 0 例 pre-existing header != circled-mark count (5/5 header==circled 一致: 14/12/12/14/15)
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-VwlpPumpReport-001":
        "Vwlp 字线开关泵核 6 节电路+波形分析报告生成器->produce-tool (Q&A analysis-Q&A->produce-tool report generator w/ HSPICE teeth reframe, §4 有牙必要, r751 spotcheck batch29): 用户 ryanren@hfeg0pfn120 (sess 1793586031652_f2xzx mc156), U0 verbatim「/proj/dscqa/.../test_lv_new.fsdb 的 HSPICE 波形 + Ryantext 库 Vwlp_switchcore_test 电路，手写了一份 6 节电路报告」(analysis-Q&A 分析电路+波形产报告); trace 金标准 156 msgs Vwlp 字线开关泵核改进(PASS 信号控制直导通支路降阻抗), net2 0.08V->2.95V, 6 节报告(电路层次/子电路/对比/波形时序/仿真条件/改进总结), agent 手写文本分析报告; A 不可行原因=纯 analysis-Q&A(分析电路+波形给答案)无 runnable artifact 无 check 牙 -> case 抽取「Vwlp pump 6 节报告生成器(vwlp_pump_report.py 真跑产 report.json)」子技能, A 档 verbatim 合规(ryanren 原话逐字含真实 test_lv_new.fsdb 路径+Ryantext 库名+Vwlp_switchcore_test 电路名), reframe 由 Q&A-driver 非配额驱动; asset_fidelity=synth_deck ✓ 已标(A=trace-verbatim 电路结构 + B=synth 不同 net/管子尺寸); trace 用户=analysis-Q&A(分析给答案), case 收敛为 produce-tool(写 vwlp_pump_report.py 真跑产 report.json) 给 check() 牙(§4.1 hidden-B cross-input guard B net/管子尺寸非 A + §4.5 幂等, check 不止跑候选 python, **真启动 HSPICE binary `subprocess.run([HSPICE,\"-i\",dp,\"-o\",...])` 验 .lis 产出与 hspice_ran==True**, 击破 no-sim/print-expected stub, 是 §4.2 真跑候选); 重构为产 Vwlp 6 节电路+波形分析报告; check.py 14 断言(a-n)验候选 vwlp_pump_report.py+report.json+hspice .lis => 收敛为 produce-tool report generator (w/ HSPICE teeth) 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: **layer 缺标(None)应补 L2**(check 真跑 HSPICE binary, 非 r788-r794 主导的「缺标应补 L1」型, 本批新形态), level 缺标应 L2, k_check=14 ✓ 已标, asset_fidelity=synth_deck ✓ 已标, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-StdcellDeckParamModify-001":
        "stdcell INV 尺寸选取 deck 参数修改器->produce-tool (portability produce-action 不可便携多步->子技能提取 reframe, §4 有牙必要, r751 spotcheck batch29): 用户 chapinc@hfeg0pkn002 (sess 1793596317022_34b72 mc14), U0 verbatim「读取 netlist_sp 文件夹...做一个 stdcell 尺寸选取的 HTML 网页...以网表激励为模板自动修改参数并自动提交仿真...选取 L W PNratio」(produce-action 多步: 建 web app+改 deck+LSF 提交 hspice+解析 mt0+分图); trace 金标准 14 msgs stdcell INV 尺寸选取 web 应用, modify_deck 改 .para(L/W/PNratio/corner)+.tran sweep, LSF 提交, mt0 解析 5 corner 分图; A 不可行原因=produce-action 多步(web app 不可便携+LSF 队列+mt0 解析+分图全链路, 单 case 无法覆盖完整 web app) -> case 抽取「.para+.tran sweep deck 修改器(modify_deck.py 真跑产改后 .sp)」子技能, A 档 verbatim 合规(chapinc 原话逐字含 7 要求 + netlist_sp 路径), reframe 由 portability-driver(多步不可便携->子技能提取)非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(.sp 模板结构)+B=synth(待 @A apply 档2); trace 用户=produce-action(建 web+改 deck+提交+解析), case 收敛为 produce-tool(写 modify_deck.py CLI 三参真跑产改后 .sp) 给 check() 牙(§4.1 hidden-B cross-input guard B PN_ratio=1.5/Wn_basic=200 非 A + sweep 行不同反硬编码 + §4.5 幂等, check 仅 subprocess 跑 sys.executable[modify_deck.py] 解析/产 .sp 文本, 不启动 hspice/LSF; LSF 提交+mt0 解析+分图作为不可便携多步被剥离); 重构为产 .para+.tran sweep deck 修改器; check.py 12 断言验候选 modify_deck.py+改后 .sp => 收敛为 produce-tool deck modifier (子技能提取) 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check subprocess 跑候选 python 解析/产 .sp 文本, 不启动 hspice/LSF), level 缺标应 L1, k_check 缺标应 12(metadata 未标, test_rationale header=12), k_rationale 缺标应 12, asset_fidelity 缺标, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-IfElsePairFix-001":
        "FineSim .if/.endif 不配对报错修复器->produce-tool (Q&A debug-Q&A 讲解报错->produce-tool fix script w/ HSPICE teeth reframe, §4 有牙必要, r751 spotcheck batch29): 用户 jianilu@hfeg0pkn004 (sess 1793691610698_fqs53 mc46), U0 verbatim「ERROR! if-else conditional statements not paired (Pattern_Power.sp:2) 讲解报错」(debug-Q&A 讲解报错); trace 金标准 46 msgs FineSim 报 .if/.endif 不配对, Pattern_Power.sp 是 DRAM power 参数表(多段 .if/.elseif/.else/.endif 嵌套设 pvcc/ptemp 范围 .param), agent 统计 .if/.endif 计数+检索 finesim 手册+给配对语义讲解(msg#33 文本答案); A 不可行原因=纯 debug-Q&A(「讲解报错」=诊断+讲解给答案)无 runnable artifact 无 check 牙 -> case 抽取「.if/.endif 配对修复器(fix_ifelse_pairing.py 真跑产修复后 .sp)」子技能, A 档 verbatim 合规(jianilu 原话逐字含报错原文+Pattern_Power.sp:2 行号), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(.sp 条件块结构)+B=synth(待 @A apply 档2); trace 用户=debug-Q&A(讲解报错), case 收敛为 produce-tool(写 fix_ifelse_pairing.py 真跑产修复后 .sp) 给 check() 牙(§4.1 hidden-B cross-input guard B broken .sp 非 A + §4.5 幂等, check **真启动 HSPICE binary `_find_hspice()+subprocess.run([hspice,\"-i\",out_A.sp,...])` 验 .lis 含 job concluded + 原始 broken A 直跑 hspice 必失败**(job aborted 证明 break 真实/修复必要), 击破 print-fake/不修复 stub, 是 §4.2 真跑候选 + §4.9 退化提交回归); 重构为产 .if/.endif 配对修复器; check.py 12 断言(a-l)验候选 fix_ifelse_pairing.py+修复后 out_A.sp+hspice .lis => 收敛为 produce-tool fix script (w/ HSPICE teeth) 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L2 ✓ 已正确(check _find_hspice + 真跑 hspice binary 验修复, 启动 EDA 二进制), level 缺标应 L2, k_check 缺标应 12(metadata 未标, test_rationale header=12), k_rationale 缺标应 12, asset_fidelity 缺标, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-SramTailorPlanClassify-001":
        "1M×72 SRAM DSPF 裁剪 plan_iface 分类器->produce-tool (Q&A debug-Q&A 裁剪报错->produce-tool plan classifier reframe, §4 有牙必要, r751 spotcheck batch29): 用户 e0044979@hfeg0pkn001 (sess 1793771550244_nlf6u mc146), U#1 verbatim「我跑脚本裁剪电路，碰到错误 ERROR: detect: testbench needs exactly one direct .include defining the conly top」(debug-Q&A 裁剪报错); trace 金标准 146 msgs 1M×72 SRAM(顶层 CXN4HC2PS1024X72M4B4C1R1W1BW1RE1_FS, 8T bitcell) FineSim 仿真前 DSPF 裁剪调试, tailor/plan_iface.py 按 row_action 分 prune/conly/full_rc 三类, prune cell 若 status 非 verified 被 rescue 回 full_rc 致 73408 cell 未裁; A 不可行原因=纯 debug-Q&A(裁剪报错诊断)无 runnable artifact 无 check 牙 -> case 抽取「SRAM tailor plan 分类器(sram_tailor_plan_classify.py 真跑产 summary)」子技能, A 档 verbatim 合规(e0044979 原话逐字含报错原文+顶层 cell 名), reframe 由 Q&A-driver 非配额驱动; asset_fidelity=synth_deck ✓ 已标(A=trace-verbatim cell 结构 + B=synth 不同 cell 数/size); trace 用户=debug-Q&A(裁剪报错诊断), case 收敛为 produce-tool(写 sram_tailor_plan_classify.py 真跑产 summary) 给 check() 牙(§4.1 hidden-B cross-input guard B1 total_cells=80/B2 total_cells=60 非 A, B2 只接受 pin_mismatch:S 反硬编码 + §4.5 幂等, check 仅 subprocess 跑 sys.executable[script] 解析 cell_map+device_map+rules 文本分类, 不启动 FineSim/tailor); 重构为产 SRAM tailor plan 分类器; check.py 14 断言(a-n)验候选 sram_tailor_plan_classify.py+B1/B2 summary => 收敛为 produce-tool plan classifier 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check subprocess 跑候选 python 解析文本分类, 不启动 FineSim/tailor), level 缺标应 L1, k_check=14 ✓ 已标, asset_fidelity=synth_deck ✓ 已标, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-SimCapLisParse-001":
        "DRAM 单管 AC 电容扫描仿真结果 .lis/.mt0 解析器->produce-tool (Q&A Q&A-how-to+produce-text 混合->produce-tool sim result parser reframe, §4 有牙必要, r751 spotcheck batch29): 用户 yazhuok@hfeg0pahpc501 (sess 1793882229682_mk098 mc21), U#1 verbatim「我用这个单管仿真激励跑完之后的结果在 result_wibls/ 文件夹中，我该如何阅读以及查看我的结果，请把我的结果整理成文本的形式」+U#2「把 result_wobls 也一并解析，二者都生成我可以直接复制的文档」(Q&A-how-to + produce-text 混合); trace 金标准 21 msgs DRDXQ 单管 AC 电容扫描仿真(model_check_DRDXQ.sp, ntk_hwl_m, .DATA 11 点 vbl/vnc/vwl 扫描, AC 100kHz 测 Cgg/Cgd/Cgs/Csg), agent 写 parse_wibls.py 后泛化 parse_wobls; A 不可行原因=Q&A-how-to+produce-text(「我该如何阅读...整理成文本」=讲解+产文本)无 runnable artifact 无 check 牙 -> case 抽取「sim .lis/.mt0 电容扫描解析器(sim_cap_lis_parse.py 真跑产 report.txt+csv)」子技能, A 档 verbatim 合规(yazhuok 两轮原话逐字+result_wibls/result_wobls 路径+model_check_DRDXQ.sp), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(.sp/.lis/.mt0 量测结构)+B=synth(待 @A apply 档2); trace 用户=Q&A-how-to+produce-text(讲解+产文本), case 收敛为 produce-tool(写 sim_cap_lis_parse.py 真跑产 report.txt+csv) 给 check() 牙(§4.1 hidden-B cross-input guard B1/B2 .DATA 索引/电容值非 A + §4.5 幂等, check 仅 subprocess 跑 sys.executable[script] 解析 .lis/.mt0 文本产 csv, 反 nonexistent_data 路径容错, 不启动 hspice/finesim); 重构为产 sim 电容扫描解析器; check.py 15 断言(a-o)验候选 sim_cap_lis_parse.py+B1/B2 report.txt+csv => 收敛为 produce-tool sim result parser 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check subprocess 跑候选 python 解析 .lis/.mt0 文本产 csv, 不启动 hspice/finesim), level 缺标应 L1, k_check 缺标应 15(metadata 未标, test_rationale header=15), k_rationale 缺标应 15, asset_fidelity 缺标, metadata bug 待 @A apply 档1/档2 补 sweep。",
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
