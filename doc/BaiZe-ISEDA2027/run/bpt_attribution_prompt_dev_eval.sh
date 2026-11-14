#!/usr/bin/env bash
# bpt_attribution_prompt_dev_eval.sh — Task B (POSTTRAIN_ENV_ATTRIBUTION_SPEC.md §3)
# 在 36.15 上, 对系统提示补丁 (P0/P1/P2/P3) 在 dev(79) 上单变量测试, vs baseline 提示.
# 一次只测一条补丁 (单变量). 门槛: dev 上 3 seed, >= +3pp 且 submit 报错率降 >= 10pp 才进下一轮.
# test = 全 158 仅最后 5-run 验一次 + McNemar (本脚本 --split test 只跑单次, 5-run 由调用方循环).
#
# ⚠️ 依赖: 36.15 5-run baseline (bpt_eval.sh --run-all) 必须先完成, 释放模型隧道 + harness.
#        不与运行中 eval 并跑 (脚本头会先 bpt_eval.sh --status 检查).
# 复用 bpt_eval.sh 的 run_cline_script.sh / CLI_DATA_DIR / EVAL_FW_DIR 口径.
# 纪律: 不改 benchmark / check.py / 题面 / 不挑题 / 不删失败样本. 反作弊钩子常开.
set -uo pipefail
EDA_BASE="/nasdata/app.e0031982/code/eda_fastmcp"
CLI_DATA_DIR="/nasdata/app.e0031982/.cline_posttrain_baseline/data"
EVAL_FW_DIR="/nasdata/app.e0031982/code/EDA-Eval-Framework"
VENV_PYTHON="$EDA_BASE/venv/bin/python"
DATASET="EDA-Eval-PyAether-v20260311_fixed.jsonl"
RESULTS_DIR="/tmp/posttrain_attribution_prompt"
MODEL_URL="http://127.0.0.1:18096/v1"   # 反向隧道 -> .17 GPU6:8096
MODEL_ID="minicpm5-2b-sft-v39-final"
# BaiZe run 目录 (36.15 前缀 /nasdata/, .17 前缀 /nas_data/; 同一份 NFS, 用 env 覆盖以便在任一机 dry-run).
BPT_BAIZE_RUN="${BPT_BAIZE_RUN:-/nasdata/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run}"
SPLIT_FILE="$BPT_BAIZE_RUN/attribution_traindev_split.json"
# 补丁模板 (本线 run/ 下起草; 运行时复制到 eda_fastmcp/prompts/ 供 run_cline_script.sh 读取).
PATCH_DIR="$BPT_BAIZE_RUN"
PATCH_TPL_BASE="eval_sys_prompt_template_old.md"   # 36.15 baseline 沙盒提示 (已存在于 eda_fastmcp/prompts/)
declare -A PATCH_TPL=(
  [baseline]="eval_sys_prompt_template_old.md"
  [p0]="attribution_prompt_p0_toolfmt.md"
  [p1]="attribution_prompt_p1_degenerate.md"
  [p2]="attribution_prompt_p2_submitstorm.md"
  [p3]="attribution_prompt_p3_retrieval.md"
)
# 单变量设计: 每个 pN = baseline_old + 该补丁的单一约束块 (非累积).
# round1: 各 --patch pN 单独 vs --patch baseline, 测每条补丁的边际效应.
# round2 (选择阶段): 通过门槛的补丁需另建累积组合模板 (如 p0+p2) 再测; 本表保持单变量.
PATCH=""; SPLIT="dev"; SEED=""; DRY_RUN=0; STATUS_ONLY=0; SKIP_STATUS_GATE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --patch) PATCH="$2"; shift ;; --split) SPLIT="$2"; shift ;;
    --seed) SEED="$2"; shift ;; --dry-run) DRY_RUN=1 ;; --status) STATUS_ONLY=1 ;;
    --skip-status-gate) SKIP_STATUS_GATE=1 ;; *) echo "未知参数: $1" ;;
  esac; shift
done
mkdir -p "$RESULTS_DIR"
if [ "$STATUS_ONLY" = 1 ]; then
  echo "===== attribution prompt dev-eval status @ $(date '+%F %T') =====  RESULTS_DIR=$RESULTS_DIR"
  for s in dev train test; do
    for p in baseline p0 p1 p2 p3; do
      [ -z "${PATCH_TPL[$p]:-}" ] && [ "$p" != "baseline" ] && continue
      fr="$RESULTS_DIR/${p}_${s}/final_report.json"
      [ -f "$fr" ] && echo "  ${p}_${s}: DONE $(grep -oE '\"pass_rate\"[: ]*[0-9.]+' \"$fr\" 2>/dev/null | head -1)" || echo "  ${p}_${s}: (未完成)"
    done
  done; exit 0
fi
[ -z "$PATCH" ] && { echo "用法: $0 --patch baseline|p0|p1|p2|p3 [--split dev|train|test] [--seed N] [--dry-run] [--status]"; exit 1; }
TPL="${PATCH_TPL[$PATCH]:-}"
[ "$PATCH" != "baseline" ] && [ -z "$TPL" ] && { echo "[FATAL] 补丁 $PATCH 的模板尚未起草 (PATCH_TPL[$PATCH] 为空). 先在 $PATCH_DIR 起草补丁模板."; exit 1; }
# 读取 split 的 task ids
if [ "$SPLIT" = "test" ]; then
  TASKS_CSV=$(python3 -c "import json;d=json.load(open('$SPLIT_FILE'));print(','.join(sorted(set(d['train_ids'])|set(d['dev_ids']))))" 2>/dev/null)
