#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""incr_eval_guarded_R2806.py — deepseek matplotlib backlog incr_eval（2026-11-20 16:3x 解冻令·Step 2.2）

走受限容器（swebench_guarded_eval.py 注入 --memory 128g --memory-swap 128g --cpus 16），串行。
backlog = deepseek R2800 暂停的 matplotlib 评测（self-test 查得 2 个 real-patch 未评测）。

用法:
  python3 incr_eval_guarded_R2806.py            # 实跑
  python3 incr_eval_guarded_R2806.py --dry-run  # 只列待评测，不跑
"""
from __future__ import annotations
import json, subprocess, time, glob, os, sys
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
PRED_DIR = HERE / "predictions_glm53"
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "evaluation"
ENRICHED = HERE / "enriched_500.json"
ROUND = "R2806"
HARNESS = "deepseek-harness"
TIMEOUT_EVAL = 1800
PY310 = "/nas_train/app.e0031982/miniforge3/envs/py310/bin/python3"
GUARDED_EVAL = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_guarded_eval.py")
DRY = "--dry-run" in sys.argv


def log(m):
    print(f"[incr-eval-guarded {time.strftime('%H:%M:%S')}] {m}", flush=True)


def load_pred(iid_file):
    try:
        d = json.loads(iid_file.read_text())
    except Exception:
        return []
    if isinstance(d, dict):
        d = [d]
    return [p for p in d if (p.get("model_patch") or "").strip()]


def get_unevaluated():
    cum_file = REPORT_DIR / f"eval_glm53_{HARNESS}.json"
    done = set()
    if cum_file.is_file():
        d = json.loads(cum_file.read_text())
        for field in ["resolved", "failed", "infra_or_quota", "no_patch", "empty_patch"]:
            val = d.get(field, [])
            if isinstance(val, list):
                done.update(val)
    preds = sorted(glob.glob(str(PRED_DIR / f"{HARNESS}__*.json")))
    real_new, empty_new = [], []
    for p in preds:
        iid = os.path.basename(p).replace(f"{HARNESS}__", "").replace(".json", "")
        if iid in done:
            continue
        if load_pred(Path(p)):
            real_new.append(iid)
        else:
            empty_new.append(iid)
    return real_new, empty_new, done


def run_guarded_eval(new_ids):
    merged_new = PRED_DIR / f"predictions_{HARNESS}_new_{ROUND}.json"
    all_preds = []
    for iid in new_ids:
        all_preds.extend(load_pred(PRED_DIR / f"{HARNESS}__{iid}.json"))
    merged_new.write_text(json.dumps(all_preds, indent=2))
    log(f"merged {len(all_preds)} new patches -> {merged_new.name}")
    run_id = f"verified_full_glm53_{HARNESS}_incr_{ROUND}"
    # ⚠️ 走 swebench_guarded_eval.py（注入 --memory 128g --memory-swap 128g --cpus 16）
    cmd = (f"nice -n 19 ionice -c 3 {PY310} {GUARDED_EVAL} "
           f"--predictions_path {merged_new} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(new_ids)} --max_workers 1 "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"EVAL {len(new_ids)} instances (GUARDED container) -> run_id={run_id}")
    EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True,
                          timeout=TIMEOUT_EVAL * len(new_ids) + 600)
    (HERE / "logs" / f"eval_{run_id}.log").write_text(
        proc.stdout + "\n[stderr]\n" + proc.stderr)
    log(f"eval rc={proc.returncode}")
    return run_id


def find_report(run_id, iid):
    cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
    return cands[0] if cands else None


def parse_and_merge(real_ids, run_id):
    ef = REPORT_DIR / f"eval_glm53_{HARNESS}.json"
    cum = json.loads(ef.read_text()) if ef.is_file() else {
        "harness": HARNESS, "harness_code": HARNESS, "run_id": run_id,
        "n": 0, "resolved": [], "failed": [], "infra_or_quota": []}
    for k in ("resolved", "failed", "infra_or_quota", "empty_patch", "no_patch"):
        cum.setdefault(k, [])
    for iid in real_ids:
        rj = find_report(run_id, iid)
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
            cum["infra_or_quota"].append(iid)
            log(f"  {iid}: parse error -> infra: {e}")
    cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
    ef.write_text(json.dumps(cum, indent=2))
    log(f"merged -> resolved={len(cum['resolved'])} failed={len(cum['failed'])} infra={len(cum['infra_or_quota'])}")
    return cum


def main():
    real_new, empty_new, done = get_unevaluated()
    log(f"survey: real_new={len(real_new)} empty_new={len(empty_new)} already_done={len(done)}")
    if empty_new:
        ef = REPORT_DIR / f"eval_glm53_{HARNESS}.json"
        cum = json.loads(ef.read_text()) if ef.is_file() else {"resolved": [], "failed": [], "infra_or_quota": [], "empty_patch": [], "no_patch": []}
        cum.setdefault("empty_patch", [])
        for iid in empty_new:
            if iid not in cum["empty_patch"]:
                cum["empty_patch"].append(iid)
        ef.write_text(json.dumps(cum, indent=2))
        log(f"merged {len(empty_new)} empty patches")
    if not real_new:
        log("no real-patch unevaluated -> nothing to eval")
        return 0
    log(f"real-patch backlog: {real_new}")
    if DRY:
        log("DRY-RUN: would eval the above through GUARDED container (serial)")
        return 0
    run_id = run_guarded_eval(real_new)
    cum = parse_and_merge(real_new, run_id)
    log(f"DONE. deepseek resolved={len(cum['resolved'])}/500")
    return 0


if __name__ == "__main__":
    sys.exit(main())

