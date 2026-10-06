#!/bin/bash
# llm_rotate.sh — 4 条 loop 共用的「额度/鉴权体检 + 自动轮换」helper
#   背景（2026-10-04 用户指令）：额度耗尽时 agent 自己在任务书里也动不了 → 这套逻辑必须在 loop 里。
#   事实依据（现场实测，见 run/ops/outbox.md RUN_ID 43/44）：
#     · cline 的 LLM base URL = 【配置项】~/.cline/data/globalState.json 的 openAiBaseUrl
#       （env CLINE_API_BASE_URL 是 Cline 平台自身 API，含 mcpBaseUrl，不是 provider base）
#     · base 必须与模型匹配：deepseek-v4-flash @ /v1 → 200，@ /cloud/v1 → 403
#     · 额度耗尽表现为 HTTP 【429】（实测 deepseek-v4-pro-fp4 → 429；其余 7 个 → 200）
#     · 候选来自 doc/keys.txt（10 项，排除 ASR 与文生图 → 8 个 chat/coding LLM）
#   用法（在每个 loop 里）：
#     KEYS_TXT="$GIT_ROOT/doc/keys.txt"; LLM_STATE="/tmp/baize_<line>_llm_idx"
#     . "$SCRIPT_DIR/llm_rotate.sh"
#     ...
#     if llm_pick "$LLM_STATE" "$KEYS_TXT"; then
#        env -u ... cline -c "$CWD" ... -m "$LLM_MODEL" -k "$LLM_KEY" -P openai-compatible ...
#     else
#        echo "[loop] 无可用 LLM —— 跳过本轮"; fi

LLM_CAND_JSON="${LLM_CAND_JSON:-/tmp/_baize_llm_cand.json}"

# python3 / python 自适应（relay 的非交互 PATH 曾缺 python3，见 2026-10-04 事故）
PYBIN="$(command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python3)"

# 解析 doc/keys.txt -> JSON 候选（必须用 python3：awk -F 对多字节分隔符在非 UTF-8 locale 下会失败）
llm_parse_candidates() {
    "$PYBIN" - "$1" "$LLM_CAND_JSON" <<'PY' 2>/dev/null
import sys, json, pathlib
src, dst = sys.argv[1], sys.argv[2]
blocks, cur = [], {}
for raw in pathlib.Path(src).read_text(encoding='utf-8', errors='replace').split('\n'):
    s = raw.strip()
    if not s:
        if cur.get('model'):
            blocks.append(cur)
        cur = {}
        continue
    for lab, k in (('模型名字', 'model'), ('API Key', 'key'), ('Base Url (OpenAI)', 'oai')):
        if lab in s:
            cur[k] = s.split('：', 1)[-1].strip() if '：' in s else s.split(':', 1)[-1].strip()
            break
if cur.get('model'):
    blocks.append(cur)
seen, out = set(), []
for b in blocks:
    m = b.get('model', '')
    if m in seen or not b.get('key') or not b.get('oai'):
        continue
    seen.add(m)
    if 'asr' in m.lower() or 'seedream' in m.lower():   # 非 chat 模型排除
        continue
    out.append({'model': m, 'key': b['key'], 'base': b['oai']})
pathlib.Path(dst).write_text(json.dumps(out, ensure_ascii=False), encoding='utf-8')
print(len(out))
PY
}

# 探针：返回 HTTP 码（200=可用；429=额度耗尽；403=base 不匹配/无权限）
llm_probe() {
    timeout 20 curl -s -o /dev/null -w '%{http_code}' --max-time 18 \
        -H "Authorization: Bearer $2" -H 'Content-Type: application/json' \
        -d "{\"model\":\"$1\",\"messages\":[{\"role\":\"user\",\"content\":\"hi\"}],\"max_tokens\":2}" \
        "$3/chat/completions" 2>/dev/null
}

# 把 base 写进 cline 配置（仅在与当前值不同时改；首次改动前备份一次）
# 🔒 2026-10-04 运维（RUN_ID 55）：目标目录可用 LLM_DATA_DIR 覆盖——
#   各线 loop 设 LLM_DATA_DIR=<本线隔离目录>（如 /nas_train/app.e0031982/.cline_vision）后，
#   base 就写进【隔离目录】的 globalState.json，不再动共享 ~/.cline/data；
#   未设时行为不变（默认仍写共享目录，harness 线即如此）。
llm_apply_base() {
    local D="${LLM_DATA_DIR:-$HOME/.cline/data}"
    local G="$D/globalState.json" cur
    [ -f "$G" ] || return 0
    cur="$(sed -n 's/.*"openAiBaseUrl"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$G" 2>/dev/null | head -1)"
    [ "$cur" = "$1" ] && return 0
    [ -f "$G.llmrot.bak" ] || cp -a "$G" "$G.llmrot.bak" 2>/dev/null
    "$PYBIN" - "$G" "$1" <<'PY' 2>/dev/null
