#!/bin/bash
# BaiZe Stage(iii) 视觉编码器预训练（四架构对比）自动推进循环：
# 让 cline 读任务书连续推进，并每约 PUSH_INTERVAL 秒兜底做一次 git commit + push（无人值守时保证成果不丢）。
# 唤醒间隔自适应：读 MEMORY_VISION.md 的 WAITING 标志——无阻塞(0)约 1 分钟续跑，有异步阻塞(1)约 30 分钟轮询省 token。
# 十一假期 2026-09-30 ~ 10-08 由本脚本驱动 research agent 逐步推进。
# 启动方式（脱离进程组，防工具超时误杀）:
#   setsid bash /path/to/baize_vision_loop.sh > /tmp/baize_vision_loop.log 2>&1 < /dev/null &
set -u

# 以脚本自身所在目录为基准，任务书 + 记忆文件均与脚本同目录（run/）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_MD="$SCRIPT_DIR/BAIZE_VISION_TASK.md"
CWD="$SCRIPT_DIR"
# git 仓库根目录（run/ 的上级 super_intelligence_2035）
GIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo '/nas_train/app.e0031982/code/super_intelligence_2035')"

MODEL="glm-5.2"                     # 编排模型（deepseek-v4-pro-fp4 额度已耗尽）

# 🔑 glm-5.2 key
CLINE_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23"
CLINE_BASE="http://agi-gateway.cxmt.com/cloud/v1"

CLINE_TIMEOUT=1500              # 单次 cline 最多 25 分钟
PUSH_INTERVAL=18000             # 每 5 小时 git push 一次（4~6 小时间隔内）
SLEEP_BUSY=60                   # 无阻塞任务时的唤醒间隔：约 1 分钟（连续推进，不空耗假期）
SLEEP_WAIT=1800                 # 有异步阻塞任务(训练 running)时的唤醒间隔：30 分钟（省 token）
MEMORY="$SCRIPT_DIR/MEMORY_VISION.md"
LAST_PUSH="/tmp/baize_vision_last_push"

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
        env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u ftp_proxy -u FTP_PROXY \
            -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE \
          cline -c "$CWD" --auto-approve true -m "$MODEL" -k "$CLINE_KEY" -b "$CLINE_BASE" -t "$CLINE_TIMEOUT" "$prompt" < /dev/null
        echo "[loop] $(date '+%F %T') cline returned (exit $?), checking git push ..."
    else
        echo "[loop] $(date '+%F %T') TASK_MD missing at $TASK_MD"
    fi
    git_push_if_needed
    # 自适应睡眠：WAITING=1（有训练等异步任务 running）→ 长睡 30 分钟省 token；
    # WAITING=0（无阻塞、应连续推进）→ 短睡 1 分钟，让 cline 尽快续跑下一轮。
    SLEEP="$SLEEP_BUSY"
    if grep -qE '^[- ]*WAITING: *1' "$MEMORY" 2>/dev/null; then
        SLEEP="$SLEEP_WAIT"
        echo "[loop] $(date '+%F %T') WAITING=1（异步任务 running）→ sleep ${SLEEP}s"
    else
        echo "[loop] $(date '+%F %T') WAITING=0（无阻塞）→ sleep ${SLEEP}s"
    fi
    sleep "$SLEEP"
done