#!/bin/bash
set -euo pipefail

echo "=== BaiZe Post-Train CUDA 12.4 venv 自动配置脚本 ==="
echo "运行时间: $(date)"
echo ""

VENV_PATH="$HOME/code/verl_cu124_venv"
echo "目标venv路径: $VENV_PATH"
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

# 2. 创建venv
if [ -d "$VENV_PATH" ]; then
    echo "⚠️  venv已存在，是否删除重建？(y/N)"
    read -r ans
    if [[ "$ans" == "y" || "$ans" == "Y" ]]; then
        echo "🗑️ 删除旧venv..."
        rm -rf "$VENV_PATH"
    else
        echo "✅ 保留现有venv，更新依赖..."
    fi
fi

if [ ! -d "$VENV_PATH" ]; then
    echo "🐍 创建Python venv..."
    python3.10 -m venv "$VENV_PATH"
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
echo "📦 安装verl、vLLM、ray等依赖..."
pip install "vllm>=0.33.0" "ray>=2.30.0" "accelerate>=0.28.0" "transformers>=4.39.0" "datasets>=2.18.0" "evaluate>=0.4.1" "pyyaml>=6.0" "numpy>=1.26" "pandas>=2.2" "tqdm>=4.66" "sentencepiece>=0.2.0" "protobuf>=4.25" "grpcio>=1.62" "packaging>=24.0"

# 安装verl
echo "🧠 安装verl GRPO框架..."
pip install verl --extra-index-url https://download.pytorch.org/whl/cu124

# 安装flash-attn（可选，用于加速）
echo "⚡ 安装flash-attention 2..."
pip install flash-attn --no-build-isolation

# 7. 验证所有依赖
echo ""
echo "=== 依赖验证 ==="
for pkg in torch vllm ray verl accelerate transformers; do
    echo -n "$pkg: "
    python -c "import $pkg; print($pkg.__version__)"
done

echo ""
echo "🎉 CUDA 12.4 venv 配置完成！"
echo "使用方法: source $VENV_PATH/bin/activate"
echo "下一步运行预飞行检查: bash baize_posttrain_preflight_check.sh"
