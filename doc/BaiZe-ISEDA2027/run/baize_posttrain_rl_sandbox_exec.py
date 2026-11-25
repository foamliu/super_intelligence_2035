#!/usr/bin/env python3
"""baize_posttrain_rl_sandbox_exec.py -- EDA sandbox execution client for the
self-written GRPO loop (baize_posttrain_rl_grpo_loop.py).

PURPOSE (R415, 2026-11-13):
  The R0 reward arm uses static analysis (no sandbox) and is already running.
  Arms R1-R4 require real execution results -- exec_success + per-assertion
  assert_results -- to be populated in extra_info before compute_score is
  called.  Without them, compute_score auto-falls back to R0 (see
  baize_posttrain_reward_functions.py _has_sandbox_results).

  This module is the bridge: for each generated rollout it (1) builds a test
  script from the model output + the task test_code/entry_point, (2) POSTs it
  to the EDA sandbox run_code HTTP endpoint (reached via the dual-nix-tunnel:
  .17 localhost:8664 -> 36.15 -> 10.129.32.75), (3) parses the response into
  the {exec_success, assert_results, stdout, stderr, returncode} dict that
  compute_score expects.

  Assertion instrumentation (R2 partial credit): the task test_code defines a
  check(candidate) function whose body is a sequence of assert statements that
  share local state (result = candidate()).  To obtain per-assertion pass/fail
  in a SINGLE sandbox call (sandbox latency is the bottleneck), we AST-transform
  each assert inside check into a try/except that appends to a result list, then
  print a JSON marker that we scrape from print_log.  This avoids N sandbox
  round-trips per rollout.

  Endpoint pool: the tunnel forwards 4 ports (8664/8665/8653/8669) each bound
  to an independent sandbox workdir -> no cross-contamination; we rotate across
  them so concurrent rollouts do not queue on one port.

  Surrogate RL results (MiniCPM5-2B) are NOT transferable to BaiZe.

RED LINES:
  5.1 contamination: this module only executes generated code in the sandbox;
    it never feeds eval-task code into training data. The RL parquet already
    passed the contamination gate (0/3347).
  5.2 anti-cheat: handled by compute_score (update_cheat_rate); this module is
    execution-only and adds no cheat surface.

Usage:
  python baize_posttrain_rl_sandbox_exec.py --selftest
  python baize_posttrain_rl_sandbox_exec.py --dry-run
"""
from __future__ import annotations

import ast
import itertools
import json
import logging
import os
import re
import sys
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

_DEFAULT_HOST = os.getenv("SANDBOX_HOST", "127.0.0.1")
_DEFAULT_PORTS = [p for p in os.getenv("SANDBOX_PORTS", "8664,8665,8653,8669").split(",") if p.strip()]
_DEFAULT_PATH = os.getenv("SANDBOX_URL_PATH", "v1/run_code").strip("/")
_DEFAULT_TIMEOUT = int(os.getenv("SANDBOX_TIMEOUT_RL", "60"))
_MARK_HOST = {"pyAether": "aether", "skill": "virtuoso"}
_ASSERT_MARKER = "BAIZE_ASSERT_RESULTS_JSON::"


class SandboxEndpointPool:
    """Round-robin across the forwarded tunnel ports (no shared state)."""

    def __init__(self, host=_DEFAULT_HOST, ports=None, path=_DEFAULT_PATH):
        self.host = host
        self.path = path
        if ports is None:
            ports = [int(p) for p in _DEFAULT_PORTS if p.strip().isdigit()]
        self.endpoints = [{"host": host, "port": int(p), "path": path} for p in ports]
        self._cycle = itertools.cycle(self.endpoints) if self.endpoints else None
        logger.info("SandboxEndpointPool: %d endpoints -> %s",
                    len(self.endpoints),
                    [(e["host"], e["port"]) for e in self.endpoints])

    def available(self):
        return bool(self.endpoints)

    def next(self):
        if self._cycle is None:
            raise RuntimeError("no sandbox endpoints configured")
        return next(self._cycle)


_POOL = None


def get_pool():
    global _POOL
    if _POOL is None:
        _POOL = SandboxEndpointPool()
    return _POOL


