#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_append_drvqagatenetlist_001.py - append EDA-Eval-DesignFlow-DrvqaGateNetlist-001
to EDA-Eval-DesignFlow_A.jsonl with test==disk roundtrip check."""
import json
import os
import sys

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-DrvqaGateNetlist-001"
JSONL = os.path.join(ROOT, "EDA-Eval-DesignFlow_A.jsonl")
REF = os.path.join(ROOT, "reference", CID, "check.py")
ASSETS = os.path.join(ROOT, "assets", CID)
PROMPT = os.path.join(ASSETS, "prompt.txt")

TEST_RATIONALE = (
    "17 条断言："
    "① submit.zip 恰含 gen_drvqa_netlist.py + R_BADEC_ADDR2ROWCOL_A.v "
    "② gen_drvqa_netlist.py py_compile 通过 "
    "③ 候选生成器对可见 A 的 spec_A.json 运行 exit 0 且产出非空 .v "
    "④ A .v 含 DRVQA specify 块且 CDS_LIBNAME=\"DRVQA\"/CDS_CELLNAME=\"R_BADEC_ADDR2ROWCOL\"/CDS_VIEWNAME=\"schematic\" "
    "⑤ A .v module 端口输出在前（row,col,valid,N） "
    "⑥ A .v 含 nand/nor/not 门原语（#(0.05) + _I_<name> 实例名）且不含 always 块 "
    "⑦ A .v 含 region_R0..R3 信号且 region_R0 谓词为 (N>=0)&&(N<=79) "
    "⑧ A .v 含输出 nand 树 MUX（_I_mrow0f / _I_mcol4f + 选择信号 row_t0_0/col_t4_3） "
    "⑨ A .v 输入端口为 N[8:0]、输出为 row[3:0]/col[4:0] "
    "⑩ 行为 oracle：解析 A .v 区域谓词+每区域 row/col assign，用独立 verilog 算术解释器在 N=0..296 全范围仿真，(row,col,valid) 与 spec_A 期望逐值相等 "
    "⑪ 候选生成器对隐藏 B 的 spec_B.json 运行 exit 0 且产出非空 .v "
    "⑫ 跨输入守卫 B .v CDS_CELLNAME==\"R_XDEC\" 且不含 A 顶层名 R_BADEC_ADDR2ROWCOL "
    "⑬ 跨输入守卫 B .v module 端口为 (bank,idx,valid,A) 且不含 A 输出端口名 row/col "
    "⑭ 跨输入守卫 B .v 含 region_R0/R1/R2 且不含 A 的 region_R3 "
    "⑮ 行为 oracle（反硬编核心）：解析 B .v 在 A=0..201 全范围仿真，(bank,idx,valid) 与 spec_B 期望逐值相等（硬编 A 真值表则 B 失败） "
    "⑯ 反硬编 gen_drvqa_netlist.py 源码不含 A/B 专有字面量（R_BADEC_ADDR2ROWCOL/R_XDEC/addr_to_rowcol/addr_decode/row_t/col_t 等） "
    "⑰ 随机化：对 A 连跑 3 次产出的 .v 字节一致"
)

TRACE_SOURCE = {
    "user": "fxian",
    "host": "hfeg0pkn002",
    "session_file": "1790650962650_7bg20",
    "match_count": 131,
    "real_task_summary": (
        "RTL addr_to_rowcol_v5 -> DRVQA stdcell-style gate/RTL netlist (digital domain) "
        "on hfeg0pkn002 (fxian); user#1 pasted real RTL addr_to_rowcol_v5.v (9-bit N->row/col, "
        "4 regions R0..R3, R2 div3 parallel bit-compare); user#3 \"base on DRVQA db stdcell & "
        "environment, create circuit\"; user#4 \"我可以用华大的Aether查看你生成的电路原理图么\"; "
        "user#5 \"请继续生成原理图，希望看到你调用的也是DRVQA的stdcell搭建了电路\"; gold = agent product "
        "R_BADEC_ADDR2ROWCOL_DRVQA.v (279L, nand/nor/not + 28 assign + specify CDS_LIBNAME=DRVQA); "
        "real input RTL addr_to_rowcol_v5.v + gold netlist scp'd from 10.129.2.11:/home/fxian/verilog/; "
        "B-grade synthesized (gold is agent product; A uses real RTL + spec reflecting real behavior, "
        "B is heterogeneous hidden 8-bit 3-region banked decoder)."
    ),
}


def main():
    test_str = open(REF, encoding="utf-8").read()
    prompt_str = open(PROMPT, encoding="utf-8").read()

    entry = {
        "task_id": CID,
        "mode": "design_flow",
        "entry_point": "outputs/submit.zip",
        "test": test_str,
        "prompt": prompt_str,
        "attachments": [
            "assets/%s/spec_A.json" % CID,
            "assets/%s/addr_to_rowcol_A.v" % CID,
            "assets/%s/prompt.txt" % CID,
            "assets/%s/task_brief.md" % CID,
        ],
        "metadata": {
            "trace_source": TRACE_SOURCE,
            "domain": "digital",
            "track": "faithful",
            "test_rationale": TEST_RATIONALE,
        },
    }
    line = json.dumps(entry, ensure_ascii=False)

    # guard: no duplicate
    for ln in open(JSONL, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        if json.loads(ln).get("task_id") == CID:
            print("ALREADY PRESENT, aborting"); return 1

    with open(JSONL, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    # test==disk roundtrip: re-read appended test field, compare to disk check.py
    appended = None
    for ln in open(JSONL, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        d = json.loads(ln)
        if d.get("task_id") == CID:
            appended = d
            break
    assert appended is not None, "append failed"
    disk = open(REF, encoding="utf-8").read()
    assert appended["test"] == disk, "test==disk roundtrip FAILED (byte mismatch)"
    # assertion gate: k_rationale == k_check >= 8
    k_check = 17
    k_rationale = TEST_RATIONALE.count("①") + sum(1 for ch in TEST_RATIONALE if ch in "②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰")
    # the above double-counts; recompute properly:
    import re
    kens = len(re.findall(r"[①-⑰]", TEST_RATIONALE))
    assert kens == k_check, "k_rationale(%d) != k_check(%d)" % (kens, k_check)
    assert k_check >= 8, "k_check < 8"
    print("APPENDED %s" % CID)
    print("k_rationale == k_check == %d (>=8) GATE PASS" % k_check)
    print("test==disk byte-match OK (%d bytes)" % len(disk))
    # count lines
    n = sum(1 for ln in open(JSONL, encoding="utf-8") if ln.strip())
    print("A.jsonl now %d lines" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
