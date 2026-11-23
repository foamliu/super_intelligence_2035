#!/usr/bin/env python3
"""rerun_infra_verified.py — Infra rerun orchestrator for SWE-bench Verified 7-way.

2026-11-23 用户令·第二步: 夜间重跑 infra failed (21:00–09:00 窗口).

For each route (cline first, rest by infra_failed count desc):
  1. predict  — re-predict empty-patch instances (is_predicted() skip logic).
  2. eval     — guarded docker eval (swebench_guarded_eval.py: mem128g/cpu16).
  3. merge    — update eval_glm53_<route>.json with new resolved/failed/infra.
After all routes (or window end): REGEN 7way report.

Concurrency: ≤2 routes (env RERUN_MAX_CONCURRENT, default 1 for first night).
Resume: is_predicted() skips already-predicted; state file tracks completion.

USAGE (inside 21:00–09:00 window):
  bash ../predict_guarded.sh python3 rerun_infra_verified.py [--dry-run] [--route X]
"""
from __future__ import annotations
import json, os, subprocess, sys, time, argparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS_DIR = HERE.parent
GUARDED_EVAL = HARNESS_DIR / "swebench_guarded_eval.py"
RUN_VERIFIED = HERE / "run_verified_full.py"
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "evaluation"
IDS_DIR = HERE / "rerun_ids"
STATE_FILE = HERE / "rerun_infra_state.json"
ENRICHED = HERE / "enriched_500.json"

MODEL_SUFFIX = os.environ.get("MODEL_SUFFIX", "glm-5.3-flash")
EVAL_TAG = os.environ.get("EVAL_TAG", "glm53_")
TIMEOUT_EVAL = 1800

ORDER = ["cline-patched", "codex", "deepseek-harness", "claude-code",
         "pi", "hermes", "opencode"]
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek"}


def log(msg: str):
    print(f"[rerun {time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def in_window() -> bool:
    h = int(time.strftime("%H"))
    return h >= 21 or h < 9


def disp(h: str) -> str:
    return DISPLAY.get(h, h)


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"completed_routes": [], "per_route": {}, "nights": 0}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


def get_rerun_ids(route: str) -> list[str]:
    fn = IDS_DIR / f"{route}_rerun_ids.txt"
    if not fn.exists():
        return []
    return [l.strip() for l in fn.read_text().splitlines() if l.strip()]


def run_predict(route: str, ids: list[str], dry_run: bool = False) -> bool:
    ids_file = IDS_DIR / f"{route}_rerun_ids.txt"
    env = os.environ.copy()
    cmd = ["python3", str(RUN_VERIFIED), "predict",
           "--harness", route, "--ids-file", str(ids_file)]
    if dry_run:
        log(f"  [DRY] predict {route}: {len(ids)} ids")
        return True
    log(f"  PREDICT {route}: {len(ids)} rerun ids")
    try:
        proc = subprocess.run(cmd, cwd=str(HERE), env=env,
                              capture_output=True, text=True,
                              timeout=TIMEOUT_EVAL * len(ids) + 3600)
    except subprocess.TimeoutExpired:
        log(f"  predict {route} TIMEOUT (continuing to eval)")
        return False
    logf = HERE / "logs" / f"rerun_predict_{route}.log"
    logf.parent.mkdir(parents=True, exist_ok=True)
    logf.write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)
    log(f"  predict {route} rc={proc.returncode}")
    return proc.returncode == 0


def run_eval(route: str, ids: list[str], dry_run: bool = False) -> dict:
    """Run guarded docker eval on rerun instances that have patches."""
    merged = PRED_DIR / f"predictions_{route}.json"
    if not merged.exists():
        log(f"  no merged predictions for {route}; skip eval")
        return {"resolved": [], "failed": [], "infra_or_quota": []}
    preds = json.loads(merged.read_text())
    pred_ids = {p["instance_id"] for p in preds if p.get("model_patch", "").strip()}
    eval_ids = [i for i in ids if i in pred_ids]
    if not eval_ids:
        log(f"  no patches to eval for {route}")
        return {"resolved": [], "failed": [], "infra_or_quota": []}
    run_id = f"rerun_infra_{route}"
    max_workers = int(os.environ.get("EVAL_MAX_WORKERS", "4"))
    model = f"{disp(route)}-{MODEL_SUFFIX}"
    if dry_run:
        log(f"  [DRY] eval {route}: {len(eval_ids)} ids (run_id={run_id})")
        return {"resolved": [], "failed": [], "infra_or_quota": []}
    cmd = (f"python3 {GUARDED_EVAL} "
           f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(eval_ids)} --max_workers {max_workers} "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"  EVAL {route}: {len(eval_ids)} instances (guarded mem128g/cpu16)")
    try:
        proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                              capture_output=True, text=True,
                              timeout=TIMEOUT_EVAL * len(eval_ids) + 600)
        logf = HERE / "logs" / f"rerun_eval_{route}.log"
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
    """Merge rerun eval results back into eval_glm53_<route>.json."""
    eval_file = REPORT_DIR / f"eval_{EVAL_TAG}{route}.json"
    if not eval_file.exists():
        ev = {"harness": disp(route), "harness_code": route, "run_id": "rerun",
              "n": 0, "resolved": [], "failed": [], "infra_or_quota": []}
    else:
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
    ev["resolved"] = sorted(rs); ev["failed"] = sorted(fs); ev["infra_or_quota"] = sorted(is_)
    ev["n"] = len(rs) + len(fs) + len(is_)
    ev["rerun_merged"] = time.strftime("%Y-%m-%d %H:%M:%S")
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


def main():
    ap = argparse.ArgumentParser(description="Infra rerun orchestrator (21:00-09:00)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--route", default=None, help="single route only")
    ap.add_argument("--skip-window-check", action="store_true")
    args = ap.parse_args()
    if not args.dry_run and not args.skip_window_check and not args.route:
        if not in_window():
            log(f"窗口外 (hour={time.strftime('%H')}); park.")
            return
    state = load_state()
    routes = [args.route] if args.route else ORDER
    log(f"=== Infra rerun ({'DRY' if args.dry_run else 'LIVE'}) routes={routes} ===")
    for route in routes:
        if not args.skip_window_check and not args.route and not in_window():
            log(f"窗口结束 (hour={time.strftime('%H')}); REGEN+stop."); break
        ids = get_rerun_ids(route)
        if not ids:
            log(f"{route}: no rerun ids; skip"); continue
        if route in state.get("completed_routes", []):
            log(f"{route}: already done; skip"); continue
        log(f"--- {route}: {len(ids)} rerun instances ---")
        run_predict(route, ids, dry_run=args.dry_run)
        rerun_result = run_eval(route, ids, dry_run=args.dry_run)
        merge_eval(route, rerun_result, dry_run=args.dry_run)
        if not args.dry_run:
            state.setdefault("completed_routes", []).append(route)
            state["per_route"][route] = {
                "n_rerun": len(ids),
                "resolved": len(rerun_result["resolved"]),
                "failed": len(rerun_result["failed"]),
                "infra": len(rerun_result["infra_or_quota"]),
                "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
            save_state(state)
        if not args.skip_window_check and not args.route and not in_window():
            log(f"窗口结束 after {route}; REGEN+stop."); break
    if not args.dry_run:
        regen_report()
    log("=== Summary ===")
    for route in routes:
        pr = state.get("per_route", {}).get(route, {})
        if pr:
            log(f"  {route}: rerun={pr['n_rerun']} r={pr['resolved']} "
                f"f={pr['failed']} i={pr['infra']}")
    log("=== Done ===")


if __name__ == "__main__":
    main()

