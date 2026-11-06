#!/usr/bin/env bash
# baize_posttrain_sft.sh — BaiZe Stage(ii) 步骤 1：监督微调（SFT）配方骨架
#
# 用途：从退火 ckpt（或 pretrain ckpt，跳过退火的对照组）起，教「生成—执行—改进」闭环。
#       语料 = agentic 指令集(UltraData-SFT-Agent-2609, 51G/50 shard) + 通用指令集(UltraData-SFT-2605,
#       319G/1504 JSONL) + 依据 API 文档合成的 PyAether 专属材料（论文 §5.2）。
# 机器：10.252.32.17（post-train 线；正式训练用，需 GPU，待退火/ckp）。
#
# 消融变量（一等变量，P2 方案书定稿后填实）：
#   --context-len  4096 / 8192 / 16384（⚠️ agentic 轨迹极易超长 → 长上下文适配是前置项）
#   --ft-mode      full（全参） vs lora
#   --tool-traces  是否包含交错的工具调用轨迹（CoT + 工具轨迹 vs 纯代码）
#   --data-mix     agentic / +code / +math / +PyAether 配比
#
# 红线：SFT 语料走与预训练同一套 check_contamination.py（158 任务黑名单，不单独放行）。
#
# 用法：
#   bash baize_posttrain_sft.sh --dry-run
#   bash baize_posttrain_sft.sh --dry-run --context-len 16384 --ft-mode lora --tool-traces
#   RESUME_DIR=<anneal_ckpt> bash baize_posttrain_sft.sh --context-len 8192 --ft-mode full
#
# ⚠️ 配方骨架：训练入口 sft_launcher.py 为占位（待确认自研 SFT trainer vs TRL/verl 封装）。
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
DATA="$BASE/data"
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
OUTPUT_DIR="$BASE/nemo_experiments/baize_posttrain_sft"
RESUME_DIR="${RESUME_DIR:-$BASE/nemo_experiments/baize_posttrain_anneal/step_final}"

CONTEXT_LEN=8192; FT_MODE=full; TOOL_TRACES=1
DATA_MIX="agent50:general30:pyaether20"
GBS=128; MBS=1; ITERS=3000; WARMUP=100; DECAY=300
LR=2e-5; MIN_LR=1e-6; SAVE_INTERVAL=300
NP=8; TP=1; PORT=29821; NAME="posttrain_sft"
LORA_R=64; LORA_ALPHA=128

SFT_AGENT_DATA="${DATA}/sft_agent_ultradata_2609"
SFT_GENERAL_DATA="${DATA}/sft_ultradata_2605"
SFT_PYAETHER_DATA="${DATA}/sft_pyaether_synth"
TOKENIZER="$DATA/tokenizer_eod"

DRY_RUN=0; SMOKE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;; --smoke) SMOKE=1 ;;
    --context-len) CONTEXT_LEN="$2"; shift ;;
    --ft-mode) FT_MODE="$2"; shift ;;
    --tool-traces) TOOL_TRACES=1 ;; --no-tool-traces) TOOL_TRACES=0 ;;
    --data-mix) DATA_MIX="$2"; shift ;;
    --resume) RESUME_DIR="$2"; shift ;;
    *) echo "未知参数: $1" ;;
  esac
  shift
done

cat <<EOF
===== BaiZe Stage(ii) SFT — RECIPE @ $(date '+%F %T') =====
  mode          : $([ $DRY_RUN = 1 ] && echo DRY-RUN || ([ $SMOKE = 1 ] && echo SMOKE || echo TRAIN))
  resume_ckpt   : ${RESUME_DIR}
  output_dir    : ${OUTPUT_DIR}
  ablations     :
    context_len : ${CONTEXT_LEN}   (4096/8192/16384; agentic 轨迹易超长 → 长上下文适配是前置项)
    ft_mode     : ${FT_MODE}       (full / lora; lora_r=${LORA_R} lora_alpha=${LORA_ALPHA})
    tool_traces : ${TOOL_TRACES}   (1=CoT+工具轨迹 / 0=纯代码)
    data_mix    : ${DATA_MIX}      (agent/general/pyaether 占比%)
  seq / GBS / MBS: ${CONTEXT_LEN} / ${GBS} / ${MBS}
  NP / TP / DP  : ${NP} / ${TP} / $((NP/TP))
  steps         : ${ITERS} (warmup=${WARMUP} decay=${DECAY})
  LR -> min_LR  : ${LR} -> ${MIN_LR} (WSD)
  save_interval : ${SAVE_INTERVAL}
  corpus        : agent=${SFT_AGENT_DATA} general=${SFT_GENERAL_DATA} pyaether=${SFT_PYAETHER_DATA}(占位)
  red line      : SFT 语料走同一套 check_contamination.py（158 任务黑名单，不单独放行）
  entrypoint    : sft_launcher.py（占位，待确认自研 vs TRL/verl）
