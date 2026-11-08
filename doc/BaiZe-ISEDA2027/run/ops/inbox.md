# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 264 | TARGET: 12 -->
## RUN_ID 264 — **`.29` relay：精确杀掉全部实例 + 检测是否被拉起 + 只留 1 个**

```bash
set -u
echo "=== RUN_ID 264 | enforce exactly one .29 relay | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'set -u
S=/tmp/ops_relay_v2_29_fixed.sh
pids(){ ps -eo pid=,args= | awk "\$2==\"bash\" && \$3 ~ /tmp.ops_relay_v2_29/ {print \$1}"; }
echo "-- pids before --"; PB=$(pids); echo "[$PB]"; for p in $PB; do ps -o pid=,ppid=,lstart=,args= -p $p | cut -c1-170; done
echo "-- kill --"; for p in $PB; do kill -TERM $p 2>/dev/null; done; sleep 3; for p in $PB; do kill -KILL $p 2>/dev/null; done; sleep 2
echo "-- after kill --"; PA=$(pids); echo "[$PA]"
echo "-- respawn watch 15s --"; sleep 15; PR=$(pids); echo "[$PR]"
for p in $PR; do PP=$(ps -o ppid= -p $p 2>/dev/null | tr -d " "); echo "pid=$p ppid=$PP"; ps -o pid=,args= -p $PP 2>/dev/null | cut -c1-160; done
if [ -z "$(pids)" ]; then
  echo "-- start one --"; setsid nohup bash "$S" >>/tmp/baize_ops_relay.29.log 2>&1 < /dev/null & echo "started=$!"; sleep 4
else
  echo "-- someone respawned; not starting another --"
fi
echo "-- final --"; PF=$(pids); echo "[$PF]"; for p in $PF; do ps -o pid=,ppid=,lstart=,args= -p $p | cut -c1-170; done
echo "-- log tail --"; tail -3 /tmp/baize_ops_relay.29.log'
echo
echo "=== 264 done ==="
```
