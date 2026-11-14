#!/bin/bash
# run_subagent_smokeA.sh — confirmatory smoke-A (验根因 A: -p 8 并发竞态)
# 复制 P1 B1 条件 (B1 config + 强 subagent 提示 + compaction basic + thinking medium)
# 唯一差异: -p 1 (串行) + 1 题, 用 fresh data-dir /tmp/subagent_smoke_A (不动 B1 dir)
# 预注册通过条件: 子 agent session n_msgs>0 且 usage.inputTokens>0 且 finishReason=completed
set -uo pipefail

REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
SMOKE_DIR="/tmp/subagent_smoke_A"
EVAL_ROOT="/tmp/zhulong_subagent_eval_smokeA"
SMOKE_LOG="/tmp/subagent_smokeA.log"
B1_DIR="/nasdata/app.e0031982/subagent_ablation/B1"
TASK_ID="EDA-Eval-PyAether-001"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

log "=== smoke-A 启动 (验根因A: -p1 串行 vs P1 -p8 并发) ==="

# 1. fresh data-dir, 复制 B1 config (逐字节 = smoke 3074b)
rm -rf "$SMOKE_DIR"
mkdir -p "$SMOKE_DIR/settings" "$SMOKE_DIR/agents"
cp "$B1_DIR/settings/providers.json"        "$SMOKE_DIR/settings/"
cp "$B1_DIR/settings/cline_mcp_settings.json" "$SMOKE_DIR/settings/" 2>/dev/null || true
cp "$B1_DIR/settings/models.json"           "$SMOKE_DIR/settings/" 2>/dev/null || true
cp "$B1_DIR/settings/global-settings.json"  "$SMOKE_DIR/settings/" 2>/dev/null || true
cp "$B1_DIR/agents/researcher.yaml"          "$SMOKE_DIR/agents/"
cp "$B1_DIR/secrets.json"                    "$SMOKE_DIR/" 2>/dev/null || true
cp "$B1_DIR/globalState.json"                "$SMOKE_DIR/" 2>/dev/null || true
log "fresh data-dir = $SMOKE_DIR (B1 config copied)"

# 2. 环境变量 (逐项对齐 run_subagent_ablation.sh run_round B1)
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
export PARALLEL=1

# 强 subagent 提示 (B1 注入, = run_subagent_ablation.sh SUBAGENT_HINT)
export LANG_HINT="
## 重要：工作流程要求
在写代码之前，你**必须**先调用 \`subagent_researcher\` 工具，让它查询本任务涉及的所有 pyAether API 文档。拿到 API 文档摘要后，再开始写代码。这是强制步骤。"

# 3. 启动 harness (1 题, -p 1, 20min cap)
mkdir -p "$EVAL_ROOT"
log "launching run_cline_script.sh -p 1 -n (1 task=$TASK_ID) -> $SMOKE_LOG"
: > "$SMOKE_LOG"
cd "$BASE_DIR"
timeout --signal=TERM --kill-after=60 1200 bash scripts/run_cline_script.sh -p 1 -n >> "$SMOKE_LOG" 2>&1
EC=$?
log "harness exit=$EC"

# 4. 扫描 cline sessions 找子 agent session
log "=== 扫描子 agent session ==="
"$BASE_DIR/venv/bin/python" - "$SMOKE_DIR" "$EVAL_ROOT" <<'PYEOF'
import json, glob, os, sys
smoke_dir, eval_root = sys.argv[1], sys.argv[2]
found_sub = False
# search smoke_dir/sessions and eval_root worker dirs for agent_*.messages.json
search_dirs = [
    os.path.join(smoke_dir, "sessions"),
    eval_root,
]
sub_files = []
for base in search_dirs:
    if not os.path.isdir(base): continue
    for f in glob.glob(os.path.join(base, "**", "agent_*.messages.json"), recursive=True):
        sub_files.append(f)
print(f"found {len(sub_files)} subagent session file(s)")
for f in sub_files:
    try:
        d = json.load(open(f))
        msgs = d if isinstance(d, list) else d.get("messages", d)
        n = len(msgs)
        usage = None; fr = None
        for m in msgs:
            if isinstance(m, dict):
                if "usage" in m: usage = m["usage"]
                if "finishReason" in m: fr = m["finishReason"]
        itok = (usage or {}).get("inputTokens", 0) if isinstance(usage, dict) else 0
        print(f"  FILE: {f}")
        print(f"  n_msgs={n}  inputTokens={itok}  finishReason={fr}")
        # pre-registered pass criteria
        if n > 0 and itok > 0 and fr == "completed":
            print("  ✅ PASS (subagent truly executed)")
        else:
            print("  ❌ FAIL (subagent did not execute)")
    except Exception as e:
        print(f"  {f}: ERROR {e}")
if not sub_files:
    # also check main session count
    main_files = glob.glob(os.path.join(smoke_dir, "sessions", "*", "*.messages.json"))
    main_files = [f for f in main_files if "/agent_" not in f]
    print(f"(no subagent files; main session files: {len(main_files)})")
    for f in main_files[:3]:
        d = json.load(open(f))
        msgs = d if isinstance(d, list) else d.get("messages", d)
        print(f"  main {os.path.basename(f)}: n_msgs={len(msgs)}")
PYEOF

log "=== smoke-A 完成 ==="