def run_sandbox_code(code, lang="pyAether", endpoint=None, timeout=_DEFAULT_TIMEOUT):
    """POST one code string to the sandbox run_code endpoint.
    Returns raw sandbox response dict; never raises (errors -> error_log)."""
    pool = get_pool()
    if endpoint is None:
        endpoint = pool.next()
    url = "http://{host}:{port}/{path}".format(**endpoint)
    payload = {"code": code, "lang": lang, "host": _MARK_HOST.get(lang, "aether")}
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        return {"response": "", "error_log": "sandbox timeout (%ds) %s" % (timeout, url),
                "print_log": "", "result": ""}
    except Exception as e:
        return {"response": "", "error_log": "sandbox error: %s" % e,
                "print_log": "", "result": ""}


_CODE_FENCE_RE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL)


def extract_generated_code(solution_str):
    """Extract the (first) fenced code block; fall back to whole text."""
    if not solution_str:
        return ""
    m = _CODE_FENCE_RE.search(solution_str)
    if m:
        return m.group(1).strip()
    for kw in ("def ", "import ", "from "):
        idx = solution_str.find(kw)
        if idx >= 0:
            return solution_str[idx:].strip()
    return solution_str.strip()


class _AssertInstrumenter(ast.NodeTransformer):
    """Rewrite assert X, msg inside the check function body into try/except
    collectors that append to _baize_results."""

    def __init__(self):
        self.counter = itertools.count()

    def _wrap_assert(self, node):
        n = next(self.counter)
        idx_const = ast.Constant(value="assert_%d" % n)
        passed_true = ast.Dict(
            keys=[ast.Constant(value="passed"), ast.Constant(value="name")],
            values=[ast.Constant(value=True), idx_const])
        append_pass = ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Name(id="_baize_results", ctx=ast.Load()),
                               attr="append", ctx=ast.Load()),
            args=[passed_true], keywords=[]))
        try_body = [node, append_pass]
        passed_false = ast.Dict(
            keys=[ast.Constant(value="passed"), ast.Constant(value="name"),
                  ast.Constant(value="error")],
            values=[ast.Constant(value=False), ast.Constant(value="assert_%d" % n),
                    ast.Call(func=ast.Name(id="str", ctx=ast.Load()),
                             args=[ast.Name(id="_e", ctx=ast.Load())], keywords=[])])
        append_fail = ast.Expr(value=ast.Call(
            func=ast.Attribute(value=ast.Name(id="_baize_results", ctx=ast.Load()),
                               attr="append", ctx=ast.Load()),
            args=[passed_false], keywords=[]))
        except_body = [append_fail]
        return ast.Try(body=try_body, handlers=[
            ast.ExceptHandler(type=ast.Name(id="Exception", ctx=ast.Load()),
                              name="_e", body=except_body)], orelse=[], finalbody=[])

    def visit_FunctionDef(self, node):
        if node.name != "check":
            return node
        self.generic_visit(node)
        return node

    def visit_Assert(self, node):
        return self._wrap_assert(node)


def instrument_test_code(test_code):
    """Return (header, instrumented_check_body, footer) so the caller can place
    the check(entry_point) call BETWEEN the body and the result-print footer.
    Returns None if instrumentation is not applicable."""
    if not test_code or "def check" not in test_code:
        return None
    try:
        tree = ast.parse(test_code)
    except SyntaxError:
        return None
    new_tree = _AssertInstrumenter().visit(tree)
    ast.fix_missing_locations(new_tree)
    # ast.unparse requires Python >= 3.9; the GRPO loop runs under the cu124
    # venv (Python 3.10) so this is available at runtime.  Guard anyway so a
    # selftest run under an older system python (e.g. 3.8) reports a clear,
    # actionable message instead of a cryptic AttributeError, and fall back to
    # the `astunparse` backport if it happens to be installed.
    unparse = getattr(ast, "unparse", None)
    if unparse is None:
        try:
            from astunparse import unparse  # type: ignore
        except ImportError:
            raise RuntimeError(
                "instrument_test_code needs ast.unparse (Python>=3.9) or the "
                "`astunparse` backport. Run via the cu124 venv: "
                "~/code/verl_cu124_venv/bin/python")
    instrumented = unparse(new_tree)
    header = "_baize_results = []\n"
    footer = ('import json as _baize_json\n'
              'print("' + _ASSERT_MARKER + '" + _baize_json.dumps(_baize_results))\n')
    return header + instrumented, footer


