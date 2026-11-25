#!/usr/bin/env python3
"""Incremental eval for backlog items (R1153, 2026-11-01).

Re-merges predictions for the given harness (to include newly produced patches)
then runs swebench docker eval on only the specified instance IDs, and updates
the eval_<harness>.json summary in reports/.

Usage:
  python3 incr_eval_backlog.py <harness> <instance_id> [<instance_id> ...]
"""
import json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED_DIR = HERE / "predictions"
REPORT_DIR = HERE / "reports"
LOG_DIR = HERE / "logs"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
ENRICHED = HERE / "enriched_500.json"
IDS_FILE = HERE / "verified_500_ids.txt"
TIMEOUT_EVAL = 1800

DISPLAY = {"cline-patched": "cline"}
def disp(h): return DISPLAY.get(h, h)

def log(m): print(f"[incr-eval {time.strftime('%H:%M:%S')}] {m}", flush=True)

def merge_predictions(harness):
    """Re-merge ALL per-instance prediction files into predictions_<harness>.json."""
    ids = IDS_FILE.read_text().split()
    all_preds = []
    for iid in ids:
        f = PRED_DIR / f"{harness}__{iid}.json"
        if f.exists() and f.stat().st_size > 30:
            try:
                preds = json.loads(f.read_text())
                if isinstance(preds, dict):
                    preds = [preds]
                preds = [p for p in preds if p.get("model_patch", "").strip()]
                all_preds.extend(preds)
            except Exception:
                pass
    merged = PRED_DIR / f"predictions_{harness}.json"
    merged.write_text(json.dumps(all_preds, indent=2))
    log(f"merged {len(all_preds)}/{len(ids)} predictions -> {merged}")
    return merged

def run_eval(harness, instance_ids, merged):
    run_id = f"verified_full_{harness}"
    max_workers = int(os.environ.get("EVAL_MAX_WORKERS", "4"))
    cmd = (f"python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(instance_ids)} --max_workers {max_workers} "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"EVAL {disp(harness)} on {len(instance_ids)} instances: {instance_ids}")
    EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    logf = LOG_DIR / f"eval_incr_{run_id}_{int(time.time())}.log"
    timeout = TIMEOUT_EVAL * len(instance_ids) + 600
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True, timeout=timeout)
    logf.write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)
    log(f"  eval finished rc={proc.returncode}; log -> {logf}")
    return run_id

def parse_and_update(run_id, eval_ids, harness):
    """Parse new report.json files and merge into existing eval summary."""
    model = f"{disp(harness)}-kimi-k2.6-cloud"
    summary_file = REPORT_DIR / f"eval_{harness}.json"
    if summary_file.exists():
        summary = json.loads(summary_file.read_text())
    else:
        summary = {"harness": disp(harness), "harness_code": harness, "run_id": run_id,
                   "resolved": [], "failed": [], "infra_or_quota": []}
    # ensure lists
    for k in ("resolved", "failed", "infra_or_quota"):
        summary.setdefault(k, [])

    for iid in eval_ids:
        rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
        if not rj.exists():
            cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
            rj = cands[0] if cands else None
        # remove from all lists first (in case of re-eval)
        for k in ("resolved", "failed", "infra_or_quota"):
            summary[k] = [x for x in summary[k] if x != iid and not x.startswith(f"{iid}(")]
        if rj is None or not rj.exists():
            summary["infra_or_quota"].append(iid)
            log(f"  {iid}: NO report.json -> infra")
            continue
        try:
            rep = json.loads(rj.read_text())
            inst_rep = rep.get(iid, rep) if isinstance(rep, dict) else {}
            resolved = inst_rep.get("resolved", False)
            (summary["resolved"] if resolved else summary["failed"]).append(iid)
            log(f"  {iid}: {'RESOLVED' if resolved else 'FAILED'}")
        except Exception as e:
            summary["infra_or_quota"].append(f"{iid}({e})")
            log(f"  {iid}: parse error -> infra ({e})")

    summary["n"] = len(summary["resolved"]) + len(summary["failed"]) + len(summary["infra_or_quota"])
    summary_file.write_text(json.dumps(summary, indent=2))
    log(f"updated {summary_file}: resolved={len(summary['resolved'])} "
        f"failed={len(summary['failed'])} infra={len(summary['infra_or_quota'])}")
    return summary

def main():
    if len(sys.argv) < 3:
        print("Usage: incr_eval_backlog.py <harness> <instance_id> [<instance_id> ...]")
        sys.exit(1)
    harness = sys.argv[1]
    instance_ids = sys.argv[2:]
    log(f"=== incr_eval for {disp(harness)}: {instance_ids} ===")
    merged = merge_predictions(harness)
    # verify the target instances are in the merged file with non-empty patch
    preds = json.loads(merged.read_text())
    pred_ids = {p["instance_id"] for p in preds if p.get("model_patch", "").strip()}
    missing = [iid for iid in instance_ids if iid not in pred_ids]
    if missing:
        log(f"WARNING: {missing} not found in merged predictions (no patch?)")
    eval_ids = [iid for iid in instance_ids if iid in pred_ids]
    if not eval_ids:
        log("No instances with patches to eval. Done.")
        return
    run_id = run_eval(harness, eval_ids, merged)
    parse_and_update(run_id, eval_ids, harness)
    log("=== incr_eval DONE ===")

if __name__ == "__main__":
    main()
