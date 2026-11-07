#!/usr/bin/env python3
"""baize_posttrain_reward_functions.py — Custom reward functions for verl GRPO
on EDA-Eval-PyAether synthetic tasks.

R13 (2026-11-07): verl's custom reward function interface is:
    compute_score(data_source, solution_str, ground_truth, extra_info, **kwargs) -> float

This module implements 4 reward arms (R1-R4) as described in the paper
(5_llm_posttrain.tex Table ref{tab:reward}) and EXPERIMENTS_POSTTRAIN.md §R3.

Reward Arms:
    R1: Binary pass/fail (too sparse for 2B, baseline only)
    R2: Partial credit (exec_success=0.2 + partial_assert=0.2 each + full_pass=1.0)
    R3: R2 + tool_call_penalty (align with harness cost model)
    R4: R3 + API_legality (penalize hallucinated API names)

Usage in verl YAML config:
    custom_reward_function:
      path: run/baize_posttrain_reward_functions.py
      name: compute_score
      reward_kwargs:
        arm: R2
        api_database: ~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json

WARNING: Surrogate RL results (MiniCPM5-2B) are NOT transferable to BaiZe.
"""
from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

REWARD_ARMS = {"R1", "R2", "R3", "R4"}
EXEC_SUCCESS_SCORE = 0.2
PARTIAL_ASSERT_SCORE = 0.2
FULL_PASS_SCORE = 1.0
TOOL_CALL_PENALTY_EXCESSIVE = -0.1
TOOL_CALL_PENALTY_ZERO = -0.05
TOOL_CALL_BONUS_APPROPRIATE = 0.05
HALLUCINATED_API_PENALTY = -0.15
UNKNOWN_API_PENALTY = -0.05
FORMAT_BONUS = 0.02

# ---------------------------------------------------------------------------
# API database loader (lazy, cached)
# ---------------------------------------------------------------------------
_API_DB_CACHE: Optional[set] = None
_API_DB_PATH: Optional[str] = None


