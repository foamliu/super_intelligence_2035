#!/usr/bin/env bash
# baize_posttrain_phase1_baseline.sh — BaiZe Stage(ii) Phase 1: 三模型基线评测
#
# 目标（13:40 用户令 Phase 1）：用 EDA-Eval-PyAether 158 任务，同口径横评三个模型，5-run mean±std。
#   - MiniCPM5-2B  : vLLM serve localhost:8098 (GPU4)
#   - Qwen3.8-27B  : root SGLang localhost:8099 (GPU0-3，不可动)
#   - DeepSeek 云端 : agi-gateway.cxmt.com (glm-5.2 替身)
#
# 冻结协议（总纲 §2）：158 任务 / Pass@1 / 2500s/任务 / 单 trace / 5-run / -p 8 -n。
# 评测资产（总纲 §3）：
#   driver   : ~/code/eda_fastmcp/scripts/run_cline_script.sh   (-p 8 -n)
#   scorer   : ~/code/eda_fastmcp/scripts/run_eval.py            (--latest 1)
#   dataset  : ~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl
#   MCP srv  : localhost:18888/sse (search_apis/get_api_details + run_code→sandbox)
#   sandbox  : 10.129.32.75:8667 (pyAether 代码执行，Phase 1 硬依赖)
#
# 交付物（里程碑报告）：reports/report_posttrain_baseline_3model_zh.html
#
# 用法：
#   bash baize_posttrain_phase1_baseline.sh --dry-run              # 打印配方+前置检查
#   bash baize_posttrain_phase1_baseline.sh --smoke                # 1模型×1run×3任务
#   bash baize_posttrain_phase1_baseline.sh --backbone minicpm5    # 单模型 5-run
#   bash baize_posttrain_phase1_baseline.sh                        # 三模型×5-run 全量
set -uo pipefail

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
source "$SCRIPT_DIR/baize_posttrain_paths.sh"

EDA_BASE="$BAIZE_EDA_BASE"
DRIVER="$EDA_BASE/scripts/run_cline_script.sh"
EVAL_PY="$EDA_BASE/scripts/run_eval.py"
DATASET="$EDA_BASE/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
MCP_PORT=18888
SANDBOX_HOST="${SANDBOX_HOST:-10.129.32.75}"
SANDBOX_PORT="${SANDBOX_PORT_HTTP:-8667}"
EVAL_ROOT="$HOME/eda_code_eval"
VENV_PY="$EDA_BASE/.venv/bin/python"

N_RUNS=5
PARALLEL=8
N_TASKS=158
SMOKE_TASKS="001,002,003"

declare -A BB_NAME BB_ENDPOINT BB_MODEL BB_KEY
BB_NAME[minicpm5]="MiniCPM5-2B"
BB_ENDPOINT[minicpm5]="http://localhost:8098/v1"
BB_MODEL[minicpm5]="minicpm5-2b"
BB_KEY[minicpm5]="sk-placeholder"

BB_NAME[qwen3827b]="Qwen3.8-27B"
BB_ENDPOINT[qwen3827b]="http://localhost:8099/v1"
BB_MODEL[qwen3827b]="qwen3.8-27b"
BB_KEY[qwen3827b]="sk-placeholder"

BB_NAME[deepseek_cloud]="DeepSeek-cloud-glm52"
BB_ENDPOINT[deepseek_cloud]="http://agi-gateway.cxmt.com/cloud/v1"
BB_MODEL[deepseek_cloud]="glm-5.2"
BB_KEY[deepseek_cloud]="02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23"

DRY_RUN=0
SMOKE=0
BACKBONE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --smoke) SMOKE=1; N_RUNS=1; PARALLEL=3 ;;
    --backbone) BACKBONE="$2"; shift ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
  shift
done

if [ -z "$BACKBONE" ] && [ "$SMOKE" = 0 ]; then
  BACKBONES="minicpm5 qwen3827b deepseek_cloud"
elif [ -z "$BACKBONE" ] && [ "$SMOKE" = 1 ]; then
  BACKBONES="minicpm5"
else
  BACKBONES="$BACKBONE"
fi

check_port() { timeout 3 bash -c "echo > /dev/tcp/$1/$2" 2>/dev/null; }

