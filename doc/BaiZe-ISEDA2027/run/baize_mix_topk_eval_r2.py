#!/usr/bin/env python3
"""BaiZe BO Round 2 top-K收尾: retrain top-5, full lm_eval, Spearman, save results.

1. Load top-5 from mix_search_eval_r2.db (ORDER BY score DESC)
2. Retrain each with same R2 params (MBS=16, 15258 steps, D=0.5B) + save ckpt
3. Convert ckpt to HF (baize_p6_ckpt_to_hf.py)
4. Run FULL lm_eval (8 T2 tasks, NO --limit) on each
5. Compute Spearman between BO score and full lm_eval avg
6. Save results to topk_lmeval_results_r2.json
"""
import argparse, json, os, random, re, sqlite3, subprocess, sys, time, glob, shutil
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import numpy as np
from scipy.stats import spearmanr

BASE = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027"
PY = "/nas_train/app.e0031982/miniforge3/envs/py310/bin"
TOKENIZER = f"{BASE}/data/tokenizer_eod"
HELDOUT = f"{BASE}/data/heldout"
DATA = f"{BASE}/data"
EXP_DIR = f"{BASE}/nemo_experiments/mix_search"
RUN_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
DB_PATH = f"{EXP_DIR}/mix_search_eval_r2.db"
GBS = 16
SEQ = 2048
MBS = 16
LR = 3e-3
SEED = 1234
D_TOKENS = 0.5e9
T2_TASKS = "arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande"
TASK_METRICS = {
    "arc_challenge": "acc_norm,none", "arc_easy": "acc_norm,none",
    "boolq": "acc,none", "hellaswag": "acc_norm,none",
    "openbookqa": "acc_norm,none", "piqa": "acc_norm,none",
    "sciq": "acc_norm,none", "winogrande": "acc,none",
}
SP = {
    "base": f"{DATA}/mix_base/mix_base_train_s0",
    "code": f"{DATA}/anneal_code",
    "math": f"{DATA}/anneal_math2",
}
VALID_BLEND_EVAL = f"1 {HELDOUT}/held_out_eval"

def build_blend(web, code):
    math_r = max(1.0 - web - code, 0.01)
    return f"{web:.6f} {SP['base']} {code:.6f} {SP['code']} {math_r:.6f} {SP['math']}"

def load_topk(db_path, k=5):
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT id, params, score, lm_eval_detail FROM trials "
        "WHERE status='complete' ORDER BY score DESC LIMIT ?", (k,)).fetchall()
    conn.close()
    trials = []
    for r in rows:
        p = json.loads(r[1])
        detail = json.loads(r[3]) if r[3] else {}
        trials.append({
            "id": r[0], "web": p["web"], "code": p["code"],
            "math": max(1 - p["web"] - p["code"], 0.01),
            "bo_score": r[2], "bo_detail": detail,
        })
    return trials

