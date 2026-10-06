#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# personal-watch OPS RELAY — 纯 bash 的「经 git 中继的命令执行通道」（**不含 LLM / 零 token**）
#
# 为什么需要它：
#   supervisor（Windows 侧）**无法 SSH** 到观察哨机器，只能用 git 交互。
#   而且 **worker loop 一旦停了 / 撞额度 / OOM，git 上就"什么都看不到"** ——
#   本中继**不依赖 cline、不依赖额度**，loop 停着也能执行诊断与运维命令。
#
#     运维 → 编辑 run/ops/inbox.md（新增一段 `## RUN_ID N` + 一个 ```bash 块）→ git push
#     中继 → 轮询 fetch → 发现 RUN_ID 变大 → 执行 → 结果 append 到 run/ops/outbox.md → push
#     运维 → git pull → 读 outbox.md
#
# ⚠️ 安全提示（务必知悉）：这是**远程代码执行通道**。
#   - **仓库必须保持 private**；只有能 push 的人才能下发命令
#   - 每条被执行的命令都会**原文记入 outbox.md**（审计留痕）
#   - 危险模式拦截只是「防手滑」，**不是安全边界**
#   - ⚠️ 与 `doc/keys.txt` 入仓（见 DEPLOY_CHECKLIST.md §6）叠加时风险放大 → 请轮换 Key
#
# 启动（⭐ 用 exec -a 起，让进程名**唯一**为 watch_ops_relay.sh —— 这样 pkill -f 又准、又不会误伤同名 cmdline）：
#   cd <repo>/doc/personal-watch/run
#   setsid bash -c 'exec -a watch_ops_relay.sh bash ops_relay.sh' > /tmp/watch_ops_relay.log 2>&1 < /dev/null &
# 停止（两种都可；PID 法最稳）：
#   pkill -f watch_ops_relay.sh
#   kill "$(cat /tmp/watch_ops_relay.pid)"
# ⚠️ 别用 pkill -f ops_relay.sh（BaiZe 的中继 cmdline 也叫它 → 会误伤）
# ⚠️ 单实例保护：脚本用 /tmp/watch_ops_relay.pid 防重复启动（发现已在跑就自动退出）
# ═══════════════════════════════════════════════════════════════════════════
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo "$SCRIPT_DIR/../../..")"
REL="doc/personal-watch/run"
OPS="$SCRIPT_DIR/ops"
INBOX="$OPS/inbox.md"
OUTBOX="$OPS/outbox.md"
STATE="$OPS/.last_run_id"
PIDFILE="/tmp/watch_ops_relay.pid"     # ⭐ 单实例锁：防「两个中继并存 → 同一 RUN_ID 被跑两遍」

POLL=20                # 本地轮询间隔（秒）
FETCH_EVERY=3          # 每 N 次轮询做一次 git fetch（=> 默认 ~60s 拉一次远端）
CMD_TIMEOUT=600        # 单次命令块总超时（秒）
MAX_OUT_CHARS=20000    # 单次输出截断上限（字符）

mkdir -p "$OPS"

# ── ⭐ 单实例保护（修「两个中继并存 → 同一 RUN_ID 被执行两遍 + 提交两遍」）──
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; then
    echo "[relay] ⚠️ 检测到已在运行（pid=$(cat "$PIDFILE" 2>/dev/null)）→ 本实例退出，避免双实例重复执行。"
    echo "[relay]    如需强制重启：kill \"\$(cat $PIDFILE)\"，然后再启动。"
    exit 0
fi
echo $$ > "$PIDFILE"
trap 'rm -f "$PIDFILE"' EXIT INT TERM

