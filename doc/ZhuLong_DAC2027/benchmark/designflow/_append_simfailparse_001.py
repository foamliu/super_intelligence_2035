#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-SimFailParse-001 to EDA-Eval-DesignFlow_A.jsonl."""
import json, os

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(REPO, "EDA-Eval-DesignFlow_A.jsonl")
CASE = "EDA-Eval-DesignFlow-SimFailParse-001"
ASSET_DIR = f"assets/{CASE}"
REF_DIR = f"reference/{CASE}"

with open(os.path.join(REPO, REF_DIR, "check.py")) as f:
    test_src = f.read()
with open(os.path.join(REPO, ASSET_DIR, "prompt.txt")) as f:
    prompt = f.read()

entry = {
    "task_id": CASE,
    "id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": test_src,
    "prompt": prompt,
    "attachments": [
        {"name": "prompt.txt", "source": f"{ASSET_DIR}/prompt.txt"},
        {"name": "task_brief.md", "source": f"{ASSET_DIR}/task_brief.md"},
        {"name": "a_compare.rpt", "source": f"{ASSET_DIR}/a_compare.rpt"},
        {"name": "xrun.log", "source": f"{ASSET_DIR}/xrun.log"},
        {"name": "hidden/hidden_manifest.json", "source": f"{ASSET_DIR}/hidden/hidden_manifest.json"},
    ],
    "metadata": {
        "trace_source": {
            "user": "nevinrao",
            "host": "hfeg0pkn001",
            "session_file": "1792658984406_7j9b9.messages.json",
            "match_count": 205,
            "real_task_summary": (
                "LPDDR5 DRAM netlist-sim read-datapath X-propagation debug. User (nevinrao) pasted a "
                "self-checking testbench A_Compare.rpt failure: pattern 37 "
                "(ActCasfAct1Wr0Wr1WrAp2Act2ActCasrRd0Rd1Rd2PreAll, bg:3 ba:2 row:5a93) shows DUT_DQ:x / "
                "DUT_DMI:x on the first read beat after sync, then DUT_DQ:z; user suspects the datapath "
                "circuit, error occurs 'after sync issue read then issue cas'. User pointed agent at simdir "
                "/proj/ddgoa/V0/simdir/verilog/qi3wang/verilog.lpddr5.ddgoa.net1015/log_net1015_10_lowspeed_pd_delay_30to40/act1act2.x16. "
                "Agent (deepseek-v4-flash) explored TB (compare_tasks.sv / lpddr5_tasks.sv / lpddr5_interface.sv), "
                "A_Pattern_Sim.v, A_Compare.rpt, xrun.log SDF warnings (*W,SDFNDP negative-delay + *W,SDFINC "
                "I_DOutEn instance not found for 16 DQ + DMI pads), netlist (I_P2STopUnitHSM5_5 / DOutEnIP "
                "read output-enable), pd_delay_testmode.run; converged on SDF annotation failure on the DQ/DMI "
                "read output-enable (I_DOutEn) + the pd_delay_30to40 experimental delay-injection scenario. "
                "Trace ends mid-investigation (130 msgs) with no single accepted deliverable, so this is a "
                "B-track synthesized case: a_compare.rpt + xrun.log are rebuilt faithfully to the real "
                "A_Compare.rpt / xrun.log formats observed in the trace (pattern header + ==== separator + "
                "per-beat DUT_DQ/DUT_DMI compare lines; xrun *W,SDFNDP / *W,SDFINC / *E,UNDIDN / *E,ELAB). "
                "Task = write parse_fail.py that parses both logs into a structured JSON diagnosis."
            ),
        },
        "domain": "verification",
        "track": "B (synthesized; trace-faithful prompt + asset formats)",
        "level": "L1-static",
        "k_rationale": 16,
        "k_check": 16,
        "test_rationale": (
            "16 条断言：① zip 含 parse_fail.py ② parse_fail.py 可 py_compile 通过 ③ CLI 接受 "
            "<A_Compare.rpt> <xrun.log> <output.json> 三位置参数且 exit 0 ④ 输出为合法 JSON 且含 "
            "8 个必需顶层键（total_failures/patterns/failure_type_counts/signals_affected/sdf_warnings/"
            "compile_errors/first_fail_pattern/root_cause_category） ⑤ total_failures == gold(B)（跨输入 "
            "hidden B，反硬编） ⑥ patterns 列表长度 == gold(B) ⑦ first_fail_pattern（按 timestamp_ps "
            "最早的 pattern id）== gold(B) ⑧ failure_type_counts {x/z/mismatch} == gold(B) ⑨ "
            "signals_affected {DUT_DQ/DUT_DMI} == gold(B) ⑩ sdf_warnings 数量与 (code,instance) 集合 == "
            "gold(B)（解析 xrun.log 的 *W,SDFNDP/*W,SDFINC） ⑪ 每个 pattern 的 id == gold(B) ⑫ 每个 "
            "pattern 的 cmd_seq == gold(B) ⑬ 每个 pattern 的 bg/ba/row/col0/col1/col2 == gold(B) ⑭ "
            "root_cause_category == gold(B)（B=compile_error，A=sdf_annotation，分支判定） ⑮ 反 stub："
            "源含 re.compile + json.dump + open ⑯ 反硬编跨输入：A gold 与 B gold 在 ≥6 字段上不同"
            "（total/first/root_cause/mismatch/sigs.DQ/pattern 数/sdf 数，sanity）；空壳/print-only/"
            "删核心三假提交全 FAIL"
        ),
    },
}

# Append (do not duplicate)
existing = []
if os.path.exists(JSONL):
    with open(JSONL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                if d.get("task_id") == CASE:
                    existing.append(d.get("task_id"))
            except Exception:
                pass
if existing:
    print(f"SKIP: {CASE} already in jsonl")
else:
    with open(JSONL, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"APPENDED: {CASE}")
# Report new count
n = 0
with open(JSONL) as f:
    for line in f:
        if line.strip():
            n += 1
print(f"jsonl now has {n} entries")
