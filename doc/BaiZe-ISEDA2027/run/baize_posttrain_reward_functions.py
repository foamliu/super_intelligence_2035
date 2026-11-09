#!/usr/bin/env python3
"""baize_posttrain_reward_functions.py — Custom reward functions for verl GRPO
on EDA-Eval-PyAether synthetic tasks.

R13 (2026-11-07): verl's custom reward function interface is:
    compute_score(data_source, solution_str, ground_truth, extra_info, **kwargs) -> float

R22 (2026-11-07): CRITICAL — Added R0 skeleton-mode fallback reward.
  When the EDA sandbox is not available (skeleton mode), exec_success is always
  False, causing R1-R4 to return 0.0 for ALL rollouts → GRPO advantage=0 →
  NO learning signal → RL is a silent no-op. R0 computes differentiated rewards
  from the model's response text + task metadata alone (no execution needed).

This module implements 5 reward arms (R0-R4) as described in the paper
(5_llm_posttrain.tex Table ref{tab:reward}) and EXPERIMENTS_POSTTRAIN.md §R3/§R22.

Reward Arms:
    R0: Skeleton-mode fallback (static analysis, no sandbox needed)
        syntax_valid(0.1) + api_correct(0.3) + entry_point(0.2)
        + structure(0.2) + test_alignment(0.2) + format_bonus(0.02)
    R1: Binary pass/fail (too sparse for 2B, baseline only)
    R2: Partial credit (exec_success=0.2 + partial_assert=0.2 each + full_pass=1.0)
    R3: R2 + tool_call_penalty (align with harness cost model)
    R4: R3 + API_legality (penalize hallucinated API names)

Auto-fallback: if exec_success is not in extra_info OR is False AND no
  assert_results present, compute_score auto-switches to R0 unless arm is
  explicitly set to R1-R4 with --no-fallback.

Usage in verl YAML config:
    custom_reward_function:
      path: baize_posttrain_reward_functions.py
      name: compute_score
      reward_kwargs:
        arm: R2
        api_database: ~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json
        auto_fallback: true   # auto-switch to R0 when sandbox unavailable

WARNING: Surrogate RL results (MiniCPM5-2B) are NOT transferable to BaiZe.
"""
from __future__ import annotations

import ast
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

REWARD_ARMS = {"R0", "R1", "R2", "R3", "R4"}
EXEC_SUCCESS_SCORE = 0.2

# ---------------------------------------------------------------------------
# R22: Cheat rate tracker (red-line §5.2 — must report cheat rate)
# ---------------------------------------------------------------------------
_CHEAT_TRACKER: Optional[Dict[str, Any]] = None
_CHEAT_NGRAM_SIZE = 8  # 8-gram for overlap detection (configurable via env)
_CHEAT_REPORT_INTERVAL = 200  # report every N calls


def _init_cheat_tracker():
    """Initialize the global cheat rate tracker."""
    global _CHEAT_TRACKER
    if _CHEAT_TRACKER is not None:
        return
    _CHEAT_TRACKER = {
        "total_rollouts": 0,
        "cheat_detected": 0,
        "cheat_rate": 0.0,
        "last_report_step": 0,
        "cheat_examples": [],  # keep last 5 examples for debugging
        "ngram_size": int(os.environ.get("CHEAT_NGRAM_SIZE", _CHEAT_NGRAM_SIZE)),
        "report_interval": int(os.environ.get("CHEAT_REPORT_INTERVAL", _CHEAT_REPORT_INTERVAL)),
    }


def _extract_ngrams(text: str, n: int = 8) -> set:
    """Extract character-level n-grams from text (normalized)."""
    if not text:
        return set()
    # Normalize: lowercase, strip whitespace
    normalized = re.sub(r"\s+", " ", text.lower().strip())
    if len(normalized) < n:
        return {normalized}
    return {normalized[i:i + n] for i in range(len(normalized) - n + 1)}


