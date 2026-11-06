#!/usr/bin/env python3
"""
Post-train P0 诊断脚本 — 从 EDA-Eval-Framework final_report.json 提取 D1–D6 统计。
"""

import json, os, sys, glob
from collections import Counter, defaultdict

EVAL_FRAMEWORK = os.path.expanduser("~/code/EDA-Eval-Framework")
EVAL_OUTPUT = os.path.join(EVAL_FRAMEWORK, "output_evaluation")
DATASET_PATH = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
)
EDA_CODE_EVAL = os.path.expanduser("~/eda_code_eval")

def load_dataset():
    with open(DATASET_PATH) as f:
        tasks = [json.loads(l) for l in f]
    task_map = {}
    for t in tasks:
        tid = t["task_id"]
        task_map[tid] = t["metadata"]
        num = tid.split("-")[-1]
        task_map[f"EDA-Eval-PyAether/{num}"] = t["metadata"]
        task_map[f"EDA-Eval-PyAether-{num}"] = t["metadata"]
    return task_map, tasks

def load_all_reports():
    reports = []
    for path in sorted(glob.glob(os.path.join(EVAL_OUTPUT, "*/final_report.json"))):
        with open(path) as f:
            r = json.load(f)
        r["_path"] = path
        r["_dir"] = os.path.basename(os.path.dirname(path))
        reports.append(r)
    return reports

def select_runs(reports):
    runs_158 = [r for r in reports if r.get("summary",{}).get("total_problems_evaluated")==158]
    deepseek_158 = [r for r in runs_158 if "deepseek" in r.get("model_name","").lower()]
    zhulong_158 = [r for r in runs_158 if r.get("model_name")=="zhulong"]
    aether = [r for r in reports if "aether" in r.get("model_name","").lower()]
    return {
        "best_deepseek": max(deepseek_158, key=lambda r: r["metrics"]["pass_rate"]) if deepseek_158 else None,
        "zhulong_baseline": zhulong_158[0] if zhulong_158 else None,
        "weak_model": aether[0] if aether else None,
    }

def compute_d1(reports_selected):
    eda_code_eval_exists = os.path.isdir(EDA_CODE_EVAL)
    return {
        "status": "字段缺失",
        "value": None,
        "reason": (
            "final_report.json 不含工具调用(tool_call)数据。"
            "D1 需要从 cline trace (~/eda_code_eval/<batch_id>/trace/) 中提取，"
            "使用 eda_fastmcp/scripts/trace_reader.py 的 extract_tool_calls_from_trace()。"
            f"本机 ~/eda_code_eval/ 目录{'存在' if eda_code_eval_exists else '不存在(在 .29 上)'}。"
            "需要补抓: MiniCPM5-2B 36% 运行的完整 trace 目录。"
        ),
        "eda_code_eval_exists": eda_code_eval_exists,
    }

def compute_d2(reports_selected):
    eda_code_eval_exists = os.path.isdir(EDA_CODE_EVAL)
    return {
        "status": "字段缺失",
        "value": None,
        "reason": (
            "final_report.json 不含工具调用频次数据。"
            "D2 需要从 cline trace 中统计每个任务的工具调用次数。"
            f"本机 ~/eda_code_eval/ 目录{'存在' if eda_code_eval_exists else '不存在(在 .29 上)'}。"
            "需要补抓: 各模型的完整 trace 目录 + DeepSeek-V4-Pro 对照 trace。"
        ),
        "eda_code_eval_exists": eda_code_eval_exists,
    }

def compute_d3(report):
    if report is None:
        return {"status": "无数据", "value": None}
    summary = report.get("summary", {})
    gen_stats = summary.get("generation_statistics", {})
    total = summary.get("total_problems_evaluated", 0)
    timeout_count = gen_stats.get("timeout", 0)
    failure_count = gen_stats.get("failure", 0) + gen_stats.get("fail", 0)
    success_count = gen_stats.get("success", 0)
    details = report.get("details_per_task", {})
    task_timeout = sum(1 for d in details.values() for et in d.get("error_types",[]) if "timeout" in et.lower())
    task_gen_fail = sum(1 for d in details.values() for et in d.get("error_types",[]) if "generation fail" in et.lower() or "generation failure" in et.lower())
    timeout_rate = timeout_count / total if total > 0 else 0
    failure_rate = failure_count / total if total > 0 else 0
    combined_rate = (timeout_count + failure_count) / total if total > 0 else 0
    return {
        "status": "已计算",
        "total_tasks": total,
        "generation_timeout": timeout_count,
        "generation_failure": failure_count,
        "generation_success": success_count,
        "timeout_rate": f"{timeout_rate:.1%}",
        "failure_rate": f"{failure_rate:.1%}",
        "combined_truncation_rate": f"{combined_rate:.1%}",
        "task_level_timeout": task_timeout,
        "task_level_gen_fail": task_gen_fail,
        "judgment": (
            "高(>15%) → 长上下文适配是 post-train 前置项" if combined_rate > 0.15
            else "中(5-15%) → 需关注长上下文适配" if combined_rate > 0.05
            else "低(<5%) → 长上下文不是主要瓶颈"
        ),
    }

