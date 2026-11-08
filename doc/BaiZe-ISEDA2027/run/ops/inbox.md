# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 276 | TARGET: 12 -->
## RUN_ID 276 — **取 chunk2/3 当前已评估计数与速率**（只读）

```bash
set -u
echo "=== RUN_ID 276 | c2/c3 progress | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'set -u
for n in chunk2_restart chunk3_numa_fix; do
  f=/tmp/baize_eval_v5/logs/client_hellaswag_${n}.log
  echo "== $n =="
  [ -f "$f" ] && tr "\r" "\n" < "$f" | grep -E "^gguf-ll:" | tail -2 | cut -c1-120 | sed "s/^/  /"
  stat -c "  mtime=%y size=%s" "$f" 2>/dev/null
done
echo "-- etimes --"; ps -o pid=,etimes=,pcpu= -p 2097234,2097251 2>/dev/null
echo "-- c2/c3 server cpu --"; ps -o pid=,pcpu=,psr= -p 2083722,2083724 2>/dev/null'
echo
echo "=== 276 done ==="
```
