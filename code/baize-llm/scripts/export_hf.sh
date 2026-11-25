#!/usr/bin/env bash
# ============================================================
# export_hf.sh — Megatron-core ckpt → HuggingFace 导出 + check_rope.py 验证
#
# 用法： bash scripts/export_hf.sh <iter> [output_dir]
#   <iter>       checkpoint 迭代号（如 2000）
#   [output_dir] 可选，默认 nemo_experiments/baize2b/hf_iter_<iter>
#
# 导出后自动 patch config.json（max_position_embeddings=1048576, rope_theta=1e6）
# 并运行 scripts/check_rope.py 验证 PASS。
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_HOME="$(cd "$SCRIPT_DIR/.." && pwd)"
source "$PROJECT_HOME/configs/common.env"

ITER="${1:?用法: bash scripts/export_hf.sh <iter> [output_dir]}"

# Megatron checkpoint dir uses zero-padded 7-digit iter: iter_0002000
CKPT_BASE="$EXP_ROOT/$NAME/checkpoints"
# Try zero-padded first, then plain
ITER_PADDED=$(printf "%07d" "$ITER")
if [ -d "$CKPT_BASE/iter_${ITER_PADDED}" ]; then
  CKPT_DIR="$CKPT_BASE/iter_${ITER_PADDED}"
elif [ -d "$CKPT_BASE/iter_${ITER}" ]; then
  CKPT_DIR="$CKPT_BASE/iter_${ITER}"
else
  # Auto-detect from latest_checkpointed_iteration.txt
  LATEST=$(cat "$CKPT_BASE/latest_checkpointed_iteration.txt" 2>/dev/null || echo "")
  if [ -n "$LATEST" ]; then
    LATEST_PADDED=$(printf "%07d" "$LATEST")
    CKPT_DIR="$CKPT_BASE/iter_${LATEST_PADDED}"
    echo "WARN: iter_${ITER} not found, using latest: iter_${LATEST_PADDED}"
    ITER="$LATEST"
  else
    CKPT_DIR="$CKPT_BASE/iter_${ITER_PADDED}"
  fi
fi

if [ -n "${2:-}" ]; then
  OUTPUT_DIR="$2"
else
  OUTPUT_DIR="$EXP_ROOT/$NAME/hf_iter_${ITER}"
fi

CONVERT_SCRIPT="$BAIZE_TRAIN_CODE/convert_mcore_to_hf.py"

echo "============================================================"
echo "  export_hf.sh · iter=${ITER}"
echo "  ckpt_dir : $CKPT_DIR"
echo "  output   : $OUTPUT_DIR"
echo "  converter: $CONVERT_SCRIPT"
echo "============================================================"

# ---- 1. 检查 ckpt 存在 ----
if [ ! -d "$CKPT_DIR" ]; then
  echo "FAIL: checkpoint 目录不存在: $CKPT_DIR"
  echo "  检查 latest_checkpointed_iteration.txt:"
  cat "$EXP_ROOT/$NAME/checkpoints/latest_checkpointed_iteration.txt" 2>/dev/null || echo "  (无)"
  exit 1
fi

# ---- 2. 转换 (mcore distcp → HF safetensors) ----
echo ""
echo "[1/3] 转换 mcore → HF ..."
PYTHON="${PY:-/nas_train/app.e0031982/miniforge3/envs/py310/bin}/python"
"$PYTHON" "$CONVERT_SCRIPT" \
  --arch hybrid \
  --ckpt-dir "$CKPT_DIR" \
  --output-dir "$OUTPUT_DIR"

# ---- 3. Patch config.json (RoPE 1M + theta 1e6) ----
echo ""
echo "[2/3] Patch config.json (max_position_embeddings=1048576, rope_theta=1000000) ..."
CONFIG_JSON="$OUTPUT_DIR/config.json"
if [ ! -f "$CONFIG_JSON" ]; then
  echo "FAIL: config.json not found at $CONFIG_JSON"
  exit 1
fi

"$PYTHON" - "$CONFIG_JSON" <<'PYEOF'
import json, sys
path = sys.argv[1]
with open(path) as f:
    cfg = json.load(f)
cfg["max_position_embeddings"] = 1048576
cfg["rope_theta"] = 1000000
cfg["rope_scaling"] = None
with open(path, "w") as f:
    json.dump(cfg, f, indent=2)
print(f"  patched: max_position_embeddings={cfg['max_position_embeddings']}, rope_theta={cfg['rope_theta']}, rope_scaling={cfg['rope_scaling']}")
PYEOF

# ---- 4. check_rope.py 验证 ----
echo ""
echo "[3/3] check_rope.py 验证 ..."
"$PYTHON" "$SCRIPT_DIR/check_rope.py" --hf-dir "$OUTPUT_DIR"
RC=$?

if [ $RC -eq 0 ]; then
  echo ""
  echo "============================================================"
  echo "  ✅ export_hf.sh 完成 — check_rope.py PASS"
  echo "  HF 目录: $OUTPUT_DIR"
  echo "============================================================"
else
  echo ""
  echo "============================================================"
  echo "  ❌ check_rope.py FAIL (rc=$RC)"
  echo "  请检查 $CONFIG_JSON"
  echo "============================================================"
  exit $RC
fi
