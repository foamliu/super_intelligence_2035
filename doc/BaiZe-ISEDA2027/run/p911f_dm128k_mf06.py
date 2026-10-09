#!/usr/bin/env python3
"""Standalone DM 128K mf=0.6 benchmark. Starts server with ctx=262144 (not 1M)."""
import json, os, signal, subprocess, sys, time, socket

RUN_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_DIR = os.path.join(RUN_DIR, "p911f_results")
os.makedirs(RESULT_DIR, exist_ok=True)

DM_PATH = os.path.join(RUN_DIR, "hf_checkpoints", "dense_matched_2.22b")
SGLANG_PY = "/nas_train/app.e0031982/miniforge3/envs/sglang/bin/python"
PORT = 30050
GPU_ID = 0
CTX_MAX = 262144  # 256K — enough for 128K testing, avoids KV pool OOM at mf=0.6

sys.path.insert(0, RUN_DIR)
from p911d_sglang_vram_bench import benchmark_cell

def start_server():
    cmd = [SGLANG_PY, "-m", "sglang.launch_server",
           "--model-path", DM_PATH, "--port", str(PORT), "--host", "127.0.0.1",
           "--tp", "1", "--mem-fraction-static", "0.6",
           "--attention-backend", "flashinfer", "--dtype", "bfloat16",
           "--context-length", str(CTX_MAX), "--disable-radix-cache",
           "--trust-remote-code", "--skip-server-warmup", "--log-level", "info"]
    env = os.environ.copy()
    env["SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN"] = "1"
    env["http_proxy"] = "http://172.19.92.25:13128"
    env["https_proxy"] = "http://172.19.92.25:13128"
    env["no_proxy"] = "localhost,127.0.0.1,0.0.0.0"
    env["NO_PROXY"] = "localhost,127.0.0.1,0.0.0.0"
    env["CUDA_VISIBLE_DEVICES"] = str(GPU_ID)
    lf = open(os.path.join(RESULT_DIR, f"srv_dm128k_gpu{GPU_ID}_mf0.6_ctx{CTX_MAX}.log"), "w")
    si = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, env=env)
    print(f"  [server] PID={si.pid} port={PORT} gpu={GPU_ID} ctx={CTX_MAX} mf=0.6", flush=True)
    return si

def wait_server(url, timeout=300):
    import requests
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"{url}/v1/models", timeout=10, proxies={"http": None, "https": None})
            if r.status_code == 200:
                print(f"  [server] healthy!", flush=True)
                return True
        except:
            pass
        time.sleep(3)
    return False

def kill_server(si):
    try:
        os.killpg(os.getpgid(si.pid), signal.SIGTERM)
    except:
        si.terminate()
    time.sleep(3)
    try:
        os.killpg(os.getpgid(si.pid), signal.SIGKILL)
    except:
        si.kill()

if __name__ == "__main__":
    si = start_server()
    try:
        base_url = f"http://127.0.0.1:{PORT}"
        if not wait_server(base_url):
            print("  [ERROR] server not healthy in 300s", flush=True)
            sys.exit(1)
        results = []
        for ctx, bs in [(131072, 1), (131072, 8)]:
            print(f"\n=== DM 2.229B | ctx={ctx} bs={bs} mf=0.6 (WARMUP=1, REPEATS=3) ===", flush=True)
            r = benchmark_cell(base_url, "default", DM_PATH, ctx, bs, 64, GPU_ID,
                               warmup=1, repeats=3)
            r["mem_frac"] = 0.6
            r["model_arch"] = "llama"
            r["ssm_dtype"] = "N/A"
            if r.get("prefill_tok_s") and bs > 0:
                r["prefill_tok_s_perB"] = round(r["prefill_tok_s"] / bs, 1)
            if r.get("decode_tok_s") and bs > 0:
                r["decode_tok_s_perB"] = round(r["decode_tok_s"] / bs, 1)
            of = os.path.join(RESULT_DIR, f"bench_dense_matched_2.229b_gpu{GPU_ID}_mf0.6_ctx{ctx}_bs{bs}.json")
            with open(of, "w") as f:
                json.dump(r, f, indent=2)
            print(f"  Saved to {of}", flush=True)
            print(f"  prefill={r.get('prefill_tok_s')} decode={r.get('decode_tok_s')} "
                  f"vram={r.get('peak_vram_gb')} tct={r.get('total_completion_tokens')} "
                  f"error={r.get('error')}", flush=True)
            results.append(r)
            time.sleep(2)
        # Save combined
        combined = {"model": "dense_matched_2.229b", "mem_frac": 0.6, "results": results}
        cf = os.path.join(RESULT_DIR, "dm128k_mf06_combined.json")
        with open(cf, "w") as f:
            json.dump(combined, f, indent=2)
        print(f"\n=== ALL DONE. Combined: {cf} ===", flush=True)
    finally:
        kill_server(si)
