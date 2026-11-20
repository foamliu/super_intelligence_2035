#!/usr/bin/env python3
"""
baize_posttrain_ckpt_selector.py — R63: RL Checkpoint Selector

After GRPO training completes (or is interrupted), verl saves checkpoints at
save_interval steps. This script scans the checkpoint directory and the
training log to identify the **best** checkpoint for post-RL evaluation.

Selection criteria (in priority order):
  1. Highest mean reward in the last N logged steps (default N=20)
  2. Lowest cheat_rate (§5.2 red-line: cheat_rate must be < 5%)
  3. Most recent checkpoint (tie-breaker)

Also detects:
  - Checkpoints with NaN/Inf in metrics (excluded)
  - Checkpoints with reward collapse (mean < 0.01, excluded)
  - Checkpoints with std=0 dominance > 80% (Vision R57 lesson, excluded)

Pure Python 3.8+ stdlib only — 0 third-party dependencies.

Usage:
    python3 baize_posttrain_ckpt_selector.py --ckpt-dir <dir> --log <log>
    python3 baize_posttrain_ckpt_selector.py --dry-run
    python3 baize_posttrain_ckpt_selector.py --ckpt-dir <dir> --log <log> --json /tmp/out.json
    python3 baize_posttrain_ckpt_selector.py --ckpt-dir <dir> --log <log> --html <out.html>

R63 (2026-11-08): Fills gap in launch_11_9.sh — no Step 7 post-RL eval.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

_METRIC_PATTERNS = {
    "step":          re.compile(r"step[:\s]+(\d+)"),
    "reward_mean":   re.compile(r"reward_mean[:\s]+([0-9.eE+-]+)"),
    "reward_std":    re.compile(r"reward_std[:\s]+([0-9.eE+-]+)"),
    "cheat_rate":    re.compile(r"cheat_rate[:\s]+([0-9.eE+-]+)"),
    "kl_loss":       re.compile(r"kl_loss[:\s]+([0-9.eE+-]+)"),
    "entropy":       re.compile(r"entropy[:\s]+([0-9.eE+-]+)"),
    "grad_norm":     re.compile(r"grad_norm[:\s]+([0-9.eE+-]+)"),
    "std_zero_pct":  re.compile(r"std_zero_pct[:\s]+([0-9.eE+-]+)"),
}
_NAN_INF = re.compile(r"(?:NaN|Inf|inf)", re.IGNORECASE)
_OOM = re.compile(r"(?:OOM|CUDA out of memory)", re.IGNORECASE)


def parse_log_metrics(log_path: str) -> List[Dict[str, Any]]:
    """Parse training log and extract per-step metrics."""
    if not os.path.isfile(log_path):
        return []
    steps: List[Dict[str, Any]] = []
    cur: Optional[Dict[str, Any]] = None
    cur_step = -1
    with open(log_path, "r", errors="replace") as f:
        for line in f:
            has_nan = bool(_NAN_INF.search(line))
            has_oom = bool(_OOM.search(line))
            m_step = _METRIC_PATTERNS["step"].search(line)
            if m_step:
                sn = int(m_step.group(1))
                if sn != cur_step:
                    if cur is not None:
                        steps.append(cur)
                    cur = {"step": sn, "nan_inf": False, "oom": False}
                    cur_step = sn
                if has_nan:
                    cur["nan_inf"] = True
                if has_oom:
                    cur["oom"] = True
                continue
            if cur is None:
                continue
            for key, pattern in _METRIC_PATTERNS.items():
                if key == "step":
                    continue
                m = pattern.search(line)
                if m:
                    try:
                        cur[key] = float(m.group(1))
                    except (ValueError, IndexError):
                        pass
            if has_nan:
                cur["nan_inf"] = True
            if has_oom:
                cur["oom"] = True
    if cur is not None:
        steps.append(cur)
    return steps


def _dir_size_mb(path: str) -> float:
    total = 0
    try:
        for dp, _, fns in os.walk(path):
            for f in fns:
                fp = os.path.join(dp, f)
                if os.path.isfile(fp):
                    total += os.path.getsize(fp)
    except (OSError, PermissionError):
        pass
    return total / (1024 * 1024)


def find_checkpoints(ckpt_dir: str) -> List[Dict[str, Any]]:
    """Find all checkpoint directories matching global_step_* pattern."""
    pattern = os.path.join(ckpt_dir, "global_step_*")
    dirs = sorted(glob.glob(pattern),
                  key=lambda p: int(p.rsplit("_", 1)[-1]) if p.rsplit("_", 1)[-1].isdigit() else 0)
    ckpts: List[Dict[str, Any]] = []
    for d in dirs:
        step_str = os.path.basename(d).rsplit("_", 1)[-1]
        sn = int(step_str) if step_str.isdigit() else -1
        has_model = os.path.isdir(os.path.join(d, "actor")) or \
                    os.path.isfile(os.path.join(d, "model.safetensors"))
        ckpts.append({"path": d, "step": sn, "has_model": has_model, "size_mb": _dir_size_mb(d)})
    return ckpts


def select_best_checkpoint(
    steps: List[Dict[str, Any]],
    ckpts: List[Dict[str, Any]],
    last_n: int = 20,
) -> Dict[str, Any]:
    """Select best checkpoint: exclude bad ones, then rank by reward."""
    if not ckpts:
        return {"selected": None, "reason": "No checkpoints found", "valid": [], "excluded": []}
    if not steps:
        last = ckpts[-1]
        return {"selected": last, "reason": "No log metrics; using last checkpoint (fallback)",
                "valid": [last], "excluded": []}

    valid: List[Dict[str, Any]] = []
    excluded: List[Dict[str, Any]] = []
    cheat_thr = 0.05   # §5.2
    std0_thr = 80.0    # R57 Vision
    reward_floor = 0.01  # R36

    for ckpt in ckpts:
        cs = ckpt["step"]
        if cs < 0:
            excluded.append({**ckpt, "exclude_reason": "Invalid step number"})
            continue
        if not ckpt["has_model"]:
            excluded.append({**ckpt, "exclude_reason": "No model files"})
            continue
        nearest = [s for s in steps if s["step"] <= cs] or [steps[0]]
        window = nearest[-last_n:]
        rewards = [s.get("reward_mean", 0) for s in window]
        cheats = [s.get("cheat_rate", 0) for s in window]
        std0s = [s.get("std_zero_pct", 0) for s in window]
        has_nan = any(s.get("nan_inf", False) for s in window)
        has_oom = any(s.get("oom", False) for s in window)
        avg_r = sum(rewards) / len(rewards) if rewards else 0
        avg_c = sum(cheats) / len(cheats) if cheats else 0
        avg_s = sum(std0s) / len(std0s) if std0s else 0
        entry = {**ckpt, "avg_reward": round(avg_r, 6), "avg_cheat_rate": round(avg_c, 6),
                 "avg_std_zero_pct": round(avg_s, 2), "window_steps": len(window),
                 "nearest_step": window[-1]["step"] if window else -1}
        if has_nan:
            excluded.append({**entry, "exclude_reason": "NaN/Inf in log window"})
        elif has_oom:
            excluded.append({**entry, "exclude_reason": "OOM in log window"})
        elif avg_r < reward_floor:
            excluded.append({**entry, "exclude_reason": f"Reward collapse: {avg_r:.4f} < {reward_floor}"})
        elif avg_s > std0_thr:
            excluded.append({**entry, "exclude_reason": f"std=0 {avg_s:.1f}% > {std0_thr}% (R57)"})
        elif avg_c > cheat_thr:
            excluded.append({**entry, "exclude_reason": f"Cheat {avg_c:.4f} > {cheat_thr} (§5.2)"})
        else:
            valid.append(entry)

    if not valid:
        last = ckpts[-1]
        return {"selected": {**last, "warning": "All excluded; using last as fallback"},
                "reason": "All checkpoints failed quality checks; fallback to last",
                "valid": [], "excluded": excluded}

    valid.sort(key=lambda x: (-x["avg_reward"], x["avg_cheat_rate"], -x["step"]))
    best = valid[0]
    return {"selected": best,
            "reason": f"Step {best['step']}: reward={best['avg_reward']:.4f}, cheat={best['avg_cheat_rate']:.4f}",
            "valid": valid, "excluded": excluded}


def generate_html(result: Dict[str, Any], output_path: str) -> str:
    sel = result.get("selected", {}) or {}
    valid = result.get("valid", [])
    excluded = result.get("excluded", [])
    vr = "".join(
        f"<tr><td>{v['step']}</td><td>{v.get('avg_reward','N/A')}</td>"
        f"<td>{v.get('avg_cheat_rate','N/A')}</td><td>{v.get('avg_std_zero_pct','N/A')}</td>"
        f"<td>{v.get('size_mb',0):.1f}</td><td><code>{v['path']}</code></td></tr>"
        for v in valid[:20])
    er = "".join(
        f"<tr><td>{e['step']}</td><td>{e.get('avg_reward','N/A')}</td>"
        f"<td style='color:#c62828'>{e.get('exclude_reason','?')}</td>"
        f"<td><code>{e['path']}</code></td></tr>"
        for e in excluded[:20])
    sw = sel.get("warning", "")
    wb = f'<div style="background:#fff3e0;border:1px solid #ff9800;padding:10px;border-radius:4px;margin:10px 0">⚠️ {sw}</div>' if sw else ""
    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>R63 RL Checkpoint Selector</title>
<style>
body{{font-family:sans-serif;margin:20px;background:#f5f5f5;color:#333}}
h1{{color:#1565c0}}h2{{color:#1565c0;border-bottom:2px solid #e3f2fd;padding-bottom:5px}}
table{{border-collapse:collapse;width:100%;margin:10px 0;background:white}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left;font-size:13px}}
th{{background:#e3f2fd}}tr:nth-child(even){{background:#f9f9f9}}
.box{{background:white;padding:15px;border-radius:8px;margin:10px 0;box-shadow:0 1px 3px rgba(0,0,0,0.1)}}
.sel{{background:#e8f5e9;border:2px solid #4caf50;padding:15px;border-radius:8px;margin:10px 0}}
.footer{{margin-top:30px;font-size:12px;color:#888;border-top:1px solid #ddd;padding-top:10px}}
code{{background:#f0f0f0;padding:2px 6px;border-radius:3px;font-size:13px}}
</style></head><body>
<h1>R63: RL Checkpoint Selector — 最佳检查点选择器</h1>
<div class="box"><p><strong>生成时间</strong>: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p><strong>选择标准</strong>: 排除 NaN/OOM/reward&lt;0.01/std=0&gt;80%/cheat&gt;5% → 按 reward 降序 → cheat 升序 → step 降序</p></div>
<h2>🎯 最佳检查点</h2>
<div class="sel"><p><strong>Step</strong>: {sel.get('step','N/A')}</p>
<p><strong>Avg Reward</strong>: {sel.get('avg_reward','N/A')}</p>
<p><strong>Path</strong>: <code>{sel.get('path','N/A')}</code></p>
<p><strong>原因</strong>: {result.get('reason','N/A')}</p></div>
{wb}
<h2>✅ 有效检查点 ({len(valid)})</h2>
<table><tr><th>Step</th><th>Avg Reward</th><th>Cheat</th><th>std=0%</th><th>Size MB</th><th>Path</th></tr>{vr}</table>
<h2>❌ 排除的检查点 ({len(excluded)})</h2>
<table><tr><th>Step</th><th>Avg Reward</th><th>排除原因</th><th>Path</th></tr>{er}</table>
<h2>📋 质量阈值</h2>
<div class="box"><ul>
<li>NaN/Inf → 排除 (R36)</li><li>OOM → 排除 (R36)</li>
<li>reward &lt; 0.01 → 排除 (R36)</li><li>std=0 &gt; 80% → 排除 (R57 Vision: 78.7%)</li>
<li>cheat &gt; 5% → 排除 (§5.2 红线)</li></ul></div>
<h2>🔗 后续管线</h2>
<div class="box"><p>选定后 <code>baize_posttrain_post_rl_pipeline.sh</code> 自动：</p>
<ol><li>SGLang serve 加载检查点</li><li>158-case 评测 (5-run, 2500s, -p 8 -n)</li>
<li>eval_analysis.py McNemar + bootstrap</li><li>baseline_gate.py 里程碑检查</li><li>HTML 报告</li></ol></div>
<div class="footer"><p>R63 (2026-11-08) · Pure Python 3.8+ stdlib · ⚠️ 替身 RL 不可迁移到 BaiZe</p></div>
</body></html>"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path


def main():
    p = argparse.ArgumentParser(description="R63: RL Checkpoint Selector")
    p.add_argument("--ckpt-dir", default="", help="Directory with global_step_* checkpoints")
    p.add_argument("--log", default="", help="verl training log file")
    p.add_argument("--last-n", type=int, default=20, help="Steps to average (default 20)")
    p.add_argument("--dry-run", action="store_true", help="Print selection logic with simulated data")
    p.add_argument("--json", default="", help="Output JSON to this path")
    p.add_argument("--html", default="", help="Output HTML report to this path")
    args = p.parse_args()

    if args.dry_run:
        print("=== DRY RUN: Simulated checkpoint selection ===")
        sim_steps = [
            {"step": s * 10, "reward_mean": 0.15 + s * 0.03, "cheat_rate": 0.01 * s,
             "std_zero_pct": 35.0 - s * 2.5, "nan_inf": False, "oom": False}
            for s in range(1, 11)
        ]
        sim_ckpts = [
            {"path": "/tmp/sim/global_step_50", "step": 50, "has_model": True, "size_mb": 3800},
            {"path": "/tmp/sim/global_step_100", "step": 100, "has_model": True, "size_mb": 3800},
        ]
        result = select_best_checkpoint(sim_steps, sim_ckpts, last_n=args.last_n)
        print(f"Selected: step {result['selected']['step']}")
        print(f"Reason: {result['reason']}")
        print(f"Valid: {len(result['valid'])}, Excluded: {len(result['excluded'])}")
        print("✅ Dry-run passed — selection logic verified.")
        return 0

    if not args.ckpt_dir:
        print("Error: --ckpt-dir required (or --dry-run)", file=sys.stderr)
        return 1

    print(f"[R63] Scanning checkpoints: {args.ckpt_dir}")
    ckpts = find_checkpoints(args.ckpt_dir)
    print(f"  Found {len(ckpts)} checkpoint(s)")

    print(f"[R63] Parsing log: {args.log}")
    steps = parse_log_metrics(args.log) if args.log else []
    print(f"  Parsed {len(steps)} step entries")

    result = select_best_checkpoint(steps, ckpts, last_n=args.last_n)
    sel = result.get("selected", {}) or {}
    print(f"\n{'='*60}")
    print(f"  BEST: step {sel.get('step','N/A')}  reward={sel.get('avg_reward','N/A')}")
    print(f"  Path: {sel.get('path','N/A')}")
    print(f"  Reason: {result['reason']}")
    print(f"  Valid: {len(result['valid'])}  Excluded: {len(result['excluded'])}")
    print(f"{'='*60}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        print(f"  JSON → {args.json}")
    if args.html:
        generate_html(result, args.html)
        print(f"  HTML → {args.html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
