#!/usr/bin/env python3
"""
Post-train P0 诊断脚本 — 从 EDA-Eval-Framework final_report.json + DeepSeek 全 harness
trace 提取 D1–D6 统计。

D1/D2/D6: 从 cline trace (api_conversation_history.json) 提取（需 trace_parser + trace_reader）。
D3/D4/D5: 从 final_report.json 的 details_per_task 提取。
MiniCPM5-2B 36% 侧: 需 ~/eda_code_eval/（在 .29 上），本脚本如实标注缺失。
"""

import json, os, sys, glob, importlib.util, statistics
from collections import Counter, defaultdict

EVAL_FRAMEWORK = os.path.expanduser("~/code/EDA-Eval-Framework")
EVAL_OUTPUT = os.path.join(EVAL_FRAMEWORK, "output_evaluation")
DATASET_PATH = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
)
EDA_CODE_EVAL = os.path.expanduser("~/eda_code_eval")
EDA_FASTMCP = os.path.expanduser("~/code/eda_fastmcp")
# DeepSeek full-harness traces (103 tasks, 2026-02-09, ≈94% 同口径)
DEEPSEEK_TRACE_DIR = os.path.join(
    EDA_FASTMCP, "pyAether-eval/cline_cli_trace/cline_trace_v1_3/cline_trace"
)

# --- Load trace_parser + trace_reader (importlib, since not a package) ---
def _load_trace_modules():
    """Load trace_parser.py and trace_reader.py via importlib."""
    modules = {}
    tp_path = os.path.join(EDA_FASTMCP, "memory_bank/trace_parser.py")
    tr_path = os.path.join(EDA_FASTMCP, "scripts/trace_reader.py")
    if os.path.isfile(tp_path):
        spec = importlib.util.spec_from_file_location("trace_parser", tp_path)
        modules["tp"] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modules["tp"])
    if os.path.isfile(tr_path):
        spec2 = importlib.util.spec_from_file_location("trace_reader", tr_path)
        modules["tr"] = importlib.util.module_from_spec(spec2)
        spec2.loader.exec_module(modules["tr"])
    return modules


_TRACE_MODS = None

def _get_trace_mods():
    global _TRACE_MODS
    if _TRACE_MODS is None:
        _TRACE_MODS = _load_trace_modules()
    return _TRACE_MODS


