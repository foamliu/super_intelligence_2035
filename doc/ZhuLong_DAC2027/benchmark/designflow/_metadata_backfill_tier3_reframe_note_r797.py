#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r797 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r753_spotcheck32.tsv (batch31, 4/12 keep_reframe cases 待 apply;
        8 keep_faithful = LvLvioSweep + SlicerDmMeasAdd + SwitchChgDchVerif + TimingMeasGen +
        NetlistDiffBankLogic + Mt0ParseFix + BisecMt0SmCalc + FloatingNetChecker 无 reframe_note OK).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r796 档3 batch9-30 done (reframe_note 32->222).
本轮 r797 档3 batch31 (r753 spotcheck32, 4 cases 待 apply). reframe_note 222->226.

reframe_note text = spotcheck32 per_case_reasoning + cases/B trace_source(user@host/session/mc) + test_rationale k_check (header).
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False.

Driver 分类 (per per_case_reasoning, spotcheck32 12 case: 4 keep_reframe + 8 keep_faithful):
  - Q&A-driver (why/debug/how-to/which/analysis Q&A -> produce-tool 给 check 牙): 4 cases (100% Q&A-driver, 0 portability/0 harness/0 sub-skill)
    SimIncMissingDiag (yanghao, Q&A-why/debug -> produce-diagnoser-tool) /
    NetlistSigTraceVerify (daiweilu, Q&A-how-to -> produce-trace-tool) /
    HspicePanelCurProjReport (e0041392, Q&A-which -> produce-report-tool) /
    PdkModelWlExtract (owench, Q&A-analysis -> produce-extractor-tool)

