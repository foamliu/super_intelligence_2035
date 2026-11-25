#!/usr/bin/env bash
# Continuous L1 autoqueue: evaluate every newly-landed 2k ckpt (>=274000) in order.
# Per 11-21 user order "放行 autoqueue" + 11-09 order: serial, one ckpt at a time,
# -t 4, nice 19, CPU only, MUST NOT drag training (step<7.4s).
#
# Design:
#   1. Serial guard -- wait for ANY running llama-server to exit (so the 272k
#      one-shot autoqueue finishes first; no two evals overlap).
#   2. Find the lowest unevaluated ckpt >= MIN_ITER (274000) whose dir is stable.
#   3. Re-check it is still unevaluated right before eval (race safety).
#   4. Check train step time < 7.4s; if not, pause 10 min and retry.
#   5. HF export -> patch config -> check_rope -> GGUF F16 -> lm_eval 8-set
#      limit=100 -> regenerate scaling report -> delete GGUF (keep results.json).
#   6. Loop back to 1.
#
# 270k / 272k are handled by their own one-shot scripts (already running/done);
# this daemon starts from 274k so there is no double-eval.
set -uo pipefail
export CUDA_VISIBLE_DEVICES=''
export OMP_NUM_THREADS=4
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export no_proxy='127.0.0.1,localhost' NO_PROXY='127.0.0.1,localhost'

# ---- paths ----
CKPT_ROOT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints
RES_DIR=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results
HF_ROOT=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b
GGUF_ROOT=/nas_train/app.e0031982/models/baize2b_gguf
CONVERTER=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/convert_mcore_to_hf.py
CHECK_ROPE=/nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm/scripts/check_rope.py
GGUF_SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/pretrain_cpu_eval_gguf/01_convert_hf_to_gguf.sh
SCRIPT_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/pretrain_cpu_eval_gguf
REPORT_GEN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/gen_llamacpp_scaling_report.py
REPORT_PATH=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/reports/report_pretrain_llamacpp_scaling_zh.html
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
SERVER=/nas_train/app.e0031982/code/llama.cpp/build/bin/llama-server
TASKS="arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande"
PORT=8201
MIN_ITER=274000
MAX_ITER=700000
LOG=/tmp/baize_l1_autoqueue_continuous.log
MASTER_LOG=/tmp/baize_s1_baize2b_master.log
WORKER_LOG=/tmp/baize_s1_baize2b_worker.log

ts() { date '+%Y-%m-%d %H:%M:%S'; }
echo "$(ts) === continuous L1 autoqueue started (MIN_ITER=$MIN_ITER) ===" | tee "$LOG"

find_train_pid() { pgrep -f "pretrain_launcher.*baize2b" 2>/dev/null | head -1; }

step_time_sec() {
  tail -10 "$WORKER_LOG" 2>/dev/null \
    | grep -oP 'elapsed time per iteration \(ms\): \K[0-9.]+' \
    | awk '{s+=$1;n++} END{if(n>0) printf "%.2f", s/n/1000; else print "99.99"}'
}

check_train_health() {
  local pid; pid=$(find_train_pid)
  local st; st=$(step_time_sec)
  echo "$(ts) train PID=${pid:-none} step=${st}s (thresh 7.4s)" | tee -a "$LOG"
  awk "BEGIN{exit !(${st:-99.99} <= 7.4)}"
}

ckpt_stable() {
  local d="$1"
  [ -d "$d" ] || return 1
  local n; n=$(find "$d" -maxdepth 1 -type f 2>/dev/null | wc -l)
  [ "$n" -gt 0 ] || return 1
  local m; m=$(stat -c %Y "$d" 2>/dev/null || echo 0)
  local now; now=$(date +%s)
  [ $((now - m)) -ge 60 ]
}

has_results() {
  local iter="$1"
  [ -f "$RES_DIR/gguf_iter_${iter}_fixed_8set/results.json" ]
}

