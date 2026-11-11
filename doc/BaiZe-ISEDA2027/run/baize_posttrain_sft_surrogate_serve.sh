#!/usr/bin/env bash
# baize_posttrain_sft_surrogate_serve.sh — Serve the Phase 2 surrogate SFT ckpt with vLLM
#
# Purpose: After baize_posttrain_sft_surrogate.sh finishes, the SFT checkpoint
#          (HF safetensors format, directly vLLM-serveable) is served as an
#          OpenAI-compatible endpoint. This is the bridge between SFT training
#          and EDA-Eval-PyAether evaluation (baize_posttrain_eval.sh).
#
# Model: MiniCPM5-2B SFT'd on R152 unified PyAether SFT parquet (1725 pairs).
#   Report results as: "替身预演，收益不可迁移到 BaiZe"
#
# GPU: Default GPU 6 (freed after SFT training on GPU 6/7).
#   🚫 Never touch GPU 0-3 (root SGLang Qwen3.8-27B on :8099).
#
# vLLM venv: /tmp/vllm_venv/bin/python (vLLM 0.7.3 + torch 2.5.1 + CUDA 12.4)
#   transformers MUST be 4.49.x — checked at launch.
#   ⚠️ venv in /tmp — lost on machine reboot, must rebuild.
#
# Usage:
#   bash baize_posttrain_sft_surrogate_serve.sh --dry-run       # print recipe only
#   bash baize_posttrain_sft_surrogate_serve.sh                 # serve latest ckpt on GPU6:8096
#   bash baize_posttrain_sft_surrogate_serve.sh --gpu 7 --port 8095
#   bash baize_posttrain_sft_surrogate_serve.sh --ckpt /path/to/global_step_72
#   bash baize_posttrain_sft_surrogate_serve.sh --status        # check if serve is running
#   bash baize_posttrain_sft_surrogate_serve.sh --stop          # stop the SFT ckpt serve
set -uo pipefail

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

# ============ config ============
VLLM_VENV="${VLLM_VENV:-/tmp/vllm_venv/bin/python}"
SFT_RUNS_DIR="$SCRIPT_DIR/sft_surrogate_runs/minicpm5_pyaether_v1"
GPU="${GPU:-6}"
PORT="${PORT:-8096}"
SERVED_NAME="${SERVED_NAME:-minicpm5-sft}"
GPU_MEM_UTIL="${GPU_MEM_UTIL:-0.85}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-32768}"
CKPT=""

# ============ arg parsing ============
DRY_RUN=0; STATUS_ONLY=0; STOP=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)  DRY_RUN=1 ;;
    --status)   STATUS_ONLY=1 ;;
    --stop)     STOP=1 ;;
    --gpu)      GPU="$2"; shift ;;
    --port)     PORT="$2"; shift ;;
    --ckpt)     CKPT="$2"; shift ;;
    --name)     SERVED_NAME="$2"; shift ;;
    --mem)      GPU_MEM_UTIL="$2"; shift ;;
    --max-len)  MAX_MODEL_LEN="$2"; shift ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
  shift
done

LOG_FILE="/tmp/vllm_sft_serve_gpu${GPU}.log"

# ============ --stop ============
if [ $STOP -eq 1 ]; then
  echo "[stop] Looking for vLLM serve on GPU${GPU} port ${PORT}..."
  PIDS=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader -i "$GPU" 2>/dev/null | tr -d ' ')
  if [ -z "$PIDS" ]; then
    echo "  No process on GPU${GPU}."
  else
    for pid in $PIDS; do
      cmd=$(ps -p "$pid" -o args= 2>/dev/null | head -c 200)
      if echo "$cmd" | grep -q "vllm.entrypoints.openai.api_server"; then
        echo "  Killing PID $pid on GPU${GPU}..."
        kill -TERM "$pid" 2>/dev/null || true; sleep 3
        kill -9 "$pid" 2>/dev/null || true
      else
        echo "  PID $pid on GPU${GPU} is not vLLM serve (skip): ${cmd:0:80}"
      fi
    done
  fi
  echo "[stop] Done. Verify: nvidia-smi -i $GPU"
  exit 0
fi

# ============ --status ============
if [ $STATUS_ONLY -eq 1 ]; then
  echo "[status] SFT ckpt serve on GPU${GPU} port ${PORT}:"
  if curl -s --max-time 3 "http://localhost:${PORT}/v1/models" | grep -q "$SERVED_NAME"; then
    echo "  ✅ Serve healthy — model: $SERVED_NAME"
    curl -s --max-time 3 "http://localhost:${PORT}/v1/models" | python3 -m json.tool 2>/dev/null || true
  else
    echo "  ❌ No response on :${PORT} (serve not running or wrong port)"
  fi
  MEM=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" 2>/dev/null)
  echo "  GPU${GPU} VRAM used: ${MEM:-?} MiB"
  exit 0
fi

# ============ find latest ckpt ============
if [ -z "$CKPT" ]; then
  if [ ! -d "$SFT_RUNS_DIR" ]; then
    echo "❌ SFT runs dir not found: $SFT_RUNS_DIR"
    echo "   Has the SFT training finished? Run baize_posttrain_sft_surrogate.sh first."
    exit 1
  fi
  # FIX R173: sort by extracted step number (numeric), not fragile `sort -t_ -k3 -n`
  # which breaks when step > 99 (e.g. global_step_100 < global_step_20 lexicographically).
  CKPT=$(ls -d "$SFT_RUNS_DIR"/global_step_* 2>/dev/null | \
    while IFS= read -r d; do
      step=$(basename "$d" | sed 's/global_step_//')
      printf '%s\t%s\n' "$step" "$d"
    done | sort -t$'\t' -k1,1n | tail -1 | cut -f2)
  if [ -z "$CKPT" ]; then
    echo "❌ No global_step_* checkpoint found in $SFT_RUNS_DIR"
    echo "   SFT training may still be running or hasn't saved a checkpoint yet."
    exit 1
  fi
