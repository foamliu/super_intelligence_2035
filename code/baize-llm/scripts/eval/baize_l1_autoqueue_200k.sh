#!/usr/bin/env bash
# Autoqueue: poll for iter_0200000 checkpoint, then run L1 8-set eval pipeline
# Per 11-09 operator order: serial, one ckpt, -t 4, nice 19, CPU only
set -uo pipefail
export CUDA_VISIBLE_DEVICES=''
export OMP_NUM_THREADS=4
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1

ITER=200000
CKPT_DIR=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/iter_0200000
HF_DIR=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_200000
GGUF_OUT=/nas_train/app.e0031982/models/baize2b_gguf/bz2b-200000-f16.gguf
CONVERTER=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/convert_mcore_to_hf.py
CHECK_ROPE=/nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm/scripts/check_rope.py
GGUF_SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/pretrain_cpu_eval_gguf/01_convert_hf_to_gguf.sh
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
SERVER=/nas_train/app.e0031982/code/llama.cpp/build/bin/llama-server
SCRIPT_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/pretrain_cpu_eval_gguf
TASKS="arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande"
PORT=8192
RES_DIR=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results
REPORT_GEN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/gen_llamacpp_scaling_report.py
LOG=/tmp/baize_l1_autoqueue_200k.log

ts() { date '+%Y-%m-%d %H:%M:%S'; }
find_train_pid() { pgrep -f "pretrain_launcher.*baize2b" 2>/dev/null | head -1; }

check_train_health() {
  local pid=$(find_train_pid)
  if [ -z "$pid" ]; then echo "$(ts) [WARN] no train PID" | tee -a "$LOG"; return 0; fi
  local step_ms=$(tail -1 /proc/$pid/fd/1 2>/dev/null | grep -oP 'elapsed time per iteration \(ms\): \K[0-9.]+' || echo "9999")
  local step_int=${step_ms%.*}
  echo "$(ts) train PID=$pid step=${step_ms}ms (thresh 7400)" | tee -a "$LOG"
  [ "$step_int" -le 7400 ] 2>/dev/null
}

# Phase 0: Poll for checkpoint
echo "$(ts) autoqueue started, polling for $CKPT_DIR" | tee "$LOG"
WAITED=0
while [ ! -d "$CKPT_DIR" ]; do
  sleep 300; WAITED=$((WAITED+300))
  [ $WAITED -ge 64800 ] && { echo "$(ts) [TIMEOUT] giving up (18h limit)" | tee -a "$LOG"; exit 1; }
  local_pid=$(find_train_pid)
  local_iter=$(tail -1 /proc/$local_pid/fd/1 2>/dev/null | grep -oP 'iteration +\K[0-9]+' || echo "?")
  echo "$(ts) waiting for ckpt (train iter=$local_iter, ${WAITED}s)..." | tee -a "$LOG"
done
echo "$(ts) checkpoint found!" | tee -a "$LOG"

# Verify training health
if ! check_train_health; then
  echo "$(ts) [WARN] step>7.4s, pausing 10min..." | tee -a "$LOG"; sleep 600
  check_train_health || { echo "$(ts) [ABORT] still slow" | tee -a "$LOG"; exit 1; }
fi
echo "$(ts) training healthy, proceeding" | tee -a "$LOG"

# Phase 1: Export HF
if [ -f "$HF_DIR/model.safetensors" ]; then
  echo "$(ts) [skip] HF exists" | tee -a "$LOG"
else
  echo "$(ts) [1/6] Convert mcore -> HF ..." | tee -a "$LOG"
  nice -n 19 "$PY" "$CONVERTER" --arch hybrid --ckpt-dir "$CKPT_DIR" --output-dir "$HF_DIR" 2>&1 | tee -a "$LOG"
  [ -f "$HF_DIR/model.safetensors" ] || { echo "[FAIL] HF export" | tee -a "$LOG"; exit 1; }
  echo "$(ts) [1/6] HF DONE" | tee -a "$LOG"
fi

# Phase 2: Patch config.json
echo "$(ts) [2/6] Patch config.json ..." | tee -a "$LOG"
nice -n 19 "$PY" - "$HF_DIR/config.json" <<'PYEOF' 2>&1 | tee -a "$LOG"
import json, sys
c = json.load(open(sys.argv[1]))
c["max_position_embeddings"] = 1048576
c["rope_theta"] = 1000000
c["rope_scaling"] = None
if "mamba_dt_limit" in c:
    del c["mamba_dt_limit"]
    print("  patched: removed mamba_dt_limit (huggingface_hub compat fix)")