next_iter() {
  local best="" d it
  for d in "$CKPT_ROOT"/iter_*; do
    [ -d "$d" ] || continue
    it=$(basename "$d" | grep -oP 'iter_\K[0-9]+') || continue
    [ -n "$it" ] || continue
    # Normalize to a decimal integer (strip any leading zeros). Without this,
    # a value like "0274000" is treated as OCTAL by $(( )) and `printf %d`
    # -> 96256, and "0278000" (contains digit 8) errors out as invalid octal.
    it=$((10#$it))
    [ "$it" -ge "$MIN_ITER" ] 2>/dev/null || continue
    [ "$it" -le "$MAX_ITER" ] 2>/dev/null || continue
    has_results "$it" && continue
    ckpt_stable "$d" || continue
    if [ -z "$best" ] || [ "$it" -lt "$best" ]; then best="$it"; fi
  done
  echo "$best"
}

pkill_server() {
  local pid; pid=$(pgrep -f "llama.cpp/build/bin/llama-server.*--port $PORT" 2>/dev/null | head -1)
  [ -n "$pid" ] && { kill "$pid" 2>/dev/null; sleep 3; kill -9 "$pid" 2>/dev/null; sleep 1; }
}

start_server() {
  pkill_server
  setsid nice -n 19 "$SERVER" -m "$1" -t 4 -c 4096 --parallel 2 \
    --host 127.0.0.1 --port $PORT --no-warmup --temp 0 --top-k 1 --seed 1234 \
    > "/tmp/baize_server_cont.log" 2>&1 < /dev/null &
  local i=0
  while [ $i -lt 60 ]; do
    curl -s -m 2 http://127.0.0.1:$PORT/health 2>/dev/null | grep -q '"ok"' && return 0
    sleep 2; i=$((i+1))
  done
  echo "$(ts) [FAIL] server timeout" | tee -a "$LOG"; return 1
}

eval_one() {
  local iter="$1"
  local ckpt="$CKPT_ROOT/iter_$(printf '%07d' "$((10#$iter))")"
  local hf="$HF_ROOT/hf_iter_${iter}"
  local gguf="$GGUF_ROOT/bz2b-${iter}-f16.gguf"
  local out="$RES_DIR/gguf_iter_${iter}_fixed_8set"
  echo "$(ts) ---- eval iter=$iter ----" | tee -a "$LOG"

  # Phase 1: HF export
  if [ -f "$hf/model.safetensors" ]; then
    echo "$(ts) [skip] HF exists" | tee -a "$LOG"
  else
    echo "$(ts) [1/6] HF export ..." | tee -a "$LOG"
    nice -n 19 "$PY" "$CONVERTER" --arch hybrid --ckpt-dir "$ckpt" --output-dir "$hf" 2>&1 | tee -a "$LOG"
    [ -f "$hf/model.safetensors" ] || { echo "$(ts) [FAIL] HF export" | tee -a "$LOG"; return 1; }
    echo "$(ts) [1/6] HF DONE" | tee -a "$LOG"
  fi

  # Phase 2: Patch config.json
  echo "$(ts) [2/6] Patch config.json ..." | tee -a "$LOG"
  nice -n 19 "$PY" - "$hf/config.json" <<'PYEOF' 2>&1 | tee -a "$LOG"
import json, sys
c = json.load(open(sys.argv[1]))
c["max_position_embeddings"] = 1048576
c["rope_theta"] = 1000000
c["rope_scaling"] = None
if "mamba_dt_limit" in c:
    del c["mamba_dt_limit"]
    print("  patched: removed mamba_dt_limit")
json.dump(c, open(sys.argv[1], "w"), indent=2, ensure_ascii=False)
print(f"  patched: max_pos={c['max_position_embeddings']}, rope_theta={c['rope_theta']}")
PYEOF

  # Phase 3: check_rope (non-fatal)
  echo "$(ts) [3/6] check_rope.py ..." | tee -a "$LOG"
  if [ -f "$CHECK_ROPE" ]; then
    nice -n 19 "$PY" "$CHECK_ROPE" "$hf/config.json" 2>&1 | tee -a "$LOG" || echo "  [warn] check_rope non-zero (skip)" | tee -a "$LOG"
  else
    echo "  [warn] check_rope missing (skip)" | tee -a "$LOG"
  fi

  # Phase 4: GGUF F16
  if [ -s "$gguf" ]; then
    echo "$(ts) [skip] GGUF exists" | tee -a "$LOG"
  else
    echo "$(ts) [4/6] Convert HF -> GGUF F16 ..." | tee -a "$LOG"
    nice -n 19 bash "$GGUF_SCRIPT" "$hf" "$gguf" f16 2>&1 | tee -a "$LOG"
    [ -s "$gguf" ] || { echo "$(ts) [FAIL] GGUF" | tee -a "$LOG"; return 1; }
    echo "$(ts) [4/6] GGUF DONE" | tee -a "$LOG"
  fi

  # Phase 5: Eval
  if [ -f "$out/results.json" ]; then
    echo "$(ts) [skip] results exist" | tee -a "$LOG"
  else
    echo "$(ts) [5/6] eval iter_${iter} (limit=100, -t4, nice19)" | tee -a "$LOG"
    start_server "$gguf" || { echo "$(ts) [FAIL] server" | tee -a "$LOG"; return 1; }
    mkdir -p "$out"
    nice -n 19 "$PY" "$SCRIPT_DIR/gguf_lmeval_run.py" \
      --base-url http://127.0.0.1:$PORT --hf-dir "$hf" \
      --output "$out" --tasks "$TASKS" --limit 100 --parallel 2 \
      --batch-size 32 --gguf "$gguf" 2>&1 | grep -vE 'gguf-ll:|it/s' | tee -a "$LOG"
    pkill_server
    if [ -f "$out/results.json" ]; then
      echo "$(ts) [done] results.json" | tee -a "$LOG"
      "$PY" - "$out/results.json" <<'PYEOF2' 2>&1 | tee -a "$LOG"
import sys, json
d = json.load(open(sys.argv[1])); r = d.get("results", {}); accs = []
for k in ["arc_challenge","arc_easy","boolq","hellaswag","openbookqa","piqa","sciq","winogrande"]:
    v = r.get(k, {}); a = v.get("acc,none")
    if a is not None: accs.append(a); print(f"  {k}: acc={a:.4f}")
if accs: print(f"  AVG acc={sum(accs)/len(accs):.4f}")
PYEOF2
    else
      echo "$(ts) [FAIL] no results.json" | tee -a "$LOG"; return 1
    fi
  fi
  pkill_server

  # Phase 6: Report
  echo "$(ts) [6/6] generating scaling report ..." | tee -a "$LOG"
  BAIZE_REPORT_PATH="$REPORT_PATH" nice -n 19 "$PY" "$REPORT_GEN" 2>&1 | tee -a "$LOG"

  # Cleanup GGUF (results.json is what matters; frees 4.4 GB)
  if [ -f "$out/results.json" ] && [ -s "$gguf" ]; then
    rm -f "$gguf" && echo "$(ts) [cleanup] removed $gguf" | tee -a "$LOG"
  fi
  echo "$(ts) ---- iter=$iter DONE ----" | tee -a "$LOG"
  return 0
}

# ---- main loop ----
while true; do
  # NOTE: must NOT use `pgrep -f 'llama-server'` -- the cline agent process
  # carries the task book (which mentions "llama-server") in its argv, causing
  # a permanent false-positive that blocks the daemon during every agent wake.
  # `pgrep -x llama-server` matches only the binary's comm (cline/bash excluded).
  while pgrep -x llama-server >/dev/null 2>&1; do
    echo "$(ts) [serial] llama-server running, waiting 60s ..." | tee -a "$LOG"
    sleep 60
  done
  it=$(next_iter)
  if [ -z "$it" ]; then
    echo "$(ts) [idle] no new ckpt to eval, sleep 300s ..." | tee -a "$LOG"
    sleep 300
    continue
  fi
  if has_results "$it"; then
    echo "$(ts) [race] iter=$it already has results, skip" | tee -a "$LOG"
    continue
  fi
  if ! check_train_health; then
    echo "$(ts) [WARN] step>7.4s, pausing eval 10min (train first) ..." | tee -a "$LOG"
    sleep 600
    continue
  fi
  eval_one "$it" || echo "$(ts) [ERR] eval_one iter=$it failed, will retry next loop" | tee -a "$LOG"
  sleep 30
done
