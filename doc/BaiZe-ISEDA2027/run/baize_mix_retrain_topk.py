#!/usr/bin/env python3
"""Retrain top-K BO configs with checkpoint saving for lm_eval."""
import argparse, json, os, sqlite3, subprocess, time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

BASE = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027"
PY = "/nas_train/app.e0031982/miniforge3/envs/py310/bin"
TOKENIZER = f"{BASE}/data/tokenizer_eod"
DATA = f"{BASE}/data"
EXP_DIR = f"{BASE}/nemo_experiments/mix_search"
DB_PATH = f"{EXP_DIR}/mix_search_eval.db"
TRAIN_ITERS = 500
GBS = 16
SEQ = 2048
LR = 3e-3
WARMUP = 50
DECAY = 450
SEED = 1234
SP = {"base": f"{DATA}/mix_base/mix_base_train_s0",
       "code": f"{DATA}/anneal_code",
       "math": f"{DATA}/anneal_math2"}
HELDOUT = f"{DATA}/heldout"
VALID_BLEND = f"1 {HELDOUT}/held_out_eval"

def build_blend(web, code):
    math_r = max(1.0 - web - code, 0.01)
    return f"{web:.6f} {SP[chr(98)+chr(97)+chr(115)+chr(101)]} {code:.6f} {SP[chr(99)+chr(111)+chr(100)+chr(101)]} {math_r:.6f} {SP[chr(109)+chr(97)+chr(116)+chr(104)]}"

def load_trials(db_path, k=5, prior_id=79, trial_ids=None):
    conn = sqlite3.connect(db_path)
    if trial_ids:
        ids = [int(x) for x in trial_ids.split(",")]
        trials = []
        for tid in ids:
            r = conn.execute("SELECT id, params, loss FROM trials WHERE id=?", (tid,)).fetchone()
            if r:
                p = json.loads(r[1])
                trials.append({"id": r[0], "web": p["web"], "code": p["code"],
                               "math": 1-p["web"]-p["code"], "loss": r[2]})
    else:
        rows = conn.execute("SELECT id, params, loss FROM trials WHERE status=? ORDER BY loss ASC", ("complete",)).fetchall()
        trials = []
        for r in rows[:k]:
            p = json.loads(r[1])
            trials.append({"id": r[0], "web": p["web"], "code": p["code"],
                           "math": 1-p["web"]-p["code"], "loss": r[2]})
        for r in rows:
            if r[0] == prior_id and r[0] not in [t["id"] for t in trials]:
                p = json.loads(r[1])
                trials.append({"id": r[0], "web": p["web"], "code": p["code"],
                               "math": 1-p["web"]-p["code"], "loss": r[2]})
                break
    conn.close()
    return trials

def run_retrain(trial, gpu_id):
    tid = trial["id"]
    name = f"topk_t{tid:04d}_gpu{gpu_id}"
    log_path = f"/tmp/mix_retrain_{name}.log"
    port = 30000 + gpu_id
    blend = build_blend(trial["web"], trial["code"])
    ckpt_dir = f"{EXP_DIR}/{name}/checkpoints"
    if os.path.exists(ckpt_dir):
        iters = sorted([d for d in os.listdir(ckpt_dir) if d.startswith("iter_")])
        if iters:
            print(f"[{name}] skip (ckpt exists: {iters[-1]})")
            return name, "skip", iters[-1]
    cmd = [f"{PY}/torchrun", "--nnodes=1", "--nproc_per_node=1",
           "--master_addr=127.0.0.1", "--master_port", str(port),
           f"{BASE}/pretrain_proxy_launcher.py", "--proxy-size", "d128",
           "--name", name, "--dir", EXP_DIR, "--tokenizer-path", TOKENIZER,
           "--train-data-path", *blend.split(),
           "--valid-data-path", *VALID_BLEND.split(),
           "--tensor-parallel", "1", "--train-iters", str(TRAIN_ITERS),
           "--global-batch-size", str(GBS), "--micro-batch-size", "1",
           "--seq-length", str(SEQ), "--eval-interval", "100", "--eval-iters", "10",
           "--save-interval", str(TRAIN_ITERS), "--lr", str(LR), "--min-lr", "1e-5",
           "--lr-warmup-iters", str(WARMUP), "--lr-decay-iters", str(DECAY),
           "--lr-decay-style", "WSD", "--seed", str(SEED), "--precision", "bf16_mixed"]
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    env["PYTHONPATH"] = "/nas_train/app.e0031982/omegaconf_230"
    print(f"[{name}] GPU{gpu_id} web={trial[chr(119)+chr(101)+chr(98)]:.4f} code={trial[chr(99)+chr(111)+chr(100)+chr(101)]:.4f} loss={trial[chr(108)+chr(111)+chr(115)+chr(115)]:.6f}")
    with open(log_path, "w") as f:
        proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, env=env)
    while proc.poll() is None:
        time.sleep(10)
    rc = proc.wait()
    ckpt_name = None
    if os.path.exists(ckpt_dir):
        iters = sorted([d for d in os.listdir(ckpt_dir) if d.startswith("iter_")])
        if iters:
            ckpt_name = iters[-1]
    print(f"[{name}] rc={rc} ckpt={ckpt_name}")
    return name, ("ok" if rc == 0 else f"fail({rc})"), ckpt_name

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gpus", default="2,3,4,5,6,7")
    p.add_argument("--k", type=int, default=5)
    p.add_argument("--prior-id", type=int, default=79)
    p.add_argument("--trial-ids", default=None)
    args = p.parse_args()
    gpu_list = [int(g) for g in args.gpus.split(",")]
    gpu_queue = Queue()
    for g in gpu_list:
        gpu_queue.put(g)
    trials = load_trials(DB_PATH, k=args.k, prior_id=args.prior_id, trial_ids=args.trial_ids)
    print(f"Retraining {len(trials)} configs:")
    for t in trials:
        print(f"  #{t[chr(105)+chr(100)]:3d} loss={t[chr(108)+chr(111)+chr(115)+chr(115)]:.6f}")
    results = []
    def worker(trial):
        gpu_id = gpu_queue.get()
        try:
            name, status, ckpt = run_retrain(trial, gpu_id)
            results.append({"id": trial["id"], "name": name, "status": status, "ckpt": ckpt})
        finally:
            gpu_queue.put(gpu_id)
    with ThreadPoolExecutor(max_workers=len(gpu_list)) as pool:
        futures = [pool.submit(worker, t) for t in trials]
        for f in futures:
            f.result()
    print(f"\nResults:")
    for r in results:
        print(f"  #{r[chr(105)+chr(100)]:3d} {r[chr(110)+chr(97)+chr(109)+chr(101)]} {r[chr(115)+chr(116)+chr(97)+chr(116)+chr(117)+chr(115)]} {r[chr(99)+chr(107)+chr(112)+chr(116)]}")

if __name__ == "__main__":
    main()
