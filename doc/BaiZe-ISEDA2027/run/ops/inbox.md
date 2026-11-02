# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 237 | TARGET: 29 -->
## RUN_ID 237 — 新会话启动后的安全复核（确认没去动 S1、没抢 GPU）

```bash
set -u
echo "=== RUN_ID 237 | post-kill safety check | $(date '+%F %T') | host=$(hostname) ==="

echo "[1] 新 cline 会话"
timeout 8 ps -eo pid,etime,pcpu,rss,cmd 2>/dev/null | grep '[.]cline_pretrain' | head -3 | cut -c1-120 | sed 's/^/    /' || echo "    (尚未启动/已结束)"
echo "    loop: $(timeout 8 ps -eo pid,etime,cmd 2>/dev/null | grep -E '[b]aize_pretrain_loop\.sh$' | cut -c1-80)"
echo "    loop log 尾 6:"
timeout 8 tail -6 /tmp/baize_pretrain_loop.log 2>/dev/null | cut -c1-150 | sed 's/^/    /'

echo
echo "[2] S1 是否仍是唯一训练"
echo "    train.sh: $(timeout 8 ps -eo pid,etime,cmd 2>/dev/null | grep -E '[t]rain\.sh s1' | cut -c1-100)"
echo "    torchrun=$(ps -eo cmd | grep -cE '[t]orchrun')"
timeout 10 grep -E 'iteration +[0-9]+/' /tmp/baize_s1_baize2b_worker.log 2>/dev/null | tail -2 | cut -c1-170 | sed 's/^/    /'
echo "    .29 GPU: $(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader | tr '\n' ' ' | cut -c1-200)"

echo
echo "[3] 有没有新起的 GPU 评测/第二训练"
timeout 10 ps -eo pid,etime,pcpu,cmd 2>/dev/null | grep -E 'lm_eval|p6_lmeval|train\.sh s[0-9]|torchrun' | grep -v grep | cut -c1-120 | head -6 | sed 's/^/    /'

echo
echo "[4] .12"
timeout 20 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=8 10.239.2.12 '
  echo "    util: $(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader | tr "\n" " ")"
  echo "    torchrun=$(ps -eo cmd | grep -cE "[t]orchrun")  train=$(ps -eo cmd | grep -cE "[t]rain\.sh")"
' 2>&1 | sed 's/^/  /' || echo "    ssh .12 failed"

echo "=== DONE 237 ==="
```
