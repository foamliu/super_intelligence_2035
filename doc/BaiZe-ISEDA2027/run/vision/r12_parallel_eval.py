#!/usr/bin/env python
"""R12 3-epoch parallel eval: split 35 ckpts across 8 GPUs using subprocess.

Launches 8 r8_eval_in1k.py processes in parallel (one per GPU), waits for all,
then merges results into /tmp/r12_continue_eval_watcher.log (the path
r12_3epoch_scaling.py reads from).

Usage: python r12_parallel_eval.py
"""
import subprocess
import os
import sys
import time
import re
from pathlib import Path

OUT = "/nas_train/app.e0031982/datasets/baize-vision/out/R12_fulldata_aimv2_w512"
PY = "/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"
VISION_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision"
MERGED_LOG = "/tmp/r12_continue_eval_watcher.log"
PARALLEL_DIR = "/tmp/r12_parallel_eval"
NGPU = 8

def main():
    os.makedirs(PARALLEL_DIR, exist_ok=True)
    # Clean old logs
    for g in range(NGPU):
        p = Path(PARALLEL_DIR) / f"gpu{g}.log"
        if p.exists():
            p.unlink()

    # Collect all ckpts sorted by step number
    step_ckpts = sorted(
        Path(OUT).glob("vision_step*.pt"),
        key=lambda p: int(re.search(r"vision_step(\d+)\.pt", p.name).group(1))
    )
    final_ckpt = Path(OUT) / "vision.pt"
    if final_ckpt.exists():
        step_ckpts.append(final_ckpt)

    print(f"Total ckpts: {len(step_ckpts)}")

    # Round-robin split across GPUs
    groups = [[] for _ in range(NGPU)]
    for i, ckpt in enumerate(step_ckpts):
        groups[i % NGPU].append(str(ckpt))

    for g in range(NGPU):
        steps = []
        for c in groups[g]:
            m = re.search(r"vision_step(\d+)\.pt", c)
            steps.append(m.group(1) if m else "344k")
        print(f"GPU {g}: {len(groups[g])} ckpts (steps: {', '.join(steps)})")

    # Launch parallel processes
    env_base = os.environ.copy()
    env_base["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

    procs = []
    for g in range(NGPU):
        env = env_base.copy()
        env["CUDA_VISIBLE_DEVICES"] = str(g)
        log_path = Path(PARALLEL_DIR) / f"gpu{g}.log"
        cmd = [PY, "r8_eval_in1k.py", "--ckpts"] + groups[g]
        print(f"Launching GPU {g}: {len(groups[g])} ckpts -> {log_path}")
        with open(log_path, "w") as f:
            p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT,
                                 env=env, cwd=VISION_DIR)
        procs.append(p)
        time.sleep(2)  # stagger launches to avoid NFS thundering herd

    print(f"\nAll {len(procs)} processes launched. Waiting...")
    print(f"PIDs: {[p.pid for p in procs]}")

    # Wait for all, reporting progress
    start = time.time()
    done = [False] * len(procs)
    while not all(done):
        time.sleep(30)
        for i, p in enumerate(procs):
            if not done[i] and p.poll() is not None:
                done[i] = True
                rc = p.returncode
                elapsed = time.time() - start
                print(f"  [{time.strftime('%H:%M:%S')}] GPU {i} done (rc={rc}, {elapsed:.0f}s)")
        # Show GPU status
        n_done = sum(done)
        n_alive = len(procs) - n_done
        if n_alive > 0:
            # Count completed ckpts across all logs
            n_ckpts_done = 0
            for g in range(NGPU):
                log = Path(PARALLEL_DIR) / f"gpu{g}.log"
                if log.exists():
                    text = log.read_text(errors="replace")
                    n_ckpts_done += text.count("linear-probe top1=")
            print(f"  [{time.strftime('%H:%M:%S')}] Progress: {n_ckpts_done}/{len(step_ckpts)} ckpts evaluated, {n_alive} GPUs still running")

    total_elapsed = time.time() - start
    print(f"\nAll eval processes complete in {total_elapsed:.0f}s")

    # Merge logs
    print("Merging results...")
    with open(MERGED_LOG, "w") as out:
        out.write("Starting IN-1k eval on 35 ckpts (full 3-epoch scaling curve)...\n")
        for g in range(NGPU):
            log = Path(PARALLEL_DIR) / f"gpu{g}.log"
            if log.exists():
                for line in log.read_text(errors="replace").splitlines():
                    if "[R8-IN1K]" in line and ("ckpt=" in line or "zero-shot" in line):
                        out.write(line + "\n")
        out.write("[R8-IN1K] DONE\n")
        out.write("===== R12-continue eval watcher ALL DONE =====\n")

    # Count results
    n_results = 0
    for g in range(NGPU):
        log = Path(PARALLEL_DIR) / f"gpu{g}.log"
        if log.exists():
            n_results += log.read_text(errors="replace").count("linear-probe top1=")
    print(f"Merged {n_results} ckpt results into {MERGED_LOG}")
    print(f"Expected: {len(step_ckpts)}")
    if n_results != len(step_ckpts):
        print(f"WARNING: expected {len(step_ckpts)} results but got {n_results}!")

    print("\nDONE")

if __name__ == "__main__":
    main()
