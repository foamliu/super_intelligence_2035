#!/usr/bin/env bash
# 00_build_llamacpp.sh — 编译 llama.cpp（CPU only），供 BaiZe 2B GGUF 评测使用。
#
# 用法:
#   bash 00_build_llamacpp.sh
#
# 可覆盖环境变量:
#   LLAMA_DIR  源码目录      (默认 /nas_train/app.e0031982/tools/llama.cpp)
#   LLAMA_REF  分支/commit   (默认 master)
#   PROXY      https proxy   (默认 http://172.19.92.23:13128；置空则不走代理)
#   JOBS       编译并发      (默认 nproc)
#   FORCE      1=强制重新拉取并重编
#
# 约束:
#   - 只编译 CPU 后端，不碰 CUDA / GPU。
#   - 不写入仓库目录，全部落在 $LLAMA_DIR。
set -euo pipefail

LLAMA_DIR="${LLAMA_DIR:-/nas_train/app.e0031982/tools/llama.cpp}"
LLAMA_REF="${LLAMA_REF:-master}"
PROXY="${PROXY-http://172.19.92.23:13128}"
JOBS="${JOBS:-$(nproc)}"
FORCE="${FORCE:-0}"

if [[ -n "$PROXY" ]]; then
  export https_proxy="$PROXY" http_proxy="$PROXY" all_proxy="$PROXY"
  export HTTPS_PROXY="$PROXY" HTTP_PROXY="$PROXY" ALL_PROXY="$PROXY"
  echo "[build] proxy = $PROXY"
fi

mkdir -p "$(dirname "$LLAMA_DIR")"

if [[ -x "$LLAMA_DIR/build/bin/llama-server" && "$FORCE" != "1" ]]; then
  echo "[build] 已存在: $LLAMA_DIR/build/bin/llama-server"
  "$LLAMA_DIR/build/bin/llama-server" --version || true
  echo "[build] 如需重编: FORCE=1 bash $0"
  exit 0
fi

if [[ -d "$LLAMA_DIR/.git" ]]; then
  echo "[build] fetch $LLAMA_REF in $LLAMA_DIR"
  git -C "$LLAMA_DIR" fetch --depth=1 origin "$LLAMA_REF"
  git -C "$LLAMA_DIR" checkout -f FETCH_HEAD
else
  echo "[build] clone -> $LLAMA_DIR"
  git clone --depth=1 --branch "$LLAMA_REF" \
    https://github.com/ggml-org/llama.cpp "$LLAMA_DIR"
fi

cd "$LLAMA_DIR"
echo "[build] cmake configure (CPU, Release, native)"
cmake -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_NATIVE=ON \
  -DGGML_OPENMP=ON \
  -DLLAMA_CURL=OFF

echo "[build] cmake build -j $JOBS"
cmake --build build -j "$JOBS" --target llama-server llama-cli llama-tokenize quantize

echo "[build] 版本:"
./build/bin/llama-server --version || true

# 软性提示：nemotron_h 分词器修复（issue #30894 / PR #30960）应已包含在 master。
if command -v grep >/dev/null 2>&1; then
  if grep -q "nemotron_h" src/llama-vocab.cpp 2>/dev/null; then
    echo "[build] ok: src/llama-vocab.cpp 含 nemotron_h 分支"
  else
    echo "[build] WARN: src/llama-vocab.cpp 未见 nemotron_h 分支，请确认版本足够新" >&2
  fi
fi

echo "[build] DONE: $LLAMA_DIR/build/bin/llama-server"
