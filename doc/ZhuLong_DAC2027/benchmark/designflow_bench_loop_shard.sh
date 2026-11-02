#!/bin/bash
# Design-Flow Benchmark shard loop（4 片并发版）
#
# 用法：SHARD=A setsid bash designflow_bench_loop_shard.sh > /tmp/designflow_bench_loop_A.log 2>&1 < /dev/null &
#       SHARD=B setsid bash designflow_bench_loop_shard.sh > /tmp/designflow_bench_loop_B.log 2>&1 < /dev/null &
#       ...
#
# 停止某个 shard：pkill -f "designflow_bench_loop_shard.sh.*SHARD=$SHARD"
# 停止全部：pkill -f designflow_bench_loop_shard.sh
set -u

SHARD="${SHARD:-A}"
SHARD_NAME="$SHARD"

# ── 路径 ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BENCH_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TASK_MD="$BENCH_DIR/BAIZE_DESIGNFLOW_BENCH_TASK_${SHARD}.md"
MEMORY="$BENCH_DIR/MEMORY_DESIGNFLOW_${SHARD}.md"
LAST_PUSH_WS="/tmp/designflow_bench_shard_${SHARD}_last_push_ws"
LAST_PUSH_BENCH="/tmp/designflow_bench_shard_${SHARD}_last_push_bench"
LAST_MERGE="/tmp/designflow_bench_shard_${SHARD}_last_merge"

# 仓库根
WS_REPO_ROOT="/nasdata/app.e0031982/code/super_intelligence_2035"
BENCH_REPO_ROOT="/nasdata/app.e0031982/code/EDA-Flow-Bench"
CWD="$BENCH_REPO_ROOT"
WS_REL="doc/ZhuLong_DAC2027/benchmark"
DESIGNFLOW_REL="${WS_REL}/designflow"

# 编排 agent
OPENCODE_MODEL="glm/glm-5.2"

# ── 时间参数 ──
AGENT_TIMEOUT=2700
PUSH_INTERVAL=1800
MERGE_INTERVAL=600       # 每 10 分钟 merge 一次（比 push 更频繁，保证主 jsonl 及时更新）
SLEEP_BUSY=60
SLEEP_WAIT=120

# ── git sync（单仓库，只提交本 shard 文件）──
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
    if ! timeout 120 git fetch origin >/dev/null 2>&1; then
        echo "[push:$commit_tag] fetch FAILED - skip."; return
    fi
    local counts behind
    counts="$(git rev-list --left-right --count origin/${branch}...HEAD 2>/dev/null || echo '0 0')"
    behind="$(echo "$counts" | awk '{print $1}')"
    if [ "${behind:-0}" -gt 0 ]; then
        if git pull --rebase --autostash origin "$branch" >/dev/null 2>&1; then
            echo "[push:$commit_tag] pull --rebase OK."
        else
            echo "[push:$commit_tag] pull --rebase FAILED - skip."
            git rebase --abort >/dev/null 2>&1 || true; return
        fi
    fi
    local f
    for f in "$@"; do
        [ -e "$repo_root/$f" ] && git add -- "$f"
    done
    if git diff --cached --quiet; then
        echo "[push:$commit_tag] nothing to commit."
    else
        git commit -m "designflow shard ${SHARD} $commit_tag $(date '+%F %T')" >/dev/null 2>&1 \
            && echo "[push:$commit_tag] committed."
    fi
    git push origin "$branch" 2>&1 && echo "[push:$commit_tag] push OK." || echo "[push:$commit_tag] push FAILED."
    date +%s > "$last_push_file"
}

