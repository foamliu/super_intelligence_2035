#!/usr/bin/env bash
# setup_llamacpp_qwen35.sh — zhulong 本机：装 llama.cpp + 下载 Qwen3.5-0.8B（hf-mirror）
#
# 用法:
#   bash setup_llamacpp_qwen35.sh              # 全流程
#   STEP=probe bash setup_llamacpp_qwen35.sh   # 只探测
#   STEP=build|download|convert|smoke
#
# 可覆盖:
#   TOOLS=$HOME/tools          llama.cpp 源码与 build
#   MODEL_DIR=$HOME/models/Qwen3.5-0.8B
#   PROXY=http://172.19.92.23:13128
#   THREADS=8
#
# 说明:
#   - Qwen3.5-0.8B 是 Image-Text-to-Text 多模态（qwen3_5），llama.cpp 可能尚不支持；
#     转换失败不视为本脚本失败，会记录日志并提示 transformers 回退。
#   - 不写入 git 仓库；不占用 8090 端口。
set -uo pipefail

TOOLS="${TOOLS:-$HOME/tools}"
MODEL_DIR="${MODEL_DIR:-$HOME/models/Qwen3.5-0.8B}"
PROXY="${PROXY:-http://172.19.92.23:13128}"
THREADS="${THREADS:-8}"
STEP="${STEP:-all}"
LOG="/tmp/setup_llamacpp_qwen35_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1

if [[ -n "$PROXY" ]]; then
  export https_proxy="$PROXY" http_proxy="$PROXY" all_proxy="$PROXY"
  export HTTPS_PROXY="$PROXY" HTTP_PROXY="$PROXY" ALL_PROXY="$PROXY"
fi

say() { echo; echo "==== $* ===="; }

probe() {
  say "0. probe"
  hostname; uname -a
  echo "nproc=$(nproc 2>/dev/null || echo '?')"
  free -g 2>/dev/null | head -3 || true
  df -h . "$HOME" 2>/dev/null | head -6 || true
  for c in git cmake g++ make python3 curl; do printf '%-8s ' "$c"; command -v "$c" || echo MISSING; done
  python3 -c 'import sys; print("python", sys.version.split()[0])' 2>/dev/null || true
  nvidia-smi 2>/dev/null | head -12 || echo "no nvidia-smi"
  nvcc --version 2>/dev/null | tail -2 || echo "no nvcc"
  echo "proxy=$PROXY"
  curl -sS -o /dev/null -w "github http=%{http_code}\n" -m 12 https://github.com || true
}

build() {
  say "1. build llama.cpp"
  mkdir -p "$TOOLS"
  if [[ -x "$TOOLS/llama.cpp/build/bin/llama-cli" ]]; then
    echo "already built: $TOOLS/llama.cpp/build/bin/llama-cli"
  else
    if [[ -d "$TOOLS/llama.cpp/.git" ]]; then
      git -C "$TOOLS/llama.cpp" fetch --depth=1 origin master && git -C "$TOOLS/llama.cpp" checkout -f FETCH_HEAD
    else
      git clone --depth=1 https://github.com/ggml-org/llama.cpp "$TOOLS/llama.cpp" || return 1
    fi
    ( cd "$TOOLS/llama.cpp" && \
      cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=ON -DGGML_OPENMP=ON && \
      cmake --build build -j "$(nproc)" --target llama-cli llama-server llama-quantize ) || return 1
  fi
  "$TOOLS/llama.cpp/build/bin/llama-cli" --version || true
}

download() {
  say "2. download Qwen/Qwen3.5-0.8B"
  mkdir -p "$MODEL_DIR"
  export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
  export HF_HUB_ENABLE_HF_TRANSFER=0
  if command -v hf >/dev/null 2>&1; then
    hf download Qwen/Qwen3.5-0.8B --local-dir "$MODEL_DIR"
  elif command -v huggingface-cli >/dev/null 2>&1; then
    huggingface-cli download Qwen/Qwen3.5-0.8B --local-dir "$MODEL_DIR"
  else
    echo "FAIL: 无 hf / huggingface-cli。请在独立 venv 安装："
    echo "  python3 -m venv ~/.venvs/qtools && ~/.venvs/qtools/bin/pip install -U -i https://pypi.tuna.tsinghua.edu.cn/simple huggingface_hub"
    return 1
  fi
}

verify() {
  say "3. verify model"
  python3 - "$MODEL_DIR" <<'PY'
import glob, json, os, sys
d = sys.argv[1]
files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(d, "*")))
print("files:", len(files))
for k in ("config.json", "preprocessor_config.json", "tokenizer_config.json"):
    print(f"  {k}: {'OK' if os.path.isfile(os.path.join(d,k)) else 'MISSING'}")
safes = glob.glob(os.path.join(d, "*.safetensors"))
print("safetensors:", len(safes), "bytes:", sum(os.path.getsize(p) for p in safes))
inc = glob.glob(os.path.join(d, "**", "*.incomplete"), recursive=True)
print("incomplete:", len(inc))
if os.path.isfile(os.path.join(d, "config.json")):
    c = json.load(open(os.path.join(d, "config.json")))
    print("model_type:", c.get("model_type"), "arch:", c.get("architectures"))
PY
  du -sh "$MODEL_DIR" 2>/dev/null || true
}

convert() {
  say "4. convert -> GGUF f16 (may fail for qwen3_5)"
  local conv="$TOOLS/llama.cpp/convert_hf_to_gguf.py"
  [[ -f "$conv" ]] || { echo "SKIP: no $conv"; return 1; }
  local out="$MODEL_DIR/Qwen3.5-0.8B-f16.gguf"
  if [[ -s "$out" ]]; then
    echo "exists: $out"
  else
    python3 "$conv" "$MODEL_DIR" --outtype f16 --outfile "$out" || {
      echo "CONVERT_FAILED（qwen3_5 可能尚未支持）→ 保留 HF 权重，改用 transformers 冒烟"
      return 1
    }
  fi
  local q="$MODEL_DIR/Qwen3.5-0.8B-Q8_0.gguf"
  if [[ ! -s "$q" ]]; then
    "$TOOLS/llama.cpp/build/bin/llama-quantize" "$out" "$q" Q8_0 || echo "QUANTIZE_FAILED"
  fi
  ls -lh "$out" "$q" 2>/dev/null || true
}

smoke() {
  say "5. smoke"
  local gguf="$MODEL_DIR/Qwen3.5-0.8B-Q8_0.gguf"
  [[ -s "$gguf" ]] || gguf="$MODEL_DIR/Qwen3.5-0.8B-f16.gguf"
  if [[ -s "$gguf" && -x "$TOOLS/llama.cpp/build/bin/llama-cli" ]]; then
    /usr/bin/time -v "$TOOLS/llama.cpp/build/bin/llama-cli" \
      -m "$gguf" -p "用一句话解释什么是 EDA 设计流程。" -n 48 -t "$THREADS" --no-warmup 2>&1 | tail -40 || true
  else
    echo "SKIP llama.cpp（无 GGUF）。transformers 回退请单独执行任务书 §3。"
  fi
}

case "$STEP" in
  probe) probe ;;
  build) probe; build ;;
  download) download; verify ;;
  convert) convert ;;
  smoke) smoke ;;
  all) probe; build; download; verify; convert || true; smoke ;;
  *) echo "unknown STEP=$STEP"; exit 2 ;;
esac

say "DONE (log: $LOG)"