def extract_deepseek_trace_diagnostics():
    """
    从 DeepSeek full-harness trace 提取 D1/D2/D6 及辅助统计。
    返回 dict 或 None（trace 目录不存在时）。
    """
    if not os.path.isdir(DEEPSEEK_TRACE_DIR):
        return None
    mods = _get_trace_mods()
    if "tp" not in mods or "tr" not in mods:
        return {"error": "trace_parser.py or trace_reader.py not found"}
    tp = mods["tp"]
    load_trace = mods["tr"].load_trace

    trace_dirs = sorted(
        d for d in os.listdir(DEEPSEEK_TRACE_DIR)
        if os.path.isdir(os.path.join(DEEPSEEK_TRACE_DIR, d))
    )
    n_total = len(trace_dirs)
    all_tool_calls = 0
    all_tool_results = 0
    tool_name_counter = Counter()
    err_type_counter = Counter()
    n_code_exec_per_task = []
    n_tool_calls_per_task = []
    n_msgs_per_task = []
    n_errors_per_task = []
    assistant_turns = 0
    has_timeout = 0
    has_assertion_err = 0
    has_exec_err = 0
    n_traces_ok = 0

    for td in trace_dirs:
        tpath = os.path.join(DEEPSEEK_TRACE_DIR, td)
        try:
            tr = load_trace(tpath)
        except Exception:
            continue
        tcs = tp.extract_tool_calls_from_trace(tr)
        trs = tp.extract_tool_results_from_trace(tr)
        n_traces_ok += 1
        all_tool_calls += len(tcs)
        all_tool_results += len(trs)
        for c in tcs:
            tool_name_counter[c.get("tool", "?")] += 1
        n_tool_calls_per_task.append(len(tcs))
        n_msgs_per_task.append(len(tr))
        for m in tr:
            if isinstance(m, dict) and m.get("role") == "assistant":
                assistant_turns += 1
        errs = [
            r for r in trs
            if r.get("has_error") in (True, "True", "true")
        ]
        n_errors_per_task.append(len(errs))
        n_exec = 0
        for c in tcs:
            if c.get("tool") in (
                "run_pyAether_code_tool", "run_code", "probe_pyAether_code",
            ):
                n_exec += 1
        n_code_exec_per_task.append(n_exec)
        for r in errs:
            ec = r.get("error_code", "UNKNOWN")
            err_type_counter[ec] += 1
            if ec == "ASSERTION_ERROR":
                has_assertion_err += 1
            elif ec in ("SANDBOX_TIMEOUT", "TIMEOUT", "TIME_OUT"):
                has_timeout += 1
            else:
                has_exec_err += 1

    d1 = (all_tool_calls / assistant_turns) if assistant_turns else 0
    d2 = (all_tool_calls / n_traces_ok) if n_traces_ok else 0
    d3r = (has_timeout / n_traces_ok) if n_traces_ok else 0

    return {
        "source": "cline_trace_v1_3 (DeepSeek full-harness 2026-02-09, 103 tasks)",
        "n_trace_dirs": n_total,
        "n_traces_parsed": n_traces_ok,
        "total_tool_calls": all_tool_calls,
        "total_tool_results": all_tool_results,
        "total_assistant_turns": assistant_turns,
        "D1_legality_proxy": round(d1, 4),
        "D1_note": "解析成功 tool_call / assistant 轮次（强度代理，非严格合法率）",
        "D2_freq_per_task": round(d2, 2),
        "D2_tool_breakdown": dict(tool_name_counter.most_common()),
        "D3_timeout_tasks": has_timeout,
        "D3_timeout_ratio": round(d3r, 4),
        "D4_error_breakdown": dict(err_type_counter.most_common()),
        "D4_assertion_err_tasks": has_assertion_err,
        "D4_exec_err_tasks": has_exec_err,
        "D6_exec_per_task_mean": round(statistics.mean(n_code_exec_per_task), 2) if n_code_exec_per_task else 0,
        "D6_exec_per_task_median": statistics.median(n_code_exec_per_task) if n_code_exec_per_task else 0,
        "D6_exec_per_task_dist": dict(Counter(n_code_exec_per_task).most_common()),
        "avg_msgs_per_task": round(statistics.mean(n_msgs_per_task), 1) if n_msgs_per_task else 0,
        "avg_tool_calls_per_task": round(statistics.mean(n_tool_calls_per_task), 2) if n_tool_calls_per_task else 0,
        "avg_errors_per_task": round(statistics.mean(n_errors_per_task), 2) if n_errors_per_task else 0,
    }

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

def compute_d1(reports_selected, trace_diag=None):
    """D1: 工具调用合法率（格式合法 tool_call / 总数）。
    DeepSeek 侧: 从本机 trace 提取（强度代理 = tool_calls / assistant_turns）。
    MiniCPM5-2B 36% 侧: 需 ~/eda_code_eval/（在 .29 上），如实标注缺失。
    """
    eda_code_eval_exists = os.path.isdir(EDA_CODE_EVAL)
    result = {
        "deepseek_full_harness": None,
        "minicpm5_36pct": {
            "status": "字段缺失",
            "value": None,
            "reason": (
                "MiniCPM5-2B 36% 全 harness trace 不在本节点（在 .29 上 ~/eda_code_eval/）。"
                "需要补抓: MiniCPM5-2B 36% 运行的完整 trace 目录。"
            ),
            "eda_code_eval_exists": eda_code_eval_exists,
        },
    }
    if trace_diag and "error" not in trace_diag:
        result["deepseek_full_harness"] = {
            "status": "已计算（强度代理）",
            "value": trace_diag["D1_legality_proxy"],
            "note": trace_diag["D1_note"],
            "total_tool_calls": trace_diag["total_tool_calls"],
            "total_assistant_turns": trace_diag["total_assistant_turns"],
            "n_traces": trace_diag["n_traces_parsed"],
        }
    elif trace_diag and "error" in trace_diag:
        result["deepseek_full_harness"] = {"status": "错误", "reason": trace_diag["error"]}
    else:
        result["deepseek_full_harness"] = {
            "status": "字段缺失",
            "value": None,
            "reason": f"DeepSeek trace 目录不存在: {DEEPSEEK_TRACE_DIR}",
        }
    return result

