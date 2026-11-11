#!/usr/bin/env bash
# baize_posttrain_phase1_launch.sh — Phase 1 基线评测：3 模型横评启动 + 预检
#
# 用途（用户令 2026-11-10 13:40 Phase 1）：
#   用 EDA-Eval-PyAether 158 任务，同口径横评三个模型，5-run mean±std。
#   ① MiniCPM5-2B  (vLLM  GPU4  :8098)
#   ② Qwen3.8-27B  (SGLang GPU0-3 :8099, root 占用不可动)
#   ③ DeepSeek 云端 (agi-gateway :glm-5.2 替身)
#
# 关键架构发现（2026-11-12 wake301 实测）：
#   - 代码 *生成* (run_cline_script.sh + cline + 模型端点) 可在 .17 本地跑（无需沙盒）。
#   - 代码 *评分* (run_eval.py → run_on_sandbox.py → 10.129.32.75:8664) 需要：
#       (a) 远程沙盒网络可达  — .17 跨子网 TCP 全端口被 ACL 过滤（106th wake 仍阻塞）
#       (b) EDA-Eval-Framework 在本机存在 (EVAL_FW_DIR, 含 run_on_sandbox.py/assemble/calculate)
#                              — .17 上不存在（~/20260806/ 缺失, NFS 无, env 空）
#       (c) pyAether 可 import — .17 上未安装（system python3 3.8.10, ModuleNotFoundError）
#     ⇒ 从 .17 只能跑 --generate；--score/--full 必须在沙盒同子网且有 framework 的机器上跑。
#
# 冻结协议（总纲 §2，🚫 不得改动）：158 任务 / Pass@1 / 2500s/任务 / 单 trace / 5-run / -p 8 -n。
# 反作弊：PreToolUse hook 全程开；报告 cheat rate。污染：158 任务不得进训练集。
#
# 用法：
#   bash baize_posttrain_phase1_launch.sh --preflight           # 预检所有前提（不跑任何评测）
#   bash baize_posttrain_phase1_launch.sh --generate --model minicpm5-2b   # 仅生成（.17 可跑）
#   bash baize_posttrain_phase1_launch.sh --score   --model minicpm5-2b     # 仅评分（需沙盒+framework）
#   bash baize_posttrain_phase1_launch.sh --full    --model minicpm5-2b     # 生成+评分
#   bash baize_posttrain_phase1_launch.sh --full    --model all             # 三模型全跑
#   bash baize_posttrain_phase1_launch.sh --score-existing 11-10            # 评分已存在的 11-10 生成集
set -uo pipefail

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"
source "$SCRIPT_DIR/baize_posttrain_paths.sh"

EDA_BASE="$BAIZE_EDA_BASE"
DRIVER="$EDA_BASE/scripts/run_cline_script.sh"
EVAL_PY="$EDA_BASE/scripts/run_eval.py"
DATASET="$EDA_BASE/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
EVAL_ROOT="${EVAL_ROOT_DIR:-$HOME/eda_code_eval}"
EVAL_FW_DIR="${EVAL_FW_DIR:-$HOME/20260806/EDA-Eval-Framework}"
OUT_BASE="$BAIZE_EXP_DIR/baize_posttrain_phase1"

N_RUNS=5; TASK_TIMEOUT=2500; PARALLEL=8; N_TASKS=158

# --- 模型端点注册表（单一事实源）-------------------------------------------
# 格式: MODEL_ID|ENDPOINT|API_KEY|CLI_AUTH_MODEL|描述
declare -a MODELS=(
  "minicpm5-2b|http://localhost:8098/v1|sk-placeholder|minicpm5-2b|vLLM MiniCPM5-2B GPU4"
  "qwen3.8-27b|http://localhost:8099/v1|sk-placeholder|qwen3.8-27b|root SGLang Qwen3.8-27B GPU0-3"
  "glm-5.2|http://agi-gateway.cxmt.com/cloud/v1|02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23|glm-5.2|DeepSeek云端替身(agi-gateway)"
)

# 沙盒配置（来自 eda_fastmcp/.env，此处显式列出供预检）
SANDBOX_HOST="${SANDBOX_HOST:-10.129.32.75}"
SANDBOX_PORTS=(8664 8665 8653 8669)
SANDBOX_URL_PATH="${SANDBOX_URL_PATH:-v1/run_code}"

ACTION=""; MODEL_SEL="minicpm5-2b"; SCORE_EXISTING_TAG=""
while [ $# -gt 0 ]; do
  case "$1" in
    --preflight) ACTION="preflight" ;;
    --generate)  ACTION="generate" ;;
    --score)     ACTION="score" ;;
    --full)      ACTION="full" ;;
    --score-existing) ACTION="score_existing"; SCORE_EXISTING_TAG="${2:-11-10}"; shift ;;
    --model) MODEL_SEL="$2"; shift ;;
    --out-base) OUT_BASE="$2"; shift ;;
    -h|--help)
      sed -n '2,30p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "未知参数: $1（--help 看用法）" ;;
  esac
  shift
