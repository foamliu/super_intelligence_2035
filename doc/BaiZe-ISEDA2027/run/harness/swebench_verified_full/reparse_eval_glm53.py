#!/usr/bin/env python3
"""Re-parse ALL existing report.json files for glm53 eval and fix eval_glm53_*.json summaries.

BUG FIX (R2056, 2026-11-10): incr_eval_R2026.py line 89 used glob(f'{results_dir}/*.json')
which only matched run.json at the top level, NOT the actual report.json files at
{results_dir}/{model}/{instance_id}/report.json.  Also, report.json format is
{instance_id: {resolved: bool, ...}} (nested dict), but the script read
rd.get('resolved', False) on the top-level dict → always False → everything went
to unresolved, and the 'resolved' list was just stale data from previous runs.

This script correctly scans ALL eval run directories, parses report.json with the
proper nested format, and regenerates eval_glm53_*.json from scratch.

Usage: python3 reparse_eval_glm53.py
"""
import json, glob, os, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"
REPORT_DIR = HERE / "reports"

DISPLAY = {"cline-patched": "cline"}
def disp(h): return DISPLAY.get(h, h)

HARNESSES = ['cline-patched', 'codex', 'opencode', 'claude-code',
             'pi', 'hermes', 'deepseek-harness']

def log(m): print(f"[reparse {time.strftime('%H:%M:%S')}] {m}", flush=True)

for h in HARNESSES:
    # Find ALL glm53 eval run directories for this harness
    # ONLY scan dirs with "glm53" in the name — non-glm53 dirs are kimi results
    patterns = [
        f'verified_full_glm53_{h}_incr_*',
        f'verified_full_glm53_{h}',
    ]
    all_dirs = set()
    for pat in patterns:
        for d in glob.glob(str(EVAL_LOG_ROOT / pat)):
            if os.path.isdir(d):
                all_dirs.add(d)

    # Parse ALL report.json files from all eval run dirs
    total_resolved = set()
    total_unresolved = set()
    total_errored = set()
    n_files = 0
    for d in sorted(all_dirs):
        # report.json is at {d}/{model}/{instance_id}/report.json
        rj_files = glob.glob(f'{d}/*/*/report.json')
        for rf in rj_files:
            n_files += 1
            try:
                rd = json.load(open(rf))
                # Format: {instance_id: {resolved: bool, errored: bool, ...}}
                if isinstance(rd, dict):
                    for iid, info in rd.items():
                        if not isinstance(info, dict):
                            continue
                        if info.get('resolved', False):
                            total_resolved.add(iid)
                        elif info.get('errored', False):
                            total_errored.add(iid)
                        elif info.get('patch_successfully_applied', False) or 'tests_status' in info:
                            # Has eval result but not resolved
                            total_unresolved.add(iid)
                        else:
                            total_errored.add(iid)
            except Exception as e:
                pass

    # Remove overlaps: resolved takes priority
    total_unresolved -= total_resolved
    total_errored -= total_resolved
    total_errored -= total_unresolved

    n = len(total_resolved) + len(total_unresolved) + len(total_errored)
    pct = 100 * len(total_resolved) / max(n, 1)

    # Write corrected summary
    eval_file = REPORT_DIR / f'eval_glm53_{h}.json'
    summary = {
        'harness': disp(h),
        'harness_code': h,
        'run_id': 'reparse_R2056',
        'n': n,
        'resolved': sorted(total_resolved),
        'unresolved': sorted(total_unresolved),
        'errored': sorted(total_errored),
        'note': f'Re-parsed from {n_files} report.json files across {len(all_dirs)} eval dirs (R2056 bug fix)',
    }
    eval_file.write_text(json.dumps(summary, indent=2))
    log(f"{h}: CORRECTED eval: {len(total_resolved)} resolved / {len(total_unresolved)} unresolved / {len(total_errored)} errored / {n} total ({pct:.1f}%) [from {n_files} report.json in {len(all_dirs)} dirs]")

log("Done. eval_glm53_*.json files have been corrected.")