print_recipe() {
  echo "===== BaiZe Phase 1 Baseline — EVAL RECIPE @ $(date '+%F %T') ====="
  echo "  frozen protocol : 158 tasks / Pass@1 / 2500s/task / single-trace / ${N_RUNS}-run / -p ${PARALLEL} -n"
  echo "  driver          : $DRIVER"
  echo "  scorer          : $EVAL_PY"
  echo "  dataset         : $DATASET (${N_TASKS} tasks)"
  echo "  MCP server      : localhost:${MCP_PORT}/sse"
  echo "  sandbox         : ${SANDBOX_HOST}:${SANDBOX_PORT} (pyAether code execution)"
  echo "  venv python     : $VENV_PY"
  echo "  eval root       : $EVAL_ROOT"
  echo "  backbones       : ${BACKBONES}"
  [ "$SMOKE" = 1 ] && echo "  mode            : SMOKE (${SMOKE_TASKS}, 1 run, p=${PARALLEL})"
  echo "  milestones      : M1=50% M2=65% M3=75% M4=85%+ (pre-registered)"
  echo "  controls        : only backbone changes; retrieval/sandbox/anti-cheat/scaffold identical"
  echo "===== END RECIPE ====="
}

preflight() {
  local fail=0
  echo "[preflight] 检查评测资产..."
  [ -f "$DATASET" ] && echo "  OK dataset: $DATASET" || { echo "  FAIL dataset: $DATASET"; fail=1; }
  [ -f "$DRIVER" ] && echo "  OK driver: $DRIVER" || { echo "  FAIL driver: $DRIVER"; fail=1; }
  [ -f "$EVAL_PY" ] && echo "  OK scorer: $EVAL_PY" || { echo "  FAIL scorer: $EVAL_PY"; fail=1; }
  [ -x "$VENV_PY" ] && echo "  OK venv: $VENV_PY" || { echo "  FAIL venv: $VENV_PY"; fail=1; }
  command -v cline >/dev/null 2>&1 && echo "  OK cline: $(command -v cline)" || { echo "  FAIL cline not in PATH"; fail=1; }

  if check_port 127.0.0.1 $MCP_PORT; then
    echo "  OK MCP server: localhost:${MCP_PORT}"
  else
    echo "  WARN MCP server: localhost:${MCP_PORT} unreachable — start: cd $EDA_BASE && .venv/bin/python main.py"
    fail=1
  fi

  if check_port "$SANDBOX_HOST" "$SANDBOX_PORT"; then
    echo "  OK sandbox: ${SANDBOX_HOST}:${SANDBOX_PORT}"
  else
    echo "  BLOCKED sandbox: ${SANDBOX_HOST}:${SANDBOX_PORT} unreachable — Phase 1 scoring impossible!"
    echo "    unlock-A: ops restart sandbox service on ${SANDBOX_HOST} / open ports"
    echo "    unlock-B: any host H with pyAether installed + set .env SANDBOX_HOST=H"
    fail=1
  fi

  for bb in $BACKBONES; do
    local ep="${BB_ENDPOINT[$bb]}"
    local hp=$(echo "$ep" | sed 's|https://||;s|http://||;s|/v1||;s|/cloud||')
    local h="${hp%%:*}"
    local p="${hp##*:}"
    [ "$h" = "$p" ] && p=80
    if check_port "$h" "$p"; then
      echo "  OK backbone ${BB_NAME[$bb]}: ${ep}"
    else
      echo "  WARN backbone ${BB_NAME[$bb]}: ${ep} unreachable"
      fail=1
    fi
  done
  return $fail
}

