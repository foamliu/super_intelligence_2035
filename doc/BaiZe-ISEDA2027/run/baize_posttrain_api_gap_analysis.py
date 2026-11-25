#!/usr/bin/env python3
"""R297 API-Level Gap Analysis: BASE vs SFT vs Expected (113 tasks)"""
import json, os, sys
from collections import Counter, defaultdict

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_FILE = os.path.join(RUN_DIR, "eda_eval_static_full_wake287.json")
OUTPUT_FILE = os.path.join(RUN_DIR, "api_gap_analysis_r297.json")

def normalize_api(api_str):
    if api_str.startswith("pyAether."):
        return api_str[len("pyAether."):]
    return api_str

def analyze(data):
    all_expected = Counter()
    base_found = Counter()
    sft_found = Counter()
    base_correct = Counter()
    sft_correct = Counter()
    sc_exp = defaultdict(Counter)
    sc_bf = defaultdict(Counter)
    sc_sf = defaultdict(Counter)
    task_gaps = []
    t_tasks = 0; t_exp = 0; t_bf = 0; t_sf = 0; t_bc = 0; t_sc = 0
    sft_better = 0; base_better = 0; equal_t = 0; both_zero = 0
    for task_id, task in data.items():
        t_tasks += 1
        meta = task.get("metadata", {})
        scenario = meta.get("scenario", "Unknown")
        expected = [normalize_api(a) for a in task.get("apis_expected", [])]
        b = task.get("base", {}); s = task.get("sft", {})
        b_found = [normalize_api(a) for a in b.get("apis_found", [])]
        s_found = [normalize_api(a) for a in s.get("apis_found", [])]
        b_correct = [normalize_api(a) for a in b.get("apis_correct", [])]
        s_correct = [normalize_api(a) for a in s.get("apis_correct", [])]
        t_exp += len(expected); t_bf += len(b_found)
        t_sf += len(s_found); t_bc += len(b_correct); t_sc += len(s_correct)
        for api in expected:
            all_expected[api] += 1; sc_exp[scenario][api] += 1
        for api in b_found:
            base_found[api] += 1; sc_bf[scenario][api] += 1
        for api in s_found:
            sft_found[api] += 1; sc_sf[scenario][api] += 1
        for api in b_correct: base_correct[api] += 1
        for api in s_correct: sft_correct[api] += 1
        b_set = set(b_found); s_set = set(s_found); exp_set = set(expected)
        if len(s_found) > len(b_found): sft_better += 1
        elif len(b_found) > len(s_found): base_better += 1
        else: equal_t += 1
        if len(b_found) == 0 and len(s_found) == 0: both_zero += 1
        task_gaps.append({"task_id": task_id, "scenario": scenario,
            "n_expected": len(expected), "n_base_found": len(b_found),
            "n_sft_found": len(s_found), "n_base_correct": len(b_correct),
            "n_sft_correct": len(s_correct),
            "sft_new_apis": sorted(s_set - b_set),
            "base_only_apis": sorted(b_set - s_set),
            "both_missed": sorted(exp_set - b_set - s_set),
            "api_coverage_base": b.get("api_coverage", 0),
            "api_coverage_sft": s.get("api_coverage", 0)})
    all_apis = sorted(set(list(all_expected.keys()) + list(base_found.keys()) + list(sft_found.keys())))
    api_matrix = []
    for api in all_apis:
        exp = all_expected.get(api, 0); bf = base_found.get(api, 0)
        sf = sft_found.get(api, 0); bc = base_correct.get(api, 0); sc = sft_correct.get(api, 0)
        cat = ("sft_learned" if sf > 0 and bf == 0 else "sft_improved" if sf > bf else
               "both_use" if sf > 0 and bf > 0 and sf == bf else
               "base_only" if bf > 0 and sf == 0 else
               "both_missed" if exp > 0 and sf == 0 and bf == 0 else "unexpected_use")
        api_matrix.append({"api": api, "n_expected": exp, "n_base_found": bf,
            "n_sft_found": sf, "n_base_correct": bc, "n_sft_correct": sc,
            "base_hit_rate": round(bf/exp,4) if exp else 0,
            "sft_hit_rate": round(sf/exp,4) if exp else 0,
            "sft_delta": round((sf-bf)/exp,4) if exp else 0, "category": cat})
    cat_counts = Counter(am["category"] for am in api_matrix)
    bm = sorted([a for a in api_matrix if a["category"]=="both_missed"], key=lambda x: x["n_expected"], reverse=True)
    sl = sorted([a for a in api_matrix if a["category"]=="sft_learned"], key=lambda x: x["n_expected"], reverse=True)
    scenario_summary = {}
    for scn in sorted(set(list(sc_exp.keys()))):
        ec = sc_exp[scn]; bc2 = sc_bf.get(scn, Counter()); sf2 = sc_sf.get(scn, Counter())
        ne = sum(ec.values()); nb = sum(bc2.values()); ns = sum(sf2.values())
        nt = sum(1 for t in task_gaps if t["scenario"] == scn)
        scenario_summary[scn] = {"n_tasks": nt, "total_expected_calls": ne,
            "total_base_found": nb, "total_sft_found": ns,
            "base_recall": round(nb/ne,4) if ne else 0,
            "sft_recall": round(ns/ne,4) if ne else 0,
            "sft_recall_delta": round((ns-nb)/ne,4) if ne else 0,
            "unique_apis_expected": len(ec),
            "unique_apis_base_found": len(bc2),
            "unique_apis_sft_found": len(sf2)}
    br = t_bf/t_exp if t_exp else 0; sr = t_sf/t_exp if t_exp else 0
    bcr = t_bc/t_exp if t_exp else 0; scr = t_sc/t_exp if t_exp else 0
    return {"meta": {"analysis": "R297 API-Level Gap Analysis",
        "source": "eda_eval_static_full_wake287.json", "n_tasks": t_tasks,
        "n_unique_apis": len(all_apis), "total_expected_calls": t_exp,
        "total_base_found": t_bf, "total_sft_found": t_sf,
        "total_base_correct": t_bc, "total_sft_correct": t_sc},
        "overall_recall": {"base_recall": round(br,4), "sft_recall": round(sr,4),
            "sft_recall_delta": round(sr-br,4), "base_correct_rate": round(bcr,4),
            "sft_correct_rate": round(scr,4), "sft_correct_delta": round(scr-bcr,4)},
        "task_level": {"sft_better_tasks": sft_better, "base_better_tasks": base_better,
            "equal_tasks": equal_t, "both_zero_tasks": both_zero},
        "api_category_counts": dict(cat_counts),
        "scenario_summary": scenario_summary,
        "top_both_missed_apis": [{"api": a["api"], "n_expected": a["n_expected"]} for a in bm[:30]],
        "top_sft_learned_apis": [{"api": a["api"], "n_expected": a["n_expected"]} for a in sl[:20]],
        "api_matrix": api_matrix, "task_gaps": task_gaps}

