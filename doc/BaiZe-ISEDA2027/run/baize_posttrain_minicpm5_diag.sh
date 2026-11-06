#!/usr/bin/env bash
# baize_posttrain_minicpm5_diag.sh — MiniCPM5-2B 诊断评测启动脚本（P0 D1-D6 · 36% 侧）
#
# 用途：GPU 可用时用 vLLM 服务 MiniCPM5-2B，通过 cline CLI 跑 EDA-Eval-PyAether
#       全 harness 评测，生成轨迹后提取 D1-D6 诊断指标。
#
# 背景：P0 D1-D6 的 MiniCPM5-2B 36% 侧轨迹不在 .17 节点，但模型已下载到
#       /tmp/models/MiniCPM5-2B/（4.7GB, 2026-11-06）。本脚本在 GPU 释放后即可运行。
#
# 冻结协议：full 模式严格遵守 158/Pass@1/2500s/单trace/5-run/-p 8 -n
#   --quick 模式仅跑 10 任务用于快速 D1/D2/D6 预诊（非正式评测）
#
# 用法：
#   bash baize_posttrain_minicpm5_diag.sh --dry-run              # 打印配方
#   bash baize_posttrain_minicpm5_diag.sh --dry-run --quick      # 快速模式配方
#   bash baize_posttrain_minicpm5_diag.sh --quick                # 快速诊断(10任务,1run)
#   bash baize_posttrain_minicpm5_diag.sh --full                 # 完整诊断(158任务,5run)
#   bash baize_posttrain_minicpm5_diag.sh --full --gpu-ids 4,5   # 指定 GPU
#   bash baize_posttrain_minicpm5_diag.sh --extract-only         # 仅提取已有轨迹
#   bash baize_posttrain_minicpm5_diag.sh --vllm-only            # 仅启动 vLLM 服务
set -uo pipefail

MODEL_PATH="/tmp/models/MiniCPM5-2B"
EDA_BASE="$HOME/code/eda_fastmcp"
DRIVER="$EDA_BASE/pyAether-eval/run_cline_script.sh"
EVAL_PY="$EDA_BASE/scripts/run_eval.py"
TRACE_READER="$EDA_BASE/scripts/trace_reader.py"
DATASET="$EDA_BASE/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
EVAL_CODE_DIR="$HOME/eda_code_eval"
EXTRACT_SCRIPT="$(dirname "$(realpath "${BASH_SOURCE[0]}")")/pt_p0_minicpm5_extract.py"
VLLM_VENV="$HOME/code/vllm_venv"
VLLM_PORT=8866
SERVED_MODEL_NAME="minicpm5-2b"

N_RUNS=5; TASK_TIMEOUT=2500; PARALLEL=8; N_TASKS=158
QUICK_TASKS=10; QUICK_RUNS=1

MODE="full"; DRY_RUN=0; GPU_IDS=""; VLLM_ONLY=0; EXTRACT_ONLY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)      DRY_RUN=1 ;;
    --quick)        MODE="quick" ;;
    --full)         MODE="full" ;;
    --gpu-ids)      GPU_IDS="$2"; shift ;;
    --vllm-only)    VLLM_ONLY=1 ;;
    --extract-only) EXTRACT_ONLY=1 ;;
    --port)         VLLM_PORT="$2"; shift ;;
    --model-path)   MODEL_PATH="$2"; shift ;;
    *) echo "未知参数: $1" ;;
  esac
  shift
done

if [ "$MODE" = "quick" ]; then
  EFF_RUNS=$QUICK_RUNS; EFF_TASKS=$QUICK_TASKS; EVAL_LABEL="quick-diagnostic"
else
  EFF_RUNS=$N_RUNS; EFF_TASKS=$N_TASKS; EVAL_LABEL="full-diagnostic"
fi

cat <<EOF
===== MiniCPM5-2B 诊断评测配方 @ $(date '+%F %T') =====
  mode            : ${MODE} (${EVAL_LABEL})
  model_path      : ${MODEL_PATH}
  served_name     : ${SERVED_MODEL_NAME}
  vllm_port       : ${VLLM_PORT}
  vllm_venv       : ${VLLM_VENV}
  gpu_ids         : ${GPU_IDS:-auto}
  dataset         : ${DATASET} (${EFF_TASKS} tasks)
  driver          : ${DRIVER}
  n_runs          : ${EFF_RUNS}
  task_timeout    : ${TASK_TIMEOUT}s
  parallel        : -p ${PARALLEL} -n
  eval_code_dir   : ${EVAL_CODE_DIR}
  trace_reader    : ${TRACE_READER}
  extract_script  : ${EXTRACT_SCRIPT}
  full 模式冻结协议: 158/Pass@1/2500s/单trace/5-run/-p 8 -n
