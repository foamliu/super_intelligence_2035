#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Incremental eval for glm-5.3-flash SWE-bench Verified (R2180 wake-up cycle).

Finds real-patch predict files NOT yet in the cumulative eval_glm53_<h>.json,
runs swebench eval on just those new instances (per-round run_id), parses
report.json, and MERGES results into the cumulative eval_glm53_<h>.json.
Pattern mirrors run_verified_full.py phase_eval + parse_eval, but merge-into-
cumulative. Per-round merged file: predictions_<h>_new_R2180.json.
"""
from __future__ import annotations
import json, subprocess, time, glob, os
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR   = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
ENRICHED   = HERE / "enriched_500.json"
ROUND = "R2273"
MODEL_SUFFIX = "glm-5.3-flash"
TIMEOUT_EVAL = 1800
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek"}
HARNESSES = ["cline-patched", "codex", "opencode", "claude-code", "pi", "hermes", "deepseek-harness"]


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


def find_new(harness):
    ef = REPORT_DIR / f"eval_glm53_{harness}.json"
    done = set()
    if ef.is_file():
        d = json.loads(ef.read_text())
        done = set(d.get("resolved", []) + d.get("failed", []) + d.get("infra_or_quota", []))
    new_ids = []
    for f in sorted(glob.glob(str(PRED_DIR / f"{harness}__*.json"))):
        iid = os.path.basename(f).replace(f"{harness}__", "").replace(".json", "")
        if iid in done:
            continue
        if load_pred(Path(f)):
            new_ids.append(iid)
    return new_ids


def run_eval(harness, new_ids):
    merged_new = PRED_DIR / f"predictions_{harness}_new_{ROUND}.json"
    all_preds = []
    for iid in new_ids:
        all_preds.extend(load_pred(PRED_DIR / f"{harness}__{iid}.json"))
    merged_new.write_text(json.dumps(all_preds, indent=2))
    log(f"{disp(harness)}: merged {len(all_preds)} new patches -> {merged_new.name}")
    run_id = f"verified_full_glm53_{harness}_incr_{ROUND}"
    cmd = (f"python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {merged_new} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(new_ids)} --max_workers 1 "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"{disp(harness)}: EVAL {len(new_ids)} instances -> run_id={run_id}")
    EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True,
                          timeout=TIMEOUT_EVAL * len(new_ids) + 600)
    (HERE / "logs" / f"eval_{run_id}.log").write_text(
        proc.stdout + "\n[stderr]\n" + proc.stderr)
    log(f"{disp(harness)}: eval rc={proc.returncode}")
    return run_id


def parse_and_merge(harness, new_ids, run_id):
    model = f"{disp(harness)}-{MODEL_SUFFIX}"
    ef = REPORT_DIR / f"eval_glm53_{harness}.json"
    cum = {"harness": disp(harness), "harness_code": harness, "run_id": run_id,
           "n": 0, "resolved": [], "failed": [], "infra_or_quota": []}
    if ef.is_file():
        cum = json.loads(ef.read_text())
        cum.setdefault("resolved", []); cum.setdefault("failed", [])
        cum.setdefault("infra_or_quota", [])
    pr = {"harness": disp(harness), "run_id": run_id, "round": ROUND,
          "n": len(new_ids), "resolved": [], "failed": [], "infra_or_quota": []}
    for iid in new_ids:
        rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
        if not rj.exists():
            cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
            rj = cands[0] if cands else None
        if rj is None or not rj.exists():
            cum["infra_or_quota"].append(iid); pr["infra_or_quota"].append(iid)
            log(f"  {iid}: NO report.json -> infra"); continue
        try:
            rep = json.loads(rj.read_text())
            inst = rep.get(iid, rep) if isinstance(rep, dict) else {}
            resolved = inst.get("resolved", False)
            b = "resolved" if resolved else "failed"
            cum[b].append(iid); pr[b].append(iid)
            log(f"  {iid}: {'RESOLVED' if resolved else 'FAILED'}")
        except Exception as e:
            cum["infra_or_quota"].append(f"{iid}({e})"); pr["infra_or_quota"].append(f"{iid}({e})")
            log(f"  {iid}: parse error -> infra ({e})")
    cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
    ef.write_text(json.dumps(cum, indent=2))
    pf = HERE / f"{disp(harness)}-{MODEL_SUFFIX}.verified_full_glm53_{harness}_incr_{ROUND}.json"
    pf.write_text(json.dumps(pr, indent=2))
    log(f"{disp(harness)}: cumulative n={cum['n']} resolved={len(cum['resolved'])} "
        f"failed={len(cum['failed'])} infra={len(cum['infra_or_quota'])} -> {ef.name}")
    return pr


def main():
    log(f"=== incr_eval {ROUND} start ===")
    grand = {"resolved": 0, "failed": 0, "infra": 0, "instances": 0}
    any_new = False
    for h in HARNESSES:
        new_ids = find_new(h)
        if not new_ids:
            log(f"{disp(h)}: 0 new instances, skip"); continue
        any_new = True
        print(f"\n=== {disp(h)} {ROUND} ===")
        print(f"new instances: {len(new_ids)} {new_ids}")
        run_id = run_eval(h, new_ids)
        pr = parse_and_merge(h, new_ids, run_id)
        grand["resolved"] += len(pr["resolved"])
        grand["failed"] += len(pr["failed"])
        grand["infra"] += len(pr["infra_or_quota"])
        grand["instances"] += len(new_ids)
    log(f"=== incr_eval {ROUND} done: {grand['instances']} instances, "
        f"+{grand['resolved']}resolved +{grand['failed']}failed +{grand['infra']}infra ===")
    if not any_new:
        log("no new instances across all routes this round")


if __name__ == "__main__":
    main()
