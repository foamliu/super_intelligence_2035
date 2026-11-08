# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 258 | TARGET: 12 -->
## RUN_ID 258 — **看 `.29` relay 是卡住还是跳过（子进程/阻塞点/本地游标/本地 outbox）**

```bash
set -u
echo "=== RUN_ID 258 | relay hang check | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'set -u
P=2259598; R=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
echo "-- state29 --"; cat $R/ops/.last_run_id.29 2>/dev/null; echo
echo "-- inbox run_id --"; sed -n "s/.*RUN_ID:[[:space:]]*\([0-9]\+\).*/\1/p" $R/ops/inbox.md | head -1
echo "-- local outbox RUN_ID 248..258 --"; grep -nE "^## RUN_ID (24[8-9]|25[0-8])" $R/ops/outbox.md | tail -12
echo "-- relay status --"; grep -E "^(State|Threads|voluntary_ctxt_switches|nonvoluntary_ctxt_switches)" /proc/$P/status 2>/dev/null
echo "-- wchan --"; cat /proc/$P/wchan 2>/dev/null; echo
echo "-- children --"; ps -o pid=,ppid=,stat=,etimes=,args= --ppid $P 2>/dev/null | cut -c1-160
echo "-- open fds --"; ls -l /proc/$P/fd 2>/dev/null | awk "{print \$9,\$10,\$11}" | head -12
echo "-- recent git procs --"; ps -eo pid=,ppid=,stat=,etimes=,args= | awk "/[g]it |[g]it-remote|[s]sh / && !/cline/ {print \"  \" \$1 \" ppid=\" \$2 \" \" \$3 \" et=\" \$4 \" :: \" substr(\$0,index(\$0,\$5),110)}" | head -10
echo "-- lock/rebase --"; ls -l .git/index.lock .git/HEAD.lock 2>/dev/null; ls -d .git/rebase-merge .git/rebase-apply 2>/dev/null
echo "-- push path test (15s) --"; cd /nas_train/app.e0031982/code/super_intelligence_2035; timeout 15 git ls-remote origin HEAD 2>&1 | tail -2; echo "lsremote_rc=$?"
echo "-- log tail --"; tail -4 /tmp/baize_ops_relay.29.log 2>/dev/null'
echo
echo "=== 258 done ==="
```
