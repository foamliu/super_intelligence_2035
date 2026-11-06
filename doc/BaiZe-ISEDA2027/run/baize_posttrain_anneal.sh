#!/usr/bin/env bash
# baize_posttrain_anneal.sh — BaiZe Stage(ii) 步骤 0：领域退火（Domain Annealing）配方骨架
#
# 用途：从 pretrain S1 收敛 ckpt resume，复用 Stage(i) 的 WSD（warmup-stable-decay）机制，
#       在「PyAether/SKILL API 参考 + EDA 工具文档 + 开源 HDL 源码」领域语料与通用混合数据
#       按受控比例 blend 上做继续预训练，把领域先验注入骨干（论文 §5.1）。
# 机器：10.252.32.17（post-train 线；正式训练用，需 GPU，待 pretrain ckpt 就绪 ETA≈2026-12-25）。
#
# 依赖（运行时才需要，骨架阶段不检查）：
#   - pretrain S1 收敛 ckpt（/nas_train/.../BaiZe-ISEDA2027/nemo_experiments/.../step_700000）
#   - 领域语料已分词为 mcore .bin/.idx（PyAether API 文档合成语料；由 data 线分词或本线补分词）
#   - 通用混合 .bin/.idx（mix_base / full_ultradata_code_l3 / full_ultradata_math_l3，见 DATA_LEDGER.md）
#   - 训练入口 pretrain_launcher.py（与 baize_p8_train.sh 同源，--arch mamba2 --lr-decay-style WSD）
#
# 红线（违反则整节作废，见 BAIZE_POSTTRAIN_TASK.md）：
#   - 污染隔离：领域语料投料前必须过 check_contamination.py（EDA-Eval-PyAether 158 任务黑名单）。
#   - 不 kill pretrain 训练；GPU 占用前确认空卡。
#
# 用法：
#   bash baize_posttrain_anneal.sh --dry-run        # 仅打印配方（不真跑，骨架阶段用）
#   bash baize_posttrain_anneal.sh --smoke          # smoke test（极小步数，验证前向）
#   RESUME_DIR=<ckpt> bash baize_posttrain_anneal.sh  # 正式退火
#
# ⚠️ 配方骨架：超参为占位默认值，待 P2 方案书定稿 + pretrain ckpt 就绪后由运维/本线确认填实。
set -uo pipefail

# ============ 路径（训练机上的 /nas_train 即本节点的 /nas_data 同一 NFS 导出） ============
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
DATA="$BASE/data"
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
OUTPUT_DIR="$BASE/nemo_experiments/baize_posttrain_anneal"

# ============ resume：从 pretrain S1 收敛 ckpt 起 ============
RESUME_DIR="${RESUME_DIR:-}"
: "${RESUME_DIR:=$BASE/nemo_experiments/baize2b/step_700000}"

# ============ 退火超参（占位默认，待 P2 定稿） ============
SEQ=4096; GBS=512; MBS=2
ITERS=4000; WARMUP=200; DECAY=400
LR=5e-4; MIN_LR=1e-5; SAVE_INTERVAL=400
NP=8; TP=1; PORT=29820; NAME="posttrain_anneal"

# ============ 领域退火数据 blend（权重=占比%，总和=100） ============
# 领域(PyAether API/EDA doc/HDL) 30% : 通用 web 50% : code 12% : math 8%
# ⚠️ 领域语料 pyAether_api_anneal 为占位（待 P1-d 调研 + data 线分词后填实）。
DOMAIN_DATA="${DATA}/pyAether_api_anneal"
WEB_DATA="${DATA}/mix_base"
CODE_DATA="${DATA}/full_ultradata_code_l3"
MATH_DATA="${DATA}/full_ultradata_math_l3"
BLEND="30 ${DOMAIN_DATA} 50 ${WEB_DATA} 12 ${CODE_DATA} 8 ${MATH_DATA}"

# ============ 模式开关 ============
DRY_RUN=0; SMOKE=0
for a in "$@"; do
  case "$a" in --dry-run) DRY_RUN=1 ;; --smoke) SMOKE=1 ;; esac
done

