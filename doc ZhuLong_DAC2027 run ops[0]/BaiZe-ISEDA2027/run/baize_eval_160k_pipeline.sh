#!/usr/bin/env bash
# Pipeline: export HF + convert GGUF + eval 160k (single server, -t 4, nice 19)
# Per 11-09 operator order: serial, one ckpt at a time, low thread to protect training
set -uo pipefail
export CUDA_VISIBLE_DEVICES=''
export OMP_NUM_THREADS=4
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"
export HF_HUB_OFFLINE=1 HF_DATASETS_OFFLINE=1 TRANSFORMERS_OFFLINE=1

ITER=160000
CKPT_DIR=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/iter_0160000
HF_DIR=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/hf_iter_160000
GGUF_OUT=/nas_train/app.e0031982/models/baize2b_gguf/bz2b-160000-f16.gguf
CONVERTER=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/convert_mcore_to_hf.py
CHECK_ROPE=/nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm/scripts/check_rope.py
GGUF_SCRIPT=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/pretrain_cpu_eval_gguf/01_convert_hf_to_gguf.sh
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
SERVER=/nas_train/app.e0031982/code/llama.cpp/build/bin/llama-server
SCRIPT_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/pretrain_cpu_eval_gguf
TASKS="arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande"
PORT=8190
RES_DIR=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results
REPORT_GEN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/gen_llamacpp_scaling_report.py
LOG=/tmp/baize_eval_160k_pipeline.log

echo "[$(date '+%H:%M:%S')] 160k pipeline started" | tee "$LOG"

# Phase 1: Export HF from NeMo checkpoint
if [ -f "$HF_DIR/model.safetensors" ]; then
  echo "[$(date '+%H:%M:%S')] [skip] HF already exists at $HF_DIR" | tee -a "$LOG"
else
  echo "[$(date '+%H:%M:%S')] [1/6] Convert mcore -> HF (iter=$ITER) ..." | tee -a "$LOG"
  nice -n 19 "$PY" "$CONVERTER" --arch hybrid --ckpt-dir "$CKPT_DIR" --output-dir "$HF_DIR" 2>&1 | tee -a "$LOG"
  if [ ! -f "$HF_DIR/model.safetensors" ]; then
    echo "[FAIL] HF export failed, no model.safetensors" | tee -a "$LOG"; exit 1
  fi
  echo "[$(date '+%H:%M:%S')] [1/6] HF export DONE" | tee -a "$LOG"
fi

# Phase 2: Patch config.json
echo "[$(date '+%H:%M:%S')] [2/6] Patch config.json ..." | tee -a "$LOG"
nice -n 19 "$PY" - "$HF_DIR/config.json" <<'PYEOF' 2>&1 | tee -a "$LOG"
import json, sys
p = sys.argv[1]
c = json.load(open(p))
c["max_position_embeddings"] = 1048576
c["rope_theta"] = 1000000
c["rope_scaling"] = None
json.dump(c, open(p, "w"), indent=2, ensure_ascii=False)
print(f"  patched: max_pos={c['max_position_embeddings']}, rope_theta={c['rope_theta']}")
PYEOF

# Phase 3: check_rope verification
echo "[$(date '+%H:%M:%S')] [3/6] check_rope.py verification ..." | tee -a "$LOG"
if [ -f "$CHECK_ROPE" ]; then
  nice -n 19 "$PY" "$CHECK_ROPE" "$HF_DIR/config.json" 2>&1 | tee -a "$LOG"
else
  echo "  [warn] check_rope.py not found, skipping" | tee -a "$LOG"
fi

# Phase 4: Convert HF -> GGUF F16
if [ -s "$GGUF_OUT" ]; then
  echo "[$(date '+%H:%M:%S')] [skip] GGUF already exists" | tee -a "$LOG"
