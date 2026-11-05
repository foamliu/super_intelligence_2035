#!/usr/bin/env bash
# Wait for an orphaned cline run to finish, then package + judge + record status.
# Usage: _wait_and_finish_B.sh <task_id> <cline_pid>
set -uo pipefail
TASK_ID="${1:?task_id}"
CLINE_PID="${2:?cline pid}"

BENCH=/nasdata/app.e0031982/code/EDA-Flow-Bench
SUPER=/nasdata/app.e0031982/code/super_intelligence_2035
JSONL=$BENCH/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_B.jsonl
ASSETS_SRC=$BENCH/benchmarks/EDA-Eval-DesignFlow/assets/$TASK_ID
REF_DIR=$BENCH/benchmarks/EDA-Eval-DesignFlow/reference/$TASK_ID
EVAL_ROOT=$SUPER/doc/ZhuLong_DAC2027/benchmark/designflow/cline_eval
WORKDIR=$EVAL_ROOT/$TASK_ID
STATUS_JSONL=$SUPER/doc/ZhuLong_DAC2027/benchmark/designflow/cline_eval_status.jsonl
JUDGE=/tmp/judge_$TASK_ID

log(){ echo "[finish_B] $*"; }

# 1. wait for cline to exit (poll pid; hard cap 2500s)
log "waiting for cline pid=$CLINE_PID (workdir=$WORKDIR)"
WAITED=0
while kill -0 "$CLINE_PID" 2>/dev/null; do
  sleep 10; WAITED=$((WAITED+10))
  if [ $WAITED -ge 2500 ]; then log "WARN: wait cap hit, killing cline"; kill -TERM "$CLINE_PID" 2>/dev/null; sleep 5; kill -KILL "$CLINE_PID" 2>/dev/null; break; fi
done
log "cline exited after ~${WAITED}s"

# reconstruct dur from session log first/last ts
DUR=$(python3 - "$WORKDIR/cline_session.jsonl" <<'PY'
import json,sys
try:
    ts=[json.loads(l)['ts'] for l in open(sys.argv[1]) if l.strip() and '"ts"' in l]
    if len(ts)>=2:
        from datetime import datetime
        t0=datetime.fromisoformat(ts[0].replace('Z','+00:00'))
        t1=datetime.fromisoformat(ts[-1].replace('Z','+00:00'))
        print(int((t1-t0).total_seconds()))
    else: print(0)
except Exception as e: print(0)
PY
)
CLINE_EXIT=0
log "reconstructed dur=${DUR}s"

# 2. harness packages outputs/ -> submit.zip if cline didn't
if [ ! -f "$WORKDIR/outputs/submit.zip" ]; then
  nfiles=$(find "$WORKDIR/outputs" -type f 2>/dev/null | wc -l)
  if [ "$nfiles" -gt 0 ]; then
    log "packaging outputs/ -> submit.zip ($nfiles files)"
    ( cd "$WORKDIR/outputs" && zip -r -q submit.zip . ) || log "zip failed"
  else
    log "outputs/ empty (cline wrote nothing)"
  fi
fi

# 3. independent judge (mirror run_one.sh logic)
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
VERDICT="ABSENT"; REASON=""
if [ ! -f "$WORKDIR/outputs/submit.zip" ]; then
  VERDICT="FAIL"; REASON="no submit.zip produced (cline wrote nothing under outputs/)"
