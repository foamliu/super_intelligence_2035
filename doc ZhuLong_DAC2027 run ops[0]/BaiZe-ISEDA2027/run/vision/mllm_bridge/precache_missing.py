#!/usr/bin/env python
"""Pre-cache missing datasets (vizwiz_vqa, infovqa) for lmms-eval.

Single process — avoids 429 from parallel hub API calls when 8 ranks
try to load the same uncached dataset simultaneously.

After this runs, the launch script can use HF_HUB_OFFLINE=1 to prevent
any API calls during the 8-GPU eval.
"""
import os, sys, time

# ---- env (same as launch_limit50_nasenv.sh) ----
os.environ["https_proxy"] = "http://172.19.92.25:13128"
os.environ["http_proxy"] = "http://172.19.92.25:13128"
os.environ.pop("HF_ENDPOINT", None)
os.environ["HF_HOME"] = "/nas_env/app.e0031982/hf_home"
os.environ["HF_DATASETS_CACHE"] = os.path.join(os.environ["HF_HOME"], "datasets")
os.environ["HF_HUB_CACHE"] = os.path.join(os.environ["HF_HOME"], "hub")
os.environ["TRANSFORMERS_CACHE"] = os.path.join(os.environ["HF_HOME"], "transformers")
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
os.environ["HF_TOKEN"] = "hf_dummy"
os.environ["LMMS_EVAL_DATASETS_CACHE"] = "/nas_env/app.e0031982/lmms_eval_cache"

from datasets import load_dataset

CACHE_DIR = os.environ["LMMS_EVAL_DATASETS_CACHE"]

datasets_to_cache = [
    # (label, dataset_path, config_name, split)
    ("vizwiz_vqa_val", "lmms-lab/VizWiz-VQA", None, "val"),
    ("infovqa_val",    "lmms-lab/DocVQA",     "InfographicVQA", "validation"),
]

print(f"Pre-caching {len(datasets_to_cache)} missing datasets into {CACHE_DIR}")
print(f"  (single process — no parallel API calls)")

for label, path, config, split in datasets_to_cache:
    # Check if already cached
    expected_dir = os.path.join(CACHE_DIR, "lmms-lab___" + path.split("/")[-1].lower().replace("-", "_"))
    # Also handle special naming
    if "vizwiz" in label:
        expected_dir = os.path.join(CACHE_DIR, "lmms-lab___viz_wiz_vqa")
    elif "infovqa" in label:
        expected_dir = os.path.join(CACHE_DIR, "lmms-lab___doc_vqa")

    if os.path.exists(expected_dir):
        print(f"\n[{label}] Already cached at {expected_dir} — skipping")
        continue

    print(f"\n[{label}] Loading {path}" + (f" config={config}" if config else "") + f" split={split}...")
    t0 = time.time()
    try:
        if config:
            ds = load_dataset(path, config, split=split, cache_dir=CACHE_DIR, token=True)
        else:
            ds = load_dataset(path, split=split, cache_dir=CACHE_DIR, token=True)
        print(f"  [{label}] Loaded {len(ds)} samples in {time.time()-t0:.1f}s")
    except Exception as e:
        print(f"  [{label}] ERROR: {e}")
        # Retry once after delay (in case of transient 429)
        print(f"  [{label}] Retrying in 30s...")
        time.sleep(30)
        try:
            if config:
                ds = load_dataset(path, config, split=split, cache_dir=CACHE_DIR, token=True)
            else:
                ds = load_dataset(path, split=split, cache_dir=CACHE_DIR, token=True)
            print(f"  [{label}] Loaded {len(ds)} samples in {time.time()-t0:.1f}s (retry)")
        except Exception as e2:
            print(f"  [{label}] FATAL: {e2}")
            sys.exit(1)

print(f"\n{'='*60}")
print("Pre-cache complete! All datasets cached.")
print(f"lmms_eval_cache contents:")
for d in sorted(os.listdir(CACHE_DIR)):
    full = os.path.join(CACHE_DIR, d)
    if os.path.isdir(full):
        print(f"  {d}/")
print(f"{'='*60}")
