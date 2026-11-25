#!/usr/bin/env python
"""Pre-download and build dataset cache for all 17 lmms-eval benchmarks.

CRITICAL: Must be run as a SINGLE process (no multi-GPU / no accelerate)
BEFORE launching the 8-GPU multi-GPU eval. This avoids 8 ranks
simultaneously writing dataset cache to disk (which caused
"No space left on device" on 2026-10-15 21:24).

Usage:
    cd run/vision
    python mllm_bridge/precache_benchmarks.py [--limit 1]

Environment:
    https_proxy=http://172.19.92.25:13128  (direct to hf.co, NOT mirror)
    HF_HOME=/nas_env/app.e0031982/hf_home  (large disk, NOT /home)
"""

import os, sys, time, argparse, traceback

# ---- proxy: direct to hf.co (NOT mirror) ----
os.environ.setdefault("https_proxy", "http://172.19.92.25:13128")
os.environ.setdefault("http_proxy", "http://172.19.92.25:13128")
os.environ.pop("HF_ENDPOINT", None)

# ---- HF cache on large disk ----
os.environ.setdefault("HF_HOME", "/nas_env/app.e0031982/hf_home")
os.environ.setdefault("HF_DATASETS_CACHE", os.path.join(os.environ["HF_HOME"], "datasets"))
os.environ.setdefault("HF_HUB_CACHE", os.path.join(os.environ["HF_HOME"], "hub"))
os.environ.setdefault("TRANSFORMERS_CACHE", os.path.join(os.environ["HF_HOME"], "transformers"))
os.makedirs(os.environ["HF_DATASETS_CACHE"], exist_ok=True)
os.makedirs(os.environ["HF_HUB_CACHE"], exist_ok=True)
os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "1")
os.environ.setdefault("HF_TOKEN", "hf_dummy")
# lmms-eval cache — use /tmp by default (same as precache's NFS→/tmp redirect)
# NOTE: /data/app.e0031982/ is root-owned and cannot be created.
os.environ.setdefault("LMMS_EVAL_DATASETS_CACHE", "/tmp/lmms_eval_hf_datasets_app.e0031982")
try:
    os.makedirs(os.environ["LMMS_EVAL_DATASETS_CACHE"], exist_ok=True)
except PermissionError:
    pass  # directory already exists

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, BRIDGE_DIR)

# Import our custom model (registers it as an importable module)
from mllm_bridge.lmms_eval_baize_llava import BaizeLLaVA  # noqa: F401

from lmms_eval.tasks import TaskManager

# 17 benchmarks (same as run_lmms_eval.py)
BENCHMARKS_17 = [
    "mmbench_en_dev",
    "mmmu_val",
    "gqa",
    "textvqa_val",
    "docvqa_val",
    "chartqa",
    "ai2d",
    "scienceqa",
    "seedbench",
    "pope",
    "vizwiz_vqa_val",
    "ocrbench",
    "mmvet",
    "hallusion_bench_image",
    "realworldqa",
    "vqav2_val",
    "infovqa_val",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=1,
                        help="Limit samples per task (default 1, just to trigger download+cache build)")
    parser.add_argument("--tasks", type=str, default=None,
                        help="Comma-separated task list (default: all 17)")
    args = parser.parse_args()

    tasks = args.tasks.split(",") if args.tasks else BENCHMARKS_17

    print(f"\n{'='*60}")
    print(f"  lmms-eval Dataset Pre-Cache Builder (SINGLE PROCESS)")
    print(f"  HF_HOME: {os.environ['HF_HOME']}")
    print(f"  HF_DATASETS_CACHE: {os.environ['HF_DATASETS_CACHE']}")
    print(f"  Proxy: {os.environ.get('https_proxy', 'none')}")
    print(f"  Tasks: {len(tasks)} benchmarks")
    print(f"  Limit: {args.limit}")
    print(f"  Start: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Check disk space
    import shutil
    total, used, free = shutil.disk_usage(os.environ["HF_HOME"])
    free_gb = free / (1024**3)
    print(f"[precache] Disk space at HF_HOME: {free_gb:.1f} GB free")
    if free_gb < 50:
        print(f"[precache] WARNING: Only {free_gb:.1f} GB free (<50G threshold)")

    tm = TaskManager()
    results_log = []
    total_start = time.time()

    for i, task_name in enumerate(tasks):
        print(f"\n[{i+1}/{len(tasks)}] Pre-caching '{task_name}'...")
        task_start = time.time()
        try:
            # load_task_or_group triggers the dataset download + cache build
            loaded = tm.load_task_or_group(task_name)
            if loaded:
                # Try to actually load the dataset by instantiating task objects
                for key, task_config in loaded.items():
                    try:
                        # Access the dataset to trigger download
                        if hasattr(task_config, 'dataset'):
                            _ = task_config.dataset
                    except Exception:
                        pass
                elapsed = time.time() - task_start
                msg = f"  ✅ {task_name} cached in {elapsed:.1f}s"
                print(msg)
                results_log.append((task_name, "OK", elapsed))
            else:
                msg = f"  ⚠️  {task_name} returned empty"
                print(msg)
                results_log.append((task_name, "EMPTY", time.time() - task_start))
        except Exception as e:
            elapsed = time.time() - task_start
            err_msg = f"  ❌ {task_name} FAILED in {elapsed:.1f}s: {e}"
            print(err_msg)
            traceback.print_exc()
            results_log.append((task_name, f"FAIL: {e}", elapsed))

        # Check disk space after each download
        total2, used2, free2 = shutil.disk_usage(os.environ["HF_HOME"])
        free_gb2 = free2 / (1024**3)
        print(f"  [disk] {free_gb2:.1f} GB free at HF_HOME")

    total_elapsed = time.time() - total_start

    print(f"\n{'='*60}")
    print(f"  Pre-Cache Summary")
    print(f"{'='*60}")
    ok_count = sum(1 for _, status, _ in results_log if status == "OK")
    fail_count = sum(1 for _, status, _ in results_log if status.startswith("FAIL"))
    for task_name, status, elapsed in results_log:
        print(f"  {task_name:30s} {status:10s} {elapsed:7.1f}s")
    print(f"\n  Total: {ok_count} OK, {fail_count} FAILED, {total_elapsed:.0f}s ({total_elapsed/60:.1f}min)")
    print(f"{'='*60}\n")

    if fail_count > 0:
        print("[precache] Some tasks failed! Check errors above before running multi-GPU eval.")
        sys.exit(1)
    else:
        print("[precache] All tasks cached successfully. Ready for multi-GPU eval.")


if __name__ == "__main__":
    main()
