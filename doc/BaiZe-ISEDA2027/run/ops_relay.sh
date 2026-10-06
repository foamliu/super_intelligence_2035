#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# BaiZe OPS RELAY — 纯 bash 的"经 git 中继的命令执行通道"（不含 LLM）
#
# 为什么需要它：Windows 侧运维无法 SSH 到 GPU 服务器（10.239.2.29 / .12），
#   只能用 git 与服务器交互。本脚本提供一条**高频、零 token**的通道：
#
#     运维 → 编辑 run/ops/inbox.md（写命令 + RUN_ID+1）→ git push
#     中继 → 轮询拉取 → 发现 RUN_ID 增加 → 执行 → 结果写 run/ops/outbox.md → push
#     运维 → git pull → 读 outbox.md
#
# ⚠️ 安全提示（务必知悉）：这本质上是一条**远程代码执行通道**。
#   - **仓库必须保持 private**；只有能 push 的人才能下发命令
#   - 每一条被执行的命令都会**原文记入 outbox.md**（审计留痕）
#   - 仅做"防手滑"级别的危险模式拦截，**不是安全边界**
#
# 启动：
#   setsid bash <repo>/doc/BaiZe-ISEDA2027/run/ops_relay.sh \
#     > /tmp/baize_ops_relay.log 2>&1 < /dev/null &
# 停止：
#   pkill -f ops_relay.sh
# ═══════════════════════════════════════════════════════════════════════════
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo '/nas_train/app.e0031982/code/super_intelligence_2035')"
REL="doc/BaiZe-ISEDA2027/run"
OPS="$SCRIPT_DIR/ops"
INBOX="$OPS/inbox.md"
OUTBOX="$OPS/outbox.md"
STATE="$OPS/.last_run_id"

POLL=20                # 本地轮询间隔（秒）
FETCH_EVERY=3          # 每 N 次轮询做一次 git fetch（=> 默认 ~60s 拉一次远端）
CMD_TIMEOUT=600        # 单次命令块总超时（秒）
MAX_OUT_CHARS=20000    # 单次输出截断上限（字符）

mkdir -p "$OPS"

# ── 从 inbox.md 提取 RUN_ID 与命令块 ──────────────────────────────────────
inbox_run_id() {
    [ -f "$INBOX" ] || { echo 0; return; }
    sed -n 's/.*RUN_ID:[[:space:]]*\([0-9]\+\).*/\1/p' "$INBOX" | head -1
}
inbox_cmd_block() {
    [ -f "$INBOX" ] || return 0
    awk '/^```bash/{f=1;next} /^```/{if(f){exit}} f' "$INBOX"
}
last_run_id() {
    [ -f "$STATE" ] && cat "$STATE" 2>/dev/null || echo 0
}

# ── 危险模式拦截（防手滑，不是安全边界）──────────────────────────────────
# 注意：必须**锚定到根目录**，否则 `rm -rf /tmp/x` 会被 `rm -rf /` 前缀误伤。
guard_block() {
    local block="$1" pat
    local -a bad=(
        'rm[[:space:]]+-[^[:space:]]*[[:space:]]+/($|[[:space:]])'   # rm ... /      （删根）
        'rm[[:space:]]+-[^[:space:]]*[[:space:]]+/\*'               # rm ... /*     （删根下全部）
        'mkfs'                                                      # 格式化
        'dd[[:space:]]+.*of=/dev/'                                   # 直接写块设备
        '>[[:space:]]*/dev/sd'                                       # 重定向到磁盘
        ':\(\)[[:space:]]*\{'                                        # fork bomb
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
    git add -- "$REL/ops/outbox.md" "$REL/ops/inbox.md" "$REL/ops/.last_run_id" 2>/dev/null
    if git diff --cached --quiet; then
        return 0
    fi
    git commit -m "ops-relay: result @ $(date '+%F %T')" >/dev/null 2>&1 || return 0
    git push origin main >/dev/null 2>&1 || echo "[relay] push FAILED (will retry next cycle)"
}

# ── 执行一次命令块 ────────────────────────────────────────────────────────
run_once() {
    local rid="$1"
    local block; block="$(inbox_cmd_block)"
    [ -n "$block" ] || { echo "[relay] RUN_ID=$rid 但命令块为空，跳过"; return; }

    local ts host out rc guard
    ts="$(date '+%F %T')"
    host="$(hostname 2>/dev/null || echo '?')"

    if guard="$(guard_block "$block")"; then
        local tmp; tmp="$(mktemp)"
        printf '%s\n' "$block" > "$tmp"
        # 显式启用 pipefail，让管道中间的错误也能被 exit code 反映
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
    echo "[relay] RUN_ID=$rid executed, exit=$rc, appended to outbox."
    git_publish
}

# ── 主循环 ────────────────────────────────────────────────────────────────
echo "[relay] $(date '+%F %T') started. repo=$GIT_ROOT  poll=${POLL}s  fetch_every=${FETCH_EVERY}x"
i=0
while true; do
    i=$((i + 1))
    if [ $((i % FETCH_EVERY)) -eq 1 ]; then
        git_sync
    fi
    rid="$(inbox_run_id)"
    if [ "${rid:-0}" -gt "$(last_run_id)" ]; then
        run_once "$rid"
    fi
    sleep "$POLL"
done
