#!/usr/bin/env python3
"""baize_posttrain_smoke_calibrator.py — R43: Day-1 Smoke Test Calibration & verl Config Lint

R43 (2026-11-08, wake91, zero GPU): Mathematical calibration of the expected
GRPO smoke test behavior + programmatic validation of the verl YAML config.

Three modules:
  1. Config Lint: Load YAML, validate all paths exist, check param ranges.
  2. Smoke Test Model: Mathematically model expected GRPO smoke test behavior.
  3. Decision Matrix: Pass/fail thresholds with GO/ADJUST/ABORT decision rules.

Usage:
  python3 baize_posttrain_smoke_calibrator.py                # Full calibration
  python3 baize_posttrain_smoke_calibrator.py --lint-only     # Config lint only
  python3 baize_posttrain_smoke_calibrator.py --html PATH     # Generate HTML report
  python3 baize_posttrain_smoke_calibrator.py --help

Dependencies: Python 3.8+ stdlib only. No numpy/scipy/yaml required.
WARNING: Surrogate RL results (MiniCPM5-2B) are NOT transferable to BaiZe.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "baize_posttrain_rl_verl_config_v2.yaml")  # R49: v2 (R47 fixes)

# R0 reward structure (from baize_posttrain_reward_functions.py lines 18-20)
R0_COMPONENTS = {
    "syntax_valid": 0.1, "api_correct": 0.3, "entry_point": 0.2,
    "structure": 0.2, "test_alignment": 0.2, "format_bonus": 0.02,
}
R0_MAX = sum(R0_COMPONENTS.values())  # 1.02, verl caps at 1.0

SMOKE_ITERS = 10
SMOKE_GROUP_SIZE = 4
SMOKE_BATCH = 16
SMOKE_CONCURRENCY = 2
FULL_GROUP_SIZE = 8
FULL_BATCH = 128

TASK_TOTAL = 3347
DIFFICULTY_DIST = {
    "L1": 1500, "L2": 347, "L3": 800, "L4": 500, "L5": 200,
}

# Expected probability of each R0 component being satisfied (36% baseline model)
EXPECTED_COMPONENT_PROB = {
    "L1": {"syntax_valid": 0.85, "api_correct": 0.55, "entry_point": 0.70,
           "structure": 0.65, "test_alignment": 0.50, "format_bonus": 0.60},
    "L2": {"syntax_valid": 0.80, "api_correct": 0.40, "entry_point": 0.55,
           "structure": 0.50, "test_alignment": 0.35, "format_bonus": 0.50},
    "L3": {"syntax_valid": 0.70, "api_correct": 0.25, "entry_point": 0.40,
           "structure": 0.35, "test_alignment": 0.20, "format_bonus": 0.40},
    "L4": {"syntax_valid": 0.55, "api_correct": 0.15, "entry_point": 0.25,
           "structure": 0.20, "test_alignment": 0.10, "format_bonus": 0.30},
    "L5": {"syntax_valid": 0.40, "api_correct": 0.08, "entry_point": 0.15,
           "structure": 0.10, "test_alignment": 0.05, "format_bonus": 0.20},
}


# ---------------------------------------------------------------------------
# Module 1: Minimal YAML Parser (no pyyaml dependency)
# ---------------------------------------------------------------------------
def parse_yaml_simple(text: str) -> Dict[str, Any]:
    """Parse a subset of YAML sufficient for our config file."""
    lines = []
    for line in text.split("\n"):
        in_quote = False
        clean = []
        i = 0
        while i < len(line):
            c = line[i]
            if c in ('"', "'"):
                in_quote = not in_quote
            if c == "#" and not in_quote:
                break
            clean.append(c)
            i += 1
        lines.append("".join(clean).rstrip())

    root: Dict[str, Any] = {}
    stack: List[Tuple[int, Dict[str, Any]]] = [(0, root)]

    for line in lines:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        while stack and stack[-1][0] > indent:
            stack.pop()
        if not stack:
            stack = [(0, root)]

        if stripped.startswith("- "):
            key = "_list"
            val_str = stripped[2:].strip()
            parent = stack[-1][1]
            if key not in parent:
                parent[key] = []
            if ":" in val_str and not val_str.startswith('"'):
                parts = val_str.split(":", 1)
                k = parts[0].strip()
                v = parts[1].strip() if len(parts) > 1 else ""
                parent[key].append({k: _parse_scalar(v)})
            else:
                parent[key].append(_parse_scalar(val_str))
            continue

        if ":" in stripped:
            parts = stripped.split(":", 1)
            key = parts[0].strip()
            val_str = parts[1].strip() if len(parts) > 1 else ""
            if val_str == "":
                new_dict: Dict[str, Any] = {}
                stack[-1][1][key] = new_dict
                stack.append((indent + 2, new_dict))
            else:
                stack[-1][1][key] = _parse_scalar(val_str)
    return root


def _parse_scalar(s: str) -> Any:
    s = s.strip()
    if s in ("null", "~", ""):
        return None
    if s in ("true", "True"):
        return True
    if s in ("false", "False"):
        return False
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


# ---------------------------------------------------------------------------
# Module 2: Config Lint
# ---------------------------------------------------------------------------
class LintResult:
    def __init__(self):
        self.passed: List[str] = []
        self.warnings: List[str] = []
        self.failed: List[str] = []

    def pass_(self, msg): self.passed.append(msg)
    def warn(self, msg): self.warnings.append(msg)
    def fail(self, msg): self.failed.append(msg)
    def summary(self): return f"PASS={len(self.passed)} WARN={len(self.warnings)} FAIL={len(self.failed)}"


def lint_config(config: Dict[str, Any], result: LintResult):
    """Validate the verl config against expected structure and constraints."""
    data = config.get("data", {})
    tokenizer = data.get("tokenizer", "")
    if tokenizer and os.path.isdir(tokenizer):
        result.pass_(f"data.tokenizer path exists: {tokenizer}")
    else:
        result.fail(f"data.tokenizer path missing: {tokenizer}")

    train_file = data.get("train_files", "")
    train_full = os.path.join(SCRIPT_DIR, str(train_file)) if train_file else ""
    if train_full and os.path.isfile(train_full):
        size = os.path.getsize(train_full)
        result.pass_(f"data.train_files exists: {train_file} ({size} bytes)")
    else:
        result.fail(f"data.train_files missing: {train_file}")

    batch = data.get("train_batch_size", 0)
    if 16 <= int(batch) <= 512:
        result.pass_(f"data.train_batch_size in range: {batch}")
    else:
        result.warn(f"data.train_batch_size unusual: {batch}")

    max_prompt = int(data.get("max_prompt_length", 0))
    max_resp = int(data.get("max_response_length", 0))
    total_ctx = max_prompt + max_resp
    if total_ctx == 8192:
        result.pass_(f"Total context = {total_ctx} (4096+4096)")
    else:
        result.warn(f"Total context = {total_ctx} (expected 8192)")

    if data.get("return_raw_chat") == True:
        result.pass_("data.return_raw_chat=True (required for multi-turn)")
    else:
        result.fail("data.return_raw_chat must be True for SGLang multi-turn")

    if data.get("need_tools_kwargs") == True:
        result.pass_("data.need_tools_kwargs=True (tool injection enabled)")
    else:
        result.fail("data.need_tools_kwargs must be True for Tool Agent Loop")

    if data.get("truncation") == "error":
        result.pass_("data.truncation=error (will alert on truncation)")
    else:
        result.warn(f"data.truncation={data.get('truncation')} (expected 'error')")
    return result


def lint_config_extended(config: Dict[str, Any], result: LintResult):
    """Extended lint: actor, rollout, algorithm, reward, trainer, runtime, smoke."""
    actor = config.get("actor_rollout_ref", {}).get("actor", {})
    clip = float(actor.get("clip_ratio", 0))
    if 0.1 <= clip <= 0.3:
        result.pass_(f"actor.clip_ratio in range: {clip}")
    else:
        result.warn(f"actor.clip_ratio unusual: {clip}")

    kl_coef = float(actor.get("kl_loss_coef", 0))
    if 0.005 <= kl_coef <= 0.1:
        result.pass_(f"actor.kl_loss_coef in range: {kl_coef}")
    else:
        result.warn(f"actor.kl_loss_coef unusual: {kl_coef}")

    entropy = float(actor.get("entropy_coeff", 0))
    if entropy > 0:
        result.pass_(f"actor.entropy_coeff > 0: {entropy} (prevents collapse)")
    else:
        result.fail(f"actor.entropy_coeff = {entropy} (must be >0)")

    if actor.get("use_kl_loss") == True:
        result.pass_("actor.use_kl_loss=True (required for GRPO)")
    else:
        result.fail("actor.use_kl_loss must be True for GRPO")

    if actor.get("entropy_checkpointing") == True:
        result.pass_("actor.entropy_checkpointing=True (memory optimization)")
    else:
        result.warn("actor.entropy_checkpointing not enabled (may OOM on A40)")

    lr = float(actor.get("optim", {}).get("lr", 0))
    if 1e-7 <= lr <= 1e-4:
        result.pass_(f"actor.optim.lr in range: {lr}")
    else:
        result.warn(f"actor.optim.lr unusual: {lr}")

    rollout = config.get("actor_rollout_ref", {}).get("rollout", {})
    if rollout.get("name") == "sglang":
        result.pass_("rollout.name=sglang (R9: required for MiniCPM5 XML tool calls)")
    else:
        result.fail(f"rollout.name={rollout.get('name')} (must be 'sglang' per R9)")

    if rollout.get("multi_turn"):
        mt = rollout.get("multi_turn")
        if isinstance(mt, dict):
            if mt.get("enable") == True:
                result.pass_("rollout.multi_turn.enable=True (multi-turn tool calling)")
            else:
                result.fail(f"rollout.multi_turn.enable={mt.get('enable')} (must be True)")
        else:
            result.pass_("rollout.multi_turn=True (enables multi-turn tool calling)")
    else:
        result.fail("rollout.multi_turn must be set for EDA tool interaction")

    mem_util = float(rollout.get("gpu_memory_utilization", 0))
    if 0.3 <= mem_util <= 0.7:
        result.pass_(f"rollout.gpu_memory_utilization in range: {mem_util}")
    else:
        result.warn(f"rollout.gpu_memory_utilization unusual: {mem_util}")

    algo = config.get("algorithm", {})
    if algo.get("name") == "grpo":
        result.pass_("algorithm.name=grpo")
    else:
        result.fail(f"algorithm.name={algo.get('name')} (must be 'grpo')")

    group_size = int(algo.get("group_size", 0))
    if 4 <= group_size <= 16:
        result.pass_(f"algorithm.group_size in range: {group_size}")
    else:
        result.warn(f"algorithm.group_size unusual: {group_size}")

    if algo.get("filter_groups") == True:
        result.pass_("algorithm.filter_groups=True (sGPO: drops all-correct/all-wrong)")
    else:
        result.warn("algorithm.filter_groups not enabled (recommended)")

    reward = config.get("reward", {})
    crf = reward.get("custom_reward_function", {})
    rpath = crf.get("path", "")
    rfull = os.path.join(SCRIPT_DIR, str(rpath)) if rpath else ""
    if rfull and os.path.isfile(rfull):
        result.pass_(f"reward.path exists: {rpath}")
    else:
        result.fail(f"reward.path missing: {rpath}")

    rname = crf.get("name", "")
    if rname == "compute_score":
        result.pass_("reward.name=compute_score")
    else:
        result.fail(f"reward.name={rname} (expected 'compute_score')")

    auto_fb = crf.get("reward_kwargs", {}).get("auto_fallback", False)
    if auto_fb == True:
        result.pass_("reward.auto_fallback=True (R22: sandbox fallback)")
    else:
        result.warn("reward.auto_fallback not enabled (R22 recommends True)")

    ac = reward.get("anti_cheat", {})
    if ac.get("enabled") == True:
        result.pass_("anti_cheat.enabled=True (red-line 5.2)")
    else:
        result.fail("anti_cheat.enabled must be True (red-line 5.2)")

    trainer = config.get("trainer", {})
    n_gpus = int(trainer.get("n_gpus_per_node", 0))
    if n_gpus == 4:
        result.pass_("trainer.n_gpus_per_node=4 (4xA40)")
    else:
        result.warn(f"trainer.n_gpus_per_node={n_gpus} (expected 4)")

    smoke = config.get("smoke", {})
    if int(smoke.get("iters", 0)) == 10:
        result.pass_("smoke.iters=10")
    else:
        result.warn(f"smoke.iters={smoke.get('iters')} (expected 10)")

    # Cross-reference: launch script uses R0 (R42 fix)
    launch = os.path.join(SCRIPT_DIR, "baize_posttrain_launch_11_9.sh")
    if os.path.isfile(launch):
        if "--reward-arm R0" in open(launch).read():
            result.pass_("launch script uses --reward-arm R0 (R42 fix verified)")
        else:
            result.fail("launch script does NOT use R0 (R42 fix missing!)")

    # Cross-reference: runbook references R0
    runbook = os.path.join(SCRIPT_DIR, "baize_posttrain_day1_runbook.sh")
    if os.path.isfile(runbook):
        if "R0" in open(runbook).read():
            result.pass_("day1_runbook references R0")
        else:
            result.warn("day1_runbook does not reference R0")

    return result


# ---------------------------------------------------------------------------
# Module 3: Smoke Test Mathematical Model
# ---------------------------------------------------------------------------
def model_r0_reward(difficulty: str) -> Tuple[float, float]:
    """Model expected R0 reward for a given difficulty level."""
    probs = EXPECTED_COMPONENT_PROB.get(difficulty, EXPECTED_COMPONENT_PROB["L3"])
    mean = 0.0
    var = 0.0
    for comp, weight in R0_COMPONENTS.items():
        p = probs.get(comp, 0.3)
        mean += weight * p
        var += (weight ** 2) * p * (1 - p)
    return min(mean, 1.0), math.sqrt(var)


def model_smoke_test() -> Dict[str, Any]:
    """Model the full smoke test: 10 iters, group_size=4, batch=16."""
    per_diff = {}
    for diff, count in DIFFICULTY_DIST.items():
        mean, std = model_r0_reward(diff)
        per_diff[diff] = {"count": count, "mean_reward": mean, "std_reward": std}

    total_count = sum(d["count"] for d in per_diff.values())
    overall_mean = sum(d["mean_reward"] * d["count"] for d in per_diff.values()) / total_count
    within_var = sum(d["std_reward"]**2 * d["count"] for d in per_diff.values()) / total_count
    between_var = sum(d["mean_reward"]**2 * d["count"] for d in per_diff.values()) / total_count - overall_mean**2
    overall_std = math.sqrt(within_var + between_var)

    total_rollouts = SMOKE_ITERS * SMOKE_BATCH * SMOKE_GROUP_SIZE
    eff_low, eff_high = int(160 * 0.70), int(160 * 0.85)

    return {
        "per_difficulty": per_diff,
        "overall_mean_reward": overall_mean,
        "overall_std_reward": overall_std,
        "total_rollouts": total_rollouts,
        "effective_groups_range": (eff_low, eff_high),
        "expected_delta_reward": 0.01,
        "expected_kl": 0.02,
        "expected_loss": -overall_mean * 0.5,
        "smoke_iters": SMOKE_ITERS,
        "smoke_group_size": SMOKE_GROUP_SIZE,
        "smoke_batch": SMOKE_BATCH,
        "task_total": TASK_TOTAL,
    }


# ---------------------------------------------------------------------------
# Module 4: Decision Matrix
# ---------------------------------------------------------------------------
def build_decision_matrix(model: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build the pass/fail decision matrix for Day-1 smoke test evaluation."""
    mean_r = model["overall_mean_reward"]
    std_r = model["overall_std_reward"]
    eg = model["effective_groups_range"]
    decisions = [
        {"metric": "Mean reward (R0)", "expected": f"{mean_r:.3f} +/- {std_r:.3f}",
         "pass_threshold": f">= {max(0.15, mean_r - 2*std_r):.3f}",
         "adjust_threshold": f"{max(0.10, mean_r - 3*std_r):.3f} - {max(0.15, mean_r - 2*std_r):.3f}",
         "abort_threshold": f"< {max(0.10, mean_r - 3*std_r):.3f} or > {min(1.0, mean_r + 3*std_r):.3f}",
         "rationale": "R0 range 0-1.02. Mean ~0.3-0.5 expected. Too low = gibberish; too high = reward bug."},
        {"metric": "Reward std (within group)", "expected": f"~{std_r:.3f}",
         "pass_threshold": ">= 0.05 (non-zero variance)",
         "adjust_threshold": "0.01 - 0.05",
         "abort_threshold": "< 0.01 (all identical -> GRPO no-op)",
         "rationale": "Identical rewards in group -> advantage=0 -> no gradient. #1 failure mode."},
        {"metric": "Effective groups (after filter)", "expected": f"{eg[0]}-{eg[1]} / 160",
         "pass_threshold": f">= {eg[0]} (>=70%)",
         "adjust_threshold": f"{int(160*0.5)} - {eg[0]}",
         "abort_threshold": f"< {int(160*0.5)} (<50% -> too sparse)",
         "rationale": "filter_groups drops all-correct/all-wrong. >50% dropped = too sparse."},
        {"metric": "Reward trajectory (iter 1->10)", "expected": "flat or +0.010",
         "pass_threshold": "delta >= -0.02 (not collapsing)",
         "adjust_threshold": "delta in [-0.05, -0.02]",
         "abort_threshold": "delta < -0.05 (collapse) or NaN/Inf",
         "rationale": "10 iters with lr=3e-6 = tiny change. Collapse = KL weak or lr high."},
        {"metric": "KL divergence", "expected": "~0.020",
         "pass_threshold": "< 0.15",
         "adjust_threshold": "0.15 - 0.30",
         "abort_threshold": "> 0.30 (diverging) or NaN",
         "rationale": "GRPO KL should stay low. kl_coef=0.02 should keep it bounded."},
        {"metric": "Policy loss", "expected": f"~{model['expected_loss']:.3f}",
         "pass_threshold": "finite and bounded [-5, 0]",
         "adjust_threshold": "[-10, -5] or [0, 1]",
         "abort_threshold": "NaN, Inf, or > 1.0",
         "rationale": "PPO loss should be negative. Positive = sign error. NaN = gradient explosion."},
        {"metric": "Gradient norm", "expected": "~0.1 - 1.0",
         "pass_threshold": "< 5.0 (grad_clip=1.0 active)",
         "adjust_threshold": "5.0 - 10.0 (frequent clipping)",
         "abort_threshold": "> 10.0 or NaN",
         "rationale": "grad_clip=1.0 should keep norms bounded. Frequent clipping = lr too high."},
        {"metric": "Cheat rate (anti-cheat)", "expected": "0.0 (skeleton mode)",
         "pass_threshold": "0.0%",
         "adjust_threshold": "N/A",
         "abort_threshold": "> 0% (red-line violation 5.2)",
         "rationale": "R0 skeleton mode with synthetic tasks: cheat rate must be 0."},
        {"metric": "Exit code", "expected": "0",
         "pass_threshold": "0", "adjust_threshold": "N/A",
         "abort_threshold": "non-zero (OOM, CUDA error, config error)",
         "rationale": "verl should exit cleanly. Non-zero = check log file."},
        {"metric": "Wall clock (smoke test)", "expected": "20-40 min (R0, no sandbox)",
         "pass_threshold": "< 60 min",
         "adjust_threshold": "60-90 min",
         "abort_threshold": "> 90 min or < 5 min",
         "rationale": "R0 needs no sandbox. < 5 min = crashed early; > 90 min = bottleneck."},
    ]
    return decisions


