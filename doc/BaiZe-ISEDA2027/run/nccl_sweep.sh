#!/bin/bash
# NCCL controlled experiments for BaiZe pretrain speedup investigation
# Runs all_reduce benchmark on GPU0-1 with different NCCL env vars
set -e

cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
TORCHRUN=/nas_train/app.e0031982/miniforge3/envs/py310/bin/torchrun
SIZES="1M,10M,100M,500M,1G"
ITERS=20
WARMUP=5

run_test() {
    local name="$1"
    shift
    local env_vars="$@"
    echo "=========================================="
    echo "TEST: $name  ENV: $env_vars"
    echo "=========================================="
    CUDA_VISIBLE_DEVICES=0,1 NCCL_DEBUG=INFO NCCL_DEBUG_FILE=nccl_debug_${name}.log \
        env $env_vars $TORCHRUN --nproc_per_node=2 --master_port=29502 \
        nccl_bench.py --sizes $SIZES --iters $ITERS --warmup $WARMUP \
        --output nccl_bench_${name}.json 2>&1 | grep -E 'Size|---|GB/s|Results' || true
    echo ""
}

# Baseline already done, but re-run for consistency
run_test "baseline" 

# 1. NVLS enable (NVLink SHARP)
run_test "nvls_on" "NCCL_NVLS_ENABLE=1"

# 2. P2P disable (should degrade - confirms NVLink usage)
run_test "p2p_disable" "NCCL_P2P_DISABLE=1"

# 3. IB disable (removes network path overhead for intra-node)
run_test "ib_disable" "NCCL_IB_DISABLE=1"

# 4. SHM disable
run_test "shm_disable" "NCCL_SHM_DISABLE=1"

# 5. Algorithm: Tree
run_test "algo_tree" "NCCL_ALGO=Tree"

# 6. Algorithm: Ring (explicit)
run_test "algo_ring" "NCCL_ALGO=Ring"

# 7. Protocol: Simple
run_test "proto_simple" "NCCL_PROTO=Simple"

# 8. NVLS + IB disable (combined best guess)
run_test "nvls_ib" "NCCL_NVLS_ENABLE=1 NCCL_IB_DISABLE=1"

# 9. P2P_LEVEL=NVL (force NVLink level)
run_test "p2p_level_nvl" "NCCL_P2P_LEVEL=NVL"

echo "=== ALL TESTS DONE ==="
