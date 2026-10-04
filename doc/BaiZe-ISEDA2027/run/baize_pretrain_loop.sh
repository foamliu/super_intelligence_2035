#!/bin/bash
# BaiZe Stage(i) LLM 预训练（Mamba2-hybrid 2B 超参搜索）自动推进循环：
# 让 cline 读任务书连续推进，并每约 PUSH_INTERVAL 秒兜底做一次 git commit + push（无人值守时保证成果不丢）。
# 唤醒间隔自适应：读 MEMORY_PRETRAIN_2B.md 的 WAITING 标志——无阻塞(0)约 1 分钟续跑，有异步阻塞(1)约 30 分钟轮询省 token。
# 启动方式（脱离进程组，防工具超时误杀）:
#   setsid bash /path/to/baize_pretrain_loop.sh > /tmp/baize_pretrain_loop.log 2>&1 < /dev/null &
set -u

# 以脚本自身所在目录为基准，任务书 + 记忆文件均与脚本同目录（run/）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_MD="$SCRIPT_DIR/BAIZE_PRETRAIN_2B_TASK.md"
CWD="$SCRIPT_DIR"
# git 仓库根目录（run/ 的上级 super_intelligence_2035）
GIT_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || echo '/nas_train/app.e0031982/code/super_intelligence_2035')"
REL="doc/BaiZe-ISEDA2027/run"   # 本任务在仓库中的相对目录（只提交这里的文件）

MODEL="glm-5.2"                     # 编排模型（deepseek-v4-pro-fp4 额度已耗尽）

# 🔑 2026-10-04 运维定稿（RUN_ID 26 四路矩阵实证）：**必须给 cline 显式传 `-k <有效key>`**
#   V0 原样 / V1 剥KEY+URL+TYPE / V2 剥proxy+KEY+URL+TYPE  → 全 `error: Forbidden`
#   V3 = 剥 proxy+KEY+URL+TYPE **且 `-k <secrets 里的有效 key>`** → **OK** ✅
#   （同一把 key 用 curl 打 /v1/chat/completions = 200；`.12` 上同命令不带 -k 也能跑，
#     但 `.29` 不行 → 以 V3 为准。）
#   key 运行时从 secrets.json 现读，**不落仓库**；secrets.json 由运维用有效 key 维护。
CLINE_KEY="$(sed -n 's/.*"openAiApiKey"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$HOME/.cline/data/secrets.json" 2>/dev/null | head -1)"
# 若 secrets.json 读不到，fallback 到 glm-5.2 硬编码 key
[ -z "$CLINE_KEY" ] && CLINE_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23"
CLINE_BASE="http://agi-gateway.cxmt.com/cloud/v1"

CLINE_TIMEOUT=1500              # 单次 cline 最多 25 分钟
PUSH_INTERVAL=18000             # 每 5 小时 git push 一次（4~6 小时间隔内）
SLEEP_BUSY=60                   # 无阻塞任务时的唤醒间隔：约 1 分钟（连续推进，不空耗）
SLEEP_WAIT=1800                 # 有异步阻塞任务(训练 running)时的唤醒间隔：30 分钟（省 token）
MEMORY="$SCRIPT_DIR/MEMORY_PRETRAIN_2B.md"
LAST_PUSH="/tmp/baize_pretrain_last_push"

git_push_if_needed() {
    local now last
    now=$(date +%s)
    last=0
    [ -f "$LAST_PUSH" ] && last="$(cat "$LAST_PUSH" 2>/dev/null)"
    if [ $((now - last)) -lt "$PUSH_INTERVAL" ]; then
        return
    fi
    echo "[push] $(date '+%F %T') push interval reached, syncing ..."
    cd "$GIT_ROOT" || return

    # 1) 先 fetch + rebase（旧版只 push 不 pull：远端一旦前进就永久卡死）
    if ! timeout 120 git fetch origin >/dev/null 2>&1; then
        echo "[push] fetch FAILED (network?) - skip this cycle."
        return
    fi
    local counts behind
    counts="$(git rev-list --left-right --count origin/main...HEAD 2>/dev/null || echo '0 0')"
    behind="$(echo "$counts" | awk '{print $1}')"
    if [ "${behind:-0}" -gt 0 ]; then
        if git pull --rebase --autostash origin main >/dev/null 2>&1; then
            echo "[push] pull --rebase OK."
        else
            echo "[push] pull --rebase FAILED - aborting rebase, skip this cycle."
            git rebase --abort >/dev/null 2>&1 || true
            return
        fi
    fi

    # 2) 只提交本任务自己的文件（共享工作副本：git add -A 会卷入其他任务的在途文件）
    git add -- "$REL/MEMORY_PRETRAIN_2B.md" "$REL/EXPERIMENTS_PRETRAIN_2B.md" \
               "$REL/EXPERIMENTS_PRETRAIN_2B_ROUND2.md" "$REL/daily-memories" 2>/dev/null
    if git diff --cached --quiet; then
        echo "[push] nothing of ours to commit."
    else
        git commit -m "pretrain auto-commit $(date '+%F %T')" >/dev/null 2>&1 && echo "[push] committed."
    fi

    # 3) 推送
    if git push origin main 2>&1; then
        echo "[push] push OK."
    else
        echo "[push] push FAILED (will retry next cycle)."
    fi
    date +%s > "$LAST_PUSH"
}

while true; do
    echo "[loop] $(date '+%F %T') wake up, invoking cline ..."
    if [[ -f "$TASK_MD" ]]; then
        prompt="$(< "$TASK_MD")"
        # 🚫 2026-10-04 运维修复：给 cline 剥掉代理环境变量。
        #   内网网关 (OPENAI_API_URL=http://agi-gateway.cxmt.com/v1) 不该走外网代理，
        #   否则网关返回 `error: Forbidden`，而 cline 仍 exit 0 → loop 静默空转（.29 曾因此瞎跑 ~9h，
        #   10-04 07:15 ops 探查定位；.12 于 2026-09-29 遇过同样问题，unset http_proxy 即解决）。
        #   ⚠️ 只作用于本行：loop 自身/`git push` 仍保留 proxy（外网仍需代理）。
        env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u ftp_proxy -u FTP_PROXY \
            -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE \
          cline -c "$CWD" --auto-approve true -m "$MODEL" -k "$CLINE_KEY" -b "$CLINE_BASE" -t "$CLINE_TIMEOUT" "$prompt" < /dev/null
        echo "[loop] $(date '+%F %T') cline returned (exit $?), checking git push ..."
    else
        echo "[loop] $(date '+%F %T') TASK_MD missing at $TASK_MD"
    fi
    git_push_if_needed
    # 自适应睡眠：WAITING=1（有训练等异步任务 running）→ 长睡 30 分钟省 token；
    # WAITING=0（无阻塞、应连续推进）→ 短睡 1 分钟，让 cline 尽快续跑下一轮。
    SLEEP="$SLEEP_BUSY"
    # ⚠️ 只认**行首**的 WAITING 字段。旧正则 'WAITING:[* ]*1' 会误匹配正文散文
    #（MEMORY_PRETRAIN_2B.md 里就有一句 `WAITING: **1**` 被命中，导致睡眠时长由散文决定）。
    if grep -qE '^WAITING:[[:space:]]*1' "$MEMORY" 2>/dev/null; then
        SLEEP="$SLEEP_WAIT"
        echo "[loop] $(date '+%F %T') WAITING=1（异步任务 running）→ sleep ${SLEEP}s"
    else
        echo "[loop] $(date '+%F %T') WAITING=0（无阻塞）→ sleep ${SLEEP}s"
    fi
    sleep "$SLEEP"
done