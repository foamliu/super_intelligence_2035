#!/usr/bin/env bash
# baize_cpu_probe_matrix.sh — 线程×batch 吞吐探测矩阵（后台运行）
#
# 用法: nohup bash baize_cpu_probe_matrix.sh <ckpt_iter> <probe_limit> > /tmp/baize_probe_matrix.log 2>&1 &
#
# 顺序运行所有 (threads, batch_size) 组合，记录 wall-clock + 分数 + samples/s
# 结果写入 /tmp/baize_probe_results.json
#
# 硬约束：OMP ≤ 80, nice 19, CUDA_VISIBLE_DEVICES=""
set -uo pipefail

CKPT_ITER="${1:?用法: bash baize_cpu_probe_matrix.sh <ckpt_iter> <probe_limit>}"
PROBE_LIMIT="${2:?用法: bash baize_cpu_probe_matrix.sh <ckpt_iter> <probe_limit>}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b"
MODEL="${BASE}/hf_iter_${CKPT_ITER}"
SUMMARY="/tmp/baize_probe_results.json"

# 探测用的任务（选 2 个代表性任务：openbookqa 小+4选, arc_challenge 中+4选）
PROBE_TASKS="openbookqa,arc_challenge"

# 线程扫描档位
THREAD_LIST="8 16 32 80"
# batch 扫描档位（bs=4在CPU上反而更慢，只扫1和2）
BATCH_LIST="1 2"

echo "========================================"
echo "  Probe Matrix Start: $(date '+%F %T')"
echo "  ckpt=${CKPT_ITER}  limit=${PROBE_LIMIT}"
echo "  tasks=${PROBE_TASKS}"
echo "  threads=${THREAD_LIST}"
echo "  batch=${BATCH_LIST}"
echo "========================================"

# 初始化 summary
echo '{"configs":[]}' > "$SUMMARY"

total=0
for t in $THREAD_LIST; do
  for b in $BATCH_LIST; do
    total=$((total + 1))
  done
done
echo "Total configs to run: $total"

idx=0
for t in $THREAD_LIST; do
  for b in $BATCH_LIST; do
    idx=$((idx + 1))
    TAG="t${t}_b${b}_lim${PROBE_LIMIT}"
    OUT="/tmp/baize_probe_${TAG}"
    rm -rf "$OUT"
    mkdir -p "$OUT"

    echo ""
    echo "========================================"
    echo "  [$idx/$total] threads=$t batch=$b limit=$PROBE_LIMIT"
    echo "  start: $(date '+%T')"
    echo "========================================"

    START_EPOCH=$(date +%s)

    # 运行评测
    export CUDA_VISIBLE_DEVICES=""
    export OMP_NUM_THREADS="$t"
    export MKL_NUM_THREADS="$t"

    bash "$SCRIPT_DIR/baize_cpu_lmeval.sh" "$MODEL" "$OUT" \
      --tasks "$PROBE_TASKS" \
      --limit "$PROBE_LIMIT" \
      --batch_size "$b" \
      > "${OUT}/stdout.log" 2>&1
    EVAL_RC=$?

    END_EPOCH=$(date +%s)
    WALL_SEC=$((END_EPOCH - START_EPOCH))

    echo "  eval rc=$EVAL_RC  wall=${WALL_SEC}s"

    # 解析结果
    if [[ $EVAL_RC -eq 0 && -f "${OUT}/results.json" ]]; then
      # 用 python 解析分数并追加到 summary
      /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -c "
import json, sys

results = json.load(open('${OUT}/results.json'))
scores = {}
for task, metrics in results.get('results', {}).items():
    for m, v in metrics.items():
        if not m.startswith('_') and isinstance(v, (int, float)):
            scores[f'{task}/{m}'] = round(v, 4)

summary = json.load(open('$SUMMARY'))
summary['configs'].append({
    'idx': $idx,
    'threads': $t,
    'batch_size': $b,
    'limit': $PROBE_LIMIT,
    'wall_sec': $WALL_SEC,
    'rc': $EVAL_RC,
    'scores': scores,
    'tasks': '$PROBE_TASKS'.split(','),
})
json.dump(summary, open('$SUMMARY', 'w'), indent=2)
print(f'  Appended to summary: {len(scores)} metrics')
" 2>&1 || echo "  WARN: failed to parse results"
    else
      echo "  WARN: no results.json or eval failed"
      # 仍然记录 wall-clock
      /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -c "
import json
summary = json.load(open('$SUMMARY'))
summary['configs'].append({
    'idx': $idx,
    'threads': $t,
    'batch_size': $b,
    'limit': $PROBE_LIMIT,
    'wall_sec': $WALL_SEC,
    'rc': $EVAL_RC,
    'scores': {},
    'tasks': '$PROBE_TASKS'.split(','),
    'error': 'eval failed or no results',
})
json.dump(summary, open('$SUMMARY', 'w'), indent=2)
" 2>&1
    fi

    # 记录内存峰值（从 /proc 采样）
    PEAK_RSS_KB=$(grep VmHWM /proc/*/status 2>/dev/null | awk '{print $2}' | sort -n | tail -1 || echo 0)
    echo "  peak RSS (any proc): ${PEAK_RSS_KB} KB"

    echo "  [$idx/$total] DONE wall=${WALL_SEC}s end=$(date '+%T')"
  done
done

echo ""
echo "========================================"
echo "  ALL PROBES DONE: $(date '+%F %T')"
echo "  Summary: $SUMMARY"
echo "========================================"
cat "$SUMMARY"
