#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_append_implantfill_deckgen_C.py - append EDA-Eval-DesignFlow-ImplantFillDeckGen-001
to EDA-Eval-DesignFlow_C.jsonl (shard C, physical_verify)."""
import os, json, hashlib

CASE = "EDA-Eval-DesignFlow-ImplantFillDeckGen-001"
REF_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/" + CASE
ASSET_DIR = "assets/" + CASE
JSONL = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_C.jsonl"

with open(os.path.join(REF_DIR, "check.py"), "r", errors="replace") as f:
    test_src = f.read()
test_sha = hashlib.sha256(test_src.encode()).hexdigest()

with open("/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/" + ASSET_DIR + "/prompt.txt") as f:
    prompt = f.read()

test_rationale = (
    "14 条断言："
    "①(a)submit.zip 含 gen_implant_fill_deck.py(>=200B)、py_compile 通过、纯标准库(无 pyAether/socket/urllib)、源码无 B 专属字面量(pch1_gap/nch2_hole/old_gap/layers_B.def/IMCleFillTop_B/decqa_B.gds/0.18/0.22/pch1_drawing/nch2_drawing) "
    "②(b)隐藏 B 上候选脚本 exit0 且输出 runFillImplant.rule 非空(>=50B) "
    "③(c)B 输出 LAYER OPERATION 行紧随 INCLUDE \"layers_B.def\" "
    "④(d)B 输出含 VARIABLE SPACE_VALUE_pch1 0.18(值被替换) "
    "⑤(e)B 输出含 VARIABLE SPACE_VALUE_nch2 0.22(值被替换) "
    "⑥(f)B 输出无 VARIABLE SPACE_VALUE_old 行(layerDict 外的变量被删除=消除 VAR2 错误源) "
    "⑦(g)B 输出含 CMACRO FILL_IMPLANT_pch1 且行内含 SPACE_VALUE_pch1(DMACRO->CMACRO 且 SPACE_VALUE 替换) "
    "⑧(h)B 输出含 CMACRO FILL_IMPLANT_nch2 且行内含 SPACE_VALUE_nch2 "
    "⑨(i)B 输出无 CMACRO FILL_IMPLANT_old(layerDict 外的 CMACRO 被过滤) "
    "⑩(j)B 输出 //FLATTEN 标记之前无原始 '= FLATTEN' 赋值行(pch1gap/nch2hole/oldgap 三行被删除) "
    "⑪(k)B(fill_in_cell=false)//FLATTEN 标记之后插入派生 pch1gap = FLATTEN pch1_gap 与 nch2hole = FLATTEN nch2_hole，且无 oldgap 派生(old 不在 layerDict) "
    "⑫(l)B 输出 //DFM 标记之后插入 FILL_DFM_RDB 块且含 DFM RDB GDS implantFill_flatten.gds "
    "⑬(m)隐藏 B2(fill_in_cell=true)//FLATTEN 之后无派生 '= FLATTEN' 行(条件分支被遵守)，且 VARIABLE SPACE_VALUE_avn 0.31 与 INCLUDE \"layers_B2.def\" 仍正确(其他变换不受影响) "
    "⑭(n)反硬编码+确定性：A 上重跑输出无 B 专属值(IMCleFillTop_B/layers_B.def/0.22)且含 VARIABLE SPACE_VALUE_cell 0.16；B 上 3 次重跑输出 sha256 一致"
)

case = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": test_src,
    "prompt": prompt,
    "attachments": [
        ASSET_DIR + "/prompt.txt",
        ASSET_DIR + "/task_brief.md",
        ASSET_DIR + "/deck_template_A.rule",
        ASSET_DIR + "/layers_A.def",
        ASSET_DIR + "/config_A.json",
    ],
    "metadata": {
        "trace_source": {
            "user": "ellawu",
            "host": "hfeg0pkn005",
            "session_file": "1793233072993_vmvz6.messages.json",
            "match_count": 285,
            "real_task_summary": "Calibre DRC implant-fill rule-deck generation: fix 'VAR2 no variable value for SPACE_VALUE_cell' error in runFillImplant.rule by generating a complete deck from template+layerFile+config (insert INCLUDE after LAYER OPERATION, replace/insert VARIABLE SPACE_VALUE_<key>, filter unknown keys, build CMACRO from DMACRO with D->C and SPACE_VALUE->SPACE_VALUE_<key>, remove/insert derived FLATTEN conditionally on fill_in_cell, insert FILL_DFM_RDB block).",
        },
        "domain": "physical_verify",
        "shard": "C",
        "track": "faithful",
        "difficulty_tier": "L1-boundary",
        "test_rationale": test_rationale,
        "test_sha256": test_sha,
        "k_assertions": 14,
        "k_check": 14,
    },
}

# dedup: skip if task_id already present
import sys
if os.path.exists(JSONL):
    with open(JSONL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
                if o.get("task_id") == CASE:
                    print("SKIP: %s already in jsonl" % CASE)
                    sys.exit(0)
            except Exception:
                pass

with open(JSONL, "a") as f:
    f.write(json.dumps(case, ensure_ascii=False) + "\n")
print("appended:", CASE, "test_sha=", test_sha[:12], "k=14")

if __name__ == "__main__":
    pass
