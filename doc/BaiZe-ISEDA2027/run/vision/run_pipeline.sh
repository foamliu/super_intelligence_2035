#!/bin/bash
# Master pipeline: S4 (multi-seed) -> S5 (retrieval) -> S6 (res/patch) -> S7 (objective)
# -> S8 (lr) -> S9 (infer bench). Run ON 10.239.2.12 (GPU 0-5).
# Each stage logs to its own out/Sx_*/train.log (via run_train.sh); this wrapper
# logs stage boundaries to /tmp/vision_pipeline.log.
set -uo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
LOG=/tmp/vision_pipeline.log
OUTROOT=/nas_train/app.e0031982/datasets/baize-vision/out
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}

mark () { echo "===== $1 $(date '+%F %T') =====" | tee -a "$LOG"; }

mark "PIPELINE START"

mark "S4 multi-seed"
bash run_s4.sh >>"$LOG" 2>&1
mark "S4 done"

mark "S5 retrieval (top-2 full ckpts)"
TOWERS="openvision2:$OUTROOT/S4_openvision2_s1234/vision.pt deepencoder_v2:$OUTROOT/S4_deepencoder_v2_s1234/vision.pt" \
  bash run_s5.sh >>"$LOG" 2>&1
mark "S5 done"

mark "S6 resolution/patch"
bash run_s6.sh >>"$LOG" 2>&1
mark "S6 done"

mark "S7 objective"
bash run_s7.sh >>"$LOG" 2>&1
mark "S7 done"

mark "S8 lr sweep"
bash run_s8.sh >>"$LOG" 2>&1
mark "S8 done"

mark "S9 infer bench"
bash run_s9.sh >>"$LOG" 2>&1
mark "S9 done"

mark "PIPELINE ALL DONE"