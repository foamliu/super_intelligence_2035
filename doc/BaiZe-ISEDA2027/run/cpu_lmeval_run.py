#!/usr/bin/env python3
"""CPU-only lm_eval wrapper for BaiZe 2B (NemotronH Mamba2-hybrid).

Handles three critical issues when running on CPU:
1. Harness agent's editable installs in /dev/shm pollute the py310 env
2. mamba_ssm / causal_conv1d are CUDA-only and segfault on CPU
3. HFLM's CLI --model_args doesn't accept device=cpu cleanly

This wrapper creates HFLM programmatically with device="cpu" and calls
lm_eval.simple_evaluate directly — the standard, well-tested path that
correctly handles request building, loglikelihood computation,
process_results, and metric aggregation (acc, acc_norm, etc.).

The previous version bypassed simple_evaluate and manually grouped results
by doc_id, which mismatched doc_idx for tasks using validation_docs as the
eval split (sciq/boolq/hellaswag/winogrande) → 0 docs processed → acc=0.0.

Usage:
  python cpu_lmeval_run.py <model_path> <output_path> [--tasks T1,T2,...] [--limit N]
"""
import sys, os, faulthandler, types, json, time, argparse

faulthandler.enable()

# ══ 1. Purge /dev/shm pollution (harness agent editable installs) ══
sys.path = [p for p in sys.path if "/dev/shm" not in p]
_new_meta_path = []
for finder in sys.meta_path:
    fs = str(finder)
    if "/dev/shm" not in fs and "Editable" not in fs:
        _new_meta_path.append(finder)
    else:
        print(f"[cpu_lmeval_run] purged meta_path finder: {fs}", file=sys.stderr)
sys.meta_path = _new_meta_path
_new_path_hooks = []
for hook in sys.path_hooks:
    hs = str(hook)
    if "Editable" not in hs and "editable" not in hs:
        _new_path_hooks.append(hook)
    else:
        print(f"[cpu_lmeval_run] purged path_hook: {hs}", file=sys.stderr)
sys.path_hooks = _new_path_hooks
for k in list(sys.modules):
    if k.startswith("__editable__"):
        del sys.modules[k]
for k in list(sys.modules):
    mod = sys.modules.get(k)
    f = getattr(mod, "__file__", "") or ""
    if "/dev/shm" in f:
        del sys.modules[k]

# ══ 2. Block mamba_ssm / causal_conv1d (CUDA-only → segfault on CPU) ══
for mod_name in ["mamba_ssm", "causal_conv1d"]:
    fake_mod = types.ModuleType(mod_name)
    fake_mod.__file__ = f"<blocked:{mod_name}>"
    fake_mod.__path__ = []
    sys.modules[mod_name] = fake_mod
for k in list(sys.modules.keys()):
    if k.startswith("mamba_ssm.") or k.startswith("causal_conv1d."):
        del sys.modules[k]

# ══ 3. Environment: CPU-only, offline ══
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_CACHE", "/nas_train/app.e0031982/hf_cache")
os.environ.setdefault("HF_HOME", "/nas_train/app.e0031982/.cache")

# ══ 4. Import torch + Patch transformers + import lm_eval ══
import torch
num_threads = int(os.environ.get("OMP_NUM_THREADS", "8"))
torch.set_num_threads(num_threads)
torch.set_num_interop_threads(2)
print(f"[cpu_lmeval_run] torch threads={num_threads}", file=sys.stderr)

import transformers.modeling_utils as _mu
def _safe_warmup(model, expanded_device_map, hf_quantizer=None):
    pass
_mu.caching_allocator_warmup = _safe_warmup
print("[cpu_lmeval_run] patched caching_allocator_warmup -> no-op", file=sys.stderr)

import lm_eval
from lm_eval.models.huggingface import HFLM

# ══ 4b. Catch deadly signals ══
import signal
def _sig_handler(signum, frame):
    sig_name = signal.Signals(signum).name
    print(f"\n[cpu_lmeval_run] CAUGHT SIGNAL {sig_name} ({signum})", file=sys.stderr, flush=True)
    faulthandler.dump_traceback(file=sys.stderr)
    sys.exit(128 + signum)
