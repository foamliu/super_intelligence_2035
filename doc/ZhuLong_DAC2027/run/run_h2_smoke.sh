#!/bin/bash
# run_h2_smoke.sh — H2 (sub-agent weak-model + MCP inheritance) confirmation smokes
# Runs TWO 1-task smokes sequentially on the H2 wrapper (cline v3.0.74 + commit 39ccd44cc):
#   S1 backward-compat : NO CLINE_SUBAGENT_* env, NO INHERIT_MCP
#                        expect: sub-agent model = parent (deepseek-v4-pro-cloud), builtin tools only (no "__" MCP names)
#                        => proves default behavior unchanged (backward compatible)
#   S2 weak-model+MCP  : CLINE_SUBAGENT_{PROVIDER_ID,MODEL_ID,API_KEY,BASE_URL}=doubao-pro, INHERIT_MCP=1
#                        expect: sub-agent model = doubao-seed-2.0-pro-cloud, AND sub-agent calls an MCP tool
#                        (name contains "__", e.g. pyAether_MCP_server__search_apis) => proves H2 patch works
# Uses A1 arm dir (anonymous spawn_agent, NO researcher.yaml — pure env-override path).
set -uo pipefail

REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
ARM_DIR="/nasdata/app.e0031982/subagent_ablation/A1"   # anonymous spawn, no agents/ dir
TS=$(date +%Y%m%d_%H%M%S)
MASTER="/tmp/h2_smoke_master_${TS}.log"
EVAL_ROOT="/tmp/zhulong_h2_smoke_eval_${TS}"

# doubao-pro weak-model credentials (verified HTTP 200 on gateway)
export DBO_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f"
export DBO_MODEL="doubao-seed-2.0-pro-cloud"
DBO_BASE="http://agi-gateway.cxmt.com/cloud/v1"

# ---- common env (replicates run_subagent_ablation.sh) ----
export CLI_DATA_DIR="$ARM_DIR"
export CLI_AGENT=cline
export CLINE_COMPACTION="basic"
export CLINE_THINKING="medium"
export CLINE_UNIFIED_DATA_DIR=1
export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"
export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT"
export TASK_FILTER="EDA-Eval-PyAether-001"
export PARALLEL=8
# venv (pydantic) + node-20 (bun) + H2 wrapper FIRST on PATH so `cline` => v3.0.74+patch
export PATH="/tmp/cline-h2/bin:/nasdata/app.e0031982/code/eda_fastmcp/venv/bin:/home/app.e0031982/.local/node-20/bin:${PATH}"
export PYTHON="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
export NO_PROXY="agi-gateway.cxmt.com,10.129.32.75,10.251.36.15,localhost,127.0.0.1"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
# do NOT set CLINE_AGENTS_SRC (A1 anonymous spawn, no configured agent)
unset CLINE_AGENTS_SRC

