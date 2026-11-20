#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r783 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r739_spotcheck18.tsv (batch17, 8 keep_reframe of 12 cases; 3 已在 r736 batch14 apply 过 reframe_note ⇒ 本轮实际 apply 5 case).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r782 档3 batch9-16 done (reframe_note 32->102).
本轮 r783 档3 batch17 (r739 spotcheck18, 5 cases 待 apply). reframe_note 102->107.

reframe_note text = spotcheck18 per_case_reasoning + cases/B trace_source(user@host) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False, round-trip identical 验过.

3 case (StimOp2MisMatchDiag/LoadModeOpTruncDiag/WtmStructReview) 已在 r736 batch14 apply 过 reframe_note (已验证 reframe_note 存在), 本轮跳过 (ALREADY).

Driver 分类 (per per_case_reasoning, spotcheck18 5 待 apply keep_reframe):
  - portability + debug-Q&A->produce-tool 解析器: 1 case (MdMaskBeatZeroDiag, dandans@hfhds201 DDR6 DSCQA vecgen md_mask beats 16-23 期望 0 -> 写脚本解析 md_mask 真跑产 out.json, L1)
  - portability + analysis/Q&A->produce-tool 分析器: 1 case (ModelQaRefactorAnalyze, rongjiez@hfeg0pkn005 runModelQA.pl 旧/新重构分析 -> 写 analyzer 真跑产 report.json, L1)
  - portability + debug-Q&A->produce-tool 诊断器: 1 case (FsdbNfsIncompleteDiag, thomasz@hfeg0pkn002 FineSim 后仿 fsdb 波形打不开 NFS 根因诊断 -> 写 fsdb_diag.py 真跑产 JSON, L1, asset_fidelity=A-faithful)
  - portability + produce-action->produce-tool 分析器: 1 case (AgingDirSeparateTransform, dandans@hfhds201 matrixrun aging step1/step2 目录分离, trace incomplete -> 写 analyzer 真跑产 JSON 报告, revival 池案, layer 缺标 metadata bug 待 @A 档1 补)
  - portability + analysis/Q&A->produce-tool 分析器: 1 case (AgingScriptAnalyze, hswang@hfeg0plg64 FineSim aging matrixrun_aging 脚本分析 -> 写 analyzer 真跑产 report.json, L1)

