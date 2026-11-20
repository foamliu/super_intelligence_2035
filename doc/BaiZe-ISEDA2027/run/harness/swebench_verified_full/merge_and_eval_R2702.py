#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge pi django-12741 (already eval'd) + run dsh eval for R2702."""
from __future__ import annotations
import json, subprocess, time, os
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "8"
os.environ["OPENBLAS_NUM_THREADS"] = "8"
os.environ["MKL_NUM_THREADS"] = "8"
os.environ["EVAL_MAX_WORKERS"] = "1"

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "evaluation"
ENRICHED = HERE / "enriched_500.json"
ROUND = "R2702"
MODEL_SUFFIX = "glm-5.3-flash"
TIMEOUT_EVAL = 1800
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek"}
CPU_SPIRAL_SKIP = {"scikit-learn__scikit-learn-14710"}

def disp(h): return DISPLAY.get(h, h)
def log(m): print(f"[R2702 {time.strftime('%H:%M:%S')}] {m}", flush=True)

def load_pred(iid_file):
    try:
        d = json.loads(iid_file.read_text())
    except Exception:
        return []
    if isinstance(d, dict):
        d = [d]
    return [p for p in d if (p.get("model_patch") or "").strip()]

def strip_iid(infra, iid):
    return [x for x in infra if x != iid and not x.startswith(f"{iid}(")]

def merge_result(harness, iid, run_id):
    ef = REPORT_DIR / f"eval_glm53_{harness}.json"
    cum = json.loads(ef.read_text())
    for k in ("resolved", "failed", "infra_or_quota"):
        cum.setdefault(k, [])
        seen = set(); out = []
        for x in cum[k]:
            if x not in seen: seen.add(x); out.append(x)
        cum[k] = out
    model = f"{disp(harness)}-{MODEL_SUFFIX}"
    rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
    if not rj.exists():
        cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
        rj = cands[0] if cands else None
    if rj is None or not rj.exists():
        cum["infra_or_quota"] = strip_iid(cum["infra_or_quota"], iid)
        cum["infra_or_quota"].append(iid)
        log(f"  {iid}: NO report.json -> infra")
    else:
        rep = json.loads(rj.read_text())
        inst = rep.get(iid, rep) if isinstance(rep, dict) else {}
        resolved = inst.get("resolved", False)
        cum["infra_or_quota"] = strip_iid(cum["infra_or_quota"], iid)
        bucket = "resolved" if resolved else "failed"
        if iid not in cum[bucket]: cum[bucket].append(iid)
        log(f"  {iid}: {'RESOLVED' if resolved else 'FAILED'}")
    cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
    ef.write_text(json.dumps(cum, indent=2))
    log(f"  {disp(harness)}: resolved={len(cum['resolved'])} failed={len(cum['failed'])} infra={len(cum['infra_or_quota'])}")

def run_eval(harness, new_ids):
    merged_new = PRED_DIR / f"predictions_{harness}_new_{ROUND}.json"
    all_preds = []
    for iid in new_ids:
        all_preds.extend(load_pred(PRED_DIR / f"{harness}__{iid}.json"))
    merged_new.write_text(json.dumps(all_preds, indent=2))
    log(f"{disp(harness)}: merged {len(all_preds)} patches -> {merged_new.name}")
    run_id = f"verified_full_glm53_{harness}_incr_{ROUND}"
    cmd = (f"python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {merged_new} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(new_ids)} --max_workers 1 "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"{disp(harness)}: EVAL {len(new_ids)} instances -> {run_id}")
    EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True,
                          timeout=TIMEOUT_EVAL * len(new_ids) + 600)
    (HERE / "logs" / f"eval_{run_id}.log").write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)
    log(f"{disp(harness)}: eval rc={proc.returncode}")
    return run_id

def main():
    log("=== R2702 merge + eval start ===")
    # Step 1: Merge pi django-12741 (already eval'd)
    pi_run_id = "verified_full_glm53_pi_incr_R2702"
    pi_rj = EVAL_LOG_ROOT / pi_run_id / "pi-glm-5.3-flash" / "django__django-12741" / "report.json"
    if pi_rj.exists():
        log("Step 1: Merge pi django-12741 (already eval'd)")
        merge_result("pi", "django__django-12741", pi_run_id)
    else:
        log("Step 1: pi report.json not found, will eval")
        rid = run_eval("pi", ["django__django-12741"])
        merge_result("pi", "django__django-12741", rid)
    # Step 2: Eval dsh django-12713 + django-12741
    dsh_new = ["django__django-12713", "django__django-12741"]
    dsh_ef = REPORT_DIR / "eval_glm53_deepseek-harness.json"
    dsh_done = set()
    if dsh_ef.is_file():
        d = json.loads(dsh_ef.read_text())
        dsh_done = set(d.get("resolved", []) + d.get("failed", []) + d.get("infra_or_quota", []))
    dsh_to_eval = [iid for iid in dsh_new if iid not in dsh_done]
    if dsh_to_eval:
        log(f"Step 2: Eval dsh {dsh_to_eval}")
        dsh_rid = run_eval("deepseek-harness", dsh_to_eval)
        for iid in dsh_to_eval:
            merge_result("deepseek-harness", iid, dsh_rid)
    else:
        log("Step 2: dsh already eval'd, skip")
    log("=== Final cumulative counts ===")
    for h in ["cline-patched","codex","claude-code","pi","deepseek-harness","opencode","hermes"]:
        ef = REPORT_DIR / f"eval_glm53_{h}.json"
        if ef.is_file():
            d = json.loads(ef.read_text())
            log(f"  {disp(h)}: resolved={len(d.get('resolved',[]))} failed={len(d.get('failed',[]))} infra={len(d.get('infra_or_quota',[]))}")
    log("=== R2702 done ===")

if __name__ == "__main__":
    main()