import json, sys
p, base = sys.argv[1], sys.argv[2]
d = json.load(open(p, encoding='utf-8'))
d['openAiBaseUrl'] = base
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
PY
    echo "[llmrot] $(date '+%F %T') openAiBaseUrl: ${cur:-<none>} -> $1"
}

# 从上次成功的下标开始**环状**探测，第一个 200 即选中；成功则写出 LLM_MODEL/LLM_KEY/LLM_BASE
llm_pick() {
    LLM_MODEL=""; LLM_KEY=""; LLM_BASE=""
    [ -s "$LLM_CAND_JSON" ] || llm_parse_candidates "$2" >/dev/null
    [ -s "$LLM_CAND_JSON" ] || { echo "[llmrot] 无法解析候选 ($2)"; return 1; }
    local n idx i j code
    n="$("$PYBIN" -c "import json;print(len(json.load(open('$LLM_CAND_JSON'))))" 2>/dev/null)"
    [ -n "$n" ] && [ "$n" -gt 0 ] || return 1

    # 🔑 2026-10-04 运维（RUN_ID 61）：**优先 glm-5.2**（RUN_ID 49 定稿规则）。
    #   原因：某些候选（如 deepseek-v4-flash @ /v1）**curl 探针 200，但 cline 实际用会 403 Forbidden**
    #   → 环状探测可能选中它并把 base 写成 /v1，导致 loop 静默 Forbidden（.12 vision/data 刚因此中招）。
    #   glm-5.2 @ http://agi-gateway.cxmt.com/cloud/v1 实测 cline 可用。
    local gidx
    gidx="$("$PYBIN" -c "import json;c=json.load(open('$LLM_CAND_JSON'));print(next((i for i,x in enumerate(c) if x['model']=='glm-5.2'),-1))" 2>/dev/null)"
    if [ -n "${gidx:-}" ] && [ "${gidx:--1}" -ge 0 ]; then
        eval "$("$PYBIN" -c "
import json
c = json.load(open('$LLM_CAND_JSON'))[$gidx]
print(\"LLM_MODEL='%s'\" % c['model'])
print(\"LLM_KEY='%s'\" % c['key'])
print(\"LLM_BASE='%s'\" % c['base'])
" 2>/dev/null)"
        if [ -n "$LLM_MODEL" ] && [ "$(llm_probe "$LLM_MODEL" "$LLM_KEY" "$LLM_BASE")" = "200" ]; then
            echo "$gidx" > "$1" 2>/dev/null
            llm_apply_base "$LLM_BASE"
            echo "[llmrot] $(date '+%F %T') 优先选中 glm-5.2 #$gidx @ ${LLM_BASE} (probe=200)"
            return 0
        fi
    fi

    idx="$(cat "$1" 2>/dev/null)"; case "$idx" in ''|*[!0-9]*) idx=0 ;; esac
    for i in $(seq 0 $((n - 1))); do
        j=$(( (idx + i) % n ))
        eval "$("$PYBIN" -c "
import json
c = json.load(open('$LLM_CAND_JSON'))[$j]
print(\"LLM_MODEL='%s'\" % c['model'])
print(\"LLM_KEY='%s'\" % c['key'])
print(\"LLM_BASE='%s'\" % c['base'])
" 2>/dev/null)"
        [ -n "$LLM_MODEL" ] || continue
        code="$(llm_probe "$LLM_MODEL" "$LLM_KEY" "$LLM_BASE")"
        if [ "$code" = "200" ]; then
            echo "$j" > "$1" 2>/dev/null
            llm_apply_base "$LLM_BASE"
            echo "[llmrot] $(date '+%F %T') 选中 #$j ${LLM_MODEL} @ ${LLM_BASE} (probe=200)"
            return 0
        fi
        echo "[llmrot] $(date '+%F %T') #$j ${LLM_MODEL} probe=$code → 跳过"
    done
    echo "[llmrot] $(date '+%F %T') !!! 全部 $n 个候选均不可用（额度/网络/网关）"
    return 1
}
