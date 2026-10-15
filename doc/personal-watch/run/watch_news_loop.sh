#!/bin/bash
# personal-watch（观察哨）· 新闻 agent 自动推进循环
# 让 cline 读任务书（WATCH_NEWS_TASK.md）连续采集新闻，并每约 PUSH_INTERVAL 秒兜底做一次 git 同步 + commit + push。
# ⏰ 唤醒节律（**2026-10-07 用户令：由「每 30 分钟」改为「每天 2 次 —— 06:00 / 18:00」**）：
#   定时模式（**默认**，SCHEDULE_HOURS=6,18）：只在时窗边界调用 cline；其余时间**纯 bash 分段睡眠（零 token）**，
#     每 SLEEP_CHUNK 秒刷新存活标记 /tmp/watch_news_loop.hb（供外部判活）—— 目的就是「**别再烧用户自己的 token**」。
#   旧模式（回退）：环境变量 `WATCH_SCHEDULE_HOURS=`（置空）⇒ 恢复 WAITING 自适应（0→60s 连续推进 / 1→1800s）。
#   时窗内致命错：**最多重试 SCHEDULE_RETRY_MAX 次**，之后等下个时窗（🚫 不做 60s 死循环重试 —— 那会疯狂烧 token）。
#
# 启动方式（脱离进程组，防工具超时误杀）:
#   cd <仓库根>/doc/personal-watch/run
#   setsid bash watch_news_loop.sh > /tmp/watch_news_loop.log 2>&1 < /dev/null &
#
# 停止方式:
#   pkill -f watch_news_loop.sh
#
# ⚠️ 本脚本以 Baize 线（`baize_harness_loop.sh`）为模板，已避开三处踩过的坑:
#   1) push 前先 fetch + pull --rebase --autostash（只 push 不 pull，远端一旦前进就永久卡死）
#   2) WAITING 正则收紧为**行首**匹配（旧版 WAITING:[* ]*1 会误匹配正文里的散文）
#   3) commit 只 add 本线自己的文件（旧版 git add -A 会把别的线在途文件一起卷进提交）
set -u

# 以脚本自身所在目录为基准，任务书 + 记忆文件均与脚本同目录（run/）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_MD="$SCRIPT_DIR/WATCH_NEWS_TASK.md"
CWD="$SCRIPT_DIR"
# git 仓库根目录
GIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/../../..")"
REL="doc/personal-watch/run"     # 本任务在仓库中的相对目录（只提交这里的文件）

# ⚠️ 模型名用 DeepSeek 官方 API 的**规范 ID**（2026-10-03 实测 `GET https://api.deepseek.com/models` → HTTP 200）：
#     `deepseek-flash`    显示名 DeepSeek-V4.1-Flash（1M ctx，text+image，reasoning）
#     `deepseek-v4-pro`   显示名 DeepSeek-V4-Pro  （1M ctx，text）
#   🚫 `deepseek-v4-pro-fp4` 本机网关不认（报 "The supported API model names are deepseek-flash, deepseek-v4-pro"）；
#   🚫 `deepseek-v4-flash` 也**不是官方 ID** —— Flash 的官方 ID 就是 `deepseek-flash`
#     （它俩在 OpenAI 兼容层会被别名成同一个，但换台机就可能像 `-fp4` 一样直接报错，别赌）。
MODEL="deepseek-flash"          # 调研+整理用 flash（便宜/快）；要更强可换 deepseek-v4-pro
# 推理强度（cline `--thinking`）：none|low|medium|high|xhigh；省略=用 provider 默认。
# ⚠️ deepseek-flash 的 provider 默认 effort 是 **high**（想得久/费 token）；
#    新闻采集主要是"搜索 + 读 + 写摘要"，不需要深推理 → ⚠️ **2026-10-11 用户令：降为 `none`**（每天 6 轮唤醒，省 token 优先；文稿质量由任务书「第 13 批」的写作要求约束）。
THINKING="none"
CLINE_TIMEOUT=1500              # 单次 cline 最多 25 分钟（与 BaiZe 一致）
PUSH_INTERVAL=1800              # 每 30 分钟兜底同步一次（2026-10-06 由 18000/5h 缩短，与 BaiZe 一致；agent 每轮自己也会提交）
SLEEP_SHORT=60                  # 【仅旧模式】WAITING=0 / 失败重试：短睡 1 分钟（= BaiZe SLEEP_BUSY）
SLEEP_LONG=1800                 # 【仅旧模式】WAITING=1（无近期待办）→ 睡 30 分钟（= BaiZe SLEEP_WAIT）
# ── ⏰ 定时唤醒时窗（2026-10-07 用户令：每天 2 次 · 06:00 / 18:00 · 本地时区）──────
SCHEDULE_HOURS="${WATCH_SCHEDULE_HOURS-07:00,09:30,12:00,15:00,18:00,21:30}"   # 逗号分隔的 **HH:MM**（也兼容纯小时）；**置空 ⇒ 回退旧模式**
SLOT_COUNT=$(printf '%s' "$SCHEDULE_HOURS" | tr ',' '\n' | grep -c '[0-9]')   # 每天唤醒次数（用于日志/判活）
# ── ⏱ 间隔唤醒模式（2026-10-11 用户令：news 改为**每 30 分钟**一轮）
#    **优先级：interval > schedule(6,18) > adaptive** —— 用 `WATCH_INTERVAL_MIN=30` 启动即生效。
INTERVAL_MIN="${WATCH_INTERVAL_MIN-}"   # >0 ⇒ 间隔模式（分钟）；空 ⇒ 走 SCHEDULE_HOURS
SLEEP_CHUNK=300                 # 时窗内分段睡：每 5 分钟刷新存活标记（零 token；可被 SIGTERM 立刻打断）
SLEEP_RETRY=300                 # 时窗内 cline 失败后的重试等待
SCHEDULE_RETRY_MAX=1            # 同一时窗内最多重试 1 次 ⇒ 之后等下个时窗（防 60s 死循环烧 token）
LOOP_HB="/tmp/watch_news_loop.hb"   # 零 token 存活标记：loop 活着、只是在等时窗（判活不必等提交）
MEMORY="$SCRIPT_DIR/MEMORY_NEWS.md"
LAST_PUSH="/tmp/watch_news_last_push"
CLINE_LOG="/tmp/watch_news_cline_last.log"   # cline 本轮输出，用于检测"报错却 exit 0"