# ── 从 inbox.md 提取 RUN_ID 与命令块 ──────────────────────────────────────
# ✅ **已修 BaiZe 的已知坑**：不再"只取第一个 ```bash 块"（那会让新命令静默失效）。
# ✅ **已修本版自身的坑**：不再"只执行 RUN_ID 最大那一段"（那会**静默跳过中间块** —— RUN_ID 4 就是这样丢的）。
#    现在支持**多段 `## RUN_ID N` 历史共存**，并把 `> last_run_id` 的块**按升序全部执行**。
inbox_run_id() {
    [ -f "$INBOX" ] || { echo 0; return; }
    { sed -n 's/^##[[:space:]]*RUN_ID[[:space:]]*\([0-9]\+\).*/\1/p' "$INBOX"
      sed -n 's/.*RUN_ID:[[:space:]]*\([0-9]\+\).*/\1/p'            "$INBOX"; } | sort -n | tail -1
}
# ⭐ 列出 inbox 里**所有** RUN_ID（升序去重）
inbox_run_ids() {
    [ -f "$INBOX" ] || return 0
    { sed -n 's/^##[[:space:]]*RUN_ID[[:space:]]*\([0-9]\+\).*/\1/p' "$INBOX"
      sed -n 's/.*RUN_ID:[[:space:]]*\([0-9]\+\).*/\1/p'            "$INBOX"; } | sort -n -u
}
# ⭐ 取**指定** RUN_ID 的 ```bash 块
inbox_cmd_block_for() {
    local want="$1"
    [ -f "$INBOX" ] || return 0
    awk -v want="$want" '
        /^##[[:space:]]*RUN_ID[[:space:]]*[0-9]+/ { rid=$3+0; next }
        /^```bash/ { inblk=1; blk=""; next }
        /^```/     { if (inblk) { blocks[rid]=blk; inblk=0 } next }
        inblk      { blk = blk $0 "\n" }
        END { if (want in blocks) printf "%s", blocks[want] }
    ' "$INBOX"
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
        'mkfs'                                                       # 格式化
        'dd[[:space:]]+.*of=/dev/'                                   # 直接写块设备
        '>[[:space:]]*/dev/(sd|nvme|vd)'                             # 重定向到磁盘
        ':\\(\\)[[:space:]]*\\{'                                     # fork bomb
        # ── 以下为本线新增（针对共享工作副本 + 中继自身）──
        'git[[:space:]]+clean[[:space:]]+.*-[a-zA-Z]*[fx]'           # 🚫 git clean -fdx（会删掉别线在途文件！）
        'git[[:space:]]+reset[[:space:]]+--hard'                     # 🚫 硬回滚（同上）
        'pkill[[:space:]].*ops_relay'                                # 🚫 别断自己的信道
        'kill[[:space:]].*ops_relay'
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
    # ⚠️ 先同步再提交/推送：本仓库与 4 条 BaiZe 线**共享同一个远端**，不先 rebase 必被拒（BaiZe 提交极频繁）
    if ! timeout 120 git fetch origin >/dev/null 2>&1; then
        echo "[relay] ⚠️ fetch FAILED（网络？）→ 本轮不发布，下轮重试"
        return 0
    fi
    local counts behind
    counts="$(git rev-list --left-right --count origin/main...HEAD 2>/dev/null || echo '0 0')"
    behind="$(echo "$counts" | awk '{print $1}')"
    if [ "${behind:-0}" -gt 0 ]; then
        if git pull --rebase --autostash origin main >/dev/null 2>&1; then
            echo "[relay] pull --rebase OK (behind=${behind})"
        else
            git rebase --abort >/dev/null 2>&1 || true
            echo "[relay] ⚠️ pull --rebase FAILED（冲突？）→ 本轮不发布，下轮重试"
            return 0
        fi
    fi
    if ! git add -- "$REL/ops/outbox.md" "$REL/ops/inbox.md" "$REL/ops/.last_run_id" 2>/tmp/_watch_relay_git.err; then
        echo "[relay] ⚠️ git add FAILED: $(tail -2 /tmp/_watch_relay_git.err 2>/dev/null | tr '\n' ' ')"
        return 0
    fi
    if git diff --cached --quiet; then
        echo "[relay] nothing to commit."
        return 0
    fi
    if ! git commit -m "watch-ops-relay: result @ $(date '+%F %T')" 2>/tmp/_watch_relay_git.err; then
        echo "[relay] ⚠️ git commit FAILED（常见原因：缺 user.email/user.name，或 index.lock 被占）: $(tail -2 /tmp/_watch_relay_git.err 2>/dev/null | tr '\n' ' ')"
        return 0
    fi
    if git push origin main 2>/tmp/_watch_relay_git.err; then
        echo "[relay] ✅ committed + pushed."
    else
        echo "[relay] ⚠️ git push FAILED: $(tail -2 /tmp/_watch_relay_git.err 2>/dev/null | tr '\n' ' ')（下轮重试）"
        return 0
    fi
}

# ── 执行一次命令块 ────────────────────────────────────────────────────────
run_once() {
    local rid="$1"
    local block; block="$(inbox_cmd_block_for "$rid")"
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
echo "[relay] $(date '+%F %T') started. pid=$$ repo=$GIT_ROOT  poll=${POLL}s  fetch_every=${FETCH_EVERY}x  pidfile=$PIDFILE"
i=0
while true; do
    i=$((i + 1))
    if [ $((i % FETCH_EVERY)) -eq 1 ]; then
        git_sync
    fi
    # ⭐ 把**所有** `> last_run_id` 的块按升序依次执行（修掉"只跑最大 → 静默跳过中间块"的坑）
    last="$(last_run_id)"
    for rid in $(inbox_run_ids); do
        if [ "${rid:-0}" -gt "${last:-0}" ]; then
            run_once "$rid"
            last="$rid"
        fi
    done
    sleep "$POLL"
done