def compute_d2(reports_selected, trace_diag=None):
    """D2: 工具调用频次（每任务平均调用次数）。
    DeepSeek 侧: 从本机 trace 提取。
    MiniCPM5-2B 36% 侧: 需 ~/eda_code_eval/，如实标注缺失。
    """
    eda_code_eval_exists = os.path.isdir(EDA_CODE_EVAL)
    result = {
        "deepseek_full_harness": None,
        "minicpm5_36pct": {
            "status": "字段缺失",
            "value": None,
            "reason": (
                "MiniCPM5-2B 36% 全 harness trace 不在本节点。"
                "需要补抓: MiniCPM5-2B 36% 运行的完整 trace 目录。"
            ),
            "eda_code_eval_exists": eda_code_eval_exists,
        },
    }
    if trace_diag and "error" not in trace_diag:
        result["deepseek_full_harness"] = {
            "status": "已计算",
            "value": trace_diag["D2_freq_per_task"],
            "tool_breakdown": trace_diag["D2_tool_breakdown"],
            "n_traces": trace_diag["n_traces_parsed"],
        }
    elif trace_diag and "error" in trace_diag:
        result["deepseek_full_harness"] = {"status": "错误", "reason": trace_diag["error"]}
    else:
        result["deepseek_full_harness"] = {
            "status": "字段缺失",
            "value": None,
            "reason": f"DeepSeek trace 目录不存在: {DEEPSEEK_TRACE_DIR}",
        }
    return result

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

def compute_d6(reports_selected, trace_diag=None):
    """D6: 平均迭代轮数 Φ 分布。
    DeepSeek 侧: 从本机 trace 统计每任务代码执行次数（mean/median/dist）。
    MiniCPM5-2B 36% 侧: 需 ~/eda_code_eval/，如实标注缺失。
    """
    eda_code_eval_exists = os.path.isdir(EDA_CODE_EVAL)
    result = {
        "deepseek_full_harness": None,
        "minicpm5_36pct": {
            "status": "字段缺失",
            "value": None,
            "reason": (
                "MiniCPM5-2B 36% 全 harness trace 不在本节点。"
                "D6 需要从 cline trace 中统计每任务的 assistant-tool_result 循环次数。"
                "需要补抓: MiniCPM5-2B 的完整 trace 目录。"
            ),
            "eda_code_eval_exists": eda_code_eval_exists,
        },
    }
    if trace_diag and "error" not in trace_diag:
        result["deepseek_full_harness"] = {
            "status": "已计算",
            "mean": trace_diag["D6_exec_per_task_mean"],
            "median": trace_diag["D6_exec_per_task_median"],
            "distribution": trace_diag["D6_exec_per_task_dist"],
            "n_traces": trace_diag["n_traces_parsed"],
            "note": "每任务代码执行次数（run_code/run_pyAether_code_tool/probe_pyAether_code）",
        }
    elif trace_diag and "error" in trace_diag:
        result["deepseek_full_harness"] = {"status": "错误", "reason": trace_diag["error"]}
    else:
        result["deepseek_full_harness"] = {
            "status": "字段缺失",
            "value": None,
            "reason": f"DeepSeek trace 目录不存在: {DEEPSEEK_TRACE_DIR}",
        }
    return result

