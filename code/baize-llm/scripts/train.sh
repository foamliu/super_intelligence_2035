#!/usr/bin/env bash
# ============================================================
# baize-llm · 训练统一入口
#   bash scripts/train.sh s1|s2|decay|longctx [--smoke N] [--dry-run] [--nodes N] [--name X]
# 配方固定：Mamba2-hybrid 2.2B / 16K / AdamW / WSD(D=exponential) / graph OFF / FP8 tensorwise
# ============================================================
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BAIZE_LLM_HOME="$(cd "$HERE/.." && pwd)"
export BAIZE_LLM_HOME
# shellcheck source=lib.sh
source "$HERE/lib.sh"

usage() {
  sed -n '2,6p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

STAGE="${1:-}"
[ -n "$STAGE" ] && shift || true
SMOKE=0; DRY=0; NODES_OVERRIDE=""; NAME_OVERRIDE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --smoke)   SMOKE="${2:-0}"; shift 2 ;;
    --smoke=*) SMOKE="${1#*=}"; shift ;;
    --dry-run) DRY=1; shift ;;
    --nodes)   NODES_OVERRIDE="${2:-}"; shift 2 ;;
    --name)    NAME_OVERRIDE="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die "未知参数：$1" ;;
  esac
done
case "$STAGE" in s1|s2|decay|longctx) ;; *) usage; exit 2 ;; esac

# shellcheck source=../configs/common.env
source "$BAIZE_LLM_HOME/configs/common.env"
# shellcheck disable=SC1090
source "$BAIZE_LLM_HOME/configs/${STAGE}.env"

[ -n "$NODES_OVERRIDE" ] && NNODES="$NODES_OVERRIDE"
DP=$(( NNODES * NPROC_PER_NODE / (TP * CP) ))
[ -n "$NAME_OVERRIDE" ] && NAME="$NAME_OVERRIDE"
if [ "$SMOKE" -gt 0 ]; then
  ITERS=$(( START_ITER + SMOKE ))
  NAME="${NAME}_smoke"
  SAVE_INTERVAL=0
  NNODES=1
  DP=$(( NNODES * NPROC_PER_NODE / (TP * CP) ))
  # WSD 调度器断言 lr_warmup_steps < lr_decay_steps；recipe.py:89-91 把
  # lr_decay_iters 设 None → bridge 默认到 train_iters，故断言等价 warmup < iters。
  # smoke 步数远小于正式 warmup(2000)，按 SMOKE/4 取 warmup（至少 1 步）。
  # 详见 megatron/core/optimizer_param_scheduler.py:157。
  WARMUP=$(( SMOKE / 4 ))
  [ "$WARMUP" -ge 1 ] || WARMUP=1
fi

MICRO=$(( MBS * DP ))
[ "$MICRO" -gt 0 ] || die "MBS*DP = $MICRO，非法"
[ $(( GBS % MICRO )) -eq 0 ] || die "GBS=$GBS 不是 MBS×DP=$MICRO 的整数倍"
ACCUM=$(( GBS / MICRO ))
TPS=$(( GBS * SEQ ))
STEPS=$(( ITERS - START_ITER ))
TOKENS=$(( STEPS * TPS ))

echo "===== ${STAGE} · ${STAGE_DESC} @ $(ts) · host=$(hostname) ====="
cat <<EOF
  并行      : NNODES=$NNODES × $NPROC_PER_NODE GPU, TP=$TP CP=$CP ⇒ DP=$DP
  batch     : MBS=$MBS GBS=$GBS accum=$ACCUM /卡
  token     : tok/step=$TPS（$(( TPS / 1000 ))K）, 本段 $STEPS 步 = $TOKENS token
  LR        : peak=$LR min=$MIN_LR warmup=$WARMUP decay_iters=$LR_DECAY_ITERS shape=$LR_DECAY_SHAPE
  优化器    : $OPTIMIZER（AdamW）  精度: $PRECISION / fp8=$FP8_RECIPE
  RoPE      : theta=$ROPE_THETA · max_pos=$ROPE_MAX_POS（1M）· 全注意力 $ATTN_LAYERS/56 层
  CUDA Graph: $([ "${CUDA_GRAPH_OFF:-1}" = "1" ] && echo "OFF（不传 --enable-cuda-graph）" || echo "ON")
  迭代区间  : [$START_ITER, $ITERS)   累计口径（S2/Decay 必须如此，否则会误判已到终点）
  name      : $NAME   exp_root=$EXP_ROOT