def compute_d4(report):
    if report is None:
        return {"status": "无数据", "value": None}
    details = report.get("details_per_task", {})
    error_type_counts = Counter()
    failed_tasks = 0
    passed_tasks = 0
    assertion_errors = 0
    generation_errors = 0
    execution_errors = 0
    other_errors = 0
    for tid, d in details.items():
        if d.get("num_correct", 0) > 0:
            passed_tasks += 1
        else:
            failed_tasks += 1
        for et in d.get("error_types", []):
            error_type_counts[et] += 1
            et_lower = et.lower()
            if "assert" in et_lower:
                assertion_errors += 1
            elif "generation" in et_lower and ("fail" in et_lower or "timeout" in et_lower):
                generation_errors += 1
            elif "unknown" in et_lower or "error" in et_lower or "exception" in et_lower:
                execution_errors += 1
            else:
                other_errors += 1
    total_errors = assertion_errors + generation_errors + execution_errors + other_errors
    return {
        "status": "已计算",
        "total_tasks": len(details),
        "passed": passed_tasks, "failed": failed_tasks,
        "pass_rate": f"{passed_tasks/len(details):.1%}" if details else "N/A",
        "error_type_breakdown": dict(error_type_counts.most_common()),
        "assertion_errors": assertion_errors, "generation_errors": generation_errors,
        "execution_errors": execution_errors, "other_errors": other_errors,
        "total_errors": total_errors,
        "assertion_pct": f"{assertion_errors/total_errors:.1%}" if total_errors > 0 else "N/A",
        "generation_pct": f"{generation_errors/total_errors:.1%}" if total_errors > 0 else "N/A",
        "execution_pct": f"{execution_errors/total_errors:.1%}" if total_errors > 0 else "N/A",
        "judgment": (
            "断言失败为主 → RL 价值更大" if assertion_errors > execution_errors + generation_errors
            else "执行/生成报错为主 → SFT 领域语料可大幅回收" if execution_errors + generation_errors > assertion_errors
            else "断言与报错均衡 → SFT + RL 双管齐下"
        ),
    }

def compute_d5(report, task_map):
    if report is None:
        return {"status": "无数据", "value": None}
    details = report.get("details_per_task", {})
    scenario_stats = defaultdict(lambda: {"total": 0, "passed": 0, "tasks": []})
    for tid, d in details.items():
        meta = task_map.get(tid)
        if meta is None:
            meta = task_map.get(tid.replace("/", "-"))
        if meta is None:
            parts = tid.split("/")
            if len(parts) > 1:
                meta = task_map.get(f"EDA-Eval-PyAether-{parts[-1]}")
        scenario = meta.get("scenario", "Unknown") if meta else "Unknown"
        category = meta.get("category", "Unknown") if meta else "Unknown"
        scenario_stats[scenario]["total"] += 1
        if d.get("num_correct", 0) > 0:
            scenario_stats[scenario]["passed"] += 1
        scenario_stats[scenario]["tasks"].append({"task_id": tid, "passed": d.get("num_correct",0)>0, "category": category})
    result = {}
    for scenario, stats in sorted(scenario_stats.items(), key=lambda x: -x[1]["total"]):
        result[scenario] = {"total": stats["total"], "passed": stats["passed"],
            "pass_rate": f"{stats['passed']/stats['total']:.1%}" if stats["total"]>0 else "N/A"}
    category_stats = defaultdict(lambda: {"total": 0, "passed": 0})
    for scenario, stats in scenario_stats.items():
        for t in stats["tasks"]:
            cat = t["category"]
            category_stats[cat]["total"] += 1
            if t["passed"]:
                category_stats[cat]["passed"] += 1
    result["_categories"] = {cat: {"total": s["total"], "passed": s["passed"],
        "pass_rate": f"{s['passed']/s['total']:.1%}" if s["total"]>0 else "N/A"}
        for cat, s in sorted(category_stats.items(), key=lambda x: -x[1]["total"])}
    result["_status"] = "已计算"
    return result

