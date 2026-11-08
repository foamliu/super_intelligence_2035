# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 263 | TARGET: 29 -->
## RUN_ID 263 — **`.29` relay 最终验证：执行 + flock 单例自检**

```bash
set -u
echo "=== RUN_ID 263 | .29 relay final check | $(date '+%F %T') ==="
echo "host=$(hostname)"
echo "-- running instances --"
ps -eo pid=,stat=,lstart=,args= | awk '$1 ~ /^[0-9]+$/ && $4=="bash" && $5 ~ /tmp.ops_relay_v2_29/ {print}' | head -5
echo "-- count --"; ps -eo args= | awk '$1=="bash" && $2 ~ /tmp.ops_relay_v2_29/ {n++} END{print n+0}'
echo "-- singleton test (should refuse and exit) --"
timeout 5 bash /tmp/ops_relay_v2_29_fixed.sh; echo "singleton_rc=$?"
echo "-- count after test --"; ps -eo args= | awk '$1=="bash" && $2 ~ /tmp.ops_relay_v2_29/ {n++} END{print n+0}'
echo "-- state --"; cat /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops/.last_run_id.29
echo "RELAY29_FINAL_OK"
```
