# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 230 | TARGET: 29 -->
## RUN_ID 230 — 恢复 S1：先停 CPU 冒烟(只杀 python smoke/eval) → 归档崩溃日志 → 从 iter 58000 重启 16 卡训练 → 现场验证

> 用户直令（11-02 19:5x）：「重启 S1 同时把卡住的 CPU 冒烟停掉（避免再抢内存/误杀）」。本块**会改状态**，只动 pretrain 相关进程。

```bash
set -u
echo "=== RUN_ID 230 | RESTART S1 | $(date '+%F %T') | host=$(hostname) ==="
LLM=/nas_train/app.e0031982/code/baize-llm
BASE=/nas_train/app.e0031982/code/BaiZe-ISEDA2027

echo
echo "[0] 前状态"
echo "  .29 GPU mem: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr '\n' ' ')"
echo "  torchrun=$(ps -eo cmd | grep -cE '[t]orchrun|[p]retrain_launcher')"
echo "  latest ckpt: $(cat "$BASE/nemo_experiments/baize2b/checkpoints/latest_checkpointed_iteration.txt" 2>/dev/null)"

echo
echo "[1] 配方核对（s1.env 关键项 + resume 逻辑）"
timeout 8 grep -nE '^(NAME|ITERS|START_ITER|NNODES|NPROC_PER_NODE|TP|CP|SEQ|MBS|GBS|SAVE_INTERVAL|LR|MIN_LR|WARMUP|LR_DECAY)' "$LLM/configs/s1.env" 2>/dev/null | head -20 | cut -c1-120 | sed 's/^/    /'
echo "  train.sh resume/checkpoint 相关行:"
timeout 8 grep -nE 'resume|load|checkpoint|--save|--no-save-optim|MASTER_ADDR|ssh ' "$LLM/scripts/train.sh" 2>/dev/null | head -12 | cut -c1-130 | sed 's/^/    /'

echo
echo "[2] 停 CPU 冒烟 / 评测（只匹配 python 进程，绝不碰训练与 cline）"
LIST=$(timeout 10 ps -eo pid,etime,pcpu,rss,cmd 2>/dev/null | grep -E 'python[^ ]* .*(cpu_smoke|test_lmeval|lm_eval)' | grep -v ' ops_relay' | head -12)
echo "$LIST" | cut -c1-130 | sed 's/^/    /'
PIDS=$(echo "$LIST" | awk '{print $1}')
echo "    命中 PID: ${PIDS:-none}"
for p in $PIDS; do kill -TERM "$p" 2>/dev/null || true; done
sleep 3
for p in $PIDS; do kill -KILL "$p" 2>/dev/null || true; done
sleep 1
echo "    剩余 smoke/eval 进程数=$(timeout 10 ps -eo cmd 2>/dev/null | grep -E 'python[^ ]* .*(cpu_smoke|test_lmeval|lm_eval)' | grep -vc ops_relay)"

echo
echo "[3] 归档崩溃现场日志（保留证据，别覆盖）"
for f in /tmp/baize_s1_baize2b_worker.log /tmp/baize_s1_baize2b_master.log; do
  [ -f "$f" ] && mv "$f" "${f}.crash_1102_1839" && echo "    moved -> ${f}.crash_1102_1839"
done
ls -l --time-style='+%F %T' /tmp/baize_s1_baize2b_worker.log.crash_1102_1839 2>/dev/null | awk '{print "    证据: "$6,$7,$5"B"}'

echo
echo "[4] 重启 S1（2 机 16 卡，自动从 latest ckpt=58000 续跑）"
cd "$LLM" || { echo "    ❌ $LLM 不存在"; exit 1; }
echo "restart $(date '+%F %T') by ops RUN_ID 230 (prev crash 18:39 SIGKILL)" >> /tmp/baize_s1_restart.log
setsid nohup bash scripts/train.sh s1 --nodes 2 > /tmp/baize_s1_baize2b_worker.log 2>&1 < /dev/null &
LPID=$!
echo "    launcher pid=$LPID  (转后台, 30s 后验证)"
sleep 30

echo
echo "[5] 验证（进程 / 显存 / 日志）"
echo "  torchrun=$(ps -eo cmd | grep -cE '[t]orchrun|[p]retrain_launcher')"
timeout 10 ps -eo pid,etime,cmd 2>/dev/null | grep -E '[t]orchrun|[p]retrain_launcher' | head -3 | cut -c1-120 | sed 's/^/    /'
echo "  .29 GPU mem: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr '\n' ' ')"
echo "  worker.log ($(stat -c %s /tmp/baize_s1_baize2b_worker.log 2>/dev/null)B) 尾 12:"
timeout 8 tail -12 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-150 | sed 's/^/    /'

echo
echo "[6] 再等 45s 看是否真的在出 step"
sleep 45
echo "  .29 GPU util: $(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader | tr '\n' ' ')"
echo "  最新 iteration 行:"
timeout 8 grep -E 'iteration +[0-9]+/' /tmp/baize_s1_baize2b_worker.log 2>/dev/null | tail -3 | cut -c1-150 | sed 's/^/    /'
echo "  worker.log 尾 6:"
timeout 8 tail -6 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-150 | sed 's/^/    /'

echo
echo "=== DONE 230 ==="
```
