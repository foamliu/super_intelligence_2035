# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 272 | TARGET: 12 -->
## RUN_ID 272 — **侦察 3：client 参数 / chunk0 修复脚本 / 各 chunk 进度**（只读）

```bash
set -u
echo "=== RUN_ID 272 | recon3 | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'set -u
echo "-- eval-py args --"; grep -nE "add_argument" /tmp/baize_eval_v4/gguf_lmeval_run.py | cut -c1-150
echo "-- hs c2/c3 full cmd --"
ps -eo pid=,args= | awk "/[g]guf_lmeval_run\.py/ && /8186|8187/ {print \"  \" \$1 \" :: \" substr(\$0,index(\$0,\$2),650)}"
echo "-- restart script 1-40 --"; sed -n "1,40p" /tmp/baize_eval_v5/restart_piqa_hellaswag.sh | cut -c1-200
echo "-- restart script 41-80 --"; sed -n "41,80p" /tmp/baize_eval_v5/restart_piqa_hellaswag.sh | cut -c1-260
echo "-- shard stats --"
for i in 0 1 2 3; do python3 -c "import json;d=json.load(open(\"/tmp/baize_eval_v5/hs_shard${i}.json\"));print(\"  shard${i}\",len(d),d[:2],d[-2:])" 2>/dev/null; done
echo "-- chunk logs tails --"
D=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results/gguf_iter_112000_full_v5_correct_binary
for f in $D/hellaswag_chunk*/log* $D/hellaswag_chunk*/*.log; do [ -f "$f" ] && { echo "  == $f"; tail -2 "$f" | cut -c1-150 | sed "s/^/    /"; }; done
echo "-- chunk dirs --"; for d in $D/hellaswag_chunk*; do [ -d "$d" ] && { echo "  $d"; ls -l "$d" | head -4 | sed "s/^/    /"; }; done
echo "-- load --"; cut -d" " -f1-3 /proc/loadavg'
echo
echo "=== 272 done ==="
```
