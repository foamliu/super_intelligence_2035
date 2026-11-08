# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 257 | TARGET: 12 -->
## RUN_ID 257 — **诊断 `.29` relay：工作副本 / 游标 / git 状态（只读，不 fetch）**

```bash
set -u
echo "=== RUN_ID 257 | diagnose .29 relay | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'set -u
P=2259598
echo "-- relay proc --"; ps -o pid=,ppid=,stat=,etimes=,args= -p $P 2>/dev/null | cut -c1-160
echo "-- cwd --"; CWD=$(readlink /proc/$P/cwd 2>/dev/null); echo "$CWD"
echo "-- script --"; tr "\0" " " < /proc/$P/cmdline 2>/dev/null | cut -c1-200; echo
echo "-- fd1 --"; readlink /proc/$P/fd/1 2>/dev/null
echo "-- env(hint) --"; tr "\0" "\n" < /proc/$P/environ 2>/dev/null | grep -Ei "^(HOSTTAG|HOME|PWD|OLDPWD)=" | head -6
echo "-- relay log tail --"; tail -8 /tmp/baize_ops_relay.29.log 2>/dev/null
echo
if [ -n "${CWD:-}" ] && cd "$CWD" 2>/dev/null; then
  echo "-- pwd/toplevel --"; pwd; git rev-parse --show-toplevel 2>/dev/null
  echo "-- branch/head --"; git status -sb 2>/dev/null | head -3; echo "HEAD=$(git rev-parse --short HEAD 2>/dev/null) origin/main=$(git rev-parse --short origin/main 2>/dev/null)"
  echo "-- state/local inbox --"; cat ops/.last_run_id.29 2>/dev/null; echo; head -3 ops/inbox.md 2>/dev/null | tr -d "\r"
  echo "-- counts --"; git count-objects -v 2>/dev/null | head -8
  echo "-- packs --"; ls -la .git/objects/pack 2>/dev/null | head -12
  echo "-- tmp packs/locks --"; find .git -maxdepth 2 \( -name "tmp_pack_*" -o -name "*.lock" \) -printf "  %s %p\n" 2>/dev/null | head -10
  echo "-- partial clone cfg --"; git config --get remote.origin.promisor; git config --get remote.origin.partialclonefilter; git config --get core.repositoryformatversion
  echo "-- git version --"; git --version
else
  echo "CWD_INVALID"
fi'
echo
echo "=== 257 done ==="
```
