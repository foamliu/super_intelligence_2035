#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge new empty-patch predictions into eval reports (R2719 monitoring round).

User order 2026-11-18: continue SWE-bench Verified eval while downloading
SWE-bench Multimodal containers.  This monitoring round has real_new(pending)=0
(<2 threshold -> no incr_eval), but 16 new empty-patch predictions appeared
since R2718.  Merge them into the `failed`+`empty_patch` buckets so n /
total_predictions stay current.  Resolved counts and Pass% are UNCHANGED
-> 7way report does NOT need REGEN.

Convention: empty_patch is a subset of failed; n = resolved+failed+infra.
"""
from __future__ import annotations
import json, glob, os, time
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
ROUND = "R2719"
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek"}
HARNESSES = ["cline-patched", "codex", "claude-code", "deepseek-harness", "pi", "opencode", "hermes"]


def disp(h): return DISPLAY.get(h, h)


def log(m): print(f"[merge-empties {time.strftime('%H:%M:%S')}] {m}", flush=True)


def load_pred_ids(harness):
    """Return (all_ids, empty_ids) for a harness."""
    all_ids, empty_ids = set(), set()
    for f in sorted(glob.glob(str(PRED_DIR / f"{harness}__*.json"))):
        iid = os.path.basename(f).replace(f"{harness}__", "").replace(".json", "")
        all_ids.add(iid)
        try:
            d = json.loads(Path(f).read_text())
            obj = d[0] if isinstance(d, list) else d
            if not str(obj.get("model_patch", "") or "").strip():
                empty_ids.add(iid)
        except Exception:
            pass
    return all_ids, empty_ids


def main():
    log(f"=== merge_empties {ROUND} start ===")
    grand_merged = 0
    for h in HARNESSES:
        ef = REPORT_DIR / f"eval_glm53_{h}.json"
        if not ef.is_file():
            log(f"{disp(h)}: no eval report, skip")
            continue
        cum = json.loads(ef.read_text())
        for k in ("resolved", "failed", "infra_or_quota", "empty_patch", "no_patch"):
            cum.setdefault(k, [])
        done = set(cum["resolved"]) | set(cum["failed"]) | set(cum["infra_or_quota"])
        all_ids, empty_ids = load_pred_ids(h)
        new_empty = sorted(empty_ids - done)
        if not new_empty:
            log(f"{disp(h)}: 0 new empty patches, skip")
            continue
        # merge: add to failed + empty_patch (empty_patch ⊆ failed by convention)
        for iid in new_empty:
            if iid not in cum["failed"]:
                cum["failed"].append(iid)
            if iid not in cum["empty_patch"]:
                cum["empty_patch"].append(iid)
        cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
        cum["total_predictions"] = len(all_ids)
        cum["evaluated"] = cum["n"]
        ef.write_text(json.dumps(cum, indent=2))
        grand_merged += len(new_empty)
        log(f"{disp(h)}: merged {len(new_empty)} empty patches -> n={cum['n']} "
            f"resolved={len(cum['resolved'])} failed={len(cum['failed'])} "
            f"infra={len(cum['infra_or_quota'])} empty_patch={len(cum['empty_patch'])} "
            f"total_predictions={cum['total_predictions']}")
        log(f"  new empty ids: {new_empty}")
    log(f"=== merge_empties {ROUND} done: {grand_merged} empty patches merged ===")


if __name__ == "__main__":
    main()
