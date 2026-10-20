#!/bin/bash
# baize_decay_watchdog.sh — BaiZe 80B decay v2 崩溃自动重启 watchdog（.29 主训练）
#
# 用途（P0-b，2026-10-20 crash 复盘）：训练进程消失且未收尾时自动 resume，
# 把"无人处理窗口 75min"压到 ≤5min。防死循环：24h 内崩溃 ≥3 次则停止并写 blocker。
#
# 用法：
#   bash baize_decay_watchdog.sh            # 常驻循环，每 300s 检查一次（默认）
#   bash baize_decay_watchdog.sh --once     # 只检查一次后退出（供 cron / 手动）
#   bash baize_decay_watchdog.sh --dry-run  # 只记录观察，绝不重启动作（叠加 --once 可测试）
#
# 🚫 纪律：当前 run 未结束前【不要】以常驻模式启动本 watchdog（避免与人工 resume 冲突）。
#    需要动作前先以 --dry-run --once 验证逻辑。
set -uo pipefail

RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
TRAIN_LOG=/tmp/baize_xmodel25_decay_v2_train.log
CKPT_BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/xmodel25_baize_80b_decay
ITERS=19980
CRASHCNT_FILE=/tmp/decay_watchdog.crashcnt
BLOCKER_FILE=/tmp/decay_watchdog.blocker
WATCH_LOG=/tmp/decay_watchdog.log
CHECK_INTERVAL=300          # 5 分钟
MAX_CRASH_24H=3             # 24h 内崩溃 ≥3 次 → 停止自动重启
DRY_RUN=0
ONCE=0
for a in "$@"; do
    case "$a" in
        --dry-run) DRY_RUN=1 ;;
        --once)    ONCE=1 ;;
    esac
done

log() { echo "[$(date '+%F %T')] $*" >> "$WATCH_LOG"; }

# 判活必须用 strings（train_log 是 sparse file，tail 不可靠）。
# 返回最近一条 '[step N/ITERS]' 中的 N；无则空。
latest_step() {
    strings "$TRAIN_LOG" 2>/dev/null | grep '^\[step' | tail -1 \
        | sed -E 's/^\[step ([0-9]+)\/.*/\1/'
}

# 选最新完好 ckpt：step_* 目录下必须存在非空的 model.safetensors（且 >1GB 防半写）。
latest_ckpt() {
    local d s best=0
    for d in "$CKPT_BASE"/step_*; do
        [ -d "$d" ] || continue
        [ -f "$d/model.safetensors" ] || continue
        s=$(basename "$d" | sed -E 's/^step_([0-9]+)$/\1/')
        [ -z "$s" ] || [ "$s" -le 0 ] 2>/dev/null && continue
        # 防半写：model.safetensors 完整应 >1GB（主 run 为 2.7GB）
        local sz; sz=$(stat -c %s "$d/model.safetensors" 2>/dev/null || echo 0)
        [ "$sz" -gt 1073741824 ] || continue
        [ "$s" -gt "$best" ] && best="$s"
    done
    [ "$best" -gt 0 ] && echo "$CKPT_BASE/step_$best"
}

# 24h 内崩溃次数（crashcnt 文件一行一个 epoch 秒，统计最近 86400s 内条数）
crash_cnt_24h() {
    local now; now=$(date +%s)
    [ -f "$CRASHCNT_FILE" ] || { echo 0; return; }
    awk -v now="$now" '{ if (now - $1 <= 86400) c++ } END { print c+0 }' "$CRASHCNT_FILE"
}

check_once() {
    local step ckpt cnt
    if pgrep -f 'xmodel25_decay_v2' >/dev/null 2>&1; then
        step=$(latest_step)
        log "ALIVE step=${step:-?}/$ITERS (pgrep 命中)"
        return 0
    fi
    # —— 进程消失 ——
    step=$(latest_step)
    log "DOWN process-gone step=${step:-?}/$ITERS"
    # 收尾判定①：final/ ckpt 存在且完好 → 训练已正常结束
    # （防 off-by-one：训练末步常为 ITERS-1，如 step19979 vs ITERS19980；
    #   且 /tmp log 收尾后可能被截断为空，latest_step 返回空，此处兜底）
    if [ -f "$CKPT_BASE/final/model.safetensors" ]; then
        local fsz; fsz=$(stat -c %s "$CKPT_BASE/final/model.safetensors" 2>/dev/null || echo 0)
        if [ "$fsz" -gt 1073741824 ]; then
            log "DONE final/ ckpt 完好 (${fsz}B) → 训练已正常收尾，不动作"
            return 0
        fi
    fi
    [ -n "$step" ] || { log "NO-STEP-IN-LOG → 无法判定，不动作"; return 0; }
    if [ "$step" -ge "$ITERS" ]; then
        log "DONE step=$step >= ITERS=$ITERS → 训练已收尾，不动作"
        return 0
    fi
    # 未收尾且进程消失 → 计一次崩溃，再按 24h 计数决定是否重启
    date +%s >> "$CRASHCNT_FILE"
    cnt=$(crash_cnt_24h)
    if [ "$cnt" -ge "$MAX_CRASH_24H" ]; then
        log "BLOCKER 24h 崩溃=$cnt ≥ $MAX_CRASH_24H → 停止自动重启"
        [ -f "$BLOCKER_FILE" ] || \
            echo "[$(date '+%F %T')] watchdog loop blocked: 24h crash cnt=$cnt >= $MAX_CRASH_24H, last step=$step/$ITERS" > "$BLOCKER_FILE"
        return 0
    fi
    ckpt=$(latest_ckpt)
    if [ -z "$ckpt" ]; then
        log "NO-VALID-CKPT → blocker（无含 model.safetensors 且 >1GB 的 ckpt）"
        echo "[$(date '+%F %T')] no valid ckpt under $CKPT_BASE (need model.safetensors >1GB)" >> "$BLOCKER_FILE"
        return 0
    fi
    if [ "$DRY_RUN" -eq 1 ]; then
        log "DRY-RUN would-restart: cnt=$cnt RESUME_DIR=$ckpt（不动作）"
        return 0
    fi
    log "RESTART cnt=$cnt from $ckpt"
    ( cd "$RUN_DIR" && RESUME_DIR="$ckpt" setsid bash baize_xmodel25_decay_v2.sh \
        > /tmp/baize_xmodel25_decay_v2_resume.log 2>&1 < /dev/null & )
}

log "watchdog start (dry_run=$DRY_RUN once=$ONCE interval=${CHECK_INTERVAL}s iters=$ITERS max_24h=$MAX_CRASH_24H)"
while :; do
    check_once
    [ "$ONCE" -eq 1 ] && break
    sleep "$CHECK_INTERVAL"
done