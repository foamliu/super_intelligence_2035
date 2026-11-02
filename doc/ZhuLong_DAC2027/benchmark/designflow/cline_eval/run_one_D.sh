#!/usr/bin/env bash
# run_one_D.sh — cline + PreToolUse hook 防泄题评测单条 runner (shard D)
#
# 与 designflow/cline_eval/run_one.sh（shard A 共用）的区别：
#   - 读 EDA-Eval-DesignFlow_D.jsonl（shard D 专用，🚫 不碰主/A/B/C jsonl）
#   - workdir 落 /nasdata/.cache/cline_eval（非 git scratch，避免 in-repo workdir 泄漏风险；
#     scope 只锁本 shard 评测会话，不影响仓库内其他 cline 会话）
#   - provider=openai-compatible（smoke 实测可用；shard A 用 openai）
#   - 每次 run 用时间戳子目录，支持重跑（shard A 用固定目录，重跑覆盖）
#   - status 落 designflow/cline_eval_status.jsonl（与 shard A 共享；harness=cline，task_id 自带 case 标识）
#
# 流程（运维令 2026-11-02 §四「换被测 cline」）：
#   1. 部署 PreToolUse hook 到 ~/.cline/hooks/ + 写 hook_scope.txt（本 shard workdir 根）
#   2. 建 workdir：只放 prompt.txt + assets/（仅合法 attachments A）+ task_brief.md
#      🚫 绝不放 check.py / _check.py / reference / hidden / hidden_manifest.json / jsonl / test
#   3. headless 跑 cline → 产出 outputs/submit.zip 后退出
#   4. 独立判分（不在 cline workdir）：submit.zip + check.py + hidden B → scratch judge dir
#   5. 追加 designflow/cline_eval_status.jsonl（harness=cline）
#
# 用法：
#   run_one_D.sh <task_id> [cline_timeout_sec]
#   run_one_D.sh EDA-Eval-DesignFlow-Schematic-001 1500
#   SKIP_RUN=1 run_one_D.sh <task_id>     # 只建 workdir + 部署 hook，不跑 cline（调试）
#   SKIP_JUDGE=1 run_one_D.sh <task_id>   # 跑完不判分
set -uo pipefail

TASK_ID="${1:?usage: run_one_D.sh <task_id> [cline_timeout_sec]}"
CLINE_TIMEOUT="${2:-1500}"

# ---- 路径 ----
BENCH=/nasdata/app.e0031982/code/EDA-Flow-Bench
SUPER=/nasdata/app.e0031982/code/super_intelligence_2035
JSONL=$BENCH/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_D.jsonl   # shard D 专用
ASSETS_SRC=$BENCH/benchmarks/EDA-Eval-DesignFlow/assets/$TASK_ID
REF_DIR=$BENCH/benchmarks/EDA-Eval-DesignFlow/reference/$TASK_ID
HOOK_SRC=$BENCH/scripts/cline_hooks/PreToolUse

STATUS_JSONL=$SUPER/doc/ZhuLong_DAC2027/benchmark/designflow/cline_eval_status.jsonl

# workdir 根 = 非 git scratch（/nasdata/.cache，realpath 干净、可写、非 git 仓库）
WORKDIR_ROOT=/nasdata/app.e0031982/.cache/cline_eval
TS=$(date +%Y%m%d_%H%M%S)
WORKDIR=$WORKDIR_ROOT/$TASK_ID/$TS
JUDGE=/nasdata/app.e0031982/.cache/judge_${TASK_ID}_${TS}_$$

CLINE=~/.local/bin/cline
MODEL=deepseek-v4-pro-cloud
THINKING=medium
PROVIDER=openai-compatible
REC_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
DUR=""; CLINE_EXIT=""

log(){ echo "[run_one_D] $*"; }
err(){ echo "[run_one_D][ERROR] $*" >&2; }

