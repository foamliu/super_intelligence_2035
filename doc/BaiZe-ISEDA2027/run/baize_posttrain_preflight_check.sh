#!/bin/bash
set -euo pipefail

echo "=== BaiZe Post-Train 11/9 预飞行检查脚本 ==="
echo "运行时间: $(date)"
echo ""

PASS=0
FAIL=0

check() {
    local name="$1"
    local cmd="$2"
    echo -n "🔍 检查 $name ... "
    if eval "$cmd"; then
        echo "✅ PASS"
        PASS=$((PASS+1))
    else
        echo "❌ FAIL"
        FAIL=$((FAIL+1))
    fi
}

# 1. 基础环境检查
check "系统CUDA驱动版本>=12.4" "nvcc --version | grep -q 'release 12\.4'"
check "当前节点是10.252.32.17" "hostname -I | grep -q '10\.252\.32\.17'"
check "工作目录存在" "cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run"

# 2. CUDA & venv 检查
VENV_PATH="$HOME/code/verl_cu124_venv"
check "CUDA 12.4 venv存在" "[ -d \"$VENV_PATH\" ]"
if [ -d "$VENV_PATH" ]; then
    check "torch版本匹配cu124" "$VENV_PATH/bin/python -c 'import torch; print(torch.version.cuda)' | grep -q '12\.4'"
    check "torch.cuda.is_available()=True" "$VENV_PATH/bin/python -c 'import torch; exit(0 if torch.cuda.is_available() else 1)'"
    check "vLLM已安装" "$VENV_PATH/bin/python -c 'import vllm; exit(0)'"
    check "verl已安装" "$VENV_PATH/bin/python -c 'import verl; exit(0)'"
fi

# 3. 模型与数据检查
check "MiniCPM5-2B模型存在" "[ -d \"/tmp/models/MiniCPM5-2B\" ] && [ -f \"/tmp/models/MiniCPM5-2B/config.json\" ]"
check "eda_fastmcp本地克隆存在" "[ -d \"$HOME/code/eda_fastmcp\" ] && [ -f \"$HOME/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json\" ]"
check "158题评测数据集存在" "[ -f \"$HOME/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl\" ]"
check "SFT语料已生成" "[ -f \"./sft_pyaether_corpus.jsonl\" ] && [ $(wc -l < ./sft_pyaether_corpus.jsonl) -eq 19610 ]"
check "合成RL题已生成" "[ -f \"./rl_pyaether_synth_v2.jsonl\" ] && [ $(wc -l < ./rl_pyaether_synth_v2.jsonl) -eq 3347 ]"
check "污染闸门脚本存在" "[ -f \"./baize_posttrain_contamination_gate.sh\" ]"

# 4. 工具与脚本检查
check "API profiler脚本语法正确" "python3 -m py_compile ./baize_posttrain_api_profiler.py"
check "SFT语料生成脚本语法正确" "python3 -m py_compile ./baize_posttrain_gen_sft_corpus.py"
check "RL配置文件YAML合法" "$VENV_PATH/bin/python -c 'import yaml; yaml.safe_load(open(\"./baize_posttrain_rl_verl_config.yaml\")); exit(0)'" 2>/dev/null || echo "⚠️  venv未就绪，跳过YAML检查"

# 5. 网络与隧道检查
echo -n "🔍 检查36.15 SSH可达性 ... "
if ssh -o ConnectTimeout=5 -o BatchMode=yes 10.251.36.15 echo ok 2>/dev/null; then
    echo "✅ PASS"
    PASS=$((PASS+1))
else
    echo "⚠️  隧道未配置，后续手动启动"
fi

echo ""
echo "=== 检查结果 ==="
echo "✅ 通过: $PASS 项"
echo "❌ 失败: $FAIL 项"
echo ""
if [ $FAIL -eq 0 ]; then
    echo "🎉 所有检查通过，可以启动训练流程！"
    exit 0
else
    echo "⚠️  有 $FAIL 项检查失败，请先修复后再启动"
    exit 1
fi
