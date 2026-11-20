#!/usr/bin/env python3
"""P-9.11-F: Param-matched Dense vs BaiZe-Hybrid SGLang benchmark runner.

Orchestrates: 3 models × 7 ctx (128K→8M ×2) × 2 mem-frac (0.6,0.85) × 2 bs (1,8)
WARMUP=1, REPEATS=3 (median)

Usage:
  python p911f_bench_runner.py --phase verify   # 128K only, both models, mf=0.6
  python p911f_bench_runner.py --phase full      # full matrix
"""
import argparse, json, os, signal, subprocess, sys, time, socket

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_DIR = os.path.join(RUN_DIR, "p911f_results")
os.makedirs(RESULT_DIR, exist_ok=True)

HYBRID_PATH = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p3_hybrid/hf_iter_5000"
DENSE_MATCHED_PATH = os.path.join(RUN_DIR, "hf_checkpoints", "dense_matched_2.22b")
DENSE_REF_PATH = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p3_dense/hf_iter_5000"

MODELS = {
    "hybrid_2.220b": {"path": HYBRID_PATH, "arch": "nemotron_h",
                      "ssm_dtype": "float32", "extra_flags": ["--mamba-ssm-dtype","float32","--disable-cuda-graph"],
                      "ctx_max": 8388608},   # 8M — hybrid can handle this (SSM layers have no KV)
    "dense_matched_2.229b": {"path": DENSE_MATCHED_PATH, "arch": "llama",
                             "ssm_dtype": None, "extra_flags": [],
                             "ctx_max": 1048576},  # 1M — dense 36L×2kv uses ~36KB/tok
    "dense_ref_2.512b": {"path": DENSE_REF_PATH, "arch": "llama",
                         "ssm_dtype": None, "extra_flags": [],
                         "ctx_max": 524288},   # 512K — 42L×4kv even more KV per token
}

def find_free_port(start=30000, end=30020):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try: s.bind(("127.0.0.1", port)); return port
            except OSError: continue
    raise RuntimeError("No free port")

def wait_for_server(url, timeout=600):
    import requests
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{url}/v1/models", timeout=10, proxies={"http": None, "https": None})
            if r.status_code == 200:
                ids = [m["id"] for m in r.json().get("data", [])]
                print(f"  [server] healthy, models={ids}", flush=True); return True
        except: pass
        time.sleep(3)
    return False

def start_sglang_server(model_key, gpu_id, mem_frac, ctx_max, port):
    mi = MODELS[model_key]; mp = mi["path"]
    if not os.path.exists(os.path.join(mp, "config.json")):
        print(f"  [ERROR] model not found: {mp}", flush=True); return None
    cmd = ["/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python", "-m", "sglang.launch_server",
           "--model-path", mp, "--port", str(port), "--host", "127.0.0.1",
           "--tp", "1",
           "--mem-fraction-static", str(mem_frac),
           "--attention-backend", "flashinfer", "--dtype", "bfloat16",
           "--context-length", str(ctx_max), "--disable-radix-cache",
           "--trust-remote-code", "--skip-server-warmup", "--log-level", "info"] + mi.get("extra_flags", [])
    env = os.environ.copy()
    env["SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN"] = "1"
    env["http_proxy"] = "http://172.19.92.25:13128"
    env["https_proxy"] = "http://172.19.92.25:13128"
    env["no_proxy"] = "localhost,127.0.0.1,0.0.0.0"
    env["NO_PROXY"] = "localhost,127.0.0.1,0.0.0.0"
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    lf = os.path.join(RESULT_DIR, f"srv_{model_key}_gpu{gpu_id}_mf{mem_frac}_ctx{ctx_max}.log")
    print(f"  [server] starting gpu={gpu_id} mf={mem_frac} ctx={ctx_max} port={port}", flush=True)
    proc = subprocess.Popen(cmd, env=env, stdout=open(lf,"w"), stderr=subprocess.STDOUT, preexec_fn=os.setsid)
    url = f"http://127.0.0.1:{port}"
    if not wait_for_server(url, timeout=300):
        print(f"  [server] FAILED. Log: {lf}", flush=True); kill_server(proc); return None
    return proc, url, lf

def kill_server(pi):
    if pi is None: return
    proc = pi[0] if isinstance(pi, tuple) else pi
    try: os.killpg(os.getpgid(proc.pid), signal.SIGTERM); proc.wait(timeout=30)
    except:
        try: os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except: pass
    time.sleep(5)

