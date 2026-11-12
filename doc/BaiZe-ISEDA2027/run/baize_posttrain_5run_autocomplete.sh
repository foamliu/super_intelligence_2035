#!/usr/bin/env bash
# baize_posttrain_5run_autocomplete.sh — Wait for run 2 to finish, then run 3-5 + compute 5-run summary
#
# This script automates the remaining 5-run eval pipeline:
#   1. Wait for run 2 (PID from --wait-pid) to finish
#   2. Run runs 3, 4, 5 sequentially via baize_posttrain_5run_eval.sh --run N
#   3. Compute 5-run mean±std from all available final_report.json files
#   4. Save summary to /tmp/posttrain_5run_eval/step105/5run_summary.json
#
# Usage (background):
#   nohup bash baize_posttrain_5run_autocomplete.sh \
#     --wait-pid 1109190 \
#     --endpoint http://127.0.0.1:8096/v1 \
#     --model minicpm5-2b-sft-v39-final \
#     --label step105 \
#     > /tmp/posttrain_5run_autocomplete.log 2>&1 &
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EVAL_SCRIPT="$SCRIPT_DIR/baize_posttrain_5run_eval.sh"
RESULTS_DIR="/tmp/posttrain_5run_eval"

WAIT_PID=""; ENDPOINT=""; MODEL=""; LABEL=""
while [ $# -gt 0 ]; do
  case "$1" in
    --wait-pid) WAIT_PID="$2"; shift ;;
    --endpoint) ENDPOINT="$2"; shift ;;
    --model) MODEL="$2"; shift ;;
    --label) LABEL="$2"; shift ;;
    *) echo "未知参数: $1" ;;
  esac
  shift
done

if [ -z "$ENDPOINT" ] || [ -z "$MODEL" ] || [ -z "$LABEL" ]; then
  echo "用法: $0 --wait-pid <PID> --endpoint <URL> --model <MODEL_ID> --label <LABEL>"
  exit 1
fi

echo "===== 5-run Autocomplete @ $(date '+%F %T') ====="
echo "  wait-pid=$WAIT_PID endpoint=$ENDPOINT model=$MODEL label=$LABEL"
echo "  eval-script=$EVAL_SCRIPT"

# 1. Wait for run 2 to finish (if PID given and still alive)
if [ -n "$WAIT_PID" ]; then
  echo "[wait] Checking PID $WAIT_PID..."
  while kill -0 "$WAIT_PID" 2>/dev/null; do
    echo "[wait] PID $WAIT_PID still running ($(date '+%T'))... sleeping 60s"
    sleep 60
  done
  echo "[wait] PID $WAIT_PID finished at $(date '+%F %T')"
else
  echo "[wait] No --wait-pid given, proceeding immediately"
fi

# 2. Run runs 3, 4, 5 sequentially (skip if final_report.json already exists)
for run_n in 3 4 5; do
  run_dir="$RESULTS_DIR/$LABEL/run${run_n}"
  if [ -f "$run_dir/final_report.json" ]; then
    echo "[run $run_n] SKIP — final_report.json already exists"
    continue
  fi
  echo "[run $run_n] === START $(date '+%F %T') ==="
  bash "$EVAL_SCRIPT" --endpoint "$ENDPOINT" --model "$MODEL" --label "$LABEL" --run "$run_n" 2>&1
  echo "[run $run_n] === END $(date '+%F %T') ==="
done

# 3. Compute 5-run mean±std
echo "===== Computing 5-run summary @ $(date '+%F %T') ====="
python3 -c "
import json, os, statistics

results_dir = '$RESULTS_DIR/$LABEL'
runs = []
for i in range(1, 6):
    fr = os.path.join(results_dir, f'run{i}', 'final_report.json')
    if os.path.exists(fr):
        d = json.load(open(fr))
        p = d.get('pass_rate', d.get('pass@1'))
        passed = d.get('passed_tasks', d.get('passed', []))
        if p is not None:
            runs.append({'run': i, 'pass_rate': float(p), 'passed_tasks': passed})
            print(f'Run {i}: Pass@1 = {p}')

summary = {
    'label': '$LABEL',
    'model': '$MODEL',
    'endpoint': '$ENDPOINT',
    'timestamp': __import__('datetime').datetime.now().isoformat(),
    'total_runs': len(runs),
    'runs': runs,
}

if len(runs) >= 2:
    rates = [r['pass_rate'] for r in runs]
    mean = statistics.mean(rates)
    std = statistics.stdev(rates)
    summary['mean'] = mean
    summary['std'] = std
    summary['mean_pct'] = f'{mean*100:.1f}%'
    summary['std_pct'] = f'{std*100:.1f}%'
    print(f'\\n5-run mean +/- std: {mean*100:.1f}% +/- {std*100:.1f}% ({len(runs)}/5 runs)')

    # McNemar test: compare run1 vs run2+ (paired on same task set)
    # For 5-run, report per-run pass rates and intersection
    if len(runs) >= 2:
        all_passed = set()
        for r in runs:
            all_passed.update(r['passed_tasks'])
        always_pass = set(runs[0]['passed_tasks'])
        for r in runs[1:]:
            always_pass &= set(r['passed_tasks'])
        summary['always_pass_tasks'] = sorted(always_pass)
        summary['any_pass_tasks'] = sorted(all_passed)
        summary['any_pass_count'] = len(all_passed)
        summary['always_pass_count'] = len(always_pass)
        print(f'Always-pass (all runs): {len(always_pass)} tasks: {sorted(always_pass)}')
        print(f'Any-pass (at least 1 run): {len(all_passed)} tasks')
elif len(runs) == 1:
    summary['mean'] = runs[0]['pass_rate']
    print(f'\\n1 run: {runs[0][\"pass_rate\"]}')
else:
    print('No results yet')

out = os.path.join(results_dir, '5run_summary.json')
json.dump(summary, open(out, 'w'), indent=2, ensure_ascii=False)
print(f'\\nSummary saved to {out}')
" 2>&1

echo "===== Autocomplete DONE @ $(date '+%F %T') ====="
