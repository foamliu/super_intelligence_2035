#!/usr/bin/env python3
"""Quick eval of deepseek xarray-3305 (R1619b)."""
import json, subprocess, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
PRED = HERE / "predictions"
# re-merge deepseek predictions
allp = []
for f in sorted(PRED.glob("deepseek-harness__*.json")):
    if f.stat().st_size < 30: continue
    preds = json.loads(f.read_text())
    if isinstance(preds, dict): preds = [preds]
    for p in preds:
        if p.get("model_patch", "").strip(): allp.append(p)
(PRED / "predictions_deepseek-harness.json").write_text(json.dumps(allp, indent=2))
print(f"merged {len(allp)} deepseek predictions")
merged = PRED / "predictions_deepseek-harness.json"
run_id = "verified_full_deepseek-harness"
cmd = ("python3 -m swebench.harness.run_evaluation "
       "--predictions_path %s --dataset_name %s --split test "
       "--instance_ids pydata__xarray-3305 --max_workers 1 "
       "--run_id %s --timeout 1800" % (merged, HERE / "enriched_500.json", run_id))
print("running eval...")
proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                      capture_output=True, text=True, timeout=2700)
print("eval rc=", proc.returncode)
rj = HERE / "logs" / "run_evaluation" / run_id / "deepseek-harness-kimi-k2.6-cloud" / "pydata__xarray-3305" / "report.json"
if not rj.exists():
    cands = list((HERE / "logs" / "run_evaluation" / run_id).glob("*/pydata__xarray-3305/report.json"))
    rj = cands[0] if cands else None
if rj and rj.exists():
    rep = json.loads(rj.read_text())
    inst = rep.get("pydata__xarray-3305", rep) if isinstance(rep, dict) else {}
    res = "RESOLVED" if inst.get("resolved", False) else "FAILED"
    print("pydata__xarray-3305:", res)
    ef = HERE / "reports" / "eval_deepseek-harness.json"
    ev = json.loads(ef.read_text())
    iid = "pydata__xarray-3305"
    for k in ("no_patch", "failed", "infra_or_quota", "resolved"):
        if iid in ev.get(k, []): ev[k].remove(iid)
    if res == "RESOLVED": ev["resolved"].append(iid)
    else: ev["failed"].append(iid)
    ev["n"] = len(ev["resolved"]) + len(ev["failed"]) + len(ev["infra_or_quota"]) + len(ev.get("no_patch", []))
    ef.write_text(json.dumps(ev, indent=2))
    print("updated eval_deepseek: resolved=%d failed=%d infra=%d no_patch=%d n=%d" % (
        len(ev["resolved"]), len(ev["failed"]), len(ev["infra_or_quota"]), len(ev.get("no_patch", [])), ev["n"]))
else:
    print("xarray-3305: INFRA (no report.json)")
