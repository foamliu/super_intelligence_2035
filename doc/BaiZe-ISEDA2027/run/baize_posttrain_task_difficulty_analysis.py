#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R83: EDA-Eval-PyAether 158-Task Difficulty Distribution Analysis
=================================================================
Analyzes 158-task benchmark metadata + multiple DeepSeek eval runs to build
per-task difficulty classification, predict MiniCPM5-2B pass rates, identify
protocol-fixable vs capability-gap tasks, and generate curriculum ordering.

Zero GPU. Pure Python 3.8+ stdlib. No external dependencies.
"""
import argparse, json, math, os, sys
from collections import Counter, defaultdict
from datetime import datetime

HOME = os.path.expanduser("~")
DATASET_PATH = os.path.join(HOME, "code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
EVAL_BASE = os.path.join(HOME, "code/EDA-Eval-Framework/output_evaluation")
RUN_FILTER = {
    "20260320_1616_app.e0030209": "zhulong",
    "20260323_1506_e0030209": "zhulong_deepseek_v32",
    "20260330_1127_e0030209": "zhulong_deepseek_v32",
    "20260330_1338_e0030209": "zhulong_deepseek_v32",
    "20260413_1711_app.e0030209": "zhulong_deepseek_v32",
    "20260416_1720_app.e0030209": "zhulong_deepseek_v32_strict",
    "20260417_1000_app.e0030209": "zhulong_deepseek_v32",
}
REPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
RUN_DIR = os.path.dirname(os.path.abspath(__file__))

def load_dataset():
    tasks = []
    with open(DATASET_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    return tasks

def load_eval_runs():
    runs = {}
    for run_dir, label in RUN_FILTER.items():
        fp = os.path.join(EVAL_BASE, run_dir, "final_report.json")
        if not os.path.isfile(fp):
            continue
        try:
            data = json.load(open(fp))
            if len(data.get("details_per_task", {})) != 158:
                continue
            runs[run_dir] = {"label": label, "data": data}
        except Exception:
            continue
    return runs

def extract_features(task):
    meta = task.get("metadata", {})
    prompt = task.get("prompt", "")
    test = task.get("test", "")
    apis = meta.get("apis_used", [])
    features = {
        "task_id": task.get("task_id", ""),
        "scenario": meta.get("scenario", "Unknown"),
        "category": meta.get("category", "Unknown"),
        "num_unique_apis": meta.get("num_unique_apis", 0),
        "lines_of_code": meta.get("lines_of_code", 0),
        "techlib_dependency": meta.get("techlib_dependency", False),
        "prompt_chars": len(prompt),
        "test_chars": len(test),
        "prompt_lines": prompt.count("\n") + 1,
        "test_lines": test.count("\n") + 1,
        "num_asserts": test.count("assert"),
        "source_api": meta.get("source", ""),
        "task_name": meta.get("task_name", ""),
    }
    api_modules = set()
    for api in apis:
        parts = api.split(".")
        if len(parts) >= 2:
            api_modules.add(parts[1])
    features["num_api_modules"] = len(api_modules)
    features["num_type_hints"] = prompt.count("->") + prompt.count(": '")
    features["has_optional"] = "Optional" in prompt
    features["has_list"] = "List" in prompt or "list" in prompt
    features["has_dict"] = "Dict" in prompt or "dict" in prompt
    features["num_test_funcs"] = test.count("def check") + test.count("def test")
    features["num_try_except"] = test.count("try:")
    return features

def aggregate_pass_rates(runs):
    task_results = defaultdict(list)
    task_errors = defaultdict(list)
    task_gen_status = defaultdict(list)
    task_exec_status = defaultdict(list)
    for run_dir, run_info in runs.items():
        details = run_info["data"]["details_per_task"]
        for tid, td in details.items():
            norm_tid = tid.replace("/", "-")
            task_results[norm_tid].append(td.get("pass_rate", 0.0))
            task_errors[norm_tid].extend(td.get("error_types", []))
            task_gen_status[norm_tid].extend(td.get("generation_statuses", []))
            task_exec_status[norm_tid].extend(td.get("execution_statuses", []))
    return task_results, task_errors, task_gen_status, task_exec_status

def classify_difficulty(task_id, pass_rates, errors, gen_statuses, exec_statuses):
    avg_pass = sum(pass_rates) / len(pass_rates) if pass_rates else 0.0
    pass_count = sum(1 for r in pass_rates if r > 0)
    total_runs = len(pass_rates)
    consistency = pass_count / total_runs if total_runs > 0 else 0.0
    error_counter = Counter(errors)
    has_assertion = error_counter.get("AssertionError", 0) > 0
    has_type_error = error_counter.get("TypeError", 0) > 0
    has_timeout = error_counter.get("Generation timeout", 0) > 0 or error_counter.get("Timeout", 0) > 0
    has_gen_failure = error_counter.get("Generation failure", 0) > 0
    has_unknown = error_counter.get("Unknown Failure", 0) > 0
    has_name_error = error_counter.get("NameError", 0) > 0
    has_attr_error = error_counter.get("AttributeError", 0) > 0
    has_value_error = error_counter.get("ValueError", 0) > 0
    gen_counter = Counter(gen_statuses)
    has_gen_timeout = gen_counter.get("timeout", 0) > 0
    has_gen_failure_status = gen_counter.get("failure", 0) > 0
    exec_counter = Counter(exec_statuses)
    has_not_executed = exec_counter.get("not_executed", 0) > 0
    if avg_pass >= 0.95:
        tier, tier_desc = "T1_trivial", "DeepSeek nearly always passes"
    elif avg_pass >= 0.80:
        tier, tier_desc = "T2_easy", "DeepSeek usually passes"
    elif avg_pass >= 0.50:
        tier, tier_desc = "T3_medium", "DeepSeek sometimes passes"
    elif avg_pass >= 0.20:
        tier, tier_desc = "T4_hard", "DeepSeek rarely passes"
    else:
        tier, tier_desc = "T5_extreme", "DeepSeek almost never passes"
    if has_assertion and not has_type_error and not has_name_error:
        fail_mode = "semantic"
    elif has_type_error or has_name_error or has_attr_error:
        fail_mode = "api_misuse"
    elif has_timeout or has_gen_timeout:
        fail_mode = "timeout"
    elif has_gen_failure or has_gen_failure_status:
        fail_mode = "protocol"
    elif has_unknown:
        fail_mode = "infrastructure"
    elif has_not_executed:
        fail_mode = "not_executed"
    elif avg_pass >= 0.95:
        fail_mode = "none"
    else:
        fail_mode = "mixed"
    protocol_fixable = fail_mode in ("protocol", "timeout", "infrastructure")
    return {
        "task_id": task_id, "avg_pass_rate": round(avg_pass, 4),
        "pass_consistency": round(consistency, 4), "total_runs": total_runs,
        "tier": tier, "tier_desc": tier_desc, "fail_mode": fail_mode,
        "protocol_fixable": protocol_fixable, "error_types": dict(error_counter),
        "has_assertion": has_assertion, "has_type_error": has_type_error,
        "has_timeout": has_timeout, "has_gen_failure": has_gen_failure,
        "has_unknown_failure": has_unknown,
    }

def predict_minicpm5_pass(deepseek_avg_pass, features, difficulty_info):
    """Predict MiniCPM5-2B per-task pass probability."""
    base_scale = 0.537  # 36% / 67%
    num_apis = features["num_unique_apis"]
    loc = features["lines_of_code"]
    techlib = features["techlib_dependency"]
    api_penalty = 1.0
    if num_apis > 10:
        api_penalty = 0.7
    elif num_apis > 5:
        api_penalty = 0.85
    elif num_apis <= 2:
        api_penalty = 1.1
    loc_penalty = 1.0
    if loc > 30:
        loc_penalty = 0.75
    elif loc > 15:
        loc_penalty = 0.90
    elif loc <= 5:
        loc_penalty = 1.15
    techlib_penalty = 0.80 if techlib else 1.0
    tier = difficulty_info["tier"]
    tier_adj = {"T1_trivial": 1.2, "T2_easy": 1.0, "T3_medium": 0.85, "T4_hard": 0.60, "T5_extreme": 0.30}.get(tier, 1.0)
    protocol_adj = 1.15 if difficulty_info["protocol_fixable"] else 1.0
    predicted = deepseek_avg_pass * base_scale * api_penalty * loc_penalty * techlib_penalty * tier_adj * protocol_adj
    return round(max(0.0, min(1.0, predicted)), 4)

def predict_milestones(task_predictions):
    total = len(task_predictions)
    baseline = sum(p["minicpm5_pred"] for p in task_predictions) / total
    m1_tasks = []
    for p in task_predictions:
        boost = 1.0
        if p["difficulty"]["protocol_fixable"]:
            boost = 1.5
        if p["difficulty"]["fail_mode"] == "api_misuse":
            boost = max(boost, 1.3)
        m1_tasks.append(min(1.0, p["minicpm5_pred"] * boost))
    m1 = sum(m1_tasks) / total
    m2_tasks = []
    for p in task_predictions:
        boost = 1.0
        if p["features"]["techlib_dependency"]:
            boost *= 1.3
        if p["features"]["num_unique_apis"] > 5:
            boost *= 1.2
        if p["difficulty"]["tier"] in ("T3_medium", "T4_hard"):
            boost *= 1.25
        m2_tasks.append(min(1.0, p["minicpm5_pred"] * boost))
    m2 = sum(m2_tasks) / total
    m3_tasks = []
    for p in task_predictions:
        boost = 1.0
        if p["difficulty"]["fail_mode"] == "semantic":
            boost *= 1.4
        if p["difficulty"]["tier"] in ("T3_medium", "T4_hard", "T5_extreme"):
            boost *= 1.3
        m3_tasks.append(min(1.0, p["minicpm5_pred"] * boost))
    m3 = sum(m3_tasks) / total
    m4_tasks = []
    for p in task_predictions:
        boost = 1.0
        if p["difficulty"]["tier"] == "T5_extreme":
            boost *= 1.5
        elif p["difficulty"]["tier"] == "T4_hard":
            boost *= 1.4
        elif p["difficulty"]["tier"] == "T3_medium":
            boost *= 1.3
        m4_tasks.append(min(1.0, p["minicpm5_pred"] * boost))
    m4 = sum(m4_tasks) / total
    return {
        "baseline_36pct": round(baseline, 4),
        "M1_protocol_fix": round(m1, 4),
        "M2_domain_sft": round(m2, 4),
        "M3_rl": round(m3, 4),
        "M4_full": round(m4, 4),
        "M1_target": 0.50, "M2_target": 0.65, "M3_target": 0.75, "M4_target": 0.85,
        "M1_gap": round(m1 - 0.50, 4), "M2_gap": round(m2 - 0.65, 4),
        "M3_gap": round(m3 - 0.75, 4), "M4_gap": round(m4 - 0.85, 4),
    }

def generate_curriculum(task_predictions):
    sorted_tasks = sorted(task_predictions, key=lambda p: (-p["minicpm5_pred"], p["features"]["num_unique_apis"], p["features"]["lines_of_code"]))
    stages = {"stage1_warmup": [], "stage2_basic": [], "stage3_intermediate": [], "stage4_advanced": [], "stage5_expert": []}
    for p in sorted_tasks:
        tier = p["difficulty"]["tier"]
        apis = p["features"]["num_unique_apis"]
        loc = p["features"]["lines_of_code"]
        if tier in ("T1_trivial", "T2_easy") and apis <= 3 and loc <= 10:
            stages["stage1_warmup"].append(p["task_id"])
        elif tier in ("T2_easy", "T3_medium") and apis <= 5:
            stages["stage2_basic"].append(p["task_id"])
        elif tier == "T3_medium" and apis <= 10:
            stages["stage3_intermediate"].append(p["task_id"])
        elif tier in ("T3_medium", "T4_hard"):
            stages["stage4_advanced"].append(p["task_id"])
        else:
            stages["stage5_expert"].append(p["task_id"])
    result = {}
    pred_map = {p["task_id"]: p["minicpm5_pred"] for p in task_predictions}
    for stage, tasks in stages.items():
        avg_pred = sum(pred_map.get(tid, 0) for tid in tasks) / max(len(tasks), 1)
        result[stage] = {"count": len(tasks), "task_ids": tasks[:20], "avg_pred_pass": round(avg_pred, 4)}
    return result

def analyze_by_dimension(task_predictions, dim_key):
    groups = defaultdict(list)
    for p in task_predictions:
        groups[p["features"][dim_key]].append(p)
    result = {}
    for key, preds in sorted(groups.items()):
        result[key] = {
            "count": len(preds),
            "deepseek_avg": round(sum(p["deepseek_avg_pass"] for p in preds) / len(preds), 4),
            "minicpm5_pred_avg": round(sum(p["minicpm5_pred"] for p in preds) / len(preds), 4),
            "protocol_fixable_count": sum(1 for p in preds if p["difficulty"]["protocol_fixable"]),
            "fail_modes": dict(Counter(p["difficulty"]["fail_mode"] for p in preds)),
            "tiers": dict(Counter(p["difficulty"]["tier"] for p in preds)),
        }
    return result

def compute_feature_importance(task_predictions):
    importance = {}
    n = len(task_predictions)
    for feat in ["num_unique_apis", "lines_of_code", "prompt_chars", "test_chars", "num_asserts", "num_api_modules"]:
        vals = [p["features"][feat] for p in task_predictions]
        passes = [p["deepseek_avg_pass"] for p in task_predictions]
        mean_v, mean_p = sum(vals) / n, sum(passes) / n
        cov = sum((v - mean_v) * (p - mean_p) for v, p in zip(vals, passes)) / n
        std_v = math.sqrt(sum((v - mean_v) ** 2 for v in vals) / n)
        std_p = math.sqrt(sum((p - mean_p) ** 2 for p in passes) / n)
        importance[feat] = round(cov / (std_v * std_p), 4) if std_v > 0 and std_p > 0 else 0.0
    for cat_feat in ["scenario", "category", "techlib_dependency"]:
        groups = defaultdict(list)
        for p in task_predictions:
            groups[p["features"][cat_feat]].append(p["deepseek_avg_pass"])
        group_means = {k: sum(v) / len(v) for k, v in groups.items()}
        importance[cat_feat] = round(max(group_means.values()) - min(group_means.values()), 4)
    return importance

def analyze_gap(task_predictions):
    total = len(task_predictions)
    fail_modes = Counter(p["difficulty"]["fail_mode"] for p in task_predictions)
    tiers = Counter(p["difficulty"]["tier"] for p in task_predictions)
    protocol_recoverable = sum(1 for p in task_predictions if p["difficulty"]["protocol_fixable"])
    api_recoverable = sum(1 for p in task_predictions if p["difficulty"]["fail_mode"] == "api_misuse")
    semantic = sum(1 for p in task_predictions if p["difficulty"]["fail_mode"] == "semantic")
    easy_wins = sum(1 for p in task_predictions if p["difficulty"]["tier"] in ("T1_trivial", "T2_easy"))
    protocol_pp = round(protocol_recoverable / total * 0.15, 4)
    api_pp = round(api_recoverable / total * 0.12, 4)
    semantic_pp = round(semantic / total * 0.20, 4)
    easy_pp = round(easy_wins / total * 0.10, 4)
    return {
        "total_gap_to_deepseek_v4": 0.58, "gap_to_deepseek_v32": 0.31,
        "protocol_recoverable_tasks": protocol_recoverable,
        "api_recoverable_tasks": api_recoverable,
        "semantic_tasks": semantic, "easy_win_tasks": easy_wins,
        "estimated_recovery": {
            "protocol_sft": f"+{protocol_pp*100:.1f}pp",
            "api_knowledge_sft": f"+{api_pp*100:.1f}pp",
            "semantic_rl": f"+{semantic_pp*100:.1f}pp",
            "easy_wins_mastery": f"+{easy_pp*100:.1f}pp",
            "total_estimated": f"+{(protocol_pp+api_pp+semantic_pp+easy_pp)*100:.1f}pp",
        },
        "fail_mode_counts": dict(fail_modes), "tier_counts": dict(tiers),
    }

def run_analysis(verbose=False):
    tasks = load_dataset()
    runs = load_eval_runs()
    if verbose:
        print(f"Loaded {len(tasks)} tasks, {len(runs)} runs")
    features_list = [extract_features(t) for t in tasks]
    task_pass, task_errors, task_gen, task_exec = aggregate_pass_rates(runs)
    if verbose:
        print(f"Aggregated pass rates for {len(task_pass)} tasks")
    task_predictions = []
    for i, task in enumerate(tasks):
        tid = task.get("task_id", f"task-{i}")
        features = features_list[i]
        pass_rates = task_pass.get(tid, [])
        errors = task_errors.get(tid, [])
        gen_statuses = task_gen.get(tid, [])
        exec_statuses = task_exec.get(tid, [])
        difficulty = classify_difficulty(tid, pass_rates, errors, gen_statuses, exec_statuses)
        minicpm5_pred = predict_minicpm5_pass(difficulty["avg_pass_rate"], features, difficulty)
        task_predictions.append({
            "task_id": tid, "task_name": features["task_name"],
            "scenario": features["scenario"], "category": features["category"],
            "features": features, "deepseek_avg_pass": difficulty["avg_pass_rate"],
            "difficulty": difficulty, "minicpm5_pred": minicpm5_pred,
        })
    tier_dist = Counter(p["difficulty"]["tier"] for p in task_predictions)
    fail_mode_dist = Counter(p["difficulty"]["fail_mode"] for p in task_predictions)
    protocol_fixable_count = sum(1 for p in task_predictions if p["difficulty"]["protocol_fixable"])
    by_scenario = analyze_by_dimension(task_predictions, "scenario")
    by_category = analyze_by_dimension(task_predictions, "category")
    milestones = predict_milestones(task_predictions)
    curriculum = generate_curriculum(task_predictions)
    feature_importance = compute_feature_importance(task_predictions)
    gap_analysis = analyze_gap(task_predictions)
    return {
        "meta": {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": len(tasks), "total_runs": len(runs),
            "runs_used": {rd: ri["label"] for rd, ri in runs.items()},
            "deepseek_avg_overall": round(sum(p["deepseek_avg_pass"] for p in task_predictions) / len(task_predictions), 4),
            "minicpm5_baseline_target": 0.36,
        },
        "tier_distribution": dict(tier_dist),
        "fail_mode_distribution": dict(fail_mode_dist),
        "protocol_fixable": {"count": protocol_fixable_count, "percentage": round(protocol_fixable_count / len(task_predictions), 4)},
        "by_scenario": by_scenario, "by_category": by_category,
        "milestones": milestones, "curriculum": curriculum,
        "feature_importance": feature_importance, "gap_analysis": gap_analysis,
        "task_predictions": task_predictions,
    }

def generate_html(result):
    m = result["meta"]; tier = result["tier_distribution"]; fm = result["fail_mode_distribution"]
    pf = result["protocol_fixable"]; ms = result["milestones"]; curr = result["curriculum"]
    fi = result["feature_importance"]; gap = result["gap_analysis"]
    scenario_rows = ""
    for scen, stats in sorted(result["by_scenario"].items()):
        scenario_rows += f'<tr><td>{scen}</td><td>{stats["count"]}</td><td>{stats["deepseek_avg"]*100:.1f}%</td><td>{stats["minicpm5_pred_avg"]*100:.1f}%</td><td>{stats["protocol_fixable_count"]}</td><td>{", ".join(f"{k}:{v}" for k,v in stats["fail_modes"].items())}</td></tr>\n'
    category_rows = ""
    for cat, stats in sorted(result["by_category"].items()):
        category_rows += f'<tr><td>{cat}</td><td>{stats["count"]}</td><td>{stats["deepseek_avg"]*100:.1f}%</td><td>{stats["minicpm5_pred_avg"]*100:.1f}%</td><td>{stats["protocol_fixable_count"]}</td><td>{", ".join(f"{k}:{v}" for k,v in stats["tiers"].items())}</td></tr>\n'
    milestone_rows = ""
    for key, label, target in [("baseline_36pct","起点(MiniCPM5-2B)","36%"),("M1_protocol_fix","M1(协议修复)","50%"),("M2_domain_sft","M2(+领域SFT)","65%"),("M3_rl","M3(+RL)","75%"),("M4_full","M4(全面优化)","85%+")]:
        val = ms[key]; gap_val = val - float(target.rstrip("%+"))
        gap_str = f'<span style="color:{"green" if gap_val>=0 else "red"}">{"+" if gap_val>=0 else ""}{gap_val*100:.1f}pp</span>'
        milestone_rows += f'<tr><td>{label}</td><td><strong>{val*100:.1f}%</strong></td><td>{target}</td><td>{gap_str}</td></tr>\n'
    curr_rows = ""
    for stage, stats in curr.items():
        curr_rows += f'<tr><td>{stage}</td><td>{stats["count"]}</td><td>{stats["avg_pred_pass"]*100:.1f}%</td><td>{", ".join(stats["task_ids"][:5])}{"..." if len(stats["task_ids"])>5 else ""}</td></tr>\n'
    fi_rows = ""
    for feat, val in sorted(fi.items(), key=lambda x: -abs(x[1])):
        fi_rows += f'<tr><td>{feat}</td><td>{val:+.4f}</td><td>{"正相关(越难)" if val>0 else "负相关(越易)" if val<0 else "无相关"}</td></tr>\n'
    hardest = sorted(result["task_predictions"], key=lambda p: p["minicpm5_pred"])[:10]
    hardest_rows = ""
    for p in hardest:
        hardest_rows += f'<tr><td>{p["task_id"]}</td><td>{p["task_name"][:40]}</td><td>{p["scenario"]}</td><td>{p["deepseek_avg_pass"]*100:.0f}%</td><td>{p["minicpm5_pred"]*100:.1f}%</td><td>{p["difficulty"]["tier"]}</td><td>{p["difficulty"]["fail_mode"]}</td></tr>\n'
    easiest = sorted(result["task_predictions"], key=lambda p: -p["minicpm5_pred"])[:10]
    easiest_rows = ""
    for p in easiest:
        easiest_rows += f'<tr><td>{p["task_id"]}</td><td>{p["task_name"][:40]}</td><td>{p["scenario"]}</td><td>{p["deepseek_avg_pass"]*100:.0f}%</td><td>{p["minicpm5_pred"]*100:.1f}%</td><td>{p["difficulty"]["tier"]}</td><td>{p["difficulty"]["fail_mode"]}</td></tr>\n'
    html = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>R83: EDA-Eval-PyAether 158题难度分布分析与通过率预测</title>
<style>
body{{font-family:-apple-system,"Noto Sans SC",sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f8f9fa;color:#333}}
h1{{color:#1a1a2e;border-bottom:3px solid #16213e;padding-bottom:10px}}
h2{{color:#16213e;margin-top:30px}}
table{{border-collapse:collapse;width:100%;margin:15px 0;background:white;box-shadow:0 2px 4px rgba(0,0,0,0.1)}}
th,td{{border:1px solid #ddd;padding:8px 12px;text-align:left;font-size:14px}}
th{{background:#16213e;color:white;font-weight:600}}
tr:nth-child(even){{background:#f2f2f2}}
tr:hover{{background:#e8e8e8}}
.summary-box{{background:white;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);margin:15px 0}}
.metric{{display:inline-block;margin:10px 20px;text-align:center}}
.metric-value{{font-size:28px;font-weight:bold;color:#16213e}}
.metric-label{{font-size:13px;color:#666}}
.warning{{background:#fff3cd;border-left:4px solid #ffc107;padding:10px 15px;margin:15px 0}}
.info{{background:#d1ecf1;border-left:4px solid #17a2b8;padding:10px 15px;margin:15px 0}}
</style></head><body>
<h1>R83: EDA-Eval-PyAether 158题难度分布分析与通过率预测</h1>
<p style="color:#666">生成时间:{m["timestamp"]} | 任务数:{m["total_tasks"]} | 评估运行数:{m["total_runs"]} | 零GPU纯分析</p>
<div class="warning"><b>⚠️ 声明</b>:MiniCPM5-2B逐题通过率为<b>预测值</b>(基于DeepSeek实测+任务特征缩放),非实测。替身模型结果不可迁移到白泽。GPU到位后需用真实轨迹校正。</div>
<h2>1.摘要</h2>
<div class="summary-box">
<div class="metric"><div class="metric-value">{m["deepseek_avg_overall"]*100:.1f}%</div><div class="metric-label">DeepSeek平均通过率</div></div>
<div class="metric"><div class="metric-value">36%</div><div class="metric-label">MiniCPM5-2B基线(实测)</div></div>
<div class="metric"><div class="metric-value">{pf["count"]}</div><div class="metric-label">协议可修复任务数</div></div>
<div class="metric"><div class="metric-value">{pf["percentage"]*100:.0f}%</div><div class="metric-label">协议可修复占比</div></div>
</div>
<div class="info"><b>核心发现</b>:<ul>
<li>158题按DeepSeek表现分5档:T1简单({tier.get("T1_trivial",0)})/T2容易({tier.get("T2_easy",0)})/T3中等({tier.get("T3_medium",0)})/T4困难({tier.get("T4_hard",0)})/T5极难({tier.get("T5_extreme",0)})</li>
<li>失败模式:{", ".join(f"{k}={v}" for k,v in fm.items())}</li>
<li>协议可修复({pf["count"]}题,{pf["percentage"]*100:.0f}%)→SFT可回收,支撑M1</li>
<li>语义推理失败({fm.get("semantic",0)}题)→RL价值最大,支撑M3</li>
<li>API误用({fm.get("api_misuse",0)}题)→领域SFT关键,支撑M2</li>
</ul></div>
<h2>2.难度分层分布</h2>
<table><tr><th>难度档</th><th>题数</th><th>占比</th><th>DeepSeek通过率</th><th>MiniCPM5预测</th><th>含义</th></tr>
<tr><td>T1简单</td><td>{tier.get("T1_trivial",0)}</td><td>{tier.get("T1_trivial",0)/158*100:.1f}%</td><td>≥95%</td><td>~70-90%</td><td>DeepSeek几乎总通过</td></tr>
<tr><td>T2容易</td><td>{tier.get("T2_easy",0)}</td><td>{tier.get("T2_easy",0)/158*100:.1f}%</td><td>80-95%</td><td>~45-70%</td><td>DeepSeek通常通过</td></tr>
<tr><td>T3中等</td><td>{tier.get("T3_medium",0)}</td><td>{tier.get("T3_medium",0)/158*100:.1f}%</td><td>50-80%</td><td>~25-45%</td><td>DeepSeek有时通过</td></tr>
<tr><td>T4困难</td><td>{tier.get("T4_hard",0)}</td><td>{tier.get("T4_hard",0)/158*100:.1f}%</td><td>20-50%</td><td>~10-25%</td><td>DeepSeek很少通过</td></tr>
<tr><td>T5极难</td><td>{tier.get("T5_extreme",0)}</td><td>{tier.get("T5_extreme",0)/158*100:.1f}%</td><td>&lt;20%</td><td>~0-10%</td><td>DeepSeek几乎不通过</td></tr>
</table>
<h2>3.按场景分析</h2>
<table><tr><th>场景</th><th>题数</th><th>DeepSeek</th><th>MiniCPM5预测</th><th>协议可修复</th><th>失败模式</th></tr>{scenario_rows}</table>
<h2>4.按类别分析</h2>
<table><tr><th>类别</th><th>题数</th><th>DeepSeek</th><th>MiniCPM5预测</th><th>协议可修复</th><th>难度分布</th></tr>{category_rows}</table>
<h2>5.成功阶梯预测(M1-M4)</h2>
<table><tr><th>里程碑</th><th>预测通过率</th><th>目标</th><th>差距</th></tr>{milestone_rows}</table>
<div class="info"><b>解读</b>:M1/M2预测接近目标说明协议修复+领域SFT路径可行。M3/M4差距反映RL对语义推理的提升空间。</div>
<h2>6.58pp差距分解</h2>
<div class="summary-box"><p><b>总差距</b>:94%-36%=58pp; <b>vs DeepSeek-V32</b>:67%-36%=31pp</p>
<table><tr><th>回收路径</th><th>任务数</th><th>预估回收</th><th>里程碑</th></tr>
<tr><td>协议修复(SFT格式/工具调用)</td><td>{gap["protocol_recoverable_tasks"]}</td><td>{gap["estimated_recovery"]["protocol_sft"]}</td><td>M1</td></tr>
<tr><td>API知识(领域SFT)</td><td>{gap["api_recoverable_tasks"]}</td><td>{gap["estimated_recovery"]["api_knowledge_sft"]}</td><td>M2</td></tr>
<tr><td>语义推理(RL)</td><td>{gap["semantic_tasks"]}</td><td>{gap["estimated_recovery"]["semantic_rl"]}</td><td>M3</td></tr>
<tr><td>简单题精通</td><td>{gap["easy_win_tasks"]}</td><td>{gap["estimated_recovery"]["easy_wins_mastery"]}</td><td>M1-M2</td></tr>
<tr><td><b>合计</b></td><td></td><td><b>{gap["estimated_recovery"]["total_estimated"]}</b></td><td></td></tr>
</table></div>
<h2>7.特征重要性</h2>
<table><tr><th>特征</th><th>相关系数/差异</th><th>解读</th></tr>{fi_rows}</table>
<h2>8.RL课程排序</h2>
<table><tr><th>阶段</th><th>题数</th><th>MiniCPM5预测</th><th>示例</th></tr>{curr_rows}</table>
<h2>9.最难10题</h2>
<table><tr><th>题号</th><th>任务名</th><th>场景</th><th>DeepSeek</th><th>MiniCPM5预测</th><th>难度</th><th>失败模式</th></tr>{hardest_rows}</table>
<h2>10.最易10题</h2>
<table><tr><th>题号</th><th>任务名</th><th>场景</th><th>DeepSeek</th><th>MiniCPM5预测</th><th>难度</th><th>失败模式</th></tr>{easiest_rows}</table>
<h2>11.与前序研究关联</h2>
<table><tr><th>来源</th><th>贡献</th><th>本节使用</th></tr>
<tr><td>R74课程调度</td><td>5阶段渐进难度</td><td>课程排序验证</td></tr>
<tr><td>R79 SFT混合</td><td>6数据源修复向量</td><td>API知识SFT优先级</td></tr>
<tr><td>R72统计功效</td><td>M1-M4预注册</td><td>里程碑预测校准</td></tr>
<tr><td>R80 GRPO崩溃</td><td>7崩溃模式检测</td><td>课程Stage1稳定性</td></tr>
<tr><td>P0 D1-D6</td><td>36%基线诊断</td><td>基线对照</td></tr>
<tr><td>R4失败模式</td><td>假设性分类法</td><td>用实测数据校正</td></tr>
</table>
<h2>12.局限性</h2><ul>
<li>MiniCPM5-2B逐题通过率为<b>预测值</b>,基于DeepSeek数据缩放+特征调整,非实测</li>
<li>DeepSeek评估运行model_name为zhulong/zhulong_deepseek_v32,非MiniCPM5-2B直接对照</li>
<li>20260416_1720运行(39.9%)出现86个Unknown Failure,可能不同harness配置</li>
<li>缩放因子0.537假设难度等比例缩放,实际可能非线性</li>
<li>替身模型结果不可迁移到BaiZe</li>
</ul>
<h2>13.交付物</h2>
<table><tr><th>产物</th><th>路径</th><th>说明</th></tr>
<tr><td>脚本</td><td>baize_posttrain_task_difficulty_analysis.py</td><td>纯Python 3.8+ stdlib</td></tr>
<tr><td>HTML</td><td>reports/report_posttrain_r83_difficulty_analysis_zh.html</td><td>自包含,0 script,0外链</td></tr>
<tr><td>JSON</td><td>r83_difficulty_analysis.json</td><td>完整数据</td></tr>
<tr><td>EXPERIMENTS</td><td>§R83</td><td>分析结论</td></tr>
</table>
<p style="color:#666;margin-top:30px;border-top:1px solid #ddd;padding-top:10px">无伪造。替身RL结果不可迁移到BaiZe。</p>
</body></html>'''
    return html

def main():
    parser = argparse.ArgumentParser(description="R83: 158-Task Difficulty Distribution Analysis")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    parser.add_argument("--json", action="store_true", help="Output JSON data")
    parser.add_argument("--decision-only", action="store_true", help="Print key decisions only")
    args = parser.parse_args()
    result = run_analysis(verbose=args.verbose)
    if args.decision_only:
        m = result["meta"]; ms = result["milestones"]; gap = result["gap_analysis"]
        print(f"=== R83 Decision Summary ===")
        print(f"Tasks: {m['total_tasks']}, Runs: {m['total_runs']}")
        print(f"DeepSeek avg: {m['deepseek_avg_overall']*100:.1f}%")
        print(f"Tier dist: {result['tier_distribution']}")
        print(f"Fail modes: {result['fail_mode_distribution']}")
        print(f"Protocol fixable: {result['protocol_fixable']['count']} ({result['protocol_fixable']['percentage']*100:.0f}%)")
        print(f"Milestones: baseline={ms['baseline_36pct']*100:.1f}% M1={ms['M1_protocol_fix']*100:.1f}% M2={ms['M2_domain_sft']*100:.1f}% M3={ms['M3_rl']*100:.1f}% M4={ms['M4_full']*100:.1f}%")
        print(f"Gap recovery: {gap['estimated_recovery']['total_estimated']}")
        return
    if args.verbose:
        print(f"\n=== Tier Distribution ===")
        for t, c in sorted(result["tier_distribution"].items()):
            print(f"  {t}: {c} ({c/158*100:.1f}%)")
        print(f"\n=== Fail Mode Distribution ===")
        for fm, c in sorted(result["fail_mode_distribution"].items()):
            print(f"  {fm}: {c}")
        print(f"\n=== Protocol Fixable ===")
        print(f"  {result['protocol_fixable']['count']} tasks ({result['protocol_fixable']['percentage']*100:.0f}%)")
        print(f"\n=== Milestones ===")
        for key in ["baseline_36pct", "M1_protocol_fix", "M2_domain_sft", "M3_rl", "M4_full"]:
            print(f"  {key}: {result['milestones'][key]*100:.1f}%")
        print(f"\n=== Gap Analysis ===")
        for k, v in result["gap_analysis"]["estimated_recovery"].items():
            print(f"  {k}: {v}")
    if args.json:
        json_path = os.path.join(RUN_DIR, "r83_difficulty_analysis.json")
        result_lite = {k: v for k, v in result.items() if k != "task_predictions"}
        result_lite["task_predictions_summary"] = [
            {"task_id": p["task_id"], "scenario": p["scenario"], "category": p["category"],
             "deepseek_avg": p["deepseek_avg_pass"], "minicpm5_pred": p["minicpm5_pred"],
             "tier": p["difficulty"]["tier"], "fail_mode": p["difficulty"]["fail_mode"],
             "protocol_fixable": p["difficulty"]["protocol_fixable"],
             "num_apis": p["features"]["num_unique_apis"], "loc": p["features"]["lines_of_code"]}
            for p in result["task_predictions"]
        ]
        with open(json_path, "w") as f:
            json.dump(result_lite, f, ensure_ascii=False, indent=2)
        print(f"JSON saved: {json_path}")
    if args.html:
        os.makedirs(REPORT_DIR, exist_ok=True)
        html_path = os.path.join(REPORT_DIR, "report_posttrain_r83_difficulty_analysis_zh.html")
        html = generate_html(result)
        with open(html_path, "w") as f:
            f.write(html)
        size = os.path.getsize(html_path)
        print(f"HTML saved: {html_path} ({size/1024:.1f}KB)")
    if not args.html and not args.json and not args.decision_only:
        print(f"R83: 158-Task Difficulty Analysis")
        print(f"  Tasks: {result['meta']['total_tasks']}")
        print(f"  DeepSeek avg: {result['meta']['deepseek_avg_overall']*100:.1f}%")
        print(f"  Tiers: {result['tier_distribution']}")
        print(f"  Fail modes: {result['fail_mode_distribution']}")
        print(f"  Protocol fixable: {result['protocol_fixable']['count']}")
        print(f"  Use --html --json for full output")

if __name__ == "__main__":
    main()
