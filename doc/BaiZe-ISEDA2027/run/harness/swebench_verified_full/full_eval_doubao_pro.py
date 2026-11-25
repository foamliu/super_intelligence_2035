#!/usr/bin/env python3
"""full_eval_doubao_pro.py — Full eval of doubao-pro 7-way SWE-bench Verified predictions.

Runs swebench_guarded_eval.py (docker mem128g/cpu16) on ALL non-empty patches
for each route, writes eval_doubao_pro_{route}.json, then generates the 7way report.

USAGE:
  PRED_SUBDIR=predictions_doubao_pro EVAL_TAG=doubao_pro_ MODEL_SUFFIX=doubao-seed-2.0-pro-cloud \
  python3 full_eval_doubao_pro.py [--route <h>] [--regen] [--dry-run]
"""
from __future__ import annotations
import json, os, subprocess, sys, time, argparse, glob
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS_DIR = HERE.parent
GUARDED_EVAL = HARNESS_DIR / "swebench_guarded_eval.py"
PRED_DIR = HERE / os.environ.get("PRED_SUBDIR", "predictions_doubao_pro")
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "evaluation"
ENRICHED = HERE / "enriched_500.json"
MODEL_SUFFIX = os.environ.get("MODEL_SUFFIX", "doubao-seed-2.0-pro-cloud")
EVAL_TAG = os.environ.get("EVAL_TAG", "doubao_pro_")
RUN_ID_PREFIX = os.environ.get("RUN_ID_PREFIX", "doubao_pro_full")
TIMEOUT_EVAL = 1800
MAX_WORKERS = int(os.environ.get("EVAL_MAX_WORKERS", "4"))

ORDER = ["cline-patched", "codex", "deepseek-harness", "claude-code",
         "pi", "hermes", "opencode"]
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek"}


def log(msg: str):
    print(f"[full-eval {time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def disp(h: str) -> str:
    return DISPLAY.get(h, h)



def rebuild_merged(route: str) -> Path:
    """Rebuild predictions_{route}.json from individual {route}__<id>.json files."""
    merged_path = PRED_DIR / f"predictions_{route}.json"
    prefix = f"{route}__"
    merged = []
    for fn in sorted(os.listdir(PRED_DIR)):
        if not fn.startswith(prefix) or not fn.endswith(".json"):
            continue
        if fn.startswith("predictions_"):
            continue
        rid = fn[len(prefix):-len(".json")]
        try:
            d = json.loads((PRED_DIR / fn).read_text())
            if isinstance(d, list):
                d = d[0] if d else {}
            if not isinstance(d, dict):
                continue
            merged.append({
                "instance_id": rid,
                "model_name_or_path": d.get("model_name_or_path", f"{disp(route)}-{MODEL_SUFFIX}"),
                "model_patch": d.get("model_patch", "") or "",
                "usage": d.get("usage"),
            })
        except Exception:
            continue
    merged_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False))
    nonempty = sum(1 for p in merged if p["model_patch"].strip())
    log(f"  rebuilt {merged_path.name}: {len(merged)} instances, {nonempty} non-empty")
    return merged_path


def run_eval(route: str, merged_path: Path, eval_ids: list[str], dry_run: bool = False) -> dict:
    run_id = f"{RUN_ID_PREFIX}_{route}"
    model = f"{route}-{MODEL_SUFFIX}"
    summary = {"harness": disp(route), "harness_code": route, "run_id": run_id,
               "n": len(eval_ids), "resolved": [], "failed": [], "infra_or_quota": []}
    if dry_run:
        log(f"  [DRY] eval {route}: {len(eval_ids)} ids (run_id={run_id})")
        return summary
    cmd = (f"python3 {GUARDED_EVAL} "
           f"--predictions_path {merged_path} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(eval_ids)} --max_workers {MAX_WORKERS} "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"  EVAL {route}: {len(eval_ids)} instances (guarded mem128g/cpu16, workers={MAX_WORKERS})")
    try:
        proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                              capture_output=True, text=True,
                              timeout=TIMEOUT_EVAL * len(eval_ids) + 600)
        logf = HERE / "logs" / f"full_eval_{route}.log"
        logf.parent.mkdir(parents=True, exist_ok=True)
        logf.write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)
        log(f"  eval {route} rc={proc.returncode}")
    except subprocess.TimeoutExpired:
        log(f"  eval {route} TIMEOUT")
        summary["infra_or_quota"] = list(eval_ids)
        return summary

    for iid in eval_ids:
        rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
        if not rj.exists():
            cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
            rj = cands[0] if cands else None
        if rj is None or not rj.exists():
            summary["infra_or_quota"].append(iid)
            continue
        try:
            rep = json.loads(rj.read_text())
            inst_rep = rep.get(iid, rep) if isinstance(rep, dict) else {}
            resolved = inst_rep.get("resolved", False)
            (summary["resolved"] if resolved else summary["failed"]).append(iid)
        except Exception as e:
            summary["infra_or_quota"].append(f"{iid}({e})")
    log(f"  eval {route}: resolved={len(summary['resolved'])} "
        f"failed={len(summary['failed'])} infra={len(summary['infra_or_quota'])}")
    return summary


def process_route(route: str, dry_run: bool = False):
    log(f"=== Full eval: {route} ===")
    merged_path = rebuild_merged(route)
    preds = json.loads(merged_path.read_text())
    eval_ids = [p["instance_id"] for p in preds if p.get("model_patch", "").strip()]
    log(f"  {route}: {len(preds)} total, {len(eval_ids)} non-empty patches to eval")
    if not eval_ids:
        log(f"  {route}: no patches to eval; skip")
        return
    result = run_eval(route, merged_path, eval_ids, dry_run=dry_run)
    if not dry_run:
        eval_file = REPORT_DIR / f"eval_{EVAL_TAG}{route}.json"
        eval_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        log(f"  WROTE {eval_file.name}")


def regen_report():
    gen = HARNESS_DIR / "gen_report_doubao_pro_7way.py"
    if not gen.exists():
        log("  gen_report_doubao_pro_7way.py not found; skip report")
        return
    log("REGEN 7way report...")
    proc = subprocess.run(["python3", str(gen)], cwd=str(HARNESS_DIR),
                          capture_output=True, text=True, timeout=120)
    log("  REGEN OK" if proc.returncode == 0
        else f"  REGEN FAILED: {proc.stderr[:200]}")


def main():
    ap = argparse.ArgumentParser(description="Full eval of doubao-pro 7-way predictions")
    ap.add_argument("--route", default=None, help="single route (default: all 7)")
    ap.add_argument("--regen", action="store_true", help="REGEN 7way report after")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    routes = [args.route] if args.route else ORDER
    for route in routes:
        process_route(route, dry_run=args.dry_run)
    if args.regen and not args.dry_run:
        regen_report()
    log("=== Done ===")


if __name__ == "__main__":
    main()

