#!/usr/bin/env python3
"""BaiZe data mixture BO search (GP-EI surrogate, offline-compatible).

Day1=Stable (base/code/math simplex). Day2=Decay (SFT% + 5-class simplex).
6 parallel trials on GPU2-7, 500 steps/trial, eval on held-out bins.

Usage:
  python baize_mix_optuna.py --phase stable --n-trials 200 --gpus 2,3,4,5,6,7
  python baize_mix_optuna.py --phase decay --n-trials 200 --gpus 2,3,4,5,6,7
"""
import argparse, json, os, re, sqlite3, subprocess, sys, time, threading
from queue import Queue
import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize
from sklearn.gaussian_process import GaussianProcessRegressor as GPR
from sklearn.gaussian_process.kernels import Matern, ConstantKernel
from concurrent.futures import ThreadPoolExecutor

BASE = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027"
PY = "/nas_train/app.e0031982/miniforge3/envs/py310/bin"
TOKENIZER = f"{BASE}/data/tokenizer_eod"
HELDOUT = f"{BASE}/data/heldout"
DATA = f"{BASE}/data"
EXP_DIR = f"{BASE}/nemo_experiments/mix_search"
DB_PATH = f"{EXP_DIR}/mix_search.db"
TRAIN_ITERS = 500
EVAL_INTERVAL = 100
EVAL_ITERS = 10
GBS = 16
SEQ = 2048
LR = 3e-3  # 必验#5 选定: 3e-4→10.19, 1e-3→8.04, 3e-3→7.40 (最优)
WARMUP = 50
DECAY = 450
SEED = 1234

SPACES = {
    "stable": {
        "dims": ["web", "code"],  # math = 1 - web - code
        "bounds": [(0.80, 0.95), (0.03, 0.12)],
        "data_paths": {
            "base": f"{DATA}/mix_base/mix_base_train_s0",
            "code": f"{DATA}/anneal_code",
            "math": f"{DATA}/anneal_math2",
        },
    },
    "decay": {
        "dims": ["sft_pct", "sft_math", "sft_code", "sft_logic"],
        "bounds": [(0.40, 0.80), (0.05, 0.40), (0.05, 0.40), (0.05, 0.40)],
        "data_paths": {},
    },
}

VALID_BLEND = f"1 {HELDOUT}/held_out_base 1 {HELDOUT}/held_out_code 1 {HELDOUT}/held_out_math"


def build_blend_stable(web, code):
    math_r = max(1.0 - web - code, 0.01)
    sp = SPACES["stable"]["data_paths"]
    return f"{web:.6f} {sp['base']} {code:.6f} {sp['code']} {math_r:.6f} {sp['math']}"


def build_blend_decay(sft_pct, sft_math, sft_code, sft_logic):
    sft_know = max(1.0 - sft_math - sft_code - sft_logic, 0.01)
    base_r = 1.0 - sft_pct
    sp = SPACES["stable"]["data_paths"]
    sft = SPACES["decay"]["data_paths"]
    parts = [f"{base_r:.6f} {sp['base']}"]
    parts.append(f"{sft_pct * sft_math:.6f} {sft['math']}")
    parts.append(f"{sft_pct * sft_code:.6f} {sft['code']}")
    parts.append(f"{sft_pct * sft_logic:.6f} {sft['logic']}")
    parts.append(f"{sft_pct * sft_know:.6f} {sft['know']}")
    return " ".join(parts)


def random_sample(bounds):
    return np.random.uniform([b[0] for b in bounds], [b[1] for b in bounds])