EOF
awk -v t="$TOKENS" -v eta="${ETA_TPS:-613992}" 'BEGIN{printf "  ETA(纯训练,按 %d tok/s): %.1f h = %.2f 天\n", eta, t/eta/3600, t/eta/86400}'

# ---------- 数据 blend ----------
BLENDFILE="/tmp/baize_blend_${STAGE}_$$.txt"
# BLEND_EXCLUDE：跳过坏 shard（逗号分隔 shard 名），不碰数据文件、只不进 blend；
# 权重在源内自动重摊。例：BLEND_EXCLUDE=env14_CC-MAIN-2023-23
EXCLUDE_ARG=()
[ -n "${BLEND_EXCLUDE:-}" ] && EXCLUDE_ARG=(--exclude "$BLEND_EXCLUDE")
"$PY/python" "$BAIZE_LLM_HOME/scripts/gen_blend.py" \
    --tsv "$BLEND_TSV" --tok-root "$TOK_ROOT" \
    --verify --total-tokens "$TOKENS" "${EXCLUDE_ARG[@]}" > "$BLENDFILE"
rc=$?
if [ "$rc" -ne 0 ]; then
  rm -f "$BLENDFILE"
  if [ "$rc" -eq 2 ]; then
    die "blend 数据缺失（rc=2）：本阶段阻塞，先补分词（见 run/data/DATA_MAPPING.md）"
  fi
  die "blend 生成失败（rc=$rc）"
fi
BLEND="$(cat "$BLENDFILE")"; rm -f "$BLENDFILE"
log "blend 就绪：$(echo "$BLEND" | wc -w | awk '{print $1/2}') 个 shard（权重+前缀对）"

# ---------- 组装 launcher 参数 ----------
ARGS=( --arch "$ARCH" --name "$NAME" --dir "$EXP_ROOT"
       --tokenizer-path "$TOKENIZER" --train-data-path "$BLEND"
       --tensor-parallel "$TP"
       --train-iters "$ITERS" --global-batch-size "$GBS"
       --micro-batch-size "$MBS" --seq-length "$SEQ"
       --eval-interval 250 --eval-iters 0 --save-interval "$SAVE_INTERVAL"
       --lr "$LR" --min-lr "$MIN_LR"
       --lr-warmup-iters "$WARMUP" --lr-decay-iters "$LR_DECAY_ITERS"
       --lr-decay-style "$LR_DECAY_STYLE" --seed "$SEED"
       --precision "$PRECISION" --optimizer "$OPTIMIZER" )

[ "$CP" -gt 1 ] && ARGS+=( --context-parallel "$CP" )
[ -n "${FP8_RECIPE:-}" ] && ARGS+=( --fp8-recipe "$FP8_RECIPE" )

# ---------- RoPE（用户令 2026-10-26：4 层注意力的 max position = 1M）----------
# 训练期真正生效的是 rope_theta（ABF）；max_position_embeddings 在导出/推理 config 生效。
# ⚠️ 只抬 max_pos 不抬 theta ⇒ 实测全 NaN（2026-10-06 B1），所以两者必须同改。
if has_flag --rotary-base; then
  ARGS+=( --rotary-base "$ROPE_THETA" )
else
  if [ "${ROPE_REQUIRED:-1}" = "1" ]; then
    die "launcher 不支持 --rotary-base ⇒ 无法把 rope_theta 设为 $ROPE_THETA（1M 位置的硬前提）。按 docs/LAUNCHER_PATCH_EXP_DECAY.md 的 §RoPE 打补丁；确需降级须显式 ROPE_REQUIRED=0 并在心跳标注。"
  fi
  warn "launcher 不支持 --rotary-base ⇒ 本次沿用默认 theta（1e4）；1M 位置会 NaN（ROPE_REQUIRED=0 已显式降级）"
fi
if has_flag --max-position-embeddings; then
  ARGS+=( --max-position-embeddings "$ROPE_MAX_POS" )
else
  warn "launcher 无 --max-position-embeddings（训练不受影响，RoPE 逐位置计算）；导出 HF config 时必须写 max_position_embeddings=$ROPE_MAX_POS，由 scripts/check_rope.py 把关"
fi
if [ -n "${ROPE_SCALING:-}" ]; then
  has_flag --rope-scaling && ARGS+=( --rope-scaling "$ROPE_SCALING" ) \
    || warn "launcher 不支持 --rope-scaling，忽略 ROPE_SCALING=$ROPE_SCALING"
fi

