#!/bin/bash
# 消融评测自动推进循环（1-shot 快速版）：每个配置只跑 1 轮，间隔更短。
# 启动方式（脱离进程组，防工具超时误杀）:
#   setsid bash /nasdata/app.e0031982/code/ZhuLong_DAC2027/run/ablation_run_loop_1shot.sh > /tmp/ablation_loop_1shot.log 2>&1 < /dev/null &
set -u

TASK_MD="/nasdata/app.e0031982/code/ZhuLong_DAC2027/run/ablation_run_task_1shot.md"
MEMORY_MD="/nasdata/app.e0031982/code/ZhuLong_DAC2027/run/MEMORY_1shot.md"
CWD="/nasdata/app.e0031982/code/ZhuLong_DAC2027/run"
MODEL="deepseek-v4-pro-fp4"
INTERVAL=1800          # 30 分钟醒来一次（原版 1h，1-shot 更快）
CLINE_TIMEOUT=5400     # 单次 cline 最多 90 分钟（含打分）

while true; do
    # 检查是否已完成（agent 会在 MEMORY.md 中写 PHASE=done_all）
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
