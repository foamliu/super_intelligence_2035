#!/bin/bash
# personal-watch（观察哨）· **research agent** 自动推进循环（arXiv 论文采集/整理）
# 让 cline 读任务书（WATCH_RESEARCH_TASK.md）连续推进，并每约 PUSH_INTERVAL 秒兜底做一次 git 同步 + commit + push。
# 唤醒间隔自适应（**与 BaiZe 的 loop 完全一致**：SLEEP_BUSY=60 / SLEEP_WAIT=1800）：
#   WAITING=0（有近期待办，如某检索要追）→ 短睡 SLEEP_SHORT = 60 秒，连续推进；
#   WAITING=1（无近期待办，常态）        → 睡 SLEEP_LONG = 1800 秒（30 分钟）省 token。
# 兜底：若本轮 cline 报致命错（模型名错 / 额度耗尽 / hook 失败）→ 无论 WAITING 都**强制短睡重试**，
#   避免"报错却 exit 0 → 白睡长觉"（BaiZe 记录过这个坑，news 线也踩过）。
#
# 启动方式（脱离进程组，防工具超时误杀）:
#   cd <仓库根>/doc/personal-watch/run
#   setsid bash watch_research_loop.sh > /tmp/watch_research_loop.log 2>&1 < /dev/null &
#
# 停止方式:
#   pkill -f watch_research_loop.sh
#
# ⚠️ 本脚本以 `watch_news_loop.sh`（已在生产验证）为模板，沿用三处防坑 + 全部加固:
#   1) push 前先 fetch + pull --rebase --autostash（只 push 不 pull，远端一旦前进就永久卡死）
#   2) WAITING 正则收紧为**行首**匹配（旧版 WAITING:[* ]*1 会误匹配正文里的散文）
#   3) commit 只 add 本线自己的文件（避免卷入其他线/兄弟项目的在途文件）
#   4) 传 `--thinking`（降推理量省 token）；记录 cline 输出并检测"报错却 exit 0"
set -u

# 以脚本自身所在目录为基准，任务书 + 记忆文件均与脚本同目录（run/）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_MD="$SCRIPT_DIR/WATCH_RESEARCH_TASK.md"
CWD="$SCRIPT_DIR"
# git 仓库根目录
GIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/../../..")"
REL="doc/personal-watch/run"     # 本任务在仓库中的相对目录（只提交这里的文件）

# ⚠️ 模型名用 DeepSeek 官方 API 的**规范 ID**（2026-10-03 实测 `GET https://api.deepseek.com/models` → HTTP 200）：
#     `deepseek-flash`（1M ctx，text+image）/ `deepseek-v4-pro`（1M ctx，text）。
#   🚫 `deepseek-v4-pro-fp4` 本机网关不认；🚫 `deepseek-v4-flash` 不是官方 ID。
MODEL="deepseek-flash"          # 论文检索/整理用 flash（便宜/快）；要更强可换 deepseek-v4-pro
# 推理强度（cline `--thinking`）：none|low|medium|high|xhigh；省略=用 provider 默认（flash 默认 high）。
THINKING="low"                  # 采集+整理为主，不需要深推理；要更省可设 none
CLINE_TIMEOUT=1500              # 单次 cline 最多 25 分钟（与 BaiZe 一致）
PUSH_INTERVAL=1800              # 每 30 分钟兜底同步一次（2026-10-06 由 18000/5h 缩短，与 BaiZe 一致；agent 每轮自己也会提交）
SLEEP_SHORT=60                  # WAITING=0 / 失败重试：短睡 1 分钟（= BaiZe SLEEP_BUSY）
SLEEP_LONG=1800                 # WAITING=1（无近期待办）→ 睡 30 分钟（= BaiZe SLEEP_WAIT）
MEMORY="$SCRIPT_DIR/MEMORY_RESEARCH.md"
LAST_PUSH="/tmp/watch_research_last_push"
CLINE_LOG="/tmp/watch_research_cline_last.log"   # cline 本轮输出，用于检测"报错却 exit 0"

