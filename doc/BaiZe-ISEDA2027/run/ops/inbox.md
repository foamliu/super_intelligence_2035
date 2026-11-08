# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 265 | TARGET: 12 -->
## RUN_ID 265 — **两台 relay 存活探测：.12 本地 + .29 远端（进程/锁/日志/心跳）**

```bash
set -u
echo "=== RUN_ID 265 | relay liveness probe | $(date '+%F %T') | host=$(hostname) ==="
R=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"

echo
echo "########## A) LOCAL (.12) ##########"
echo "-- hostname / now --"; hostname; date '+%F %T'
echo "-- relay procs (ops_relay_v2) --"
ps -eo pid=,ppid=,lstart=,stat=,args= | grep -F 'ops_relay_v2' | grep -v grep | cut -c1-190
echo "-- relay procs count --"
ps -eo args= | grep -F 'ops_relay_v2' | grep -v grep | wc -l
echo "-- state files --"
for f in .last_run_id .last_run_id.12 .last_run_id.29; do printf '%-18s ' "$f"; cat "$R/$f" 2>/dev/null | tr -d '\n'; echo; done
echo "-- state mtime --"; stat -c '%y  %n' "$R"/.last_run_id* 2>/dev/null
echo "-- log files --"
ls -l /tmp/baize_ops_relay* 2>/dev/null | cut -c1-150
echo "-- log tail (.12) --"
tail -8 /tmp/baize_ops_relay.12.log 2>/dev/null || echo "(no .12 log)"

echo
echo "########## B) REMOTE (.29 via ssh) ##########"
$SSH 10.239.2.29 'set -u
echo "-- hostname / now --"; hostname; date "+%F %T"
echo "-- relay procs --"
ps -eo pid=,ppid=,lstart=,stat=,args= | grep -F ops_relay_v2 | grep -v grep | cut -c1-190
echo "-- relay procs count --"
ps -eo args= | grep -F ops_relay_v2 | grep -v grep | wc -l
echo "-- script on disk --"
ls -l /tmp/ops_relay_v2_29_fixed.sh /tmp/ops_relay_v2.sh 2>/dev/null
echo "-- flock holder --"
if [ -f /tmp/ops_relay_v2_29.lock ]; then
  ls -l /tmp/ops_relay_v2_29.lock
  (command -v fuser >/dev/null 2>&1 && fuser -v /tmp/ops_relay_v2_29.lock) 2>&1 | head -6
fi
echo "-- state --"
cat /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops/.last_run_id.29 2>/dev/null
echo "-- log tail (.29) --"
ls -l /tmp/baize_ops_relay*.log 2>/dev/null | cut -c1-150
tail -12 /tmp/baize_ops_relay.29.log 2>/dev/null || echo "(no .29 log)"
echo "-- worktree HEAD --"
cd /nas_train/app.e0031982/code/super_intelligence_2035 2>/dev/null && timeout 8 git rev-parse --short HEAD 2>&1 | head -2
'
echo "ssh_rc=$?"
echo
echo "=== 265 done ==="
```


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