tongfanl DDR6 diag/Q&A 集群占 spotcheck18 5/12 (StimOp2/MdMaskBeat/LoadModeOp/WtmStructReview/WriteDqPsd), 其中 3 已 apply, 1 (MdMaskBeat, dandans 实际非 tongfanl) 本轮 apply.
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-MdMaskBeatZeroDiag-001":
        "DDR6 DSCQA vecgen md_mask beats 16-23 期望 0 解析器->produce-tool (portability+debug-Q&A->produce-tool 解析器 reframe, §4 有牙必要, r739 spotcheck batch17): 用户 dandans@hfhds201 原话「帮我解析下ddr6_test.sv文件，告诉我为啥在CRC没开的时候+MD_8b+1P6时，PSD0的dq5的D16-D23位期望值是0？」(debug-Q&A 诊断给答案, trace 金标准 M#63 根因=md_mask in write_mem_arr ddr6_tasks.sv L1684-1774 阻止 DQ5 beats 16-23 写入 mem_arr + X1P6+MD_8b_B+DqSelect=0 非 SC1 else 分支 + md_mask=144'hFF0000... 在 DQ5 24-bit field bits 143:120 高 8 bits=beats 16-23 masked), agent 在 trace 读 sv 诊断 md_mask 根因(文本答案)未产出结构化解析脚本; A 不可行原因=真实 vecgen 代码生产文件 SUT 沙盒不可达 -> 用真实场景便携化的合成 sv fixture 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=debug-Q&A(「告诉我为啥」= 诊断给答案), case 收敛为 produce-tool(写脚本解析 md_mask 真跑产 out.json)给 check() 牙(§4.1 hidden-B cross-input guard B masked_dqs[0].dq_index==3 ≠ A 的 DQ5 + beat_range==[8,15] ≠ 硬编 [16,23] + §4.9 防硬编/防 print-expected); 重构为产 md_mask 解析脚本+out.json; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 debug-Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-ModelQaRefactorAnalyze-001":
        "runModelQA.pl 旧/新重构六维创新分析器->produce-tool (portability+analysis/Q&A->produce-tool 分析器 reframe, §4 有牙必要, r739 spotcheck batch17): 用户 rongjiez@hfeg0pkn005 原话「runModelQA_new.pl是我对原始代码runModelQA.pl进行重构得到的新代码，请你仔细分析这两个文件，给出我的新代码到技术突破与创新，例如新的代码支持primesim hspice nanospice finesim多种仿真器」(analysis/Q&A 分析给答案, trace 中 assistant read_files 分段读全两文件, 定位旧 run_simulation 仅 finesim+primesim / 新 runSimulation 四分支 + build_testbench_* + summary_all_results + dry-run/CI + 3042→1630 -46%, 给六维创新分析报告), agent 在 trace 读两文件产分析报告(文本答案)未产出结构化分析脚本; A 不可行原因=真实 runModelQA.pl 生产文件 SUT 沙盒不可达 -> 用真实场景便携化的合成 Perl fixture 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=analysis/Q&A(「分析...给出创新」= 分析给答案), case 收敛为 produce-tool(写 modelqa_refactor_analyze.py 分析器真跑产 report.json)给 check() 牙(§4.1 hidden-B cross-input guard B old_script.line_count==1850 ≠ A 3042 + new==920 ≠ A 1630 + §4.9 防硬编/防 print-expected); 重构为产 analyzer+report.json; check.py 17 断言验 hidden-B cross-input guard+防硬编使纯 analysis/Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-FsdbNfsIncompleteDiag-001":
        "FineSim 后仿 fsdb 波形不完整 NFS 根因诊断器->produce-tool (portability+debug-Q&A->produce-tool 诊断器 reframe, §4 有牙必要, r739 spotcheck batch17): 用户 thomasz@hfeg0pkn002 原话「看下这个log，最后产生的波形打不开，报错说波形不完整」(debug-Q&A 诊断给答案, trace 中 agent read_files 读 ff-40.log 全文 + 对比 3 corner 后定位根因: 瞬态 100% 跑完 finished at 16us 但 fsdb 落盘报 'tlist file size should not be zero' scope_blk_cnt:2/var_blk_cnt:19 + 'fd_slist file size should not be zero' vc_blk_cnt:355963 + SyncControl_Lock errno:116 Stale file handle / NFS), agent 在 trace 读 log 诊断 NFS 根因(文本答案)未产出结构化诊断脚本; A 不可行原因=真实 FineSim log 生产文件 SUT 沙盒不可达 -> 用真实 FineSim log 场景便携化 fixture(asset_fidelity=A-faithful 已标); trace 用户=debug-Q&A(「波形打不开...为啥」= 诊断给答案), case 收敛为 produce-tool(写 fsdb_diag.py 诊断器真跑产 JSON)给 check() 牙(§4.1 hidden-B cross-input guard B sim_end_time=='20us' ≠ A 16us + fd_slist_vc_blk_cnt==418725 ≠ A 355963 + §4.9 防硬编/防 print-expected); 重构为产 fsdb_diag.py+JSON; check.py 19 断言验 hidden-B cross-input guard+防硬编使纯 debug-Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-AgingDirSeparateTransform-001":
        "matrixrun aging step1/step2 目录分离分析器->produce-tool (portability+produce-action->produce-tool 分析器 reframe, trace-incomplete 驱动非配额驱动, §4 有牙必要, r739 spotcheck batch17): 用户 dandans@hfhds201 原话「修改aging部分的代码，使得step1的仿真放在同一个目录，step2的仿真统一放在另一个目录」+ attached matrixrun(127029B Perl, 当前 step1 目录建在 $MatrixDir _step1 后缀, step2 嵌套在 step1/AgingStep2Sim _step2 后缀, 用户要分离成两独立目录), agent 读 matrixrun 分析 aging 段 243-354 行, 但 trace 在 U15 截断 agent 未完成 edit; A 不可行原因=trace 不完整(agent 未完成 edit, 旧判 parked scout: incomplete trace) -> case 收敛为 produce-tool(写 aging_dir_restructure_analyzer.py 分析器真跑产 JSON 报告, 非直接交付 modified matrixrun), B 档 synthesized 合规(§3 允许 A 档不可行时 B 档), reframe 由 trace 不完整驱动非配额驱动; 用真实 matrixrun Perl 场景便携化为合成 fixture 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=produce-action(「修改...代码」= code-modification, 但 trace incomplete), case 收敛为 produce-tool 给 check() 牙(§4.1 hidden-B cross-input guard B aging_flag_var==$agingEnabled ≠ A $aging + step1_suffix==_phase1 ≠ A + §4.9 防硬编/防 print-expected); 重构为产 analyzer+JSON 报告; check.py 20 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(无法落盘 modified matrixrun)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。revival 池案。注: layer 缺标(应 L1, check 仅 subprocess 跑候选 python 分析, 不启动 HSPICE), metadata bug 待 @A apply 档1 补。",
    "EDA-Eval-DesignFlow-AgingScriptAnalyze-001":
        "FineSim aging matrixrun_aging 脚本结构化分析器->produce-tool (portability+analysis/Q&A->produce-tool 分析器 reframe, §4 有牙必要, r739 spotcheck batch17): 用户 hswang@hfeg0plg64 原话「帮我查看该目录下的 matrixrun_aging 脚本，并分析关于 aging 部分的代码」(analysis/Q&A 分析给答案, trace 中助手 read_files 读 3522 行 Perl cxmt_runMatrixSim.pl + search_codebase aging/eageba/..., 产出 10KB 中文结构化分析报告: aging CLI 参数表 11 参数 + 两阶段 MOSRA 工作流 step1 stress simmode=0/step2 measure simmode=1 + 子程序 + agingPVT corner 映射), agent 在 trace 读 Perl 产分析报告(文本答案)未产出结构化分析脚本; A 不可行原因=真实 matrixrun_aging Perl 生产文件 SUT 沙盒不可达 -> 用真实 matrixrun_aging Perl 场景便携化为合成 fixture 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=analysis/Q&A(「分析...代码」= 分析给答案), case 收敛为 produce-tool(写 analyzer 真跑产 report.json)给 check() 牙(§4.1 hidden-B cross-input guard B script_name ≠ A matrixrun_aging + simulator ≠ A finesim + author ≠ A Shao You + §4.9 防硬编/防 print-expected + 22 顶层键齐全); 重构为产 analyzer+report.json; check.py 22 断言验 hidden-B cross-input guard+22 顶层键齐全+防硬编使纯 analysis/Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-MdMaskBeatZeroDiag-001": "portability+debug-Q&A->produce-tool 解析器",
    "EDA-Eval-DesignFlow-ModelQaRefactorAnalyze-001": "portability+analysis/Q&A->produce-tool 分析器",
    "EDA-Eval-DesignFlow-FsdbNfsIncompleteDiag-001": "portability+debug-Q&A->produce-tool 诊断器",
    "EDA-Eval-DesignFlow-AgingDirSeparateTransform-001": "portability+produce-action->produce-tool 分析器 (trace-incomplete 驱动)",
    "EDA-Eval-DesignFlow-AgingScriptAnalyze-001": "portability+analysis/Q&A->produce-tool 分析器",
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
    print(f"=== r783 batch17 reframe_note apply: {len(REFRAME_NOTES)} cases (target) ===")
    counts = {"OK": 0, "ALREADY": 0, "MISSING": 0}
    for cid, note in REFRAME_NOTES.items():
        status, info = apply_one(cid, note)
        counts[status] = counts.get(status, 0) + 1
        print(f"  [{status}] {info} (driver={DRIVER.get(cid,'?')})")
    print(f"\nSummary: OK={counts['OK']} ALREADY={counts['ALREADY']} MISSING={counts['MISSING']}")
    print(f"Expected reframe_note count after apply: 102 + {counts['OK']} = {102 + counts['OK']}")


if __name__ == "__main__":
    main()
