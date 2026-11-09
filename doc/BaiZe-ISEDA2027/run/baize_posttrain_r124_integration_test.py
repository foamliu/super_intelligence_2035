#!/usr/bin/env python3
"""baize_posttrain_r124_integration_test.py -- R124 dotted-path fix integration test.

R124 (2026-11-10): Validates the complete pipeline after the class.method
dotted-path mapping fix.

Surrogate RL results are NOT transferable to BaiZe.
"""
from __future__ import annotations

import asyncio, json, os, re, sys, time
from typing import Any, Dict, List

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

RESULTS: List[Dict[str, Any]] = []

def record(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    RESULTS.append({"name": name, "status": status, "detail": detail})
    print(f"  [{status}] {name}" + (f" -- {detail}" if detail else ""))

def test_extract_dotted_path():
    print("\n" + "=" * 70)
    print("Test 1: _extract_dotted_path() dotted-path reconstruction")
    print("=" * 70)
    import ast
    from baize_posttrain_eda_tool_v3 import EDARunCodeTool
    cases = [
        ("pyScript.emyDesign.setCp()", "emyDesign.setCp"),
        ("pyScript.aeGetCurDesign()", "aeGetCurDesign"),
        ("pyAether.emyDesign.setCp()", "emyDesign.setCp"),
        ("print('hello')", "print"),
        ("pyScript.emyCell.getCellName()", "emyCell.getCellName"),
        ("pyScript.aeGetCVIdByDa('lib', 'cell')", "aeGetCVIdByDa"),
    ]
    all_pass = True
    for code, expected in cases:
        tree = ast.parse(code)
        call_node = next((n for n in ast.walk(tree) if isinstance(n, ast.Call)), None)
        if call_node is None:
            record(f"dotted_path('{code[:30]}')", False, "No Call node")
            all_pass = False
            continue
        result = EDARunCodeTool._extract_dotted_path(call_node.func)
        ok = result == expected
        record(f"dotted_path('{code[:40]}') -> '{result}'", ok, f"expected '{expected}'" if not ok else "")
        if not ok: all_pass = False
    return all_pass

def test_reward_regex():
    print("\n" + "=" * 70)
    print("Test 3: _PYTHON_API_PATTERN dotted-path capture")
    print("=" * 70)
    from baize_posttrain_reward_functions import _PYTHON_API_PATTERN, extract_tool_calls
    cases = [
        ("pyScript.emyDesign.setCp()", "emyDesign.setCp"),
        ("pyScript.aeGetCurDesign()", "aeGetCurDesign"),
        ("pyAether.emyCell.getCellName()", "emyCell.getCellName"),
        ("pyScript.aeGetCVIdByDa('a', 'b')", "aeGetCVIdByDa"),
    ]
    all_pass = True
    for text, expected in cases:
        m = _PYTHON_API_PATTERN.search(text)
        if m:
            result = m.group(1)
            ok = result == expected
            record(f"regex('{text[:40]}') -> '{result}'", ok, f"expected '{expected}'" if not ok else "")
            if not ok: all_pass = False
        else:
            record(f"regex('{text[:40]}')", False, "No match")
            all_pass = False
    combined = ("import pyAether as pyScript\ndesign = pyScript.emyDesign.setCp()\ncell = pyScript.aeGetCurDesign()\n")
    calls = extract_tool_calls(combined)
    has_dotted = any("." in c for c in calls)
    record("extract_tool_calls captures dotted", has_dotted, f"calls={calls}")
    if not has_dotted: all_pass = False
    return all_pass

def test_reward_r0_dotted():
    print("\n" + "=" * 70)
    print("Test 4: reward_r0_skeleton with dotted-path code")
    print("=" * 70)
    from baize_posttrain_reward_functions import reward_r0_skeleton
    extra_info = {
        "test_code": "def check(c):\n    r = c()\n    assert r is not None",
        "canonical_solution": "import pyAether as pyScript\ndef solution():\n    return pyScript.aeGetCurDesign()",
        "entry_point": "solution",
        "metadata": json.dumps({"apis_used": ["aeGetCurDesign"], "assertion_template": "T1_type_check"}),
    }
    good_resp = "```python\nimport pyAether as pyScript\ndef solution():\n    return pyScript.aeGetCurDesign()\n```\n"
    score_good = reward_r0_skeleton(good_resp, extra_info)
    bad_resp = "I don't know how to solve this."
    score_bad = reward_r0_skeleton(bad_resp, extra_info)
    record("R0 good response > 0.3", score_good > 0.3, f"score={score_good:.4f}")
    record("R0 bad < good", score_bad < score_good, f"bad={score_bad:.4f} < good={score_good:.4f}")
    return score_good > 0.3 and score_bad < score_good

def test_v3_config():
    print("\n" + "=" * 70)
    print("Test 5: v3 verl config validation")
    print("=" * 70)
    try:
        import yaml
    except ImportError:
        record("yaml import", False, "PyYAML not available")
        return False
    cfg_path = os.path.join(_SCRIPT_DIR, "baize_posttrain_rl_verl_config_v3.yaml")
    with open(cfg_path, "r") as f:
        cfg = yaml.safe_load(f)
    rfn = cfg.get("custom_reward_function", {})
    mt = cfg.get("actor_rollout_ref", {}).get("rollout", {}).get("multi_turn", {})
    checks = [
        ("reward path", rfn.get("path") == "baize_posttrain_reward_functions.py"),
        ("reward arm R0", rfn.get("reward_kwargs", {}).get("arm") == "R0"),
        ("multi_turn enabled", mt.get("enable") is True),
        ("max_turns >= 4", mt.get("max_turns", 0) >= 4),
        ("tool_config v3", mt.get("tool_config_path") == "baize_posttrain_tool_config_v3.yaml"),
        ("format chatml", mt.get("format") == "chatml"),
        ("tool_config file exists", os.path.exists(os.path.join(_SCRIPT_DIR, "baize_posttrain_tool_config_v3.yaml"))),
    ]
    all_pass = True
    for name, ok in checks:
        record(name, ok)
        if not ok: all_pass = False
    return all_pass

async def test_static_analysis_dotted():
    print("\n" + "=" * 70)
    print("Test 2: _static_analysis() dotted-path KB verification")
    print("=" * 70)
    from baize_posttrain_eda_tool_v3 import EDARunCodeTool
    tool = EDARunCodeTool(
        config={"sandbox_endpoint": "", "max_code_length": 10000, "timeout": 30, "tier": 3},
        tool_schema={"type": "function", "function": {"name": "run_code"}})
    cases = [
        ("import pyAether as pyScript\ndesign = pyScript.emyDesign.setCp()\nprint(design)\n", "dotted: emyDesign.setCp", True, True),
        ("import pyAether as pyScript\ncell = pyScript.aeGetCurDesign()\nprint(cell)\n", "single: aeGetCurDesign", True, True),
        ("def foo(\n  # syntax error", "syntax error", False, False),
    ]
    all_pass = True
    for code, desc, expect_syntax, expect_verified in cases:
        result = tool._static_analysis(code)
        syntax_ok = result.get("syntax_ok", False)
        apis_verified = result.get("apis_verified", [])
        legality = result.get("api_legality", 0)
        if syntax_ok != expect_syntax:
            record(f"static('{desc}') syntax", False, f"got {syntax_ok}, expected {expect_syntax}")
            all_pass = False
        else:
            record(f"static('{desc}') syntax", True)
        if expect_syntax and expect_verified:
            if len(apis_verified) > 0:
                record(f"static('{desc}') API verified (R124 fix)", True, f"verified={apis_verified}, legality={legality:.2f}")
            else:
                record(f"static('{desc}') API verified (R124 fix)", False, f"verified=[] (BUG: should find APIs)")
                all_pass = False
    return all_pass

async def test_e2e_pipeline():
    print("\n" + "=" * 70)
    print("Test 6: End-to-end pipeline (tool -> static analysis -> reward)")
    print("=" * 70)
    from baize_posttrain_eda_tool_v3 import EDARunCodeTool
    from baize_posttrain_reward_functions import reward_r0_skeleton
    model_code = (
        "import pyAether as pyScript\n"
        "def solution():\n"
        "    design = pyScript.emyDesign.setCp()\n"
        "    cell = pyScript.aeGetCurDesign()\n"
        "    return cell\n")
    tool = EDARunCodeTool(
        config={"sandbox_endpoint": "", "max_code_length": 10000, "timeout": 30, "tier": 3},
        tool_schema={"type": "function", "function": {"name": "run_code"}})
    iid = await tool.create(instance_id="e2e-001")
    resp, rew, meta = await tool.execute(iid, {"code": model_code})
    sr = json.loads(resp)
    record("e2e: syntax OK", sr.get("syntax_ok", False))
    record("e2e: apis_verified non-empty (R124)", len(sr.get("apis_verified", [])) > 0, f"verified={sr.get('apis_verified', [])}")
    record("e2e: api_legality > 0 (R124)", sr.get("api_legality", 0) > 0, f"legality={sr.get('api_legality', 0):.2f}")
    extra_info = {
        "test_code": "def check(c):\n    r = c()\n    assert r is not None",
        "canonical_solution": "import pyAether as pyScript\ndef solution():\n    return pyScript.aeGetCurDesign()",
        "entry_point": "solution",
        "metadata": json.dumps({"apis_used": ["aeGetCurDesign"], "assertion_template": "T1_type_check"}),
    }
    reward = reward_r0_skeleton(model_code, extra_info)
    record("e2e: R0 reward > 0.3", reward > 0.3, f"reward={reward:.4f}")
    await tool.release(iid)
    return sr.get("syntax_ok", False) and len(sr.get("apis_verified", [])) > 0 and reward > 0.3

async def main():
    print("=" * 70)
    print("R124 Integration Test -- Dotted-Path API Mapping Fix")
    print("=" * 70)
    t0 = time.time()
    results = []
    results.append(("dotted_path_extraction", test_extract_dotted_path()))
    results.append(("static_analysis_dotted", await test_static_analysis_dotted()))
    results.append(("reward_regex", test_reward_regex()))
    results.append(("reward_r0_dotted", test_reward_r0_dotted()))
    results.append(("v3_config", test_v3_config()))
    results.append(("e2e_pipeline", await test_e2e_pipeline()))
    elapsed = round(time.time() - t0, 2)
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["status"] == "PASS")
    for r in RESULTS:
        print(f"  [{r['status']}] {r['name']}" + (f" -- {r['detail']}" if r["detail"] else ""))
    print(f"\n  {passed}/{total} checks passed")
    print(f"  Elapsed: {elapsed}s")
    all_ok = all(ok for _, ok in results)
    if all_ok:
        print("\n  ALL TEST GROUPS PASSED -- R124 integration verified")
    else:
        print(f"\n  FAILED groups: {[n for n, ok in results if not ok]}")
    print("=" * 70)
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
