#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Incremental eval for routes with unevaluated real-patch predictions (R2794).

Survey this round (2026-11-19 ~23:17, monitoring round after R2793):
  codex:             3 real (sklearn-14710[SPIRAL-SKIP], sphinx-8593, sphinx-8595)
                     + 6 empty -> EVAL 2 + skip 1 + merge
  deepseek-harness:  2 real (django-16642, django-16667)
                     + 11 empty -> EVAL + merge
  pi:                0 real + 2 empty -> merge only
  cline-patched:     COMPLETE 500/500 (cline303) -> skip
  claude-code:       COMPLETE 500/500 (cc295) -> skip
  opencode:          COMPLETE 500/500 (opencode415) -> skip
  hermes:            COMPLETE 500/500 (hermes444) -> skip

CPU guardrail (运维令 11-02 + 11-19 CPU-spiral kill at 09:18):
  ALL evals run with CPU limits:
     taskset -ac 0-15 (pin to 16 cores, max 1600% CPU << 8000% kill threshold)
     OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
  CPU_SPIRAL_SKIP = {scikit-learn__scikit-learn-14710} (known spiral, mark infra, no eval).
  Load at launch = 41/224 (18.5%), MM 2x3 predict running nice19 alongside.
"""
from __future__ import annotations
import json, subprocess, time, glob, os
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "evaluation"
ENRICHED = HERE / "enriched_500.json"
ROUND = "R2794"
TIMEOUT_EVAL = 1800
PY310 = "/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3"
ROUTES = ["pi", "codex", "deepseek-harness"]
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek", "claude-code": "cc"}

CPU_SPIRAL_SKIP = {"scikit-learn__scikit-learn-14710"}
CPU_LIMIT_ENV = "OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1"
CPU_LIMIT_TASKSET = "taskset -ac 0-15"


def disp(h): return DISPLAY.get(h, h)


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
        if load_pred(Path(p)):
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
    log(f"{disp(harness)}: merged {len(all_preds)} new patches -> {merged_new.name}")
    run_id = f"verified_full_glm53_{harness}_incr_{ROUND}"
    cmd = (f"{CPU_LIMIT_ENV} {CPU_LIMIT_TASKSET} nice -n 19 ionice -c 3 {PY310} "
           f"-m swebench.harness.run_evaluation "
           f"--predictions_path {merged_new} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(new_ids)} --max_workers 1 "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"{disp(harness)}: EVAL {len(new_ids)} instances [CPU-limited 16 cores] -> run_id={run_id}")
    EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True,
                          timeout=TIMEOUT_EVAL * len(new_ids) + 600)
    (HERE / "logs" / f"eval_{run_id}.log").write_text(
        proc.stdout + "\n[stderr]\n" + proc.stderr)
    log(f"{disp(harness)}: eval rc={proc.returncode}")
    return run_id


def find_report(run_id, iid):
    cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
    return cands[0] if cands else None


def parse_and_merge(harness, real_ids, empty_ids, spiral_ids, run_id):
    ef = REPORT_DIR / f"eval_glm53_{harness}.json"
    run_id_eff = run_id or f"no_eval_{ROUND}"
    cum = json.loads(ef.read_text()) if ef.is_file() else {
        "harness": harness, "harness_code": harness, "run_id": run_id_eff,
        "n": 0, "resolved": [], "failed": [], "infra_or_quota": []}
    for k in ("resolved", "failed", "infra_or_quota", "empty_patch", "no_patch"):
        cum.setdefault(k, [])
    for iid in real_ids:
        rj = find_report(run_id_eff, iid)
        if rj is None or not rj.exists():
            cum["infra_or_quota"].append(iid)
            log(f"  {iid}: NO report.json -> infra")
            continue
        try:
            rep = json.loads(rj.read_text())
            inst = rep.get(iid, rep) if isinstance(rep, dict) else {}
            resolved = inst.get("resolved", False)
            cum["resolved" if resolved else "failed"].append(iid)
            log(f"  {iid}: {'RESOLVED' if resolved else 'FAILED'}")
        except Exception as e:
            cum["infra_or_quota"].append(f"{iid}({e})")
            log(f"  {iid}: parse error -> infra ({e})")
    for iid in spiral_ids:
        tag = f"{iid}(cpu-spiral-skip)"
        if tag not in cum["infra_or_quota"] and iid not in cum["resolved"] and iid not in cum["failed"]:
            cum["infra_or_quota"].append(tag)
            log(f"  {iid}: -> infra (CPU-spiral-skip)")
    for iid in empty_ids:
        if iid not in cum["failed"] and iid not in cum["resolved"]:
            cum["empty_patch"].append(iid)
            cum["failed"].append(iid)
            log(f"  {iid}: EMPTY PATCH -> failed")
    cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
    cum["total_predictions"] = len(glob.glob(str(PRED_DIR / f"{harness}__*.json")))
    cum["evaluated"] = cum["n"]
    ef.write_text(json.dumps(cum, indent=2))
    log(f"{disp(harness)}: cumulative n={cum['n']} resolved={len(cum['resolved'])} "
        f"failed={len(cum['failed'])} infra={len(cum['infra_or_quota'])} "
        f"empty_patch={len(cum.get('empty_patch', []))} total_pred={cum['total_predictions']}")
    return cum


if __name__ == "__main__":
    log(f"Starting incr_eval_all {ROUND} (CPU-limited: taskset 0-15 + OMP=1)")
    summary = {}
    for h in ROUTES:
        log(f"--- {disp(h)} ---")
        real_new, empty_new, done = get_unevaluated(h)
        spiral_ids = [iid for iid in real_new if iid in CPU_SPIRAL_SKIP]
        eval_ids = [iid for iid in real_new if iid not in CPU_SPIRAL_SKIP]
        if spiral_ids:
            log(f"{disp(h)}: CPU_SPIRAL_SKIP -> {spiral_ids} (mark infra, no eval)")
        log(f"{disp(h)}: unevaluated real_patch={len(eval_ids)} (spiral={len(spiral_ids)}) empty_patch={len(empty_new)}")
        if not eval_ids and not empty_new and not spiral_ids:
            log(f"{disp(h)}: nothing to do")
            continue
        run_id = None
        if eval_ids:
            run_id = run_eval(h, eval_ids)
        result = parse_and_merge(h, eval_ids, empty_new, spiral_ids, run_id or f"no_eval_{ROUND}")
        summary[h] = {
            "resolved": len(result["resolved"]),
            "failed": len(result["failed"]),
            "infra": len(result["infra_or_quota"]),
            "n": result["n"],
            "new_real_evald": len(eval_ids),
            "new_empty": len(empty_new),
            "spiral": len(spiral_ids),
        }
    log("=== SUMMARY ===")
    for h, s in summary.items():
        log(f"{disp(h)}: resolved={s['resolved']} failed={s['failed']} infra={s['infra']} "
            f"n={s['n']} (new_real={s['new_real_evald']} new_empty={s['new_empty']} spiral={s['spiral']})")
    log("DONE")
