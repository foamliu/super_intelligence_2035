#!/usr/bin/env python3
"""Deep debug: run DeepSeekHarness with full stderr/event capture."""
import sys, os, json, time
sys.path.insert(0, "/tmp/dsh_sdk")

from deepseek_harness import DeepSeekHarness
from pathlib import Path

INST = json.loads(Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/instances/django__django-10097.json").read_text())
WORKDIR = "/dev/shm/harness_verified_full/workdirs/deepseek-harness/django_django"

# Reset workdir
import subprocess
subprocess.run(["git", "reset", "--hard", INST["base_commit"]], cwd=WORKDIR, capture_output=True)
subprocess.run(["git", "clean", "-fdq"], cwd=WORKDIR, capture_output=True)

print(f"=== DEEPSEEK HARNESS DEEP DEBUG ===")
print(f"instance: {INST['instance_id']}")
print(f"base_url: http://127.0.0.1:9091/v1")
print(f"profile: sdk-minimal")
print(f"dsh_home: /tmp/dsh_home")
print(f"workdir: {WORKDIR}")
print(f"DEEPSEEK_BASE_URL will be set to http://127.0.0.1:9091/v1")
print(f"DEEPSEEK_API_KEY will be set to dummy-key-for-proxy")
print()

# Check env that will be passed
env_preview = {
    "DEEPSEEK_BASE_URL": "http://127.0.0.1:9091/v1",
    "DEEPSEEK_API_KEY": "dummy-key-for-proxy",
    "DSH_HOME": "/tmp/dsh_home",
}
print(f"env preview: {json.dumps(env_preview, indent=2)}")
print()

t0 = time.time()
try:
    harness = DeepSeekHarness(
        provider="deepseek-official",
        model="kimi-k2.6-cloud",
        base_url="http://127.0.0.1:9091/v1",
        api_key="dummy-key-for-proxy",
        cwd=WORKDIR,
        dsh_home="/tmp/dsh_home",
        profile="sdk-minimal",
        request_timeout_seconds=300.0,
        initialize_timeout_seconds=60.0,
    )
    print(f"[{time.time()-t0:.1f}s] DeepSeekHarness created")

    with harness:
        print(f"[{time.time()-t0:.1f}s] runtime started (entered context)")
        # Access the client's stderr lines and process info
        client = harness._client
        proc = client._proc
        if proc:
            print(f"  runtime pid={proc.pid}, poll={proc.poll()}")
            print(f"  runtime args (first 5): {proc.args[:5] if hasattr(proc,'args') else 'N/A'}")

        print(f"[{time.time()-t0:.1f}s] calling harness.run()...")
        result = harness.run(INST["problem_statement"], session_id=INST["instance_id"])
        print(f"[{time.time()-t0:.1f}s] harness.run() returned")

        print(f"  final_response len: {len(result.final_response)}")
        print(f"  final_response (first 500): {result.final_response[:500]}")
        print(f"  finish_reason: {result.finish_reason}")
        print(f"  events count: {len(result.events)}")
        for i, ev in enumerate(result.events):
            print(f"    event[{i}]: {json.dumps(ev, default=str)[:500]}")
        print(f"  notifications count: {len(result.notifications)}")
        for i, n in enumerate(result.notifications[:10]):
            print(f"    notif[{i}]: method={n.method} payload={json.dumps(n.payload, default=str)[:300]}")

    print(f"[{time.time()-t0:.1f}s] runtime closed (exited context)")

    # Print captured stderr
    print(f"\n=== RUNTIME STDERR (last 50 lines) ===")
    stderr_lines = list(client._stderr_lines)
    for line in stderr_lines[-50:]:
        print(f"  {line}")

    # Check if runtime process exited cleanly
    if proc:
        print(f"\n=== RUNTIME PROCESS ===")
        print(f"  pid={proc.pid}, returncode={proc.returncode}, poll={proc.poll()}")

except Exception as ex:
    print(f"[{time.time()-t0:.1f}s] EXCEPTION: {type(ex).__name__}: {ex}")
    import traceback
    traceback.print_exc()

# Check git diff
print(f"\n=== GIT DIFF (workdir changes) ===")
r = subprocess.run(["git", "--no-pager", "diff", "--stat"], cwd=WORKDIR, capture_output=True, text=True)
print(r.stdout[:1000] if r.stdout else "(no changes)")

print(f"\nTotal wall: {time.time()-t0:.1f}s")
