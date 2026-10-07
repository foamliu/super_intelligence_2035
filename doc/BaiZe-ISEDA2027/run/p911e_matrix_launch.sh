#!/bin/bash
# ============================================================================
# P-9.11-E — 长上下文推理成本矩阵（**多卡并行版**）
#   BaiZe Mamba2-hybrid-2.2B  ⚔  MiniCPM5-2B(dense)   @ ctx {128K,256K,512K,1M}
#   **用户直令 2026-10-07**：在 `.12` 借 GPU1–7 **并行**跑完、**尽快交还**。
#
# 用法（在 `10.239.2.12` 上，从仓库 run/ 目录）：
#   bash p911e_matrix_launch.sh                     # 默认波次（GPU1-7 共 7 格）
#   bash p911e_matrix_launch.sh "4 dense 1048576"   # 第 2 波：dense 1M 接首张空卡
#   STAGGER=40 bash p911e_matrix_launch.sh          # 错峰间隔（默认 20s；防 NFS 尖峰）
#   # 每个 spec 必须整条加引号："<gpu> <hybrid|dense> <ctx>"
#
# 产出：
#   run/p911e_results/p911e_<model>_ctx<ctx>_gpu<g>.json   ← 逐格结果（TTFT/prefill/decode/e2e/peak VRAM/OOM）
#   /tmp/p911e/<model>_ctx<ctx>_gpu<g>.{srv,bench}.log     ← 逐格原始日志
#
# 设计要点（照抄 P-9.11D 已验证口径）：
#   --mem-fraction-static 0.3  → sglang 不预分配 ~68GB，露出**真实 VRAM**
#   SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1 → 允许 ctx > max_position_embeddings(4096)
#   --attention-backend flashinfer → 规避 cutlass/flash_attn RoundingModeKind bug
#   hybrid 额外 --mamba-ssm-dtype float32
#   每格结束**自动 kill 该卡 server** 并打印 memory.used 归零（交还纪律）
# ============================================================================
set -uo pipefail

ROOT=/nas_train/app.e0031982
RUN=$ROOT/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
HYBRID_HF=$ROOT/code/BaiZe-ISEDA2027/nemo_experiments/p3_hybrid/hf_iter_5000
DENSE_HF=$ROOT/code/BaiZe-ISEDA2027/nemo_experiments/p3_dense/hf_iter_5000
BENCH_PY=$RUN/p911d_sglang_vram_bench.py
OUTDIR=$RUN/p911e_results
LOGDIR=${LOGDIR:-/tmp/p911e}
GEN_LEN=${GEN_LEN:-64}
BATCHES=${BATCHES:-"1 8"}              # bs 列表（大 ctx 时用 BATCHES="1"）
MEM_FRACTION=${MEM_FRACTION:-0.3}      # --mem-fraction-static（V2 扫描时改 0.6/0.85）
STAGGER=${STAGGER:-20}                 # 相邻两格启动间隔（秒）——错峰，避免 7 个 server 同时压 NFS
MAX_WAIT=${MAX_WAIT:-420}              # 单格 server 就绪最长等待（秒）
BENCH_TIMEOUT=${BENCH_TIMEOUT:-5400}   # 单格 bench 硬超时（秒）

# ---- 选一个能 import sglang 的 python（.12/.29 共享同一 NFS miniforge3）----
SGLANG_PY=""
for cand in "$ROOT/miniforge3/envs/sglang/bin/python" "$ROOT/miniforge3/envs/vllm/bin/python"; do
    if [ -x "$cand" ] && "$cand" -c 'import sglang' >/dev/null 2>&1; then SGLANG_PY=$cand; break; fi
done
if [ -z "$SGLANG_PY" ]; then
    echo "[fatal] 找不到能 import sglang 的 python；先看 ls $ROOT/miniforge3/envs/"
    exit 3
fi

mkdir -p "$OUTDIR" "$LOGDIR"
export SGLANG_ALLOW_OVERWRITE_LONGER_CONTEXT_LEN=1
export no_proxy=localhost,127.0.0.1,0.0.0.0 NO_PROXY=localhost,127.0.0.1,0.0.0.0
export http_proxy=http://172.19.92.25:13128 https_proxy=http://172.19.92.25:13128

# ---- 默认波次：GPU1-4 = hybrid 四档；GPU5-7 = dense 128K/256K/512K ----
#      （dense 1M 留作第 2 波：bash p911e_matrix_launch.sh "4 dense 1048576"）
DEFAULT_CELLS=(
  "1 hybrid 131072"  "2 hybrid 262144"  "3 hybrid 524288"  "4 hybrid 1048576"
  "5 dense 131072"   "6 dense 262144"   "7 dense 524288"
)


