#!/bin/bash
# ==============================================================================
# run_armD_r2_stage2_only.sh — ArmD-R2 Stage-2 ONLY (operator instruction 2026-10-21)
#
# Stage-2 FAILED 2026-10-21 13:32 because the opt47 instruct dataset was deleted
# from NFS (0 samples -> StopIteration). Operator instruction 2026-10-21:
#   "让 vision 使用原版" -> switch DATA_DIR to original LLaVA-NeXT-780k-webdataset
#   and glob pretrain-*.tar (78 tars). Resume Stage-2 (3500 steps) directly from
#   the already-completed Stage-1.5 step20000 product. DO NOT rerun train/ProtB/
#   Stage-1/Stage-1.5.
#
# Reporting caveat (must appear in final report): Stage-2 instruct data version
#   changed opt47 (738588) -> original quick-start subset; MLLM 12-set results vs
#   ArmB/ArmC MUST be annotated with this data-version difference. Encoder
#   conclusions (ProtB lp/5-NN) are unaffected.
#
# Launch (on .12):
#   setsid bash run_armD_r2_stage2_only.sh > /tmp/armD_r2_stage2_only.log 2>&1 < /dev/null &
# ==============================================================================
set -uo pipefail
VISION_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision
cd "$VISION_DIR"
export PATH="$HOME/.bun/bin:$PATH"
export https_proxy=http://172.19.92.25:13128
export http_proxy=http://172.19.92.25:13128
source /nas_train/app.e0031982/miniforge3/etc/profile.d/conda.sh
conda activate py310

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export NCCL_TIMEOUT=1800
export OMP_NUM_THREADS=8
export MASTER_ADDR=127.0.0.1
export TOKENIZERS_PARALLELISM=false

echo "============================================================"
echo "  ArmD-R2 Stage-2 ONLY (original LLaVA-NeXT-780k) started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Data: /nas_train/app.e0031982/datasets/mvp-lab/LLaVA-NeXT-780k-webdataset (pretrain-*.tar)"
echo "  Resume from Stage-1.5 step20000 (not rerunning train/ProtB/Stage-1/1.5)"
echo "============================================================"

# Pre-flight: confirm Stage-1.5 checkpoint exists
STAGE15_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage15_armD_r2_20261020/step20000
if [ ! -f "$STAGE15_DIR/projector.pt" ] || [ ! -f "$STAGE15_DIR/adapter_model.safetensors" ]; then
    echo "ERROR: Stage-1.5 step20000 checkpoint missing (projector.pt / adapter_model.safetensors). ABORT."
    exit 1
fi
echo "[$(date '+%H:%M:%S')] Stage-1.5 checkpoint present. Starting Stage-2..."

torchrun --nproc_per_node=8 --nnodes=1 --master_addr=$MASTER_ADDR --master_port=$((29800 + RANDOM % 1000)) mllm_bridge/stage2_train_armD_r2.py >> /tmp/armD_r2_stage2.log 2>&1
RC=$?
echo "[$(date '+%H:%M:%S')] Stage-2 exit=$RC"
if [ $RC -ne 0 ]; then echo "ERROR: Stage-2 failed."; tail -30 /tmp/armD_r2_stage2.log; exit $RC; fi
STAGE2_DIR=/nas_train/app.e0031982/datasets/baize-vision/out/mllm_stage2_armD_r2_20261020/step3500
if [ ! -f "$STAGE2_DIR/projector.pt" ]; then echo "ERROR: Stage-2 projector missing."; exit 1; fi
echo "Stage-2 checkpoint saved at $STAGE2_DIR"
echo "============================================================"
echo "  ArmD-R2 Stage-2 COMPLETE: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  Next (manual): ④12-set eval -> ⑤ report + EXPERIMENTS_VISION.md §14"
echo "============================================================"
exit $RC
