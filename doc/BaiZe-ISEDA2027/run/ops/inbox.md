# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 266 | TARGET: 12 -->
## RUN_ID 266 — **查 Data 线停摆 29 小时：loop 进程 / 日志 / cline 子进程 / 下载 PID**

```bash
set -u
echo "=== RUN_ID 266 | data-line stall diagnosis | $(date '+%F %T') | host=$(hostname) ==="
R=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

echo
echo "########## A) loop 进程 ##########"
echo "-- baize_data_loop --"
ps -eo pid=,ppid=,lstart=,stat=,etime=,args= | grep -F 'baize_data_loop' | grep -v grep | cut -c1-190
echo "-- count --"; ps -eo args= | grep -F 'baize_data_loop' | grep -v grep | wc -l
echo "-- vision loop (对照) --"
ps -eo pid=,ppid=,lstart=,stat=,etime=,args= | grep -F 'baize_vision_loop' | grep -v grep | cut -c1-190
echo "-- all baize_* loop --"
ps -eo pid=,lstart=,etime=,args= | grep -E 'baize_.*loop' | grep -v grep | cut -c1-170

echo
echo "########## B) loop 日志 ##########"
ls -l /tmp/baize_data_loop.log /tmp/baize_*loop*.log 2>/dev/null | cut -c1-150
echo "-- data loop log tail 25 --"
tail -25 /tmp/baize_data_loop.log 2>/dev/null || echo "(no data loop log)"

echo
echo "########## C) cline 子进程（data 线是否在跑） ##########"
ps -eo pid=,ppid=,lstart=,etime=,stat=,pcpu=,args= | grep -i 'cline' | grep -v grep | cut -c1-200 | head -12
echo "-- cline count --"; ps -eo args= | grep -ci cline || true

echo
echo "########## D) 下载进程 PID 1920377 ##########"
ps -o pid=,ppid=,lstart=,etime=,stat=,args= -p 1920377 2>/dev/null || echo "PID 1920377 NOT FOUND"
echo "-- roi download procs --"
ps -eo pid=,etime=,args= | grep -F 'roi_download_20261107' | grep -v grep | cut -c1-170
echo "-- hf download / python download --"
ps -eo pid=,etime=,args= | grep -E 'huggingface|hf_transfer|snapshot_download' | grep -v grep | cut -c1-170 | head -8

echo
echo "########## E) MEMORY_DATA 状态 ##########"
head -3 "$R/MEMORY_DATA.md" 2>/dev/null | cut -c1-200
echo "-- mtime --"; stat -c '%y  %n' "$R/MEMORY_DATA.md" 2>/dev/null
echo "-- git last commit touching data --"
cd /nas_train/app.e0031982/code/super_intelligence_2035 && timeout 10 git log -1 --format='%h %ad %s' --date=iso -- doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md 2>&1 | cut -c1-180

echo
echo "########## F) 系统负载（是否被别的东西占满） ##########"
uptime; echo "-- top cpu --"; ps -eo pid=,pcpu=,etime=,args= --sort=-pcpu | head -8 | cut -c1-170

echo
echo "=== 266 done ==="
```


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
