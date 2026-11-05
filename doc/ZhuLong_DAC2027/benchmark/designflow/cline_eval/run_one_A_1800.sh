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
CLINE_TIMEOUT=1800   # 秒，单 case 上限（30min；覆盖正常 PASS 多在 ~1300s 内）
# 🚨 r120 harness bug 修复：cline 自带 `--timeout` 在 v3.0.51 不可靠
#   （r118 QualibTimingFix-001 设 1800s 实际跑了 2283s 才被外层 session 超时杀掉）。
#   → 用 coreutils `timeout -s KILL` 在 OS 层硬杀，确保不超时。
#   timeout 触发 → exit 137 (128+SIGKILL)，记 cline_exit=137 + reason 标 TIMEOUT。
STALLED_KILL=780   # 秒，cline 连续 ~13min 无新 tool_call 主动 KILL（r120 first-step 铁律）
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
DUR=""           # 跑 cline 后填
CLINE_EXIT=""    # 跑 cline 后填
TIMEOUT_HIT=0    # 1 = OS timeout 触发；0 = 正常退出
STALL_HIT=0      # 1 = stalled-killer 触发；0 = 否

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
if [ "${SKIP_RUN:-0}" = "1" ] && [ -d "$WORKDIR/outputs" ]; then
  log "   SKIP_RUN=1 且 workdir 已存在 → 保留 workdir（用于复判已存 submit.zip），仅重建 assets/prompt/brief"
  rm -rf "$WORKDIR/assets" "$WORKDIR/prompt.txt" "$WORKDIR/task_brief.md"
else
  rm -rf "$WORKDIR"
fi
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
    if d.get('task_id') == task_id or d.get('id') == task_id:
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

# 仅复制合法 attachments，保留 assets/<task_id>/ 下的相对子目录结构
# （修复 r80：此前用 basename 抹平子目录，导致 lib/lib_A.lib 这类嵌套附件
#   在 ASSETS_SRC/lib_A.lib 找不到 → cline 拿不到输入文件 → 假 FAIL）
forbidden = {'_check.py','check.py','_reference_check.py',
             'reference_submit.zip','reference','negative','hidden',
             'hidden_manifest.json'}
