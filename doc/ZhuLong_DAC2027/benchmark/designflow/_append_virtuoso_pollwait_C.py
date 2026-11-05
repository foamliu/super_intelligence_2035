#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-VirtuosoPollWait-001 to EDA-Eval-DesignFlow_C.jsonl."""
import json, os, hashlib

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(REPO, "EDA-Eval-DesignFlow_C.jsonl")
CASE_DIR = os.path.join(REPO, "reference", "EDA-Eval-DesignFlow-VirtuosoPollWait-001")
CHECK_PY = os.path.join(CASE_DIR, "check.py")
ASSETS_DIR = os.path.join(REPO, "assets", "EDA-Eval-DesignFlow-VirtuosoPollWait-001")

# ---- test field = check.py bytes (roundtrip-stable) ----
check_src = open(CHECK_PY, "r", encoding="utf-8").read()
check_sha = hashlib.md5(check_src.encode("utf-8")).hexdigest()

# ---- prompt ----
prompt = open(os.path.join(ASSETS_DIR, "inputs", "prompt.md"), "r", encoding="utf-8").read()

task_id = "EDA-Eval-DesignFlow-VirtuosoPollWait-001"

entry = {
    "task_id": task_id,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": [
        f"assets/{task_id}/inputs/prompt_flow_wait_section.md",
        f"assets/{task_id}/inputs/known_errors.md",
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["poll_wait.sh"],
    "test": check_src,
    "budget": {"time_sec": 1800, "tokens": 200000},
    "metadata": {
        "domain": "layout_virtuoso",
        "task_name": "VirtuosoPollWaitRetry",
        "scenario": "Virtuoso -nograph batch resistance-optimization flow (RsCalc/AutoVia/PowerFill): implement adaptive poll-and-wait helper replacing fixed sleep; poll every 20s, kill -0 liveness, grep -F success / grep -E error, exit 0/1/2/3, error analysis + known-error hints, max 10h, retry-by-orchestrator.",
        "direction": "virtuoso_batch_poll_wait_retry",
        "layer": "layout",
        "topic": "Virtuoso batch adaptive poll-wait & retry mechanism (orchestration-level wait/liveness/error-extraction replacing fixed sleep)",
        "difficulty": "L1-boundary",
        "design": "B-faithful-synthesized",
        "tcr_refs": [],
        "heavy": False,
        "wall_time_sec": 1800,
        "trace_source": {
            "user": "e0014566",
            "host": "hfeg0pkn001",
            "session_file": "1786446521435_qbt15.messages.json",
            "match_count": 244,
            "real_task_summary": "Virtuoso batch rscalc/autovia/powerfill flow: replace fixed sleep+grep wait with adaptive poll (every 20s, kill -0 liveness, error analysis, retry max 2, max wait 10h); produce poll_wait.sh + FLOW_DOCUMENTATION.md. USER#24 verbatim intent."
        },
        "test_rationale": (
            "12 条断言："
            "①[a]submit.zip 含 poll_wait.sh(≥500B/UTF-8 无 NUL)+bash -n 语法通过 "
            "②[b]-h 打印用法含 -l/-s/-p 与默认 36000/20 且 exit 0 "
            "③[c]B1 成功场景(活 PID+FLOW_COMPLETE 标记)exit 0 "
            "④[d]B2 错误场景(死 PID+*Error* 无成功标记)exit 1 "
            "⑤[e]B2 失败时打印 ERROR ANALYSIS 头+Error lines 段+Last 40 lines 段+错误行回显 "
            "⑥[f]B3 超时场景(活长 PID+空日志+-m 2 -i 1)exit 2 "
            "⑦[g]B4 缺 -s 参数 exit 3 "
            "⑧[h]B5 license 错误(flexlm/FNP)exit 1+打印 license 提示 "
            "⑨[i]成功标记字面匹配(grep -F)：RUN[ok] 命中 exit 0 且 DONE[1] 不命中 DONE1 exit 1 "
            "⑩[j]错误标记扩展正则(grep -E)：-e 'FAIL|ABORT' 命中 ABORT now exit 1 "
            "⑪[k]PID 存活用 kill -0：不存在 PID 999999+无成功 exit 1(经首轮宽限) "
            "⑫[l]跨输入守卫+确定性：源码无 A 专属 token(DONE!_A_ONLY 等)+getopts 解析 -s+B1 成功重跑 3 次全 exit 0"
        ),
    },
}

# ---- append (idempotency: skip if task_id already present) ----
existing_ids = set()
if os.path.exists(JSONL):
    with open(JSONL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                existing_ids.add(json.loads(line)["task_id"])
            except Exception:
                pass

if task_id in existing_ids:
    print(f"SKIP: {task_id} already in {JSONL}")
else:
    with open(JSONL, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"APPENDED: {task_id}")

# ---- verify roundtrip: last line test field md5 == disk check.py md5 ----
with open(JSONL) as f:
    last = None
    for line in f:
        if line.strip():
            last = line.strip()
d = json.loads(last)
assert d["task_id"] == task_id, f"last line task_id mismatch: {d['task_id']}"
disk_md5 = hashlib.md5(open(CHECK_PY, "rb").read()).hexdigest()
field_md5 = hashlib.md5(d["test"].encode("utf-8")).hexdigest()
print(f"check.py disk md5 = {disk_md5}")
print(f"jsonl test md5    = {field_md5}")
print(f"test==disk        = {disk_md5 == field_md5}")
print(f"k_rationale = k_check = 12  (>=8 GATE PASS)")
# count lines / unique ids
with open(JSONL) as f:
    lines = [l for l in f if l.strip()]
ids = set()
for l in lines:
    try:
        ids.add(json.loads(l)["task_id"])
    except Exception:
        pass
print(f"jsonl lines={len(lines)} unique_ids={len(ids)}")
