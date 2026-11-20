#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r789 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r745_spotcheck24.tsv (batch23, 8/8 keep_reframe cases).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r788 档3 batch9-22 done (reframe_note 32->155).
本轮 r789 档3 batch23 (r745 spotcheck24, 8 cases 待 apply). reframe_note 155->163.

reframe_note text = spotcheck24 per_case_reasoning + cases/B trace_source(user@host/session/mc) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False.

Driver 分类 (per per_case_reasoning, spotcheck24 8 keep_reframe):
  - produce-action 跑仿真→produce-tool deck-gen/judge/modify/tune portability-driven (portability-driver): 4 cases
    Vcc2scActDeckGen (tongni@hfeg0pkn001, foundry PDK+真跑 HSPICE 不可便携 -> 抽 deck 生成子技能) /
    SimSpecJudge (tongni@hfeg0pkn001, 121 PVT corner + 500 MC 真跑不可便携 -> 抽 parse+judge 子技能) /
    PUvddSweep (e0030760@hfeg0pkn004, foundry 6T bitcell + 真跑 hspice 不可便携 -> 抽 modify+sweep deck 生成子技能) /
    IoBufParamTune (elianaz@hfeg0pkn002, FineSim 4-corner MC + foundry IO 不可便携 -> 抽 tune 子技能)
  - Q&A/analysis/check/diag/compare/explain->produce-tool (Q&A-driver): 3 cases
    TbMeasCheck (e0030760@hfeg0pkn004, check-Q&A 问测量指令是否有问题 -> 产 check 脚本+out.json) /
    NetlistMisModCompare (e0030760@hfeg0pkn004, compare+explain-Q&A 对比网表+解释 mis_mod -> 产 compare 脚本+report.json) /
    CharRemovalAbort (ronghu@hfeg0pkn005, diag-Q&A 诊断 removal abort 根因 -> 产 diagnose 脚本+out.json)
  - produce-action file/list->script harness (harness-driver): 1 case
    VwlpRefDeckSet (tongni@hfeg0plg63, 用户要 deck-set -> case 抽 deck generator .py 支撑 §4.1 hidden-B cross-input guard)

