# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 265 | TARGET: 12 -->
## RUN_ID 265 — **侦察 v5 eval：chunk0–3 的端口/亲和性/进度 + v5 启动脚本**（只读）

> 背景：v5 eval 中 piqa + hs chunk0/1/2/3 并行；chunk0 NUMA 修复后 2.3 s/it，chunk2/3 约 22–27 s/it。
> 目标：拿到可复制的命令行与 CPU/NUMA 现状，设计 chunk2/3 的 NUMA 重绑 + 速率均衡拆分。
> 只读：`ps` / `/proc/*/status` / `sed` / `tail` / `ls`，不 kill、不改文件。

```bash
set -u
echo "=== RUN_ID 265 | recon v5 eval | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'set -u
echo "-- lscpu --"; lscpu | grep -E "^CPU\(s\)|^Model name|^NUMA node" | cut -c1-140
echo "-- servers --"
ps -eo pid=,psr=,pcpu=,etimes=,args= | awk "/[l]lama-server/ && !/cline/ {print \"  \" \$1 \" psr=\" \$2 \" cpu=\" \$3 \" et=\" \$4 \" :: \" substr(\$0,index(\$0,\$5),120)}"
echo "-- clients --"
ps -eo pid=,psr=,pcpu=,etimes=,args= | awk "/[g]guf_lmeval_run\.py/ && !/cline/ {print \"  \" \$1 \" psr=\" \$2 \" cpu=\" \$3 \" et=\" \$4 \" :: \" substr(\$0,index(\$0,\$5),170)}"
echo "-- affinity --"
for p in $(ps -eo pid=,args= | awk "/[l]lama-server|[g]guf_lmeval_run\.py/ && !/cline/ {print \$1}"); do
  echo "  pid=$p cpus=$(grep Cpus_allowed_list /proc/$p/status 2>/dev/null | cut -f2) mems=$(grep Mems_allowed_list /proc/$p/status 2>/dev/null | cut -f2)"
done
echo "-- v5 dir --"; ls -l /tmp/baize_eval_v5/ 2>/dev/null | head -12
echo "-- launch script (1-60) --"; sed -n "1,60p" /tmp/baize_eval_v5/baize_eval_v5_correct.sh 2>/dev/null | cut -c1-170
echo "-- chunk logs --"
D=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_112000_full_v5_correct_binary
ls -l $D/*.log 2>/dev/null | awk "{print \"  \" \$5 \" \" \$9}"
echo "-- tails --"
for f in $D/hellaswag_chunk0*.log $D/hellaswag_chunk1*.log $D/hellaswag_chunk2*.log $D/hellaswag_chunk3*.log; do
  [ -f "$f" ] && { echo "  == $(basename $f)"; tail -2 "$f" | cut -c1-170 | sed "s/^/    /"; }
done
echo "-- watchers --"; ps -eo pid=,args= | awk "/redistribute|watcher|rebalance/ && !/cline/ {print \"  \" \$1 \" \" substr(\$0,index(\$0,\$2),130)}" | head -8
echo "-- load --"; cut -d" " -f1-3 /proc/loadavg'
echo
echo "=== 265 done ==="
```