else
  echo "[$(date '+%H:%M:%S')] [4/6] Convert HF -> GGUF F16 ..." | tee -a "$LOG"
  nice -n 19 bash "$GGUF_SCRIPT" "$HF_DIR" "$GGUF_OUT" f16 2>&1 | tee -a "$LOG"
  if [ ! -s "$GGUF_OUT" ]; then
    echo "[FAIL] GGUF conversion failed" | tee -a "$LOG"; exit 1
  fi
  echo "[$(date '+%H:%M:%S')] [4/6] GGUF conversion DONE" | tee -a "$LOG"
fi

# Phase 5: Run eval (llama-server + lm_eval 8 sets limit=100)
pkill_server() {
  local pid=$(pgrep -f "llama-server.*--port $PORT" 2>/dev/null | head -1)
  [ -n "$pid" ] && { kill "$pid" 2>/dev/null; sleep 3; kill -9 "$pid" 2>/dev/null; sleep 1; }
}

start_server() {
  local gguf=$1
  pkill_server
  setsid nice -n 19 "$SERVER" -m "$gguf" -t 4 -c 4096 --parallel 2 \
    --host 127.0.0.1 --port $PORT --no-warmup \
    --temp 0 --top-k 1 --seed 1234 > /tmp/baize_server_160k.log 2>&1 < /dev/null &
  local i=0
  while [ $i -lt 60 ]; do
    curl -s -m 2 http://127.0.0.1:$PORT/health 2>/dev/null | grep -q '"ok"' && return 0
    sleep 2; i=$((i+1))
  done
  echo "[FAIL] server did not start" | tee -a "$LOG"; return 1
}

OUT=$RES_DIR/gguf_iter_160000_fixed_8set
if [ -f "$OUT/results.json" ]; then
  echo "[$(date '+%H:%M:%S')] [skip] iter_160000 already has results.json" | tee -a "$LOG"
else
  echo "[$(date '+%H:%M:%S')] [5/6] === eval iter_160000 (limit=100, -t 4, nice 19) ===" | tee -a "$LOG"
  start_server "$GGUF_OUT" || { echo "[FAIL] could not start server" | tee -a "$LOG"; exit 1; }
  mkdir -p "$OUT"
  nice -n 19 "$PY" "$SCRIPT_DIR/gguf_lmeval_run.py" \
    --base-url http://127.0.0.1:$PORT --hf-dir "$HF_DIR" \
    --output "$OUT" --tasks "$TASKS" --limit 100 --parallel 2 \
    --batch-size 32 --gguf "$GGUF_OUT" 2>&1 | grep -vE 'gguf-ll:|it/s' | tee -a "$LOG"
  pkill_server
  if [ -f "$OUT/results.json" ]; then
    echo "[$(date '+%H:%M:%S')] [done] iter_160000 results.json written" | tee -a "$LOG"
    "$PY" - "$OUT/results.json" <<'PYEOF2' 2>&1 | tee -a "$LOG"
import sys, json
d = json.load(open(sys.argv[1]))
r = d.get("results", {})
accs = []
for k in ["arc_challenge","arc_easy","boolq","hellaswag","openbookqa","piqa","sciq","winogrande"]:
    v = r.get(k, {})
    a = v.get("acc,none")
    if a is not None:
        accs.append(a)
        print(f"  {k}: acc={a:.4f} acc_norm={v.get('acc_norm,none','NA')}")
if accs:
    print(f"  AVG acc={sum(accs)/len(accs):.4f}")
PYEOF2
  else
    echo "[FAIL] iter_160000 no results.json" | tee -a "$LOG"
  fi
fi
pkill_server

# Phase 6: Generate refreshed report
echo "[$(date '+%H:%M:%S')] [6/6] === generating scaling report ===" | tee -a "$LOG"
nice -n 19 "$PY" "$REPORT_GEN" 2>&1 | tee -a "$LOG"
echo "[$(date '+%H:%M:%S')] 160k pipeline ALL DONE" | tee -a "$LOG"
