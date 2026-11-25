#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""incr_eval R1589: scan backlog + run incremental eval on new predictions."""
from __future__ import annotations
import json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED_DIR = HERE / "predictions"
REPORT_DIR = HERE / "reports"
LOG_DIR = HERE / "logs"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
ENRICHED = HERE / "enriched_500.json"
TIMEOUT_EVAL = 1800
PROXY = "http://172.19.92.25:13128"
HARNESS_ORDER = ["cline-patched", "codex", "deepseek-harness",
                 "opencode", "pi", "claude-code", "hermes"]
DISPLAY = {"cline-patched": "cline"}

def disp(h): return DISPLAY.get(h, h)
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

def load_eval(harness):
    ef = REPORT_DIR / f"eval_{harness}.json"
    if ef.exists(): return json.loads(ef.read_text())
    return {"harness": disp(harness), "harness_code": harness,
            "run_id": f"verified_full_{harness}",
            "n": 0, "resolved": [], "failed": [], "infra_or_quota": [], "no_patch": []}

def scan_backlog(harness):
    merged = merge_predictions(harness)  # always re-merge to pick up new predictions
    preds = json.loads(merged.read_text()) if merged.exists() else []
    ev = load_eval(harness)
    already = set(ev.get("resolved", []) + ev.get("failed", [])
                  + ev.get("infra_or_quota", []) + ev.get("no_patch", []))
    backlog = []
    for p in preds:
        iid = p.get("instance_id", "")
        patch = p.get("model_patch", "").strip()
        if not patch or iid in already: continue
        backlog.append({"instance_id": iid, "patchlen": len(patch)})
    return backlog

def run_incr_eval(harness, eval_ids):
    merged = PRED_DIR / f"predictions_{harness}.json"
    run_id = f"verified_full_{harness}"
    max_workers = int(os.environ.get("EVAL_MAX_WORKERS", "4"))
    cmd = (f"python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(eval_ids)} --max_workers {max_workers} "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"EVAL {disp(harness)} on {len(eval_ids)} instances (workers={max_workers})")
    EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    logf = LOG_DIR / f"eval_incr_verified_full_{harness}_{int(time.time())}.log"
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True,
                          timeout=TIMEOUT_EVAL * len(eval_ids) + 600)
    logf.write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)
    log(f"  eval finished rc={proc.returncode}; log -> {logf}")
    model = f"{disp(harness)}-kimi-k2.6-cloud"
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
    ev = load_eval(harness)
    for iid, status in new_results.items():
        if status == "resolved":
            if iid not in ev["resolved"]: ev["resolved"].append(iid)
        elif status == "failed":
            if iid not in ev["failed"]: ev["failed"].append(iid)
        else:
            if iid not in ev["infra_or_quota"]: ev["infra_or_quota"].append(iid)
    ev["n"] = len(ev["resolved"]) + len(ev["failed"]) + len(ev["infra_or_quota"]) + len(ev.get("no_patch", []))
    ef = REPORT_DIR / f"eval_{harness}.json"
    ef.write_text(json.dumps(ev, indent=2))
    log(f"updated {ef}: resolved={len(ev['resolved'])} failed={len(ev['failed'])} "
        f"infra={len(ev['infra_or_quota'])} no_patch={len(ev.get('no_patch', []))} n={ev['n']}")

def main():
    R = "R1589"
    log(f"=== incr_eval {R} start ===")
    all_backlog = {}
    total_backlog = 0
    for h in HARNESS_ORDER:
        bl = scan_backlog(h)
        all_backlog[h] = bl
        total_backlog += len(bl)
        for item in bl:
            log(f"  BACKLOG {disp(h):20s} {item['instance_id']:50s} patchlen={item['patchlen']}")
    bl_report = {"round": R, "total_backlog": total_backlog,
                 "per_harness": {h: bl for h, bl in all_backlog.items()}}
    blf = REPORT_DIR / f"backlog_scan_{R}.json"
    blf.write_text(json.dumps(bl_report, indent=2))
    log(f"backlog scan: {total_backlog} items total -> {blf}")
    if total_backlog == 0:
        log("No backlog items. Nothing to eval.")
        log(f"=== incr_eval {R} DONE (no backlog) ===")
        return
    for h in HARNESS_ORDER:
        bl = all_backlog[h]
        if not bl: continue
        eval_ids = [item["instance_id"] for item in bl]
        log(f"=== incr_eval for {disp(h)}: {eval_ids} ===")
        merge_predictions(h)
        new_results = run_incr_eval(h, eval_ids)
        update_eval_json(h, new_results)
    log("=== FINAL EVAL SUMMARY ===")
    for h in HARNESS_ORDER:
        ev = load_eval(h)
        log(f"  {disp(h):20s}: resolved={len(ev['resolved'])} failed={len(ev['failed'])} "
            f"infra={len(ev['infra_or_quota'])} no_patch={len(ev.get('no_patch', []))} n={ev['n']}")
    log(f"=== incr_eval {R} DONE ===")

if __name__ == "__main__":
    main()
