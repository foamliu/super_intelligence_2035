#!/usr/bin/env bash
# baize_eval_100k_autopipeline.sh — 自主轮询 100k ckpt → HF导出 → GGUF → 8集eval → 报告刷新
#
# 在 .12 上 setsid 挂活。每 600s 查 latest_checkpointed_iteration.txt，
# 当训练产出 iter_0100000 后自动完成全链路：
#   NeMo distcp → HF safetensors → 修 config.json → GGUF f16 → llama-server 8集 eval → 刷新 10/10 报告
#
# 用法:
#   setsid nice -n 19 bash baize_eval_100k_autopipeline.sh > /tmp/baize_eval_100k_autopipeline.log 2>&1 &
#
# 纪律: CUDA_VISIBLE_DEVICES="" 全程, OMP=8, nice19, 不碰 GPU/S1训练/他线
set -euo pipefail

# ── 路径常量 ──
BASE_NEMO="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b"
CKPT_DIR="$BASE_NEMO/checkpoints"
HF_OUT="$BASE_NEMO/hf_iter_100000"
GGUF_DIR="/nas_train/app.e0031982/models/baize2b_gguf"
GGUF="$GGUF_DIR/bz2b-100000-f16.gguf"
EVAL_OUT="$BASE_NEMO/lm_eval_results/gguf_iter_100000"
EVAL_OUT_FINAL="$BASE_NEMO/lm_eval_results/gguf_iter_100000_fixed_8set"
DONE_MARKER="/tmp/baize_100k_eval_done.marker"
LOG="/tmp/baize_eval_100k_autopipeline.log"
PY310="/nas_train/app.e0031982/miniforge3/envs/py310/bin/python"
CONVERT_SCRIPT="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/convert_mcore_to_hf.py"
EVAL_DIR="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/pretrain_cpu_eval_gguf"
REPORT_GEN="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/gen_llamacpp_scaling_report.py"
REPORT_OUT="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/reports/report_pretrain_llamacpp_scaling_60k_100k_zh.html"
PORT=8090

# ── 环境（CPU 评测纪律）──
export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=8
export PYTHONPATH="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/p6_tf5:${PYTHONPATH:-}"
export HF_DATASETS_OFFLINE=1
export HF_HUB_OFFLINE=1
export HF_DATASETS_CACHE="/nas_train/app.e0031982/hf_cache"
export HF_HOME="/nas_train/app.e0031982/.cache"

log() { echo "[$(date '+%F %T')] [pipeline] $*" | tee -a "$LOG"; }

# ── 幂等：已完成则退出 ──
if [[ -f "$DONE_MARKER" && -f "$EVAL_OUT_FINAL/results.json" ]]; then
  log "Already done (marker + results.json exist). Exiting."
  exit 0
fi

# ── Phase 1: 轮询 100k ckpt ──
log "=== 100k autopipeline START ==="
log "Polling latest_checkpointed_iteration.txt every 600s (max 144 polls = 24h)"
POLL=0
MAX_POLLS=144
while true; do
  POLL=$((POLL + 1))
  ITER=$(cat "$CKPT_DIR/latest_checkpointed_iteration.txt" 2>/dev/null || echo "0")
  # 去除可能的空白
  ITER=$(echo "$ITER" | tr -d '[:space:]')
  if [[ "$ITER" == "100000" ]]; then
    log "100k checkpoint detected (poll #$POLL)! Verifying directory..."
    if [[ -d "$CKPT_DIR/iter_0100000" ]]; then
      NFILES=$(ls "$CKPT_DIR/iter_0100000/"*.distcp 2>/dev/null | wc -l)
      if [[ "$NFILES" -gt 10 ]]; then
        log "iter_0100000 has $NFILES .distcp files. Proceeding to export."
        break
      else
        log "iter_0100000 exists but only $NFILES .distcp files (incomplete?). Waiting 60s..."
        sleep 60
        continue
      fi
    else
      log "latest_checkpointed_iteration.txt=100000 but iter_0100000 dir missing. Waiting 60s..."
      sleep 60
      continue
    fi
  fi
  if [[ "$POLL" -ge "$MAX_POLLS" ]]; then
    log "TIMEOUT: 100k not produced after $MAX_POLLS polls (24h). Giving up."
    exit 1
  fi
  log "100k not yet (poll #$POLL, current=$ITER). Sleeping 600s..."
  sleep 600
