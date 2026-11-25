#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Incremental eval for deepseek-harness backlog (R1641 wake-up cycle).

Models run_verified_full.phase_eval + parse_eval but MERGES results into the
existing eval_deepseek-harness.json (does not overwrite). Only evaluates
backlog instances = predicted but not yet in (resolved|failed|infra|no_patch).

Pipeline:
  1. merge_predictions(all 500 ids) -> predictions_deepseek-harness.json
  2. compute backlog; empty-patch -> no_patch (no docker); non-empty -> docker eval
  3. swebench.harness.run_evaluation via `sg docker` on backlog patch-ids
     (unique run_id so existing report.json dirs are not disturbed)
  4. parse report.json per backlog id -> resolved/failed/infra
  5. merge into existing eval json (append, dedup, recompute n) + write log
"""
from __future__ import annotations
import json, subprocess, sys, time
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions"
REPORT_DIR = HERE / "reports"
LOG_DIR = HERE / "logs"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
# swebench may write per-instance report.json under logs/evaluation/ (observed
# for incr run_ids); check both to avoid false INFRA classification.
EVAL_LOG_ROOT_ALT = HERE / "logs" / "evaluation"
ENRICHED = HERE / "enriched_500.json"
IDS_FILE = HERE / "verified_500_ids.txt"
HARNESS = "deepseek-harness"
MODEL = f"{HARNESS}-kimi-k2.6-cloud"
TIMEOUT_EVAL = 1800
ROUND = "R1644"

def log(m):
    ts = time.strftime("%H:%M:%S")
    print(f"[incr-eval {ts}] {m}", flush=True)

def load_ids():
    return [l.strip() for l in IDS_FILE.read_text().splitlines() if l.strip()]

def merge_predictions(ids):
    merged = PRED_DIR / f"predictions_{HARNESS}.json"
    all_preds = []
    for iid in ids:
        f = PRED_DIR / f"{HARNESS}__{iid}.json"
        if f.exists() and f.stat().st_size > 30:
            try:
                preds = json.loads(f.read_text())
                preds = [p for p in preds if p.get("model_patch", "").strip()]
                all_preds.extend(preds)
            except Exception:
                pass
    merged.write_text(json.dumps(all_preds, indent=2))
    log(f"merged {len(all_preds)}/{len(ids)} predictions -> {merged}")
    return merged

def patch_len(iid):
    f = PRED_DIR / f"{HARNESS}__{iid}.json"
    if not f.exists():
        return 0
    try:
        d = json.loads(f.read_text())
        if isinstance(d, list):
            d = d[0] if d else {}
        return len((d.get("model_patch") or "").strip())
    except Exception:
        return 0

def main():
    ev_path = REPORT_DIR / f"eval_{HARNESS}.json"
    ev = json.loads(ev_path.read_text())
    seen = set(ev.get("resolved", [])) | set(ev.get("failed", [])) | set(ev.get("infra_or_quota", [])) | set(ev.get("no_patch", []))
    ids = load_ids()
    merge_predictions(ids)
    # backlog = predicted but not seen
    backlog = [i for i in ids if (PRED_DIR / f"{HARNESS}__{i}.json").exists() and i not in seen]
    log(f"=== incr_eval for {HARNESS}: {backlog} ===")
    if not backlog:
        log("no backlog; nothing to do")
        return
    # split: empty-patch -> no_patch; non-empty -> docker eval
    no_patch_new = [i for i in backlog if patch_len(i) == 0]
    eval_ids = [i for i in backlog if patch_len(i) > 0]
    for i in no_patch_new:
        ev.setdefault("no_patch", []).append(i)
    log(f"  no_patch (empty patch, no docker): {no_patch_new}")
    log(f"  to docker-eval: {eval_ids}")
    if eval_ids:
        run_id = f"verified_full_{HARNESS}_incr_{ROUND}"
        merged = PRED_DIR / f"predictions_{HARNESS}.json"
        cmd = (f"PYTHONPATH=/tmp/swebench_repo python3 -m swebench.harness.run_evaluation "
               f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
               f"--instance_ids {' '.join(eval_ids)} --max_workers 4 "
               f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
        log(f"EVAL {HARNESS} on {len(eval_ids)} instances (run_id={run_id})")
        EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
        logf = LOG_DIR / f"eval_incr_verified_full_{HARNESS}_{int(time.time())}.log"
        proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                              capture_output=True, text=True,
                              timeout=TIMEOUT_EVAL * len(eval_ids) + 600)
        logf.write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)
        log(f"  eval finished rc={proc.returncode}; log -> {logf}")
        for iid in eval_ids:
            rj = EVAL_LOG_ROOT / run_id / MODEL / iid / "report.json"
            if not rj.exists():
                cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
                rj = cands[0] if cands else None
            if rj is None or not rj.exists():
                rj = EVAL_LOG_ROOT_ALT / run_id / MODEL / iid / "report.json"
            if not rj.exists():
                cands = list((EVAL_LOG_ROOT_ALT / run_id).glob(f"*/{iid}/report.json"))
                rj = cands[0] if cands else None
            if rj is None or not rj.exists():
                ev.setdefault("infra_or_quota", []).append(iid)
                log(f"  {iid}: INFRA (no report.json)")
                continue
            try:
                rep = json.loads(rj.read_text())
                inst_rep = rep.get(iid, rep) if isinstance(rep, dict) else {}
                resolved = inst_rep.get("resolved", False)
                (ev.setdefault("resolved", []) if resolved else ev.setdefault("failed", [])).append(iid)
                log(f"  {iid}: {'RESOLVED' if resolved else 'FAILED'}")
            except Exception as e:
                ev.setdefault("infra_or_quota", []).append(f"{iid}({e})")
                log(f"  {iid}: INFRA ({e})")
    # dedup + recompute
    for k in ("resolved", "failed", "infra_or_quota", "no_patch"):
        ev[k] = sorted(set(ev.get(k, [])))
    ev["n"] = len(ev["resolved"]) + len(ev["failed"]) + len(ev["infra_or_quota"]) + len(ev["no_patch"])
    ev["run_id"] = f"incr_{ROUND}"
    ev_path.write_text(json.dumps(ev, indent=2))
    log(f"updated {ev_path}: resolved={len(ev['resolved'])} failed={len(ev['failed'])} "
        f"infra={len(ev['infra_or_quota'])} no_patch={len(ev['no_patch'])} n={ev['n']}")
    log("=== incr_eval DONE ===")

if __name__ == "__main__":
    main()
