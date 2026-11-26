#!/usr/bin/env bash
# BaiZe R2 · B: 长上下文适配 4096→8192+ zero-shot eval
# Operator 2026-10-06 approved B: GPU0 · 1 card · <=4h
# Q: Does ABF (rope_theta=1e6, max_pos=8192) degrade short-context zero-shot?
# B1 showed PPL at 4K goes 75→83 with ABF — verify downstream degradation.
# Usage: bash baize_b_longctx_eval.sh [gpu_id]
set -uo pipefail
GPU_ID="${1:-0}"
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export HF_HUB_ENABLE_HF_TRANSFER=0
export http_proxy="http://172.19.92.25:13128"
export https_proxy="http://172.19.92.25:13128"
export no_proxy="localhost,127.0.0.1,0.0.0.0"
export NO_PROXY="localhost,127.0.0.1,0.0.0.0"

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
BASE_MODEL=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/hf_iter_4771
ABF_DIR=/tmp/baize_b_abf_8k
OUT_BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/p5b/lm_eval_longctx
SUM="/tmp/baize_b_longctx.sum"; : > "$SUM"
echo "===== B: Longctx 4096->8192+ START @ $(date '+%F %T') =====" >> "$SUM"

# Step 1: Create symlinked model dir with ABF config
echo "[$(date '+%T')] Creating ABF model dir..." >> "$SUM"
mkdir -p "$ABF_DIR"
for f in "$BASE_MODEL"/*; do
    bn=$(basename "$f")
    [ "$bn" != "config.json" ] && ln -sf "$f" "$ABF_DIR/$bn"
done
$PY -c "import json; c=json.load(open('$BASE_MODEL/config.json')); c['max_position_embeddings']=8192; c['rope_theta']=1000000.0; json.dump(c,open('$ABF_DIR/config.json','w'),indent=2); print(f'  max_pos={c[\"max_position_embeddings\"]}, rope_theta={c[\"rope_theta\"]}')" >> "$SUM" 2>&1
mkdir -p "$OUT_BASE/abf"

# Step 2: Run zero-shot tasks with ABF model
TASKS=("hellaswag:500" "arc_easy:500" "mmlu:200" "bbh_zeroshot:100")
echo "[$(date '+%T')] Running zero-shot tasks with ABF model..." >> "$SUM"
for task_spec in "${TASKS[@]}"; do
    task="${task_spec%%:*}"; limit="${task_spec##*:}"
    LOG="/tmp/baize_b_longctx_${task}.log"
    echo "  ABF $task (limit=$limit) @ $(date '+%T')" >> "$SUM"
    CUDA_VISIBLE_DEVICES=$GPU_ID $PY -m lm_eval \
        --model hf --model_args "pretrained=${ABF_DIR},dtype=bfloat16,trust_remote_code=False" \
        --tasks "$task" --num_fewshot 0 --batch_size 4 --limit "$limit" \
        --output_path "$OUT_BASE/abf" > "$LOG" 2>&1
    rc=$?
    [ $rc -ne 0 ] && { echo "    rc=$rc FAILED:" >> "$SUM"; tail -3 "$LOG" | sed 's/^/    /' >> "$SUM"; } || echo "    rc=0 done" >> "$SUM"
done

# Step 3: Passkey retrieval at 4K and 8K
echo "[$(date '+%T')] Passkey retrieval 4K/8K..." >> "$SUM"
CUDA_VISIBLE_DEVICES=$GPU_ID $PY /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_b_passkey_test.py \
    --model-path "$ABF_DIR" --output "$OUT_BASE/passkey_results.json" >> "$SUM" 2>&1
echo "  passkey rc=$?" >> "$SUM"

# Step 4: Collect and compare with baseline
echo "[$(date '+%T')] Collecting..." >> "$SUM"
$PY /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_b_collect.py >> "$SUM" 2>&1
echo "===== B END @ $(date '+%F %T') =====" >> "$SUM"
