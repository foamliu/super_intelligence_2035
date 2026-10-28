#!/usr/bin/env bash
# activate_preblend.sh — pre-blend 完成后激活：更新 TSV 绝对路径 + common.env nw=8
# 用法：bash scripts/activate_preblend.sh
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BAIZE_LLM_HOME="$(cd "$HERE/.." && pwd)"
PB_ROOT="/nas_user/app.e0031982/datasets/pre-blend"
TSV="$BAIZE_LLM_HOME/configs/blend_s1_preblend.tsv"
COMMON="$BAIZE_LLM_HOME/configs/common.env"

# 7 sources and their pre-blend dirs
declare -A SOURCES=(
  [en_v1_4]="$PB_ROOT/en_v1_4"
  [ufw_l1_en_hq]="$PB_ROOT/ufw_l1_en_hq"
  [math_l1]="$PB_ROOT/math_l1"
  [math_l3]="$PB_ROOT/math_l3"
  [code_l2]="$PB_ROOT/code_l2"
  [code_l3]="$PB_ROOT/code_l3"
)
# ufw_zh: 4 shards, no pre-blend needed (keep original path)

echo "=== Checking pre-blend completion ==="
ALL_DONE=1
for key in en_v1_4 ufw_l1_en_hq math_l1 math_l3 code_l2 code_l3; do
  dir="${SOURCES[$key]}"
  if [ -f "$dir/MANIFEST.json" ]; then
    echo "  $key: DONE (MANIFEST.json exists)"
  else
    echo "  $key: NOT DONE (no MANIFEST.json in $dir)"
    ALL_DONE=0
  fi
done

if [ "$ALL_DONE" = 0 ]; then
  echo "Some sources not done yet. Aborting."
  exit 1
fi

echo "=== Updating blend TSV with absolute paths ==="
cat > "$TSV" << 'TSVEOF'
# S 共用配比（2026-10-28 定稿 · pre-blend 激活版）
# 列：key <TAB> tokenized 子目录（绝对路径=pre-blend / 相对=TOK_ROOT） <TAB> prop <TAB> epochs
# prop 之和 = 1.000；绝对路径源用 pre-blend 大 shard，ufw_zh 保持原 4 shards
tsven_v_v1_4	/nas_user/app.e0031982/datasets/pre-blend/en_v1_4/en_v1_4_pb	0.65	0.81
ufw_l1_en_hq	/nas_user/app.e0031982/datasets/pre-blend/ufw_l1_en_hq/ufw_l1_en_hq_pb	0.05	0.93
ufw_zh	Ultra-FineWeb/ultrafineweb_zh	0.04	0.99
math_l1	/nas_user/app.e0031982/datasets/pre-blend/math_l1/math_l1_pb	0.05	0.85
math_l3	/nas_user/app.e0031982/datasets/pre-blend/math_l3/math_l3_pb	0.02	0.72
code_l2	/nas_user/app.e0031982/datasets/pre-blend/code_l2/code_l2_pb	0.15	1.00
code_l3	/nas_user/app.e0031982/datasets/pre-blend/code_l3/code_l3_pb	0.04	0.87
TSVEOF
# Fix the first line (heredoc tab issue)
sed -i 's/^tsven_v_v1_4/  en_v1_4/' "$TSV"
sed -i 's/^  en_v1_4/ en_v1_4/' "$TSV"
echo "TSV updated: $TSV"

echo "=== Updating common.env: nw=8, fork, mmap re-enabled ==="
sed -i 's/export BAIZE_NUM_WORKERS="${BAIZE_NUM_WORKERS:-0}"/export BAIZE_NUM_WORKERS="${BAIZE_NUM_WORKERS:-8}"/' "$COMMON"
sed -i 's/export BAIZE_NO_MMAP_BIN_FILES="${BAIZE_NO_MMAP_BIN_FILES:-1}"/export BAIZE_NO_MMAP_BIN_FILES="${BAIZE_NO_MMAP_BIN_FILES:-0}"/' "$COMMON"
echo "common.env updated: nw=8, mmap re-enabled"

echo "=== Verifying blend ==="
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
"$PY" "$BAIZE_LLM_HOME/scripts/gen_blend.py" --tsv "$TSV" --tok-root /nas_train/app.e0031982/datasets/baize-data/tokenized --quiet 2>&1 | head -5
echo "=== Activation complete ==="
