#!/bin/bash
# Design-Flow Benchmark 构建自动推进循环（opencode 版 · 双仓库迁移版）
#
# workspace 已从 EDA-Flow-Bench/agent_workspace 迁移到
#   super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/
# workspace 文件（TASK/MEMORY/EXPERIMENTS/ARCHIVE/designflow/pi_debug/loop脚本）入
#   super_intelligence_2035 git（main 分支）。
# agent 写的用例产物（benchmarks/EDA-Eval-DesignFlow + docs/reports）仍入
#   EDA-Flow-Bench git（master 分支）—— agent 的 cwd = EDA-Flow-Bench，跨目录提交用例。
#
# 唤醒间隔自适应：读 MEMORY_DESIGNFLOW.md 的 WAITING 标志——
#   无阻塞(0)约 1 分钟续跑，有异步阻塞(1)约 30 分钟轮询省 token。
#
# 启动方式（脱离进程组，防工具超时误杀）:
#   setsid bash /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow_bench_loop.sh \
#     > /tmp/designflow_bench_loop.log 2>&1 < /dev/null &
#
# 停止:
#   pkill -f designflow_bench_loop.sh
#
# ⚠️ 已避开 pretrain/vision/cline 版踩过的坑:
#   1) push 前先 fetch + pull --rebase（旧版只 push 不 pull：远端一旦前进就永久卡死）
#   2) WAITING 正则收紧为**行首**匹配（旧版会误匹配正文里的散文）
#   3) commit 只 add 本任务自己的文件（旧版 git add -A 会把别的任务在途文件一起卷进提交）
#   4) 编排 harness 用 opencode（config 在 ~/.config/opencode/），与被采样对象 cline 完全隔离。
#   5) 双仓库 sync：workspace → super_intelligence_2035(main)；用例 → EDA-Flow-Bench(master)。
#   6) 一轮只做 1 条 case（控制上下文不膨胀）；交付后 WAITING:0，sleep 60s 立即开下一条。
set -u

# ── 路径 ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_MD="$SCRIPT_DIR/BAIZE_DESIGNFLOW_BENCH_TASK.md"
MEMORY="$SCRIPT_DIR/MEMORY_DESIGNFLOW.md"
LAST_PUSH_WS="/tmp/designflow_bench_last_push_ws"      # workspace 仓库（super_intelligence_2035）
LAST_PUSH_BENCH="/tmp/designflow_bench_last_push_bench" # 用例仓库（EDA-Flow-Bench）

# 仓库根
WS_REPO_ROOT="/nasdata/app.e0031982/code/super_intelligence_2035"   # workspace 入此 repo（main）
BENCH_REPO_ROOT="/nasdata/app.e0031982/code/EDA-Flow-Bench"          # 用例入此 repo（master）
CWD="$BENCH_REPO_ROOT"   # agent 运行时 cwd：在 EDA-Flow-Bench 下，方便读写 benchmarks/ + docs/reports/

# workspace 在 super_intelligence_2035 repo 内的相对路径前缀
WS_REL="doc/ZhuLong_DAC2027/benchmark"

# 编排 agent 的模型（opencode 的 provider/model 格式）
OPENCODE_MODEL="glm/glm-5.2"

# ── 时间参数 ──
AGENT_TIMEOUT=2700        # 单次编排 opencode 最多 45 分钟
PUSH_INTERVAL=1800        # 每 30 分钟兜底同步一次
SLEEP_BUSY=60             # WAITING=0：1 分钟后续跑下一条 case
SLEEP_WAIT=120            # WAITING=1（真外部阻塞：pi 异步/推送挂）：最多等 2 分钟，不再长睡

# ── 通用 git sync（单仓库）──
# 用法: git_sync_one REPO_ROOT BRANCH REL_PATHS... LAST_PUSH_FILE COMMIT_TAG
git_sync_one() {
    local repo_root="$1"; shift
    local branch="$1"; shift
    local last_push_file="$1"; shift
    local commit_tag="$1"; shift
    local now last
    now=$(date +%s); last=0
    [ -f "$last_push_file" ] && last="$(cat "$last_push_file" 2>/dev/null)"
    if [ $((now - last)) -lt "$PUSH_INTERVAL" ]; then return; fi
    echo "[push:$commit_tag] $(date '+%F %T') push interval reached, syncing ..."

    cd "$repo_root" || { echo "[push:$commit_tag] cd repo FAILED"; return; }

    # 1) fetch + rebase
    if ! timeout 120 git fetch origin >/dev/null 2>&1; then
        echo "[push:$commit_tag] fetch FAILED (network?) - skip."; return
    fi
    local counts behind
    counts="$(git rev-list --left-right --count origin/${branch}...HEAD 2>/dev/null || echo '0 0')"
    behind="$(echo "$counts" | awk '{print $1}')"
    if [ "${behind:-0}" -gt 0 ]; then
        if git pull --rebase --autostash origin "$branch" >/dev/null 2>&1; then
            echo "[push:$commit_tag] pull --rebase OK."
        else
            echo "[push:$commit_tag] pull --rebase FAILED - aborting, skip."
            git rebase --abort >/dev/null 2>&1 || true; return
        fi
    fi

    # 2) 只 add 本线文件（逐项判存在，避免 pathspec 不匹配整体失败）
    local f
    for f in "$@"; do
        [ -e "$repo_root/$f" ] && git add -- "$f"
    done
    if git diff --cached --quiet; then
        echo "[push:$commit_tag] nothing of ours to commit."
    else
        git commit -m "designflow $commit_tag $(date '+%F %T')" >/dev/null 2>&1 \
            && echo "[push:$commit_tag] committed."
    fi

    # 3) push
    if git push origin "$branch" 2>&1; then
        echo "[push:$commit_tag] push OK."
    else
        echo "[push:$commit_tag] push FAILED (will retry next cycle)."
    fi
    date +%s > "$last_push_file"
}

