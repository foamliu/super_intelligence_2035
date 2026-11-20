#!/usr/bin/env python3
"""baize_posttrain_reward_adversarial_test.py -- R35 adversarial robustness test suite
for reward functions used in verl GRPO training.

Test categories:
  T1: Edge-case inputs (empty, None, garbage, super long, unicode)
  T2: Reward hacking vectors (format-only, hardcoded, token gaming)
  T3: Reward signal properties (variance, range, monotonicity)
  T4: Auto-fallback behavior (R0 switch when sandbox absent)
  T5: Cheat detection edge cases
  T6: Cross-arm consistency

Usage: python baize_posttrain_reward_adversarial_test.py [--api-db PATH] [--verbose]
Exit code: 0 = all pass, 1 = any critical failure.
"""
from __future__ import annotations
import argparse, json, math, os, sys, traceback
from typing import Any, Dict, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from baize_posttrain_reward_functions import (
    compute_score, extract_tool_calls, check_cheat_overlap,
    _extract_ngrams, _init_cheat_tracker,
    reward_r1_binary, reward_r2_partial, reward_r3_tool_penalty,
    reward_r4_api_legality, REWARD_ARMS, FULL_PASS_SCORE,
)

class TestResult:
    def __init__(self, name, category):
        self.name = name; self.category = category
        self.passed = False; self.score = None; self.detail = ""; self.is_critical = False
    def __repr__(self):
        s = f"  {'PASS' if self.passed else 'FAIL'}{' [CRIT]' if self.is_critical else ''} {self.name}"
        if self.score is not None: s += f"  score={self.score:.4f}"
        if self.detail: s += f"  -- {self.detail}"
        return s

class TestSuite:
    def __init__(self, api_db_path="", verbose=False):
        self.results = []; self.api_db_path = api_db_path; self.verbose = verbose
        _init_cheat_tracker()
    def run(self, name, category, fn, critical=False):
        tr = TestResult(name, category); tr.is_critical = critical
        try: fn(tr)
        except Exception as e:
            tr.detail = f"EXCEPTION: {e}"
            if self.verbose: traceback.print_exc()
        self.results.append(tr)
        if self.verbose or not tr.passed: print(tr)
        return tr
    def summary(self):
        total = len(self.results); passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        crit = sum(1 for r in self.results if not r.passed and r.is_critical)
        cats = {}
        for r in self.results:
            k = r.category
            cats[k] = cats.get(k, {"pass":0,"fail":0})
            cats[k]["pass" if r.passed else "fail"] += 1
        return {"total":total,"passed":passed,"failed":failed,"critical_fail":crit,"categories":cats}
    def print_summary(self):
        s = self.summary()
        print(f"\n{'='*70}\n  ADVERSARIAL TEST SUITE SUMMARY (R35)\n{'='*70}")
        print(f"  Total: {s['total']}  Passed: {s['passed']}  Failed: {s['failed']}")
        print(f"  Critical failures: {s['critical_fail']}")
        for cat, c in s["categories"].items():
            print(f"  {cat}: {c['pass']} pass / {c['fail']} fail")
        v = "ALL PASS" if s["failed"]==0 else ("CRITICAL FAIL" if s["critical_fail"]>0 else "NON-CRITICAL FAIL")
        print(f"  Verdict: {v}\n{'='*70}")
        return s["failed"] == 0

# Helper functions
def make_task_meta(apis_used=None, entry_point="call_test_func",
                   canonical="return pyScript.testFunc()", test_code="assert result is not None"):
    apis = apis_used or ["pyAether.testFunc"]
    return {"test_code": test_code, "canonical_solution": canonical,
            "entry_point": entry_point, "metadata": json.dumps({"apis_used": apis})}

def make_sandbox(exec_success=True, assert_results=None, returncode=0):
    return {"exec_success": exec_success, "returncode": returncode, "stdout": "OK",
            "stderr": "", "assert_results": assert_results or [{"passed": True}, {"passed": True}]}

GOOD_CODE = "```python\nimport pyAether as pyScript\n\ndef call_test_func():\n    return pyScript.testFunc()\n```"