json.dump(c, open(sys.argv[1], "w"), indent=2, ensure_ascii=False)
print(f"  patched: max_pos={c['max_position_embeddings']}, rope_theta={c['rope_theta']}")
PYEOF

# Phase 3: check_rope
echo "$(ts) [3/6] check_rope.py ..." | tee -a "$LOG"
[ -f "$CHECK_ROPE" ] && nice -n 19 "$PY" "$CHECK_ROPE" "$HF_DIR/config.json" 2>&1 | tee -a "$LOG" || echo "  [warn] skip" | tee -a "$LOG"

# Phase 4: Convert GGUF F16
if [ -s "$GGUF_OUT" ]; then
  echo "$(ts) [skip] GGUF exists" | tee -a "$LOG"
else
  echo "$(ts) [4/6] Convert HF -> GGUF F16 ..." | tee -a "$LOG"
  nice -n 19 bash "$GGUF_SCRIPT" "$HF_DIR" "$GGUF_OUT" f16 2>&1 | tee -a "$LOG"
  [ -s "$GGUF_OUT" ] || { echo "[FAIL] GGUF" | tee -a "$LOG"; exit 1; }
  echo "$(ts) [4/6] GGUF DONE" | tee -a "$LOG"
fi

# Phase 5: Eval
pkill_server() {
  local pid=$(pgrep -f "llama-server.*--port $PORT" 2>/dev/null | head -1)
  [ -n "$pid" ] && { kill "$pid" 2>/dev/null; sleep 3; kill -9 "$pid" 2>/dev/null; sleep 1; }
}
start_server() {
  pkill_server
  setsid nice -n 19 "$SERVER" -m "$1" -t 4 -c 4096 --parallel 2 \
    --host 127.0.0.1 --port $PORT --no-warmup --temp 0 --top-k 1 --seed 1234 \
    > /tmp/baize_server_200k.log 2>&1 < /dev/null &
  local i=0
  while [ $i -lt 60 ]; do
    curl -s -m 2 http://127.0.0.1:$PORT/health 2>/dev/null | grep -q '"ok"' && return 0
    sleep 2; i=$((i+1))
  done
  echo "[FAIL] server timeout" | tee -a "$LOG"; return 1
}

OUT=$RES_DIR/gguf_iter_200000_fixed_8set
if [ -f "$OUT/results.json" ]; then
  echo "$(ts) [skip] results exist" | tee -a "$LOG"
else
  echo "$(ts) [5/6] eval iter_200000 (limit=100, -t4, nice19)" | tee -a "$LOG"
  start_server "$GGUF_OUT" || { echo "[FAIL] server" | tee -a "$LOG"; exit 1; }
  mkdir -p "$OUT"
  nice -n 19 "$PY" "$SCRIPT_DIR/gguf_lmeval_run.py" \
    --base-url http://127.0.0.1:$PORT --hf-dir "$HF_DIR" \
    --output "$OUT" --tasks "$TASKS" --limit 100 --parallel 2 \
    --batch-size 32 --gguf "$GGUF_OUT" 2>&1 | grep -vE 'gguf-ll:|it/s' | tee -a "$LOG"
  pkill_server
  if [ -f "$OUT/results.json" ]; then
    echo "$(ts) [done] results.json" | tee -a "$LOG"
    "$PY" - "$OUT/results.json" <<'PYEOF2' 2>&1 | tee -a "$LOG"
import sys, json
d = json.load(open(sys.argv[1])); r = d.get("results", {}); accs = []
for k in ["arc_challenge","arc_easy","boolq","hellaswag","openbookqa","piqa","sciq","winogrande"]:
    v = r.get(k, {}); a = v.get("acc,none")
    if a is not None: accs.append(a); print(f"  {k}: acc={a:.4f}")
if accs: print(f"  AVG acc={sum(accs)/len(accs):.4f}")
PYEOF2
  else
    echo "[FAIL] no results.json" | tee -a "$LOG"
  fi
fi
pkill_server

# Phase 6: Generate report
echo "$(ts) [6/6] generating scaling report ..." | tee -a "$LOG"
nice -n 19 "$PY" "$REPORT_GEN" 2>&1 | tee -a "$LOG"
echo "$(ts) 200k autoqueue ALL DONE" | tee -a "$LOG"
