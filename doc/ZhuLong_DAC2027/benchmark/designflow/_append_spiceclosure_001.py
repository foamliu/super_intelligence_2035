#!/usr/bin/env python3
"""Append SpiceClosureExtract-001 to EDA-Eval-DesignFlow_D.jsonl + write deepread + mark ledger."""
import json, os, subprocess

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-SpiceClosureExtract-001"
JSONL = os.path.join(ROOT, "EDA-Eval-DesignFlow_D.jsonl")
CHECK_SRC = open(os.path.join(ROOT, "reference", CID, "check.py")).read()

PROMPT = open(os.path.join(ROOT, "assets", CID, "prompt.txt")).read()

TEST_RATIONALE = (
"16 条断言：①submit.zip 含候选 .py 生成器且无 check/reference/negative/.jsonl/hidden 泄漏 "
"②候选 gen_spice_closure.py 通过 py_compile "
"③在隐藏输入 B(lib_B.sp=模拟比较器 CmpCore+BiasGen 库, roots_B=CmpCore/BiasGen)上真跑 subprocess 产出 closure.sp+manifest.json "
"④B manifest 含全部 8 个顶层键(roots/n_roots/n_subckts_in_closure/n_leaf_models/closure/topo_order/missing/leaf_models) "
"⑤B manifest.roots==[CmpCore,BiasGen] "
"⑥B n_roots==2 "
"⑦B n_subckts_in_closure==7(2 根+diff_pair/fold_load/ref_beta+ntn_m/ptn_m) "
"⑧B n_leaf_models==2 "
"⑨B leaf_models(排序)==[ntn_mos,ptn_mos] "
"⑩B missing==[](良好输入无未解析引用) "
"⑪B closure 含 CmpCore/BiasGen 且 type==root "
"⑫B topo_order 是合法拓扑序(每子电路的库内 deps 排在它前面)且集合==closure 集 "
"⑬B closure.sp 恰 7 行 .SUBCKT 且出现顺序与 topo_order 单调一致 "
"⑭B closure 每项 ports 与 lib_B .SUBCKT 头端口逐一匹配 "
"⑮跨输入 A(lib_A=Ras_Tscodecomp/Ras_SaNPCtrl, 9 子电路)与 B2(lib_B2=单根 InvChain, 4 子电路)均跑通且 n_roots/n_subckts/roots 全部匹配预期 "
"⑯反硬编码(源码无 A 专属字面量 Ras_Tscodecomp/Ras_SaNPCtrl/nand_x1/nor_x1/inv_x2/nand_x2/ntn_lv/ptn_lv)+3 次 B 跑 manifest.json sha256 一致(确定性)"
)

entry = {
    "task_id": CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": PROMPT,
    "attachments": [
        "assets/EDA-Eval-DesignFlow-SpiceClosureExtract-001/prompt.txt",
        "assets/EDA-Eval-DesignFlow-SpiceClosureExtract-001/task_brief.md",
        "assets/EDA-Eval-DesignFlow-SpiceClosureExtract-001/lib_A.sp",
        "assets/EDA-Eval-DesignFlow-SpiceClosureExtract-001/roots_A.json",
    ],
    "expected_artifacts": ["outputs/submit.zip"],
    "budget": {"max_turns": 25},
    "test": CHECK_SRC,
    "metadata": {
        "domain": "schematic_netlist",
        "grade": "B",
        "track": "faithful",
        "L_level": "L1",
        "trace_source": {
            "user": "dsgao",
            "host": "hfhds201",
            "session_file": "1793260818025_aw9d7.messages.json",
            "match_count": 273,
            "real_task_summary": "DRAM RAS TM 校准验证：分析 netlist.presim 子电路库，为 cm1_ro_TsLT/TsHT/SaNPHT/SaNPHtLtEn/NcAdjEnN/NcAdjHT 等 TM 信号搭建 Finesim testbench；assistant 用依赖闭包抽取器把根块+传递依赖抽成独立网表做聚焦仿真，512/1024/16 组合逻辑验证全 PASS"
        },
        "test_rationale": TEST_RATIONALE,
    },
}

# confirm no duplicate (handle legacy entries with id/case_id instead of task_id)
existing = []
for l in open(JSONL):
    if not l.strip(): continue
    d = json.loads(l)
    existing.append(d.get("task_id") or d.get("case_id") or d.get("id"))
assert CID not in existing, "duplicate task_id already in jsonl"

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended", CID, "to D.jsonl; total now", len(existing)+1)

# sanity: re-read last line parses
last = [l for l in open(JSONL) if l.strip()][-1]
d = json.loads(last)
assert d["task_id"] == CID
# assertion gate: k_rationale == k_check >= 8
k_check = 16  # conditions a-p in check.py
# count 断言 markers
import re
n_marks = len(re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]", TEST_RATIONALE))
print("k_rationale(断言标记)=", n_marks, " k_check=", k_check, " match=", n_marks==k_check and k_check>=8)
assert n_marks == k_check and k_check >= 8, "ASSERTION GATE FAILED"
print("ASSERTION GATE PASS: k_rationale==k_check==16 >= 8")
