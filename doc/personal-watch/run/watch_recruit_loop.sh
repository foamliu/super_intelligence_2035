#!/bin/bash
# personal-watch（观察哨）· **recruit agent** 自动推进循环（Boss 直聘招聘链路：继承 HR 记忆与能力 + 常态化推进）
# 让 cline 读任务书（WATCH_RECRUIT_TASK.md）连续推进，并每约 PUSH_INTERVAL 秒兜底做一次 git 同步 + commit + push。
#
# ⚠️ 运行位置（**与 news/research 不同**）：本线要驱动浏览器（Boss 登录态 + playwright-mcp），
#    故 **必须跑在「持有 Boss 登录态的那台机器」上**（当前 = 本 Windows 机）。
#    Windows 下请用 **Git Bash / WSL**（需要 GNU `date -d`）；`setsid` 在 Git Bash 可能没有 ⇒ 用 `nohup ... &`。
#
# ⏰ 唤醒节律（沿用 2026-10-07 用户令：每天 2 次 —— 06:00 / 18:00）：
#   定时模式（**默认**，SCHEDULE_HOURS=6,18）：只在时窗边界调用 cline；其余时间**纯 bash 分段睡眠（零 token）**，
#     每 SLEEP_CHUNK 秒刷新存活标记 /tmp/watch_recruit_loop.hb（供外部判活）—— 目的就是「**别再烧用户自己的 token**」。
#   ⏱ **间隔模式（临时）**：环境变量 `WATCH_INTERVAL_MIN=<分钟>` ⇒ 固定每 N 分钟唤醒一次
#     （**优先级最高**：interval > schedule(6,18) > adaptive；置空即回退）。
#   旧模式（回退）：环境变量 `WATCH_SCHEDULE_HOURS=`（置空）⇒ 恢复 WAITING 自适应（0→60s 连续推进 / 1→1800s）。
#   时窗内致命错：**最多重试 SCHEDULE_RETRY_MAX 次**，之后等下个时窗（🚫 不做 60s 死循环重试 —— 那会疯狂烧 token）。
#
# 启动方式（脱离进程组，防工具超时误杀；Linux/WSL）:
#   cd <仓库根>/doc/personal-watch/run
#   setsid bash watch_recruit_loop.sh > /tmp/watch_recruit_loop.log 2>&1 < /dev/null &
# Git Bash（无 setsid）替代:
#   cd <仓库根>/doc/personal-watch/run
#   nohup bash watch_recruit_loop.sh > /tmp/watch_recruit_loop.log 2>&1 &
#
# 停止方式:
#   pkill -f watch_recruit_loop.sh
#
# ⚠️ 本脚本以 `watch_research_loop.sh`（已生产验证）为模板，沿用三处防坑 + 全部加固:
#   1) push 前先 fetch + pull --rebase --autostash（只 push 不 pull，远端一旦前进就永久卡死）
#   2) WAITING 正则收紧为**行首**匹配（旧版 WAITING:[* ]*1 会误匹配正文里的散文）
#   3) commit 只 add 本线自己的文件（避免卷入其他线/兄弟项目的在途文件）
#   4) 传 `--thinking`（降推理量省 token）；记录 cline 输出并检测"报错却 exit 0"
set -u

# 以脚本自身所在目录为基准，任务书 + 记忆文件均与脚本同目录（run/）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_MD="$SCRIPT_DIR/WATCH_RECRUIT_TASK.md"
CWD="$SCRIPT_DIR"
# git 仓库根目录
GIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/../../..")"
REL="doc/personal-watch/run"     # 本任务在仓库中的相对目录（只提交这里的文件）

# ── 继承源（`$HR_DIR`）**不再由 loop 处理**：loop 只负责唤醒，记忆/能力的可达性由任务书 §0 规定，
#    缺省时 agent 用 §0.2/§0.3 内嵌摘要兜底。此处不再打印/自检（避免误导为"功能依赖"）。──

# ⚠️ 模型名用 DeepSeek 官方 API 的**规范 ID**（2026-10-03 实测）：
#     `deepseek-flash`（1M ctx，text+image）/ `deepseek-v4-pro`（1M ctx，text）。
MODEL="deepseek-flash"          # 招聘流程编排/起草用 flash；要更强可换 deepseek-v4-pro
# 推理强度（cline `--thinking`）：none|low|medium|high|xhigh；省略=用 provider 默认（flash 默认 high）。
THINKING="low"                  # 读记忆+巡检+起草为主，不需要深推理；要更省可设 none
CLINE_TIMEOUT=1500              # 单次 cline 最多 25 分钟（与 BaiZe 一致）
PUSH_INTERVAL=1800              # 每 30 分钟兜底同步一次（agent 每轮自己也会提交）
SLEEP_SHORT=60                  # 【仅旧模式】WAITING=0 / 失败重试：短睡 1 分钟
SLEEP_LONG=1800                 # 【仅旧模式】WAITING=1（无近期待办）→ 睡 30 分钟
# ── ⏰ 定时唤醒时窗（每天 2 次 · 06:00 / 18:00 · 本地时区）──────
SCHEDULE_HOURS="${WATCH_SCHEDULE_HOURS-6,18}"   # 逗号分隔的小时；**置空 ⇒ 回退旧模式**
SLEEP_CHUNK=300                 # 时窗内分段睡：每 5 分钟刷新存活标记（零 token；可被 SIGTERM 立刻打断）
SLEEP_RETRY=300                 # 时窗内 cline 失败后的重试等待
SCHEDULE_RETRY_MAX=1            # 同一时窗内最多重试 1 次 ⇒ 之后等下个时窗（防 60s 死循环烧 token）
# ── ⏱ 间隔唤醒（**临时模式**：`WATCH_INTERVAL_MIN=30` ⇒ 每 30 分钟唤醒一次；**优先级最高**；置空即回退「时窗 / 自适应」）──
INTERVAL_MIN="${WATCH_INTERVAL_MIN-}"
LOOP_HB="/tmp/watch_recruit_loop.hb"   # 零 token 存活标记：loop 活着、只是在等时窗
# 模式判定（优先级）：interval > schedule(6,18) > adaptive
if [ -n "${INTERVAL_MIN:-}" ] && [ "${INTERVAL_MIN:-0}" -gt 0 ] 2>/dev/null; then
    MODE="interval"
