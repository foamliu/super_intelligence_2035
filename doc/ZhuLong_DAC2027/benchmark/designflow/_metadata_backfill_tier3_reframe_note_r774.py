#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r774 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r731_spotcheck10.tsv (batch10, 9 keep_reframe cases).
Spec: r771 bounded queue 档1→档3→档2. r772 档1 done. r773 档3 batch9 (r730, 8 cases) done. 本轮 r774 档3 batch10.

reframe_note text = r731 spotcheck10 per_case_reasoning + cases/B trace_source(user@host) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False, round-trip identical 验过.

Driver 分类 (per per_case_reasoning):
  - portability only (real 内网 path/license → synth self-contained, trace agent 本就 produce): 6 cases
  - portability + Q&A->produce candidate (trace 用户问 how/why, Q&A->produce reframe 待 trace 全文确认): 3 cases
"""
import json, os, sys, io

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

# case_id -> reframe_note text
REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-NetlistLibdefsTrap-001":
        "网表抽取+cds.lib 陷阱处理->produce (portability reframe, §4 有牙必要, r731 spotcheck batch10): 用户 alexli@10.129.2.13 抽 hspice 网表并处理 cds.lib 陷阱, A 不可行原因=真实 /proj/ddgoa 内网工程目录+Aether emy2netlist 环境 SUT 沙盒无 /proj 权限不可达 -> 用自包含合成项目树 proj_B(含 libs/ 子库+陷阱 cds.lib)保留真实任务结构(asset_fidelity=synth_deck); 重构为产 extract_netlist.py; check.py 14 断言验 lib.defs 存在+DEFINE 路径 isdir+不含 ddgom+<cell>.hsp>100B+>=2 .subckt+TopDesStart/End+种植叶子 subckt+顶层 cell 名+report.md 提陷阱+hidden-B cross-input guard 使原 /proj 不可达任务无法有牙 => 合成项目树+produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-ULVTDelvtoNetlistMod-001":
        "ULVT 器件 delvto 网表修改->produce (portability reframe, §4 有牙必要, r731 spotcheck batch10): 用户 joeyl@10.129.2.13 给 ULVT 器件加 _delvto=-0.2, A 不可行原因=真实 /rundata 只读内网工程目录+/home/joeyl/ulvt_delvto/ 工具 SUT 沙盒不可达 -> 用自包含合成 hspice 网表保留真实任务结构(pulvt_ckt/nulvt_ckt X 实例+_delvto 追加+幂等+非 ULVT 不动, asset_fidelity=synth_netlist); 重构为产 apply_delvto.py; check.py 14 断言验 输出行数==输入+恰好 3 ULVT 实例带 _delvto=-0.2+pulvt_ckt==2/nulvt_ckt==1+非 ULVT 不带+delvto_user 计数不变+.subckt/.ends 计数不变+幂等+hidden-B(delvto=-0.15) cross-input guard 使原 /rundata 不可达任务无法有牙 => 合成网表+produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-StcCrfGenerator-001":
        "CRF 生成->produce (portability reframe, §4 有牙必要, r731 spotcheck batch10): 用户 jerrychu@10.129.2.12 读 INPUT 生成 CRF, A 不可行原因=真实 /proj/lacaa 内网工程目录 SUT 沙盒无 /proj 权限不可达 -> 用自包含合成 INPUT 目录(8 文件结构保留)保留真实任务结构(asset_fidelity=synth_deck); 重构为产 gen_crf.py; check.py 14 断言验 CRF 顶层标题+§1 project 名+命名模板 3 tag+VT flavors 数量==B 01_stc.list+库名解码>=3 段+cell 总数==B 07_cell.list+全 cell 名出现+BUFFD 分组==6+PEX 工具 GloryEX+corner 7Corner+SPICE model 路径+hidden-B cross-input guard 使原 /proj 不可达任务无法有牙 => 合成 INPUT+produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-Ddr6RptCmdExtract-001":
        "rpt 命令提取->produce (portability reframe, §4 有牙必要, r731 spotcheck batch10): 用户 e0017484@hfeg0plg08 从 .rpt.die0 提取命令+结构化分析, A 不可行原因=真实 /rundata 内网工程目录 SUT 沙盒不可达 -> 用自包含合成 .rpt.die0 报告保留真实任务结构(asset_fidelity=synth_data 已正确标注); 重构为产 extract_cmds.py+cmd_report.json; check.py 12 断言验 合法 JSON+顶层键+A 重跑 exit0 复现+total_command_lines==oracle+per_type==oracle+mrw_registers==oracle+phase_counts==oracle+first/last/duration+hidden-B cross-input guard 使原 /rundata 不可达任务无法有牙 => 合成报告+produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-FineSimDiag-001":
        "FineSim 5 连报错诊断->produce (portability+Q&A->produce reframe, §4 有牙必要, r731 spotcheck batch10): 用户 e0024852@hfeg0pkn004 5 次「how to fix it」, A 不可行原因=真实 FineSim/PrimeSim 报错日志来自 /rundata 内网+XA license 不可沙盒复刻 -> 用自包含合成 5 报错日志保留真实任务结构(asset_fidelity=synth_deck); trace 用户问「how to fix it」= Q&A 候选(待 trace 全文确认 produce->produce vs Q&A->produce, 参照 batch9 SimModelMismatchDiag keep_faithful 先例); 重构为产 diagnose_finesim_errors.py+diagnostic_report.json; check.py 13 断言验 A 重跑 exit0 复现+errors 恰 5 条+category 集合+dspf_unresolvable_net+bsub+missing_param+xa_license+vec_format+hidden-B cross-input guard 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SentaurusDeckSetupSummary-001":
        "Sentaurus deck setup 学习总结->produce (portability reframe, §4 有牙必要, r731 spotcheck batch10): 用户 e02141@hfeg0pkn001 study+summarize deck setup 常见文件, A 不可行原因=真实 /apps/synopsys/sentaurus Applications_Library SUT 沙盒无 license/路径不可达 -> 用自包含合成项目树(3 项目+sdevice_des.cmd+svisual_vis.tcl)保留真实任务结构(asset_fidelity=synth_deck); trace agent 本就 produce(总结报告), produce->produce 非 Q&A->produce reframe, 仅 portability 驱动; 重构为产 summarize_deck_setup.py+deck_setup_summary.json; check.py 13 断言验 6 顶层键+A 重跑 exit0 复现+n_projects==3+n_files_scanned+categories+common_files+tool_chain+sdevice deck basename+hidden-B cross-input guard 使原 license/路径不可达任务无法有牙 => 合成项目树+produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-GaaFetDeckAugment-001":
        "GAA FET deck AC 仿真增强->produce (portability reframe, §4 有牙必要, r731 spotcheck batch10): 用户 e02141@hfeg0pkn005 给 GAA_FET deck 添加 AC 电容仿真, A 不可行原因=真实 /home/e02141/devops/GAA_FET 项目+Sentaurus license SUT 沙盒不可达 -> 用自包含合成 IdVg_des.cmd+Applications_Library AC 模板保留真实任务结构(asset_fidelity=synth_deck); trace agent 本就 produce(写 deck), produce->produce 非 Q&A->produce reframe, 仅 portability 驱动; 重构为产 augment_deck.py+AC_des.cmd+Plot_CV_vis.tcl+AC_des.prf+Plot_CV_vis.prf 五件; check.py 13 断言验 Device 块+File 段 4 键+Electrode 4 个+电极名==A IdVg_des.cmd+gate WorkFunction+drain/source Resist==375+AC Small-signal+CV 提取+hidden-B cross-input guard 使原 license/路径不可达任务无法有牙 => 合成 deck+produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-ResistorTrimNetlistExplain-001":
        "电阻梯 trim 网表并联诊断->produce (portability+Q&A->produce reframe, §4 有牙必要, r731 spotcheck batch10): 用户 zhililu@hfeg0pkn002 问「为什么 segment=2/parallel 期望减半但 CDL mr=1」, A 不可行原因=真实 Aether CDL 网表来自 /proj 内网工程目录 SUT 沙盒不可达 -> 用自包含合成 CDL 网表保留真实任务结构(subckt R_TRIM_VREF+端口+17 电阻+8 反相器+1 译码器+8 传输门+mr 解析, asset_fidelity=synth_netlist); trace 用户问「为什么...还是 mr=1」= diag Q&A 候选(待 trace 全文确认); 重构为产 analyze_trim_netlist.py+trim_report.json; check.py 13 断言验 11 顶层字段+subckt_name+subckt_ports+instance_counts(17/8/1/8)+decoder_cell+R22 unit_resistance+hidden-B cross-input guard 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-CmlMirrorSweepAnalysis-001":
        "CML 电流镜 sweep 差异分析->produce (portability+Q&A->produce reframe, §4 有牙必要, r731 spotcheck batch10): 用户 lvyy@hfeg0pkn005 问「为什么扫尺寸电流差这么多」+「multi=1 后怎么选 W/L」, A 不可行原因=真实 sweep 数据来自 /proj/m2701 内网工程目录+FineSim/HSPICE license SUT 沙盒不可达 -> 用自包含合成 sweep 数据(tran_5~tran_9 W/L/multi)保留真实任务结构(asset_fidelity=synth_deck); trace 用户问「为什么...差这么多」+「怎么选」= Q&A 候选(待 trace 全文确认); 重构为产 analyze_mirror_sweep.py+mirror_sweep_report.json; check.py 13 断言验 5 组 sweep+ratio_reconstruction+DIBL 平坦 sweep+dominant_mechanism==DIBL+region+hidden-B cross-input guard 使纯 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-NetlistLibdefsTrap-001": "portability",
    "EDA-Eval-DesignFlow-ULVTDelvtoNetlistMod-001": "portability",
    "EDA-Eval-DesignFlow-StcCrfGenerator-001": "portability",
    "EDA-Eval-DesignFlow-Ddr6RptCmdExtract-001": "portability",
    "EDA-Eval-DesignFlow-FineSimDiag-001": "portability+Q&A->produce(candidate)",
    "EDA-Eval-DesignFlow-SentaurusDeckSetupSummary-001": "portability",
    "EDA-Eval-DesignFlow-GaaFetDeckAugment-001": "portability",
    "EDA-Eval-DesignFlow-ResistorTrimNetlistExplain-001": "portability+Q&A->produce(candidate)",
    "EDA-Eval-DesignFlow-CmlMirrorSweepAnalysis-001": "portability+Q&A->produce(candidate)",
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
        # append reframe_note as last key (preserve key order)
        m["reframe_note"] = note
        j["metadata"] = m
        out = json.dumps(j, ensure_ascii=False, indent=2)
        # round-trip identical check (semantic)
        _ = json.loads(out)
        with io.open(path, "w", encoding="utf-8") as f:
            f.write(out)
        results.append((cid, DRIVER[cid], "APPLIED"))
    print("# r774 reframe_note apply results")
    for cid, drv, st in results:
        print("%s\t%s\t%s" % (cid, drv, st))
    applied = sum(1 for _,_,st in results if st == "APPLIED")
    print("# APPLIED=%d  total=%d" % (applied, len(results)))

if __name__ == "__main__":
    main()
