#!/usr/bin/env bash
# run_one.sh — cline + PreToolUse hook 防泄题评测单条 runner (shard A)
#
# 流程（运维令 2026-11-02 §四）：
#   1. 部署 PreToolUse hook 到 ~/.cline/hooks/ + 写 hook_scope.txt（本批次根）
#   2. 建 workdir：只放 prompt.txt + assets/（仅合法 attachments）+ task_brief.md
#      🚫 绝不放 check.py / _check.py / reference / hidden / jsonl / test 字段
#   3. headless 跑 cline，产出 outputs/submit.zip 后退出
#   4. 独立判分（不在 cline workdir）：submit.zip + check.py + A 附件 → /tmp/judge
#   5. 记 designflow/cline_eval_status.jsonl（harness=cline）
#
# 用法：
#   run_one.sh <task_id> [model] [thinking]
#   run_one.sh EDA-Eval-DesignFlow-Verification-001 deepseek-v4-pro-cloud medium
#
# 环境变量：
#   SKIP_RUN=1   只建 workdir + 部署 hook，不跑 cline（调试用）
#   SKIP_JUDGE=1 跑完 cline 不判分
set -uo pipefail

TASK_ID="${1:?usage: run_one.sh <task_id> [model] [thinking]}"
MODEL="${2:-deepseek-v4-pro-cloud}"
THINKING="${3:-medium}"

# ---- 路径 ----
BENCH=/nasdata/app.e0031982/code/EDA-Flow-Bench
SUPER=/nasdata/app.e0031982/code/super_intelligence_2035
JSONL=$BENCH/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_A.jsonl
ASSETS_SRC=$BENCH/benchmarks/EDA-Eval-DesignFlow/assets/$TASK_ID
REF_DIR=$BENCH/benchmarks/EDA-Eval-DesignFlow/reference/$TASK_ID
HOOK_SRC=$BENCH/scripts/cline_hooks/PreToolUse

EVAL_ROOT=$SUPER/doc/ZhuLong_DAC2027/benchmark/designflow/cline_eval
WORKDIR=$EVAL_ROOT/$TASK_ID
STATUS_JSONL=$SUPER/doc/ZhuLong_DAC2027/benchmark/designflow/cline_eval_status.jsonl
JUDGE=/tmp/judge_$TASK_ID

CLINE=~/.local/bin/cline
CLINE_TIMEOUT=1500   # 秒，单 case 上限
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
DUR=""           # 跑 cline 后填
CLINE_EXIT=""    # 跑 cline 后填

log(){ echo "[run_one] $*"; }
err(){ echo "[run_one][ERROR] $*" >&2; }

# ---- 0. 前置检查 ----
[ -x "$CLINE" ] || { err "cline 不存在: $CLINE"; exit 2; }
[ -f "$JSONL"  ] || { err "jsonl 不存在: $JSONL"; exit 2; }
[ -d "$ASSETS_SRC" ] || { err "assets 目录不存在: $ASSETS_SRC"; exit 2; }
[ -f "$REF_DIR/check.py" ] || { err "reference/check.py 不存在"; exit 2; }
[ -f "$HOOK_SRC" ] || { err "hook 源不存在: $HOOK_SRC"; exit 2; }

# ---- 1. 部署 hook + scope ----
log "1. 部署 PreToolUse hook"
mkdir -p ~/.cline/hooks
cp "$HOOK_SRC" ~/.cline/hooks/PreToolUse
chmod +x ~/.cline/hooks/PreToolUse
# scope = 本批次 workdir 根；多 shard 并发部署时用 flock + append(去重),
# 避免互相覆盖 hook_scope.txt 导致 scope 外会话被放行(隔离失效)
SCOPE_LOCK=/tmp/cline_hook_scope.lock
(
  flock 9
  touch ~/.cline/hooks/hook_scope.txt
  grep -qxF "$EVAL_ROOT" ~/.cline/hooks/hook_scope.txt 2>/dev/null || \
    printf '%s\n' "$EVAL_ROOT" >> ~/.cline/hooks/hook_scope.txt
) 9>"$SCOPE_LOCK"
log "   scope += $EVAL_ROOT (multi-shard safe)"

# ---- 2. 建 workdir（防泄题核心）----
log "2. 建 workdir: $WORKDIR"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR/assets" "$WORKDIR/outputs"

# 绝不进 workdir 的文件名（判分器/答案/隐藏）
FORBIDDEN='_check.py check.py _reference_check.py reference_submit.zip reference negative hidden hidden_manifest.json'
is_forbidden(){ local f=$(basename "$1"); local b; for b in $FORBIDDEN; do [ "$f" = "$b" ] && return 0; done; return 1; }

python3 - "$TASK_ID" "$JSONL" "$ASSETS_SRC" "$WORKDIR" <<'PY'
import json, os, shutil, sys
task_id, jsonl, assets_src, workdir = sys.argv[1:5]
case = None
for line in open(jsonl):
    d = json.loads(line)
    if d.get('task_id') == task_id:
        case = d; break
assert case, f'case {task_id} not found in {jsonl}'

