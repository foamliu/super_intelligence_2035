#!/usr/bin/env bash
# launch_full_eval_v4.sh — v4 全量 GGUF eval 的「完全脱离」启动器
# 用 setsid 让整个脚本成为新 session leader，cline 退出后不会被 SIGHUP 杀掉。
# v4 改进: hellaswag 分片 4 servers + NFS 修复 (脚本复制到 /tmp 执行)
set -euo pipefail

RUN_DIR="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
MODEL="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_112000"
OUT="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_112000_full_v4"
LOG="/tmp/baize_full_eval_v4.log"
MARK="/tmp/baize_full_eval_v4.marker"

echo "$(date '+%Y-%m-%d %H:%M:%S') START epoch=$(date +%s)" > "$MARK"

# NFS 修复: 把脚本复制到 /tmp 再执行 (避免 bash 从 NFS 增量读取时遇到 stale handle)
TMPSCRIPT="/tmp/baize_llamacpp_full_eval_v4.sh"
cp "$RUN_DIR/baize_llamacpp_full_eval_v4.sh" "$TMPSCRIPT"
echo "[launcher] Script copied to $TMPSCRIPT (NFS fix)"

cd "$RUN_DIR"
bash "$TMPSCRIPT" "$MODEL" "$OUT" 16

RC=$?
echo "$(date '+%Y-%m-%d %H:%M:%S') END epoch=$(date +%s) rc=$RC" >> "$MARK"
exit $RC