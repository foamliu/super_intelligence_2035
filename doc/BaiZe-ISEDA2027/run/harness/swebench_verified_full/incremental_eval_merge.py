#!/usr/bin/env python3
"""incremental_eval_merge.py — Incremental eval+merge of recovered infra-rerun patches.

2026-11-24: The orchestrator only evals AFTER full predict completes (multi-night).
This script evals patches recovered SO FAR, so the 7way report reflects progress
each night. Safe to run while predict is ongoing (eval uses docker, predict uses host).

Flow: rebuild merged → find non-empty rerun IDs in failed/infra → guarded eval → merge.
USAGE: python3 incremental_eval_merge.py --route cline-patched [--regen] [--dry-run]
       python3 incremental_eval_merge.py --all [--regen]
"""
from __future__ import annotations
import json, os, subprocess, sys, time, argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS_DIR = HERE.parent
GUARDED_EVAL = HARNESS_DIR / "swebench_guarded_eval.py"
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "evaluation"
IDS_DIR = HERE / "rerun_ids"
ENRICHED = HERE / "enriched_500.json"
MODEL_SUFFIX = os.environ.get("MODEL_SUFFIX", "glm-5.3-flash")
EVAL_TAG = os.environ.get("EVAL_TAG", "glm53_")
TIMEOUT_EVAL = 1800
ORDER = ["cline-patched", "codex", "deepseek-harness", "claude-code",
         "pi", "hermes", "opencode"]
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek"}


def log(msg: str):
    print(f"[incr-merge {time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def disp(h: str) -> str:
    return DISPLAY.get(h, h)

def get_rerun_ids(route: str) -> list[str]:
    fn = IDS_DIR / f"{route}_rerun_ids.txt"
    if not fn.exists():
        return []
    return [l.strip() for l in fn.read_text().splitlines() if l.strip()]


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
    log(f"  rebuilt {merged_path.name}: {len(merged)} instances, "
        f"{sum(1 for p in merged if p['model_patch'].strip())} non-empty")
    return merged_path


def find_reeval_targets(route: str, rerun_ids: list[str]) -> list[str]:
    """Rerun IDs with non-empty patch AND currently in failed/infra (need re-eval)."""
    eval_file = REPORT_DIR / f"eval_{EVAL_TAG}{route}.json"
    if not eval_file.exists():
        return []
    ev = json.loads(eval_file.read_text())
    failed = set(ev.get("failed", []))
    infra = set(ev.get("infra_or_quota", []))
    targets = []
    for rid in rerun_ids:
        fpath = PRED_DIR / f"{route}__{rid}.json"
        if not fpath.exists():
            continue
        try:
            d = json.loads(fpath.read_text())
            if isinstance(d, list):
                d = d[0] if d else {}
            mp = (d.get("model_patch", "") or "").strip()
            if mp and (rid in failed or rid in infra):
                targets.append(rid)
        except Exception:
            continue
    return targets


def run_eval(route: str, merged_path: Path, eval_ids: list[str], dry_run: bool = False) -> dict:
    run_id = f"rerun_incr_{route}_{time.strftime('%m%d%H%M')}"
    max_workers = int(os.environ.get("EVAL_MAX_WORKERS", "4"))
    model = f"{disp(route)}-{MODEL_SUFFIX}"
    if dry_run:
        log(f"  [DRY] eval {route}: {len(eval_ids)} ids (run_id={run_id})")
        return {"resolved": [], "failed": [], "infra_or_quota": []}
    cmd = (f"python3 {GUARDED_EVAL} "
           f"--predictions_path {merged_path} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(eval_ids)} --max_workers {max_workers} "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"  EVAL {route}: {len(eval_ids)} instances (guarded mem128g/cpu16, run_id={run_id})")
    try:
        proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                              capture_output=True, text=True,
                              timeout=TIMEOUT_EVAL * len(eval_ids) + 600)
        logf = HERE / "logs" / f"rerun_incr_eval_{route}.log"
        logf.parent.mkdir(parents=True, exist_ok=True)
        logf.write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)
        log(f"  eval {route} rc={proc.returncode}")
    except subprocess.TimeoutExpired:
        log(f"  eval {route} TIMEOUT")
        return {"resolved": [], "failed": [], "infra_or_quota": eval_ids}
    result = {"resolved": [], "failed": [], "infra_or_quota": []}
    for iid in eval_ids:
        rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
        if not rj.exists():
            cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
            rj = cands[0] if cands else None
        if rj is None or not rj.exists():
            result["infra_or_quota"].append(iid); continue
        try:
            rep = json.loads(rj.read_text())
            inst_rep = rep.get(iid, rep) if isinstance(rep, dict) else {}
            (result["resolved"] if inst_rep.get("resolved", False)
             else result["failed"]).append(iid)
        except Exception as e:
            result["infra_or_quota"].append(f"{iid}({e})")
    log(f"  eval {route}: resolved={len(result['resolved'])} "
        f"failed={len(result['failed'])} infra={len(result['infra_or_quota'])}")
    return result


