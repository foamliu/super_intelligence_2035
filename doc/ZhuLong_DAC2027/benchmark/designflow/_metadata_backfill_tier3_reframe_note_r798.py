#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r798 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r754_spotcheck33.tsv (batch32, 2/12 keep_reframe cases 待 apply;
        10 keep_faithful = 无 reframe_note OK).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r797 档3 batch9-31 done (reframe_note 32->226).
本轮 r798 档3 batch32 (r754 spotcheck33, 2 cases 待 apply). reframe_note 226->228.

reframe_note text = spotcheck33 per_case_reasoning + cases/B trace_source(user@host/session/mc) + test_rationale k_check (header).
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False.

Driver 分类 (per per_case_reasoning, spotcheck33 12 case: 2 keep_reframe + 10 keep_faithful):
  - Q&A-driver (why/debug/which/analysis Q&A -> produce-tool 给 check 牙): 2 cases (100% Q&A-driver, 0 portability/0 harness/0 sub-skill)
    AplmmxGen025RootCause (thomasz, Q&A-why/debug -> produce-diagnoser-tool) /
    FineSimCoreCounter (mwxi, Q&A-which/analysis -> produce-report-tool)

spotcheck33 关键发现 (本轮 reframe_note scope 限定不修 layer/level/asset_fidelity, 仅在 note 文本标注 layer bug 待 @A 档1 补 sweep):
  - layer 缺标(None)应补 L1 2/2 (本批 reframe 集 2 keep_reframe 全 layer=L1 缺标, 全 12 中 L2 全在 keep_faithful 集)
  - layer 误分类候选 0/2 (本批 reframe 集 0 误分类)
  - **B 域累计 layer 漏网 61->63 例**(r797 累计 61 + 本批 2 缺标: 47 缺标 + 11 误分类 + 本批 2 = 60... 更正: r796 累计 61 = 47 缺标+11 误分类+3(r796 2 缺标+1 误分类候选); 本批 +2 缺标 -> 63, 即 49 缺标 + 11 误分类 + 3 误分类候选 = 63)
  - asset_fidelity 缺标 2/2 (待 @A apply 档2)
  - k_check metadata 缺标 2/2 (AplmmxGen025 应标 21; FineSimCoreCounter 应标 23)
  - 0 例 pre-existing header != circled-mark count (2/2 header==circled: 21/23 ✓)
  - level 缺标 2/2, track 缺标 2/2, shard: AplmmxGen025 ✓ 已标 / FineSimCoreCounter 缺标应 B
  - 注: FineSimCoreCounter mc=9 (legacy, 低于 mc>=10 阈值, 审计判意图非判 mc, 保留)
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-AplmmxGen025RootCause-001":
        "APLMMX GEN-025 连锁错误根因诊断器->produce-tool (Q&A-why/debug->produce-diagnoser-tool reframe, §4 有牙必要, r754 spotcheck batch32): 用户 thomasz@hfeg0pfn058 (sess 1794225494607_gp99g mc10), U0 verbatim「读一下 /rundata/totem/drgqx/IR/.../aplmmx.err 为什么会报 ERROR(GEN-025): Failed to open file '.../tiashu_R_RowCtrl_spicesim_idd98C_ALPS_0904/netlist'...我没有指定这个路径的文件啊」(Q&A-why/debug, 未给根因/修复, A-faithful); trace 金标准 34 msgs agent read_files(aplmmx.err)+list_allowed_files+read_files(netlist@96900-96930)+python-runner 诊断, 定位 netlist 第96915行 .inc 引用已删除旧 ALPS workdir(/proj/drgqx/V0/.../tiashu_R_RowCtrl_spicesim_idd98C_ALPS_0904/) netlist 文件/目录均不存在, 触发 GEN-025 连锁 MMX-314(parse fail@96915)+MMX-312(no sim output), 全表 .inc 共2条(另一条573331 Array_vcap_Param.sp 正常), 子电路 R_RowCtrl(drgqa_cmos_digital/spicesim_idd), design WOWTOP/drgqx_top/config_IDD_trans_RevC, agent 给文本诊断; A 不可行原因=纯 Q&A-why/debug(「为什么会报...我没有指定...」=给诊断答案)无 runnable artifact 无 check 牙 -> case 抽取「APLMMX GEN-025 诊断器(aplmmx_gen025_diagnoser.py 真跑解析 aplmmx.err/netlist 文本产 JSON 诊断报告 22 顶层键)」子技能, A 档 verbatim 合规(thomasz 原话逐字含「为什么会报 ERROR(GEN-025)...我没有指定这个路径的文件啊」+三现场产物 aplmmx.err/netlist_inc_snippet.txt/diag_probe.txt), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 real-from-trace(用真实 aplmmx.err/netlist .inc 结构合成, 待 @A apply 档2); trace 用户=Q&A-why/debug(给诊断答案), case 收敛为 produce-tool(写 aplmmx_gen025_diagnoser.py 真跑解析 aplmmx.err/netlist 文本产 JSON 诊断报告) 给 check() 牙(§4.1 hidden-B cross-input B 缺失文件路径/报错行/子电路名 非 A 的 tiashu_R_RowCtrl_spicesim_idd98C_ALPS_0904 + §4.4 a0-a6 结构(zip 含脚本+py_compile+hidden B 在位未泄漏+exit0 产 JSON+3 次重跑 sha256 一致+JSON dict+22 键齐全)+a7-a19 语义(tool_name==APLMMX/primary_error_code==GEN-025/missing_file_path/missing_file_exists==False/inc_line_number/inc_referenced_path/subcircuit_name/...), check 仅 subprocess 跑候选 python 解析 aplmmx.err/netlist 文本+验 JSON 结构, 无 EDA 二进制调用); 重构为产 APLMMX GEN-025 连锁错误根因诊断器; check.py 21 断言验候选 aplmmx_gen025_diagnoser.py+JSON 报告 => 收敛为 produce-diagnoser-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check 仅 subprocess 跑候选 python 解析文本+验 JSON, 无 EDA 二进制), level 缺标应 L1, k_check 缺标应 21(test_rationale header=21 circled=21 一致), track 缺标应 faithful, asset_fidelity 缺标应 real-from-trace, shard=B ✓ 已标, task_archetype ✓ 已标, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-FineSimCoreCounter-001":
        "FineSim 总核数统计报告器->produce-tool (Q&A-which/analysis->produce-report-tool reframe, §4 有牙必要, r754 spotcheck batch32): 用户 mwxi@hfhds228 (sess 1794291924966_ws1x6 mc9, legacy 低于 mc>=10 阈值, 审计判意图非判 mc, 保留), U0 verbatim「查看此路径内容 /home/adminai/ObsidianVault/项目/protal 及日志，给我现在 finesim 的总核数，之前有让你统计过」(Q&A-which/analysis, 查当前总核数); trace 金标准 agent 发现路径实为 'Portal'(大写 P), 定位 §7 方法论(04-经验与检查清单.md: cloud clnd hosts = 类型列==finesim AND hostname 含 clnd; 排除 45 台 klib/bcp 非 finesim clnd), 读 LSF_Server_List.202261015.xlsx(2614 行 openpyxl), 按 §7 算得 total 155,440 cores/1,820 hosts = cloud(clnd) 51,488/457(HF 0, SH 51,488) + self-buy 103,952/1,363(HF 34,696, SH 69,256), 非 finesim clnd 45 排除, cross-check 通过, agent 给文本答案; A 不可行原因=纯 Q&A-which/analysis(「给我现在 finesim 的总核数」=给统计答案)无 runnable artifact 无 check 牙 -> case 抽取「finesim 总核数统计器(finesim_core_counter.py 真跑读 CSV 产 JSON 报告 9 顶层键)」子技能, A 档 verbatim 合规(mwxi 原话逐字含「查看此路径内容...给我现在 finesim 的总核数，之前有让你统计过」+§7 口径要点 finesim 行=类型列==finesim/云=含 clnd/自购=不含 clnd/HF·SH 按 ENV 拆分/排除非 finesim clnd + lsf_server_list.csv 附件), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 real-from-trace(用真实 LSF_Server_List 结构裁剪合成, 待 @A apply 档2); trace 用户=Q&A-which/analysis(给统计答案), case 收敛为 produce-tool(写 finesim_core_counter.py 真跑读 CSV 产 JSON 报告) 给 check() 牙(§4.1 hidden-B cross-input B total_hosts/total_cores/cloud/self_buy/non_finesim_clnd 非 A 的 1,820/155,440/... + §4.4 zip 含脚本+py_compile+可调用入口 finesim_core_counter(workdir,out_dir)+B 上 exit0 产 JSON+dict+9 顶层键齐全+total_hosts==46(B)+total_cores==2896(B)+cloud/self_buy hosts/cores/hf/sh+non_finesim_clnd_hosts+cross_check_passed+methodology_source, check 仅 subprocess 跑候选 python 读 CSV+验 JSON 结构, 无 EDA 二进制调用); 重构为产 FineSim 总核数统计报告器; check.py 23 断言验候选 finesim_core_counter.py+JSON 报告 => 收敛为 produce-report-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check 仅 subprocess 跑候选 python 读 CSV+验 JSON, 无 EDA 二进制), level 缺标应 L1, k_check 缺标应 23(test_rationale header=23 circled=23 一致), track 缺标应 faithful, asset_fidelity 缺标应 real-from-trace, shard 缺标应 B, metadata bug 待 @A apply 档1/档2 补 sweep。",
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
