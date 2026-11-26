#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate reports/eval_{harness}.json from swebench report.json files
AND prediction files (no-patch detection, R1434 2026-11-03).

Why: the chain_eval script runs `swebench.harness.run_evaluation` but does NOT
call `parse_eval` afterwards, so reports/eval_{h}.json stay stale (gate-run
data).  This script scans the per-instance report.json files produced by the
swebench docker harness and writes the summary JSON that
gen_report_swebench_verified_full500_zh.py consumes.

Classification (四分类, aligns with 运维令 10-28 铁律 3):
  - resolved       : report.json exists AND resolved == True
  - failed         : report.json exists AND resolved == False AND infra_failure == False
  - infra_or_quota : report.json missing (has patch, needs eval), OR infra_failure == True,
                     OR patch_is_None / patch_does_not_exist in report.json
                     (单列，不计入模型能力)
  - no_patch       : prediction file exists but model_patch is empty/missing
                     (model did not produce a solution — adapter health metric)
                     (单列，不计入模型能力，也不算 infra)

Reusable: re-run anytime (e.g. after claude-code / codex eval finishes).
Only rewrites files whose content actually changed (mtime-preserving for
unchanged harnesses so we don't create spurious git diffs).

Usage:
  python3 regen_eval_summaries.py            # all 7 harnesses
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

# 7 路：5 gate-PASS + 2 adapter-fixed (R988: hermes/deepseek 适配器修复后恢复全量)
HARNESS_MAP = {
    "cline-patched": "cline-kimi-k2.6-cloud",
    "opencode": "opencode-kimi-k2.6-cloud",
    "pi": "pi-kimi-k2.6-cloud",
    "claude-code": "claude-code-kimi-k2.6-cloud",
    "codex": "codex-kimi-k2.6-cloud",
    "hermes": "hermes-kimi-k2.6-cloud",
    "deepseek-harness": "deepseek-harness-kimi-k2.6-cloud",
}
DISPLAY = {"cline-patched": "cline", "opencode": "opencode", "pi": "pi",
           "claude-code": "claude-code", "codex": "codex",
           "hermes": "hermes", "deepseek-harness": "deepseek-harness"}


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


def _has_real_patch(pred_file: Path) -> bool:
    """Check if a prediction file has a non-empty model_patch."""
    try:
        if pred_file.stat().st_size < 30:
            return False
        d = json.loads(pred_file.read_text())
        if isinstance(d, dict):
            d = [d]
        return any(x.get("model_patch", "").strip() for x in d)
    except Exception:
        return False


def regen(harness: str) -> dict | None:
    model = HARNESS_MAP[harness]
    run_id = f"verified_full_{harness}"
    run_dir = EVAL_LOG_ROOT / run_id
    PRED_DIR = HERE / "predictions"

    resolved, failed, infra, no_patch = [], [], [], []
    evaluated_ids = set()

    # Phase 1: scan report.json files from docker eval across ALL run dirs
    # (main `verified_full_<h>` + any `verified_full_<h>_rerun_RXXXX`), taking
    # the NEWEST report.json per instance.
    # R1597 fix: previously only the main run dir was scanned, so items that
    # were eval'd in a rerun dir (e.g. cline rerun_R1592/R1594) had no
    # report.json in the main dir and were misclassified as `infra` (via
    # Phase 2's "has real patch but no eval" rule) even when the rerun
    # report.json showed a clean resolved=False/failed result.  This violated
    # 运维令 10-28 铁律 3 (infra must be单列, not mixed with model failures).
    newest = {}  # iid -> (mtime, report_path)
    run_dirs = sorted(EVAL_LOG_ROOT.glob(f"verified_full_{harness}*"))
    for run_d in run_dirs:
        if not run_d.is_dir():
            continue
        cands = [p for p in run_d.iterdir() if p.is_dir() and p.name != "run.json"]
        if not cands:
            continue
        model_dir = run_d / model
        if not model_dir.exists():
            model_dir = cands[0]
        for iid_dir in sorted(model_dir.iterdir()):
            if not iid_dir.is_dir():
                continue
            iid = iid_dir.name
            rj = iid_dir / "report.json"
            if not rj.exists():
                continue
            mt = rj.stat().st_mtime
            if iid not in newest or mt > newest[iid][0]:
                newest[iid] = (mt, rj)
    for iid, (_mt, rj) in sorted(newest.items()):
        cls = classify_one(rj, iid)
        {"resolved": resolved, "failed": failed, "infra": infra}[cls].append(iid)
        evaluated_ids.add(iid)
    print(f"  {harness}: scanned {len(run_dirs)} run dir(s), "
          f"{len(newest)} instances with report.json")

    # Phase 2: scan prediction files for no-patch items (R1434)
    for pf in sorted(PRED_DIR.glob(f"{harness}__*.json")):
        iid = pf.stem.split("__", 1)[1] if "__" in pf.stem else pf.stem
        if iid in evaluated_ids:
            continue
        if _has_real_patch(pf):
            infra.append(iid)
        else:
            no_patch.append(iid)

    summary = {
        "harness": DISPLAY[harness],
        "harness_code": harness,
        "run_id": run_id,
        "n": len(resolved) + len(failed) + len(infra) + len(no_patch),
        "resolved": sorted(resolved),
        "failed": sorted(failed),
        "infra_or_quota": sorted(infra),
        "no_patch": sorted(no_patch),
    }

    out = REPORT_DIR / f"eval_{harness}.json"
    new_text = json.dumps(summary, indent=2)
    if out.exists() and out.read_text() == new_text:
        print(f"  {harness}: unchanged (n={summary['n']} resolved={len(resolved)} "
              f"failed={len(failed)} infra={len(infra)} no_patch={len(no_patch)})")
    else:
        out.write_text(new_text)
        print(f"  {harness}: WROTE {out.name}  n={summary['n']} "
              f"resolved={len(resolved)} failed={len(failed)} infra={len(infra)} "
              f"no_patch={len(no_patch)})")
    return summary


def main():
    args = sys.argv[1:]
    targets = [h for h in args if h in HARNESS_MAP] or list(HARNESS_MAP)
    print(f"regen_eval_summaries: {', '.join(targets)}")
    for h in targets:
        regen(h)


if __name__ == "__main__":
    main()
