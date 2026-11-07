#!/bin/bash
set -euo pipefail

# === R14 FIX (2026-11-07): Non-interactive mode + Python auto-detection ===
#   --yes : Skip interactive prompts (auto-recreate venv if exists)
#   python3.10 is NOT in PATH on .17; auto-detect from miniforge3/eda_fastmcp .venv

FORCE_YES=0
while [ $# -gt 0 ]; do
    case "$1" in
        --yes|-y) FORCE_YES=1 ;;
        *) echo "Unknown arg: $1" ;;
    esac
    shift
done

echo "=== BaiZe Post-Train CUDA 12.4 venv 自动配置脚本 (R14 fixed) ==="
echo "运行时间: $(date)"
echo "Non-interactive: $([ $FORCE_YES = 1 ] && echo 'YES' || echo 'NO')"
echo ""

VENV_PATH="$HOME/code/verl_cu124_venv"
echo "目标venv路径: $VENV_PATH"
echo ""

# 0. Auto-detect Python >= 3.10 (python3.10 not in PATH on .17)
echo "🔍 检测可用的 Python >= 3.10..."
PYTHON_BIN=""
for candidate in \
    "/nas_data/app.e0031982/miniforge3/envs/py310/bin/python3.10" \
    "$HOME/miniforge3/envs/py310/bin/python3.10" \
    "$HOME/code/eda_fastmcp/.venv/bin/python" \
    "$(command -v python3.10 2>/dev/null)" \
    "$(command -v python3.11 2>/dev/null)" \
    "$(command -v python3.12 2>/dev/null)"; do
    if [ -n "$candidate" ] && [ -x "$candidate" ]; then
        PY_VER=$("$candidate" --version 2>&1 | awk '{print $2}')
        PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
        PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
        if [ "$PY_MAJOR" -ge 3 ] 2>/dev/null && [ "$PY_MINOR" -ge 10 ] 2>/dev/null; then
            PYTHON_BIN="$candidate"
            echo "✅ 找到 Python $PY_VER: $candidate"
            break
        fi
    fi
done
if [ -z "$PYTHON_BIN" ]; then
    echo "❌ 未找到 Python >= 3.10。请先安装："
    echo "   conda create -n py310 python=3.10  或  apt install python3.10"
    exit 1
fi
echo ""

# 1. 检查系统CUDA版本
echo "🔍 检查系统CUDA版本..."
CUDA_VERSION=$(nvcc --version | grep -o 'release [0-9]*\.[0-9]*' | cut -d' ' -f2)
if [[ "$CUDA_VERSION" != "12.4"* ]]; then
    echo "❌ 系统CUDA版本是 $CUDA_VERSION，需要12.4.x"
    exit 1
fi
echo "✅ 系统CUDA版本 $CUDA_VERSION 符合要求"
echo ""

# 2. 创建venv (R14: non-interactive)
if [ -d "$VENV_PATH" ]; then
    if [ $FORCE_YES = 1 ]; then
        echo "🗑️ --yes 模式：自动删除旧 venv..."
        rm -rf "$VENV_PATH"
    else
        echo "⚠️  venv已存在，是否删除重建？(y/N)"
        read -r ans
        if [[ "$ans" == "y" || "$ans" == "Y" ]]; then
            echo "🗑️ 删除旧venv..."
            rm -rf "$VENV_PATH"
        else
            echo "✅ 保留现有venv，更新依赖..."
        fi
    fi
fi

if [ ! -d "$VENV_PATH" ]; then
    echo "🐍 使用 $PYTHON_BIN 创建 venv..."
    "$PYTHON_BIN" -m venv "$VENV_PATH"
fi

# 3. 激活venv
echo "🔧 激活venv并升级pip..."
source "$VENV_PATH/bin/activate"
pip install --upgrade pip setuptools wheel

# 4. 安装torch + cu124
echo "🔥 安装PyTorch 2.4.0 + CUDA 12.4..."
pip install torch==2.4.0 torchvision==0.19.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu124