# T1: Edge-case inputs
def test_t1_empty(suite):
    def fn(tr):
        s = compute_score("t", "", "", make_task_meta(), arm="R0", auto_fallback=False)
        tr.score = s; tr.passed = 0.0 <= s <= 0.1
    suite.run("T1.1_empty", "T1-EdgeCases", fn, critical=True)

def test_t1_none(suite):
    def fn(tr):
        try:
            s = compute_score("t", None, "", make_task_meta(), arm="R0", auto_fallback=False)
            tr.score = s if isinstance(s, (int,float)) else -999
            tr.passed = isinstance(s, (int,float)) and not math.isnan(s)
        except Exception as e:
            tr.detail = f"Crashed: {e}"
    suite.run("T1.2_none", "T1-EdgeCases", fn, critical=True)

def test_t1_garbage(suite):
    def fn(tr):
        s = compute_score("t", "asdf jkl 12345", "", make_task_meta(), arm="R0", auto_fallback=False)
        tr.score = s; tr.passed = 0.0 <= s <= 0.15
    suite.run("T1.3_garbage", "T1-EdgeCases", fn)

def test_t1_long(suite):
    def fn(tr):
        c = "```python\nimport pyAether as pyScript\n" + "x = 0\n" * 5000 + "\ndef call_test_func():\n    return pyScript.testFunc()\n```"
        s = compute_score("t", c, "", make_task_meta(), arm="R0", auto_fallback=False)
        tr.score = s; tr.passed = 0.0 <= s <= 1.1 and not math.isnan(s)
        tr.detail = f"10k chars R0={s:.4f}"
    suite.run("T1.4_super_long", "T1-EdgeCases", fn, critical=True)

def test_t1_unicode(suite):
    def fn(tr):
        s = compute_score("t", "```python\n# c\ndef call_test_func():\n    return 'h'\n```", "", make_task_meta(), arm="R0", auto_fallback=False)
        tr.score = s; tr.passed = 0.0 <= s <= 1.1 and not math.isnan(s)
    suite.run("T1.5_unicode", "T1-EdgeCases", fn)

def test_t1_no_code(suite):
    def fn(tr):
        s = compute_score("t", "I think use pyAether.", "", make_task_meta(), arm="R0", auto_fallback=False)
        tr.score = s; tr.passed = 0.0 <= s <= 0.5
    suite.run("T1.6_no_code", "T1-EdgeCases", fn)

def test_t1_syntax_err(suite):
    def fn(tr):
        s = compute_score("t", "```python\ndef call_test_func(\n    return pyScript.testFunc(\n```", "", make_task_meta(), arm="R0", auto_fallback=False)
        tr.score = s; tr.passed = 0.0 <= s <= 0.3  # R35 anti-gaming cap
    suite.run("T1.7_syntax_err", "T1-EdgeCases", fn)

# T2: Reward hacking
def test_t2_format_only(suite):
    def fn(tr):
        s = compute_score("t", "```python\npass\n```", "", make_task_meta(), arm="R0", auto_fallback=False)
        tr.score = s; tr.passed = s < 0.3
        tr.detail = f"format-only R0={s:.4f} (expected <0.3)"
    suite.run("T2.1_format_gaming", "T2-RewardHacking", fn, critical=True)

def test_t2_hardcoded(suite):
    def fn(tr):
        e = make_task_meta(test_code="assert result is not None\nassert isinstance(result, bool)")
        s = compute_score("t", "```python\ndef call_test_func():\n    return True\n```", "", e, arm="R0", auto_fallback=False)
        tr.score = s; tr.passed = 0.0 <= s <= 0.7
        tr.detail = f"hardcoded R0={s:.4f} (no API, expected <=0.7)"
    suite.run("T2.2_hardcoded", "T2-RewardHacking", fn, critical=True)

def test_t2_copy_test(suite):
    def fn(tr):
        tc = "import pyAether as pyScript\ndef check(candidate):\n    result = candidate()\n    assert result is not None"
        s = compute_score("t", f"```python\n{tc}\n```", "", make_task_meta(test_code=tc), arm="R0", auto_fallback=False)
        tr.score = s; tr.passed = 0.0 <= s <= 0.8
    suite.run("T2.3_copy_test", "T2-RewardHacking", fn)

