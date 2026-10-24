#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# BaiZe OPS RELAY v2 — 双机中继（每台服务器一个），支持"按机器投递"
#
# 与 v1 的差别（只此三条）：
#   ① **每台机各用一份 state**：`ops/.last_run_id.<TAG>`（TAG = hostname 末尾两位，29 / 12）
#      → 两台机不再共用同一个 RUN_ID 游标，也就不会互相"吃掉"对方的任务（v1 的竞态根源）
#   ② inbox 的 RUN_ID 注释可写投递目标：
#        <!-- RUN_ID: 163 | TARGET: 12 -->   → 只在 .12 执行
#        <!-- RUN_ID: 164 | TARGET: 29 -->   → 只在 .29 执行
#        <!-- RUN_ID: 165 -->                → 缺省 = both，两台机各执行一次
#   ③ 日志/启动横幅带 TAG，便于分辨是哪台机干的
#
# 启动：setsid bash <repo>/doc/BaiZe-ISEDA2027/run/ops_relay_v2.sh \
#         > /tmp/baize_ops_relay.<TAG>.log 2>&1 < /dev/null &
# 停止：pkill -f ops_relay_v2.sh
# ═══════════════════════════════════════════════════════════════════════════
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo '/nas_train/app.e0031982/code/super_intelligence_2035')"
REL="doc/BaiZe-ISEDA2027/run"
OPS="$SCRIPT_DIR/ops"
INBOX="$OPS/inbox.md"
OUTBOX="$OPS/outbox.md"

HOSTTAG="${HOSTTAG:-$(hostname | sed -n 's/.*\([0-9][0-9]\)$/\1/p')}"
[ -n "$HOSTTAG" ] || HOSTTAG="$(hostname)"
STATE="$OPS/.last_run_id.$HOSTTAG"

POLL=20                # 本地轮询间隔（秒）
FETCH_EVERY=3          # 每 N 次轮询做一次 git fetch（≈ 60s）
CMD_TIMEOUT=600        # 单次命令块总超时（秒）
MAX_OUT_CHARS=20000    # 单次输出截断上限（字符）

mkdir -p "$OPS"

# ── 从 inbox.md 提取 RUN_ID / TARGET / 命令块 ─────────────────────────────
inbox_run_id() {
    [ -f "$INBOX" ] || { echo 0; return; }
    sed -n 's/.*RUN_ID:[[:space:]]*\([0-9]\+\).*/\1/p' "$INBOX" | head -1
}
inbox_target() {
    [ -f "$INBOX" ] || return 0
    sed -n 's/.*TARGET:[[:space:]]*\([A-Za-z0-9_]*\).*/\1/p' "$INBOX" | head -1
}
inbox_cmd_block() {
    [ -f "$INBOX" ] || return 0
    awk '/^```bash/{f=1;next} /^```/{if(f){exit}} f' "$INBOX"
}
last_run_id() {
    [ -f "$STATE" ] && cat "$STATE" 2>/dev/null || echo 0
}

# ── 危险模式拦截（防手滑，不是安全边界）──────────────────────────────────
guard_block() {
    local block="$1" pat
    local -a bad=(
        'rm[[:space:]]+-[^[:space:]]*[[:space:]]+/($|[[:space:]])'
        'rm[[:space:]]+-[^[:space:]]*[[:space:]]+/\*'
        'mkfs'
        'dd[[:space:]]+.*of=/dev/'
        '>[[:space:]]*/dev/sd'
        ':\(\)[[:space:]]*\{'
        '>[[:space:]]*/dev/nvme'
    )
    for pat in "${bad[@]}"; do
        if printf '%s' "$block" | grep -qE -- "$pat"; then
            echo "REFUSED: 命中危险模式 [${pat}]（如需强行执行，请人工在服务器上操作）"
            return 1
        fi
    done
    return 0
}

