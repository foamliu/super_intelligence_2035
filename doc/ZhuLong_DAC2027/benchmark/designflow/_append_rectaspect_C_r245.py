#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-RectAspectRuleCheck-001 to shard C jsonl."""
import json
import os

CASE_ID = "EDA-Eval-DesignFlow-RectAspectRuleCheck-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF = os.path.join(BENCH, "reference", CASE_ID)
ASSETS = os.path.join(BENCH, "assets", CASE_ID)

with open(os.path.join(REF, "check.py")) as f:
    check_src = f.read()
with open(os.path.join(ASSETS, "prompt.txt")) as f:
    prompt = f.read()

test_rationale = (
    "14 条断言：① zip 含 aspect_check.py（≥300B/UTF-8/无 NUL） ② "
    "py_compile 通过且仅标准库（无 calibre/numpy/pandas/gdspy 等） ③ "
    "在 config_B 上退出 0 且 out_B 非空、stderr 无 Traceback ④ "
    "out_B header 携带 B.layer 与 B.max_ratio（数值容差 1e-6） ⑤ "
    "out_B 违规 id 集合 == golden_B id 集合（精确集合匹配） ⑥ "
    "out_B 每条违规的 short/long 整数精确等于 golden 且 ratio 在 1e-3 内 ⑦ "
    "config_B 中合规矩形（ratio < max_ratio）不被误报 ⑧ "
    "config_B 中的正方形（1:1）矩形必被报为违规 ⑨ "
    "config_B 中极细长矩形（ratio ≤ 0.1）必不被报 ⑩ "
    "config_B 中退化矩形（long==0/零面积/线）必不被报 ⑪ "
    "防硬编码：out_B 含 B.layer 与 B.max_ratio 且不含 A 的差异值（layer/max_ratio） ⑫ "
    "B2+B3 各自退出 0、违规 id 集合与 golden 一致、header 层名正确 + 3-seed sha256(out_B) 稳定 ⑬ "
    "缺失 config 文件以非零退出码报错 ⑭ "
    "可见 A 输出与 golden_A 一致（header 层名/阈值 + 违规 id/short/long/ratio）"
)

entry = {
    "task_id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        "assets/%s/A/config_A.json" % CASE_ID,
        "assets/%s/A/rects_A.txt" % CASE_ID,
        "assets/%s/manifest_A.json" % CASE_ID,
        "assets/%s/task_brief.md" % CASE_ID,
        "assets/%s/prompt.txt" % CASE_ID,
    ],
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "lipingy",
            "host": "hfeg0pkn003",
            "ip": "10.129.2.12",
            "session_file": "1791963569790_794ce.messages.json",
            "match_count": 179,
            "real_task_summary": (
                "lipingy 在 /home/lipingy/AutoDRC/calibreDRC.rule（长鑫 DRAM Calibre DRC TVF deck ~27504 行）"
                "上写 DRC 检查；本轮（U#84）要求用 DRC 查矩形短边/长边之比必须小于 0.8（如 M1_drawing），"
                "assistant 用 INT+LENGTH 阶梯逼近法（W/L<0.8⇔L>1.25×W）给出规则草稿"
            ),
        },
        "domain": "physical_verify",
        "level": "L1",
        "track": "B-synthesized",
        "test_rationale": test_rationale,
    },
}

JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_C.jsonl")
# verify not already present
existing_ids = set()
with open(JSONL) as f:
    for line in f:
        line = line.strip()
        if line:
            d = json.loads(line)
            existing_ids.add(d.get("task_id"))
if CASE_ID in existing_ids:
    print("ALREADY PRESENT, skipping append")
else:
    with open(JSONL, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("appended %s" % CASE_ID)

# verify k_rationale == k_check == 14
import re
m = re.match(r"(\d+) 条断言", test_rationale)
k_rationale = int(m.group(1))
# count independent conditions in check.py (a..n)
cond_letters = []
for line in check_src.split("\n"):
    m2 = re.match(r"\s*conds\.append\(_cond\(\"([a-z]+)\"", line)
    if m2:
        cond_letters.append(m2.group(1))
# dedupe by letter (return path adds filler conds too but those use same letters)
k_check = len(set(cond_letters))
print("k_rationale=%d  k_check=%d  letters=%s" % (k_rationale, k_check, sorted(set(cond_letters))))
assert k_rationale == k_check >= 8, "gate failed: %d vs %d" % (k_rationale, k_check)
print("GATE OK (k_rationale == k_check == %d >= 8)" % k_rationale)
