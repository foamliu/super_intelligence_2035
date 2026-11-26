#!/usr/bin/env python3
"""Diagnose codex rerun exceptions and verifier_null cases."""
import json, glob, os, sys

JOBS = sys.argv[1] if len(sys.argv) > 1 else "/tmp/tb21_glm53_jobs/codex_rerun_20261117_1526"
files = sorted(glob.glob(os.path.join(JOBS, "**", "result.json"), recursive=True))
exc_msgs = {}
vnull_tasks = []
agent_timeout = 0
runtime_error = 0
other_exc = 0
for f in files:
    d = json.load(open(f))
    exc = d.get("exception_info")
    vr = d.get("verifier_result")
    ar = d.get("agent_result") or {}
    meta = ar.get("metadata") or {}
    task = d.get("task_name", "") or os.path.basename(os.path.dirname(f))
    if exc:
        # exception_info may be {type, message} or a string
        if isinstance(exc, dict):
            msg = (exc.get("message") or "")[:150]
            etype = str(exc.get("type") or exc.get("exception_type") or exc.get("class") or "")
        else:
            msg = str(exc)[:150]
            etype = ""
        if "Timeout" in msg or "timeout" in msg or "Timeout" in etype:
            agent_timeout += 1
        elif "RuntimeError" in etype or "RuntimeError" in msg:
            runtime_error += 1
        else:
            other_exc += 1
            print(f"OTHER_EXC {task}: type={etype!r} msg={msg!r}")
        exc_msgs.setdefault(etype or msg[:60], []).append(task)
    elif vr is None or (isinstance(vr, dict) and not vr):
        vnull_tasks.append(task)
print(f"agent_timeout={agent_timeout} runtime_error={runtime_error} other_exc={other_exc}")
print(f"verifier_null_no_exc={len(vnull_tasks)}: {vnull_tasks}")
print("--- exception type groups ---")
for key, tasks in sorted(exc_msgs.items(), key=lambda x: -len(x[1])):
    print(f"[{len(tasks)}] {key}: {tasks[:6]}")
# Show one full exception_info sample
for f in files:
    d = json.load(open(f))
    exc = d.get("exception_info")
    if exc:
        print("--- sample exception_info ---")
        print(json.dumps(exc, indent=2)[:800])
        break