done

# ── Phase 2: NeMo distcp → HF safetensors ──
log "Phase 2: Exporting NeMo ckpt → HF format (convert_mcore_to_hf.py)"
if [[ -f "$HF_OUT/model.safetensors" ]]; then
  log "HF export already exists ($HF_OUT/model.safetensors). Skipping."
else
  nice -n 19 "$PY310" "$CONVERT_SCRIPT" \
    --arch hybrid \
    --ckpt-dir "$CKPT_DIR/iter_0100000" \
    --output-dir "$HF_OUT" 2>&1 | tee -a "$LOG"
  [[ -f "$HF_OUT/model.safetensors" ]] || { log "FAIL: HF export did not produce model.safetensors"; exit 1; }
  log "HF export done. $(ls -lh "$HF_OUT/model.safetensors" | awk '{print $5}')"
fi

# ── Phase 3: 修 config.json（移除 mamba_dt_limit → 避免 GGUF Duplicated key）──
log "Phase 3: Fixing config.json (remove mamba_dt_limit)"
"$PY310" - "$HF_OUT/config.json" <<'PYFIX'
import json, sys
p = sys.argv[1]
cfg = json.load(open(p))
if "mamba_dt_limit" in cfg:
    del cfg["mamba_dt_limit"]
    json.dump(cfg, open(p, "w"), indent=2)
    print(f"  removed mamba_dt_limit from {p}")
else:
    print(f"  mamba_dt_limit not present in {p} (already clean)")
PYFIX
log "Config fix done."

# ── Phase 4: GGUF 转换 + llama-server 8集 eval（04_run_one_ckpt.sh 一条龙）──
log "Phase 4: Running eval pipeline (GGUF convert + 8-set eval, ETA ~74min)"
log "  port=$PORT  threads=16  parallel=4  limit=100  outtype=f16"
bash "$EVAL_DIR/04_run_one_ckpt.sh" 100000 \
  --limit 100 --threads 16 --parallel 4 --port "$PORT" 2>&1 | tee -a "$LOG"
[[ -f "$EVAL_OUT/results.json" ]] || { log "FAIL: eval did not produce results.json at $EVAL_OUT"; exit 1; }
log "Eval done. results.json at $EVAL_OUT ($(wc -c < "$EVAL_OUT/results.json") bytes)"

# ── Phase 5: 重命名输出 → _fixed_8set（与 10k–90k 口径一致）──
log "Phase 5: Renaming output to _fixed_8set"
if [[ -d "$EVAL_OUT_FINAL" ]]; then
  log "$EVAL_OUT_FINAL already exists. Removing old and replacing."
  rm -rf "$EVAL_OUT_FINAL"
fi
mv "$EVAL_OUT" "$EVAL_OUT_FINAL"
log "Renamed to $EVAL_OUT_FINAL"

# ── Phase 6: 刷新 10/10 报告 ──
log "Phase 6: Regenerating 10/10 report (gen_llamacpp_scaling_report.py)"
"$PY310" "$REPORT_GEN" 2>&1 | tee -a "$LOG"
[[ -f "$REPORT_OUT" ]] || { log "FAIL: report not generated at $REPORT_OUT"; exit 1; }
log "Report regenerated: $(wc -c < "$REPORT_OUT") bytes"

# ── Phase 7: Done marker ──
touch "$DONE_MARKER"
log "=== 100k autopipeline COMPLETE ==="
log "  10/10 ckpt report: $REPORT_OUT ($(wc -c < "$REPORT_OUT") bytes)"
log "  results.json: $EVAL_OUT_FINAL/results.json"
log "  GGUF: $GGUF ($(ls -lh "$GGUF" 2>/dev/null | awk '{print $5}' || echo 'N/A'))"
log "  HF: $HF_OUT"
