#!/bin/bash
# smoke-B3-spawnagent — 决定性实验: anonymous spawn_agent 子 agent 用 researcher.yaml modelId 还是 providers.json 默认?
# B3 配置: researcher.yaml modelId=doubao-seed-2.0-pro-cloud, providers.json 默认=dsv4-pro (lastUsedProvider=openai-compatible)
#   子=dsv4-pro → anonymous spawn 子=主模型 (H2 基座梯度不可行)
#   子=doubao-pro → anonymous spawn 读 researcher.yaml modelId (H2 可行!)
# 通过条件: ≥1 spawn_agent 调用 + ≥1 子 session n_msgs>0 + 报告子 session model
set -uo pipefail
REPO_RUN="/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run"
BASE_DIR="/nasdata/app.e0031982/code/eda_fastmcp"
ARM_DIR="/nasdata/app.e0031982/subagent_ablation/B3"
EVAL_ROOT="/tmp/zhulong_subagent_eval_smokeB3sp"
TS=$(date +%H%M%S)
LOG="/tmp/subagent_smokeB3sp_${TS}.log"
MASTER="/tmp/subagent_smokeB3sp_master.log"

echo "[$(date +%H:%M:%S)] === smoke-B3-spawnagent 启动 (B3 doubao-pro researcher + dsv4-pro providers 默认) ===" | tee "$MASTER"

# fresh eval root
rm -rf "$EVAL_ROOT"; mkdir -p "$EVAL_ROOT"

# 重写 providers.json + researcher.yaml (cline auto-migration 防护)
python3 "$REPO_RUN/setup_subagent_arm_dirs.py" --arm B3 --providers-only 2>>"$MASTER" || true

# 1 题子集
TASK_FILE=/tmp/subagent_smokeB3sp_subset.txt
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
export PARALLEL=8
# venv (pydantic) + node (cline) + 直连内部 gateway (不走代理)
export PATH="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin:/home/app.e0031982/.local/node-20/bin:$PATH"
export PYTHON="/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python"
export NO_PROXY="agi-gateway.cxmt.com,10.129.32.75,localhost,127.0.0.1"
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY

# 🔑 关键改动: LANG_HINT 用 spawn_agent 措辞 (复刻 smoke 3074b 成功 prompt), 不是 subagent_researcher
export LANG_HINT="
## CRITICAL WORKFLOW REQUIREMENT
Before writing any code, you MUST use the \`spawn_agent\` tool to delegate to a researcher sub-agent.
Call \`spawn_agent\` with a systemPrompt describing a pyAether API researcher, and a task asking it to
look up the pyAether APIs relevant to this problem using the search_apis and get_api_details tools.
Do NOT answer directly or write code until the sub-agent returns its findings. This is a mandatory step."

cd "$BASE_DIR"
echo "[$(date +%H:%M:%S)] launching run_cline_script.sh -p 8 -n (1 task, B3 spawn_agent smoke) -> $LOG" | tee -a "$MASTER"
timeout --signal=TERM --kill-after=120 900 bash scripts/run_cline_script.sh -p 8 -n >> "$LOG" 2>&1
ec=$?
echo "[$(date +%H:%M:%S)] harness exit=$ec" | tee -a "$MASTER"

echo "[$(date +%H:%M:%S)] === 扫描 subagent session + 模型 ===" | tee -a "$MASTER"
python3 - "$EVAL_ROOT" "$MASTER" <<'PYEOF'
import json, os, sys, glob
eval_root = sys.argv[1]; master = sys.argv[2]

# 找所有 session messages (主 + 子)
all_msgs = glob.glob(f"{eval_root}/**/sessions/*/*.messages.json", recursive=True)
sub_sessions = [f for f in all_msgs if "agent_" in os.path.basename(f)]
main_files = [f for f in all_msgs if "agent_" not in os.path.basename(f)]

with open(master,"a") as f:
    f.write(f"found {len(sub_sessions)} subagent session(s), {len(main_files)} main session(s)\n")

    # 子 session 模型 (关键!)
    for sf in sorted(sub_sessions):
        try:
            d = json.load(open(sf))
            msgs = d.get("messages",[])
            mi = ""
            for m in msgs:
                minfo = m.get("modelInfo",{})
                if minfo.get("id"): mi = f"{minfo.get('id')} (provider={minfo.get('provider','?')})"; break
            # 统计 tool_use
            from collections import Counter
            tc = Counter()
            for m in msgs:
                if m.get("role")=="assistant":
                    for b in (m.get("content",[]) if isinstance(m.get("content"),list) else []):
                        if isinstance(b,dict) and b.get("type")=="tool_use": tc[b.get("name")]+=1
            f.write(f"  SUB {os.path.basename(sf)}: n_msgs={len(msgs)} model={mi} tools={dict(tc)}\n")
        except Exception as e:
            f.write(f"  SUB {os.path.basename(sf)}: ERR {e}\n")

    # 主 session: model + spawn_agent 调用 + e.trim
    for mf in sorted(main_files):
        try:
            d = json.load(open(mf))
            msgs = d.get("messages",[])
            main_model = ""
            for m in msgs:
                minfo = m.get("modelInfo",{})
                if minfo.get("id"): main_model = f"{minfo.get('id')} (provider={minfo.get('provider','?')})"; break
            from collections import Counter
            tc = Counter()
            spawn_inputs = []
            etrim = False
            for m in msgs:
                if m.get("role")=="assistant":
                    for b in (m.get("content",[]) if isinstance(m.get("content"),list) else []):
                        if isinstance(b,dict) and b.get("type")=="tool_use":
                            tc[b.get("name")]+=1
                            if b.get("name")=="spawn_agent":
                                spawn_inputs.append(b.get("input",{}))
                if m.get("role")=="user":
                    for b in (m.get("content",[]) if isinstance(m.get("content"),list) else []):
                        if isinstance(b,dict) and b.get("type")=="tool_result":
                            ct = json.dumps(b.get("content",""))
                            if "e.trim" in ct: etrim = True
            f.write(f"  MAIN {os.path.basename(mf)}: n_msgs={len(msgs)} model={main_model}\n")
            f.write(f"    tools={dict(tc)} spawn_agent_calls={len(spawn_inputs)} e.trim={etrim}\n")
            for i,si in enumerate(spawn_inputs):
                f.write(f"    spawn_agent[{i}] input: {json.dumps(si,ensure_ascii=False)[:300]}\n")
        except Exception as e:
            f.write(f"  MAIN {os.path.basename(mf)}: ERR {e}\n")

    # 判定
    sub_models = []
    for sf in sub_sessions:
        try:
            d = json.load(open(sf))
            for m in d.get("messages",[]):
                minfo = m.get("modelInfo",{})
                if minfo.get("id"): sub_models.append(minfo.get("id")); break
        except: pass

    spawn_called = any("spawn_agent" in json.dumps(json.load(open(mf)).get("messages",[]),ensure_ascii=False) for mf in main_files)
    has_sub = len(sub_sessions) > 0 and any(
        len(json.load(open(sf)).get("messages",[])) > 0 for sf in sub_sessions
    )

    if not spawn_called:
        verdict = "INCONCLUSIVE (agent did not call spawn_agent)"
    elif not has_sub:
        verdict = "INCONCLUSIVE (spawn_agent called but no sub session created)"
    else:
        if any("doubao" in sm for sm in sub_models):
            verdict = "H2_FEASIBLE: subagent uses researcher.yaml modelId (doubao) — base gradient IS possible"
        elif all("deepseek-v4-pro" in sm for sm in sub_models if sm):
            verdict = "H2_NOT_FEASIBLE: subagent uses main model (dsv4-pro) — base gradient NOT possible via anonymous spawn"
        else:
            verdict = f"UNCLEAR: sub models = {sub_models}"
    f.write(f"\nSMOKE-B3-SPAWNAGENT VERDICT: {verdict}\n")
PYEOF
echo "[$(date +%H:%M:%S)] === smoke-B3-spawnagent 完成 ===" | tee -a "$MASTER"
echo "=== master log ==="
cat "$MASTER"