def test_t2_excessive(suite):
    def fn(tr):
        calls = "\n".join([f"<function>func_{i}</function>" for i in range(25)])
        r3 = reward_r3_tool_penalty(0.5, extract_tool_calls(calls))
        tr.score = r3; tr.passed = r3 < 0.5
    suite.run("T2.4_excessive_calls", "T2-RewardHacking", fn, critical=True)

def test_t2_zero_calls(suite):
    def fn(tr):
        r3 = reward_r3_tool_penalty(0.5, [])
        tr.score = r3; tr.passed = r3 < 0.5
    suite.run("T2.5_zero_calls", "T2-RewardHacking", fn)

def test_t2_hallucinated(suite):
    def fn(tr):
        if not suite.api_db_path:
            tr.passed = True; tr.detail = "Skipped: no API DB"; return
        r4 = reward_r4_api_legality(0.5, ["fakeApi123", "nonExist456"], suite.api_db_path)
        tr.score = r4; tr.passed = r4 < 0.5
    suite.run("T2.6_hallucinated_R4", "T2-RewardHacking", fn, critical=True)

# T3: Signal properties
def test_t3_range(suite):
    def fn(tr):
        good = make_sandbox(assert_results=[{"passed": True}]*3)
        bad = make_sandbox(exec_success=False)
        meta = make_task_meta()
        ok = True
        for arm in sorted(REWARD_ARMS):
            if arm == "R0":
                sg = compute_score("t", GOOD_CODE, "", meta, arm="R0", auto_fallback=False)
                sb = compute_score("t", "", "", meta, arm="R0", auto_fallback=False)
            else:
                sg = compute_score("t", GOOD_CODE, "", good, arm=arm, auto_fallback=False)
                sb = compute_score("t", GOOD_CODE, "", bad, arm=arm, auto_fallback=False)
            for s in [sg, sb]:
                if not (0.0 <= s <= 1.1) or (isinstance(s, float) and math.isnan(s)): ok = False
        tr.passed = ok
    suite.run("T3.1_range_all_arms", "T3-SignalProps", fn, critical=True)

def test_t3_variance(suite):
    def fn(tr):
        extra = make_task_meta()
        resps = [GOOD_CODE,
                 "```python\nimport pyAether as pyScript\n\ndef call_test_func():\n    x = pyScript.testFunc\n    return x\n```",
                 "```python\ndef call_test_func():\n    return wrongApi()\n```",
                 "", "I don't know"]
        scores = [compute_score("t", r, "", extra, arm="R0", auto_fallback=False) for r in resps]
        m = sum(scores)/len(scores)
        std = math.sqrt(sum((s-m)**2 for s in scores)/len(scores))
        tr.score = std; tr.passed = std > 0.05
        tr.detail = f"R0 std={std:.4f} scores={[f'{s:.3f}' for s in scores]}"
    suite.run("T3.2_variance_R0", "T3-SignalProps", fn, critical=True)

def test_t3_mono(suite):
    def fn(tr):
        extra = make_task_meta()
        resp = ["", "I don't know",
                "```python\ndef call_test_func():\n    return True\n```", GOOD_CODE]
        scores = [compute_score("t", r, "", extra, arm="R0", auto_fallback=False) for r in resp]
        mono = all(scores[i] <= scores[i+1]+0.05 for i in range(len(scores)-1))
        tr.passed = mono and scores[-1] > scores[0]
        tr.detail = f"scores={[f'{s:.3f}' for s in scores]} mono={mono}"
    suite.run("T3.3_monotonicity", "T3-SignalProps", fn, critical=True)

def test_t3_r1_binary(suite):
    def fn(tr):
        full = make_sandbox(assert_results=[{"passed": True}]*2)
        part = make_sandbox(assert_results=[{"passed": True}, {"passed": False}])
        fail = make_sandbox(exec_success=False)
        sf, sp, sfl = reward_r1_binary(full), reward_r1_binary(part), reward_r1_binary(fail)
        tr.passed = sf == FULL_PASS_SCORE and sp == 0.0 and sfl == 0.0
        tr.detail = f"R1: full={sf} partial={sp} fail={sfl}"
    suite.run("T3.4_R1_binary", "T3-SignalProps", fn)

