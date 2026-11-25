#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R118: R0++ GRPO Learning Signal Verification on Real Model Rollouts.
R116 showed API coverage scoring gives std=0 for 100% of tasks.
R117 showed R0++ has GOOD SEPARATION on synthetic good/bad variants.
This script re-scores R116's 1200 REAL model completions with R0++.
Zero GPU. Python 3.8+ stdlib only.
Surrogate (Qwen3.8-27B) results NOT transferable to BaiZe.
"""
from __future__ import annotations
import argparse, ast, json, math, os, re, sys
from datetime import datetime
from collections import defaultdict

# ============================================================
# R0++ Reward (from R117, self-contained)
# ============================================================
class RewardR0PlusPlus:
    def __init__(self):
        self.weights = {"api_coverage": 0.20, "ast_call_verified": 0.30,
                        "return_path": 0.25, "arg_plausibility": 0.15,
                        "hardcode_penalty": 0.10}
    @staticmethod
    def _get_attr_chain(node):
        if isinstance(node, ast.Name): return node.id
        if isinstance(node, ast.Attribute):
            base = RewardR0PlusPlus._get_attr_chain(node.value)
            return base + "." + node.attr if base else None
        return None
    @staticmethod
    def _normalize_api(api):
        for prefix in ("pyAether.", "pyScript."):
            if api.startswith(prefix): return api[len(prefix):]
        return api
    def compute(self, code, apis_used, entry_point="", canonical_solution=""):
        r = {"api_coverage": 0.0, "ast_call_verified": 0.0, "return_path": 0.0,
             "arg_plausibility": 0.0, "hardcode_detected": False, "hardcode_penalty": 0.0,
             "syntax_ok": False, "final_reward": 0.0, "details": []}
        try:
            tree = ast.parse(code); r["syntax_ok"] = True
        except SyntaxError:
            r["details"].append("SyntaxError -> reward=0"); return r
        if not apis_used:
            r["details"].append("No required APIs -> reward=0"); return r
        mentioned = sum(1 for api in apis_used if self._normalize_api(api) in code or api in code)
        r["api_coverage"] = mentioned / len(apis_used)
        func_body_calls = []; candidate_func = None
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == entry_point or not entry_point:
                    candidate_func = node; break
        if candidate_func:
            for node in ast.walk(candidate_func):
                if isinstance(node, ast.Call):
                    chain = self._get_attr_chain(node.func)
                    func_body_calls.append((chain, len(node.args) > 0))
        verified = 0
        for api in apis_used:
            norm = self._normalize_api(api)
            for chain, _ in func_body_calls:
                cn = self._normalize_api(chain) if chain else ""
                if cn and (norm == cn or cn.endswith(norm) or norm.endswith(cn)):
                    verified += 1; break
        r["ast_call_verified"] = verified / len(apis_used)
        return_uses_api = False; has_return = False; return_literals = []
        if candidate_func:
            for node in ast.walk(candidate_func):
                if isinstance(node, ast.Return) and node.value is not None:
                    has_return = True
                    if isinstance(node.value, ast.Constant): return_literals.append(repr(node.value.value))
                    elif isinstance(node.value, (ast.List, ast.Tuple, ast.Dict, ast.Set)): return_literals.append(type(node.value).__name__)
                    for child in ast.walk(node.value):
                        if isinstance(child, ast.Call):
                            if self._get_attr_chain(child.func): return_uses_api = True; break
                    if isinstance(node.value, ast.Name) and not return_uses_api:
                        for asn in ast.walk(candidate_func):
                            if isinstance(asn, ast.Assign):
                                for t in asn.targets:
                                    if isinstance(t, ast.Name) and t.id == node.value.id:
                                        for sub in ast.walk(asn.value):
                                            if isinstance(sub, ast.Call): return_uses_api = True
        r["return_path"] = 1.0 if return_uses_api else (0.3 if has_return else 0.0)
        if return_literals and not func_body_calls:
            r["hardcode_detected"] = True; r["hardcode_penalty"] = 1.0
        elif return_literals and func_body_calls and not return_uses_api:
            r["hardcode_detected"] = True; r["hardcode_penalty"] = 0.5
        arg_score = 0.0; param_apis = 0
        for api in apis_used:
            norm = self._normalize_api(api)
            canon_has_args = bool(canonical_solution and re.search(re.escape(norm.split('.')[-1]) + r'\([^)]+\)', canonical_solution))
            if canon_has_args:
                param_apis += 1
                for chain, has_args in func_body_calls:
                    cn = self._normalize_api(chain) if chain else ""
                    if cn and (norm == cn or cn.endswith(norm)):
                        if has_args: arg_score += 1
        r["arg_plausibility"] = arg_score / param_apis if param_apis > 0 else 1.0
        w = self.weights
        base = w["api_coverage"]*r["api_coverage"] + w["ast_call_verified"]*r["ast_call_verified"] + w["return_path"]*r["return_path"] + w["arg_plausibility"]*r["arg_plausibility"]
        r["final_reward"] = round(max(0.0, min(1.0, base - w["hardcode_penalty"]*r["hardcode_penalty"])), 4)
        return r

# ============================================================
# Data Loading
# ============================================================
def load_synth_tasks(jsonl_path):
    tasks = {}
    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            d = json.loads(line)
            tid = d.get("task_id", "")
            meta = d.get("metadata", {})
            if isinstance(meta, str):
                try: meta = eval(meta)
                except Exception: meta = {}
            apis = meta.get("apis_used", [])
            if isinstance(apis, str):
                try: apis = eval(apis)
                except Exception: apis = [apis]
            tasks[tid] = {"apis_used": apis, "entry_point": d.get("entry_point", ""),
                          "canonical_solution": d.get("canonical_solution", ""),
                          "difficulty": meta.get("difficulty", "unknown")}
    return tasks

def load_r116_rollouts(json_path):
    with open(json_path) as f: return json.load(f)

# ============================================================
# R0++ Re-scoring + GRPO Signal Analysis
# ============================================================
def rescore_rollouts(r116_data, task_map, reward_fn):
    task_results = []
    for tr in r116_data.get("task_results", []):
        tid = tr["task_id"]; diff = tr.get("difficulty", "unknown")
        tinfo = task_map.get(tid, {})
        apis = tinfo.get("apis_used", []); entry = tinfo.get("entry_point", "")
        canonical = tinfo.get("canonical_solution", "")
        samples_scored = []
        for s in tr.get("samples", []):
            code = s.get("code", "")
            r = reward_fn.compute(code, apis, entry, canonical)
            samples_scored.append({
                "r0pp_reward": r["final_reward"],
                "r0pp_breakdown": {"api_coverage": r["api_coverage"],
                    "ast_call_verified": r["ast_call_verified"],
                    "return_path": r["return_path"],
                    "arg_plausibility": r["arg_plausibility"],
                    "hardcode_detected": r["hardcode_detected"],
                    "hardcode_penalty": r["hardcode_penalty"],
                    "syntax_ok": r["syntax_ok"]},
                "r0_api_coverage": s.get("api_coverage", 0),
                "r0_passed": s.get("passed", False)})
        rewards = [s["r0pp_reward"] for s in samples_scored]
        r0_covs = [s["r0_api_coverage"] for s in samples_scored]
        n = len(rewards)
        mean_r0pp = sum(rewards)/n if n else 0
        std_r0pp = (sum((x-mean_r0pp)**2 for x in rewards)/n)**0.5 if n else 0
        mean_r0 = sum(r0_covs)/n if n else 0
        std_r0 = (sum((x-mean_r0)**2 for x in r0_covs)/n)**0.5 if n else 0
        eps = 1e-8
        advs = [(r-mean_r0pp)/(std_r0pp+eps) if std_r0pp>eps else 0.0 for r in rewards]
        n_nz_adv = sum(1 for a in advs if abs(a)>0.01)
        task_results.append({"task_id": tid, "difficulty": diff, "n_samples": n,
            "r0pp": {"mean": round(mean_r0pp,4), "std": round(std_r0pp,4),
                      "min": round(min(rewards),4) if rewards else 0,
                      "max": round(max(rewards),4) if rewards else 0,
                      "n_nonzero_std": 1 if std_r0pp>0.01 else 0},
            "r0_api_coverage": {"mean": round(mean_r0,4), "std": round(std_r0,4),
                                 "n_nonzero_std": 1 if std_r0>0.01 else 0},
            "n_nonzero_advantages": n_nz_adv,
            "advantage_fraction": round(n_nz_adv/n,4) if n else 0,
            "samples": samples_scored})
    return task_results

def aggregate_analysis(task_results):
    n_tasks = len(task_results)
    r0pp_stds = [tr["r0pp"]["std"] for tr in task_results]
    r0pp_means = [tr["r0pp"]["mean"] for tr in task_results]
    r0_stds = [tr["r0_api_coverage"]["std"] for tr in task_results]
    r0_means = [tr["r0_api_coverage"]["mean"] for tr in task_results]
    adv_fracs = [tr["advantage_fraction"] for tr in task_results]
    n_r0pp_nz = sum(1 for s in r0pp_stds if s > 0.01)
    n_r0_nz = sum(1 for s in r0_stds if s > 0.01)
    tier_stats = defaultdict(lambda: {"n_tasks": 0, "r0pp_means": [], "r0pp_stds": [],
        "r0_means": [], "r0_stds": [], "adv_fracs": [], "n_nz_r0pp": 0, "n_nz_r0": 0})
    for tr in task_results:
        ts = tier_stats[tr["difficulty"]]
        ts["n_tasks"] += 1
        ts["r0pp_means"].append(tr["r0pp"]["mean"]); ts["r0pp_stds"].append(tr["r0pp"]["std"])
        ts["r0_means"].append(tr["r0_api_coverage"]["mean"]); ts["r0_stds"].append(tr["r0_api_coverage"]["std"])
        ts["adv_fracs"].append(tr["advantage_fraction"])
        ts["n_nz_r0pp"] += tr["r0pp"]["n_nonzero_std"]; ts["n_nz_r0"] += tr["r0_api_coverage"]["n_nonzero_std"]
    tier_summary = {}
    for diff, ts in sorted(tier_stats.items()):
        n = ts["n_tasks"]
        tier_summary[diff] = {"n_tasks": n,
            "r0pp_mean": round(sum(ts["r0pp_means"])/n, 4), "r0pp_std_avg": round(sum(ts["r0pp_stds"])/n, 4),
            "r0pp_nz_pct": round(ts["n_nz_r0pp"]/n*100, 1), "r0_mean": round(sum(ts["r0_means"])/n, 4),
            "r0_std_avg": round(sum(ts["r0_stds"])/n, 4), "r0_nz_pct": round(ts["n_nz_r0"]/n*100, 1),
            "avg_adv_frac": round(sum(ts["adv_fracs"])/n, 4)}
    hacking = []
    for tr in task_results:
        for i, s in enumerate(tr["samples"]):
            if s["r0pp_breakdown"]["hardcode_detected"] and s["r0pp_reward"] > 0.3:
                hacking.append({"task_id": tr["task_id"], "sample": i,
                    "r0pp": s["r0pp_reward"], "penalty": s["r0pp_breakdown"]["hardcode_penalty"]})
    all_bd = [s["r0pp_breakdown"] for tr in task_results for s in tr["samples"]]
    nt = len(all_bd)
    bd_agg = {"n_total": nt,
        "syntax_ok_pct": round(sum(1 for b in all_bd if b["syntax_ok"])/nt*100, 1),
        "hardcode_pct": round(sum(1 for b in all_bd if b["hardcode_detected"])/nt*100, 1),
        "avg_api_cov": round(sum(b["api_coverage"] for b in all_bd)/nt, 4),
        "avg_ast_call": round(sum(b["ast_call_verified"] for b in all_bd)/nt, 4),
        "avg_ret_path": round(sum(b["return_path"] for b in all_bd)/nt, 4),
        "avg_arg_plaus": round(sum(b["arg_plausibility"] for b in all_bd)/nt, 4)}
    r0pp_pct = n_r0pp_nz/n_tasks*100 if n_tasks else 0
    r0_pct = n_r0_nz/n_tasks*100 if n_tasks else 0
    if r0pp_pct > 30 and r0pp_pct > r0_pct*3:
        verdict = "GOOD: R0++ provides significantly more GRPO signal than R0"
    elif r0pp_pct > 15:
        verdict = "MODERATE: R0++ provides some GRPO signal, but many tasks still zero-variance"
    else:
        verdict = "POOR: R0++ does not provide sufficient GRPO signal on this surrogate"
    return {"n_tasks": n_tasks, "r0pp_nz_count": n_r0pp_nz, "r0pp_nz_pct": round(r0pp_pct, 1),
        "r0_nz_count": n_r0_nz, "r0_nz_pct": round(r0_pct, 1),
        "r0pp_mean_means": round(sum(r0pp_means)/n_tasks, 4),
        "r0pp_mean_stds": round(sum(r0pp_stds)/n_tasks, 4),
        "r0_mean_means": round(sum(r0_means)/n_tasks, 4),
        "r0_mean_stds": round(sum(r0_stds)/n_tasks, 4),
        "avg_adv_frac": round(sum(adv_fracs)/n_tasks, 4),
        "tier_summary": tier_summary, "breakdown_agg": bd_agg,
        "hacking_cases": hacking[:20], "n_hacking": len(hacking), "verdict": verdict}

# ============================================================
# Main
# ============================================================
def _print_summary(label, a):
    print("\n  --- " + label + " Summary ---")
    print("  Tasks: " + str(a["n_tasks"]))
    print("  R0++ non-zero std: " + str(a["r0pp_nz_count"]) + "/" + str(a["n_tasks"]) + " (" + str(a["r0pp_nz_pct"]) + "%)")
    print("  R0 non-zero std:   " + str(a["r0_nz_count"]) + "/" + str(a["n_tasks"]) + " (" + str(a["r0_nz_pct"]) + "%)")
    print("  R0++ mean reward:  " + str(a["r0pp_mean_means"]) + " (R0: " + str(a["r0_mean_means"]) + ")")
    print("  R0++ mean std:     " + str(a["r0pp_mean_stds"]) + " (R0: " + str(a["r0_mean_stds"]) + ")")
    print("  Avg adv fraction:  " + str(a["avg_adv_frac"]))
    print("  Hacking cases:     " + str(a["n_hacking"]))
    print("  Verdict: " + a["verdict"])

def main():
    parser = argparse.ArgumentParser(description="R118: R0++ GRPO Signal Verification")
    parser.add_argument("--mode", choices=["full","nodocs","withdocs"], default="full")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    sd = os.path.dirname(os.path.abspath(__file__))
    out = args.output or os.path.join(sd, "r118_r0pp_grpo_signal.json")
    print("=" * 70)
    print("R118: R0++ GRPO Learning Signal on Real Model Rollouts")
    print("=" * 70)
    print("\n[1] Loading synthetic task metadata...")
    task_map = load_synth_tasks(os.path.join(sd, "rl_pyaether_synth_v2.jsonl"))
    print("  Loaded " + str(len(task_map)) + " tasks")
    reward_fn = RewardR0PlusPlus()
    result = {"r118": True, "timestamp": datetime.now().isoformat(),
              "surrogate_warning": "Qwen3.8-27B surrogate NOT transferable to BaiZe",
              "r0pp_weights": reward_fn.weights}
    conditions = []
    if args.mode in ("full", "nodocs"):
        p = os.path.join(sd, "r116_pass8_profiling_nodocs.json")
        if os.path.exists(p):
            print("\n[2] Loading R116 NO-DOCS rollouts...")
            d = load_r116_rollouts(p)
            nt = len(d.get("task_results", []))
            ns = sum(len(tr.get("samples", [])) for tr in d.get("task_results", []))
            print("  " + str(nt) + " tasks, " + str(ns) + " samples")
            print("  Re-scoring with R0++...")
            rs = rescore_rollouts(d, task_map, reward_fn)
            an = aggregate_analysis(rs)
            result["nodocs"] = {"n_tasks": nt, "n_samples": ns, "analysis": an, "task_results": rs}
            conditions.append(("NO-DOCS", an))
            _print_summary("NO-DOCS", an)
    if args.mode in ("full", "withdocs"):
        p = os.path.join(sd, "r116_pass8_profiling_withdocs.json")
        if os.path.exists(p):
            print("\n[3] Loading R116 WITH-DOCS rollouts...")
            d = load_r116_rollouts(p)
            nt = len(d.get("task_results", []))
            ns = sum(len(tr.get("samples", [])) for tr in d.get("task_results", []))
            print("  " + str(nt) + " tasks, " + str(ns) + " samples")
            print("  Re-scoring with R0++...")
            rs = rescore_rollouts(d, task_map, reward_fn)
            an = aggregate_analysis(rs)
            result["withdocs"] = {"n_tasks": nt, "n_samples": ns, "analysis": an, "task_results": rs}
            conditions.append(("WITH-DOCS", an))
            _print_summary("WITH-DOCS", an)
    if len(conditions) == 2:
        nd, wd = conditions[0][1], conditions[1][1]
        print("\n" + "=" * 70)
        print("[4] Cross-condition: R0++ vs R0 API coverage")
        print("=" * 70)
        print("\n  Metric                          NO-DOCS    WITH-DOCS   R0(NO-DOCS)")
        print("  " + "-" * 66)
        print("  Non-zero std tasks (R0++)       {:>5.1f}%   {:>5.1f}%    {:>5.1f}%".format(nd["r0pp_nz_pct"], wd["r0pp_nz_pct"], nd["r0_nz_pct"]))
        print("  Mean within-group std           {:>7.4f}    {:>7.4f}     {:>7.4f}".format(nd["r0pp_mean_stds"], wd["r0pp_mean_stds"], nd["r0_mean_stds"]))
        print("  Mean reward                     {:>7.4f}    {:>7.4f}     {:>7.4f}".format(nd["r0pp_mean_means"], wd["r0pp_mean_means"], nd["r0_mean_means"]))
        print("  Avg advantage fraction          {:>7.4f}    {:>7.4f}".format(nd["avg_adv_frac"], wd["avg_adv_frac"]))
        print("  Hacking cases                   {:>5d}      {:>5d}".format(nd["n_hacking"], wd["n_hacking"]))
        print("\n  NO-DOCS verdict:  " + nd["verdict"])
        print("  WITH-DOCS verdict: " + wd["verdict"])
        result["comparison"] = {"r0pp_nz_nodocs": nd["r0pp_nz_pct"], "r0_nz_nodocs": nd["r0_nz_pct"],
            "r0pp_nz_withdocs": wd["r0pp_nz_pct"], "r0_nz_withdocs": wd["r0_nz_pct"],
            "improvement_factor": round(nd["r0pp_nz_pct"]/max(nd["r0_nz_pct"],0.1), 1)}
    if conditions:
        print("\n[5] Per-tier R0++ (NO-DOCS):")
        ts = conditions[0][1]["tier_summary"]
        print("  Tier  Tasks  R0++mean  R0++std  R0++nz%  R0nz%  AdvFrac")
        print("  " + "-" * 60)
        for diff in sorted(ts.keys()):
            t = ts[diff]
            print("  {:<4}  {:>5}  {:>8.4f}  {:>7.4f}  {:>6.1f}%  {:>5.1f}%  {:>7.4f}".format(
                diff, t["n_tasks"], t["r0pp_mean"], t["r0pp_std_avg"], t["r0pp_nz_pct"], t["r0_nz_pct"], t["avg_adv_frac"]))
        nd = conditions[0][1]
        print("\n[6] GRPO Implications:")
        print("  R0++ non-zero var: " + str(nd["r0pp_nz_count"]) + "/" + str(nd["n_tasks"]) + " (" + str(nd["r0pp_nz_pct"]) + "%)")
        print("  R0 non-zero var:   " + str(nd["r0_nz_count"]) + "/" + str(nd["n_tasks"]) + " (" + str(nd["r0_nz_pct"]) + "%)")
        print("  Improvement: " + str(round(nd["r0pp_nz_count"]/max(nd["r0_nz_count"],1), 1)) + "x")
        print("  Hacking caught: " + str(nd["n_hacking"]))
        print("  Verdict: " + nd["verdict"])
    with open(out, "w") as f: json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    print("\n[7] Saved to " + out + " (" + str(os.path.getsize(out)) + " bytes)")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())
