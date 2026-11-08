# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 262 | TARGET: 12 -->
## RUN_ID 262 — **收口：`.29` relay 单例化（杀重复实例 + flock）**

> 261 验证成功，但 `pgrep` 显示 **两个** `ops_relay_v2_29_fixed.sh`（1727811 / 1958576），存在重复执行风险。
> 本命令：列出 → 全杀 → 给脚本加 `flock` 单例 → 只启一个 → 复核。

```bash
set -u
echo "=== RUN_ID 262 | single-instance .29 relay | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'set -u
R=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
S=/tmp/ops_relay_v2_29_fixed.sh
echo "-- procs before --"
ps -eo pid=,ppid=,lstart=,args= | awk "\$2==\"bash\" && \$3 ~ /tmp.ops_relay_v2_29/ {print}"
echo "-- dup 261 blocks in local outbox --"; grep -c "^## RUN_ID 261" $R/ops/outbox.md
echo "-- fd1 per instance --"
for p in $(ps -eo pid=,args= | awk "\$2==\"bash\" && \$3 ~ /tmp.ops_relay_v2_29/ {print \$1}"); do echo "  $p -> $(readlink /proc/$p/fd/1 2>/dev/null)"; done
echo "-- stop all --"
for p in $(ps -eo pid=,args= | awk "\$2==\"bash\" && \$3 ~ /tmp.ops_relay_v2_29/ {print \$1}"); do kill -TERM "$p" 2>/dev/null; done
sleep 2
for p in $(ps -eo pid=,args= | awk "\$2==\"bash\" && \$3 ~ /tmp.ops_relay_v2_29/ {print \$1}"); do kill -KILL "$p" 2>/dev/null; done
sleep 1
LEFT=$(ps -eo pid=,args= | awk "\$2==\"bash\" && \$3 ~ /tmp.ops_relay_v2_29/ {print \$1}" | wc -l); echo "left=$LEFT"
echo "-- add flock singleton --"
if command -v flock >/dev/null 2>&1; then
  if ! grep -q "ops_relay_v2_29.lock" "$S"; then
    sed -i "/^set -u$/a exec 9>/tmp/ops_relay_v2_29.lock\nflock -n 9 || { echo \"[relay-29] another instance running, exit\"; exit 0; }" "$S"
  fi
  echo "flock=yes"; head -5 "$S"
else
  echo "flock=NO (skip)"; head -3 "$S"
fi
chmod +x "$S"
echo "-- start one --"
setsid nohup bash "$S" >>/tmp/baize_ops_relay.29.log 2>&1 < /dev/null &
sleep 3
echo "-- procs after --"
ps -eo pid=,stat=,lstart=,args= | awk "\$2!=\"\" && \$0 ~ /tmp.ops_relay_v2_29/ {print}" | head -5
echo "-- count after --"; ps -eo args= | awk "\$1==\"bash\" && \$2 ~ /tmp.ops_relay_v2_29/ {n++} END{print n+0}"
echo "-- log tail --"; tail -3 /tmp/baize_ops_relay.29.log
echo "-- state --"; cat $R/ops/.last_run_id.29'
echo
echo "=== 262 done ==="
```
