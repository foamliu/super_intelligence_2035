#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-StarRCDspfFlow-001 to EDA-Eval-DesignFlow_A.jsonl."""
import json, os, re

CASE = "EDA-Eval-DesignFlow-StarRCDspfFlow-001"
REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
BENCH = os.path.join(REPO, "benchmarks", "EDA-Eval-DesignFlow")
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")
REF = os.path.join(BENCH, "reference", CASE)
ASSETS = os.path.join(BENCH, "assets", CASE)

check_src = open(os.path.join(REF, "check.py")).read()

rationale = (
    "14 条断言："
    "① submit.zip 含 5 个交付文件(starrc_dspf.cmd/spf_layers.py/run_starrc_dspf.sh/run_analysis.sh/filelist.f) "
    "② 两个 run 脚本通过 bash -n 语法检查且可执行 "
    "③ python3 spf_layers.py 真跑可见 A dspf 成功退出(L2 真跑) "
    "④ A 报告正确性: 6 电阻 + 正确层映射 + ALL RESISTORS PARSED PASS(L2) "
    "⑤ 注入变异 dspf(RRA1 lvl 1->3)解析层应为 M3 非 M1(击穿硬编码假打印,L2) "
    "⑥ 隐藏 B dspf(异构层集 M4/M5/M6/CO/PO+netB_*+RBT*)+候选 parser 真跑成功且 7 电阻层正确(交叉输入护栏,parser 未硬编码 A 层图,L2) "
    "⑦ starrc_dspf.cmd 含完整 DSPF 关键词集(NETLIST_FORMAT:SPF/GDS_FILE/TCAD_GRD_FILE/MAPPING_FILE/NETLIST_FILE/NETLIST_MINRES/COUPLING_) "
    "⑧ starrc_dspf.cmd 经 @placeholder@ 参数化且无 /home/ 硬编码(注释行不计) "
    "⑨ run_starrc_dspf.sh 参数化(module load STARRC_MODULE)且无 /home/ 硬编码 "
    "⑩ run_analysis.sh 参数化(SPF_FILE/argv)且无 /home/ 硬编码 "
    "⑪ spf_layers.py 参数化(argv[1] 或 SPF_FILE env)且无 /home/ 硬编码 "
    "⑫ filelist.f 列出 .spf+脚本且无 /home/ 硬编码 "
    "⑬ run_starrc_dspf.sh --check-cmd 真跑(fake StarXtract fixture)成功调用 starrc 并打印 STARRC_INVOKED(L2 真跑,击穿不调用 starrc 的桩脚本) "
    "⑭ spf_layers.py 在 A 上 3 次重跑 stdout 完全一致(确定性 PASS)"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": open(os.path.join(ASSETS, "prompt.txt")).read(),
    "attachments": [
        {"name": "prompt.txt", "source": "prompt.txt", "desc": "StarRC DSPF 抽取流程 + SPF 电阻层分析任务说明"},
        {"name": "task_brief.md", "source": "task_brief.md", "desc": "交付接口与文件位置(<=3 行)"},
        {"name": "dspf_A/dspf_A.spf", "source": "dspf_A/dspf_A.spf", "desc": "可见 DSPF 示例(M1/M2/M3/PO/NW 多层电阻)"},
        {"name": "feint/starrc_dspf_partial.cmd", "source": "feint/starrc_dspf_partial.cmd", "desc": "StarRC 命令文件残缺模板(硬编码 /home + 缺 DSPF 选项,待修复)"},
        {"name": "feint/spf_layers_partial.py", "source": "feint/spf_layers_partial.py", "desc": "SPF 解析器残缺模板(仅读 header + 硬编码单层,待修复)"},
        {"name": "hidden/hidden_manifest.json", "source": "hidden/hidden_manifest.json", "desc": "隐藏输入 B 清单(不进 SUT 沙箱)"},
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["scripts/starrc_dspf.cmd", "scripts/spf_layers.py", "run/run_starrc_dspf.sh", "run/run_analysis.sh", "filelist.f"],
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "e0045488",
            "host": "hfeg0pkn002",
            "session_file": "1792386615426_npf2k.messages.json",
            "match_count": 103,
            "real_task_summary": "StarRC DSPF flow: 用户原话 'I want to work on dspf flow. Now I need to know some parameters or options to use StarRC' + 'what does lvl mean here' + 'tell me what layer each Resistor is on' -> 助手交付 starrc_dspf.cmd(StarRC DSPF 命令文件)+ spf_layers.py(.spf 电阻层解析器)"
        },
        "domain": "pnr_signoff",
        "verb": "starrc-dspf-flow-build",
        "level": "L2",
        "track": "B",
        "test_rationale": rationale,
        "hidden_input": {
            "b_path": "hidden/dspf_B/",
            "b_files": ["dspf_B.spf"],
            "diff_dims": ["layer_set(M4/M5/M6/CO/PO vs M1/M2/M3/PO/NW)", "nets(netB_* vs netA_*)", "resistor_names(RBT* vs RRA*)", "same_dspf_format", "same_parsing_requirement"]
        },
        "l2_real_run": "check.py L2 真跑 = subprocess 真跑 python3 spf_layers.py + bash run_starrc_dspf.sh --check-cmd: (c)(d) python3 跑可见 A dspf -> 6 电阻 PASS; (e) 变异 dspf(RRA1 lvl 1->3) -> 期望 M3 非 M1(击穿假打印); (f) 隐藏 B dspf(异构层集)+候选 parser -> 7 电阻层正确(交叉输入护栏); (m) fake StarXtract fixture 真跑 run_starrc_dspf.sh --check-cmd -> STARRC_INVOKED; (n) A 上 3 次重跑一致. 静态 (a)(b)(g)(h)(i)(j)(k)(l) 纯字符串/正则断言. .75 实测确认: StarXtract R-2020.09-SP5-4 真跑 resolved cmd -> SX-0271(unknown keyword) count=0, 仅 SX-0967/0969(data-missing,因无真实 ITF/GDS/MAP) -> 命令文件语法 100% 合法; python3 3.7.1 parser on A(6)/B(7) PASS + 3x md5 一致(确定性). judge env 无真实 StarRC -> check.py (m) 用 fake StarXtract fixture(同 njd2w StarRCFlow-001 模式).",
        "harness": "cline",
        "notes": "B 档 synthesized. 真实 trace npf2k (e0045488@hfeg0pkn002, mc=103) 用户原话 'I want to work on dspf flow... what does lvl mean... tell me what layer each Resistor is on' -> 助手交付 starrc_dspf.cmd(StarRC DSPF 命令文件,全注释模板含 NETLIST_FORMAT:SPF)+ spf_layers.py(.spf 电阻层解析器). 本 case 重构 design_flow: 给定 dspf_A(可见 DSPF 示例), SUT 交付参数化 StarRC DSPF flow(5 文件), 判分真跑 python3 parser + fake StarXtract 验证解析+交叉输入+变异+确定性. 关键修正: trace 的 cmd 模板含多个未经验证的关键词(CONNECTION/DEF_FILE/LAYER_MAP_FILE/NETLIST_PARASITIC_RESISTOR_MODEL/NETLIST_INDUCTANCE/OUTPUT_FORMAT/OUTPUT_SPF_FILE/COUPLING_TO_GROUND/MAX_OPENS),.75 实测 StarXtract R-2020.09 均报 SX-0271 unknown keyword; 逐一探测后保留 24 个 StarRC 真接受关键词(TCAD_GRD_FILE/TEMPERATURE_SENSITIVITY/OPERATING_TEMPERATURE/GDS_FILE/MAPPING_FILE/NETLIST_FILE/NETLIST_FORMAT:SPF/NETLIST_INSTANCE_SECTION/NETLIST_NODE_SECTION/NETLIST_GROUND_NODE_NAME/NETLIST_NODENAME_NETNAME/NETLIST_PRINT_CC_TWICE/NETLIST_CONNECT_OPENS/NETLIST_DELIMITER/NETLIST_MINCAP/NETLIST_TOTALCAP/NETLIST_MINRES/NETLIST_MINRES_HANDLING/NETLIST_REMOVE_DANGLING_BRANCHES/NETLIST_REMOVE_LOOPS/COUPLING_ABS/COUPLING_REL/COUPLING_REPORT_FILE/COUPLING_REPORT_NUMBER). run 脚本用 StarXtract <cmd>(positional) 非 starrc_shell -clean -cmd_command_file(后者 SX-010 拒绝). 资产 /proj/drexp/.../invBx2.spf 权限拒绝(同 tzth7/FlatNet 模式) -> B 档合成 dspf_A(M1/M2/M3/PO/NW)+dspf_B(M4/M5/M6/CO/PO) 同格式异构."
    }
}

# byte-sync guard: test field must equal disk check.py
assert entry["test"] == check_src, "test field != disk check.py"
# rationale prefix gate
assert entry["metadata"]["test_rationale"].startswith("14 条断言："), "rationale prefix"
# count circled marks ①..⑭
marks = re.findall(r"[①-⑮]", entry["metadata"]["test_rationale"])
assert len(set(marks)) == 14 and marks == list("①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭"), "rationale marks: %s" % marks
print("GATE: k_rationale=14 == k_check=14 >= 8  PASS")
print("test bytes:", len(entry["test"]))

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended to", JSONL)

# verify: last line is this case, test == check.py bytes
with open(JSONL) as f:
    lines = f.readlines()
last = json.loads(lines[-1])
assert last["task_id"] == CASE
assert last["test"] == check_src
assert last["metadata"]["test_rationale"] == rationale
print("verified: %d lines, last=%s, test==disk check.py OK" % (len(lines), CASE))
