# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 247 -->
## RUN_ID 247 — **定位 eval / 训练日志所在机器**（RUN_ID 246 在 .12 上发现 0 个 eval 进程，需重新定位）

> 目的：确认 `llama-server` / `gguf_lmeval_run.py` 与 `Step Time` 日志现在落在 `.12` 还是 `.29`。
> 只读：`ps` / `uptime` / `nvidia-smi` / `stat` / `tail`，不写任何训练或评测文件。

```bash
set -u
echo "=== RUN_ID 247 discovery | host=$(hostname) | $(date '+%F %T') ==="
echo "-- nproc / load --"; nproc; uptime
echo
echo "-- eval processes (top 20) --"
ps -eo pid=,pcpu=,psr=,args= | awk '(/[l]lama-server/ || /[g]guf_lmeval_run\.py/) && !/cline/ && !/awk/ {print "  " $1 " cpu=" $2 " psr=" $3 " :: " substr($0,index($0,$4),150)}' | head -20
echo
echo "-- counts --"
ps -eo args= | awk '/[l]lama-server/ && !/cline/{s++} /[g]guf_lmeval_run\.py/ && !/cline/{c++} END{printf "  servers=%d clients=%d\n",s,c}'
echo
echo "-- train logs --"
for f in /tmp/baize_s1_baize2b_master.log /tmp/baize_s1_baize2b_worker.log /tmp/baize_s1_baize2b.log; do
  if [ -f "$f" ]; then
    echo "  FILE $f size=$(stat -c %s "$f") mtime=$(stat -c %y "$f" | cut -c1-19)"
    grep -E 'elapsed time per iteration' "$f" | tail -3 | sed 's/^ */    /'
  fi
done
echo
echo "-- launcher / torchrun --"
ps -eo pid=,etimes=,pcpu=,args= | awk '(/scripts\/train\.sh s1/ || /[t]orchrun/) && !/cline/ {print "  " $1 " etimes=" $2 " cpu=" $3 " :: " substr($0,index($0,$4),150)}' | head -8
echo
echo "-- GPU --"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,power.draw --format=csv,noheader 2>/dev/null | sed 's/^/  /'
echo
echo "-- eval log files fresh (last 60min, /tmp) --"
find /tmp -maxdepth 1 -type f -name '*.log' -mmin -60 -printf '  %TY-%Tm-%Td %TH:%TM %10s %p\n' 2>/dev/null | sort -k2 | tail -12
echo "=== DONE 247 | $(hostname) ==="
```
