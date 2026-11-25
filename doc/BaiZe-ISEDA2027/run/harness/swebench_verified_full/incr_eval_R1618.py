#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""incr_eval R1618: eval 2 genuine backlog items (cline sphinx-9602 + codex django-13023).

Backlog detected by regen_eval_summaries.py + _backlog_scan_R1615.py
(patch_len>0 but not in eval file). Mid-flight exclusion:
  cline sympy-13647 EXCLUDED (cline proc PID 1669000 actively running it now).
  codex django-13028 EXCLUDED (codex proc PID 1314343 actively running it now).
Stable (safe to eval):
  cline-patched: sphinx-doc__sphinx-9602  (patchlen=3739)
  codex:         django__django-13023      (patchlen=1417)

CPU guard: max_workers=1 (S1 pretrain running, load ~24/224).
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
    log(f"EVAL {DISPLAY.get(harness,harness)} on {len(eval_ids)} instances (workers={max_workers}): {eval_ids}")
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
    "cline-patched": ["sphinx-doc__sphinx-9602"],
    "codex": ["django__django-13023"],
}

def main():
    R = "R1618"
    log(f"=== incr_eval {R} start ===")
    log(f"backlog: cline=1 (sphinx-9602) + codex=1 (django-13023) = 2 total")
    log("mid-flight excluded: cline sympy-13647 (proc active) / codex django-13028 (proc active)")
    for h, ids in BACKLOG.items():
        log(f"=== {DISPLAY.get(h,h)}: merge + eval {ids} ===")
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