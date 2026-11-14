#!/usr/bin/env python3
# posttrain_attribution_3615_profile.py
# 36.15 run1 (15.82%) 逐题画像 —— Task B profiling（用户令 2026-11-14 19:2x）
# 输入：attribution_3615_run1/{final_report.json, completed_code_generation.jsonl,
#        execution_results.jsonl, codegen_rejection_stats.json}
# 输出：attribution_3615_run1_profile.json（可复算）
# 纪律：只读既有 run1 trace，不挑题、不改 benchmark。
import json, os, sys, collections

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "attribution_3615_run1")
fr = json.load(open(os.path.join(BASE, "final_report.json")))
cg = [json.loads(l) for l in open(os.path.join(BASE, "completed_code_generation.jsonl")) if l.strip()]
ex = [json.loads(l) for l in open(os.path.join(BASE, "execution_results.jsonl")) if l.strip()]
rej = json.load(open(os.path.join(BASE, "codegen_rejection_stats.json")))
det = fr["details_per_task"]

ex_by_id = {r["task_id"]: r for r in ex}

# details_per_task 是权威逐题结果（generation_statuses / execution_statuses / num_correct）
total = len(det)
buckets = collections.defaultdict(list)   # key -> [task_id,...]
gen_status_counter = collections.Counter()
exec_status_counter = collections.Counter()
quality_fail = []
for tid, d in det.items():
    gs = (d.get("generation_statuses") or ["unknown"])[0]
    es = (d.get("execution_statuses") or ["unknown"])[0]
    gen_status_counter[gs] += 1
    exec_status_counter[es] += 1
    nc = d.get("num_correct", 0)
    if gs == "success" and es == "passed":
        buckets["gen_success_exec_passed"].append(tid)
    elif gs == "success" and es == "failed":
        buckets["gen_success_exec_failed"].append(tid)
        e = ex_by_id.get(tid, {})
        quality_fail.append({
            "task_id": tid,
            "runtime_key": e.get("runtime_key") or d.get("runtime_key"),
            "stderr_head": (e.get("stderr") or "")[:400],
            "stdout_head": (e.get("stdout") or "")[:200],
        })
    else:
        buckets["gen_fail_or_timeout"].append(tid)

gen_success = gen_status_counter.get("success", 0)
gen_fail = gen_status_counter.get("fail", 0)
gen_timeout = gen_status_counter.get("timeout", 0)
passed_n = exec_status_counter.get("passed", 0)

funnel = {
    "total": total,
    "generation_statuses": dict(gen_status_counter),
    "execution_statuses": dict(exec_status_counter),
    "codegen_success": gen_success,
    "codegen_success_rate": round(gen_success / total, 4),
    "codegen_fail": gen_fail,
    "codegen_timeout": gen_timeout,
    "codegen_fail_or_timeout": gen_fail + gen_timeout,
    "codegen_fail_or_timeout_rate": round((gen_fail + gen_timeout) / total, 4),
    "passed": passed_n,
    "pass_rate": round(passed_n / total, 4),
    "gen_success_then_pass": len(buckets["gen_success_exec_passed"]),
    "gen_success_then_fail": len(buckets["gen_success_exec_failed"]),
    "gen_success_pass_rate": round(len(buckets["gen_success_exec_passed"]) / max(1, gen_success), 4),
}

genfail_breakdown = {"gen_fail": gen_fail, "gen_timeout": gen_timeout, "not_executed": gen_fail + gen_timeout}
genfail_ids = buckets["gen_fail_or_timeout"]
passed_ids = buckets["gen_success_exec_passed"]

# 5. 拒绝归因（来自 codegen_rejection_stats）
rejection_summary = {
    "rejected_total": rej.get("rejected_total"),
    "top_tools": dict(collections.Counter(rej.get("rejection_by_tool", {})).most_common(8)),
    "run_commands_string_not_array": rej.get("run_commands_string_not_array"),
    "submit_and_exit_count": rej.get("submit_and_exit_count"),
    "timeout_markers": rej.get("timeout_markers"),
    "eda_flow_sandbox_calls": rej.get("eda_flow_calls"),
    "pyAether_rag_calls": rej.get("pyAether_MCP_calls"),
}

# 6. 与 .17（3.04%）对照要点
contrast = {
    "metric": "same model minicpm5-2b-sft step105 (verified .17:8096 /v1/models id=minicpm5-2b-sft-v39-final root=global_step_105; reverse tunnel 36.15:18096->.17:8096)",
    "model_name_field_note": "final_report.json model_name=zhulong_deepseek_v32 is a STALE config label (EDA-Eval-Framework/config.yaml active_model), NOT the served model; calculate_results.py:109 reads config active_model",
    "dot17_submit_storm": "13699 submit_and_exit / 91.77% error / degenerate_pass 60.63% (RCA v2, 790-task run)",
    "dot3615_submit": f"{rej.get('submit_and_exit_count')} submit_and_exit; sandbox actively used (eda_flow open_session={rej.get('eda_flow_calls',{}).get('open_session')}, run_code={rej.get('eda_flow_calls',{}).get('run_code')}); RAG used (search_apis={rej.get('pyAether_MCP_calls',{}).get('search_apis')}, get_api_details={rej.get('pyAether_MCP_calls',{}).get('get_api_details')})",
    "dot3615_bottleneck": f"codegen completion {gen_success}/{total}={funnel['codegen_success_rate']} (not code quality {funnel['gen_success_pass_rate']}); dominant rejection run_commands={rej.get('rejection_by_tool',{}).get('run_commands')} (string-not-array={rej.get('run_commands_string_not_array')})",
}

out = {
    "source": "attribution_3615_run1/ (36.15 run1, timestamp 2026-11-14T15:29:32, pass_rate 0.1582)",
    "funnel": funnel,
    "genfail_breakdown_by_runtime": dict(genfail_breakdown),
    "genfail_ids": genfail_ids,
    "passed_ids": passed_ids,
    "quality_fail_details": quality_fail,
    "rejection_summary": rejection_summary,
    "contrast_dot17_vs_dot3615": contrast,
    "task_b_implication": (
        "5x jump is same-model env change. 36.15 bottleneck = code-gen COMPLETION (18.35%), "
        "dominated by tool-call format errors (run_commands string-not-array). P0-tool-format patch "
        "directly targets this. Code quality once generated is high (86.2%). "
        "Prompt iteration ROI: fix tool format -> raise completion -> raise pass rate above 15.82%."
    ),
}

with open(os.path.join(os.path.dirname(BASE), "attribution_3615_run1_profile.json"), "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(json.dumps(out, ensure_ascii=False, indent=2))
