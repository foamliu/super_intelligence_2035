#!/usr/bin/env python3
"""baize_posttrain_r319_api_misuse_analysis.py -- R319 API Misuse Taxonomy

R319 (2026-11-12): Deep analysis of API misuse patterns across 3 models
(MC5-base, MC5-SFT, Qwen3.8-27B) from the 113-task static eval, to refine
the RL R4 reward arm (API legality check).

Key question: SFT fixed syntax (54.9%->93.8%) but API correctness stayed at
0%->0% (all_apis_correct=2.7% for all 3 models). WHAT exactly are the models
getting wrong about APIs? Which APIs are most commonly misused? Are there
systematic confusion patterns that RL can target?

Output: JSON summary + human-readable report to stdout.
"""
from __future__ import annotations
import json, os, re, sys
from collections import Counter, defaultdict
from pathlib import Path

RUN_DIR = Path(__file__).parent
R311_FILE = RUN_DIR / "static_eval_r311_results.json"
QWEN_FILE = RUN_DIR / "static_eval_qwen_results.json"
OUT_FILE  = RUN_DIR / "r319_api_misuse_analysis.json"

def load(path):
    with open(path) as f:
        return json.load(f)

def normalize_api(api):
    if not api:
        return api
    for pfx in ("pyAether.", "pyScript.", "py."):
        if api.startswith(pfx):
            return api[len(pfx):]
    return api

def extract_wrong_apis(entry, model_key):
    blk = entry.get(model_key, {})
    found = set(blk.get("apis_found", []))
    correct = set(blk.get("apis_correct", []))
    wrong = found - correct
    missing = set(blk.get("apis_missing", []))
    return wrong, missing, correct, found

def analyze(data, model_label, model_key):
    tasks = []
    wrong_api_counter = Counter()
    missing_api_counter = Counter()
    confusion_pairs = defaultdict(int)
    per_scenario = defaultdict(lambda: {
        "n": 0, "all_correct": 0, "has_wrong": 0,
        "wrong_apis": Counter(), "missing_apis": Counter()
    })
    per_category = defaultdict(lambda: {
        "n": 0, "all_correct": 0, "has_wrong": 0,
        "wrong_apis": Counter(), "missing_apis": Counter()
    })

    for task_id, entry in data.items():
        meta = entry.get("metadata", {})
        scenario = meta.get("scenario", "Unknown")
        category = meta.get("category", "Unknown")
        expected = set(entry.get("apis_expected", []))
        expected_norm = {normalize_api(a) for a in expected}

        wrong, missing, correct, found = extract_wrong_apis(entry, model_key)
        all_correct = (len(missing) == 0 and len(wrong) == 0 and len(expected) > 0)

        tasks.append({
            "task_id": task_id,
            "scenario": scenario,
            "category": category,
            "expected": sorted(expected),
            "found": sorted(found),
            "correct": sorted(correct),
            "wrong": sorted(wrong),
            "missing": sorted(missing),
            "all_correct": all_correct,
        })

        for wa in wrong:
            wrong_api_counter[normalize_api(wa)] += 1
            for ea in expected_norm:
                confusion_pairs[(normalize_api(wa), ea)] += 1

        for ma in missing:
            missing_api_counter[normalize_api(ma)] += 1

        sc = per_scenario[scenario]
        sc["n"] += 1
        if all_correct:
            sc["all_correct"] += 1
        if wrong:
            sc["has_wrong"] += 1
            for wa in wrong:
                sc["wrong_apis"][normalize_api(wa)] += 1
        if missing:
            for ma in missing:
                sc["missing_apis"][normalize_api(ma)] += 1

        ct = per_category[category]
        ct["n"] += 1
        if all_correct:
            ct["all_correct"] += 1
        if wrong:
            ct["has_wrong"] += 1
            for wa in wrong:
                ct["wrong_apis"][normalize_api(wa)] += 1
        if missing:
            for ma in missing:
                ct["missing_apis"][normalize_api(ma)] += 1

    return {
        "model": model_label,
        "n_tasks": len(tasks),
        "n_all_correct": sum(1 for t in tasks if t["all_correct"]),
        "n_has_wrong_apis": sum(1 for t in tasks if t["wrong"]),
        "n_has_missing_apis": sum(1 for t in tasks if t["missing"]),
        "top_wrong_apis": wrong_api_counter.most_common(30),
        "top_missing_apis": missing_api_counter.most_common(30),
        "top_confusion_pairs": sorted(confusion_pairs.items(), key=lambda x: -x[1])[:30],
        "per_scenario": {k: {**v, "wrong_apis": v["wrong_apis"].most_common(10),
                             "missing_apis": v["missing_apis"].most_common(10)}
                         for k, v in sorted(per_scenario.items())},
        "per_category": {k: {**v, "wrong_apis": v["wrong_apis"].most_common(10),
                             "missing_apis": v["missing_apis"].most_common(10)}
                         for k, v in sorted(per_category.items())},
        "tasks": tasks,
    }

