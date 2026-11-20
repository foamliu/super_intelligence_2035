#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-PortCatch-001 to EDA-Eval-DesignFlow_A.jsonl."""
import os, json, textwrap

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-PortCatch-001"
REF = os.path.join(REPO, "reference", CASE)
AST = os.path.join(REPO, "assets", CASE)

check_py = open(os.path.join(REF, "check.py"), encoding="utf-8").read()
prompt = open(os.path.join(AST, "prompt.txt"), encoding="utf-8").read()

test_rationale = (
    "15 条断言：① submit.zip 含 port_catch.py + report_A.json 两件齐全 "
    "② port_catch.py 可 py_compile "
    "③ 候选抓取器对可见 A 网表 nand2_CPSel_A.netlist 目标 nand2_CPSel.XI1 运行 exit 0 "
    "④ A 报告 instance == nand2_CPSel.XI1 "
    "⑤ A 报告 master == nand2LV "
    "⑥ A 报告端口名集合 == {A,B,Y,vbulkn!,vbulkp!,vcc!,vss!}（7 端口） "
    "⑦ A 各端口方向与 .PININFO 一致（A/B:input, Y:output, vbulkn!/vbulkp!/vcc!/vss!:bidir） "
    "⑧ A 端口→连线映射正确（与独立 oracle 对账，如 A→A、vbulkn!→vbn!） "
    "⑨ A 邻居实例提取正确（与独立 oracle 对账，每端口邻居 {inst,terminal,master} 集合一致） "
    "⑩ 候选抓取器对隐藏 B 网表 and3_dly_B.sp 目标 and3_dly.Xg1 运行 exit 0 "
    "⑪ 跨输入守卫：B 报告 master == nand2 且 ≠ A 的 nand2LV "
    "⑫ 跨输入守卫：B 端口名集合 == {P,Q,Z,vcc!,vss!} 且 ≠ A 端口集合 "
    "⑬ 跨输入守卫：B 端口 P 邻居数为 0（primary input，A 无 0-邻居端口） "
    "⑭ 跨输入守卫：B 端口 Z 邻居 == {Xg2 的 P 端子, nand2}（B 特有结构） "
    "⑮ 反硬编：port_catch.py 源码不含 A/B 具体标识字面量（nand2_CPSel/nand2LV/and3_dly/XI0/XI1/Xg1/Xg2/Xg3）"
)

trace_source = {
    "user": "chengk",
    "host": "hfeg0plg74",
    "session_file": "1792136569651_4a8f9.messages.json",
    "match_count": 826,
    "real_task_summary": (
        "CDL/SPICE netlist instance port-connectivity extraction (digital) on "
        "hfeg0plg74 (chengk); user turn #0 verbatim: 「参考路径 "
        "/home/chengk/work/code/wv_trig/port_catch/code/ 下的代码，希望实现以下功能，"
        "输入网表中的一个实例化的层级结构，能够用cck的api实现抓取这个实例化的所有端口和连接的连线，"
        "通过连线关系得到这个实例的输入和输出端口链接到的实例，示例网表的位置在 "
        "/home/chengk/work/code/wv_trig/port_catch/data/nand2_CPSel.netlist」 -- clean task request "
        "(implement a netlist port/net/neighbor extractor using cck API), no root cause / fix given "
        "=> A-grade rule 2 OK => A-grade faithful. 176-msg session; assistant delivered driverFind.tcl "
        "(cck Tcl port-driver finder, 456L) + PortCatch.tcl wrapper under task3_src/, fixing segfault/"
        "missing-model issues; user accepted (final assistant msg '已完成...脚本能自动解决网表加载时的 "
        "missing MOSFET model 编译失败问题'). This case scopes a generic pure-stdlib CDL port/net/neighbor "
        "connectivity extractor (verb: netlist-port-connectivity-extract), distinct from all existing "
        "shard-A verbs (lib-to-parm / synth-upf-diagnose / apr-stamp-fix / flat-net / apr-setup-audit / "
        "apr-log-audit / vcs-equiv / itf-compare / calibre-pdf2md / dc-synth / simlib-idx / power-fill / etc.)."
    ),
}

attachments = [
    "assets/EDA-Eval-DesignFlow-PortCatch-001/nand2_CPSel_A.netlist",
    "assets/EDA-Eval-DesignFlow-PortCatch-001/prompt.txt",
    "assets/EDA-Eval-DesignFlow-PortCatch-001/task_brief.md",
]

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": check_py,
    "prompt": prompt,
    "attachments": attachments,
    "metadata": {
        "trace_source": trace_source,
        "domain": "digital",
        "track": "faithful",
        "test_rationale": test_rationale,
    },
}

jsonl = os.path.join(REPO, "EDA-Eval-DesignFlow_A.jsonl")
with open(jsonl, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended", CASE, "to", jsonl)

# verify
n = 0
with open(jsonl, encoding="utf-8") as f:
    for line in f:
        n += 1
        if CASE in line:
            d = json.loads(line)
            # count assertions in rationale
            import re
            k = len(re.findall(r"[①-⑮⓪]", d["metadata"]["test_rationale"]))
            print("line", n, "task_id=", d["task_id"], "k_rationale=", k, "domain=", d["metadata"]["domain"], "track=", d["metadata"]["track"])
print("A.jsonl total lines =", n)