def test_t3_r2_grad(suite):
    def fn(tr):
        results = []
        for np_ in range(5):
            asserts = [{"passed": True}]*np_ + [{"passed": False}]*(4-np_)
            results.append(reward_r2_partial(make_sandbox(assert_results=asserts)))
        inc = all(results[i] <= results[i+1] for i in range(len(results)-1))
        distinct = len(set(round(r, 4) for r in results))
        tr.passed = inc and distinct >= 3
        tr.detail = f"R2: {[f'{r:.3f}' for r in results]} distinct={distinct}"
    suite.run("T3.5_R2_graduated", "T3-SignalProps", fn, critical=True)

# T4: Auto-fallback
def test_t4_autofb(suite):
    def fn(tr):
        s_fb = compute_score("t", GOOD_CODE, "", make_task_meta(), arm="R2", auto_fallback=True)
        s_no = compute_score("t", GOOD_CODE, "", make_task_meta(), arm="R2", auto_fallback=False)
        tr.score = s_fb; tr.passed = s_fb > 0.0 and s_no == 0.0
        tr.detail = f"autofb={s_fb:.4f}(>0) nofb={s_no:.4f}(=0)"
    suite.run("T4.1_autofallback", "T4-AutoFallback", fn, critical=True)

def test_t4_nofb_zero(suite):
    def fn(tr):
        s = compute_score("t", "code", "", make_task_meta(), arm="R2", auto_fallback=False)
        tr.score = s; tr.passed = s == 0.0
    suite.run("T4.2_nofb_zero", "T4-AutoFallback", fn)

def test_t4_fb_not_trig(suite):
    def fn(tr):
        s = compute_score("t", GOOD_CODE, "", make_sandbox(assert_results=[{"passed": True}]*2), arm="R2", auto_fallback=True)
        tr.score = s; tr.passed = s > 0.0
        tr.detail = f"R2+sandbox+autofb={s:.4f} (should use R2 not R0)"
    suite.run("T4.3_no_fb_with_sandbox", "T4-AutoFallback", fn, critical=True)

# T5: Cheat detection
def test_t5_empty_ng(suite):
    def fn(tr):
        ic, r, c = check_cheat_overlap("text", None)
        tr.passed = ic == False and r == 0.0 and c == 0
    suite.run("T5.1_empty_ngrams", "T5-CheatDetect", fn, critical=True)

def test_t5_empty_sol(suite):
    def fn(tr):
        ng = _extract_ngrams("assert result is not None", 8)
        ic, r, c = check_cheat_overlap("", ng)
        tr.passed = ic == False
    suite.run("T5.2_empty_solution", "T5-CheatDetect", fn)

def test_t5_exact_copy(suite):
    def fn(tr):
        t = "import pyAether as pyScript\ndef check(candidate):\n    result = candidate()\n    assert result is not None"
        ng = _extract_ngrams(t, 8)
        ic, r, c = check_cheat_overlap(t, ng)
        tr.passed = ic == True and r > 0.8
        tr.detail = f"exact copy: cheat={ic} ratio={r:.4f}"
    suite.run("T5.3_exact_copy", "T5-CheatDetect", fn, critical=True)

def test_t5_clean(suite):
    def fn(tr):
        t = "import pyAether as pyScript\ndef check(candidate):\n    result = candidate()\n    assert result is not None"
        ng = _extract_ngrams(t, 8)
        clean = "```python\ndef my_func():\n    data = process_input()\n    return transform(data)\n```"
        ic, r, c = check_cheat_overlap(clean, ng)
        tr.passed = ic == False
    suite.run("T5.4_clean_not_flagged", "T5-CheatDetect", fn, critical=True)

def test_t5_short(suite):
    def fn(tr):
        ng = _extract_ngrams("ab", 8)
        tr.passed = len(ng) == 1 and "ab" in ng
    suite.run("T5.5_short_text", "T5-CheatDetect", fn)

