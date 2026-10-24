#!/usr/bin/env python3
"""Orchestrator: long-context inference cost eval for BaiZe-2B / MiniCPM5-2B / Qwen3.5-2B."""
import argparse, glob, json, os, subprocess, sys, time, requests

PY = "/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python"
HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.join(HERE, "benchmark_longctx_sglang.py")
RESULTS_DIR = os.path.join(HERE, "longctx_eval_results")
GPU = 0
PORT = 30050
GEN_LEN = 128

MODELS = {
    "baize-2b": {"path": "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/hf_checkpoints/p3_hybrid", "serve_name": "baize-2b", "extra_args": ["--mamba-ssm-dtype", "float32"]},
    "minicpm5-2b": {"path_glob": "/nas_train/app.e0031982/hf_cache/hub/models--openbmb--MiniCPM5-2B/snapshots/*", "serve_name": "MiniCPM5-2B", "extra_args": []},
    "qwen35-2b": {"path_glob": "/nas_train/app.e0031982/hf_cache/hub/models--Qwen--Qwen3.5-2B/snapshots/*", "serve_name": "Qwen3.5-2B", "extra_args": []},
}
CONTEXTS = [65536, 131072, 262144, 524288, 1048576, 2097152]

def resolve_path(md):
    if "path" in md: return md["path"]
    ps = glob.glob(md["path_glob"]); return ps[0] if ps else None

def wait_server(url, max_wait=300):
    elapsed = 0
    while elapsed < max_wait:
        try:
            if requests.get(f"{url}/v1/models", timeout=10).status_code == 200: return True
        except Exception: pass
        time.sleep(5); elapsed += 5
        if elapsed % 30 == 0: print(f"  [wait] {elapsed}s...", flush=True)
    return False

def kill_server(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try: proc.wait(timeout=10)
        except subprocess.TimeoutExpired: proc.kill(); proc.wait(timeout=5)
    subprocess.run(f"pkill -f 'sglang.launch_server.*port {PORT}'", shell=True, timeout=10)
    time.sleep(3)
    for _ in range(20):
        try:
            out = subprocess.check_output(["nvidia-smi", f"--id={GPU}", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], text=True, timeout=5).strip()
            if int(out) < 1000: break
        except Exception: pass
        time.sleep(3)

def start_server(model_path, serve_name, ctx, extra_args):
    cmd = [PY, "-m", "sglang.launch_server", "--model-path", model_path,
           "--served-model-name", serve_name, "--port", str(PORT), "--host", "127.0.0.1",
           "--context-length", str(ctx), "--mem-fraction-static", "0.88",
           "--dtype", "bfloat16", "--attention-backend", "flashinfer",
           "--disable-radix-cache", "--log-level", "info"] + extra_args
    log_file = os.path.join(RESULTS_DIR, f"server_{serve_name}_ctx{ctx}.log")
    log_f = open(log_file, "w")
    env = os.environ.copy(); env["CUDA_VISIBLE_DEVICES"] = str(GPU)
    env["SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN"] = "1"
    proc = subprocess.Popen(cmd, stdout=log_f, stderr=subprocess.STDOUT, env=env)
    return proc, log_file

def run_bench(model_path, serve_name, ctx, output_file):
    cmd = [PY, BENCH, "--base-url", f"http://127.0.0.1:{PORT}", "--model-name", serve_name,
           "--model-path", model_path, "--gpu-id", str(GPU), "--output", output_file,
           "--start-ctx", str(ctx), "--gen-len", str(GEN_LEN), "--max-ctx", str(ctx),
           "--warmup", "1", "--repeats", "2"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1200)
    print(proc.stdout[-500:] if len(proc.stdout) > 500 else proc.stdout, flush=True)
    if proc.stderr: print(f"  [stderr] {proc.stderr[-300:]}", flush=True)
    return proc.returncode == 0

def eval_model(name, model_def):
    model_path = resolve_path(model_def)
    if not model_path or not os.path.isdir(model_path):
        print(f"[error] Model path not found for {name}: {model_path}")
        return {"model": name, "error": "path_not_found", "results": []}
    serve_name = model_def["serve_name"]
    extra_args = model_def.get("extra_args", [])
    output_file = os.path.join(RESULTS_DIR, f"results_{name}.json")
    all_results = []
    print(f"\n{'#'*60}\n# Model: {name} | path: {model_path}\n{'#'*60}", flush=True)
    for ctx in CONTEXTS:
        print(f"\n===== {name} | ctx={ctx} ({ctx//1024}K) =====", flush=True)
        proc, log_file = start_server(model_path, serve_name, ctx, extra_args)
        print(f"  [server] PID={proc.pid}, log={log_file}", flush=True)
        if not wait_server(f"http://127.0.0.1:{PORT}", max_wait=300):
            print(f"  [OOM] Server failed to start at ctx={ctx}", flush=True)
            all_results.append({"context": ctx, "status": "oom", "error": "server_failed_to_start"})
            kill_server(proc); break
        ctx_output = os.path.join(RESULTS_DIR, f"results_{name}_ctx{ctx}.json")
        run_bench(model_path, serve_name, ctx, ctx_output)
        if os.path.exists(ctx_output):
            with open(ctx_output) as f: ctx_data = json.load(f)
            ctx_results = ctx_data.get("results", [])
            if ctx_results and ctx_results[-1].get("status") == "success":
                last = ctx_results[-1]
                all_results.append(last)
                print(f"  [OK] VRAM={last.get('peak_vram_gb')}GB prefill={last.get('prefill_tok_s')}tok/s decode={last.get('decode_tok_s')}tok/s", flush=True)
            else:
                all_results.append({"context": ctx, "status": "oom", "error": ctx_results[-1].get("error","fail") if ctx_results else "no_results"})
                kill_server(proc); break
        else:
            all_results.append({"context": ctx, "status": "error", "error": "no_output"})
            kill_server(proc); break
        kill_server(proc); time.sleep(5)
    output = {"experiment": "longctx_infer_cost", "framework": "SGLang 0.5.9",
              "model_name": name, "model_path": model_path, "serve_name": serve_name,
              "gpu": f"H100-80GB #{GPU}", "gen_len": GEN_LEN,
              "contexts_tested": CONTEXTS, "results": all_results,
              "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(output_file, "w") as f: json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[done] {name}: {output_file}", flush=True)
    return output

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    global GPU, CONTEXTS
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=list(MODELS.keys()))
    ap.add_argument("--gpu", type=int, default=GPU)
    ap.add_argument("--contexts", type=int, nargs="+", default=CONTEXTS)
    args = ap.parse_args()
    GPU = args.gpu; CONTEXTS = args.contexts
    print(f"=== Long-Context Inference Cost Evaluation ===", flush=True)
    print(f"Models: {args.models}", flush=True)
    print(f"GPU: H100-80GB #{GPU}", flush=True)
    print(f"Contexts: {CONTEXTS}", flush=True)
    print(f"Start: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    all_outputs = {}
    for name in args.models:
        if name not in MODELS: print(f"[skip] Unknown: {name}"); continue
        all_outputs[name] = eval_model(name, MODELS[name])
    summary_file = os.path.join(RESULTS_DIR, "summary_all.json")
    with open(summary_file, "w") as f: json.dump(all_outputs, f, indent=2, ensure_ascii=False)
    print(f"\n=== ALL DONE ===\nSummary: {summary_file}\nEnd: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

if __name__ == "__main__":
    main()

