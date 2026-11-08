#!/usr/bin/env python3
"""baize_posttrain_day1_diag.py — R62: Day-1 Cold-Start Warm-up + Smoke Test Diagnostic Classifier

R62 (2026-11-08, wake110, zero GPU): On the eve of 11/9 GPU arrival, this tool
addresses two critical Day-1 risks that existing scripts (R36 monitor, R43
calibrator, R38 runbook) do not cover:

1. NFS Cold-Start Latency: R45 measured torch import >30s on first NFS access.
   On Day-1, the first import of torch/verl/sglang/ray from NFS will be slow
   and could cause false-negative preflight diagnostics (timeout misreads as
   "missing dependency"). This tool performs structured warm-up with timing.

2. Smoke Test Output Classification: R38 runbook has text-level decision trees,
   R43 calibrator models expected behavior mathematically, R36 monitor detects
   divergence during training. But none automatically classify the SMOKE TEST
   OUTPUT (10 iters) into GO/WARN/DEBUG/ABORT with specific remediation. This
   tool parses verl stdout logs and produces an actionable verdict.

Vision-line failure pattern detection (R57 lessons):
  - std=0 dominance >60% -> zero gradient (vision v1/v3 pattern)
  - loss ~0 with reward variance -> policy gradient too weak (vision v3 pattern)
  - reward collapse -> all rollouts fail
  - KL explosion -> policy drift
  - NaN/Inf -> numerical instability
  - cheat rate >5% -> reward hacking (red-line 5.2)

Usage:
  python3 baize_posttrain_day1_diag.py --warmup              # NFS warm-up with timing
  python3 baize_posttrain_day1_diag.py --classify <log_path> # Classify smoke test output
  python3 baize_posttrain_day1_diag.py --warmup --classify <log_path>  # Both
  python3 baize_posttrain_day1_diag.py --html <output.html>  # Generate HTML report
  python3 baize_posttrain_day1_diag.py --help

Dependencies: Python 3.8+ stdlib only. No numpy/yaml required.
WARNING: Surrogate RL results (MiniCPM5-2B) are NOT transferable to BaiZe.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Vision-line failure thresholds (R57: calibrated from vision GRPO 4 rounds)
# Vision v1: std=0 = 78.7% (G=4) / 73.0% (G=8) -> zero gradient -> training failed
# Vision v3: loss~0 + reward variance -> policy gradient too weak
# BaiZe advantage: 36% base >> 9.2% -> P(mixed signal) = 97.2% (R57 section 4)
VISION_THRESHOLDS = {
    "std_zero_pct_warn": 60.0,
    "std_zero_pct_abort": 80.0,
    "loss_near_zero": 1e-4,
    "reward_variance_high": 0.3,
    "reward_floor": 0.01,
    "kl_max": 10.0,
    "entropy_floor": 0.1,
    "grad_max": 100.0,
    "cheat_max": 0.05,
    "nan_inf": True,
}

# R0 reward expected behavior (from R43 calibrator)
R0_EXPECTED = {
    "mean_range": (0.15, 0.55),
    "std_range": (0.05, 0.50),
    "min_iters_completed": 8,
}

WARMUP_IMPORTS = [
    ("torch", "import torch"),
    ("torch.cuda", "import torch; torch.cuda.is_available()"),
    ("transformers", "import transformers"),
    ("sglang", "import sglang"),
    ("verl", "import verl"),
    ("ray", "import ray"),
    ("flash_attn", "import flash_attn"),
]

WARMUP_MODEL_FILES = [
    "/tmp/models/MiniCPM5-2B/config.json",
    "/tmp/models/MiniCPM5-2B/model.safetensors",
    "/tmp/models/MiniCPM5-2B/tokenizer.json",
]

# ============================================================================
# Module 1: NFS Cold-Start Warm-up
# ============================================================================

def warmup_import(name, code, venv_python):
    """Time a single import in the target venv. Returns timing + status."""
    t0 = time.time()
    try:
        result = subprocess.run(
            [venv_python, "-c", code],
            capture_output=True, text=True, timeout=120
        )
        elapsed = time.time() - t0
        if result.returncode == 0:
            status = "OK" if elapsed < 30 else "SLOW"
        else:
            status = "FAIL"
        return {
            "name": name,
            "elapsed_s": round(elapsed, 2),
            "status": status,
            "stderr": result.stderr.strip()[:500] if result.returncode != 0 else "",
        }
    except subprocess.TimeoutExpired:
        return {"name": name, "elapsed_s": 120.0, "status": "TIMEOUT",
                "stderr": "Import timed out after 120s (NFS cold start?)"}
    except FileNotFoundError:
        return {"name": name, "elapsed_s": 0.0, "status": "NO_VENV",
                "stderr": "Python not found: " + venv_python}


def warmup_file(path):
    """Pre-touch a file to warm NFS cache. Read first/last 4KB."""
    t0 = time.time()
    try:
        p = Path(path)
        if not p.exists():
            return {"path": path, "elapsed_s": 0.0, "status": "MISSING", "size_mb": 0}
        size = p.stat().st_size
        with open(path, "rb") as f:
            f.read(4096)
            if size > 8192:
                f.seek(-4096, 2)
                f.read(4096)
        elapsed = time.time() - t0
        return {"path": path, "elapsed_s": round(elapsed, 3),
                "status": "OK" if elapsed < 5 else "SLOW",
                "size_mb": round(size / 1048576, 1)}
    except Exception as e:
        return {"path": path, "elapsed_s": 0.0, "status": "ERROR", "error": str(e)}


def do_warmup(venv_python):
    """Perform full NFS warm-up sequence."""
    print("=" * 70)
    print("  R62 Day-1 NFS Cold-Start Warm-up")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("  Venv: " + venv_python)
    print("=" * 70)

    results = {"timestamp": datetime.now().isoformat(), "venv": venv_python,
               "imports": [], "files": [], "summary": {}}

    print("\n--- Phase 1: Import Warm-up ---")
    total_import_time = 0
    for name, code in WARMUP_IMPORTS:
        r = warmup_import(name, code, venv_python)
        results["imports"].append(r)
        total_import_time += r["elapsed_s"]
        icons = {"OK": "[OK]", "SLOW": "[SLOW]", "FAIL": "[FAIL]",
                 "TIMEOUT": "[TIMEOUT]", "NO_VENV": "[NO_VENV]"}
        icon = icons.get(r["status"], "[?]")
        print("  %s %-20s %7.2fs  %s" % (icon, name, r["elapsed_s"], r["status"]))
        if r["status"] == "FAIL":
            print("     stderr: " + r["stderr"][:200])

    print("\n--- Phase 2: Model File Warm-up ---")
    for path in WARMUP_MODEL_FILES:
        r = warmup_file(path)
        results["files"].append(r)
        icons = {"OK": "[OK]", "SLOW": "[SLOW]", "MISSING": "[MISSING]", "ERROR": "[ERROR]"}
        icon = icons.get(r["status"], "[?]")
        size_str = "%.1fMB" % r.get("size_mb", 0) if r.get("size_mb") else "-"
        print("  %s %-25s %6.3fs  %-8s %s" % (icon, os.path.basename(path),
                                               r["elapsed_s"], r["status"], size_str))

    ok_imports = sum(1 for r in results["imports"] if r["status"] == "OK")
    slow_imports = sum(1 for r in results["imports"] if r["status"] == "SLOW")
    fail_imports = sum(1 for r in results["imports"] if r["status"] in ("FAIL", "TIMEOUT", "NO_VENV"))
    ok_files = sum(1 for r in results["files"] if r["status"] == "OK")

    results["summary"] = {
        "total_import_time_s": round(total_import_time, 1),
        "ok_imports": ok_imports, "slow_imports": slow_imports, "fail_imports": fail_imports,
        "ok_files": ok_files,
        "cold_start_detected": slow_imports > 0 or total_import_time > 60,
        "ready": fail_imports == 0 and ok_files >= 2,
    }

    print("\n--- Warm-up Summary ---")
    print("  Total import time: %.1fs" % total_import_time)
    print("  OK: %d  SLOW: %d  FAIL: %d" % (ok_imports, slow_imports, fail_imports))
    print("  Model files OK: %d/%d" % (ok_files, len(WARMUP_MODEL_FILES)))
    print("  Cold start detected: %s" % ("YES" if results["summary"]["cold_start_detected"] else "NO"))
    print("  Ready for launch: %s" % ("YES" if results["summary"]["ready"] else "NO"))

    if results["summary"]["cold_start_detected"]:
        print("\n  ! NFS cold start detected. Re-run --warmup in 60s to confirm")
        print("    cache is now warm (second run should be <5s per import).")

    return results


# ============================================================================
# Module 2: Smoke Test Log Parser
# ============================================================================

LOG_PATTERNS = {
    "step": re.compile(r"\b(?:step|global_step)\s*[:=]\s*(\d+)", re.I),
    "kl_loss": re.compile(r"\bkl[_\s]*loss\s*[:=]\s*([\d.eE+-]+)", re.I),
    "reward_mean": re.compile(r"\breward[s]*[_/\s]*mean\s*[:=]\s*([\d.eE+-]+)", re.I),
    "reward_std": re.compile(r"\breward[s]*[_/\s]*std\s*[:=]\s*([\d.eE+-]+)", re.I),
    "entropy": re.compile(r"\bentropy\s*[:=]\s*([\d.eE+-]+)", re.I),
    "grad_norm": re.compile(r"\bgrad[_\s]*norm\s*[:=]\s*([\d.eE+-]+)", re.I),
    "loss": re.compile(r"(?<!kl_)(?<!policy_)\bloss\s*[:=]\s*([\d.eE+-]+)", re.I),
    "policy_loss": re.compile(r"\bpolicy[_\s]*loss\s*[:=]\s*([\d.eE+-]+)", re.I),
    "cheat_rate": re.compile(r"\bcheat[_\s]*rate\s*[:=]\s*([\d.eE+-]+)", re.I),
    "std_zero_pct": re.compile(r"\bstd[_\s]*zero[_\s]*pct\s*[:=]\s*([\d.eE+-]+)", re.I),
    "filter_rate": re.compile(r"\bfilter[_\s]*(?:rate|groups)\s*[:=]\s*([\d.eE+-]+)", re.I),
    "nan_inf": re.compile(r"\b(?:nan|inf|NaN|Inf|NAN|INF)\b"),
    "oom": re.compile(r"\b(?:OOM|out of memory|CUDA out of memory|OutOfMemoryError)\b", re.I),
    "error": re.compile(r"\b(?:ERROR|Traceback|Exception|RuntimeError)\b"),
    "timeout": re.compile(r"\b(?:timeout|timed out|TimeoutError)\b", re.I),
}


def parse_log_line(line):
    """Extract metrics from a single log line."""
    found = {}
    for key, pattern in LOG_PATTERNS.items():
        m = pattern.search(line)
        if m:
            if key in ("nan_inf", "oom", "error", "timeout"):
                found[key] = True
            else:
                try:
                    found[key] = float(m.group(1))
                except (ValueError, IndexError):
                    pass
    return found


def parse_log_file(log_path):
    """Parse a verl stdout log file and extract per-step metrics."""
    steps = []
    raw_lines = []
    global_flags = {"nan_inf": False, "oom": False, "error": False, "timeout": False}
    current_step = {}

    try:
        with open(log_path, "r") as f:
            for line in f:
                raw_lines.append(line.rstrip())
                parsed = parse_log_line(line)
                for flag in global_flags:
                    if parsed.get(flag):
                        global_flags[flag] = True
                if "step" in parsed:
                    if current_step:
                        steps.append(current_step)
                    current_step = {"step": int(parsed["step"])}
                if not current_step:
                    current_step = {"step": 0}
                for k, v in parsed.items():
                    if k != "step" and k not in global_flags:
                        if k not in current_step:
                            current_step[k] = v
    except FileNotFoundError:
        return {"error": "Log file not found: " + log_path, "steps": [], "global_flags": global_flags}
    except Exception as e:
        return {"error": str(e), "steps": [], "global_flags": global_flags}

    if current_step:
        steps.append(current_step)

    return {"log_path": log_path, "total_lines": len(raw_lines),
            "steps": steps, "global_flags": global_flags, "raw_lines": raw_lines}


# ============================================================================
# Module 3: Smoke Test Diagnostic Classifier
# ============================================================================

def classify_smoke(parsed):
    """Classify smoke test results into GO / WARN / DEBUG / ABORT."""
    verdict = "GO"
    reasons = []
    actions = []
    checks = []
    metrics_summary = {}

    if "error" in parsed:
        return {"verdict": "ABORT", "reasons": ["Log parse error: " + parsed["error"]],
                "actions": ["Fix log file path or format"], "checks": [], "metrics_summary": {}}

    steps = parsed.get("steps", [])
    global_flags = parsed.get("global_flags", {})
    n_steps = len(steps)

    reward_means = [s.get("reward_mean", 0) for s in steps if "reward_mean" in s]
    reward_stds = [s.get("reward_std", 0) for s in steps if "reward_std" in s]
    kl_losses = [s.get("kl_loss", 0) for s in steps if "kl_loss" in s]
    losses = [s.get("loss", s.get("policy_loss", 0)) for s in steps if "loss" in s or "policy_loss" in s]
    entropies = [s.get("entropy", 0) for s in steps if "entropy" in s]
    grad_norms = [s.get("grad_norm", 0) for s in steps if "grad_norm" in s]
    cheat_rates = [s.get("cheat_rate", 0) for s in steps if "cheat_rate" in s]
    std_zero_pcts = [s.get("std_zero_pct", 0) for s in steps if "std_zero_pct" in s]

    metrics_summary = {
        "n_steps": n_steps,
        "reward_mean_avg": sum(reward_means) / len(reward_means) if reward_means else None,
        "reward_std_avg": sum(reward_stds) / len(reward_stds) if reward_stds else None,
        "kl_loss_max": max(kl_losses) if kl_losses else None,
        "loss_avg": sum(losses) / len(losses) if losses else None,
        "entropy_min": min(entropies) if entropies else None,
        "grad_norm_max": max(grad_norms) if grad_norms else None,
        "cheat_rate_max": max(cheat_rates) if cheat_rates else None,
        "std_zero_pct_avg": sum(std_zero_pcts) / len(std_zero_pcts) if std_zero_pcts else None,
    }

    def add_check(name, status, value):
        checks.append({"name": name, "status": status, "value": value})

    # Check 1: NaN/Inf -> ABORT
    if global_flags.get("nan_inf"):
        verdict = "ABORT"
        reasons.append("NaN/Inf detected in training log")
        actions.append("STOP: Reduce lr, decrease grad_clip, resume from checkpoint")
        add_check("NaN/Inf", "FAIL", "detected")
    else:
        add_check("NaN/Inf", "PASS", "none")

    # Check 2: OOM -> ABORT
    if global_flags.get("oom"):
        verdict = "ABORT"
        reasons.append("CUDA OOM detected -- GPU memory exhausted")
        actions.append("Reduce: micro_batch 4->2, gpu_memory_utilization 0.50->0.35, max_response 8192->4096")
        add_check("OOM", "FAIL", "detected")
    else:
        add_check("OOM", "PASS", "none")

    # Check 3: Steps completed
    if n_steps == 0:
        verdict = "ABORT"
        reasons.append("No training steps parsed -- training may not have started")
        actions.append("Check: venv python, config, parquet, GPU. Run preflight.")
        add_check("Steps completed", "FAIL", "%d/10" % n_steps)
    elif n_steps < R0_EXPECTED["min_iters_completed"]:
        if verdict != "ABORT":
            verdict = "DEBUG"
        reasons.append("Only %d/10 steps completed -- crashed or hung" % n_steps)
        actions.append("Check last log lines. Check GPU memory. Re-run --smoke after fix.")
        add_check("Steps completed", "WARN", "%d/10 (need >=%d)" % (n_steps, R0_EXPECTED["min_iters_completed"]))
    else:
        add_check("Steps completed", "PASS", "%d/10" % n_steps)

    # Check 4: Timeout
    if global_flags.get("timeout"):
        if verdict != "ABORT":
            verdict = "DEBUG"
        reasons.append("Timeout detected -- sandbox or SGLang unreachable")
        actions.append("Check sandbox (R37: TCP filtered). Use --reward-arm R0. Verify SGLang port.")
        add_check("Timeout", "FAIL", "detected")
    else:
        add_check("Timeout", "PASS", "none")

    # Check 5: Reward collapse
    if reward_means:
        avg_r = metrics_summary["reward_mean_avg"]
        if avg_r is not None and avg_r < VISION_THRESHOLDS["reward_floor"]:
            if verdict != "ABORT":
                verdict = "DEBUG"
            reasons.append("Reward collapse: mean=%.4f < %s" % (avg_r, VISION_THRESHOLDS["reward_floor"]))
            actions.append("Check: reward function non-zero? Sandbox running? Switch to R0.")
            add_check("Reward collapse", "FAIL", "mean=%.4f" % avg_r)
        elif avg_r is not None and avg_r < 0.05:
            if verdict not in ("ABORT", "DEBUG"):
                verdict = "WARN"
            reasons.append("Low reward: mean=%.4f -- mostly-failing rollouts" % avg_r)
            actions.append("Monitor. If persists >50 steps: mix easier L1/L2 tasks.")
            add_check("Reward level", "WARN", "mean=%.4f" % avg_r)
        else:
            add_check("Reward level", "PASS", "mean=%.4f" % avg_r)

    # Check 6: std=0 dominance (Vision pattern)
    if std_zero_pcts:
        avg_sz = metrics_summary["std_zero_pct_avg"]
        if avg_sz is not None:
            if avg_sz > VISION_THRESHOLDS["std_zero_pct_abort"]:
                if verdict != "ABORT":
                    verdict = "DEBUG"
                reasons.append("CRITICAL std=0 dominance: %.1f%% > %.0f%% (Vision v1/v3: 78.7%%)" %
                               (avg_sz, VISION_THRESHOLDS["std_zero_pct_abort"]))
                actions.append("Switch to Dr.GRPO. Increase G 8->16. Switch R1->R2. sGPO filtering.")
                add_check("std=0 dominance", "FAIL", "%.1f%%" % avg_sz)
            elif avg_sz > VISION_THRESHOLDS["std_zero_pct_warn"]:
                if verdict not in ("ABORT", "DEBUG"):
                    verdict = "WARN"
                reasons.append("High std=0: %.1f%% > %.0f%% -- reduced GRPO signal" %
                               (avg_sz, VISION_THRESHOLDS["std_zero_pct_warn"]))
                actions.append("Monitor trend. If increasing: increase G or R2. BaiZe P(mixed)=97.2%% (R57).")
                add_check("std=0 dominance", "WARN", "%.1f%%" % avg_sz)
            else:
                add_check("std=0 dominance", "PASS", "%.1f%%" % avg_sz)

    # Check 7: Loss ~0 (Vision v3)
    if losses:
        avg_l = metrics_summary["loss_avg"]
        if avg_l is not None and avg_l < VISION_THRESHOLDS["loss_near_zero"]:
            if verdict not in ("ABORT",):
                if verdict != "DEBUG":
                    verdict = "WARN"
            reasons.append("Loss near zero: %.6f < %s -- policy gradient weak (Vision v3)" %
                           (avg_l, VISION_THRESHOLDS["loss_near_zero"]))
            actions.append("Check reward std. Increase entropy_coeff 0.001->0.01.")
            add_check("Loss level", "WARN", "%.6f" % avg_l)
        else:
            add_check("Loss level", "PASS", "%.6f" % avg_l)

    # Check 8: KL divergence
    if kl_losses:
        max_kl = metrics_summary["kl_loss_max"]
        if max_kl is not None and max_kl > VISION_THRESHOLDS["kl_max"]:
            if verdict != "ABORT":
                verdict = "DEBUG"
            reasons.append("KL explosion: max=%.2f > %s" % (max_kl, VISION_THRESHOLDS["kl_max"]))
            actions.append("Increase kl_loss_coef 0.04->0.08. Decrease lr. ppo_epochs 2->1.")
            add_check("KL divergence", "FAIL", "max=%.2f" % max_kl)
        elif max_kl is not None and max_kl > 3.0:
            if verdict not in ("ABORT", "DEBUG"):
                verdict = "WARN"
            reasons.append("Elevated KL: max=%.2f (threshold=10)" % max_kl)
            actions.append("Monitor KL trend. If increasing: increase kl_loss_coef.")
            add_check("KL divergence", "WARN", "max=%.2f" % max_kl)
        else:
            add_check("KL divergence", "PASS", "max=%.2f" % max_kl)

    # Check 9: Entropy collapse
    if entropies:
        min_e = metrics_summary["entropy_min"]
        if min_e is not None and min_e < VISION_THRESHOLDS["entropy_floor"]:
            if verdict not in ("ABORT", "DEBUG"):
                verdict = "WARN"
            reasons.append("Entropy collapse: min=%.4f < %s" % (min_e, VISION_THRESHOLDS["entropy_floor"]))
            actions.append("Increase entropy_coeff 0.001->0.01. Increase temperature.")
            add_check("Entropy", "WARN", "min=%.4f" % min_e)
        else:
            add_check("Entropy", "PASS", "min=%.4f" % min_e)

    # Check 10: Gradient explosion
    if grad_norms:
        max_g = metrics_summary["grad_norm_max"]
        if max_g is not None and max_g > VISION_THRESHOLDS["grad_max"]:
            if verdict != "ABORT":
                verdict = "DEBUG"
            reasons.append("Gradient explosion: max=%.1f > %s" % (max_g, VISION_THRESHOLDS["grad_max"]))
            actions.append("Decrease lr 3e-6->1e-6. Decrease grad_clip 1.0->0.5. If NaN: stop.")
            add_check("Gradient norm", "FAIL", "max=%.1f" % max_g)
        else:
            add_check("Gradient norm", "PASS", "max=%.1f" % max_g)

    # Check 11: Cheat rate (red-line 5.2)
    if cheat_rates:
        max_c = metrics_summary["cheat_rate_max"]
        if max_c is not None and max_c > VISION_THRESHOLDS["cheat_max"]:
            if verdict != "ABORT":
                verdict = "DEBUG"
            reasons.append("Cheat rate exceeded red-line: %.1f%% > %.0f%% (5.2)" %
                           (max_c * 100, VISION_THRESHOLDS["cheat_max"] * 100))
            actions.append("Tighten anti-cheat PreToolUse hook. Report cheat rate. Red-line violation.")
            add_check("Cheat rate (5.2)", "FAIL", "%.1f%%" % (max_c * 100))
        else:
            add_check("Cheat rate (5.2)", "PASS", "%.1f%%" % (max_c * 100))

    # Check 12: Reward std (signal quality)
    if reward_stds:
        avg_std = metrics_summary["reward_std_avg"]
        if avg_std is not None and avg_std < VISION_THRESHOLDS["reward_floor"]:
            if verdict not in ("ABORT", "DEBUG"):
                verdict = "WARN"
            reasons.append("Reward std ~0: %.4f -- no GRPO advantage signal" % avg_std)
            actions.append("Increase group_size. Switch to R2. Check task difficulty.")
            add_check("Reward std (signal)", "WARN", "avg=%.4f" % avg_std)
        else:
            add_check("Reward std (signal)", "PASS", "avg=%.4f" % avg_std)

    pass_count = sum(1 for c in checks if c["status"] == "PASS")
    warn_count = sum(1 for c in checks if c["status"] == "WARN")
    fail_count = sum(1 for c in checks if c["status"] == "FAIL")

    return {
        "verdict": verdict,
        "reasons": reasons if reasons else ["All checks passed -- smoke test looks healthy"],
        "actions": actions if actions else [
            "Proceed to full RL training (Step 6 of launch_11_9.sh)",
            "Enable RL monitor: python baize_posttrain_rl_monitor.py --log-dir <path>",
            "Watch first 50 steps: reward trend, KL stability, cheat rate",
        ],
        "checks": checks,
        "metrics_summary": metrics_summary,
        "check_counts": {"PASS": pass_count, "WARN": warn_count, "FAIL": fail_count},
        "vision_pattern_match": any("Vision" in r for r in reasons),
    }


# ============================================================================
# Module 4: HTML Report
# ============================================================================

def generate_html(warmup, classification):
    """Generate self-contained HTML report."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    warmup_html = ""
    if warmup:
        summary = warmup.get("summary", {})
        imports_html = ""
        for imp in warmup.get("imports", []):
            color = {"OK": "#27ae60", "SLOW": "#f39c12", "FAIL": "#e74c3c",
                     "TIMEOUT": "#e74c3c", "NO_VENV": "#e74c3c"}.get(imp["status"], "#333")
            imports_html += '<tr><td>%s</td><td style="color:%s">%s</td><td>%.2fs</td></tr>' % (
                imp["name"], color, imp["status"], imp["elapsed_s"])
        files_html = ""
        for f in warmup.get("files", []):
            color = {"OK": "#27ae60", "SLOW": "#f39c12",
                     "MISSING": "#e74c3c", "ERROR": "#e74c3c"}.get(f["status"], "#333")
            size = f.get("size_mb", 0)
            files_html += '<tr><td>%s</td><td style="color:%s">%s</td><td>%.3fs</td><td>%.1f MB</td></tr>' % (
                os.path.basename(f["path"]), color, f["status"], f["elapsed_s"], size)
        ready = summary.get("ready", False)
        rc = "#27ae60" if ready else "#e74c3c"
        warmup_html = '<h2>1. NFS Cold-Start Warm-up</h2>'
        warmup_html += '<table class="data"><tr><th>Module</th><th>Status</th><th>Time</th></tr>%s</table>' % imports_html
        warmup_html += '<h3>Model File Warm-up</h3>'
        warmup_html += '<table class="data"><tr><th>File</th><th>Status</th><th>Time</th><th>Size</th></tr>%s</table>' % files_html
        warmup_html += '<div class="summary-box" style="border-color:%s"><strong>Summary:</strong> Total %.1fs | OK=%d SLOW=%d FAIL=%d | Cold start=%s | <span style="color:%s">%s</span></div>' % (
            rc, summary.get("total_import_time_s", 0), summary.get("ok_imports", 0),
            summary.get("slow_imports", 0), summary.get("fail_imports", 0),
            summary.get("cold_start_detected", False), rc, "READY" if ready else "NOT READY")

    class_html = ""
    if classification:
        verdict = classification["verdict"]
        vc = {"GO": "#27ae60", "WARN": "#f39c12", "DEBUG": "#e67e22", "ABORT": "#e74c3c"}[verdict]
        counts = classification.get("check_counts", {})
        checks_html = ""
        for c in classification.get("checks", []):
            color = {"PASS": "#27ae60", "WARN": "#f39c12", "FAIL": "#e74c3c"}[c["status"]]
            checks_html += '<tr><td>%s</td><td style="color:%s">%s</td><td>%s</td></tr>' % (
                c["name"], color, c["status"], c["value"])
        reasons_html = "".join("<li>%s</li>" % r for r in classification["reasons"])
        actions_html = "".join("<li>%s</li>" % a for a in classification["actions"])
        ms = classification.get("metrics_summary", {})
        ms_rows = ""
        for k, v in ms.items():
            if v is not None:
                v_str = "%.4f" % v if isinstance(v, float) else str(v)
                ms_rows += "<tr><td>%s</td><td>%s</td></tr>" % (k, v_str)
        vm = classification.get("vision_pattern_match", False)
        va = '<div class="alert-box"><strong>Vision failure pattern!</strong> R57: R2 not R1, monitor std=0, step 500 check</div>' if vm else ""
        class_html = '<h2>2. Smoke Test Diagnostic</h2>'
        class_html += '<div class="verdict-box" style="background:%s"><strong>VERDICT: %s</strong> (P=%d W=%d F=%d)</div>' % (
            vc, verdict, counts.get("PASS", 0), counts.get("WARN", 0), counts.get("FAIL", 0))
        class_html += va
        class_html += '<h3>Checks</h3><table class="data"><tr><th>Check</th><th>Status</th><th>Value</th></tr>%s</table>' % checks_html
        class_html += '<h3>Reasons</h3><ul>%s</ul>' % reasons_html
        class_html += '<h3>Actions</h3><ul>%s</ul>' % actions_html
        class_html += '<h3>Metrics</h3><table class="data"><tr><th>Metric</th><th>Value</th></tr>%s</table>' % ms_rows

    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R62 Day-1 Diagnostic</title>
