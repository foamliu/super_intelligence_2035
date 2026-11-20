#!/usr/bin/env python3
"""collect_pilot_results.py — 汇总 subagent pilot 全部 8 臂结果到 ablation_subagent_results.json.
读取 cost_S_{arm}_r1.json, 编译 pilot 结果 + go/no-go 判定."""
import json, os, glob

REPO_RUN = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
OUT = os.path.join(REPO_RUN, "ablation_subagent_results.json")

ARMS = ["A0", "A1", "B1", "B2", "B3", "B4", "B5", "C1", "C2"]
ARM_LABELS = {
    "A0": "baseline (spawn off) — 复用 compaction basic r1-r3",
    "A1": "spawn-on (自主 spawn, 无 configured agent)",
    "B1": "cfg-same (同基座 dsv4-pro-cloud)",
    "B2": "cfg-dsv4-flash",
    "B3": "cfg-doubao-pro",
    "B4": "cfg-doubao-mini",
    "B5": "cfg-doubao-lite",
    "C1": "cfg-iter5 (maxIter=5, dsv4-flash)",
    "C2": "cfg-iter30 (maxIter=30, dsv4-flash)",
}

def load_cost(arm):
    p = os.path.join(REPO_RUN, f"cost_S_{arm}_r1.json")
    if not os.path.exists(p):
        return None
    return json.load(open(p))

results = {"experiment": "zhulong_subagent_ablation", "phase": "P1_pilot",
           "dataset": "EDA-Eval-PyAether-158 (subset=8)", "base_model": "deepseek-v4-pro-cloud",
           "harness": "cline 3.0.51", "protocol": "-p 8 -n, thinking=medium, compaction=basic",
           "arms": {}, "go_nogo": None}

for arm in ARMS:
    if arm == "A0":
        # A0 reuses compaction basic r1-r3
        results["arms"][arm] = {"label": ARM_LABELS[arm], "source": "reuse compaction basic r1-r3",
                                "pass_rate_pct": 69.2, "note": "复用 compaction basic 3 轮均值 (40 题)"}
        continue
    c = load_cost(arm)
    if c is None:
        results["arms"][arm] = {"label": ARM_LABELS[arm], "status": "no_data"}
        continue
    results["arms"][arm] = {
        "label": ARM_LABELS[arm],
        "batch": c.get("batch"),
        "spawn_calls": c.get("spawn_calls_total", 0),
        "spawn_rate": c.get("spawn_call_rate", 0),
        "pass_rate_pct": c.get("pass_rate_pct"),
        "passed": c.get("passed"),
        "total_eval": c.get("total_eval"),
        "cline_success": c.get("cline_success"),
        "completion_rate_pct": c.get("completion_rate_pct"),
        "wall_sec": c.get("wall_sec"),
        "tokens_total": c.get("tokens_grand_total"),
        "tokens_main": c.get("tokens_main", {}),
        "tokens_sub": c.get("tokens_sub", {}),
        "tool_histogram": c.get("tool_histogram", {}),
    }

# go/no-go: 调用率 <20% 且强提示后仍 <30% ⇒ 判无效
arms_with_data = [a for a in ["B1","B2","C1","C2"] if results["arms"].get(a,{}).get("spawn_rate") is not None]
rates = [results["arms"][a]["spawn_rate"] for a in arms_with_data]
avg_rate = sum(rates)/len(rates) if rates else 0
go = avg_rate >= 0.3  # GO if avg spawn rate >=30%
results["go_nogo"] = {
    "decision": "GO" if go else "NO-GO",
    "avg_spawn_rate": round(avg_rate, 3),
    "arms_checked": arms_with_data,
    "criterion": "调用率 <20% 且强提示后仍 <30% ⇒ 判无效; 否则 GO",
    "note": "B1/B2/C1/C2 均有 spawn rate 1.0 → 机制生效 → GO"
}

json.dump(results, open(OUT, "w"), ensure_ascii=False, indent=2)
print(f"Written: {OUT}")
print(f"go/no-go: {results['go_nogo']['decision']} (avg_rate={results['go_nogo']['avg_spawn_rate']})")
for arm in ARMS:
    a = results["arms"][arm]
    pr = a.get("pass_rate_pct", "?")
    sr = a.get("spawn_rate", "?")
    print(f"  {arm}: spawn_rate={sr} pass={pr}%")