===== END RECIPE =====
EOF

[ $DRY_RUN = 1 ] && { echo "[dry-run] 配方已打印，不执行训练。"; exit 0; }

cd "$RUN_DIR" || { echo "❌ RUN_DIR 不存在: $RUN_DIR"; exit 1; }
[ -d "$RESUME_DIR" ] || { echo "❌ RESUME_DIR 不存在: $RESUME_DIR"; exit 1; }
for prefix in "$SFT_AGENT_DATA" "$SFT_GENERAL_DATA"; do
  [ -f "${prefix}.bin" ] && [ -f "${prefix}.idx" ] || { echo "❌ 缺 SFT 数据 ${prefix}.{bin,idx}"; exit 1; }
done
[ -f "${SFT_PYAETHER_DATA}.bin" ] || echo "⚠️ PyAether SFT 合成语料未就绪（${SFT_PYAETHER_DATA}.bin）→ 待 P1-d/P2 合成后补"
[ -f "$RUN_DIR/data_pipeline/check_contamination.py" ] || echo "⚠️ 污染闸脚本未找到，投料前须补扫描"
GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' '{gsub(/[^0-9]/,"",$2); if($2+0>1000) print $1}')
[ -n "$GPU_BUSY" ] && { echo "❌ GPU $GPU_BUSY 非空，停手"; exit 1; }

[ $SMOKE = 1 ] && { ITERS=20; WARMUP=2; DECAY=5; SAVE_INTERVAL=10; OUTPUT_DIR="${OUTPUT_DIR}_smoke"; }

export HF_HOME=/nas_train/app.e0031982/.cache
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export TORCH_NCCL_ASYNC_ERROR_HANDLING=1

LOG=/tmp/baize_posttrain_sft_train.log
echo "===== SFT START @ $(date '+%F %T') =====" | tee /tmp/baize_posttrain_sft.sum
"$PY/torchrun" --nnodes=1 --nproc_per_node="$NP" \
    --master_addr=127.0.0.1 --master_port="$PORT" \
    sft_launcher.py \
    --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
    --tokenizer-path "$TOKENIZER" \
    --init-from-ckpt "$RESUME_DIR" \
    --train-data-path "$SFT_AGENT_DATA" "$SFT_GENERAL_DATA" "$SFT_PYAETHER_DATA" \
    --data-mix "$DATA_MIX" \
    --seq-length "$CONTEXT_LEN" --global-batch-size "$GBS" --micro-batch-size "$MBS" \
    --train-iters "$ITERS" --lr "$LR" --min-lr "$MIN_LR" \
    --lr-warmup-iters "$WARMUP" --lr-decay-iters "$DECAY" --lr-decay-style WSD \
    --save-interval "$SAVE_INTERVAL" --seed 1234 --precision bf16_mixed \
    --ft-mode "$FT_MODE" --lora-r "$LORA_R" --lora-alpha "$LORA_ALPHA" \
    --tool-traces "$TOOL_TRACES" --loss-on-response-only > "$LOG" 2>&1
RC=$?
echo "  rc=${RC}" | tee -a /tmp/baize_posttrain_sft.sum
echo "===== SFT END @ $(date '+%F %T') rc=${RC} =====" | tee -a /tmp/baize_posttrain_sft.sum
exit $RC
