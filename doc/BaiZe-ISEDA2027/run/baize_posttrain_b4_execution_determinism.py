#!/usr/bin/env python3
"""B4 - Execution determinism acceptance item (baseline-nailed task B.4).

10 tasks (5 PASS + 5 FAIL from A0 run1), same code run 10x in sandbox, report verdict flip rate.
判据: 同一份代码多次执行判决应稳定; 翻转率高 => 沙盒非确定性污染 Pass@1.
历史参考 wake533: direct 2/79 vs rescue 0/79.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

RUN_DIR = Path(__file__).resolve().parent
EDA_BASE = Path("/home/app.e0031982/code/eda_fastmcp")
VENV_PY = EDA_BASE / ".venv" / "bin" / "python"
RUN1_DIR = Path("/tmp/posttrain_5run_eval/A0_base/run1")
RUN1_REPORT = RUN1_DIR / "final_report.json"
RUN1_JSONL = RUN1_DIR / "completed_code_generation.jsonl"
RUN4_BATCH = Path("/home/app.e0031982/eda_code_eval/2026_1121_154639")
OUT_DIR = Path("/tmp/b4_det")
SUBSET_JSONL = Path("/home/app.e0031982/eda_code_eval/completed_code_generation_B4_DET.jsonl")
RESULT_JSON = RUN_DIR / "baseline_B4_execution_determinism.json"


def log(msg):
    ts = datetime.now().strftime("%F %T")
    print(f"[B4 {ts}] {msg}", flush=True)


def load_run1_tasks():
    rep = json.load(open(RUN1_REPORT))
    det = rep["details_per_task"]
    pass_ids = [k for k, v in det.items() if v.get("pass_rate", 0) >= 1.0][:5]
    fail_ids = [k for k, v in det.items()
                if v.get("pass_rate", 0) == 0.0 and "failed" in (v.get("execution_statuses") or [])][:5]
    if len(pass_ids) < 5 or len(fail_ids) < 5:
        raise RuntimeError(f"not enough pass/fail: pass={len(pass_ids)} fail={len(fail_ids)}")
    return pass_ids, fail_ids


def write_subset_jsonl(task_ids):
    wanted = set(task_ids)
    out = []
    with open(RUN1_JSONL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("task_id") in wanted:
                out.append(rec)
                wanted.discard(rec["task_id"])
                if not wanted:
                    break
    if len(out) != len(task_ids):
        found = {r["task_id"] for r in out}
        raise RuntimeError(f"missing tasks: {set(task_ids) - found}")
    with open(SUBSET_JSONL, "w") as f:
        for rec in out:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return [r["task_id"] for r in out]


def run4_eval_imminent():
    fr4 = Path("/tmp/posttrain_5run_eval/A0_base/run4/final_report.json")
    if fr4.exists():
        return True
    total = 0
    for k in ("success", "failure", "timeout"):
        p = RUN4_BATCH / "stats" / k
        if p.exists():
            try:
                total += int(p.read_text().strip() or 0)
            except ValueError:
                pass
    return total >= 156


def eval_fw_dir():
    envf = EDA_BASE / ".env"
    with open(envf) as f:
        for line in f:
            if line.startswith("EVAL_FW_DIR="):
                return Path(line.strip().split("=", 1)[1])
    return Path("/home/app.e0031982/code/EDA-Eval-Framework")


def run_one_eval(repeat_i):
    marker = OUT_DIR / f".marker_run{repeat_i}"
    marker.touch()
    env = os.environ.copy()
    env["PYTHON"] = str(VENV_PY)
    cmd = [str(VENV_PY), "scripts/run_eval.py", "--generations", str(SUBSET_JSONL)]
    log(f"run_eval #{repeat_i} starting...")
    proc = subprocess.run(cmd, cwd=str(EDA_BASE), env=env,
                          capture_output=True, text=True, timeout=900)
    if proc.returncode != 0:
        log(f"run_eval #{repeat_i} rc={proc.returncode} stderr_tail={proc.stderr[-400:]}")
    fw = eval_fw_dir()
    out_eval = fw / "output_evaluation"
    cand = list(out_eval.rglob("final_report*.json")) if out_eval.exists() else []
    cand = [c for c in cand if c.stat().st_mtime >= marker.stat().st_mtime]
    if not cand:
        log(f"run_eval #{repeat_i} NO final_report found")
        return None
    fr = max(cand, key=lambda c: c.stat().st_mtime)
    rdir = OUT_DIR / f"run{repeat_i}"
    rdir.mkdir(parents=True, exist_ok=True)
    shutil.copy(fr, rdir / "final_report.json")
    rep = json.load(open(fr))
    det = rep.get("details_per_task", {})
    verdicts = {}
    for tid, v in det.items():
        st = v.get("execution_statuses") or [None]
        verdicts[tid] = st[0]
    log(f"run_eval #{repeat_i} done: {len(verdicts)} tasks, verdicts={verdicts}")
    return verdicts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repeats", type=int, default=10)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--time-budget-min", type=int, default=50)
    args = ap.parse_args()

    if not VENV_PY.exists():
        sys.exit(f"FATAL: venv python not found: {VENV_PY}")
    if not RUN1_REPORT.exists() or not RUN1_JSONL.exists():
        sys.exit(f"FATAL: run1 artifacts missing: {RUN1_REPORT} / {RUN1_JSONL}")

    pass_ids, fail_ids = load_run1_tasks()
    task_ids = pass_ids + fail_ids
    log(f"PASS(5)={pass_ids}  FAIL(5)={fail_ids}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ordered = write_subset_jsonl(task_ids)
    log(f"subset jsonl written: {SUBSET_JSONL} ({len(ordered)} tasks: {ordered})")

    if args.dry_run:
        log(f"DRY-RUN: would run run_eval.py {args.repeats} times on subset.")
        return

    t0 = time.time()
    per_run = []
    for i in range(1, args.repeats + 1):
        if run4_eval_imminent():
            log(f"ABORT: run4 eval imminent (sandbox busy) -- stopping at {i-1} runs")
            break
        if time.time() - t0 > args.time_budget_min * 60:
            log(f"ABORT: time budget {args.time_budget_min}min exceeded -- stopping at {i-1} runs")
            break
        v = run_one_eval(i)
        if v is None:
            log(f"run {i} produced no report, skipping")
            continue
        per_run.append(v)

    n_runs = len(per_run)
    all_tasks = sorted({t for rv in per_run for t in rv})
    per_task = {}
    n_flip = 0
    for t in all_tasks:
        verdicts = [rv.get(t) for rv in per_run if t in rv]
        uniq = sorted(set(verdicts))
        per_task[t] = {"verdicts": verdicts, "unique": uniq, "flipped": len(uniq) > 1}
        if len(uniq) > 1:
            n_flip += 1
    flip_rate = n_flip / len(all_tasks) if all_tasks else None

    result = {
        "acceptance_item": "B4_execution_determinism",
        "spec": "10 tasks (5 PASS + 5 FAIL from A0 run1), same code run 10x in sandbox, report verdict flip rate",
        "source_run": "A0_base_run1",
        "pass_task_ids": pass_ids,
        "fail_task_ids": fail_ids,
        "subset_jsonl": str(SUBSET_JSONL),
        "n_runs_completed": n_runs,
        "n_tasks": len(all_tasks),
        "n_tasks_flipped": n_flip,
        "flip_rate": flip_rate,
        "historical_reference": "wake533: direct 2/79 vs rescue 0/79",
        "per_task": per_task,
        "per_run_raw": per_run,
        "timestamp_iso": datetime.now().isoformat(),
    }
    RESULT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    log(f"RESULT: n_runs={n_runs} n_tasks={len(all_tasks)} n_flipped={n_flip} flip_rate={flip_rate}")
    log(f"saved -> {RESULT_JSON}")
    print(json.dumps({"n_runs": n_runs, "n_tasks": len(all_tasks),
                      "n_flipped": n_flip, "flip_rate": flip_rate}, ensure_ascii=False))


if __name__ == "__main__":
    main()

