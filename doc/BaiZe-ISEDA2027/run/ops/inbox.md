# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 253 | TARGET: 12 -->
## RUN_ID 253 — **取回三段 Step Time（sleep 90 保证解析器已落盘）+ 原始 step 行交叉验证**

```bash
set -u
echo "=== RUN_ID 253 | read A/B analysis (after 90s) | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'sleep 90; echo "=== START ==="; echo "-- file --"; ls -l /tmp/baize_ab_analyze.txt 2>/dev/null; echo; cat /tmp/baize_ab_analyze.txt 2>/dev/null; echo; echo "-- raw last 25 step lines --"; grep -E "elapsed time per iteration" /tmp/baize_s1_baize2b_master.log | tail -25 | sed -E "s/^[[:space:]]*\[([^]]+)\].*iteration +([0-9]+)\/.*\(ms\): ([0-9.]+).*/t=\1 it=\2 ms=\3/"; echo "=== END253 ==="'
echo
echo "=== 253 done ==="
```
