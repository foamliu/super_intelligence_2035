#!/bin/bash
# baize_posttrain_postSFT_eval.sh — Post-SFT EDA-Eval-PyAether 评测驱动
#
# 用途：用 v11v38 SFT ckpt (minicpm5-2b-sft) 跑 EDA-Eval 158 任务评测，
#       对比 baseline 36% Pass@1，验证 SFT data gap coverage 改善（目标 M1=50%）。
#
# 冻结协议（总纲 §2，🚫 不得改动）：158 任务 / Pass@1 / 2500s/任务 / 单 trace / -p 8 -n
# 本脚本默认 1-run（快速验证）；5-run 需多次调用或用 --runs 5。
#
# 架构：cline(on .17) → model(:8097 SFT) → MCP(:18888) → sandbox(localhost:8664 via SSH -L tunnel → 36.15)
#
# 用法：
#   bash baize_posttrain_postSFT_eval.sh              # 1-run 全量 158 任务
#   bash baize_posttrain_postSFT_eval.sh --runs 5     # 5-run（长时间）
#   bash baize_posttrain_postSFT_eval.sh --dry-run     # 打印配方不执行
#   bash baize_posttrain_postSFT_eval.sh --smoke       # 2-task 冒烟测试
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$(realpath "${BASH_SOURCE[0]}")")" && pwd)"
EDA_FASTMCP_DIR="$HOME/code/eda_fastmcp"
EVAL_SCRIPT="$EDA_FASTMCP_DIR/scripts/run_cline_script.sh"
EVAL_PY="$EDA_FASTMCP_DIR/scripts/run_eval.py"
VENV_PY="$EDA_FASTMCP_DIR/.venv/bin/python"
RESULTS_DIR="$SCRIPT_DIR/baseline_eval_results"
mkdir -p "$RESULTS_DIR"

# 模型配置
MODEL_ENDPOINT="http://localhost:8097/v1"
MODEL_ID="minicpm5-2b-sft"
API_KEY="dummy-key"
LABEL="postSFT_minicpm5_2b_sft"

# 冻结协议参数
PARALLEL=8
NUM_RUNS=1
DRY_RUN=false
SMOKE=false

print_info()    { echo -e "\033[36m[INFO]\033[0m $*"; }
print_success() { echo -e "\033[32m[OK]\033[0m $*"; }
print_error()   { echo -e "\033[31m[ERROR]\033[0m $*"; }

while [[ $# -gt 0 ]]; do
    case "$1" in
        --runs) NUM_RUNS="$2"; shift 2;;
        --dry-run) DRY_RUN=true; shift;;
        --smoke) SMOKE=true; shift;;
        -h|--help) echo "用法: $0 [--runs N] [--dry-run] [--smoke]"; exit 0;;
        *) print_error "未知: $1"; exit 1;;
    esac
done

print_info "=== Post-SFT EDA-Eval-PyAether 评测 ==="
print_info "  模型: $MODEL_ID @ $MODEL_ENDPOINT"
print_info "  轮数: $NUM_RUNS | 并行: $PARALLEL | dry-run=$DRY_RUN | smoke=$SMOKE"
print_info "  venv python: $VENV_PY ($($VENV_PY --version 2>&1))"
print_info "  冻结协议: 158任务 / Pass@1 / 2500s / 单trace / -p $PARALLEL -n"

if [[ "$DRY_RUN" == true ]]; then
    print_info "[dry-run] 配方已打印，不执行。"
    exit 0
fi

# 前置检查
command -v cline &>/dev/null || { print_error "cline 不在 PATH"; exit 1; }
[[ -f "$EVAL_SCRIPT" ]] || { print_error "eval driver 缺失: $EVAL_SCRIPT"; exit 1; }
[[ -f "$EVAL_PY" ]] || { print_error "eval scorer 缺失: $EVAL_PY"; exit 1; }
[[ -x "$VENV_PY" ]] || { print_error "venv python 缺失: $VENV_PY"; exit 1; }
curl -s -m 5 "$MODEL_ENDPOINT/models" | grep -q model || { print_error "模型端点不可达: $MODEL_ENDPOINT"; exit 1; }
print_success "前置检查通过"

