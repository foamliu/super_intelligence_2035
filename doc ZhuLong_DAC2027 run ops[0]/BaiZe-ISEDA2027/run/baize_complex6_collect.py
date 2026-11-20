#!/usr/bin/env python3
"""Collector for BaiZe A: 复杂推理 6 集.
Scans all lm_eval result JSONs under lm_eval_complex/iter_*/ and extracts
the aggregate metric for each of the 6 tasks across the 6 milestone ckpts.
Outputs a summary JSON + prints a table.  Used by baize_complex6_eval_v2.sh.
"""
import json, glob, os, sys

BASE = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b"
OUT_BASE = os.path.join(BASE, "lm_eval_complex")
ITERS = ["0156", "0312", "0624", "1248", "2496", "4771"]
# tokens seen at each milestone iter (P-5b: GBS=1024, seq=4094, MBS=1 -> 1024 tok/step)
TOKENS = {"0156": 655e6, "0312": 1.31e9, "0624": 2.62e9,
          "1248": 5.24e9, "2496": 10.5e9, "4771": 20.0e9}

# primary metric key per task (prefer flexible-extract for generative)
# NOTE: lm_eval uses comma-suffixed keys like "acc,none", "pass@1,create_test"
TASK_METRICS = {
    "gsm8k": ["exact_match,flexible-extract", "exact_match,strict-match"],
    "hendrycks_math500": ["exact_match,flexible-extract", "exact_match,strict-match"],
    "mmlu": ["acc,none", "acc_norm,none", "acc_norm", "acc"],
    "bbh_zeroshot": ["exact_match,flexible-extract", "exact_match,strict-match"],
    "humaneval": ["pass@1,create_test", "pass@1"],
    "mbpp": ["pass_at_1,none", "pass@1"],
}


def find_result_files(iter_dir):
    """Return all results_*.json under iter_dir (any depth)."""
    return sorted(glob.glob(os.path.join(iter_dir, "**", "results_*.json"), recursive=True))


def extract_metric(results_block, metric_keys):
    """Given a results dict for one task, return first available metric value."""
    for k in metric_keys:
        if k in results_block:
            v = results_block[k]
            if isinstance(v, (int, float)):
                return v
    # fallback: any key starting with the base metric
    base = metric_keys[0].split(",")[0]
    for k, v in results_block.items():
        if k.startswith(base) and isinstance(v, (int, float)):
            return v
    return None


def main():
    table = {}  # iter -> {task: metric}
    for it in ITERS:
        iter_dir = os.path.join(OUT_BASE, f"iter_{it}")
        table[it] = {}
        rfiles = find_result_files(iter_dir)
        # scan all result files; a file may contain one or more tasks
        for rf in rfiles:
            try:
                data = json.load(open(rf))
            except Exception:
                continue
            res = data.get("results", {})
            for task, mkeys in TASK_METRICS.items():
                if task in res and task not in table[it]:
                    val = extract_metric(res[task], mkeys)
                    if val is not None:
                        table[it][task] = val
    # print table
    tasks = list(TASK_METRICS.keys())
    hdr = f"{'iter':>6} " + " ".join(f"{t:>20}" for t in tasks)
    print(hdr)
    print("-" * len(hdr))
    for it in ITERS:
        row = f"{it:>6} "
        for t in tasks:
            v = table[it].get(t)
            row += f"{(f'{v:.4f}' if v is not None else 'N/A'):>20} "
        print(row)
    # write summary json
    summary = {
        "iters": ITERS,
        "tokens": {it: TOKENS[it] for it in ITERS},
        "tasks": tasks,
        "table": table,
    }
    out_path = os.path.join(OUT_BASE, "complex6_summary.json")
    json.dump(summary, open(out_path, "w"), indent=2)
    print(f"\nSummary written to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
