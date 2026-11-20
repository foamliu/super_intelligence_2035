#!/bin/bash
# run_subagent_smokeA_harness.sh — confirmatory smoke-A via HARNESS (验根因 + 修复)
# 条件 = P1 B1 (B1 config + 强 subagent 提示 + compaction basic + thinking medium + -p 8)
# 唯一差异: 1 题 (vs P1 8 题) + run_cli.sh agent 路径修复 (.cline/agents/ → agents/)
# fresh data-dir /tmp/subagent_smoke_A2 (不动 B1 dir)
# 预注册通过: 子 agent session n_msgs>0 且 metrics.inputTokens>0
set -uo pipefail

REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
SMOKE_DIR="/tmp/subagent_smoke_A2"
EVAL_ROOT="/tmp/zhulong_subagent_eval_smokeA2"
SMOKE_LOG="/tmp/subagent_smokeA2.log"
B1_DIR="/nasdata/app.e0031982/subagent_ablation/B1"
TASK_ID="EDA-Eval-PyAether-001"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

log "=== smoke-A harness 启动 (-p 8, 1 题, agent 路径修复) ==="

rm -rf "$SMOKE_DIR"
mkdir -p "$SMOKE_DIR/settings" "$SMOKE_DIR/agents"
cp "$B1_DIR/settings/providers.json"        "$SMOKE_DIR/settings/"
cp "$B1_DIR/settings/cline_mcp_settings.json" "$SMOKE_DIR/settings/" 2>/dev/null || true
cp "$B1_DIR/settings/models.json"           "$SMOKE_DIR/settings/" 2>/dev/null || true
cp "$B1_DIR/settings/global-settings.json"  "$SMOKE_DIR/settings/" 2>/dev/null || true
cp "$B1_DIR/agents/researcher.yaml"          "$SMOKE_DIR/agents/"
cp "$B1_DIR/secrets.json"                    "$SMOKE_DIR/" 2>/dev/null || true
cp "$B1_DIR/globalState.json"                "$SMOKE_DIR/" 2>/dev/null || true
log "fresh data-dir = $SMOKE_DIR (B1 config, agents/ path)"

export CLI_AGENT=cline
export PYTHON="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
export PATH="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin:$PATH"
export CLI_DATA_DIR="$SMOKE_DIR"
export CLINE_COMPACTION="basic"
export CLINE_THINKING="medium"
export CLINE_AGENTS_SRC="$SMOKE_DIR/agents"
export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-PyAether-158.jsonl"
export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT"
export TASK_FILTER="$TASK_ID"
export PARALLEL=8

export LANG_HINT="
## 重要：工作流程要求
在写代码之前，你**必须**先调用 \`spawn_agent\` 工具，委托 \"researcher\" 子 agent 查询本任务涉及的所有 pyAether API 文档。拿到 API 文档摘要后，再开始写代码。这是强制步骤。"

mkdir -p "$EVAL_ROOT"
log "launching run_cline_script.sh -p 8 -n (1 task=$TASK_ID) -> $SMOKE_LOG"
: > "$SMOKE_LOG"
cd "$BASE_DIR"
timeout --signal=TERM --kill-after=60 1500 bash scripts/run_cline_script.sh -p 8 -n >> "$SMOKE_LOG" 2>&1
EC=$?
log "harness exit=$EC"

log "=== 扫描子 agent session (trace + worker data-dirs) ==="
"$BASE_DIR/venv/bin/python" - "$EVAL_ROOT" "$BASE_DIR" <<'PYEOF'
import json, glob, os, sys
eval_root, base_dir = sys.argv[1], sys.argv[2]
search = [eval_root, os.path.join(base_dir, "cli_data")]
sub_files = []
for base in search:
    if not os.path.isdir(base): continue
    for f in glob.glob(os.path.join(base, "**", "agent_*.messages.json"), recursive=True):
        sub_files.append(f)
print(f"found {len(sub_files)} subagent session file(s)")
any_pass = False
for f in sub_files:
    try:
        d = json.load(open(f))
        msgs = d if isinstance(d, list) else d.get("messages", d)
        n = len(msgs)
        max_itok = 0; model = None
        for m in msgs:
            if isinstance(m, dict):
                mt = m.get("metrics", {})
                if isinstance(mt, dict) and mt.get("inputTokens", 0) > 0:
                    max_itok = max(max_itok, mt.get("inputTokens", 0))
                mi = m.get("modelInfo", {})
                if isinstance(mi, dict) and mi.get("id"): model = mi.get("id")
        ok = n > 0 and max_itok > 0
        any_pass = any_pass or ok
        print(f"  {os.path.basename(f)}: n_msgs={n} maxInputTokens={max_itok} model={model} -> {'✅PASS' if ok else 'check'}")
    except Exception as e:
        print(f"  {f}: ERROR {e}")
# also check main session for spawn_agent tool registration
main_files = [f for f in glob.glob(os.path.join(eval_root, "**", "*.messages.json"), recursive=True) if "/agent_" not in f]
spawn_seen = False
for f in main_files:
    try:
        txt = open(f).read()
        if "spawn_agent" in txt and "AI_NoSuchToolError" not in txt:
            spawn_seen = True
    except: pass
print(f"\nmain sessions: {len(main_files)} | spawn_agent called without error: {spawn_seen}")
print("SMOKE-A HARNESS:", "✅ PASS — subagent executed via harness" if any_pass else "❌ FAIL — subagent did not execute")
PYEOF

log "=== smoke-A harness 完成 ==="