def count_assertions(test_code):
    """Count assert statements inside the check function."""
    if not test_code:
        return 0
    try:
        tree = ast.parse(test_code)
    except SyntaxError:
        return 0
    total = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "check":
            for child in ast.walk(node):
                if isinstance(child, ast.Assert):
                    total += 1
    return total


def build_test_script(generated_code, test_code, entry_point, instrument=True):
    """Assemble the full script sent to the sandbox.

    Order matters: define candidate -> define check() -> RUN check(entry_point)
    -> print results marker.  The check call must come BEFORE the footer print
    so the per-assertion results are populated when printed."""
    gen = extract_generated_code(generated_code) if generated_code else ""
    parts = [gen]
    footer = None
    if instrument:
        inst = instrument_test_code(test_code)
        if inst is not None:
            body, footer = inst
            parts.append(body)
        else:
            parts.append(test_code)
            footer = None
    else:
        parts.append(test_code)
    if entry_point:
        parts.append("check(%s)" % entry_point)
    if footer is not None:
        parts.append(footer)
    return "\n\n".join(p for p in parts if p.strip())


def _scrape_assert_results(print_log):
    if not print_log:
        return None
    idx = print_log.find(_ASSERT_MARKER)
    if idx < 0:
        return None
    rest = print_log[idx + len(_ASSERT_MARKER):]
    m = re.match(r"\[.*\]", rest, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def parse_exec_result(response, test_code="", entry_point=""):
    """Convert a raw sandbox response into the extra_info dict compute_score
    expects: {exec_success, returncode, stdout, stderr, assert_results,
              tool_results}."""
    error_log = (response or {}).get("error_log", "") or ""
    print_log = (response or {}).get("print_log", "") or ""
    resp_msg = (response or {}).get("response", "") or ""
    failed = bool(error_log.strip()) or "failed" in resp_msg.lower()
    exec_success = not failed
    assert_results = _scrape_assert_results(print_log)
    if assert_results is None:
        total = count_assertions(test_code)
        if total > 0:
            if exec_success:
                assert_results = [{"passed": True, "name": "assert_%d" % i}
                                  for i in range(total)]
            else:
                assert_results = [{"passed": False, "name": "assert_%d" % i}
                                  for i in range(total)]
        else:
            assert_results = []
    return {
        "exec_success": exec_success,
        "returncode": 0 if exec_success else 1,
        "stdout": print_log,
        "stderr": error_log,
        "assert_results": assert_results,
        "tool_results": [{"response": resp_msg}] if resp_msg else [],
    }


def score_rollout(generated_text, test_code, entry_point, lang="pyAether",
                  timeout=_DEFAULT_TIMEOUT, endpoint=None, instrument=True):
    """Execute one generated rollout in the sandbox and return the extra_info
    dict to pass to compute_score (arm R1-R4)."""
    script = build_test_script(generated_text, test_code, entry_point, instrument)
    if not script.strip():
        return {"exec_success": False, "returncode": 1, "stdout": "",
                "stderr": "empty test script", "assert_results": [],
                "tool_results": []}
    raw = run_sandbox_code(script, lang=lang, endpoint=endpoint, timeout=timeout)
    return parse_exec_result(raw, test_code=test_code, entry_point=entry_point)


def _selftest():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    pool = get_pool()
    if not pool.available():
        print("FAIL: no sandbox endpoints (tunnel down?)")
        return 1
    print("== sandbox endpoint probe ==")
    probe = run_sandbox_code("print(2+2)")
    print("  print(2+2) ->", json.dumps(probe, ensure_ascii=False))
    if probe.get("error_log"):
        print("FAIL: sandbox unreachable:", probe["error_log"][:120])
        return 1
    test_code = (
        "import pyAether as pyScript\n"
        "def check(candidate):\n"
        "    result = candidate()\n"
        "    assert result is not None, 'Should return non-None'\n"
        "    assert isinstance(result, bool), 'Expected bool'\n")
    entry_point = "call_dummy"
    print("\n== assertion instrumentation ==")
    inst = instrument_test_code(test_code)
    print(inst)
    print("\n== PASS case (candidate returns True) ==")
    gen_pass = "def call_dummy():\n    return True\n"
    extra_pass = score_rollout(gen_pass, test_code, entry_point)
    print("  extra_info:", json.dumps(extra_pass, ensure_ascii=False))
    assert extra_pass["exec_success"] is True, "PASS case should run ok"
    assert all(a["passed"] for a in extra_pass["assert_results"]), "all asserts should pass"
    print("\n== PARTIAL case (candidate returns 42, not bool) ==")
    gen_fail = "def call_dummy():\n    return 42\n"
    extra_fail = score_rollout(gen_fail, test_code, entry_point)
    print("  extra_info:", json.dumps(extra_fail, ensure_ascii=False))
    # Instrumented: code RAN (exec_success=True) but assert_1 fails -> partial.
    passed_names = [a["name"] for a in extra_fail["assert_results"] if a["passed"]]
    failed_names = [a["name"] for a in extra_fail["assert_results"] if not a["passed"]]
    print("  passed=%s failed=%s" % (passed_names, failed_names))
    assert "assert_0" in passed_names, "non-None assert should pass (42)"
    assert "assert_1" in failed_names, "type assert should fail (42 not bool)"
    print("\n== CRASH case (candidate raises) ==")
    gen_crash = "def call_dummy():\n    raise AttributeError('bad api')\n"
    extra_crash = score_rollout(gen_crash, test_code, entry_point)
    print("  extra_info:", json.dumps(extra_crash, ensure_ascii=False)[:300])
    assert extra_crash["exec_success"] is False, "crash case should be exec_success=False"
    print("\n== reward function integration (R1/R2) ==")
    here = os.path.dirname(os.path.abspath(__file__))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "baize_reward", os.path.join(here, "baize_posttrain_reward_functions.py"))
    rmod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rmod)
    rm = {"test_code": test_code, "entry_point": entry_point,
          "canonical_solution": "    return True"}
    s_pass = rmod.compute_score("pyaether_synth_v2", gen_pass, "    return True",
                                extra_pass, arm="R2", auto_fallback=False)
    s_partial = rmod.compute_score("pyaether_synth_v2", gen_fail, "    return True",
                                   extra_fail, arm="R2", auto_fallback=False)
    s_crash = rmod.compute_score("pyaether_synth_v2", gen_crash, "    return True",
                                 extra_crash, arm="R2", auto_fallback=False)
    s_pass_r1 = rmod.compute_score("pyaether_synth_v2", gen_pass, "    return True",
                                   extra_pass, arm="R1", auto_fallback=False)
    s_partial_r1 = rmod.compute_score("pyaether_synth_v2", gen_fail, "    return True",
                                      extra_fail, arm="R1", auto_fallback=False)
    s_pass_fb = rmod.compute_score("pyaether_synth_v2", gen_pass, "    return True",
                                   rm, arm="R2", auto_fallback=False)
    print("  R2 pass=%.4f partial=%.4f crash=%.4f" % (s_pass, s_partial, s_crash))
    print("  R1 pass=%.4f partial=%.4f" % (s_pass_r1, s_partial_r1))
    print("  R2 pass(no exec->fallback R0)=%.4f" % s_pass_fb)
    assert s_pass >= 0.9, "full pass should score ~1.0 under R2"
    assert s_partial > s_crash, "partial should beat crash"
    assert s_partial < s_pass, "partial should be below full pass"
    assert s_crash == 0.0, "crash should score 0"
    assert s_pass_r1 >= 0.9, "R1 full pass ~1.0"
    assert s_partial_r1 == 0.0, "R1 binary: partial -> 0"
    print("\nALL SELFTEST CHECKS PASSED")
    return 0


def _dryrun():
    print("== baize_posttrain_rl_sandbox_exec dry-run ==")
    pool = get_pool()
    print("endpoints:", [(e["host"], e["port"]) for e in pool.endpoints])
    print("timeout:", _DEFAULT_TIMEOUT)
    print("marker:", _ASSERT_MARKER)
    tc = ("def check(candidate):\n    result = candidate()\n"
          "    assert result is not None\n")
    print("\ninstrument_test_code sample (body+footer tuple):\n", instrument_test_code(tc))
    print("\nbuild_test_script sample:\n",
          build_test_script("def f():\n    return 1\n", tc, "f"))
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(_selftest())
    sys.exit(_dryrun())
