#!/bin/bash
# Round 2 (R2) RESUME pipeline — 12 机器重启后，只重跑「未完成」的 R2-3 群组 + R2-5。
# 停训时 R2-3 已完成 9/12：openvision2/deepencoder_v2/moevie/mambaeye × r224 & r336 全完成 + openvision2 r448 完成。
# 未完成：deepencoder_v2 r448（被中断，无 vision.pt，须整组重跑）、moevie r448、mambaeye r448，以及 R2-5。
# 重要：run_r2.sh 无 resume/skip 逻辑——重启后【不要】再跑完整 run_r2.sh（会把已完成的 R2-1/4/2 与 9 组全部重做）。
# Run ON 10.239.2.12 (GPU 0-5). Log to /tmp/vision_r2_resume.log.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

DATA='/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar'
EVAL='/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar'
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
LOG=/tmp/vision_r2_resume.log
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}

mark() { echo "===== $1 $(date '+%F %T') =====" | tee -a "$LOG"; }

train() {
  local tower=$1 steps=$2 out=$3; shift 3
  local batch=32
  # 448/14 -> 1024 tokens; VRAM constraint -> drop to bs16 (same as run_r2.sh).
  local argline=" $* "
  if [[ "$argline" == *" --resolution 448 "* && "$argline" == *" --patch 14 "* ]]; then
    batch=16
  fi
  bash run_train.sh "$tower" "$steps" "$out" --data "$DATA" --batch-size "$batch" --log-every 50 "$@" >>"$LOG" 2>&1
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

# 清掉被中断的 deepencoder_v2 r448 残留（只有 train.log 无 vision.pt；train.py 日志是 append 模式，须清干净再重跑）。
rm -rf "$OUTROOT/R2_deepencoder_v2_r448_p14"

mark "R2 RESUME START"

# ---- R2-3 剩余群组（patch=14, lr=3e-3）----
# group 10: deepencoder_v2 r448（原被中断于 ~step2850/3000，无 vision.pt -> 整组重跑）
# group 11: moevie r448
# group 12: mambaeye r448
for t in deepencoder_v2 moevie mambaeye; do
  RES=448
  OUT="$OUTROOT/R2_${t}_r${RES}_p14"
  train "$t" 3000 "$OUT" --resolution "$RES" --patch 14 --lr 3e-3
  mark "R2-3 ${t} r${RES} train done"
  bench_one "$t" "$RES" 14 1 "R2-3_bench_${t}_r${RES}_bs1"
  bench_one "$t" "$RES" 14 8 "R2-3_bench_${t}_r${RES}_bs8"
  eval_one "$t" "$OUT/vision.pt" "R2-3_${t}_r${RES}"
done
mark "R2-3 DONE (resume)"

# ---- R2-5 ----
mark "R2-5 mambaeye bs1 stall diagnosis START (timebox 40min)"
echo "---- mamba_ssm version ----" >>"$LOG"
CUDA_VISIBLE_DEVICES=0 "$PY" -c 'import mamba_ssm; print("mamba_ssm:", mamba_ssm.__file__)' >>"$LOG" 2>&1
CUDA_VISIBLE_DEVICES=0 "$PY" -c 'import mamba_ssm, pkg_resources; print("dist:", pkg_resources.get_distribution("mamba_ssm").version)' >>"$LOG" 2>&1
python3 -c 'import subprocess; print(subprocess.run(["pip","show","mamba_ssm"],capture_output=True,text=True).stdout)' >>"$LOG" 2>&1
for b in 1 2 4 8; do
  bench_one mambaeye 224 16 "$b" "R2-5_mambaeye_bs${b}"
done
mark "R2-5 DONE"

mark "R2 RESUME ALL DONE"