fi

if [ ! -f "$CKPT/config.json" ] && ! ls "$CKPT"/model*.safetensors >/dev/null 2>&1; then
  echo "❌ Checkpoint incomplete (no config.json or safetensors): $CKPT"
  exit 1
fi

CKPT_SIZE=$(du -sh "$CKPT" 2>/dev/null | cut -f1)
CKPT_STEP=$(basename "$CKPT")

# ============ pre-launch checks ============
if [ ! -x "$VLLM_VENV" ]; then
  echo "❌ vLLM venv not found: $VLLM_VENV"
  echo "   Rebuild: see AGENTS.md / MEMORY for venv setup instructions"
  exit 1
fi

TF_VER=$("$VLLM_VENV" -c "import transformers; print(transformers.__version__)" 2>/dev/null || echo "unknown")
if ! echo "$TF_VER" | grep -q "^4\.49"; then
  echo "⚠️  transformers version is ${TF_VER} (expected 4.49.x)"
  echo "   Fix: uv pip install --python $VLLM_VENV 'transformers>=4.45,<4.50'"
  echo "   Continuing anyway (may fail with tokenizer error)..."
fi

GPU_APPS=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader -i "$GPU" 2>/dev/null | tr -d ' ')
if [ -n "$GPU_APPS" ]; then
  echo "⚠️  GPU${GPU} has running processes (PIDs: $(echo $GPU_APPS | tr '\n' ','))"
  echo "   If from SFT training, wait for it to finish first."
  if [ $DRY_RUN -eq 0 ]; then
    echo "   Aborting (use --dry-run to preview)."
    exit 1
  fi
fi

if ss -tlnp 2>/dev/null | grep -q ":${PORT} "; then
  echo "⚠️  Port ${PORT} already in use. Choose another with --port <N>."
  if [ $DRY_RUN -eq 0 ]; then exit 1; fi
fi

# ============ print recipe ============
cat <<EOF
===== Phase 2 Surrogate SFT — vLLM SERVE RECIPE @ $(date '+%F %T') =====
  ckpt            : ${CKPT}  (${CKPT_STEP}, ${CKPT_SIZE})
  gpu             : ${GPU}
  port            : ${PORT}
  served-model-name : ${SERVED_NAME}
  gpu-mem-util    : ${GPU_MEM_UTIL}
  max-model-len   : ${MAX_MODEL_LEN}
  vllm venv       : ${VLLM_VENV}
  transformers    : ${TF_VER}
  log file        : ${LOG_FILE}
  ---- Next step after serve is healthy ----
  Eval: bash baize_posttrain_eval.sh \\
          --backbone minicpm5-sft \\
          --endpoint http://localhost:${PORT}/v1 \\
          --model ${SERVED_NAME}
  ⚠️ Eval requires sandbox (10.129.32.75:8667) — currently BLOCKED (cross-subnet TCP ACL).
  Report results as: 替身预演，收益不可迁移到 BaiZe
===== END RECIPE =====
EOF

[ $DRY_RUN -eq 1 ] && { echo "[dry-run] Recipe printed, not launching serve."; exit 0; }

# ============ launch serve ============
echo "[serve] Launching vLLM on GPU${GPU} port ${PORT}..."
echo "[serve] Ckpt: $CKPT"

CUDA_VISIBLE_DEVICES="$GPU" \
  HF_HOME=/tmp/hf_home TRANSFORMERS_CACHE=/tmp/hf_home HF_MODULES_CACHE=/tmp/hf_home/modules \
  nohup "$VLLM_VENV" -m vllm.entrypoints.openai.api_server \
  --model "$CKPT" \
  --served-model-name "$SERVED_NAME" \
  --host 0.0.0.0 --port "$PORT" \
  --trust-remote-code \
  --gpu-memory-utilization "$GPU_MEM_UTIL" \
  --max-model-len "$MAX_MODEL_LEN" \
  > "$LOG_FILE" 2>&1 &

SERVE_PID=$!
echo "[serve] vLLM PID: $SERVE_PID"
echo "[serve] Log: tail -f $LOG_FILE"

# ============ wait for health ============
echo "[serve] Waiting for endpoint (up to 180s)..."
for i in $(seq 1 36); do
  sleep 5
  if curl -s --max-time 3 "http://localhost:${PORT}/v1/models" | grep -q "$SERVED_NAME"; then
    echo "[serve] ✅ Healthy after $((i*5))s — model: $SERVED_NAME"
    curl -s --max-time 3 "http://localhost:${PORT}/v1/models" | python3 -m json.tool 2>/dev/null
    echo "[serve] VRAM: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader -i $GPU)"
    echo "  Next: bash baize_posttrain_eval.sh --backbone minicpm5-sft --endpoint http://localhost:${PORT}/v1 --model ${SERVED_NAME}"
    exit 0
  fi
  if ! kill -0 "$SERVE_PID" 2>/dev/null; then
    echo "❌ vLLM died after $((i*5))s. Check: tail -50 $LOG_FILE"
    tail -20 "$LOG_FILE" 2>/dev/null
    exit 1
  fi
  echo "  ...waiting (${i}x5s=$((i*5))s)"
done
echo "❌ Not healthy within 180s. Check: tail -50 $LOG_FILE"
tail -20 "$LOG_FILE" 2>/dev/null
exit 1
