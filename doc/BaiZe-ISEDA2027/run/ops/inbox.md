# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 252 | TARGET: 12 -->
## RUN_ID 252 — **取回 pre / FROZEN / post 三段 Step Time 统计**（解析器已于 12:39:20 生成）

> 冻结窗口 12:23:46–12:33:46，客户端已全部恢复（`251` 在 12:36:25 确认 7×`Ssl`，chunk 日志继续增长）。
> 本命令只 `cat` 结果 + 复核当前状态，不再改动任何进程。

```bash
set -u
echo "=== RUN_ID 252 | read A/B analysis | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'echo "-- file --"; ls -l /tmp/baize_ab_analyze.txt 2>/dev/null; echo; cat /tmp/baize_ab_analyze.txt 2>/dev/null; echo; echo "-- clients now --"; ps -eo pid=,stat=,pcpu=,args= | awk "/[g]guf_lmeval_run\\.py/ && !/cline/ {print \"  \" \$1 \" \" \$2 \" \" \$3}" ; echo "-- guard watchdog --"; ps -eo pid=,stat=,args= | awk "/guard_sigcont/ && !/awk/ {print \"  \" \$1 \" \" \$2 \" \" substr(\$0,index(\$0,\$3),100)}"; echo "-- load --"; cut -d\" \" -f1-3 /proc/loadavg'
echo
echo "=== 252 done ==="
```
