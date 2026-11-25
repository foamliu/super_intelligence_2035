#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R1594: incr_eval for 5 genuine backlog items.
cline-patched(2): astropy__astropy-7336, django__django-11087
deepseek-harness(3): matplotlib__matplotlib-25287, 25775, 26113
"""
import json, os, subprocess, sys, time, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED_DIR = HERE / "predictions"
REPORT_DIR = HERE / "reports"
LOG_DIR = HERE / "logs"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
ENRICHED = HERE / "enriched_500.json"
TIMEOUT_EVAL = 1800
PY = "/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3"

CONFIGS = [
    {"harness":"cline-patched","display":"cline","model":"cline-kimi-k2.6-cloud",
     "run_id":"verified_full_cline-patched_rerun_R1594",
     "ids":["astropy__astropy-7336","django__django-11087"]},
    {"harness":"deepseek-harness","display":"deepseek-harness","model":"deepseek-harness-kimi-k2.6-cloud",
     "run_id":"verified_full_deepseek-harness_rerun_R1594",
     "ids":["matplotlib__matplotlib-25287","matplotlib__matplotlib-25775","matplotlib__matplotlib-26113"]},
]

def log(m): print(f"[R1594 {time.strftime('%H:%M:%S')}] {m}", flush=True)

def merge_predictions(harness):
    all_preds = []
    for f in sorted(PRED_DIR.glob(f"{harness}__*.json")):
        if f.stat().st_size < 30: continue
        try:
            preds = json.loads(f.read_text())
            if isinstance(preds, dict): preds = [preds]
            for p in preds:
                if p.get("model_patch","").strip(): all_preds.append(p)
        except Exception: pass
    merged = PRED_DIR / f"predictions_{harness}.json"
    merged.write_text(json.dumps(all_preds, indent=2))
    log(f"  merged {len(all_preds)} predictions -> {merged}")
    return merged

def run_eval(merged, run_id, model, eval_ids):
    max_workers = min(4, len(eval_ids))
    cmd = (f"python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(eval_ids)} --max_workers {max_workers} "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"  EVAL run_id={run_id} on {len(eval_ids)} instances")
    logf = LOG_DIR / f"eval_incr_{run_id}_{int(time.time())}.log"
    try:
        proc = subprocess.run(["sg","docker","-c",cmd], cwd=str(HERE),
                              capture_output=True, text=True,
                              timeout=TIMEOUT_EVAL*len(eval_ids)+600)
        logf.write_text(proc.stdout+"\n[stderr]\n"+proc.stderr)
        log(f"  eval finished rc={proc.returncode}; log -> {logf}")
        for line in proc.stdout.splitlines():
            if any(k in line for k in ("resolved","unresolved","skipping","submitted","completed","error","Error")):
                log(f"    {line}")
        return True
    except subprocess.TimeoutExpired:
        logf.write_text("TIMEOUT in run_eval")
        log(f"  eval TIMEOUT; log -> {logf}")
        return False

def parse_results(run_id, model, eval_ids, harness):
    new_dir = EVAL_LOG_ROOT / run_id / model
    summary_file = REPORT_DIR / f"eval_{harness}.json"
    summary = json.loads(summary_file.read_text()) if summary_file.exists() else {}
    for k in ("resolved","failed","infra_or_quota","no_patch"): summary.setdefault(k, [])
    for iid in eval_ids:
        rj = new_dir / iid / "report.json"
        for k in ("resolved","failed","infra_or_quota","no_patch"):
            summary[k] = [x for x in summary[k] if x != iid and not x.startswith(f"{iid}(")]
        if not rj.exists():
            summary["infra_or_quota"].append(iid)
            log(f"    {iid}: NO report.json -> infra")
            continue
        try:
            rep = json.loads(rj.read_text())
            inst_rep = rep.get(iid, rep) if isinstance(rep, dict) else {}
            resolved = inst_rep.get("resolved", False)
            (summary["resolved"] if resolved else summary["failed"]).append(iid)
            log(f"    {iid}: {'RESOLVED' if resolved else 'FAILED'}")
        except Exception as e:
            summary["infra_or_quota"].append(f"{iid}({e})")
            log(f"    {iid}: parse error -> infra ({e})")
    summary["n"] = len(summary["resolved"])+len(summary["failed"])+len(summary["infra_or_quota"])
    summary_file.write_text(json.dumps(summary, indent=2))
    log(f"  updated {summary_file}: resolved={len(summary['resolved'])} failed={len(summary['failed'])} infra={len(summary['infra_or_quota'])} n={summary['n']}")

def main():
    log("=== R1594 incr_eval for 5 backlog items ===")
    for cfg in CONFIGS:
        h = cfg["harness"]
        log(f"--- {h}: {len(cfg['ids'])} items ---")
        merged = merge_predictions(h)
        ok = run_eval(merged, cfg["run_id"], cfg["model"], cfg["ids"])
        if ok:
            parse_results(cfg["run_id"], cfg["model"], cfg["ids"], h)
        else:
            log(f"  eval failed for {h}, adding to infra")
            sf = REPORT_DIR / f"eval_{h}.json"
            summary = json.loads(sf.read_text()) if sf.exists() else {}
            for k in ("resolved","failed","infra_or_quota","no_patch"): summary.setdefault(k, [])
            for iid in cfg["ids"]:
                for k in ("resolved","failed","infra_or_quota","no_patch"):
                    summary[k] = [x for x in summary[k] if x != iid and not x.startswith(f"{iid}(")]
                summary["infra_or_quota"].append(iid)
            summary["n"] = len(summary["resolved"])+len(summary["failed"])+len(summary["infra_or_quota"])
            sf.write_text(json.dumps(summary, indent=2))
    log("=== regen report ===")
    os.chdir(HERE.parent)
    proc = subprocess.run([PY,"gen_report_swebench_verified_full500_zh.py"],
                          capture_output=True, text=True, timeout=120)
    logf = LOG_DIR / f"regen_R1594_{int(time.time())}.log"
    logf.write_text(proc.stdout+proc.stderr)
    for line in proc.stdout.splitlines():
        if any(k in line.lower() for k in ("cline","deepseek","resolved","report")):
            log(f"  {line}")
    log("=== R1594 DONE ===")

if __name__ == "__main__":
    main()