# ── git 同步（共享工作副本：只 add 本通道自己的文件）─────────────────────
git_sync() {
    local counts behind
    cd "$GIT_ROOT" || return 0
    timeout 60 git fetch origin >/dev/null 2>&1 || return 0
    counts="$(git rev-list --left-right --count origin/main...HEAD 2>/dev/null || echo '0 0')"
    behind="$(echo "$counts" | awk '{print $1}')"
    if [ "${behind:-0}" -gt 0 ]; then
        git pull --rebase --autostash origin main >/dev/null 2>&1 || { git rebase --abort >/dev/null 2>&1; return 0; }
    fi
}
git_publish() {
    cd "$GIT_ROOT" || return 0
    git add -- "$REL/ops/outbox.md" "$REL/ops/inbox.md" "$STATE" 2>/dev/null
    if git diff --cached --quiet; then
        return 0
    fi
    git commit -m "ops-relay[$HOSTTAG]: result @ $(date '+%F %T')" >/dev/null 2>&1 || return 0
    for i in 1 2 3; do
        git push origin main >/dev/null 2>&1 && return 0
        sleep 3
        git fetch origin >/dev/null 2>&1
        git pull --rebase --autostash origin main >/dev/null 2>&1 || git rebase --abort >/dev/null 2>&1
    done
    echo "[relay-$HOSTTAG] push FAILED (will retry next cycle)"
}

# ── 执行一次命令块 ────────────────────────────────────────────────────────
run_once() {
    local rid="$1"
    local block; block="$(inbox_cmd_block)"
    [ -n "$block" ] || { echo "[relay-$HOSTTAG] RUN_ID=$rid 但命令块为空，跳过"; return; }

    local ts host out rc guard
    ts="$(date '+%F %T')"
    host="$(hostname 2>/dev/null || echo '?')"

    if guard="$(guard_block "$block")"; then
        local tmp; tmp="$(mktemp)"
        printf '%s\n' "$block" > "$tmp"
        out="$(cd "$GIT_ROOT" && timeout "$CMD_TIMEOUT" bash -c "set -o pipefail; bash '$tmp'" 2>&1)"
        rc=$?
        rm -f "$tmp"
        if [ "$rc" -eq 124 ]; then
            out="${out}
[relay] ⚠️ 命令块超时（>${CMD_TIMEOUT}s），已被 timeout 终止"
        fi
    else
        out="$guard"
        rc=126
    fi

    if [ "${#out}" -gt "$MAX_OUT_CHARS" ]; then
        out="$(printf '%s' "$out" | head -c "$MAX_OUT_CHARS")
[relay] ⚠️ 输出超长，已截断到 ${MAX_OUT_CHARS} 字符"
    fi

    { echo ""
      echo "---"
      echo ""
      echo "## RUN_ID $rid · $ts · host=\`$host\` · exit=$rc"
      echo ""
      echo "**命令**"
      echo '```bash'
      printf '%s\n' "$block"
      echo '```'
      echo ""
      echo "**输出**"
      echo '```'
      printf '%s\n' "$out"
      echo '```'
    } >> "$OUTBOX"

    echo "$rid" > "$STATE"
    echo "[relay-$HOSTTAG] RUN_ID=$rid executed, exit=$rc, appended to outbox."
    git_publish
}

# ── 主循环 ────────────────────────────────────────────────────────────────
echo "[relay-$HOSTTAG] $(date '+%F %T') v2 started. repo=$GIT_ROOT tag=$HOSTTAG state=$STATE poll=${POLL}s"
i=0
while true; do
    i=$((i + 1))
    if [ $((i % FETCH_EVERY)) -eq 1 ]; then
        git_sync
    fi
    rid="$(inbox_run_id)"
    tgt="$(inbox_target)"; tgt="${tgt:-both}"
    if [ "$tgt" != "both" ] && [ "$tgt" != "$HOSTTAG" ]; then
        : # 不是投给本机的，保持自己的游标不动
    elif [ "${rid:-0}" -gt "$(last_run_id)" ]; then
        run_once "$rid"
    fi
    sleep "$POLL"
done
