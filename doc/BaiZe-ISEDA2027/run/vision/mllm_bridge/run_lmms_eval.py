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

# ---- HF cache on large disk (NOT /home which is only 196G) ----
# CRITICAL: /home has only 47G free; 8 ranks writing datasets cache simultaneously
# caused "No space left on device" crash on 2026-10-15 21:24.
# /nas_env has 9.9T free — all ranks share this cache.
os.environ.setdefault("HF_HOME", "/nas_env/app.e0031982/hf_home")
os.environ.setdefault("HF_DATASETS_CACHE", os.path.join(os.environ["HF_HOME"], "datasets"))
os.environ.setdefault("HF_HUB_CACHE", os.path.join(os.environ["HF_HOME"], "hub"))
os.environ.setdefault("TRANSFORMERS_CACHE", os.path.join(os.environ["HF_HOME"], "transformers"))
os.makedirs(os.environ["HF_DATASETS_CACHE"], exist_ok=True)
os.makedirs(os.environ["HF_HUB_CACHE"], exist_ok=True)
os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "1")
os.environ.setdefault("HF_TOKEN", "hf_dummy")

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

CKPT_4EP = "/nas_train/app.e0031982/datasets/baize-vision/out/scaling_E4_4ep_ov2_w512_d30_p16_224/vision.pt"
CKPT_ARMB = "/nas_train/app.e0031982/datasets/baize-vision/out/armB_aimv2_openclip_vitb16_224/open_clip_state_dict.pt"
CKPT_ARMC = "/nas_train/app.e0031982/datasets/baize-vision/out/armC_20261018_aimv2_openclip_vitb16_224/open_clip_state_dict.pt"
LLM_PATH = "/nas_train/app.e0031982/models/Qwen/Qwen3-4B-Instruct-2507"
STAGE2_BASE_4EP = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage2"
STAGE2_BASE_ARMB = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage2_armB"
STAGE2_BASE_ARMC = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage2_armC_20261018"
RESULTS_DIR_4EP = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results"
RESULTS_DIR_ARMB = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_armB"
RESULTS_DIR_ARMC = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_armC_20261018"

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
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size for evaluation (increase for throughput)")
    parser.add_argument("--vision_backend", type=str, default="baize_4ep",
                        choices=["baize_4ep", "armB", "armC"],
                        help="baize_4ep=④-4ep BaiZe ViT(512d); armB=open_clip ViT-B/16(768d); armC=ArmC(768d, min_lr1e-5+wd0.01)")
    parser.add_argument("--ckpt", type=str, default=None, help="Override vision tower checkpoint path")
    parser.add_argument("--stage2_base", type=str, default=None, help="Override stage2 ckpt base dir (step appended)")
    args = parser.parse_args()

    # Resolve backend-specific defaults
    if args.vision_backend == "armB":
        ckpt = args.ckpt or CKPT_ARMB
        stage2_base = args.stage2_base or STAGE2_BASE_ARMB
        results_dir = RESULTS_DIR_ARMB
    elif args.vision_backend == "armC":
        ckpt = args.ckpt or CKPT_ARMC
        stage2_base = args.stage2_base or STAGE2_BASE_ARMC
        results_dir = RESULTS_DIR_ARMC
    else:
        ckpt = args.ckpt or CKPT_4EP
        stage2_base = args.stage2_base or STAGE2_BASE_4EP
        results_dir = RESULTS_DIR_4EP
    stage2_ckpt = os.path.join(stage2_base, f"step{args.step}")
    if not os.path.exists(os.path.join(stage2_ckpt, "projector.pt")):
        print(f"ERROR: Stage-2 checkpoint not found at {stage2_ckpt}")
        sys.exit(1)

    tasks = args.tasks.split(",") if args.tasks else BENCHMARKS_17
    os.makedirs(results_dir, exist_ok=True)
    output_path = args.output or os.path.join(
        results_dir, f"eval_{args.vision_backend}_step{args.step}_{int(time.time())}.json"
    )

    model_args = f"ckpt={ckpt},stage2_ckpt={stage2_ckpt},llm_path={LLM_PATH},vision_backend={args.vision_backend},max_new_tokens=128"

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

    # log_samples=False: prevents gather_object OOM on large datasets.
    # When log_samples=True, lmms-eval gathers ALL logged samples from 8 ranks
    # to rank 0 via torch.distributed.gather_object, which tried to allocate
    # 119 GiB for GQA (12k samples) → CUDA OOM crash.
    # With log_samples=False, only aggregate metrics are gathered (tiny).
    results = simple_evaluate(
        model="baize_llava",
        model_args=model_args,
        tasks=tasks,
        batch_size=args.batch_size,
        limit=args.limit,
        log_samples=False,
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
