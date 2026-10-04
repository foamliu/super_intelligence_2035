#!/bin/bash
# ZhuLong（DAC2027）EDA 消融评测自动推进循环（合并版：S1 保真度 → 组件 → S2 Φ → 模型，单任务书单循环）
# 让 cline 读任务书连续推进，并每约 PUSH_INTERVAL 秒兜底做一次 git 同步 + commit + push。
# 唤醒间隔自适应：读 MEMORY_ZHULONG.md 的 WAITING 标志——
#   无阻塞(0)约 1 分钟续跑，有异步阻塞(1，即一轮 eval 正在跑 / infra 不就绪)约 30 分钟轮询省 token。
#
# 启动方式（脱离进程组，防工具超时误杀）:
#   当前 2.12 开发机:
#     setsid bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run/zhulong_loop.sh \
#       > /tmp/zhulong_loop.log 2>&1 < /dev/null &
#   最终 36.15 服务器（将 /nas_train/ 替换为 /nasdata/）:
#     setsid bash /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run/zhulong_loop.sh \
#       > /tmp/zhulong_loop.log 2>&1 < /dev/null &
#
# 停止方式:
#   pkill -f zhulong_loop.sh
#
# ⚠️ 本脚本以 baize_harness_loop.sh 为模板，已避开 vision/pretrain 两版踩过的坑:
#   1) push 前先 fetch + pull --rebase --autostash（那两版只 push 不 pull，远端一旦前进就永久卡死）
#   2) WAITING 正则收紧为**行首**匹配（旧版会误匹配正文里的散文）
#   3) commit 只 add 本任务自己的文件（旧版 git add -A 会把别的任务在途文件一起卷进提交）
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_MD="$SCRIPT_DIR/ZHULONG_TASK.md"
CWD="$SCRIPT_DIR"
GIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo '/nasdata/app.e0031982/code/super_intelligence_2035')"
RUN_REL="doc/ZhuLong_DAC2027/run"                      # 编排文件：MEMORY / daily-memories / 自建脚本
PAPER_REL="doc/ZhuLong_DAC2027/ZhuLong_DAC2027"        # 论文权威树：最终回填 [TBD] 的地方

# 编排 agent 的模型（固定），不是被评测模型：
#   本 loop 的 `-m "$MODEL"` 只负责读 MEMORY / pgrep / 打分 / 切臂 / cline auth。
#   被评测的求解 agent 由任务书内 `cline auth -m <MODEL_ID>` 切换（见 ablation_run_task_model_full.md），
#   run_cline_script.sh 读取 ~/.cline/data/settings，与本 loop 的 -m 无关。
MODEL="glm-5.2"

# 🔑 glm-5.2 key（编排模型；deepseek-v4-pro-fp4 额度已耗尽，改用 glm-5.2）
CLINE_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23"

CLINE_TIMEOUT=2700              # 单次编排 cline 最多 45 分钟（读态+打分+切臂+启动，足够）
PUSH_INTERVAL=18000             # 每 5 小时兜底同步一次
SLEEP_BUSY=60                   # 无阻塞时的唤醒间隔
SLEEP_WAIT=1800                 # 有异步阻塞（eval 跑着/infra 不就绪）时的唤醒间隔
MEMORY="$SCRIPT_DIR/MEMORY_ZHULONG.md"
LAST_PUSH="/tmp/zhulong_last_push"

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

    # 1) 先同步远端（共享工作副本：别的 agent 可能已 pull）
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

    # 2) 只提交本任务自己的文件（编排 run/ + 论文权威树）
    git add -- "$RUN_REL" "$PAPER_REL" 2>/dev/null
    if git diff --cached --quiet; then
        echo "[push] nothing of ours to commit."
    else
        if git commit -m "zhulong auto-commit $(date '+%F %T')" >/dev/null 2>&1; then
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

while true; do
    echo "[loop] $(date '+%F %T') wake up, invoking cline ..."
    if [[ -f "$TASK_MD" ]]; then
        prompt="$(< "$TASK_MD")"
        # 🚫 剥掉代理环境变量（内网网关 agi-gateway.cxmt.com 不该走外网代理，否则 `error: Forbidden`）。
        #    ⚠️ 只作用于本行 cline；loop 自身 / git push 仍保留 proxy（外网仍需代理）。
        env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u ftp_proxy -u FTP_PROXY \
            -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE \
          cline -c "$CWD" --auto-approve true -m "$MODEL" -k "$CLINE_KEY" -t "$CLINE_TIMEOUT" "$prompt" < /dev/null
        echo "[loop] $(date '+%F %T') cline returned (exit $?), checking git sync ..."
    else
        echo "[loop] $(date '+%F %T') TASK_MD missing at $TASK_MD"
    fi
    git_sync_and_push
    if waiting_is_1; then
        echo "[loop] $(date '+%F %T') WAITING=1 (eval running / infra not ready) → sleep ${SLEEP_WAIT}s"
        sleep "$SLEEP_WAIT"
    else
        echo "[loop] $(date '+%F %T') WAITING=0 (no blocker) → sleep ${SLEEP_BUSY}s"
        sleep "$SLEEP_BUSY"
    fi
done