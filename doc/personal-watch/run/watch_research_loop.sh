#!/bin/bash
# personal-watch（观察哨）· **research agent** 自动推进循环（arXiv 论文采集/整理）
# 让 cline 读任务书（WATCH_RESEARCH_TASK.md）连续推进，并每约 PUSH_INTERVAL 秒兜底做一次 git 同步 + commit + push。
# ⏰ 唤醒节律（**2026-10-07 用户令：由「每 30 分钟」改为「每天 2 次 —— 06:00 / 18:00」**）：
#   定时模式（**默认**，SCHEDULE_HOURS=6,18）：只在时窗边界调用 cline；其余时间**纯 bash 分段睡眠（零 token）**，
#     每 SLEEP_CHUNK 秒刷新存活标记 /tmp/watch_research_loop.hb（供外部判活）—— 目的就是「**别再烧用户自己的 token**」。
#   旧模式（回退）：环境变量 `WATCH_SCHEDULE_HOURS=`（置空）⇒ 恢复 WAITING 自适应（0→60s 连续推进 / 1→1800s）。
#   时窗内致命错：**最多重试 SCHEDULE_RETRY_MAX 次**，之后等下个时窗（🚫 不做 60s 死循环重试 —— 那会疯狂烧 token）。
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
SLEEP_SHORT=60                  # 【仅旧模式】WAITING=0 / 失败重试：短睡 1 分钟（= BaiZe SLEEP_BUSY）
SLEEP_LONG=1800                 # 【仅旧模式】WAITING=1（无近期待办）→ 睡 30 分钟（= BaiZe SLEEP_WAIT）
# ── ⏰ 定时唤醒时窗（2026-10-07 用户令：每天 2 次 · 06:00 / 18:00 · 本地时区）──────
SCHEDULE_HOURS="${WATCH_SCHEDULE_HOURS-6,18}"   # 逗号分隔的小时；**置空 ⇒ 回退旧模式**
SLEEP_CHUNK=300                 # 时窗内分段睡：每 5 分钟刷新存活标记（零 token；可被 SIGTERM 立刻打断）
SLEEP_RETRY=300                 # 时窗内 cline 失败后的重试等待
SCHEDULE_RETRY_MAX=1            # 同一时窗内最多重试 1 次 ⇒ 之后等下个时窗（防 60s 死循环烧 token）
LOOP_HB="/tmp/watch_research_loop.hb"   # 零 token 存活标记：loop 活着、只是在等时窗（判活不必等提交）
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

# ── ⏰ 定时唤醒：下一个时窗的 epoch 秒（SCHEDULE_HOURS=6,18 ⇒ 06:00 / 18:00）──
next_slot_epoch() {
    local now h target best=""
    now=$(date +%s)
    local IFS=','
    for h in $SCHEDULE_HOURS; do
        h="${h//[^0-9]/}"                       # 去掉空格等杂字符
        [ -z "$h" ] && continue
        h="$(printf '%02d:00' "$((10#$h))")"    # → 06:00（10# 防前导零被判成八进制）
        if ! target=$(date -d "today $h" +%s 2>/dev/null); then continue; fi
        if [ "$target" -le "$now" ]; then       # 今天该时窗已过 ⇒ 顺延到明天
            # ⚠️ 必须写 "tomorrow $h"：GNU date 会把 "06:00 +1 day" 里的 `+1` 当成**时区偏移**（→ 13:00，实测踩过）
            target=$(date -d "tomorrow $h" +%s 2>/dev/null) || continue
        fi
        if [ -z "$best" ] || [ "$target" -lt "$best" ]; then best="$target"; fi
    done
    unset IFS
    [ -z "$best" ] && return 1
    echo "$best"
}

# ── 睡到下一个时窗（分段睡；**不调用 cline ⇒ 零 token**）──
sleep_until_next_slot() {
    local target now remain chunk ticks=0
    if ! target=$(next_slot_epoch); then
        echo "[loop] $(date '+%F %T') ⚠️ SCHEDULE_HOURS 为空/非法 → 回退 sleep ${SLEEP_LONG}s"
        sleep "$SLEEP_LONG"
        return
    fi
    now=$(date +%s)
    remain=$((target - now))
    [ "$remain" -le 0 ] && remain=1
    echo "[loop] $(date '+%F %T') ⏰ 定时模式：下次唤醒 = $(date -d "@$target" '+%F %T %Z')（$((remain / 60))min 后；每天 2 次 · 时窗 ${SCHEDULE_HOURS}）"
    while [ "$remain" -gt 0 ]; do
        chunk="$SLEEP_CHUNK"
        [ "$remain" -lt "$chunk" ] && chunk="$remain"
        sleep "$chunk"
        remain=$((remain - chunk))
        date +%s > "$LOOP_HB" 2>/dev/null || true      # 零 token 存活标记
        ticks=$((ticks + 1))
        if [ $((ticks % (1800 / SLEEP_CHUNK))) -eq 0 ]; then
            echo "[loop] $(date '+%F %T') 💤 等时窗中（剩余 $((remain / 60))min；未调 cline = 零 token）"
        fi
    done
}

# ── 启动横幅：让外部一眼看出「跑的是哪种模式 / 时窗」（中继据此核验）──
if [ -n "$SCHEDULE_HOURS" ]; then
    echo "[loop] ⏰ 定时模式已启用：唤醒时窗 = ${SCHEDULE_HOURS}（每天 2 次）· 存活标记 = $LOOP_HB · 回退：WATCH_SCHEDULE_HOURS= 置空"
    if _t=$(next_slot_epoch); then
        echo "[loop] ⏰ 时窗参考：此刻之后的下一个时窗 = $(date -d "@$_t" '+%F %T %Z')（首轮唤醒=立即执行；各轮跑完会实时重算）"
    fi
else
    echo "[loop] 🔁 旧模式（WAITING 自适应）：SLEEP_SHORT=${SLEEP_SHORT}s / SLEEP_LONG=${SLEEP_LONG}s"
fi

RETRY=0     # 本时窗内的致命错重试计数（定时模式用）
while true; do
    echo "[loop] $(date '+%F %T') wake up, invoking cline ... [mode=${SCHEDULE_HOURS:-adaptive}]"
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
    date +%s > "$LOOP_HB" 2>/dev/null || true       # 每轮唤醒回来都刷新存活标记
    if [ -n "$SCHEDULE_HOURS" ]; then
        # ── ⏰ 定时模式：每天 2 次（06:00 / 18:00）──
        if [ "$FORCE_SHORT" -eq 1 ]; then
            RETRY=$((RETRY + 1))
            if [ "$RETRY" -le "$SCHEDULE_RETRY_MAX" ]; then
                echo "[loop] $(date '+%F %T') ⚠️ cline 失败/报错 → 本时窗内重试 ${RETRY}/${SCHEDULE_RETRY_MAX}（sleep ${SLEEP_RETRY}s 后立刻重试）"
                sleep "$SLEEP_RETRY"
                continue
            fi
            echo "[loop] $(date '+%F %T') 🛑 已达本时窗重试上限（${SCHEDULE_RETRY_MAX}）→ 不再重试（防死循环烧 token），等下一个时窗"
        fi
        RETRY=0                                     # 无致命错（或重试已耗尽）⇒ 清零，睡到下一个时窗
        sleep_until_next_slot
    else
        # ── 旧模式（WAITING 自适应；仅当 WATCH_SCHEDULE_HOURS 被置空）──
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
    fi
done
