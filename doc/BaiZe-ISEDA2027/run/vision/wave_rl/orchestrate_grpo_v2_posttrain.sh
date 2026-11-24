#!/usr/bin/env bash
# orchestrate_grpo_v2_posttrain.sh — runs AFTER GRPOv2 training finishes.
# 用户令 2026-11-24 08:5x · P1 collect -> decide adapter -> P2 launch codegen -> P3 report.
# Decision rule (preregistered): if post-GRPOv2 held-out > rft2(0.90) reload :30003 with
# new step500 adapter; else keep rft2 (reproducibility re-run). Either way launch V2-only
# codegen on 36.15 into /tmp/wv_cg_full_v2grpo2 (baseline /tmp/wv_cg_full preserved).
set -uo pipefail
RUN=/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
VQATOOL=$RUN/vision/vqa_tool
V2DIR=$VQATOOL/grpo_mllm_runs_v2
PY=/nas_data/app.e0031982/miniforge3/envs/py310/bin/python
RFT2_ADAPTER=$VQATOOL/strengthen_runs/rft2_adapter_seed11
NEW_ADAPTER=$V2DIR/step500
STATUS=/tmp/grpo_v2_p2_status.json
TRAIN_PID=2486723
log(){ echo "[$(date '+%F %T')] $*"; }

# Guard against duplicate orchestrators (two would double-launch codegen on
# 36.15 into the same /tmp/wv_cg_full_v2grpo2/results.json -> corruption).
LOCK=/tmp/orchestrate_grpo_v2.lock
exec 9>"$LOCK"
if ! flock -n 9; then log "another orchestrator holds lock $LOCK; exit."; exit 0; fi
log "acquired orchestrator lock $LOCK"

log "orchestrator start; waiting for training PID $TRAIN_PID to exit..."
while kill -0 "$TRAIN_PID" 2>/dev/null; do sleep 30; done
log "training PID exited."

# --- decision ---
DEC=$($PY - <<PY
import json,os
v2="$V2DIR"
paired=json.load(open(os.path.join(v2,"grpo_v2_paired_test.json")))
post=paired["post_grpo_acc"]; cold=paired["coldstart_acc"]; verdict=paired.get("verdict","?")
rft=json.load(open("$VQATOOL/strengthen_runs/rft2_seed11_eval.json"))
rft_acc=rft.get("accuracy",0.9)
use_new = bool(post > rft_acc)
adapter = os.path.join(v2,"step500") if use_new else "$RFT2_ADAPTER"
print("\t".join([str(use_new), str(post), str(cold), str(rft_acc), adapter, verdict]))
PY
)
USE_NEW=$(echo "$DEC" | cut -f1)
POST_ACC=$(echo "$DEC" | cut -f2)
COLD_ACC=$(echo "$DEC" | cut -f3)
RFT_ACC=$(echo "$DEC" | cut -f4)
ADAPTER=$(echo "$DEC" | cut -f5)
VERDICT=$(echo "$DEC" | cut -f6)
log "DECISION: use_new=$USE_NEW post=$POST_ACC cold=$COLD_ACC rft=$RFT_ACC verdict=$VERDICT adapter=$ADAPTER"

# --- reload :30003 only if using new adapter ---
SERVER_RELOADED=false
NEW_SRV_PID=""
if [ "$USE_NEW" = "True" ]; then
  log "reloading :30003 with NEW adapter $ADAPTER"
  pkill -f 'qwen35_vqa_server.py --host 0.0.0.0 --port 30003' 2>/dev/null
  sleep 8
  cd "$VQATOOL"
  CUDA_VISIBLE_DEVICES=6 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    setsid $PY qwen35_vqa_server.py --host 0.0.0.0 --port 30003 --gpu 0 --adapter "$ADAPTER" \
    > /tmp/vqa30003_grpo2.log 2>&1 < /dev/null &
  NEW_SRV_PID=$!
  log "new :30003 server PID=$NEW_SRV_PID; waiting health..."
  HEALTH_OK=false
  for i in $(seq 1 60); do
    H=$(curl -s -m 5 http://127.0.0.1:30003/health 2>/dev/null)
    if echo "$H" | grep -q '"ready": true'; then log "health ok: $H"; HEALTH_OK=true; break; fi
    sleep 5
  done
  SERVER_RELOADED=true
  [ "$HEALTH_OK" = "true" ] || log "WARN: :30003 health not ok after reload"
else
  log "keeping rft2 on :30003 (no reload) — reproducibility re-run"
  H=$(curl -s -m 5 http://127.0.0.1:30003/health 2>/dev/null)
  log "existing :30003 health: $H"
fi

# --- launch V2-only codegen on 36.15 (detached) ---
log "launching V2-only codegen on 36.15 (182 cases, ETA ~9-18h, resumable)..."
SSHOUT=$(ssh -p 3333 -o BatchMode=yes -o StrictHostKeyChecking=no app.e0031982@localhost \
  'cd /nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow && setsid bash -c "python3 run_codegen_v2only_grpo2.py > /tmp/wv_cg_v2grpo2_runner.log 2>&1 < /dev/null" & sleep 2; echo LAUNCHED' 2>&1)
log "codegen launch ssh output: $SSHOUT"

# --- P3: update GRPO report §11 ---
log "updating GRPO report §11..."
cd "$VQATOOL"
$PY gen_grpo_v2_report_section.py 2>&1
REPORT_BYTES=$(stat -c %s "$RUN/reports/report_vision_wave_grpo_mllm_result_zh.html")

# --- status ---
cat > "$STATUS" <<EOF
{"use_new_adapter": $USE_NEW, "post_grpo_acc": $POST_ACC, "coldstart_acc": $COLD_ACC, "rft2_acc": $RFT_ACC, "verdict": "$VERDICT", "adapter_used": "$ADAPTER", "server_reloaded": $SERVER_RELOADED, "new_server_pid": "$NEW_SRV_PID", "report_bytes": $REPORT_BYTES, "codegen_launched_on_3615": true, "codegen_runner_log_3615": "/tmp/wv_cg_v2grpo2_runner.log", "codegen_results_3615": "/tmp/wv_cg_full_v2grpo2/results.json", "baseline_preserved_3615": "/tmp/wv_cg_full/results.json", "ts": "$(date -Iseconds)"}
EOF
log "STATUS: $(cat "$STATUS")"
log "ORCHESTRATOR DONE"
