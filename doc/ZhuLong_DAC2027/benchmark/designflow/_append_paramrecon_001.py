#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-ParamRecon-001 to EDA-Eval-DesignFlow_A.jsonl."""
import json, os, sys

CASE = "EDA-Eval-DesignFlow-ParamRecon-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")
ASSET_DIR = os.path.join(BENCH, "assets", CASE)
REF_DIR = os.path.join(BENCH, "reference", CASE)
CHECK_PY = os.path.join(REF_DIR, "check.py")

with open(CHECK_PY, "r", encoding="utf-8") as f:
    check_src = f.read()

with open(os.path.join(ASSET_DIR, "prompt.txt"), "r", encoding="utf-8") as f:
    prompt = f.read()

attachments = [
    "assets/" + CASE + "/prompt.txt",
    "assets/" + CASE + "/task_brief.md",
    "assets/" + CASE + "/params.json",
    "assets/" + CASE + "/verilog_A/rhr_parameter.pkg",
    "assets/" + CASE + "/verilog_A/rhr_driver.sv",
    "assets/" + CASE + "/verilog_A/top.sv",
    "assets/" + CASE + "/verilog_A/RH_MULTI_OSC_R01.v",
    "assets/" + CASE + "/verilog_A/dlut_top.v",
    "assets/" + CASE + "/verilog_A/rhr_netlist.sv",
]

test_rationale = (
    "15 条断言："
    "①zip含param_compare.py ②param_compare.py可py_compile ③CLI 3位置参数exit0产出out_csv "
    "④CSV含7列表头(类别/Python参数/Python值/对应Verilog文件(行号)/Verilog对应机制/Verilog实际值/结论) "
    "⑤tREFI行verilog实际值反映8x加速(31200ns)且结论非一致(python 3900≠verilog 31200) "
    "⑥tRFC行verilog实际值=独立求和B ref_cmd #延时(~380.25ns)±1ns且结论一致 "
    "⑦tRC行verilog实际值=独立求和B act_cmd #延时(~60.0ns)±1ns且结论一致 "
    "⑧OSC1_T行verilog实际值=2×#延时=200ns且与python 200一致 "
    "⑨OSC4_T行结论Verilog无(无第4路OSC) "
    "⑩nREFinBurst_replace行结论Verilog无(无replace双档) "
    "⑪DiscardUnder2行识别netlist AND6链+top DisUnder2=1且结论含极性一致/保护开启 "
    "⑫DDRDiscardRateMode行2'b10→÷32(独立解码)且与python 2一致 "
    "⑬lfsr_seq_osc_discard_init行verilog实际值=5(B的RDVALUELat初值)且与python 5一致 "
    "⑭跨输入守卫B CSV不泄漏A专属字面量(15600/260ns/440ns/860ns/2'b00→÷16/33条/280000死参数/4x加速) "
    "⑮反stub param_compare.py源含re.*(compile/search/finditer/sub)+open(+写入机制(csv.writer/.write)"
)

entry = {
    "id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": check_src,
    "prompt": prompt,
    "attachments": attachments,
    "metadata": {
        "trace_source": {
            "user": "xuluo",
            "host": "hfeg0pkn001",
            "session_file": "1793605487158_evxj6.messages.json",
            "match_count": 333,
            "real_task_summary": "DRAM RHR (Row Hammer Refresh) 验证：python 行为模型参数 vs Verilog RTL+TB+netlist 源码参数对齐分析。用户(xuluo)逐字「分析这个目录下的代码，这是python下对应的参数，告诉我两者参数有何不同」。assistant(deepseek-v4 lead, 293 msgs)对每个 python 参数找出 verilog 文件:行号+机制+实际生效值+结论，产出 para_compare_dbcoa_v2.csv。关键实测：tRFC/tRC 实际=rhr_driver.sv task #延时逐条求和(pkg tRFC=280000 为死参数)；tREFI=pkg 表达式含加速倍数；OSC 周期=#翻转延时×2；under2=netlist AND6(全<=2)&cm1_ro_DisUnder2→DiscardSkipN=NAND；RHDiscardRate 2'b00→Hat4÷16。真实 /proj/dbcoa verilog 对 e0031982 不可读(permission denied)，assets 装载忠实裁剪的 verilog 摘录(真值+真延时和取自 trace)。"
        },
        "domain": "verification",
        "track": "synthesized",
        "test_rationale": test_rationale,
        "k_rationale": 15,
        "k_check": 15,
    },
}

# sanity: ensure no existing id
existing = []
if os.path.isfile(JSONL):
    with open(JSONL, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                o = json.loads(line)
                if o.get("id") == CASE:
                    print("SKIP: %s already in jsonl" % CASE); sys.exit(0)
                existing.append(o.get("id"))
            except Exception:
                pass

with open(JSONL, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print("appended %s (k_rationale=%d k_check=%d) to %s; total lines now %d" % (
    CASE, entry["metadata"]["k_rationale"], entry["metadata"]["k_check"], JSONL, len(existing)+1))
