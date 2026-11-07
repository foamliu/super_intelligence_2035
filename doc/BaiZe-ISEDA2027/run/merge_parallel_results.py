#!/usr/bin/env python3
"""Merge parallel eval results (hellaswag chunks + single-task dirs) into one results.json.

Usage: python merge_parallel_results.py <output_dir>

Reads:
  <output_dir>/hellaswag_chunk{0..3}/results.json  (hellaswag split)
  <output_dir>/<task>/results.json                 (other 7 tasks)

Produces:
  <output_dir>/results.json  (merged, same format as lm_eval)

For hellaswag: averages acc/acc_norm across chunks weighted by sample_len.
For other tasks: copies directly.
"""
import json, os, sys, glob

def main():
    if len(sys.argv) < 2:
        print("Usage: python merge_parallel_results.py <output_dir>")
        sys.exit(1)
    out_dir = sys.argv[1]

    merged_results = {}
    merged_configs = {}

    # ── hellaswag chunks ──
    hs_chunks = sorted(glob.glob(os.path.join(out_dir, "hellaswag_chunk*")))
    if hs_chunks:
        # Collect all chunk results for hellaswag
        chunk_accs = []
        chunk_acc_norms = []
        chunk_stderrs = []
        chunk_norm_stderrs = []
        total_samples = 0

        for chunk_dir in hs_chunks:
            rj = os.path.join(chunk_dir, "results.json")
            if not os.path.exists(rj):
                print(f"WARNING: missing {rj}, skipping", file=sys.stderr)
                continue
            with open(rj) as f:
                data = json.load(f)
            hs = data.get("results", {}).get("hellaswag", {})
            n = hs.get("sample_len", 0)
            acc = hs.get("acc,none", 0)
            acc_norm = hs.get("acc_norm,none", 0)
            stderr = hs.get("acc_stderr,none", 0)
            norm_stderr = hs.get("acc_norm_stderr,none", 0)
            chunk_accs.append((n, acc))
            chunk_acc_norms.append((n, acc_norm))
            chunk_stderrs.append((n, stderr))
            chunk_norm_stderrs.append((n, norm_stderr))
            total_samples += n
            print(f"  hellaswag chunk {os.path.basename(chunk_dir)}: n={n} acc={acc:.4f} norm={acc_norm:.4f}", file=sys.stderr)

        if total_samples > 0:
            # Weighted average
            wavg_acc = sum(n * a for n, a in chunk_accs) / total_samples
            wavg_norm = sum(n * a for n, a in chunk_acc_norms) / total_samples
            # Combined stderr (assuming independent samples)
            import math
            combined_stderr = math.sqrt(sum((n ** 2 * s ** 2) for n, s in chunk_stderrs)) / total_samples
            combined_norm_stderr = math.sqrt(sum((n ** 2 * s ** 2) for n, s in chunk_norm_stderrs)) / total_samples

            merged_results["hellaswag"] = {
                "name": "hellaswag",
                "alias": "hellaswag",
                "sample_len": total_samples,
                "acc,none": wavg_acc,
                "acc_stderr,none": combined_stderr,
                "acc_norm,none": wavg_norm,
                "acc_norm_stderr,none": combined_norm_stderr,
            }
            print(f"  hellaswag MERGED: n={total_samples} acc={wavg_acc:.4f} norm={wavg_norm:.4f}", file=sys.stderr)

    # ── hellaswag single dir (when not split into chunks, e.g. multi-server eval) ──
    if not hs_chunks:
        hs_single = os.path.join(out_dir, "hellaswag", "results.json")
        if os.path.exists(hs_single):
            with open(hs_single) as f:
                data = json.load(f)
            hs = data.get("results", {}).get("hellaswag", {})
            if hs:
                merged_results["hellaswag"] = hs
                print(f"  hellaswag (single): n={hs.get('sample_len',0)} acc={hs.get('acc,none',0):.4f} norm={hs.get('acc_norm,none',0):.4f}", file=sys.stderr)

    # ── other tasks (single dir each) ──
    other_tasks = ["arc_challenge", "arc_easy", "boolq", "openbookqa", "piqa", "sciq", "winogrande"]
    for task in other_tasks:
        rj = os.path.join(out_dir, task, "results.json")
        if not os.path.exists(rj):
            print(f"WARNING: missing {rj}, skipping", file=sys.stderr)
            continue
        with open(rj) as f:
            data = json.load(f)
        task_results = data.get("results", {}).get(task, {})
        if task_results:
            merged_results[task] = task_results
            print(f"  {task}: n={task_results.get('sample_len',0)} acc={task_results.get('acc,none',0):.4f}", file=sys.stderr)

    # ── compute averages ──
    avg_acc = 0
    avg_acc_norm = 0
    n_tasks_acc = 0
    n_tasks_norm = 0
    for task, res in merged_results.items():
        if "acc,none" in res:
            avg_acc += res["acc,none"]
            n_tasks_acc += 1
        if "acc_norm,none" in res:
            avg_acc_norm += res["acc_norm,none"]
            n_tasks_norm += 1

    if n_tasks_acc > 0:
        merged_results["__average__"] = {
            "name": "average",
            "alias": "average",
            "acc,none": avg_acc / n_tasks_acc,
        }
        print(f"  AVERAGE acc: {avg_acc / n_tasks_acc:.4f} ({n_tasks_acc} tasks)", file=sys.stderr)
    if n_tasks_norm > 0:
        if "__average__" not in merged_results:
            merged_results["__average__"] = {}
        merged_results["__average__"]["acc_norm,none"] = avg_acc_norm / n_tasks_norm
        print(f"  AVERAGE acc_norm: {avg_acc_norm / n_tasks_norm:.4f} ({n_tasks_norm} tasks)", file=sys.stderr)

    # ── save merged results ──
    output = {
        "results": merged_results,
        "n_samples": sum(r.get("sample_len", 0) for r in merged_results.values() if r.get("name") != "average"),
    }
    out_file = os.path.join(out_dir, "results.json")
    with open(out_file, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nMerged results saved to {out_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