===== END RECIPE =====
EOF

[ $DRY_RUN = 1 ] && { echo "[dry-run] 配方已打印，不执行。"; exit 0; }

echo "[check] 前置检查..."
if [ "$EXTRACT_ONLY" = 0 ]; then
  [ -f "$MODEL_PATH/model-00000-of-00001.safetensors" ] || { echo "❌ 模型文件不存在: $MODEL_PATH"; exit 1; }
  [ -f "$DRIVER" ] || { echo "❌ 评测 driver 不存在: $DRIVER"; exit 1; }
  [ -f "$DATASET" ] || { echo "❌ 158-case 数据集不存在: $DATASET"; exit 1; }
  command -v cline >/dev/null 2>&1 || {
    export PATH="$HOME/.bun/bin:$PATH"
    command -v cline >/dev/null 2>&1 || { echo "❌ cline 未在 PATH"; exit 1; }
  }
fi

if [ "$EXTRACT_ONLY" = 1 ]; then
  echo "[extract-only] 跳过服务+评测，直接提取 D1-D6..."
  [ -f "$EXTRACT_SCRIPT" ] || { echo "❌ 提取脚本不存在: $EXTRACT_SCRIPT"; exit 1; }
  PYTHON_BIN="$EDA_BASE/.venv/bin/python"
  [ -x "$PYTHON_BIN" ] || PYTHON_BIN="python3"
  "$PYTHON_BIN" "$EXTRACT_SCRIPT" --eval-dir "$EVAL_CODE_DIR" --dataset "$DATASET" --trace-reader "$TRACE_READER" --eda-base "$EDA_BASE"
  exit $?
fi

echo "[step1] 检查/创建 vLLM 虚拟环境..."
if [ ! -d "$VLLM_VENV" ]; then
  echo "  创建 venv: $VLLM_VENV"
  python3 -m venv "$VLLM_VENV" || { echo "❌ venv 创建失败"; exit 1; }
  "$VLLM_VENV/bin/pip" install --upgrade pip wheel
  echo "  安装 vLLM（可能需要数分钟）..."
  "$VLLM_VENV/bin/pip" install vllm || { echo "❌ vLLM 安装失败"; exit 1; }
else
  echo "  venv 已存在"
  "$VLLM_VENV/bin/python" -c "import vllm" 2>/dev/null || {
    echo "  vLLM 未安装，正在安装..."
    "$VLLM_VENV/bin/pip" install vllm || { echo "❌ vLLM 安装失败"; exit 1; }
  }
fi
VLLM_BIN="$VLLM_VENV/bin/vllm"
VLLM_PY="$VLLM_VENV/bin/python"

ENDPOINT="http://127.0.0.1:${VLLM_PORT}/v1"
GPU_FLAG=""
[ -n "$GPU_IDS" ] && GPU_FLAG="CUDA_VISIBLE_DEVICES=$GPU_IDS"

echo "[step2] 启动 vLLM 服务 MiniCPM5-2B..."
if curl -s "$ENDPOINT/v1/models" 2>/dev/null | grep -q "$SERVED_MODEL_NAME"; then
  echo "  vLLM 已在运行，跳过启动"
else
  mkdir -p "$EVAL_CODE_DIR"
  eval "$GPU_FLAG $VLLM_BIN serve '$MODEL_PATH' \
    --served-model-name '$SERVED_MODEL_NAME' \
    --port '$VLLM_PORT' --dtype bfloat16 \
    --max-model-len 32768 --gpu-memory-utilization 0.85 \
    --trust-remote-code" > "$EVAL_CODE_DIR/vllm_serve.log" 2>&1 &
  VLLM_PID=$!
  echo "  vLLM PID: $VLLM_PID, 等待就绪..."
  READY=0
  for i in $(seq 1 60); do
    sleep 5
    curl -s "$ENDPOINT/v1/models" 2>/dev/null | grep -q "$SERVED_MODEL_NAME" && { READY=1; break; }
    echo "  [$i/60] 等待中..."
  done
  [ $READY = 0 ] && { echo "❌ vLLM 超时(300s)，见 $EVAL_CODE_DIR/vllm_serve.log"; kill $VLLM_PID 2>/dev/null; exit 1; }
  echo "  ✅ vLLM 就绪: $ENDPOINT"