else
  KEY="${SPLIT}_ids"; TASKS_CSV=$(python3 -c "import json;d=json.load(open('$SPLIT_FILE'));print(','.join(d['$KEY']))" 2>/dev/null)
fi
[ -z "$TASKS_CSV" ] && { echo "[FATAL] 无法从 $SPLIT_FILE 读取 $SPLIT 的 task ids."; exit 1; }
NTASKS=$(awk -F, '{print NF}' <<<"$TASKS_CSV")
# dry-run: 只做计划预览, 不检查 36.15 依赖 (venv/harness/隧道), 便于在任一机器验证补丁表与 split.
if [ $DRY_RUN = 1 ]; then
  echo "===== [dry-run] attribution prompt dev-eval patch=$PATCH split=$SPLIT seed=${SEED:-<none>} @ $(date '+%F %T') ====="
  echo "  prompt_template=$TPL  model=$MODEL_ID @ $MODEL_URL  tasks=$NTASKS"
  echo "  [dry-run] 计划: 依次 --patch baseline --split dev (3 seed) 与 --patch <p0|p1|p2|p3> --split dev (3 seed) 对比;"
  echo "  [dry-run] 门槛: Pass@1 >= +3pp 且 submit 报错率降 >= 10pp 才进下一轮 (累积组合)."
  echo "  [dry-run] split task ids: $TASKS_CSV"
  echo "  [dry-run] 不执行, 不检查 36.15 依赖."
  exit 0
fi
# 36.15 5-run baseline 完成闸门 (不与运行中 eval 并跑)
if [ "$SKIP_STATUS_GATE" = 0 ]; then
  if bash /nasdata/app.e0031982/bpt_eval.sh --status 2>/dev/null | grep -q '(未完成)'; then
    echo "[BLOCKED] 36.15 5-run baseline 尚未全部完成 (harness+隧道被占). 待全部 DONE 后再跑. (--skip-status-gate 可强制, 仅诊断用)"; exit 2
  fi
fi
chk() { [ -e "$1" ] || { echo "[FATAL] 缺失: $1"; exit 1; }; }
chk "$VENV_PYTHON"; chk "$EDA_BASE/scripts/run_cline_script.sh"
chk "$CLI_DATA_DIR/settings/providers.json"; chk "$EDA_BASE/pyAether-eval/original_dataset/$DATASET"
chk "$SPLIT_FILE"
curl -s --max-time 8 "$MODEL_URL/models" >/dev/null 2>&1 || { echo "[FATAL] 模型端点 18096 不可达"; exit 1; }
# 部署补丁模板到 eda_fastmcp/prompts/ (本线起草 -> 评测期临时放置; 运行后不主动删, 便于复算)
DEPLOYED_TPL="$TPL"
if [ "$PATCH" != "baseline" ]; then
  SRC="$PATCH_DIR/$TPL"; chk "$SRC"
  DST="$EDA_BASE/prompts/$TPL"
  cp -f "$SRC" "$DST" && echo "[deploy] $SRC -> $DST"
  DEPLOYED_TPL="$TPL"
else
  DEPLOYED_TPL="$PATCH_TPL_BASE"
fi
LABEL="${PATCH}_${SPLIT}${SEED:+_seed${SEED}}"
ARM_DIR="$RESULTS_DIR/$LABEL"; mkdir -p "$ARM_DIR"
export EDA_PROMPT_TEMPLATE_PYAETHER="$DEPLOYED_TPL"   # run_cline_script.sh L26 读此 env
export CLI_DATA_DIR PYTHON="$VENV_PYTHON" EVAL_FW_DIR
export PATH="$HOME/.local/bin:$HOME/.local/node-20/bin:$HOME/.bun/bin:$PATH"
echo "===== attribution prompt dev-eval patch=$PATCH split=$SPLIT seed=${SEED:-<none>} @ $(date '+%F %T') ====="
echo "  prompt_template=$DEPLOYED_TPL  model=$MODEL_ID @ $MODEL_URL  tasks=$NTASKS"
[ $DRY_RUN = 1 ] && { echo "[dry-run] 不执行. tasks=$TASKS_CSV"; echo "[dry-run] 提示: 依次 --patch baseline --split dev (3 seed) 与 --patch p0 --split dev (3 seed) 对比; 门槛 +3pp & submit 报错率降 10pp."; exit 0; }
cd "$EDA_BASE"
echo "[$LABEL] code-gen+eval starting..."
BATCH_ID="attnprompt_${LABEL}_$(date '+%Y_%m%d_%H%M%S')" \
  timeout --signal=TERM --kill-after=120 72000 \
  bash scripts/run_cline_script.sh -p 8 -n -b "$DATASET" -t "$TASKS_CSV" > "$ARM_DIR/codegen.log" 2>&1
echo "[$LABEL] done (rc=$?) $(date '+%F %T')"
fr=$(ls -dt "$EVAL_FW_DIR/output_evaluation/"*/final_report.json 2>/dev/null | head -1)
[ -n "$fr" ] && cp "$fr" "$ARM_DIR/final_report.json" && echo "[$LABEL] final_report -> $ARM_DIR/final_report.json"
[ -f "$ARM_DIR/final_report.json" ] && grep -oE '\"pass_rate\"[: ]*[0-9.]+' "$ARM_DIR/final_report.json" | head -1 | sed "s/^/[$LABEL] /" || echo "[$LABEL] WARNING: 无 final_report"
echo "===== $LABEL done @ $(date '+%F %T') ====="
