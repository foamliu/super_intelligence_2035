#!/bin/bash
# BaiZe Stage(i) R2 P-9.5 Level-3 RE-RUN (crash fix): torch.profiler top kernels.
#
# === CRASH ROOT CAUSE (first run, 2026-10-04 17:19, baize_p95_prof.sh) ===
#   RuntimeError: iteration 40 "found NaN in local forward loss calculation" (ranks 2,3)
#   at the END of profile window [10,40).  Rank 0 then began a HEAVY on_trace_ready
#   export (profile_memory=True + with_stack=True + record_shapes=True on GBS=1024
#   = 64 grad-accum steps -> enormous accumulated trace).  Other ranks had already
#   thrown on NaN; rank 0 was blocked in export -> NCCL collective TIMEOUT (600000ms)
#   on DATA_PARALLEL group -> SIGABRT (Signal 6).  KEYAVG file empty (0 lines):
#   export never completed.
#
# === FIX ===
#   Use the STANDALONE profile_bf16.py (proven in P-4, rc=0) which uses LIGHT flags:
#     record_shapes=False, with_stack=False, profile_memory=False
#   (these heavy flags are unnecessary for kernel-TIME attribution).
#   + speed-optimal config: MBS=2 / seq=4094 (vs P-4's MBS=1).
#   + GPU0-1 only (DP2) because GPU2-7 are occupied by data experiments (MUST NOT kill).
#   + short safe run: 20 steps, warmup=5, profile=10 steps [5,15), GBS=4 (1 grad-accum).
#
# Caveat: DP2 under-counts NCCL comm vs the DP8 optimal config; cross-reference P-4
# (DP8, NCCL=41.7%) for the comm proportion at production DP degree.
#
# 铁律：不改 P-5b recipe、不回训、不存 ckpt；🚫 不对 live 长跑 attach。
# 启动：CUDA_VISIBLE_DEVICES=0,1 setsid bash baize_p95_prof2.sh &
set -uo pipefail
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
export CUDA_VISIBLE_DEVICES=0,1

NAME="p95_prof_v2"
LOG="/tmp/baize_p95_prof2.log"
OUT="/tmp/baize_p95_keyavg_v2.txt"
SUM="/tmp/baize_p95_prof2.sum"
: > "$OUT"
: > "$SUM"
echo "===== P-9.5 torch.profiler RE-RUN START @ $(date '+%F %T') config=TP1·DP2·MBS2·seq4094·bf16 GPU0-1 iters=20 prof=[5,15) =====" > "$SUM"
echo "  FIX: light flags (record_shapes=False/with_stack=False/profile_memory=False)" >> "$SUM"
echo "  CRASH-ROOT: heavy flags + NaN@iter40 + NCCL timeout -> SIGABRT (first run)" >> "$SUM"

# 后台采样峰值显存 (GPU 0,1 only)
PEAK_FILE="/tmp/baize_p95_prof2.peakmem"
: > "$PEAK_FILE"
(
  MAX=0
  while :; do
    USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 0,1 2>/dev/null | sort -n | tail -1)
    [ -n "$USED" ] && [ "$USED" -gt "$MAX" ] && MAX=$USED
    echo "$MAX" > "$PEAK_FILE"
    sleep 2
  done
) &
SAMPLER_PID=$!

cd "$BASE" || exit 1
"$PY/torchrun" --nnodes=1 --nproc_per_node=2 \
    --master_addr=127.0.0.1 --master_port=29935 \
    profile_bf16.py \
    --name "$NAME" \
    --steps 20 --warmup 5 --profile-steps 10 \
    --gbs 4 --mbs 2 --seq-length 4094 --tensor-parallel 1 \
    --lr 1e-3 --lr-warmup-iters 2 --lr-decay-iters 2 \
    --out "$OUT" > "$LOG" 2>&1
RC=$?

kill "$SAMPLER_PID" 2>/dev/null
wait "$SAMPLER_PID" 2>/dev/null
PEAK=$(cat "$PEAK_FILE" 2>/dev/null)

echo "  rc=${RC} peak_gpu_mem_MiB=${PEAK} (max over GPU 0,1)" >> "$SUM"

if [ "$RC" -ne 0 ]; then
    echo "  ❌ ERROR 最后 15 行：" >> "$SUM"
    tail -15 "$LOG" >> "$SUM"
else
    echo "  ✅ rc=0" >> "$SUM"
    echo "  --- key_averages head (self_device_time_total) ---" >> "$SUM"
    head -20 "$OUT" >> "$SUM"
    echo "  --- keyavg line count ---" >> "$SUM"
    wc -l "$OUT" >> "$SUM"
fi

echo "===== P-9.5 torch.profiler RE-RUN END @ $(date '+%F %T') rc=${RC} =====" >> "$SUM"
echo "LOG=$LOG  OUT=$OUT  SUM=$SUM"