def cross_model_comparison(results):
    models = list(results.keys())
    all_correct_sets = {}
    for m in models:
        all_correct_sets[m] = {t["task_id"] for t in results[m]["tasks"] if t["all_correct"]}
    wrong_sets = {}
    for m in models:
        wrong_sets[m] = set()
        for t in results[m]["tasks"]:
            for wa in t["wrong"]:
                wrong_sets[m].add(normalize_api(wa))
    missing_sets = {}
    for m in models:
        missing_sets[m] = set()
        for t in results[m]["tasks"]:
            for ma in t["missing"]:
                missing_sets[m].add(normalize_api(ma))
    return {
        "all_correct_tasks": {m: sorted(all_correct_sets[m]) for m in models},
        "all_correct_intersection": sorted(
            set.intersection(*all_correct_sets.values()) if all_correct_sets else set()),
        "wrong_api_overlap": {
            "all_models": sorted(set.intersection(*wrong_sets.values()) if wrong_sets else set()),
        },
        "missing_api_overlap": {
            "all_models": sorted(set.intersection(*missing_sets.values()) if missing_sets else set()),
        },
    }

def print_report(results, comparison):
    lines = []
    lines.append("=" * 80)
    lines.append("R319 API Misuse Taxonomy -- 3-Model Static Eval Deep Analysis")
    lines.append("=" * 80)
    lines.append("")
    for m, r in results.items():
        lines.append(f"## {r['model']} ({r['n_tasks']} tasks)")
        lines.append(f"  all_apis_correct: {r['n_all_correct']}/{r['n_tasks']} ({100*r['n_all_correct']/r['n_tasks']:.1f}%)")
        lines.append(f"  tasks with wrong APIs: {r['n_has_wrong_apis']}/{r['n_tasks']} ({100*r['n_has_wrong_apis']/r['n_tasks']:.1f}%)")
        lines.append(f"  tasks with missing APIs: {r['n_has_missing_apis']}/{r['n_tasks']} ({100*r['n_has_missing_apis']/r['n_tasks']:.1f}%)")
        lines.append(f"  Top 15 WRONG APIs:")
        for api, cnt in r["top_wrong_apis"][:15]:
            lines.append(f"    {api:40s}  {cnt:4d}x")
        lines.append(f"  Top 15 MISSING APIs:")
        for api, cnt in r["top_missing_apis"][:15]:
            lines.append(f"    {api:40s}  {cnt:4d}x")
        lines.append("")
    lines.append("## Cross-Model Comparison")
    lines.append(f"  all_correct intersection: {len(comparison['all_correct_intersection'])} tasks")
    for tid in comparison["all_correct_intersection"]:
        lines.append(f"    - {tid}")
    lines.append(f"  WRONG APIs common to ALL 3 models ({len(comparison['wrong_api_overlap']['all_models'])} APIs):")
    for api in comparison["wrong_api_overlap"]["all_models"][:20]:
        lines.append(f"    - {api}")
    lines.append(f"  MISSING APIs common to ALL 3 models ({len(comparison['missing_api_overlap']['all_models'])} APIs):")
    for api in comparison["missing_api_overlap"]["all_models"][:20]:
        lines.append(f"    - {api}")
    lines.append("")
    sft = results.get("MC5-SFT", {})
    if sft and "per_scenario" in sft:
        lines.append("## MC5-SFT Per-Scenario (RL starting point)")
        for sc, v in sorted(sft["per_scenario"].items()):
            lines.append(f"  {sc:20s}: n={v['n']:3d}  all_correct={v['all_correct']:3d}  has_wrong={v['has_wrong']:3d}")
        lines.append("")
    if sft and "top_confusion_pairs" in sft:
        lines.append("## MC5-SFT Top 15 API Confusion Pairs (wrong -> expected)")
        for (wa, ea), cnt in sft["top_confusion_pairs"][:15]:
            lines.append(f"    {wa:30s} -> {ea:30s}  {cnt:3d}x")
        lines.append("")
    lines.append("## Implications for RL R4 Reward Arm")
    sft_wrong = set()
    for t in sft.get("tasks", []):
        for wa in t["wrong"]:
            sft_wrong.add(normalize_api(wa))
    lines.append(f"  SFT generates {len(sft_wrong)} distinct wrong APIs across 113 tasks")
    lines.append(f"  R4 should: (1) check API exists in pyAether database,")
    lines.append(f"  (2) check API is in correct module/context,")
    lines.append(f"  (3) give partial credit for correct module prefix")
    lines.append("")
    return "\n".join(lines)

def main():
    r311 = load(R311_FILE)
    qwen = load(QWEN_FILE)
    results = {}
    results["MC5-base"] = analyze(r311, "MC5-base (MiniCPM5-2B)", "base")
    results["MC5-SFT"]  = analyze(r311, "MC5-SFT (MiniCPM5-2B SFT step70)", "sft")
    results["Qwen3.8-27B"] = analyze(qwen, "Qwen3.8-27B", "qwen")
    comparison = cross_model_comparison(results)
    output = {
        "R319": "API Misuse Taxonomy from 3-model static eval (113 tasks each)",
        "date": "2026-11-12",
        "source_files": [str(R311_FILE), str(QWEN_FILE)],
        "models": results,
        "cross_model": comparison,
    }
    with open(OUT_FILE, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    print(f"[OK] Analysis written to {OUT_FILE}")
    print()
    print(print_report(results, comparison))

if __name__ == "__main__":
    main()
