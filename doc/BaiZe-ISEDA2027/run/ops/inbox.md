# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 235 | TARGET: 29 -->
## RUN_ID 235 — 收尾复核：S1 是否稳定在出 step、有没有出现第二个训练进程/GPU 评测

```bash
set -u
echo "=== RUN_ID 235 | S1 steady check | $(date '+%F %T') | host=$(hostname) ==="
W=/tmp/baize_s1_baize2b_worker.log

echo "[1] 最新 3 条 iteration（lr 应逐步爬升）"
timeout 10 grep -E 'iteration +[0-9]+/' "$W" 2>/dev/null | tail -3 | cut -c1-175 | sed 's/^/    /'
echo "    日志 mtime=$(stat -c %y "$W" 2>/dev/null | cut -c1-19)  size=$(stat -c %s "$W" 2>/dev/null)B"

echo
echo "[2] .29 GPU"
timeout 12 nvidia-smi --query-gpu=index,utilization.gpu,memory.used,power.draw,temperature.gpu --format=csv,noheader 2>/dev/null | sed 's/^/    /'

echo
echo "[3] 进程唯一性（防第二个训练）"
echo "    torchrun=$(ps -eo cmd | grep -cE '[t]orchrun')  launcher=$(ps -eo cmd | grep -cE '[p]retrain_launcher')"
echo "    train.sh 实例:"
timeout 10 ps -eo pid,etime,cmd 2>/dev/null | grep -E '[t]rain\.sh s1' | cut -c1-110 | sed 's/^/    /'
echo "    GPU 评测类进程（应为 0）:"
timeout 10 ps -eo pid,etime,pcpu,cmd 2>/dev/null | grep -E 'python[^ ]* .*(lm_eval|p6_lmeval|cpu_smoke)' | cut -c1-120 | head -5 | sed 's/^/    /' || true

echo
echo "[4] .12"
timeout 20 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=8 10.239.2.12 '
  echo "    util: $(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader | tr "\n" " ")"
  echo "    torchrun=$(ps -eo cmd | grep -cE "[t]orchrun")  train=$(ps -eo cmd | grep -cE "[t]rain\.sh s1")"
  echo "    mem_avail=$(free -g | awk "/Mem:/{print \$7\"G\"}")"
' 2>&1 | sed 's/^/  /' || echo "    ssh .12 failed"

echo "=== DONE 235 ==="
```
