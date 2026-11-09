#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R117: Execution-Correctness Reward Architecture (R1 + R3 directions).
Zero GPU. Python 3.8+ stdlib only.
Follows R116: API coverage scoring has ZERO discriminability -> need execution correctness.
But EDA sandbox (10.129.32.75) is UNREACHABLE from .17.
This script designs R0++ enhanced static analysis reward + verl integration.
Surrogate results NOT transferable to BaiZe.
"""
from __future__ import annotations
import argparse, ast, json, os, re, sys, textwrap
from datetime import datetime

# --- 1. Sandbox Connectivity ---
def check_sandbox_connectivity():
    import socket
    host = os.getenv("SANDBOX_HOST", "10.129.32.75")
    ports = [8667, 8669, 8664, 8665, 8653, 8668]
    results = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        try:
            sock.connect((host, port))
            results.append({"port": port, "status": "OPEN"})
        except (socket.timeout, ConnectionRefusedError, OSError):
            results.append({"port": port, "status": "FILTERED"})
        finally:
            sock.close()
    any_open = any(r["status"] == "OPEN" for r in results)
    return {"host": host, "ports_checked": results, "any_open": any_open,
            "verdict": "REACHABLE" if any_open else "UNREACHABLE (all TCP filtered)",
            "timestamp": datetime.now().isoformat(),
            "implication": "Execution-correctness reward BLOCKED until firewall or local sandbox"}

# --- 2. R0++ Enhanced Static Analysis Reward ---
class RewardR0PlusPlus:
    """AST-level reward: api_coverage + ast_call_verified + return_path + arg_plausibility - hardcode_penalty."""
    def __init__(self):
        self.weights = {"api_coverage": 0.20, "ast_call_verified": 0.30,
                        "return_path": 0.25, "arg_plausibility": 0.15, "hardcode_penalty": 0.10}

    @staticmethod
    def _get_attr_chain(node):
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = RewardR0PlusPlus._get_attr_chain(node.value)
            return base + "." + node.attr if base else None
        return None

    @staticmethod
    def _normalize_api(api):
        for prefix in ("pyAether.", "pyScript."):
            if api.startswith(prefix):
                return api[len(prefix):]
        return api

    def compute(self, code, apis_used, entry_point="", canonical_solution=""):
        r = {"api_coverage": 0.0, "ast_call_verified": 0.0, "return_path": 0.0,
             "arg_plausibility": 0.0, "hardcode_detected": False, "hardcode_penalty": 0.0,
             "syntax_ok": False, "final_reward": 0.0, "details": []}
        try:
            tree = ast.parse(code)
            r["syntax_ok"] = True
        except SyntaxError:
            r["details"].append("SyntaxError -> reward=0")
            return r
        if not apis_used:
            r["details"].append("No required APIs -> reward=0")
            return r

        # 2a. API Coverage (text mention)
        mentioned = sum(1 for api in apis_used if self._normalize_api(api) in code or api in code)
        r["api_coverage"] = mentioned / len(apis_used)

        # 2b. AST Call Verification
        func_body_calls = []
        candidate_func = None
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == entry_point or not entry_point:
                    candidate_func = node
                    break
        if candidate_func:
            for node in ast.walk(candidate_func):
                if isinstance(node, ast.Call):
                    chain = self._get_attr_chain(node.func)
                    func_body_calls.append((chain, len(node.args) > 0))
        verified = 0
        for api in apis_used:
            norm = self._normalize_api(api)
            for chain, _ in func_body_calls:
                if chain and (norm == self._normalize_api(chain) or self._normalize_api(chain).endswith(norm) or norm.endswith(self._normalize_api(chain))):
                    verified += 1
                    break
        r["ast_call_verified"] = verified / len(apis_used)

        # 2c. Return Path Analysis
        return_uses_api = False
        has_return = False
        return_literals = []
        if candidate_func:
            for node in ast.walk(candidate_func):
                if isinstance(node, ast.Return) and node.value is not None:
                    has_return = True
                    if isinstance(node.value, ast.Constant):
                        return_literals.append(repr(node.value.value))
                    elif isinstance(node.value, (ast.List, ast.Tuple, ast.Dict, ast.Set)):
                        return_literals.append(type(node.value).__name__)
                    for child in ast.walk(node.value):
                        if isinstance(child, ast.Call):
                            if self._get_attr_chain(child.func):
                                return_uses_api = True
                                break
                    if isinstance(node.value, ast.Name) and not return_uses_api:
                        for asn in ast.walk(candidate_func):
                            if isinstance(asn, ast.Assign):
                                for t in asn.targets:
                                    if isinstance(t, ast.Name) and t.id == node.value.id:
                                        for sub in ast.walk(asn.value):
                                            if isinstance(sub, ast.Call):
                                                return_uses_api = True
        r["return_path"] = 1.0 if return_uses_api else (0.3 if has_return else 0.0)

        # 2d. Hardcode Detection
        if return_literals and not func_body_calls:
            r["hardcode_detected"] = True
            r["hardcode_penalty"] = 1.0
            r["details"].append("Hardcode: return " + return_literals[0] + " without API call")
        elif return_literals and func_body_calls and not return_uses_api:
            r["hardcode_detected"] = True
            r["hardcode_penalty"] = 0.5
            r["details"].append("Partial hardcode: API called but returns literal")

        # 2e. Argument Plausibility
        arg_score = 0.0
        param_apis = 0
        for api in apis_used:
            norm = self._normalize_api(api)
            canon_has_args = bool(canonical_solution and re.search(re.escape(norm.split('.')[-1]) + r'\([^)]+\)', canonical_solution))
            if canon_has_args:
                param_apis += 1
                for chain, has_args in func_body_calls:
                    if chain and (norm == self._normalize_api(chain) or self._normalize_api(chain).endswith(norm)):
                        if has_args:
                            arg_score += 1
                        break
        r["arg_plausibility"] = arg_score / param_apis if param_apis > 0 else 1.0

        # 2f. Final Reward
        w = self.weights
        base = w["api_coverage"]*r["api_coverage"] + w["ast_call_verified"]*r["ast_call_verified"] + w["return_path"]*r["return_path"] + w["arg_plausibility"]*r["arg_plausibility"]
        r["final_reward"] = round(max(0.0, min(1.0, base - w["hardcode_penalty"]*r["hardcode_penalty"])), 4)
        return r

# --- 3. Discriminability Test ---
def generate_variants(task):
    entry = task.get("entry_point", "candidate")
    apis = task.get("metadata", {}).get("apis_used", [])
    canonical = task.get("canonical_solution", "")
    good = "import pyAether as pyScript\n\ndef " + entry + "():\n" + canonical
    bad_hc = "import pyAether as pyScript\n\ndef " + entry + "():\n    return True"
    api_py = apis[0].replace("pyAether.", "pyScript.") if apis else "pyScript.unknown"
    bad_nr = "import pyAether as pyScript\n\ndef " + entry + "():\n    " + api_py + "()\n    return None"
    bad_syn = "import pyAether as pyScript\n\ndef " + entry + "():\n    return pyScript."
    parts = apis[0].split(".") if apis else ["pyScript"]
    wrong = ".".join(parts[:-1] + [parts[-1]+"_wrong"]) if len(parts)>=2 else "pyScript.unknown"
    bad_w = "import pyAether as pyScript\n\ndef " + entry + "():\n    return " + wrong.replace("pyAether.","pyScript.") + "()"
    bad_e = "import pyAether as pyScript\n\ndef " + entry + "():\n    pass"
    return {"good": good, "bad_hardcode": bad_hc, "bad_no_return": bad_nr,
            "bad_syntax": bad_syn, "bad_wrong_api": bad_w, "bad_empty": bad_e}

def test_discriminability(tasks, reward_fn):
    vns = ["good", "bad_hardcode", "bad_no_return", "bad_syntax", "bad_wrong_api", "bad_empty"]
    results = {"variants": {vn: {"rewards": []} for vn in vns}, "per_task": [], "summary": {}}
    for task in tasks:
        entry = task.get("entry_point", "candidate")
        apis = task.get("metadata", {}).get("apis_used", [])
        canonical = task.get("canonical_solution", "")
        variants = generate_variants(task)
        tr = {"task_id": task.get("task_id", ""), "variants": {}}
        for vn in vns:
            r = reward_fn.compute(variants[vn], apis, entry, canonical)
            tr["variants"][vn] = r["final_reward"]
            results["variants"][vn]["rewards"].append(r["final_reward"])
        results["per_task"].append(tr)
    for vn in vns:
        rw = results["variants"][vn]["rewards"]
        if rw:
            m = sum(rw)/len(rw)
            results["summary"][vn] = {"mean": round(m,4), "min": round(min(rw),4),
                                       "max": round(max(rw),4), "std": round((sum((x-m)**2 for x in rw)/len(rw))**0.5,4)}
    good_mean = results["summary"].get("good",{}).get("mean",0)
    gaps = {vn: round(good_mean - results["summary"].get(vn,{}).get("mean",0), 4) for vn in vns if vn != "good"}
    results["summary"]["discriminability_gaps"] = gaps
    results["summary"]["verdict"] = "GOOD SEPARATION" if all(g > 0.1 for g in gaps.values()) else ("MODERATE" if any(g > 0.1 for g in gaps.values()) else "POOR (no separation)")
    return results

# --- 4. verl Integration ---
def design_verl_integration():
    return {
        "title": "R117: verl Integration for Execution-Correctness Reward",
        "phase_1_no_sandbox": {
            "description": "Current: sandbox unreachable -> R0++ static only",
            "expected_std0_ratio": "15-25% (vs R0 API coverage: 95%+)",
            "reward_fn": "RewardR0PlusPlus.compute(code, apis, entry, canonical)"
        },
        "phase_2_sandbox_available": {
            "description": "Future: 0.3*R0++ + 0.7*execution_score",
            "execution_score": {"pass": 1.0, "assertion_fail": 0.3, "import_error": 0.1, "runtime_error": 0.05, "timeout": 0.02, "syntax_error": 0.0},
            "pipeline": "R0++ pre-filter -> assembly -> sandbox -> parse -> score -> fallback to R0++"
        },
        "phase_3_local_sandbox": {
            "description": "Ideal: Docker container with pyAether on .17",
            "blocker": "pyAether proprietary, need infra deployment"
        }
    }

# --- 5. Main ---
def main():
    parser = argparse.ArgumentParser(description="R117: Execution-Correctness Reward Architecture")
    parser.add_argument("--mode", choices=["full","connectivity","discriminability","verl"], default="full")
    parser.add_argument("--n-tasks", type=int, default=100)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    sd = os.path.dirname(os.path.abspath(__file__))
    out = args.output or os.path.join(sd, "r117_exec_reward_arch.json")
    print("=" * 70)
    print("R117: Execution-Correctness Reward Architecture")
    print("=" * 70)
    result = {"r117": True, "timestamp": datetime.now().isoformat(), "mode": args.mode}

    if args.mode in ("full", "connectivity"):
        print("\n[1] Sandbox connectivity...")
        conn = check_sandbox_connectivity()
        result["sandbox_connectivity"] = conn
        print("  Verdict: " + conn["verdict"])
        for p in conn["ports_checked"]:
            print("  Port " + str(p["port"]) + ": " + p["status"])

    if args.mode in ("full", "discriminability"):
        print("\n[2] Loading tasks (n=" + str(args.n_tasks) + ")...")
        tp = os.path.join(sd, "rl_pyaether_synth_tasks.jsonl")
        tasks = []
        if os.path.exists(tp):
            with open(tp) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        tasks.append(json.loads(line))
        tasks = tasks[:args.n_tasks]
        print("  Loaded " + str(len(tasks)) + " tasks")
        print("\n[3] R0++ discriminability test...")
        disc = test_discriminability(tasks, RewardR0PlusPlus())
        result["discriminability"] = disc
        print("\n  Summary (mean reward per variant):")
        for vn, stats in disc["summary"].items():
            if isinstance(stats, dict) and "mean" in stats:
                print("    " + vn.ljust(20) + ": mean=" + str(stats["mean"]) + " std=" + str(stats["std"]) + " min=" + str(stats["min"]) + " max=" + str(stats["max"]))
        print("\n  Discriminability gaps:")
        for vn, gap in disc["summary"].get("discriminability_gaps", {}).items():
            print("    good - " + vn.ljust(20) + ": " + str(gap))
        print("\n  Verdict: " + disc["summary"].get("verdict", "N/A"))
        if disc["per_task"]:
            ex = disc["per_task"][0]
            print("\n  Example: " + ex["task_id"])
            for vn, rv in ex["variants"].items():
                print("    " + vn.ljust(20) + ": " + str(rv))

    if args.mode in ("full", "verl"):
        print("\n[4] verl integration...")
        result["verl_integration"] = design_verl_integration()
        print("  Phase 1: R0++ static only")
        print("  Phase 2: 0.3*R0++ + 0.7*execution")
        print("  Phase 3: Local Docker sandbox")

    with open(out, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    print("\n[5] Saved to " + out + " (" + str(os.path.getsize(out)) + " bytes)")
    if "discriminability" in result:
        print("\n" + "=" * 70)
        print("R117 VERDICT: " + result["discriminability"]["summary"].get("verdict", ""))
        print("Sandbox: " + result.get("sandbox_connectivity", {}).get("verdict", "N/A"))
        print("=" * 70)
    return 0

if __name__ == "__main__":
    sys.exit(main())