# ---- 0. 前置检查 ----
[ -x "$CLINE" ] || { err "cline 不存在: $CLINE"; exit 2; }
[ -f "$JSONL"  ] || { err "shard D jsonl 不存在: $JSONL"; exit 2; }
[ -d "$ASSETS_SRC" ] || { err "assets 目录不存在: $ASSETS_SRC"; exit 2; }
[ -f "$REF_DIR/check.py" ] || { err "reference/check.py 不存在: $REF_DIR/check.py"; exit 2; }
[ -f "$HOOK_SRC" ] || { err "hook 源不存在: $HOOK_SRC"; exit 2; }

# ---- 1. 部署 hook + scope ----
log "1. 部署 PreToolUse hook (scope+=$WORKDIR_ROOT)"
mkdir -p ~/.cline/hooks
cp "$HOOK_SRC" ~/.cline/hooks/PreToolUse
chmod +x ~/.cline/hooks/PreToolUse
# scope = 本 shard workdir 根；多 shard 并发部署时用 flock + append(去重),
# 避免互相覆盖 hook_scope.txt 导致 scope 外会话被放行(隔离失效)
SCOPE_LOCK=/tmp/cline_hook_scope.lock
(
  flock 9
  touch ~/.cline/hooks/hook_scope.txt
  grep -qxF "$WORKDIR_ROOT" ~/.cline/hooks/hook_scope.txt 2>/dev/null || \
    printf '%s\n' "$WORKDIR_ROOT" >> ~/.cline/hooks/hook_scope.txt
) 9>"$SCOPE_LOCK"

# ---- 2. 建 workdir（防泄题核心）----
log "2. 建 workdir: $WORKDIR"
mkdir -p "$WORKDIR/assets" "$WORKDIR/outputs"

# 绝不进 workdir 的文件名（判分器/答案/隐藏输入 B）
FORBIDDEN='_check.py check.py _reference_check.py reference_submit.zip reference negative hidden hidden_manifest.json'
is_forbidden(){ local f=$(basename "$1"); local b; for b in $FORBIDDEN; do [ "$f" = "$b" ] && return 0; done; return 1; }

python3 - "$TASK_ID" "$JSONL" "$ASSETS_SRC" "$WORKDIR" <<'PY'
import json, os, shutil, sys
task_id, jsonl, assets_src, workdir = sys.argv[1:5]
case = None
for line in open(jsonl):
    line = line.strip()
    if not line: continue
    d = json.loads(line)
    if d.get('task_id') == task_id:
        case = d; break
assert case, f'case {task_id} not found in {jsonl}'

# prompt.txt：用户原话任务说明（trace-faithful 时不改写）
open(os.path.join(workdir, 'prompt.txt'), 'w').write(case['prompt'])

# task_brief.md：≤3 行，只写交付接口与文件位置，不写「要做什么」
brief = (
    "# 交付接口\n"
    f"- 工作目录：{workdir}\n"
    "- 输入：assets/ 目录下的附件\n"
    "- 交付：把要求的文件打包成 outputs/submit.zip 后停止，不要做额外的事。\n"
)
open(os.path.join(workdir, 'task_brief.md'), 'w').write(brief)

# 仅复制合法 attachments A（按 source 名），过滤判分器/答案/隐藏 B
forbidden = {'_check.py','check.py','_reference_check.py',
             'reference_submit.zip','reference','negative','hidden',
             'hidden_manifest.json'}
copied = []
for a in case.get('attachments', []):
    src = a.get('source') or a.get('name')
    if not src or src in forbidden: continue
    # 双重防御：路径里带 hidden/ 的也跳过
    if src.startswith('hidden/') or '/hidden/' in src:
        continue
    sp = os.path.join(assets_src, src)
    if os.path.exists(sp):
        dst = os.path.join(workdir, 'assets', src)
        os.makedirs(os.path.dirname(dst), exist_ok=True) if os.path.dirname(src) else None
        shutil.copy(sp, dst)
        copied.append(src)
# 防御：扫描 workdir 确认无泄漏
leak = []
for root, _, files in os.walk(workdir):
    for f in files:
        if f in forbidden:
            leak.append(os.path.join(root, f))
