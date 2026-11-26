#!/bin/bash
# run_h2_smoke.sh — ZhuLong H2 ablation smoke (cline v3.0.74 + env-driven sub-agent model override)
#
# 🔴 用户令 2026-11-14 17:0x: H2 恢复 — 改 cline 源码 (commit 39ccd44cc) 让 spawn_agent 的子 agent
#   通过 env var 用弱模型 + 继承 MCP 工具。本脚本验证：
#   ① 向后兼容: 不设 CLINE_SUBAGENT_* → 子 agent 仍继承父模型 (deepseek-v4-pro-cloud), 行为同 3.0.51
#   ② 弱模型覆盖: 设 CLINE_SUBAGENT_MODEL_ID=deepseek-v4-flash → 子 agent 模型 = flash
#   ③ MCP 转发: CLINE_SUBAGENT_INHERIT_MCP=1 → 子 agent 获得 pyAether MCP 工具
#
# 用法:
#   MODE=bcompat  bash run_h2_smoke.sh   # 向后兼容 (无 env override)
#   MODE=weak     bash run_h2_smoke.sh   # 弱模型 + MCP 转发
#
# 1 题 (EDA-Eval-PyAether-001), v3.0.74 via bun, A2 verifier hint (triggers spawn_agent)
# 产物落 /tmp/h2_smoke_<mode>/ · 不影响 A1/A2 结果 · 不覆盖 3.0.51 全局 cline
set -euo pipefail

REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"

MODE="${MODE:-bcompat}"
H2_DIR="/nasdata/app.e0031982/subagent_ablation/H2"
SUBSET_FILE="/tmp/h2_smoke_subset.txt"   # EDA-Eval-PyAether-001
EVAL_ROOT="/tmp/h2_smoke_${MODE}_eval"
TRACE_DIR="/tmp/h2_smoke_${MODE}_trace"
ROUND_LOG="/tmp/h2_smoke_${MODE}.log"
MASTER_LOG="/tmp/h2_smoke_${MODE}_master.log"

# v3.0.74 wrapper (bun-based, separate path — does NOT touch global 3.0.51)
export PATH="/home/app.e0031982/.local/bin/h2:$PATH"

# harness env (same as A2, all arms constant)
export CLI_AGENT=cline
export CLI_DATA_DIR="$H2_DIR"
export CLINE_COMPACTION="basic"
export CLINE_THINKING="medium"
export CLINE_UNIFIED_DATA_DIR=1
export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"
export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT"
export SUBSET_FILE
export PARALLEL=1
export PYTHON="${PYTHON:-/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python}"

# A2 verifier hint (triggers spawn_agent after code written, before submit)
SUBAGENT_HINT_A2_FILE="$REPO_RUN/subagent_hint_a2.txt"
export LANG_HINT="$(cat "$SUBAGENT_HINT_A2_FILE")"

# 🔑 reset providers.json each run (cline auto-migration overwrites)
python3 -c "
import json
template = json.load(open('/nasdata/app.e0031982/compaction_ablation/basic/settings/providers.json'))
json.dump(template, open('$H2_DIR/settings/providers.json', 'w'), ensure_ascii=False, indent=2)
print('providers.json reset from compaction basic template')
" 2>>"$MASTER_LOG"

# verify parent model
if ! grep -q 'deepseek-v4-pro-cloud' "$H2_DIR/settings/providers.json"; then
  echo "❌ providers.json missing dsv4-pro-cloud parent" | tee -a "$MASTER_LOG"
  exit 1
fi

# H2 env vars per mode
if [[ "$MODE" == "weak" ]]; then
  # 弱模型: deepseek-v4-flash (weaker than parent dsv4-pro-cloud)
  export CLINE_SUBAGENT_PROVIDER_ID="openai-compatible"
  export CLINE_SUBAGENT_MODEL_ID="deepseek-v4-flash"
  export CLINE_SUBAGENT_API_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_c43c1f4a-03c6-4148-b722-f4c8604c78d3"
  export CLINE_SUBAGENT_BASE_URL="http://agi-gateway.cxmt.com/v1"
  export CLINE_SUBAGENT_INHERIT_MCP="1"
  echo "[$(date '+%H:%M:%S')] MODE=weak: sub-agent override = deepseek-v4-flash + MCP inherit" | tee -a "$MASTER_LOG"
elif [[ "$MODE" == "bcompat" ]]; then
  # 向后兼容: NO env override → sub-agent inherits parent (dsv4-pro-cloud), no MCP forwarding
  unset CLINE_SUBAGENT_PROVIDER_ID CLINE_SUBAGENT_MODEL_ID CLINE_SUBAGENT_API_KEY CLINE_SUBAGENT_BASE_URL CLINE_SUBAGENT_INHERIT_MCP || true
  echo "[$(date '+%H:%M:%S')] MODE=bcompat: no CLINE_SUBAGENT_* env → sub-agent inherits parent (dsv4-pro-cloud)" | tee -a "$MASTER_LOG"
else
  echo "❌ unknown MODE=$MODE (use bcompat|weak)" >&2
  exit 1
fi

# verify cline version
echo "[$(date '+%H:%M:%S')] cline version: $(cline --version 2>&1 | head -1)" | tee -a "$MASTER_LOG"

# clean previous smoke artifacts
rm -rf "$EVAL_ROOT" "$TRACE_DIR"
mkdir -p "$EVAL_ROOT" "$TRACE_DIR"

# launch 1-question eval (foreground, 2h cap)
echo "[$(date '+%H:%M:%S')] launching 1-question smoke -> $ROUND_LOG" | tee -a "$MASTER_LOG"
: > "$ROUND_LOG"
cd "$BASE_DIR"
timeout --signal=TERM --kill-after=120 7200 bash scripts/run_cline_script.sh -p 1 -n >> "$ROUND_LOG" 2>&1
exit_code=$?
echo "[$(date '+%H:%M:%S')] smoke finished exit=$exit_code" | tee -a "$MASTER_LOG"

# archive trace
batch_dir=$(ls -td "$EVAL_ROOT"/*/ 2>/dev/null | head -1)
if [[ -n "${batch_dir:-}" ]]; then
  cp -a "$batch_dir" "$TRACE_DIR/" 2>/dev/null || true
  echo "[$(date '+%H:%M:%S')] trace archived -> $TRACE_DIR/$(basename "${batch_dir%/}")" | tee -a "$MASTER_LOG"
fi

echo "[$(date '+%H:%M:%S')] DONE. Inspect sub-session messages.json for model name:" | tee -a "$MASTER_LOG"
echo "  find $TRACE_DIR -name 'agent_*.messages.json' -exec python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(sys.argv[1], \"model=\", d.get(\"modelInfo\",{}).get(\"id\",\"?\"), \"n_msgs=\", len(d.get(\"messages\",[])))' {} \;" | tee -a "$MASTER_LOG"
