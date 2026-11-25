#!/usr/bin/env bash
# ============================================================
# baize-llm · 一眼看状态（只读）：进程 / 显存 / 最新步数 / ckpt / LR / TensorBoard
#   bash scripts/status.sh [--name X]
# ============================================================
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BAIZE_LLM_HOME="$(cd "$HERE/.." && pwd)"
export BAIZE_LLM_HOME
# shellcheck source=lib.sh
source "$HERE/lib.sh"
# shellcheck source=../configs/common.env
source "$BAIZE_LLM_HOME/configs/common.env"

[ "${1:-}" = "--name" ] && NAME="${2:-$NAME}"

echo "===== baize-llm status @ $(ts) · host=$(hostname) ====="
echo "  name=$NAME  exp=$EXP_ROOT/$NAME"

echo
echo "--- 训练进程 ---"
pgrep -af 'torchrun.*pretrain_launcher' | cut -c1-160 || echo "  （无）"

echo
echo "--- GPU ---"
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader | sed 's/^/  /'

echo
echo "--- 最新日志（各 /tmp/baize_*.log）---"
for f in $(ls -t /tmp/baize_*worker.log /tmp/baize_*_train.log 2>/dev/null | head -3); do
  echo "  [$f]  mtime=$(date -r "$f" '+%F %T' 2>/dev/null)"
  grep -E 'iteration +[0-9]+/' "$f" 2>/dev/null | tail -1 | cut -c1-150 | sed 's/^/    /'
  tail -2 "$f" 2>/dev/null | cut -c1-150 | sed 's/^/    /'
done

echo
echo "--- 最新 checkpoint ---"
CKPT_DIR="$EXP_ROOT/$NAME/checkpoints"
if [ -d "$CKPT_DIR" ]; then
  ls -dt "$CKPT_DIR"/iter_* 2>/dev/null | head -3 | sed 's/^/  /'
  [ -f "$CKPT_DIR/latest_checkpointed_iteration.txt" ] && \
    echo "  latest_checkpointed_iteration = $(cat "$CKPT_DIR/latest_checkpointed_iteration.txt")"
else
  echo "  （还没有：$CKPT_DIR）"
fi

echo
echo "--- TensorBoard ---"
bash "$HERE/tb_6006.sh" status

echo
echo "--- 提示 ---"
echo "  理论 LR 曲线：python scripts/lr_schedule.py --peak $LR --min $MIN_LR --warmup $WARMUP \\"
echo "                  --decay-iters 20000 --total-iters 1070000"