SUBAGENT_HINT="
## CRITICAL WORKFLOW REQUIREMENT
Before writing any code, you MUST use the \`spawn_agent\` tool to delegate to a researcher sub-agent.
Call \`spawn_agent\` with a systemPrompt describing a pyAether API researcher, and a task asking it to
look up the pyAether APIs relevant to this problem using the search_apis and get_api_details tools.
Do NOT answer directly or write code until the sub-agent returns its findings. This is a mandatory step."
export LANG_HINT="$SUBAGENT_HINT"

# H2 env defaults (cleared per-smoke)
unset CLINE_SUBAGENT_PROVIDER_ID CLINE_SUBAGENT_MODEL_ID CLINE_SUBAGENT_API_KEY CLINE_SUBAGENT_BASE_URL CLINE_SUBAGENT_INHERIT_MCP

run_one_smoke() {
  local SMOKE="$1"      # S1 | S2
  local LOG="/tmp/h2_smoke_${SMOKE}_${TS}.log"
  local SMOKE_EVAL_ROOT="$EVAL_ROOT/${SMOKE}"
  rm -rf "$SMOKE_EVAL_ROOT"; mkdir -p "$SMOKE_EVAL_ROOT"
  export EVAL_ROOT_DIR_OVERRIDE="$SMOKE_EVAL_ROOT"

  echo "[$(date '+%H:%M:%S')] === $SMOKE starting ===" | tee -a "$MASTER"
  if [[ "$SMOKE" == "S1" ]]; then
    unset CLINE_SUBAGENT_PROVIDER_ID CLINE_SUBAGENT_MODEL_ID CLINE_SUBAGENT_API_KEY CLINE_SUBAGENT_BASE_URL CLINE_SUBAGENT_INHERIT_MCP
    echo "  env: CLINE_SUBAGENT_* all UNSET, INHERIT_MCP UNSET (backward-compat)" | tee -a "$MASTER"
  else
    export CLINE_SUBAGENT_PROVIDER_ID="openai-compatible"
    export CLINE_SUBAGENT_MODEL_ID="$DBO_MODEL"
    export CLINE_SUBAGENT_API_KEY="$DBO_KEY"
    export CLINE_SUBAGENT_BASE_URL="$DBO_BASE"
    export CLINE_SUBAGENT_INHERIT_MCP=1
    echo "  env: CLINE_SUBAGENT model=$DBO_MODEL INHERIT_MCP=1" | tee -a "$MASTER"
  fi

  echo "[$(date '+%H:%M:%S')] cline version: $(cline --version 2>&1 | head -1)  which: $(command -v cline)" | tee -a "$MASTER"
  echo "[$(date '+%H:%M:%S')] launching harness (1 task, $SMOKE) -> $LOG" | tee -a "$MASTER"
  cd "$BASE_DIR"
  timeout --signal=TERM --kill-after=120 1500 bash scripts/run_cline_script.sh -p 8 -n >> "$LOG" 2>&1
  local ec=$?
  echo "[$(date '+%H:%M:%S')] $SMOKE harness exit=$ec" | tee -a "$MASTER"
  scan_sessions "$SMOKE" "$SMOKE_EVAL_ROOT"
  echo "[$(date '+%H:%M:%S')] === $SMOKE done ===" | tee -a "$MASTER"
}

scan_sessions() {
  local SMOKE="$1" ROOT="$2"
  echo "[$(date '+%H:%M:%S')] === scanning $SMOKE sessions under $ROOT ===" | tee -a "$MASTER"
  python3 - "$SMOKE" "$ROOT" "$MASTER" <<'PYEOF'
import json, os, sys, glob
from collections import Counter
smoke, root, master = sys.argv[1], sys.argv[2], sys.argv[3]

all_msgs = glob.glob(f"{root}/**/sessions/*/*.messages.json", recursive=True)
# also scan CLI_DATA_DIR sessions (cline --data-dir may store sessions there)
arm = "/nasdata/app.e0031982/subagent_ablation/A1"
all_msgs += glob.glob(f"{arm}/**/sessions/*/*.messages.json", recursive=True)
all_msgs += glob.glob(f"{root}/**/code/**/sessions/*/*.messages.json", recursive=True)

sub_sessions = [f for f in all_msgs if "agent_" in os.path.basename(f)]
main_files = [f for f in all_msgs if "agent_" not in os.path.basename(f)]

def summarize(path, label):
    try:
        d = json.load(open(path))
        msgs = d.get("messages", [])
        model = ""
        for m in msgs:
            mi = m.get("modelInfo", {})
            if mi.get("id"):
                model = f"{mi.get('id')} (provider={mi.get('provider','?')})"
                break
        tc = Counter()
        spawn_inputs = []
        mcp_calls = []
        for m in msgs:
            if m.get("role") == "assistant":
                content = m.get("content", [])
                if not isinstance(content, list): content = []
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "tool_use":
                        tc[b.get("name")] += 1
                        if b.get("name") == "spawn_agent":
                            spawn_inputs.append(b.get("input", {}))
                        if "__" in str(b.get("name", "")):
                            mcp_calls.append(b.get("name"))
        return {
            "n_msgs": len(msgs), "model": model, "tools": dict(tc),
            "spawn_calls": len(spawn_inputs), "mcp_calls": mcp_calls,
            "spawn_inputs": [json.dumps(s, ensure_ascii=False)[:200] for s in spawn_inputs],
        }
    except Exception as e:
        return {"err": str(e)}

with open(master, "a") as f:
    f.write(f"  [{smoke}] total msg files={len(all_msgs)} sub_sessions={len(sub_sessions)} main={len(main_files)}\n")
    for sf in sorted(sub_sessions):
        s = summarize(sf, "SUB")
        f.write(f"  SUB {os.path.basename(sf)}: {json.dumps(s, ensure_ascii=False)}\n")
    for mf in sorted(main_files):
        s = summarize(mf, "MAIN")
        f.write(f"  MAIN {os.path.basename(mf)}: {json.dumps(s, ensure_ascii=False)}\n")

    # verdict
    spawn_called = any(summarize(mf, "M").get("spawn_calls", 0) > 0 for mf in main_files)
    has_sub = any(summarize(sf, "S").get("n_msgs", 0) > 0 for sf in sub_sessions)
    sub_models = [summarize(sf, "S").get("model", "") for sf in sub_sessions]
    sub_mcp = [c for sf in sub_sessions for c in (summarize(sf, "S").get("mcp_calls", []) or [])]
    sub_tools = {t for sf in sub_sessions for t in (summarize(sf, "S").get("tools", {}) or {})}

    if not spawn_called:
        verdict = "INCONCLUSIVE: agent did not call spawn_agent"
    elif not has_sub:
        verdict = "INCONCLUSIVE: spawn called but no sub session"
    else:
        if smoke == "S1":
            if all("deepseek-v4-pro" in m for m in sub_models if m):
                verdict = "BACKWARD_COMPAT_OK: sub=parent(dsv4-pro)"
            else:
                verdict = f"BACKWARD_COMPAT_FAIL: sub_models={sub_models}"
            if sub_tools and any("__" in t for t in sub_tools):
                verdict += " ⚠️ sub has MCP tool names (expected NONE for backward-compat)"
            else:
                verdict += " ✅ sub has no MCP tools (builtin only, unchanged)"
        else:  # S2
            ok_model = any("doubao" in m for m in sub_models)
            ok_mcp = len(sub_mcp) > 0
            verdict = f"WEAK_MODEL={'OK' if ok_model else 'FAIL'} sub_models={sub_models} | MCP_INHERIT={'OK' if ok_mcp else 'NO_CALL'} mcp_calls={sub_mcp}"
            if ok_model and ok_mcp:
                verdict = "H2_OK: sub=doubao AND sub called MCP tool — env-override + MCP forwarding WORK"
            elif ok_model and not ok_mcp:
                verdict = "H2_PARTIAL: sub=doubao (model override OK) but sub did not call MCP tool (INHERIT_MCP=1 set; check tool availability)"
    f.write(f"\n  [{smoke}] VERDICT: {verdict}\n\n")
PYEOF
}

# ===== main =====
mkdir -p "$EVAL_ROOT"
echo "[$(date '+%H:%M:%S')] ===== H2 SMOKE START (wrapper=$(command -v cline) v$(cline --version 2>&1|head -1)) =====" | tee "$MASTER"
echo "[$(date '+%H:%M:%S')] EVAL_FW_DIR=${EVAL_FW_DIR:-<unset>}  TASK_FILTER=$TASK_FILTER  ARM_DIR=$ARM_DIR" | tee -a "$MASTER"

run_one_smoke S1
run_one_smoke S2

echo "[$(date '+%H:%M:%S')] ===== H2 SMOKE ALL DONE =====" | tee -a "$MASTER"
echo "===== master log ====="
cat "$MASTER"
