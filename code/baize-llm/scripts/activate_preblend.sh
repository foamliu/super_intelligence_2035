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
# Use printf to ensure actual TAB characters (heredoc \t would be literal backslash-t).
# Paths are the pre-blend OUTPUT DIRECTORY (contains *_pb_sNNN.bin files),
# NOT the _pb file prefix — gen_blend.py globs "*.bin" inside the directory.
{
  printf '# S 共用配比（2026-10-28 定稿 · pre-blend 激活版）\n'
  printf '# 列：key <TAB> tokenized 子目录（绝对路径=pre-blend / 相对=TOK_ROOT） <TAB> prop <TAB> epochs\n'
  printf '# prop 之和 = 1.000；绝对路径源用 pre-blend 大 shard，ufw_zh 保持原 4 shards\n'
  printf 'en_v1_4\t/nas_user/app.e0031982/datasets/pre-blend/en_v1_4\t0.65\t0.81\n'
  printf 'ufw_l1_en_hq\t/nas_user/app.e0031982/datasets/pre-blend/ufw_l1_en_hq\t0.05\t0.93\n'
  printf 'ufw_zh\tUltra-FineWeb/ultrafineweb_zh\t0.04\t0.99\n'
  printf 'math_l1\t/nas_user/app.e0031982/datasets/pre-blend/math_l1\t0.05\t0.85\n'
  printf 'math_l3\t/nas_user/app.e0031982/datasets/pre-blend/math_l3\t0.02\t0.72\n'
  printf 'code_l2\t/nas_user/app.e0031982/datasets/pre-blend/code_l2\t0.15\t1.00\n'
  printf 'code_l3\t/nas_user/app.e0031982/datasets/pre-blend/code_l3\t0.04\t0.87\n'
} > "$TSV"
echo "TSV updated: $TSV"
echo "--- TSV content ---"
cat -A "$TSV" | head -12

echo "=== Updating common.env: nw=8, fork, mmap re-enabled ==="
sed -i 's/export BAIZE_NUM_WORKERS="${BAIZE_NUM_WORKERS:-0}"/export BAIZE_NUM_WORKERS="${BAIZE_NUM_WORKERS:-8}"/' "$COMMON"
sed -i 's/export BAIZE_NO_MMAP_BIN_FILES="${BAIZE_NO_MMAP_BIN_FILES:-1}"/export BAIZE_NO_MMAP_BIN_FILES="${BAIZE_NO_MMAP_BIN_FILES:-0}"/' "$COMMON"
echo "common.env updated: nw=8, mmap re-enabled"

echo "=== Verifying blend ==="
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
"$PY" "$BAIZE_LLM_HOME/scripts/gen_blend.py" --tsv "$TSV" --tok-root /nas_train/app.e0031982/datasets/baize-data/tokenized --quiet 2>&1 | head -5
echo "=== Activation complete ==="
