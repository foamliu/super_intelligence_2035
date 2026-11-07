#!/usr/bin/env bash
# baize_llamacpp_full_eval_v4.sh — v4: hellaswag 分片 + NFS 修复
# v3 失败根因: NFS "Stale file handle" 杀死 bash 脚本
# v4 修复: 脚本复制到 /tmp 执行; hellaswag 分片到 4 servers
# 用法: bash baize_llamacpp_full_eval_v4.sh <hf_model_dir> <output_dir> [threads_per]
set -euo pipefail

MODEL="${1:?用法: bash baize_llamacpp_full_eval_v4.sh <hf_model_dir> <output_dir> [threads_per]}"
OUT="${2:?缺 output_dir}"
THREADS_PER="${3:-16}"

SCRIPT_DIR="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
GGUF_DIR="/nas_train/app.e0031982/models/baize2b_gguf"
LLAMA_DIR="/nas_train/app.e0031982/tools/llama.cpp"
BIN="$LLAMA_DIR/build/bin/llama-server"
PY="/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"

# NFS 修复: 复制关键脚本到 /tmp
TMPDIR_V4="/tmp/baize_eval_v4"
mkdir -p "$TMPDIR_V4"
GGUF_RUN_PY="$TMPDIR_V4/gguf_lmeval_run.py"
cp "$SCRIPT_DIR/pretrain_cpu_eval_gguf/gguf_lmeval_run.py" "$GGUF_RUN_PY"
MERGE_PY="$TMPDIR_V4/merge_parallel_results.py"
cp "$SCRIPT_DIR/merge_parallel_results.py" "$MERGE_PY"
echo "[v4] Scripts copied to $TMPDIR_V4 (NFS stale handle fix)"

GGUF="$GGUF_DIR/bz2b-$(basename "$MODEL" | sed 's/hf_iter_//')-f16.gguf"
if [[ ! -f "$GGUF" ]]; then
  echo "[v4] GGUF not found at $GGUF, converting..."
  bash "$SCRIPT_DIR/pretrain_cpu_eval_gguf/01_convert_hf_to_gguf.sh" "$MODEL" "$GGUF" f16
fi

echo "============================================================"
echo "  v4 Full llama.cpp eval: model=$MODEL"
echo "  GGUF=$GGUF  threads=$THREADS_PER  output=$OUT"
echo "  hellaswag: 4 shards × 4 servers | other 7 tasks: 4 servers"
echo "============================================================"

mkdir -p "$OUT"
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_DATASETS_OFFLINE=1
export HF_HUB_OFFLINE=1

BASE_PORT=8080
CLIENT_PARALLEL=4

# 启动 8 个 llama-server
SERVER_PIDS=()
for i in $(seq 0 7); do
  PORT=$((BASE_PORT + i))
  PIDFILE="/tmp/llamacpp_server_${PORT}.pid"
  if [[ -f "$PIDFILE" ]] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
    kill "$(cat "$PIDFILE")" 2>/dev/null || true; sleep 2
  fi
  echo "[v4] Starting server $i on port $PORT (threads=$THREADS_PER)"
  OMP_NUM_THREADS=1 setsid nice -n 19 "$BIN" \
    -m "$GGUF" -t "$THREADS_PER" -tb "$THREADS_PER" \
    -c $((2048 * 8)) --parallel 8 \
    --host 127.0.0.1 --port "$PORT" \
    --no-warmup --metrics --slots \
    --cache-prompt --temp 0 --top-k 1 --seed 1234 \
    > "/tmp/llamacpp_server_${PORT}.log" 2>&1 &
  echo $! > "$PIDFILE"
  SERVER_PIDS+=($!)
done

echo "[v4] Waiting for servers to be ready..."
for i in $(seq 0 7); do
  PORT=$((BASE_PORT + i))
  for _ in $(seq 1 120); do
    if curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
      echo "[v4] Server $i (port $PORT) READY"; break
    fi; sleep 1
  done
done

# 生成 hellaswag 分片 samples
HS_DOCS=10042
HS_SHARDS=4
SHARD_SIZE=$(( (HS_DOCS + HS_SHARDS - 1) / HS_SHARDS ))
echo "[v4] hellaswag: $HS_DOCS docs -> $HS_SHARDS shards of ~$SHARD_SIZE"

declare -a HS_SAMPLES
for s in $(seq 0 $((HS_SHARDS - 1))); do
  S=$((s * SHARD_SIZE))
  E=$((S + SHARD_SIZE - 1))
  if [ $E -ge $HS_DOCS ]; then E=$((HS_DOCS - 1)); fi
  HS_SAMPLES[$s]=$("$PY" -c "import json; print(json.dumps({'hellaswag': list(range($S, $E+1))}))")
  echo "[v4] hellaswag shard $s: docs $S..$E ($((E-S+1)) docs)"
done

# 启动评测进程
EVAL_PIDS=()
declare -A EVAL_TASK_NAMES
T_START=$(date +%s)

