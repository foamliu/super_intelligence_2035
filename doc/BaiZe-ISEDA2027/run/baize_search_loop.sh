#!/bin/bash
# BaiZe 1B 架构与超参搜索自动推进循环：每隔 INTERVAL 秒，让 cline 读任务书执行一步。
# 启动方式（脱离进程组，防工具超时误杀）:
#   setsid bash /path/to/baize_search_loop.sh > /tmp/baize_loop.log 2>&1 < /dev/null &
set -u

# 以脚本自身所在目录为基准，任务书与脚本同目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_MD="$SCRIPT_DIR/BAIZE_PRETRAIN_TASK.md"
CWD="$SCRIPT_DIR"

MODEL="deepseek-v4-pro-fp4"      # 换成你用于工程任务的模型
INTERVAL=900                   # 15 分钟醒来一次
CLINE_TIMEOUT=600              # 单次 cline 最多 10 分钟

while true; do
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