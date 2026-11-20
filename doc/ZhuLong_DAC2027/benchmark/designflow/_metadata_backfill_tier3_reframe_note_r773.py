#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r773 metadata-debt backfill tier3 (reframe_note) apply — spotcheck batch9 (r730, 8 cases).
Adds metadata.reframe_note to 8 keep_reframe_for_teeth cases that lack it.
Source of truth = cases/B/<case>.json (EDA-Flow-Bench repo).
Preserves JSON key order (reframe_note appended as last metadata key), indent=2, ensure_ascii=False.
reframe_note text constructed from r730 spotcheck9 per_case_reasoning + trace_source(user@host) + k_check.
"""
import json, os, sys

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

# case_id -> reframe_note text
NOTES = {
"EDA-Eval-DesignFlow-VlshftParamOpt-001":
 "参数扫描优化->produce (§4 有牙必要, r730 spotcheck batch9): 用户 hairuizh@hfeg0pkn001 做电平转换器参数扫描优化, A 不可行原因=foundry GL22 PDK /proj/m2701 不可沙盒外访问 -> 用自包含 LEVEL=1 MOS 模型替代 PDK(asset_fidelity=synth_deck) 保留完整优化问题结构(5 参数/8 测量目标/双模目标函数/area 排除 Xindrv+Xoutdrv); 重构为产 params.json + HSPICE deck 真跑 hidden B; check.py 12 断言验 5 参数+范围+精度 0.1+HSPICE exit0+8 测量全有效+area 一致+目标函数一致+优于 baseline+cross-input guard 使纯参数扫描优化 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
"EDA-Eval-DesignFlow-BiasOpAnalysis-001":
 ".op 仿真分析->produce (§4 有牙必要, r730 spotcheck batch9): 用户 joeyl@hfeg0pkn004 做 opamp 钳位失效根因 .op 分析+网表修改, asset_fidelity=trace_faithful_op_synthesized_hidden_b(A 档 prompt trace-faithful 用真实 subckt 命名 WCKIbBias_Res/WCKIbBias_Opamp/Bias+器件 XM9/XM10/XM13/XM14, hidden B 档 synthesized R=20u/负载 w=4u/vfb 0.285-0.3 反背题); 重构为产 bias_analyzer.py+analysis_report.json+modified_netlist.sp; check.py 13 断言验 5 corner vfb/vcm/vbn 实算+xm9 linear+xm10 subth+opamp_gain+max_min_ratio+root_cause+fix_strategy 使纯 .op 分析 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
"EDA-Eval-DesignFlow-PcpnScriptAnalysis-001":
 "脚本结构化分析->produce (§4 有牙必要, r730 spotcheck batch9): 用户 pdsong@hfeg0plg74 分析 PCPN 脚本, A 不可行原因=真实 v2 脚本在 /proj/drjqa 内网工程目录 SUT 沙盒无 /proj 权限不可达 -> 从 trace 还原任务意图用同族可读 RATIO 变体 grepPCPNLoc_ratio.py V0.0.9 作输入 A, hidden B 在版本号/默认值/选项名/选项串/输出文件名/记录前缀/过滤图层名上取值不同结构相同(asset_fidelity=B-synthesized 反背题, 参考解为通用正则/文本解析器不硬编码任一变体值); 重构为产通用解析器; check.py 16 断言验 zip+subprocess exit0+JSON+14 顶层键+latest_version V0.1.0+keep_ratio 0.25+floor 5+getopt gK:F:+cli -K/-F+output instPinSamp.txt 全 cross-input guard 使纯脚本分析 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
"EDA-Eval-DesignFlow-McVoltMarginSummary-001":
 "MC 电压裕量汇总->produce (§4 有牙必要, r730 spotcheck batch9): 用户 stephens@hfeg0plg58 做 MC 电压裕量汇总(characterization 域), asset_fidelity=synth_deck(真实 MC CSV 结构保留: 18 alter*300 samples+汇总行+.alter 节段映射); 重构为产 mc_margin_summary.csv+analyzer.py; check.py 14 断言验 表头+6 corners*3 stats=18 行+corner 标签+VMLH_LV/VMHL_LV/VMLH/VMHL avg 匹配+min<=avg<=max+mV 量级+cross-input guard B avg!=A+B corner!=A+脚本 B exit0 使纯汇总 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
"EDA-Eval-DesignFlow-Mt0CharExtract-001":
 ".mt0 提取汇总->produce (§4 有牙必要, r730 spotcheck batch9): 用户 fan1yang@hfeg0pkn005 做 .mt0 提取汇总(characterization 域), asset_fidelity=synth_deck(真实 .mt0 文件名格式+config_signal 重命名结构保留); 重构为产 extract_mt0_table.py; check.py 12 断言验 hidden B exit0+CSV 3 行+必需列+FEATURE HC2P_C1R2W3BW2RE2+words 256 bits 36+mux 2 bank 4+3 PVT process/volt/temp+测量值 oracle 一致+重命名映射+cross-input guard B!=A 使纯提取 Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
"EDA-Eval-DesignFlow-NetlistChlMirrorDiff-001":
 "netlist 差异比对+补丁->produce (§4 有牙必要, r730 spotcheck batch9): 用户 kevin3d@hfeg0pkn002 比对两 netlist 差异, A 不可行原因=原 netlist 100MB+含晶圆设计不可沙盒外访问 -> 用自包含小型 HSPICE 网表(LEVEL=1 MOS)保留真实子电路命名与 L/R 拆分结构(asset_fidelity=synth_netlist); 重构为产 compare_and_patch.py+report.json+netlist_B_patched.sp; check.py 12 断言验 missing_subckts 含 AG_VwlnActAmpChL+pumpcore_chl B 错挂+pumpcore_chr R 未破坏+chl_vs_ch_diff L/R 镜像+hidden B' 重跑 exit0+B' missing 含 AG_VwlnActAmpChL(泛化)+B' patched 含且仅含一个 .subckt 定义 使纯 diff Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
"EDA-Eval-DesignFlow-SimRunScriptDiff-001":
 "脚本 diff+根因诊断->produce (§4 有牙必要, r730 spotcheck batch9): 用户 ericw@10.129.32.80 做仿真脚本 diff+错误根因诊断, asset_fidelity=synth_deck(真实脚本结构+调用链保留: PROJECT/MODEL_PATH/CORNERS/NETIGNORE_FILE/setupIGZO/createIgnoreCtrlFile); 重构为产 analyze.py+diff_report.json+diag_report.json; check.py 12 断言验 schema 键+PROJECT 默认值差异+MODEL_PATH 差异+CORNERS 3vs4+NETIGNORE_FILE 差异+setupIGZO igzo only+ctrl_tool_version+drdxq 根因=createControlFile_v3 非 matrixrun 本身 使纯 diff Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
"EDA-Eval-DesignFlow-SimErrSubcktRefDiag-001":
 "子电路引用缺失诊断->produce (§4 有牙必要, r730 spotcheck batch9): 用户 ericw@hfeg0plg07 诊断 si.out 子电路引用缺失, asset_fidelity=synth_deck(真实 si.out 报错格式+incFile .subckt 命名约定+GAA level=72 器件结构保留); 重构为产 analyze.py+diag_report.json; check.py 12 断言验 simulator/errors_total/missing_subckts/summary 键+errors_total==si.out 行数+missing_subckts name 集合精确匹配+parent_cells+netlist_lines+occurrence_count+definition_status(命名不一致 vs 真缺失)+defined_as 变体名 使纯 diagnose Q&A 无法有牙 => 重构为 produce 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
}

def main():
    applied=[]; skipped=[]; failed=[]
    for cid, note in NOTES.items():
        fn = os.path.join(CASES_DIR, cid+".json")
        if not os.path.exists(fn):
            failed.append((cid,"file missing")); continue
        try:
            m = json.load(open(fn))
        except Exception as e:
            failed.append((cid,"load: %s"%e)); continue
        meta = m.get("metadata", {})
        if meta.get("reframe_note"):
            skipped.append((cid,"already has reframe_note")); continue
        meta["reframe_note"] = note
        m["metadata"] = meta
        s = json.dumps(m, ensure_ascii=False, indent=2)+"\n"
        open(fn,"w").write(s)
        applied.append(cid)
    print("APPLIED (%d):"%len(applied))
    for c in applied: print("  +",c)
    print("SKIPPED (%d):"%len(skipped))
    for c,r in skipped: print("  ~",c,r)
    print("FAILED (%d):"%len(failed))
    for c,r in failed: print("  x",c,r)
    # exit non-zero if any failure
    sys.exit(1 if failed else 0)

if __name__=="__main__":
    main()
