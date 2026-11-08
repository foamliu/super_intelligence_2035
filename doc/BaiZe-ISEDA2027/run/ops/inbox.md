# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 256 | TARGET: 12 -->
## RUN_ID 256 — **改用 `worker.log` 重跑三段统计**（255 证实 master.log 无 step 行）

```bash
set -u
echo "=== RUN_ID 256 | buckets from worker.log | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'cp -f /tmp/baize_ab_analyze.sh /tmp/baize_ab_analyze_worker.sh; sed -i "s#baize_s1_baize2b_master.log#baize_s1_baize2b_worker.log#; /^sleep 800$/d" /tmp/baize_ab_analyze_worker.sh; bash /tmp/baize_ab_analyze_worker.sh; echo "-- buckets --"; grep -E "^[[:space:]]*(pre|FROZEN|post)[[:space:]]+n=" /tmp/baize_ab_analyze.txt; echo; echo "-- raw last 14 --"; sed -n "/--- last 14 step lines ---/,/=== END ===/p" /tmp/baize_ab_analyze.txt | head -20; echo; echo "-- grep count worker --"; grep -c "elapsed time per iteration" /tmp/baize_s1_baize2b_worker.log'
echo
echo "=== 256 done ==="
```
