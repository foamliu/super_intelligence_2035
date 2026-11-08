# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 255 | TARGET: 12 -->
## RUN_ID 255 — **调试：为什么 awk 没匹配到 step 行**

```bash
set -u
echo "=== RUN_ID 255 | debug parser | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'echo "-- analyzer section --"; sed -n "/--- step-time buckets/,/--- last 14 step lines/p" /tmp/baize_ab_analyze.txt | head -25; echo; echo "-- grep count --"; grep -c "elapsed time per iteration" /tmp/baize_s1_baize2b_master.log; echo "-- raw tail (cat -A, 200 cols) --"; grep "elapsed time per iteration" /tmp/baize_s1_baize2b_master.log | tail -2 | cut -c1-200 | cat -A; echo "-- log mtime/size --"; stat -c "%y %s" /tmp/baize_s1_baize2b_master.log'
echo
echo "=== 255 done ==="
```
