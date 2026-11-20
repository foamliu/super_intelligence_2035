#!/usr/bin/env bash
# bpt_attribution_overnight_chain.sh — 2026-11-14 夜自主执行链 (用户令 21:5x, 明早 09:00 看结果)
# 在 36.15 上串行跑 (共享 .17 GPU6:8096 经反向隧道 18096, --max-num-seqs 4 ⇒ 串行避免 serve 争用):
#   1) Task A 臂 A1 (40q, no_sandbox 提示 + 基线 MCP)        → /tmp/posttrain_attribution_ablation/A1/
#   2) Task A 臂 A3 (40q, no_sandbox 提示 + 沙盒关[移除 eda_flow]) → /tmp/posttrain_attribution_ablation/A3/
#   3) Task B P0 dev baseline (79q, 基线提示 + 基线 MCP)      → /tmp/posttrain_attribution_prompt/baseline_dev/
#   4) Task B P0 dev p0      (79q, P0 工具格式补丁 + 基线 MCP) → /tmp/posttrain_attribution_prompt/p0_dev/
# 纪律: 单变量 · 预注册判据 · 不改 benchmark/check.py/题面 · 反作弊钩子常开.
# 起跑前已人工核验: 无 36.15 baseline eval 在跑 (pgrep run_cline_script 无), 故 dev-eval 用 --skip-status-gate.
set -uo pipefail
RUN_DIR="/nasdata/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"
LOG="/tmp/posttrain_attribution_overnight_chain.log"
echo "=== overnight chain START $(date '+%F %T') ===" > "$LOG"
curl -s -m 8 http://127.0.0.1:18096/v1/models >> "$LOG" 2>&1; echo >> "$LOG"

# --- wait-gate: 等 36.15 baseline run2 (PID 2747266) 释放 GPU6:8096 serve ---
# bpt_eval --run-all chainer (PID 1229657) 已被 kill ⇒ run3-5 不会启动; 仅等 run2 自然结束,
# 避免与 baseline 并跑争用 4-seq serve (会污染单变量消融数据). 最长等 4h, 之后即使仍忙也强行起跑(标注可能争用).
RUN2_PID=2747266
MAX_WAIT=14400; WAITED=0
echo "[gate] waiting for baseline run2 (PID $RUN2_PID) to finish @ $(date '+%F %T')" >> "$LOG"
while kill -0 "$RUN2_PID" 2>/dev/null; do
  sleep 60; WAITED=$((WAITED+60))
  if [ $WAITED -ge $MAX_WAIT ]; then echo "[gate] max-wait ${MAX_WAIT}s reached; proceeding (may contend) @ $(date '+%F %T')" >> "$LOG"; break; fi
done
echo "[gate] run2 cleared (waited=${WAITED}s) @ $(date '+%F %T')" >> "$LOG"
curl -s -m 8 http://127.0.0.1:18096/v1/models >> "$LOG" 2>&1; echo >> "$LOG"

run() { local name="$1"; shift; echo ">>> [$name] $(date '+%F %T')" >> "$LOG"; "$@" >> "$LOG" 2>&1; echo "<<< [$name] rc=$? $(date '+%F %T')" >> "$LOG"; }

run "A1_40q"    bash "$RUN_DIR/bpt_attribution_ablation.sh"        --arm A1
run "A3_40q"    bash "$RUN_DIR/bpt_attribution_ablation.sh"        --arm A3
run "P0_base_dev" bash "$RUN_DIR/bpt_attribution_prompt_dev_eval.sh" --patch baseline --split dev --skip-status-gate
run "P0_p0_dev"   bash "$RUN_DIR/bpt_attribution_prompt_dev_eval.sh" --patch p0      --split dev --skip-status-gate

echo "=== overnight chain DONE $(date '+%F %T') ===" >> "$LOG"
# 汇总各臂 final_report
echo "=== SUMMARY ===" >> "$LOG"
for d in /tmp/posttrain_attribution_ablation/A1 /tmp/posttrain_attribution_ablation/A3 /tmp/posttrain_attribution_prompt/baseline_dev /tmp/posttrain_attribution_prompt/p0_dev; do
  fr="$d/final_report.json"
  if [ -f "$fr" ]; then echo "$d: $(grep -oE '\"pass_rate\"[: ]*[0-9.]+' "$fr" | head -1)" >> "$LOG"; else echo "$d: (无 final_report)" >> "$LOG"; fi
done