copied = []
# assets_src 末尾形如 .../assets/<task_id>；prefix = 'assets/<task_id>/'
_prefix = f'assets/{task_id}/'
for a in case.get('attachments', []):
    # attachments 可能是 list[str]（如 'assets/<id>/<sub>/<name>'）或 list[dict]
    # dict 可能含 'source'(全路径) / 'path'(全路径,有时带子目录) / 'name'(裸文件名).
    # 修复 r123：此前仅读 source/name → 当附件放在 assets/<id>/<sub>/ 子目录时
    #   （如 itf/01.itf），name=basename 丢了 <sub>/，workdir 拿不到输入文件 →
    #   cline 空转 1800s 假 FAIL（ItfCompare-001 实证）。现在优先读 path/source 全路径
    #   以保留子目录结构，name 仅作 basename 回退。
    if isinstance(a, dict):
        src = a.get('source') or a.get('path') or a.get('name') or ''
        name = a.get('name') or (os.path.basename(src) if src else '')
    else:
        src = str(a) if a is not None else ''
        name = os.path.basename(src) if src else ''
    if not name or name in forbidden: continue
    # 推导 assets_src 内的相对路径：剥掉 'assets/<task_id>/' 前缀，否则用裸 name
    rel = src[len(_prefix):] if src.startswith(_prefix) else name
    rel = rel.lstrip('/')
    # 绝对不允许 rel 落进 forbidden 顶层名（hidden/ 等）
    if rel in forbidden or rel.split('/')[0] in forbidden: continue
    def _copy(src_path, rel_):
        dst = os.path.join(workdir, 'assets', rel_)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src_path, dst)
        copied.append(rel_)
    sp = os.path.join(assets_src, rel)
    if os.path.exists(sp):
        _copy(sp, rel)
    else:
        # 回退 1：按裸 name（旧 case 无子目录）
        alt = os.path.join(assets_src, name)
        if os.path.exists(alt) and os.path.basename(alt) not in forbidden:
            _copy(alt, name)
        else:
            # 回退 2：path 字段可能是 assets/<id>/<sub>/<name> 但磁盘上 flat；
            #   或 dict 只给了 name + path 指向别处。递归找 basename 匹配。
            hit = None
            for root, _, files in os.walk(assets_src):
                if name in files and os.path.basename(root) not in forbidden:
                    hit = os.path.join(root, name); break
            if hit:
                # 保留 assets_src 内的相对子目录（若 path 给了 <sub>/）
                sub = rel if '/' in rel else name
                _copy(hit, sub)
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
- First call 'eda_flow__open_session' to get a remote session workdir on the EDA server (32.75). Pass that workdir to all subsequent eda_flow calls.
- All EDA and shell commands (running tools, building, simulating, running python scripts on the EDA server) MUST use the MCP tool 'eda_flow__run_commands' (pass the workdir from open_session). It executes on the EDA server (32.75) which has python3, EDA tools, and the session workdir. The built-in run_commands runs on the local dev machine which CANNOT reach the EDA server or EDA NAS, and will only return a NOTICE telling you to switch to the MCP tool.
- To run pyAether/SKILL/Tcl code on the EDA server, use 'eda_flow__run_code' (pass workdir).
- To read EDA-side files (produced on 32.75), use 'eda_flow__read_file'. To list EDA-side dirs, use 'eda_flow__list_files'.
- To upload assets from local workspace to the EDA session workdir: read locally with read_file, then write with 'eda_flow__write_file' (pass workdir + path).
- Do NOT attempt to read, list, or access any file named check.py, _check.py, reference/, or anything outside the current workspace."
  cd "$WORKDIR"
  START=$(date +%s)
  set +e
  # r120 修复：cline `--timeout` v3.0.51 不可靠（r118 跑 2283s 才被外层杀）。
  # 方案：cline 直接作为 `timeout -s KILL` 的子进程前台跑（OS 层硬兜底）；
  # 同时启动 stalled-killer 后台 watcher：监控 cline_session.jsonl 文件大小，
  # 若连续 $STALLED_KILL 秒无增长 → kill cline pid（防 thrash 卡死）。
  CLINE_PIDFILE=$WORKDIR/.cline.pid
  STALL_LOG=$WORKDIR/.stall_killer.log
  rm -f "$WORKDIR/.stall_hit"
  # 后台 stalled-killer
  (
    last_grow_ts=$START
    last_seen_size=0
    while true; do
      sleep 30
      [ -f "$CLINE_PIDFILE" ] || break
      pid=$(cat "$CLINE_PIDFILE" 2>/dev/null) || break
      kill -0 "$pid" 2>/dev/null || break
      now=$(date +%s)
      sz=$(stat -c%s "$WORKDIR/cline_session.jsonl" 2>/dev/null || echo 0)
      if [ "$sz" != "$last_seen_size" ]; then
        last_grow_ts=$now
        last_seen_size=$sz
      fi
      idle=$((now - last_grow_ts))
      if [ "$idle" -ge "$STALLED_KILL" ]; then
        echo "[stall-killer] no output growth ${idle}s >= ${STALLED_KILL}s → KILL cline pid $pid" >> "$STALL_LOG"
        kill -9 "$pid" 2>/dev/null || true
        echo "STALL_HIT=1" > "$WORKDIR/.stall_hit"
        break
      fi
    done
  ) &
  STALLER_PID=$!
  # cline 直接前台跑，`timeout -s KILL` 为其父进程，到点必杀
  timeout -s KILL "$CLINE_TIMEOUT" \
      "$CLINE" -c "$WORKDIR" -P openai -m "$MODEL" \
      --auto-approve true --json --thinking "$THINKING" \
      --timeout "$CLINE_TIMEOUT" \
      "$CLI_PROMPT" > "$WORKDIR/cline_session.jsonl" 2> "$WORKDIR/cline_stderr.log" &
  CLINE_PID=$!
  echo "$CLINE_PID" > "$CLINE_PIDFILE"
  wait "$CLINE_PID"
  CLINE_EXIT=$?
  rm -f "$CLINE_PIDFILE"
  kill "$STALLER_PID" 2>/dev/null || true
  wait "$STALLER_PID" 2>/dev/null || true
  [ -f "$WORKDIR/.stall_hit" ] && STALL_HIT=1 || STALL_HIT=0
  # 137 = SIGKILL by OS timeout；若 stall-killer 先杀则 cline 也以 137 退出，靠 STALL_HIT 区分
  if [ "$CLINE_EXIT" -eq 137 ] && [ "$STALL_HIT" = "0" ]; then
    TIMEOUT_HIT=1
  fi
  set -e
  END=$(date +%s)
  DUR=$((END-START))
  log "   cline exit=$CLINE_EXIT dur=${DUR}s timeout_hit=$TIMEOUT_HIT stall_hit=$STALL_HIT"
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
    # 复制 check.py 在 REF_DIR 内引用的判分侧辅助文件（grading-side helpers）：
    # 若干 case 的 check.py 经 REF_DIR=os.path.dirname(check.py) 找兄弟文件
    # (build_fixture.py / reference_submit.zip / mock_*.py / gold_*.py / fixture_*.json 等)。
    # 不复制会导致独立 judge dir 缺依赖 → CalledProcessError / FileNotFoundError
    # （非候选失败，是 judge-env 缺失 = harness bug）。下面白名单复制（排除 negative/）。
    for h in build_fixture.py reference_submit.zip mock_pyAether.py \
             gold_find_pcells.py fixture_A.json fixture_B.json; do
      [ -f "$REF_DIR/$h" ] && cp "$REF_DIR/$h" "$JUDGE/" 2>/dev/null || true
    done
    # 兜底：把 REF_DIR 内所有 .py / .json 兄弟文件复制（除 check.py 已复制 / negative 目录），
    # 覆盖未来新增的 grading-side helper，避免再漏。
    for f in "$REF_DIR"/*.py "$REF_DIR"/*.json; do
      [ -f "$f" ] || continue
      b=$(basename "$f")
      [ "$b" = "check.py" ] && continue
      [ "$b" = "negative_selftest.py" ] && continue
      [ -f "$JUDGE/$b" ] || cp "$f" "$JUDGE/" 2>/dev/null || true
    done
    # 把合法 A 附件也复制进 judge dir（保留子目录结构，r80 修复）
    # check.py 可能从 workdir 读附件（如 lib/lib_A.lib），需要 relpath 一致
    for a in $(python3 - "$TASK_ID" "$JSONL" <<'PY'
import json,sys,os
tid=sys.argv[1]; jl=sys.argv[2]
_prefix=f'assets/{tid}/'
for line in open(jl):
    d=json.loads(line)
    if d.get('task_id')==tid or d.get('id')==tid:
        forbidden={'_check.py','check.py','_reference_check.py','reference_submit.zip','reference','negative','hidden','hidden_manifest.json'}
        for a in d.get('attachments',[]):
            if isinstance(a, dict):
                s=a.get('source') or a.get('path') or a.get('name') or ''
                n=a.get('name') or (os.path.basename(s) if s else '')
            else:
                s=str(a) if a is not None else ''
                n=os.path.basename(s) if s else ''
            if not n or n in forbidden: continue
            rel=s[len(_prefix):] if s.startswith(_prefix) else n
            rel=rel.lstrip('/')
            if rel in forbidden or rel.split('/')[0] in forbidden: continue
            print(rel)
        break
PY
); do
      if [ -f "$ASSETS_SRC/$a" ]; then
        mkdir -p "$JUDGE/$(dirname "$a")"
        cp "$ASSETS_SRC/$a" "$JUDGE/$a" 2>/dev/null || true
      fi
    done
    # 复制隐藏 B 输入进 judge dir（check.py 的 cross-input guard 需要 workdir/hidden/）。
    # hidden/ 不进 SUT workdir（防泄题），但判分器在独立 judge dir 里需要它。
    # judge-env bug 修复（r77 audit）：hidden B 可能存在于三个位置之一（按 case 而定），
    # 全部尝试并合并进 $JUDGE/hidden/，避免 run_one.sh 漏拷导致 FileNotFoundError 假 FAIL：
    #   1. assets/<id>/hidden/      （标准位置，多数 case）
    #   2. reference/<id>/hidden/   （少数 case 把 hidden 放在 reference 侧）
    #   3. benchmarks/.../hidden/<id>/  （顶层共享 hidden/，LibArcExtract/StarRCFlow 等 7 case）
    # 用 cp -r <src>/. 合并（不覆盖已有文件），三源都缺则 $JUDGE/hidden 不存在 →
    # check.py 须自行 _resolve 回退到 repo 路径（见各 case check.py 的 _resolve_*）。
    mkdir -p "$JUDGE/hidden"
    TOPLEVEL_HIDDEN=$BENCH/benchmarks/EDA-Eval-DesignFlow/hidden/$TASK_ID
    for hsrc in "$ASSETS_SRC/hidden" "$REF_DIR/hidden" "$TOPLEVEL_HIDDEN"; do
      if [ -d "$hsrc" ]; then
        cp -r "$hsrc/." "$JUDGE/hidden/" 2>/dev/null || true
      fi
    done
    # r121 judge-env fix：复制 check.py 在 REF_DIR 内引用的判分侧 fixture 数据目录
    # （fixture_A/ fixture_B/ 等）。若干 case 的 check.py 用 HERE/fixture_A 解析候选
    # 真跑所需的输入数据；run_one.sh 独立 judge dir 不复制 → FileNotFoundError 假 FAIL
    # （BLOCKER ⑤ 同类）。仅复制 reference/<id>/ 下名为 fixture_* 的目录（白名单）。
    for fdir in "$REF_DIR"/fixture_*; do
      [ -d "$fdir" ] || continue
      b=$(basename "$fdir")
      [ -d "$JUDGE/$b" ] || cp -r "$fdir" "$JUDGE/$b" 2>/dev/null || true
    done
    cd "$JUDGE"
    JUDGE_OUT=$(python3 - <<'PY'
import importlib.util, sys, os, json
spec = importlib.util.spec_from_file_location('check', 'check.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
deliverable = 'submit.zip'; workdir = '.'
try:
    r = m.check(deliverable, workdir)
    # check 约定有三种，统一化：
    #   (a) 抛 AssertionError/异常 -> FAIL（见 except 分支）
    #   (b) 显式返回 True  -> PASS；显式返回 False -> FAIL
    #   (c) 返回 None（无显式 return，仅靠 _fail raise 标 FAIL）-> PASS
    #   (d) 返回 dict：含 pass/ok/passed=True 字段 -> PASS，否则 FAIL
    if r is True:
        print(json.dumps({'verdict':'PASS','detail':str(r)}))
    elif r is False:
        print(json.dumps({'verdict':'FAIL','detail':str(r)}))
    elif r is None:
        # 无异常 + 无显式 False = 全部条件通过
        print(json.dumps({'verdict':'PASS','detail':'None (no exception, all conditions passed)'}))
    elif isinstance(r, dict):
        ok = bool(r.get('pass') or r.get('ok') or r.get('passed'))
        print(json.dumps({'verdict':'PASS' if ok else 'FAIL','detail':str(r)}))
    else:
        # 其它真值（非空 str/list 等）按真值判定
        print(json.dumps({'verdict':'PASS' if r else 'FAIL','detail':str(r)}))
except Exception as e:
    print(json.dumps({'verdict':'FAIL','detail':'exception: '+repr(e)}))
PY
)
    VERDICT=$(echo "$JUDGE_OUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['verdict'])")
    REASON=$(echo "$JUDGE_OUT" | python3 -c "import json,sys; print(json.load(sys.stdin)['detail'][:300])")
    log "   verdict=$VERDICT  detail=$REASON"
  fi
fi

# r120：把 timeout/stall 信号并入 reason（判分侧不会感知 OS kill，需显式标注）
if [ "$TIMEOUT_HIT" = "1" ]; then
  REASON="${REASON} | [HARNESS] OS timeout -s KILL hit @ ${CLINE_TIMEOUT}s (cline --timeout unreliable)"
elif [ "$STALL_HIT" = "1" ]; then
  REASON="${REASON} | [HARNESS] stalled-killer hit @ ${STALLED_KILL}s-no-activity (cline thrash)"
fi

# ---- 5. 记 status jsonl ----
log "5. 记 $STATUS_JSONL"
python3 - "$TASK_ID" "$TS" "$MODEL" "$THINKING" "$DUR" "$CLINE_EXIT" "$VERDICT" "$REASON" "$STATUS_JSONL" "$TIMEOUT_HIT" "$STALL_HIT" <<'PY'
import json, sys, os
task_id, ts, model, thinking, dur, cexit, verdict, reason, out, to_hit, st_hit = sys.argv[1:12]
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
    "os_timeout_hit": int(to_hit),
    "stalled_kill_hit": int(st_hit),
}
with open(out, 'a') as f:
    f.write(json.dumps(rec, ensure_ascii=False) + '\n')
print('   recorded:', json.dumps(rec, ensure_ascii=False))
PY

log "DONE  verdict=$VERDICT  ($TASK_ID)"
echo "$VERDICT"