spotcheck24 关键发现 (本轮 reframe_note scope 限定不修 layer/level/asset_fidelity, 仅在 note 文本标注 layer bug 待 @A 档1 补 sweep):
  - layer 缺标(None→应 L1) 6/8: VwlpRefDeckSet/Vcc2scActDeckGen/SimSpecJudge/PUvddSweep/NetlistMisModCompare/IoBufParamTune
  - layer 误分类 L2→应 L1 2/8: TbMeasCheck(解析 .sp 不启动 SPICE)/CharRemovalAbort(解析 .lis 不启动 HSPICE/SiliconSmart)
  - 全 8/8 layer 应 L1(check subprocess 跑 python 解析 .sp/.lis/.netlist/产 deck 文本, 0 例启动 EDA 二进制)
  - B 域累计 layer 漏网 17(r788 累计) + 8(本轮) = 25 例, r772 档1 level→layer normalize 漏网之鱼
  - asset_fidelity 缺标 7/8(仅 VwlpRefDeckSet=synth_deck ✓ 已标), 待 @A apply 档2
  - level/tier 缺标或为 L2 应统一 L1, 待 @A apply 档1 补 sweep
  - CharRemovalAbort doc-text bug: rationale header 15 vs circled 14 vs check.py _cond 16 (硬闸门 k_check≥8 满足, header/circled/check 三计数两两不等, pre-existing 非 r789 引入), 待 @A apply 修
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-VwlpRefDeckSet-001":
        "DRAM VwlpRef 参考电压缓冲器(5T-OTA+PMOS pass unity-feedback LDO)多分析 HSPICE deck-set 生成器->produce-tool (harness produce-action deck-set->script reframe, §4 有牙必要, r745 spotcheck batch23): 用户 tongni@hfeg0plg63 用 sim-sp-gen 技能(deepread 1793103982380_vdwab mc236), trace 给定 netlist/corner/power/spec 资产产 5 deck(tran/ac/dc/tran_mc/psrr); A 不可行原因=produce-action 交付 deck-set(file-based, 5 个 .sp 静态文件)无法支撑 §4.1 hidden-B cross-input guard(隐藏 B 不同 SPEC/参数需重新生成) -> case 抽取「harness-wrap: 解析 spec.json 按结构产 5 deck 的 vwlpref_deckset_gen.py」子技能, B 档 synthesized 合规(prompt 模拟混合信号设计验证工程师场景, 列 dut.sp/corner.sp/power.sp/spec.json 资产), reframe 由 harness-driven 非配额驱动; asset_fidelity ✓ 已标(synth_deck); trace 用户=produce-action(生成 deck-set), case 收敛为 produce-tool(写 vwlpref_deckset_gen.py 产 5 deck + report.json/py_compile/exit 0/跨输入 A vs B 反硬编/确定性) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 vwlpref_deckset_gen.py+deck-set; check.py 14 断言验 5 deck 齐全/tran 含 .tran+阶跃负载 pwl+9 measure/ac/dc/tran_mc/psrr 各自结构/反硬编 => 收敛为 produce-tool harness 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 产 deck 文本, 不启动 HSPICE), tier/level 缺标应 L1, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-Vcc2scActDeckGen-001":
        "Vcc2scAct SPEC-driven 5-deck 仿真生成器->produce-tool (portability produce-action run->produce-tool deck-gen reframe, §4 有牙必要, r745 spotcheck batch23): 用户 tongni@hfeg0pkn001 原话 U0 逐字「/home/tongni/Desktop/1_Vcc2sc_stdby/Vcc2scAct_sim_sp 根据文件夹下的文件跑仿真，把对应的结果放到/proj/dscqa/V0/simdir/hspice/tongni/00_AI_test/」(produce-action 跑仿真, deepread 1793341440302_sqm07 mc223), trace agent 读 SPEC.sp(5 段 tran/ac/ac_load/dc_capbi/tran_mc)生成 5 deck; A 不可行原因=produce-action 真跑 HSPICE 依赖 foundry PDK 不可便携 .75 -> case 抽取「按 SPEC.sp 结构产 5 deck 的 gen_decks.py」子技能, A 档 verbatim 合规(U0 原话逐字含真实 /home + /proj 路径), reframe 由 portability-driven 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(SPEC.sp 真实)+hidden B=synthesized(待 @A apply 档2); trace 用户=produce-action(跑仿真), case 收敛为 produce-tool(写 gen_decks.py 产 5 deck 子目录/netlist 拷贝/tran 含 SPEC measure 名/ac_load/ac/dc_capbi/tran_mc 各自结构/跨输入 A vs B 反硬编/确定性) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 gen_decks.py+5 deck; check.py 12 断言验 5 deck 齐全+SPEC measure 名+反硬编(本批最低 k) => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 产 deck 文本, 不启动 HSPICE), tier=L2 应改 L1(同因), metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-SimSpecJudge-001":
        "Vcc2scAct 多 sim 类型 SPEC 合规判定器->produce-tool (portability produce-action run+judge->produce-tool parse+judge reframe, §4 有牙必要, r745 spotcheck batch23): 用户 tongni@hfeg0pkn001 原话 U0 逐字「[sim-sp-gen] /home/tongni/Desktop/1_Vcc2sc_stdby/Vcc2scAct_sim_sp/ 路径下给出了对应的网表和SPEC 根据此跑对应的仿真」(produce-action 跑仿真+判合规, deepread 1793266803039_g89xb mc224), trace agent 跑 5 sim 类型(tran/ac/ac_load/dc_capbi/tran_mc)+解析 .mt0/.ma0/.mc0+比对 ~10 SPEC metrics 跨 121 PVT corner+500 MC; A 不可行原因=produce-action 真跑 121 PVT+500 MC 不可便携 .75 -> case 抽取「解析 .mt0/.ma0/.mc0 + 比对 SPEC 产合规判定的 judge_sim_vs_spec.py」子技能, A 档 verbatim 合规(U0 原话逐字含 [sim-sp-gen] 标记+真实 /home 路径), reframe 由 portability-driven 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(真实 SPEC+measure 文件)+hidden B=synthesized(待 @A apply 档2); trace 用户=produce-action(跑仿真+判合规), case 收敛为 produce-tool(写 judge_sim_vs_spec.py 产 report.json/5 类别 measure 比对/SPEC 合规判定/跨输入 A vs B 反硬编/确定性) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 judge_sim_vs_spec.py+report.json; check.py 13 断言验 5 类别 measure+合规判定+反硬编 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 解析 .mt0/.ma0/.mc0, 不启动 HSPICE), tier=A-faithful 应 normalize 为 L1(同因), metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-PUvddSweep-001":
        "SRAM 6T bitcell PU VDD sweep testbench 修改器+deck 生成器->produce-tool (portability produce-action modify+run->produce-tool modify+deck-gen reframe, §4 有牙必要, r745 spotcheck batch23): 用户 e0030760@hfeg0pkn004 原话 U0 逐字「/home/e0030760/Documents/SRAM_6T_testbench/6Ttestbench.sp 根据这个6T的testbench.sp修改testbench仿真不同PU管的VDD电压对Iread、Iwrite、WSNM、RSNM、HSNM等参数的影响，该testbench内有电路netlist，直接读取并进行修改仿真」(produce-action 修改 testbench+跑 sweep 仿真, deepread 1793187913089_e6xdf mc185), trace agent 修改 6Ttestbench.sp 做 PU VDD sweep; A 不可行原因=produce-action 真跑 hspice 依赖 foundry 6T bitcell 不可便携 .75 -> case 抽取「修改 testbench 加独立 PU 电源轨+参数 sweep 产 deck 的 modify_tb.py」子技能, A 档 verbatim 合规(U0 原话逐字含真实 /home 路径+PU VDD sweep 指标), reframe 由 portability-driven 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(6Ttestbench.sp 真实)+hidden B=synthesized(待 @A apply 档2); trace 用户=produce-action(修改+跑仿真), case 收敛为 produce-tool(写 modify_tb.py 产 deck/VPUP 参数声明/独立 PU 电源轨/sweep 遍历/measure 保留 Iread/Iwrite/WSNM/RSNM/HSNM/跨输入 A vs B 反硬编/确定性) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 modify_tb.py+sweep deck; check.py 15 断言验 VPUP 声明+独立 PU 轨+sweep 遍历+5 measure 保留+反硬编 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 产 sweep deck 文本, 不启动 HSPICE), tier=L2 应改 L1(同因), metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-TbMeasCheck-001":
        "SRAM bitcell testbench 测量指令检查器->produce-tool (Q&A check-Q&A->produce-tool check+JSON reframe, §4 有牙必要, r745 spotcheck batch23): 用户 e0030760@hfeg0pkn004 原话 U0 逐字「/home/e0030760/Documents/Solido/test_fix.sp 帮我检查一下这个testbench，里面测试WSNM、Iread、Iwrite、Ileak的指令是否存在问题」(check-Q&A 问测量指令是否有问题, deepread 1793791169909_2ka5p mc257), trace agent 读 test_fix.sp+bitcell netlist+实测 .ms0/.mt0 诊断测量指令; A 不可行原因=纯 check-Q&A(问指令是否有问题)无 runnable artifact 无 check 牙 -> case 抽取「静态解析 .sp 验测量指令结构产 tb_meas_check.py+out.json」子技能, A 档 verbatim 合规(U0 原话逐字含真实 /home 路径+WSNM/Iread/Iwrite/Ileak 指标), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(test_fix.sp 真实)+hidden B=synthesized(待 @A apply 档2); trace 用户=check-Q&A(检查指令是否有问题), case 收敛为 produce-tool(写 tb_meas_check.py 产 out.json/tool_version+measures+other_issues/measures 恰含 WSNM/Iread/Iwrite/Ileak/各 measure 指令结构校验/跨输入 A vs B 反硬编/确定性) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 tb_meas_check.py+out.json; check.py 15 断言验 4 measure 齐全+指令结构校验+反硬编 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L2 误分类应改 L1(check 仅 subprocess 跑 python 解析 .sp, 不启动 HSPICE/Solido), level 缺标应 L1, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-NetlistMisModCompare-001":
        "SRAM bitcell 网表对比+mis_mod 作用解释器->produce-tool (Q&A compare+explain-Q&A->produce-tool compare+JSON reframe, §4 有牙必要, r745 spotcheck batch23): 用户 e0030760@hfeg0pkn004 原话 U0 逐字「对比一下这两个路径下的网表，其中一个调用的mis_mod是用来做什么的？」(给两 .netlist 路径, compare+explain-Q&A, deepread 1793679618975_i1zyw mc158), trace agent 经 list_allowed_paths/read_files 对比+解释失配模型; A 不可行原因=纯 compare+explain-Q&A(对比+解释)无 runnable artifact 无 check 牙 -> case 抽取「静态解析两 .netlist 对比+定位 mis_mod 调用+解释作用产 compare_netlists.py+report.json」子技能, A 档 verbatim 合规(U0 原话逐字, 路径改写为 assets/netlist_A.sp assets/netlist_B.sp 适配沙箱), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(真实两 netlist)+hidden B=synthesized(待 @A apply 档2); trace 用户=compare+explain-Q&A(对比+解释 mis_mod 作用), case 收敛为 produce-tool(写 compare_netlists.py 产 report.json/15 顶层必需键/对比结构/mis_mod 调用定位/mis_mod 作用说明/跨输入 A vs B 反硬编/确定性) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 compare_netlists.py+report.json; check.py 14 断言验 15 键+对比结构+mis_mod 定位+作用+反硬编 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 解析 .netlist, 不启动 SPICE), tier=L2 应改 L1(同因), metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-IoBufParamTune-001":
        "IO buffer(DqPrampBuf)FineSim 参数调优器+报告器->produce-tool (portability produce-action run+tune->produce-tool tune+report reframe, §4 有牙必要, r745 spotcheck batch23): 用户 elianaz@hfeg0pkn002 原话 U0 逐字「@/rundata/drcoa/V0/simdir/finesim/workdir/elianaz/simulation/99_IO_buffer/001_z_top_drgqa_slow_MC_PDA_TT.sp 用这个文件跑仿真，调整参数值，使measure得到的data_H的值大于等于0.99*VDDQ，data_L的值小于等于0.001，参数范围如下 LR56...LMP12...WMP12...WP1...WN1...」(produce-action 跑仿真+调参达标, deepread 1793792373749_l5r0u mc218), trace agent 用 FineSim 4-corner(TT/25C/1.1V, SS/-40C/...) MC + foundry IO; A 不可行原因=produce-action 真跑 FineSim 4-corner MC + foundry IO 不可便携 .75 -> case 抽取「按 5 参数范围调优产 tuned .sp+report 的 tune_io_buffer.py」子技能, A 档 verbatim 合规(U0 原话逐字含真实 @路径+5 参数范围+data_H/data_L 指标), reframe 由 portability-driven 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(真实 .sp+参数范围)+hidden B=synthesized(待 @A apply 档2); trace 用户=produce-action(跑仿真+调参达标), case 收敛为 produce-tool(写 tune_io_buffer.py 产 tuned .sp+report.json/6 顶层键 original_params/tuned_params/参数范围合规/data_H/data_L 达标判定/跨输入 A vs B 反硬编/确定性) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 tune_io_buffer.py+tuned .sp+report.json; check.py 13 断言验 6 键+参数范围合规+达标判定+反硬编 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 python 产 tuned .sp 文本, 不启动 FineSim), tier=L2 应改 L1(同因), metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-CharRemovalAbort-001":
        "SiliconSmart timing char removal 弧 abort 根因诊断器->produce-tool (Q&A diag-Q&A->produce-tool diagnose+JSON reframe, §4 有牙必要, r745 spotcheck batch23): trace 用 Synopsys SiliconSmart V-2023.12-SP5 对 ffrqN_Rfreshtokenx2(异步复位 DFF, back-bias)做 timing characterization, 两条 removal 弧(Task 27/30)同时 hspice rc=1 abort, recovery/setup/hold 正常, deepread 1793692877234_xlzwr mc159, 用户 ronghu@hfeg0pkn005; A 不可行原因=纯 diag-Q&A(诊断 abort 根因)无 runnable artifact 无 check 牙 -> case 抽取「静态解析 deck.cir/deck.lis 定位 abort 根因=no_pass_point_in_search 产 diagnose_removal_abort.py+out.json」子技能, B 档 synthesized 合规(prompt 模拟 char 工程师场景, 列 deck.cir/deck.lis/单元 lib 资产, 保留真实单元名 ffrqN_Rfreshtokenx2+Task 27/30+SiliconSmart 版本), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(deck.cir/deck.lis 真实)+hidden B=synthesized(待 @A apply 档2); trace 用户=diag-Q&A(诊断 removal abort 根因), case 收敛为 produce-tool(写 diagnose_removal_abort.py 产 out.json/12 字段/root_cause_category=='no_pass_point_in_search'/removal arc 定位/transient_points 显式值 284100/data_state_d≈0.8 bug 值/fix_action 含 D=0/跨输入 A vs B 反硬编/确定性) 给 check() 牙(§4.1 hidden-B cross-input guard A vs B 反硬编 + §4.9 反硬编); 重构为产 diagnose_removal_abort.py+out.json; check.py 15 断言验 root_cause+transient_completed+transient_points+bug 值+fix_action+hidden guard+反硬编 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L2 误分类应改 L1(check 仅 subprocess 跑 python 解析 .lis, 不启动 HSPICE/SiliconSmart), level 缺标应 L1, metadata bug 待 @A apply 档1 补 sweep; **另注 pre-existing doc-text bug**: test_rationale header 文本「15 条断言」与 circled 计数 14 与 check.py _cond 计数 16 三者两两不等(硬闸门 k_check≥8 满足, 但 header/circled/check 三计数对不上, 非本轮引入), 待 @A apply 修 rationale 一致性。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-VwlpRefDeckSet-001": "harness produce-action deck-set->script",
    "EDA-Eval-DesignFlow-Vcc2scActDeckGen-001": "portability produce-action run->produce-tool deck-gen",
    "EDA-Eval-DesignFlow-SimSpecJudge-001": "portability produce-action run+judge->produce-tool parse+judge",
    "EDA-Eval-DesignFlow-PUvddSweep-001": "portability produce-action modify+run->produce-tool modify+deck-gen",
    "EDA-Eval-DesignFlow-TbMeasCheck-001": "Q&A check-Q&A->produce-tool check+JSON",
    "EDA-Eval-DesignFlow-NetlistMisModCompare-001": "Q&A compare+explain-Q&A->produce-tool compare+JSON",
    "EDA-Eval-DesignFlow-IoBufParamTune-001": "portability produce-action run+tune->produce-tool tune+report",
    "EDA-Eval-DesignFlow-CharRemovalAbort-001": "Q&A diag-Q&A->produce-tool diagnose+JSON",
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
    print(f"=== r789 batch23 reframe_note apply: {len(REFRAME_NOTES)} cases (target) ===")
    counts = {"OK": 0, "ALREADY": 0, "MISSING": 0}
    for cid, note in REFRAME_NOTES.items():
        status, info = apply_one(cid, note)
        counts[status] = counts.get(status, 0) + 1
        print(f"  [{status}] {info} (driver={DRIVER.get(cid,'?')})")
    print(f"\nSummary: OK={counts['OK']} ALREADY={counts['ALREADY']} MISSING={counts['MISSING']}")
    print(f"Expected reframe_note count after apply: 155 + {counts['OK']} = {155 + counts['OK']}")


if __name__ == "__main__":
    main()