# ---------------------------------------------------------------------------
# Module 5: HTML Report Generator
# ---------------------------------------------------------------------------
def generate_html(model, decisions, lint):
    mean_r = model["overall_mean_reward"]
    std_r = model["overall_std_reward"]
    diff_rows = ""
    for diff in ["L1", "L2", "L3", "L4", "L5"]:
        d = model["per_difficulty"][diff]
        pct = d["count"] / model["task_total"] * 100
        diff_rows += f"<tr><td><b>{diff}</b></td><td>{d['count']}</td><td>{pct:.1f}%</td><td>{d['mean_reward']:.4f}</td><td>{d['std_reward']:.4f}</td></tr>"
    dec_rows = ""
    for d in decisions:
        dec_rows += f"<tr><td><b>{d['metric']}</b></td><td>{d['expected']}</td><td class='pt'>{d['pass_threshold']}</td><td class='at'>{d['adjust_threshold']}</td><td class='ab'>{d['abort_threshold']}</td><td>{d['rationale']}</td></tr>"
    lint_pass = "".join(f"<li>PASS {p}</li>" for p in lint.passed)
    lint_warn = "".join(f"<li>WARN {w}</li>" for w in lint.warnings)
    lint_fail = "".join(f"<li>FAIL {f}</li>" for f in lint.failed)
    eg = model["effective_groups_range"]
    abort_low = max(0.10, mean_r - 3*std_r)
    return _html_template(mean_r, std_r, diff_rows, dec_rows, lint, lint_pass, lint_warn, lint_fail, model, eg, abort_low)


