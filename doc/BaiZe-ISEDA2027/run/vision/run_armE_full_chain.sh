#!/bin/bash
# ==============================================================================
# run_armE_full_chain.sh — ArmE (2026-10-19) full post-training chain
#
# Operator instruction 2026-10-19, steps ②→③→④ (STRICT SERIAL):
#   ② ProtB eval (~1h)        — run_armE_protb_eval.sh
#   ③ MLLM alignment (~1.8h)  — Stage-1 (2500) -> Stage-1.5 (20000) -> Stage-2 (3500)
#   ④ 12-benchmark eval (~1.5h) — launch_12benchmarks_armE_offline.sh (/tmp cache fix)
#
# This script WAITS for the ArmE training process to exit, verifies the final
# checkpoint exists, then runs the chain. Each step must succeed before the next.
#
# Variables: data 3src->6src + epoch 4->3 + lr 1e-3->2e-3 + min_lr 1e-5->2e-5
#            (FOUR vars, NOT single-var ablation).
#
# Launch (on .12):
#   setsid bash run_armE_full_chain.sh > /tmp/armE_full_chain.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
VISION_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision
OUT_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/armE_20261021_aimv2_openclip_vitl14_224
cd "$VISION_DIR"
export PATH="$HOME/.bun/bin:$PATH"
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310
echo "============================================================"
echo "  ArmE Full Chain started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Variables: data 3src->6src + epoch 4->3 + lr 1e-3->2e-3 + min_lr 1e-5->2e-5 (FOUR vars)"
echo "============================================================"
# ============================================================
# PHASE 0: Wait for ArmE training to finish
# ============================================================
echo ""
echo "===== PHASE 0: Waiting for ArmE training to complete ====="
while true; do
    TRAIN_PIDS=$(pgrep -f 'armE_aimv2_openclip_vitl14.py.*armE_20261021' 2>/dev/null || true)
    if [ -z "$TRAIN_PIDS" ]; then echo "[$(date '+%H:%M:%S')] ArmE training process exited."; break; fi
    echo "[$(date '+%H:%M:%S')] Training still running (PIDs: $(echo $TRAIN_PIDS | tr '\n' ' ')). Sleeping 300s..."
    sleep 300
done
echo "[$(date '+%H:%M:%S')] Checking for ArmE final checkpoint..."
if [ ! -f "$OUT_DIR/open_clip_state_dict.pt" ]; then
    echo "[$(date '+%H:%M:%S')] ERROR: open_clip_state_dict.pt not found — training may have failed!"
    tail -20 /tmp/armE_openclip_train.log 2>&1
    exit 1
fi
if grep -q 'ArmE done' /tmp/armE_openclip_train.log 2>/dev/null; then
    echo "[$(date '+%H:%M:%S')] Training log confirms 'ArmE done' — success."
else
    echo "[$(date '+%H:%M:%S')] WARNING: 'ArmE done' not in log. Last 5 lines:"
    tail -5 /tmp/armE_openclip_train.log 2>&1
    echo "Proceeding with available checkpoint."
fi
# ============================================================
# PHASE ②: Protocol B evaluation (~1h)
# ============================================================
echo ""
echo "===== PHASE 2: Protocol B eval ($(date '+%H:%M:%S')) ====="
bash run_armE_protb_eval.sh
RC=$?
echo "[$(date '+%H:%M:%S')] ProtB exit=$RC"
if [ $RC -ne 0 ]; then echo "ERROR: ProtB failed. ABORT."; exit $RC; fi
if [ -f "armE_20261021_protb_vitl14_224_results.json" ]; then echo "ProtB results:"; cat armE_20261021_protb_vitl14_224_results.json; fi
# ============================================================
# PHASE ③: MLLM 3-stage alignment (~1.8h)
# ============================================================
echo ""
echo "===== PHASE 3: MLLM 3-stage ($(date '+%H:%M:%S')) ====="
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export NCCL_TIMEOUT=1800
export OMP_NUM_THREADS=8
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false
# ---- Stage-1: projector 768->2560, 2500 steps (~6.7min) ----
echo "[$(date '+%H:%M:%S')] 3-1: Stage-1 projector (2500 steps)..."
torchrun --nproc_per_node=8 --nnodes=1 --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) mllm_bridge/stage1_train_armE.py >> /tmp/armE_stage1.log 2>&1
RC=$?
echo "[$(date '+%H:%M:%S')] Stage-1 exit=$RC"
if [ $RC -ne 0 ]; then echo "ERROR: Stage-1 failed."; tail -30 /tmp/armE_stage1.log; exit $RC; fi
STAGE1_PROJ=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage1_armE_20261021/step2500/projector.pt
if [ ! -f "$STAGE1_PROJ" ]; then echo "ERROR: Stage-1 projector missing."; exit 1; fi
echo "Stage-1 projector saved."
# ---- Stage-1.5: LoRA r=64 + projector, 20000 steps (~86min) ----
echo "[$(date '+%H:%M:%S')] 3-2: Stage-1.5 LoRA (20000 steps)..."
torchrun --nproc_per_node=8 --nnodes=1 --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) mllm_bridge/stage15_train_armE.py >> /tmp/armE_stage15.log 2>&1
RC=$?
echo "[$(date '+%H:%M:%S')] Stage-1.5 exit=$RC"
if [ $RC -ne 0 ]; then echo "ERROR: Stage-1.5 failed."; tail -30 /tmp/armE_stage15.log; exit $RC; fi
STAGE15_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage15_armE_20261021/step20000
if [ ! -f "$STAGE15_DIR/projector.pt" ]; then echo "ERROR: Stage-1.5 projector missing."; exit 1; fi
echo "Stage-1.5 checkpoint saved."
# ---- Stage-2: instruct tuning, 3500 steps (~15.3min) ----
echo "[$(date '+%H:%M:%S')] 3-3: Stage-2 instruct (3500 steps)..."
torchrun --nproc_per_node=8 --nnodes=1 --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) mllm_bridge/stage2_train_armE.py >> /tmp/armE_stage2.log 2>&1
RC=$?
echo "[$(date '+%H:%M:%S')] Stage-2 exit=$RC"
if [ $RC -ne 0 ]; then echo "ERROR: Stage-2 failed."; tail -30 /tmp/armE_stage2.log; exit $RC; fi
STAGE2_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage2_armE_20261021/step3500
if [ ! -f "$STAGE2_DIR/projector.pt" ]; then echo "ERROR: Stage-2 projector missing."; exit 1; fi
echo "Stage-2 checkpoint saved."
# ============================================================
# PHASE ④: 12-benchmark eval (~1.5h)
# ============================================================
echo ""
echo "===== PHASE 4: 12-benchmark eval ($(date '+%H:%M:%S')) ====="
bash mllm_bridge/launch_12benchmarks_armE_offline.sh
RC=$?
echo "[$(date '+%H:%M:%S')] 12-benchmark exit=$RC"
echo ""
echo "============================================================"
echo "  ArmE Full Chain COMPLETE: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  ProtB:  $VISION_DIR/armE_20261021_protb_vitl14_224_results.json"
echo "  12-set: /nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_armE_20261021/"
echo "  Next: generate report + EXPERIMENTS_VISION.md + MEMORY"
echo "============================================================"
exit $RC
