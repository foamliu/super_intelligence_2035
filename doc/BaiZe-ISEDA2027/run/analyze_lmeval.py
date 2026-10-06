#!/usr/bin/env python3
"""Analyze lm_eval results: per-task Spearman + noise assessment."""
import json
from scipy.stats import spearmanr
import numpy as np

RESULTS_PATH = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/topk_lmeval_results.json"

with open(RESULTS_PATH) as f:
    data = json.load(f)

results = data["results"]
bo_losses = data["bo_losses"]
tids = sorted([int(t) for t in results.keys()])

print("=== Per-task Spearman ===")
tasks = list(results[str(tids[0])]["per_task"].keys())
for task in tasks:
    losses = [bo_losses[str(t)] for t in tids]
    scores = [results[str(t)]["per_task"][task] for t in tids]
    rho, pval = spearmanr(losses, scores)
    scores_str = ", ".join(f"{s:.4f}" for s in scores)
    print(f"  {task:20s} rho={rho:+.4f} p={pval:.4f}  scores=[{scores_str}]")

print()
print("=== Overall ===")
losses = [bo_losses[str(t)] for t in tids]
avgs = [results[str(t)]["avg"] for t in tids]
rho, pval = spearmanr(losses, avgs)
print(f"  avg                 rho={rho:+.4f} p={pval:.4f}")
print()
print("=== Data table ===")
print(f"{'TID':>5} {'BO_loss':>10} {'lm_avg':>8} {'BO_rank':>8} {'lm_rank':>8}")
bo_ranks = np.argsort(np.argsort(losses)) + 1
lm_ranks = np.argsort(np.argsort(avgs)) + 1
for i, t in enumerate(tids):
    print(f"{t:>5} {losses[i]:>10.6f} {avgs[i]:>8.4f} {bo_ranks[i]:>8} {lm_ranks[i]:>8}")
print()
print(f"Score range: {min(avgs):.4f} - {max(avgs):.4f} (spread={max(avgs)-min(avgs):.4f})")
print(f"Loss range:  {min(losses):.6f} - {max(losses):.6f} (spread={max(losses)-min(losses):.6f})")
print()

# Check which tasks have signal above random
print("=== Task signal assessment ===")
for task in tasks:
    scores = [results[str(t)]["per_task"][task] for t in tids]
    avg_score = np.mean(scores)
    # Random baselines: arc_challenge=0.25 (4 choices), arc_easy=0.25, boolq=0.5,
    # hellaswag=0.25, openbookqa=0.25, piqa=0.5, sciq=0.25, winogrande=0.5
    baselines = {
        "arc_challenge": 0.25, "arc_easy": 0.25, "boolq": 0.5,
        "hellaswag": 0.25, "openbookqa": 0.25, "piqa": 0.5,
        "sciq": 0.25, "winogrande": 0.5,
    }
    baseline = baselines.get(task, 0.25)
    diff = avg_score - baseline
    print(f"  {task:20s} avg={avg_score:.4f} baseline={baseline:.2f} diff={diff:+.4f}")