def _load_api_database(api_db_path: str) -> set:
    """Load API names from the PyAether API database JSON file."""
    global _API_DB_CACHE, _API_DB_PATH
    if _API_DB_CACHE is not None and _API_DB_PATH == api_db_path:
        return _API_DB_CACHE
    api_names = set()
    try:
        expanded = os.path.expanduser(os.path.expandvars(api_db_path))
        if os.path.exists(expanded):
            with open(expanded, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for entry in data:
                    name = entry.get("api_name")
                    if name:
                        api_names.add(name)
            elif isinstance(data, dict):
                api_names = set(data.keys())
                for entry in data.values():
                    if isinstance(entry, dict):
                        name = entry.get("api_name")
                        if name:
                            api_names.add(name)
            logger.info("Loaded %d API names from %s", len(api_names), expanded)
        else:
            logger.warning("API database not found at %s", expanded)
    except Exception as e:
        logger.warning("Failed to load API database %s: %s", api_db_path, e)
    _API_DB_CACHE = api_names
    _API_DB_PATH = api_db_path
    return api_names


# ---------------------------------------------------------------------------
# Tool call extraction from trajectory text
# ---------------------------------------------------------------------------
_TOOL_CALL_PATTERN = re.compile(r"<function>\s*(\w+)\s*</function>", re.IGNORECASE)
_PYTHON_API_PATTERN = re.compile(r"(?:pyScript|pyAether)\.(\w+)\s*\(")


def extract_tool_calls(solution_str: str) -> list:
    """Extract tool/API call names from the model's response trajectory."""
    calls = []
    calls.extend(_TOOL_CALL_PATTERN.findall(solution_str))
    calls.extend(_PYTHON_API_PATTERN.findall(solution_str))
    return calls


def extract_code_blocks(solution_str: str) -> list:
    """Extract Python code blocks from the response text."""
    blocks = []
    for match in re.finditer(r"```(?:python)?\s*\n(.*?)```", solution_str, re.DOTALL):
        blocks.append(match.group(1).strip())
    for match in re.finditer(r"<code>(.*?)</code>", solution_str, re.DOTALL):
        blocks.append(match.group(1).strip())
    return blocks


# ---------------------------------------------------------------------------
# Execution result parsing
# ---------------------------------------------------------------------------
def parse_execution_result(extra_info):
    """Parse execution results from extra_info (populated by sandbox tool)."""
    if extra_info is None:
        return {}
    return {
        "exec_success": extra_info.get("exec_success", False),
        "returncode": extra_info.get("returncode", -1),
        "stdout": extra_info.get("stdout", ""),
        "stderr": extra_info.get("stderr", ""),
        "assert_results": extra_info.get("assert_results", []),
        "tool_results": extra_info.get("tool_results", []),
    }


def count_passed_assertions(assert_results):
    """Count passed/total assertions. Returns (passed, total)."""
    total = len(assert_results)
    passed = sum(1 for a in assert_results if a.get("passed", False))
    return passed, total


# ---------------------------------------------------------------------------
# Reward Arm implementations
# ---------------------------------------------------------------------------
def reward_r1_binary(exec_result):
    """R1: Binary pass/fail reward."""
    if not exec_result.get("exec_success", False):
        return 0.0
    passed, total = count_passed_assertions(exec_result.get("assert_results", []))
    if total == 0:
        return 0.0
    return FULL_PASS_SCORE if passed == total else 0.0


def reward_r2_partial(exec_result):
    """R2: Partial credit reward."""
    if not exec_result.get("exec_success", False):
        return 0.0
    passed, total = count_passed_assertions(exec_result.get("assert_results", []))
    if total == 0:
        return EXEC_SUCCESS_SCORE
    if passed == total:
        return FULL_PASS_SCORE
    score = EXEC_SUCCESS_SCORE + (passed * PARTIAL_ASSERT_SCORE)
    return min(score, 0.99)


def reward_r3_tool_penalty(r2_score, tool_calls):
    """R3: R2 + tool call usage penalty/bonus."""
    n_calls = len(tool_calls)
    if n_calls == 0:
        return r2_score + TOOL_CALL_PENALTY_ZERO
    elif n_calls > 20:
        return r2_score + TOOL_CALL_PENALTY_EXCESSIVE
    elif 3 <= n_calls <= 15:
        return r2_score + TOOL_CALL_BONUS_APPROPRIATE
    return r2_score


def reward_r4_api_legality(r3_score, tool_calls, api_db_path):
    """R4: R3 + API legality check."""
    api_db = _load_api_database(api_db_path)
    if not api_db:
        return r3_score
    penalty = 0.0
    for call_name in tool_calls:
        if call_name not in api_db:
            if re.match(r"^[a-z][a-zA-Z0-9_]*$", call_name):
                penalty += UNKNOWN_API_PENALTY
            else:
                penalty += HALLUCINATED_API_PENALTY
    return r3_score + penalty


def check_format(solution_str):
    """Check if the response follows expected format."""
    if not solution_str or len(solution_str.strip()) < 10:
        return False
    return len(extract_code_blocks(solution_str)) > 0 or len(extract_tool_calls(solution_str)) > 0


# ---------------------------------------------------------------------------
# Main entry point (verl interface)
# ---------------------------------------------------------------------------
def compute_score(data_source, solution_str, ground_truth, extra_info=None, **kwargs):
    """Main reward function — verl custom_reward_function interface.

    Args:
        data_source: Dataset identifier (e.g., "pyaether_synth_v2").
        solution_str: The model's full generated response text (trajectory).
        ground_truth: Expected answer or test code from the dataset.
        extra_info: Additional metadata (may contain sandbox execution results).
        **kwargs: Additional arguments from YAML reward_kwargs:
            arm: Reward arm to use (R1/R2/R3/R4, default R2).
            api_database: Path to API database JSON (for R4).

    Returns:
        Float reward score.
    """
    arm = kwargs.get("arm", "R2")
    api_db_path = kwargs.get(
        "api_database",
        os.path.expanduser("~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json"),
    )
    if arm not in REWARD_ARMS:
        logger.warning("Unknown reward arm '%s', defaulting to R2", arm)
        arm = "R2"

    exec_result = parse_execution_result(extra_info)
    tool_calls = extract_tool_calls(solution_str)

    if arm == "R1":
        score = reward_r1_binary(exec_result)
    elif arm == "R2":
        score = reward_r2_partial(exec_result)
    elif arm == "R3":
        r2 = reward_r2_partial(exec_result)
        score = reward_r3_tool_penalty(r2, tool_calls)
    elif arm == "R4":
        r2 = reward_r2_partial(exec_result)
        r3 = reward_r3_tool_penalty(r2, tool_calls)
        score = reward_r4_api_legality(r3, tool_calls, api_db_path)
    else:
        score = 0.0

    if check_format(solution_str) and score > 0:
        score += FORMAT_BONUS
    score = max(0.0, min(score, 1.1))

    logger.debug("compute_score: arm=%s, exec=%s, calls=%d, score=%.4f",
                 arm, exec_result.get("exec_success", False), len(tool_calls), score)
    return score


# ---------------------------------------------------------------------------
# Self-test / dry-run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Reward function self-test")
    parser.add_argument("--arm", default="R2", choices=list(REWARD_ARMS))
    parser.add_argument("--api-database", default="", help="Path to API database JSON")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    test_cases = [
        {"name": "full_pass", "solution_str": "```python\nimport pyAether as pyScript\nresult = pyScript.get_cell_by_id('cell1')\nprint(result)\n```",
         "ground_truth": "assert result is not None",
         "extra_info": {"exec_success": True, "returncode": 0, "stdout": "ok", "stderr": "",
                        "assert_results": [{"passed": True, "name": "t1"}], "tool_results": [{"response": "ok"}]}},
        {"name": "partial_pass", "solution_str": "```python\nimport pyAether as pyScript\nresult = pyScript.get_cell_by_id('cell1')\n```",
         "ground_truth": "assert isinstance(result, dict)",
         "extra_info": {"exec_success": True, "returncode": 0, "stdout": "", "stderr": "",
                        "assert_results": [{"passed": True, "name": "t1"}, {"passed": False, "name": "t2"}], "tool_results": []}},
        {"name": "exec_failure", "solution_str": "```python\nimport pyAether as pyScript\nresult = pyScript.nonexistent_api()\n```",
         "ground_truth": "assert result is not None",
         "extra_info": {"exec_success": False, "returncode": 1, "stdout": "", "stderr": "AttributeError",
                        "assert_results": [], "tool_results": []}},
        {"name": "no_tools", "solution_str": "The answer is cell1.",
         "ground_truth": "assert result is not None",
         "extra_info": {"exec_success": False, "returncode": 1, "stdout": "", "stderr": "No code",
                        "assert_results": [], "tool_results": []}},
        {"name": "xml_tool_calls", "solution_str": "<function>get_cell_by_id</function><param>cell1</param>\n```python\nresult = pyScript.get_cell_by_id('cell1')\nassert result is not None\n```",
         "ground_truth": "assert result is not None",
         "extra_info": {"exec_success": True, "returncode": 0, "stdout": "ok", "stderr": "",
                        "assert_results": [{"passed": True, "name": "t1"}], "tool_results": [{"response": "ok"}]}},
    ]

    extra_kw = {"arm": args.arm}
    if args.api_database:
        extra_kw["api_database"] = args.api_database

    print(f"\n{'='*60}\nReward self-test — arm={args.arm}\n{'='*60}\n")
    for tc in test_cases:
        sc = compute_score("pyaether_synth_v2", tc["solution_str"], tc["ground_truth"],
                           tc["extra_info"], **extra_kw)
        tc_calls = extract_tool_calls(tc["solution_str"])
        print(f"  {tc['name']:20s}  score={sc:.4f}  tool_calls={len(tc_calls)}")

    print(f"\n{'='*60}\nAll arms on 'full_pass':\n{'='*60}\n")
    for arm_name in sorted(REWARD_ARMS):
        sc = compute_score("pyaether_synth_v2", test_cases[0]["solution_str"],
                           test_cases[0]["ground_truth"], test_cases[0]["extra_info"], arm=arm_name,
                           **({"api_database": args.api_database} if args.api_database else {}))
        print(f"  {arm_name}: score={sc:.4f}")
    print(f"\nSelf-test PASSED\n")