for sig in [signal.SIGSEGV, signal.SIGABRT, signal.SIGBUS, signal.SIGFPE]:
    try:
        signal.signal(sig, _sig_handler)
    except (ValueError, OSError):
        pass

# ══ 5. Parse args and run ══
parser = argparse.ArgumentParser(description="CPU-only lm_eval for BaiZe 2B")
parser.add_argument("model_path", help="Path to HF-format model directory")
parser.add_argument("output_path", help="Directory for result files")
parser.add_argument("--tasks", default="arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande")
parser.add_argument("--limit", type=int, default=None)
parser.add_argument("--num_fewshot", type=int, default=0)
parser.add_argument("--dtype", default="bfloat16")
parser.add_argument("--batch_size", type=int, default=1)
parser.add_argument("--samples", default=None, help='JSON string: {"task_name": [doc_idx,...]}')
args = parser.parse_args()

samples_dict = None
if args.samples:
    samples_dict = json.loads(args.samples)
    print(f"[cpu_lmeval_run] samples={samples_dict}", file=sys.stderr)

task_list = [t.strip() for t in args.tasks.split(",")]
os.makedirs(args.output_path, exist_ok=True)

print(f"[cpu_lmeval_run] model={args.model_path}", file=sys.stderr)
print(f"[cpu_lmeval_run] tasks={task_list} limit={args.limit} dtype={args.dtype}", file=sys.stderr)

t0 = time.time()
print("[cpu_lmeval_run] Creating HFLM (device=cpu)...", file=sys.stderr, flush=True)
# device_map="cpu" is passed via **kwargs so that lm_eval's _get_accelerate_args
# takes the `else` branch (parallelize=False, device_map is not None) and sets
# args["device_map"]=None.  This avoids from_pretrained's check_and_set_device_map
# which requires accelerate>=1.1.0 (p6_tf5 transformers 5.17 gate) while the env
# only has accelerate 0.34.2.  With device_map=None the model loads on CPU
# natively and HFLM's own .to(device) handles placement — no accelerate needed.
lm = HFLM(
    pretrained=args.model_path,
    dtype=args.dtype,
    device="cpu",
    batch_size=args.batch_size,
    trust_remote_code=False,
    logits_cache=False,
    max_length=2048,
    device_map="cpu",
)
t_load = time.time() - t0
print(f"[cpu_lmeval_run] HFLM loaded in {t_load:.1f}s device={lm.device} max_length={lm.max_length}", file=sys.stderr, flush=True)
print(f"[cpu_lmeval_run] model dtype={lm.model.dtype}", file=sys.stderr, flush=True)

# ══ 6. Run simple_evaluate (standard lm_eval path) ══
from lm_eval import simple_evaluate

t0 = time.time()
print("[cpu_lmeval_run] Starting simple_evaluate (standard lm_eval path)...", file=sys.stderr, flush=True)

results = simple_evaluate(
    model=lm,
    tasks=task_list,
    num_fewshot=args.num_fewshot,
    limit=args.limit,
    samples=samples_dict,
    log_samples=False,
)

t_eval = time.time() - t0
print(f"[cpu_lmeval_run] simple_evaluate done in {t_eval:.1f}s", file=sys.stderr, flush=True)

# ══ 7. Save results ══
result_file = os.path.join(args.output_path, "results.json")
with open(result_file, "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"[cpu_lmeval_run] Results saved to {result_file}", file=sys.stderr, flush=True)

print("\n" + "=" * 60, file=sys.stderr)
print("EVALUATION RESULTS SUMMARY", file=sys.stderr)
print("=" * 60, file=sys.stderr)
for task_name, task_results in results.get("results", {}).items():
    for metric, value in task_results.items():
        if not metric.startswith("_"):
            if isinstance(value, float):
                print(f"  {task_name}/{metric}: {value:.4f}", file=sys.stderr)
            else:
                print(f"  {task_name}/{metric}: {value}", file=sys.stderr)
print("=" * 60, file=sys.stderr)
print(f"Total eval time: {t_eval:.1f}s", file=sys.stderr)
