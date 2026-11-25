#!/usr/bin/env python3
"""gen_rerun_summary_20261025.py -> summary_rerun_20261025.json.
Collects codex err classification + hermes/claude-code old & rerun rewards.
Re-running is idempotent (overwrites with current state)."""
from __future__ import annotations
import json, os, glob
from collections import Counter

REPO = "/nas_train/app.e0031982/code/super_intelligence_2035"
OUT = f"{REPO}/doc/BaiZe-ISEDA2027/run/harness/summary_rerun_20261025.json"
TB_ROOT = "/tmp/tb_7x89"

def _trial_dirs(jobs_dir):
    if not os.path.isdir(jobs_dir):
        return []
    subs = sorted(glob.glob(os.path.join(jobs_dir, "*/")))
    if not subs:
        return []
    ts = subs[-1]
    out = []
    for d in sorted(glob.glob(os.path.join(ts, "*__*"))):
        out.append((os.path.basename(d).split("__")[0], d))
    return out

def _reward(trial_dir):
    p = os.path.join(trial_dir, "verifier", "reward.txt")
    if os.path.exists(p):
        try:
            return int(open(p).read().strip())
        except Exception:
            return None
    return None

def _classify_codex_err(trial_dir):
    exc = os.path.join(trial_dir, "exception.txt")
    if not os.path.exists(exc):
        return ("no_exception", "", "")
    tail = open(exc).read().strip().splitlines()[-1] if os.path.getsize(exc) else ""
    if "AgentTimeoutError" in tail:
        return ("AgentTimeoutError", "timeout_900s", "")
    rj = os.path.join(trial_dir, "result.json")
    st = ""
    ec = None
    if os.path.exists(rj):
        try:
            j = json.load(open(rj))
            ar = j.get("agent_result")
            if ar is not None:
                md = ar.get("metadata") or {}
                st = md.get("stdout", "") or ""
                ec = md.get("exit_code")
        except Exception:
            pass
    if "429" in st:
        return ("RuntimeError_exit1", "429_rate_limit", st[-300:])
    if "unexpected argument" in st or "Usage: codex exec" in st:
        return ("RuntimeError_exit1", "cli_arg_parse", st[-300:])
    if ec in (137, 139):
        return ("RuntimeError_exit1", f"signal_exit_{ec}", st[-300:])
    if "turn.failed" in st:
        return ("RuntimeError_exit1", "turn_failed_other", st[-300:])
    if not st:
        return ("RuntimeError_exit1", "exit1_no_stdout", "")
    return ("RuntimeError_exit1", "exit1_other", st[-300:])

def collect_harness(jobs_dir, harness, classify_err=False):
    rows = []
    for task, d in _trial_dirs(jobs_dir):
        rw = _reward(d)
        err = None
        if classify_err and os.path.exists(os.path.join(d, "exception.txt")):
            err = _classify_codex_err(d)
        rows.append({"task": task, "harness": harness, "reward": rw,
                     "err_type": err[0] if err else None,
                     "err_subcause": err[1] if err else None})
    return rows

def main():
    summary = {
        "generated_at": os.popen("date -u '+%Y-%m-%dT%H:%M:%SZ'").read().strip(),
        "directive": "2026-10-25 17:5x: hermes/claude-code full rerun + codex err triage",
        "denominator_note": "89 task dirs; canonical 87 after __hash dedup",
    }
    codex_rows = collect_harness(f"{TB_ROOT}/jobs_codex", "codex", classify_err=True)
    err_counter = Counter(r["err_subcause"] for r in codex_rows if r["err_type"])
    summary["codex_old_7x89"] = {
        "pass": sum(1 for r in codex_rows if r["reward"] == 1),
        "rewarded": sum(1 for r in codex_rows if r["reward"] is not None),
        "exceptions": sum(1 for r in codex_rows if r["err_type"]),
        "err_by_subcause": dict(err_counter),
        "rows": codex_rows,
    }
    for h in ("hermes", "claude-code"):
        rows = collect_harness(f"{TB_ROOT}/jobs_{h}", h)
        summary[f"{h}_old_7x89"] = {
            "pass": sum(1 for r in rows if r["reward"] == 1),
            "rewarded": sum(1 for r in rows if r["reward"] is not None),
            "exceptions": sum(1 for r in rows if r["reward"] is None),
            "rows": rows,
        }
    for h in ("hermes", "claude-code"):
        rows = collect_harness(f"{TB_ROOT}/jobs_{h}_rerun_20261025", f"{h}_rerun")
        summary[f"{h}_rerun_20261025"] = {
            "pass": sum(1 for r in rows if r["reward"] == 1),
            "rewarded": sum(1 for r in rows if r["reward"] is not None),
            "exceptions": sum(1 for r in rows if r["reward"] is None),
            "completed": len(rows),
            "rows": rows,
        }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"== summary written to {OUT} ==")
    for k in ("codex_old_7x89", "hermes_old_7x89", "claude-code_old_7x89",
              "hermes_rerun_20261025", "claude-code_rerun_20261025"):
        v = summary.get(k, {})
        print(f"  {k}: pass={v.get('pass')} rewarded={v.get('rewarded')} "
              f"exc={v.get('exceptions')} completed={v.get('completed','-')}")
    print(f"  codex err_by_subcause: {summary['codex_old_7x89']['err_by_subcause']}")

if __name__ == "__main__":
    main()