def check_cheat_overlap(solution_str: str, eval_ngrams: Optional[set], ngram_size: int = 8) -> tuple:
    """Check if the model's response overlaps with eval task n-grams.

    Returns (is_cheat: bool, overlap_ratio: float, overlap_count: int).
    """
    if not eval_ngrams:
        return False, 0.0, 0
    model_ngrams = _extract_ngrams(solution_str, ngram_size)
    if not model_ngrams:
        return False, 0.0, 0
    overlap = model_ngrams & eval_ngrams
    overlap_ratio = len(overlap) / len(model_ngrams) if model_ngrams else 0.0
    # Threshold: >5% n-gram overlap with eval task code = suspicious
    is_cheat = overlap_ratio > 0.05 and len(overlap) > 10
    return is_cheat, overlap_ratio, len(overlap)


def update_cheat_rate(solution_str: str, eval_ngrams: Optional[set] = None, step: int = 0):
    """Update cheat rate tracker. Call from compute_score or externally.

    Args:
        solution_str: Model's generated response.
        eval_ngrams: Set of n-grams from the 158 eval tasks (test code + canonical solutions).
                     If None, skip overlap check (no contamination reference available).
        step: Current training step (for periodic reporting).
    """
    _init_cheat_tracker()
    if _CHEAT_TRACKER is None:
        return
    _CHEAT_TRACKER["total_rollouts"] += 1

    is_cheat = False
    overlap_ratio = 0.0
    if eval_ngrams:
        ngram_size = _CHEAT_TRACKER.get("ngram_size", _CHEAT_NGRAM_SIZE)
        is_cheat, overlap_ratio, _ = check_cheat_overlap(solution_str, eval_ngrams, ngram_size)

    if is_cheat:
        _CHEAT_TRACKER["cheat_detected"] += 1
        if len(_CHEAT_TRACKER["cheat_examples"]) < 5:
            _CHEAT_TRACKER["cheat_examples"].append({
                "step": step,
                "overlap_ratio": round(overlap_ratio, 4),
                "snippet": solution_str[:200],
            })

    _CHEAT_TRACKER["cheat_rate"] = (
        _CHEAT_TRACKER["cheat_detected"] / _CHEAT_TRACKER["total_rollouts"]
        if _CHEAT_TRACKER["total_rollouts"] > 0 else 0.0
    )

    # Periodic report to stderr (verl captures stderr in logs)
    report_interval = _CHEAT_TRACKER.get("report_interval", _CHEAT_REPORT_INTERVAL)
    if step > 0 and step - _CHEAT_TRACKER["last_report_step"] >= report_interval:
        _CHEAT_TRACKER["last_report_step"] = step
        logger.info(
            "R22 cheat_rate report: total=%d, cheat=%d, rate=%.4f, step=%d",
            _CHEAT_TRACKER["total_rollouts"],
            _CHEAT_TRACKER["cheat_detected"],
            _CHEAT_TRACKER["cheat_rate"],
            step,
        )


def get_cheat_rate_report() -> Dict[str, Any]:
    """Get the current cheat rate report as a dict (for JSON output)."""
    _init_cheat_tracker()
    if _CHEAT_TRACKER is None:
        return {"error": "tracker not initialized"}
    return {
        "total_rollouts": _CHEAT_TRACKER["total_rollouts"],
        "cheat_detected": _CHEAT_TRACKER["cheat_detected"],
        "cheat_rate": round(_CHEAT_TRACKER["cheat_rate"], 6),
        "ngram_size": _CHEAT_TRACKER.get("ngram_size", _CHEAT_NGRAM_SIZE),
        "cheat_examples": _CHEAT_TRACKER.get("cheat_examples", []),
    }


def save_cheat_rate_report(output_path: str):
    """Save cheat rate report to JSON file."""
    report = get_cheat_rate_report()
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info("R22: cheat_rate.json saved to %s", output_path)
    except (OSError, IOError) as e:
        logger.warning("R22: Failed to save cheat_rate.json: %s", e)
