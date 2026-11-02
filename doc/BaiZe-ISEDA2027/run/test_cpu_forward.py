#!/usr/bin/env python3
"""Test CPU forward pass for NemotronH model - specifically test autocast behavior."""
import sys, os, faulthandler, signal, traceback
faulthandler.enable()
faulthandler.dump_traceback_later(600, exit=True)

sys.path = [p for p in sys.path if "/dev/shm" not in p]
sys.meta_path = [f for f in sys.meta_path if "Editable" not in str(f) and "/dev/shm" not in str(f)]
sys.path_hooks = [h for h in sys.path_hooks if "Editable" not in str(h)]
for k in list(sys.modules):
    mod = sys.modules.get(k)
    f = getattr(mod, "__file__", "") or ""
    if k.startswith("__editable__") or "/dev/shm" in f:
        del sys.modules[k]
for k in list(sys.modules.keys()):
    if k.startswith("mamba_ssm") or k.startswith("causal_conv1d"):
        del sys.modules[k]

class _BlockImport:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith("mamba_ssm") or fullname.startswith("causal_conv1d"):
            raise ImportError(f"Blocked: {fullname}")
        return None
sys.meta_path.insert(0, _BlockImport())

os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['HF_DATASETS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_DATASETS_CACHE'] = '/nas_train/app.e0031982/hf_cache'
os.environ['HF_HOME'] = '/nas_train/app.e0031982/.cache'

import torch
import torch.nn.functional as F
torch.set_num_threads(8)

print("=== Creating HFLM like lm_eval does ===", flush=True)
from lm_eval.models.huggingface import HFLM
model_path = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_10000"

try:
    lm = HFLM(
        pretrained=model_path,
        dtype="float32",
        device="cpu",
        batch_size=1,
        trust_remote_code=False,
        softmax_dtype="float32",
    )
    print(f"HFLM created! device={lm.device}", flush=True)
except Exception as e:
    print(f"ERROR creating HFLM: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)

# Test: run simple_evaluate with sciq limit=20 (timed)
import time
import lm_eval
print("\n=== Running simple_evaluate sciq limit=20 (timed) ===", flush=True)
t0 = time.time()
try:
    results = lm_eval.simple_evaluate(
        model=lm,
        tasks=["sciq"],
        num_fewshot=0,
        limit=20,
        batch_size=1,
    )
    elapsed = time.time() - t0
    print(f"\n=== sciq limit=20 completed in {elapsed:.1f}s ===", flush=True)
    print(f"Per-sample: {elapsed/20:.2f}s  Per-request(4x): {elapsed/80:.2f}s", flush=True)
    for task_name, task_results in results.get("results", {}).items():
        for metric, value in task_results.items():
            if not metric.startswith("_"):
                print(f"  {task_name}/{metric}: {value}", flush=True)
except Exception as e:
    elapsed = time.time() - t0
    print(f"ERROR after {elapsed:.1f}s: {e}", flush=True)
    import traceback
    traceback.print_exc()

# Also test arc_easy with limit=20 (different seq lengths)
print("\n=== Running simple_evaluate arc_easy limit=20 (timed) ===", flush=True)
t0 = time.time()
try:
    results2 = lm_eval.simple_evaluate(
        model=lm,
        tasks=["arc_easy"],
        num_fewshot=0,
        limit=20,
        batch_size=1,
    )
    elapsed2 = time.time() - t0
    print(f"\n=== arc_easy limit=20 completed in {elapsed2:.1f}s ===", flush=True)
    print(f"Per-sample: {elapsed2/20:.2f}s", flush=True)
    for task_name, task_results in results2.get("results", {}).items():
        for metric, value in task_results.items():
            if not metric.startswith("_"):
                print(f"  {task_name}/{metric}: {value}", flush=True)
except Exception as e:
    elapsed2 = time.time() - t0
    print(f"ERROR after {elapsed2:.1f}s: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("\nDone!", flush=True)