def _html_template(mean_r, std_r, diff_rows, dec_rows, lint, lp, lw, lf, model, eg, abort_low):
    css = "body{font-family:sans-serif;max-width:1200px;margin:0 auto;padding:20px;background:#f8f9fa;color:#222}"
    css += "h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:10px}h2{color:#2874a6;margin-top:30px}"
    css += "table{border-collapse:collapse;width:100%;margin:15px 0;background:#fff}"
    css += "th,td{border:1px solid #ddd;padding:8px 12px;text-align:left;font-size:14px}th{background:#2980b9;color:#fff}tr:nth-child(even){background:#f2f2f2}"
    css += ".pt{background:#d4edda;font-weight:600}.at{background:#fff3cd}.ab{background:#f8d7da;font-weight:600}"
    css += ".box{background:#fff;border-radius:8px;padding:20px;margin:15px 0;box-shadow:0 2px 4px rgba(0,0,0,.1)}"
    css += ".go{background:#d4edda;border:2px solid #28a745;padding:15px;border-radius:8px;text-align:center;font-size:18px;font-weight:700}"
    css += ".warn{background:#fff3cd;border:1px solid #ffc107;padding:12px;border-radius:6px;margin:10px 0}"
    css += ".hl{font-size:24px;font-weight:700;color:#2980b9}"
    head = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>R43 Day-1 Smoke Test Calibration</title>
