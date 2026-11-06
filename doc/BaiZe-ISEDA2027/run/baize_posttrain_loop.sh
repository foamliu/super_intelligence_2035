#!/bin/bash
# BaiZe Stage(ii) LLM Post-Training（领域退火 / SFT / RLVR-GRPO / EDA-Eval 评测）自动推进循环
# 机器：10.252.32.17（post-train 线专用）
# 让 cline 读任务书连续推进，并每约 PUSH_INTERVAL 秒兜底做一次 git 同步 + commit + push。
# 唤醒间隔自适应：读 MEMORY_POSTTRAIN.md 的 WAITING 标志——无阻塞(0)约 1 分钟续跑，有异步阻塞(1)约 15 分钟轮询省 token。
#
# 启动方式（脱离进程组，防工具超时误杀）:
#   setsid bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_posttrain_loop.sh \
#     > /tmp/baize_posttrain_loop.log 2>&1 < /dev/null &
#
# 停止方式:
#   pkill -f baize_posttrain_loop.sh
#
# ⚠️ 本脚本以 baize_harness_loop.sh 为模板（已是修正版），已避开 vision/pretrain 两版踩过的坑:
#   1) push 前先 fetch + pull --rebase --autostash（旧版只 push 不 pull，远端一旦前进就永久卡死）
#   2) WAITING 正则收紧为**行首**匹配（旧版 WAITING:[* ]*1 会误匹配正文里的散文）
#   3) commit 只 add 本任务自己的文件（旧版 git add -A 会把别的任务在途文件一起卷进提交）
#   4) loop 重启必须带「正确 PATH」（cline 在 ~/.bun/bin；非登录 shell 会找不到 cline → 静默空转）
#      ✅ 重启后必查：`command -v cline` 有输出；`tail` 日志出现 `invoking cline ...` 且无 `No such file`。
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_MD="$SCRIPT_DIR/BAIZE_POSTTRAIN_TASK.md"
CWD="$SCRIPT_DIR"
GIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo '/nas_train/app.e0031982/code/super_intelligence_2035')"
REL="doc/BaiZe-ISEDA2027/run"

MODEL="glm-5.2"                     # 编排模型（deepseek-v4-pro-fp4 额度已耗尽）

# 🔑 glm-5.2 key（编排模型；deepseek-v4-pro-fp4 额度已耗尽，改用 glm-5.2）
CLINE_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23"

CLINE_TIMEOUT=3600              # 单次 cline 最多 60 分钟（post-train 诊断/盘点/方案是连续任务，给足时间）
PUSH_INTERVAL=900               # 每 15 分钟兜底同步一次
SLEEP_BUSY=60                   # 无阻塞时的唤醒间隔（连续推进，用短睡尽快续跑）
SLEEP_WAIT=900                  # 有异步阻塞时的唤醒间隔（省 token）
MEMORY="$SCRIPT_DIR/MEMORY_POSTTRAIN.md"
LAST_PUSH="/tmp/baize_posttrain_last_push"

# 🔑 额度/鉴权体检 + 自动轮换（候选 = doc/keys.txt 的 8 个 chat LLM；200 可用 / 429 额度耗尽 / 403 base 不匹配）
KEYS_TXT="$GIT_ROOT/doc/keys.txt"
LLM_STATE="/tmp/baize_posttrain_llm_idx"
[ -f "$SCRIPT_DIR/llm_rotate.sh" ] && . "$SCRIPT_DIR/llm_rotate.sh"

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

    # 1) 先同步远端（共享工作副本：别的 agent 可能已经 pull 过，此处通常是 no-op）
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

    # 2) 只提交本任务自己的文件（避免卷入其他任务的在途文件）
    #    逐项判存在后再 add（git add 只要有一个 pathspec 不匹配就整体失败）
    for p in "$REL/MEMORY_POSTTRAIN.md" "$REL/EXPERIMENTS_POSTTRAIN.md" \
             "$REL/BAIZE_POSTTRAIN_TASK.md" "$REL/daily-memories-posttrain" \
             "$REL/baize_posttrain_anneal.sh" "$REL/baize_posttrain_sft.sh" \
             "$REL/baize_posttrain_rl_grpo.sh" "$REL/baize_posttrain_eval.sh"; do
        [ -e "$p" ] && git add -- "$p"
    done
    if git diff --cached --quiet; then
        echo "[push] nothing of ours to commit."
    else
        if git commit -m "posttrain auto-commit $(date '+%F %T')" >/dev/null 2>&1; then
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
        # 🚫 给 cline 剥掉代理环境变量（内网网关不该走外网代理，否则 Forbidden + 静默空转）
        #   只作用于本行：loop 自身/git push 仍保留 proxy（外网仍需代理）。
        # 🔑 额度/鉴权体检 + 自动轮换；全挂 → 跳过本轮（不静默空转）
        # ⚠️ llm_pick 的 curl 探针也要剥代理 —— agi-gateway.cxmt.com 是内网地址，
        #    走外网代理(.25)会 503（2026-11-06 .17 本机实测全 503）
        #    不能用子 shell（llm_pick 设的 LLM_MODEL 等回不来），用 save/restore
        _sv_http_proxy="${http_proxy:-}"; _sv_https_proxy="${https_proxy:-}"
        _sv_HTTP_PROXY="${HTTP_PROXY:-}"; _sv_HTTPS_PROXY="${HTTPS_PROXY:-}"
        unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
        if llm_pick "$LLM_STATE" "$KEYS_TXT"; then
            env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u ftp_proxy -u FTP_PROXY \
                -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE \
              cline -c "$CWD" --auto-approve true -m "$LLM_MODEL" -k "$LLM_KEY" -P openai-compatible -t "$CLINE_TIMEOUT" "$prompt" < /dev/null
        else
            echo "[loop] $(date '+%F %T') !!! 无可用 LLM 候选 → 跳过本轮 cline"
        fi
        # restore proxy for git push
        [ -n "$_sv_http_proxy" ] && export http_proxy="$_sv_http_proxy" || unset http_proxy
        [ -n "$_sv_https_proxy" ] && export https_proxy="$_sv_https_proxy" || unset https_proxy
        [ -n "$_sv_HTTP_PROXY" ] && export HTTP_PROXY="$_sv_HTTP_PROXY" || unset HTTP_PROXY
        [ -n "$_sv_HTTPS_PROXY" ] && export HTTPS_PROXY="$_sv_HTTPS_PROXY" || unset HTTPS_PROXY
        echo "[loop] $(date '+%F %T') cline returned (exit $?), checking git sync ..."
    else
        echo "[loop] $(date '+%F %T') TASK_MD missing at $TASK_MD"
    fi
    git_sync_and_push
    if waiting_is_1; then
        echo "[loop] $(date '+%F %T') WAITING=1 (async task running) → sleep ${SLEEP_WAIT}s"
        sleep "$SLEEP_WAIT"
    else
        echo "[loop] $(date '+%F %T') WAITING=0 (no blocker) → sleep ${SLEEP_BUSY}s"
        sleep "$SLEEP_BUSY"
    fi
done