if [ -n "${WEIGHT_DECAY:-}" ]; then
  if has_flag --weight-decay; then
    ARGS+=( --weight-decay "$WEIGHT_DECAY" )
  else
    warn "launcher 不支持 --weight-decay，忽略 WEIGHT_DECAY=$WEIGHT_DECAY（沿用默认）"
  fi
fi

# D 段形状：本计划要求 exponential
if [ "${LR_DECAY_ITERS:-0}" -gt 0 ] && [ "${LR_DECAY_SHAPE:-linear}" != "linear" ]; then
  if has_flag --lr-decay-shape; then
    ARGS+=( --lr-decay-shape "$LR_DECAY_SHAPE" )
  else
    die "launcher 不支持 --lr-decay-shape ⇒ 无法实现『D 段 exponential』。按 docs/LAUNCHER_PATCH_EXP_DECAY.md 打补丁；临时降级须显式 LR_DECAY_SHAPE=linear 并在心跳注明。"
  fi
fi

# CUDA Graph 必须 OFF（16K 满速前提）：默认永不追加 --enable-cuda-graph
if [ "${CUDA_GRAPH_OFF:-1}" != "1" ]; then
  warn "CUDA_GRAPH_OFF!=1 ⇒ 将启用 CUDA Graph；16K 下预期掉到 ~110K tok/s（#786/#788）"
  ARGS+=( --enable-cuda-graph )
fi

# ---------- 日志路径 ----------
TLOG="/tmp/baize_${STAGE}_${NAME}.log"
LOG_M="/tmp/baize_${STAGE}_${NAME}_master.log"
LOG_W="/tmp/baize_${STAGE}_${NAME}_worker.log"
NCCL_ENV="NCCL_DEBUG=INFO NCCL_IB_GID_INDEX=3 NCCL_IB_MTU=4096 NCCL_IB_TC=106 NCCL_IB_TIMEOUT=22"
# 2026-10-27 fix: TORCH_DISTRIBUTED_DEBUG=DETAIL removed from PYTORCH_ENV.
# Root cause: DETAIL mode makes PyTorch wrap ProcessGroupNCCL in
# _ProcessGroupWrapper (distributed_c10d.py:2098), which does NOT implement
# reduce_scatter_tensor_coalesced → DDP gradient sync crashes with
# "Backend nccl does not support reduce_scatter_tensor_coalesced".
# The DataLoader OOM (#798) was diagnosed as swap exhaustion and mitigated
# by BAIZE_NUM_WORKERS=4 (common.env), so default debug tracing is no longer
# needed. To re-enable for debugging: export TORCH_DISTRIBUTED_DEBUG=DETAIL
# (and optionally TORCH_DISTRIBUTED_TORCH_TRACE=/tmp/td_trace_%rank) before
# launching train.sh — but note DDP coalesced ops may crash under the wrapper.
PYTORCH_ENV="PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True NCCL_GRAPH_REGISTER=0 TORCH_NCCL_BLOCKING_WAIT=1"
# Optional: append distributed-debug vars only if explicitly set in the env
if [ -n "${TORCH_DISTRIBUTED_DEBUG:-}" ]; then
  PYTORCH_ENV="$PYTORCH_ENV TORCH_DISTRIBUTED_DEBUG=$TORCH_DISTRIBUTED_DEBUG"
fi
if [ -n "${TORCH_DISTRIBUTED_TORCH_TRACE:-}" ]; then
  PYTORCH_ENV="$PYTORCH_ENV TORCH_DISTRIBUTED_TORCH_TRACE=$TORCH_DISTRIBUTED_TORCH_TRACE"
fi

# ---------- dry-run（跳过 GPU/端口门禁，只验参数与数据）----------
if [ "$DRY" = "1" ]; then
  echo
  echo "--- DRY RUN：rank0=${MASTER_IP} / rank1=local（${NNODES}×${NPROC_PER_NODE} GPU）---"
  printf '  '
  printf '%q ' "$PY/torchrun" --nnodes "$NNODES" --nproc_per_node "$NPROC_PER_NODE" \
      --master_addr "$MASTER_IP" --master_port "$MASTER_PORT" pretrain_launcher.py "${ARGS[@]}"
  echo
  exit 0
fi

# ---------- 门禁（GPU / 磁盘 / 端口）----------
gpus_free_local || die "$(hostname) GPU 非空闲（>2GB）：$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader | tr '\n' ' ')"
if [ "$NNODES" -gt 1 ]; then
  ssh_ok || die "ssh $MASTER_IP 不可达（16 卡需要 rank0；或改 --nodes 1 单机 8 卡）"
  gpus_free_remote || die "$MASTER_IP GPU 非空闲（vision 在跑？铁律：不抢）"
