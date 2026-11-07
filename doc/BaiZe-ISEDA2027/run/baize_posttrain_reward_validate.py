#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baize_posttrain_reward_validate.py — R29: Comprehensive reward function validation.

Tests all 5 reward arms (R0-R4) with synthetic test cases.
R29 (2026-11-08): Zero-GPU validation before 11/9 GPU arrival.
"""
import json, os, sys, time
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from baize_posttrain_reward_functions import (
    compute_score, extract_tool_calls, check_cheat_overlap,
    get_cheat_rate_report, REWARD_ARMS,
)

API_DB = os.path.expanduser("~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json")


SANDBOX_CASES = [
    {"name": "full_pass", "desc": "Exec success + all assertions pass",
     "solution_str": "```python\nimport pyAether as pyScript\nresult = pyScript.get_cell_by_id('cell1')\nprint(result)\n```",
     "ground_truth": "assert result is not None",
     "extra_info": {"exec_success": True, "returncode": 0, "stdout": "ok", "stderr": "",
                    "assert_results": [{"passed": True, "name": "t1"}], "tool_results": [{"response": "ok"}]},
     "expected": {"R1": 1.0, "R2": 1.02}},
    {"name": "partial_pass_2of3", "desc": "Exec success + 2/3 assertions pass",
     "solution_str": "```python\nimport pyAether as pyScript\nresult = pyScript.get_cell_by_id('cell1')\n```",
     "ground_truth": "assert isinstance(result, dict)",
     "extra_info": {"exec_success": True, "returncode": 0, "stdout": "", "stderr": "",
                    "assert_results": [{"passed": True}, {"passed": True}, {"passed": False}],
                    "tool_results": []},
     "expected": {"R1": 0.0, "R2": 0.62}},
    {"name": "exec_failure", "desc": "Exec failure -> R1/R2=0",
     "solution_str": "```python\nimport pyAether as pyScript\nresult = pyScript.nonexistent_api()\n```",
     "ground_truth": "assert result is not None",
     "extra_info": {"exec_success": False, "returncode": 1, "stdout": "", "stderr": "AttributeError",
                    "assert_results": [], "tool_results": []},
     "expected": {"R1": 0.0, "R2": 0.0}},
    {"name": "no_code_garbage", "desc": "No code, garbage response",
     "solution_str": "I don't know how to solve this.",
     "ground_truth": "assert result is not None",
     "extra_info": {"exec_success": False, "returncode": 1, "stdout": "", "stderr": "No code",
                    "assert_results": [], "tool_results": []},
     "expected": {"R1": 0.0, "R2": 0.0}},
    {"name": "xml_tool_calls", "desc": "XML-format tool calls + exec success",
     "solution_str": "<function>get_cell_by_id</function><param>cell1</param>\n```python\nresult = pyScript.get_cell_by_id('cell1')\nassert result is not None\n```",
     "ground_truth": "assert result is not None",
     "extra_info": {"exec_success": True, "returncode": 0, "stdout": "ok", "stderr": "",
                    "assert_results": [{"passed": True, "name": "t1"}], "tool_results": [{"response": "ok"}]},
     "expected": {"R2": 1.02}},
]

R0_CASES = [
    {"name": "r0_good_code", "desc": "Valid syntax + correct API + entry point match",
     "solution_str": "```python\nimport pyAether as pyScript\n\ndef call_aesesavenethighlight():\n    return pyScript.aeSeSaveNetHighlight()\n```",
     "ground_truth": "",
     "extra_info": {"test_code": "import pyAether as pyScript\ndef check(candidate):\n    result = candidate()\n    assert result is not None",
                   "canonical_solution": "    return pyScript.aeSeSaveNetHighlight()",
                   "entry_point": "call_aesesavenethighlight",
                   "metadata": json.dumps({"apis_used": ["pyAether.aeSeSaveNetHighlight"]})}},
    {"name": "r0_syntax_error", "desc": "Syntax error -> R0 syntax=0",
     "solution_str": "```python\ndef call_aesesavenethighlight(\n    return pyScript.aeSeSaveNetHighlight(\n```",
     "ground_truth": "",
     "extra_info": {"test_code": "assert result is not None",
                   "canonical_solution": "return pyScript.aeSeSaveNetHighlight()",
                   "entry_point": "call_aesesavenethighlight",
                   "metadata": json.dumps({"apis_used": ["pyAether.aeSeSaveNetHighlight"]})}},
    {"name": "r0_wrong_api", "desc": "Wrong API name -> R0 API=0",
     "solution_str": "```python\nimport pyAether as pyScript\n\ndef call_aesesavenethighlight():\n    return pyScript.wrongApiName()\n```",
     "ground_truth": "",
     "extra_info": {"test_code": "assert isinstance(result, bool)",
                   "canonical_solution": "return pyScript.aeSeSaveNetHighlight()",
                   "entry_point": "call_aesesavenethighlight",
                   "metadata": json.dumps({"apis_used": ["pyAether.aeSeSaveNetHighlight"]})}},
    {"name": "r0_garbage", "desc": "No code at all -> R0=0",
     "solution_str": "I don't know how to solve this.",
     "ground_truth": "",
     "extra_info": {"test_code": "assert result is not None",
                   "canonical_solution": "return pyScript.aeSeSaveNetHighlight()",
                   "entry_point": "call_aesesavenethighlight",
                   "metadata": json.dumps({"apis_used": ["pyAether.aeSeSaveNetHighlight"]})}},
]

R3R4_CASES = [
    {"name": "r4_hallucinated_api", "desc": "Hallucinated API -> R4 penalty",
     "solution_str": "```python\nimport pyAether as pyScript\nresult = pyScript.FakeAPI_xyz123()\nassert result is not None\n```",
     "ground_truth": "assert result is not None",
     "extra_info": {"exec_success": True, "returncode": 0, "stdout": "ok", "stderr": "",
                    "assert_results": [{"passed": True, "name": "t1"}], "tool_results": []}},
    {"name": "r3_excessive_tool_calls", "desc": "25 tool calls -> R3 excessive penalty",
     "solution_str": "\n".join([f"pyScript.get_cell_by_id('c{i}')" for i in range(25)]) + "\n```python\nresult = True\nassert result\n```",
     "ground_truth": "assert result",
     "extra_info": {"exec_success": True, "returncode": 0, "stdout": "", "stderr": "",
                    "assert_results": [{"passed": True, "name": "t1"}], "tool_results": []}},
    {"name": "r3_zero_tool_calls", "desc": "0 tool calls, exec success -> R3 zero penalty",
     "solution_str": "```python\nresult = 42\nassert result == 42\n```",
     "ground_truth": "assert result == 42",
     "extra_info": {"exec_success": True, "returncode": 0, "stdout": "", "stderr": "",
                    "assert_results": [{"passed": True, "name": "t1"}], "tool_results": []}},
]


def run_validation():
    results = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "arms_tested": sorted(REWARD_ARMS), "cases": []}
    print("=" * 70)
    print("R29 Reward Function Validation — All Arms (R0-R4)")
    print("=" * 70)
    print(f"API DB: {API_DB} ({'exists' if os.path.exists(API_DB) else 'MISSING'})")
    print()

    # Test sandbox cases with R0-R4 (force arm, no fallback)
    for tc in SANDBOX_CASES:
        cr = {"name": tc["name"], "desc": tc["desc"], "type": "sandbox", "scores": {}}
        print(f"  [{tc['name']}] {tc['desc']}")
        for arm in ["R0", "R1", "R2", "R3", "R4"]:
            kw = {"arm": arm, "auto_fallback": False, "api_database": API_DB}
            sc = compute_score("pyaether_synth_v2", tc["solution_str"], tc["ground_truth"], tc["extra_info"], **kw)
            cr["scores"][arm] = round(sc, 4)
            print(f"    {arm}: {sc:.4f}")
        for ea, es in tc.get("expected", {}).items():
            act = cr["scores"].get(ea)
            if act is not None:
                ok = abs(act - es) < 0.05
                cr.setdefault("checks", {})[ea] = {"expected": es, "actual": act, "pass": ok}
                print(f"    {'OK' if ok else 'WARN'} expected {ea}={es:.2f} got {act:.4f}")
        print()
        results["cases"].append(cr)

    # R0 skeleton cases (no sandbox -> auto-fallback)
    print("-" * 70)
    print("R0 Skeleton-Mode Cases (no sandbox -> auto-fallback)")
    print("-" * 70)
    for tc in R0_CASES:
        cr = {"name": tc["name"], "desc": tc["desc"], "type": "r0_skeleton", "scores": {}}
        print(f"  [{tc['name']}] {tc['desc']}")
        for arm in ["R0", "R2"]:
            kw = {"arm": arm, "api_database": API_DB}
            sc = compute_score("pyaether_synth_v2", tc["solution_str"], tc["ground_truth"], tc["extra_info"], **kw)
            cr["scores"][arm] = round(sc, 4)
            print(f"    {arm}: {sc:.4f}")
        print()
        results["cases"].append(cr)

    # R3/R4 edge cases
    print("-" * 70)
    print("R3/R4 Edge Cases")
    print("-" * 70)
    for tc in R3R4_CASES:
        cr = {"name": tc["name"], "desc": tc["desc"], "type": "r3r4_edge", "scores": {}}
        print(f"  [{tc['name']}] {tc['desc']}")
        for arm in ["R2", "R3", "R4"]:
            kw = {"arm": arm, "auto_fallback": False, "api_database": API_DB}
            sc = compute_score("pyaether_synth_v2", tc["solution_str"], tc["ground_truth"], tc["extra_info"], **kw)
            cr["scores"][arm] = round(sc, 4)
            calls = extract_tool_calls(tc["solution_str"])
            print(f"    {arm}: {sc:.4f} (tool_calls={len(calls)})")
        print()
        results["cases"].append(cr)

    # Auto-fallback test
    print("-" * 70)
    print("Auto-Fallback Test (arm=R2, no sandbox -> should fallback to R0)")
    print("-" * 70)
    ns_info = {"test_code": "assert result is not None",
               "canonical_solution": "return pyScript.aeSeSaveNetHighlight()",
               "entry_point": "call_aesesavenethighlight",
               "metadata": json.dumps({"apis_used": ["pyAether.aeSeSaveNetHighlight"]})}
    good = "```python\nimport pyAether as pyScript\n\ndef call_aesesavenethighlight():\n    return pyScript.aeSeSaveNetHighlight()\n```"
    sf = compute_score("t", good, "", ns_info, arm="R2", api_database=API_DB)
    sff = compute_score("t", good, "", ns_info, arm="R2", auto_fallback=False, api_database=API_DB)
    s0 = compute_score("t", good, "", ns_info, arm="R0", api_database=API_DB)
    print(f"  R2 auto_fallback=True  -> {sf:.4f} (should==R0)")
    print(f"  R2 auto_fallback=False -> {sff:.4f} (should==0.0)")
    print(f"  R0                     -> {s0:.4f}")
    fb_ok = abs(sf - s0) < 0.01
    fz_ok = sff == 0.0
    print(f"  Fallback matches R0: {fb_ok}")
    print(f"  Forced R2 no sandbox =0: {fz_ok}")
    results["auto_fallback"] = {"fallback_score": round(sf,4), "forced_score": round(sff,4),
                                "r0_score": round(s0,4), "fallback_matches_r0": fb_ok, "forced_is_zero": fz_ok}
    print()

    # Cheat rate test
    print("-" * 70)
    print("Cheat Rate Tracking Test")
    print("-" * 70)
    eval_ng = {"assert result is not None", "import pyAether as pyS", "pyScript.aeSeSaveNetH"}
    cheat_sol = "assert result is not None\nimport pyAether as pyScript\npyScript.aeSeSaveNetHighlight()"
    clean_sol = "result = 42\nprint(result)"
    isc, ovr, ovc = check_cheat_overlap(cheat_sol, eval_ng, ngram_size=10)
    iscl, _, _ = check_cheat_overlap(clean_sol, eval_ng, ngram_size=10)
    print(f"  Cheat sol: is_cheat={isc}, overlap_ratio={ovr:.4f}, count={ovc}")
    print(f"  Clean sol: is_cheat={iscl}")
    results["cheat_rate"] = {"cheat_is_cheat": isc, "cheat_overlap": round(ovr,4),
                             "clean_is_cheat": iscl, "report": get_cheat_rate_report()}
    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    tc_count = len(results["cases"])
    all5 = len(results["arms_tested"]) == 5
    print(f"  Total test cases: {tc_count}")
    print(f"  All 5 arms tested: {all5}")
    print(f"  Auto-fallback works: {fb_ok}")
    print(f"  Cheat detection works: {isc}")
    results["summary"] = {"total_cases": tc_count, "all_arms_tested": all5,
                          "auto_fallback_works": fb_ok, "forced_no_sandbox_is_zero": fz_ok,
                          "cheat_detection_works": isc}

    out = "/tmp/pt_r29_reward_validation.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n  JSON output: {out}")
    return results

if __name__ == "__main__":
    run_validation()
