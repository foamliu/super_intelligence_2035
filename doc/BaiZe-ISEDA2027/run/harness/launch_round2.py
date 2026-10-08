#!/usr/bin/env python3
"""Launch 7 harnesses in parallel for round-2 (100 instances each, --resume)."""
import json, os, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ["PATH"] = os.path.expanduser("~/.bun/bin:") + os.environ["PATH"]
os.environ["https_proxy"] = "http://172.19.92.25:13128"
os.environ["http_proxy"] = "http://172.19.92.25:13128"
os.environ["HARNESS_MODEL"] = "kimi-k2.6-cloud"
os.environ["PYTHONUNBUFFERED"] = "1"

sel = json.load(open(HERE / "instance_selection_100.json"))
instances = sel["instances"]

HARNESSES = ["cline-patched", "pi", "hermes", "opencode", "codex", "claude-code", "deepseek-harness"]
pids = []

for h in HARNESSES:
    log_path = HERE / f"round2_{h}.log"
    log_f = open(log_path, "w")
    cmd = [sys.executable, str(HERE / "run_serial_kimi.py"),
           "--harness", h, "--instances"] + instances + ["--resume"]
    proc = subprocess.Popen(cmd, stdout=log_f, stderr=subprocess.STDOUT, env=os.environ.copy())
    pids.append((h, proc.pid))
    print(f"[{time.strftime('%H:%M:%S')}] Launched {h} PID={proc.pid} -> {log_path}")
    time.sleep(2)

print(f"\n[{time.strftime('%H:%M:%S')}] All 7 launched. ETA ~9-12 hours.")
print("PIDs:", {h: p for h, p in pids})
