#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_r128_solvability_verifier.py — BaiZe Stage(ii) R128

Comprehensive static quality audit & solvability verification of the 3,347
synthetic RL tasks (rl_pyaether_synth_v2.jsonl).

Six verification dimensions:
  V1  API existence       — every api_used exists in 8,463-API KB
  V2  Canonical validity  — canonical_solution parses as valid Python AST
  V3  Entry-point match   — entry_point matches function in prompt/canonical
  V4  Assertion quality   — test code has real assertions (not bare pass)
  V5  Type consistency    — test assertion type matches API return type
  V6  Contamination       — zero overlap with 158 eval tasks

Zero GPU. Pure Python 3.8+ stdlib.
⚠️ Surrogate analysis results are NOT transferable to BaiZe.
"""

import argparse, ast, hashlib, json, os, re, sys
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
V2_TASKS_PATH = os.path.join(SCRIPT_DIR, "rl_pyaether_synth_v2.jsonl")
API_KB_PATH = os.path.expanduser("~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json")
EVAL_DATASET_PATH = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
REPORT_PATH = os.path.join(SCRIPT_DIR, "r128_quality_audit_report.json")
VERIFIED_OUTPUT = os.path.join(SCRIPT_DIR, "rl_pyaether_synth_v2_verified.jsonl")

PY_TYPE_MAP = {
    "bool": "bool", "emyBoolean": "bool", "str": "str", "emyString": "str",
    "aeStringField": "str", "int": "int", "emyUInt4": "int", "emyInt4": "int",
    "emyChar": "int", "float": "float", "emyDouble": "float", "emyDist": "float",
    "list": "list", "tuple": "tuple", "List[str]": "list",
    "List[int]": "list", "List[bool]": "list",
}

# ═══════════════════════════════════════════════════
#  Loaders
# ═══════════════════════════════════════════════════

def load_jsonl(path):
    results = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                results.append(json.loads(line))
    return results

def load_api_kb(path):
    if not os.path.exists(path):
        print(f"  WARNING: API KB not found: {path}")
        return set(), {}
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    api_names, api_details = set(), {}
    if isinstance(raw, list):
        for entry in raw:
            name = entry.get("api_name") or entry.get("name") or ""
            if name:
                api_names.add(name)
                api_details[name] = entry
    elif isinstance(raw, dict):
        for key, val in raw.items():
            api_names.add(key)
            if isinstance(val, dict):
                api_details[key] = val
    return api_names, api_details

# ═══════════════════════════════════════════════════
#  Verification Dimensions
# ═══════════════════════════════════════════════════

def verify_v1_api_existence(task, api_kb):
    apis = task.get("metadata", {}).get("apis_used", [])
    if not apis:
        return {"pass": False, "reason": "no apis_used in metadata"}
    missing = [a for a in apis if a not in api_kb]
    if missing:
        normalized = []
        for a in missing:
            short = a.replace("pyAether.", "").replace("pyScript.", "")
            if short in api_kb or a in api_kb:
                continue
            normalized.append(a)
        missing = normalized
    return {"pass": len(missing) == 0,
            "reason": f"{len(missing)}/{len(apis)} not in KB" if missing else "all in KB"}

def verify_v2_canonical_validity(task):
    canonical = task.get("canonical_solution", "")
    if not canonical.strip():
        return {"pass": False, "reason": "empty canonical_solution"}
    wrapped = f"def {task.get('entry_point', 'func')}():\n{canonical}"
    try:
        ast.parse(wrapped)
        return {"pass": True, "reason": "valid AST"}
    except SyntaxError as e:
        return {"pass": False, "reason": f"syntax error: {e.msg} L{e.lineno}"}

def verify_v3_entry_point_match(task):
    ep = task.get("entry_point", "")
    prompt = task.get("prompt", "")
    if not ep:
        return {"pass": False, "reason": "no entry_point"}
    pattern = r"\bdef\s+" + re.escape(ep) + r"\s*\("
    if re.search(pattern, prompt):
        return {"pass": True, "reason": "entry_point in prompt"}
    return {"pass": False, "reason": f"'{ep}' not in prompt"}

def verify_v4_assertion_quality(task):
    test = task.get("test", "")
    if not test.strip():
        return {"pass": False, "reason": "empty test"}
    if re.match(r"^\s*pass\s*#", test) or test.strip() == "pass":
        return {"pass": False, "reason": "bare pass"}
    assert_count = len(re.findall(r"\bassert\b", test))
    if assert_count == 0:
        return {"pass": False, "reason": "no assert in test"}
    if "def check" not in test:
        return {"pass": False, "reason": "no check() function"}
    return {"pass": True, "reason": f"{assert_count} asserts", "assert_count": assert_count}

def _extract_assertion_types(test):
    types_found = set()
    for m in re.finditer(r"isinstance\([^,]+,\s*([^)]+)\)", test):
        for t in m.group(1).strip().split(","):
            types_found.add(t.strip().strip("()"))
    return types_found

def _get_expected_py_type(api_name, api_details):
    info = api_details.get(api_name)
    if not info:
        short = api_name.replace("pyAether.", "").replace("pyScript.", "")
        info = api_details.get(short)
    if not info:
        return None
    desc = info.get("api_descriptions", "") or info.get("description", "")
    if not desc:
        return None
    for pattern in [r"\*\*out\*\*\s*(\S+)", r"Returns\s+\*\*(\S+?)\*\*", r"->\s*(\S+)"]:
        m = re.search(pattern, desc)
        if m:
            rt = m.group(1).strip().rstrip(",")
            return PY_TYPE_MAP.get(rt, "object" if rt else None)
    return None

def verify_v5_type_consistency(task, api_details):
    test = task.get("test", "")
    apis = task.get("metadata", {}).get("apis_used", [])
    if not apis:
        return {"pass": True, "reason": "no APIs (skip)", "skip": True}
    if len(apis) == 1:
        expected = _get_expected_py_type(apis[0], api_details)
        if expected is None:
            return {"pass": True, "reason": "API type unknown (skip)", "skip": True}
        actual_types = _extract_assertion_types(test)
        if not actual_types:
            return {"pass": True, "reason": "no isinstance (skip)", "skip": True}
        type_compat = {"bool": {"bool"}, "str": {"str"}, "int": {"int"},
                       "float": {"int", "float"}, "list": {"list", "tuple"},
                       "tuple": {"list", "tuple"}}
        compatible = type_compat.get(expected, {expected})
        if actual_types & compatible:
            return {"pass": True, "reason": f"type match ({expected})"}
        return {"pass": False, "reason": f"mismatch: API={expected}, test={actual_types}"}
    actual_types = _extract_assertion_types(test)
    if actual_types:
        return {"pass": True, "reason": f"multi-API, {len(actual_types)} type checks"}
    return {"pass": True, "reason": "multi-API structural (skip)", "skip": True}

def _prompt_hash(prompt):
    return hashlib.md5(prompt.strip().encode()).hexdigest()

def _entry_points_from_eval(eval_tasks):
    eps = set()
    for t in eval_tasks:
        ep = t.get("entry_point", "")
        if ep:
            eps.add(ep)
        for m in re.finditer(r"def\s+(\w+)\s*\(", t.get("prompt", "")):
            eps.add(m.group(1))
    return eps

def _api_sets_from_eval(eval_tasks):
    api_sets = []
    for t in eval_tasks:
        apis = set()
        meta = t.get("metadata", {})
        for key in ("apis_used", "unique_apis", "api_list"):
            val = meta.get(key, [])
            if isinstance(val, list):
                apis.update(val)
        canonical = t.get("canonical_solution", "")
        for m in re.finditer(r"pyScript\.(\w+(?:\.\w+)*)", canonical):
            apis.add(m.group(1))
        for m in re.finditer(r"pyAether\.(\w+(?:\.\w+)*)", canonical):
            apis.add(m.group(1))
        if apis:
            api_sets.append(apis)
    return api_sets

def verify_v6_contamination(task, eval_prompt_hashes, eval_entry_points, eval_api_sets):
    issues = []
    ph = _prompt_hash(task.get("prompt", ""))
    if ph in eval_prompt_hashes:
        issues.append("prompt_hash")
    ep = task.get("entry_point", "")
    if ep in eval_entry_points:
        issues.append("entry_point")
    task_apis = set(task.get("metadata", {}).get("apis_used", []))
    if task_apis:
        for eval_set in eval_api_sets:
            if task_apis <= eval_set and len(task_apis) >= 2:
                issues.append("api_subset")
                break
    return {"pass": len(issues) == 0,
            "reason": "clean" if not issues else f"contam: {issues}"}

def compute_solvability_score(verifications):
    weights = {"V1_api_existence": 0.25, "V2_canonical_validity": 0.25,
               "V3_entry_point_match": 0.10, "V4_assertion_quality": 0.20,
               "V5_type_consistency": 0.10, "V6_contamination": 0.10}
    score = 0.0
    for key, weight in weights.items():
        result = verifications.get(key, {})
        if result.get("skip") or result.get("pass"):
            score += weight
    return round(score, 4)

# ═══════════════════════════════════════════════════
#  Main Audit
# ═══════════════════════════════════════════════════

def run_audit(max_tasks=None, dry_run=False):
    print("=" * 70)
    print("R128: Solvability Verifier & Quality Audit")
    print("=" * 70)

    print("\n[1] Loading data...")
    v2_tasks = load_jsonl(V2_TASKS_PATH)
    print(f"  v2 tasks: {len(v2_tasks)}")
    api_names, api_details = load_api_kb(API_KB_PATH)
    print(f"  API KB: {len(api_names)} APIs")
    eval_tasks = load_jsonl(EVAL_DATASET_PATH)
    print(f"  eval tasks: {len(eval_tasks)}")
    if max_tasks:
        v2_tasks = v2_tasks[:max_tasks]
        print(f"  [limited to {max_tasks} tasks]")

    eval_prompt_hashes = set(_prompt_hash(t.get("prompt", "")) for t in eval_tasks)
    eval_entry_points = _entry_points_from_eval(eval_tasks)
    eval_api_sets = _api_sets_from_eval(eval_tasks)
    print(f"  eval fingerprints: {len(eval_prompt_hashes)} hashes, {len(eval_entry_points)} EPs, {len(eval_api_sets)} API sets")

    print("\n[2] Running 6-dimension verification...")
    all_results = []
    vkeys = ["V1_api_existence", "V2_canonical_validity", "V3_entry_point_match",
             "V4_assertion_quality", "V5_type_consistency", "V6_contamination"]
    pass_counts = {k: 0 for k in vkeys}
    skip_counts = {k: 0 for k in vkeys}
    fail_details = defaultdict(list)

    for i, task in enumerate(v2_tasks):
        if (i + 1) % 500 == 0:
            print(f"  ...{i+1}/{len(v2_tasks)}")
        verifications = {
            "V1_api_existence": verify_v1_api_existence(task, api_names),
            "V2_canonical_validity": verify_v2_canonical_validity(task),
            "V3_entry_point_match": verify_v3_entry_point_match(task),
            "V4_assertion_quality": verify_v4_assertion_quality(task),
            "V5_type_consistency": verify_v5_type_consistency(task, api_details),
            "V6_contamination": verify_v6_contamination(
                task, eval_prompt_hashes, eval_entry_points, eval_api_sets),
        }
        score = compute_solvability_score(verifications)
        all_results.append({
            "task_id": task.get("task_id", ""),
            "difficulty": task.get("metadata", {}).get("difficulty", ""),
            "solvability_score": score,
            "all_pass": all(v.get("skip", False) or v.get("pass", False)
                           for v in verifications.values()),
            "verifications": verifications,
        })
        for vkey, vresult in verifications.items():
            if vresult.get("skip"):
                skip_counts[vkey] += 1
            elif vresult.get("pass"):
                pass_counts[vkey] += 1
            else:
                fail_details[vkey].append({
                    "task_id": task.get("task_id", ""),
                    "reason": vresult.get("reason", "unknown")[:100]})

    total = len(v2_tasks)
    print("\n[3] Verification summary:")
    for vkey in sorted(pass_counts.keys()):
        p, s = pass_counts[vkey], skip_counts[vkey]
        f = total - p - s
        print(f"  {vkey}: PASS={p} SKIP={s} FAIL={f} ({(p+s)/max(total,1)*100:.1f}% ok)")

    scores = [r["solvability_score"] for r in all_results]
    score_buckets = {"1.0": 0, "0.8-0.99": 0, "0.6-0.79": 0, "0.4-0.59": 0, "<0.4": 0}
    for s in scores:
        if s >= 1.0: score_buckets["1.0"] += 1
        elif s >= 0.8: score_buckets["0.8-0.99"] += 1
        elif s >= 0.6: score_buckets["0.6-0.79"] += 1
        elif s >= 0.4: score_buckets["0.4-0.59"] += 1
        else: score_buckets["<0.4"] += 1

    print(f"\n[4] Solvability score distribution:")
    for bucket, count in score_buckets.items():
        print(f"  {bucket}: {count} ({count/max(total,1)*100:.1f}%)")

    all_pass_count = sum(1 for r in all_results if r["all_pass"])
    high_quality = [r for r in all_results if r["solvability_score"] >= 0.8]
    print(f"\n  All-pass: {all_pass_count}/{total} ({all_pass_count/max(total,1)*100:.1f}%)")
    print(f"  High-quality (>=0.8): {len(high_quality)}/{total} ({len(high_quality)/max(total,1)*100:.1f}%)")
    return _finalize_audit(v2_tasks, all_results, pass_counts, skip_counts,
                           fail_details, score_buckets, api_names, total,
                           all_pass_count, high_quality, dry_run)

def _finalize_audit(v2_tasks, all_results, pass_counts, skip_counts,
                    fail_details, score_buckets, api_names, total,
                    all_pass_count, high_quality, dry_run):
    print(f"\n[5] Difficulty breakdown:")
    diff_stats = defaultdict(lambda: {"total": 0, "pass": 0, "sum_score": 0.0})
    for r in all_results:
        d = r["difficulty"]
        diff_stats[d]["total"] += 1
        if r["all_pass"]: diff_stats[d]["pass"] += 1
        diff_stats[d]["sum_score"] += r["solvability_score"]
    for d in sorted(diff_stats.keys()):
        s = diff_stats[d]
        avg = s["sum_score"] / max(s["total"], 1)
        print(f"  {d}: {s['pass']}/{s['total']} all-pass ({s['pass']/max(s['total'],1)*100:.1f}%), avg={avg:.3f}")

    print(f"\n[6] API coverage:")
    all_apis_used = set()
    for task in v2_tasks:
        for a in task.get("metadata", {}).get("apis_used", []):
            all_apis_used.add(a)
    # Normalize for coverage comparison (strip pyAether. prefix like V1 does)
    all_apis_normalized = set()
    for a in all_apis_used:
        short = a.replace("pyAether.", "").replace("pyScript.", "")
        all_apis_normalized.add(short)
        all_apis_normalized.add(a)
    covered = len(all_apis_normalized & api_names)
    print(f"  Unique APIs in tasks: {len(all_apis_used)}")
    print(f"  API KB size: {len(api_names)}")
    print(f"  Coverage: {covered}/{len(api_names)} ({covered/max(len(api_names),1)*100:.1f}%)")

    print(f"\n[7] Failure details (first 5 per dimension):")
    for vkey in sorted(fail_details.keys()):
        fails = fail_details[vkey]
        if fails:
            print(f"  {vkey} ({len(fails)} failures):")
            for fd in fails[:5]:
                print(f"    {fd['task_id']}: {fd['reason']}")
            if len(fails) > 5:
                print(f"    ... and {len(fails)-5} more")

    verified_tasks = []
    for task, result in zip(v2_tasks, all_results):
        if result["solvability_score"] >= 0.8:
            tc = dict(task)
            tc["metadata"]["solvability_score"] = result["solvability_score"]
            tc["metadata"]["verified"] = result["all_pass"]
            verified_tasks.append(tc)

    print(f"\n[8] Verified output: {len(verified_tasks)}/{total} tasks (>=0.8)")

    if not dry_run:
        with open(VERIFIED_OUTPUT, "w", encoding="utf-8") as f:
            for task in verified_tasks:
                f.write(json.dumps(task, ensure_ascii=False) + "\n")
        print(f"  Written: {VERIFIED_OUTPUT}")
        report = {
            "round": "R128", "timestamp": "2026-11-10", "total_tasks": total,
            "verification_summary": {vkey: {"pass": pass_counts[vkey], "skip": skip_counts[vkey],
                "fail": total - pass_counts[vkey] - skip_counts[vkey]}
                for vkey in sorted(pass_counts.keys())},
            "solvability_distribution": score_buckets,
            "all_pass_count": all_pass_count, "high_quality_count": len(high_quality),
            "difficulty_breakdown": {d: {"total": diff_stats[d]["total"],
                "pass": diff_stats[d]["pass"],
                "avg_score": round(diff_stats[d]["sum_score"] / max(diff_stats[d]["total"], 1), 4)}
                for d in sorted(diff_stats.keys())},
            "api_coverage": {"unique_apis_used": len(all_apis_used), "api_kb_size": len(api_names),
                "coverage_pct": round(covered / max(len(api_names), 1) * 100, 2)},
            "verified_output_count": len(verified_tasks),
            "fail_details_sample": {vkey: fails[:10] for vkey, fails in fail_details.items() if fails},
        }
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"  Report: {REPORT_PATH}")

    contam_fails = fail_details.get("V6_contamination", [])
    print(f"\n[9] Contamination: {len(contam_fails)} failures")
    if contam_fails:
        print(f"  RED: CONTAMINATION DETECTED — {len(contam_fails)} tasks overlap!")
    else:
        print(f"  GREEN: ZERO contamination — all {total} tasks clean")

    return report if not dry_run else {"total_tasks": total}

def main():
    parser = argparse.ArgumentParser(description="R128: Solvability Verifier & Quality Audit")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-tasks", type=int, default=None)
    args = parser.parse_args()
    result = run_audit(max_tasks=args.max_tasks, dry_run=args.dry_run)
    print(f"\n{'='*70}")
    print(f"R128 complete. Tasks: {result.get('total_tasks', '?')}")
    print(f"{'='*70}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
