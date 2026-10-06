#!/usr/bin/env python3
"""BaiZe data mixture BO search Round 2 (lm_eval objective, MBS=16, D=0.5B).

Key changes from Round 1 (baize_mix_optuna.py):
- Objective: lm_eval 8-task average score (NOT val-loss proxy)
  Round 1 proved proxy val-loss has NEGATIVE Spearman rho=-0.43 with lm_eval
- MBS=16 (not 1) -> 8.6x speedup (s_step 1432->166ms)
- D=0.5B/trial (not 0.016B) -> 15259 steps @ GBS=16 x seq=2048
- Save final ckpt -> HF conversion -> lm_eval -> cleanup
- New DB: mix_search_eval_r2.db
- Subsampled lm_eval (--limit 500) for BO; full eval on top-K at end

Usage:
  python baize_mix_optuna_r2.py --phase stable --n-trials 200 --gpus 0,1,2,3,4,5,6,7
  python baize_mix_optuna_r2.py --phase stable --n-trials 200 --gpus 2,3,4,5,6,7
  python baize_mix_optuna_r2.py --d-tokens 0.25e9 --n-trials 400 --gpus 0,1,2,3,4,5,6,7
"""
import argparse, json, os, re, sqlite3, subprocess, sys, time, threading, shutil, glob
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
RUN_DIR = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
GBS = 16
SEQ = 2048
MBS = 16
LR = 3e-3
SEED = 1234
EVAL_LIMIT = 500
T2_TASKS = "arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande"
T3_TASKS = "gsm8k,math,bbh,mmlu,humaneval,mbpp"
TASK_METRICS = {
    "arc_challenge": "acc_norm,none", "arc_easy": "acc_norm,none",
    "boolq": "acc,none", "hellaswag": "acc_norm,none",
    "openbookqa": "acc_norm,none", "piqa": "acc_norm,none",
    "sciq": "acc_norm,none", "winogrande": "acc,none",
}
SPACES = {
    "stable": {
        "dims": ["web", "code"],
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
VALID_BLEND_EVAL = f"1 {HELDOUT}/held_out_eval"



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


def init_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS trials(
        id INTEGER PRIMARY KEY AUTOINCREMENT, phase TEXT, params TEXT,
        score REAL, status TEXT, start_time REAL, end_time REAL, gpu INTEGER,
        intermediate TEXT, lm_eval_detail TEXT)""")
    conn.commit()
    conn.close()


def save_trial(db_path, phase, params, score, status, gpu, intermediate, detail):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO trials(phase,params,score,status,start_time,end_time,gpu,intermediate,lm_eval_detail)"
        " VALUES(?,?,?,?,?,?,?,?,?)",
        (phase, json.dumps(params), score, status, time.time(), time.time(), gpu,
         json.dumps(intermediate), json.dumps(detail)))
    conn.commit()
    conn.close()


def load_trials(db_path, phase):
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT params,score FROM trials WHERE phase=? AND status='complete'",
        (phase,)).fetchall()
    conn.close()

class GPSurrogate:
    """GP-EI surrogate. Stores NEGATED score so minimize -> maximize original."""
    def __init__(self, bounds):
        self.bounds = np.array(bounds)
        self.X = []
        self.y = []
        self.gp = None
        self._fitted = False
        self._lock = threading.Lock()

    def add(self, x, neg_score):
        with self._lock:
            self.X.append(list(x))
            self.y.append(neg_score)
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
                res = minimize(lambda x: -self._ei(x), x0, bounds=self.bounds, method="L-BFGS-B")
                if -res.fun > best_ei:
                    best_ei = -res.fun
                    best_x = res.x
            return best_x


def parse_lm_eval_score(eval_dir):
    """Parse lm_eval results JSON -> 8-task average score."""
    json_files = glob.glob(os.path.join(eval_dir, "**", "results_*.json"), recursive=True)
    if not json_files:
        return None, {}
    with open(json_files[0]) as f:
        data = json.load(f)
    results = data.get("results", {})
    scores = {}
    for task, metrics in results.items():
        if task in TASK_METRICS:
            val = metrics.get(TASK_METRICS[task])
            if val is None:
                val = metrics.get("acc,none")
            if val is not None:
                scores[task] = val
    if not scores:
        return None, {}
    return sum(scores.values()) / len(scores), scores


VAL_LOSS_RE = re.compile(r"validation loss at iteration\s+(\d+).*?lm loss value:\s*([\d.eE+-]+)")


def run_trial(trial_id, params, gpu_id, phase, train_iters, warmup, decay_iters, keep_ckpt=False):
    """Train -> ckpt -> HF -> lm_eval -> score. Returns (score, status, intermediate, detail)."""
    os.makedirs(EXP_DIR, exist_ok=True)
    name = f"r2_{phase}_t{trial_id:04d}_gpu{gpu_id}"
    log_path = f"/tmp/mix_search_r2_{name}.log"
    port = 30000 + gpu_id

    if phase == "stable":
        blend = build_blend_stable(params[0], params[1])
    else:
        blend = build_blend_decay(*params)

    # Step 1: Train with MBS=16, save final ckpt
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

    print(f"[trial {trial_id}] GPU{gpu_id} training {train_iters} steps (MBS={MBS})...")
    proc = subprocess.Popen(cmd, stdout=open(log_path, "w"), stderr=subprocess.STDOUT, env=env)
    intermediate = {}
    while proc.poll() is None:
        time.sleep(10)
        try:
            with open(log_path, "r") as f:
                for line in f:
                    m = VAL_LOSS_RE.search(line)
                    if m:
                        step = int(m.group(1))
                        if step not in intermediate:
                            intermediate[step] = float(m.group(2))
        except Exception:
            pass
    proc.wait()
    if proc.returncode != 0:
        print(f"[trial {trial_id}] GPU{gpu_id} TRAINING FAILED (rc={proc.returncode})")
        return None, "failed", intermediate, {}

    # Step 2: Find checkpoint
    ckpt_dir = f"{EXP_DIR}/{name}/checkpoints"
    ckpt = None
    if os.path.isdir(ckpt_dir):
        ckpts = sorted(glob.glob(os.path.join(ckpt_dir, "iter_*")))
        if ckpts:
            ckpt = ckpts[-1]
    if ckpt is None:
        print(f"[trial {trial_id}] GPU{gpu_id} NO CKPT in {ckpt_dir}")
        return None, "failed", intermediate, {}

    # Step 3: Convert ckpt -> HF
    hf_out = f"{EXP_DIR}/{name}/hf_model"
    if not os.path.exists(os.path.join(hf_out, "config.json")):
        conv_env = os.environ.copy()
        conv_env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
        conv_env["PYTHONPATH"] = "/nas_train/app.e0031982/omegaconf_230"
        conv_cmd = [f"{PY}/python", f"{RUN_DIR}/baize_p6_ckpt_to_hf.py",
                    "--ckpt", ckpt, "--tokenizer", TOKENIZER, "--out", hf_out]
        conv_proc = subprocess.run(conv_cmd, capture_output=True, text=True, env=conv_env, timeout=300)
        if conv_proc.returncode != 0:
            print(f"[trial {trial_id}] GPU{gpu_id} HF CONV FAILED: {conv_proc.stderr[-300:]}")
            if not keep_ckpt:
                shutil.rmtree(f"{EXP_DIR}/{name}", ignore_errors=True)
            return None, "failed", intermediate, {}

    # Step 4: Run lm_eval (subsampled)
    eval_out = f"{EXP_DIR}/{name}/lm_eval_results"
    os.makedirs(eval_out, exist_ok=True)
    tasks = T2_TASKS if phase == "stable" else T3_TASKS
    eval_env = os.environ.copy()
    eval_env["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    eval_env["PYTHONPATH"] = f"/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:{eval_env.get('PYTHONPATH', '')}"
    eval_env["HF_DATASETS_CACHE"] = "/nas_train/app.e0031982/hf_cache"
    eval_env["HF_HOME"] = "/nas_train/app.e0031982/.cache"
    eval_env["HF_ENDPOINT"] = "https://hf-mirror.com"
    eval_env["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    eval_cmd = [f"{PY}/python", "-m", "lm_eval", "--model", "hf",
                "--model_args", f"pretrained={hf_out},dtype=bfloat16,trust_remote_code=False",
                "--tasks", tasks, "--num_fewshot", "0", "--batch_size", "4",
                "--limit", str(EVAL_LIMIT), "--output_path", eval_out]
    print(f"[trial {trial_id}] GPU{gpu_id} running lm_eval (--limit {EVAL_LIMIT})...")
    eval_proc = subprocess.run(eval_cmd, capture_output=True, text=True, env=eval_env, timeout=1800)
    if eval_proc.returncode != 0:
        print(f"[trial {trial_id}] GPU{gpu_id} LM_EVAL FAILED: {eval_proc.stderr[-300:]}")
        if not keep_ckpt:
            shutil.rmtree(f"{EXP_DIR}/{name}", ignore_errors=True)
        return None, "failed", intermediate, {}

    # Step 5: Parse score
    score, detail = parse_lm_eval_score(eval_out)
    if score is None:
        print(f"[trial {trial_id}] GPU{gpu_id} SCORE PARSE FAILED")
        if not keep_ckpt:
            shutil.rmtree(f"{EXP_DIR}/{name}", ignore_errors=True)

def main():
    p = argparse.ArgumentParser(description="BaiZe BO Round 2 (lm_eval objective)")
    p.add_argument("--phase", choices=["stable", "decay"], default="stable")
    p.add_argument("--n-trials", type=int, default=200)
    p.add_argument("--gpus", default="0,1,2,3,4,5,6,7")
    p.add_argument("--n-random", type=int, default=12)
    p.add_argument("--d-tokens", type=float, default=0.5e9, help="Tokens/trial (default 0.5B)")
    p.add_argument("--db-suffix", default="_eval_r2")
    p.add_argument("--keep-topk", type=int, default=5)
    args = p.parse_args()

    train_iters = int(args.d_tokens / (GBS * SEQ))
    warmup = max(int(train_iters * 0.10), 50)
    decay_iters = int(train_iters * 0.90)
    db_path = f"{EXP_DIR}/mix_search{args.db_suffix}.db"

    print(f"{'='*60}")
    print(f"BaiZe BO Round 2 - lm_eval objective")
    print(f"  D={args.d_tokens/1e9:.2f}B -> {train_iters} steps (GBS={GBS}, MBS={MBS}, seq={SEQ})")
    print(f"  Warmup={warmup}, Decay@{decay_iters}, LR={LR}, EvalLimit={EVAL_LIMIT}")
    print(f"  Trials={args.n_trials}, GPUs={args.gpus}, DB={db_path}")
    est_min = train_iters * 0.166 / 60 + 5
    print(f"  Est: ~{est_min:.0f}min/trial, ~{args.n_trials*est_min/len(args.gpus.split(','))/60:.1f}h total")
    print(f"{'='*60}")

    gpu_list = [int(g) for g in args.gpus.split(",")]
    n_workers = len(gpu_list)
    space = SPACES[args.phase]
    bounds = space["bounds"]
    if args.phase == "decay":
        space["data_paths"] = {"math": f"{DATA}/sft_math", "code": f"{DATA}/sft_code",
                               "logic": f"{DATA}/sft_logic", "know": f"{DATA}/sft_know"}

    init_db(db_path)
    gp = GPSurrogate(bounds)
    for params, neg_score in load_trials(db_path, args.phase):
        gp.add([params[d] for d in space["dims"]], neg_score)
    print(f"Loaded {len(gp.X)} existing trials for phase={args.phase}")

    trial_counter = len(gp.X)
    gpu_queue = Queue()
    for g in gpu_list:
        gpu_queue.put(g)
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
            score, status, intermediate, detail = run_trial(
                trial_id, params, gpu_id, args.phase, train_iters, warmup, decay_iters)
            print(f"[trial {trial_id}] GPU{gpu_id} status={status} score={score}")
            if status == "complete" and score is not None:
                with results_lock:
                    gp.add(params, -score)
            save_trial(db_path, args.phase, param_dict, score, status, gpu_id, intermediate, detail)
        finally:
            gpu_queue.put(gpu_id)

    with ThreadPoolExecutor(max_workers=n_workers) as pool:
        futures = [pool.submit(worker, i) for i in range(trial_counter, trial_counter + args.n_trials)]
        for f in futures:
            f.result()

    if gp.y:
        scores = [-y for y in gp.y]
        best_idx = int(np.argmax(scores))
        best_params = {d: v for d, v in zip(space["dims"], gp.X[best_idx])}
        print(f"\n{'='*60}")
        print(f"Best lm_eval score: {scores[best_idx]:.4f}")
        print(f"Best params: {best_params}")
        print(f"Total trials: {len(scores)}")
        topk_idx = np.argsort(scores)[-args.keep_topk:][::-1]
        print(f"\nTop-{args.keep_topk}:")
        for i, idx in enumerate(topk_idx):
            params = {d: v for d, v in zip(space["dims"], gp.X[idx])}
            print(f"  #{i+1}: score={scores[idx]:.4f} params={params}")


if __name__ == "__main__":
    main()
