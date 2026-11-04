#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-DFTTestmaxFlow-001 to EDA-Eval-DesignFlow_A.jsonl."""
import json, os, sys

CASE = "EDA-Eval-DesignFlow-DFTTestmaxFlow-001"
REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
BENCH = os.path.join(REPO, "benchmarks", "EDA-Eval-DesignFlow")
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")
REF = os.path.join(BENCH, "reference", CASE)
ASSETS = os.path.join(BENCH, "assets", CASE)

check_src = open(os.path.join(REF, "check.py")).read()

rationale = (
    "14 条断言："
    "① submit.zip 含 5 个交付文件(dft_compile.tcl/atpg.tcl/tb_*.v/run_dft.sh/sim_filelist.f) "
    "② run_dft.sh 通过 bash -n 语法检查 "
    "③ VCS 编译+运行可见 A rtl 与候选 testbench 成功(L2 真跑) "
    "④ A 运行日志含 ALL TESTS PASSED 且无 FAIL 标记(L2) "
    "⑤ 注入 bug 的 dft_top(led_out 恒 0)+候选 testbench 运行日志含 FAIL(testbench 检测到注入 bug，击穿只打印期望串的假提交，L2) "
    "⑥ 隐藏 B rtl(异构同端口同功能)+候选 testbench VCS 编译运行成功(交叉输入护栏，testbench 未硬编码 A 内部层次引用，L2) "
    "⑦ dft_compile.tcl 含完整 DFT 命令集(set_dft_configuration/set_scan_configuration/5 类 set_dft_signal/compile/insert_dft/dft_drc/report_scan_path/create_test_protocol/write -format verilog) "
    "⑧ atpg.tcl 含完整 ATPG 命令集(read_netlist/run_build_model/read_test_protocol/run_drc/set_fault_type -stuck_at/add_faults -all/create_patterns -auto/write_patterns) "
    "⑨ dft_compile.tcl 经环境变量参数化(env(DESIGN_NAME))且无 /home/ 硬编码绝对路径 "
    "⑩ atpg.tcl 经环境变量参数化且无 /home/ 硬编码绝对路径 "
    "⑪ run_dft.sh 参数化(引用 DESIGN_NAME)且无 /home/ 硬编码绝对路径 "
    "⑫ testbench 含功能模式阶段 + 扫描测试阶段(scan_en=1 或 Phase 2 头) + 错误计数 PASS/FAIL 汇总 "
    "⑬ sim_filelist.f 列出 .v 文件含 testbench 且无 /home/ 硬编码绝对路径 "
    "⑭ A 上 VCS 重跑 3 次结果一致(确定性 PASS)"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": open(os.path.join(ASSETS, "prompt.txt")).read(),
    "attachments": [
        {"name": "prompt.txt", "source": "prompt.txt", "desc": "DFT TestMAX flow 搭建任务说明(中端 flow 开发场景)"},
        {"name": "task_brief.md", "source": "task_brief.md", "desc": "交付接口与文件位置(<=3 行)"},
        {"name": "rtl_A/adder_top.v", "source": "rtl_A/adder_top.v", "desc": "8 位累加器 RTL(带 scan 端口)"},
        {"name": "rtl_A/add_sub_unit.v", "source": "rtl_A/add_sub_unit.v", "desc": "16 位加减单元 RTL(层次化扫描链)"},
        {"name": "rtl_A/dft_top.v", "source": "rtl_A/dft_top.v", "desc": "顶层集成 dft_top(含 DFT 扫描端口)"},
        {"name": "feint/dft_compile_partial.tcl", "source": "feint/dft_compile_partial.tcl", "desc": "DFT Compiler 脚本残缺模板(含 TODO + 硬编码路径，待修复)"},
        {"name": "feint/atpg_partial.tcl", "source": "feint/atpg_partial.tcl", "desc": "TetraMAX ATPG 脚本残缺模板(缺多条命令)"},
        {"name": "feint/tb_partial.v", "source": "feint/tb_partial.v", "desc": "testbench 残缺模板(仅功能无扫描无错误计数)"},
        {"name": "hidden/hidden_manifest.json", "source": "hidden/hidden_manifest.json", "desc": "隐藏输入 B 清单(不进 SUT 沙箱)"},
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["scripts/dft_compile.tcl", "scripts/atpg.tcl", "tb/tb_dft_top.v", "run/run_dft.sh", "sim_filelist.f"],
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "e0030085",
            "host": "hfeg0pkn005",
            "session_file": "1793081732674_ole38.messages.json",
            "match_count": 21,
            "real_task_summary": "DFT TestMAX demo flow 搭建: 用 Synopsys TestMAX(DFT Compiler + TetraMAX)为 8 位累加器小设计做扫描链插入 + ATPG 向量生成 + VCS 功能/扫描仿真 testbench"
        },
        "domain": "verification",
        "verb": "dft-testmax-flow-build",
        "level": "L2",
        "track": "B",
        "test_rationale": rationale,
        "hidden_input": {
            "b_path": "hidden/rtl_B/",
            "b_files": ["dft_top.v", "shift_acc.v", "mult_core.v"],
            "diff_dims": ["submodules(shift_acc+mult_core vs adder_top+add_sub_unit)", "internal_nets", "no_adder_top_no_add_sub_unit", "same_top_name_same_ports", "functionally_equivalent(led_out=key_in+5)"]
        },
        "l2_real_run": "check.py L2 真跑 = subprocess 真跑 VCS on .75 (module load ds/vcs/2023.12-SP2-3 + -timescale=1ns/1ps): (c)(d) VCS 编译+运行可见 A rtl+候选 tb -> ALL TESTS PASSED; (e) 注入 bug(led_out 恒0)+候选 tb -> 期望 FAIL(testbench 检测); (f) 隐藏 B rtl(异构同端口)+候选 tb -> VCS 编译运行成功(交叉输入护栏); (n) A 上 3 次重跑一致. 静态条件 (a)(b)(g)(h)(i)(j)(k)(l)(m) 纯字符串/正则断言. .75 实测确认: A+ref_tb PASS / buggy+ref_tb FAIL / B+ref_tb PASS / buggy+fake_print_tb 无FAIL(击穿假打印).",
        "harness": "cline",
        "notes": "B 档 synthesized. 真实 trace ole38 (e0030085@hfeg0pkn005) 用户原话 'gvim me a DFT testmax demo' → 助手生成完整 DFT TestMAX demo 项目(RTL+dc_shell DFT Compiler 脚本+TetraMAX ATPG 脚本+VCS testbench+run 脚本). 本 case 重构为 design_flow: 给定 rtl_A(带 scan 端口的 8 位累加器), SUT 交付参数化 DFT flow(5 文件), 判分真跑 VCS 验证功能+扫描+bug 检测+交叉输入. .75 VCS license: 默认 vcs/R-2020.12 license 耗尽, 改用 ds/vcs/2023.12-SP2-3(可用). RTL timescale 冲突 -> -timescale=1ns/1ps 标志. testbench race(sys_en 同沿采样) -> negedge 驱动修复."
    }
}

# byte-sync guard: test field must equal disk check.py
assert entry["test"] == check_src, "test field != disk check.py"
# rationale prefix gate
assert entry["metadata"]["test_rationale"].startswith("14 条断言："), "rationale prefix"
# count circled marks ①..⑭
import re
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
