#!/bin/bash
# ============================================================================
# P-9.11-F — hybrid ctx 继续扩 2M/4M/8M/16M（运维指令 2026-10-07③ · 用户直令）
#   复用 p911e_matrix_launch.sh 的全部口径（同一 sglang 栈、同一 flag），
#   仅把 ctx 档换成 {2097152, 4194304, 8388608, 16777216}，hybrid 单模型。
#
# 口径（与 P-9.11-E 完全一致，便于拼接）：
#   --mem-fraction-static 0.3  --attention-backend flashinfer
#   --mamba-ssm-dtype float32  SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1
#   hybrid HF: NemotronHForCausalLM, max_pos=4096（RoPE 外推，仅影响 4/56 attn 层）
#
# ⏰ 何时开跑（铁律：🚫 不抢 data BO / vision）：
#   - .12 vision mask-ratio 消融结束（ETA ~14:30）→ 8 卡空 → 可并行 4 档
#   - .29 data Round2 BO 结束（ETA ~19:00, --gpus 0-7）→ 8 卡空
#   - 确认目标 GPU 的 memory.used < 2000MiB 且无人即将占用再起。
#
# 用法：
#   bash p911f_longctx_2m_16m_launch.sh            # 顺序：GPU1 上 2M→4M→8M→16M（1 卡即可）
#   bash p911f_longctx_2m_16m_launch.sh 5          # 顺序跑在 GPU5
#   # 并行（≥4 卡空时，直接调基脚本，一格一卡）：
#   #   bash p911e_matrix_launch.sh "1 hybrid 2097152" "2 hybrid 4194304" "3 hybrid 8388608" "4 hybrid 16777216"
#
# 产出：run/p911e_results/p911e_hybrid_ctx{2097152,4194304,8388608,16777216}_gpu<g>.json
#       /tmp/p911e/<...>.{srv,bench}.log   ← 逐格原始日志（**V1 诊断需要 srv.log 的 max_total_num_tokens**，务必保留！）
#       跑完 merge 进 p911e_longctx_cost_results.json + 刷 report_pretrain_longctx_infer_cost.html
#
# ⚠️ prompt 精确计数：基脚本用 p911d_sglang_vram_bench.py 构造 prompt；1M 实测 prompt_tokens_actual=1008124
#    （未严格 = ctx−64）。2M-16M 跑前先核 bench 是否能精确到 ctx−64，否则需调 bench 的 prompt 构造。
# ============================================================================
set -uo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="$DIR/p911e_matrix_launch.sh"
CTXS=(2097152 4194304 8388608 16777216)   # 2M 4M 8M 16M
g="${1:-1}"

echo "=== P-9.11-F hybrid ctx extend 2M/4M/8M/16M | sequential on GPU$g | reuse $BASE ==="
for ctx in "${CTXS[@]}"; do
    echo "----- cell: gpu$g hybrid ctx=$ctx -----"
    bash "$BASE" "$g hybrid $ctx" || echo "[warn] cell ctx=$ctx rc=$? (记未测/OOM)"
done
echo "=== P-9.11-F 结束。产出见 run/p911e_results/p911e_hybrid_ctx*_gpu${g}.json ==="
echo "=== 收尾自查：本 GPU 上不该有自己的 server 残留 ==="
nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory --format=csv | grep -i "gpu.*$g" || true