# ---- SQLite storage ----
def init_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS trials(
        id INTEGER PRIMARY KEY AUTOINCREMENT, phase TEXT, params TEXT,
        loss REAL, status TEXT, start_time REAL, end_time REAL, gpu INTEGER,
        intermediate TEXT)""")
    conn.commit()
    conn.close()


def save_trial(db_path, phase, params, loss, status, gpu, intermediate):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO trials(phase,params,loss,status,start_time,end_time,gpu,intermediate)"
        " VALUES(?,?,?,?,?,?,?,?)",
        (phase, json.dumps(params), loss, status, time.time(), time.time(), gpu,
         json.dumps(intermediate)))
    conn.commit()
    conn.close()


def load_trials(db_path, phase):
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT params,loss FROM trials WHERE phase=? AND status='complete'",
        (phase,)).fetchall()
    conn.close()
    return [(json.loads(r[0]), r[1]) for r in rows]


# ---- GP-EI surrogate ----
class GPSurrogate:
    def __init__(self, bounds):
        self.bounds = np.array(bounds)
        self.X = []
        self.y = []
        self.gp = None
        self._fitted = False
        self._lock = threading.Lock()

    def add(self, x, y):
        with self._lock:
            self.X.append(list(x))
            self.y.append(y)
            if len(self.X) >= 3:
                kernel = ConstantKernel(1.0) * Matern(nu=2.5)
                self.gp = GPR(kernel=kernel, alpha=1e-6, normalize_y=True)
                self.gp.fit(np.array(self.X), np.array(self.y))
                self._fitted = True

    def _ei(self, x):
        if self.gp is None or not self._fitted:
            return 0.0
        x = x.reshape(1, -1)
        mu, sigma = self.gp.predict(x, return_std=True)
        f_best = min(self.y)
        z = (f_best - mu[0]) / (sigma[0] + 1e-9)
        return max((f_best - mu[0]) * norm.cdf(z) + sigma[0] * norm.pdf(z), 0.0)

    def suggest(self, n_restarts=20):
        with self._lock:
            if self.gp is None or not self._fitted:
                return None
            best_x, best_ei = None, -1
            for _ in range(n_restarts):
                x0 = np.random.uniform(self.bounds[:, 0], self.bounds[:, 1])
                res = minimize(lambda x: -self._ei(x), x0, bounds=self.bounds,
                               method="L-BFGS-B")
                if -res.fun > best_ei:
                    best_ei = -res.fun
                    best_x = res.x
            return best_x


# ---- Log parsing ----
# Validation: " validation loss at iteration 10 | lm loss value: 9.344584E+00 | ..."
# Training:   " [datetime] iteration 10/20 | ... | lm loss: 1.071757E+01 | ..."
VAL_LOSS_RE = re.compile(r"validation loss at iteration\s+(\d+).*?lm loss value:\s*([\d.eE+-]+)")
TRAIN_LOSS_RE = re.compile(r"iteration\s+(\d+)/.*?lm loss:\s*([\d.eE+-]+)")


def parse_intermediate_losses(log_path):
    results = {}
    try:
        with open(log_path, "r") as f:
            for line in f:
                m = VAL_LOSS_RE.search(line)
                if m:
                    step = int(m.group(1))
                    results[step] = float(m.group(2))
    except Exception:
        pass
    return results


def parse_final_loss(log_path):
    vals = parse_intermediate_losses(log_path)
    if vals:
        return list(vals.values())[-1], list(vals.keys())[-1]
    try:
        last_loss = None
        with open(log_path, "r") as f:
            for line in f:
                m = TRAIN_LOSS_RE.search(line)
                if m:
                    last_loss = float(m.group(2))
        return last_loss, TRAIN_ITERS
    except Exception:
        return None, 0


# ---- Trial runner ----
def run_trial(trial_id, params, gpu_id, phase, gp_median=None):
    os.makedirs(EXP_DIR, exist_ok=True)
    name = f"{phase}_t{trial_id:04d}_gpu{gpu_id}"
    log_path = f"/tmp/mix_search_{name}.log"
    port = 30000 + gpu_id

    if phase == "stable":
        blend = build_blend_stable(params[0], params[1])
    else:
        blend = build_blend_decay(*params)

    cmd = [
        f"{PY}/torchrun", "--nnodes=1", "--nproc_per_node=1",
        "--master_addr=127.0.0.1", "--master_port", str(port),
        f"{BASE}/pretrain_proxy_launcher.py",
        "--proxy-size", "d128",
        "--name", name, "--dir", EXP_DIR,
        "--tokenizer-path", TOKENIZER,
        "--train-data-path", *blend.split(),
        "--valid-data-path", *VALID_BLEND.split(),
        "--tensor-parallel", "1",
        "--train-iters", str(TRAIN_ITERS),
        "--global-batch-size", str(GBS),
        "--micro-batch-size", "1",
        "--seq-length", str(SEQ),
        "--eval-interval", str(EVAL_INTERVAL),
        "--eval-iters", str(EVAL_ITERS),
        "--save-interval", str(TRAIN_ITERS),
        "--lr", str(LR), "--min-lr", "1e-5",
        "--lr-warmup-iters", str(WARMUP), "--lr-decay-iters", str(DECAY),
        "--lr-decay-style", "WSD",
        "--seed", str(SEED), "--precision", "bf16_mixed",
    ]

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    env["PYTHONPATH"] = "/nas_train/app.e0031982/omegaconf_230"

    proc = subprocess.Popen(cmd, stdout=open(log_path, "w"),
                            stderr=subprocess.STDOUT, env=env)
    intermediate = {}
    pruned = False

    while proc.poll() is None:
        time.sleep(5)
        vals = parse_intermediate_losses(log_path)
        for step, loss in vals.items():
            if step not in intermediate:
                intermediate[step] = loss
                if gp_median and len(intermediate) >= 2 and loss > gp_median * 1.5:
                    proc.kill()
                    pruned = True
                    break
        if pruned:
            break

    proc.wait()
    loss, _ = parse_final_loss(log_path)
    status = "pruned" if pruned else ("complete" if loss is not None else "failed")

    # Clean up checkpoint to save disk (BO only needs loss, not weights)
    ckpt_dir = f"{EXP_DIR}/{name}"
    if os.path.exists(ckpt_dir):
        import shutil
        shutil.rmtree(ckpt_dir, ignore_errors=True)

    return loss, status, intermediate


# ---- Main ----
def main():
    p = argparse.ArgumentParser(description="BaiZe data mixture BO search")
    p.add_argument("--phase", choices=["stable", "decay"], default="stable")
    p.add_argument("--n-trials", type=int, default=200)
    p.add_argument("--gpus", default="2,3,4,5,6,7")
    p.add_argument("--n-random", type=int, default=12)
    args = p.parse_args()

    gpu_list = [int(g) for g in args.gpus.split(",")]
    n_workers = len(gpu_list)
    space = SPACES[args.phase]
    bounds = space["bounds"]

    if args.phase == "decay":
        space["data_paths"] = {
            "math": f"{DATA}/sft_math", "code": f"{DATA}/sft_code",
            "logic": f"{DATA}/sft_logic", "know": f"{DATA}/sft_know",
        }

    init_db(DB_PATH)
    gp = GPSurrogate(bounds)
    for params, loss in load_trials(DB_PATH, args.phase):
        gp.add([params[d] for d in space["dims"]], loss)
    print(f"Loaded {len(gp.X)} existing trials for phase={args.phase}")

    trial_counter = len(gp.X)
    gpu_queue = Queue()
    for g in gpu_list:
        gpu_queue.put(g)

    completed_losses = [y for y in gp.y]
    results_lock = threading.Lock()

    def worker(trial_id):
        gpu_id = gpu_queue.get()
        try:
            if trial_id < args.n_random or not gp._fitted:
                params = random_sample(bounds)
            else:
                suggested = gp.suggest()
                params = suggested if suggested is not None else random_sample(bounds)

            param_dict = {d: float(v) for d, v in zip(space["dims"], params)}
            print(f"[trial {trial_id}] GPU{gpu_id} params={param_dict}")

            with results_lock:
                median_loss = np.median(completed_losses) if completed_losses else None

            loss, status, intermediate = run_trial(
                trial_id, params, gpu_id, args.phase, gp_median=median_loss)

            print(f"[trial {trial_id}] GPU{gpu_id} status={status} loss={loss}")

            if status == "complete" and loss is not None:
                with results_lock:
                    gp.add(params, loss)
                    completed_losses.append(loss)
            save_trial(DB_PATH, args.phase, param_dict, loss, status, gpu_id, intermediate)
        finally:
            gpu_queue.put(gpu_id)

    with ThreadPoolExecutor(max_workers=n_workers) as pool:
        futures = []
        for i in range(trial_counter, trial_counter + args.n_trials):
            futures.append(pool.submit(worker, i))
        for f in futures:
            f.result()

    if gp.y:
        best_idx = int(np.argmin(gp.y))
        best_params = {d: v for d, v in zip(space["dims"], gp.X[best_idx])}
        print(f"\n{'='*60}")
        print(f"Best loss: {gp.y[best_idx]:.4f}")
        print(f"Best params: {best_params}")
        print(f"Total trials: {len(gp.y)}")


if __name__ == "__main__":
    main()
