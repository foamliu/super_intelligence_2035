#!/bin/bash
# 组件消融 + S2 Φ 轴完整 5-run 自动推进循环
# Phase 1: pure_llm → rag → wo_retrieval (各 5 轮)
# Phase 2: phi_k10 → phi_k3 → phi_k1 → phi_lagged (各 5 轮)
# 启动方式（脱离进程组，防工具超时误杀）:
#   setsid bash /nasdata/app.e0031982/code/ZhuLong_DAC2027/run/ablation_run_loop_component_s2_full.sh > /tmp/ablation_loop_component_s2_full.log 2>&1 < /dev/null &
set -u

TASK_MD="/nasdata/app.e0031982/code/ZhuLong_DAC2027/run/ablation_run_task_component_s2_full.md"
MEMORY_MD="/nasdata/app.e0031982/code/ZhuLong_DAC2027/run/MEMORY_component_full.md"
CWD="/nasdata/app.e0031982/code/ZhuLong_DAC2027/run"
MODEL="deepseek-v4-pro-fp4"
INTERVAL=1800          # 30 分钟醒来一次
CLINE_TIMEOUT=5400     # 单次 cline 最多 90 分钟（含打分）

echo "[loop] $(date '+%F %T') === COMPONENT+S2 FULL LOOP STARTED ==="

while true; do
    # 检查是否已完成
    if [[ -f "$MEMORY_MD" ]] && grep -q 'PHASE=done_all' "$MEMORY_MD" 2>/dev/null; then
        echo "[loop] $(date '+%F %T') PHASE=done_all detected, loop exiting."
        break
    fi

    echo "[loop] $(date '+%F %T') wake up, invoking cline ..."
    if [[ -f "$TASK_MD" ]]; then
        prompt="$(< "$TASK_MD")"
        cline -c "$CWD" --auto-approve true -m "$MODEL" -t "$CLINE_TIMEOUT" "$prompt" < /dev/null
        echo "[loop] $(date '+%F %T') cline returned (exit $?), sleep ${INTERVAL}s ..."
    else
        echo "[loop] $(date '+%F %T') TASK_MD missing at $TASK_MD, sleep ${INTERVAL}s ..."
    fi
    sleep "$INTERVAL"
done

echo "[loop] $(date '+%F %T') === COMPONENT+S2 FULL LOOP EXITED ==="
