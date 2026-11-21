#!/usr/bin/env bash
# 04_run_one_ckpt.sh — 单个 ckpt 一条龙：转换 -> 起服 -> 分词对拍 -> 评测 -> 收服
#
# 用法:
#   bash 04_run_one_ckpt.sh <iter> [--limit N] [--tasks T1,T2] \
#        [--port 8080] [--parallel 2] [--threads 32] [--outtype f16] [--keep-server]
#
# 例（冒烟）:
#   bash 04_run_one_ckpt.sh 10000 --limit 100 --tasks sciq,piqa
# 例（全量 8 集 limit=500）:
#   bash 04_run_one_ckpt.sh 10000 --limit 500
set -euo pipefail

ITER="${1:?用法: bash 04_run_one_ckpt.sh <iter> [--limit N] [--tasks T1,T2]}"
shift

LIMIT_ARG=()
TASKS="arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande"
PORT="${PORT:-8080}"
PARALLEL="${PARALLEL:-2}"
THREADS="${THREADS:-32}"
OUTTYPE="${OUTTYPE:-f16}"
KEEP_SERVER="${KEEP_SERVER:-0}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --limit)       LIMIT_ARG=(--limit "$2"); shift 2 ;;
    --tasks)       TASKS="$2"; shift 2 ;;
    --port)        PORT="$2"; shift 2 ;;
    --parallel)    PARALLEL="$2"; shift 2 ;;
    --threads)     THREADS="$2"; shift 2 ;;
    --outtype)     OUTTYPE="$2"; shift 2 ;;
    --keep-server) KEEP_SERVER=1; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

BASE="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b"
HF_DIR="$BASE/hf_iter_${ITER}"
GGUF_DIR="${GGUF_DIR:-/nas_train/app.e0031982/models/baize2b_gguf}"
GGUF="$GGUF_DIR/bz2b-${ITER}-${OUTTYPE}.gguf"
OUT="$BASE/lm_eval_results/gguf_iter_${ITER}"
PY="${PY:-/nas_train/app.e0031982/miniforge3/envs/py310/bin/python}"
HERE="$(cd "$(dirname "$0")" && pwd)"

# 与 baize_cpu_lmeval.sh 对齐：离线 + p6_tf5（transformers 5.x 含 NemotronH）
export CUDA_VISIBLE_DEVICES=""
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_OFFLINE=1
export HF_HUB_OFFLINE=1
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"

[[ -d "$HF_DIR" ]] || { echo "FAIL: HF 目录不存在: $HF_DIR" >&2; exit 1; }
mkdir -p "$OUT" "$GGUF_DIR"

echo "============================================================"
echo "  ckpt      = $ITER"
echo "  hf_dir    = $HF_DIR"
echo "  gguf      = $GGUF"
echo "  output    = $OUT"
echo "  tasks     = $TASKS  limit=${LIMIT_ARG[*]:-full}"
echo "  port      = $PORT  parallel=$PARALLEL threads=$THREADS"
echo "  start     = $(date '+%F %T')"
echo "============================================================"

# 1) 转换（不存在才转）
if [[ ! -s "$GGUF" ]]; then
  bash "$HERE/01_convert_hf_to_gguf.sh" "$HF_DIR" "$GGUF" "$OUTTYPE"
else
  echo "[run] 复用已存在 GGUF: $(ls -lh "$GGUF" | awk '{print $5, $9}')"
fi

# 2) 起服（若已就绪则复用）
SERVER_STARTED=0
if curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
  echo "[run] 复用已运行 server: port=$PORT"
else
  WAIT_SECONDS="${WAIT_SECONDS:-300}" bash "$HERE/03_serve_llama_server.sh" "$GGUF" "$PORT" "$THREADS" "$PARALLEL"
  SERVER_STARTED=1
fi

cleanup() {
  if [[ "$SERVER_STARTED" == "1" && "$KEEP_SERVER" != "1" ]]; then
    local pidfile="/tmp/llamacpp_server_${PORT}.pid"
    if [[ -f "$pidfile" ]]; then
      echo "[run] 关闭 server pid=$(cat "$pidfile")"
      kill "$(cat "$pidfile")" 2>/dev/null || true
      sleep 2
      kill -9 "$(cat "$pidfile")" 2>/dev/null || true
      rm -f "$pidfile"
    fi
  fi
}
trap cleanup EXIT

# 3) API 契约自检 + 分词对拍（硬门槛；任一失败直接退出）
"$PY" "$HERE/06_server_selftest.py" --base-url "http://127.0.0.1:${PORT}"
"$PY" "$HERE/02_check_tokenizer.py" "$HF_DIR" --base-url "http://127.0.0.1:${PORT}"

# 4) 评测
nice -n 19 "$PY" "$HERE/gguf_lmeval_run.py" \
  --base-url "http://127.0.0.1:${PORT}" \
  --hf-dir "$HF_DIR" \
  --output "$OUT" \
  --gguf "$GGUF" \
  --tasks "$TASKS" \
  --parallel "$PARALLEL" \
  "${LIMIT_ARG[@]}"

echo "============================================================"
echo "  DONE ckpt=$ITER  $(date '+%F %T')"
echo "  results: $OUT/results.json"
echo "  meta   : $OUT/meta.json"
echo "============================================================"