assert not leak, f'LEAK 检测到判分器/答案文件进入 workdir: {leak}'
print(f'   attachments copied: {copied}')
print(f'   workdir clean (no check.py/reference/hidden)')
PY

# 泄漏隔离自检（再确认一遍）
LEAK_HIT=$(find "$WORKDIR" \( -name '_check.py' -o -name 'check.py' -o -name '_reference_check.py' \
           -o -name 'reference_submit.zip' -o -name 'hidden_manifest.json' \) -print)
if [ -n "$LEAK_HIT" ]; then
  err "LEAK: 判分器/答案文件进了 workdir:"; echo "$LEAK_HIT" >&2; exit 3
fi
log "   workdir leak 自检通过"

# ---- 3. headless 跑 cline ----
if [ "${SKIP_RUN:-0}" = "1" ]; then
  log "3. SKIP_RUN=1，跳过 cline 执行"
else
  log "3. 跑 cline (model=$MODEL thinking=$THINKING timeout=${CLINE_TIMEOUT}s)"
  CLI_PROMPT="Read prompt.txt in the current directory. It describes a complete multi-step task. Use the files in the assets/ folder as inputs. Produce the deliverable exactly as prompt.txt specifies: package the required files into outputs/submit.zip. When outputs/submit.zip exists, stop immediately and do not perform any further tool calls.

IMPORTANT tool usage rules (the built-in run_commands/bash/shell tools will NOT work for this task):
- All EDA and shell commands MUST use the MCP tool 'mcp__pyAether_MCP_server__run_commands' — it executes on the EDA server (32.75) in your session workdir. The built-in run_commands runs on the local dev machine which CANNOT reach the EDA server or EDA NAS, and will only return a NOTICE telling you to switch to the MCP tool.
- To run pyAether/SKILL/Tcl code on the EDA server, use 'mcp__pyAether_MCP_server__run_code'.
- To read EDA-side files (produced on 32.75), use 'mcp__pyAether_MCP_server__read_file'. To list EDA-side dirs, use 'mcp__pyAether_MCP_server__list_files'.
- To read files already in your local workspace (assets/, prompt.txt, task_brief.md), use the built-in read_file tool.
- Do NOT attempt to read, list, or access any file named check.py, _check.py, reference/, hidden/, or anything outside the current workspace."
  # 解析 api key（providers.json openai-compatible）
  API_KEY=$(python3 - <<'PY'
import json
try:
    d = json.load(open('/home/app.e0031982/.cline/data/settings/providers.json'))
    print(d['providers']['openai-compatible']['settings']['apiKey'])
except Exception:
    pass
PY
)
  [ -n "$API_KEY" ] || { err "no api key resolved from providers.json"; exit 4; }
  cd "$WORKDIR"
  START=$(date +%s)
  set +e
  timeout "$CLINE_TIMEOUT" "$CLINE" -c "$WORKDIR" -P "$PROVIDER" -m "$MODEL" -k "$API_KEY" \
      --auto-approve true --json --thinking "$THINKING" \
      "$CLI_PROMPT" > "$WORKDIR/cline_session.jsonl" 2> "$WORKDIR/cline_stderr.log"
  CLINE_EXIT=$?
  set -e
  END=$(date +%s)
  DUR=$((END-START))
  log "   cline exit=$CLINE_EXIT dur=${DUR}s"
fi

# ---- 4. 独立判分（不在 cline workdir）----
VERDICT="ABSENT"; REASON=""
if [ "${SKIP_JUDGE:-0}" = "1" ]; then
  log "4. SKIP_JUDGE=1，跳过判分"
