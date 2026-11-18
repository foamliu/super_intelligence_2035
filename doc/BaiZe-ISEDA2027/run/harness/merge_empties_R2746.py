#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R2746 monitoring round: merge empties only.

Continues the R2727~R2745 cadence: auto-detect newly-arrived empty-patch
predictions and merge them into the cumulative eval json (failed/empty_patch),
without running docker eval. real-patch predictions stay pending until the
>=2 threshold is met for an incr_eval round.

Survey at wake (2026-11-19 ~07:34, survey_uneval_R2746.py):
  cline-patched     443  (was 442 at R2745, +1)  1 real_new (pytest-7521) -> pending
  codex             381  (was 381, +0)           1 real_new (scikit-learn-11310) -> pending
  deepseek-harness  247  (unchanged)             0 / 0
  pi                379  (unchanged)             0 real / 1 empty -> MERGE
  claude-code       500  (COMPLETE)              skip
  opencode          500  (COMPLETE)              skip
  hermes            500  (COMPLETE)              skip

No route reaches >=2 real_new -> no incr_eval this round.
User order 2026-11-18: continue SWE-bench Verified eval while downloading
SWE-bench Multimodal containers (nice19/ionice=idle, no .29 CPU contention).
"""
from __future__ import annotations
import json, glob, os, time
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
ROUND = "R2746"
ROUTES = ["cline-patched", "codex", "claude-code", "deepseek-harness", "pi", "opencode", "hermes"]
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek", "claude-code": "cc"}


def disp(h): return DISPLAY.get(h, h)


def log(m): print(f"[merge-empties {time.strftime('%H:%M:%S')}] {m}", flush=True)


def load_pred(iid_file):
    try:
        d = json.loads(iid_file.read_text())
    except Exception:
        return []
    if isinstance(d, dict):
        d = [d]
    return [p for p in d if (p.get("model_patch") or "").strip()]


def get_unevaluated(harness):
    cum_file = REPORT_DIR / f"eval_glm53_{harness}.json"
    done = set()
    if cum_file.is_file():
        d = json.loads(cum_file.read_text())
        for field in ["resolved", "failed", "infra_or_quota", "no_patch", "empty_patch"]:
            val = d.get(field, [])
            if isinstance(val, list):
                done.update(val)
    preds = sorted(glob.glob(str(PRED_DIR / f"{harness}__*.json")))
    real_new, empty_new = [], []
    for p in preds:
        iid = os.path.basename(p).replace(f"{harness}__", "").replace(".json", "")
        if iid in done:
            continue
        if load_pred(Path(p)):
            real_new.append(iid)
        else:
            empty_new.append(iid)
    return real_new, empty_new, done


def merge_empties(harness, empty_ids):
    ef = REPORT_DIR / f"eval_glm53_{harness}.json"
    cum = json.loads(ef.read_text()) if ef.is_file() else {
        "harness": harness, "harness_code": harness, "run_id": f"no_eval_{ROUND}",
        "n": 0, "resolved": [], "failed": [], "infra_or_quota": [],
        "empty_patch": [], "no_patch": []}
    for k in ("resolved", "failed", "infra_or_quota", "empty_patch"):
        cum.setdefault(k, [])
        if not isinstance(cum[k], list):
            cum[k] = []
    merged = 0
    for iid in empty_ids:
        if iid not in cum["failed"] and iid not in cum["resolved"]:
            cum["empty_patch"].append(iid)
            cum["failed"].append(iid)
            merged += 1
            log(f"  {iid}: EMPTY PATCH -> failed")
    cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
    cum["total_predictions"] = len(glob.glob(str(PRED_DIR / f"{harness}__*.json")))
    cum["evaluated"] = cum["n"]
    ef.write_text(json.dumps(cum, indent=2))
    log(f"{disp(harness)}: merged {merged} empties -> n={cum['n']} resolved={len(cum['resolved'])} "
        f"failed={len(cum['failed'])} empty_patch={len(cum['empty_patch'])} total_pred={cum['total_predictions']}")
    return cum, merged


if __name__ == "__main__":
    log(f"Starting merge_empties {ROUND}")
    summary = {}
    pending_real = {}
    for h in ROUTES:
        log(f"--- {disp(h)} ---")
        real_new, empty_new, done = get_unevaluated(h)
        log(f"{disp(h)}: unevaluated real_patch={len(real_new)} empty_patch={len(empty_new)}")
        if real_new:
            pending_real[h] = real_new
        if empty_new:
            cum, merged = merge_empties(h, empty_new)
            summary[h] = {"merged": merged, "n": cum["n"], "resolved": len(cum["resolved"])}
        else:
            log(f"{disp(h)}: no empties to merge")
    log("=== SUMMARY ===")
    for h, s in summary.items():
        log(f"{disp(h)}: merged={s['merged']} n={s['n']} resolved={s['resolved']}")
    if pending_real:
        log("PENDING real-patches (not eval'd, < 2 threshold):")
        for h, ids in pending_real.items():
            log(f"  {disp(h)}: {ids}")
    log("DONE")