# ── 双仓库兜底 git 同步 ──
git_push_if_needed() {
    # (A) workspace 仓库：super_intelligence_2035 (main) — 含 workspace + 日报
    git_sync_one "$WS_REPO_ROOT" main "$LAST_PUSH_WS" "ws" \
        "$WS_REL/BAIZE_DESIGNFLOW_BENCH_TASK.md" \
        "$WS_REL/MEMORY_DESIGNFLOW.md" \
        "$WS_REL/EXPERIMENTS_DESIGNFLOW.md" \
        "$WS_REL/ARCHIVE_OPERATOR_DESIGNFLOW.md" \
        "$WS_REL/designflow" \
        "$WS_REL/daily-memories-designflow" \
        "doc/ZhuLong_DAC2027/reports"

    # (B) 用例仓库：EDA-Flow-Bench (master) — 仅用例产物
    git_sync_one "$BENCH_REPO_ROOT" master "$LAST_PUSH_BENCH" "bench" \
        benchmarks/EDA-Eval-DesignFlow
}

# WAITING 判定：只认**行首**的 WAITING 字段；文件不存在时按"等待"处理（省 token）
waiting_is_1() {
    [ -f "$MEMORY" ] || return 0
    grep -qE '^WAITING:[[:space:]]*1' "$MEMORY" 2>/dev/null
}

# ── 主循环 ──
while true; do
    echo "[loop] $(date '+%F %T') wake up, invoking opencode ..."
    if [[ -f "$TASK_MD" ]]; then
        budget_min=$(( AGENT_TIMEOUT / 60 - 5 ))
        prompt="$(< "$TASK_MD")"
        prompt="${prompt}

---

## 本轮任务卡（loop 自动生成 · $(date '+%F %T')）
- **本轮只做 1 条 case**：选料 → 深读 → 合成 → 自验 → 写入 jsonl → 日报一行；做完即收尾，**不要在本轮开第二条**（控制上下文不膨胀）。
- 硬预算：${budget_min} 分钟（进程 ${AGENT_TIMEOUT}s 后被 timeout 终止）。
- 交付定义（DoD，§3）：该 case 通过 ref 自验 + §4.9 三种假提交 FAIL，并已进 `EDA-Eval-DesignFlow.jsonl`。
- **交付后必须把 MEMORY 首行写成 `WAITING: 0`**（loop 60s 后立刻唤醒做下一条）；`WAITING: 1` 仅用于真外部阻塞（pi 异步未回 / 推送失败 / 等人工）。"
        # 🚫 剥代理环境变量：内网网关 agi-gateway.cxmt.com 不该走外网代理。
        #    ⚠️ 只作用于本行 opencode；loop 自身 git push 到内网 devops.cxmt.com 不需要代理。
        cd "$CWD" && env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \
            -u all_proxy -u ALL_PROXY -u ftp_proxy -u FTP_PROXY \
            -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE \
          timeout -k 15 "$AGENT_TIMEOUT" opencode run --auto -m "$OPENCODE_MODEL" "$prompt" < /dev/null
        echo "[loop] $(date '+%F %T') opencode returned (exit $?), checking git push ..."
    else
        echo "[loop] $(date '+%F %T') TASK_MD missing at $TASK_MD"
    fi

    git_push_if_needed

    # 自适应睡眠：只认行首的 WAITING 字段
    if waiting_is_1; then
        echo "[loop] $(date '+%F %T') WAITING=1（异步任务 running）→ sleep ${SLEEP_WAIT}s"
        sleep "$SLEEP_WAIT"
    else
        echo "[loop] $(date '+%F %T') WAITING=0（无阻塞）→ sleep ${SLEEP_BUSY}s"
        sleep "$SLEEP_BUSY"
    fi
done