def compute_d6(reports_selected):
    eda_code_eval_exists = os.path.isdir(EDA_CODE_EVAL)
    return {
        "status": "字段缺失",
        "value": None,
        "reason": (
            "final_report.json 的 num_samples=1 (单 trace 原则), 不含迭代轮数。"
            "D6 需要从 cline trace 中统计每任务的 assistant-tool_result 循环次数。"
            f"本机 ~/eda_code_eval/ 目录{'存在' if eda_code_eval_exists else '不存在(在 .29 上)'}。"
            "需要补抓: MiniCPM5-2B + DeepSeek-V4-Pro 的完整 trace 目录。"
        ),
        "eda_code_eval_exists": eda_code_eval_exists,
    }

def main():
    print("=" * 70)
    print("Post-train P0 诊断: D1–D6 统计提取")
    print("=" * 70)
    print(f"\n[数据源检查]")
    print(f"  EDA-Eval-Framework: {EVAL_FRAMEWORK} {'OK' if os.path.isdir(EVAL_FRAMEWORK) else 'MISSING'}")
    print(f"  Dataset (158 tasks): {DATASET_PATH} {'OK' if os.path.isfile(DATASET_PATH) else 'MISSING'}")
    print(f"  ~/eda_code_eval/: {EDA_CODE_EVAL} {'OK' if os.path.isdir(EDA_CODE_EVAL) else 'MISSING (on .29)'}")
    task_map, tasks = load_dataset()
    scenario_counts = Counter(t["metadata"]["scenario"] for t in tasks)
    print(f"\n[158 tasks] scenarios: {dict(scenario_counts.most_common())}")
    reports = load_all_reports()
    print(f"\n[{len(reports)} eval runs found]")
    for r in reports:
        print(f"  {r['_dir']}: model={r['model_name']}, pass_rate={r['metrics']['pass_rate']:.1%}, n={r['summary']['total_problems_evaluated']}")
    selected = select_runs(reports)
    primary = selected["best_deepseek"]
    baseline = selected["zhulong_baseline"]
    d1 = compute_d1(selected)
    d2 = compute_d2(selected)
    d3 = compute_d3(primary)
    d4 = compute_d4(primary)
    d5 = compute_d5(primary, task_map)
    d6 = compute_d6(selected)
    print(f"\n[D1] {d1['status']} | [D2] {d2['status']} | [D6] {d6['status']}")
    print(f"[D3] timeout={d3.get('generation_timeout')}, fail={d3.get('generation_failure')}, combined={d3.get('combined_truncation_rate')}")
    print(f"[D4] pass={d4.get('pass_rate')}, assert={d4.get('assertion_pct')}, exec={d4.get('execution_pct')}")
    print(f"[D4] judgment: {d4.get('judgment')}")
    if d5.get("_status") == "已计算":
        for k, v in d5.items():
            if not k.startswith("_"):
                print(f"[D5] {k}: {v['passed']}/{v['total']} ({v['pass_rate']})")
    result = {
        "meta": {"machine": ".17", "dataset": "EDA-Eval-PyAether-v20260311.jsonl (158 tasks)",
            "scenario_distribution": dict(scenario_counts.most_common()),
            "eda_code_eval_exists": os.path.isdir(EDA_CODE_EVAL),
            "note": "~/eda_code_eval/ not on .17 (on .29). MiniCPM5-2B 36% & DeepSeek 94% runs not local. Using zhulong_deepseek_v32 (~70%) as primary. D1/D2/D6 need trace data, marked missing."},
        "available_runs": [{"dir": r["_dir"], "model": r["model_name"], "pass_rate": r["metrics"]["pass_rate"], "n_tasks": r["summary"]["total_problems_evaluated"]} for r in reports],
        "selected_runs": {n: {"dir": r["_dir"] if r else None, "model": r["model_name"] if r else None, "pass_rate": r["metrics"]["pass_rate"] if r else None, "n_tasks": r["summary"]["total_problems_evaluated"] if r else None} for n, r in selected.items()},
        "D1_tool_call_legal_rate": d1, "D2_tool_call_frequency": d2,
        "D3_truncation_rate": d3, "D4_failure_type_breakdown": d4,
        "D5_per_scenario_pass_rate": d5, "D6_iteration_rounds": d6,
    }
    if baseline:
        result["baseline_zhulong"] = {"D3": compute_d3(baseline), "D4": compute_d4(baseline), "D5": compute_d5(baseline, task_map)}
    output_path = os.path.join(os.path.dirname(__file__), "posttrain_diag_d1d6_results.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n[Saved] {output_path}")
    return result

if __name__ == "__main__":
    main()