def print_summary(r):
    m = r["meta"]; rec = r["overall_recall"]; tl = r["task_level"]; cc = r["api_category_counts"]
    print("=" * 70)
    print("R297 API-Level Gap Analysis Summary")
    print("=" * 70)
    print("Tasks: {} | Unique APIs: {} | Expected calls: {}".format(m["n_tasks"], m["n_unique_apis"], m["total_expected_calls"]))
    print("\n--- Overall Recall ---")
    print("  BASE recall:  {:.1%} ({}/{})".format(rec["base_recall"], m["total_base_found"], m["total_expected_calls"]))
    print("  SFT  recall:  {:.1%} ({}/{})".format(rec["sft_recall"], m["total_sft_found"], m["total_expected_calls"]))
    print("  SFT delta:    +{:.1%}".format(rec["sft_recall_delta"]))
    print("  BASE correct: {:.1%} | SFT correct: {:.1%} | delta: +{:.1%}".format(rec["base_correct_rate"], rec["sft_correct_rate"], rec["sft_correct_delta"]))
    print("\n--- Task-Level ---")
    print("  SFT>BASE: {} | BASE>SFT: {} | Equal: {} | Both 0: {}".format(tl["sft_better_tasks"], tl["base_better_tasks"], tl["equal_tasks"], tl["both_zero_tasks"]))
    print("\n--- API Categories ---")
    for cat, cnt in sorted(cc.items(), key=lambda x: -x[1]):
        print("  {:20s}: {} APIs".format(cat, cnt))
    print("\n--- Per-Scenario Recall ---")
    for sc, s in r["scenario_summary"].items():
        print("  {:20s}: t={:>3} exp={:>4} BASE={:.1%} SFT={:.1%} d=+{:.1%}".format(sc, s["n_tasks"], s["total_expected_calls"], s["base_recall"], s["sft_recall"], s["sft_recall_delta"]))
    print("\n--- Top 15 Both-Missed (RL Target) ---")
    for a in r["top_both_missed_apis"][:15]:
        print("  {:45s} exp in {} tasks".format(a["api"], a["n_expected"]))
    print("\n--- Top 10 SFT-Learned (SFT Wins) ---")
    for a in r["top_sft_learned_apis"][:10]:
        print("  {:45s} exp in {} tasks".format(a["api"], a["n_expected"]))
    print("\nOutput: {}".format(OUTPUT_FILE))

def main():
    if not os.path.exists(STATIC_FILE):
        print("ERROR: {} not found".format(STATIC_FILE), file=sys.stderr); sys.exit(1)
    with open(STATIC_FILE) as f: data = json.load(f)
    result = analyze(data)
    with open(OUTPUT_FILE, "w") as f: json.dump(result, f, indent=2, ensure_ascii=False)
    print_summary(result)

if __name__ == "__main__":
    main()