done

[ -z "$ACTION" ] && { echo "❌ 必须指定动作: --preflight / --generate / --score / --full / --score-existing"; exit 1; }

# ───────────────────────── 预检 ─────────────────────────
preflight() {
  echo "===== Phase 1 PREFLIGHT @ $(date '+%F %T') ====="
  local pass=0 fail=0 warn=0
  local json_file="$OUT_BASE/preflight_$(date +%s).json"
  mkdir -p "$OUT_BASE"
  {
    echo "{"
    echo "  \"timestamp\": \"$(date -Iseconds)\","
    echo "  \"node\": \"$(hostname)\","
    echo "  \"checks\": ["

  # 1. 158-case 数据集
  local c1="PASS"
  if [ -f "$DATASET" ]; then
    local n; n=$(wc -l < "$DATASET")
    [ "$n" -eq 158 ] || { c1="FAIL(n=$n)"; ((fail++)); }
    [ "$c1" = "PASS" ] && ((pass++))
  else c1="FAIL(missing)"; ((fail++)); fi
  echo "    {\"check\":\"dataset_158\",\"status\":\"$c1\",\"path\":\"$DATASET\"},"

  # 2. driver
  local c2; [ -f "$DRIVER" ] && { c2="PASS"; ((pass++)); } || { c2="FAIL"; ((fail++)); }
  echo "    {\"check\":\"driver\",\"status\":\"$c2\",\"path\":\"$DRIVER\"},"

  # 3. scorer
  local c3; [ -f "$EVAL_PY" ] && { c3="PASS"; ((pass++)); } || { c3="FAIL"; ((fail++)); }
  echo "    {\"check\":\"scorer\",\"status\":\"$c3\",\"path\":\"$EVAL_PY\"},"

  # 4. cline
  local c4; command -v cline >/dev/null 2>&1 && { c4="PASS($(cline --version 2>/dev/null | head -1))"; ((pass++)); } || { c4="FAIL"; ((fail++)); }
  echo "    {\"check\":\"cline\",\"status\":\"$c4\"},"

  # 5. 3 模型端点
  echo "    {\"check\":\"model_endpoints\",\"items\":["
  local first_ep=1
  for entry in "${MODELS[@]}"; do
    IFS='|' read -r mid ep key authmod desc <<< "$entry"
    local st; curl -s -m 5 "$ep/models" -H "Authorization: Bearer $key" >/dev/null 2>&1 && { st="UP"; ((pass++)); } || { st="DOWN"; ((fail++)); }
    [ $first_ep -eq 0 ] && echo ","
    printf '      {"model":"%s","endpoint":"%s","status":"%s","desc":"%s"}' "$mid" "$ep" "$st" "$desc"
    first_ep=0
  done
  echo ""
  echo "    ]},"

  # 6. 沙盒可达性（4 端口）
  echo "    {\"check\":\"sandbox\",\"host\":\"$SANDBOX_HOST\",\"ports\":["
  local first_sb=1
  for p in "${SANDBOX_PORTS[@]}"; do
    local s; timeout 4 bash -c "echo > /dev/tcp/$SANDBOX_HOST/$p" 2>/dev/null && s="OPEN" || s="FILTERED"
    [ $first_sb -eq 0 ] && echo ","
    printf '      {"port":%s,"status":"%s"}' "$p" "$s"
    first_sb=0
    [ "$s" = "FILTERED" ] && ((fail++)) || ((pass++))
  done
  echo ""
  echo "    ]},"

  # 7. ICMP
  local c7; ping -c 1 -W 2 "$SANDBOX_HOST" >/dev/null 2>&1 && { c7="UP"; ((pass++)); } || { c7="DOWN"; ((fail++)); }
  echo "    {\"check\":\"sandbox_icmp\",\"status\":\"$c7\"},"

  # 8. EDA-Eval-Framework
  local c8; [ -d "$EVAL_FW_DIR" ] && [ -f "$EVAL_FW_DIR/run_on_sandbox.py" ] && { c8="PRESENT"; ((pass++)); } || { c8="ABSENT"; ((fail++)); }
  echo "    {\"check\":\"eval_framework\",\"status\":\"$c8\",\"path\":\"$EVAL_FW_DIR\"},"

  # 9. pyAether
  local c9; python3 -c 'import pyAether' 2>/dev/null && { c9="INSTALLED"; ((pass++)); } || { c9="NOT_INSTALLED"; ((fail++)); }
  echo "    {\"check\":\"pyAether\",\"status\":\"$c9\"},"

  # 10. 已有未评分生成集（扫描所有 completed 文件，找 158 行的）
  local c10="NONE"
  local existing_gen=""
  local comp_file
  for comp_file in $(ls -t "$EVAL_ROOT"/completed_code_generation_*.jsonl 2>/dev/null); do
    local n; n=$(wc -l < "$comp_file" 2>/dev/null)
    if [ "${n:-0}" -eq 158 ]; then
      local tag; tag=$(basename "$comp_file" | sed 's/completed_code_generation_//; s/.jsonl//')
      c10="FOUND($tag,158tasks,unscored)"; existing_gen="$comp_file"; ((warn++)); break
    fi
  done
  echo "    {\"check\":\"existing_unscored_generation\",\"status\":\"$c10\",\"path\":\"$existing_gen\"}"

  echo "  ],"
  echo "  \"summary\": {\"pass\":$pass,\"fail\":$fail,\"warn\":$warn}"
  echo "}"
  } > "$json_file"

  # 人类可读汇总
  echo "----- 预检汇总 -----"
  echo "  dataset(158)    : $([ -f "$DATASET" ] && wc -l < "$DATASET" || echo MISSING)"
  echo "  driver          : $([ -f "$DRIVER" ] && echo OK || echo MISSING)"
  echo "  scorer          : $([ -f "$EVAL_PY" ] && echo OK || echo MISSING)"
  echo "  cline           : $(command -v cline >/dev/null 2>&1 && cline --version 2>/dev/null | head -1 || echo MISSING)"
  for entry in "${MODELS[@]}"; do
    IFS='|' read -r mid ep key authmod desc <<< "$entry"
    local st; curl -s -m 5 "$ep/models" -H "Authorization: Bearer $key" >/dev/null 2>&1 && st="UP" || st="DOWN"
    echo "  endpoint $mid : $st  ($desc)"
  done
  local sb_open=0
  for p in "${SANDBOX_PORTS[@]}"; do timeout 4 bash -c "echo > /dev/tcp/$SANDBOX_HOST/$p" 2>/dev/null && sb_open=1; done
  echo "  sandbox($SANDBOX_HOST) : $([ $sb_open -eq 1 ] && echo REACHABLE || echo 'FILTERED(ACL阻塞)')"
  echo "  eval_framework  : $([ -d "$EVAL_FW_DIR" ] && echo PRESENT || echo 'ABSENT(.17无,需沙盒侧机器)')"
  echo "  pyAether        : $(python3 -c 'import pyAether' 2>/dev/null && echo INSTALLED || echo 'NOT_INSTALLED(.17无)')"
  echo "  existing unscored gen : $c10"
  echo ""
  echo "  PASS=$pass  FAIL=$fail  WARN=$warn"
  echo "  报告: $json_file"
  echo ""
  if [ $sb_open -eq 1 ] && [ -d "$EVAL_FW_DIR" ]; then
    echo "✅ 沙盒可达 + framework 在位 → 可跑 --full / --score"
  elif [ $sb_open -eq 1 ]; then
    echo "🟡 沙盒可达但 framework 缺失 → 只能 --generate（评分需在有 framework 的机器上跑）"
  else
    echo "🔴 沙盒不可达 → 从本节点只能 --generate；评分需沙盒 ACL 恢复 + framework"
  fi
  echo "===== PREFLIGHT END ====="
}