def benchmark_model(model_key, gpu_id, mem_frac, contexts, batches, ctx_max, warmup=1, repeats=3, port_base=30000):
    mi = MODELS[model_key]
    port = find_free_port(start=port_base, end=port_base+20)
    eff_ctx_max = mi.get("ctx_max", ctx_max)  # use model-specific limit if set
    si = start_sglang_server(model_key, gpu_id, mem_frac, eff_ctx_max, port)
    if si is None:
        return {"model": model_key, "mem_frac": mem_frac, "error": "server_failed", "results": []}
    proc, base_url, lf = si; results = []; oom = False
    try:
        for ctx in contexts:
            if oom: break
            if ctx > eff_ctx_max:
                print(f"\n  [SKIP] ctx={ctx} > model ctx_max={eff_ctx_max} — stopping", flush=True)
                break
            if mi["arch"] == "llama":  # dense models (Llama arch)
                eff_batches = [b for b in batches if ctx < 524288 or b == 1]  # dense: skip bs=8 for ctx>=512K (KV cache can't fit 4M tokens)
            else:  # hybrid models (Nemotron-H arch)
                eff_batches = [b for b in batches if ctx < 1048576 or b == 1]  # hybrid: skip bs=8 for ctx>=1M (SSM scan too slow)
            eff_repeats = repeats if ctx <= 1048576 else 1  # reduce repeats for ctx>1M
            for bs in eff_batches:
                print(f"\n  === {model_key} | ctx={ctx} bs={bs} mf={mem_frac} (repeats={eff_repeats}) ===", flush=True)
                sys.path.insert(0, RUN_DIR)
                from p911d_sglang_vram_bench import benchmark_cell
                r = benchmark_cell(base_url, "default", mi["path"], ctx, bs, 64, gpu_id, warmup=warmup, repeats=eff_repeats)
                r["mem_frac"] = mem_frac; r["model_arch"] = mi["arch"]; r["ssm_dtype"] = mi.get("ssm_dtype","N/A")
                if r.get("prefill_tok_s") and bs>0: r["prefill_tok_s_perB"] = round(r["prefill_tok_s"]/bs,1)
                if r.get("decode_tok_s") and bs>0: r["decode_tok_s_perB"] = round(r["decode_tok_s"]/bs,1)
                results.append(r)
                of = os.path.join(RESULT_DIR, f"bench_{model_key}_gpu{gpu_id}_mf{mem_frac}_ctx{ctx}_bs{bs}.json")
                with open(of,"w") as f: json.dump(r, f, indent=2)
                if r.get("error") and any(k in str(r["error"]).lower() for k in ("memory","oom","timeout","timed out","too long","exceeds","rejected","server_rejected")):
                    print(f"  [STOP] {r['error'][:100]} at ctx={ctx} — stopping higher ctx", flush=True); oom = True; break
                time.sleep(2)
    finally:
        kill_server(si)
    return {"model": model_key, "mem_frac": mem_frac, "results": results}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["verify","full","hybrid_only","dense_only"], default="verify")
    ap.add_argument("--gpu-id", type=int, default=0)
    ap.add_argument("--ctx-start", type=int, default=131072)
    ap.add_argument("--warmup", type=int, default=1)
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--mem-fracs", type=float, nargs="+", default=[0.6,0.85])
    ap.add_argument("--models", nargs="+", default=list(MODELS.keys()))
    ap.add_argument("--ctx-max", type=int, default=8388608)
    ap.add_argument("--port-base", type=int, default=30000, help="port range start (use 30000+gpu*100 for parallel runs)")
    args = ap.parse_args()
    ALL_CTXS = [131072,262144,524288,1048576,2097152,4194304,8388608]
    ALL_BATCHES = [1,8]
    if args.phase == "verify":
        contexts=[131072]; batches=[1,8]; mem_fracs=[0.6]; models=args.models; ctx_max=262144
    else:
        contexts=[c for c in ALL_CTXS if c>=args.ctx_start]; batches=ALL_BATCHES
        mem_fracs=args.mem_fracs; ctx_max=args.ctx_max
        if args.phase == "hybrid_only":
            models = ["hybrid_2.220b"]
        elif args.phase == "dense_only":
            models = [k for k in args.models if "dense" in k]
        else:  # full
            models = args.models
    print(f"=== P-9.11-F Benchmark Runner ===")
    print(f"  Phase={args.phase} Models={models} Ctxs={contexts} BS={batches} MF={mem_fracs}")
    print(f"  WARMUP={args.warmup} REPEATS={args.repeats} GPU={args.gpu_id} ctx_max={ctx_max}\n")
    all_results = []
    for mk in models:
        for mf in mem_fracs:
            print(f"\n{'='*60}\n  MODEL: {mk} | MF: {mf}\n{'='*60}")
            res = benchmark_model(mk, args.gpu_id, mf, contexts, batches, ctx_max, warmup=args.warmup, repeats=args.repeats, port_base=args.port_base)
            all_results.append(res)
            cf = os.path.join(RESULT_DIR, f"combined_{mk}_mf{mf}.json")
            with open(cf,"w") as f: json.dump(res, f, indent=2)
            print(f"\n  Saved to {cf}")
    sf = os.path.join(RESULT_DIR, f"summary_{args.phase}_{int(time.time())}.json")
    with open(sf,"w") as f: json.dump({"phase":args.phase,"warmup":args.warmup,"repeats":args.repeats,
        "models":models,"contexts":contexts,"batches":batches,"mem_fracs":mem_fracs,"results":all_results}, f, indent=2)
    print(f"\n=== DONE === Summary: {sf}")

if __name__ == "__main__":
    main()
