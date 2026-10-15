#!/usr/bin/env python3
"""Collect lm-eval results from output directory and produce p8_eval_summary.json.
Usage: python collect_eval_summary.py <output_dir> <label> <tokens_B>
"""
import json, os, glob, sys

def find_result_files(base_dir, prefix):
    """Find results JSON files in cs_*/cx_* subdirectories."""
    results = {}
    pattern = os.path.join(base_dir, f'{prefix}*', '**', 'results_*.json')
    for f in sorted(glob.glob(pattern, recursive=True)):
        try:
            with open(f) as fh:
                data = json.load(fh)
            for task_name, task_data in data.get('results', {}).items():
                if task_name == 'model_name':
                    continue
                results[task_name] = task_data
        except Exception as e:
            print(f"WARN: failed to parse {f}: {e}")
    return results

def extract_cs8(results):
    """Extract Common8 scores using acc_norm where available, acc otherwise."""
    cs_tasks = {
        'openbookqa': 'acc_norm',
        'arc_easy': 'acc_norm',
        'boolq': 'acc',
        'arc_challenge': 'acc_norm',
        'hellaswag': 'acc_norm',
        'piqa': 'acc_norm',
        'sciq': 'acc_norm',
        'winogrande': 'acc',
    }
    scores = {}
    errors = []
    for task, metric in cs_tasks.items():
        key = f'{metric},none'
        if task in results and key in results[task]:
            scores[task] = results[task][key]
        elif task in results and 'acc,none' in results[task]:
            # Fallback to acc if acc_norm not available
            scores[task] = results[task]['acc,none']
        else:
            errors.append(f'cs_{task}: no result')
    return scores, errors

def extract_complex6(results):
    """Extract Complex6 scores."""
    cx_tasks = {
        'gsm8k': 'acc,none',
        'hendrycks_math500': 'exact_match,flexible-extract',
        'mmlu': 'acc,none',
        'bbh_zeroshot': 'exact_match,flexible-extract',
        'humaneval': 'pass@1,none',
        'mbpp': 'pass@1,none',
    }
    scores = {}
    errors = []
    for task, metric in cx_tasks.items():
        if task in results and metric in results[task]:
            scores[task] = results[task][metric]
        else:
            # Try alternative metrics
            if task in results:
                for k in results[task]:
                    if 'exact_match' in k or 'acc' in k or 'pass' in k:
                        scores[task] = results[task][k]
                        break
                else:
                    scores[task] = None
                    errors.append(f'cx_{task}: no result file')
            else:
                scores[task] = None
                errors.append(f'cx_{task}: no result file')
    return scores, errors

def main():
    if len(sys.argv) < 4:
        print("Usage: python collect_eval_summary.py <output_dir> <label> <tokens_B>")
        sys.exit(1)
    
    out_dir = sys.argv[1]
    label = sys.argv[2]
    tokens_b = float(sys.argv[3])
    
    # Find all result files
    cs_results = find_result_files(out_dir, 'cs_')
    cx_results = find_result_files(out_dir, 'cx_')
    
    cs_scores, cs_errors = extract_cs8(cs_results)
    cx_scores, cx_errors = extract_complex6(cx_results)
    
    all_errors = cs_errors + cx_errors
    
    cs_avg = sum(cs_scores.values()) / len(cs_scores) if cs_scores and len(cs_scores) == 8 else None
    cx_valid = [v for v in cx_scores.values() if v is not None]
    cx_avg = sum(cx_valid) / len(cx_valid) if len(cx_valid) == 6 else None
    
    summary = {
        'common_sense': cs_scores,
        'complex': cx_scores,
        'errors': all_errors,
        'common_sense_avg': cs_avg,
        'complex_avg': cx_avg,
        'label': label,
        'tokens_B': tokens_b,
    }
    
    out_path = os.path.join(out_dir, 'p8_eval_summary.json')
    with open(out_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"  {label} ({tokens_b}B tokens)")
    print(f"{'='*60}")
    print(f"  Common8 Avg: {cs_avg*100:.2f}%" if cs_avg else "  Common8 Avg: N/A")
    if cs_scores:
        for t in ['hellaswag', 'arc_easy', 'boolq', 'arc_challenge', 'sciq', 'piqa', 'winogrande', 'openbookqa']:
            v = cs_scores.get(t)
            print(f"    {t:20s}: {v*100:.2f}%" if isinstance(v, float) else f"    {t:20s}: {v}")
    print(f"  Complex6 Avg: {cx_avg*100:.2f}%" if cx_avg else "  Complex6 Avg: N/A (incomplete)")
    if cx_scores:
        for t in ['gsm8k', 'hendrycks_math500', 'mmlu', 'bbh_zeroshot', 'humaneval', 'mbpp']:
            v = cx_scores.get(t)
            print(f"    {t:20s}: {v*100:.2f}%" if isinstance(v, float) else f"    {t:20s}: {v}")
    if all_errors:
        print(f"  Errors: {all_errors}")
    print(f"\n  Summary saved to: {out_path}")

if __name__ == '__main__':
    main()
