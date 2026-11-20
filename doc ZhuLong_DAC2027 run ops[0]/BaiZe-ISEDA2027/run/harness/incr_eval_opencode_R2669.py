#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Incremental eval for opencode sphinx-doc__sphinx-10673 (R2669).

opencode predict is COMPLETE at 500/500. 498 already evaluated (414 resolved
+ 84 failed). 1 unevaluated real-patch instance: sphinx-doc__sphinx-10673.
Run swebench eval on just that instance and merge into cumulative
eval_glm53_opencode.json.
"""
from __future__ import annotations
import json, subprocess, time, glob, os
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR   = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
ENRICHED   = HERE / "enriched_500.json"
ROUND = "R2669"
MODEL_SUFFIX = "glm-5.3-flash"
TIMEOUT_EVAL = 1800
HARNESS = "opencode"
TARGET_IID = "sphinx-doc__sphinx-10673"
PY310 = "/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3"


def log(m):
    print(f"[incr-eval {time.strftime('%H:%M:%S')}] {m}", flush=True)


def load_pred(iid_file):
    try:
        d = json.loads(iid_file.read_text())
    except Exception:
        return []
    if isinstance(d, dict):
        d = [d]
    return [p for p in d if (p.get("model_patch") or "").strip()]


def run_eval(new_ids):
    merged_new = PRED_DIR / f"predictions_{HARNESS}_new_{ROUND}.json"
    all_preds = []
    for iid in new_ids:
        all_preds.extend(load_pred(PRED_DIR / f"{HARNESS}__{iid}.json"))
    merged_new.write_text(json.dumps(all_preds, indent=2))
    log(f"opencode: merged {len(all_preds)} new patches -> {merged_new.name}")
    run_id = f"verified_full_glm53_{HARNESS}_incr_{ROUND}"
    cmd = (f"{PY310} -m swebench.harness.run_evaluation "
           f"--predictions_path {merged_new} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(new_ids)} --max_workers 1 "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"opencode: EVAL {len(new_ids)} instances -> run_id={run_id}")
    EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True,
                          timeout=TIMEOUT_EVAL * len(new_ids) + 600)
    (HERE / "logs" / f"eval_{run_id}.log").write_text(
        proc.stdout + "\n[stderr]\n" + proc.stderr)
    log(f"opencode: eval rc={proc.returncode}")
    return run_id


def parse_and_merge(new_ids, run_id):
    model = f"opencode-{MODEL_SUFFIX}"
    ef = REPORT_DIR / f"eval_glm53_{HARNESS}.json"
    cum = json.loads(ef.read_text()) if ef.is_file() else {
        "harness": "opencode", "harness_code": HARNESS, "run_id": run_id,
        "n": 0, "resolved": [], "failed": [], "infra_or_quota": []}
    cum.setdefault("resolved", [])
    cum.setdefault("failed", [])
    cum.setdefault("infra_or_quota", [])
    for iid in new_ids:
        rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
        if not rj.exists():
            cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
            rj = cands[0] if cands else None
        if rj is None or not rj.exists():
            cum["infra_or_quota"].append(iid)
            log(f"  {iid}: NO report.json -> infra")
            continue
        try:
            rep = json.loads(rj.read_text())
            inst = rep.get(iid, rep) if isinstance(rep, dict) else {}
            resolved = inst.get("resolved", False)
            b = "resolved" if resolved else "failed"
            cum[b].append(iid)
            log(f"  {iid}: {'RESOLVED' if resolved else 'FAILED'}")
        except Exception as e:
            cum["infra_or_quota"].append(f"{iid}({e})")
            log(f"  {iid}: parse error -> infra ({e})")
    cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
    ef.write_text(json.dumps(cum, indent=2))
    log(f"opencode: cumulative n={cum['n']} resolved={len(cum['resolved'])} "
        f"failed={len(cum['failed'])} infra={len(cum['infra_or_quota'])} -> {ef.name}")
    return cum


if __name__ == "__main__":
    log(f"Starting incr_eval for opencode {TARGET_IID}")
    # Verify the prediction has a real patch
    preds = load_pred(PRED_DIR / f"{HARNESS}__{TARGET_IID}.json")
    if not preds:
        log(f"ERROR: {TARGET_IID} has no real patch, skipping eval")
        exit(1)
    log(f"Confirmed {TARGET_IID} has real patch ({len(preds[0].get('model_patch',''))} bytes)")
    # Check it's not already evaluated
    ef = REPORT_DIR / f"eval_glm53_{HARNESS}.json"
    done = set()
    if ef.is_file():
        d = json.loads(ef.read_text())
        done = set(d.get("resolved", []) + d.get("failed", []) + d.get("infra_or_quota", []))
    if TARGET_IID in done:
        log(f"{TARGET_IID} already evaluated, nothing to do")
        exit(0)
    run_id = run_eval([TARGET_IID])
    result = parse_and_merge([TARGET_IID], run_id)
    log(f"DONE. opencode cumulative: resolved={len(result['resolved'])} "
        f"failed={len(result['failed'])} infra={len(result['infra_or_quota'])}")
