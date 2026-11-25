#!/bin/bash
# harness_resource_guard.sh — .29 宿主内存/负载硬护栏（「拦截」而非「报告」）
#
# 背景（2026-11-19 夜事故）：deepseek incr_eval R2800 的 matplotlib 评测容器把宿主 ~2TB
#   内存吃穿（docker ps 里 Exit 255），整机 OOM 卡死。此前 harness 的自检只在「每次唤醒」
#   采样并写"clean"，两次唤醒之间（WAITING=1 时约 15 分钟）无人拦截失控的评测容器。
#
# 本脚本是**独立常驻守护**：每 POLL 秒采样一次宿主 MemAvailable 与 1min load，
# 一旦越界就**当场杀掉 harness 拥有的评测容器**（绝不碰别的线/别的主机进程）。
#
# 范围（只清本线 · 保守）：
#   - 只识别并杀 Docker 容器，判定 = 容器名 `sweb.eval.*` 或镜像 `swebench/*`/`alexgshaw/*`
#     （这三类只属于 harness 的 SWE-bench Verified / Multimodal / Terminal-Bench 评测）。
#   - 宿主进程（predict 的 cline/codex/opencode 等）**不识别不杀**——它们与 pretrain/data/vision
#     共用一个 app.e0031982 用户，无法安全区分；宿主侧内存用 `ulimit -v`（见任务书新令）预防。
#
# 用法（脱离进程组启动，防工具超时误杀）：
#   setsid bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness_resource_guard.sh \
#     > /tmp/harness_resource_guard.log 2>&1 < /dev/null &
# 停止：
#   pkill -f harness_resource_guard.sh
set -u

MEM_MIN_AVAIL_GB="${MEM_MIN_AVAIL_GB:-400}"   # MemAvailable 低于此(GB) → 触发内存拦截
LOAD_MAX="${LOAD_MAX:-160}"                    # 1min load 超此 → 触发 CPU 拦截（224 核 ≈71%）
POLL="${POLL:-15}"                             # 采样间隔（秒）
COOLDOWN="${COOLDOWN:-60}"                     # 两次处置之间最小间隔（秒），给 teardown 留时间
LOG="/tmp/harness_resource_guard.log"
STATE="/tmp/harness_resource_guard.last_action"

log() { echo "[$(date '+%F %T')] $*" >> "$LOG"; }

mem_avail_gb() { awk '/MemAvailable/{printf "%d", $2/1024/1024}' /proc/meminfo 2>/dev/null || echo 0; }
load1()        { awk '{print $1}' /proc/loadavg 2>/dev/null || echo 0; }

# 列出「运行中」的 harness 评测容器：ID<TAB>NAME<TAB>IMAGE
harness_containers() {
    docker ps --format '{{.ID}}\t{{.Names}}\t{{.Image}}' 2>/dev/null \
      | awk -F'\t' '$2 ~ /^sweb\.eval\./ || $3 ~ /^swebench\// || $3 ~ /^alexgshaw\// {print $1}'
}

cooldown_ok() {
    local last now
    last=0
    [ -f "$STATE.last_ts" ] && last="$(cat "$STATE.last_ts" 2>/dev/null || echo 0)"
    now=$(date +%s)
    [ $((now - last)) -ge "$COOLDOWN" ]
}

act() {
    local reason="$1"
    local ids
    ids="$(harness_containers)"
    if [ -z "$ids" ]; then
        log "越界($reason) 但无运行中的 harness 容器——不动作（宿主内存由非容器进程占用，交给任务书的 ulimit/自检）"
        date +%s > "$STATE.last_ts"
        return
    fi
    local n
    n=$(echo "$ids" | wc -l)
    log "🚨 越界($reason)→ 杀 $n 个 harness 评测容器: $(echo "$ids" | tr '\n' ' ')"
    for id in $ids; do
        docker kill "$id" >/dev/null 2>&1 && log "  killed $id" || log "  kill FAILED $id"
    done
    log "  处置后 MemAvailable=$(mem_avail_gb)GB load=$(load1)"
    date +%s > "$STATE.last_ts"
}

log "启动: MEM_MIN_AVAIL_GB=${MEM_MIN_AVAIL_GB} LOAD_MAX=${LOAD_MAX} POLL=${POLL}s COOLDOWN=${COOLDOWN}s"

while true; do
    avail="$(mem_avail_gb)"
    load="$(load1)"
    if [ "$avail" -gt 0 ] && [ "$avail" -lt "$MEM_MIN_AVAIL_GB" ]; then
        if cooldown_ok; then
            act "MemAvailable=${avail}GB < ${MEM_MIN_AVAIL_GB}GB"
        fi
    elif awk -v a="$load" -v b="$LOAD_MAX" 'BEGIN{exit !(a>b)}'; then
        if cooldown_ok; then
            act "load1=${load} > ${LOAD_MAX}"
        fi
    fi
    sleep "$POLL"
done