# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 254 | TARGET: 12 -->
## RUN_ID 254 — **只取三段统计与原始尾行**（253 输出被 20k 上限截断）

```bash
set -u
echo "=== RUN_ID 254 | buckets only | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'echo "-- buckets --"; grep -E "^[[:space:]]*(pre|FROZEN|post)[[:space:]]+n=" /tmp/baize_ab_analyze.txt; echo; echo "-- raw last steps --"; sed -n "/--- last 14 step lines ---/,/=== END ===/p" /tmp/baize_ab_analyze.txt | head -20; echo; echo "-- file size/lines --"; wc -lc /tmp/baize_ab_analyze.txt'
echo
echo "=== 254 done ==="
```
