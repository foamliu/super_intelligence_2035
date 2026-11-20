#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r799 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r755_spotcheck34.tsv (batch33, 6/12 keep_reframe cases 待 apply;
        6 keep_faithful = 无 reframe_note OK).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r798 档3 batch9-32 done (reframe_note 32->228).
本轮 r799 档3 batch33 (r755 spotcheck34, 6 cases 待 apply). reframe_note 228->234.

reframe_note text = spotcheck34 per_case_reasoning + cases/B trace_source(user@host/session/mc) + test_rationale k_check (header).

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False.

Driver 分类 (per per_case_reasoning, spotcheck34 12 case: 6 keep_reframe + 6 keep_faithful):
  - Q&A-driver (how-to/why/debug/analysis Q&A -> produce-tool 给 check 牙): 4 cases (67% Q&A-driver)
    FinesimVhDiagGuide (phoebeli, Q&A-how-to+debug -> produce-guide-tool) /
    SimlibMatchAnalyze (e0039602, Q&A-analysis -> produce-analyzer-tool) /
    SrefOscTranFlowAnalyze (junweix, Q&A-analysis -> produce-flow-analyzer-tool) /
    SnmSquareValidator (e0030760, Q&A-debug -> produce-validator-tool)
  - portability-driver (foundry PDK / FineSim model 不可便携 -> HSPICE+portable synth deck): 2 cases (33% portability)
    StrongarmFomSweep (jiangbaol, portability:FineSim+G4B foundry model -> HSPICE+level-1 portable model) /
    PlatMosThinIdsatIoffSweep (hairuizh, portability:5 foundry PDK -> portable synthesized decks + HSPICE)
  - harness-driver: 0 cases
  - sub-skill-driver: 0 cases (本轮 reframe 集无 sub-skill 抽取)

