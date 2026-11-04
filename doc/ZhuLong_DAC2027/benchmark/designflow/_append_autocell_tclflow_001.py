#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-AutoCellTclFlow-001 to EDA-Eval-DesignFlow_A.jsonl."""
import os, json, re

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-AutoCellTclFlow-001"
REF = os.path.join(REPO, "reference", CASE)
AST = os.path.join(REPO, "assets", CASE)

check_py = open(os.path.join(REF, "check.py"), encoding="utf-8").read()
prompt = open(os.path.join(AST, "prompt.txt"), encoding="utf-8").read()

test_rationale = (
    "20 条断言：① submit.zip 恰含 generate_autocell_flow.py + report_A.json 两件 "
    "② generate_autocell_flow.py 可 py_compile "
    "③ 候选生成器对可见 A bundle（spec_planar.json+skeleton）运行 exit 0 且 outA 含 8 个 TCL 文件 "
    "④ run.tcl 按 layers/layer_functions/viadefs/globals/rules/place/route 恰 7 行 source 顺序引用 "
    "⑤ layers.tcl 含 tech -process 且 run.tcl 不含 tech -process（tech 创建仅在 layers） "
    "⑥ layers.tcl 对 spec gds_mapping 每层含 create_layer -name 声明 "
    "⑦ layer_functions.tcl 对 spec 已声明层含 set_layer_function -layer -function "
    "⑧ viadefs.tcl 对 spec 每条 via 含 create_viadef -name -cut -lower -upper 且层名匹配 "
    "⑨ globals.tcl 对 spec 每角色含 set_global_net -role VDD/VSS/BODY "
    "⑩ rules.tcl 对 spec 每条规则含 create_rule -name -value "
    "⑪ place.tcl 模式自适应：auto 模式含 set_placer -mode auto 且不含 read_placement "
    "⑫ route.tcl set_router 含 grid_map/pin_template/pin_grid/vdd_connector/vss_connector 五参数 "
    "⑬ run.tcl 含 generate_layout 与 write_layout 调用 "
    "⑭ 8 个 TCL 文件均经 tclsh info complete 返回 1（脚本完整闭合） "
    "⑮ 输出文件不含 TODO 占位符 "
    "⑯ run.tcl write_layout -output 使用 [file join $case_dir ...] 路径格式 "
    "⑰ 候选生成器对隐藏 B bundle（spec_finfet.json）运行 exit 0 且 outB 含 8 个 TCL 文件 "
    "⑱ 跨输入守卫：outB layers.tcl 含 tech -process finfet 且不含 planar（process 自适应，非硬编 A） "
    "⑲ 跨输入守卫：outB 含 A 无的 finfet 专属层（fin/active_fin/nwell_fin/contact_fin）create_layer 声明 "
    "⑳ 跨输入守卫：outB 含 A 无的 finfet 专属规则（min_fin_width/min_fin_spacing）create_rule 声明"
)

trace_source = {
    "user": "miccao",
    "host": "hfeg0plg37",
    "session_file": "1789895218929_1xhgy.messages.json",
    "match_count": 370,
    "real_task_summary": (
        "AutoCell standard-cell TCL flow generation (eda_other) on hfeg0plg37 "
        "(miccao); user turn #0 verbatim: a 9639-char spec '# AutoCell TCL Flow "
        "Generator' defining 8 TCL files (run/layers/layer_functions/viadefs/"
        "globals/rules/place/route), 3 work modes (Create/Modify/Validate), 2 "
        "process profiles (Planar/FinFET), generation+sourcing order, 8 hard "
        "constraints, naming constraints, parameter provenance, and a specific "
        "task tail (generate GDS from netlist, iterate DRC, per-cell logs) -- "
        "clean task request (generate a complete AutoCell standard-cell TCL "
        "flow from spec), no root cause / fix given => A-grade rule 2 OK => "
        "A-grade faithful. 324-msg session; assistant explored AutoCell install "
        "dirs, read reference docs, created batch automation scripts. This case "
        "scopes a generic AutoCell TCL flow generator (verb: "
        "autocell-tcl-flow-gen), distinct from all existing shard-A verbs "
        "(sta-flow-scaffold / netlist-port-connectivity-extract / lib-to-parm "
        "/ synth-upf-diagnose / apr-stamp-fix / flat-net / apr-setup-audit / "
        "apr-log-audit / vcs-equiv / vcs-makefile / itf-compare / calibre-pdf2md)."
    ),
}

attachments = [
    "assets/EDA-Eval-DesignFlow-AutoCellTclFlow-001/references",
    "assets/EDA-Eval-DesignFlow-AutoCellTclFlow-001/assets",
    "assets/EDA-Eval-DesignFlow-AutoCellTclFlow-001/inputs",
    "assets/EDA-Eval-DesignFlow-AutoCellTclFlow-001/prompt.txt",
    "assets/EDA-Eval-DesignFlow-AutoCellTclFlow-001/task_brief.md",
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
        "domain": "eda_other",
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
            
            # roundtrip: check.py on disk == test field in jsonl
            disk_check = open(os.path.join(REF, "check.py"), encoding="utf-8").read()
            assert disk_check == d["test"], "roundtrip FAIL: check.py on disk != test in jsonl"
            print("roundtrip: check.py == test field OK (%d bytes)" % len(disk_check))
            
            # test_rationale starts with "k 条断言"
            assert d["metadata"]["test_rationale"].startswith("20 条断言"), \
                "test_rationale must start with '20 条断言'"
            print("test_rationale starts with '20 条断言' OK")
print("A.jsonl total lines =", n)
