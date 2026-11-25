#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Incremental eval for all routes with unevaluated real-patch predictions (R2672).

Routes with new real-patch predictions (detected R2672 13:0x):
  cline-patched:  1  (django__django-12754)
  hermes:         1  (pylint-dev__pylint-7080)
  claude-code:    2  (django__django-11138, django__django-11149)
Also merge empty-patch for: codex(6), hermes(1), pi(2), opencode(1)
"""
from __future__ import annotations
import json, subprocess, time, glob, os, sys
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
ENRICHED = HERE / "enriched_500.json"
ROUND = "R2672"
MODEL_SUFFIX = "glm-5.3-flash"
TIMEOUT_EVAL = 1800
PY310 = "/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3"
ROUTES = ["cline-patched", "hermes", "claude-code", "codex", "pi", "opencode", "deepseek-harness"]

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
        patch_preds = load_pred(Path(p))
        if patch_preds:
            real_new.append(iid)
        else:
            empty_new.append(iid)
    return real_new, empty_new, done

def run_eval(harness, new_ids):
    merged_new = PRED_DIR / f"predictions_{harness}_new_{ROUND}.json"
    all_preds = []
    for iid in new_ids:
        all_preds.extend(load_pred(PRED_DIR / f"{harness}__{iid}.json"))
    merged_new.write_text(json.dumps(all_preds, indent=2))
    log(f"{harness}: merged {len(all_preds)} new patches -> {merged_new.name}")
    run_id = f"verified_full_glm53_{harness}_incr_{ROUND}"
    cmd = (f"{PY310} -m swebench.harness.run_evaluation "
           f"--predictions_path {merged_new} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(new_ids)} --max_workers 1 "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"{harness}: EVAL {len(new_ids)} instances -> run_id={run_id}")
    EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True,
                          timeout=TIMEOUT_EVAL * len(new_ids) + 600)
    (HERE / "logs" / f"eval_{run_id}.log").write_text(
        proc.stdout + "\n[stderr]\n" + proc.stderr)
    log(f"{harness}: eval rc={proc.returncode}")
    return run_id

def parse_and_merge(harness, real_ids, empty_ids, run_id):
    model = f"{harness}-{MODEL_SUFFIX}"
    ef = REPORT_DIR / f"eval_glm53_{harness}.json"
    cum = json.loads(ef.read_text()) if ef.is_file() else {
        "harness": harness, "harness_code": harness, "run_id": run_id,
        "n": 0, "resolved": [], "failed": [], "infra_or_quota": []}
    cum.setdefault("resolved", [])
    cum.setdefault("failed", [])
    cum.setdefault("infra_or_quota", [])
    cum.setdefault("empty_patch", [])
    for iid in real_ids:
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
    for iid in empty_ids:
        cum["empty_patch"].append(iid)
        cum["failed"].append(iid)
        log(f"  {iid}: EMPTY PATCH -> failed")
    cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
    ef.write_text(json.dumps(cum, indent=2))
    log(f"{harness}: cumulative n={cum['n']} resolved={len(cum['resolved'])} "
        f"failed={len(cum['failed'])} infra={len(cum['infra_or_quota'])} "
        f"empty_patch={len(cum.get('empty_patch', []))} -> {ef.name}")
    return cum

if __name__ == "__main__":
    log(f"Starting incr_eval_all {ROUND}")
    summary = {}
    for h in ROUTES:
        log(f"--- {h} ---")
        real_new, empty_new, done = get_unevaluated(h)
        log(f"{h}: unevaluated real_patch={len(real_new)} empty_patch={len(empty_new)}")
        if not real_new and not empty_new:
            log(f"{h}: nothing to do")
            continue
        run_id = None
        if real_new:
            run_id = run_eval(h, real_new)
        result = parse_and_merge(h, real_new, empty_new, run_id or f"no_eval_{ROUND}")
        summary[h] = {
            "resolved": len(result["resolved"]),
            "failed": len(result["failed"]),
            "infra": len(result["infra_or_quota"]),
            "n": result["n"],
            "new_real_evald": len(real_new),
            "new_empty": len(empty_new),
        }
    log("=== SUMMARY ===")
    for h, s in summary.items():
        log(f"{h}: resolved={s['resolved']} failed={s['failed']} infra={s['infra']} "
            f"n={s['n']} (new_real={s['new_real_evald']} new_empty={s['new_empty']})")
    log("DONE")