<style>{css}</style></head><body>
<h1>R43: Day-1 Smoke Test Calibration &amp; verl Config Lint</h1>
<p><small>R43 - 2026-11-08 - wake91 - zero GPU - pure Python stdlib</small></p>
<div class="box"><h3>Summary</h3>
<p>Mathematical calibration of expected GRPO smoke test behavior + verl config validation.</p>
<div class="go">Expected smoke test mean reward: <span class="hl">{mean_r:.3f}</span> +/- {std_r:.3f}<br>
Decision matrix: 10 metrics - 3-level thresholds (PASS/ADJUST/ABORT)<br>
Config lint: {lint.summary()}</div></div>"""
    return head + _html_body(mean_r, std_r, diff_rows, dec_rows, lint, lp, lw, lf, model, eg, abort_low)



def _html_body(mean_r, std_r, diff_rows, dec_rows, lint, lp, lw, lf, model, eg, abort_low):
    return f"""
<h2>1. R0 Reward Structure</h2>
<div class="box"><p>R0 (skeleton-mode fallback) is the smoke test reward arm (R42 fix).</p>
<table><tr><th>Component</th><th>Weight</th><th>Judgment</th></tr>
<tr><td>syntax_valid</td><td>0.10</td><td>AST parse success</td></tr>
<tr><td>api_correct</td><td>0.30</td><td>API names in knowledge base</td></tr>
<tr><td>entry_point</td><td>0.20</td><td>Contains def check(candidate)</td></tr>
<tr><td>structure</td><td>0.20</td><td>Code structure (assert/return)</td></tr>
<tr><td>test_alignment</td><td>0.20</td><td>Assertions align with task</td></tr>
<tr><td>format_bonus</td><td>0.02</td><td>Format (XML/tool call)</td></tr>
<tr><td><b>Max</b></td><td><b>1.02</b></td><td>verl caps at 1.0</td></tr></table>
<div class="warn">R0 has 6 Bernoulli components - discrete reward. group_size=4: some groups all-identical -> dropped. Effective: 70-85%.</div></div>

