#!/bin/bash
# 模型消融评测自动推进循环（5-run 完整版）：依次 glm-5.2 / deepseek-v4-flash / kimi-k2.6-cloud / doubao，各 5 轮。
#
# ⚠️ 关键区分：本 loop 的 `-m "$MODEL"` 是「编排 agent」的模型（固定 deepseek-v4-pro-fp4，
#   只负责读 MEMORY / pgrep / 打分 / cline auth 切模型）。**被评测的求解 agent 模型**由
#   task book 内的 `cline auth -m <MODEL_ID>` 切换 —— run_cline_script.sh 会读取
#   ~/.cline/data/settings 下的 providers/models（由 cline auth 写入），与本 loop 的 -m 无关。
#   因此 MODEL 这里保持不变即可，切模型完全在 task book 内完成。
#
# 启动方式（脱离进程组，防工具超时误杀）:
#   setsid bash /nasdata/app.e0031982/code/ZhuLong_DAC2027/run/ablation_run_loop_model_full.sh > /tmp/ablation_loop_model_full.log 2>&1 < /dev/null &
set -u

TASK_MD="/nasdata/app.e0031982/code/ZhuLong_DAC2027/run/ablation_run_task_model_full.md"
MEMORY_MD="/nasdata/app.e0031982/code/ZhuLong_DAC2027/run/MEMORY_model_full.md"
CWD="/nasdata/app.e0031982/code/ZhuLong_DAC2027/run"
MODEL="deepseek-v4-pro-fp4"   # 编排 agent 固定主基座（不是被评测模型）
INTERVAL=1800          # 30 分钟醒来一次
CLINE_TIMEOUT=5400     # 单次 cline 最多 90 分钟（含打分）

while true; do
    # 检查是否已完成（agent 会在 MEMORY_model_full.md 中写 PHASE=done_all）
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