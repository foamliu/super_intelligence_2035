#!/usr/bin/env bash
# restart_piqa_hellaswag_v6.sh — 重启 piqa + hellaswag(4 shard) 全量评测
# 使用修复版 llama-server 二进制 (code/llama.cpp, MD5=f95ac952, 含 nemotron-h logits 修复)
# 2026-11-08 22:30 创建（第4次服务器被SIGTERM后重建）
set -euo pipefail

# ============ 路径配置 ============
LLAMA_BIN="/nas_train/app.e0031982/code/llama.cpp/build/bin/llama-server"
GGUF="/nas_train/app.e0031982/models/baize2b_gguf/bz2b-112000-f16.gguf"
HF_DIR="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_112000"
EVAL_PY="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/pretrain_cpu_eval_gguf/gguf_lmeval_run.py"
PY="/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"
OUT_BASE="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_112000_full_v5_correct_binary"
LOG_DIR="/tmp/baize_eval_v6/logs"
mkdir -p "$LOG_DIR" "$OUT_BASE"

# 环境变量（与 04_run_one_ckpt.sh 对齐）
export CUDA_VISIBLE_DEVICES=""
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_OFFLINE=1
export HF_HUB_OFFLINE=1
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export OMP_NUM_THREADS=1

# ============ MD5 校验 ============
EXPECTED_MD5="f95ac95215a7e61a534eccba9a4ed49d"
ACTUAL_MD5=$(md5sum "$LLAMA_BIN" | awk '{print $1}')
if [[ "$ACTUAL_MD5" != "$EXPECTED_MD5" ]]; then
  echo "FATAL: llama-server MD5 mismatch! expected=$EXPECTED_MD5 actual=$ACTUAL_MD5"
  echo "       必须使用修复版二进制 (code/llama.cpp, 含 nemotron-h logits 修复)"
  exit 1
fi
echo "[check] llama-server MD5=$ACTUAL_MD5 ✓ (修复版)"

# ============ 清理旧进程 ============
echo "[cleanup] 杀掉残留的 llama-server (port 8183-8187)..."
for port in 8183 8184 8185 8186 8187; do
  pidfile="/tmp/llamacpp_server_${port}.pid"
  if [[ -f "$pidfile" ]] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
    kill "$(cat "$pidfile")" 2>/dev/null || true
    sleep 1
  fi
done
pkill -f "llama-server.*--port 818[3-7]" 2>/dev/null || true
sleep 2

# ============ 启动 llama-server ============
THREADS=16
CTX_PER_SLOT=2048
PARALLEL=2

start_server() {
  local port=$1 cores=$2 name=$3
  local log="$LOG_DIR/server_${name}_${port}.log"
  echo "[server] 启动 $name: port=$port cores=$cores threads=$THREADS"
  setsid taskset -c "$cores" \
    nice -n 10 "$LLAMA_BIN" \
    --model "$GGUF" \
    --port "$port" \
    --threads "$THREADS" \
    --parallel "$PARALLEL" \
    --ctx-size $((CTX_PER_SLOT * PARALLEL)) \
    --temp 0 --top-k 1 \
    --cache-prompt \
    --seed 1234 \
    > "$log" 2>&1 &
  local pid=$!
  echo "$pid" > "/tmp/llamacpp_server_${port}.pid"
  echo "[server] $name PID=$pid, 等待 health..."
  for i in $(seq 1 60); do
    if curl -s --connect-timeout 2 "http://127.0.0.1:${port}/health" | grep -q "ok"; then
      echo "[server] $name READY (port $port) ✓"
      return 0
    fi
    sleep 2
  done
  echo "[server] $name FAILED to start (port $port) ✗"
  return 1
}

# piqa: port 8183, cores 0-15 (NUMA node0)
start_server 8183 "0-15" "piqa"
# hellaswag shard0: port 8184, cores 16-31
start_server 8184 "16-31" "hs_chunk0"
# hellaswag shard1: port 8185, cores 32-47
start_server 8185 "32-47" "hs_chunk1"
# hellaswag shard2: port 8186, cores 48-63
start_server 8186 "48-63" "hs_chunk2"
# hellaswag shard3: port 8187, cores 64-79
start_server 8187 "64-79" "hs_chunk3"

echo "[servers] 全部 5 个 server 已启动"

# ============ 生成 hellaswag 分片 samples JSON ============
# hellaswag 全量 = 10042 docs, 分 4 片: [0..2510], [2511..5021], [5022..7531], [7532..10041]
$PY -c "
import json
total = 10042
shard_size = (total + 3) // 4  # 2511
for i in range(4):
    start = i * shard_size
    end = min((i+1) * shard_size, total)
    idxs = list(range(start, end))
    with open('$LOG_DIR/hs_shard${i}_samples.json', 'w') as f:
        json.dump({'hellaswag': idxs}, f)
    print(f'[shard] chunk{i}: docs {start}..{end-1} ({len(idxs)} docs)')
"

# ============ 启动 eval 客户端 ============
run_eval() {
  local task=$1 port=$2 output_subdir=$3 samples_file="${4:-}"
  local out="$OUT_BASE/$output_subdir"
  mkdir -p "$out"
  local log="$LOG_DIR/eval_${output_subdir}.log"
  echo "[eval] 启动 $task -> $out (port $port)"

  local cmd_args=()
  cmd_args+=(--base-url "http://127.0.0.1:${port}")
  cmd_args+=(--hf-dir "$HF_DIR")
  cmd_args+=(--output "$out")
  cmd_args+=(--tasks "$task")
  cmd_args+=(--parallel 2)
  cmd_args+=(--timeout 600)
  cmd_args+=(--gguf "$GGUF")
  if [[ -n "$samples_file" && -f "$samples_file" ]]; then
    cmd_args+=(--samples "$(cat "$samples_file")")
  fi

  setsid nice -n 10 "$PY" "$EVAL_PY" "${cmd_args[@]}" > "$log" 2>&1 &
  local pid=$!
  echo "[eval] $task PID=$pid, log=$log"
}

# piqa (全量, 无分片)
run_eval "piqa" 8183 "piqa"
# hellaswag 4 shards
run_eval "hellaswag" 8184 "hellaswag_chunk0" "$LOG_DIR/hs_shard0_samples.json"
run_eval "hellaswag" 8185 "hellaswag_chunk1" "$LOG_DIR/hs_shard1_samples.json"
run_eval "hellaswag" 8186 "hellaswag_chunk2" "$LOG_DIR/hs_shard2_samples.json"
run_eval "hellaswag" 8187 "hellaswag_chunk3" "$LOG_DIR/hs_shard3_samples.json"

echo ""
echo "========================================"
echo "  v6 eval 已启动: 5 server + 5 client"
echo "  piqa: port 8183 (cores 0-15)"
echo "  hellaswag: ports 8184-8187 (cores 16-79)"
echo "  输出: $OUT_BASE"
echo "  日志: $LOG_DIR"
echo "========================================"
echo ""
echo "[done] 脚本退出，eval 在后台运行。用以下命令检查进度："
echo "  ps -eo pid,etimes,args | grep gguf_lmeval | grep -v grep"
echo "  tail -f $LOG_DIR/eval_piqa.log"
echo "  tail -f $LOG_DIR/eval_hellaswag_chunk0.log"