<h2>2. Expected Reward per Difficulty</h2>
<div class="box"><table><tr><th>Level</th><th>Tasks</th><th>Share</th><th>Mean</th><th>Std</th></tr>
{diff_rows}
<tr style="font-weight:700;background:#eaf2f8"><td>Total</td><td>{model['task_total']}</td><td>100%</td><td>{mean_r:.4f}</td><td>{std_r:.4f}</td></tr></table>
<p><b>Interpretation</b>: Weighted avg ~{mean_r:.2f}, std ~{std_r:.2f}. Variance sufficient for GRPO non-zero advantages.</p></div>

<h2>3. GRPO Smoke Test Model</h2>
<div class="box"><table><tr><th>Param</th><th>Value</th></tr>
<tr><td>Iterations</td><td>{model['smoke_iters']}</td></tr>
<tr><td>Group size</td><td>{model['smoke_group_size']}</td></tr>
<tr><td>Prompts/iter</td><td>{model['smoke_batch']}</td></tr>
<tr><td>Total rollouts</td><td>{model['total_rollouts']}</td></tr>
<tr><td>Effective groups</td><td>{eg[0]}-{eg[1]} / 160</td></tr>
<tr><td>Reward arm</td><td>R0 (R42 fix)</td></tr>
<tr><td>Learning rate</td><td>3e-6</td></tr>
<tr><td>KL coef</td><td>0.02</td></tr></table>
<h3>Expected Dynamics</h3>
<table><tr><th>Metric</th><th>Expected</th></tr>
<tr><td>Mean reward iter 1</td><td>{mean_r:.3f}</td></tr>
<tr><td>Mean reward iter 10</td><td>{mean_r + model['expected_delta_reward']:.3f}</td></tr>
<tr><td>KL divergence</td><td>~{model['expected_kl']:.3f}</td></tr>
<tr><td>Policy loss</td><td>~{model['expected_loss']:.3f}</td></tr></table>
<div class="warn"><b>Key</b>: 10-iter smoke test validates pipeline, NOT performance. Expected: non-zero reward+variance, finite loss, bounded KL, exit=0.</div></div>""" + _html_tail(dec_rows, lint, lp, lw, lf, abort_low)


def _html_tail(dec_rows, lint, lp, lw, lf, abort_low):
    return f"""
