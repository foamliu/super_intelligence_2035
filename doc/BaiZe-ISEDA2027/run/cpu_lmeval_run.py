#!/usr/bin/env python3
"""CPU-only lm_eval wrapper for BaiZe 2B (NemotronH Mamba2-hybrid).

Handles three critical issues when running on CPU:
1. Harness agent's editable installs in /dev/shm pollute the py310 env
2. mamba_ssm / causal_conv1d are CUDA-only and segfault on CPU
3. HFLM's CLI --model_args doesn't accept device=cpu cleanly

This wrapper creates HFLM programmatically with device="cpu" and calls
simple_evaluate directly, bypassing the CLI.

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

# ══ 4. Import torch + patch transformers + import lm_eval ══
import torch
num_threads = int(os.environ.get("OMP_NUM_THREADS", "4"))
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
for sig in [signal.SIGSEGV, signal.SIGABRT, signal.SIGBUS, signal.SIGFPE, signal.SIGKILL if hasattr(signal, 'SIGKILL') else signal.SIGTERM]:
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
parser.add_argument("--dtype", default="float32")
parser.add_argument("--batch_size", type=int, default=1)
args = parser.parse_args()

task_list = [t.strip() for t in args.tasks.split(",")]
os.makedirs(args.output_path, exist_ok=True)

print(f"[cpu_lmeval_run] model={args.model_path}", file=sys.stderr)
print(f"[cpu_lmeval_run] tasks={task_list} limit={args.limit} dtype={args.dtype}", file=sys.stderr)

t0 = time.time()
print("[cpu_lmeval_run] Creating HFLM (device=cpu)...", file=sys.stderr, flush=True)
lm = HFLM(
    pretrained=args.model_path,
    dtype=args.dtype,
    device="cpu",
    batch_size=args.batch_size,
    trust_remote_code=False,
    logits_cache=False,
    max_length=2048,
)
t_load = time.time() - t0
print(f"[cpu_lmeval_run] HFLM loaded in {t_load:.1f}s device={lm.device} max_length={lm.max_length}", file=sys.stderr, flush=True)
print(f"[cpu_lmeval_run] model dtype={lm.model.dtype}", file=sys.stderr, flush=True)

t0 = time.time()
print("[cpu_lmeval_run] Starting simple_evaluate...", file=sys.stderr, flush=True)

# Instead of simple_evaluate (which crashes during task construction/metric
# computation due to sklearn binary incompatibility from harness agent's
# editable install), we directly:
# 1. Load each task's dataset
# 2. Build loglikelihood requests
# 3. Call lm.loglikelihood directly
# 4. Compute acc/acc_norm manually

from lm_eval.tasks import TaskManager
from lm_eval.api.instance import Instance
import numpy as np

all_results = {}
total_n_samples = 0
for task_name in task_list:
    print(f"\n[cpu_lmeval_run] --- Task: {task_name} ---", file=sys.stderr, flush=True)
    tm = TaskManager()
    task_dict = tm.load_task_or_group([task_name])
    task = task_dict[task_name]

    # Build dataset
    task.build_all_requests(limit=args.limit, rank=0, world_size=1)
    requests = task.instances
    print(f"[cpu_lmeval_run] {task_name}: {len(requests)} requests", file=sys.stderr, flush=True)
    total_n_samples += len(requests)

    # Run loglikelihood — but first try a single forward pass manually
    print(f"[cpu_lmeval_run] {task_name}: {len(requests)} requests", file=sys.stderr, flush=True)

    # Debug: try first request manually
    if requests:
        req = requests[0]
        print(f"[cpu_lmeval_run] DEBUG: first request args={repr(req.args)[:200]}", file=sys.stderr, flush=True)
        ctx, cont = req.args
        ctx_enc = lm.tok_encode(ctx) if ctx else [lm.prefix_token_id]
        cont_enc = lm.tok_encode(cont, add_special_tokens=False)
        full_inp = (ctx_enc + cont_enc)
        print(f"[cpu_lmeval_run] DEBUG: ctx_enc len={len(ctx_enc)} cont_enc len={len(cont_enc)} full len={len(full_inp)}", file=sys.stderr, flush=True)
        import torch as _torch
        inp_tensor = _torch.tensor([full_inp[:-1]], dtype=_torch.long, device="cpu")
        print(f"[cpu_lmeval_run] DEBUG: inp_tensor shape={inp_tensor.shape}", file=sys.stderr, flush=True)
        try:
            with _torch.no_grad():
                out = lm.model(inp_tensor)
            print(f"[cpu_lmeval_run] DEBUG: forward OK, logits shape={out.logits.shape}", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"[cpu_lmeval_run] DEBUG: forward FAILED: {e}", file=sys.stderr, flush=True)
            import traceback
            traceback.print_exc(file=sys.stderr)

    t_task = time.time()
    ll_results = lm.loglikelihood(requests)
    t_task_elapsed = time.time() - t_task
    print(f"[cpu_lmeval_run] {task_name}: eval done in {t_task_elapsed:.1f}s", file=sys.stderr, flush=True)

    # Process results using the task's own process_results method
    task_results = {}

    # Group results by doc_id
    results_by_doc = {}
    for req, (ll, is_greedy) in zip(requests, ll_results):
        doc_id = req.doc_id if req.doc_id is not None else 0
        if doc_id not in results_by_doc:
            results_by_doc[doc_id] = []
        results_by_doc[doc_id].append((ll, is_greedy))

    # Use the task's process_results for proper metric computation
    aggregated = {}
    doc_count = 0
    # Get the docs that were actually evaluated
    if hasattr(task, 'eval_docs') and task.eval_docs is not None:
        docs_iter = task.eval_docs
    elif hasattr(task, 'test_docs') and task.has_test_docs():
        docs_iter = task.test_docs()
    elif hasattr(task, 'validation_docs') and task.has_validation_docs():
        docs_iter = task.validation_docs()
    else:
        docs_iter = task.training_docs()

    docs_list = list(docs_iter)
    for doc_idx, doc in enumerate(docs_list):
        if doc_idx not in results_by_doc:
            continue
        resps = results_by_doc[doc_idx]
        try:
            processed = task.process_results(doc, resps)
            if processed:
                for metric, value in processed.items():
                    if metric not in aggregated:
                        aggregated[metric] = []
                    aggregated[metric].append(value)
                doc_count += 1
        except Exception as e:
            print(f"[cpu_lmeval_run] {task_name}: process_results error for doc {doc_idx}: {e}", file=sys.stderr, flush=True)

    # Aggregate (mean for most metrics)
    for metric, values in aggregated.items():
        if values:
            task_results[metric] = float(np.mean(values))

    all_results[task_name] = task_results
    metrics_str = " ".join(f"{k}={v:.4f}" for k, v in task_results.items())
    print(f"[cpu_lmeval_run] {task_name}: {metrics_str} ({doc_count} docs)", file=sys.stderr, flush=True)

t_eval = time.time() - t0
print(f"\n[cpu_lmeval_run] All tasks done in {t_eval:.1f}s", file=sys.stderr, flush=True)

# Build results dict
results = {
    "results": {k: v for k, v in all_results.items()},
    "n_samples": total_n_samples,
}
t_eval = time.time() - t0
print(f"[cpu_lmeval_run] Evaluation done in {t_eval:.1f}s", file=sys.stderr, flush=True)

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