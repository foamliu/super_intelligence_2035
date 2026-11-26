#!/bin/bash
# smoke-B1-unified — 验证 wake#925 Option B 修复 (CLINE_UNIFIED_DATA_DIR=1, -p8)
# 预期: 无 e.trim + subagent 执行 + subagent model=deepseek-v4-pro-cloud + main agent=dsv4-pro
# 通过条件: ≥1 subagent session n_msgs>0 且 model=deepseek-v4-pro-cloud 且 main model 含 deepseek-v4-pro
set -uo pipefail
REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
ARM_DIR="/nasdata/app.e0031982/subagent_ablation/B1"
EVAL_ROOT="/tmp/zhulong_subagent_eval_smokeB1uni"
TS=$(date +%H%M%S)
LOG="/tmp/subagent_smokeB1uni_${TS}.log"
MASTER="/tmp/subagent_smokeB1uni_master.log"

echo "[$(date +%H:%M:%S)] === smoke-B1-unified 启动 (Option B: CLINE_UNIFIED_DATA_DIR=1, -p8) ===" | tee "$MASTER"

# fresh eval root
rm -rf "$EVAL_ROOT"; mkdir -p "$EVAL_ROOT"

# 重写 providers.json (cline auto-migration 防护)
python3 "$REPO_RUN/setup_subagent_arm_dirs.py" --arm B1 --providers-only 2>>"$MASTER" || true

# 1 题子集
TASK_FILE=/tmp/subagent_smokeB1uni_subset.txt
echo "EDA-Eval-PyAether-001" > "$TASK_FILE"
TASK_FILTER="EDA-Eval-PyAether-001"

export CLI_DATA_DIR="$ARM_DIR"
export CLI_AGENT=cline
export CLINE_COMPACTION="basic"
export CLINE_THINKING="medium"
export CLINE_AGENTS_SRC="$ARM_DIR/agents"
export CLINE_UNIFIED_DATA_DIR=1
export EVAL_BENCHMARK="benchmarks/EDA-Eval-pyAether/EDA-Eval-pyAether-158.jsonl"
export EVAL_ROOT_DIR_OVERRIDE="$EVAL_ROOT"
export TASK_FILTER
export PARALLEL
# venv (pydantic) + node (cline) + 直连内部 gateway (不走代理)
export PATH="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin:/home/app.e0031982/.local/node-20/bin:$PATH"
export PYTHON="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
export NO_PROXY="agi-gateway.cxmt.com,10.129.32.75,localhost,127.0.0.1"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY=8
export LANG_HINT="
## 重要：工作流程要求
在写代码之前，你**必须**先调用 \`subagent_researcher\` 工具，让它查询本任务涉及的所有 pyAether API 文档。拿到 API 文档摘要后，再开始写代码。这是强制步骤。"

cd "$BASE_DIR"
echo "[$(date +%H:%M:%S)] launching run_cline_script.sh -p 8 -n (1 task, CLINE_UNIFIED_DATA_DIR=1) -> $LOG" | tee -a "$MASTER"
timeout --signal=TERM --kill-after=120 900 bash scripts/run_cline_script.sh -p 8 -n >> "$LOG" 2>&1
ec=$?
echo "[$(date +%H:%M:%S)] harness exit=$ec" | tee -a "$MASTER"

echo "[$(date +%H:%M:%S)] === 扫描 subagent session ===" | tee -a "$MASTER"
python3 - "$EVAL_ROOT" "$MASTER" <<'PYEOF'
import json, os, sys, glob
eval_root = sys.argv[1]; master = sys.argv[2]
sub_sessions = glob.glob(f"{eval_root}/**/agent_*.messages.json", recursive=True)
main_files = glob.glob(f"{eval_root}/**/trace/**/*.messages.json", recursive=True)
main_files = [s for s in main_files if "agent_" not in os.path.basename(s)]
results = []
for sf in sub_sessions:
    try:
        d = json.load(open(sf))
        msgs = d.get("messages",[])
        mi = ""
        for m in msgs:
            if "modelInfo" in m and m["modelInfo"].get("id"): mi = m["modelInfo"]["id"]; break
        inp = 0
        for m in msgs:
            if "metrics" in m: inp = max(inp, m["metrics"].get("inputTokens",0))
        results.append((sf, len(msgs), mi, inp))
    except Exception as e:
        results.append((sf, "ERR", str(e), 0))
with open(master,"a") as f:
    f.write(f"found {len(sub_sessions)} subagent session file(s)\n")
    main_models=set(); etrim=False; spawn_called=False; subagent_researcher_called=False
    for mf in main_files:
        try:
            d = json.load(open(mf))
            for m in d.get("messages",[]):
                if "modelInfo" in m and m["modelInfo"].get("id"): main_models.add(m["modelInfo"]["id"])
                c = m.get("content",[])
                if isinstance(c,list):
                    for b in c:
                        if isinstance(b,dict):
                            nm=b.get("name","")
                            if b.get("type")=="tool_use":
                                if nm=="spawn_agent": spawn_called=True
                                if nm=="subagent_researcher": subagent_researcher_called=True
                            if b.get("type")=="tool_result":
                                ct = json.dumps(b.get("content",""))
                                if "e.trim" in ct: etrim=True
        except: pass
    for sf,n,mi,inp in results:
        status = "PASS" if (isinstance(n,int) and n>0 and mi and "deepseek-v4-pro" in mi) else "check"
        f.write(f"  {os.path.basename(sf)}: n_msgs={n} model={mi} maxInputTokens={inp} -> {status}\n")
    f.write(f"main models: {main_models} | spawn_agent={spawn_called} | subagent_researcher={subagent_researcher_called} | e.trim={etrim}\n")
    ok_sub = any(isinstance(n,int) and n>0 and mi and "deepseek-v4-pro" in mi for _,n,mi,_ in results)
    ok_main = any("deepseek-v4-pro" in mm for mm in main_models)
    ok_etrim = not etrim
    verdict = "PASS" if (ok_sub and ok_main and ok_etrim) else "FAIL"
    f.write(f"SMOKE-B1-UNIFIED: {verdict} (sub_dsv4={ok_sub} main_dsv4={ok_main} no_etrim={ok_etrim})\n")
PYEOF
echo "[$(date +%H:%M:%S)] === smoke-B1-unified 完成 ===" | tee -a "$MASTER"
echo "=== master log ==="
cat "$MASTER"