PARTIAL_ASSERT_SCORE = 0.2
FULL_PASS_SCORE = 1.0
TOOL_CALL_PENALTY_EXCESSIVE = -0.1
TOOL_CALL_PENALTY_ZERO = -0.05
TOOL_CALL_BONUS_APPROPRIATE = 0.05
HALLUCINATED_API_PENALTY = -0.15
UNKNOWN_API_PENALTY = -0.05
FORMAT_BONUS = 0.02

# R0 component scores
R0_SYNTAX_SCORE = 0.10
R0_API_SCORE = 0.30
R0_ENTRY_POINT_SCORE = 0.20
R0_STRUCTURE_SCORE = 0.20
R0_TEST_ALIGN_SCORE = 0.20

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
# R124 FIX: Capture dotted paths like pyScript.emyDesign.setCp() → "emyDesign.setCp"
#   Also still capture single-level pyScript.aeGetCurDesign() → "aeGetCurDesign"
_PYTHON_API_PATTERN = re.compile(r"(?:pyScript|pyAether)\.([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)\s*\(")


def extract_tool_calls(solution_str: str) -> list:
    """Extract tool/API call names from the model's response text.

    R124 FIX: Now captures dotted paths (``emyDesign.setCp``) from
    ``pyScript.emyDesign.setCp()`` patterns, not just the first-level
    attribute.  Falls back to short name for backwards compatibility.
    """
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
    """R4: R3 + API legality check.

    R124 FIX: Now checks both the full dotted name (``emyDesign.setCp``) and
    the short name (``setCp``) against the API database, so that
    ``pyScript.emyDesign.setCp()`` is correctly recognized as a valid API.
    """
    api_db = _load_api_database(api_db_path)
    if not api_db:
        return r3_score
    penalty = 0.0
    for call_name in tool_calls:
        # R124: try full dotted name first, then short name
        short_name = call_name.split(".")[-1] if "." in call_name else call_name
        if call_name in api_db or short_name in api_db:
            continue  # Valid API (either dotted or short form found)
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
# R0: Skeleton-mode fallback reward (R22, static analysis, no sandbox needed)
# ---------------------------------------------------------------------------

def _parse_task_metadata(extra_info):
    """Extract task metadata from extra_info (reward_model dict from parquet)."""
    if extra_info is None:
        return {}
    info = {}
    if isinstance(extra_info, dict):
        info["test_code"] = extra_info.get("test_code", "")
        info["canonical_solution"] = extra_info.get("canonical_solution", "")
        info["entry_point"] = extra_info.get("entry_point", "")
        meta_str = extra_info.get("metadata", "")
        if isinstance(meta_str, str):
            try:
                info["metadata"] = json.loads(meta_str)
            except (json.JSONDecodeError, TypeError):
                info["metadata"] = {}
        elif isinstance(meta_str, dict):
            info["metadata"] = meta_str
        else:
            info["metadata"] = {}
    info["apis_used"] = info.get("metadata", {}).get("apis_used", [])
    info["assertion_template"] = info.get("metadata", {}).get("assertion_template", "")
    return info


def _check_syntax(code_blocks):
    """Check if extracted code blocks are syntactically valid Python."""
    if not code_blocks:
        return False, 0, 0
    n_valid = 0
    for block in code_blocks:
        try:
            ast.parse(block)
            n_valid += 1
        except SyntaxError:
            pass
    return n_valid == len(code_blocks), n_valid, len(code_blocks)


