#!/usr/bin/env python3
"""Collect P-8 intermediate checkpoint CS8 results and produce summary JSON."""
import json, os, glob

def find_results(result_dir):
    """Find all results JSON files in the output directory."""
    results = {}
    for f in glob.glob(os.path.join(result_dir, '**', 'results_*.json'), recursive=True):
        try:
            with open(f) as fh:
                data = json.load(fh)
            for task_name, task_data in data.get('results', {}).items():
                if task_name == 'model_name':
                    continue
                results[task_name] = {
                    'acc': task_data.get('acc,none'),
                    'acc_stderr': task_data.get('acc_stderr,none'),
                    'acc_norm': task_data.get('acc_norm,none'),
                    'acc_norm_stderr': task_data.get('acc_norm_stderr,none'),
                }
        except Exception as e:
            print(f"WARN: failed to parse {f}: {e}")
    return results

def compute_avg(results):
    """Compute raw acc avg (8 tasks, using acc for BoolQ/Winogrande, acc_norm for rest)."""
    raw_tasks = ['openbookqa', 'arc_easy', 'boolq', 'arc_challenge',
                 'hellaswag', 'piqa', 'sciq', 'winogrande']
    norm_tasks = {'openbookqa', 'arc_easy', 'arc_challenge', 'hellaswag', 'piqa', 'sciq'}

    vals = []
    per_task = {}
    for t in raw_tasks:
        if t not in results:
            return None, None
        if t in norm_tasks and results[t].get('acc_norm') is not None:
            v = results[t]['acc_norm']
        else:
            v = results[t].get('acc')
        if v is None:
            return None, None
        vals.append(v)
        per_task[t] = v

    avg = sum(vals) / len(vals) * 100
    return avg, per_task

def main():
    # P-8 intermediate checkpoints with token counts
    # P-8: 44.4B tokens / 10490 steps = 4.23M tokens/step
    # iter_N = N * 4.23M tokens
    checkpoints = [
        # (iter_name, tokens_B, label)
        ('iter_1049', 4.4,  'P-8 iter_1049 (4.4B)'),
        ('iter_3147', 13.2, 'P-8 iter_3147 (13.2B)'),
        ('iter_5245', 22.0, 'P-8 iter_5245 (22.0B)'),
        ('iter_7343', 30.8, 'P-8 iter_7343 (30.8B)'),
        ('iter_9441', 39.6, 'P-8 iter_9441 (39.6B)'),
    ]

    base = '/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p8_adamw/lm_eval_cs8'

    print("=" * 80)
    print("P-8 Intermediate Checkpoint Common8 Results Summary")
    print("=" * 80)

    all_data = []
    for iter_name, tokens, label in checkpoints:
        result_dir = os.path.join(base, iter_name)
        if not os.path.isdir(result_dir):
            print(f"\n[SKIP] {label}: no results dir")
            all_data.append({'name': iter_name, 'label': label, 'tokens': tokens, 'avg': None, 'per_task': {}})
            continue

        results = find_results(result_dir)
        if not results:
            print(f"\n[SKIP] {label}: no results found")
            all_data.append({'name': iter_name, 'label': label, 'tokens': tokens, 'avg': None, 'per_task': {}})
            continue

        avg, per_task = compute_avg(results)
        all_data.append({'name': iter_name, 'label': label, 'tokens': tokens, 'avg': avg, 'per_task': per_task or {}})

        print(f"\n[{label}]")
        if per_task:
            for t in ['arc_challenge', 'arc_easy', 'boolq', 'hellaswag', 'openbookqa', 'piqa', 'sciq', 'winogrande']:
                v = per_task.get(t, '?')
                print(f"  {t:20s}: {v*100:.2f}%" if isinstance(v, float) else f"  {t:20s}: {v}")
            print(f"  {'Avg':20s}: {avg:.2f}%")
        else:
            print("  (incomplete results)")

    # Also add P-8 final (44.4B tokens) if available
    final_dir = '/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p8_adamw/lm_eval_cs8'
    # Check for final results (non-iter directories)
    final_results = {}
    for f in glob.glob(os.path.join(final_dir, '**', 'results_*.json'), recursive=True):
        if '/iter_' in f:
            continue
        try:
            with open(f) as fh:
                data = json.load(fh)
            for task_name, task_data in data.get('results', {}).items():
                if task_name == 'model_name':
                    continue
                final_results[task_name] = {
                    'acc': task_data.get('acc,none'),
                    'acc_norm': task_data.get('acc_norm,none'),
                }
        except:
            pass

    if final_results:
        avg, per_task = compute_avg(final_results)
        if avg:
            all_data.append({'name': 'p8_final', 'label': 'P-8 final (44.4B)', 'tokens': 44.4, 'avg': avg, 'per_task': per_task or {}})
            print(f"\n[P-8 final (44.4B)]")
            if per_task:
                for t in ['arc_challenge', 'arc_easy', 'boolq', 'hellaswag', 'openbookqa', 'piqa', 'sciq', 'winogrande']:
                    v = per_task.get(t, '?')
                    print(f"  {t:20s}: {v*100:.2f}%" if isinstance(v, float) else f"  {t:20s}: {v}")
                print(f"  {'Avg':20s}: {avg:.2f}%")

    # Save JSON
    out_path = os.path.join(base, 'p8_cs8_summary.json')
    with open(out_path, 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"\nSummary saved to: {out_path}")

if __name__ == '__main__':
    main()
