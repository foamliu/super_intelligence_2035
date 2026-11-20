#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-StaFlowScaffold-001 to EDA-Eval-DesignFlow_A.jsonl."""
import os, json, re

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-StaFlowScaffold-001"
REF = os.path.join(REPO, "reference", CASE)
AST = os.path.join(REPO, "assets", CASE)

check_py = open(os.path.join(REF, "check.py"), encoding="utf-8").read()
prompt = open(os.path.join(AST, "prompt.txt"), encoding="utf-8").read()

test_rationale = (
    "20 条断言：① submit.zip 恰含 build_sta_flow.py + report_A.json 两件 "
    "② build_sta_flow.py 可 py_compile "
    "③ 候选构建器对可见 A bundle（lint_flow_A+feint_ref_A）运行 exit 0 且 outA 含 config/run/data/script/all_out 五个核心子目录 "
    "④ outA/all_out/v1.0_Latest/ 含 filelist/log/out_src/QA/report 五子目录 "
    "⑤ outA/run/ 含 CXDP_STA_CFG、sta.tcl、sta_setup.tcl、Makefile 四文件及 CXDP_DESIGN_CFG、CXDP_PROJ_CFG 两符号链接 "
    "⑥ outA/data/ 含 cla_top.netlist.f、cla_top.sdc、sta_override.tcl 三文件 "
    "⑦ outA/script/sta_qa_chk.pl 经 perl -c 语法校验通过 "
    "⑧ outA/run/sta.tcl 经 tclsh info complete 返回 1（脚本完整闭合） "
    "⑨ outA/run/sta_setup.tcl 经 tclsh info complete 返回 1 "
    "⑩ outA/run/Makefile 经 make -n help 退出 0（语法可解析） "
    "⑪ outA/run/sta.tcl 含 PrimeTime 命令集 read_sdc/update_timing/report_timing "
    "⑫ outA/run/Makefile 含 pt_shell 与 bsub（LSF 队列）引用 "
    "⑬ outA/run/CXDP_STA_CFG 含 CXDP_DESIGN_NAME=cla_top、STA_PBA=gbv、STA_CORNER=、CXDP_PROJ_TAG=v1.0_Latest "
    "⑭ outA 含 README.md 与 install.sh 且 install.sh 经 bash -n 语法校验通过 "
    "⑮ report_A.json（zip 内）解析为 JSON 且 design==cla_top、tag==v1.0_Latest、pba==gbv、mcmm==false "
    "⑯ 候选构建器对隐藏 B bundle（lint_flow_B+feint_ref_B）运行 exit 0 且 outB 含五个核心子目录 "
    "⑰ 跨输入守卫：outB 的 CXDP_STA_CFG design==uart_top 且不含 cla_top（自适应，非硬编 A） "
    "⑱ 跨输入守卫：outB 含 mcmm/ 子目录而 outA 不含（B 独有结构被传播） "
    "⑲ 跨输入守卫：outB sta_setup.tcl PBA==exhaustive 而 outA sta_setup.tcl PBA==gbv "
    "⑳ 跨输入守卫：outB all_out tag==v2.1_Latest 且不含 v1.0_Latest（tag 自适应，非硬编 A）"
)

trace_source = {
    "user": "e0046913",
    "host": "hfeg0pkn003",
    "session_file": "1793618961003_q11i6.messages.json",
    "match_count": 874,
    "real_task_summary": (
        "Post-synthesis STA flow directory scaffolding (digital) on hfeg0pkn003 "
        "(e0046913); user turn #0 verbatim: 「/proj/lacaa/TV1_digital/simdir/yutingq/"
        "CXDP/cla_top/lint 仔细阅读该目录下的文件层次和结构，以cla_top的lint flow为参考，"
        "为我构建一个相同文件层次结构的sta flow。（sta flow的脚本参考来源为/proj/lacaa/TV1_digital/"
        "simdir/yutingq/feint）」 -- clean task request (construct an STA flow dir tree "
        "mirroring an existing lint flow, referencing feint PrimeTime scripts), no root "
        "cause / fix given => A-grade rule 2 OK => A-grade faithful. 178-msg session; "
        "assistant read the lint flow dir tree + feint PT scripts, then editor-wrote a "
        "mirrored STA flow tree under /home/e0046913/cla_top_sta/ (run/{CXDP_STA_CFG, "
        "sta.tcl, sta_setup.tcl, Makefile}, data/{cla_top.netlist.f, cla_top.sdc, "
        "sta_override.tcl}, script/sta_qa_chk.pl, all_out/v1.0_Latest/{filelist,log,"
        "out_src,QA,report}/, README.md, install.sh), validating with make -n help / "
        "perl -c / tcl brace balance; user accepted (engaged, requested Chinese version, "
        "explicitly preserved cla_top_sta/ on home cleanup). This case scopes a generic "
        "STA flow scaffolding builder (verb: sta-flow-scaffold), distinct from all "
        "existing shard-A verbs (netlist-port-connectivity-extract / lib-to-parm / "
        "synth-upf-diagnose / apr-stamp-fix / flat-net / apr-setup-audit / apr-log-audit "
        "/ vcs-equiv / vcs-makefile / itf-compare / calibre-pdf2md)."
    ),
}

attachments = [
    "assets/EDA-Eval-DesignFlow-StaFlowScaffold-001/lint_flow_A",
    "assets/EDA-Eval-DesignFlow-StaFlowScaffold-001/feint_ref_A",
    "assets/EDA-Eval-DesignFlow-StaFlowScaffold-001/prompt.txt",
    "assets/EDA-Eval-DesignFlow-StaFlowScaffold-001/task_brief.md",
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

# verify + gate
n = 0
with open(jsonl, encoding="utf-8") as f:
    for line in f:
        n += 1
        if CASE in line:
            d = json.loads(line)
            k_rationale = len(re.findall(r"[①-⑳]", d["metadata"]["test_rationale"]))
            k_check = len(re.findall(r"# \(([a-z])\)", d["test"]))
            print("line", n, "task_id=", d["task_id"])
            print("k_rationale=", k_rationale, "k_check=", k_check,
                  "GATE", "PASS" if (k_rationale == k_check and k_check >= 8) else "FAIL")
            print("domain=", d["metadata"]["domain"], "track=", d["metadata"]["track"])
            assert k_rationale == k_check and k_check >= 8, "GATE FAIL"
print("A.jsonl total lines =", n)
