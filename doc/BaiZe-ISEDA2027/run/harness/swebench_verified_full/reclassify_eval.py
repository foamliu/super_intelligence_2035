#!/usr/bin/env python3
"""Reclassify eval results from existing report.json files (no Docker re-run)."""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRED_DIR = HERE / "predictions_doubao_pro"
REPORT_DIR = HERE / "reports"
EVAL_LOG_ROOT = HERE / "logs" / "evaluation"
MODEL_SUFFIX = "doubao-seed-2.0-pro-cloud"

def reclassify(route: str):
    run_id = f"doubao_pro_full_{route}"
    model = f"{route}-{MODEL_SUFFIX}"
    disp = {"cline-patched": "cline", "deepseek-harness": "deepseek"}.get(route, route)

    merged_path = PRED_DIR / f"predictions_{route}.json"
    if not merged_path.exists():
        print(f"  {route}: merged predictions not found, skip")
        return
    preds = json.loads(merged_path.read_text())
    eval_ids = [p["instance_id"] for p in preds if p.get("model_patch", "").strip()]
    print(f"  {route}: {len(preds)} total, {len(eval_ids)} non-empty patches to classify")

    summary = {"harness": disp, "harness_code": route, "run_id": run_id,
               "n": len(eval_ids), "resolved": [], "failed": [], "infra_or_quota": []}

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
            # report.json format: {"<iid>": {"resolved": true/false, ...}}
            if isinstance(rep, dict) and iid in rep and isinstance(rep[iid], dict):
                resolved = bool(rep[iid].get("resolved", False))
            elif isinstance(rep, dict) and "resolved" in rep:
                resolved = bool(rep.get("resolved", False))
            else:
                resolved = False
            if resolved:
                summary["resolved"].append(iid)
            else:
                summary["failed"].append(iid)
        except Exception as e:
            summary["infra_or_quota"].append(f"{iid}({e})")

    n = len(eval_ids) if eval_ids else 1
    print(f"  {route}: resolved={len(summary['resolved'])} "
          f"failed={len(summary['failed'])} infra={len(summary['infra_or_quota'])}")
    print(f"  Pass% (of {len(eval_ids)} non-empty): {len(summary['resolved'])/n*100:.1f}%")
    print(f"  Pass% (of 500 total): {len(summary['resolved'])/500*100:.1f}%")

    eval_file = REPORT_DIR / f"eval_doubao_pro_{route}.json"
    eval_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"  WROTE {eval_file.name}")

if __name__ == "__main__":
    routes = sys.argv[1:] if len(sys.argv) > 1 else ["deepseek-harness"]
    for r in routes:
        print(f"=== Reclassify: {r} ===")
        reclassify(r)