fi

[ $VLLM_ONLY = 1 ] && { echo "[vllm-only] 服务已启动，退出。"; exit 0; }

echo "[step3] 配置 cline auth..."
CLINE_AUTH_BACKUP="$EVAL_CODE_DIR/cline_auth_backup_$(date '+%s')"
mkdir -p "$CLINE_AUTH_BACKUP"
cp -r "$HOME/.cline/data/settings" "$CLINE_AUTH_BACKUP/" 2>/dev/null || true
cline auth -p openai -k "sk-vllm-placeholder" -b "$ENDPOINT" -m "$SERVED_MODEL_NAME" || { echo "❌ cline auth 失败"; exit 1; }
echo "  ✅ cline auth 配置完成"

echo "[step4] 运行 EDA-Eval-PyAether 评测 (${MODE} 模式)..."
BATCH_ID="minicpm5_diag_$(date '+%Y_%m%d_%H%M%S')"
SUMMARY_FILE="$EVAL_CODE_DIR/${BATCH_ID}_summary.txt"
echo "===== MiniCPM5-2B 诊断评测 START @ $(date '+%F %T') mode=${MODE} =====" | tee "$SUMMARY_FILE"

for run in $(seq 1 "$EFF_RUNS"); do
  echo "[eval] run ${run}/${EFF_RUNS} @ $(date '+%T')" | tee -a "$SUMMARY_FILE"
  export BATCH_ID="${BATCH_ID}_run${run}"
  export EVAL_ROOT_DIR="$EVAL_CODE_DIR"
  if [ "$MODE" = "quick" ]; then
    QUICK_DATASET="/tmp/minicpm5_quick_dataset.jsonl"
    head -"$QUICK_TASKS" "$DATASET" > "$QUICK_DATASET"
    CONFIG_FILE="$EDA_BASE/pyAether-eval/config.yaml"
    cp "$CONFIG_FILE" "$CONFIG_FILE.bak"
    sed -i "s|benchmark_file:.*|benchmark_file: \"$QUICK_DATASET\"|" "$CONFIG_FILE"
    bash "$DRIVER" > "$EVAL_CODE_DIR/${BATCH_ID}_run${run}_driver.log" 2>&1 || echo "  ❌ run ${run} 失败" | tee -a "$SUMMARY_FILE"
    cp "$CONFIG_FILE.bak" "$CONFIG_FILE"; rm -f "$CONFIG_FILE.bak"
  else
    bash "$DRIVER" > "$EVAL_CODE_DIR/${BATCH_ID}_run${run}_driver.log" 2>&1 || echo "  ❌ run ${run} 失败" | tee -a "$SUMMARY_FILE"
  fi
  echo "  run ${run} 完成" | tee -a "$SUMMARY_FILE"
done
echo "===== END @ $(date '+%F %T') =====" | tee -a "$SUMMARY_FILE"

echo "[step5] 提取 D1-D6..."
if [ -f "$EXTRACT_SCRIPT" ]; then
  "$VLLM_PY" "$EXTRACT_SCRIPT" --eval-dir "$EVAL_CODE_DIR" --dataset "$DATASET" --trace-reader "$TRACE_READER" --eda-base "$EDA_BASE" --output "$EVAL_CODE_DIR/minicpm5_d1d6_results.json" | tee -a "$SUMMARY_FILE"
  echo "  ✅ D1-D6 → $EVAL_CODE_DIR/minicpm5_d1d6_results.json"
else
  echo "  ⚠️ 提取脚本不存在: $EXTRACT_SCRIPT"
fi

echo "[done] 结果: $EVAL_CODE_DIR | 汇总: $SUMMARY_FILE"
echo "  停止 vLLM: kill \$(pgrep -f 'vllm serve.*$SERVED_MODEL_NAME')"