else
  log "judge: $JUDGE"
  rm -rf "$JUDGE"; mkdir -p "$JUDGE"
  cp "$WORKDIR/outputs/submit.zip" "$JUDGE/"
  cp "$REF_DIR/check.py" "$JUDGE/" 2>/dev/null || { VERDICT="FAIL"; REASON="judge-env: check.py missing"; }
  if [ "$VERDICT" != "FAIL" ]; then
    for f in "$REF_DIR"/*.py "$REF_DIR"/*.json; do
      [ -f "$f" ] || continue; b=$(basename "$f")
      [ "$b" = "check.py" ] && continue; [ "$b" = "negative_selftest.py" ] && continue
      [ -f "$JUDGE/$b" ] || cp "$f" "$JUDGE/" 2>/dev/null || true
    done
    # copy A attachments preserving rel structure
    for a in $(python3 - "$TASK_ID" "$JSONL" <<'PY'
import json,sys,os
tid=sys.argv[1]; jl=sys.argv[2]; _p=f'assets/{tid}/'
for line in open(jl):
    d=json.loads(line)
    if d.get('task_id')==tid:
        forb={'_check.py','check.py','_reference_check.py','reference_submit.zip','reference','negative','hidden','hidden_manifest.json'}
        for a in d.get('attachments',[]):
            if isinstance(a,dict):
                s=a.get('source') or a.get('name') or ''; n=a.get('name') or (os.path.basename(s) if s else '')
            else: s=str(a) if a is not None else ''; n=os.path.basename(s) if s else ''
            if not n or n in forb: continue
            rel=s[len(_p):] if s.startswith(_p) else n; rel=rel.lstrip('/')
            if rel in forb or rel.split('/')[0] in forb: continue
            print(rel)
        break
PY
); do
      [ -f "$ASSETS_SRC/$a" ] && { mkdir -p "$JUDGE/$(dirname "$a")"; cp "$ASSETS_SRC/$a" "$JUDGE/$a" 2>/dev/null || true; }
    done
    # hidden B (judge-side only)
    mkdir -p "$JUDGE/hidden"
    TOPLEVEL_HIDDEN=$BENCH/benchmarks/EDA-Eval-DesignFlow/hidden/$TASK_ID
    for hsrc in "$ASSETS_SRC/hidden" "$REF_DIR/hidden" "$TOPLEVEL_HIDDEN"; do
      [ -d "$hsrc" ] && cp -r "$hsrc/." "$JUDGE/hidden/" 2>/dev/null || true
    done
    cd "$JUDGE"
    JUDGE_OUT=$(python3 - <<'PY'
import importlib.util, sys, json
spec = importlib.util.spec_from_file_location('check','check.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
try:
    r = m.check('submit.zip','.')
    if r is True or r is None: print(json.dumps({'verdict':'PASS','detail':str(r)}))
    elif r is False: print(json.dumps({'verdict':'FAIL','detail':str(r)}))
    elif isinstance(r,dict): print(json.dumps({'verdict':'PASS' if (r.get('pass') or r.get('ok') or r.get('passed')) else 'FAIL','detail':str(r)}))
    else: print(json.dumps({'verdict':'PASS' if r else 'FAIL','detail':str(r)}))
except Exception as e: print(json.dumps({'verdict':'FAIL','detail':'exception: '+repr(e)}))
PY
)
    VERDICT=$(echo "$JUDGE_OUT" | python3 -c "import json,sys;print(json.load(sys.stdin)['verdict'])")
    REASON=$(echo "$JUDGE_OUT" | python3 -c "import json,sys;print(json.load(sys.stdin)['detail'][:300])")
    log "verdict=$VERDICT detail=$REASON"
  fi
fi

# 4. record status (skip if a real run_one record already exists for this task at a later ts)
log "record $STATUS_JSONL"
python3 - "$TASK_ID" "$TS" "$DUR" "$CLINE_EXIT" "$VERDICT" "$REASON" "$STATUS_JSONL" <<'PY'
import json,sys,os
task_id,ts,dur,cexit,verdict,reason,out=sys.argv[1:8]
rec={"ts":ts,"task_id":task_id,"harness":"cline","cline_version":"3.0.51",
     "model":"deepseek-v4-pro-cloud","thinking":"medium",
     "dur_sec":int(dur) if dur else None,"cline_exit":int(cexit) if cexit else None,
     "verdict":verdict,"reason":reason,"hook":"PreToolUse",
     "scope":os.path.expanduser("~/.cline/hooks/hook_scope.txt")}
# dedup: if an existing record for this task already has a real dur_sec (not null), skip
existing=[json.loads(l) for l in open(out) if l.strip()]
has_real=any(r.get('task_id')==task_id and r.get('dur_sec') for r in existing)
if has_real:
    print('skip: real run_one record already exists for', task_id)
else:
    with open(out,'a') as f: f.write(json.dumps(rec,ensure_ascii=False)+'\n')
    print('recorded:', json.dumps(rec,ensure_ascii=False))
PY
log "DONE verdict=$VERDICT ($TASK_ID)"
