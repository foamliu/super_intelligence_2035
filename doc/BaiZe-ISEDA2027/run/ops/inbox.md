# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 234 | TARGET: 29 -->
## RUN_ID 234 — 重启后核对两件事：① LR 是否从 warmup 重来（58010 步 lr=5e-6 可疑）② 是否 restore 了 optimizer/scheduler

```bash
set -u
echo "=== RUN_ID 234 | S1 lr/resume audit | $(date '+%F %T') | host=$(hostname) ==="
W=/tmp/baize_s1_baize2b_worker.log
LLM=/nas_train/app.e0031982/code/baize-llm

echo
echo "[1] 最新 iteration 行（看 lr 是否随步数上升）"
timeout 10 grep -E 'iteration +[0-9]+/' "$W" 2>/dev/null | tail -4 | cut -c1-175 | sed 's/^/    /'

echo
echo "[2] train.sh 启动 banner（并行/LR/迭代区间）"
timeout 10 grep -nE '并行|LR|迭代区间|ckpt|CHECK|resume' "$W" 2>/dev/null | head -14 | cut -c1-150 | sed 's/^/    /'

echo
echo "[3] 关键参数是否 restore optimizer / scheduler"
timeout 10 grep -nE '\-\-load|--finetune|--use-checkpoint|--no-load|--ckpt-|--use-dist-ckpt|--no-save-optim|--no-save-rng|--save-interval' "$LLM/scripts/train.sh" 2>/dev/null | head -14 | cut -c1-140 | sed 's/^/    /'

echo
echo "[4] s1.env 里的 LR 相关"
timeout 8 grep -nE 'LR|WARMUP|DECAY|START_ITER|ITERS' "$LLM/configs/s1.env" 2>/dev/null | head -12 | cut -c1-120 | sed 's/^/    /'

echo
echo "[5] ckpt 里是否带 scheduler 状态"
LR_DIR=$(ls -dt /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/iter_0058000 2>/dev/null | head -1)
echo "    dir=$LR_DIR"
timeout 10 ls -1 "$LR_DIR" 2>/dev/null | head -12 | sed 's/^/    /'

echo
echo "[6] 下一步（20s 后）看 lr 变化"
sleep 20
timeout 10 grep -E 'iteration +[0-9]+/' "$W" 2>/dev/null | tail -2 | cut -c1-175 | sed 's/^/    /'

echo "=== DONE 234 ==="
```