# ───────────────────────── 单模型评测 ─────────────────────────
# 参数: model_entry  action(generate|score|full)
run_one_model() {
  local entry="$1"; local act="$2"
  IFS='|' read -r mid ep key authmod desc <<< "$entry"
  local out_dir="$OUT_BASE/$mid"
  mkdir -p "$out_dir"
  echo "[phase1] model=$mid endpoint=$ep action=$act @ $(date '+%T')"

  # cline auth（生成+评分都需要）
  if [ "$act" = "generate" ] || [ "$act" = "full" ]; then
    command -v cline >/dev/null 2>&1 || { echo "❌ cline 不在 PATH"; return 1; }
    echo "  [auth] cline auth -p openai -b $ep -m $authmod"
    cline auth -p openai -k "$key" -b "$ep" -m "$authmod" || { echo "❌ cline auth 失败 ($mid)"; return 1; }
  fi

  local sum="$out_dir/eval_summary.txt"
  echo "===== Phase1 $mid 5-run START @ $(date '+%F %T') =====" | tee "$sum"

  for run in $(seq 1 "$N_RUNS"); do
    local rd="$out_dir/run_${run}"; mkdir -p "$rd"
    local gen="$rd/generated.jsonl"; local rep="$rd/final_report.json"

    if [ "$act" = "generate" ] || [ "$act" = "full" ]; then
      echo "  [run $run/$N_RUNS] generate @ $(date '+%T')"
      bash "$DRIVER" -p "$PARALLEL" -n --timeout "$TASK_TIMEOUT" \
        > "$rd/driver.log" 2>&1 || { echo "  ❌ run $run 生成失败 (见 $rd/driver.log)"; continue; }
      local latest; latest=$(ls -dt "$EVAL_ROOT"/2026_* 2>/dev/null | head -1)
      [ -n "$latest" ] && cp "$EVAL_ROOT/completed_code_generation_$(basename "$latest").jsonl" "$gen" 2>/dev/null || true
    fi

    if [ "$act" = "score" ] || [ "$act" = "full" ]; then
      [ -f "$gen" ] || { echo "  ❌ run $run 无生成文件, 跳过评分"; continue; }
      [ -d "$EVAL_FW_DIR" ] || { echo "  ❌ EDA-Eval-Framework 缺失 ($EVAL_FW_DIR) — 评分需在沙盒侧机器跑"; continue; }
      echo "  [run $run/$N_RUNS] score @ $(date '+%T')"
      EVAL_ROOT_DIR="$EVAL_ROOT" EVAL_FW_DIR="$EVAL_FW_DIR" python "$EVAL_PY" -g "$gen" --out "$rep" \
        > "$rd/eval.log" 2>&1 || { echo "  ❌ run $run 评分失败 (见 $rd/eval.log)"; continue; }
      local pr; pr=$(python3 -c "import json;d=json.load(open('$rep'));print(d.get('pass_rate',d.get('pass@1','N/A')))" 2>/dev/null)
      echo "  run $run: pass@1=$pr" | tee -a "$sum"
    fi
  done

  python3 - "$out_dir" "$mid" <<'PYEOF' | tee -a "$sum"
import json, sys, glob, statistics
out_dir, mid = sys.argv[1], sys.argv[2]
rates = []
for rp in sorted(glob.glob(f"{out_dir}/run_*/final_report.json")):
    try:
        d = json.load(open(rp)); r = d.get("pass_rate", d.get("pass@1"))
        if r is not None: rates.append(float(r) if isinstance(r,(int,float)) else float(str(r).rstrip('%')))
    except Exception as e: print(f"  parse fail {rp}: {e}")
if rates:
    m = statistics.mean(rates); s = statistics.pstdev(rates) if len(rates)>1 else 0.0
    print(f"===== AGGREGATE {mid} =====")
    print(f"  n_runs={len(rates)} pass@1 mean={m:.2f}% std={s:.2f}% runs={rates}")
else:
    print(f"  ⚠️ {mid}: 无可用 pass_rate（评分未跑/沙盒阻塞?）")
PYEOF
  echo "===== Phase1 $mid END @ $(date '+%F %T') =====" | tee -a "$sum"
}

