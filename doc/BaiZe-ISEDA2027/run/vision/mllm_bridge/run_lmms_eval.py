#!/usr/bin/env python
"""Run lmms-eval 17 benchmarks on BaiZe-LLaVA (Stage-2 checkpoint).

Usage:
    cd run/vision
    python mllm_bridge/run_lmms_eval.py [--step 3500] [--limit 100]

Environment:
    https_proxy=http://172.19.92.25:13128  (direct to hf.co, NOT mirror)
"""

import os, sys, json, time, argparse

# ---- proxy: direct to hf.co (NOT mirror) ----
os.environ.setdefault("https_proxy", "http://172.19.92.25:13128")
os.environ.setdefault("http_proxy", "http://172.19.92.25:13128")
# Remove any hf-mirror settings
os.environ.pop("HF_ENDPOINT", None)

VISION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, VISION_DIR)
sys.path.insert(0, BRIDGE_DIR)

# Import our custom model (registers it as an importable module)
from mllm_bridge.lmms_eval_baize_llava import BaizeLLaVA  # noqa: F401

from lmms_eval.evaluator import simple_evaluate
from lmms_eval.tasks import TaskManager
from lmms_eval.models import MODEL_REGISTRY_V2
from lmms_eval.models.registry_v2 import ModelManifest

# Register our custom model in lmms-eval's V2 registry
MODEL_REGISTRY_V2.register_manifest(
    ModelManifest(
        model_id="baize_llava",
        chat_class_path="mllm_bridge.lmms_eval_baize_llava.BaizeLLaVA",
    ),
    overwrite=True,
)
print(f"[run_lmms_eval] Registered 'baize_llava' in MODEL_REGISTRY_V2")

CKPT = "/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E4_4ep_ov2_w512_d30_p16_224/vision.pt"
LLM_PATH = "/nas_train/app.e0031982/models/Qwen/Qwen3-4B-Instruct-2507"
STAGE2_BASE = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage2"
RESULTS_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results"

# 17 benchmarks (standard VLM evaluation suite)
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
    parser.add_argument("--step", type=int, default=3500, help="Stage-2 checkpoint step")
    parser.add_argument("--limit", type=int, default=None, help="Limit samples per task (for testing)")
    parser.add_argument("--tasks", type=str, default=None, help="Comma-separated task list (default: all 17)")
    parser.add_argument("--output", type=str, default=None, help="Output JSON path")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size for evaluation (increase for throughput)")
    args = parser.parse_args()

    stage2_ckpt = os.path.join(STAGE2_BASE, f"step{args.step}")
    if not os.path.exists(os.path.join(stage2_ckpt, "projector.pt")):
        print(f"ERROR: Stage-2 checkpoint not found at {stage2_ckpt}")
        sys.exit(1)

    tasks = args.tasks.split(",") if args.tasks else BENCHMARKS_17
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output_path = args.output or os.path.join(
        RESULTS_DIR, f"eval_step{args.step}_{int(time.time())}.json"
    )

    model_args = f"ckpt={CKPT},stage2_ckpt={stage2_ckpt},llm_path={LLM_PATH},max_new_tokens=128"

    print(f"\n{'='*60}")
    print(f"BaiZe-LLaVA lmms-eval 17 Benchmarks")
    print(f"  Stage-2 ckpt: {stage2_ckpt}")
    print(f"  Tasks: {len(tasks)} benchmarks")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Limit: {args.limit or 'full'}")
    print(f"  Output: {output_path}")
    print(f"  Proxy: {os.environ.get('https_proxy', 'none')}")
    print(f"  LOCAL_RANK: {os.environ.get('LOCAL_RANK', 'N/A')}")
    print(f"  WORLD_SIZE: {os.environ.get('WORLD_SIZE', '1')}")
    print(f"{'='*60}\n")

    tm = TaskManager()

    results = simple_evaluate(
        model="baize_llava",
        model_args=model_args,
        tasks=tasks,
        batch_size=args.batch_size,
        limit=args.limit,
        log_samples=True,
        task_manager=tm,
        verbosity="INFO",
    )

    # Save results
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}")

    # Print summary
    if results and "results" in results:
        print(f"\n{'='*60}")
        print(f"Benchmark Results Summary")
        print(f"{'='*60}")
        for task_name, metrics in results["results"].items():
            # Extract primary metric
            primary = ""
            for k, v in metrics.items():
                if isinstance(v, (int, float)) and "acc" in k.lower():
                    primary = f"{k}={v:.4f}"
                    break
            if not primary:
                for k, v in metrics.items():
                    if isinstance(v, (int, float)):
                        primary = f"{k}={v:.4f}"
                        break
            print(f"  {task_name:30s} {primary}")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
