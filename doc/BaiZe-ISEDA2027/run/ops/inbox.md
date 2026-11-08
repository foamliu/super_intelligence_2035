# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 274 | TARGET: 12 -->
## RUN_ID 274 — **取 `/tmp/baize_eval_v5/logs` 的 tqdm 进度与速率**（只读）

```bash
set -u
echo "=== RUN_ID 274 | v5 logs | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'set -u
L=/tmp/baize_eval_v5/logs
echo "-- files --"; ls -lt $L | head -12 | sed "s/^/  /"
echo "-- progress --"
for f in $L/*chunk*.log $L/*piqa*.log; do
  [ -f "$f" ] || continue
  n=$(basename "$f")
  p=$(grep -oE "[0-9]+/[0-9]+ \[[^]]*\]" "$f" | tail -1)
  echo "  $n :: ${p:-noprog}"
  tail -1 "$f" | cut -c1-120 | sed "s/^/      /"
done
echo "-- mtimes --"; stat -c "%y %n" $L/*.log 2>/dev/null | cut -c1-100 | sed "s/^/  /"'
echo
echo "=== 274 done ==="
```