# ── git 兜底同步：fetch → 必要时 pull --rebase → 只提交本线文件 → push ──
git_sync_and_push() {
    local now last counts behind ahead
    now=$(date +%s)
    last=0
    [ -f "$LAST_PUSH" ] && last="$(cat "$LAST_PUSH" 2>/dev/null || echo 0)"
    if [ $((now - last)) -lt "$PUSH_INTERVAL" ]; then
        return
    fi
    echo "[push] $(date '+%F %T') push interval reached, syncing ..."
    cd "$GIT_ROOT" || return

    # 1) 先同步远端（共享工作副本：别的线可能已经 pull 过，此处通常是 no-op）
    if ! timeout 120 git fetch origin; then
        echo "[push] fetch FAILED (network?) - skip this cycle."
        return
    fi
    counts="$(git rev-list --left-right --count origin/main...HEAD 2>/dev/null || echo '0 0')"
    behind="$(echo "$counts" | awk '{print $1}')"
    ahead="$(echo "$counts" | awk '{print $2}')"
    echo "[push] ahead=${ahead:-0} behind=${behind:-0}"
    if [ "${behind:-0}" -gt 0 ]; then
        if git pull --rebase --autostash origin main; then
            echo "[push] pull --rebase OK."
        else
            echo "[push] pull --rebase FAILED (conflict?) - aborting rebase, skip this cycle."
            git rebase --abort >/dev/null 2>&1 || true
            return
        fi
    fi

    # 2) 只提交本线自己的文件（避免卷入其他线/兄弟项目的在途文件）
    git add -- "$REL/MEMORY_RESEARCH.md" "$REL/research" "$REL/daily-memories-research" 2>/dev/null
    if git diff --cached --quiet; then
        echo "[push] nothing of ours to commit."
    else
        if git commit -m "research auto-commit $(date '+%F %T')" >/dev/null 2>&1; then
            echo "[push] committed."
        else
            echo "[push] commit failed."
        fi
    fi

    # 3) 推送
    if git push origin main 2>&1; then
        echo "[push] push OK."
    else
        echo "[push] push FAILED (will retry next cycle)."
    fi
    date +%s > "$LAST_PUSH"
}

# WAITING 判定：只认**行首**的 WAITING 字段；文件不存在时按"等待"处理（省 token）
waiting_is_1() {
    [ -f "$MEMORY" ] || return 0
    grep -qE '^WAITING:[[:space:]]*1' "$MEMORY" 2>/dev/null
}

# cline 级致命错误特征（**不要**用裸 `error:` —— agent 干活时会把 API 报错当证据贴出来，会误判）
FATAL_RE='(supported API model names|额度已用完|hook dispatch failed|[Uu]nauthoriz|[Aa]uthentication (failed|error)|请等待[0-9]+分钟)'

while true; do
    echo "[loop] $(date '+%F %T') wake up, invoking cline ..."
    FORCE_SHORT=0
    if [[ -f "$TASK_MD" ]]; then
        prompt="$(< "$TASK_MD")"
        cline -c "$CWD" --auto-approve true -m "$MODEL" -t "$CLINE_TIMEOUT" --thinking "$THINKING" "$prompt" < /dev/null 2>&1 | tee "$CLINE_LOG"
        rc="${PIPESTATUS[0]}"
        echo "[loop] $(date '+%F %T') cline returned (exit ${rc}); log=$CLINE_LOG"
        # 兜底：cline 常"报错仍 exit 0"（模型名错 / 额度耗尽）→ 从日志抓错，失败则强制短睡重试，不空耗
        if [ "${rc:-0}" -ne 0 ] || grep -qiE "$FATAL_RE" "$CLINE_LOG" 2>/dev/null; then
            FORCE_SHORT=1
            echo "[loop] $(date '+%F %T') ⚠️ 检测到 cline 失败/报错 → 本轮强制短睡重试（不睡长觉）"
        fi
    else
        echo "[loop] $(date '+%F %T') TASK_MD missing at $TASK_MD"
        FORCE_SHORT=1
    fi
    git_sync_and_push
    if [ "$FORCE_SHORT" -eq 1 ]; then
        echo "[loop] $(date '+%F %T') 失败/异常重试 → sleep ${SLEEP_SHORT}s"
        sleep "$SLEEP_SHORT"
    elif waiting_is_1; then
        echo "[loop] $(date '+%F %T') WAITING=1 (no pending follow-up) → sleep ${SLEEP_LONG}s"
        sleep "$SLEEP_LONG"
    else
        echo "[loop] $(date '+%F %T') WAITING=0 (pending follow-up) → sleep ${SLEEP_SHORT}s"
        sleep "$SLEEP_SHORT"
    fi
done
