# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 275 | TARGET: 12 -->
## RUN_ID 275 — **弄清 `--samples` 过滤逻辑 + chunk2/3 当前真实位置**（只读）

```bash
set -u
echo "=== RUN_ID 275 | samples logic | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'set -u
P=/tmp/baize_eval_v4/gguf_lmeval_run.py
echo "-- samples refs --"; grep -nE "samples|filter|select\(|limit" $P | cut -c1-150 | head -24
echo "-- code 260-330 --"; sed -n "260,330p" $P | cut -c1-180
echo "-- chunk2 last progress --"; f=/tmp/baize_eval_v5/logs/client_hellaswag_chunk2_restart.log; tr "\r" "\n" < "$f" | grep -E "^gguf-ll:" | tail -3 | cut -c1-130
echo "-- chunk3 last progress --"; f=/tmp/baize_eval_v5/logs/client_hellaswag_chunk3_numa_fix.log; tr "\r" "\n" < "$f" | grep -E "^gguf-ll:" | tail -3 | cut -c1-130
echo "-- clients etime --"; ps -o pid=,etimes=,args= -p 2097234,2097251 2>/dev/null | cut -c1-90'
echo
echo "=== 275 done ==="
```