<h2>4. Day-1 Decision Matrix</h2>
<div class="box"><table><tr><th>Metric</th><th>Expected</th><th style="background:#28a745">PASS</th><th style="background:#ffc107">ADJUST</th><th style="background:#dc3545">ABORT</th><th>Rationale</th></tr>
{dec_rows}</table></div>

<h2>5. verl Config Lint</h2>
<div class="box"><h3>Results: {lint.summary()}</h3>
<details><summary>PASS ({len(lint.passed)})</summary><ul>{lp}</ul></details>
<details><summary>WARN ({len(lint.warnings)})</summary><ul>{lw}</ul></details>
<details><summary>FAIL ({len(lint.failed)})</summary><ul>{lf}</ul></details></div>

<h2>6. Day-1 Decision Flow</h2>
<div class="box"><pre style="background:#1e1e1e;color:#d4d4d4;padding:15px;border-radius:6px;font-size:13px">
Smoke test completed
    +-- Exit != 0? -> ABORT: check log
    +-- Mean reward < {abort_low:.3f}? -> ABORT: gibberish
    +-- Reward std < 0.01? -> ABORT: GRPO no-op
    +-- Effective groups < 80? -> ADJUST: increase group_size
    +-- KL > 0.30? -> ADJUST: increase kl_coef
    +-- Cheat rate > 0%? -> ABORT: red-line violation
    +-- All PASS? -> GO: bash baize_posttrain_rl_grpo.sh --reward-arm R0 --gpu-ids 0,1,2,3
