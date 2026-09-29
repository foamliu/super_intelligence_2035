#!/bin/bash
# BaiZe 2B 架构搜索（从零训练）自动推进循环：每隔 INTERVAL 秒让 cline 读任务书执行一步，
# 并每约 PUSH_INTERVAL 秒兜底做一次 git commit + push（假期无人值守时保证成果不丢）。
# 十一假期 2026-09-30 ~ 10-08 由本脚本驱动 research agent 逐步推进。
# 启动方式（脱离进程组，防工具超时误杀）:
#   setsid bash /path/to/baize_2b_search_loop.sh > /tmp/baize_2b_loop.log 2>&1 < /dev/null &
set -u

# 以脚本自身所在目录为基准，任务书 + 记忆文件均与脚本同目录（run/）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_MD="$SCRIPT_DIR/BAIZE_2B_ARCH_SEARCH_TASK.md"
CWD="$SCRIPT_DIR"
# git 仓库根目录（run/ 的上级 super_intelligence_2035）
GIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo '/nas_train/app.e0031982/code/super_intelligence_2035')"

MODEL="deepseek-v4-pro-fp4"      # 换成你用于工程任务的模型
INTERVAL=1800                   # 30 分钟醒来一次
CLINE_TIMEOUT=1500              # 单次 cline 最多 25 分钟
PUSH_INTERVAL=18000             # 每 5 小时 git push 一次（4~6 小时间隔内）
LAST_PUSH="/tmp/baize_2b_last_push"

git_push_if_needed() {
    local now last
    now=$(date +%s)
    last=0
    [ -f "$LAST_PUSH" ] && last="$(cat "$LAST_PUSH" 2>/dev/null)"
    if [ $((now - last)) -lt "$PUSH_INTERVAL" ]; then
        return
    fi
    echo "[push] $(date '+%F %T') push interval reached, committing + pushing ..."
    cd "$GIT_ROOT" || return
    git add -A
    if git commit -m "auto-commit $(date '+%F %T')" >/dev/null 2>&1; then
        echo "[push] committed."
    else
        echo "[push] nothing to commit."
    fi
    if git push origin main 2>&1; then
        echo "[push] push OK."
    else
        echo "[push] push FAILED (will retry next cycle)."
    fi
    date +%s > "$LAST_PUSH"
}

while true; do
    echo "[loop] $(date '+%F %T') wake up, invoking cline ..."
    if [[ -f "$TASK_MD" ]]; then
        prompt="$(< "$TASK_MD")"
        cline -c "$CWD" --auto-approve true -m "$MODEL" -t "$CLINE_TIMEOUT" "$prompt" < /dev/null
        echo "[loop] $(date '+%F %T') cline returned (exit $?), checking git push ..."
    else
        echo "[loop] $(date '+%F %T') TASK_MD missing at $TASK_MD"
    fi
    git_push_if_needed
    sleep "$INTERVAL"
done