# ============ 配方打印 ============
cat <<EOF
===== BaiZe Stage(ii) Domain Annealing — RECIPE @ $(date '+%F %T') =====
  mode          : $([ $DRY_RUN = 1 ] && echo DRY-RUN || ([ $SMOKE = 1 ] && echo SMOKE || echo TRAIN))
  resume_ckpt   : ${RESUME_DIR}
  output_dir    : ${OUTPUT_DIR}
  arch          : mamba2 (reuse Stage(i) WSD machinery)
  seq / GBS / MBS: ${SEQ} / ${GBS} / ${MBS}
  NP / TP / DP  : ${NP} / ${TP} / $((NP/TP))
  steps         : ${ITERS} (warmup=${WARMUP} decay=${DECAY})
  LR -> min_LR  : ${LR} -> ${MIN_LR} (WSD exponential)
  save_interval : ${SAVE_INTERVAL}
  data blend    : domain(PyAether) 30% : web 50% : code 12% : math 8%
    ${BLEND}
  red line      : 领域语料投料前必须过 check_contamination.py（158 任务黑名单）
  note          : 与「仅 SFT」对照组隔离（同 pretrain ckpt，跳过退火）以分离退火贡献
===== END RECIPE =====
EOF

[ $DRY_RUN = 1 ] && { echo "[dry-run] 配方已打印，不执行训练。"; exit 0; }

# ============ 前置检查（真跑 / smoke 才做） ============
cd "$RUN_DIR" || { echo "❌ RUN_DIR 不存在: $RUN_DIR"; exit 1; }
[ -d "$RESUME_DIR" ] || { echo "❌ RESUME_DIR 不存在: $RESUME_DIR（pretrain S1 ckpt 未就绪？ETA≈2026-12-25）"; exit 1; }
for prefix in "$DOMAIN_DATA" "$CODE_DATA" "$MATH_DATA"; do
  for ext in bin idx; do
    [ -f "${prefix}.${ext}" ] || { echo "❌ 缺 ${prefix}.${ext}（领域语料占位未分词？提需求给 data 线）"; exit 1; }
  done
done
for ext in bin idx; do [ -f "${WEB_DATA}/mix_base_train_s0.${ext}" ] || { echo "❌ 缺 ${WEB_DATA}/mix_base_train_s0.${ext}"; exit 1; }; done
[ -f "$RUN_DIR/data_pipeline/check_contamination.py" ] || echo "⚠️ check_contamination.py 未找到，投料前须补污染扫描"
GPU_BUSY=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | awk -F', ' '{gsub(/[^0-9]/,"",$2); if($2+0>1000) print $1}')
[ -n "$GPU_BUSY" ] && { echo "❌ GPU $GPU_BUSY 非空（used>1GB），停手（不 kill pretrain/他人）"; exit 1; }

[ $SMOKE = 1 ] && { ITERS=20; WARMUP=2; DECAY=5; SAVE_INTERVAL=10; OUTPUT_DIR="${OUTPUT_DIR}_smoke"; echo "[smoke] ITERS=20"; }

export HF_HOME=/nas_train/app.e0031982/.cache
export HF_ENDPOINT=https://hf-mirror.com
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export http_proxy=http://172.19.92.25:13128
export https_proxy=http://172.19.92.25:13128
export TORCH_NCCL_ASYNC_ERROR_HANDLING=1

LOG=/tmp/baize_posttrain_anneal_train.log
echo "===== Anneal START @ $(date '+%F %T') =====" | tee /tmp/baize_posttrain_anneal.sum
"$PY/torchrun" --nnodes=1 --nproc_per_node="$NP" \
    --master_addr=127.0.0.1 --master_port="$PORT" \
    pretrain_launcher.py \
    --arch mamba2 --name "$NAME" --dir "$BASE/nemo_experiments" \
    --tokenizer-path "$DATA/tokenizer_eod" \
    --train-data-path $BLEND \
    --tensor-parallel "$TP" \
    --train-iters "$ITERS" --global-batch-size "$GBS" --micro-batch-size "$MBS" --seq-length "$SEQ" \
    --eval-interval 250 --eval-iters 0 \
    --save-interval "$SAVE_INTERVAL" \
    --lr "$LR" --min-lr "$MIN_LR" \
    --lr-warmup-iters "$WARMUP" --lr-decay-iters "$DECAY" --lr-decay-style WSD \
    --seed 1234 --precision bf16_mixed --optimizer dist_muon \
    --resume "$RESUME_DIR" > "$LOG" 2>&1
RC=$?
echo "  rc=${RC}" | tee -a /tmp/baize_posttrain_anneal.sum
echo "===== Anneal END @ $(date '+%F %T') rc=${RC} =====" | tee -a /tmp/baize_posttrain_anneal.sum
exit $RC