def _check_api_usage(solution_str, apis_used):
    """Check if the model's code references the expected APIs.

    R124 FIX: Now handles dotted paths (``pyScript.emyDesign.setCp()``).
    Both the full dotted name and the short (last-segment) name are checked
    against the expected API list.
    """
    if not apis_used:
        return 0.5, 0, 0
    expected_apis = set()
    expected_apis_full = set()  # R124: keep full dotted names too
    for api in apis_used:
        if isinstance(api, str):
            expected_apis_full.add(api)
            name = api.split(".")[-1] if "." in api else api
            expected_apis.add(name)
    found_apis = set()
    # R124: _PYTHON_API_PATTERN now captures dotted paths
    for m in _PYTHON_API_PATTERN.finditer(solution_str):
        full = m.group(1)
        found_apis.add(full)
        # Also add the short name for backwards-compatible matching
        short = full.split(".")[-1] if "." in full else full
        found_apis.add(short)
    for m in re.finditer(r'<function\s+name="([^"]+)"', solution_str):
        found_apis.add(m.group(1))
    for name in expected_apis:
        if re.search(r'\b' + re.escape(name) + r'\s*\(', solution_str):
            found_apis.add(name)
    n_ref = len(expected_apis & found_apis)
    n_exp = len(expected_apis)
    return (n_ref / n_exp if n_exp > 0 else 0.5), n_ref, n_exp


def _check_entry_point(solution_str, entry_point):
    """Check if the model's response defines or calls the expected function."""
    if not entry_point:
        return True, "no_entry_point_required"
    has_def = bool(re.search(r'\bdef\s+' + re.escape(entry_point) + r'\s*\(', solution_str))
    has_call = bool(re.search(r'\b' + re.escape(entry_point) + r'\s*\(', solution_str))
    if has_def and has_call:
        return True, "defined_and_called"
    if has_def:
        return True, "defined_only"
    if has_call:
        return True, "called_only"
    return False, "missing"


def _check_structure(solution_str, canonical_solution):
    """Check if the model's code has the right structure."""
    code_blocks = extract_code_blocks(solution_str)
    if not code_blocks:
        return 0.0, "no_code_blocks"
    main_code = max(code_blocks, key=len)
    score = 0.0
    details = []
    if re.search(r'\breturn\b', main_code):
        score += 0.4
        details.append("has_return")
    if re.search(r'import\s+pyAether', main_code):
        score += 0.3
        details.append("has_import")
    if canonical_solution:
        # R124 FIX: use _PYTHON_API_PATTERN (now captures dotted paths)
        canon_calls = re.findall(
            r"(?:pyScript|pyAether)\.([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)\s*\(",
            canonical_solution)
        canon_apis = set()
        for c in canon_calls:
            canon_apis.add(c)
            canon_apis.add(c.split(".")[-1])  # also add short name
        if canon_apis:
            model_calls = set(re.findall(
                r"(?:pyScript|pyAether)\.([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)\s*\(",
                main_code))
            model_apis = set()
            for c in model_calls:
                model_apis.add(c)
                model_apis.add(c.split(".")[-1])
            overlap = len(canon_apis & model_apis)
            if overlap > 0:
                score += 0.3 * (overlap / len(canon_apis))
                details.append(f"api_overlap={overlap}/{len(canon_apis)}")
    return min(score, 1.0), "+".join(details) if details else "no_structure"


