#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix false 'infra' classifications caused by path mismatch (R2698).

The incr_eval script's parse_and_merge looks for per-instance report.json in
logs/run_evaluation/<run_id>/<model>/<iid>/report.json (old swebench format,
used by the initial full eval R1789).  But incremental evals (R2683+) use the
new swebench format that writes a single results.json to
logs/evaluation/<run_id>/results.json with resolved_ids / unresolved_ids lists.

Result: real-patch instances eval'd in incremental rounds were falsely marked
'infra_or_quota' because report.json was never found in the old path.

This script cross-references ALL results.json in logs/evaluation/ and moves
falsely-classified 'infra' entries to their correct 'resolved' or 'failed' bucket.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full")
EVAL_DIR = HERE / "logs" / "evaluation"
REPORT_DIR = HERE / "reports"
ROUTES = ["cline-patched", "hermes", "claude-code", "codex", "pi", "opencode", "deepseek-harness"]

def build_verdict(harness: str) -> dict:
    """Scan all results.json for a route; latest round wins."""
    verdict = {}
    for f in sorted(EVAL_DIR.glob(f"verified_full_glm53_{harness}_incr_*/results.json")):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        for iid in d.get("resolved_ids", []):
            verdict[iid] = "resolved"
        for iid in d.get("unresolved_ids", []):
            verdict[iid] = "failed"
        for iid in d.get("ambiguous_failure_ids", []):
            verdict[iid] = "failed"  # ambiguous = not resolved
        for iid in d.get("infra_failure_ids", []):
            verdict[iid] = "infra"
    return verdict

if __name__ == "__main__":
    total_fixed = 0
    for h in ROUTES:
        cum_file = REPORT_DIR / f"eval_glm53_{h}.json"
        if not cum_file.is_file():
            print(f"{h}: no cumulative file, skip")
            continue
        cum = json.loads(cum_file.read_text())
        verdict = build_verdict(h)

        infra = cum.get("infra_or_quota", [])
        resolved = cum.get("resolved", [])
        failed = cum.get("failed", [])

        new_infra = []
        fixed = []
        for entry in infra:
            clean = entry.split("(")[0].strip()
            if clean in verdict and verdict[clean] != "infra":
                target = resolved if verdict[clean] == "resolved" else failed
                target.append(clean)
                fixed.append((clean, verdict[clean]))
            else:
                new_infra.append(entry)

        if fixed:
            cum["infra_or_quota"] = new_infra
            cum["resolved"] = resolved
            cum["failed"] = failed
            cum["n"] = len(resolved) + len(failed) + len(new_infra)
            cum_file.write_text(json.dumps(cum, indent=2))
            total_fixed += len(fixed)
            for iid, v in fixed:
                print(f"  {h}: {iid} infra -> {v}")
            print(f"{h}: fixed {len(fixed)} false infra | "
                  f"resolved={len(resolved)} failed={len(failed)} infra={len(new_infra)} n={cum['n']}")
        else:
            print(f"{h}: no false infra | resolved={len(resolved)} failed={len(failed)} infra={len(infra)} n={cum['n']}")
    print(f"\nTOTAL fixed: {total_fixed}")