spotcheck32 关键发现 (本轮 reframe_note scope 限定不修 layer/level/asset_fidelity, 仅在 note 文本标注 layer bug 待 @A 档1 补 sweep):
  - layer 缺标(None)应补 L1 0/4 (全批 4 keep_reframe layer=L1 ✓ 已正确, 本批 reframe 集无 layer bug; spotcheck32 全 12 中 3 L2 全在 keep_faithful 集 SlicerDmMeasAdd/SwitchChgDchVerif/TimingMeasGen)
  - layer 误分类候选 0/4 (本批 reframe 集 0 误分类, spotcheck32 全 12 误分类 0/12)
  - **B 域累计 layer 漏网 61->61 例**(r796 累计 61 + 本批 0: 47 缺标 + 11 误分类 + 本批 0, **本批 reframe 集零 layer bug 首例**, 对照 r796 2 缺标+1 误分类候选)
  - asset_fidelity 缺标 3/4 (PdkModelWlExtract ✓ A-faithful, 其余 3 缺标待 @A apply 档2)
  - k_check metadata 缺标 1/4 (SimIncMissingDiag 应标 16; NetlistSigTraceVerify=15/HspicePanelCurProjReport=13/PdkModelWlExtract=18 已标)
  - 0 例 pre-existing header != circled-mark count (4/4 header==circled: 16/15/13/18, 对照 r796 1 例 FinesimOptionExtend 12vs14)
  - level 缺标 4/4, track 缺标 1/4(HspicePanelCurProjReport), shard 缺标 3/4(PdkModelWlExtract ✓ B)
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-SimIncMissingDiag-001":
        "仿真 .inc 缺失文件诊断器->produce-tool (Q&A-why/debug->produce-diagnoser-tool reframe, §4 有牙必要, r753 spotcheck batch31): 用户 yanghao@hfhds201 (sess 1794105806205_mah5p mc72), U0 verbatim「/proj/commonIP/analog/v1/lp5x/v0/simdir/anasim/yanghao/2_TsComp_post/result_post 下面的仿真为什么报错了」(Q&A-why/debug, 未给根因/修复, A-faithful); trace 金标准 72 msgs 9 sims 全在 netlist-parse 阶段(~2s)同一错 'unable to read file AG_TS_1stStgComp.spf_RCC (Setting.sp:18)', 根因=Setting.sp 18-19 相对路径 .inc 引用两个 PEX .spf_RCC 寄生网表但文件项目内不存在且 netlist.presim 无 AG_TS_1stStgComp/AG_TS_comp 实例化→残模模板行, 修复=注释 18-19, agent 给文本诊断; A 不可行原因=纯 Q&A-why/debug(「为什么报错了」=给诊断答案)无 runnable artifact 无 check 牙 -> case 抽取「sim inc 缺失诊断器(diagnose_sim_inc_missing.py 真跑解析 sim *.log/Setting.sp 文本产 JSON 诊断报告)」子技能, A 档 verbatim 合规(yanghao 原话逐字含「为什么报错了」+路径), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 real-from-trace(用真实 Setting.sp/sim log 结构合成, 待 @A apply 档2); trace 用户=Q&A-why/debug(诊断给答案), case 收敛为 produce-tool(写 diagnose_sim_inc_missing.py 真跑解析产 JSON 诊断报告) 给 check() 牙(§4.1 hidden-B cross-input B missing_file='AG_XY_foobar.spf_RCC' 非 A 的 AG_TS_1stStgComp + §4.4 sim_count/failed_sims/unified_error/root_cause.missing_file/setting_sp_line/path_type/file_exists/unused_includes/fix_suggestion, check 仅 subprocess 跑候选 python 解析 sim *.log/Setting.sp 文本+验 JSON 结构, 无 EDA 二进制调用); 重构为产 sim inc 缺失诊断器; check.py 16 断言验候选 diagnose_sim_inc_missing.py+outB.json => 收敛为 produce-diagnoser-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check 仅 subprocess 跑候选 python 解析文本+验 JSON, 无 EDA 二进制), level 缺标应 L1, k_check 缺标应 16(test_rationale header=16 circled=16 一致), asset_fidelity 缺标应 real-from-trace, shard 缺标应 B, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-NetlistSigTraceVerify-001":
        "Verilog 网表信号连线路径追踪验证器->produce-tool (Q&A-how-to->produce-trace-tool reframe, §4 有牙必要, r753 spotcheck batch31): 用户 daiweilu@hfhds209 (sess 1794192133796_quioy mc102), U0 verbatim 问 testmode cm1_ag_VkbSenseAddActBiasEn 在 Verilog 网表中的连线路径,「我该如何验证」(Q&A-how-to); trace 金标准 102 msgs LPDDR5 testmode(0=default 不加偏置, 1=add 2*glbbias active bias), agent 写 search_netlist.py 搜目标信号按 module 归属输出结构化 JSON, 后给完整验证指南(信号路径 ChanEdgeL->CmLeft->VkbSenseIP->VncsgnSenseCompHysIP, MPSW5 PMOS 开关, ActHBiasN 逻辑), 本 case 取 U#0 纯需求轮重构为通用 trace_signal.py; A 不可行原因=纯 Q&A-how-to(「我该如何验证」=给验证方法答案)无 runnable artifact 无 check 牙 -> case 抽取「网表信号追踪器(trace_signal.py 真跑搜 Verilog 网表产 JSON)」子技能, A 档 verbatim 合规(daiweilu 原话需求逐字含验证 testmode 信号路径+功能描述 0/1)+网表目录, reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 real-from-trace(用真实 lpddr5 网表结构裁剪合成, 待 @A apply 档2); trace 用户=Q&A-how-to(给验证方法答案), case 收敛为 produce-tool(写通用 trace_signal.py 真跑搜网表产 JSON) 给 check() 牙(§4.1 hidden-B cross-input B 模块名 CmRight/VSenseLogicX/ChanEdgeX 非 A 的 CmLeft/VkbSenseLogicA + §4.4 occurrences/modules_found/num_modules+每条含 line/module/text+⑬ A 专属模块名不泄漏+⑭⑮ 大小写不敏感, check 仅 subprocess 跑候选 python 解析 Verilog 网表文本+验 JSON 结构, 无 EDA 二进制调用); 重构为产 网表信号追踪验证器; check.py 15 断言验候选 trace_signal.py => 收敛为 produce-trace-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check 仅 subprocess 跑候选 python 解析 Verilog 网表文本+验 JSON, 无 EDA 二进制), level 缺标应 L1, k_check=15 ✓ 已标(header=15 circled=15 一致), asset_fidelity 缺标应 real-from-trace, track=synthesized ✓, shard 缺标应 B, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-HspicePanelCurProjReport-001":
        "HSPICE 面板当前项目报告器->produce-tool (Q&A-which->produce-report-tool reframe, §4 有牙必要, r753 spotcheck batch31): 用户 e0041392@hfeg0pkn003 (sess 1794200811873_k36er mc12), U0 verbatim「检查一下workspace中设置的当前项目是哪一个」(Q&A-which, 查当前项目); trace 金标准 12 msgs agent list_allowed_files+read_files 读 .anasim_pro_folders.json(active=/home/e0041392)+.hspice_panel_config.json(finesim/fqueue3/6cores), 判定当前项目=active 并整理面板设置, agent 给文本答案; A 不可行原因=纯 Q&A-which(「检查...当前项目是哪一个」=给答案)无 runnable artifact 无 check 牙 -> case 抽取「hspice 面板当前项目报告器(hspice_panel_curproj_report.py 真跑读配置产 JSON 报告)」子技能, A 档 verbatim 合规(e0041392 原话逐字含「检查...当前项目是哪一个」+doc/ 附件说明), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 real-from-trace(用真实 .anasim_pro_folders.json/.hspice_panel_config.json 结构合成, 待 @A apply 档2); trace 用户=Q&A-which(给答案), case 收敛为 produce-tool(写 hspice_panel_curproj_report.py 真跑读配置产 JSON 报告) 给 check() 牙(§4.1 hidden-B cross-input B current_project/simulator_type/queue/cores 非 A 的 /home/e0041392/finesim/fqueue3/6 + §4.4 13 顶层键齐全+workspace_folders+simulator_version+⑬ A-leak 守护+⑭ 确定性 rerun, check 仅 subprocess 跑候选 python 读 JSON 配置+验 JSON 结构, 无 EDA 二进制调用); 重构为产 hspice 面板当前项目报告器; check.py 13 断言验候选 hspice_panel_curproj_report.py+JSON 报告 => 收敛为 produce-report-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check 仅 subprocess 跑候选 python 读 JSON 配置+验 JSON, 无 EDA 二进制), level 缺标应 L1, k_check=13 ✓ 已标(header=13 circled=13 一致), asset_fidelity 缺标应 real-from-trace, track 缺标应 faithful, shard 缺标应 B, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-PdkModelWlExtract-001":
        "PDK model W/L 范围提取器->produce-tool (Q&A-analysis->produce-extractor-tool reframe, §4 有牙必要, r753 spotcheck batch31): 用户 owench@hfeg0pkn002 (sess 1794210761770_t9j7w mc24), U0 verbatim「/apps/imctf/extpdk/HL22/.../hspice/model_thick.sp 分析一下这个model」+多轮追问 ntk/ptk/ntk_lv/ptk_lv/ntk_s/ptk_s/ptk_sv 的 W/L 尺寸范围、ntk_asy1/asy2 与 ntk_sv1/sv2 区别、跨版本对比(Q&A-analysis 分析 PDK model); trace 金标准 24 msgs agent 用 list_allowed_files/read_files 探目录读文件, 写多个 Python 解析脚本(verify_wl.py/compare_asy_sv.py 等), 逐行扫 .subckt 边界+.model 卡续行拼接+正则提 lmin/lmax/wmin/wmax(IGNORECASE), 产各管子 W/L 范围与 bin 数对比表, 真实意图=分析 PDK 厚栅氧 model 识别管子并提取 W/L 范围, 纯分析 Q&A 无仿真无 deliverable, agent 给文本/表分析; A 不可行原因=纯 Q&A-analysis(「分析一下这个model」=给分析答案)无 runnable artifact 无 check 牙 -> case 抽取「PDK W/L 提取器(pdk_wl_extract.py 真跑解析 HSPICE model 产 JSON 报告)」子技能, A 档 verbatim 合规(owench 原话逐字含「分析一下这个model」+功能说明识别厚栅氧 .subckt+提 lmin/lmax/wmin/wmax+bin 数)+命令行签名, reframe 由 Q&A-driver 非配额驱动; asset_fidelity=A-faithful ✓ 已标(用真实 HL22 PDK model 结构合成); trace 用户=Q&A-analysis(给分析答案), case 收敛为 produce-tool(写 pdk_wl_extract.py 真跑解析 model 产 JSON 报告) 给 check() 牙(§4.1 hidden-B cross-input B model_name=='XJ28' 非 A 的 HL22+device_count==11 非 A 的 8+device 名集 ntk2/ptk2/... 非 A 的 ntk/ptk + §4.4 model_name/devices/device_count+per-device type/port_count/bin_count/lmin/lmax/wmin/wmax 全匹配 B 真值+A-leak token/numeric 守护+⑱⑲⑳ 确定性 3 rerun, check 仅 subprocess 跑候选 python 解析 HSPICE model 文本+验 JSON 结构, 无 EDA 二进制调用); 重构为产 PDK model W/L 范围提取器; check.py 18 断言验候选 pdk_wl_extract.py+JSON 报告 => 收敛为 produce-extractor-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check 仅 subprocess 跑候选 python 解析 HSPICE model 文本+验 JSON, 无 EDA 二进制), level 缺标应 L1, k_check=18 ✓ 已标(header=18 circled=18 一致), asset_fidelity=A-faithful ✓ 已标, track=analysis-Q&A ✓ 已标, shard=B ✓ 已标, metadata bug 待 @A apply 档1 补 level sweep。",
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
