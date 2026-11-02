# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 238 | TARGET: 29 -->
## RUN_ID 238 — 例行进展快照：S1 进度/lr 爬升、CPU smoke 结果、CPU 负载是否 ≤80%

```bash
set -u
echo "=== RUN_ID 238 | progress snapshot | $(date '+%F %T') | host=$(hostname) ==="
W=/tmp/baize_s1_baize2b_worker.log

echo
echo "[1] S1 训练"
timeout 10 grep -E 'iteration +[0-9]+/' "$W" 2>/dev/null | tail -3 | cut -c1-175 | sed 's/^/    /'
echo "    log mtime=$(stat -c %y "$W" 2>/dev/null | cut -c1-19)"
echo "    train.sh=$(timeout 8 ps -eo pid,etime,cmd 2>/dev/null | grep -E '[t]rain\.sh s1' | awk '{print $1" "$2}')"

echo
echo "[2] .29 GPU"
timeout 12 nvidia-smi --query-gpu=index,utilization.gpu,memory.used,power.draw,temperature.gpu --format=csv,noheader 2>/dev/null | sed 's/^/    /'

echo
echo "[3] CPU 负载 / eval 占用（要求整机 ≤80%）"
echo "    nproc=$(nproc) load=$(cut -d' ' -f1-3 /proc/loadavg)"
timeout 8 vmstat 1 2 2>/dev/null | tail -1 | awk '{print "    us%="$13" sy%="$14" id%="$15}'
echo "    eval 进程:"
timeout 10 ps -eo pid,etime,pcpu,rss,cmd 2>/dev/null | grep -E 'python[^ ]* .*(cpu_lmeval|lm_eval|test_lmeval)' | grep -v grep | cut -c1-130 | head -5 | sed 's/^/    /' || echo "    (无)"

echo
echo "[4] CPU smoke / 评测日志（找 acc 是否 >0）"
timeout 10 ls -lt --time-style='+%F %T' /tmp 2>/dev/null | grep -iE 'cpu_lmeval|lmeval|cpu_smoke' | head -6 | awk '{print "    "$6,$7,$5"B",$8}'
for f in $(ls -t /tmp/*cpu_lmeval*.log /tmp/*lmeval*.log 2>/dev/null | head -2); do
  echo "    ---- $f 尾 12 ----"
  timeout 8 tail -12 "$f" 2>/dev/null | cut -c1-140 | sed 's/^/      /'
done

echo
echo "[5] .12（训练 + 负载）"
timeout 20 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=8 10.239.2.12 '
  echo "    util: $(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader | tr "\n" " ")"
  echo "    load=$(cut -d" " -f1-3 /proc/loadavg)  nproc=$(nproc)"
  echo "    eval=$(ps -eo pcpu,cmd | grep -E "python[^ ]* .*(cpu_lmeval|lm_eval)" | grep -v grep | head -3 | tr "\n" "|")"
' 2>&1 | sed 's/^/  /' || echo "    ssh .12 failed"

echo "=== DONE 238 ==="
```