# 5. 验证CUDA可用
echo "✅ 验证CUDA可用性..."
python -c 'import torch; print(f"PyTorch版本: {torch.__version__}"); print(f"CUDA版本: {torch.version.cuda}"); print(f"CUDA可用: {torch.cuda.is_available()}"); print(f"GPU数量: {torch.cuda.device_count()}")'

# 6. 安装依赖包
# 🔴 R25 FIX (2026-11-07): SGLang's deps pull torch==2.9.1 (generic PyPI) which
#   breaks CUDA 12.4 compat. Use constraints file to pin torch at 2.4.0+cu124.
#   See EXPERIMENTS_POSTTRAIN.md §R25 for full analysis.
echo "📋 创建 torch 约束文件（防止 SGLang 升级 torch）..."
CONSTRAINT_FILE="/tmp/torch_constraint_$$.txt"
echo "torch==2.4.0" > "$CONSTRAINT_FILE"
echo "torchvision==0.19.0" >> "$CONSTRAINT_FILE"
echo "torchaudio==2.4.0" >> "$CONSTRAINT_FILE"

# 🔴 R16 UPDATE: SGLang's minicpm5 parser is NOT needed!
#   verl has its OWN ToolParser layer (verl/experimental/agent_loop/tool_parser.py)
#   that parses tool calls from model output text. We register a custom "minicpm5"
#   parser via baize_posttrain_minicpm5_parser.py. SGLang just generates text.
#   Therefore: pip release SGLang is sufficient (no main branch, no CUDA 13.x).
#   See EXPERIMENTS_POSTTRAIN.md §R16 for full analysis.
echo "📦 安装 SGLang (pip release — verl ToolParser handles tool calls, torch pinned)..."
pip install "sglang[srt]==0.5.6.post3" -c "$CONSTRAINT_FILE" 2>&1 || pip install "sglang[srt]>=0.4.0" -c "$CONSTRAINT_FILE"
echo "  ✅ SGLang pip 发行版安装完成 (verl ToolParser 处理工具解析, torch 仍为 2.4.0+cu124)"

# Verify SGLang basic import (tool parser check no longer needed — R16)
echo "🔍 验证 SGLang 基本导入..."
python -c "import sglang; print(f'SGLang version: {sglang.__version__}')" 2>&1 || echo "  (SGLang import check skipped)"

pip install "ray>=2.41.0" "accelerate>=0.28.0" "transformers>=4.39.0" "datasets>=2.18.0" "evaluate>=0.4.1" "pyyaml>=6.0" "numpy>=1.26" "pandas>=2.2" "tqdm>=4.66" "sentencepiece>=0.2.0" "protobuf>=4.25" "grpcio>=1.62" "packaging>=24.0" "mlflow>=2.0"

# 安装verl with SGLang backend (R9: verl natively supports SGLang for multi-turn rollout)
echo "🧠 安装 verl[sglang] GRPO框架..."
pip install "verl[sglang]" --extra-index-url https://download.pytorch.org/whl/cu124 -c "$CONSTRAINT_FILE"

# 安装flash-attn（可选，用于加速）
echo "⚡ 安装flash-attention 2..."
pip install flash-attn --no-build-isolation

# 7. 验证所有依赖
echo ""
echo "=== 依赖验证 ==="
for pkg in torch sglang ray verl accelerate transformers; do
    echo -n "$pkg: "
    python -c "import $pkg; print($pkg.__version__)"
done

# R25: Verify torch CUDA compat not broken by SGLang/verl install
echo ""
echo "🔍 R25 验证 torch CUDA 兼容性..."
python -c 'import torch; assert torch.version.cuda == "12.4", f"CUDA mismatch: {torch.version.cuda}"; assert torch.cuda.is_available(), "CUDA not available"; print(f"✅ torch={torch.__version__}, CUDA={torch.version.cuda}, available={torch.cuda.is_available()}")'

# Cleanup constraint file
rm -f "$CONSTRAINT_FILE"

echo ""
echo "🎉 CUDA 12.4 venv 配置完成！"
echo "使用方法: source $VENV_PATH/bin/activate"
echo "下一步运行预飞行检查: bash baize_posttrain_preflight_check.sh"