# ── 🔒 cline 可执行解析 & PATH 兜底（2026-10-15 修复）────────────────────────────
#   故障：loop 环境 PATH 缺 cline ⇒ 第 211 行 `cline: command not found`（exit 127）
#         ⇒ 每天 6 个时窗**全部静默失败**、news 停摆 ~2 天（心跳正常，极具迷惑性）。
#   修法：① 并入【登录 shell】的 PATH —— nvm / npm-global / ~/.local/bin 常**只在 login shell 生效**；
#         ② 显式解析 cline 绝对路径 → `$CLINE_BIN`，之后调用不再依赖环境 PATH；
#         ③ 解析不到就**每轮显式报错**（🚫 不再"看着正常、其实什么都没干"）。
# ①a 内生并入 nvm 的 node bin（本机 ~/.bashrc 有「非交互即 return」守卫 ⇒ ①b 的 bash -lc 拿不到 nvm）
#     launcher 也只补这一条 —— 这里内生补上，保证「不走 launcher 直接起 loop」同样可用。
for _nb in "$HOME"/.nvm/versions/node/*/bin; do
    [ -x "$_nb/node" ] && PATH="$_nb:$PATH"
done
# ①b 并入登录 shell 的 PATH（对「无交互守卫」的机器有效）
if [ "${WATCH_NO_LOGINPATH:-0}" != "1" ]; then
    _login_path="$(bash -lc 'echo $PATH' 2>/dev/null)"
    if [ -n "$_login_path" ]; then PATH="${_login_path}:${PATH}"; fi
fi
export PATH
CLINE_BIN="${CLINE_BIN:-}"
if [ -z "$CLINE_BIN" ]; then CLINE_BIN="$(command -v cline 2>/dev/null || true)"; fi
if [ -z "$CLINE_BIN" ]; then
    echo "[loop] ❌ 找不到 cline（PATH=$PATH）→ 本线无法工作"
    # 🩹 自愈（2026-10-13 事故：`npm update -g cline` 中断把包删了 ⇒ 全线 exit 127 静默停摆 2 天）
    if [ "${WATCH_NO_CLINE_SELFHEAL:-0}" != "1" ]; then
        echo "[loop] 🩹 尝试自动重装 cline（npm i -g cline@latest，最多 240s；日志 → $CLINE_LOG）"
        (
            export NVM_DIR="$HOME/.nvm"
            [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" >/dev/null 2>&1
            timeout 240 npm i -g cline@latest --no-fund --no-audit
        ) >> "$CLINE_LOG" 2>&1 || true
        CLINE_BIN="$(command -v cline 2>/dev/null || true)"
    fi
    if [ -n "$CLINE_BIN" ]; then
        echo "[loop] 🩹 自愈成功：cline=$CLINE_BIN"
    else
        echo "[loop] 🩹 自愈失败：cline 仍不可用（详见 $CLINE_LOG）；请人工修 PATH/重装"
    fi
else
    echo "[loop] ✅ cline=$CLINE_BIN · $(timeout 15 "$CLINE_BIN" --version 2>/dev/null | head -1)"
fi

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
    git add -- "$REL/MEMORY_NEWS.md" "$REL/news" "$REL/daily-memories-news" 2>/dev/null
    if git diff --cached --quiet; then
        echo "[push] nothing of ours to commit."
    else
        if git commit -m "news auto-commit $(date '+%F %T')" >/dev/null 2>&1; then
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
FATAL_RE='(supported API model names|额度已用完|hook dispatch failed|[Uu]nauthoriz|[Aa]uthentication (failed|error)|请等待[0-9]+分钟|cline: command not found|cline: not found)'

# ── ⏰ 定时唤醒：下一个时窗的 epoch 秒（SCHEDULE_HOURS=6,18 ⇒ 06:00 / 18:00）──
next_slot_epoch() {
    local now h target best=""
    now=$(date +%s)
    local IFS=','
    for h in $SCHEDULE_HOURS; do
        h="${h//[^0-9:]/}"                      # 只留数字与冒号 ⇒ 支持 HH:MM
        [ -z "$h" ] && continue
        case "$h" in
            *:*) : ;;                                 # 已是 HH:MM，直接使用
            *)   h="$(printf '%02d:00' "$((10#$h))")" ;;   # 纯小时 → HH:00（10# 防八进制）
        esac
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
    echo "[loop] $(date '+%F %T') ⏰ 定时模式：下次唤醒 = $(date -d "@$target" '+%F %T %Z')（$((remain / 60))min 后；每天 ${SLOT_COUNT} 次 · 时窗 ${SCHEDULE_HOURS}）"
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

# ── ⏱ 睡一个间隔（分段睡；**不调用 cline ⇒ 零 token**；每段刷新存活标记）──
sleep_interval() {
    local secs remain chunk ticks=0
    secs=$(( INTERVAL_MIN * 60 ))
    [ "$secs" -le 0 ] && secs=1800
    remain="$secs"
    echo "[loop] $(date '+%F %T') ⏱ 间隔模式：每 ${INTERVAL_MIN} 分钟唤醒一次（下次 ≈ $(date -d "@$(( $(date +%s) + secs ))" '+%F %T')）"
    while [ "$remain" -gt 0 ]; do
        chunk="$SLEEP_CHUNK"
        [ "$remain" -lt "$chunk" ] && chunk="$remain"
        sleep "$chunk"
        remain=$((remain - chunk))
        date +%s > "$LOOP_HB" 2>/dev/null || true
        ticks=$((ticks + 1))
        if [ $((ticks % 6)) -eq 0 ]; then
            echo "[loop] $(date '+%F %T') 💤 间隔等待中（剩余 $((remain / 60))min；未调 cline = 零 token）"
        fi
    done
}

# ── 启动横幅：让外部一眼看出「跑的是哪种模式 / 时窗」（中继据此核验）──
if [ -n "$INTERVAL_MIN" ] && [ "$INTERVAL_MIN" -gt 0 ] 2>/dev/null; then
    MODE_LABEL="interval:${INTERVAL_MIN}min"
    echo "[loop] ⏱ 间隔模式已启用：每 ${INTERVAL_MIN} 分钟唤醒一次（interval > schedule(6,18) > adaptive）· 存活标记 = $LOOP_HB · 回退：去掉 WATCH_INTERVAL_MIN"
elif [ -n "$SCHEDULE_HOURS" ]; then
    MODE_LABEL="$SCHEDULE_HOURS"
    echo "[loop] ⏰ 定时模式已启用：唤醒时窗 = ${SCHEDULE_HOURS}（每天 ${SLOT_COUNT} 次）· 存活标记 = $LOOP_HB · 回退：WATCH_SCHEDULE_HOURS= 置空"
    if _t=$(next_slot_epoch); then
        echo "[loop] ⏰ 时窗参考：此刻之后的下一个时窗 = $(date -d "@$_t" '+%F %T %Z')（首轮唤醒=立即执行；各轮跑完会实时重算）"
    fi
else
    MODE_LABEL="adaptive"
    echo "[loop] 🔁 旧模式（WAITING 自适应）：SLEEP_SHORT=${SLEEP_SHORT}s / SLEEP_LONG=${SLEEP_LONG}s"
fi

RETRY=0     # 本时窗内的致命错重试计数（定时模式用）
while true; do
    echo "[loop] $(date '+%F %T') wake up, invoking cline ... [mode=${MODE_LABEL:-${INTERVAL_MIN:+interval:${INTERVAL_MIN}min}${INTERVAL_MIN:-${SCHEDULE_HOURS:-adaptive}}}]"
    FORCE_SHORT=0
    if [[ -f "$TASK_MD" ]]; then
        prompt="$(< "$TASK_MD")"
        "${CLINE_BIN:-cline}" -c "$CWD" --auto-approve true -m "$MODEL" -t "$CLINE_TIMEOUT" --thinking "$THINKING" "$prompt" < /dev/null 2>&1 | tee "$CLINE_LOG"
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
    if [ -n "$INTERVAL_MIN" ] && [ "$INTERVAL_MIN" -gt 0 ] 2>/dev/null; then
        # ── ⏱ 间隔模式（优先级最高）──
        sleep_interval
    elif [ -n "$SCHEDULE_HOURS" ]; then
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
