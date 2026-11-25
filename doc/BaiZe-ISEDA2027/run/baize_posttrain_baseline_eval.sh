#!/bin/bash
# baize_posttrain_baseline_eval.sh — Phase 1 基线评测驱动
# 用 EDA-Eval 158 任务，同口径横评模型，5-run mean±std。
# 协议冻结：158 任务 / Pass@1 / 2500s / 单 trace / 5-run / -p 8 -n
# 用法: bash baize_posttrain_baseline_eval.sh --model minicpm5_2b --runs 5
#       bash baize_posttrain_baseline_eval.sh --all --runs 5
#       bash baize_posttrain_baseline_eval.sh --check-env
set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "$(realpath "${BASH_SOURCE[0]}")")" && pwd)"
EDA_FASTMCP_DIR="$HOME/code/eda_fastmcp"
EVAL_SCRIPT="$EDA_FASTMCP_DIR/scripts/run_cline_script.sh"
EVAL_PY="$EDA_FASTMCP_DIR/scripts/run_eval.py"
RESULTS_DIR="$SCRIPT_DIR/baseline_eval_results"
mkdir -p "$RESULTS_DIR"
# name|endpoint|model_id|api_key|label
MODEL_minicpm5_2b="http://localhost:8098/v1|minicpm5-2b|dummy-key|MiniCPM5-2B"
MODEL_qwen3_8_27b="http://localhost:8099/v1|qwen3.8-27b|dummy-key|Qwen3.8-27B"
MODEL_glm_5_2="http://agi-gateway.cxmt.com/cloud/v1|glm-5.2|02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23|GLM-5.2"
ALL_MODELS="minicpm5_2b qwen3_8_27b glm_5_2"
PARALLEL=8; NUM_RUNS=1; DRY_RUN=false; TARGET_MODEL=""; RUN_OFFSET=0
print_info()    { echo -e "\033[36m[INFO]\033[0m $*"; }
print_success() { echo -e "\033[32m[OK]\033[0m $*"; }
print_error()   { echo -e "\033[31m[ERROR]\033[0m $*"; }
print_warn()    { echo -e "\033[33m[WARN]\033[0m $*"; }
usage() { echo "用法: $0 [--model <name>|--all] [--runs N|--run N] [-p N] [--dry-run] [--check-env]"; exit 0; }
get_field() { local var="MODEL_$1"; echo "${!var}" | cut -d'|' -f"$2"; }
check_env() {
    print_info "=== 环境检查 ==="
    local errs=0
    command -v cline &>/dev/null && print_success "cline OK" || { print_error "cline 不在 PATH"; errs=$((errs+1)); }
    [[ -f "$EVAL_SCRIPT" ]] && print_success "eval driver OK" || { print_error "eval driver 缺失"; errs=$((errs+1)); }
    # MCP SSE: head -1 on SSE stream is unreliable (stream may not flush a line
    # before pipe closes); grab first 500 bytes which include "event: endpoint".
    local mcp_resp; mcp_resp=$(curl -s --max-time 5 http://127.0.0.1:18888/sse 2>/dev/null | head -c 500)
    echo "$mcp_resp" | grep -q "endpoint" && print_success "MCP OK" || { print_error "MCP 不可达"; errs=$((errs+1)); }
    local sb_ok=false
    for port in 8664 8665 8653 8669 8667; do
        timeout 5 bash -c "echo > /dev/tcp/10.129.32.75/$port" 2>/dev/null && { print_success "sandbox :$port OK"; sb_ok=true; break; }
    done
    [[ "$sb_ok" == false ]] && { print_error "sandbox 不可达 (所有端口 CLOSED)"; errs=$((errs+1)); }
    for m in $ALL_MODELS; do
        local u; u=$(get_field "$m" 1)
        curl -s --max-time 10 "${u}/models" 2>/dev/null | grep -q model && print_success "$m OK" || print_warn "$m 不可达"
    done
    [[ "$errs" -eq 0 ]] && print_success "环境检查通过 (0 errors)" || print_error "环境检查失败 ($errs errors)"
    return $errs
}
configure_auth() {
    local m="$1" ep mid key
    ep=$(get_field "$m" 1); mid=$(get_field "$m" 2); key=$(get_field "$m" 3)
    print_info "cline auth: $mid @ $ep"
    [[ "$DRY_RUN" == true ]] && return 0
    cline auth -p openai-compatible -k "$key" -m "$mid" -b "$ep" 2>&1 | head -3
    local cfg; cfg=$(python3 -c "import json;print(json.load(open('$HOME/.cline/data/settings/providers.json'))['providers']['openai-compatible']['settings']['model'])" 2>/dev/null)
    [[ "$cfg" == "$mid" ]] && print_success "auth OK: $mid" || { print_error "auth FAIL"; return 1; }
}
run_single_eval() {
    local m="$1" ri="$2" ts label rf
    ts=$(date '+%Y%m%d_%H%M%S'); label="${m}_run${ri}_${ts}"; rf="$RESULTS_DIR/${label}.json"
    print_info "=== 评测: $(get_field "$m" 4) | Run $ri ==="
    if [[ "$DRY_RUN" == true ]]; then
        print_info "  [dry-run] $EVAL_SCRIPT -p $PARALLEL -n + $EVAL_PY --latest 1"
        return 0
    fi
    configure_auth "$m" || return 1
    print_info "Step 1/3: 代码生成 (158任务 -p $PARALLEL -n)"
    cd "$EDA_FASTMCP_DIR"
    PARALLEL=$PARALLEL bash "$EVAL_SCRIPT" -p "$PARALLEL" -n 2>&1 | tee "$RESULTS_DIR/${label}_gen.log"
    print_info "Step 2/3: 评测打分"
    python3 "$EVAL_PY" --latest 1 2>&1 | tee "$RESULTS_DIR/${label}_eval.log"
    print_info "Step 3/3: 收集结果"
    local lr; lr=$(find "$HOME/eda_code_eval" -name "final_report.json" -newer "$RESULTS_DIR" 2>/dev/null | head -1)
    if [[ -n "$lr" && -f "$lr" ]]; then
        cp "$lr" "$rf"; local pr; pr=$(python3 -c "import json;print(json.load(open('$rf')).get('metrics',{}).get('pass_rate','?'))" 2>/dev/null)
        print_success "完成: $label pass_rate=$pr"
    else
        print_error "未找到 final_report.json"; echo '{"error":"no report"}' > "$rf"
    fi
}
aggregate() {
    local m="$1"; print_info "=== $m 汇总 ==="
    python3 -c "
import json,glob,statistics
fs=sorted(glob.glob('$RESULTS_DIR/${m}_run*_*.json'))
rs=[json.load(open(f)).get('metrics',{}).get('pass_rate') for f in fs if '_gen' not in f and '_eval' not in f and 'error' not in json.load(open(f))]
rs=[r for r in rs if r is not None]
for f in sorted(glob.glob('$RESULTS_DIR/${m}_run*_*.json')):
    if '_gen' in f or '_eval' in f: continue
    try: print(f'  {f.split(\"/\")[-1]}: {json.load(open(f))[\"metrics\"][\"pass_rate\"]*100:.2f}%')
    except: pass
if rs: print(f'  mean={statistics.mean(rs)*100:.2f}% std={statistics.stdev(rs)*100:.2f}%' if len(rs)>1 else f'  mean={rs[0]*100:.2f}%')
" 2>&1
}
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --model) TARGET_MODEL="$2"; shift 2;;
            --all) TARGET_MODEL="$ALL_MODELS"; shift;;
            --runs) NUM_RUNS="$2"; shift 2;;
            --run) NUM_RUNS=1; RUN_OFFSET=$(( $2 - 1 )); shift 2;;
            -p) PARALLEL="$2"; shift 2;;
            --dry-run) DRY_RUN=true; shift;;
            --check-env) check_env; exit $?;;
            -h|--help) usage;;
            *) print_error "未知: $1"; usage;;
        esac
    done
}
main() {
    parse_args "$@"
    [[ -z "$TARGET_MODEL" ]] && { print_error "未指定模型"; usage; }
    print_info "Phase1 基线评测 | 模型=$TARGET_MODEL | 轮数=$NUM_RUNS | dry-run=$DRY_RUN"
    for m in $TARGET_MODEL; do
        for ((i=1; i<=NUM_RUNS; i++)); do
            run_single_eval "$m" $((i + RUN_OFFSET)) || print_error "失败: $m run $((i + RUN_OFFSET))"
        done
        aggregate "$m"
    done
    print_success "完毕"
}
main "$@"