run_cell() {
    local g="$1" model="$2" ctx="$3"
    local tag="${model}_ctx${ctx}_gpu${g}_mf${MEM_FRACTION}"
    local port=$((30100 + g))
    local mpath="$HYBRID_HF"
    local extra=(--mamba-ssm-dtype float32)
    if [ "$model" = "dense" ]; then mpath="$DENSE_HF"; extra=(); fi
    local srv_log="$LOGDIR/${tag}.srv.log" bench_log="$LOGDIR/${tag}.bench.log"
    local out="$OUTDIR/p911e_${tag}.json"

    local used
    used=$(nvidia-smi --id="$g" --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | tr -d ' ')
    echo "[$(date +%H:%M:%S)] [gpu$g] $model ctx=$ctx 起跑前 memory.used=${used:-?}MiB"
    if [ "${used:-99999}" -gt 2000 ]; then
        echo "[$(date +%H:%M:%S)] [gpu$g] SKIP 卡被占（${used}MiB > 2000MiB）"
        printf '{"cell":"%s","model":"%s","ctx":%s,"gpu":%s,"error":"gpu_occupied_%sMiB"}\n' \
               "$tag" "$model" "$ctx" "$g" "$used" > "$out"
        return 1
    fi

    CUDA_VISIBLE_DEVICES="$g" "$SGLANG_PY" -m sglang.launch_server \
        --model-path "$mpath" --host 127.0.0.1 --port "$port" \
        --context-length "$ctx" --trust-remote-code \
        --mem-fraction-static "$MEM_FRACTION" --attention-backend flashinfer \
        "${extra[@]}" --skip-server-warmup --log-level info \
        > "$srv_log" 2>&1 &
    local srv_pid=$!

    local ok=0 code=000
    for _ in $(seq 1 $((MAX_WAIT / 2))); do
        code=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:${port}/v1/models" 2>/dev/null || echo 000)
        [ "$code" = "200" ] && { ok=1; break; }
        kill -0 "$srv_pid" 2>/dev/null || break
        sleep 2
    done
    if [ "$ok" -ne 1 ]; then
        echo "[$(date +%H:%M:%S)] [gpu$g] server 未就绪（HTTP=$code）→ 记失败/OOM"
        tail -5 "$srv_log" >&2
        printf '{"cell":"%s","model":"%s","ctx":%s,"gpu":%s,"error":"server_not_ready_http_%s"}\n' \
               "$tag" "$model" "$ctx" "$g" "$code" > "$out"
        kill "$srv_pid" 2>/dev/null || true
        return 1
    fi
    echo "[$(date +%H:%M:%S)] [gpu$g] server ready → bench（ctx=$ctx, bs {$BATCHES}, gen_len=$GEN_LEN）"

    # ---- V1/V3 诊断：捕获 server 启动日志关键行 + host RSS ----
    local diag_file="$OUTDIR/p911e_${tag}_diag.txt"
    {
        echo "=== server startup log key lines ==="
        grep -iE 'max_total_num_tokens|max_running_requests|available_gpu_mem|mem_fraction|kv_pool|mem_pool|cache|total_token|num_cpu_blocks|num_gpu_blocks|max_prefill' "$srv_log" 2>/dev/null | head -30
        echo "=== server PID & host RSS (V3: 验证无 host swap) ==="
        local rss_pid
        rss_pid=$(pgrep -f "sglang.launch_server.*--port $port" | head -1)
        if [ -n "$rss_pid" ]; then
            echo "server_pid=$rss_pid"
            cat /proc/$rss_pid/status 2>/dev/null | grep -iE 'VmRSS|VmSize|VmPeak'
            echo "ps_rss_kb=$(ps -o rss= -p $rss_pid 2>/dev/null | tr -d ' ')"
        else
            echo "server_pid=NOT_FOUND"
        fi
    } > "$diag_file" 2>&1
    echo "[$(date +%H:%M:%S)] [gpu$g] diag → $diag_file"

    timeout "$BENCH_TIMEOUT" "$SGLANG_PY" "$BENCH_PY" \
        --base-url "http://127.0.0.1:${port}" --model-name default \
        --model-path "$mpath" --gpu-id "$g" --output "$out" \
        --contexts "$ctx" --batches $BATCHES --gen-len "$GEN_LEN" \
        > "$bench_log" 2>&1
    local rc=$?
    echo "[$(date +%H:%M:%S)] [gpu$g] $model ctx=$ctx bench rc=$rc → $out"

    kill "$srv_pid" 2>/dev/null || true
    sleep 3
    kill -9 "$srv_pid" 2>/dev/null || true
    sleep 2
    echo "[$(date +%H:%M:%S)] [gpu$g] 已归还 memory.used=$(nvidia-smi --id="$g" --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null)MiB"
    return 0
}

# ---- 解析 specs（每个 spec 必须整条加引号："<gpu> <model> <ctx>"）----
if [ "$#" -ge 1 ]; then CELLS=("$@"); else CELLS=("${DEFAULT_CELLS[@]}"); fi
for spec in "${CELLS[@]}"; do
    # shellcheck disable=SC2086
    set -- $spec
    if [ "$#" -ne 3 ]; then
        echo "[fatal] spec 非法：'$spec'（应为 \"<gpu> <hybrid|dense> <ctx>\"，整条加引号）"
        exit 4
    fi
done

echo "=== P-9.11-E 并行矩阵 | ${#CELLS[@]} 格 | STAGGER=${STAGGER}s | python=$SGLANG_PY ==="
echo "=== 逐格 spec：${CELLS[*]} ==="
pids=(); i=1
for spec in "${CELLS[@]}"; do
    # shellcheck disable=SC2086
    run_cell $spec &
    pids+=($!)
    if [ "$i" -lt "${#CELLS[@]}" ]; then sleep "$STAGGER"; fi
    i=$((i + 1))
done
fail=0
for p in "${pids[@]}"; do wait "$p" || fail=$((fail + 1)); done
echo "=== 结束：${#CELLS[@]} 格，失败/跳过 $fail 格 ==="
echo "=== 产出目录 $OUTDIR ==="
ls -la "$OUTDIR"
echo "=== 收尾自查（本脚本的 server 应已 kill；GPU1-7 上不该有自己的进程）==="
nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory --format=csv