# prompt.txt：用户原话任务说明（trace-faithful 时不改写）
open(os.path.join(workdir, 'prompt.txt'), 'w').write(case['prompt'])

# task_brief.md：≤3 行，只写交付接口与文件位置，不写「要做什么」
# 优先用 case 专属的 assets/<task_id>/task_brief.md（含交付件清单/目录契约），
# 否则回退到通用模板。运维令 21:3x §①3 允许 task_brief 只写交付接口与文件位置。
# 根因修复：此前用通用模板覆盖了 case 专属 brief，导致 cline 看不到交付件结构契约
# → ①交付形态/④判分歧义 失败（A-faithful ①+④ 破 30% 阈值）。
brief_path = os.path.join(assets_src, 'task_brief.md')
if os.path.isfile(brief_path):
    shutil.copy(brief_path, os.path.join(workdir, 'task_brief.md'))
    print('   task_brief.md: copied from assets (case-specific deliverable manifest)')
else:
    brief = (
        "# 交付接口\n"
        f"- 工作目录：{workdir}\n"
        "- 输入：assets/ 目录下的附件\n"
        "- 交付：把要求的文件打包成 outputs/submit.zip 后停止，不要做额外的事。\n"
    )
    open(os.path.join(workdir, 'task_brief.md'), 'w').write(brief)
    print('   task_brief.md: generic template (no case-specific brief in assets/)')

# 仅复制合法 attachments（按 source 名），过滤判分器/答案/隐藏
forbidden = {'_check.py','check.py','_reference_check.py',
             'reference_submit.zip','reference','negative','hidden',
             'hidden_manifest.json'}
copied = []
for a in case.get('attachments', []):
    src = a.get('source') or a.get('name')
    name = a.get('name') or os.path.basename(src)
    if not name or name in forbidden: continue
    # source 可能是 'assets/<task_id>/<name>' 或裸 '<name>'；统一按 name 在 ASSETS_SRC 取
    def _copy(src_path, name_):
        dst = os.path.join(workdir, 'assets', name_)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src_path, dst)
        copied.append(name_)
    sp = os.path.join(assets_src, name)
    if os.path.exists(sp):
        _copy(sp, name)
    else:
        alt = os.path.join(assets_src, src)
        if os.path.exists(alt):
            _copy(alt, name)
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
  CLI_PROMPT="Read prompt.txt in the current directory. It describes a complete multi-step task. Use the files in the assets/ folder as inputs. Produce the deliverable exactly as prompt.txt specifies: write each required deliverable file directly under the outputs/ directory, preserving the EXACT internal directory structure the task names (e.g. if the task asks for tcl/pt_sta.tcl, write it to outputs/tcl/pt_sta.tcl). Do NOT zip or package anything yourself, and do NOT run any zip/tar/packaging command — the harness will package outputs/ into outputs/submit.zip for judging after you finish. When every required deliverable file has been written under outputs/, stop immediately and do not perform any further tool calls.

IMPORTANT tool usage rules (the built-in run_commands/bash/shell tools will NOT work for this task — they are sandboxed to prevent answer leakage):
- To WRITE deliverable files and to READ files already in your local workspace (assets/, prompt.txt, task_brief.md, outputs/), use the built-in write_to_file / read_file tools. These work inside the workspace. The internal directory structure under outputs/ must match what the task specifies — create subdirectories as needed (e.g. outputs/tcl/, outputs/setup/).
- All EDA and shell commands (running tools, zipping, building, simulating on the EDA server) MUST use the MCP tool 'mcp__pyAether_MCP_server__run_commands' — it executes on the EDA server (32.75) in your session workdir. The built-in run_commands runs on the local dev machine which CANNOT reach the EDA server or EDA NAS, and will only return a NOTICE telling you to switch to the MCP tool.
- To run pyAether/SKILL/Tcl code on the EDA server, use 'mcp__pyAether_MCP_server__run_code'.
- To read EDA-side files (produced on 32.75), use 'mcp__pyAether_MCP_server__read_file'. To list EDA-side dirs, use 'mcp__pyAether_MCP_server__list_files'.
- Do NOT attempt to read, list, or access any file named check.py, _check.py, reference/, or anything outside the current workspace."
  cd "$WORKDIR"
  START=$(date +%s)
  set +e
  "$CLINE" -c "$WORKDIR" -P openai -m "$MODEL" \
      --auto-approve true --json --thinking "$THINKING" \
      --timeout "$CLINE_TIMEOUT" \
      "$CLI_PROMPT" > "$WORKDIR/cline_session.jsonl" 2> "$WORKDIR/cline_stderr.log"
  CLINE_EXIT=$?
  set -e
  END=$(date +%s)
  DUR=$((END-START))
  log "   cline exit=$CLINE_EXIT dur=${DUR}s"
fi

