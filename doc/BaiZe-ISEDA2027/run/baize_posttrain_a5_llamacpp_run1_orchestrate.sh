#!/usr/bin/env bash
# baize_posttrain_a5_llamacpp_run1_orchestrate.sh
# Autonomous B2+B3+B4 for the A5 Q4_K_M+llama.cpp single run (OPS_A5_LLAMACPP_Q4KM_RUN1.md).
#
# Pre-conditions (already done by the launching wake):
#   - llama-server UP on :8095, preflight PASS, pid in /tmp/a5_llamacpp_server.latest.pid
#   - providers.json backup at /tmp/providers.pre_a5.json (sha recorded)
#
# This script:
#   B2  launches baize_posttrain_5run_eval.sh --run 1 (codegen -p8 -n + scoring)
#   B3  watchdog @20min & @45min: first-10-tasks empty-code >=3  => kill, INFRA_FAIL
#   B4  stop serve, verify providers.json sha, build pertask + summary JSON, write STATUS
#
# Hard cap: 8h (28800s) for the eval.
set -uo pipefail

RUN_DIR="/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
LABEL="qwen35_q4km_llamacpp"
MODEL="qwen3.5-2b-a5"
ENDPOINT="http://127.0.0.1:8095/v1"
PORT="8095"
EVAL_OUT="/tmp/posttrain_5run_eval/${LABEL}/run1"
PROVIDERS_JSON="$HOME/.cline/data/settings/providers.json"
PROVIDERS_PRE="/tmp/providers.pre_a5.json"
STATUS_JSON="/tmp/a5_run1_status.json"
ORCH_LOG="/tmp/a5_run1_orchestrate.log"
SERVER_LATEST_PID="/tmp/a5_llamacpp_server.latest.pid"
HARD_CAP=28800   # 8h

log(){ echo "[$(date '+%F %T')] $*" | tee -a "$ORCH_LOG"; }

log "===== A5 llama.cpp Q4_K_M run1 ORCHESTRATOR START ====="
T0=$(date +%s)

PRE_SHA="$(sha256sum "$PROVIDERS_PRE" 2>/dev/null | cut -d' ' -f1)"
log "providers pre sha256 = $PRE_SHA"

# ---------- B2: launch eval ----------
mkdir -p "$EVAL_OUT"
cd "$RUN_DIR/.."
log "B2 launching 5run_eval.sh --run 1 (label=$LABEL model=$MODEL endpoint=$ENDPOINT)"
bash run/baize_posttrain_5run_eval.sh \
    --endpoint "$ENDPOINT" --model "$MODEL" --label "$LABEL" --run 1 \
    > "$EVAL_OUT/orchestrate_eval.log" 2>&1 &
EVAL_PID=$!
log "B2 eval pid=$EVAL_PID  log=$EVAL_OUT/orchestrate_eval.log"

# ---------- B3: watchdog ----------
watchdog_verdict="not_triggered"
wd_checked_20=0; wd_checked_45=0
empty_threshold=3

find_completed_jsonl(){
  ls -t "$HOME"/eda_code_eval/completed_code_generation_*.jsonl 2>/dev/null \
    | grep -v 'completed_code_generation\.jsonl$' | head -1
}

count_empty_first_n(){
  local f="$1"; local n="${2:-10}"
  [ -f "$f" ] || { echo -1; return; }
  python3 - "$f" "$n" <<'PY'
import json,sys
f,n=sys.argv[1],int(sys.argv[2])
empty=0; seen=0
try:
    with open(f,encoding='utf-8') as fh:
        for line in fh:
            line=line.strip()
            if not line: continue
            seen+=1
            if seen>n: break
            try: d=json.loads(line)
            except: continue
            comp=(d.get('completion') or '').strip()
            if not comp: empty+=1
except FileNotFoundError:
    print(-1); sys.exit(0)
print(empty)
PY
}