def run_retrain(trial, gpu_id, train_iters, warmup, decay_iters):
    tid = trial["id"]
    name = f"r2_topk_t{tid:04d}_gpu{gpu_id}"
    log_path = f"/tmp/mix_topk_r2_{name}.log"
    port = random.randint(20000, 60000)
    blend = build_blend(trial["web"], trial["code"])
    ckpt_dir = f"{EXP_DIR}/{name}/checkpoints"
    if os.path.isdir(ckpt_dir):
        ckpts = sorted(glob.glob(os.path.join(ckpt_dir, "iter_*")))
        if ckpts:
            print(f"[{name}] skip retrain (ckpt exists: {ckpts[-1]})")
            return name, "skip", ckpts[-1]
    cmd = [
        f"{PY}/torchrun", "--nnodes=1", "--nproc_per_node=1",
        "--master_addr=127.0.0.1", "--master_port", str(port),
        f"{BASE}/pretrain_proxy_launcher.py",
        "--proxy-size", "d128",
        "--name", name, "--dir", EXP_DIR,
        "--tokenizer-path", TOKENIZER,
        "--train-data-path", *blend.split(),
        "--valid-data-path", *VALID_BLEND_EVAL.split(),
        "--tensor-parallel", "1",
        "--train-iters", str(train_iters),
        "--global-batch-size", str(GBS),
        "--micro-batch-size", str(MBS),
        "--seq-length", str(SEQ),
        "--eval-interval", str(max(train_iters // 5, 100)),
        "--eval-iters", "10",
        "--save-interval", str(train_iters),
        "--lr", str(LR), "--min-lr", "1e-5",
        "--lr-warmup-iters", str(warmup),
        "--lr-decay-iters", str(decay_iters),
        "--lr-decay-style", "WSD",
        "--seed", str(SEED), "--precision", "bf16_mixed",
    ]
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    env["PYTHONPATH"] = "/nas_train/app.e0031982/omegaconf_230"
    print(f"[{name}] GPU{gpu_id} training {train_iters} steps MBS={MBS} "
          f"web={trial['web']:.4f} code={trial['code']:.4f}")
    with open(log_path, "w") as f:
        proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
    while proc.poll() is None:
        time.sleep(10)
    rc = proc.wait()
    ckpt = None
    if os.path.isdir(ckpt_dir):
        ckpts = sorted(glob.glob(os.path.join(ckpt_dir, "iter_*")))
        if ckpts:
            ckpt = ckpts[-1]
    print(f"[{name}] rc={rc} ckpt={ckpt}")
    return name, ("ok" if rc == 0 and ckpt else f"fail(rc={rc})"), ckpt

def ckpt_to_hf(name, ckpt_path, gpu_id):
    hf_out = f"{EXP_DIR}/{name}/hf_model"
    if os.path.exists(os.path.join(hf_out, "config.json")):
        print(f"[{name}] HF model exists, skip conversion")
        return hf_out
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    env["PYTHONPATH"] = "/nas_train/app.e0031982/omegaconf_230"
    env["MASTER_ADDR"] = "127.0.0.1"
    env["MASTER_PORT"] = str(random.randint(20000, 60000))
    cmd = [f"{PY}/python", f"{RUN_DIR}/baize_p6_ckpt_to_hf.py",
           "--ckpt", ckpt_path, "--tokenizer", TOKENIZER, "--out", hf_out]
    print(f"[{name}] Converting ckpt -> HF on GPU{gpu_id}")
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"[{name}] HF CONV FAILED: {r.stderr[-500:]}")
        return None
    return hf_out

def run_full_lmeval(hf_path, gpu_id, name):
    eval_out = f"{EXP_DIR}/{name}/lm_eval_results_full"
    os.makedirs(eval_out, exist_ok=True)
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{BASE}/p6_tf5:{pp}"
    env["HF_DATASETS_CACHE"] = "/nas_train/app.e0031982/hf_cache"
    env["HF_HOME"] = "/nas_train/app.e0031982/.cache"
    env["HF_ENDPOINT"] = "https://hf-mirror.com"
    env["HF_HUB_OFFLINE"] = "1"
    env["HF_DATASETS_OFFLINE"] = "1"
    env["https_proxy"] = "http://172.19.92.25:13128"
    env["http_proxy"] = "http://172.19.92.25:13128"
    env["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    log_file = f"{eval_out}/eval_full.log"
    cmd = [f"{PY}/python", "-m", "lm_eval", "--model", "hf",
           "--model_args", f"pretrained={hf_path},dtype=bfloat16,trust_remote_code=False",
           "--tasks", T2_TASKS, "--num_fewshot", "0", "--batch_size", "4",
           "--output_path", eval_out]
    print(f"[{name}] Full lm_eval on GPU{gpu_id} (8 tasks, no limit)")
    with open(log_file, "w") as f:
        r = subprocess.run(cmd, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=3600)
    return r.returncode == 0

def collect_scores(name):
    eval_out = f"{EXP_DIR}/{name}/lm_eval_results_full"
    result_files = glob.glob(os.path.join(eval_out, "**", "results*.json"), recursive=True) + \
                   glob.glob(os.path.join(eval_out, "results*.json"))
    if not result_files:
        return None
    with open(sorted(result_files)[-1]) as f:
        data = json.load(f)
    scores = {}
    for task, metrics in data.get("results", {}).items():
        if task in TASK_METRICS:
            val = metrics.get(TASK_METRICS[task])
            if val is None:
                val = metrics.get("acc,none")
            if val is not None:
                scores[task] = float(val)
    avg = float(np.mean(list(scores.values()))) if scores else None
    return {"per_task": scores, "avg": avg}

def find_arm_name(tid):
    for d in os.listdir(EXP_DIR):
        if d.startswith(f"r2_topk_t{tid:04d}"):
            return d
    return None

def main():
    p = argparse.ArgumentParser(description="R2 top-K收尾")
    p.add_argument("--gpus", default="2,3,4,5,6")
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--mode", choices=["all", "retrain", "eval", "analyze"], default="all")
    args = p.parse_args()
    gpu_list = [int(g) for g in args.gpus.split(",")]
    train_iters = int(D_TOKENS / (GBS * SEQ))
    warmup = max(int(train_iters * 0.10), 50)
    decay_iters = int(train_iters * 0.90)
    print(f"{'='*60}")
    print(f"R2 top-K收尾 (k={args.k}, GPUs={args.gpus})")
    print(f"  train_iters={train_iters}, warmup={warmup}, decay={decay_iters}")
    print(f"  MBS={MBS}, GBS={GBS}, SEQ={SEQ}, LR={LR}")
    print(f"{'='*60}")
    trials = load_topk(DB_PATH, k=args.k)
    print(f"\nTop-{args.k} from DB (score DESC = best):")
    for t in trials:
        print(f"  t{t['id']}: bo_score={t['bo_score']:.4f} "
              f"web={t['web']:.4f} code={t['code']:.4f} math={t['math']:.4f}")
    if args.mode in ("all", "retrain"):
        gpu_q = Queue()
        for g in gpu_list:
            gpu_q.put(g)
        retrain_results = {}
        def retrain_worker(trial):
            gpu = gpu_q.get()
            try:
                name, status, ckpt = run_retrain(trial, gpu, train_iters, warmup, decay_iters)
                retrain_results[trial["id"]] = {"name": name, "status": status, "ckpt": ckpt}
            finally:
                gpu_q.put(gpu)
        with ThreadPoolExecutor(max_workers=len(gpu_list)) as pool:
            futures = [pool.submit(retrain_worker, t) for t in trials]
            for f in futures:
                f.result()
        print(f"\nRetrain results:")
        for tid, r in retrain_results.items():
            print(f"  t{tid}: {r['name']} {r['status']} ckpt={r['ckpt']}")
    if args.mode in ("all", "eval"):
        gpu_q = Queue()
        for g in gpu_list:
            gpu_q.put(g)
        eval_results = {}
        def eval_worker(trial):
            gpu = gpu_q.get()
            try:
                tid = trial["id"]
                name = find_arm_name(tid)
                if not name:
                    print(f"  t{tid}: no arm directory found")
                    return
                ckpt_dir = f"{EXP_DIR}/{name}/checkpoints"
                ckpts = sorted(glob.glob(os.path.join(ckpt_dir, "iter_*"))) if os.path.isdir(ckpt_dir) else []
                if not ckpts:
                    print(f"  t{tid}: no checkpoint in {name}")
                    return
                hf = ckpt_to_hf(name, ckpts[-1], gpu)
                if not hf:
                    return
                ok = run_full_lmeval(hf, gpu, name)
                if ok:
                    sc = collect_scores(name)
                    if sc:
                        eval_results[tid] = sc
                        print(f"  t{tid}: full_avg={sc['avg']:.4f} "
                              f"bo_score={trial['bo_score']:.4f} ({len(sc['per_task'])} tasks)")
                    else:
                        print(f"  t{tid}: lm_eval ok but no scores")
                else:
                    print(f"  t{tid}: lm_eval FAILED")
            finally:
                gpu_q.put(gpu)
        with ThreadPoolExecutor(max_workers=len(gpu_list)) as pool:
            futures = [pool.submit(eval_worker, t) for t in trials]
            for f in futures:
                f.result()
        out = {
            "trials": [
                {"id": t["id"], "web": t["web"], "code": t["code"], "math": t["math"],
                 "bo_score": t["bo_score"], "bo_detail": t["bo_detail"],
                 "full_eval": eval_results.get(t["id"])}
                for t in trials
            ],
        }
        out_path = f"{RUN_DIR}/topk_lmeval_results_r2.json"
        with open(out_path, "w") as f:
            json.dump(out, f, indent=2)
        print(f"\nResults saved to {out_path}")
    if args.mode in ("all", "analyze"):
        out_path = f"{RUN_DIR}/topk_lmeval_results_r2.json"
        if not os.path.exists(out_path):
            print("No results file. Run --mode eval first.")
            return
        with open(out_path) as f:
            data = json.load(f)
        bo_scores, full_avgs = [], []
        print(f"\n{'='*60}")
        print(f"Spearman analysis (BO score vs full lm_eval avg):")
        for t in data["trials"]:
            fe = t.get("full_eval")
            if fe and fe.get("avg") is not None:
                bo_scores.append(t["bo_score"])
                full_avgs.append(fe["avg"])
                print(f"  t{t['id']}: bo_score={t['bo_score']:.4f} "
                      f"full_avg={fe['avg']:.4f} delta={fe['avg'] - t['bo_score']:+.4f}")
        if len(bo_scores) >= 3:
            rho, pval = spearmanr(bo_scores, full_avgs)
            print(f"\n  Spearman rho={rho:.4f} p={pval:.4f} (n={len(bo_scores)})")
            print(f"  Pearson r={np.corrcoef(bo_scores, full_avgs)[0,1]:.4f}")
        else:
            print(f"  Not enough data (n={len(bo_scores)})")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