</pre></div>

<h2>7. Limitations</h2>
<div class="box"><ul>
<li>Component probabilities extrapolated from DeepSeek-side data, not measured on MiniCPM5-2B.</li>
<li>R0 reward discreteness: 6 Bernoulli -> finite values.</li>
<li>10 iters insufficient for convergence - validates pipeline only.</li>
<li>Surrogate warning: MiniCPM5-2B RL results NOT transferable to BaiZe.</li>
</ul></div>
<p style="text-align:center;color:#888;margin-top:30px">R43 - BaiZe Post-Train - 2026-11-08 - self-contained</p>
</body></html>"""


def main():
    parser = argparse.ArgumentParser(description="R43: Day-1 Smoke Test Calibration")
    parser.add_argument("--lint-only", action="store_true")
    parser.add_argument("--html", type=str, default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not os.path.isfile(CONFIG_PATH):
        print(f"Config not found: {CONFIG_PATH}"); sys.exit(1)
    with open(CONFIG_PATH) as f:
        config = parse_yaml_simple(f.read())

    lint = LintResult()
    lint_config(config, lint)
    lint_config_extended(config, lint)
    print(f"\n{'='*60}\n  R43 Config Lint: {lint.summary()}\n{'='*60}")
    for p in lint.passed: print(f"  PASS {p}")
    for w in lint.warnings: print(f"  WARN {w}")
    for f_ in lint.failed: print(f"  FAIL {f_}")

    if args.lint_only:
        sys.exit(1 if lint.failed else 0)

    model = model_smoke_test()
    print(f"\n{'='*60}\n  R43 Smoke Test Model\n{'='*60}")
    print(f"  Mean reward:  {model['overall_mean_reward']:.4f}")
    print(f"  Std reward:   {model['overall_std_reward']:.4f}")
    print(f"  Rollouts:     {model['total_rollouts']}")
    eg = model['effective_groups_range']
    print(f"  Eff groups:   {eg[0]}-{eg[1]} / 160")
    for diff in ["L1", "L2", "L3", "L4", "L5"]:
        d = model["per_difficulty"][diff]
        print(f"    {diff}: mean={d['mean_reward']:.4f} std={d['std_reward']:.4f} (n={d['count']})")

    decisions = build_decision_matrix(model)
    print(f"\n  Decision Matrix ({len(decisions)} metrics):")
    for d in decisions:
        print(f"  {d['metric']}: PASS={d['pass_threshold']} ABORT={d['abort_threshold']}")

    if args.html:
        html = generate_html(model, decisions, lint)
        with open(args.html, "w") as f:
            f.write(html)
        print(f"\n  HTML: {args.html} ({len(html)} bytes)")

    print(f"\n{'='*60}")
    if lint.failed:
        print("  CONFIG LINT FAILED"); sys.exit(1)
    else:
        print(f"  PASS. Expected reward: {model['overall_mean_reward']:.3f} +/- {model['overall_std_reward']:.3f}")
        sys.exit(0)


if __name__ == "__main__":
    main()