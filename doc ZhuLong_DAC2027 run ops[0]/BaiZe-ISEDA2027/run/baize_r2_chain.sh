#!/bin/bash
# BaiZe Stage(i) R2 编排链：等 P-1 LR 网格扩展 sweep 完成后 → 串行跑 P-2（补 seed n=5）→ P-3（架构对比 5000 步）。
#   每个阶段前后记录 GPU 占用核验（nvidia-smi --query-compute-apps）。
#   启动：setsid bash baize_r2_chain.sh & （PPID=1 真后台）
set -uo pipefail
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
LOG=/tmp/baize_r2_chain.log

gpuv() {
    echo "--- nvidia-smi @ $(date '+%F %T') ---"
    nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader 2>&1
    echo "---"
}

{
    echo "===== R2 chain START @ $(date '+%F %T') ====="
    echo "waiting for P-1 sweep (baize_p1_sweep.log) to finish ..."
    while ! grep -q "ALL DONE" /tmp/baize_p1_sweep.log 2>/dev/null; do sleep 60; done
    echo "P-1 DONE @ $(date '+%F %T')"
    gpuv

    echo "===== launching P-2 @ $(date '+%F %T') ====="
    bash "$RUN/baize_p2_sweep.sh"
    echo "P-2 DONE @ $(date '+%F %T')"
    gpuv

    echo "===== launching P-3 @ $(date '+%F %T') ====="
    bash "$RUN/baize_p3_sweep.sh"
    echo "P-3 DONE @ $(date '+%F %T')"
    gpuv

    echo "===== R2 chain ALL DONE @ $(date '+%F %T') ====="
} >> "$LOG" 2>&1