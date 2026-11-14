#!/bin/bash
# run_h2_smoke_S2.sh — H2 smoke S2 ONLY: weak-model (doubao-pro) + MCP inheritance (INHERIT_MCP=1)
# Expect: sub-agent model = doubao-seed-2.0-pro-cloud, AND sub-agent calls an MCP tool (name contains "__")
set -uo pipefail
REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
ARM_DIR="/nasdata/app.e0031982/subagent_ablation/A1"
TS=$(date +%Y%m%d_%H%M%S)
MASTER="/tmp/h2_smoke_S2_master_${TS}.log"
EVAL_ROOT="/tmp/zhulong_h2_smoke_S2_eval_${TS}"

# ---- env (replicates run_subagent_ablation.sh + H2 weak-model override) ----
export CLI_DATA_DIR="$ARM_DIR"
export CLI_AGENT=cline
export CLINE_COMPACTION="basic"
export CLINE_THINKING="medium"
export CLINE_UNIFIED_DATA_DIR=1
export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"
export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT"
export TASK_FILTER="EDA-Eval-PyAether-001"
export PARALLEL=8
export PATH="/tmp/cline-h2/bin:/nasdata/app.e0031982/code/eda_fastmcp/venv/bin:/home/app.e0031982/.local/node-20/bin:${PATH}"
export PYTHON="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
export NO_PROXY="agi-gateway.cxmt.com,10.129.32.75,10.251.36.15,localhost,127.0.0.1"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
unset CLINE_AGENTS_SRC
# H2 weak-model override: doubao-pro
export CLINE_SUBAGENT_PROVIDER_ID="openai-compatible"
export CLINE_SUBAGENT_MODEL_ID="doubao-seed-2.0-pro-cloud"
export CLINE_SUBAGENT_API_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f"
export CLINE_SUBAGENT_BASE_URL="http://agi-gateway.cxmt.com/cloud/v1"
export CLINE_SUBAGENT_INHERIT_MCP=1

export LANG_HINT="
## CRITICAL WORKFLOW REQUIREMENT
Before writing any code, you MUST use the \`spawn_agent\` tool to delegate to a researcher sub-agent.
Call \`spawn_agent\` with a systemPrompt describing a pyAether API researcher, and a task asking it to
look up the pyAether APIs relevant to this problem using the search_apis and get_api_details tools.
Do NOT answer directly or write code until the sub-agent returns its findings. This is a mandatory step."

LOG="/tmp/h2_smoke_S2_${TS}.log"
rm -rf "$EVAL_ROOT"; mkdir -p "$EVAL_ROOT"
echo "[$(date '+%H:%M:%S')] === H2 SMOKE S2 (weak=doubao-pro + INHERIT_MCP=1) ===" | tee "$MASTER"
echo "  cline=$(command -v cline) v$(cline --version 2>&1|head -1)  sub_model=$CLINE_SUBAGENT_MODEL_ID  INHERIT_MCP=$CLINE_SUBAGENT_INHERIT_MCP" | tee -a "$MASTER"

cd "$BASE_DIR"
echo "[$(date '+%H:%M:%S')] launching harness (1 task) -> $LOG" | tee -a "$MASTER"
timeout --signal=TERM --kill-after=120 1500 bash scripts/run_cline_script.sh -p 8 -n >> "$LOG" 2>&1
ec=$?
echo "[$(date '+%H:%M:%S')] harness exit=$ec" | tee -a "$MASTER"

echo "[$(date '+%H:%M:%S')] === scanning S2 sessions ===" | tee -a "$MASTER"
python3 - "$EVAL_ROOT" "$ARM_DIR" "$MASTER" <<'PYEOF'
import json, glob, os, sys
from collections import Counter
root, arm, master = sys.argv[1], sys.argv[2], sys.argv[3]
files=set()
for r in (root, arm):
    files.update(glob.glob(f"{r}/**/sessions/*/*.messages.json", recursive=True))
sub=sorted(f for f in files if "agent_" in os.path.basename(f))
main=sorted(f for f in files if "agent_" not in os.path.basename(f))

def scan(f):
    try:
        d=json.load(open(f, errors="replace"))
    except: return {"err":"load"}
    msgs=d.get("messages",[])
    if not isinstance(msgs,list): msgs=[]
    model=""
    for m in msgs:
        mi=m.get("modelInfo",{}) or {}
        if mi.get("id"):
            model=f"{mi.get('id')}|{mi.get('provider','?')}"; break
    tc=Counter()
    for m in msgs:
        if m.get("role")=="assistant":
            c=m.get("content")
            if isinstance(c,list):
                for b in c:
                    if isinstance(b,dict) and b.get("type")=="tool_use": tc[b.get("name","")]+=1
    return {"n":len(msgs),"model":model,"tools":dict(tc),"mcp":[t for t in tc if "__" in t]}

with open(master,"a") as out:
    out.write(f"sub={len(sub)} main={len(main)}\n")
    sub_models=[]; sub_mcp=[]
    for f in sub:
        s=scan(f)
        out.write(f"  SUB {os.path.basename(f)[:24]}: {json.dumps(s,ensure_ascii=False)}\n")
        if s.get("n",0)>0:
            sub_models.append(s.get("model",""))
            sub_mcp+=s.get("mcp",[])
    for f in main:
        s=scan(f)
        out.write(f"  MAIN {os.path.basename(f)[:24]}: {json.dumps(s,ensure_ascii=False)}\n")
    ok_model=any("doubao" in m for m in sub_models)
    ok_mcp=len(sub_mcp)>0
    out.write(f"\n  sub_models(non-empty)={sub_models}\n  sub_mcp_calls={sub_mcp}\n")
    if ok_model and ok_mcp:
        verdict=f"H2_OK: sub=doubao AND sub called MCP tool {sub_mcp} — env-override + MCP forwarding WORK"
    elif ok_model:
        verdict=f"H2_PARTIAL: sub=doubao (model OK) but no MCP tool call (INHERIT_MCP=1 set; sub may not have used MCP)"
    else:
        verdict=f"H2_FAIL: sub_models={sub_models} (expected doubao)"
    out.write(f"  [S2] VERDICT: {verdict}\n")
PYEOF
echo "[$(date '+%H:%M:%S')] === S2 done ===" | tee -a "$MASTER"
cat "$MASTER"
