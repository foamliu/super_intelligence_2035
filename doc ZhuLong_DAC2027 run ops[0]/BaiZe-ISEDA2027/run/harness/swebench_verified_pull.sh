#!/usr/bin/env bash
# swebench_verified_pull.sh — 后台批量拉取 SWE-bench Verified 500 镜像（限速、不抢 TB）
# 限制：Docker Hub 匿名限速 100 manifest 请求/小时/共享IP(203.127.181.131)
#   - layer 下载不计入限速；瓶颈是 manifest 请求（每张 ~2 次）
#   - docker pull 遇 429 立即失败（daemon 不重试）→ 本脚本检测 toomanyrequests 后长退避 300s
#   - 串行 pull，批间查磁盘，TB 在跑时加 pause
#   - 已存在本地则跳过；进度写 swebench_verified_pull_progress.txt
# 用法: setsid sg docker -c "bash swebench_verified_pull.sh" > /tmp/swebench_verified_pull.log 2>&1 < /dev/null &
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LIST="$HERE/swebench_verified_image_list.txt"
PROG="$HERE/swebench_verified_pull_progress.txt"
LOG="/tmp/swebench_verified_pull_detail.log"
DOCKER_ROOT="/data/docker"
BATCH=50; MAX_ATTEMPT=15; RATE_BACKOFF=300; ERR_BACKOFF=30; DISK_MIN_GB=50
echo "[swebench-pull] started $(date '+%F %T')" | tee "$PROG"
[ ! -f "$LIST" ] && { echo "[swebench-pull] FATAL: $LIST not found" | tee -a "$PROG"; exit 1; }
total=$(wc -l < "$LIST"); echo "[swebench-pull] total=$total list=$LIST" | tee -a "$PROG"
pulled=0; failed=0; skipped=0; failed_list=""; idx=0
tb_running(){ pgrep -f 'harbor run -p /tmp/tb_7x89_dataset' >/dev/null 2>&1; }
disk_free_gb(){ df -BG "$DOCKER_ROOT" 2>/dev/null | awk 'NR==2{gsub("G","",$4);print $4}'; }
while IFS=$'\t' read -r iid img; do
    [ -z "$iid" ] && continue; idx=$((idx+1))
    if docker image inspect "$img" >/dev/null 2>&1; then
        skipped=$((skipped+1))
        echo "[swebench-pull] [$idx/$total] SKIP $iid (present) pulled=$pulled failed=$failed skipped=$skipped" | tee -a "$PROG"; continue; fi
    ok=0
    for attempt in $(seq 1 $MAX_ATTEMPT); do
        out=$(docker pull "$img" 2>&1); rc=$?
        if [ $rc -eq 0 ]; then ok=1; break; fi
        if echo "$out" | grep -qiE 'toomanyrequests|rate.limit|429'; then
            echo "[swebench-pull] [$idx/$total] 429 $iid attempt=$attempt sleep=${RATE_BACKOFF}s" | tee -a "$LOG"
            sleep "$RATE_BACKOFF"
        else
            echo "[swebench-pull] [$idx/$total] ERR $iid attempt=$attempt: $(echo "$out"|tail -1|head -c 150)" | tee -a "$LOG"
            sleep "$ERR_BACKOFF"
        fi
    done
    if [ "$ok" -eq 1 ]; then
        pulled=$((pulled+1))
        echo "[swebench-pull] [$idx/$total] OK $iid pulled=$pulled failed=$failed skipped=$skipped" | tee -a "$PROG"
    else
        failed=$((failed+1)); failed_list="$failed_list $iid"
        echo "[swebench-pull] [$idx/$total] FAIL $iid after $MAX_ATTEMPT attempts" | tee -a "$PROG"
    fi
    if [ $((idx % BATCH)) -eq 0 ]; then
        free=$(disk_free_gb)
        echo "[swebench-pull] === BATCH idx=$idx pulled=$pulled failed=$failed skipped=$skipped disk_free=${free}GB ===" | tee -a "$PROG"
        if [ -n "$free" ] && [ "$free" -lt "$DISK_MIN_GB" ]; then
            echo "[swebench-pull] ⚠️ disk ${free}GB<${DISK_MIN_GB}GB pause 120s" | tee -a "$PROG"; sleep 120; fi
        sleep 10
    else
        if tb_running; then sleep 5; else sleep 1; fi
    fi
done < "$LIST"
echo "[swebench-pull] DONE $(date '+%F %T') total=$total pulled=$pulled failed=$failed skipped=$skipped" | tee -a "$PROG"
[ -n "$failed_list" ] && echo "[swebench-pull] FAILED:$failed_list" | tee -a "$PROG"
present=$(docker images --filter "reference=swebench/*" --format '{{.Repository}}' | sort -u | wc -l)
echo "[swebench-pull] swebench/* present: $present / $total" | tee -a "$PROG"
