#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""incr_eval R1620: eval 26 genuine backlog items (18 cline + 8 deepseek).

Backlog detected by scan_backlog.py (real patch on disk, no report.json):
  cline-patched (18): astropy-7336, django-11087/14725/15098/16429/16527/17087,
    matplotlib-20676/24026/24149, pytest-10356/5631/6202/7205/7236/7432/8399,
    scikit-learn-25102
  deepseek-harness (8): matplotlib-26291/26466, psf__requests-1724/1766/1921/
    2317/2931, pydata__xarray-3677

Mid-flight EXCLUDED (active run_single, prediction not finalized):
  cline sympy-14248 / codex django-13033 / deepseek xarray-3993

CPU guard: max_workers=1 (S1 pretrain running, load ~29/224).
Hard constraint: NEVER commit result JSON.
"""
from __future__ import annotations
import json, os, subprocess, sys, time, glob
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED_DIR = HERE / "predictions"
REPORT_DIR = HERE / "reports"
LOG_DIR = HERE / "logs"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
ENRICHED = HERE / "enriched_500.json"
TIMEOUT_EVAL = 1800
DISPLAY = {"cline-patched": "cline", "codex": "codex", "deepseek-harness": "deepseek"}

def log(msg): print(f"[incr-eval {time.strftime('%H:%M:%S')}] {msg}", flush=True)

def merge_predictions(harness):
    merged = PRED_DIR / f"predictions_{harness}.json"
    all_preds = []
    count = 0
    for f in sorted(PRED_DIR.glob(f"{harness}__*.json")):
        if f.stat().st_size < 30: continue
        try:
            preds = json.loads(f.read_text())
            if isinstance(preds, dict): preds = [preds]
            for p in preds:
                if p.get("model_patch", "").strip():
                    all_preds.append(p); count += 1
        except Exception: pass
    merged.write_text(json.dumps(all_preds, indent=2))
    log(f"merged {count} predictions -> {merged}")
    return merged

def run_incr_eval(harness, eval_ids):
    merged = PRED_DIR / f"predictions_{harness}.json"
    run_id = f"verified_full_{harness}"
    max_workers = 1
    cmd = (f"python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(eval_ids)} --max_workers {max_workers} "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"EVAL {DISPLAY.get(harness,harness)} on {len(eval_ids)} instances (workers={max_workers})")
    EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    logf = LOG_DIR / f"eval_incr_verified_full_{harness}_{int(time.time())}.log"
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True,
                          timeout=TIMEOUT_EVAL * len(eval_ids) + 900)
    logf.write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)
    log(f"  eval finished rc={proc.returncode}; log -> {logf}")
    model = f"{harness}-kimi-k2.6-cloud"
    results = {}
    for iid in eval_ids:
        rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
        if not rj.exists():
            cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
            rj = cands[0] if cands else None
        if rj is None or not rj.exists():
            results[iid] = "infra"; log(f"  {iid}: INFRA (no report.json)"); continue
        try:
            rep = json.loads(rj.read_text())
            inst_rep = rep.get(iid, rep) if isinstance(rep, dict) else {}
            resolved = inst_rep.get("resolved", False)
            results[iid] = "resolved" if resolved else "failed"
            log(f"  {iid}: {'RESOLVED' if resolved else 'FAILED'}")
        except Exception as e:
            results[iid] = "infra"; log(f"  {iid}: INFRA ({e})")
    return results

def update_eval_json(harness, new_results):
    ef = REPORT_DIR / f"eval_{harness}.json"
    ev = json.loads(ef.read_text())
    for iid, status in new_results.items():
        for k in ("no_patch", "failed", "infra_or_quota", "resolved"):
            if iid in ev.get(k, []):
                ev[k].remove(iid)
        if status == "resolved":
            ev["resolved"].append(iid)
        elif status == "failed":
            ev["failed"].append(iid)
        else:
            ev["infra_or_quota"].append(iid)
    ev["n"] = len(ev["resolved"]) + len(ev["failed"]) + len(ev["infra_or_quota"]) + len(ev.get("no_patch", []))
    ef.write_text(json.dumps(ev, indent=2))
    log(f"updated {ef.name}: resolved={len(ev['resolved'])} failed={len(ev['failed'])} "
        f"infra={len(ev['infra_or_quota'])} no_patch={len(ev.get('no_patch', []))} n={ev['n']}")

BACKLOG = {
    "cline-patched": [
        "astropy__astropy-7336", "django__django-11087", "django__django-14725",
        "django__django-15098", "django__django-16429", "django__django-16527",
        "django__django-17087", "matplotlib__matplotlib-20676",
        "matplotlib__matplotlib-24026", "matplotlib__matplotlib-24149",
        "pytest-dev__pytest-10356", "pytest-dev__pytest-5631",
        "pytest-dev__pytest-6202", "pytest-dev__pytest-7205",
        "pytest-dev__pytest-7236", "pytest-dev__pytest-7432",
        "pytest-dev__pytest-8399", "scikit-learn__scikit-learn-25102",
    ],
    "deepseek-harness": [
        "matplotlib__matplotlib-26291", "matplotlib__matplotlib-26466",
        "psf__requests-1724", "psf__requests-1766", "psf__requests-1921",
        "psf__requests-2317", "psf__requests-2931", "pydata__xarray-3677",
    ],
}

def main():
    R = "R1620"
    log(f"=== incr_eval {R} start ===")
    total = sum(len(v) for v in BACKLOG.values())
    log(f"backlog: cline=18 + deepseek=8 = {total} total")
    log("mid-flight excluded: cline sympy-14248 / codex django-13033 / deepseek xarray-3993")
    for h, ids in BACKLOG.items():
        log(f"=== {DISPLAY.get(h,h)}: merge + eval {len(ids)} instances ===")
        merge_predictions(h)
        new_results = run_incr_eval(h, ids)
        update_eval_json(h, new_results)
    log("=== FINAL EVAL SUMMARY ===")
    for h in BACKLOG:
        ev = json.loads((REPORT_DIR / f"eval_{h}.json").read_text())
        log(f"  {DISPLAY.get(h,h):20s}: resolved={len(ev['resolved'])} failed={len(ev['failed'])} "
            f"infra={len(ev['infra_or_quota'])} no_patch={len(ev.get('no_patch', []))} n={ev['n']}")
    log(f"=== incr_eval {R} DONE ===")

if __name__ == "__main__":
    main()
