#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-PVTvarSpecJudge-001 to EDA-Eval-DesignFlow_B.jsonl
(matching the existing schema: task_id / attachments[{name,source,desc}] / expected_artifacts / budget / metadata{trace_source,domain,layer,layer_rationale,test_rationale})."""
import os, re, json

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-PVTvarSpecJudge-001"
JSONL = os.path.join(REPO, "EDA-Eval-DesignFlow_B.jsonl")

check_src = open(os.path.join(REPO, "reference", CASE, "check.py")).read()
prompt = open(os.path.join(REPO, "assets", CASE, "prompt.txt")).read()

test_rationale = (
    "14 条断言：①submit.zip 含 pvt_var_judge.py "
    "②候选 py_compile 通过 "
    "③候选 subprocess 真跑 hspice（B 的 sim_log 含 'job concluded' 且产出 .mt 文件、hspice_rc=0）"
    "④解析 .alter 多 corner，n_corners>=9（B=15）"
    "⑤B 每指标 variation=max-min 匹配 GT（vref_heavy=0.1817V、vref_light=0.0535V，±5%）"
    "⑥spec 限值从 spec_B.json 读出（=0.020）非硬编 A 的 0.008"
    "⑦B overall_pass=False（FAIL，B 设计为超标）"
    "⑧每个 B 指标的 pass 标志正确（vref_light/vref_heavy 均 False）"
    "⑨per_temperature 分组>=3（B 有 5 个温度）"
    "⑩root_cause 每指标含 worst_low/worst_high（value+temper 非空）"
    "⑪verdict.json 字段完整（overall_pass/n_corners/metrics/per_temp/root_cause/sim_log_path/deck_path）"
    "⑫跨输入守卫：候选重跑 A 得 overall_pass=True 且 A 指标名(vout_unload/vout_load1ma)出现"
    "⑬name-agnostic：B verdict 指标名=={vref_light,vref_heavy}，无 A 名泄漏"
    "⑭确定性：重跑 B 两次 variation 一致（1% 内）"
)

attachments = [
    {"name": "vcc2sc_A.sp", "source": "vcc2sc_A.sp",
     "desc": "公开输入 A：Level-1 Shichman-Hodges PMOS 自偏置电流参考 + 输出镜像 Vcc2sc 网表（pvdd=1.0/vto_p=-0.55/kp=45u，M1 二极管+Rref 120k 偏置、Mout W=200u 镜像、Rout 30k、PWL 5u 负载在 100.5u 切换；.tran 200u + .measure vout_unload(60-70u)/vout_load1ma(110-120u)；9 个 .alter PVT corner = 3 temp{-40,25,130} × 3 窄工艺{vto±2mV,kp±0.2u}）。供 SUT 开发与本地调试。"},
    {"name": "spec_A.json", "source": "spec_A.json",
     "desc": "公开 A 的 SPEC：vout_unload/vout_load1ma 的变化量限值均 limit_V=0.008 (8mV)。A 实测 variation≈4.8/5.6mV → PASS。"},
    {"name": "task_brief.md", "source": "task_brief.md",
     "desc": "交付接口：python3 pvt_var_judge.py <netlist.sp> <spec.json> <out_dir> → out_dir/verdict.json；交付 outputs/submit.zip（顶层 pvt_var_judge.py）；公开 A 仅示例，判分用隐藏 B。"},
]

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": attachments,
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["pvt_var_judge.py", "verdict.json"],
    "test": check_src,
    "budget": ["max_turns"],
    "metadata": {
        "trace_source": {
            "user": "tongni",
            "host": "hfeg0pkn002",
            "session_file": "1792373325953_z6mt7.messages.json",
            "match_count": 83,
            "real_task_summary": "tongni 在 hfeg0pkn002 上对 cline 说「Vcc2scstdby_tran.sp 用 bsub finesim 丢仿真…variation 是所有 corner 的电压的分布范围要小于 5mV，所以你要读取 measure 的文件，做判断，并给出优化策略」——要求 agent 跑 FineSim tran PVT 多 corner 仿真、读 .measure 文件、判定所有 corner 电压变化范围(max-min)<5mV 的 SPEC 合规性并给优化意见。trace 中 agent 走 LSF bsub + foundry PDK（不可移植），写 check_vcc2sc_stdby_var.py 解析 .mt0、算 variation、判 FAIL(unload 5.13mV/load1mA 15.26mV)、按温度拆分根因。本 case 为 B档 synthesized：保留「PVT variation SPEC 合规判定器」子技能，DUT 用 Level-1 PMOS 自偏置 Vcc2sc（.75 无 foundry PDK/LSF），hspice .alter 跑 PVT corner。"
        },
        "domain": "characterization",
        "layer": "L2",
        "layer_rationale": "真跑 hspice V-2023.12-SP1-1 跨 PVT corner 仿真（.alter 多温度/工艺），解析真实 .mtN measure 文件，是 L2 真跑沙盒工具，非离线 Python 复刻。",
        "test_rationale": test_rationale,
    },
}

# GATE
circled = len(re.findall(r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳]', test_rationale))
cond_labels = sorted(set(re.findall(r'_cond\("([a-z])",', check_src)))
print("k_rationale(circled)=%d  k_check(unique labels %s)=%d" % (circled, cond_labels, len(cond_labels)))
assert circled == 14 and len(cond_labels) == 14, "GATE FAIL"
assert test_rationale.startswith("14 条断言："), "prefix GATE FAIL"

# remove any prior append of this case (idempotent)
lines = open(JSONL).read().splitlines() if os.path.exists(JSONL) else []
kept = []
removed = 0
for l in lines:
    try:
        if json.loads(l).get("task_id") == CASE:
            removed += 1; continue
    except Exception:
        pass
    kept.append(l)
with open(JSONL, "w") as fh:
    fh.write("\n".join(kept) + ("\n" if kept else ""))
print("removed prior copies:", removed)

seen = set()
for l in kept:
    try: seen.add(json.loads(l).get("task_id"))
    except Exception: pass
print("existing unique task_ids:", len(seen))

with open(JSONL, "a") as fh:
    fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify
last = open(JSONL).read().strip().split("\n")[-1]
d = json.loads(last)
assert d["task_id"] == CASE
assert d["test"] == check_src
print("appended OK, task_id=%s, test bytes=%d" % (d["task_id"], len(d["test"])))
print("total lines now:", sum(1 for _ in open(JSONL)))