# T6: Cross-arm
def test_t6_full_pass(suite):
    def fn(tr):
        extra = {**make_task_meta(), **make_sandbox(assert_results=[{"passed": True}]*3)}
        scores = {}
        for arm in ["R1","R2","R3","R4"]:
            kw = {"api_database": suite.api_db_path} if suite.api_db_path and arm=="R4" else {}
            scores[arm] = compute_score("t", GOOD_CODE, "", extra, arm=arm, auto_fallback=False, **kw)
        tr.passed = all(s >= 0.8 for s in scores.values())
        tr.detail = f"{', '.join(f'{k}={v:.3f}' for k,v in scores.items())}"
    suite.run("T6.1_full_pass_high", "T6-CrossArm", fn)

def test_t6_total_fail(suite):
    def fn(tr):
        extra = make_sandbox(exec_success=False)
        scores = {}
        for arm in ["R1","R2","R3","R4"]:
            kw = {"api_database": suite.api_db_path} if suite.api_db_path and arm=="R4" else {}
            scores[arm] = compute_score("t", "```python\ndef f(): pass\n```", "", extra, arm=arm, auto_fallback=False, **kw)
        tr.passed = all(s == 0.0 for s in scores.values())
    suite.run("T6.2_total_fail_zero", "T6-CrossArm", fn)

def test_t6_r3_vs_r2(suite):
    def fn(tr):
        extra = make_sandbox(assert_results=[{"passed": True}]*2)
        code = "```python\ndef f():\n    return 42\n```"
        r2 = compute_score("t", code, "", extra, arm="R2", auto_fallback=False)
        r3 = compute_score("t", code, "", extra, arm="R3", auto_fallback=False)
        tr.passed = r3 <= r2
        tr.detail = f"R2={r2:.4f} R3={r3:.4f}"
    suite.run("T6.3_R3_le_R2", "T6-CrossArm", fn)

def main():
    parser = argparse.ArgumentParser(description="R35 adversarial reward test")
    parser.add_argument("--api-db", default=os.path.expanduser(
        "~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json"))
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    api_db = args.api_db if os.path.exists(args.api_db) else ""
    suite = TestSuite(api_db_path=api_db, verbose=args.verbose)
    print(f"\n{'='*70}\n  R35 Adversarial Reward Function Test Suite\n  API DB: {api_db or '(not found)'}\n{'='*70}\n")
    print("--- T1: Edge-case inputs ---")
    test_t1_empty(suite); test_t1_none(suite); test_t1_garbage(suite)
    test_t1_long(suite); test_t1_unicode(suite); test_t1_no_code(suite); test_t1_syntax_err(suite)
    print("\n--- T2: Reward hacking ---")
    test_t2_format_only(suite); test_t2_hardcoded(suite); test_t2_copy_test(suite)
    test_t2_excessive(suite); test_t2_zero_calls(suite); test_t2_hallucinated(suite)
    print("\n--- T3: Signal properties ---")
    test_t3_range(suite); test_t3_variance(suite); test_t3_mono(suite)
    test_t3_r1_binary(suite); test_t3_r2_grad(suite)
    print("\n--- T4: Auto-fallback ---")
    test_t4_autofb(suite); test_t4_nofb_zero(suite); test_t4_fb_not_trig(suite)
    print("\n--- T5: Cheat detection ---")
    test_t5_empty_ng(suite); test_t5_empty_sol(suite); test_t5_exact_copy(suite)
    test_t5_clean(suite); test_t5_short(suite)
    print("\n--- T6: Cross-arm ---")
    test_t6_full_pass(suite); test_t6_total_fail(suite); test_t6_r3_vs_r2(suite)
    all_pass = suite.print_summary()
    results_json = {
        "test_suite": "R35_adversarial_reward_test",
        "timestamp": "2026-11-08",
        "api_db_available": bool(api_db),
        "summary": suite.summary(),
        "results": [{"name": r.name, "category": r.category, "passed": r.passed,
                      "score": r.score, "detail": r.detail, "critical": r.is_critical}
                     for r in suite.results],
    }
    out = os.path.join(SCRIPT_DIR, "baize_posttrain_reward_adversarial_results.json")
    with open(out, "w") as f:
        json.dump(results_json, f, indent=2, ensure_ascii=False)
    print(f"\n  Results JSON: {out}")
    sys.exit(0 if all_pass else 1)

if __name__ == "__main__":
    main()
