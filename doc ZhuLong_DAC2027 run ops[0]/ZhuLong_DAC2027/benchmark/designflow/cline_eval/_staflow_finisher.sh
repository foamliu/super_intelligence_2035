#!/usr/bin/env bash
# _staflow_finisher.sh — 接续被 shell-tool timeout 杀掉的 run_one.sh，
# 等 cline PID 退出后做 packaging + 独立判分 + 记 status（镜像 run_one.sh 3b-5）
set -uo pipefail
TASK_ID=EDA-Eval-DesignFlow-StaFlowScaffold-001
CLINE_PID=2992315
BENCH=/nasdata/app.e0031982/code/EDA-Flow-Bench
SUPER=/nasdata/app.e0031982/code/super_intelligence_2035
JSONL=$BENCH/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_A.jsonl
ASSETS_SRC=$BENCH/benchmarks/EDA-Eval-DesignFlow/assets/$TASK_ID
REF_DIR=$BENCH/benchmarks/EDA-Eval-DesignFlow/reference/$TASK_ID
EVAL_ROOT=$SUPER/doc/ZhuLong_DAC2027/benchmark/designflow/cline_eval
WORKDIR=$EVAL_ROOT/$TASK_ID
STATUS_JSONL=$SUPER/doc/ZhuLong_DAC2027/benchmark/designflow/cline_eval_status.jsonl
JUDGE=/tmp/judge_$TASK_ID
MODEL=deepseek-v4-pro-cloud; THINKING=medium
TS_START=2026-11-05T00:30:00Z   # cline 启动约 08:30 local = 00:30 UTC
log(){ echo "[finisher] $*"; }

# 1. 等 cline 退出（最多再等 50 min 兜底）
log "waiting for cline PID=$CLINE_PID to exit..."
for i in $(seq 1 3000); do
  kill -0 $CLINE_PID 2>/dev/null || break
  sleep 1
done
if kill -0 $CLINE_PID 2>/dev/null; then
  log "cline 仍存活超过 50min 兜底，强杀"
  kill -KILL $CLINE_PID 2>/dev/null; sleep 2
fi
END=$(date +%s)
# cline 启动时间戳从 proc 取
START=$(stat -c %Y /proc/$CLINE_PID 2>/dev/null || date +%s)
# 退而求其次：用 workdir cline_session.jsonl 第一行 ts
DUR=$((END - $(date -d '2026-11-05 00:30:00 UTC' +%s)))
log "cline exited. dur≈${DUR}s"

# 2. harness 打包 outputs/ -> submit.zip（若 cline 未自建包）
if [ ! -f "$WORKDIR/outputs/submit.zip" ]; then
  nfiles=$(find "$WORKDIR/outputs" -type f 2>/dev/null | wc -l)
  if [ "$nfiles" -gt 0 ]; then
    log "packaging outputs/ -> submit.zip ($nfiles files)"
    ( cd "$WORKDIR/outputs" && zip -r -q submit.zip . ) || log "zip failed"
  else
    log "outputs/ empty — no submit.zip"
  fi
fi

# 3. 独立判分
VERDICT=ABSENT; REASON=""
log "independent judge: $JUDGE"
rm -rf "$JUDGE"; mkdir -p "$JUDGE/hidden"
if [ ! -f "$WORKDIR/outputs/submit.zip" ]; then
  VERDICT=FAIL; REASON="no submit.zip produced"
else
  cp "$WORKDIR/outputs/submit.zip" "$JUDGE/"
  cp "$REF_DIR/check.py" "$JUDGE/"
  # grading-side helpers (REF_DIR 兄弟 .py/.json，排除 negative_selftest.py)
  for f in "$REF_DIR"/*.py "$REF_DIR"/*.json; do
    [ -f "$f" ] || continue; b=$(basename "$f")
    [ "$b" = "check.py" -o "$b" = "negative_selftest.py" ] && continue
    cp "$f" "$JUDGE/" 2>/dev/null || true
  done
  # A 附件（保留子目录）
  python3 - "$TASK_ID" "$JSONL" "$ASSETS_SRC" "$JUDGE" <<'PY'
import json,os,shutil,sys
tid,jl,asrc,J=sys.argv[1:5]
prefix=f'assets/{tid}/'
for line in open(jl):
    d=json.loads(line)
    if d.get('task_id')==tid:
        forb={'_check.py','check.py','_reference_check.py','reference_submit.zip','reference','negative','hidden','hidden_manifest.json'}
        for a in d.get('attachments',[]):
            s=str(a); rel=s[len(prefix):] if s.startswith(prefix) else os.path.basename(s); rel=rel.lstrip('/')
            if not rel or rel in forb or rel.split('/')[0] in forb: continue
            sp=os.path.join(asrc,rel)
            if os.path.exists(sp):
                dst=os.path.join(J,rel); os.makedirs(os.path.dirname(dst),exist_ok=True); shutil.copy(sp,dst)
        break
PY
  # hidden B（三源合并，faithful to run_one.sh cp -r）
  TOPLEVEL_HIDDEN=$BENCH/benchmarks/EDA-Eval-DesignFlow/hidden/$TASK_ID
  for hsrc in "$ASSETS_SRC/hidden" "$REF_DIR/hidden" "$TOPLEVEL_HIDDEN"; do
    [ -d "$hsrc" ] && cp -r "$hsrc/." "$JUDGE/hidden/" 2>/dev/null || true
  done
  cd "$JUDGE"
  JUDGE_OUT=$(python3 - <<'PY'
import importlib.util,sys,json
spec=importlib.util.spec_from_file_location('check','check.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
try:
    r=m.check('submit.zip','.')
    if r is True: print(json.dumps({'verdict':'PASS','detail':str(r)}))
    elif r is False: print(json.dumps({'verdict':'FAIL','detail':str(r)}))
    elif r is None: print(json.dumps({'verdict':'PASS','detail':'None (no exception, all conditions passed)'}))
    elif isinstance(r,dict):
        ok=bool(r.get('pass') or r.get('ok') or r.get('passed'))
        print(json.dumps({'verdict':'PASS' if ok else 'FAIL','detail':str(r)}))
    else: print(json.dumps({'verdict':'PASS' if r else 'FAIL','detail':str(r)}))
except Exception as e:
    print(json.dumps({'verdict':'FAIL','detail':'exception: '+repr(e)}))
PY
)
  VERDICT=$(echo "$JUDGE_OUT" | python3 -c "import json,sys;print(json.load(sys.stdin)['verdict'])")
  REASON=$(echo "$JUDGE_OUT" | python3 -c "import json,sys;print(json.load(sys.stdin)['detail'][:300])")
fi
log "verdict=$VERDICT detail=$REASON"

# 4. 记 status jsonl
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
python3 - "$TASK_ID" "$TS" "$MODEL" "$THINKING" "$DUR" "$VERDICT" "$REASON" "$STATUS_JSONL" <<'PY'
import json,sys,os
tid,ts,model,think,dur,verdict,reason,out=sys.argv[1:8]
rec={"ts":ts,"task_id":tid,"harness":"cline","cline_version":"3.0.51","model":model,
     "thinking":think,"dur_sec":int(dur) if dur else None,"cline_exit":None,
     "verdict":verdict,"reason":reason,"hook":"PreToolUse",
     "scope":os.path.expanduser("~/.cline/hooks/hook_scope.txt")}
open(out,'a').write(json.dumps(rec,ensure_ascii=False)+'\n')
print('recorded:',json.dumps(rec,ensure_ascii=False))
PY
log "DONE verdict=$VERDICT ($TASK_ID)"
echo "$VERDICT"