def main():
    print("=" * 70)
    print("Post-train P0 诊断: D1–D6 统计提取")
    print("=" * 70)
    print(f"\n[数据源检查]")
    print(f"  EDA-Eval-Framework: {EVAL_FRAMEWORK} {'OK' if os.path.isdir(EVAL_FRAMEWORK) else 'MISSING'}")
    print(f"  Dataset (158 tasks): {DATASET_PATH} {'OK' if os.path.isfile(DATASET_PATH) else 'MISSING'}")
    print(f"  ~/eda_code_eval/: {EDA_CODE_EVAL} {'OK' if os.path.isdir(EDA_CODE_EVAL) else 'MISSING (on .29)'}")
    print(f"  DeepSeek trace dir: {DEEPSEEK_TRACE_DIR} {'OK' if os.path.isdir(DEEPSEEK_TRACE_DIR) else 'MISSING'}")
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

    # --- Extract DeepSeek trace diagnostics (D1/D2/D6) ---
    print(f"\n[DeepSeek trace extraction] {DEEPSEEK_TRACE_DIR}")
    trace_diag = extract_deepseek_trace_diagnostics()
    if trace_diag and "error" not in trace_diag:
        print(f"  parsed {trace_diag['n_traces_parsed']}/{trace_diag['n_trace_dirs']} traces")
        print(f"  D1={trace_diag['D1_legality_proxy']} D2={trace_diag['D2_freq_per_task']} D6_mean={trace_diag['D6_exec_per_task_mean']}")
    elif trace_diag and "error" in trace_diag:
        print(f"  ERROR: {trace_diag['error']}")
    else:
        print(f"  trace dir not found, D1/D2/D6 DeepSeek side will be marked missing")

    d1 = compute_d1(selected, trace_diag)
    d2 = compute_d2(selected, trace_diag)
    d3 = compute_d3(primary)
    d4 = compute_d4(primary)
    d5 = compute_d5(primary, task_map)
    d6 = compute_d6(selected, trace_diag)

    ds_d1 = d1.get("deepseek_full_harness", {})
    ds_d2 = d2.get("deepseek_full_harness", {})
    ds_d6 = d6.get("deepseek_full_harness", {})
    print(f"\n[D1] DeepSeek={ds_d1.get('status')} val={ds_d1.get('value')} | MiniCPM5={d1.get('minicpm5_36pct',{}).get('status')}")
    print(f"[D2] DeepSeek={ds_d2.get('status')} val={ds_d2.get('value')} | MiniCPM5={d2.get('minicpm5_36pct',{}).get('status')}")
    print(f"[D3] timeout={d3.get('generation_timeout')}, fail={d3.get('generation_failure')}, combined={d3.get('combined_truncation_rate')}")
    print(f"[D4] pass={d4.get('pass_rate')}, assert={d4.get('assertion_pct')}, exec={d4.get('execution_pct')}")
    print(f"[D4] judgment: {d4.get('judgment')}")
    if d5.get("_status") == "已计算":
        for k, v in d5.items():
            if not k.startswith("_"):
                print(f"[D5] {k}: {v['passed']}/{v['total']} ({v['pass_rate']})")
    print(f"[D6] DeepSeek={ds_d6.get('status')} mean={ds_d6.get('mean')} | MiniCPM5={d6.get('minicpm5_36pct',{}).get('status')}")

    result = {
        "meta": {"machine": ".17", "dataset": "EDA-Eval-PyAether-v20260311.jsonl (158 tasks)",
            "scenario_distribution": dict(scenario_counts.most_common()),
            "eda_code_eval_exists": os.path.isdir(EDA_CODE_EVAL),
            "deepseek_trace_dir_exists": os.path.isdir(DEEPSEEK_TRACE_DIR),
            "note": "DeepSeek full-harness D1/D2/D6 extracted from local traces (cline_trace_v1_3, 103 tasks). MiniCPM5-2B 36% side needs ~/eda_code_eval/ (on .29), marked missing. D3/D4/D5 from final_report.json (zhulong_deepseek_v32 ~70% code-gen mode)."},
        "available_runs": [{"dir": r["_dir"], "model": r["model_name"], "pass_rate": r["metrics"]["pass_rate"], "n_tasks": r["summary"]["total_problems_evaluated"]} for r in reports],
        "selected_runs": {n: {"dir": r["_dir"] if r else None, "model": r["model_name"] if r else None, "pass_rate": r["metrics"]["pass_rate"] if r else None, "n_tasks": r["summary"]["total_problems_evaluated"] if r else None} for n, r in selected.items()},
        "deepseek_trace_diagnostics": trace_diag,
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
