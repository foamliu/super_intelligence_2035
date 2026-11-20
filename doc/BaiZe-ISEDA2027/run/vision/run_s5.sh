#!/bin/bash
# S5 downstream proxy: zero-shot text<->image retrieval R@K on a held-out set.
# Eval set is carved from laioncn/EN (a DIFFERENT source than training imagenet/EN),
# so retrieval is genuinely zero-shot (no training-set memorization).
#
# NOTE on text tower: retrieval needs jointly-trained text (vision+text). The
# updated train.py saves the full model; S4+ checkpoints have 'text'. S1/S3
# checkpoints (older train.py) are vision-only -> retrieval requires a full ckpt.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
EVAL=/nas_train/app.e0031982/datasets/baize-vision/eval5k
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out

# 1) materialize a held-out eval set (5000 pairs) once.
if [ ! -d "$EVAL" ] || [ -z "$(ls -A "$EVAL" 2>/dev/null)" ]; then
  SRC="/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M/laioncn/EN/part00/*.parquet"
  echo "[S5] prepping eval set from laioncn/EN -> $EVAL"
  "$PY" prep_data.py --src "$SRC" --out "$EVAL" --max 5000 --shard 5000
fi
EVAL_TAR="$EVAL/*.tar"

# 2) Tokens: "tower:ckpt" pairs to evaluate (full ckpts w/ text). Override inline.
TOWERS="${TOWERS:-openvision2:$OUTROOT/S4_openvision2_s1234/vision.pt}"

for entry in $TOWERS; do
  TOWER="${entry%%:*}"; CKPT="${entry#*:}"
  echo "===== S5 $TOWER ($CKPT) ====="
  [ -f "$CKPT" ] || { echo "  [skip] ckpt missing: $CKPT"; continue; }
  "$PY" eval_downstream.py --tower "$TOWER" --ckpt "$CKPT" \
      --eval-tar "$EVAL_TAR" --n 5000 2>&1 | grep -vE 'warning|Warning|FutureWarning|pynvml'
  echo "===== S5 $TOWER done ===== "
done
echo "===== S5 ALL DONE ====="