git_push_if_needed() {
    # (A) workspace：只提交本 shard 的 MEMORY + ledger + deepreads + daily
    git_sync_one "$WS_REPO_ROOT" main "$LAST_PUSH_WS" "ws-shard${SHARD}" \
        "$WS_REL/MEMORY_DESIGNFLOW_${SHARD}.md" \
        "$WS_REL/designflow/trace_ledger_${SHARD}.tsv" \
        "$WS_REL/designflow/trace_deepreads" \
        "$WS_REL/daily-memories-designflow" \
        "doc/ZhuLong_DAC2027/reports"

    # (B) 用例：只提交本 shard 的 jsonl + assets/reference（flock 防多 shard 同时 push 冲突）
    (
        flock -x 200
        git_sync_one "$BENCH_REPO_ROOT" master "$LAST_PUSH_BENCH" "bench-shard${SHARD}" \
            "benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_${SHARD}.jsonl" \
            "benchmarks/EDA-Eval-DesignFlow/assets" \
            "benchmarks/EDA-Eval-DesignFlow/reference" \
            "benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl"
    ) 200>/tmp/designflow_bench_git.lock
}

# ── merge：合并 4 片 shard jsonl → 主 jsonl + regen 日报 ──
merge_if_needed() {
    local now last
    now=$(date +%s); last=0
    [ -f "$LAST_MERGE" ] && last="$(cat "$LAST_MERGE" 2>/dev/null)"
    if [ $((now - last)) -lt "$MERGE_INTERVAL" ]; then return; fi
    echo "[merge] $(date '+%F %T') merging 4 shards → main jsonl ..."
    (
        flock -x 200
        cd "$BENCH_DIR" && python3 designflow/merge_shards.py 2>&1 | tail -5
    ) 200>/tmp/designflow_bench_merge.lock
    date +%s > "$LAST_MERGE"
}

# WAITING 判定
waiting_is_1() {
    [ -f "$MEMORY" ] || return 0
    grep -qE '^WAITING:[[:space:]]*1' "$MEMORY" 2>/dev/null
}

# ── 主循环 ──
echo "[loop-shard-${SHARD}] $(date '+%F %T') START (TASK=$TASK_MD, MEMORY=$MEMORY)"
while true; do
    echo "[loop-shard-${SHARD}] $(date '+%F %T') wake up, invoking opencode ..."
    if [[ -f "$TASK_MD" ]]; then
        budget_min=$(( AGENT_TIMEOUT / 60 - 5 ))
        card="$(cat <<CARD

---

## 本轮任务卡（loop shard ${SHARD} 自动生成 · __TS__）
- **你是 shard ${SHARD}**，只做 domain 属于本 shard 的 case。
- **本轮只做 1 条 case**：trace_ledger.py --shard ${SHARD} next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_${SHARD}.jsonl → 日报一行。
- 🚫 不要碰主 jsonl（EDA-Eval-DesignFlow.jsonl），它由 merge 脚本自动合并。
- 🚫 不要碰别的 shard 的文件（MEMORY_DESIGNFLOW_{其他}.md、trace_ledger_{其他}.tsv、EDA-Eval-DesignFlow_{其他}.jsonl）。
- 硬预算：__BUDGET__ 分钟（进程 __TIMEOUT__s 后被 timeout 终止）。
- 交付后必须把 MEMORY_DESIGNFLOW_${SHARD}.md 首行写成 WAITING: 0。
CARD
)"
        card="${card//__TS__/$(date '+%F %T')}"
        card="${card//__BUDGET__/$budget_min}"
        card="${card//__TIMEOUT__/$AGENT_TIMEOUT}"
        prompt="$(< "$TASK_MD")${card}"
        cd "$CWD" && env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \
            -u all_proxy -u ALL_PROXY -u ftp_proxy -u FTP_PROXY \
            -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE \
          timeout -k 15 "$AGENT_TIMEOUT" opencode run --auto -m "$OPENCODE_MODEL" "$prompt" < /dev/null
        echo "[loop-shard-${SHARD}] $(date '+%F %T') opencode returned (exit $?)"
    else
        echo "[loop-shard-${SHARD}] TASK_MD missing at $TASK_MD"
    fi

    merge_if_needed
    git_push_if_needed

    if waiting_is_1; then
        echo "[loop-shard-${SHARD}] WAITING=1 → sleep ${SLEEP_WAIT}s"
        sleep "$SLEEP_WAIT"
    else
        echo "[loop-shard-${SHARD}] WAITING=0 → sleep ${SLEEP_BUSY}s"
        sleep "$SLEEP_BUSY"
    fi
done
