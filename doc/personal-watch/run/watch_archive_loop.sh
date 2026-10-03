#!/bin/bash
# personal-watch（观察哨）· **archive（历史回溯）agent** 自动推进循环
# 让 cline 读任务书（WATCH_ARCHIVE_TASK.md）连续推进，并每约 PUSH_INTERVAL 秒兜底做一次 git 同步 + commit + push。
# 唤醒间隔自适应（**对齐 BaiZe**：SLEEP_BUSY=60 / SLEEP_WAIT=1800）：
#   WAITING=0（有近期待办，如正在跑计数扫描）→ 短睡 SLEEP_SHORT = 60 秒，连续推进；
#   WAITING=1（无近期待办/等人工定主题）      → 睡 SLEEP_LONG = 1800 秒（30 分钟）。
# 兜底：若本轮 cline 报致命错（模型名错 / 额度耗尽 / hook 失败）→ 无论 WAITING 都**强制短睡重试**。
#
# 启动方式（脱离进程组，防工具超时误杀）:
#   cd <仓库根>/doc/personal-watch/run
#   setsid bash watch_archive_loop.sh > /tmp/watch_archive_loop.log 2>&1 < /dev/null &
# 停止方式:
#   pkill -f watch_archive_loop.sh
#
# ⚠️ 本脚本以生产验证过的 `watch_news_loop.sh` 为模板，沿用全部加固：
#   1) push 前先 fetch + pull --rebase --autostash  2) WAITING 行首正则
#   3) 兜底提交只 add 本线文件  4) 传 --thinking 降推理量  5) tee 输出 + 报错兜底
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_MD="$SCRIPT_DIR/WATCH_ARCHIVE_TASK.md"
CWD="$SCRIPT_DIR"
GIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/../../..")"
REL="doc/personal-watch/run"

# ⚠️ 模型名用 DeepSeek 官方 API 的**规范 ID**：只 `deepseek-flash` / `deepseek-v4-pro`。
MODEL="deepseek-flash"
THINKING="low"                  # 端点勘察/计数为主，不需深推理；要更省可设 none
CLINE_TIMEOUT=1500              # 单次 cline 最多 25 分钟
PUSH_INTERVAL=18000             # 每 5 小时兜底同步一次
SLEEP_SHORT=60                  # WAITING=0 / 失败重试
SLEEP_LONG=1800                 # WAITING=1
MEMORY="$SCRIPT_DIR/MEMORY_ARCHIVE.md"
LAST_PUSH="/tmp/watch_archive_last_push"
CLINE_LOG="/tmp/watch_archive_cline_last.log"

git_sync_and_push() {
    local now last counts behind ahead
    now=$(date +%s); last=0
    [ -f "$LAST_PUSH" ] && last="$(cat "$LAST_PUSH" 2>/dev/null || echo 0)"
    if [ $((now - last)) -lt "$PUSH_INTERVAL" ]; then return; fi
    echo "[push] $(date '+%F %T') push interval reached, syncing ..."
    cd "$GIT_ROOT" || return
    if ! timeout 120 git fetch origin; then echo "[push] fetch FAILED - skip."; return; fi
    counts="$(git rev-list --left-right --count origin/main...HEAD 2>/dev/null || echo '0 0')"
    behind="$(echo "$counts" | awk '{print $1}')"; ahead="$(echo "$counts" | awk '{print $2}')"
    echo "[push] ahead=${ahead:-0} behind=${behind:-0}"
    if [ "${behind:-0}" -gt 0 ]; then
        if git pull --rebase --autostash origin main; then echo "[push] pull --rebase OK."
        else echo "[push] pull --rebase FAILED - abort."; git rebase --abort >/dev/null 2>&1 || true; return; fi
    fi
    git add -- "$REL/MEMORY_ARCHIVE.md" "$REL/archive" "$REL/daily-memories-archive" 2>/dev/null
    if git diff --cached --quiet; then echo "[push] nothing of ours to commit."
    else git commit -m "archive auto-commit $(date '+%F %T')" >/dev/null 2>&1 && echo "[push] committed." || echo "[push] commit failed."; fi
    if git push origin main 2>&1; then echo "[push] push OK."; else echo "[push] push FAILED (retry next cycle)."; fi
    date +%s > "$LAST_PUSH"
}

waiting_is_1() {
    [ -f "$MEMORY" ] || return 0
    grep -qE '^WAITING:[[:space:]]*1' "$MEMORY" 2>/dev/null
}

FATAL_RE='(supported API model names|额度已用完|hook dispatch failed|[Uu]nauthoriz|[Aa]uthentication (failed|error)|请等待[0-9]+分钟)'

while true; do
    echo "[loop] $(date '+%F %T') wake up, invoking cline ..."
    FORCE_SHORT=0
    if [[ -f "$TASK_MD" ]]; then
        prompt="$(< "$TASK_MD")"
        cline -c "$CWD" --auto-approve true -m "$MODEL" -t "$CLINE_TIMEOUT" --thinking "$THINKING" "$prompt" < /dev/null 2>&1 | tee "$CLINE_LOG"
        rc="${PIPESTATUS[0]}"
        echo "[loop] $(date '+%F %T') cline returned (exit ${rc}); log=$CLINE_LOG"
        if [ "${rc:-0}" -ne 0 ] || grep -qiE "$FATAL_RE" "$CLINE_LOG" 2>/dev/null; then
            FORCE_SHORT=1; echo "[loop] $(date '+%F %T') ⚠️ 检测到 cline 失败/报错 → 强制短睡重试"
        fi
    else
        echo "[loop] $(date '+%F %T') TASK_MD missing at $TASK_MD"; FORCE_SHORT=1
    fi
    git_sync_and_push
    if [ "$FORCE_SHORT" -eq 1 ]; then echo "[loop] 失败重试 → sleep ${SLEEP_SHORT}s"; sleep "$SLEEP_SHORT"
    elif waiting_is_1; then echo "[loop] WAITING=1 → sleep ${SLEEP_LONG}s"; sleep "$SLEEP_LONG"
    else echo "[loop] WAITING=0 → sleep ${SLEEP_SHORT}s"; sleep "$SLEEP_SHORT"; fi
done
