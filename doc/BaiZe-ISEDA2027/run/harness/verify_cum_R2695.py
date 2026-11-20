#!/usr/bin/env python3
import json
from pathlib import Path
REP = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/reports")
for h in ["cline-patched", "hermes", "claude-code", "codex", "pi", "opencode", "deepseek-harness"]:
    d = json.loads((REP / f"eval_glm53_{h}.json").read_text())
    r = len(d["resolved"])
    print(f"{h}: resolved={r} failed={len(d['failed'])} infra={len(d.get('infra_or_quota', []))} n={d['n']} Pass%={r/500*100:.1f}%")
