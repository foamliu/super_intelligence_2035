#!/usr/bin/env python3
"""Update cline eval summary: django-15375 RESOLVED (R2696 incr_eval)."""
import json
from pathlib import Path
REP = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports")
f = REP / "eval_glm53_cline-patched.json"
d = json.loads(f.read_text())
iid = "django__django-15375"
for k in ("resolved", "failed", "infra_or_quota"):
    d[k] = [x for x in d.get(k, []) if x != iid and not x.startswith(iid + "(")]
d.setdefault("resolved", []).append(iid)
d["resolved"] = list(dict.fromkeys(d["resolved"]))
d["n"] = len(d["resolved"]) + len(d["failed"]) + len(d["infra_or_quota"])
f.write_text(json.dumps(d, indent=2))
r = len(d["resolved"]); fa = len(d["failed"]); inf = len(d["infra_or_quota"])
print("cline: +%s RESOLVED | resolved=%d failed=%d infra=%d n=%d" % (iid, r, fa, inf, d["n"]))
