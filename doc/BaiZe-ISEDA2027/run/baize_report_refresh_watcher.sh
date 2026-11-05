#!/usr/bin/env bash
# baize_report_refresh_watcher.sh — 轮询 100k results.json → 刷新 v2 报告 → 退出
#
# 旧管线 (baize_eval_60k_100k_pipeline.sh PID 3543961) 负责 100k 的
# HF导出+GGUF+8集eval, 但不刷新报告。本脚本补上「报告刷新」环节。
# 安全：只读 results.json + 生成 HTML, 不占端口/GPU, 不与旧管线冲突。
#
# 用法: setsid nice -n 19 bash baize_report_refresh_watcher.sh > /tmp/baize_report_refresh_watcher.log 2>&1 < /dev/null &
set -uo pipefail
export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=4

RES_100K="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_100000_fixed_8set/results.json"
REPORT_GEN="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/gen_llamacpp_scaling_report.py"
PY="/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"
LOG="/tmp/baize_report_refresh_watcher.log"
DONE="/tmp/baize_report_refresh_done.marker"

log() { echo "[$(date '+%F %T')] [report-watcher] $*" | tee -a "$LOG"; }

if [[ -f "$DONE" ]]; then
  log "Already done (marker exists). Exiting."
  exit 0
fi

log "=== report-refresh watcher START ==="
log "Polling for 100k results.json every 300s (max 120 polls = 10h)"

POLL=0
MAX_POLLS=120
while true; do
  POLL=$((POLL + 1))
  if [[ -f "$RES_100K" ]]; then
    SZ=$(wc -c < "$RES_100K" 2>/dev/null || echo 0)
    if [[ "$SZ" -gt 5000 ]]; then
      log "100k results.json found ($SZ bytes)! Refreshing report..."
      $PY "$REPORT_GEN" 2>&1 | tee -a "$LOG"
      RC=$?
      if [[ $RC -eq 0 ]]; then
        log "Report refreshed successfully. Touching done marker."
        touch "$DONE"
        log "=== report-refresh watcher DONE ==="
        exit 0
      else
        log "Report generator failed (rc=$RC). Retrying in 300s..."
        sleep 300
        continue
      fi
    else
      log "100k results.json exists but too small ($SZ bytes). Waiting 300s..."
    fi
  else
    [[ $((POLL % 4)) -eq 0 ]] && log "100k results.json not yet (poll #$POLL). Sleeping 300s..."
  fi
  if [[ "$POLL" -ge "$MAX_POLLS" ]]; then
    log "TIMEOUT: 100k results not produced after $MAX_POLLS polls (10h). Giving up."
    exit 1
  fi
  sleep 300
done
