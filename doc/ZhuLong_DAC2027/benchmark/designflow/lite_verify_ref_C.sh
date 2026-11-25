#!/usr/bin/env bash
# lite_verify_ref_C.sh — 用真实 run_one.sh harness judge 验证 reference_submit.zip
# 用法: lite_verify_ref_C.sh <TaskId-001> [<TaskId-001> ...]
# 原理: SKIP_RUN=1 跳过 cline, 但 harness 仍跑 judge (line 350+). 预放 reference_submit.zip
#       到 workdir/outputs/submit.zip, harness 直接判分 (line 340 见 submit.zip 存在则不打包).
set -uo pipefail
BENCH=/nasdata/app.e0031982/code/EDA-Flow-Bench
REF_BASE=$BENCH/benchmarks/EDA-Eval-DesignFlow/reference
CACHE=/nasdata/app.e0031982/.cache/lite_verify_C

for TID in "$@"; do
  FULL=EDA-Eval-DesignFlow-$TID
  REF=$REF_BASE/$FULL
  REFZIP=$REF/reference_submit.zip
  if [ ! -f "$REFZIP" ]; then
    echo "[$TID] SKIP: no reference_submit.zip at $REFZIP"
    continue
  fi
  WDIR=$CACHE/$TID
  rm -rf "$WDIR"; mkdir -p "$WDIR/outputs"
  cp "$REFZIP" "$WDIR/outputs/submit.zip"
  echo "=== [$TID] running real harness judge (SKIP_RUN=1) ==="
  SKIP_RUN=1 SKIP_JUDGE=0 "$BENCH/eval/run_one.sh" "$FULL" --shard C --workdir "$WDIR" \
    --status "$CACHE/status_${TID}.jsonl" 2>&1 | tail -15
  echo "--- status ---"
  tail -1 "$CACHE/status_${TID}.jsonl" 2>/dev/null | python3 -c \
    "import json,sys; d=json.load(sys.stdin); print(f\"verdict={d['verdict']} reason={d.get('reason','')[:200]} fail_stage={d.get('fail_stage','')}\")" 2>/dev/null || echo "(no status)"
  echo
done
