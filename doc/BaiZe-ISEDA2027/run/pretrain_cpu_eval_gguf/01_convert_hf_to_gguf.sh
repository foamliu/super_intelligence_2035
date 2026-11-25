#!/usr/bin/env bash
# 01_convert_hf_to_gguf.sh — hf_iter_<it> (nemotron_h) -> GGUF
#
# 用法:
#   bash 01_convert_hf_to_gguf.sh <hf_dir> <out.gguf> [f16|bf16|q8_0]
#
# 默认 f16（官方数字口径）。量化只用于冒烟。
#
# 可覆盖环境变量:
#   LLAMA_DIR  llama.cpp 源码目录
#   PY         转换用的 python（默认 py310，含 torch/transformers/safetensors）
set -euo pipefail

HF_DIR="${1:?用法: bash 01_convert_hf_to_gguf.sh <hf_dir> <out.gguf> [f16|bf16|q8_0]}"
OUT="${2:?缺输出 .gguf 路径}"
OUTTYPE="${3:-f16}"

LLAMA_DIR="${LLAMA_DIR:-/nas_train/app.e0031982/tools/llama.cpp}"
PY="${PY:-/nas_train/app.e0031982/miniforge3/envs/py310/bin/python}"

CONVERT="$LLAMA_DIR/convert_hf_to_gguf.py"
[[ -f "$CONVERT" ]] || { echo "FAIL: 缺 $CONVERT（先跑 00_build_llamacpp.sh）" >&2; exit 1; }
[[ -d "$HF_DIR" ]] || { echo "FAIL: HF 目录不存在: $HF_DIR" >&2; exit 1; }

# 结构自检：必须是 nemotron_h，且 tokenizer 文件齐全
"$PY" - "$HF_DIR" <<'PY'
import json, os, sys
d = sys.argv[1]
cfg_path = os.path.join(d, "config.json")
if not os.path.isfile(cfg_path):
    sys.exit(f"FAIL: 缺 {cfg_path}")
cfg = json.load(open(cfg_path))
mt = cfg.get("model_type")
arch = cfg.get("architectures") or []
print(f"[convert] model_type={mt} architectures={arch} layers={cfg.get('num_hidden_layers')}")
if mt != "nemotron_h" and not any("NemotronH" in str(a) for a in arch):
    sys.exit("FAIL: 不是 nemotron_h 结构，llama.cpp 无法按该路径转换")
pat = cfg.get("hybrid_override_pattern")
if pat:
    print(f"[convert] hybrid_override_pattern={pat} "
          f"(M={pat.count('M')} *={pat.count('*')} -={pat.count('-')})")
tok = [f for f in ("tokenizer.json", "tokenizer.model", "tokenizer_config.json") if os.path.isfile(os.path.join(d, f))]
print(f"[convert] tokenizer files: {tok}")
if not tok:
    sys.exit("FAIL: 缺 tokenizer.json / tokenizer.model，无法写 GGUF 词表")
PY

mkdir -p "$(dirname "$OUT")"

export PYTHONPATH="$LLAMA_DIR/gguf-py:${PYTHONPATH:-}"
echo "[convert] $HF_DIR -> $OUT (outtype=$OUTTYPE)"
"$PY" "$CONVERT" "$HF_DIR" --outtype "$OUTTYPE" --outfile "$OUT"

[[ -s "$OUT" ]] || { echo "FAIL: 输出为空: $OUT" >&2; exit 1; }
ls -lh "$OUT"

# 快速元数据自检：架构必须是 nemotron_h
TOK_BIN="$LLAMA_DIR/build/bin/llama-tokenize"
if [[ -x "$TOK_BIN" ]]; then
  echo "[convert] 冒烟：llama-tokenize"
  "$TOK_BIN" -m "$OUT" -p "The capital of France is" --ids --no-bos | head -5
fi

echo "[convert] DONE: $OUT"