spotcheck34 关键发现 (本轮 reframe_note scope 限定不修 layer/level/asset_fidelity/k_check, 仅在 note 文本标注 layer bug 待 @A 档1 补 sweep):
  - layer 缺标(None)应补 L1 2/6 (SimlibMatchAnalyze + SrefOscTranFlowAnalyze, check 仅 subprocess python 解析文本)
  - layer 缺标(None)应补 L2 2/6 (StrongarmFomSweep + PlatMosThinIdsatIoffSweep, check 真跑 HSPICE binary)
    -- **承接 r795 VwlpPumpReport 缺标应补 L2 反向首例**, 本批 +2 例缺标应补 L2, 即 r795-r798 累计 3 例缺标应补 L2,
       缺标值的 L1/L2 二分方差在 r799 batch33 再加强(不是孤例)
  - layer 误分类(L2 标 -> 应 L1) 1/6 (SnmSquareValidator, check 仅 subprocess python 解析 butterfly CSV, 0 EDA 二进制)
    -- 本批首例误分类 (对照 r796 batch30 1 例误分类候选 SharedLibDeployFix L1->应 L2, 本批反向 L2->应 L1)
  - layer=L1 ✓ 已正确 1/6 (FinesimVhDiagGuide, metadata 已标 L1)
  - **B 域累计 layer 漏网 63 -> 68 例** (r798 累计 63 = 49 缺标 + 11 误分类 + 3 误分类候选;
       本批 +5: 4 缺标(2 L1 + 2 L2) + 1 误分类(L2->L1) => 53 缺标 + 12 误分类 + 3 误分类候选 = 68)
  - asset_fidelity 缺标 5/6 (仅 StrongarmFomSweep/PlatMosThinIdsatIoffSweep 已标 synth_deck, 其余 4 缺标应 real-from-trace; 待 @A apply 档2)
  - k_check metadata 缺标 3/6 (SimlibMatchAnalyze 应标 32 / SrefOscTranFlowAnalyze 应标 16 / SnmSquareValidator 应标 13;
       FinesimVhDiagGuide=16 / StrongarmFomSweep=14 / PlatMosThinIdsatIoffSweep=14 已标 ✓)
  - **0 例 pre-existing header != circled-mark count** (6/6 header==circled: 16/32/16/14/14/13 ✓)
       -- 延续 r797/r798 零不符 (对照 r796 batch30 1 例 FinesimOptionExtend 12vs14)
  - level 缺标 6/6 (全 6 case level 字段缺标), track 缺标 5/6 (仅 FinesimVhDiagGuide 已标 faithful? -- 复核),
    shard 缺标 5/6 (仅 FinesimVhDiagGuide 已标 B)
  - 2 user-cluster: e0030760 SRAM SNM 三连之一 (SnmSquareValidator, 同 user 同 host pkn004) /
    hairuizh 第 3 例 (PlatMosThinIdsatIoffSweep, DRAM presim device char verb-heterogeneous, 同 host pkn001)
  - 1 WAVEVIEW-domain case in spice_sim shard? (本轮 reframe 集 0, spotcheck34 全集 RiseEdgeMarginMeas 在 keep_faithful 集, 不在本 apply)
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-FinesimVhDiagGuide-001":
        "LPDDR5X DLDO FineSim/PrimeSim MatrixRun vh 报错诊断指南生成器->produce-tool (Q&A-how-to+debug->produce-guide-tool reframe, §4 有牙必要, r755 spotcheck batch33): 用户 phoebeli@hfeg0plg96 U0 三类问题(how-to「如何在 block 网表里定义一个 pwl 电压源」+debug「ERROR! no reference ckt vh for xi_setiddampoip_111(netlist:67170)」求解决方案+网表分析), trace 金标准 91 msgs agent 逐轮给文本解答+诊断, A 不可行原因=纯 Q&A how-to+debug(「如何...」「为什么报错...」=给解答答案)无 runnable artifact 无 check 牙 -> case 抽取「finesim_vh_diag_guide_gen.py(真跑解析 netlist 文本产 JSON 诊断指南 14 顶层键)」子技能, A 档 verbatim 合规(phoebeli 原话逐字含三类问题+现场产物), reframe 由 Q&A-driver 非配额驱动; trace 用户=Q&A how-to+debug(给解答答案), case 收敛为 produce-tool(写 finesim_vh_diag_guide_gen.py 真跑解析产 JSON 诊断指南) 给 check() 牙(§4.1 hidden-B cross-input B error_count/instance/line_no/missing_cell 非 A + §4.4 zip 含脚本+py_compile+hidden B 在位未泄漏+exit0 产 JSON+3 次重跑 sha256 一致+JSON dict+14 顶层键齐全+error_count/instance/line_no/missing_cell, check 仅 subprocess 跑候选 python 解析 netlist 文本+验 JSON 结构, 无 EDA 二进制调用); 重构为产 vh 报错诊断指南生成器; check.py 16 断言验候选 finesim_vh_diag_guide_gen.py+JSON 报告 => 收敛为 produce-guide-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(metadata 已标, check 仅 subprocess 跑候选 python 解析 netlist 文本+验 JSON, 无 EDA 二进制), level 缺标应 L1, asset_fidelity 缺标应 real-from-trace, track 缺标应 faithful, shard=B ✓ 已标, k_check=16 ✓ 已标(metadata 已标, header=16 circled=16 一致), metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-SimlibMatchAnalyze-001":
        "simlib 相似 model 匹配逻辑分析器->produce-tool (Q&A-analysis->produce-analyzer-tool reframe, §4 有牙必要, r755 spotcheck batch33): 用户 e0039602@hfeg0pkn005 U0 多轮 verbatim「请你检查一下这里面这个相似model匹配的一个逻辑，并告诉我 or4GSx2 会在我们的库里匹配到哪个相似 model」+「你只通过 tb_family 的名字判断...没有用...实际代码对吧」+「那实际上可以完全不利用这个 tb_family 对吗...请你收集这个目录里 tb_family 的名字」+「or4GSx2 和 or4FSSx1 会匹配到什么...tb_family 这个文件夹完全不需要了...可把它删了?」+「把新目录里所有的族都提取出来放到...」(analysis-Q&A 检查逻辑+收集+提取), trace 金标准 57 msgs agent 分析 verilog_lib_trans_v2.3 simlib_ref_db.py 相似 model 匹配逻辑+收集族名+提取到 family_names.txt, A 不可行原因=纯 analysis-Q&A(「检查...逻辑并告诉我」=给分析答案)无 runnable artifact 无 check 牙 -> case 抽取「simlib_match_analyzer.py(真跑解析 simlib 文本产 JSON 报告, k=32 本批最高)」子技能, A 档 verbatim 合规(e0039602 原话逐字 5 轮+verilog_lib 路径), reframe 由 Q&A-driver 非配额驱动; trace 用户=analysis-Q&A(给分析答案), case 收敛为 produce-tool(写 simlib_match_analyzer.py 真跑分析产 JSON 报告) 给 check() 牙(§4.1 hidden-B cross-input B 匹配结果/族名/tb_family 非 A 的 or4GSx2/or4FSSx1 + §4.4 zip 含脚本+py_compile+可调用入口+hidden B 在位未泄漏+B 上 exit0 产 JSON+3 次重跑 sha256 一致+JSON dict+12 顶层键齐全(family_names/family_count/ref_model_count/ref_models/matching_results/matching_details/logic_explanation/tb_family_removable/...)+family_names 排序+matching_results 与 oracle 一致+tb_family_removable==true, check 仅 subprocess 跑候选 python 解析 simlib 文本+验 JSON 结构, 无 EDA 二进制调用); 重构为产 simlib 相似 model 匹配逻辑分析器; check.py 32 断言验候选 simlib_match_analyzer.py+JSON 报告(本批最高 k) => 收敛为 produce-analyzer-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标应 L1(check 仅 subprocess 跑候选 python 解析 simlib 文本+验 JSON, 无 EDA 二进制), level 缺标应 L1, k_check 缺标应 32(test_rationale header=32 circled=32 一致), asset_fidelity 缺标应 real-from-trace, shard 缺标应 B, track 缺标应 faithful, domain=characterization ✓, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-SrefOscTranFlowAnalyze-001":
        "srefosc 瞬态仿真流程分析器->produce-tool (Q&A-analysis->produce-flow-analyzer-tool reframe, §4 有牙必要, r755 spotcheck batch33): 用户 junweix@hfeg0plg76 U0 verbatim「/proj/.../srefosc/tran.sp 分析一下整个仿真的流程以及查看的信号」+「继续」(analysis-Q&A 分析仿真流程), trace 金标准 19 msgs agent 读 tran.sp(159 行 Finesim spicead 瞬态 deck)+ddgoa_wkf_sim_sr 流程, 分析仿真流程+查看信号, A 不可行原因=纯 analysis-Q&A(「分析一下...流程」=给分析答案)无 runnable artifact 无 check 牙 -> case 抽取「tran_sim_flow_analyzer.py(真跑解析 .sp deck 产 JSON 流程报告 8 section)」子技能, A 档 verbatim 合规(junweix 原话逐字含「分析一下整个仿真的流程以及查看的信号」+「继续」+tran.sp 路径), reframe 由 Q&A-driver 非配额驱动; trace 用户=analysis-Q&A(给分析答案), case 收敛为 produce-tool(写 tran_sim_flow_analyzer.py 真跑解析 deck 产 JSON 流程报告) 给 check() 牙(§4.1 hidden-B cross-input B simulator/power_domain/signals/stimulus/measure/flow_summary 非 A + §4.4 zip 含脚本+py_compile+可调用入口+hidden B 在位未泄漏+B 上 exit0 产 JSON+3 次重跑 sha256 一致+JSON dict+8 section 齐全, check 仅 subprocess 跑候选 python 解析 .sp deck 文本+验 JSON 结构, 无 EDA 二进制调用); 重构为产 srefosc 瞬态仿真流程分析器; check.py 16 断言验候选 tran_sim_flow_analyzer.py+JSON 报告 => 收敛为 produce-flow-analyzer-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标应 L1(check 仅 subprocess 跑候选 python 解析 .sp deck 文本+验 JSON, 无 EDA 二进制), level 缺标应 L1, k_check 缺标应 16(test_rationale header=16 circled=16 一致), asset_fidelity 缺标应 real-from-trace, shard 缺标应 B, track 缺标应 faithful, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-StrongarmFomSweep-001":
        "strongarm 比较器 FOM sizing sweep 优化器->produce-tool (portability:FineSim+G4B foundry model->HSPICE+level-1 portable model reframe, §4 有牙必要 + 私有资产逼出保真度降级(P-005) r392 portability-driver, r755 spotcheck batch33): 用户 jiangbaol@hfeg0pkn001 U0 verbatim「我现在需要优化一个 strongarm 比较器电路，目标是提高速度(减小比较时间 ck2q)同时降低功耗(减小偏置电流)」(produce-action 优化+sweep+FOM), trace 金标准 196 msgs agent 跑 FineSim+G4B 工艺模型 NMOS/PMOS sizing sweep+FOM 分析脚本, 目标=提速+降功耗, 用户原始意图是 produce-action(verb「优化」=action+sweep-FOM script), case 用可移植 level-1 strongarm 网表+HSPICE 复现 (FineSim+G4B foundry 模型不可便携⇒HSPICE+level-1) ⇒ keep_reframe for portability, A 档 verbatim 合规(jiangbaol 原话逐字含「我现在需要优化一个 strongarm 比较器电路...」+sweep_config+FOM 公式), reframe 由 portability-driver 非配额驱动; case 收敛为 produce-tool(写 strongarm_fom_sweep.py 真跑 HSPICE sweep 产 JSON 报告) 给 check() 牙(§4.1 hidden-B cross-input B points/best_point/fom_min/max 非 A + §4.2 真跑 HSPICE binary: subprocess.run([HSPICE,\"-i\",dp,\"-o\",...])+hspice_ran==True+.lis 存在+§4.4 zip 含脚本+py_compile+hidden B 在位未泄漏+exit0 产 JSON+3 次重跑 sha256 一致+JSON dict+points/best_point/fom_min/max, check 真跑 HSPICE 二进制调用); 重构为产 strongarm FOM sizing sweep 优化器; check.py 14 断言验候选 strongarm_fom_sweep.py+JSON 报告 => 收敛为 portable sweep+HSPICE 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标应 L2(check.py 实读 subprocess.run([HSPICE,\"-i\",dp,\"-o\",...])+hspice_ran==True+.lis 存在, check 真跑 HSPICE), level 缺标应 L2, k_check=14 ✓ 已标(metadata 已标, header=14 circled=14 一致), asset_fidelity=synth_deck ✓ 已标(metadata 已标, 因 foundry PDK 不可便携用可移植 level-1 网表合成), shard 缺标应 B, track 缺标应 faithful, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-PlatMosThinIdsatIoffSweep-001":
        "plat_mos_thin idsat/ioff sweep deck 生成器->produce-tool (portability:5 foundry PDK->portable synthesized decks+HSPICE reframe, §4 有牙必要 + 私有资产逼出保真度降级(P-005) r392 portability-driver, r755 spotcheck batch33): 用户 hairuizh@hfeg0pkn001 U0 原意「参考已有的 plat_mos_thin_vthlin/ 文件夹里的 .sp 仿真网表，在 plat_mos_thin_idsat_ioff/ 内创建一组结构相同但测量目标不同的 .sp 文件，用于扫描不同 length 下各个薄氧管的 idsat 与 ioff」(produce-action 创建+扫描+deck-gen), trace 金标准 agent 跑 5 foundry 平台 HSPICE/finesim sweep, 用户原始意图是 produce-action(verb「创建...扫描」=action+deck-gen script), case 用可移植合成 deck+HSPICE (5 foundry PDK 不可便携⇒portable synthesized decks) ⇒ keep_reframe for portability, A 档 verbatim 合规(hairuizh 原话含创建 idsat/ioff .sp 文件+5 平台/idsat/ioff 口径), reframe 由 portability-driver 非配额驱动; case 收敛为 produce-tool(写 plat_mos_idsat_ioff_gen.py 真跑 HSPICE 产 JSON 报告) 给 check() 牙(§4.1 hidden-B cross-input B n_platforms/n_lengths/points 非 A + §4.2 真跑 HSPICE binary: subprocess.run(\"{HSPICE} {sp} -o {prefix}\")+hspice_ran==True+.lis+§4.4 zip 含脚本+py_compile+hidden B 在位未泄漏+exit0 产 JSON+3 次重跑 sha256 一致+JSON dict+n_platforms/n_lengths/points, check 真跑 HSPICE 二进制调用); 重构为产 plat_mos_thin idsat/ioff sweep deck 生成器; check.py 14 断言验候选 plat_mos_idsat_ioff_gen.py+JSON 报告 => 收敛为 portable synth deck+HSPICE 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标应 L2(check.py 实读 subprocess.run(\"{HSPICE} {sp} -o {prefix}\")+hspice_ran==True+.lis, check 真跑 HSPICE), level 缺标应 L2, k_check=14 ✓ 已标(metadata 已标, header=14 circled=14 一致), asset_fidelity=synth_deck ✓ 已标(metadata 已标, 5 foundry PDK 不可便携用 portable synthesized decks), shard 缺标应 B, track 缺标应 faithful, hairuizh 第 3 例(DRAM presim device char verb-heterogeneous user-cluster, 同 host pkn001, 扩展 b30 PwlStimTransform+PlatInvsThick 双), metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-SnmSquareValidator-001":
        "SRAM SNM 蝶形内接正方形逻辑验证器->produce-tool (Q&A-debug->produce-validator-tool reframe, §4 有牙必要, r755 spotcheck batch33): 用户 e0030760@hfeg0pkn004 U0 verbatim(msg128)「输出的 butterfly 图内接正方形没在蝴蝶曲线内，测试逻辑是否正确?」+蝶形曲线/VTC/SNM 口径+诊断背景(Q&A-debug 测试逻辑是否正确=给诊断答案, 定位逻辑错误), trace 金标准 agent 给文本诊断(朴素垂直间距法越界), A 不可行原因=纯 Q&A-debug(「测试逻辑是否正确?」=给诊断答案)无 runnable artifact 无 check 牙 -> case 抽取「snm_square_validator.py(真跑验算法产 JSON 对比报告)」子技能, A 档 verbatim 合规(e0030760 原话逐字含「输出的 butterfly 图内接正方形没在蝴蝶曲线内，测试逻辑是否正确?」+蝶形曲线/VTC/SNM 口径+诊断背景), reframe 由 Q&A-driver 非配额驱动; trace 用户=Q&A-debug(给诊断答案), case 收敛为 produce-tool(写 snm_square_validator.py 真跑验算法产 JSON 对比报告) 给 check() 牙(§4.1 hidden-B cross-input B correct_snm/correct_square/naive_snm/naive_square/corners_valid/overlaps 非 A + §4.4 zip 含脚本+py_compile+可调用入口+hidden B 在位未泄漏+B 上 exit0 产 JSON+3 次重跑 sha256 一致+JSON dict+correct_snm/correct_square/naive_snm/naive_square/corners_valid/overlaps, check 仅 subprocess 跑候选 python 解析 butterfly CSV 数据计算 SNM+验 JSON 结构, 无 EDA 二进制调用); 重构为产 SRAM SNM 蝶形内接正方形逻辑验证器; check.py 13 断言验候选 snm_square_validator.py+JSON 报告 => 收敛为 produce-validator-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: **layer 误分类(metadata 标 L2 应 L1)**(check.py 实读仅 subprocess.run([sys.executable,script,csv_path])+subprocess.run([sys.executable,\"-m\",\"py_compile\",script]), 0 EDA 二进制调用, 候选解析 butterfly CSV 数据计算 SNM, check 验 JSON 结构; 原始 trace 跑 HSPICE MC 5000 但 check 阶段不跑 HSPICE, 只解析预生成 butterfly 数据文本), level 缺标应 L1, k_check 缺标应 13(test_rationale header=13 circled=13 一致), asset_fidelity 缺标应 real-from-trace, shard 缺标应 B, track 缺标应 faithful, e0030760 SRAM SNM 三连之一(同 user 同 host pkn004, verb-homogeneous SNM 分析 user-cluster), metadata bug 待 @A apply 档1/档2 补 sweep。",
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