def merge_eval(route: str, rerun_result: dict, dry_run: bool = False):
    eval_file = REPORT_DIR / f"eval_{EVAL_TAG}{route}.json"
    if not eval_file.exists():
        log(f"  no eval file for {route}; skip merge"); return
    ev = json.loads(eval_file.read_text())
    rs = set(ev.get("resolved", []))
    fs = set(ev.get("failed", []))
    is_ = set(ev.get("infra_or_quota", []))
    rerun_all = set(rerun_result["resolved"] + rerun_result["failed"] + rerun_result["infra_or_quota"])
    for iid in rerun_all:
        rs.discard(iid); fs.discard(iid); is_.discard(iid)
    rs.update(rerun_result["resolved"])
    fs.update(rerun_result["failed"])
    is_.update(rerun_result["infra_or_quota"])
    ev["resolved"] = sorted(rs)
    ev["failed"] = sorted(fs)
    ev["infra_or_quota"] = sorted(is_)
    ev["n"] = len(rs) + len(fs) + len(is_)
    ev["incr_merged"] = time.strftime("%Y-%m-%d %H:%M:%S")
    if dry_run:
        log(f"  [DRY] merge {route}: r={len(rs)} f={len(fs)} i={len(is_)}")
    else:
        eval_file.write_text(json.dumps(ev, indent=2, ensure_ascii=False))
        log(f"  MERGED {route}: r={len(rs)} f={len(fs)} i={len(is_)}")


def regen_report():
    gen = HARNESS_DIR / "gen_report_glm53_7way.py"
    if not gen.exists():
        log("  gen_report_glm53_7way.py not found"); return
    log("REGEN 7way report...")
    proc = subprocess.run(["python3", str(gen)], cwd=str(HARNESS_DIR),
                          capture_output=True, text=True, timeout=120)
    log("  REGEN OK" if proc.returncode == 0
        else f"  REGEN FAILED: {proc.stderr[:200]}")


def process_route(route: str, dry_run: bool = False):
    log(f"=== Incremental eval+merge: {route} ===")
    rerun_ids = get_rerun_ids(route)
    if not rerun_ids:
        log(f"  {route}: no rerun ids; skip"); return
    merged_path = rebuild_merged(route)
    targets = find_reeval_targets(route, rerun_ids)
    log(f"  {route}: {len(rerun_ids)} rerun ids, {len(targets)} need re-eval")
    if not targets:
        log(f"  {route}: nothing to re-eval; skip"); return
    result = run_eval(route, merged_path, targets, dry_run=dry_run)
    merge_eval(route, result, dry_run=dry_run)


def main():
    ap = argparse.ArgumentParser(description="Incremental eval+merge of recovered patches")
    ap.add_argument("--route", default=None, help="single route")
    ap.add_argument("--all", action="store_true", help="process all routes in ORDER")
    ap.add_argument("--regen", action="store_true", help="REGEN 7way report after")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    routes = ORDER if args.all else ([args.route] if args.route else ORDER)
    for route in routes:
        process_route(route, dry_run=args.dry_run)
    if args.regen and not args.dry_run:
        regen_report()
    log("=== Done ===")


if __name__ == "__main__":
    main()
