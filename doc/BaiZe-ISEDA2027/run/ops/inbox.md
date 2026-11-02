# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 228 | TARGET: 29 -->
## RUN_ID 228 — 复核"16 卡是否真空"+ 取证 SIGBUS/SIGKILL（只读，多手段交叉验证）

```bash
set -u
echo "=== RUN_ID 228 | GPU idle cross-check | $(date '+%F %T %Z') | host=$(hostname) ==="
echo "  uptime: $(uptime | tr -s ' ')"
echo "  nvidia-smi 设备数: $(nvidia-smi -L 2>/dev/null | wc -l)  ($(nvidia-smi -L 2>/dev/null | head -1 | cut -c1-60))"

echo
echo "[1] nvidia-smi 全表（.29）"
timeout 15 nvidia-smi 2>/dev/null | sed -n '1,12p' | cut -c1-150 | sed 's/^/    /'
echo "  --- GPU 行 ---"
timeout 15 nvidia-smi 2>/dev/null | sed -n '13,24p' | cut -c1-150 | sed 's/^/    /'

echo
echo "[2] 计算进程视角（三种查法）"
echo "  a) nvidia-smi --query-compute-apps:"
timeout 12 nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv 2>/dev/null | sed 's/^/    /'
echo "  b) nvidia-smi pmon -c 1:"
timeout 15 nvidia-smi pmon -c 1 2>/dev/null | head -12 | sed 's/^/    /'
echo "  c) 3 次间隔采样（utilization.gpu / memory.used / power / temp）:"
timeout 20 nvidia-smi --query-gpu=index,utilization.gpu,memory.used,power.draw,temperature.gpu --format=csv,noheader -l 1 -c 3 2>/dev/null | sed 's/^/    /'

echo
echo "[3] 有没有 python/torch 训练进程（全用户，按 CPU 排序前 10）"
timeout 10 ps -eo user,pid,etime,pcpu,pmem,rss,cmd --sort=-pcpu 2>/dev/null | head -11 | cut -c1-120 | sed 's/^/    /'
echo "  python 进程数=$(timeout 10 ps -eo cmd 2>/dev/null | grep -c '[p]ython')"

echo
echo "[4] 内存/swap（判断是否曾发生内存压力）"
free -g | sed 's/^/    /'
echo "  oom 计数: $(timeout 5 cat /proc/vmstat 2>/dev/null | grep oom_kill | tr '\n' ' ')"

echo
echo "[5] 内核日志（多种入口，找 OOM / SIGBUS 线索）"
echo "  dmesg tail 20:"
timeout 12 dmesg 2>/dev/null | tail -20 | cut -c1-150 | sed 's/^/    /' || echo "    (dmesg 受限)"
echo "  /var/log/syslog|messages grep -i 'killed process|oom|mce|machine check':"
for f in /var/log/syslog /var/log/messages /var/log/kern.log; do
  [ -r "$f" ] || continue
  timeout 10 grep -iE 'killed process|out of memory|oom-kill|machine check|mce:' "$f" 2>/dev/null | tail -6 | cut -c1-150 | sed "s|^|    $f: |"
done

echo
echo "[6] master 日志：失败顺序（SIGKILL vs SIGBUS 谁先）"
timeout 10 grep -nE 'SIGKILL|SIGBUS|SIGSEGV|Root Cause|first observed|exitcode|Traceback|Error' /tmp/baize_s1_baize2b_master.log 2>/dev/null | tail -14 | cut -c1-160 | sed 's/^/    /'
echo "  master 里最后的训练进度行:"
timeout 10 grep -E 'iteration +[0-9]+/' /tmp/baize_s1_baize2b_worker.log 2>/dev/null | tail -2 | cut -c1-160 | sed 's/^/    /'

echo
echo "[7] CPU 冒烟测试文件（18:46-19:18 那批）+ 是否有进程在跑"
timeout 10 ls -lt --time-style='+%F %T' /tmp 2>/dev/null | grep -iE 'cpu_smoke|lmeval' | head -8 | awk '{print "    "$6,$7,$5"B",$8}'
timeout 10 ps -eo pid,etime,pcpu,cmd 2>/dev/null | grep -E '[t]est_lmeval|[l]m_eval|[c]pu_smoke' | cut -c1-120 | head -5 | sed 's/^/    /' || echo "    (无相关进程)"

echo
echo "[8] .12 侧交叉验证"
timeout 20 ssh -o StrictHostKeyChecking=no -o ConnectTimeout=8 10.239.2.12 '
  echo "    host=$(hostname) date=$(date +%H:%M:%S) up=$(cut -d" " -f1 /proc/uptime)s"
  echo "    gpu_lines=$(nvidia-smi -L | wc -l)"
  nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader | tr "\n" " " | cut -c1-160
  echo ""
  echo "    compute_apps=$(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader | tr "\n" "|")"
  echo "    torch=$(ps -eo cmd | grep -cE "[t]orchrun|[p]retrain_launcher")"
  echo "    mem: $(free -g | awk "/Mem:/{print \"total=\"\$2\"G used=\"\$3\"G avail=\"\$7\"G\"}")"
' 2>&1 | sed 's/^/  /' || echo "    ssh .12 failed"

echo
echo "=== DONE 228 ==="
```
