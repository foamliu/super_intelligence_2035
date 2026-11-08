# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 261 | TARGET: 29 -->
## RUN_ID 261 — **`.29` 新 relay 端到端验证（本机执行）**

```bash
set -u
echo "=== RUN_ID 261 | .29 relay E2E | $(date '+%F %T') ==="
echo "host=$(hostname)"
echo "-- relay --"; pgrep -af "[o]ps_relay" | cut -c1-150
echo "-- state --"; cat /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops/.last_run_id.29 2>/dev/null
echo "-- git locks --"; ls -l /nas_train/app.e0031982/code/super_intelligence_2035/.git/index.lock /nas_train/app.e0031982/code/super_intelligence_2035/.git/HEAD.lock 2>/dev/null || echo "no locks"
echo "-- load --"; cut -d" " -f1-3 /proc/loadavg
echo "RELAY29_E2E_OK"
```
