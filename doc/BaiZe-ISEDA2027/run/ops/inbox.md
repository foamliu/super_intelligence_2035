# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 232 | TARGET: 29 -->
## RUN_ID 232 — 复核：是否已在出 step（19:53 只见 16GB 已分配但 0% util + 74 个 launcher，需确认不是 elastic 反复重启）

```bash
set -u
echo "=== RUN_ID 232 | S1 step check | $(date '+%F %T') | host=$(hostname) ==="
W=/tmp/baize_s1_baize2b_worker.log

echo
echo "[1] 日志增长（10s 两采样）"
S1=$(stat -c %s "$W" 2>/dev/null); sleep 10; S2=$(stat -c %s "$W" 2>/dev/null)
echo "    size: $S1 -> $S2  (delta=$((S2-S1))B)  mtime=$(stat -c %y "$W" 2>/dev/null | cut -c1-19)"

echo
echo "[2] iteration 行数 / 最新 3 条"
echo "    iteration_lines=$(timeout 10 grep -cE 'iteration +[0-9]+/' "$W" 2>/dev/null)"
timeout 10 grep -E 'iteration +[0-9]+/' "$W" 2>/dev/null | tail -3 | cut -c1-165 | sed 's/^/    /'

echo
echo "[3] 进程画像（判断是否 elastic 反复重启）"
echo "    launcher 进程按 etime 分布:"
timeout 10 ps -eo etime,cmd 2>/dev/null | grep -E '[p]retrain_launcher' | awk '{print $1}' | sort | uniq -c | sort -rn | head -6 | sed 's/^/    /'
echo "    torchrun 行:"
timeout 10 ps -eo pid,etime,cmd 2>/dev/null | grep -E '[t]orchrun' | head -4 | cut -c1-130 | sed 's/^/    /'

echo
echo "[4] GPU 3 采样（.29）"
timeout 20 nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader -l 1 -c 3 2>/dev/null | paste -sd'|' | sed 's/^/    /'

echo
echo "[5] 日志尾 25 行里找 错误/重启/信号"
timeout 10 tail -60 "$W" 2>/dev/null | grep -nE 'Error|error|Signal|restart|Traceback|nan|iteration' | tail -12 | cut -c1-160 | sed 's/^/    /'
echo "    原样尾 10 行:"
timeout 10 tail -10 "$W" 2>/dev/null | cut -c1-140 | sed 's/^/    /'

echo
echo "[6] .12 侧"
timeout 20 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=8 10.239.2.12 '
  echo "    util: $(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader | tr "\n" " ")"
  echo "    n_launcher=$(ps -eo cmd | grep -cE "[p]retrain_launcher")  torchrun=$(ps -eo cmd | grep -cE "[t]orchrun")"
  echo "    load=$(cut -d" " -f1-3 /proc/loadavg)"
' 2>&1 | sed 's/^/  /' || echo "    ssh .12 failed"

echo
echo "=== DONE 232 ==="
```
