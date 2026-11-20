#!/bin/bash
# UltraX-Preview download (2026-10-07 用户直令：解禁白名单)
# repo: openbmb/UltraX-Preview, ~487GB, 479 parquet, 5 config, ~100B token
# 落盘: /nas_train/app.e0031982/datasets/openbmb/UltraX-Preview/
# 口径: hf download + proxy + setsid nohup (ppid=1) + retry-loop (sleep 30)
set -uo pipefail

P=http://172.19.92.25:13128
export https_proxy=$P http_proxy=$P
HF=/nas_train/app.e0031982/miniforge3/envs/py310/bin/hf
DIR=/nas_train/app.e0031982/datasets/openbmb/UltraX-Preview
LOG="$DIR/download.log"
mkdir -p "$DIR"

while true; do
    echo "[retry-loop] START $(date '+%F %T')" >> "$LOG"
    "$HF" download --repo-type dataset openbmb/UltraX-Preview \
        --local-dir "$DIR" \
        >> "$LOG" 2>&1
    rc=$?
    echo "[retry-loop] rc=$rc $(date '+%F %T')" >> "$LOG"
    if [ $rc -eq 0 ]; then
        echo "[retry-loop] DONE rc=0 $(date '+%F %T')" >> "$LOG"
        break
    fi
    echo "[retry-loop] retry in 30s..." >> "$LOG"
    sleep 30
done
