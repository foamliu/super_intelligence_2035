#!/usr/bin/env bash
# BaiZe 数据配比实验（§0.6-B）— 评测脚本：ckpt → HF → lm_eval
#
# 用法：
#   bash baize_mix_eval.sh <arm_name> [iter] [table]
#     arm_name = 训练 arm 名（如 mix_stable_s0a）
#     iter     = checkpoint 迭代号（默认=最后保存的 iter）
#     table    = "t2"（Table 2 常识 8 集，Stable 段）或 "t3"（Table 3 复杂推理 6 集，Decay 段）或 "both"（默认 t2）
#
# 示例：
#   bash baize_mix_eval.sh mix_stable_s0a 5000 t2
#   bash baize_mix_eval.sh mix_decay_d0a 5000 t3
#
# GPU：默认用 GPU2-7（data 名下 6 卡），训练完后即可评测。
#      若 GPU2-7 不空则用所有空闲卡。
set -uo pipefail

BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

ARM="${1:?用法: bash baize_mix_eval.sh <arm_name> [iter] [t2|t3|both]}"
TABLE="${3:-t2}"

EXP_DIR="$BASE/nemo_experiments/$ARM"
CKPT_DIR="$EXP_DIR/checkpoints"

# ── 找 checkpoint ──
if [ -n "${2:-}" ]; then
    ITER="$2"
    CKPT="$CKPT_DIR/iter_$(printf '%07d' "$ITER")"
else
    # 取最后一个 iter_* 目录
    CKPT=$(ls -d "$CKPT_DIR"/iter_* 2>/dev/null | sort | tail -1)
    if [ -z "$CKPT" ]; then
        echo "❌ 未找到 $ARM 的 checkpoint（$CKPT_DIR/iter_* 不存在）"
        exit 1
    fi
    ITER=$(basename "$CKPT" | sed 's/iter_0*//')
fi
echo "===== eval $ARM iter=$ITER table=$TABLE @ $(date '+%F %T') ====="

HF_OUT="$EXP_DIR/hf_model"
EVAL_OUT="$EXP_DIR/lm_eval_results"
mkdir -p "$EVAL_OUT"

# ── Step 1: ckpt → HF ──
if [ ! -f "$HF_OUT/config.json" ]; then
    echo "[1/2] 转换 ckpt → HF Nemotron-H ..."
    export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230
    "$PY/python" "$RUN/baize_p6_ckpt_to_hf.py" \
        --ckpt "$CKPT" \
        --tokenizer "$BASE/data/tokenizer_eod" \
        --out "$HF_OUT"
    echo "[1/2] ✅ HF 模型已写入 $HF_OUT"
else
    echo "[1/2] ⏭ HF 模型已存在，跳过转换"
fi

# ── Step 2: lm_eval ──
echo "[2/2] 运行 lm_eval ..."
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_ENDPOINT="https://hf-mirror.com"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"

# Table 2: 8 常识集（Stable 段用）
T2_TASKS="arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande"
# Table 3: 6 复杂推理集（Decay 段用）
T3_TASKS="gsm8k,math,bbh,mmlu,humaneval,mbpp"

case "$TABLE" in
    t2)  TASKS="$T2_TASKS";  SHOTS=0 ;;
    t3)  TASKS="$T3_TASKS";  SHOTS=0 ;;  # gsm8k/math/bbh 各自 shot 数由 lm_eval 默认
    both) TASKS="$T2_TASKS,$T3_TASKS"; SHOTS=0 ;;
    *) echo "❌ table 参数应为 t2 / t3 / both"; exit 1 ;;
esac

# GPU 选择：优先 GPU2-7（data 名下），否则所有空闲
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-2,3,4,5,6,7}
BATCH=${LM_EVAL_BATCH:-4}

echo "  TASKS=$TASKS  GPU=$CUDA_VISIBLE_DEVICES  BATCH=$BATCH"

# 串行跑（单 GPU 即可，避免与训练争卡；若需并行可改 baize_p6_run_full.sh 的 8 路模式）
"$PY/python" -m lm_eval \
    --model hf \
    --model_args "pretrained=${HF_OUT},dtype=bfloat16,trust_remote_code=False" \
    --tasks "$TASKS" \
    --num_fewshot "$SHOTS" \
    --batch_size "$BATCH" \
    --output_path "$EVAL_OUT" \
    2>&1 | tee "$EVAL_OUT/eval_${ARM}_iter${ITER}_${TABLE}.log"

echo "===== eval $ARM DONE @ $(date '+%F %T') → $EVAL_OUT ====="