# ───────────────────────── 主分发 ─────────────────────────
case "$ACTION" in
  preflight) preflight ;;
  generate|score|full)
    if [ "$MODEL_SEL" = "all" ]; then
      for entry in "${MODELS[@]}"; do run_one_model "$entry" "$ACTION"; done
    else
      found=0
      for entry in "${MODELS[@]}"; do
        IFS='|' read -r mid _ _ _ _ <<< "$entry"
        [ "$mid" = "$MODEL_SEL" ] && { run_one_model "$entry" "$ACTION"; found=1; break; }
      done
      [ $found -eq 0 ] && { echo "❌ 未知 model: $MODEL_SEL（可选: minicpm5-2b / qwen3.8-27b / glm-5.2 / all）"; exit 1; }
    fi
    ;;
  score_existing)
    [ -d "$EVAL_FW_DIR" ] || { echo "❌ EDA-Eval-Framework 缺失 — 评分需在沙盒侧机器跑"; exit 1; }
    echo "[phase1] score-existing tag=$SCORE_EXISTING_TAG"
    for entry in "${MODELS[@]}"; do
      IFS='|' read -r mid _ _ authmod _ <<< "$entry"
      gen=$(ls "$EVAL_ROOT"/completed_code_generation_*${SCORE_EXISTING_TAG}*.jsonl 2>/dev/null | head -1)
      [ -f "$gen" ] || { echo "  ⏭ $mid: 无匹配生成集 ($SCORE_EXISTING_TAG), 跳过"; continue; }
      out_dir="$OUT_BASE/$mid/score_existing_${SCORE_EXISTING_TAG}"; mkdir -p "$out_dir"
      echo "  [$mid] 评分 $gen"
      EVAL_ROOT_DIR="$EVAL_ROOT" EVAL_FW_DIR="$EVAL_FW_DIR" python "$EVAL_PY" -g "$gen" --out "$out_dir/final_report.json" \
        > "$out_dir/eval.log" 2>&1 || echo "  ❌ $mid 评分失败"
    done
    ;;
esac
