#!/usr/bin/env python3
"""s_step attribution profiling for BaiZe data-mix BO proxy model.

Hypothesis: MBS=1 + GBS=16 => 16 microbatches/step, each with ~94ms overhead => ~1.5s/step.
By increasing MBS (reducing microbatch count), we eliminate gradient-accumulation overhead.

Usage (on .29): CUDA_VISIBLE_DEVICES=1 python baize_sstep_profile.py --gpus 1
"""
import argparse, json, os, re, subprocess, sys, time

BASE = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027"
PY = "/nas_train/app.e0031982/miniforge3/envs/py310/bin"
TOKENIZER = f"{BASE}/data/tokenizer_eod"
DATA = f"{BASE}/data"
EXP_DIR = f"{BASE}/nemo_experiments/sstep_profile"
HELDOUT = f"{BASE}/data/heldout"

GBS = 16
SEQ = 2048
LR = 3e-3
SEED = 1234
TRAIN_ITERS = 50  # 10 warmup + 40 measured (log every 10 => 5 data points)
WARMUP = 10
DECAY = 40

BLEND_88_8_4 = f"88 {DATA}/mix_base/mix_base_train_s0 8 {DATA}/anneal_code 4 {DATA}/anneal_math2"
VALID_BLEND = f"1 {HELDOUT}/held_out_eval"

ELAPSED_RE = re.compile(r"elapsed time per iteration \(ms\):\s*([\d.]+)")
MEM_RE = re.compile(r"max allocated:\s*([\d.]+)")

def median(values):
    if not values:
        return None
    s = sorted(values)
    n = len(s)
    return s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2

def run_mbs(mbs, gpu_id, label=""):
    name = f"sstep_mbs{mbs}_{label}"
    log_path = f"/tmp/sstep_{name}.log"
    port = 31000 + mbs
    cmd = [
        f"{PY}/torchrun", "--nnodes=1", "--nproc_per_node=1",
        "--master_addr=127.0.0.1", "--master_port", str(port),
        f"{BASE}/pretrain_proxy_launcher.py",
        "--proxy-size", "d128", "--name", name, "--dir", EXP_DIR,
        "--tokenizer-path", TOKENIZER,
        "--train-data-path", *BLEND_88_8_4.split(),
        "--valid-data-path", *VALID_BLEND.split(),
        "--tensor-parallel", "1", "--train-iters", str(TRAIN_ITERS),
        "--global-batch-size", str(GBS), "--micro-batch-size", str(mbs),
        "--seq-length", str(SEQ), "--eval-interval", "999", "--eval-iters", "1",
        "--save-interval", "0", "--lr", str(LR), "--min-lr", "1e-5",
        "--lr-warmup-iters", str(WARMUP), "--lr-decay-iters", str(DECAY),
        "--lr-decay-style", "WSD", "--seed", str(SEED), "--precision", "bf16_mixed",
    ]
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    env["PYTHONPATH"] = "/nas_train/app.e0031982/omegaconf_230"
    print(f"\n{'='*60}")
    print(f"  MBS={mbs} (microbatches/step = {GBS//mbs}) on GPU{gpu_id}")
    print(f"{'='*60}")
    t0 = time.time()
    with open(log_path, "w") as f:
        proc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, env=env, timeout=300)
    elapsed = time.time() - t0
    print(f"  Wall time: {elapsed:.1f}s (exit code {proc.returncode})")
    timings = []
    peak_mem = None
    with open(log_path) as f:
        for line in f:
            m = ELAPSED_RE.search(line)
            if m:
                step_match = re.search(r"iteration\s+(\d+)/", line)
                step = int(step_match.group(1)) if step_match else 0
                ms = float(m.group(1))
                timings.append((step, ms))
                print(f"  step {step:3d}: {ms:.1f} ms/iter")
            m2 = MEM_RE.search(line)
            if m2 and peak_mem is None:
                peak_mem = float(m2.group(1))
    ckpt_dir = f"{EXP_DIR}/{name}"
    if os.path.exists(ckpt_dir):
        import shutil
        shutil.rmtree(ckpt_dir, ignore_errors=True)
    return timings, peak_mem

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gpus", type=int, default=1, help="GPU id to use")
    p.add_argument("--mbs-list", type=str, default="1,4,8,16",
                   help="comma-separated MBS values to test")
    args = p.parse_args()
    mbs_values = [int(x) for x in args.mbs_list.split(",")]
    gpu_id = args.gpus
    print("s_step profiling: GBS=%d, seq=%d, iters=%d" % (GBS, SEQ, TRAIN_ITERS))
    print("GPU=%d, MBS values=%s" % (gpu_id, mbs_values))
    print("Data blend: 88:8:4 (base:code:math)")
    results = {}
    for mbs in mbs_values:
        n_microbatches = GBS // mbs
        timings, peak_mem = run_mbs(mbs, gpu_id)
        measured = [ms for step, ms in timings if step > WARMUP]
        if not measured:
            measured = [ms for step, ms in timings]
        med = median(measured)
        tok_per_s = (GBS * SEQ / (med / 1000)) if med else None
        results[mbs] = {"n_microbatches": n_microbatches, "timings_ms": timings,
                        "measured_ms": measured, "median_ms": med,
                        "tok_per_s": tok_per_s, "peak_mem_mb": peak_mem}
        if med:
            print("  => MBS=%d: median=%.1fms, tok/s=%.0f" % (mbs, med, tok_per_s))
        else:
            print("  => MBS=%d: FAILED" % mbs)
    print("\n" + "=" * 70)
    print("  SUMMARY: s_step attribution (GBS=%d, seq=%d)" % (GBS, SEQ))
    print("=" * 70)
    print("  %4s %10s %10s %10s %12s %8s" % ("MBS", "microbatch", "median_ms", "tok/s", "peak_mem_MB", "speedup"))
    print("  %4s %10s %10s %10s %12s %8s" % ("----", "----------", "----------", "----------", "------------", "--------"))
    baseline = results.get(1, {}).get("median_ms")
    for mbs in mbs_values:
        r = results[mbs]
        med = r["median_ms"]
        speedup = "%.1fx" % (baseline / med) if (baseline and med) else "-"
        mem = "%.0f" % r["peak_mem_mb"] if r["peak_mem"] else "?"
        print("  %4d %10d %10.1f %10.0f %12s %8s" % (mbs, r["n_microbatches"], med, r["tok_per_s"], mem, speedup))
    print("\n  D projection (6 GPU, 24h, GBS=%d, seq=%d):" % (GBS, SEQ))
    for mbs in mbs_values:
        r = results[mbs]
        med = r["median_ms"]
        if med:
            steps_per_trial = 500
            trial_time_s = steps_per_trial * med / 1000
            trials_per_gpu_24h = int(24 * 3600 / trial_time_s)
            total_trials_6gpu = trials_per_gpu_24h * 6
            D_per_trial = steps_per_trial * GBS * SEQ
            D_total = total_trials_6gpu * D_per_trial
            print("    MBS=%d: %.0fms/step => %.1fs/trial => %d trials/24h => D=%.2fB tokens" %
                  (mbs, med, trial_time_s, total_trials_6gpu, D_total / 1e9))
    out_path = "%s/sstep_profile_results.json" % EXP_DIR
    os.makedirs(EXP_DIR, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("\n  Results saved to %s" % out_path)

if __name__ == "__main__":
    main()
