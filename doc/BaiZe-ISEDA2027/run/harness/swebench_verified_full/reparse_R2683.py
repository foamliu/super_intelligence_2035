#!/usr/bin/env python3
"""Re-parse R2683 incr_eval results from correct path (logs/evaluation/)."""
import json
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
EVAL_LOG_ROOT = HERE / "logs" / "evaluation"
REPORT_DIR = HERE / "reports"
DISPLAY = {"cline-patched": "cline", "deepseek-harness": "deepseek"}
MODEL_SUFFIX = "glm-5.3-flash"
ROUND = "R2683"

def disp(h): return DISPLAY.get(h, h)

all_instances = {
    "cline-patched": ["django__django-13658", "django__django-14376"],
    "codex": ["django__django-11163", "django__django-11179", "django__django-11206"],
    "claude-code": ["django__django-12276", "django__django-13837", "django__django-15252", "scikit-learn__scikit-learn-15100"],
    "pi": ["django__django-11211", "django__django-11239", "django__django-11276", "scikit-learn__scikit-learn-14087", "scikit-learn__scikit-learn-14710", "sympy__sympy-13852"],
    "hermes": ["django__django-14631", "django__django-14725", "sympy__sympy-22714", "sympy__sympy-22914"],
    "deepseek-harness": ["django__django-11603"],
}

for h, iids in all_instances.items():
    run_id = f"verified_full_glm53_{h}_incr_{ROUND}"
    model = f"{disp(h)}-{MODEL_SUFFIX}"
    ef = REPORT_DIR / f"eval_glm53_{h}.json"
    cum = json.loads(ef.read_text())
    for iid in iids:
        rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
        for k in ("resolved", "failed", "infra_or_quota"):
            cum[k] = [x for x in cum[k] if x != iid and not x.startswith(f"{iid}(")]
        if rj.exists():
            rep = json.loads(rj.read_text())
            inst = rep.get(iid, rep) if isinstance(rep, dict) else {}
            resolved = inst.get("resolved", False)
            b = "resolved" if resolved else "failed"
            cum[b].append(iid)
            status = "RESOLVED" if resolved else "FAILED"
            print(f"{disp(h)} {iid}: {status}")
        else:
            cum["infra_or_quota"].append(iid)
            print(f"{disp(h)} {iid}: NO report.json -> infra")
    cum["n"] = len(cum["resolved"]) + len(cum["failed"]) + len(cum["infra_or_quota"])
    ef.write_text(json.dumps(cum, indent=2))
    r, f, i = len(cum["resolved"]), len(cum["failed"]), len(cum["infra_or_quota"])
    print(f"{disp(h)}: cumulative n={cum['n']} resolved={r} failed={f} infra={i}")
    print()
