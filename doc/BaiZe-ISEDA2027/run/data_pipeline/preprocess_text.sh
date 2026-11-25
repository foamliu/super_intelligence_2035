#!/bin/bash
# preprocess_text.sh — 通用文本分词打包（phase2 text），复用 Round 1 的 preprocess_data.py。
# 目标：raw parquet → megatron `.bin/.idx/.json`（stable 主体 + 退火源 code / math / EDA）。
#
# ⚠️ 红线 P0 —— 污染闸门：正式产出前，必须先对源跑 `check_contamination.py` 同闸扫描，
#    命中文档（重合率 ≥0.8 或短串兜底命中）必须剔除后再打包（改写也不洗白，见 CONTAMINATION_CHECK.md）。
#    本脚本 --with-contam 会在打包前跑闸；如果发现任何命中则**拒绝打包**（退出码 2）。
#    冒烟/调试可 --skip-contam（默认跳过），但**正式产出绝不带 --skip-contam**。
#
# 复用资产（DATA_LEDGER §3）：
#   preprocess_data.py : /nas_train/app.e0031982/code/BaiZe-ISEDA2027/mamba2_hybrid_2b/preprocess_data.py
#   tokenizer 源       : /nas_train/app.e0031982/models/DeepSeek-V4.1-Flash
#   EOD tokenizer 副本 : 由 preprocess_data.py 自动生成（--tokenizer-output-dir 或 output-prefix 同目录 tokenizer_eod）
#
# 用法：
#   # stable 主体（L3 通用文本，content 列）
#   bash preprocess_text.sh --source /nas_inference/app.e0031982/datasets/openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa \
#       --out-prefix /nas_train/app.e0031982/datasets/baize-data/text/ultrafineweb_l3_qa_text_document --mode content
#
#   # 退火源 code L3（texts 对话 turn 列；多语言子目录，逐语言各切一份，launch 时 blend）
#   bash preprocess_text.sh --source /nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/UltraData-Code-L3/py \
#       --out-prefix /nas_train/app.e0031982/datasets/baize-data/text/anneal_code_py --mode turns
#
#   # 退火源 math L3（Conversation-Synthetic 等子集，texts turn 列）
#   bash preprocess_text.sh --source /nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data/UltraData-Math-L3/Conversation-Synthetic \
#       --out-prefix /nas_train/app.e0031982/datasets/baize-data/text/anneal_math_conv_synth --mode turns
#
#   # 冒烟（只切前 N 文档，验证格式/词表/EOD 可跑通）
#   bash preprocess_text.sh --source /path/to/qa --out-prefix /tmp/smoke --mode content --docs 2000 --skip-contam
#
# 说明：preprocess_data.py 的 --input-dir 只 glob 单目录（非递归）。code/math 是多语言/多子集目录树，
#   因此按「一个语言子目录 / 一个子集 = 一份 .bin」切分，最终由 pretrain_launcher 的 blend JSON 合并配比。
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREPROCESS="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/mamba2_hybrid_2b/preprocess_data.py"
TOKENIZER="/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash"
BLACKLIST_DIR="$SCRIPT_DIR/blacklist"
CHECK_CONTAM="$SCRIPT_DIR/check_contamination.py"

SOURCE=""
OUT_PREFIX=""
MODE="content"
DOCS=""
DTYPE="int32"
DO_CONTAM=0          # 默认跳过污染闸（冒烟）；正式产出必须手动去掉 --skip-contam

usage() {
  sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'
}

while [ $# -gt 0 ]; do
  case "$1" in
    --source)       SOURCE="$2"; shift 2 ;;
    --out-prefix)   OUT_PREFIX="$2"; shift 2 ;;
    --mode)         MODE="$2"; shift 2 ;;
    --docs)         DOCS="$2"; shift 2 ;;
    --dtype)        DTYPE="$2"; shift 2 ;;
    --with-contam)  DO_CONTAM=1; shift ;;
    --skip-contam)  DO_CONTAM=0; shift ;;
    -h|--help)      usage; exit 0 ;;
    *) echo "未知参数: $1" >&2; usage; exit 2 ;;
  esac
done

if [ -z "$SOURCE" ] || [ -z "$OUT_PREFIX" ]; then
  echo "错误：--source 与 --out-prefix 必填" >&2
  usage
  exit 2
fi
if [ ! -f "$PREPROCESS" ]; then
  echo "错误：未找到复用脚本 $PREPROCESS" >&2
  exit 2
fi
if [ ! -d "$SOURCE" ]; then
  echo "错误：源目录不存在 $SOURCE" >&2
  exit 2
fi
case "$MODE" in
  content|turns) ;;
  *) echo "错误：--mode 只能是 content 或 turns" >&2; exit 2 ;;
esac

# ---- 污染闸门（红线 P0）----
if [ "$DO_CONTAM" -eq 1 ]; then
  echo "[contam] 打包前污染闸门扫描：$SOURCE"
  contam_report="${OUT_PREFIX}.contam.md"
  if ! python "$CHECK_CONTAM" \
      --blacklist-dir "$BLACKLIST_DIR" \
      --input "$SOURCE" \
      --ngram 13 --threshold 0.8 \
      --out "$contam_report"; then
    echo "[contam] 扫描脚本执行失败，拒绝打包" >&2
    exit 2
  fi
  # 命中数记在报告末行；任何命中即中止（不自动剔除，需人工/脚本确认后重跑）
  if grep -qE '命中（污染）文档数：[1-9]' "$contam_report"; then
    echo "[contam] ❌ 检测到污染命中，拒绝打包。报告：$contam_report" >&2
    exit 2
  fi
  echo "[contam] ✅ 无命中，放行打包。报告：$contam_report"
fi

# ---- 调用 Round 1 脚本 ----
ARGS=(--input-dir "$SOURCE" --output-prefix "$OUT_PREFIX" --tokenizer "$TOKENIZER" --mode "$MODE" --dtype "$DTYPE")
[ -n "$DOCS" ] && ARGS+=(--max-docs "$DOCS")

echo "[preprocess] $PREPROCESS ${ARGS[*]}"
python "$PREPROCESS" "${ARGS[@]}"

echo "[done] 产物：${OUT_PREFIX}.bin / .idx / .json"
echo "       tokenizer_eod 副本：$(dirname "$OUT_PREFIX")/tokenizer_eod"