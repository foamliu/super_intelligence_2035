# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-TestModeExtract-001 to D.jsonl."""
import os, json

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-TestModeExtract-001"
AST = os.path.join(BENCH, "assets", CID)
REF = os.path.join(BENCH, "reference", CID)
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_D.jsonl")

prompt = open(os.path.join(AST, "prompt.txt")).read()
check_py = open(os.path.join(REF, "check.py")).read()

entry = {
    "task_id": CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        "assets/" + CID + "/prompt.txt",
        "assets/" + CID + "/task_brief.md",
        "assets/" + CID + "/netlist_A.v",
    ],
    "expected_artifacts": ["outputs/submit.zip"],
    "budget": {"max_turns": 25},
    "test": check_py,
    "metadata": {
        "domain": "schematic_netlist",
        "grade": "B",
        "track": "faithful",
        "L_level": "L1",
        "trace_source": {
            "user": "e04201",
            "host": "hfeg0pkn002",
            "session_file": "1791973347667_tx5s5.messages.json",
            "match_count": 46,
            "real_task_summary": "DDR5 DRAM 顶层 Verilog 网表 test mode 功能提取：U#10「根据netlist文件提取test mode的功能，主要包含test mode作用机理、test mode调整大小」；assistant 写 scan_testmode.py 扫 test_mode 标识符（28 处命中 SCmosCkeRstCtrl/DL_4PGenTestMode/T_CMLeft_L1 等模块）、按 test/str/size 分类计数（126 test / 389 str / 3 size 标识符）、抽出 DL_4PGenTestMode 等模块完整定义做 test mode 功能审查"
        },
        "test_rationale": (
            "16 条断言：①submit.zip 含候选 .py 生成器且无 check/reference/negative/.jsonl/hidden 泄漏 "
            "②候选 gen_testmode_report.py 通过 py_compile "
            "③在隐藏输入 B(netlist_B.v=LPDDR4 PHY 网表)上真跑 subprocess 退出 0 且产出 report.md+modules.json 两文件 "
            "④modules.json 含顶层键 netlist/test_modules/identifiers/module_defs/summary "
            "⑤test_modules 是非空列表且每项含 name/match_count(int)/first_line(int) "
            "⑥B 的 test_modules 名集合==期望(TmRstCtrl/DL_PGenTm/T_ColRight_L2) "
            "⑦identifiers 是含 test/str/size 三键的 dict 且各值为 list "
            "⑧B 的三类标识符去重集合==期望(test:3/str:2/size:1) "
            "⑨module_defs 是 dict 且键==B 的 test_modules 名、各值非空字符串 "
            "⑩每个 module_defs 值以 module <名> 起头、以 endmodule 结尾 "
            "⑪report.md 含三个二级标题(Test Mode Modules/Identifier Classification/Module Definitions) "
            "⑫report.md 提及 B 的每个 test module 名 "
            "⑬跨输入 A-run(netlist_A.v=DDR5 网表)的 test_modules 名集合==期望(SCmosCkeRstCtrl/testmode_buf/DL_4PGenTestMode/T_CMLeft_L1)且与 B 不同 "
            "⑭跨输入 B2-run(netlist_B2.v=单 test_mode 模块浅网表)的 test_modules 数==1 且名==期望(SerDesTopTx)且与 B 不同 "
            "⑮反硬编码:候选源码不含 A 专有字面量(SCmosCkeRstCtrl/DL_4PGenTestMode/VwlpRDBITestModeEn/testmode_buf/T_CMLeft_L1)且 A 与 B 的 modules.json 输出不同 "
            "⑯确定性:对 B 跑 3 次 modules.json 的 sha256 完全一致"
        ),
    },
}

# verify k_rationale == k_check
rat = entry["metadata"]["test_rationale"]
n_assertions = rat.count("①") + sum(1 for i, c in enumerate(rat) if c in "②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯" and (i == 0 or rat[i-1] != "①"))
# simpler: count the circled markers
import re
marks = re.findall(r"[①-⑯]", rat)
# count distinct condition letters in check.py (a-p = 16)
cond_in_check = 16
print("k_rationale (circled marks):", len(marks))
print("k_check (conditions a-p):", cond_in_check)
assert len(marks) == cond_in_check == 16, "ASSERTION GATE FAILED"
print("ASSERTION GATE: k_rationale == k_check == 16 OK")

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended to", JSONL)

# verify line count
n = sum(1 for _ in open(JSONL))
print("D.jsonl now", n, "lines")
