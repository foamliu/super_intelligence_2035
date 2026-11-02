# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 231 | TARGET: 29 -->
## RUN_ID 231 — 重启后 3 分钟复核：是否真在出 step / 双机 16 卡 / 0 NaN / 断点是否接上 58110

```bash
set -u
echo "=== RUN_ID 231 | S1 restart verify | $(date '+%F %T') | host=$(hostname) ==="

echo
echo "[1] 进程"
echo "  torchrun=$(ps -eo cmd | grep -cE '[t]orchrun')  launcher=$(ps -eo cmd | grep -cE '[p]retrain_launcher')"
timeout 10 ps -eo pid,etime,pcpu,rss,cmd 2>/dev/null | grep -E '[p]retrain_launcher' | head -2 | cut -c1-120 | sed 's/^/    /'

echo
echo "[2] .29 GPU"
timeout 12 nvidia-smi --query-gpu=index,utilization.gpu,memory.used,power.draw,temperature.gpu --format=csv,noheader 2>/dev/null | sed 's/^/    /'

echo
echo "[3] 训练进度（worker.log 最新 iteration 行）"
echo "  log size=$(stat -c %s /tmp/baize_s1_baize2b_worker.log 2>/dev/null)B  mtime=$(stat -c %y /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-19)"
timeout 10 grep -E 'iteration +[0-9]+/' /tmp/baize_s1_baize2b_worker.log 2>/dev/null | tail -3 | cut -c1-165 | sed 's/^/    /'
echo "  尾部 8 行:"
timeout 10 tail -8 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-150 | sed 's/^/    /'

echo
echo "[4] 0 NaN / 断点是否接上（应 >=58110，不应回到 0/58000 之前）"
timeout 10 grep -cE 'nan iterations: +[1-9]' /tmp/baize_s1_baize2b_worker.log 2>/dev/null | sed 's/^/    nan_hits=/'
timeout 10 grep -E 'load-checkpoint|Loading checkpoint|successfully loaded' /tmp/baize_s1_baize2b_worker.log 2>/dev/null | tail -3 | cut -c1-150 | sed 's/^/    /'

echo
echo "[5] .12 侧"
timeout 20 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=8 10.239.2.12 '
  echo "    util: $(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader | tr "\n" " ")"
  echo "    mem:  $(nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr "\n" " ")"
  echo "    torch=$(ps -eo cmd | grep -cE "[t]orchrun|[p]retrain_launcher")  load=$(cut -d" " -f1-3 /proc/loadavg)"
  echo "    mem_avail=$(free -g | awk "/Mem:/{print \$7\"G\"}")"
' 2>&1 | sed 's/^/  /' || echo "    ssh .12 failed"

echo
echo "=== DONE 231 ==="
```
