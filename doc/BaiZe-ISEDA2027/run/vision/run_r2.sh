#!/bin/bash
# Round 2 (R2) master pipeline for the vision encoder.
# Exec order: R2-1 (res/patch @ lr=3e-3) -> R2-4 (clean throughput) -> R2-2 (objective)
#             -> R2-3 (arch x res matrix) -> R2-5 (mambaeye bs1 stall diagnosis).
# Run ON 10.239.2.12 (GPU 0-5). Log to /tmp/vision_r2.log.
# Global R2 anchor change: lr 1e-3 -> 3e-3 (per R2.2).
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

DATA='/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
LOG=/tmp/vision_r2.log
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}

mark() { echo "===== $1 $(date '+%F %T') =====" | tee -a "$LOG"; }

train() {
  local tower=$1 steps=$2 out=$3; shift 3
  bash run_train.sh "$tower" "$steps" "$out" --data "$DATA" --batch-size 32 --log-every 50 "$@" >>"$LOG" 2>&1
}

eval_one() {
  local tower=$1 ckpt=$2 tag=$3
  echo "  ---- EVAL $tag (tower=$tower) ----" >>"$LOG"
  if [ ! -f "$ckpt" ]; then echo "  [skip] missing ckpt $ckpt" >>"$LOG"; return; fi
  CUDA_VISIBLE_DEVICES=0 "$PY" eval_downstream.py --tower "$tower" --ckpt "$ckpt" --eval-tar "$EVAL" --n 5000 >>"$LOG" 2>&1
}

bench_one() {
  local tower=$1 res=$2 patch=$3 batch=$4 tag=$5
  echo "  ---- BENCH $tag (batch=$batch) ----" >>"$LOG"
  timeout 120 env CUDA_VISIBLE_DEVICES=0 "$PY" bench.py --tower "$tower" --resolution "$res" --patch "$patch" --batch "$batch" --iters 50 --warmup 10 >>"$LOG" 2>&1 \
    || echo "  [bench timeout/stall] $tag batch=$batch" >>"$LOG"
}

mark "R2 PIPELINE START (lr anchor 3e-3)"

# ============================ R2-1 ============================
mark "R2-1 res/patch ablation @ lr=3e-3 START"
for rp in "336 16" "448 16" "224 14" "336 14" "448 14"; do
  set -- $rp; RES=$1; P=$2
  OUT="$OUTROOT/R2_ov2_r${RES}_p${P}"
  train openvision2 3000 "$OUT" --resolution "$RES" --patch "$P" --lr 3e-3
  mark "R2-1 r${RES}_p${P} train done"
done
mark "R2-1 training done"

eval_one openvision2 "$OUTROOT/S8_ov2_lr3e-3/vision.pt" "R2-1_224p16_lr3e-3(reuse S8)"
eval_one openvision2 "$OUTROOT/S8_ov2_lr1e-3/vision.pt" "R2-1_224p16_lr1e-3(collapse)"
eval_one openvision2 "$OUTROOT/R2_ov2_r336_p16/vision.pt" "R2-1_336p16"
eval_one openvision2 "$OUTROOT/R2_ov2_r448_p16/vision.pt" "R2-1_448p16"
eval_one openvision2 "$OUTROOT/R2_ov2_r224_p14/vision.pt" "R2-1_224p14"
eval_one openvision2 "$OUTROOT/R2_ov2_r336_p14/vision.pt" "R2-1_336p14"
eval_one openvision2 "$OUTROOT/R2_ov2_r448_p14/vision.pt" "R2-1_448p14"
mark "R2-1 eval done"

for rp in "224 16" "336 16" "448 16" "224 14" "336 14" "448 14"; do
  set -- $rp; RES=$1; P=$2
  bench_one openvision2 "$RES" "$P" 1 "R2-1_bench_r${RES}_p${P}"
done
mark "R2-1 DONE"

# ============================ R2-4 ============================
mark "R2-4 clean throughput START"
echo "---- GPU exclusivity check (verbatim) ----" >>"$LOG"
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv >>"$LOG" 2>&1
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv >>"$LOG" 2>&1
echo "---- pretrain task state (NFS contention check) ----" >>"$LOG"
grep -E '^\- (STAGE|PHASE|WAITING)' /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md | head -5 >>"$LOG" 2>&1
for t in openvision2 deepencoder_v2 moevie mambaeye; do
  OUT="$OUTROOT/R2_tp_${t}"
  train "$t" 400 "$OUT" --lr 3e-3
  mark "R2-4 $t train done"
  bench_one "$t" 224 16 1 "R2-4_bench_${t}_bs1"
done
mark "R2-4 DONE"

# ============================ R2-2 ============================
mark "R2-2 objective @ lr=3e-3 START"
OUT="$OUTROOT/R2_ov2_clip_lr3e-3"
train openvision2 3000 "$OUT" --loss clip --lr 3e-3
mark "R2-2 clip train done"
eval_one openvision2 "$OUTROOT/S8_ov2_lr3e-3/vision.pt" "R2-2_siglip(reuse S8)"
eval_one openvision2 "$OUT/vision.pt" "R2-2_clip"
mark "R2-2 DONE"

# ============================ R2-3 ============================
mark "R2-3 arch x res matrix (patch=14, lr=3e-3) START"
for RES in 224 336 448; do
  for t in openvision2 deepencoder_v2 moevie mambaeye; do
    OUT="$OUTROOT/R2_${t}_r${RES}_p14"
    train "$t" 3000 "$OUT" --resolution "$RES" --patch 14 --lr 3e-3
    mark "R2-3 ${t} r${RES} train done"
    bench_one "$t" "$RES" 14 1 "R2-3_bench_${t}_r${RES}_bs1"
    bench_one "$t" "$RES" 14 8 "R2-3_bench_${t}_r${RES}_bs8"
    eval_one "$t" "$OUT/vision.pt" "R2-3_${t}_r${RES}"
  done
done
mark "R2-3 DONE"

# ============================ R2-5 ============================
mark "R2-5 mambaeye bs1 stall diagnosis START (timebox 40min)"
echo "---- mamba_ssm version ----" >>"$LOG"
CUDA_VISIBLE_DEVICES=0 "$PY" -c 'import mamba_ssm; print("mamba_ssm:", mamba_ssm.__file__)' >>"$LOG" 2>&1
CUDA_VISIBLE_DEVICES=0 "$PY" -c 'import mamba_ssm, pkg_resources; print("dist:", pkg_resources.get_distribution("mamba_ssm").version)' >>"$LOG" 2>&1
python3 -c 'import subprocess; print(subprocess.run(["pip","show","mamba_ssm"],capture_output=True,text=True).stdout)' >>"$LOG" 2>&1
for b in 1 2 4 8; do
  bench_one mambaeye 224 16 "$b" "R2-5_mambaeye_bs${b}"
done
mark "R2-5 DONE"

mark "R2 PIPELINE ALL DONE"