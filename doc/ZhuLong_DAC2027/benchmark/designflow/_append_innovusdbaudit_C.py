#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-InnovusDbAudit-001 to EDA-Eval-DesignFlow_C.jsonl."""
import json
import os

CASE_ID = "EDA-Eval-DesignFlow-InnovusDbAudit-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_C.jsonl")
REF = os.path.join(BENCH, "reference", CASE_ID)
ASSETS = os.path.join(BENCH, "assets", CASE_ID)

check_src = open(os.path.join(REF, "check.py")).read()

entry = {
    "task_id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["outputs/submit.zip"],
    "attachments": [
        "assets/%s/task_brief.md" % CASE_ID,
        "assets/%s/flow_audit_manifest.json" % CASE_ID,
        "assets/%s/prompt.txt" % CASE_ID,
    ],
    "prompt": open(os.path.join(ASSETS, "prompt.txt")).read(),
    "test": check_src,
    "metadata": {
        "domain": "pg_layout",
        "track": "synthesized",
        "level": "L1-boundary",
        "layer": "physical_layout",
        "difficulty_tier": "B",
        "direction": "read-only-audit",
        "harness": "cline",
        "task_name": "Innovus digital-backend capability audit classifier",
        "topic": "pg_layout/innovus feasibility audit from full-custom flow manifest",
        "scenario": "全定制(Aether/OA)流程下调查能否用 Innovus 走完整数字后端(布局/电源/CTS/布线/时序/寄生/DRC-LVS/功能一致); 本轮只做现状与可行性审计不实现. 输入 flow_audit_manifest.json(工程/库/工具/约束事实清单) -> 输出 audit_report.json(每阶段 must/conditional/non_must 分类 + PVT校核 + cell覆盖 + blocking_gaps + final_verdict).",
        "test_rationale": "16 条断言：①[a]submit.zip 恰含 1 个 .py(>=400B,UTF-8 无 NUL)且 py_compile 通过 ②[b]在隐藏 B 上跑 exit0 + stdout 为合法 JSON 对象 + 顶层 9 键(circuit/pvt_check/cell_coverage/constraints/stages/innovus/blocking_gaps/final_verdict/stage_order)齐全 ③[c]circuit 判定与 B manifest 一致(type=sequential 因 has_flop、n_masters、n_instances、flop_masters 逐项对账) ④[d]CTS 分类: B 含触发器 -> class=must 且 status≠n_a(击穿 always-non_must) ⑤[e]PVT mismatch 检测: B 时序库 0.9V/-40C vs 目标 pvcc 0.9 temp 25 -> verdict=mismatch 且 mismatches 含 temperature 项(击穿 always-match) ⑥[f]cell 覆盖: B 12/12 full, covered_count==n_masters, missing_count==0, ratio==1.0 ⑦[g]placement: B 有 LEF -> status=satisfied(击穿 always-conditional/missing) ⑧[h]timing_opt: B 覆盖 full+SDC 但 PVT mismatch -> status=satisfied_with_pvt_mismatch(击穿 always-satisfied 与 always-missing) ⑨[i]innovus: B installed+license+startup_verified 三项 True(击穿 always-False) ⑩[j]parasitic: B StarRC+ITF 或 Quantus -> satisfied(击穿 always-missing) ⑪[k]blocking_gaps: B LEF 就绪 -> gaps==[](击穿 always-[LEF]) ⑫[l]跨输入 B2(组合+LEF 缺): CTS non_must/n_a + placement conditional + gaps==[LEF](击穿 always-must-cts 与 always-satisfied-placement) ⑬[m]跨输入 B3(组合+LEF 有+PVT 匹配): placement satisfied + pvt match + mismatches==[] + timing_opt satisfied(击穿 always-mismatch 与 always-conditional) ⑭[n]跨输入 B4(Innovus 未装): blocking_gaps 含 Innovus + final_verdict=infeasible_innovus_missing(击穿 always-feasible) ⑮[o]确定性: B 连跑 3 次 md5 完全一致 ⑯[p]A<->B guard: A 跑出 combinational+CTS non_must+gaps==[LEF]+feasible_pending_lef, 且 A 与 B 的 n_masters/gaps 必不同(击穿 fake_print_expected 硬编码单输出), 且 osc_period(1.59)不被当作 max_delay(0.5)(击穿混淆 osc 与约束)",
        "trace_source": {
            "user": "johnl",
            "host": "hfeg0pfn119",
            "session_file": "1792489769571_ch2cw.messages.json",
            "match_count": 255,
            "real_task_summary": "johnl/hfeg0pfn119(10.129.x), mc=255, keywords innovus:645;schematic:233;netlist:145;calibre:66;hspice:36;synthesis:27, tools run_approved_command:32/editor:33/read_files:13/list_allowed_files:7/run_commands:2/search_codebase:1, 158 msgs/0.95MB. USER#0 逐字(A-档 seed 提出目标, 未给根因/修复)「全定制环境下 Innovus 完整数字后端能力审计: 从当前已有全定制流程出发, 调查能否用 Innovus 完成指定电路的完整数字后端流程, 定位可复用的数据/工具/真实缺项, 本轮只调查现状和可行性不实现, 区分必须/条件/非必须三类」; USER#135「继续」=无信息. assistant read_files+run_approved_command(只读调查: lib.defs/emy2netlist/asOut/StarRC lpe_RCC/Calibre runset/TECHLIB tech.db/Innovus modulefile)+editor(在 innovus_audit/ 写 inspect_e/find_inno/phys_lib/proj_lib/check_map/lib_phys/cell_phys/tech_inno/innovus_s/cell_cove 等审计脚本)+run_commands(env -i 启动 Innovus 验证). 关键发现: mapped.v=纯组合(addr_to_rowcol_v7, N[8:0]->row/col/valid, 18 LVSx master, 107 实例, 无触发器->CTS 不适用); 时序库 SS_0p98_m40c_lvs.db(SS/0.98V/-40C, PrimeLib 2023.12, 18/18 覆盖) vs 目标 SPICE pvcc=1.1/pvdd1=1.8/pvdbias=0.9323/25C -> PVT mismatch; stdcells_ac 有 OA layout view 但无现成 LEF, genlef 可用 -> placement conditional(缺 LEF 可生成); Innovus 23.1 已装(INNOVUS231 v23.32-s091_1, license invs, startup_verified, 含 NanoRoute/IQuantus/OA22.61); RC=CalibreLPE+StarRC(ITF/nxtgrd G5CIP, corner TYP_25); DRC/LVS=Calibre runset cxmtG5_CIP + Empyrean Argus; 用户 Innovus 工程 flow.tcl 完整但缺 tech.lef+stdcells_ac_comb.lef; 唯一 blocking_gap=LEF; final=feasible_pending_lef. gold=审计结论(AUDIT_REPORT.md + audit_classifier), 依赖 live Innovus+live drcoa OA 库(/proj/drcoa/V0 内网) -> .75 沙盒不可达 -> A-档 disqualified(tooling) -> B-档 synthesized L1-boundary(纯离线 manifest->audit 分类器生成). 与 r83 PwrGlobalsGen/r82 PGReproGuide(规划/指南)正交——本案是 read-only 能力审计分类(每阶段 must/conditional/non_must + PVT/覆盖/缺口), 不生成 PG 实现代码."
        }
    }
}

# validate json roundtrip
_ = json.dumps(entry, ensure_ascii=False)

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# report
with open(JSONL) as f:
    n = sum(1 for _ in f)
print("appended %s; jsonl_C now %d lines" % (CASE_ID, n))
print("test field bytes:", len(check_src))
