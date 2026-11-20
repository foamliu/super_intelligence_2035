#!/bin/bash
# predict_guarded.sh — 宿主 predict 硬护栏 wrapper（2026-11-20 用户令·Step 1.2）
#
# WHY: 10-29 cline 路 predict 在 .29 宿主机跑 sympy 时 list(partitions(200)) 吃 ~1.2TB 内存，
#   威胁 S1 训练。predict 阶段跑在宿主机（非容器），不受 docker 限制 = 根因。
#   本 wrapper 在 exec predict 前：
#     1) ulimit -v 209715200  (=200 GiB，单位 KB) — 单进程虚拟内存硬上限
#     2) OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS ≤8 — 禁跑满 224 核
#     3) nice -n 19 ionice -c 3 — 最低 CPU/IO 优先级
#
# USAGE (包在 predict python 调用外层):
#   bash predict_guarded.sh python3 run_verified_full.py predict --harness codex
#   bash predict_guarded.sh python3 run_mm_2x3.py predict --route cline__deepseek-v4-flash
#
# 环境变量可覆盖（默认保守）:
#   PRED_VSLEEP_KB=209715200   PRED_OMP=8   PRED_NICE=19   PRED_IONICE=3
set -u

PRED_VSLEEP_KB="${PRED_VSLEEP_KB:-209715200}"   # 200 GiB (KB)
PRED_OMP="${PRED_OMP:-8}"
PRED_NICE="${PRED_NICE:-19}"
PRED_IONICE="${PRED_IONICE:-3}"

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <command> [args...]" >&2
  echo "  e.g. $0 python3 run_verified_full.py predict --harness codex" >&2
  exit 2
fi

# 1) 虚拟内存硬上限（ulimit -v 只对当前 shell 及其子进程生效）
if ! ulimit -v "$PRED_VSLEEP_KB" 2>/dev/null; then
  echo "[predict_guarded] WARN: ulimit -v $PRED_VSLEEP_KB failed (已有限制更低?) — 继续" >&2
fi
_cur_vsz=$(ulimit -v 2>/dev/null || echo unlimited)
echo "[predict_guarded] $(date '+%F %T') ulimit -v = ${_cur_vsz} KB (上限 $((PRED_VSLEEP_KB/1024/1024)) GiB) · OMP=${PRED_OMP} · nice=${PRED_NICE} · ionice=${PRED_IONICE}"

# 2) 线程数上限（OMP/MKL/OPENBLAS/NUMEXPR）
export OMP_NUM_THREADS="$PRED_OMP"
export MKL_NUM_THREADS="$PRED_OMP"
export OPENBLAS_NUM_THREADS="$PRED_OMP"
export NUMEXPR_NUM_THREADS="$PRED_OMP"

# 3) 最低 CPU/IO 优先级 + exec 原命令
exec nice -n "$PRED_NICE" ionice -c "$PRED_IONICE" "$@"
