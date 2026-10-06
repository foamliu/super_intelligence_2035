#!/usr/bin/env python3
"""Run lm_eval on top-K retrained checkpoints, compute Spearman + noise."""
import argparse, json, os, subprocess, sys, time, glob
import sqlite3
from scipy.stats import spearmanr
import numpy as np

BASE = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027"
PY = "/nas_train/app.e0031982/miniforge3/envs/py310/bin"
RUN = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
EXP_DIR = BASE + "/nemo_experiments/mix_search"
DB_PATH = EXP_DIR + "/mix_search_eval.db"
T2_TASKS = "arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande"
TRIAL_IDS = [182, 198, 155, 149, 96, 79]

def find_ckpt(name):
    ckpt_dir = EXP_DIR + "/" + name + "/checkpoints"
    if not os.path.exists(ckpt_dir):
        return None
    iters = sorted([d for d in os.listdir(ckpt_dir) if d.startswith("iter_")])
    return iters[-1] if iters else None

def find_arm_name(tid):
    for d in os.listdir(EXP_DIR):
        if d.startswith("topk_t" + str(tid).zfill(4)):
            return d
    return None

def ckpt_to_hf(arm_name, ckpt_name):
    exp = EXP_DIR + "/" + arm_name
    hf_out = exp + "/hf_model"
    if os.path.exists(hf_out + "/config.json"):
        return hf_out
    ckpt = exp + "/checkpoints/" + ckpt_name
    cmd = [PY + "/python", RUN + "/baize_p6_ckpt_to_hf.py",
           "--ckpt", ckpt, "--tokenizer", BASE + "/data/tokenizer_eod", "--out", hf_out]
    env = os.environ.copy()
    env["PYTHONPATH"] = "/nas_train/app.e0031982/omegaconf_230"
    print("  Converting ckpt -> HF: " + arm_name + "/" + ckpt_name)
    r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print("  ERROR: " + r.stderr[-500:])
        return None
    return hf_out

def run_lmeval(hf_path, gpu_id, arm_name):
    eval_out = EXP_DIR + "/" + arm_name + "/lm_eval_results"
    os.makedirs(eval_out, exist_ok=True)
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    pp = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = BASE + "/p6_tf5:" + pp
    env["HF_DATASETS_CACHE"] = "/nas_train/app.e0031982/hf_cache"
    env["HF_HOME"] = "/nas_train/app.e0031982/.cache"
    env["HF_ENDPOINT"] = "https://hf-mirror.com"
    env["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    log_file = eval_out + "/eval_t2.log"
    cmd = [PY + "/python", "-m", "lm_eval", "--model", "hf",
           "--model_args", "pretrained=" + hf_path + ",dtype=bfloat16,trust_remote_code=False",
           "--tasks", T2_TASKS, "--num_fewshot", "0", "--batch_size", "4",
           "--output_path", eval_out]
    print("  lm_eval on GPU" + str(gpu_id) + ": " + arm_name)
    with open(log_file, "w") as f:
        r = subprocess.run(cmd, env=env, stdout=f, stderr=subprocess.STDOUT, timeout=3600)
    return r.returncode == 0

def collect_scores(arm_name):
    eval_out = EXP_DIR + "/" + arm_name + "/lm_eval_results"
    result_files = glob.glob(eval_out + "/**/results*.json", recursive=True) + \
                   glob.glob(eval_out + "/results*.json")
    if not result_files:
        return None
    with open(sorted(result_files)[-1]) as f:
        data = json.load(f)
    scores = {}
    for task, val in data.get("results", {}).items():
        for metric, v in val.items():
            if isinstance(metric, str) and ("acc" in metric or "acc_norm" in metric):
                scores.setdefault(task, {})[metric] = v
    task_scores = {}
    for task, metrics in scores.items():
        if "acc_norm,none" in metrics:
            task_scores[task] = metrics["acc_norm,none"]
        elif "acc,none" in metrics:
            task_scores[task] = metrics["acc,none"]
        elif "acc" in metrics:
            task_scores[task] = metrics["acc"]
    avg = np.mean(list(task_scores.values())) if task_scores else None
    return {"per_task": task_scores, "avg": float(avg) if avg is not None else None}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gpus", default="2,3,4,5,6,7")
    p.add_argument("--mode", choices=["eval", "analyze", "all"], default="all")
    args = p.parse_args()
    gpu_list = [int(g) for g in args.gpus.split(",")]
    conn = sqlite3.connect(DB_PATH)
    bo_losses = {}
    for tid in TRIAL_IDS:
        r = conn.execute("SELECT loss FROM trials WHERE id=?", (tid,)).fetchone()
        if r:
            bo_losses[tid] = r[0]
    conn.close()
    if args.mode in ["eval", "all"]:
        from concurrent.futures import ThreadPoolExecutor
        from queue import Queue
        gpu_q = Queue()
        for g in gpu_list:
            gpu_q.put(g)
        results = {}
        def worker(tid):
            arm = find_arm_name(tid)
            if not arm:
                print("  #" + str(tid) + ": no arm directory found")
                return
            ckpt = find_ckpt(arm)
            if not ckpt:
                print("  #" + str(tid) + ": no checkpoint in " + arm)
                return
            gpu = gpu_q.get()
            try:
                hf = ckpt_to_hf(arm, ckpt)
                if not hf:
                    return
                ok = run_lmeval(hf, gpu, arm)
                if ok:
                    sc = collect_scores(arm)
                    if sc:
                        results[tid] = sc
                        print("  #" + str(tid) + ": avg=" + str(round(sc["avg"], 4)) + " (" + str(len(sc["per_task"])) + " tasks)")
                    else:
                        print("  #" + str(tid) + ": lm_eval ok but no scores collected")
                else:
                    print("  #" + str(tid) + ": lm_eval FAILED")
            finally:
                gpu_q.put(gpu)
        with ThreadPoolExecutor(max_workers=len(gpu_list)) as pool:
            futures = [pool.submit(worker, tid) for tid in TRIAL_IDS]
            for f in futures:
                f.result()
        out_path = RUN + "/topk_lmeval_results.json"
        with open(out_path, "w") as f:
            json.dump({"results": {str(k): v for k, v in results.items()},
                       "bo_losses": {str(k): v for k, v in bo_losses.items()}}, f, indent=2)
        print("Results saved to " + out_path)
    if args.mode in ["analyze", "all"]:
        out_path = RUN + "/topk_lmeval_results.json"
        if not os.path.exists(out_path):
            print("No results file found. Run --mode eval first.")
            return
        with open(out_path) as f:
            data = json.load(f)
        results = data.get("results", {})
        bo_losses = data.get("bo_losses", {})
        tids = [int(t) for t in results.keys() if int(t) in bo_losses]
        if len(tids) >= 3:
            losses = [bo_losses[str(t)] for t in tids]
            avgs = [results[str(t)]["avg"] for t in tids]
            rho, pval = spearmanr(losses, avgs)
            print("Spearman: n=" + str(len(tids)) + " rho=" + str(round(rho, 4)) + " p=" + str(round(pval, 4)))
            for t in tids:
                print("  #" + str(t) + " BO_loss=" + str(round(bo_losses[str(t)], 6)) + " lm_eval_avg=" + str(round(results[str(t)]["avg"], 4)))
        else:
            print("Not enough results for Spearman (n=" + str(len(tids)) + ")")

if __name__ == "__main__":
    main()
