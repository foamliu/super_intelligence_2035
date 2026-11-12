#!/usr/bin/env bash
# baize_posttrain_5run_eval.sh — 5-run EDA-Eval-PyAether Pass@1 evaluation
#
# 冻结协议（总纲 §2）：158 任务 / Pass@1 / 2500s/任务 / 单 trace / 5-run / -p 8 -n
#
# 用法：
#   bash baize_posttrain_5run_eval.sh --dry-run
#   bash baize_posttrain_5run_eval.sh --endpoint http://127.0.0.1:8096/v1 --model minicpm5-2b-sft-v39-final --label step105 --run 2
#   bash baize_posttrain_5run_eval.sh --endpoint http://127.0.0.1:8096/v1 --model minicpm5-2b-sft-v39-final --label step105 --run-all
set -uo pipefail

EDA_BASE="/home/app.e0031982/code/eda_fastmcp"
PROVIDERS_JSON="$HOME/.cline/data/settings/providers.json"
VENV_PYTHON="$EDA_BASE/.venv/bin/python"
RESULTS_DIR="/tmp/posttrain_5run_eval"

ENDPOINT=""; MODEL=""; LABEL=""; RUN_NUM=""; RUN_ALL=0; DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --endpoint) ENDPOINT="$2"; shift ;;
    --model) MODEL="$2"; shift ;;
    --label) LABEL="$2"; shift ;;
    --run) RUN_NUM="$2"; shift ;;
    --run-all) RUN_ALL=1 ;;
    *) echo "未知参数: $1" ;;
  esac
  shift
done

if [ -z "$ENDPOINT" ] || [ -z "$MODEL" ] || [ -z "$LABEL" ]; then
  echo "用法: $0 --endpoint <URL> --model <MODEL_ID> --label <LABEL> [--run N | --run-all]"
  exit 1
fi

mkdir -p "$RESULTS_DIR/$LABEL"
echo "===== 5-run Eval @ $(date '+%F %T') ====="
echo "  endpoint=$ENDPOINT model=$MODEL label=$LABEL"
echo "  protocol: 158 tasks, Pass@1, 2500s, 5-run mean±std, -p 8 -n"
echo "===== End ====="

[ $DRY_RUN = 1 ] && { echo "[dry-run] 不执行。"; exit 0; }

run_single() {
  local run_n="$1"
  local batch_id="${LABEL}_run${run_n}_$(date '+%Y_%m%d_%H%M%S')"
  local run_dir="$RESULTS_DIR/$LABEL/run${run_n}"
  mkdir -p "$run_dir"
  echo "[run $run_n] === START $(date '+%F %T') === batch_id=$batch_id"

  # 1. Save and update providers.json
  cp "$PROVIDERS_JSON" "$run_dir/providers.json.bak"
  python3 -c "
import json
cfg = {'version':1,'lastUsedProvider':'openai-compatible','providers':{'openai-compatible':{'settings':{'provider':'openai-compatible','apiKey':'dummy-key','model':'$MODEL','baseUrl':'$ENDPOINT'},'updatedAt':'2026-11-13T06:00:00.000Z','tokenSource':'migration'}}}
json.dump(cfg, open('$PROVIDERS_JSON','w'), indent=2)
"
  echo "[run $run_n] providers.json → $ENDPOINT / $MODEL"

  # 2. Code generation (PYTHON env var required: system lacks bare 'python')
  echo "[run $run_n] code-gen starting..."
  cd "$EDA_BASE"
  export PYTHON="$VENV_PYTHON"
  export PATH="$HOME/.bun/bin:$PATH"
  BATCH_ID="$batch_id" bash scripts/run_cline_script.sh -p 8 -n > "$run_dir/codegen.log" 2>&1
  echo "[run $run_n] code-gen done (rc=$?) $(date '+%F %T')"

  # 3. Restore providers.json
  cp "$run_dir/providers.json.bak" "$PROVIDERS_JSON"
  echo "[run $run_n] providers.json restored"

  # 4. Find JSONL
  local jsonl="$HOME/eda_code_eval/completed_code_generation_${batch_id}.jsonl"
  [ ! -f "$jsonl" ] && jsonl=$(ls -t "$HOME/eda_code_eval/completed_code_generation_${LABEL}_run${run_n}_"*.jsonl 2>/dev/null | head -1)
  if [ -z "$jsonl" ]; then echo "[run $run_n] FATAL: no JSONL"; return 1; fi
  cp "$jsonl" "$run_dir/completed_code_generation.jsonl"
  echo "[run $run_n] JSONL: $jsonl"

  # 5. Sandbox eval
  echo "[run $run_n] sandbox eval starting..."
  PYTHON="$VENV_PYTHON" python scripts/run_eval.py --generations "$jsonl" > "$run_dir/eval.log" 2>&1
  echo "[run $run_n] eval done (rc=$?) $(date '+%F %T')"

  # 6. Copy final report
  local fr=$(find "$HOME/eda_code_eval" -name 'final_report*.json' -newer "$jsonl" 2>/dev/null | head -1)
  if [ -n "$fr" ]; then
    cp "$fr" "$run_dir/final_report.json"
    echo "[run $run_n] Pass@1: $(python3 -c "import json;d=json.load(open('$run_dir/final_report.json'));print(d.get('pass_rate',d.get('pass@1','N/A')))" 2>/dev/null || echo N/A)"
  else echo "[run $run_n] WARNING: no final_report.json"; fi
  echo "[run $run_n] === END ==="
  return 0
}

if [ $RUN_ALL = 1 ]; then
  for i in 1 2 3 4 5; do run_single "$i" || echo "[run $i] FAILED"; done
  echo "=== Computing 5-run mean±std ==="
  python3 -c "
import json,os,statistics
r=[]
for i in range(1,6):
  f='$RESULTS_DIR/$LABEL/run'+str(i)+'/final_report.json'
  if os.path.exists(f):
    d=json.load(open(f));p=d.get('pass_rate',d.get('pass@1'))
    if p is not None: r.append(float(p)); print(f'Run {i}: {p}')
if len(r)>=2: print(f'5-run mean±std: {statistics.mean(r):.4f}±{statistics.stdev(r):.4f} ({len(r)}/5)')
elif len(r)==1: print(f'1 run: {r[0]}')
else: print('No results yet')
" 2>&1
elif [ -n "$RUN_NUM" ]; then run_single "$RUN_NUM"
else echo "Specify --run N or --run-all"; exit 1; fi
