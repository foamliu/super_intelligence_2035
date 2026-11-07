#!/usr/bin/env bash
# baize_cpu_scaling_orchestrator.sh — 编排：等探测矩阵→全量8集评测→生成报告
#
# 用法: nohup bash baize_cpu_scaling_orchestrator.sh <probe_pid> > /tmp/baize_orchestrator.log 2>&1 &
#
# 流程:
#   1. 等待探测矩阵(PID)结束
#   2. 保存探测结果到永久位置
#   3. 启动全量8集评测(80线程, bs=1, 无limit) —— 后台运行，预计多天
#   4. 立即生成含探测数据的初步报告
#   5. 全量评测完成后更新报告(含实际分数)
#
# 硬约束: OMP≤80, nice 19, CUDA_VISIBLE_DEVICES="", 不碰GPU
set -uo pipefail

PROBE_PID="${1:?用法: bash baize_cpu_scaling_orchestrator.sh <probe_pid>}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b"
MODEL="${BASE}/hf_iter_112000"
CKPT="112000"
PROBE_SUMMARY="/tmp/baize_probe_results.json"
PROBE_LOG="/tmp/baize_probe_matrix.log"
PERM_PROBE="${BASE}/lm_eval_results/probe_scaling_${CKPT}.json"
PERM_PROBE_LOG="${BASE}/lm_eval_results/probe_scaling_${CKPT}.log"
FULL_OUT="${BASE}/lm_eval_results/hf_iter_${CKPT}"
FULL_LOG="/tmp/baize_full_eval_${CKPT}.log"
REPORT_DIR="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports"
REPORT="${REPORT_DIR}/report_pretrain_cpu_eval_thread_scaling_zh.html"

echo "========================================"
echo "  Scaling Orchestrator Start: $(date '+%F %T')"
echo "  probe_pid=${PROBE_PID}"
echo "  model=${MODEL}"
echo "  full_out=${FULL_OUT}"
echo "========================================"

# ── 1. 等待探测矩阵结束 ──
echo "[orchestrator] Waiting for probe PID ${PROBE_PID}..."
WAIT_START=$(date +%s)
while kill -0 "$PROBE_PID" 2>/dev/null; do
  sleep 30
done
WAIT_END=$(date +%s)
echo "[orchestrator] Probe finished after $((WAIT_END - WAIT_START))s at $(date '+%T')"

# ── 2. 保存探测结果到永久位置 ──
if [[ -f "$PROBE_SUMMARY" ]]; then
  cp "$PROBE_SUMMARY" "$PERM_PROBE"
  echo "[orchestrator] Probe results saved to ${PERM_PROBE}"
fi
if [[ -f "$PROBE_LOG" ]]; then
  cp "$PROBE_LOG" "$PERM_PROBE_LOG"
  echo "[orchestrator] Probe log saved to ${PERM_PROBE_LOG}"
fi

# ── 3. 立即生成初步报告（仅探测数据） ──
echo "[orchestrator] Generating preliminary report (probe data only)..."
mkdir -p "$REPORT_DIR"
cd "$SCRIPT_DIR"
/nas_train/app.e0031982/miniforge3/envs/py310/bin/python gen_cpu_eval_scaling_report.py \
  "$PERM_PROBE" "$REPORT" "$CKPT" 2>&1 || echo "[orchestrator] WARN: preliminary report generation failed"

# ── 4. 启动全量8集评测（80线程, bs=1, 无limit） ──
echo "[orchestrator] Starting full 8-set eval (16 threads, bs=1, no limit)..."
echo "[orchestrator] Full eval start: $(date '+%T')"
echo "[orchestrator] Estimated time: ~69,650 requests × ~14s/req ≈ 11 days (16 threads optimal)"

mkdir -p "$FULL_OUT"

export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=16
export MKL_NUM_THREADS=16

START_EPOCH=$(date +%s)

# 运行全量评测
bash "$SCRIPT_DIR/baize_cpu_lmeval.sh" "$MODEL" "$FULL_OUT" \
  --batch_size 1 \
  > "$FULL_LOG" 2>&1
EVAL_RC=$?

END_EPOCH=$(date +%s)
WALL_SEC=$((END_EPOCH - START_EPOCH))

echo "[orchestrator] Full eval finished: rc=$EVAL_RC wall=${WALL_SEC}s at $(date '+%T')"

# ── 5. 生成最终报告（含全量分数） ──
if [[ $EVAL_RC -eq 0 && -f "${FULL_OUT}/results.json" ]]; then
  echo "[orchestrator] Full eval results available, generating final report..."
  /nas_train/app.e0031982/miniforge3/envs/py310/bin/python gen_cpu_eval_scaling_report.py \
    "$PERM_PROBE" "$REPORT" "$CKPT" "${FULL_OUT}/results.json" 2>&1 \
    || echo "[orchestrator] WARN: final report generation failed"
else
  echo "[orchestrator] Full eval failed or no results, keeping preliminary report"
fi

echo "========================================"
echo "  Orchestrator Done: $(date '+%F %T')"
echo "  Report: ${REPORT}"
echo "  Full results: ${FULL_OUT}/results.json"
echo "========================================"
