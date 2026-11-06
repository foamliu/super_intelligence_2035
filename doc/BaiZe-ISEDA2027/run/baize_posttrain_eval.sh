#!/usr/bin/env bash
# baize_posttrain_eval.sh — BaiZe Stage(ii) 步骤 3：EDA-Eval-PyAether 评测脚本骨架
#
# 用途：在冻结协议下评测 BaiZe 各阶段 ckpt（base/anneal/SFT/RL），复用 harness 线的 driver + 评分，只换 backbone（论文 §5.5）。
#
# 冻结协议（总纲 §2，🚫 不得改动）：158 任务 / Pass@1 / 2500s/任务 / 单 trace / 5 次独立运行(reshuffled, fresh context) / -p 8 -n。
#
# 评测关键资产（总纲 §3）：
#   - driver   : /nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh
#   - 评分     : /nasdata/app.e0031982/code/eda_fastmcp/scripts/run_eval.py
#   - 158 集   : eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl
#   - BASE_DIR : /nasdata/app.e0031982/code/eda_fastmcp
#   - BaiZe 接入: vLLM/SGLang OpenAI-compatible endpoint → cline auth -p openai -k <KEY> -b <BASE_URL> -m <MODEL_ID>
#
# 对照：污染由 n-gram 黑名单排除；只换 backbone，检索栈/沙盒/anti-cheat/agent 脚手架逐字节一致。
# 统计：mean ± std (5-run)；两系统比较用 McNemar / paired bootstrap；预注册 M1–M4 先定后测。
#
# 用法：
#   bash baize_posttrain_eval.sh --dry-run
#   bash baize_posttrain_eval.sh --dry-run --backbone baize-rl --endpoint http://127.0.0.1:8000/v1
#   bash baize_posttrain_eval.sh --backbone baize-rl --endpoint http://127.0.0.1:8000/v1 --key <KEY> --model <MODEL_ID>
set -uo pipefail

EDA_BASE=/nasdata/app.e0031982/code/eda_fastmcp
DRIVER="$EDA_BASE/scripts/run_cline_script.sh"
EVAL_PY="$EDA_BASE/scripts/run_eval.py"
DATASET="$EDA_BASE/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl"
RUN_DIR=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
OUT_BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize_posttrain_eval

N_RUNS=5; TASK_TIMEOUT=2500; PARALLEL=8; FRESH_CONTEXT=1; RESHUFFLE=1; N_TASKS=158

BACKBONE="${BACKBONE:-baize-rl}"
ENDPOINT="${ENDPOINT:-http://127.0.0.1:8000/v1}"
API_KEY="${API_KEY:-sk-placeholder}"
MODEL_ID="${MODEL_ID:-baize-rl}"

DRY_RUN=0
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --backbone) BACKBONE="$2"; shift ;;
    --endpoint) ENDPOINT="$2"; shift ;;
    --key) API_KEY="$2"; shift ;;
    --model) MODEL_ID="$2"; shift ;;
    --out-base) OUT_BASE="$2"; shift ;;
    *) echo "未知参数: $1" ;;
  esac
  shift
done

cat <<EOF
===== BaiZe Stage(ii) EDA-Eval-PyAether — EVAL RECIPE @ $(date '+%F %T') =====
  backbone        : ${BACKBONE}
  endpoint        : ${ENDPOINT}
  model_id        : ${MODEL_ID}
  out_base        : ${OUT_BASE}/${BACKBONE}
  ---- 冻结协议（🚫 不得改动）----
  dataset         : ${DATASET}  (${N_TASKS} tasks)
  driver          : ${DRIVER}
  scorer          : ${EVAL_PY}
  metric          : Pass@1 (vendor sandbox execution)
  n_runs          : ${N_RUNS}  (reshuffle=${RESHUFFLE}, fresh_context=${FRESH_CONTEXT})
  task_timeout    : ${TASK_TIMEOUT}s
  parallel        : -p ${PARALLEL} -n   (单 trace 原则)
  ---- 对照与统计 ----
  contamination   : n-gram 黑名单（CONTAMINATION_CHECK.md）
  controls        : 只换 backbone；检索栈/沙盒/anti-cheat/agent 脚手架逐字节一致
  stats           : mean ± std (5-run)；两系统比较用 McNemar / paired bootstrap
  milestones      : M1=50% M2=65% M3=75% M4=85%+（预注册，先定后测）
  ---- BaiZe 接入 ----
  cline auth      : cline auth -p openai -k <KEY> -b ${ENDPOINT} -m ${MODEL_ID}
