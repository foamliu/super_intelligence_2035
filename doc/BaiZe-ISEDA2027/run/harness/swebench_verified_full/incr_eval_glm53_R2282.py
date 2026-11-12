#!/usr/bin/env python3
"""incr_eval_glm53_R2282 — incremental eval for new real patches (R2282).

Auto-detects real (non-empty model_patch) predictions not yet in eval_glm53_<h>.json,
runs swebench eval (workers=1, timeout=1800) on just those, merges results back.

R2282 backlog (detected by detect_backlog_R2202.py):
  opencode: django__django-12039  (patchlen=3578, real patch just predicted)

pi matplotlib-21568 was empty (ability) — no eval needed.
All other harnesses backlog=0.

Hard constraint: NEVER commit result JSON. Guardrails: OMP=8, max_workers=1.
"""
import json, os, subprocess, sys, time, glob
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
ENRICHED = HERE / "enriched_500.json"
MODEL_SUFFIX = "glm-5.3-flash"
TIMEOUT_EVAL = 1800
ROUND = "R2282"

os.environ['OMP_NUM_THREADS'] = '8'
os.environ['OPENBLAS_NUM_THREADS'] = '8'
os.environ['MKL_NUM_THREADS'] = '8'
os.environ['EVAL_MAX_WORKERS'] = '1'

DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek"}
def disp(h): return DISPLAY.get(h, h)
HARNESSES = ["cline-patched","codex","opencode","claude-code","pi","hermes","deepseek-harness"]
EXCLUDE = {}  # R2282: no in-flight exclusions

def log(msg): print(f"[{ROUND}-eval {time.strftime('%H:%M:%S')}] {msg}", flush=True)

def real_preds(harness):
    out = []
    excl = EXCLUDE.get(harness, set())
    for f in sorted(glob.glob(str(PRED_DIR / f"{harness}__*.json"))):
        try:
            preds = json.loads(Path(f).read_text())
            if isinstance(preds, list) and preds:
                p = preds[0]
            elif isinstance(preds, dict):
                p = preds
            else:
                continue
            iid = p.get("instance_id", "")
            if iid in excl: continue
            if p.get("model_patch", "").strip():
                out.append((iid, p))
        except Exception: pass
    return out

def merge_for(harness, preds):
    merged = PRED_DIR / f"predictions_{harness}.json"
    merged.write_text(json.dumps([p for _, p in preds], indent=2))
    return merged

def run_eval(harness, merged, new_ids, run_id):
    cmd = (f"python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(new_ids)} --max_workers 1 "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"{disp(harness)}: launching eval on {len(new_ids)} NEW instances (workers=1, timeout={TIMEOUT_EVAL})...")
    EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True,
                          timeout=TIMEOUT_EVAL * len(new_ids) + 600)
    logf = REPORT_DIR / f"incr_eval_{ROUND}.log"
    with open(logf, "a") as lf:
        lf.write(f"\n=== {harness} {ROUND} ===\n{proc.stdout}\n[stderr]\n{proc.stderr}\n")
    log(f"  eval finished rc={proc.returncode}")
    return proc.returncode

def parse_and_merge(harness, new_ids, run_id):
    model = f"{disp(harness)}-{MODEL_SUFFIX}"
    ef = REPORT_DIR / f"eval_glm53_{harness}.json"
    summary = json.loads(ef.read_text()) if ef.exists() else {
        "harness": disp(harness), "harness_code": harness, "run_id": run_id,
        "n": 0, "resolved": [], "failed": [], "infra_or_quota": [], "no_patch": 0}
    new_res, new_fail, new_infra = [], [], []
    for iid in new_ids:
        rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
        if not rj.exists():
            cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
            rj = cands[0] if cands else None
        if rj is None or not rj.exists():
            new_infra.append(iid); continue
        try:
            rep = json.loads(rj.read_text())
            inst_rep = rep.get(iid, rep) if isinstance(rep, dict) else {}
            resolved = inst_rep.get("resolved", False)
            (new_res if resolved else new_fail).append(iid)
        except Exception as e:
            new_infra.append(f"{iid}({e})")
    existing = set(summary.get("resolved", []) + summary.get("failed", []) + summary.get("infra_or_quota", []))
    for iid in new_res:
        if iid not in existing: summary.setdefault("resolved", []).append(iid)
    for iid in new_fail:
        if iid not in existing: summary.setdefault("failed", []).append(iid)
    for iid in new_infra:
        if iid not in existing: summary.setdefault("infra_or_quota", []).append(iid)
    summary["n"] = len(summary.get("resolved", [])) + len(summary.get("failed", []))
    summary["evaluated"] = summary["n"]
    summary["resolved_count"] = len(summary.get("resolved", []))
    summary["total_predictions"] = summary["n"] + len(summary.get("infra_or_quota", []))
    summary["run_id"] = run_id
    ef.write_text(json.dumps(summary, indent=2))
    log(f"  {disp(harness)}: +{len(new_res)} resolved +{len(new_fail)} failed +{len(new_infra)} infra => total resolved={len(summary['resolved'])}")
    return len(new_res), len(new_fail), len(new_infra)

def main():
    total_new_res = 0; grand_new = 0
    for harness in HARNESSES:
        preds = real_preds(harness)
        ef = REPORT_DIR / f"eval_glm53_{harness}.json"
        evaluated = set()
        if ef.exists():
            ev = json.loads(ef.read_text())
            evaluated = set(ev.get("resolved", []) + ev.get("failed", []) + ev.get("infra_or_quota", []))
        real_ids = [iid for iid, _ in preds]
        new_ids = [iid for iid in real_ids if iid not in evaluated]
        if EXCLUDE.get(harness):
            log(f"{disp(harness)}: EXCLUDING in-flight {EXCLUDE[harness]}")
        log(f"{disp(harness)}: {len(evaluated)} evald, {len(real_ids)} real, {len(new_ids)} new")
        if not new_ids: continue
        grand_new += len(new_ids)
        merged = merge_for(harness, preds)
        run_id = f"verified_full_glm53_{harness}_incr_{ROUND}"
        run_eval(harness, merged, new_ids, run_id)
        nr, nf, ni = parse_and_merge(harness, new_ids, run_id)
        total_new_res += nr
    log(f"DONE {ROUND}: {grand_new} instances eval'd, total new resolved = {total_new_res}")

if __name__ == "__main__":
    main()
