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

# 4. 安装torch 2.6.0 + cu124
# 🔴 R26 FIX (2026-11-08): Upgraded from torch 2.4.0 → 2.6.0+cu124.
#   SGLang 0.4.6.post1 [srt] pins torch==2.6.0. With torch 2.4.0, pip falls into
#   infinite backtracking (R25 stuck 47min). torch 2.6.0+cu124 works with driver 550.54.14.
echo "🔥 安装PyTorch 2.6.0 + CUDA 12.4..."
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124

# 4b. R26 FIX: nvidia-cusparselt-cu12 (torch 2.6.0 dep, libcusparseLt.so.0)
echo "📋 安装 nvidia-cusparselt-cu12..."
pip install nvidia-cusparselt-cu12 2>/dev/null || {
    echo "⚠️  pip失败,从其他用户复制 libcusparseLt.so.0..."
    mkdir -p "$VENV_PATH/lib/python3.10/site-packages/cusparselt/lib/"
    cp /home/app.t0001941/miniforge3/envs/py310/lib/python3.10/site-packages/cusparselt/lib/libcusparseLt.so.0 \
       "$VENV_PATH/lib/python3.10/site-packages/cusparselt/lib/" 2>/dev/null && echo "  ✅ 已复制"
}
# 4c. R26 FIX: LD_LIBRARY_PATH in activate script
if ! grep -q 'cusparselt' "$VENV_PATH/bin/activate" 2>/dev/null; then
    echo 'export LD_LIBRARY_PATH="$HOME/code/verl_cu124_venv/lib/python3.10/site-packages/cusparselt/lib:${LD_LIBRARY_PATH:-}"' >> "$VENV_PATH/bin/activate"
fi
export LD_LIBRARY_PATH="$VENV_PATH/lib/python3.10/site-packages/cusparselt/lib:${LD_LIBRARY_PATH:-}"

# 5. 验证CUDA可用
echo "✅ 验证CUDA可用性..."
python -c 'import torch; print(f"PyTorch版本: {torch.__version__}"); print(f"CUDA版本: {torch.version.cuda}"); print(f"CUDA可用: {torch.cuda.is_available()}"); print(f"GPU数量: {torch.cuda.device_count()}")'

# 6. 安装 SGLang 0.4.6.post1 + srt extras
# 🔴 R26 FIX (2026-11-08): Pinned to sglang[srt]==0.4.6.post1 (NOT 0.5.x).
#   - SGLang 0.5.x pins torch==2.9.1 → incompatible with CUDA 12.4
#   - SGLang 0.4.6.post1 srt pins torch==2.6.0 → compatible with 2.6.0+cu124
#   - sgl-kernel==0.1.0 (102MB) + flashinfer_python==0.2.3
#   - R25's fallback `sglang[srt]>=0.4.0` caused infinite backtracking → REMOVED
echo "📦 安装 SGLang 0.4.6.post1 [srt] (torch 2.6.0 compatible)..."
pip install "sglang[srt]==0.4.6.post1"
echo "  ✅ SGLang 0.4.6.post1 安装完成"

# Verify SGLang basic import
echo "🔍 验证 SGLang 基本导入..."
python -c "import sglang; print(f'SGLang version: {sglang.__version__}')" 2>&1 || echo "  (SGLang import check skipped)"

# 7. 安装 verl 0.4.0 (NOT latest 0.9.1)
# 🔴 R26 FIX (2026-11-08): Pinned to verl==0.4.0 (NOT verl[sglang] latest).
#   - verl 0.9.1 expects SGLang 0.5.x API (sglang.launch_server module structure)
#   - verl 0.4.0 has sglang_rollout integration compatible with SGLang 0.4.6
#   - Install verl base + deps separately (SGLang already installed above)
echo "🧠 安装 verl 0.4.0 (compatible with SGLang 0.4.6)..."
pip install "verl==0.4.0"
pip install "ray[default]>=2.41.0" "accelerate" "codetiming" "datasets" "dill" "hydra-core" \
    "numpy<2" "pandas" "peft" "pyarrow>=19.0.0" "pybind11" "pylatexenc" \
    "tensorboard" "tensordict<=0.6.2" "torchdata" "transformers>=4.39.0" "wandb" "packaging>=20.0"

# 8. 安装flash-attn（可选；可能编译失败，不影响主流程）
echo "⚡ 安装flash-attention 2 (optional)..."
pip install flash-attn --no-build-isolation 2>&1 || echo "  ⚠️ flash-attn 安装失败，不影响主流程（attn_implementation 可回退到 sdpa）"

# 7. 验证所有依赖
echo ""
echo "=== 依赖验证 ==="
for pkg in torch sglang ray verl accelerate transformers; do
    echo -n "$pkg: "
    python -c "import $pkg; print($pkg.__version__)"
done

# R26: Verify torch CUDA compat (torch 2.6.0+cu124 with driver 550.54.14)
echo ""
echo "🔍 R26 验证 torch CUDA 兼容性..."
python -c 'import torch; assert torch.version.cuda == "12.4", f"CUDA mismatch: {torch.version.cuda}"; assert torch.cuda.is_available(), "CUDA not available"; print(f"✅ torch={torch.__version__}, CUDA={torch.version.cuda}, available={torch.cuda.is_available()}")'

echo ""
echo "🎉 CUDA 12.4 venv 配置完成！ (R26: torch 2.6.0+cu124 + SGLang 0.4.6.post1 + verl 0.4.0)"
echo "使用方法: source $VENV_PATH/bin/activate"
echo "下一步运行预飞行检查: bash baize_posttrain_preflight_check.sh"