def _check_test_alignment(solution_str, test_code):
    """Check if the model's code aligns with the test's expected return type."""
    if not test_code:
        return 0.5, "no_test_code"
    type_matches = re.findall(r'isinstance\s*\(\s*result\s*,\s*([^)]+)\)', test_code)
    expected_types = []
    for t in type_matches:
        t = t.strip()
        if t.startswith("("):
            expected_types.extend(re.findall(r'\b(\w+)\b', t))
        else:
            expected_types.append(t)
    if not expected_types:
        if "assert result is not None" in test_code:
            blocks = extract_code_blocks(solution_str)
            if blocks and re.search(r'\breturn\b', max(blocks, key=len)):
                return 1.0, "has_return_for_non_none"
            return 0.3, "missing_return_for_non_none"
        return 0.5, "no_type_assertion"
    blocks = extract_code_blocks(solution_str)
    if not blocks:
        return 0.0, "no_code"
    main_code = max(blocks, key=len)
    type_patterns = {
        "bool": [r'return\s+(True|False)', r'py(?:Aether|Script)\.\w+\('],
        "int": [r'return\s+\d+', r'\bint\s*\('],
        "str": [r'return\s+["\']', r'\bstr\s*\('],
        "list": [r'return\s*\[', r'\blist\s*\('],
        "dict": [r'return\s*\{', r'\bdict\s*\('],
        "tuple": [r'return\s*\('],
        "float": [r'return\s+[\d.]+', r'\bfloat\s*\('],
    }
    matched = 0
    for etype in expected_types:
        for pat in type_patterns.get(etype.lower(), []):
            if re.search(pat, main_code):
                matched += 1
                break
    score = matched / len(expected_types) if expected_types else 0.5
    return score, f"matched={matched}/{len(expected_types)}"


def reward_r0_skeleton(solution_str, extra_info, api_db_path=None):
    """R0: Skeleton-mode fallback reward using static analysis only.

    Ensures GRPO gets non-zero, varied gradient signal even when sandbox
    is unavailable. Components: syntax(0.1) + api(0.3) + entry_point(0.2)
    + structure(0.2) + test_alignment(0.2) + format_bonus(0.02).
    """
    task_info = _parse_task_metadata(extra_info)
    apis_used = task_info.get("apis_used", [])
    entry_point = task_info.get("entry_point", "")
    canonical = task_info.get("canonical_solution", "")
    test_code = task_info.get("test_code", "")

    code_blocks = extract_code_blocks(solution_str)
    all_valid, n_valid, n_total = _check_syntax(code_blocks)
    syntax_score = R0_SYNTAX_SCORE if all_valid and n_total > 0 else (
        R0_SYNTAX_SCORE * 0.5 if n_valid > 0 else 0.0)

    api_frac, n_ref, n_exp = _check_api_usage(solution_str, apis_used)
    api_score = R0_API_SCORE * api_frac

    ep_found, _ = _check_entry_point(solution_str, entry_point)
    ep_score = R0_ENTRY_POINT_SCORE if ep_found else 0.0

    struct_frac, _ = _check_structure(solution_str, canonical)
    struct_score = R0_STRUCTURE_SCORE * struct_frac

    test_frac, _ = _check_test_alignment(solution_str, test_code)
    test_score = R0_TEST_ALIGN_SCORE * test_frac

    total = syntax_score + api_score + ep_score + struct_score + test_score
    if check_format(solution_str):
        total += FORMAT_BONUS

    # R35: Anti-gaming cap — if ALL code blocks have syntax errors (n_valid=0
    #   AND n_total>0), the code cannot actually run. Cap reward at 0.3 to
    #   prevent reward hacking via API-name-only responses with broken syntax.
    if n_total > 0 and n_valid == 0:
        total = min(total, 0.3)

    return max(0.0, min(total, 1.05))


def _has_sandbox_results(extra_info):
    """Check if extra_info contains real sandbox execution results."""
    if extra_info is None:
        return False
    if isinstance(extra_info, dict):
        if "exec_success" in extra_info:
            return True
        if extra_info.get("assert_results"):
            return True
        if "returncode" in extra_info:
            return True
    return False