while kill -0 "$EVAL_PID" 2>/dev/null; do
  sleep 60
  NOW=$(date +%s); ELAPSED=$((NOW-T0))
  if [ $ELAPSED -ge $HARD_CAP ]; then
    log "B3 HARD CAP ${HARD_CAP}s reached -> killing eval"
    kill -TERM "$EVAL_PID" 2>/dev/null; sleep 5; kill -9 "$EVAL_PID" 2>/dev/null
    watchdog_verdict="hard_cap"; break
  fi
  if [ $wd_checked_20 -eq 0 ] && [ $ELAPSED -ge 1200 ]; then
    wd_checked_20=1
    JL=$(find_completed_jsonl)
    log "B3 @20min check: jsonl=$JL"
    if [ -n "$JL" ]; then
      EM=$(count_empty_first_n "$JL" 10)
      log "B3 @20min: first-10 empty=$EM (threshold=$empty_threshold)"
      if [ "$EM" != "-1" ] && [ "$EM" -ge $empty_threshold ]; then
        log "B3 @20min WATCHDOG TRIGGERED (empty=$EM>=3) -> INFRA_FAIL, killing eval"
        kill -TERM "$EVAL_PID" 2>/dev/null; sleep 5; kill -9 "$EVAL_PID" 2>/dev/null
        watchdog_verdict="infra_fail_20min"; break
      fi
    else
      log "B3 @20min: no completed jsonl yet (eval may be slow to emit first tasks)"
    fi
  fi
  if [ $wd_checked_45 -eq 0 ] && [ $ELAPSED -ge 2700 ]; then
    wd_checked_45=1
    JL=$(find_completed_jsonl)
    log "B3 @45min check: jsonl=$JL"
    if [ -n "$JL" ]; then
      EM=$(count_empty_first_n "$JL" 10)
      log "B3 @45min: first-10 empty=$EM (threshold=$empty_threshold)"
      if [ "$EM" != "-1" ] && [ "$EM" -ge $empty_threshold ]; then
        log "B3 @45min WATCHDOG TRIGGERED (empty=$EM>=3) -> INFRA_FAIL, killing eval"
        kill -TERM "$EVAL_PID" 2>/dev/null; sleep 5; kill -9 "$EVAL_PID" 2>/dev/null
        watchdog_verdict="infra_fail_45min"; break
      fi
    fi
  fi
  if ! curl -sf --noproxy '*' "http://127.0.0.1:${PORT}/health" >/dev/null 2>&1; then
    log "B3 WARN server /health not OK (may be busy); continuing"
  fi
done

wait "$EVAL_PID" 2>/dev/null
EVAL_RC=$?
T1=$(date +%s); WALL=$((T1-T0))
log "B2 eval finished rc=$EVAL_RC wallclock=${WALL}s  watchdog=$watchdog_verdict"

# ---------- B4: cleanup + deliverables ----------
log "B4 cleanup starting"

# 4.1 stop serve (only our pidfile)
if [ -f "$SERVER_LATEST_PID" ]; then
  SPID=$(cat "$SERVER_LATEST_PID")
  log "B4 stopping llama-server pid=$SPID"
  bash "$RUN_DIR/baize_posttrain_a5_llamacpp_serve.sh" stop >> "$ORCH_LOG" 2>&1 || true
  kill "$SPID" 2>/dev/null || true
  for _ in $(seq 1 10); do kill -0 "$SPID" 2>/dev/null || break; sleep 1; done
  kill -9 "$SPID" 2>/dev/null || true
fi

# 4.2 verify providers.json restored
POST_SHA="$(sha256sum "$PROVIDERS_JSON" 2>/dev/null | cut -d' ' -f1)"
providers_ok="unknown"
if [ -n "$PRE_SHA" ] && [ "$POST_SHA" = "$PRE_SHA" ]; then
  providers_ok="ok"
  log "B4 providers.json restored OK (sha matches pre)"
else
  providers_ok="MISMATCH"
  log "B4 FATAL providers.json sha MISMATCH pre=$PRE_SHA post=$POST_SHA -> restoring from backup"
  cp "$PROVIDERS_PRE" "$PROVIDERS_JSON"
fi

# 4.3 locate batch eval dir (newest with cli_data)
BATCH_DIR=""
for d in $(ls -dt "$HOME"/eda_code_eval/2026_* 2>/dev/null); do
  if [ -d "$d/cli_data" ]; then BATCH_DIR="$d"; break; fi
done
log "B4 batch eval dir = $BATCH_DIR"

# 4.4 server token metrics (best-effort)
SRV_PROMPT_TOK="N/A"; SRV_DECODE_TOK="N/A"
METRICS=$(curl -s --noproxy '*' "http://127.0.0.1:${PORT}/metrics" 2>/dev/null || true)
if [ -n "$METRICS" ]; then
  PT=$(echo "$METRICS" | grep -oP 'llamacpp:prompt_tokens\s+\K[0-9]+' | tail -1)
  DT=$(echo "$METRICS" | grep -oP 'llamacpp:tokens_predicted\s+\K[0-9]+' | tail -1)
  [ -n "$PT" ] && SRV_PROMPT_TOK="$PT"
  [ -n "$DT" ] && SRV_DECODE_TOK="$DT"
fi

# 4.5 final_report
FR="$EVAL_OUT/final_report.json"
log "B4 final_report = $FR (exists=$([ -f "$FR" ] && echo yes || echo no))"

# 4.6 pertask profile
PERTASK_OUT="$RUN_DIR/baseline_A5_qwen35_2b_llamacpp_q4km_run1_pertask.json"
if [ -n "$BATCH_DIR" ] && [ -f "$FR" ]; then
  log "B4 building pertask profile -> $PERTASK_OUT"
  python3 "$RUN_DIR/baize_posttrain_baseline_pertask_profile.py" \
      --eval-dir "$BATCH_DIR" --report "$FR" \
      --arm "A5_qwen35_q4km_llamacpp" --run 1 --out "$PERTASK_OUT" \
      >> "$ORCH_LOG" 2>&1 || log "B4 WARN pertask profile failed"
