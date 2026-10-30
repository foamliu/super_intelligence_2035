#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate reports/eval_{harness}.json from swebench report.json files.

Why: the chain_eval script runs `swebench.harness.run_evaluation` but does NOT
call `parse_eval` afterwards, so reports/eval_{h}.json stay stale (gate-run
data).  This script scans the per-instance report.json files produced by the
swebench docker harness and writes the summary JSON that
gen_report_swebench_verified_full500_zh.py consumes.

Classification (三分类, aligns with 运维令 10-28 铁律 3):
  - resolved       : report.json exists AND resolved == True
  - failed         : report.json exists AND resolved == False AND infra_failure == False
  - infra_or_quota : report.json missing, OR infra_failure == True,
                     OR patch_is_None / patch_does_not_exist
                     (单列，不计入模型能力)

Reusable: re-run anytime (e.g. after claude-code / codex eval finishes).
Only rewrites files whose content actually changed (mtime-preserving for
unchanged harnesses so we don't create spurious git diffs).

Usage:
  python3 regen_eval_summaries.py            # all 5 gate-PASS harnesses
  python3 regen_eval_summaries.py pi codex   # specific harnesses
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
REPORT_DIR = HERE / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# 5 路 gate-PASS（与 gen_report 一致）
HARNESS_MAP = {
    "cline-patched": "cline-kimi-k2.6-cloud",
    "opencode": "opencode-kimi-k2.6-cloud",
    "pi": "pi-kimi-k2.6-cloud",
    "claude-code": "claude-code-kimi-k2.6-cloud",
    "codex": "codex-kimi-k2.6-cloud",
}
DISPLAY = {"cline-patched": "cline", "opencode": "opencode", "pi": "pi",
           "claude-code": "claude-code", "codex": "codex"}


def classify_one(report_path: Path, iid: str) -> str:
    """Return 'resolved' | 'failed' | 'infra'."""
    if not report_path.exists():
        return "infra"
    try:
        rep = json.loads(report_path.read_text())
    except Exception:
        return "infra"
    inst = rep.get(iid, rep) if isinstance(rep, dict) else {}
    if not isinstance(inst, dict):
        return "infra"
    if inst.get("infra_failure", False):
        return "infra"
    if inst.get("patch_is_None", False) or not inst.get("patch_exists", True):
        return "infra"
    return "resolved" if inst.get("resolved", False) else "failed"


def regen(harness: str) -> dict | None:
    model = HARNESS_MAP[harness]
    run_id = f"verified_full_{harness}"
    run_dir = EVAL_LOG_ROOT / run_id
    if not run_dir.exists():
        print(f"  {harness}: no run dir {run_dir} — skip")
        return None
    model_dir = run_dir / model
    # fall back to glob if model dir name differs
    if not model_dir.exists():
        cands = [p for p in run_dir.iterdir() if p.is_dir() and p.name != "run.json"]
        model_dir = cands[0] if cands else None
        if model_dir is None:
            print(f"  {harness}: no model dir under {run_dir} — skip")
            return None

    resolved, failed, infra = [], [], []
    for iid_dir in sorted(model_dir.iterdir()):
        if not iid_dir.is_dir():
            continue
        iid = iid_dir.name
        rj = iid_dir / "report.json"
        cls = classify_one(rj, iid)
        {"resolved": resolved, "failed": failed, "infra": infra}[cls].append(iid)

    summary = {
        "harness": DISPLAY[harness],
        "harness_code": harness,
        "run_id": run_id,
        "n": len(resolved) + len(failed) + len(infra),
        "resolved": sorted(resolved),
        "failed": sorted(failed),
        "infra_or_quota": sorted(infra),
    }

    out = REPORT_DIR / f"eval_{harness}.json"
    # only write if changed (avoid spurious mtime bump for running evals)
    new_text = json.dumps(summary, indent=2)
    if out.exists() and out.read_text() == new_text:
        print(f"  {harness}: unchanged (n={summary['n']} resolved={len(resolved)} "
              f"failed={len(failed)} infra={len(infra)})")
    else:
        out.write_text(new_text)
        print(f"  {harness}: WROTE {out.name}  n={summary['n']} "
              f"resolved={len(resolved)} failed={len(failed)} infra={len(infra)}")
    return summary


def main():
    args = sys.argv[1:]
    targets = [h for h in args if h in HARNESS_MAP] or list(HARNESS_MAP)
    print(f"regen_eval_summaries: {', '.join(targets)}")
    for h in targets:
        regen(h)


if __name__ == "__main__":
    main()