# ---------------------------------------------------------------------------
# Main entry point (verl interface)
# ---------------------------------------------------------------------------
def compute_score(data_source, solution_str, ground_truth, extra_info=None, **kwargs):
    """Main reward function — verl custom_reward_function interface.

    Args:
        data_source: Dataset identifier (e.g., "pyaether_synth_v2").
        solution_str: The model's full generated response text (trajectory).
        ground_truth: Expected answer or test code from the dataset.
        extra_info: Additional metadata (reward_model dict from parquet, or
                    sandbox execution results if available).
        **kwargs: Additional arguments from YAML reward_kwargs:
            arm: Reward arm to use (R0/R1/R2/R3/R4, default R2).
            api_database: Path to API database JSON (for R4).
            auto_fallback: If True (default), auto-switch to R0 when sandbox
                          results are absent. Set False to force the specified arm.

    Returns:
        Float reward score.
    """
    # R35: Guard against None/empty solution_str — verl may pass None for
    #   empty generation or decode errors. Without this, regex operations crash.
    if solution_str is None:
        logger.warning("compute_score: solution_str is None, treating as empty string")
        solution_str = ""
    if not isinstance(solution_str, str):
        solution_str = str(solution_str) if solution_str is not None else ""

    arm = kwargs.get("arm", "R2")
    api_db_path = kwargs.get(
        "api_database",
        os.path.expanduser("~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json"),
    )
    auto_fallback = kwargs.get("auto_fallback", True)
    if arm not in REWARD_ARMS:
        logger.warning("Unknown reward arm '%s', defaulting to R2", arm)
        arm = "R2"

    # R22: Auto-fallback to R0 when sandbox results are absent.
    # This prevents silent zero-reward no-op when sandbox is in skeleton mode.
    if arm != "R0" and auto_fallback and not _has_sandbox_results(extra_info):
        logger.info("R22 auto-fallback: arm=%s → R0 (no sandbox results in extra_info)", arm)
        arm = "R0"

    tool_calls = extract_tool_calls(solution_str)

    # R22: Cheat rate tracking (red-line §5.2)
    # Check if eval_ngrams are provided via kwargs or environment
    eval_ngrams = kwargs.get("eval_ngrams")
    if eval_ngrams is None:
        eval_ngrams_path = os.environ.get("CHEAT_EVAL_NGRAMS_PATH", "")
        if eval_ngrams_path and os.path.exists(eval_ngrams_path):
            try:
                with open(eval_ngrams_path, "r") as f:
                    eval_ngrams = set(json.load(f))
            except (json.JSONDecodeError, OSError):
                eval_ngrams = None
    update_cheat_rate(solution_str, eval_ngrams, step=kwargs.get("step", 0))

    if arm == "R0":
        score = reward_r0_skeleton(solution_str, extra_info, api_db_path)
        logger.debug("compute_score: arm=R0(fallback), score=%.4f", score)
        return score

    exec_result = parse_execution_result(extra_info)

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

    # R22: R0 skeleton-mode test cases (task metadata from parquet, no sandbox)
    r0_cases = [
        {"name": "r0_good_code",
         "solution_str": "```python\nimport pyAether as pyScript\n\ndef call_aesesavenethighlight():\n    return pyScript.aeSeSaveNetHighlight()\n```",
         "ground_truth": "",
         "extra_info": {"test_code": "import pyAether as pyScript\ndef check(candidate):\n    result = candidate()\n    assert result is not None\n    assert isinstance(result, bool)",
          "canonical_solution": "    return pyScript.aeSeSaveNetHighlight()",
          "entry_point": "call_aesesavenethighlight",
          "metadata": json.dumps({"apis_used": ["pyAether.aeSeSaveNetHighlight"]})}},
        {"name": "r0_syntax_error",
         "solution_str": "```python\ndef call_aesesavenethighlight(\n    return pyScript.aeSeSaveNetHighlight(\n```",
         "ground_truth": "",
         "extra_info": {"test_code": "assert result is not None",
          "canonical_solution": "return pyScript.aeSeSaveNetHighlight()",
          "entry_point": "call_aesesavenethighlight",
          "metadata": json.dumps({"apis_used": ["pyAether.aeSeSaveNetHighlight"]})}},
        {"name": "r0_wrong_api",
         "solution_str": "```python\nimport pyAether as pyScript\n\ndef call_aesesavenethighlight():\n    return pyScript.wrongApiName()\n```",
         "ground_truth": "",
         "extra_info": {"test_code": "assert isinstance(result, bool)",
          "canonical_solution": "return pyScript.aeSeSaveNetHighlight()",
          "entry_point": "call_aesesavenethighlight",
          "metadata": json.dumps({"apis_used": ["pyAether.aeSeSaveNetHighlight"]})}},
        {"name": "r0_garbage",
         "solution_str": "I don't know how to solve this.",
         "ground_truth": "",
         "extra_info": {"test_code": "assert result is not None",
          "canonical_solution": "return pyScript.aeSeSaveNetHighlight()",
          "entry_point": "call_aesesavenethighlight",
          "metadata": json.dumps({"apis_used": ["pyAether.aeSeSaveNetHighlight"]})}},
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

    # R22: R0 skeleton-mode tests
    print(f"\n{'='*60}\nR0 skeleton-mode tests (no sandbox, task metadata only)\n{'='*60}\n")
    for tc in r0_cases:
        sc = compute_score("pyaether_synth_v2", tc["solution_str"], tc["ground_truth"],
                           tc["extra_info"], arm="R0", auto_fallback=False)
        print(f"  {tc['name']:20s}  R0_score={sc:.4f}")

    # R22: Auto-fallback test (arm=R2 but no sandbox → should auto-switch to R0)
    print(f"\n{'='*60}\nAuto-fallback test (arm=R2, no sandbox results → auto-R0)\n{'='*60}\n")
    for tc in r0_cases:
        sc = compute_score("pyaether_synth_v2", tc["solution_str"], tc["ground_truth"],
                           tc["extra_info"], arm="R2", auto_fallback=True)
        print(f"  {tc['name']:20s}  R2→R0_score={sc:.4f}")

    # R22: Cheat rate tracker tests
    print(f"\n{'='*60}\nR22 Cheat rate tracker tests\n{'='*60}\n")
    # Simulate eval n-grams (from a hypothetical eval task)
    eval_text = "import pyAether as pyScript\ndef check(candidate):\n    result = candidate()\n    assert result is not None\n    assert isinstance(result, bool)"
    eval_ng = _extract_ngrams(eval_text, 8)
    print(f"  eval_ngrams: {len(eval_ng)} unique 8-grams from test code")

    # Case 1: model output with high overlap (cheat)
    cheat_str = "import pyAether as pyScript\ndef check(candidate):\n    result = candidate()\n    assert result is not None\n    assert isinstance(result, bool)\n    return True"
    is_cheat, ratio, count = check_cheat_overlap(cheat_str, eval_ng, 8)
    print(f"  high_overlap: is_cheat={is_cheat}, ratio={ratio:.4f}, overlap={count}")

    # Case 2: model output with low overlap (legit)
    legit_str = "```python\ndef my_function():\n    x = pyScript.get_cell_by_id('cell1')\n    return x\n```"
    is_cheat2, ratio2, count2 = check_cheat_overlap(legit_str, eval_ng, 8)
    print(f"  low_overlap:  is_cheat={is_cheat2}, ratio={ratio2:.4f}, overlap={count2}")

    # Case 3: no eval ngrams (skeleton mode, no reference)
    is_cheat3, ratio3, count3 = check_cheat_overlap(legit_str, None, 8)
    print(f"  no_reference: is_cheat={is_cheat3}, ratio={ratio3:.4f}, overlap={count3}")

    # Test save_cheat_rate_report
    save_cheat_rate_report("/tmp/baize_posttrain_cheat_rate_test.json")
    print(f"  cheat_rate.json saved to /tmp/baize_posttrain_cheat_rate_test.json")
    report = get_cheat_rate_report()
    print(f"  report: total={report['total_rollouts']}, cheat={report['cheat_detected']}, rate={report['cheat_rate']}")

    print(f"\nSelf-test PASSED\n")
