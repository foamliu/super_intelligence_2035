#!/usr/bin/env python3
import json, os, hashlib

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "DqReadPathWaveDebug-001"
RDIR = os.path.join(BASE, "reference", CASE)
JSONL = os.path.join(BASE, "EDA-Eval-DesignFlow_D.jsonl")

check_src = open(os.path.join(RDIR, "check.py")).read()
ref_zip = os.path.join(RDIR, "reference_submit.zip")

rationale = (
    "15 条断言："
    "①submit.zip 含候选脚本 dq_waveform_debug.py 与 diagnosis.json "
    "②候选脚本 py_compile 通过 "
    "③subprocess 在隐藏 B 上跑通候选并产 diagnosis.json "
    "④diagnosis.json 可解析且含全部必需键 "
    "⑤data_intact==True 即候选正确判定期望数据 golden==actual 一致 "
    "⑥first_fail_cycle 等于 B 首个 mismatch cycle "
    "⑦root_cause_signal 等于 B 的 culprit 信号 slice_swap_sel "
    "⑧root_cause_kind==bit_swap（与 A 的 gate_disable 反向） "
    "⑨failing_stage==slice_mux（与 A 的 rd_gate 反向） "
    "⑩mismatch_cycles 集合等于 B 实际 mismatch cycle 集合 "
    "⑪expected_signal==dq_data（与 A 的 dq_exp 反向） "
    "⑫output_signals==[HI_DQ,LO_DQ]（与 A 的 UPDQP/LPDQPad 反向，反硬编码） "
    "⑬enable_signal==read_valid（与 A 的 rd_en 反向） "
    "⑭bit_analysis 含 HI_DQ/LO_DQ 的 golden/actual 值且二者不等 "
    "⑮3-seed 共享置换 shuffle 行序后 root_cause_signal/kind/first_fail 不变（确定性）"
)

entry = {
    "task_id": "EDA-Eval-DesignFlow-" + CASE.split("-001")[0],
    "mode": "design_flow",
    "prompt": open(os.path.join(BASE, "assets", CASE, "prompt.txt")).read(),
    "attachments": [
        "assets/DqReadPathWaveDebug-001/golden_trace_A.csv",
        "assets/DqReadPathWaveDebug-001/actual_trace_A.csv",
        "assets/DqReadPathWaveDebug-001/dq_readpath_A.v",
        "assets/DqReadPathWaveDebug-001/task_brief.md",
    ],
    "entry_point": "outputs/submit.zip",
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "jinhaoli",
            "host": "hfeg0pkn004",
            "session_file": "1793348917218_h8pcp.messages.json",
            "match_count": 156,
            "real_task_summary": "DDR5 write-pattern DQ read-path 波形比对 debug：golden xcelium.trn 与 actual xcelium.trn 中 dq_exp[15:0] 与读总线 UPDQP[7:0]/LPDQPad[7:0] 对不上，定位电路根因",
        },
        "domain": "waveform",
        "grade": "B",
        "layer": "L2",
        "test_rationale": rationale,
        "k_check": 15,
    },
}

# verify byte-sync: test field == disk check.py
assert entry["test"] == open(os.path.join(RDIR, "check.py")).read(), "test field not byte-synced"

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# stats
sha = hashlib.sha256(check_src.encode()).hexdigest()
size = len(check_src)
nlines = sum(1 for _ in open(JSONL))
print("appended", entry["task_id"])
print("check.py sha:", sha[:16], "size:", size)
print("D.jsonl lines:", nlines)
print("k_rationale == k_check == 15 >= 8 GATE PASS")