# Servers 0-3: hellaswag shards
for s in $(seq 0 $((HS_SHARDS - 1))); do
  PORT=$((BASE_PORT + s))
  task_out="$OUT/hellaswag_chunk${s}"
  mkdir -p "$task_out"
  echo "[v4] Launching hellaswag shard $s on port $PORT"
  setsid bash -c "$PY '$GGUF_RUN_PY' \
    --base-url http://127.0.0.1:${PORT} --hf-dir '$MODEL' \
    --output '$task_out' --tasks hellaswag \
    --parallel $CLIENT_PARALLEL --batch-size 32 \
    --samples '${HS_SAMPLES[$s]}' --gguf '$GGUF'" > "$task_out.log" 2>&1 &
  EVAL_PIDS+=($!)
  EVAL_TASK_NAMES[$!]="hellaswag_chunk${s}"
done

# Server 4: arc_easy
PORT=$((BASE_PORT + 4)); task_out="$OUT/arc_easy"; mkdir -p "$task_out"
echo "[v4] Launching arc_easy on port $PORT"
setsid bash -c "$PY '$GGUF_RUN_PY' --base-url http://127.0.0.1:${PORT} \
  --hf-dir '$MODEL' --output '$task_out' --tasks arc_easy \
  --parallel $CLIENT_PARALLEL --batch-size 32 --gguf '$GGUF'" > "$task_out.log" 2>&1 &
EVAL_PIDS+=($!); EVAL_TASK_NAMES[$!]="arc_easy"

# Server 5: boolq -> winogrande
PORT=$((BASE_PORT + 5))
echo "[v4] Launching boolq+winogrande on port $PORT"
setsid bash -c "$PY '$GGUF_RUN_PY' --base-url http://127.0.0.1:${PORT} \
  --hf-dir '$MODEL' --output '$OUT/boolq' --tasks boolq \
  --parallel $CLIENT_PARALLEL --batch-size 32 --gguf '$GGUF' && \
  $PY '$GGUF_RUN_PY' --base-url http://127.0.0.1:${PORT} \
  --hf-dir '$MODEL' --output '$OUT/winogrande' --tasks winogrande \
  --parallel $CLIENT_PARALLEL --batch-size 32 --gguf '$GGUF'" > "$OUT/boolq_winogrande.log" 2>&1 &
EVAL_PIDS+=($!); EVAL_TASK_NAMES[$!]="boolq+winogrande"

# Server 6: sciq -> piqa
PORT=$((BASE_PORT + 6))
echo "[v4] Launching sciq+piqa on port $PORT"
setsid bash -c "$PY '$GGUF_RUN_PY' --base-url http://127.0.0.1:${PORT} \
  --hf-dir '$MODEL' --output '$OUT/sciq' --tasks sciq \
  --parallel $CLIENT_PARALLEL --batch-size 32 --gguf '$GGUF' && \
  $PY '$GGUF_RUN_PY' --base-url http://127.0.0.1:${PORT} \
  --hf-dir '$MODEL' --output '$OUT/piqa' --tasks piqa \
  --parallel $CLIENT_PARALLEL --batch-size 32 --gguf '$GGUF'" > "$OUT/sciq_piqa.log" 2>&1 &
EVAL_PIDS+=($!); EVAL_TASK_NAMES[$!]="sciq+piqa"

# Server 7: arc_challenge -> openbookqa
PORT=$((BASE_PORT + 7))
echo "[v4] Launching arc_challenge+openbookqa on port $PORT"
setsid bash -c "$PY '$GGUF_RUN_PY' --base-url http://127.0.0.1:${PORT} \
  --hf-dir '$MODEL' --output '$OUT/arc_challenge' --tasks arc_challenge \
  --parallel $CLIENT_PARALLEL --batch-size 32 --gguf '$GGUF' && \
  $PY '$GGUF_RUN_PY' --base-url http://127.0.0.1:${PORT} \
  --hf-dir '$MODEL' --output '$OUT/openbookqa' --tasks openbookqa \
  --parallel $CLIENT_PARALLEL --batch-size 32 --gguf '$GGUF'" > "$OUT/arc_challenge_openbookqa.log" 2>&1 &
EVAL_PIDS+=($!); EVAL_TASK_NAMES[$!]="arc_challenge+openbookqa"

echo "[v4] All ${#EVAL_PIDS[@]} eval processes launched: ${EVAL_PIDS[*]}"
echo "[v4] Waiting for completion..."

FAIL=0
for i in "${!EVAL_PIDS[@]}"; do
  pid="${EVAL_PIDS[$i]}"; task_name="${EVAL_TASK_NAMES[$pid]}"
  if ! wait "$pid" 2>/dev/null; then
    echo "[v4] Process $i ($task_name PID $pid) FAILED"; FAIL=$((FAIL+1))
  else
    echo "[v4] $task_name DONE (wall=$(($(date +%s) - T_START))s)"
  fi
done

T_END=$(date +%s); ELAPSED=$((T_END - T_START))
echo "[v4] All done in ${ELAPSED}s ($(echo "scale=2; $ELAPSED/3600" | bc) hours). Failures: $FAIL"

echo "[v4] Merging results..."
$PY "$MERGE_PY" "$OUT" || echo "[v4] WARNING: merge failed"

echo "[v4] Stopping servers..."
for pid in "${SERVER_PIDS[@]}"; do kill "$pid" 2>/dev/null || true; done

echo "[v4] DONE. Results at $OUT/results.json"
echo "[v4] Elapsed: ${ELAPSED}s, Failures: $FAIL"