else
  log "B4 SKIP pertask profile (batch_dir or final_report missing)"
fi

# 4.7 summary JSON
SUMMARY_OUT="$RUN_DIR/baseline_A5_qwen35_2b_llamacpp_q4km_run1_summary.json"
PY=python3
[ -x /nas_data/app.e0031982/miniforge3/envs/py310/bin/python ] && PY=/nas_data/app.e0031982/miniforge3/envs/py310/bin/python
"$PY" - "$FR" "$PERTASK_OUT" "$SUMMARY_OUT" "$WALL" "$EVAL_RC" "$watchdog_verdict" "$providers_ok" "$PRE_SHA" "$POST_SHA" "$SRV_PROMPT_TOK" "$SRV_DECODE_TOK" "$BATCH_DIR" <<'PYEOF'
import json, sys
fr_path, pt_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
wall, rc, wd, pok, pre_sha, post_sha, spt, sdt, batch = sys.argv[4:13]
s = {
  "arm": "A5_qwen35_q4km_llamacpp", "run": 1,
  "caliber": "Q4_K_M quantization + llama.cpp (CPU); NOT comparable to A0 vLLM fp16 43.29% (no McNemar / no subtraction)",
  "model_served": "qwen3.5-2b-a5",
  "weight_gguf": "/nas_data/app.e0031982/models/qwen35_gguf/qwen3.5-2b-Q4_K_M.gguf",
  "weight_sha256": "0b4f5f0c3dd04beee30c1bfa951e0999a3801fdad462abd418ad2350b306040e",
  "backend": "llama.cpp rev 969d733, --parallel 8 -t 16 -tb 16 -c 262144 --jinja --temp 0 --top-k 1 --seed 1234",
  "protocol": "158 tasks / Pass@1 / 2500s / single trace / -p 8 -n",
  "wallclock_s": int(wall), "eval_rc": int(rc), "watchdog_verdict": wd,
  "providers_json_restore": pok, "providers_pre_sha256": pre_sha, "providers_post_sha256": post_sha,
  "batch_eval_dir": batch, "final_report_path": fr_path, "pertask_path": pt_path,
  "server_prompt_tokens": spt, "server_decode_tokens": sdt,
}
try:
  fr = json.load(open(fr_path)); m = fr.get("metrics", fr)
  s["pass_at_1"] = m.get("pass_rate", fr.get("pass_rate", fr.get("pass@1")))
  s["n_pass"] = m.get("pass_count", m.get("n_pass"))
  s["n_total"] = m.get("total_count", m.get("n_total"))
  s["final_report_model_name"] = fr.get("model_name")
except Exception as e:
  s["final_report_error"] = repr(e)
try:
  pt = json.load(open(pt_path)); fm = pt.get("fail_mode_five_class", {})
  for k in ("F1_no_code","F2_tool_format","F3_timeout","F4_api_misuse","F5_logic_error"):
    s["fail_mode_"+k] = fm.get(k)
  s["n_pass_pertask"] = pt.get("n_pass"); s["n_fail_pertask"] = pt.get("n_fail")
  s["overall_pass1_pertask"] = pt.get("overall_pass1")
  agg = pt.get("aggregate_tool_calls", {}); s["aggregate_tool_calls"] = agg
  rc_calls = agg.get("run_commands", 0)
  total_calls = sum(v for v in agg.values() if isinstance(v, (int, float)))
  s["cheat_rate_proxy_run_commands_fraction"] = (rc_calls/total_calls) if total_calls else None
  s["cheat_rate_note"] = "proxy = run_commands tool_use attempts / total tool calls (PreToolUse hook blocks run_commands/bash; authoritative cheat rate pending harness audit)"
  s["four_metric_means"] = pt.get("four_metric_means_over_tasks", {})
except Exception as e:
  s["pertask_error"] = repr(e)
with open(out_path, "w") as fh:
  json.dump(s, fh, ensure_ascii=False, indent=2)
print(json.dumps(s, ensure_ascii=False, indent=2))
PYEOF
log "B4 summary written -> $SUMMARY_OUT"

# 4.8 STATUS
WD_FINAL="$watchdog_verdict"
if [ "$WD_FINAL" = "not_triggered" ] && [ -f "$FR" ]; then ST="COMPLETE"; else ST="$WD_FINAL"; fi
cat > "$STATUS_JSON" <<EOF
{
 "status": "$ST",
 "watchdog_verdict": "$watchdog_verdict",
 "eval_rc": $EVAL_RC,
 "wallclock_s": $WALL,
 "final_report_present": $([ -f "$FR" ] && echo true || echo false),
 "pertask_present": $([ -f "$PERTASK_OUT" ] && echo true || echo false),
 "summary_present": $([ -f "$SUMMARY_OUT" ] && echo true || echo false),
 "providers_restore": "$providers_ok"
}
EOF
log "STATUS -> $STATUS_JSON"
log "===== A5 llama.cpp Q4_K_M run1 ORCHESTRATOR END ====="
