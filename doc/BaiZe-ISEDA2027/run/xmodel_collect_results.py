#!/usr/bin/env python3
"""Collect lm-eval common8 results from Xmodel-2/2.5 checkpoints and produce summary."""
import json, os, glob, sys

def find_results(result_dir):
    """Find all results JSON files in the output directory."""
    results = {}
    for pattern in [os.path.join(result_dir, '**', 'results_*.json'),
                    os.path.join(result_dir, 'results_*.json')]:
        for f in glob.glob(pattern, recursive=True):
            try:
                with open(f) as fh:
                    data = json.load(fh)
                for task_name, task_data in data.get('results', {}).items():
                    if task_name == 'model_name': continue
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
    
    avg = sum(vals) / len(vals) * 100  # percentage
    return avg, per_task

def main():
    # Define checkpoint mapping
    checkpoints = [
        # (name, result_dir, tokens_B, label)
        # Token counts verified from papers:
        #   Xmodel-2: 3.93M tokens/step (arXiv:2412.19638, confirmed by news article:
        #     "批次大小为393万个token"; decay T=5000 steps = 20B tokens → 5000×3.93M≈20B)
        #   Xmodel-2.5: 13.2M tokens/step (arXiv:2511.19496)
        #     Paper Table 1: seq_len=3712; total=1.4T tokens; 106K total steps
        #     → 1.4T / 106000 = 13.2M tokens/step
        #     (Earlier "3712×480" was wrong: 3712 is seq_len not batch_size)
        ('xmodel2_s1_10000', None, 39.3,  'Xmodel-2 s1/10K (39.3B)'),
        ('xmodel2_s1_20000', None, 78.6,  'Xmodel-2 s1/20K (78.6B)'),
        ('xmodel2_s1_30000', None, 117.9, 'Xmodel-2 s1/30K (117.9B)'),
        ('xmodel2_s1_40000', None, 157.2, 'Xmodel-2 s1/40K (157.2B)'),
        ('xmodel2_final',    None, 1500.0, 'Xmodel-2 final (1.5T)'),
        ('xmodel25_step_2000',  None, 26.4,  'Xmodel-2.5 step 2K (26.4B)'),
        ('xmodel25_step_4000',  None, 52.8,  'Xmodel-2.5 step 4K (52.8B)'),
        ('xmodel25_step_6000',  None, 79.2,  'Xmodel-2.5 step 6K (79.2B)'),
        ('xmodel25_step_8000',  None, 105.6, 'Xmodel-2.5 step 8K (105.6B)'),
        ('xmodel25_step_10000', None, 132.0, 'Xmodel-2.5 step 10K (132B)'),
        ('xmodel25_step_18000', None, 237.6, 'Xmodel-2.5 step 18K (237.6B)'),
    ]
    
    base = '/nas_train/app.e0031982/code/BaiZe-ISEDA2027/xmodel_eval'
    eval_base = '/nas_train/app.e0031982/code/BaiZe-ISEDA2027/xmodel_eval/lm_eval_results'
    
    print("=" * 80)
    print("Xmodel-2 / Xmodel-2.5 Common8 Results Summary")
    print("=" * 80)
    
    all_data = []
    for name, _, tokens, label in checkpoints:
        result_dir = os.path.join(eval_base, name)
        if not os.path.isdir(result_dir):
            print(f"\n[SKIP] {label}: no results dir at {result_dir}")
            all_data.append({'name': name, 'label': label, 'tokens': tokens, 'avg': None, 'per_task': {}})
            continue
        
        results = find_results(result_dir)
        if not results:
            print(f"\n[SKIP] {label}: no results found")
            all_data.append({'name': name, 'label': label, 'tokens': tokens, 'avg': None, 'per_task': {}})
            continue
        
        avg, per_task = compute_avg(results)
        all_data.append({'name': name, 'label': label, 'tokens': tokens, 'avg': avg, 'per_task': per_task or {}})
        
        print(f"\n[{label}]")
        if per_task:
            for t in ['arc_challenge', 'arc_easy', 'boolq', 'hellaswag', 'openbookqa', 'piqa', 'sciq', 'winogrande']:
                v = per_task.get(t, '?')
                print(f"  {t:20s}: {v*100:.2f}%" if isinstance(v, float) else f"  {t:20s}: {v}")
            print(f"  {'Avg':20s}: {avg:.2f}%")
        else:
            print("  (incomplete results)")
    
    # Save JSON
    out_path = os.path.join(base, 'xmodel_common8_summary.json')
    with open(out_path, 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"\nSummary saved to: {out_path}")

if __name__ == '__main__':
    main()