===== END RECIPE =====
EOF

[ $DRY_RUN = 1 ] && { echo "[dry-run] 配方已打印，不执行评测。"; exit 0; }

[ -f "$DATASET" ] || { echo "❌ 158-case 数据集不存在: $DATASET（本节点未挂载 eda_fastmcp？）"; exit 1; }
[ -f "$DRIVER" ] || { echo "❌ 评测 driver 不存在: $DRIVER"; exit 1; }
[ -f "$EVAL_PY" ] || { echo "❌ 评分脚本不存在: $EVAL_PY"; exit 1; }
command -v cline >/dev/null 2>&1 || { echo "❌ cline 未在 PATH（重启 loop 须带正确 PATH，见 AGENTS.md §3(4)）"; exit 1; }

OUT_DIR="$OUT_BASE/$BACKBONE"
mkdir -p "$OUT_DIR"

echo "[eval] cline auth -> backbone=${BACKBONE} endpoint=${ENDPOINT} model=${MODEL_ID}"
cline auth -p openai -k "$API_KEY" -b "$ENDPOINT" -m "$MODEL_ID" || { echo "❌ cline auth 失败"; exit 1; }

SUM="$OUT_DIR/eval_summary.txt"
echo "===== EDA-Eval-PyAether 5-run START @ $(date '+%F %T') backbone=${BACKBONE} =====" | tee "$SUM"
for run in $(seq 1 "$N_RUNS"); do
  RD="$OUT_DIR/run_${run}"
  mkdir -p "$RD"
  GEN="$RD/generated.jsonl"
  REP="$RD/final_report.json"
  echo "[eval] run ${run}/${N_RUNS} @ $(date '+%T') (reshuffle=${RESHUFFLE} fresh_context=${FRESH_CONTEXT})"
  bash "$DRIVER" --dataset "$DATASET" --out "$GEN" -p "$PARALLEL" -n \
      --timeout "$TASK_TIMEOUT" --reshuffle-seed "$run" > "$RD/driver.log" 2>&1 \
      || { echo "  ❌ run ${run} driver 失败，见 $RD/driver.log"; continue; }
  python "$EVAL_PY" -g "$GEN" --out "$REP" > "$RD/eval.log" 2>&1 \
      || { echo "  ❌ run ${run} 评分失败"; continue; }
  PASS=$(python -c "import json;d=json.load(open('$REP'));print(d.get('pass_rate', d.get('pass@1','N/A')))" 2>/dev/null)
  echo "  run ${run}: pass@1=${PASS}" | tee -a "$SUM"
done

python - "$OUT_DIR" "$BACKBONE" <<'PYEOF' | tee -a "$SUM"
import json, sys, glob, statistics
out_dir, backbone = sys.argv[1], sys.argv[2]
rates = []
for rp in sorted(glob.glob(f"{out_dir}/run_*/final_report.json")):
    try:
        d = json.load(open(rp))
        r = d.get("pass_rate", d.get("pass@1"))
        if r is not None:
            rates.append(float(r) if isinstance(r,(int,float)) else float(str(r).rstrip('%')))
    except Exception as e:
        print(f"  parse fail {rp}: {e}")
if rates:
    mean = statistics.mean(rates); std = statistics.pstdev(rates) if len(rates)>1 else 0.0
    print(f"===== AGGREGATE backbone={backbone} =====")
    print(f"  n_runs={len(rates)}  pass@1 mean={mean:.2f}%  std={std:.2f}%  runs={rates}")
    print(f"  (配对检验 vs baseline: 见 §Eval 统计脚本；此处仅汇总)")
else:
    print("  ⚠️ 无可用 pass_rate，检查各 run final_report.json")
PYEOF
echo "===== EDA-Eval-PyAether 5-run END @ $(date '+%F %T') backbone=${BACKBONE} =====" | tee -a "$SUM"