run_backbone() {
  local bb="$1"
  local name="${BB_NAME[$bb]}" ep="${BB_ENDPOINT[$bb]}" model="${BB_MODEL[$bb]}" key="${BB_KEY[$bb]}"
  local out_dir="$EVAL_ROOT/phase1_baseline/${bb}"
  mkdir -p "$out_dir"
  local sum="$out_dir/eval_summary.txt"

  echo ""
  echo "========== backbone=${name} endpoint=${ep} model=${model} =========="
  echo "===== Phase 1 ${N_RUNS}-run START @ $(date '+%F %T') backbone=${name} =====" | tee "$sum"

  echo "[auth] cline auth -p openai -b ${ep} -m ${model}"
  cline auth -p openai -k "$key" -b "$ep" -m "$model" || {
    echo "  FAIL cline auth for ${name}" | tee -a "$sum"; return 1; }

  local task_flag=""
  [ "$SMOKE" = 1 ] && task_flag="-t ${SMOKE_TASKS}"

  for run in $(seq 1 "$N_RUNS"); do
    echo "[run ${run}/${N_RUNS}] @ $(date '+%T') backbone=${name}"
    local gen_log="$out_dir/run_${run}_gen.log"
    cd "$EDA_BASE"
    bash "$DRIVER" -p "$PARALLEL" -n $task_flag > "$gen_log" 2>&1
    local gen_rc=$?
    cd - >/dev/null
    if [ $gen_rc -ne 0 ]; then
      echo "  FAIL run ${run} gen (rc=${gen_rc}), see $gen_log" | tee -a "$sum"; continue; fi

    local gen_file=$(ls -t "$EVAL_ROOT"/completed_code_generation_*.jsonl 2>/dev/null | head -1)
    [ -z "$gen_file" ] && gen_file=$(find "$EVAL_ROOT" -name "completed_code_generation_*.jsonl" -newer "$sum" 2>/dev/null | head -1)
    [ -z "$gen_file" ] && { echo "  WARN run ${run} no generation output" | tee -a "$sum"; continue; }
    echo "  [gen] output: $(basename "$gen_file")"

    local eval_log="$out_dir/run_${run}_eval.log"
    cd "$EDA_BASE"
    "$VENV_PY" "$EVAL_PY" --latest 1 > "$eval_log" 2>&1
    local eval_rc=$?
    cd - >/dev/null
    if [ $eval_rc -ne 0 ]; then
      echo "  FAIL run ${run} eval (rc=${eval_rc}), see $eval_log" | tee -a "$sum"; continue; fi

    local rep=$(find "$EVAL_ROOT" -name "final_report.json" -newer "$gen_file" 2>/dev/null | head -1)
    [ -z "$rep" ] && rep=$(ls -t "$EVAL_ROOT"/final_report.json 2>/dev/null | head -1)
    local pass=$("$VENV_PY" -c "import json;d=json.load(open('$rep'));print(d.get('pass_rate',d.get('pass@1','N/A')))" 2>/dev/null)
    echo "  run ${run}: pass@1=${pass}" | tee -a "$sum"
    [ -f "$rep" ] && cp "$rep" "$out_dir/run_${run}_final_report.json"
  done

  "$VENV_PY" - "$out_dir" "$name" <<'PYEOF' | tee -a "$sum"
import json, sys, glob, statistics
out_dir, name = sys.argv[1], sys.argv[2]
rates = []
for rp in sorted(glob.glob(f"{out_dir}/run_*_final_report.json")):
    try:
        d = json.load(open(rp))
        r = d.get("pass_rate", d.get("pass@1"))
        if r is not None:
            rates.append(float(r) if isinstance(r,(int,float)) else float(str(r).rstrip('%')))
    except Exception as e:
        print(f"  parse fail {rp}: {e}")
if rates:
    mean = statistics.mean(rates)
    std = statistics.pstdev(rates) if len(rates)>1 else 0.0
    print(f"===== AGGREGATE backbone={name} =====")
    print(f"  n_runs={len(rates)}  pass@1 mean={mean:.2f}%  std={std:.2f}%  runs={rates}")
else:
    print(f"  WARN {name}: no pass_rate available")
PYEOF
  echo "===== Phase 1 ${N_RUNS}-run END @ $(date '+%F %T') backbone=${name} =====" | tee -a "$sum"
}

print_recipe

if [ "$DRY_RUN" = 1 ]; then
  echo ""
  echo "[dry-run] 执行前置检查..."
  preflight || echo "[dry-run] 前置检查有失败项（见上）。"
  echo "[dry-run] 不执行评测。"
  exit 0
fi

preflight || { echo "FAIL 前置检查失败，Phase 1 无法启动。"; exit 1; }

echo ""
echo "[Phase 1] 开始三模型基线评测..."
for bb in $BACKBONES; do
  run_backbone "$bb"
done

echo ""
echo "[Phase 1] 全部完成。汇总: $EVAL_ROOT/phase1_baseline/*/eval_summary.txt"
echo "[Phase 1] 交付物: reports/report_posttrain_baseline_3model_zh.html"