<style>
body{font-family:-apple-system,"Microsoft YaHei",sans-serif;max-width:960px;margin:0 auto;padding:20px;background:#f5f5f5;color:#333;line-height:1.6}
h1{color:#2c3e50;border-bottom:3px solid #3498db;padding-bottom:10px}
h2{color:#2c3e50;margin-top:30px} h3{color:#34495e}
table.data{width:100%%;border-collapse:collapse;margin:10px 0;background:white}
table.data th{background:#2c3e50;color:white;padding:8px;text-align:left}
table.data td{padding:8px;border:1px solid #ddd} table.data tr:nth-child(even){background:#f9f9f9}
.verdict-box{padding:15px;border-radius:8px;color:white;margin:15px 0;font-size:1.2em}
.summary-box{padding:12px;border:2px solid;border-radius:8px;margin:10px 0;background:white}
.alert-box{padding:12px;background:#fff3cd;border:1px solid #ffeaa7;border-radius:8px;margin:10px 0;color:#856404}
ul{background:white;padding:15px 15px 15px 35px;border-radius:8px}
.footer{margin-top:30px;padding-top:15px;border-top:1px solid #ddd;font-size:0.85em;color:#7f8c8d}
</style>
</head>
<body>
<h1>R62: Day-1 Cold-Start Warm-up + Smoke Test Diagnostic Classifier</h1>
<p><strong>Time:</strong> %s | <strong>Machine:</strong> 10.252.32.17 (4xA40) | <strong>GPU:</strong> 2026-11-09</p>
<p>Addresses Day-1 risks: (1) NFS cold-start latency (R45: torch import >30s), (2) Smoke test output auto-classification.</p>
%s
%s
<div class="footer">
<p><strong>R62 (wake110, 2026-11-08):</strong> Day-1 cold-start warm-up + smoke test diagnostic classifier.</p>
<p><strong>Sources:</strong> R45 NFS cold start | R43 smoke calibrator | R57 Vision GRPO lessons | R36 RL monitor | R38 runbook | R60/R61 ctx+throughput</p>
<p>Red lines: 5.1 contamination | 5.2 anti-cheat | 5.3 5-run mean+/-std | eval protocol frozen. Surrogate results NOT transferable to BaiZe.</p>
</div>
</body>
</html>''' % (ts, warmup_html, class_html)


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="R62: Day-1 Cold-Start Warm-up + Smoke Test Diagnostic Classifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="WARNING: Surrogate RL results are NOT transferable to BaiZe."
    )
    parser.add_argument("--warmup", action="store_true",
                        help="Perform NFS cold-start warm-up (import timing)")
    parser.add_argument("--classify", metavar="LOG_PATH",
                        help="Classify smoke test output from verl log file")
    parser.add_argument("--venv", default=os.path.expanduser("~/code/verl_cu124_venv/bin/python"),
                        help="Python venv path for warm-up imports")
    parser.add_argument("--html", metavar="OUTPUT_PATH",
                        help="Generate HTML report to specified path")
    parser.add_argument("--json", metavar="OUTPUT_PATH",
                        help="Generate JSON results to specified path")
    args = parser.parse_args()

    if not args.warmup and not args.classify and not args.html:
        parser.print_help()
        return 0

    warmup_results = None
    classification = None

    if args.warmup:
        warmup_results = do_warmup(args.venv)

    if args.classify:
        print("\n" + "=" * 70)
        print("  R62 Smoke Test Diagnostic Classifier")
        print("  Log: " + args.classify)
        print("=" * 70)

        parsed = parse_log_file(args.classify)
        classification = classify_smoke(parsed)

        verdict = classification["verdict"]
        counts = classification["check_counts"]
        print("\n  VERDICT: %s" % verdict)
        print("  Checks: PASS=%d WARN=%d FAIL=%d" % (counts["PASS"], counts["WARN"], counts["FAIL"]))

        print("\n  --- Reasons ---")
        for r in classification["reasons"]:
            print("  * " + r)
        print("\n  --- Actions ---")
        for a in classification["actions"]:
            print("  -> " + a)
        print("\n  --- Checks ---")
        for c in classification["checks"]:
            print("  [%s] %-30s %s" % (c["status"], c["name"], c["value"]))

        if classification.get("vision_pattern_match"):
            print("\n  !! VISION LINE FAILURE PATTERN DETECTED!")
            print("  R57: R2 not R1, monitor std=0, step 500 check, no RFT fallback")

        ms = classification["metrics_summary"]
        if ms.get("n_steps", 0) > 0:
            print("\n  --- Metrics Summary ---")
            for k, v in ms.items():
                if v is not None:
                    v_str = "%.4f" % v if isinstance(v, float) else str(v)
                    print("  %-30s %s" % (k, v_str))

    if args.html:
        html = generate_html(warmup_results, classification)
        html_dir = os.path.dirname(args.html)
        if html_dir:
            os.makedirs(html_dir, exist_ok=True)
        with open(args.html, "w") as f:
            f.write(html)
        size_kb = os.path.getsize(args.html) / 1024
        print("\n  HTML report: %s (%.1fKB)" % (args.html, size_kb))

    if args.json:
        results = {"timestamp": datetime.now().isoformat(),
                   "warmup": warmup_results, "classification": classification}
        json_dir = os.path.dirname(args.json)
        if json_dir:
            os.makedirs(json_dir, exist_ok=True)
        with open(args.json, "w") as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        print("\n  JSON results: %s" % args.json)

    return 0


if __name__ == "__main__":
    sys.exit(main())