# ---- 3b. harness 打包 outputs/ -> submit.zip（防泄题关键：cline 不能跑本地 shell
#         建包，由 run_one.sh 在 cline 退出后打包；cline 只用 write 工具写文件，
#         全程不接触 check.py/reference，判分仍独立在 /tmp/judge 跑）----
if [ ! -f "$WORKDIR/outputs/submit.zip" ]; then
  nfiles=$(find "$WORKDIR/outputs" -type f 2>/dev/null | wc -l)
  if [ "$nfiles" -gt 0 ]; then
    log "3b. harness 打包 outputs/ -> submit.zip ($nfiles 个文件，cline 未自建包)"
    ( cd "$WORKDIR/outputs" && zip -r -q submit.zip . ) || err "zip 打包失败"
  else
    log "3b. outputs/ 为空，不打包（cline 未产出任何交付件）"
  fi
fi

# ---- 4. 独立判分（不在 cline workdir）----
VERDICT="ABSENT"; REASON=""
if [ "${SKIP_JUDGE:-0}" = "1" ]; then
  log "4. SKIP_JUDGE=1，跳过判分"
else
  log "4. 独立判分: $JUDGE"
  rm -rf "$JUDGE"; mkdir -p "$JUDGE"
  if [ ! -f "$WORKDIR/outputs/submit.zip" ]; then
    VERDICT="FAIL"; REASON="no submit.zip produced (cline wrote nothing under outputs/)"
    log "   $REASON"
  else
    cp "$WORKDIR/outputs/submit.zip" "$JUDGE/"
    cp "$REF_DIR/check.py" "$JUDGE/"
    # 把合法 A 附件也复制进 judge dir（check.py 可能从 workdir 读附件）
    for a in $(python3 - "$TASK_ID" "$JSONL" <<'PY'
import json,sys,os
tid=sys.argv[1]; jl=sys.argv[2]
for line in open(jl):
    d=json.loads(line)
    if d.get('task_id')==tid:
        forbidden={'_check.py','check.py','_reference_check.py','reference_submit.zip','reference','negative','hidden','hidden_manifest.json'}
        for a in d.get('attachments',[]):
            s=a.get('source') or a.get('name')
            n=a.get('name') or (os.path.basename(s) if s else '')
            if n and n not in forbidden: print(n)
        break
PY
); do
      [ -f "$ASSETS_SRC/$a" ] && cp "$ASSETS_SRC/$a" "$JUDGE/" 2>/dev/null || true
    done
    # 复制隐藏 B 输入进 judge dir（check.py 的 cross-input guard 需要 workdir/hidden/）。
    # hidden/ 不进 SUT workdir（防泄题），但判分器在独立 judge dir 里需要它。
    # 两个可能位置：assets/<id>/hidden/ 或 reference/<id>/hidden/（按 case 而定）。
    if [ -d "$ASSETS_SRC/hidden" ]; then
      cp -r "$ASSETS_SRC/hidden" "$JUDGE/hidden" 2>/dev/null || true
    elif [ -d "$REF_DIR/hidden" ]; then
      cp -r "$REF_DIR/hidden" "$JUDGE/hidden" 2>/dev/null || true
    fi
    cd "$JUDGE"
    JUDGE_OUT=$(python3 - <<'PY'
import importlib.util, sys, os, json
spec = importlib.util.spec_from_file_location('check', 'check.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
deliverable = 'submit.zip'; workdir = '.'
try:
    r = m.check(deliverable, workdir)
    # check 返回 True/False 或 dict；统一化
    if r is True or r == True:
        print(json.dumps({'verdict':'PASS','detail':str(r)}))
    elif r is False or r == False:
        print(json.dumps({'verdict':'FAIL','detail':str(r)}))
    else:
        # dict / 其他：含 pass/ok 字段则判 PASS
        ok = False
        if isinstance(r, dict):
            ok = bool(r.get('pass') or r.get('ok') or r.get('passed'))
        print(json.dumps({'verdict':'PASS' if ok else 'FAIL','detail':str(r)}))
except Exception as e:
    print(json.dumps({'verdict':'FAIL','detail':'exception: '+repr(e)}))
PY
)
    VERDICT=$(echo "$JUDGE_OUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['verdict'])")
    REASON=$(echo "$JUDGE_OUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['detail'][:300])")
    log "   verdict=$VERDICT  detail=$REASON"
  fi
fi

# ---- 5. 记 status jsonl ----
log "5. 记 $STATUS_JSONL"
python3 - "$TASK_ID" "$TS" "$MODEL" "$THINKING" "$DUR" "$CLINE_EXIT" "$VERDICT" "$REASON" "$STATUS_JSONL" <<'PY'
import json, sys, os
task_id, ts, model, thinking, dur, cexit, verdict, reason, out = sys.argv[1:10]
rec = {
    "ts": ts,
    "task_id": task_id,
    "harness": "cline",
    "cline_version": "3.0.51",
    "model": model,
    "thinking": thinking,
    "dur_sec": int(dur) if dur else None,
    "cline_exit": int(cexit) if cexit else None,
    "verdict": verdict,
    "reason": reason,
    "hook": "PreToolUse",
    "scope": os.path.expanduser("~/.cline/hooks/hook_scope.txt"),
}
with open(out, 'a') as f:
    f.write(json.dumps(rec, ensure_ascii=False) + '\n')
print('   recorded:', json.dumps(rec, ensure_ascii=False))
PY

log "DONE  verdict=$VERDICT  ($TASK_ID)"
echo "$VERDICT"
