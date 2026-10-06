#!/usr/bin/env python3
"""B: Collector for long-context zero-shot comparison (ABF vs baseline)."""
import json, glob, os

OUT_BASE = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/lm_eval_longctx"
BASELINE_DIR = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/lm_eval_results/iter_4771"

TASK_MAP = {
    "hellaswag": ["acc_norm,none", "acc,none"],
    "arc_easy": ["acc,none", "acc_norm,none"],
    "mmlu": ["acc,none", "acc_norm,none"],
    "bbh_zeroshot": ["exact_match,flexible-extract", "exact_match,strict-match"],
}

def extract(results_block, metric_keys):
    for k in metric_keys:
        if k in results_block and isinstance(results_block[k], (int, float)):
            return results_block[k]
    base = metric_keys[0].split(",")[0]
    for k, v in results_block.items():
        if k.startswith(base) and isinstance(v, (int, float)):
            return v
    return None

def load_results(search_dir):
    res = {}
    for rf in sorted(glob.glob(os.path.join(search_dir, "**", "results_*.json"), recursive=True)):
        try:
            data = json.load(open(rf))
        except Exception:
            continue
        for task, mkeys in TASK_MAP.items():
            if task in data.get("results", {}) and task not in res:
                val = extract(data["results"][task], mkeys)
                if val is not None:
                    res[task] = val
    return res

def main():
    abf = load_results(os.path.join(OUT_BASE, "abf"))
    baseline = load_results(BASELINE_DIR) if os.path.isdir(BASELINE_DIR) else {}

    # Also load passkey
    passkey = {}
    pk_path = os.path.join(OUT_BASE, "passkey_results.json")
    if os.path.exists(pk_path):
        pk_data = json.load(open(pk_path))
        for r in pk_data.get("results", []):
            passkey[r["context"]] = r["passkey_acc"]

    print(f"{'task':>30} {'baseline':>12} {'ABF_1e6':>12} {'delta':>10}")
    print("-" * 66)
    for t in sorted(set(list(baseline.keys()) + list(abf.keys()))):
        b = baseline.get(t)
        a = abf.get(t)
        bs = f"{b:.4f}" if b is not None else "N/A"
        as_ = f"{a:.4f}" if a is not None else "N/A"
        ds = f"{a-b:+.4f}" if (a is not None and b is not None) else "N/A"
        print(f"{t:>30} {bs:>12} {as_:>12} {ds:>10}")

    if passkey:
        print(f"\n{'passkey':>30} {'ctx':>12} {'acc':>12}")
        for ctx, acc in sorted(passkey.items()):
            print(f"{'passkey':>30} {ctx:>12} {acc:>12.2f}")

    out = {"baseline": baseline, "abf_1e6": abf, "passkey": passkey}
    json.dump(out, open(os.path.join(OUT_BASE, "b_longctx_comparison.json"), "w"), indent=2)
    print(f"\nSaved to {OUT_BASE}/b_longctx_comparison.json")

if __name__ == "__main__":
    main()