#!/bin/bash
# BaiZe 正式训练数据准备（Stage i/iii/iv 数据侧）自动推进循环
# 让 cline 读任务书连续推进，并每约 PUSH_INTERVAL 秒兜底做一次 git 同步 + commit + push。
# 唤醒间隔自适应：读 MEMORY_DATA.md 的 WAITING 标志——无阻塞(0)约 1 分钟续跑，有异步阻塞(1)约 30 分钟轮询省 token。
#
# 启动方式（脱离进程组，防工具超时误杀）:
#   setsid bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_data_loop.sh \
#     > /tmp/baize_data_loop.log 2>&1 < /dev/null &
#
# 停止方式:
#   pkill -f baize_data_loop.sh
#
# ⚠️ 与 baize_vision_loop.sh / baize_pretrain_loop.sh 的关键差异（都是那些脚本踩过的坑）:
#   1) 本脚本在 push 前**先 fetch + pull --rebase --autostash**（那两版只 push 不 pull，远端一旦前进就永久卡死）
#   2) WAITING 正则收紧为 **行首** 匹配（旧版 WAITING:[* ]*1 会误匹配正文里的散文）
#   3) commit 只 add 本任务自己的文件（旧版 git add -A 会把别的任务在途文件一起卷进提交）
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_MD="$SCRIPT_DIR/BAIZE_DATA_TASK.md"
CWD="$SCRIPT_DIR"
GIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo '/nas_train/app.e0031982/code/super_intelligence_2035')"
REL="doc/BaiZe-ISEDA2027/run"

MODEL="glm-5.2"                     # 编排模型（deepseek-v4-pro-fp4 额度已耗尽）

# 🔒 2026-10-04 运维（RUN_ID 55）：本线专用 cline 隔离配置目录
#   背景：多条线共用 ~/.cline/data/globalState.json，谁改了 openAiBaseUrl 就会影响别人。
#   隔离目录已由 ops 建好：含 globalState.json + secrets.json + settings/（base=agi-gateway …/cloud/v1）。
DATA_DIR="/nas_train/app.e0031982/.cline_data"
LLM_DATA_DIR="$DATA_DIR"            # 让 llm_rotate.sh 把 openAiBaseUrl 写进【本线隔离目录】

# 🔑 glm-5.2 key（编排模型；deepseek-v4-pro-fp4 额度已耗尽，改用 glm-5.2）
CLINE_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23"

CLINE_TIMEOUT=1500              # 单次 cline 最多 25 分钟
PUSH_INTERVAL=1800              # 每 30 分钟兜底同步一次（=SLEEP_WAIT；2026-10-06 由 5h 缩短：心跳 >30min 即按卡死处理）
SLEEP_BUSY=60                   # 无阻塞时的唤醒间隔
SLEEP_WAIT=1800                 # 有异步阻塞时的唤醒间隔（省 token）
MEMORY="$SCRIPT_DIR/MEMORY_DATA.md"
LAST_PUSH="/tmp/baize_data_last_push"

# 🔑 额度/鉴权体检 + 自动轮换（2026-10-04 用户指令）：额度耗尽时 agent 自己在任务书里也动不了 → 必须在 loop 里。
#   候选来自 doc/keys.txt（10 项 → 取 8 个 chat/coding LLM，排除 ASR/文生图）；
#   探针 = curl /chat/completions（200 可用 / 429 额度耗尽 / 403 base 不匹配）——现场实测见 run/ops/outbox.md RUN_ID 43/44。
#   ⚠️ base 必须与模型匹配（flash@/v1=200 但 flash@/cloud/v1=403）→ llm_pick 会自动改写 cline 的 openAiBaseUrl（首次改动前备份 .llmrot.bak）。
KEYS_TXT="$GIT_ROOT/doc/keys.txt"
LLM_STATE="/tmp/baize_data_llm_idx"
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

    # 2) 只提交本任务自己的文件（共享工作副本：git add -A 会卷入其他任务的在途文件）
    # 🧭 2026-10-06：① 补齐此前漏掉的本线产物（任务书/配方/磁盘清单/HTML），否则它们永不会被兜底提交；
    #             ② 逐项判存在后再 add —— `git add` 只要有一个 pathspec 不匹配就整体失败，而 2>/dev/null 会吞掉报错。
    for p in "$REL/MEMORY_DATA.md" "$REL/DATA_LEDGER.md" "$REL/CONTAMINATION_CHECK.md" \
             "$REL/BAIZE_DATA_TASK.md" "$REL/DATA_MIX_RECIPE.md" "$REL/DISK_CLEANUP_INVENTORY.md" \
             "$REL/data_pipeline" "$REL/daily-memories-data" "$REL/GPU29_ALLOC.md"; do
        [ -e "$p" ] && git add -- "$p"
    done
    for g in doc/BaiZe-ISEDA2027/report_data_*.html; do
        [ -e "$g" ] && git add -- "$g"
    done
    if git diff --cached --quiet; then
        echo "[push] nothing of ours to commit."
    else
        if git commit -m "data-prep auto-commit $(date '+%F %T')" >/dev/null 2>&1; then
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
          # 🔑 额度/鉴权体检 + 自动轮换（候选 = doc/keys.txt 的 8 个 chat LLM；200 可用 / 429 额度耗尽 / 403 base 不匹配）
          #    全挂 → 跳过本轮（不静默空转）；选中项的 base 会自动写进 cline 的 openAiBaseUrl
          if llm_pick "$LLM_STATE" "$KEYS_TXT"; then
        env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u ftp_proxy -u FTP_PROXY \
            -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE \
          cline --data-dir "$DATA_DIR" -c "$CWD" --auto-approve true -m "$LLM_MODEL" -k "$LLM_KEY" -P openai-compatible -t "$CLINE_TIMEOUT" "$prompt" < /dev/null
          else
            echo "[loop] $(date '+%F %T') !!! 无可用 LLM 候选 → 跳过本轮 cline"
          fi
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