elif [ -n "$SCHEDULE_HOURS" ]; then
    MODE="schedule"
else
    MODE="adaptive"
fi
MEMORY="$SCRIPT_DIR/MEMORY_RECRUIT.md"
LAST_PUSH="/tmp/watch_recruit_last_push"
CLINE_LOG="/tmp/watch_recruit_cline_last.log"   # cline 本轮输出，用于检测"报错却 exit 0"

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
    git add -- "$REL/MEMORY_RECRUIT.md" "$REL/recruit" "$REL/daily-memories-recruit" 2>/dev/null
    if git diff --cached --quiet; then
        echo "[push] nothing of ours to commit."
    else
        if git commit -m "recruit auto-commit $(date '+%F %T')" >/dev/null 2>&1; then
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

# ── ⏱ 间隔模式：固定每 INTERVAL_MIN 分钟唤醒一次（同样分段睡 + 零 token + 刷新存活标记）──
sleep_until_next_interval() {
    local secs=$(( INTERVAL_MIN * 60 ))
    local remain=$secs chunk ticks=0
    echo "[loop] $(date '+%F %T') ⏱ 间隔模式：每 ${INTERVAL_MIN} 分钟唤醒一次（下次 ≈ $(date -d "@$(( $(date +%s) + secs ))" '+%F %T %Z')）"
    while [ "$remain" -gt 0 ]; do
        chunk="$SLEEP_CHUNK"
        [ "$remain" -lt "$chunk" ] && chunk="$remain"
        sleep "$chunk"
        remain=$((remain - chunk))
        date +%s > "$LOOP_HB" 2>/dev/null || true      # 零 token 存活标记
        ticks=$((ticks + 1))
        if [ $((ticks % (1800 / SLEEP_CHUNK))) -eq 0 ]; then
            echo "[loop] $(date '+%F %T') ⏱ 间隔等待中（剩余 $((remain / 60))min；未调 cline = 零 token）"
        fi
    done
}

# ── 启动横幅：让外部一眼看出「跑的是哪种模式 / 时窗」（中继据此核验）──
if [ "$MODE" = "interval" ]; then
    echo "[loop] ⏱ 间隔模式已启用：每 ${INTERVAL_MIN} 分钟唤醒一次 · 存活标记 = $LOOP_HB · 回退：WATCH_INTERVAL_MIN= 置空"
elif [ "$MODE" = "schedule" ]; then
    echo "[loop] ⏰ 定时模式已启用：唤醒时窗 = ${SCHEDULE_HOURS}（每天 2 次）· 存活标记 = $LOOP_HB · 回退：WATCH_SCHEDULE_HOURS= 置空"
    if _t=$(next_slot_epoch); then
        echo "[loop] ⏰ 时窗参考：此刻之后的下一个时窗 = $(date -d "@$_t" '+%F %T %Z')（首轮唤醒=立即执行；各轮跑完会实时重算）"
    fi
else
    echo "[loop] 🔁 旧模式（WAITING 自适应）：SLEEP_SHORT=${SLEEP_SHORT}s / SLEEP_LONG=${SLEEP_LONG}s"
fi
# （原「🧬 继承源自检」横幅已移除：loop 对 $HR_DIR 无功能依赖，可达性交由 agent 按任务书 §0 处理。）

RETRY=0     # 本时窗内的致命错重试计数（定时模式用）
while true; do
    echo "[loop] $(date '+%F %T') wake up, invoking cline ... [mode=${MODE}${INTERVAL_MIN:+:${INTERVAL_MIN}min}]"
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
    if [ "$MODE" = "schedule" ] || [ "$MODE" = "interval" ]; then
        # ── ⏰ 定时（每天 2 次 06:00/18:00）/ ⏱ 间隔（每 30min）──
        if [ "$FORCE_SHORT" -eq 1 ]; then
            RETRY=$((RETRY + 1))
            if [ "$RETRY" -le "$SCHEDULE_RETRY_MAX" ]; then
                echo "[loop] $(date '+%F %T') ⚠️ cline 失败/报错 → 本轮内重试 ${RETRY}/${SCHEDULE_RETRY_MAX}（sleep ${SLEEP_RETRY}s 后立刻重试）"
                sleep "$SLEEP_RETRY"
                continue
            fi
            echo "[loop] $(date '+%F %T') 🛑 已达重试上限（${SCHEDULE_RETRY_MAX}）→ 不再重试（防死循环烧 token），等下一个唤醒"
        fi
        RETRY=0                                     # 无致命错（或重试已耗尽）⇒ 清零，睡到下一次唤醒
        if [ "$MODE" = "interval" ]; then
            sleep_until_next_interval
        else
            sleep_until_next_slot
        fi
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