else
  log "4. 独立判分: $JUDGE"
  rm -rf "$JUDGE"; mkdir -p "$JUDGE/hidden"
  if [ ! -f "$WORKDIR/outputs/submit.zip" ]; then
    VERDICT="FAIL"; REASON="no submit.zip produced"
    log "   $REASON"
  else
    cp "$WORKDIR/outputs/submit.zip" "$JUDGE/submit.zip"
    cp "$REF_DIR/check.py" "$JUDGE/check.py"
    # 隐藏输入 B 复制到 judge dir（check.py 多通过 workdir-walk / BENCH_HIDDEN_B 发现）
    if [ -d "$ASSETS_SRC/hidden" ]; then
      cp -r "$ASSETS_SRC/hidden/." "$JUDGE/hidden/" 2>/dev/null || true
    fi
    # 合法 A 附件也复制进 judge dir（check.py 可能从 workdir 读附件）
    for a in $(python3 - "$TASK_ID" "$JSONL" <<'PY'
import json,sys
tid=sys.argv[1]; jl=sys.argv[2]
forbidden={'_check.py','check.py','_reference_check.py','reference_submit.zip','reference','negative','hidden','hidden_manifest.json'}
for line in open(jl):
    line=line.strip()
    if not line: continue
    d=json.loads(line)
    if d.get('task_id')==tid:
        for a in d.get('attachments',[]):
            s=a.get('source') or a.get('name')
            if s and s not in forbidden and not s.startswith('hidden/'):
                print(s)
        break
PY
); do
      [ -f "$ASSETS_SRC/$a" ] && cp "$ASSETS_SRC/$a" "$JUDGE/" 2>/dev/null || true
    done
    cd "$JUDGE"
    JUDGE_OUT=$(BENCH_HIDDEN_B="$JUDGE/hidden/hidden_netlist.v" python3 - <<'PY'
import importlib.util, sys, os, json
spec = importlib.util.spec_from_file_location('check', 'check.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
deliverable = 'submit.zip'; workdir = '.'
try:
    r = m.check(deliverable, workdir)
    if r is True or r == True:
        print(json.dumps({'verdict':'PASS','detail':str(r)}))
    elif r is False or r == False:
        print(json.dumps({'verdict':'FAIL','detail':str(r)}))
    else:
        ok = False
        if isinstance(r, dict):
            ok = bool(r.get('pass') or r.get('ok') or r.get('passed'))
        print(json.dumps({'verdict':'PASS' if ok else 'FAIL','detail':str(r)}))
except Exception as e:
    print(json.dumps({'verdict':'FAIL','detail':'exception: '+repr(e)[:400]}))
PY
)
    VERDICT=$(echo "$JUDGE_OUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['verdict'])")
    REASON=$(echo "$JUDGE_OUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['detail'][:300])")
    log "   verdict=$VERDICT  detail=$REASON"
  fi
fi

# hook 拦截统计（cline session 里 ACCESS RESTRICTED 出现次数）
HOOK_BLOCKS=0
[ -f "$WORKDIR/cline_session.jsonl" ] && HOOK_BLOCKS=$(grep -c "ACCESS RESTRICTED" "$WORKDIR/cline_session.jsonl" 2>/dev/null || echo 0)

# ---- 5. 记 status jsonl ----
log "5. 记 $STATUS_JSONL"
python3 - "$TASK_ID" "$REC_TS" "$MODEL" "$THINKING" "$DUR" "$CLINE_EXIT" "$VERDICT" "$REASON" "$STATUS_JSONL" "$WORKDIR" "$JUDGE" "$HOOK_BLOCKS" <<'PY'
import json, sys, os
(task_id, ts, model, thinking, dur, cexit, verdict, reason,
 out, workdir, judge, blocks) = sys.argv[1:13]
rec = {
    "ts": ts,
    "task_id": task_id,
    "shard": "D",
    "harness": "cline",
    "cline_version": "3.0.51",
    "model": model,
    "thinking": thinking,
    "dur_sec": int(dur) if dur else None,
    "cline_exit": int(cexit) if cexit else None,
    "verdict": verdict,
    "reason": reason,
    "hook": "PreToolUse",
    "hook_blocks": int(blocks),
    "scope": "/nasdata/app.e0031982/.cache/cline_eval",
    "workdir": workdir,
    "judge_dir": judge,
}
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'a') as f:
    f.write(json.dumps(rec, ensure_ascii=False) + '\n')
print('   recorded:', json.dumps(rec, ensure_ascii=False))
PY

log "DONE  verdict=$VERDICT  ($TASK_ID)"
echo "$VERDICT"
