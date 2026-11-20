#!/bin/bash
# run_r4_grading.sh — 手动跑 r4 grading (Step 5/6 已由 auto-grading 完成, 此为 Step 7.1 run_eval re-grade)
# batch=2026_1011_181038, full config, 4 ports 8650/8651/8652/8654 (remote 10.129.32.75)
# 根因: run_eval.py patch_config() 默认替换 benchmark 为不存在的文件 → 154/158 task "未找到 task_id" → 1.9%
# 修复: --benchmark 覆盖指向 EDA-Eval-pyAether-158.jsonl (158 task) + --lang pyAether
# 先例: r3(batch 2026_1011_145925) 同 bug → re-grade → 122/158 pass(77.2%) ✅
#       r2(batch 2026_1011_083246) 同 bug → re-grade → 125/158 pass(79.1%) ✅
# r4 code-gen stats: success=154 / timeout=4 / failure=0 → 158/158 done, timeout=4≤10 ✅
set -euo pipefail
cd /nasdata/app.e0031982/code/eda_fastmcp
export EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework
set -a; source .env 2>/dev/null || true; set +a
echo "=== R4 RE-GRADE START $(date '+%F %T') ==="
echo "EVAL_FW_DIR=$EVAL_FW_DIR"
echo "SANDBOX_ENDPOINTS=$SANDBOX_ENDPOINTS"
echo "PROXY_PORTS=$PROXY_PORTS"
echo "RAG_RECALL_URL=$RAG_RECALL_URL"
echo "SANDBOX_HOST=${SANDBOX_HOST:-10.129.32.75(default)}"
venv/bin/python scripts/run_eval.py \
  --generations completed_code_generation_2026_1011_181038.jsonl \
  --benchmark benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl \
  --lang pyAether
echo "=== R4 RE-GRADE END $(date '+%F %T') exit=$? ==="