# 配置 cline auth
print_info "cline auth → $MODEL_ID @ $MODEL_ENDPOINT"
cline auth -p openai-compatible -k "$API_KEY" -m "$MODEL_ID" -b "$MODEL_ENDPOINT" 2>&1 | head -3

# 设置环境
export PYTHON="$VENV_PY"
export PATH="$EDA_FASTMCP_DIR/.venv/bin:$HOME/.bun/bin:$PATH"
export CLI_AGENT=cline

TASK_FILTER=""
[[ "$SMOKE" == true ]] && TASK_FILTER="-t 001,002"

for ((run=1; run<=NUM_RUNS; run++)); do
    TS=$(date '+%Y%m%d_%H%M%S')
    RUN_LABEL="${LABEL}_run${run}_${TS}"
    print_info "=== Run $run/$NUM_RUNS @ $(date '+%T') ==="

    cd "$EDA_FASTMCP_DIR"
    print_info "Step 1/2: 代码生成 (158任务 -p $PARALLEL -n)"
    PARALLEL=$PARALLEL bash "$EVAL_SCRIPT" $TASK_FILTER -p "$PARALLEL" -n 2>&1 | tee "$RESULTS_DIR/${RUN_LABEL}_gen.log"
    GEN_RC=${PIPESTATUS[0]}

    print_info "Step 2/2: 评测打分 (--latest 1)"
    "$VENV_PY" "$EVAL_PY" --latest 1 2>&1 | tee "$RESULTS_DIR/${RUN_LABEL}_eval.log"

    # 收集 final_report.json
    LATEST_REPORT=$(find "$HOME/eda_code_eval" -name "final_report.json" -newer "$RESULTS_DIR/${RUN_LABEL}_gen.log" 2>/dev/null | head -1)
    if [[ -n "$LATEST_REPORT" && -f "$LATEST_REPORT" ]]; then
        cp "$LATEST_REPORT" "$RESULTS_DIR/${RUN_LABEL}.json"
        PASS_RATE=$("$VENV_PY" -c "import json;print(json.load(open('$RESULTS_DIR/${RUN_LABEL}.json')).get('metrics',{}).get('pass_rate','?'))" 2>/dev/null)
        print_success "Run $run 完成: pass_rate=$PASS_RATE (report: $RESULTS_DIR/${RUN_LABEL}.json)"
    else
        print_error "Run $run: 未找到 final_report.json"
        echo '{"error":"no report","run":'$run'}' > "$RESULTS_DIR/${RUN_LABEL}.json"
    fi
done

# 汇总
print_info "=== 汇总 ==="
"$VENV_PY" - "$RESULTS_DIR" "$LABEL" "$NUM_RUNS" <<'PYEOF' 2>&1
import json, sys, glob, statistics
results_dir, label, num_runs = sys.argv[1], sys.argv[2], int(sys.argv[3])
rates = []
for f in sorted(glob.glob(f"{results_dir}/{label}_run*_*.json")):
    if '_gen' in f or '_eval' in f:
        continue
    try:
        d = json.load(open(f))
        if 'error' in d:
            print(f"  {f.split('/')[-1]}: ERROR")
            continue
        r = d.get('metrics', {}).get('pass_rate')
        if r is not None:
            rates.append(float(r))
            print(f"  {f.split('/')[-1]}: pass_rate={float(r)*100:.2f}%")
    except Exception as e:
        print(f"  {f.split('/')[-1]}: parse fail: {e}")
if rates:
    mean = statistics.mean(rates)
    std = statistics.stdev(rates) if len(rates) > 1 else 0.0
    print(f"\n  n_runs={len(rates)}  pass@1 mean={mean*100:.2f}%  std={std*100:.2f}%")
    print(f"  baseline=36.00%  M1=50.00%  delta_vs_baseline={(mean-0.36)*100:+.2f}pp")
else:
    print("  ⚠️ 无可用 pass_rate")
PYEOF
print_success "评测完毕"
