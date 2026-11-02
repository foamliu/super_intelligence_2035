# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 233 | TARGET: 29 -->
## RUN_ID 233 — S1 首次 step 复核（19:54 时日志 30s 未增长、iteration 仍 0；确认是启动期还是卡住）

```bash
set -u
echo "=== RUN_ID 233 | S1 first-step check | $(date '+%F %T') | host=$(hostname) ==="
W=/tmp/baize_s1_baize2b_worker.log

echo "[1] 日志增长（15s 两采样）+ iteration 行"
S1=$(stat -c %s "$W"); sleep 15; S2=$(stat -c %s "$W")
echo "    size $S1 -> $S2 (delta=$((S2-S1))B)  mtime=$(stat -c %y "$W" | cut -c1-19)"
echo "    iteration_lines=$(timeout 10 grep -cE 'iteration +[0-9]+/' "$W" 2>/dev/null)"
timeout 10 grep -E 'iteration +[0-9]+/' "$W" 2>/dev/null | tail -3 | cut -c1-165 | sed 's/^/    /'

echo
echo "[2] .29 GPU（不支持 -l，用单次查询）"
timeout 12 nvidia-smi --query-gpu=index,utilization.gpu,memory.used,power.draw,temperature.gpu --format=csv,noheader 2>/dev/null | sed 's/^/    /'

echo
echo "[3] 日志尾 15 行（是否有报错/等待）"
timeout 10 tail -15 "$W" 2>/dev/null | cut -c1-150 | sed 's/^/    /'

echo
echo "[4] 进程代数（etime 分布）+ 是否有 rank 退出"
timeout 10 ps -eo etime,cmd 2>/dev/null | grep -E '[p]retrain_launcher' | awk '{print $1}' | sort | uniq -c | sort -rn | head -5 | sed 's/^/    /'
echo "    python 总数=$(ps -eo cmd | grep -c '[p]ython')"

echo
echo "[5] .12"
timeout 20 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=8 10.239.2.12 '
  echo "    util: $(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader | tr "\n" " ")"
  echo "    torchrun=$(ps -eo cmd | grep -cE "[t]orchrun") load=$(cut -d" " -f1-3 /proc/loadavg)"
' 2>&1 | sed 's/^/  /' || echo "    ssh .12 failed"

echo "=== DONE 233 ==="
```
