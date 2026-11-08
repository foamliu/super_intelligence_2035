# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 271 | TARGET: 12 -->
## RUN_ID 271 — **补充侦察：端口映射 / client 完整命令行 / chunk0 NUMA 修复写法**（只读）

```bash
set -u
echo "=== RUN_ID 271 | recon2 | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'set -u
echo "-- ports --"; ss -ltnp 2>/dev/null | grep -E ":818[0-9]" | tr -s " " | cut -c1-170
echo "-- client cmdlines --"
ps -eo pid=,args= | awk "/[g]guf_lmeval_run\.py/ && !/cline/ {print \"  \" \$1 \" :: \" substr(\$0,index(\$0,\$2),400)}"
echo "-- script key lines --"
grep -nE "taskset|numactl|llama-server|gguf_lmeval_run|--port|--limit|--tasks|--output|shard|nohup" /tmp/baize_eval_v5/restart_piqa_hellaswag.sh /tmp/baize_eval_v5/run_hellaswag_only.sh /tmp/baize_eval_v5/baize_eval_v5_correct.sh 2>/dev/null | cut -c1-190
echo "-- relaunch log --"; cat /tmp/baize_eval_v5/relaunch_2034.log 2>/dev/null
echo "-- logs --"; D=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_112000_full_v5_correct_binary; ls -l $D/*.log 2>/dev/null | awk "{print \"  \" \$5 \" \" \$9}"
echo "-- tails --"
for f in $D/piqa*.log $D/hellaswag_chunk*.log; do [ -f "$f" ] && { echo "  == $(basename $f)"; tail -1 "$f" | cut -c1-150 | sed "s/^/    /"; }; done
echo "-- load --"; cut -d" " -f1-3 /proc/loadavg'
echo
echo "=== 271 done ==="
```
