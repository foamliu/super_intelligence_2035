#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-VmMhlAlterStats-001 to shard B jsonl."""
import os, json, hashlib

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE_ID = "EDA-Eval-DesignFlow-VmMhlAlterStats-001"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")
CHECK = os.path.join(BENCH, "reference", CASE_ID, "check.py")
AST = os.path.join(BENCH, "assets", CASE_ID)

with open(CHECK, "r") as fh:
    check_src = fh.read()
check_md5 = hashlib.md5(check_src.encode("utf-8")).hexdigest()

prompt = open(os.path.join(AST, "prompt.txt")).read()

entry = {
    "task_id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": check_src,
    "prompt": prompt,
    "attachments": ["assets/" + CASE_ID + "/mt0_A.csv",
                    "assets/" + CASE_ID + "/prompt.txt",
                    "assets/" + CASE_ID + "/task_brief.md"],
    "metadata": {
        "trace_source": {
            "user": "stephens",
            "host": "hfeg0pkn002",
            "session_file": "1793244287787_11tjs",
            "match_count": 139,
            "real_task_summary": "FineSim 蒙特卡洛 .csv 测量结果按 .alter 分组求 VMHL/VMLH 的 min/max/mean"
        },
        "domain": "spice_sim",
        "track": "faithful",
        "layer": "L1",
        "test_rationale": (
            "15 条断言："
            "①交付件是 zip 且内含 analyze_vm.py "
            "②analyze_vm.py 通过 py_compile（语法正确）"
            "③候选在隐藏 B 的 mt0.csv 上运行 exit 0 且产出 vm_alter_stats.csv "
            "④输出表头恰好为 alter#,N,vmlh_min,vmlh_max,vmlh_mean,vmhl_min,vmhl_max,vmhl_mean 八列顺序 "
            "⑤输出 8 行数据且 alter# 为 1..8 整数升序 "
            "⑥每行 N==80（B 每 alter 80 次蒙特卡洛采样）"
            "⑦alter1 的 vmlh_min/vmlh_max/vmhl_min/vmhl_max 四值与独立重算的 B 金标一致 "
            "⑧alter5 的 vmlh_min 与金标一致 "
            "⑨alter8 的 vmhl_max 与金标一致 "
            "⑩alter3 的 vmlh_mean 与金标一致（击败只算 min/max 的 stub）"
            "⑪alter3 的 vmhl_mean 与金标一致（mean 必须算，非仅 min/max）"
            "⑫跨输入护栏：候选在 A 上重跑得 6 alter（非 8）且 A 的 alter1 vmlh_min 与 B 不同（击败硬编码 A 值）"
            "⑬按列名解析护栏：B 的 vmlh 列被移到非典范位置且含 ramp 干扰列，alter1 的 vmlh_min 不得等于 ramp 列的最小值（击败按固定下标读取的位置解析器）"
            "⑭确定性：候选在 B 上重跑两次，输出 sha256 完全一致 "
            "⑮健全性：每行 vmlh_max>=vmlh_min 且 vmhl_max>=vmhl_min"
        ),
        "selftest": "ref PASS 15/15; 6 neg ALL-FAIL distinct {b,g,j,m,c,k}; §4.9 {empty->b, hardcode_A->g, core_deleted->k}"
    }
}

# verify byte sync: test field roundtrips to same md5
assert entry["test"] == check_src, "test field != disk check.py"
assert hashlib.md5(entry["test"].encode("utf-8")).hexdigest() == check_md5

# dedup check
existing = []
with open(JSONL) as fh:
    for line in fh:
        d = json.loads(line)
        existing.append(d.get("task_id") or d.get("id"))
assert CASE_ID not in existing, "case already in jsonl!"
print("existing rows:", len(existing), "| new case not present OK")

with open(JSONL, "a") as fh:
    fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

# re-verify
with open(JSONL) as fh:
    rows = [json.loads(l) for l in fh]
last = rows[-1]
assert last["task_id"] == CASE_ID
assert hashlib.md5(last["test"].encode("utf-8")).hexdigest() == check_md5
print("appended. total rows:", len(rows))
print("test md5:", check_md5, "size:", len(check_src))
print("unique ids:", len(set(r.get("task_id") or r.get("id") for r in rows)), "/", len(rows))