fi
AVAIL=$(df -Pk /tmp | awk 'NR==2{print $4}')
[ "${AVAIL:-0}" -ge "${TMP_MIN_KB:-5000000}" ] || die "/tmp 可用 $((AVAIL / 1024 / 1024))GB < 5GB"
used_port "$MASTER_PORT" && die "MASTER_PORT=$MASTER_PORT 已被占用"

# ---------- 监控先起来 ----------
[ "${TB_AUTOSTART:-1}" = "1" ] && bash "$HERE/tb_6006.sh" start

# ---------- 启动 ----------
cd "$BAIZE_TRAIN_CODE" || die "cd $BAIZE_TRAIN_CODE 失败"
export PYTHONPATH
{
  echo "===== ${STAGE} START $(ts) ====="
  echo "  name=$NAME iters=$ITERS (from $START_ITER) gbs=$GBS mbs=$MBS seq=$SEQ dp=$DP accum=$ACCUM"
  echo "  tok/step=$TPS tokens=$TOKENS optimizer=$OPTIMIZER lr=$LR min=$MIN_LR warmup=$WARMUP"
  echo "  decay_iters=$LR_DECAY_ITERS shape=$LR_DECAY_SHAPE graph=OFF fp8=$FP8_RECIPE"
  echo "  blend=$(echo "$BLEND" | wc -w | awk '{print $1/2}') shards"
} >> "$TLOG"

ulimit -n 65536 2>/dev/null || true

# Export NCCL/PyTorch env vars for BOTH single-node and multi-node paths.
# 2026-10-27 fix: single-node path was missing these exports → NCCL Error 1
# (unhandled cuda error) at reduce_scatter_tensor_coalesced because
# PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True was not set.
# The multi-node path already exports them (lines below for ssh + local),
# but the single-node smoke path ran torchrun without any of them.
export $NCCL_ENV
export $PYTORCH_ENV

if [ "$NNODES" -eq 1 ]; then
  log "单机启动：${NPROC_PER_NODE} 卡"
  "$PY/torchrun" --nnodes=1 --nproc_per_node="$NPROC_PER_NODE" \
      --master_addr=127.0.0.1 --master_port="$MASTER_PORT" \
      pretrain_launcher.py "${ARGS[@]}" > "$LOG_W" 2>&1
  RC=$?
  MRC="-"
else
  q() { printf '%q ' "$@"; }
  REMOTE_ARGS="$(q "${ARGS[@]}")"
  log "rank0 @ ${MASTER_IP}（后台 ssh）"
  ssh -n -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o BatchMode=yes "$MASTER_IP" \
      "ulimit -n 65536 && cd $BAIZE_TRAIN_CODE && export PYTHONPATH=$PYTHONPATH && \
       export $NCCL_ENV && export $PYTORCH_ENV && \
       $PY/torchrun --nnodes=2 --node_rank=0 --nproc_per_node=$NPROC_PER_NODE \
         --master_addr=$MASTER_IP --master_port=$MASTER_PORT \
         pretrain_launcher.py $REMOTE_ARGS" > "$LOG_M" 2>&1 &
  MPID=$!
  sleep 10
  log "rank1 @ $(hostname)（前台）"
  export $NCCL_ENV
  export $PYTORCH_ENV
  if [ "$SMOKE" -gt 0 ]; then
    timeout 1800 "$PY/torchrun" --nnodes=2 --node_rank=1 --nproc_per_node="$NPROC_PER_NODE" \
        --master_addr="$MASTER_IP" --master_port="$MASTER_PORT" \
        pretrain_launcher.py "${ARGS[@]}" > "$LOG_W" 2>&1
  else
    "$PY/torchrun" --nnodes=2 --node_rank=1 --nproc_per_node="$NPROC_PER_NODE" \
        --master_addr="$MASTER_IP" --master_port="$MASTER_PORT" \
        pretrain_launcher.py "${ARGS[@]}" > "$LOG_W" 2>&1
  fi
  RC=$?
  wait "$MPID" 2>/dev/null; MRC=$?
fi

echo "===== ${STAGE} END $(ts) worker_rc=$RC master_rc=$MRC =====" >> "$TLOG"
log "结束：worker_rc=$RC master_rc=$MRC"
log "日志：$LOG_W / $LOG_M ；摘要：$TLOG"
tail -5 "$LOG_W" 2>/dev/null | sed 's/^/  | /'
exit "$RC"
